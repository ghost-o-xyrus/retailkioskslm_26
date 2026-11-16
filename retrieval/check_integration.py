"""
Step 7a of Objective 2: check the assistant's knowledge base before any model run, and fix how many chunks the
model sees.

    python retrieval\\check_integration.py
    python retrieval\\check_integration.py --fake        # code path test, no downloads

1. Same retriever? Runs retrieval/knowledge_base.py on all 500 retrieval questions and compares it with the saved
   Step 5b scores (openvino-len256-depth20). Top-1 chunks should agree and scores should match to about 0.01;
   otherwise the Step 6 threshold would not apply to the assistant.
2. How many chunks (k)? Rule, fixed before the run: on DEV, the smallest k from 1 to 5 whose Recall@k is at most
   2 points below Recall@5 (the Step 5b tolerance), with at most 1,500 context tokens. Fewer chunks means a
   shorter prompt, which matters most on the Tier A CPU, where prompt processing is the slow part.
3. Latency and RAM of the knowledge base inside the assistant's process.

Writes results_retrieval\\integration\\report.md and integration.json (k, read by the harness).
"""

import argparse
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bench_retrieval as B  # noqa: E402
from knowledge_base import KnowledgeBase, DEFAULT_FALLBACK, DEFAULT_CORPUS  # noqa: E402

KS = (1, 2, 3, 4, 5)
TOLERANCE = 0.02
MAX_CONTEXT_TOKENS = 1500


def pctl(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))] if xs else None


def recall_at(items, ranks, tokens, k, split):
    hits, toks = [], []
    for it in items:
        if it["split"] != split or not it["gold_ids"]:
            continue
        chosen, used = [], 0
        for cid, _ in ranks[it["id"]][:k]:
            if chosen and used + tokens[cid] > MAX_CONTEXT_TOKENS:
                break
            chosen.append(cid)
            used += tokens[cid]
        hits.append(1 if set(it["gold_ids"]) & set(chosen) else 0)
        toks.append(used)
    return sum(hits) / len(hits), statistics.mean(toks), pctl(toks, 0.9), len(hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranks", default=os.path.join(ROOT, "results_retrieval", "latency", "ranks", "openvino-len256-depth20.jsonl"))
    ap.add_argument("--eval", default=os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    ap.add_argument("--fallback", default=DEFAULT_FALLBACK)
    ap.add_argument("--out", default=os.path.join(ROOT, "results_retrieval", "integration"))
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--limit", type=int, default=None, help="questions for checks 1 and 3 (default all 500)")
    ap.add_argument("--fake", action="store_true")
    a = ap.parse_args()
    for p, hint in ((a.ranks, "Run Step 5b (bench_latency.py) first."),
                    (a.fallback, "Run: python retrieval\\calibrate_fallback.py --hinglish-bypass")):
        if not os.path.exists(p):
            sys.exit(f"Not found: {p}\n{hint}")
    items = B.load_jsonl(a.eval)
    saved = {r["id"]: [tuple(x) for x in r["top"]] for r in B.load_jsonl(a.ranks)}
    tokens = {c["id"]: c.get("tokens", 0) for c in B.load_jsonl(DEFAULT_CORPUS)}

    # ---- 2. k, from the saved Step 5b ranks (dev only) ----
    table = {k: {s: recall_at(items, saved, tokens, k, s) for s in ("dev", "test")} for k in KS}
    r5 = table[5]["dev"][0]
    k = min(kk for kk in KS if table[kk]["dev"][0] >= r5 - TOLERANCE - 1e-9)

    # ---- 1 and 3. the knowledge base itself ----
    r0 = B.rss_mb()
    t = time.perf_counter()
    kb = KnowledgeBase(fallback_path=a.fallback, k=k, threads=a.threads, fake=a.fake,
                       max_context_tokens=MAX_CONTEXT_TOKENS)
    load_s = time.perf_counter() - t
    r1 = B.rss_mb()
    run = items[:a.limit] if a.limit else items
    top1_same, top5_overlap, dscore, lat, stages, fb_same = 0, [], [], [], {}, 0
    for i, it in enumerate(run, 1):
        r = kb.retrieve(it["query"])
        lat.append(r["timings_ms"]["total"])
        for s, v in r["timings_ms"].items():
            stages.setdefault(s, []).append(v)
        mine, theirs = r["top10"], saved[it["id"]]
        if mine and theirs:
            top1_same += mine[0][0] == theirs[0][0]
            dscore.append(abs(mine[0][1] - theirs[0][1]))
            top5_overlap.append(len({c for c, _ in mine[:5]} & {c for c, _ in theirs[:5]}) / 5)
            would = theirs[0][1] < kb.threshold and not (kb.bypass and r["hinglish"])
            fb_same += would == r["refuse"]
        if i % 100 == 0:
            print(f"  {i}/{len(run)} questions", flush=True)
    r2 = B.rss_mb()
    n = len(dscore)

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "integration.json"), "w", encoding="utf-8") as f:
        json.dump(dict(k=k, rule=f"smallest k in 1-5 with dev Recall@k >= dev Recall@5 - {TOLERANCE:.0%}, "
                                 f"at most {MAX_CONTEXT_TOKENS} context tokens",
                       max_context_tokens=MAX_CONTEXT_TOKENS, dev_recall={kk: round(table[kk]["dev"][0], 4) for kk in KS},
                       knowledge_base=kb.config, fake=a.fake), f, indent=2)

    pct = lambda x: f"{100 * x:.1f}%"
    L = ["# Step 7a: knowledge base check", "",
         "## 1. Is it the same retriever as Step 5b?", "",
         f"Questions: {n}. Same top-1 chunk: {top1_same}/{n} = {pct(top1_same / n)}. "
         f"Top-1 score difference: median {statistics.median(dscore):.4f}, max {max(dscore):.4f}. "
         f"Top-5 overlap: {pct(statistics.mean(top5_overlap))}. "
         f"Same fallback decision: {fb_same}/{n} = {pct(fb_same / n)}.", "",
         "Expected: about 100% and differences near 0.01 or less (small numeric noise between runs is normal). "
         "Large differences mean the assistant is not using the benchmarked retriever, and Step 6's threshold "
         "would not apply.", "",
         "## 2. How many chunks the model sees (k)", "",
         f"Rule, fixed before the run: on dev, the smallest k from 1 to 5 with Recall@k at most "
         f"{TOLERANCE * 100:.0f} points below Recall@5, and at most {MAX_CONTEXT_TOKENS} context tokens. "
         "Computed from the saved Step 5b ranks.", "",
         "| k | Dev Recall@k | Dev context tokens, mean / p90 | Test Recall@k |", "|---|---|---|---|"]
    for kk in KS:
        d, te = table[kk]["dev"], table[kk]["test"]
        L.append(f"| {kk}{' **chosen**' if kk == k else ''} | {pct(d[0])} | {d[1]:.0f} / {d[2]} | {pct(te[0])} |")
    L += ["", f"**k = {k}.** Test Recall@k is shown for the record; it did not choose k.", "",
          "## 3. Latency and RAM inside the assistant", "",
          f"Load time {load_s:.1f} s. Added RAM after loading: "
          + (f"{r1 - r0:.0f} MB; after {len(run)} questions: {r2 - r0:.0f} MB." if r0 is not None else "psutil not installed."),
          "", "| Stage | p50 ms | p90 ms |", "|---|---|---|"]
    for s in ("bm25", "dense", "fuse", "rerank", "total"):
        L.append(f"| {s} | {statistics.median(stages[s]):.1f} | {pctl(stages[s], 0.9):.1f} |")
    L += ["", f"Knowledge base settings: `{json.dumps(kb.config)}`"]
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nWrote {os.path.join(a.out, 'report.md')} and integration.json")


if __name__ == "__main__":
    main()
