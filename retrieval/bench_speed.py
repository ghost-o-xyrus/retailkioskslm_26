"""
Objective 3, Step 12c: retrieval speed and RAM on dev, each configuration in its own fresh process (so RAM and the
PyTorch import are measured honestly). On the laptop; about 10-15 minutes. Close other apps.

    python retrieval\\bench_speed.py
    python retrieval\\bench_speed.py --fake          # code-path test, no models

Configurations (re-rank depth stays 20: Step 9 showed depth 10 costs 5.6-7.2 points of Recall@3):
    base                       deployed: bge-small on PyTorch + MiniLM on OpenVINO (sentence-transformers), 256 tokens
    rt-fp32-l256-full          both models on the OpenVINO runtime, no PyTorch
    rt-fp32-l128-compact       + the re-ranker reads the card without its description, 128 tokens
    rt-int8-l256-full          + the 8-bit re-ranker
    rt-int8-l128-compact       + both
each at 4 and 8 threads (retrieval runs before the language model starts, so it can use more cores).
Measured per configuration: dev Recall@3 (and Hinglish), wait p50/p95 over 60 dev questions after a warm-up
(the whole KnowledgeBase.retrieve call), RAM added by loading the retrieval stack, whether torch was imported.

Rule (written in the plan before the run): a configuration qualifies if its dev Recall@3 is at most 1 point below
base. Among qualifiers the lowest p50 wins; within 5% of the best p50, the lower RAM wins. Targets reported, not
used to choose: p50 <= 300 ms, added RAM <= 0.8 GB. Dev only. Writes results_obj3/_speed_step12/{report.md,
summary.json, ranks/<config>.jsonl} and choice.json (for run_eval --reranker-choice and calibrate_step9.py).
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
OUT = os.path.join(ROOT, "results_obj3", "_speed_step12")
CONFIGS = {
    "base": dict(backend="openvino", int8=False, max_length=256, rerank_view="full"),
    "rt-fp32-l256-full": dict(backend="ovrt", int8=False, max_length=256, rerank_view="full"),
    "rt-fp32-l128-compact": dict(backend="ovrt", int8=False, max_length=128, rerank_view="compact"),
    "rt-int8-l256-full": dict(backend="ovrt", int8=True, max_length=256, rerank_view="full"),
    "rt-int8-l128-compact": dict(backend="ovrt", int8=True, max_length=128, rerank_view="compact"),
    # second 8-bit try (retrieval/quantize_reranker.py, NNCF): static with in-domain calibration, and weights only
    "rt-int8s-l256-full": dict(backend="ovrt", int8="static", max_length=256, rerank_view="full"),
    "rt-int8w-l256-full": dict(backend="ovrt", int8="weights", max_length=256, rerank_view="full"),
}
THREADS = (4, 8)
MAX_DROP_PTS = 1.0
P50_TIE = 0.05


def rss_mb():
    try:
        import psutil
        return psutil.Process().memory_info().rss / 1e6
    except Exception:  # noqa: BLE001
        return None


def worker(name, threads, fake, out_dir, fb=None):
    """Runs in a fresh process: load, score dev, time 60 questions, report."""
    sys.path.insert(0, HERE)
    r0 = rss_mb()
    t0 = time.time()
    from knowledge_base import KnowledgeBase
    import bench_retrieval as B
    cfg = dict(CONFIGS[name])
    fb = fb or os.path.join(ROOT, "results_obj3", "_tau_step8", "fallback.json")
    if not os.path.exists(fb):
        fb = os.path.join(ROOT, "results_retrieval", "fallback_bypass", "fallback.json")
    kb = KnowledgeBase(fallback_path=fb, depth=20, threads=threads, fake=fake, k=3, **cfg)
    load_s, r1 = time.time() - t0, rss_mb()
    dev = [it for it in B.load_jsonl(os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl")) if it["split"] == "dev"]
    ranks = {}
    for it in dev:
        ranks[it["id"]] = kb.retrieve(it["query"])["top10"]
    gold = [it for it in dev if it["gold_ids"]]
    hit = lambda it, k: int(bool(set(it["gold_ids"]) & {c for c, _ in ranks[it["id"]][:k]}))   # noqa: E731
    hi = [it for it in gold if it["language"] == "hinglish"]
    sample = random.Random(11).sample(dev, min(60, len(dev)))
    kb.retrieve(sample[0]["query"])                         # warm-up
    lat = []
    for it in sample:
        t = time.perf_counter()
        kb.retrieve(it["query"])
        lat.append((time.perf_counter() - t) * 1000)
    key = f"{name}-t{threads}"
    os.makedirs(os.path.join(out_dir, "ranks"), exist_ok=True)
    with open(os.path.join(out_dir, "ranks", key + ".jsonl"), "w", encoding="utf-8") as f:
        for it in dev:
            f.write(json.dumps({"id": it["id"], "top": ranks[it["id"]]}) + "\n")
    lat.sort()
    res = dict(config=key, name=name, threads=threads, **cfg, r3=sum(hit(it, 3) for it in gold) / len(gold),
               r1=sum(hit(it, 1) for it in gold) / len(gold), r5=sum(hit(it, 5) for it in gold) / len(gold),
               r3_hinglish=sum(hit(it, 3) for it in hi) / max(1, len(hi)), p50_ms=round(statistics.median(lat), 1),
               p95_ms=round(lat[int(0.95 * (len(lat) - 1))], 1), load_s=round(load_s, 1),
               added_ram_mb=round(r1 - r0) if r0 is not None and r1 is not None else None,
               torch_imported="torch" in sys.modules, hits3=[hit(it, 3) for it in gold])
    print("RESULT " + json.dumps(res))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--configs", default=",".join(CONFIGS))
    ap.add_argument("--threads", default=",".join(map(str, THREADS)))
    ap.add_argument("--worker", default=None)
    ap.add_argument("--worker-threads", type=int, default=4)
    ap.add_argument("--fallback", default=None, help="fallback.json (default: the Step 8 one)")
    ap.add_argument("--merge", action="store_true",
                    help="add these configurations to the earlier summary.json instead of starting over")
    a = ap.parse_args(argv)
    if a.worker:
        worker(a.worker, a.worker_threads, a.fake, a.out, a.fallback)
        return 0
    sys.path.insert(0, ROOT)
    from harness.machine import machine_info
    sys.path.insert(0, HERE)
    import bench_retrieval as B
    os.makedirs(a.out, exist_ok=True)
    rows, skipped = [], {}
    for name in a.configs.split(","):
        for th in [int(x) for x in a.threads.split(",")]:
            cmd = [sys.executable, os.path.abspath(__file__), "--worker", name, "--worker-threads", str(th), "--out", a.out]
            if a.fake:
                cmd.append("--fake")
            if a.fallback:
                cmd += ["--fallback", a.fallback]
            print(f"== {name} at {th} threads ...", flush=True)
            env = dict(os.environ, OMP_NUM_THREADS=str(th))
            r = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
            line = next((x for x in (r.stdout or "").splitlines() if x.startswith("RESULT ")), None)
            if r.returncode != 0 or not line:
                skipped[f"{name}-t{th}"] = ((r.stderr or r.stdout or "").strip().splitlines() or ["no output"])[-1][:300]
                print(f"   SKIPPED: {skipped[f'{name}-t{th}']}", flush=True)
                continue
            rows.append(json.loads(line[7:]))
            x = rows[-1]
            print(f"   R@3 {x['r3']:.1%}, p50 {x['p50_ms']} ms, +{x['added_ram_mb']} MB, torch {x['torch_imported']}", flush=True)
    prev_path = os.path.join(a.out, "summary.json")
    if a.merge and os.path.exists(prev_path):     # keep the configurations measured in an earlier run
        with open(prev_path, encoding="utf-8") as f:
            done = {r["config"] for r in rows}
            rows = [r for r in json.load(f)["rows"] if r["config"] not in done] + rows
    base = next((r for r in rows if r["name"] == "base" and r["threads"] == 4), None)
    if base is None:
        print("The base configuration could not be run; nothing decided.", file=sys.stderr)
        return 2
    for r in rows:
        d, lo, hi = B.paired_bootstrap(r["hits3"], base["hits3"])
        r["r3_diff_pts"], r["r3_ci"] = 100 * d, [100 * lo, 100 * hi]
        r["qualifies"] = 100 * (r["r3"] - base["r3"]) >= -MAX_DROP_PTS
    q = [r for r in rows if r["qualifies"]]
    best = min(r["p50_ms"] for r in q)
    near = [r for r in q if r["p50_ms"] <= best * (1 + P50_TIE)]
    choice = min(near, key=lambda r: (r["added_ram_mb"] if r["added_ram_mb"] is not None else 1e9, r["p50_ms"]))
    mach = machine_info()
    L = ["# Step 12: retrieval speed and RAM (dev)", "",
         f"Machine: {mach['label']} ({mach['cpu']}, {mach['cores']} logical cores). Each configuration ran in a fresh "
         "process; wait = the whole retrieval call over 60 dev questions after a warm-up. Re-rank depth 20.", "",
         f"Rule: Recall@3 at most {MAX_DROP_PTS:g} point below base (4 threads); lowest p50; within {P50_TIE:.0%} of "
         "the best p50, lower RAM. Targets (reported): p50 <= 300 ms, added RAM <= 800 MB.", "",
         "| Config | R@1 | R@3 | R@3 − base [95% CI] | R@5 | R@3 Hinglish | p50 ms | p95 ms | Added RAM MB | Load s | PyTorch | Qualifies |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['config']} | {r['r1']:.1%} | {r['r3']:.1%} | {r['r3_diff_pts']:+.1f} [{r['r3_ci'][0]:+.1f}, "
                 f"{r['r3_ci'][1]:+.1f}] | {r['r5']:.1%} | {r['r3_hinglish']:.1%} | {r['p50_ms']} | {r['p95_ms']} "
                 f"| {r['added_ram_mb']} | {r['load_s']} | {'yes' if r['torch_imported'] else 'no'} "
                 f"| {'yes' if r['qualifies'] else 'no'} |")
    for k, v in skipped.items():
        L.append(f"\nSkipped {k}: {v}")
    L += ["", f"**Chosen: {choice['config']}** (p50 {choice['p50_ms']} ms: target {'met' if choice['p50_ms'] <= 300 else 'missed'}; "
              f"added RAM {choice['added_ram_mb']} MB: target {'met' if (choice['added_ram_mb'] or 1e9) <= 800 else 'missed'})."]
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "skipped": skipped, "choice": choice["config"], "machine": mach}, f, indent=1)
    with open(os.path.join(a.out, "choice.json"), "w", encoding="utf-8") as f:
        json.dump({"config": choice["config"], "backend": choice["backend"], "int8": choice["int8"],
                   "max_length": choice["max_length"], "rerank_view": choice["rerank_view"], "threads": choice["threads"],
                   "depth": 20, "ranks": os.path.relpath(os.path.join(a.out, "ranks", choice["config"] + ".jsonl"), ROOT)},
                  f, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
