"""Run Kaggle jobs in the right order - one command instead of push / wait / push.

    python kaggle/run.py --user YOURNAME k03 k04 k60          # these jobs (+ any unfinished inputs)
    python kaggle/run.py --user YOURNAME --phase expansion    # a named group, see PHASES
    python kaggle/run.py --user YOURNAME k60 --rerun          # run again even if it already completed
    python kaggle/run.py --user YOURNAME --status             # just show the status of every job

What it does, every minute until everything has finished:
  * a job is pushed only when every job it reads from has COMPLETED (otherwise Kaggle would start it
    without that input - the "not valid kernel sources" warning);
  * at most 5 CPU and 2 GPU jobs run at once (Kaggle's limits); when Kaggle still refuses, it waits;
  * jobs that already completed are skipped (use --rerun to repeat them); failed jobs are pushed again;
  * when a job fails, the end of its log is printed, and every job depending on it is skipped;
  * at the end it downloads the results of the completed jobs into out/<job> (like fetch.py).
Ctrl-C only stops watching: jobs keep running on Kaggle. Run the same command again to continue.
Run make_kernels.py first (it writes the job folders this script pushes).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_kernels import EXTRA, KERNELS, slug  # noqa: E402

GPU = {s: g for s, _, g, *_ in KERNELS}
TITLE = {s: t for s, t, *_ in KERNELS}
BASE = {s: (["k00"] if k00 else []) + (["k01"] if k01 else []) for s, _, _, k00, k01, _ in KERNELS}
AFTER = {"k90": ["k89"], "k91": ["k89"], "k92": ["k89"], "k93": ["k89"]}   # smoke test first
PHASES = {
    "inputs": ["k03", "k04"],
    "expansion": ["k60", "k44a", "k44b", "k23", "k43", "k51", "k33", "k70a", "k70b", "k71a", "k71b", "k80"],
    "trained": ["k89", "k90", "k91", "k92", "k93", "k95a", "k95b", "k95c", "k52"],
    "yalcin": ["k93", "k96a", "k96b", "k96c", "k53"],
}
TRAIN_JOB = {"chiu2020": "k90", "clep_gan": "k91", "p2e_wgan": "k92", "yalcin2026": "k93"}
# soft inputs: the job waits until they have ended, and runs if at least ONE of them completed
SOFT = {j: set(TRAIN_JOB.values()) for j in ("k95a", "k95b", "k95c", "k52")}
LIMIT = {False: 5, True: 2}
HEARTBEAT = 600   # seconds between "still running" lines


def deps(job):
    return BASE.get(job, []) + EXTRA.get(job, []) + AFTER.get(job, [])


def smoke_failures(user):
    """After k89: which models failed their smoke test (read from its smoke_status.json)."""
    dest = Path("out") / "k89"
    kaggle("kernels", "output", f"{user}/{slug(TITLE['k89'])}", "-p", str(dest), "-o",
           "--file-pattern", r"smoke_status\.json$")
    f = dest / "smoke_status.json"
    if not f.exists():
        return {}
    return {m: v for m, v in json.loads(f.read_text()).items() if v != "ok"}


def kaggle(*args):
    try:
        r = subprocess.run(["kaggle", *args], capture_output=True, text=True, timeout=180)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, "timeout talking to Kaggle"


def status(user, job):
    code, out = kaggle("kernels", "status", f"{user}/{slug(TITLE[job])}")
    low = out.lower()
    if code != 0:
        return "missing" if ("404" in low or "not found" in low) else "unknown"
    for key in ("complete", "error", "cancel", "running", "queued"):
        if key in low:
            return {"cancel": "error"}.get(key, key)
    return "unknown"


def log_tail(user, job, n=40):
    dest = Path("out") / job
    kaggle("kernels", "output", f"{user}/{slug(TITLE[job])}", "-p", str(dest), "-o", "--file-pattern", r".*\.log$")
    logs = sorted(dest.glob("*.log"))
    if not logs:
        return "(no log available - the job may not have started; open it on kaggle.com)"
    text = logs[0].read_text(errors="replace")
    try:
        text = "".join(e.get("data", "") for e in json.loads(text))
    except (ValueError, AttributeError):
        pass
    return "\n".join(text.strip().splitlines()[-n:])


def push(job):
    folder = HERE / "kernels" / slug(TITLE[job])
    if not folder.exists():
        return "nofolder", f"{folder} does not exist - run make_kernels.py first"
    code, out = kaggle("kernels", "push", "-p", str(folder))
    if "maximum batch" in out.lower() or "session count" in out.lower():
        return "busy", out
    if code != 0:
        return "failed", out
    if "not valid kernel sources" in out.lower():
        return "warn", out
    return "ok", out


def stamp():
    return time.strftime("%H:%M:%S")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("jobs", nargs="*")
    ap.add_argument("--phase", choices=sorted(PHASES))
    ap.add_argument("--rerun", action="store_true", help="push the named jobs even if they already completed")
    ap.add_argument("--status", action="store_true", help="only print the status of every job")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--every", type=int, default=60)
    a = ap.parse_args()

    if a.status:
        for s, *_ in KERNELS:
            print(f"{s:5s} {status(a.user, s):9s} {TITLE[s]}")
        return
    # the classic failure: job folders / uploaded code / local code out of step -> every job dies in 1 s
    from codehash import code_hash
    local = code_hash()
    pushed = (HERE / ".pushed_hash").read_text().strip() if (HERE / ".pushed_hash").exists() else None
    expected = (HERE / "kernels" / "EXPECTED_HASH").read_text().strip() if (HERE / "kernels" / "EXPECTED_HASH").exists() else None
    problems = []
    if pushed != local:
        problems.append(f"your code (version {local}) has not been uploaded"
                        + (f" (last upload: {pushed})" if pushed else "") + " -> python kaggle/push_code.py YOURNAME \"update\"")
    if expected != local:
        problems.append("the job folders were made for another code version -> python kaggle/make_kernels.py ... (README section 2)")
    if problems:
        ap.error("not starting anything:\n  - " + "\n  - ".join(problems))
    code, out = kaggle("datasets", "status", f"{a.user}/ppg2ecg-bench-code")
    if "ready" not in out.lower():
        ap.error(f"the uploaded code is not ready on Kaggle yet ({out.strip()}); wait a minute and try again")

    want = list(dict.fromkeys(a.jobs + (PHASES[a.phase] if a.phase else [])))
    unknown = [j for j in want if j not in TITLE]
    if unknown or not want:
        ap.error(f"unknown or no jobs: {unknown}. Known: {', '.join(TITLE)}")

    # add unfinished inputs automatically
    st, plan, queue = {}, [], list(want)
    while queue:
        j = queue.pop(0)
        if j in plan:
            continue
        st[j] = status(a.user, j)
        if j in want or st[j] != "complete":
            plan.append(j)
            queue += [d for d in deps(j) if d not in plan]
    added = [j for j in plan if j not in want]
    if added:
        print(f"{stamp()}  not finished yet, added to this run: {added}")
    todo = {j for j in plan if (a.rerun and j in want) or st[j] != "complete"}
    running = {j for j in plan if st[j] in ("running", "queued") and j in todo}
    pushed_by_us = set(running)
    since = {j: time.time() for j in running}          # when we started watching / pushed each job
    last_beat = time.time()
    done = {j for j in st if j not in todo and st[j] == "complete"}   # incl. inputs finished in earlier runs
    failed, skipped = {}, {}
    if "k89" in done and any(t in todo for t in TRAIN_JOB.values()):   # smoke test passed in an earlier run
        for model, why in smoke_failures(a.user).items():
            t = TRAIN_JOB.get(model)
            if t in todo and t not in running and not (a.rerun and t in want):
                skipped[t] = ["k89"]
                print(f"{stamp()}  {t} skipped: the smoke test of {model} failed (re-run k89 after a fix):\n{why}")
    print(f"{stamp()}  plan: " + ", ".join(f"{j}({'done' if j in done else st[j]})" for j in plan))

    try:
        while todo - set(failed) - set(skipped) - done:
            # 1) update running jobs
            for j in sorted(running):
                s = status(a.user, j)
                if s == "complete":
                    running.discard(j), done.add(j)
                    print(f"{stamp()}  {j} COMPLETE")
                    if j == "k89":
                        for model, why in smoke_failures(a.user).items():
                            t = TRAIN_JOB.get(model)
                            if t in todo and t not in done | running:
                                skipped[t] = ["k89"]
                                print(f"{stamp()}  {t} skipped: the smoke test of {model} failed:\n{why}")
                elif s == "error":
                    running.discard(j)
                    failed[j] = log_tail(a.user, j)
                    print(f"{stamp()}  {j} FAILED - last lines of its log:\n{'-' * 70}\n{failed[j]}\n{'-' * 70}")
            # 2) skip jobs whose inputs failed
            for j in sorted(todo - done - running - set(failed) - set(skipped)):
                ended = set(failed) | set(skipped)
                bad = [d for d in deps(j) if d in ended and d not in SOFT.get(j, ())]
                soft = [d for d in deps(j) if d in SOFT.get(j, ())]
                if soft and all(d in ended for d in soft):
                    bad += soft
                if bad:
                    skipped[j] = bad
                    print(f"{stamp()}  {j} skipped: its input {bad} failed")
            # 3) push what is ready, within the CPU/GPU limits
            for j in [x for x in plan if x in todo and x not in done | running | set(failed) | set(skipped)]:
                ended = done | set(failed) | set(skipped)
                if not all(d in done or (d in SOFT.get(j, ()) and d in ended) for d in deps(j)):
                    continue
                if sum(1 for r in running if GPU[r] == GPU[j]) >= LIMIT[GPU[j]]:
                    continue
                res, out = push(j)
                if res in ("ok", "warn"):
                    running.add(j), pushed_by_us.add(j)
                    since[j] = time.time()
                    print(f"{stamp()}  {j} pushed ({'GPU' if GPU[j] else 'CPU'})")
                    if res == "warn":
                        print(f"           WARNING from Kaggle: {out.splitlines()[0]}")
                elif res == "busy":
                    print(f"{stamp()}  {j} waiting: Kaggle's {'GPU' if GPU[j] else 'CPU'} job limit is reached "
                          f"(other jobs of yours may be running)")
                    break
                else:
                    failed[j] = out
                    print(f"{stamp()}  {j} could not be pushed: {out}")
            if todo - set(failed) - set(skipped) - done:
                if time.time() - last_beat >= HEARTBEAT:      # heartbeat: silence must never look like a hang
                    last_beat = time.time()
                    run_txt = ", ".join(f"{j} ({(time.time() - since.get(j, time.time())) / 60:.0f} min)"
                                        for j in sorted(running)) or "none"
                    waiting = sorted(todo - done - running - set(failed) - set(skipped))
                    why = []
                    for j in waiting:
                        need = [d for d in deps(j) if d not in done]
                        why.append(f"{j} (needs {','.join(need)})" if need else
                                   f"{j} ({'GPU' if GPU[j] else 'CPU'} limit)")
                    print(f"{stamp()}  still running: {run_txt}" + (f" | waiting: {', '.join(why)}" if why else ""),
                          flush=True)
                time.sleep(a.every)
    except KeyboardInterrupt:
        print("\nStopped watching. Jobs that were pushed keep running on Kaggle; run the same command again "
              "to continue (finished jobs are skipped).")
        return

    print(f"\n{stamp()}  finished.  completed: {sorted(done & set(plan))}")
    if failed:
        print(f"  FAILED: {sorted(failed)}  (their logs were printed above and saved in out/<job>/)")
    if skipped:
        print(f"  skipped because an input failed: {sorted(skipped)}")
    to_fetch = sorted((done & pushed_by_us) | (done & set(want)))
    if to_fetch and not a.no_fetch:
        print(f"{stamp()}  downloading results of {to_fetch} into out/ ...")
        subprocess.run([sys.executable, str(HERE / "fetch.py"), "--user", a.user, *to_fetch])
    sys.exit(1 if failed or skipped else 0)


if __name__ == "__main__":
    main()
