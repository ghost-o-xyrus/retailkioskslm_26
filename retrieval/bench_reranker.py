"""
Objective 3, Step 9c: re-ranker trial on dev retrieval questions (no language model).

    python retrieval\\bench_reranker.py
    python retrieval\\bench_reranker.py --fake            # code-path test, no models

Candidates, each with the deployed first stage (BM25 + bge-small, fused, top 20), 256 tokens, OpenVINO:
    minilm          cross-encoder/ms-marco-MiniLM-L-6-v2 (deployed; depth 20 is the baseline)
    minilm-veyra    the same model fine-tuned on generated Veyra pairs (retrieval/finetune_reranker.py)
    mminilm-l12     cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 (small multilingual, not fine-tuned)
Each at re-rank depth 20 and 10. Latency: first stage + re-rank, on 60 fixed dev questions, after one warm-up.

Rule (written in the plan before the run): a configuration qualifies if its p50 is at most 300 ms AND either
dev Recall@3 is at least 2 points above the baseline, or Hinglish dev Recall@3 is at least 5 points above it with
overall Recall@3 not below the baseline. Among qualifiers: highest Recall@3, then lowest p50. Dev only; the test
split is not read. Bootstrap intervals are reported but are not part of the rule (the dev Hinglish set has only
14 answerable questions, so one question is 7 points).

Writes results_obj3/_rerank_step9/{report.md, summary.json, ranks/<config>.jsonl} and, if one qualifies,
choice.json for the knowledge base.

Latency belongs to the kiosk's machine. When this runs elsewhere (SLM_MACHINE=kaggle-..., set by the Kaggle runner),
recall is final but no choice is made: run it again on the laptop with --latency-only, which re-times every
configuration there (about 5 minutes, no full scoring), keeps the recall from summary.json and then applies the rule.
"""

import argparse
import gc
import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from retrievers import BM25Retriever, DenseRetriever, HybridRetriever, Reranker  # noqa: E402
import bench_retrieval as B  # noqa: E402
from bench_latency import load_cross_encoder  # noqa: E402
sys.path.insert(0, ROOT)
from harness.machine import machine_info  # noqa: E402

EMBEDDER = "BAAI/bge-small-en-v1.5"
CANDIDATES = {"minilm": "cross-encoder/ms-marco-MiniLM-L-6-v2",
              "minilm-veyra": os.path.join("models", "reranker-veyra-minilm"),
              "mminilm-l12": "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"}
DEPTHS = (20, 10)
BASELINE = ("minilm", 20)
MAX_P50_MS = 300
GAIN_ALL, GAIN_HI = 2.0, 5.0


def recall_hits(items, ranks, k):
    return {it["id"]: int(bool(set(it["gold_ids"]) & {c for c, _ in ranks[it["id"]][:k]})) for it in items}


def qualifies(row, base):
    if row["p50_ms"] is None or row["p50_ms"] > MAX_P50_MS:
        return False
    d_all = 100 * (row["r3"] - base["r3"])
    d_hi = 100 * (row["r3_hinglish"] - base["r3_hinglish"])
    return d_all >= GAIN_ALL or (d_hi >= GAIN_HI and d_all >= 0)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", default=",".join(CANDIDATES))
    ap.add_argument("--backend", default="openvino")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--latency-sample", type=int, default=60)
    ap.add_argument("--corpus", default=os.path.join(ROOT, "knowledge", "corpus.jsonl"))
    ap.add_argument("--eval", default=os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj3", "_rerank_step9"))
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--latency-only", action="store_true",
                    help="re-time the configurations in summary.json on this machine and apply the rule")
    a = ap.parse_args(argv)
    mach = machine_info()
    os.environ.setdefault("OMP_NUM_THREADS", str(a.threads))
    os.makedirs(os.path.join(a.out, "ranks"), exist_ok=True)
    chunks = B.load_jsonl(a.corpus)
    dev = [it for it in B.load_jsonl(a.eval) if it["split"] == "dev"]
    gold = [it for it in dev if it["gold_ids"]]
    hi = [it for it in gold if it["language"] == "hinglish"]
    en = [it for it in gold if it["language"] != "hinglish"]
    sample = random.Random(11).sample(dev, min(a.latency_sample, len(dev)))

    bm25 = BM25Retriever(chunks)
    dense = DenseRetriever(chunks, EMBEDDER, encoder=B.FakeEncoder() if a.fake else None)
    hybrid = HybridRetriever(bm25, dense)
    first = {it["id"]: hybrid.search(it["query"], max(DEPTHS)) for it in dev}
    first_lat = []
    for it in sample:
        t0 = time.perf_counter()
        hybrid.search(it["query"], max(DEPTHS))
        first_lat.append((time.perf_counter() - t0) * 1000)

    rows, skipped, hits3, prev = [], {}, {}, {}
    if a.latency_only:
        with open(os.path.join(a.out, "summary.json"), encoding="utf-8") as f:
            prev = {r["config"]: r for r in json.load(f)["rows"]}
    for name in a.candidates.split(","):
        if a.latency_only and not any(k.startswith(name + "-d") for k in prev):
            continue
        path = CANDIDATES[name]
        src = os.path.join(ROOT, path) if path.startswith("models") else path
        if path.startswith("models") and not os.path.isdir(src) and not a.fake:
            skipped[name] = f"{path} not found (run retrieval\\finetune_reranker.py first)"
            continue
        r0 = B.rss_mb()
        try:
            model = B.FakeCrossEncoder() if a.fake else load_cross_encoder(a.backend, 256, a.threads, a.out, model_name=src)
        except Exception as e:  # noqa: BLE001
            skipped[name] = f"{type(e).__name__}: {str(e)[:200]}"
            print(f"{name}: SKIPPED ({skipped[name]})", flush=True)
            continue
        ram = round(B.rss_mb() - r0) if r0 is not None else None
        rr = Reranker(chunks, name, model=model)
        rr.rerank(sample[0]["query"], first[sample[0]["id"]][:max(DEPTHS)])   # warm-up
        for depth in DEPTHS:
            if a.latency_only:
                key = f"{name}-d{depth}"
                row = prev.get(key)
                if row is None:
                    continue
                fresh = Reranker(chunks, name, model=model)
                lat = []
                for j, it in enumerate(sample):
                    t0 = time.perf_counter()
                    fresh.rerank(it["query"], first[it["id"]][:depth])
                    lat.append((time.perf_counter() - t0) * 1000 + first_lat[j])
                row = dict(row, p50_ms=round(statistics.median(lat), 1),
                           p95_ms=round(sorted(lat)[int(0.95 * (len(lat) - 1))], 1), added_ram_mb=ram,
                           latency_machine=mach["label"])
                rows.append(row)
                hits3[(name, depth)] = dict(zip([it["id"] for it in gold], row["hits3"]))
                print(f"{key}: p50 {row['p50_ms']} ms on {mach['label']}", flush=True)
                continue
            ranks = {it["id"]: rr.rerank(it["query"], first[it["id"]][:depth]) for it in dev}
            fresh = Reranker(chunks, name, model=model)      # no score cache, so latency is real
            lat = []
            for j, it in enumerate(sample):
                t0 = time.perf_counter()
                fresh.rerank(it["query"], first[it["id"]][:depth])
                lat.append((time.perf_counter() - t0) * 1000 + first_lat[j])
            key = f"{name}-d{depth}"
            with open(os.path.join(a.out, "ranks", key + ".jsonl"), "w", encoding="utf-8") as f:
                for it in dev:
                    f.write(json.dumps({"id": it["id"], "top": [[c, round(s, 4)] for c, s in ranks[it["id"]][:10]]}) + "\n")
            h3 = recall_hits(gold, ranks, 3)
            hits3[(name, depth)] = h3
            rec = lambda its, k: sum(recall_hits(its, ranks, k).values()) / max(1, len(its))   # noqa: E731
            mrr = statistics.mean(next((1 / i for i, (c, _) in enumerate(ranks[it["id"]][:10], 1)
                                        if c in set(it["gold_ids"])), 0.0) for it in gold)
            rows.append(dict(config=key, candidate=name, model=path, depth=depth, r1=rec(gold, 1), r3=rec(gold, 3),
                             r5=rec(gold, 5), mrr=mrr, r3_hinglish=rec(hi, 3), r3_english=rec(en, 3),
                             p50_ms=round(statistics.median(lat), 1), p95_ms=round(sorted(lat)[int(0.95 * (len(lat) - 1))], 1),
                             added_ram_mb=ram, hits3=[h3[it["id"]] for it in gold],
                             recall_machine=mach["label"], latency_machine=mach["label"]))
            print(f"{key}: R@3 {rows[-1]['r3']:.1%} (Hinglish {rows[-1]['r3_hinglish']:.1%}), p50 {rows[-1]['p50_ms']} ms",
                  flush=True)
        del model, rr
        gc.collect()

    base = next((r for r in rows if (r["candidate"], r["depth"]) == BASELINE), None)
    if base is None:
        print("The baseline could not be run; nothing decided.", file=sys.stderr)
        return 2
    for r in rows:
        x, y = list(hits3[BASELINE].values()), list(hits3[(r["candidate"], r["depth"])].values())
        d, lo, hi_ = B.paired_bootstrap(y, x)
        r["r3_diff_pts"], r["r3_ci"] = 100 * d, [100 * lo, 100 * hi_]
        r["qualifies"] = (r["candidate"], r["depth"]) != BASELINE and qualifies(r, base)
    remote = any(not str(r.get("latency_machine", "local")).startswith("local") for r in rows)
    q = sorted([r for r in rows if r["qualifies"]], key=lambda r: (-r["r3"], r["p50_ms"]))
    choice = q[0] if q and not remote else None

    L = ["# Step 9: re-ranker trial (dev retrieval questions)", "",
         f"Dev: {len(gold)} answerable ({len(hi)} Hinglish), {len(dev) - len(gold)} unanswerable. Backend "
         f"{a.backend}, 256 tokens, {a.threads} threads; latency = first stage + re-rank on {len(sample)} dev questions.",
         "", f"Rule: p50 <= {MAX_P50_MS} ms and (Recall@3 +{GAIN_ALL:g} points, or Hinglish Recall@3 +{GAIN_HI:g} with "
         "Recall@3 not lower) against minilm at depth 20.", "",
         "| Config | R@1 | R@3 | R@3 − base [95% CI] | R@5 | MRR | R@3 Hinglish | R@3 English | p50 ms | p95 ms | Added RAM MB | Qualifies |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['config']} | {r['r1']:.1%} | {r['r3']:.1%} | {r['r3_diff_pts']:+.1f} [{r['r3_ci'][0]:+.1f}, "
                 f"{r['r3_ci'][1]:+.1f}] | {r['r5']:.1%} | {r['mrr']:.3f} | {r['r3_hinglish']:.1%} | {r['r3_english']:.1%} "
                 f"| {r['p50_ms']} | {r['p95_ms']} | {r['added_ram_mb'] if r['added_ram_mb'] is not None else '–'} "
                 f"| {'yes' if r['qualifies'] else ('baseline' if r is base else 'no')} |")
    for k, v in skipped.items():
        L.append(f"\nSkipped {k}: {v}")
    L.insert(3, f"Recall computed on: {rows[0].get('recall_machine', 'local')}. Latency measured on: "
                f"{rows[0].get('latency_machine', 'local')}.")
    if remote:
        L += ["", "**Latency was not measured on the kiosk's machine, so no choice is made yet.** Run "
                  "`python retrieval\\bench_reranker.py --latency-only` on the laptop."]
    else:
        L += ["", f"**Chosen: {choice['config']}**" if choice else "**No configuration qualifies: the deployed re-ranker stays.**"]
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "skipped": skipped, "choice": choice and choice["config"], "machine": mach,
                   "latency_remote": remote}, f, indent=1)
    cpath = os.path.join(a.out, "choice.json")
    if choice:
        with open(cpath, "w", encoding="utf-8") as f:
            json.dump({"config": choice["config"], "reranker": choice["model"], "depth": choice["depth"],
                       "max_length": 256, "backend": a.backend,
                       "ranks": os.path.relpath(os.path.join(a.out, "ranks", choice["config"] + ".jsonl"), ROOT)}, f, indent=1)
    elif os.path.exists(cpath):
        os.remove(cpath)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
