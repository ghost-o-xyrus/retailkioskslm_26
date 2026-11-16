"""
Objective 5, Step 8: in-place measurement of the deployed setup, through the app and through the harness.

For one tier and stage policy, this starts the app (Lab mode, the tier's Deployed setup), waits until it has loaded,
then runs the speed subset through the app's API (as the browser does: server-sent events, streamed reply) and through
the harness engine in this process (the same engine, configuration and llama-server, called directly), alternating
case by case (app then harness, then harness then app). It records per-stage time, first word, total, writing speed
and peak RAM, and the app's overhead against the harness.

Rules (fixed before the run):
  - App overhead: median total through the app within 5% of the harness (paired); first word at most 0.3 s later.
  - RAM: Tier A peak, model server plus app, at most 5 GB; Tier B reported against its Objective 2 measurement.
  - Tier A policy: the policy with the lower median total, if its peak stays within 5 GB; otherwise the one that fits.
The numbers reported for the write-up come from one run on the O3-T speed subset with the chosen policy.

    python app\\measure.py --tier A --policy resident   --subset dev      # about 30-40 min
    python app\\measure.py --tier A --policy sequential --subset dev
    python app\\measure.py --choose                                          # applies the policy rule (Tier A)
    python app\\measure.py --tier A --policy <chosen>   --subset test --repeats 1
    python app\\measure.py --tier B --policy resident   --subset dev
    python app\\measure.py --tier B --policy resident   --subset test --repeats 1
    python app\\measure.py --report                                          # the summary of every run

Stop any llama-server and any running app first; this script starts and stops its own.
Writes results_obj5/_measure_step8/<tier>_<policy>_<subset>.json and report.md.
"""
import argparse
import json
import os
import random
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from smoke_real import get, post  # noqa: E402

OUT = os.path.join(ROOT, "results_obj5", "_measure_step8")
SUBSETS = {"dev": ("eval/o3_dev_speed_ids.json", "eval/rag_cases.jsonl", "eval/eval_set_v1.2.jsonl"),
           "test": ("eval/o3t_speed_ids.json", "eval/rag_cases_o3t.jsonl", "eval/eval_set_o3t.jsonl")}
BUDGET_MB = {"A": 5 * 1024, "B": 10 * 1024}


def load_cases(subset):
    ids_f, rag_f, tool_f = SUBSETS[subset]
    ids = json.load(open(os.path.join(ROOT, ids_f), encoding="utf-8"))
    out = []
    for f, want, kind in ((rag_f, set(ids["rag_ids"]), "store"), (tool_f, set(ids["v11_ids"]), "tools")):
        with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
            for line in fh:
                c = json.loads(line)
                if c["id"] in want and len(c["messages"]) == 1:
                    out.append((c["id"], c["messages"][0]["content"], kind))
    return out


def app_turn(base, sel, message):
    s = post(base, "/api/sessions", {"selection": sel})
    t0 = time.time()
    r = post(base, f"/api/sessions/{s['id']}/turns", {"message": message}, stream=True)
    first, end = None, None
    for raw in r:
        line = raw.decode("utf-8").strip()
        if not line.startswith("data:"):
            continue
        ev = json.loads(line[5:])
        t = (time.time() - t0) * 1000
        if ev.get("type") in ("token", "final") and first is None:
            first = t
        if ev.get("type") == "turn_end":
            end = ev
        if ev.get("type") == "done":
            total = t
            break
    if not end:
        return {"error": "no turn_end"}
    tr = get(base, f"/api/turns/{end['turn_id']}/trace")
    return {"first_ms": first, "total_ms": total, "trace": tr}


def peak_mb(tr):
    best = 0
    for st in tr.get("stages") or []:
        p = st.get("peak_mb") or {}
        if isinstance(p, dict):
            best = max(best, sum(v for v in p.values() if isinstance(v, (int, float))))
    return best or None


def harness_turn(engine, message):
    from kiosk_core.turn import Session, run_turn
    first = []
    t0 = time.time()

    def emit(ev):
        if ev.get("type") in ("token", "final") and not first:
            first.append((time.time() - t0) * 1000)
    rec = run_turn(Session(), message, engine, emit=emit, stream=True)
    return {"first_ms": first[0] if first else None, "total_ms": (time.time() - t0) * 1000, "rec": rec}


def start_app(tier, policy, port, llama_port, base_dir, fake=False):
    cmd = [sys.executable, os.path.join(HERE, "server.py"), "--mode", "lab", "--tier", tier, "--port", str(port),
           "--llama-port", str(llama_port), "--stage-policy", policy] + (["--fake"] if fake else [])
    if base_dir:
        cmd += ["--base-dir", base_dir]
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, f"app_{tier}_{policy}.log"), "a", encoding="utf-8")
    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
    base = f"http://127.0.0.1:{port}"
    t = time.time()
    while time.time() - t < 900:
        if proc.poll() is not None:
            sys.exit(f"the app stopped; see {log.name}")
        try:
            r = get(base, "/api/ready")
            if r.get("state") == "ready":
                return proc, base, r
            if r.get("state") == "error":
                stop_app(proc)
                sys.exit(r.get("text"))
        except Exception:  # noqa: BLE001 - not up yet
            pass
        time.sleep(2)
    stop_app(proc)
    sys.exit("the app did not become ready in 15 minutes")


def stop_app(proc):
    """Stop the app and the llama-server it started (a plain terminate would leave llama-server holding the port)."""
    try:
        import psutil
        kids = psutil.Process(proc.pid).children(recursive=True)
    except Exception:  # noqa: BLE001
        kids = []
    for k in kids:
        try:
            k.terminate()
        except Exception:  # noqa: BLE001
            pass
    proc.terminate()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
    for k in kids:
        try:
            k.wait(timeout=15)
        except Exception:  # noqa: BLE001
            try:
                k.kill()
            except Exception:  # noqa: BLE001
                pass


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else None


def boot_ci(diffs, n=2000, seed=8):
    rng = random.Random(seed)
    d = [x for x in diffs if x is not None]
    if not d:
        return None, None
    ms = sorted(statistics.median(rng.choices(d, k=len(d))) for _ in range(n))
    return ms[int(.025 * n)], ms[int(.975 * n)]


def run(a):
    from tools import mock_tools  # noqa: F401  (loads the catalogue before timing)
    from app.config import Registry
    from kiosk_core import engine as E
    from kiosk_core.turn import Engine
    from app.service import brand
    cases = load_cases(a.subset)
    proc, base, ready = start_app(a.tier, a.policy, a.port, a.llama_port, a.base_dir, a.fake)
    try:
        sel = {"tier": a.tier, "pipeline": "deployed"}
        mark = get(base, "/api/configs").get("brand")
        reg = Registry(base_dir=a.base_dir, fake=a.fake)
        cfg, server, sel_r, _ = reg.resolve(sel)
        if a.policy != "resident":
            cfg = dict(cfg, stage_policy=a.policy)
        eng = Engine.from_plan_run(cfg, base_url=f"http://127.0.0.1:{a.llama_port}",
                                   results_dir=os.path.join(ROOT, "results_obj5", "_app"))
        E.REQUEST_EXTRA.clear()
        if server.get("loras"):
            E.REQUEST_EXTRA["lora"] = [{"id": i, "scale": 1.0 if i == server.get("lora_index") else 0.0}
                                       for i in range(len(server["loras"]))]
        print(f"Tier {a.tier}, {a.policy}, {a.subset}: {len(cases)} cases x {a.repeats}; app ready in "
              f"{ready.get('load_s')} s ({cfg['config_label']})")
        rows = []
        for rep in range(a.repeats):
            for i, (cid, msg, kind) in enumerate(cases):
                order = ("app", "harness") if (i + rep) % 2 == 0 else ("harness", "app")
                got = {}
                for side in order:
                    if side == "app":
                        got["app"] = app_turn(base, sel, msg)
                    else:
                        got["harness"] = harness_turn(eng, msg)
                ap_, h = got["app"], got["harness"]
                tr = ap_.get("trace") or {}
                rows.append({"id": cid, "kind": kind, "repeat": rep, "order": order[0],
                             "app_first_ms": ap_.get("first_ms"), "app_total_ms": ap_.get("total_ms"),
                             "h_first_ms": h["first_ms"], "h_total_ms": h["total_ms"],
                             "same_reply": (tr.get("final_reply") or "") == brand(h["rec"].get("final_reply") or "", mark),
                             "by_stage_ms": (tr.get("stage_summary") or {}).get("by_stage_ms"),
                             "tokens_per_s": (tr.get("metrics") or {}).get("tokens_per_s"),
                             "peak_mb": peak_mb(tr), "error": ap_.get("error")})
                r = rows[-1]
                print(f"  [{rep}] {cid:12s} app {r['app_total_ms'] / 1000 if r['app_total_ms'] else 0:6.1f} s "
                      f"(first {(r['app_first_ms'] or 0) / 1000:5.1f})  harness {r['h_total_ms'] / 1000:6.1f} s "
                      f"(first {(r['h_first_ms'] or 0) / 1000:5.1f})", flush=True)
        try:
            status = get(base, "/api/stages/status")
        except Exception:  # noqa: BLE001
            status = {}
        eng.close()
    finally:
        stop_app(proc)
    out = {"tier": a.tier, "policy": a.policy, "subset": a.subset, "repeats": a.repeats,
           "label": cfg["config_label"], "load_s": ready.get("load_s"), "rows": rows, "status": status}
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{a.tier}_{a.policy}_{a.subset}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=str)
    print(f"Wrote {p}")
    report()


def summary(d):
    rows = [r for r in d["rows"] if not r.get("error")]
    per = {}
    for r in rows:                                   # per case: median over repeats
        per.setdefault(r["id"], []).append(r)
    def pcm(key):
        return [med([x[key] for x in v]) for v in per.values()]
    at, ht, af, hf = pcm("app_total_ms"), pcm("h_total_ms"), pcm("app_first_ms"), pcm("h_first_ms")
    dt = [x - y for x, y in zip(at, ht) if x is not None and y is not None]
    df = [x - y for x, y in zip(af, hf) if x is not None and y is not None]
    stages = {}
    for r in rows:
        for k, v in (r.get("by_stage_ms") or {}).items():
            stages.setdefault(k, []).append(v)
    peak = max([r["peak_mb"] or 0 for r in rows] or [0])
    s = {"cases": len(per), "turns": len(rows), "errors": len(d["rows"]) - len(rows),
         "app_total_p50": med(at), "app_total_p90": pct(at, .9), "app_first_p50": med(af), "app_first_p90": pct(af, .9),
         "h_total_p50": med(ht), "h_first_p50": med(hf),
         "overhead_total_ms": med(dt), "overhead_total_ci": boot_ci(dt),
         "overhead_pct": (100 * med(dt) / med(ht)) if dt and med(ht) else None,
         "overhead_first_ms": med(df), "overhead_first_ci": boot_ci(df),
         "tokens_per_s": med([r["tokens_per_s"] for r in rows]), "peak_mb": peak,
         "same_reply": sum(r["same_reply"] for r in rows), "stages_p50": {k: med(v) for k, v in stages.items()},
         "by_kind": {k: {"app_total_p50": med([med([x["app_total_ms"] for x in v]) for v in per.values()
                                               if v[0]["kind"] == k]),
                         "app_first_p50": med([med([x["app_first_ms"] for x in v]) for v in per.values()
                                               if v[0]["kind"] == k])} for k in ("store", "tools")}}
    s["overhead_ok"] = s["overhead_pct"] is not None and s["overhead_pct"] <= 5 and \
        (s["overhead_first_ms"] or 0) <= 300
    s["ram_ok"] = peak <= BUDGET_MB[d["tier"]] if peak else None
    return s


def choose():
    res = {}
    for pol in ("resident", "sequential"):
        p = os.path.join(OUT, f"A_{pol}_dev.json")
        if os.path.exists(p):
            res[pol] = summary(json.load(open(p, encoding="utf-8")))
    if len(res) < 2:
        sys.exit("run both policies on Tier A dev first")
    fits = {k: v for k, v in res.items() if v["ram_ok"]}
    pool = fits or res
    pick = min(pool, key=lambda k: pool[k]["app_total_p50"])
    why = ("lower median total and within 5 GB" if fits and len(fits) == 2 else
           "the only one within 5 GB" if fits else "neither fits 5 GB; lower median total")
    out = {"chosen": pick, "why": why, "resident": res["resident"], "sequential": res["sequential"]}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "policy.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"Tier A stage policy: {pick} ({why}). resident {res['resident']['app_total_p50'] / 1000:.2f} s, "
          f"peak {res['resident']['peak_mb'] / 1024:.2f} GB; sequential {res['sequential']['app_total_p50'] / 1000:.2f} s, "
          f"peak {res['sequential']['peak_mb'] / 1024:.2f} GB")
    report()
    return pick


def report():
    if not os.path.isdir(OUT):
        return
    L = ["# Objective 5, Step 8: in-place measurement (app and harness, same cases, alternating)", "",
         "Times in seconds, medians over cases (each case: median over repeats). Overhead: app minus harness, "
         "median of per-case differences [95% bootstrap interval].", "",
         "| Run | Cases | App total p50 / p90 | App first word p50 / p90 | Harness total / first | Overhead total "
         "(rule ≤5%) | Overhead first word (rule ≤0.3 s) | Writing tok/s | Peak RAM (budget) | Same reply |",
         "|---|---:|---|---|---|---|---|---:|---|---:|"]
    stage_lines = []
    for fn in sorted(os.listdir(OUT)):
        if not (fn.endswith(".json") and fn.count("_") == 2 and fn[0] in "AB"):
            continue
        d = json.load(open(os.path.join(OUT, fn), encoding="utf-8"))
        s = summary(d)
        f = lambda x: "–" if x is None else f"{x / 1000:.2f}"  # noqa: E731
        ci = s["overhead_total_ci"]
        cf = s["overhead_first_ci"]
        L.append(f"| {d['tier']} {d['policy']} {d['subset']} ×{d['repeats']} | {s['cases']} | "
                 f"{f(s['app_total_p50'])} / {f(s['app_total_p90'])} | {f(s['app_first_p50'])} / {f(s['app_first_p90'])} | "
                 f"{f(s['h_total_p50'])} / {f(s['h_first_p50'])} | "
                 f"{f(s['overhead_total_ms'])} s = {s['overhead_pct']:.1f}% [{f(ci[0])}, {f(ci[1])}] "
                 f"{'met' if s['overhead_pct'] is not None and s['overhead_pct'] <= 5 else 'NOT met'} | "
                 f"{f(s['overhead_first_ms'])} [{f(cf[0])}, {f(cf[1])}] "
                 f"{'met' if (s['overhead_first_ms'] or 0) <= 300 else 'NOT met'} | "
                 f"{s['tokens_per_s'] or '–'} | {s['peak_mb'] / 1024:.2f} GB ({BUDGET_MB[d['tier']] // 1024} GB) "
                 f"{'met' if s['ram_ok'] else 'NOT met' if s['ram_ok'] is False else ''} | "
                 f"{s['same_reply']}/{s['turns']} |")
        stage_lines.append(f"| {d['tier']} {d['policy']} {d['subset']} | " + " | ".join(
            f"{(s['stages_p50'].get(k) or 0):.0f}" for k in ("input", "route", "retrieval", "harness_tools",
                                                              "model_round", "model_tools", "checks", "output"))
            + f" | {f(s['by_kind']['store']['app_total_p50'])} / {f(s['by_kind']['tools']['app_total_p50'])} |")
    L += ["", "## Per stage (median ms per turn, through the app) and totals by kind", "",
          "| Run | input | route | retrieval | harness tools | model rounds | model tools | checks | output | "
          "total: store / tools (s) |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"] + stage_lines
    pp = os.path.join(OUT, "policy.json")
    if os.path.exists(pp):
        c = json.load(open(pp, encoding="utf-8"))
        L += ["", f"**Tier A stage policy: {c['chosen']}** ({c['why']})."]
    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["A", "B"])
    ap.add_argument("--policy", default="resident", choices=["resident", "sequential"])
    ap.add_argument("--subset", default="dev", choices=["dev", "test"])
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--llama-port", type=int, default=8080)
    ap.add_argument("--base-dir", default=None)
    ap.add_argument("--fake", action="store_true", help="stand-in model (tests the script only)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--limit", type=int, default=None, help="first N cases only (a quick check)")
    ap.add_argument("--choose", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)
    global OUT
    if a.out:
        OUT = a.out
    if a.choose:
        choose()
        return 0
    if a.report:
        report()
        return 0
    if not a.tier:
        sys.exit("--tier A or B")
    if a.limit:
        global load_cases
        _lc = load_cases
        load_cases = lambda s: _lc(s)[:a.limit]  # noqa: E731
    run(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
