"""
Step 5 of Objective 2: benchmark retrievers on the kiosk corpus, without the language model.

    python retrieval\\bench_retrieval.py --configs bm25            # 1-minute smoke test, no downloads
    python retrieval\\bench_retrieval.py --configs all             # the full benchmark (14 configurations)
    python retrieval\\bench_retrieval.py --configs all --fake      # code path test with a stand-in encoder

Configurations: 7 first-stage retrievers, each alone and re-ranked by two cross-encoders on its top 20 (21 in all):
    bm25 | dense-<model> | hybrid-<model>   for model in bge-small-en-v1.5, bge-base-en-v1.5, multilingual-e5-small
    ...+bge     re-ranked by BAAI/bge-reranker-base
    ...+minilm  re-ranked by cross-encoder/ms-marco-MiniLM-L-6-v2

Writes results_retrieval\\:
    report.md      metrics on dev and test, per question type, latency, RAM, score separation
    summary.csv    one row per configuration and split
    ranks\\<config>.jsonl   top-10 chunk IDs and scores for every question (Step 6 calibrates the fallback on these)
    run_meta.json  machine, threads, library versions, timings

Runs on CPU with a fixed thread count (default 4, the Tier A setting), one query at a time for latency.
"""

import argparse
import gc
import json
import os
import platform
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from retrievers import BM25Retriever, DenseRetriever, HybridRetriever, Reranker  # noqa: E402

DENSE_MODELS = ["BAAI/bge-small-en-v1.5", "BAAI/bge-base-en-v1.5", "intfloat/multilingual-e5-small"]
RERANKERS = {"bge": "BAAI/bge-reranker-base",                 # 278M parameters, multilingual
             "minilm": "cross-encoder/ms-marco-MiniLM-L-6-v2"}   # 22M parameters, English, much cheaper
KS = (1, 5, 10)


def rss_mb():
    try:
        import psutil
        return psutil.Process().memory_info().rss / 1e6
    except Exception:
        return None


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def wilson(k, n, z=1.96):
    if n == 0:
        return None, None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def auroc(pos, neg):
    """Probability that a random answerable question's top score beats a random unanswerable one's."""
    if not pos or not neg:
        return None
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def paired_bootstrap(a, b, n=5000, seed=7):
    rng = random.Random(seed)
    m = len(a)
    diffs = []
    for _ in range(n):
        idx = [rng.randrange(m) for _ in range(m)]
        diffs.append(sum(a[i] - b[i] for i in idx) / m)
    diffs.sort()
    return sum(x - y for x, y in zip(a, b)) / m, diffs[int(0.025 * n)], diffs[int(0.975 * n)]


class FakeEncoder:
    """Hashing bag-of-words stand-in for tests: deterministic, no downloads."""

    def __init__(self, dim=256):
        import numpy as np
        self.np, self.dim = np, dim

    def encode(self, texts, batch_size=16, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False):
        import zlib
        from retrievers import tokenize
        out = self.np.zeros((len(texts), self.dim), dtype="float32")
        for i, t in enumerate(texts):
            for w in tokenize(t):
                out[i, zlib.crc32(w.encode()) % self.dim] += 1.0
        n = self.np.linalg.norm(out, axis=1, keepdims=True)
        return out / self.np.maximum(n, 1e-9)


class FakeCrossEncoder:
    def predict(self, pairs, batch_size=16, show_progress_bar=False):
        from retrievers import tokenize
        return [len(set(tokenize(q)) & set(tokenize(p))) / (1 + len(set(tokenize(q)))) for q, p in pairs]


def metrics(items, ranks, split):
    rows = [it for it in items if it["split"] == split]
    gold = [it for it in rows if it["gold_ids"]]
    out = {"n_answerable": len(gold), "n_unanswerable": sum(1 for it in rows if not it["gold_ids"])}
    hits = {k: [] for k in KS}
    rr = []
    for it in gold:
        top = [cid for cid, _ in ranks[it["id"]]]
        g = set(it["gold_ids"])
        for k in KS:
            hits[k].append(1 if g & set(top[:k]) else 0)
        r = next((i for i, cid in enumerate(top[:10], 1) if cid in g), None)
        rr.append(1.0 / r if r else 0.0)
    for k in KS:
        p, lo, hi = wilson(sum(hits[k]), len(hits[k]))
        out[f"recall@{k}"], out[f"recall@{k}_lo"], out[f"recall@{k}_hi"] = p, lo, hi
    out["mrr@10"] = sum(rr) / len(rr) if rr else None
    out["_hits5"] = {it["id"]: h for it, h in zip(gold, hits[5])}
    top1 = lambda it: ranks[it["id"]][0][1] if ranks[it["id"]] else float("-inf")
    out["auroc_top1"] = auroc([top1(it) for it in gold], [top1(it) for it in rows if it["answer_type"] == "none"])
    by = {}
    for it, h in zip(gold, hits[5]):
        for key in (it["subtype"], "lang:" + it["language"], "near_miss" if it["near_miss"] else None):
            if key:
                by.setdefault(key, []).append(h)
    out["by_group"] = {k: (sum(v), len(v)) for k, v in by.items()}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", default="bm25", help="'all', or a comma list such as bm25,hybrid-bge-small-en-v1.5")
    ap.add_argument("--rerankers", default="bge,minilm", help="comma list from: bge, minilm; empty for none")
    ap.add_argument("--rerank-depth", type=int, default=20)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--latency-sample", type=int, default=60, help="questions timed one at a time per config")
    ap.add_argument("--corpus", default=os.path.join(ROOT, "knowledge", "corpus.jsonl"))
    ap.add_argument("--eval", default=os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results_retrieval"))
    ap.add_argument("--fake", action="store_true", help="stand-in encoders, for testing the code without downloads")
    a = ap.parse_args()

    chunks, items = load_jsonl(a.corpus), load_jsonl(a.eval)
    os.makedirs(os.path.join(a.out, "ranks"), exist_ok=True)
    try:
        import torch
        torch.set_num_threads(a.threads)
        torch_version = torch.__version__
    except Exception:
        torch_version = None
    os.environ.setdefault("OMP_NUM_THREADS", str(a.threads))

    wanted = a.configs.split(",") if a.configs != "all" else (
        ["bm25"] + [f"{kind}-{m.split('/')[-1]}" for m in DENSE_MODELS for kind in ("dense", "hybrid")])
    rerankers = [r for r in a.rerankers.split(",") if r] if a.configs == "all" else \
        sorted({w.split("+")[1] for w in wanted if "+" in w})
    to_rerank = None if a.configs == "all" else {w.split("+")[0]: w.split("+")[1] for w in wanted if "+" in w}
    keep_plain = a.configs == "all" or [w for w in wanted if "+" not in w]
    wanted = sorted({w.split("+")[0] for w in wanted}, key=lambda w: (w != "bm25", w))
    sample = random.Random(11).sample(items, min(a.latency_sample, len(items)))
    meta = dict(machine=platform.processor() or platform.machine(), python=sys.version.split()[0],
                torch=torch_version, threads=a.threads, fake=a.fake, timings={}, ram_mb={})
    try:
        import sentence_transformers
        meta["sentence_transformers"] = sentence_transformers.__version__
    except Exception:
        pass

    base_rss = rss_mb()
    t = time.perf_counter()
    bm25 = BM25Retriever(chunks)
    meta["timings"]["bm25_index_s"] = round(time.perf_counter() - t, 2)
    first_stage = {}   # config name -> {qid: [(cid, score)] top max(10, depth)}
    latency = {}       # config name -> list of ms
    depth = max(10, a.rerank_depth)

    if "bm25" in wanted:
        first_stage["bm25"] = {it["id"]: bm25.search(it["query"], depth) for it in items}
        lat = []
        for it in sample:
            t0 = time.perf_counter()
            bm25.search(it["query"], depth)
            lat.append((time.perf_counter() - t0) * 1000)
        latency["bm25"] = lat
        print(f"bm25: done ({statistics.median(lat):.1f} ms per query)")

    for model in DENSE_MODELS:
        short = model.split("/")[-1]
        names = [n for n in wanted if n in (f"dense-{short}", f"hybrid-{short}")]
        if not names:
            continue
        print(f"{short}: loading and encoding {len(chunks)} chunks ...", flush=True)
        r0 = rss_mb()
        t = time.perf_counter()
        dense = DenseRetriever(chunks, model, encoder=FakeEncoder() if a.fake else None)
        meta["timings"][f"{short}_load_and_index_s"] = round(time.perf_counter() - t, 1)
        if r0 is not None:
            meta["ram_mb"][short] = round(rss_mb() - r0)
        qv = {it["id"]: dense.encode_query(it["query"]) for it in items}
        dhits = {qid: dense.search_vector(v, 50) for qid, v in qv.items()}
        hybrid = HybridRetriever(bm25, dense)
        for name in names:
            if name.startswith("dense"):
                first_stage[name] = {qid: h[:depth] for qid, h in dhits.items()}
            else:
                first_stage[name] = {it["id"]: hybrid.search(it["query"], depth, dense_hits=dhits[it["id"]]) for it in items}
            lat = []
            for it in sample:
                t0 = time.perf_counter()
                (dense.search(it["query"], depth) if name.startswith("dense") else hybrid.search(it["query"], depth))
                lat.append((time.perf_counter() - t0) * 1000)
            latency[name] = lat
            print(f"{name}: done ({statistics.median(lat):.1f} ms per query)", flush=True)
        del dense, hybrid
        gc.collect()

    results = {}
    for name, hits in first_stage.items():
        if a.configs == "all" or name in keep_plain:
            results[name] = {qid: h[:10] for qid, h in hits.items()}
    qtext = {it["id"]: it["query"] for it in items}
    for rk in rerankers:
        model_name = RERANKERS[rk]
        names = list(first_stage) if to_rerank is None else [n for n, r in to_rerank.items() if r == rk]
        if not names:
            continue
        print(f"reranker {rk}: loading {model_name} ...", flush=True)
        r0 = rss_mb()
        reranker = Reranker(chunks, model_name, model=FakeCrossEncoder() if a.fake else None)
        if r0 is not None:
            meta["ram_mb"][model_name.split("/")[-1]] = round(rss_mb() - r0)
        by_q = {}
        for name in names:
            for it in items:
                for cid, _ in first_stage[name][it["id"]][:a.rerank_depth]:
                    by_q.setdefault(it["id"], set()).add(cid)
        n_pairs = sum(len(v) for v in by_q.values())
        print(f"reranker {rk}: scoring {n_pairs} unique question-chunk pairs (shared across configs) ...", flush=True)
        t = time.perf_counter()
        for i, (qid, cids) in enumerate(sorted(by_q.items()), 1):
            reranker.score(qtext[qid], sorted(cids))
            if i % 100 == 0:
                print(f"  {i}/{len(by_q)} questions", flush=True)
        meta["timings"][f"rerank_{rk}_all_s"] = round(time.perf_counter() - t, 1)
        for name in names:
            results[f"{name}+{rk}"] = {it["id"]: reranker.rerank(it["query"], first_stage[name][it["id"]][:a.rerank_depth])
                                       for it in items}
        fresh = Reranker(chunks, model_name, model=reranker.model)   # empty cache: true per-question cost
        lat = []
        for it in sample:
            cands = first_stage[names[0]][it["id"]][:a.rerank_depth]
            t0 = time.perf_counter()
            fresh.rerank(it["query"], cands)
            lat.append((time.perf_counter() - t0) * 1000)
        for name in names:
            latency[f"{name}+{rk}"] = [x + y for x, y in zip(latency[name], lat)]
        meta[f"rerank_{rk}_only_ms_median"] = round(statistics.median(lat), 1)
        del reranker, fresh
        gc.collect()

    # ---- score and write ----
    summary, per = [], {}
    for name, ranks in results.items():
        with open(os.path.join(a.out, "ranks", f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps({"id": it["id"], "split": it["split"], "top": ranks[it["id"]]}) + "\n")
        per[name] = {s: metrics(items, ranks, s) for s in ("dev", "test")}
        lat = sorted(latency.get(name, [0]))
        for s in ("dev", "test"):
            m = per[name][s]
            summary.append(dict(config=name, split=s, n_answerable=m["n_answerable"],
                                **{k: (round(m[k], 4) if isinstance(m[k], float) else m[k]) for k in
                                   ("recall@1", "recall@5", "recall@5_lo", "recall@5_hi", "recall@10", "mrr@10", "auroc_top1")},
                                latency_ms_p50=round(statistics.median(lat), 1),
                                latency_ms_p95=round(lat[min(len(lat) - 1, int(0.95 * len(lat)))], 1)))
    import csv
    with open(os.path.join(a.out, "summary.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)

    best = max(per, key=lambda n: (per[n]["dev"]["recall@5"], per[n]["dev"]["mrr@10"]))
    pct = lambda x: "-" if x is None else f"{100 * x:.0f}%"
    L = ["# Retrieval benchmark (Objective 2, Step 5)", "",
         f"Corpus: {len(chunks)} chunks. Questions: {sum(1 for i in items if i['split'] == 'dev')} dev, "
         f"{sum(1 for i in items if i['split'] == 'test')} test. CPU threads: {a.threads}." + (" **FAKE ENCODERS (code test only)**" if a.fake else ""),
         "", "Recall@k: share of answerable questions with a gold chunk in the top k (95% CI for @5). "
         "AUROC: how well the top-1 score separates answerable from unanswerable questions (0.5 = no better than chance); "
         "this is what the Step 6 fallback threshold relies on. Latency: one question at a time, p50 / p95.", "",
         "| Config | Split | R@1 | R@5 [95% CI] | R@10 | MRR@10 | AUROC | Latency p50 / p95 |", "|---|---|---|---|---|---|---|---|"]
    for row in sorted(summary, key=lambda r: (r["split"] != "dev", -(r["recall@5"] or 0))):
        L.append(f"| {row['config']} | {row['split']} | {pct(row['recall@1'])} | {pct(row['recall@5'])} "
                 f"[{pct(row['recall@5_lo'])}-{pct(row['recall@5_hi'])}] | {pct(row['recall@10'])} | "
                 f"{row['mrr@10']:.3f} | {row['auroc_top1'] if row['auroc_top1'] is None else round(row['auroc_top1'], 3)} | "
                 f"{row['latency_ms_p50']} / {row['latency_ms_p95']} ms |")
    L += ["", f"## Paired differences in Recall@5 against the best dev config ({best})", "",
          "| Config | Dev diff [95% CI] | Test diff [95% CI] |", "|---|---|---|"]
    for name in per:
        if name == best:
            continue
        cells = []
        for s in ("dev", "test"):
            hb, hn = per[best][s]["_hits5"], per[name][s]["_hits5"]
            ids = sorted(hb)
            d, lo, hi = paired_bootstrap([hn[i] for i in ids], [hb[i] for i in ids])
            cells.append(f"{100 * d:+.1f} [{100 * lo:+.1f}, {100 * hi:+.1f}]")
        L.append(f"| {name} | {cells[0]} | {cells[1]} |")
    groups = sorted({g for n in per for g in per[n]["test"]["by_group"]})
    sizes = {g: next(per[x]["test"]["by_group"][g][1] for x in per if g in per[x]["test"]["by_group"]) for g in groups}
    L += ["", "## Recall@5 by question type (test split; n under each heading)", "",
          "| Config | " + " | ".join(f"{g} ({sizes[g]})" for g in groups) + " |", "|---|" + "---|" * len(groups)]
    for x in sorted(per, key=lambda n: -per[n]["dev"]["recall@5"]):
        cells = []
        for g in groups:
            k, m = per[x]["test"]["by_group"].get(g, (0, 0))
            cells.append(pct(k / m) if m else "-")
        L.append(f"| {x} | " + " | ".join(cells) + " |")
    L += ["", "## Memory and build time", "", "| Item | Value |", "|---|---|"]
    for k, v in meta["ram_mb"].items():
        L.append(f"| RAM added by {k} | {v} MB |")
    for k, v in meta["timings"].items():
        L.append(f"| {k} | {v} |")
    for rk in rerankers:
        if f"rerank_{rk}_only_ms_median" in meta:
            L.append(f"| Re-rank only ({rk}), {a.rerank_depth} candidates, median | {meta[f'rerank_{rk}_only_ms_median']} ms |")
    if base_rss is not None:
        L.append(f"| Process RAM at start | {round(base_rss)} MB |")
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("\n".join(L[:12 + len(summary)]))
    print("\nWrote " + os.path.join(a.out, "report.md") + ", summary.csv and ranks/")


if __name__ == "__main__":
    main()
