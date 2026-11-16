"""
Run many plan jobs on Kaggle unattended (Objective 3, Step 15: the test ladder). Run on the laptop and leave it.

    python kaggle\\run_queue.py harness\\plans\\obj3_step15\\*.json        # as many at once as Kaggle allows
    python kaggle\\run_queue.py ... --parallel 5                              # or at most 5 at once
    python kaggle\\run_queue.py --status                 # progress so far, no Kaggle calls

For every plan file (one Kaggle job each, its CPU runs only):
  1. push the waiting jobs together: ONE code upload carrying every unfinished job's inputs, then one kernel push
     per job (a job accepts that upload or any newer one, so later uploads never break a queued job);
     with --parallel auto (the default) it pushes every waiting job; if Kaggle refuses a push, the number running
     then is taken as Kaggle's limit and the rest wait for a free slot (the limit is probed again every 30 min);
  2. a job that Kaggle ends within a few minutes without any output (not started, e.g. over the session limit)
     goes back to waiting and does not count as a push;
  3. when a job ends, pull its results into the project (kaggle/pull_job.py);
  4. if some runs are still unfinished (a job stops itself before Kaggle's 12-hour limit and packs what it has),
     push it again: run_plan.py resumes where it stopped. At most --max-pushes per job.
State is kept in kaggle/_queue/state.json, so the command can be stopped (Ctrl+C) and started again at any time;
finished runs are also recognised from the results folders themselves.
"""

import argparse
import glob
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
STATE = os.path.join(HERE, "_queue", "state.json")
ENDED = ("complete", "error", "cancelacknowledged")
KAGGLE_CPU_SESSIONS = 5      # Kaggle allows at most 5 CPU sessions at once per account (reduced from 10)
KAGGLE_GPU_SESSIONS = 2      # GPU sessions at once: a guess, lowered if Kaggle refuses
_KIND = {}


def kind(p):
    """'gpu' for a plan whose Kaggle jobs run on a GPU session, else 'cpu'; each kind has its own session limit."""
    if p not in _KIND:
        try:
            with open(p, encoding="utf-8") as f:
                _KIND[p] = "gpu" if json.load(f).get("kaggle_backend") == "cuda" else "cpu"
        except (OSError, ValueError):
            _KIND[p] = "cpu"
    return _KIND[p]


def plan_runs(plan_path):
    """[(run name, finished cases, expected cases)] for the plan's CPU runs, read from the results folders."""
    from harness import run_eval
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    res = os.path.join(ROOT, plan.get("results_dir", "results"))
    out = []
    for run in plan["runs"]:
        cfg = dict(plan.get("defaults", {}), **run)
        if cfg.get("backend") != plan.get("kaggle_backend", "cpu"):     # the runs this job makes on Kaggle
            continue
        ids = os.path.join(ROOT, cfg["ids"]) if cfg.get("ids") else None
        if cfg.get("dialogues"):
            cases = run_eval.load_dialogues(os.path.join(ROOT, cfg["dialogues"]), cfg.get("split", "all"), ids,
                                            cfg.get("limit"))
        else:
            cases = run_eval.load_cases(os.path.join(ROOT, cfg.get("eval", "eval/eval_set.jsonl")), cfg.get("set", "all"),
                                        cfg.get("split", "all"), ids, cfg.get("category"), cfg.get("limit"))
        expected = len(cases) * int(cfg.get("repeats", 1))
        done = set()
        p = os.path.join(res, cfg["name"], "cases.jsonl")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not r.get("error"):
                        done.add((r["id"], r.get("repeat", 0)))
        if not os.path.exists(os.path.join(res, cfg["name"], "run_meta.json")):
            done = set()
        out.append((cfg["name"], len(done), expected))
    return out


def finished(plan_path):
    runs = plan_runs(plan_path)
    return bool(runs) and all(d >= e for _, d, e in runs)


def job_name(plan_path):
    return "plan_" + os.path.splitext(os.path.basename(plan_path))[0]


def kernel_status(kernel):
    import pull_job
    return pull_job.status(kernel)[0]


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, STATE)


def show(plans, st):
    tot_d = tot_e = 0
    print(f"\n{'job':44} {'state':10} {'pushes':>6}  cases")
    for p in plans:
        runs = plan_runs(p)
        d, e = sum(x[1] for x in runs), sum(x[2] for x in runs)
        tot_d, tot_e = tot_d + d, tot_e + e
        s = st.get(p, {})
        state = "finished" if d >= e else s.get("state", "waiting")
        print(f"{os.path.basename(p):44} {state:10} {s.get('pushes', 0):>6}  {d}/{e}")
    print(f"{'all':44} {'':10} {'':>6}  {tot_d}/{tot_e} ({100 * tot_d / max(1, tot_e):.0f}%)", flush=True)


def push_batch(batch, unfinished, user):
    """One code upload for the batch (inputs of every unfinished job), then one kernel push per job.
    Returns {plan: kernel id} for the pushes Kaggle accepted, and whether one was refused."""
    import push_job as PJ
    user = user or PJ.username()
    jobs = {p: PJ.plan_job(p) for p in unfinished}
    inputs = sorted({x for _, j in jobs.values() for x in j.get("inputs", [])
                     if os.path.exists(os.path.join(ROOT, x))})        # runs not started yet have no folder
    code, bundle_id, n, mb = PJ.build_code(inputs)
    PJ.write_code_metadata(code, user)
    print(f"  one upload for {len(batch)} job(s): {n} files, {mb:.1f} MB (bundle {bundle_id})", flush=True)
    PJ.upload_code(code, user, f"queue: {len(batch)} jobs")
    done, refused = {}, False
    for p in batch:
        name, job = jobs[p]
        kern, kernel_id = PJ.build_kernel(name, job, user, bundle_id)
        ok, text = PJ.push_kernel(name, kern)
        if not ok:
            print(f"  {name}: Kaggle refused the push: {text[-300:]}", flush=True)
            refused = True
            break
        print(f"  {name}: pushed -> https://www.kaggle.com/code/{kernel_id}", flush=True)
        done[p] = kernel_id
    return done, refused


def push(p, user):          # one job alone (kept for tests and manual use)
    done, _ = push_batch([p], [p], user)
    return bool(done)


def PUSH(batch, unfinished, user):
    return push_batch(batch, unfinished, user)


def pull(name):
    return subprocess.run([sys.executable, os.path.join(HERE, "pull_job.py"), name], cwd=ROOT).returncode


def main(argv=None):
    try:
        return _main(argv)
    except KeyboardInterrupt:
        print("\nStopped. Jobs already on Kaggle keep running; run the same command again to pick up where it was "
              "(their results are pulled when they end).")
        return 130


def _main(argv=None):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("plans", nargs="*", help="plan files (wildcards allowed)")
    ap.add_argument("--parallel", default="auto",
                    help="Kaggle jobs at the same time: a number, or auto (default): Kaggle's published limit of "
                         f"{KAGGLE_CPU_SESSIONS} CPU sessions, lowered if Kaggle refuses")
    ap.add_argument("--parallel-gpu", default="auto",
                    help=f"GPU jobs at the same time: a number, or auto (default: {KAGGLE_GPU_SESSIONS}, lowered if "
                         "Kaggle refuses)")
    ap.add_argument("--max-pushes", type=int, default=4, help="pushes per job before it is given up (default 4)")
    ap.add_argument("--poll", type=int, default=180, help="seconds between checks (default 180)")
    ap.add_argument("--user")
    ap.add_argument("--status", action="store_true", help="print progress and stop")
    ap.add_argument("--retry", action="store_true", help="give jobs that were given up a fresh set of pushes")
    a = ap.parse_args(argv)
    st = load_state()
    plans = []
    for pat in a.plans or sorted(st):
        for p in sorted(glob.glob(pat)) or [pat]:
            p = os.path.abspath(p)
            if os.path.exists(p) and p not in plans:
                plans.append(p)
    if not plans:
        raise SystemExit("no plan files given (and none remembered in kaggle/_queue/state.json)")
    for p in plans:
        st.setdefault(p, {"state": "waiting", "pushes": 0})
        if a.retry and st[p]["state"] == "given up":
            st[p].update(state="waiting", pushes=0)
        if st[p]["state"] == "finished" and not finished(p):           # marked finished by mistake earlier
            st[p]["state"] = "waiting"
    if a.status:
        show(plans, st)
        return 0
    save_state(st)
    caps = {}                                   # kind -> (Kaggle's limit as seen, when)
    while True:
        import pull_job  # noqa: F401  (fails early if the Kaggle tool is missing)
        running = [p for p in plans if st[p]["state"] == "running"]
        for p in running:
            s = kernel_status(st[p]["kernel"])
            if s not in ENDED:
                continue
            print(f"\n== {job_name(p)} ended ({s}); pulling its results", flush=True)
            rc = pull(job_name(p))
            if rc == 2:                 # Kaggle still serves the previous run's output: look again next time
                print(f"   {job_name(p)}: the new output is not served yet; checking again at the next poll", flush=True)
                continue
            quick = time.time() - st[p].get("pushed_at", 0) < 600
            if s == "error" and quick and not os.path.exists(os.path.join(HERE, "_pulled", job_name(p), "status.json")):
                st[p].update(state="waiting", pushes=st[p]["pushes"] - 1)      # never started: not a real try
                caps[kind(p)] = (max(1, len([q for q in plans if st[q]["state"] == "running" and kind(q) == kind(p)])),
                                 time.time())
                print(f"   {job_name(p)} did not start (Kaggle session limit?); it waits for a free slot", flush=True)
                save_state(st)
                continue
            if finished(p):
                st[p]["state"] = "finished"
            elif st[p]["pushes"] >= a.max_pushes:
                st[p]["state"] = "given up"
                print(f"   {job_name(p)}: still unfinished after {st[p]['pushes']} pushes; given up. See "
                      f"kaggle\\_pulled\\{job_name(p)}\\job_log.txt", flush=True)
            else:
                st[p]["state"] = "waiting"          # pushed again below; run_plan resumes
            save_state(st)
        for p in plans:
            if st[p]["state"] == "waiting" and finished(p):
                st[p]["state"] = "finished"
        for k in ("cpu", "gpu"):
            running = [p for p in plans if st[p]["state"] == "running" and kind(p) == k]
            waiting = [p for p in plans if st[p]["state"] == "waiting" and kind(p) == k]
            if not waiting:
                continue
            if k in caps and time.time() - caps[k][1] > 1800:
                del caps[k]                                  # probe Kaggle's limit again
            want = a.parallel if k == "cpu" else a.parallel_gpu
            limit = caps[k][0] if k in caps else (KAGGLE_CPU_SESSIONS if k == "cpu" else KAGGLE_GPU_SESSIONS)
            if want != "auto":
                limit = min(limit, int(want)) if k in caps else int(want)
            batch = waiting[:max(0, limit - len(running))]
            if not batch:
                continue
            print(f"\n== pushing {len(batch)} {k.upper()} job(s): {', '.join(job_name(p) for p in batch)}", flush=True)
            unfinished = [p for p in plans if st[p]["state"] in ("waiting", "running")]
            try:
                pushed, refused = PUSH(batch, unfinished, a.user)
            except SystemExit as e:
                print(f"   upload failed ({e}); trying again at the next check", flush=True)
                pushed, refused = {}, False
            for p, kid in pushed.items():
                st[p].update(state="running", kernel=kid, pushes=st[p]["pushes"] + 1, pushed_at=time.time())
            if refused:
                caps[k] = (max(1, len(running) + len(pushed)), time.time())
                print(f"   Kaggle's {k.upper()} limit now looks like {caps[k][0]} job(s) at once; the rest wait",
                      flush=True)
            save_state(st)
        show(plans, st)
        if all(st[p]["state"] in ("finished", "given up") for p in plans):
            left = [p for p in plans if st[p]["state"] == "given up"]
            print("\nAll jobs ended." + (f" {len(left)} given up: " + ", ".join(map(os.path.basename, left))
                                         if left else " Every run finished."))
            return 1 if left else 0
        time.sleep(a.poll)


if __name__ == "__main__":
    sys.exit(main())
