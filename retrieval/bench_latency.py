"""
Step 5b of Objective 2: make the chosen retriever (hybrid bge-small-en-v1.5 + MiniLM re-ranker) faster
without losing recall.

    python retrieval\\bench_latency.py                 # torch, onnx, onnx-int8 (and openvino if installed)
    python retrieval\\bench_latency.py --fake          # code path test, no downloads

Variants: re-ranker backend x passage length x re-rank depth
    backend     torch (the Step 5 baseline), onnx, onnx-int8 (dynamic 8-bit, AVX2), openvino
    max_length  512 (baseline), 256 tokens per question+passage pair
    depth       20 (baseline), 10, 5 candidates re-ranked

Decision rule (fixed before the run): a variant qualifies if its dev Recall@5 is statistically tied with the
baseline (paired 95% interval of the difference includes 0) and not more than 2 points below it. Among
qualifying variants, the one with the lowest p50 latency is chosen; its test numbers are the ones reported.

Writes results_retrieval\\latency\\report.md, summary.csv, ranks\\<variant>.jsonl, run_meta.json.
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

EMBEDDER = "BAAI/bge-small-en-v1.5"
RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEPTHS = (20, 10, 5)
LENGTHS = (512, 256)
BASELINE = ("torch", 512, 20)


def load_cross_encoder(backend, max_length, threads, workdir, model_name=RERANKER):
    """Return a CrossEncoder for the backend, or raise with a readable reason. model_name: a hub name or a local
    folder (Objective 3, Step 9 candidates); the default is the deployed MiniLM."""
    from sentence_transformers import CrossEncoder
    if backend == "torch":
        return CrossEncoder(model_name, max_length=max_length, device="cpu")
    if backend in ("onnx", "onnx-int8"):
        kwargs = {"provider": "CPUExecutionProvider"}
        try:
            import onnxruntime as ort
            so = ort.SessionOptions()
            so.intra_op_num_threads = threads
            kwargs["session_options"] = so
        except Exception:
            pass
        if backend == "onnx":
            return CrossEncoder(model_name, max_length=max_length, device="cpu", backend="onnx", model_kwargs=kwargs)
        # 8-bit: export the ONNX model locally, quantize it once, then load the quantized file
        from sentence_transformers import export_dynamic_quantized_onnx_model
        local = os.path.join(workdir, "minilm-onnx" if model_name == RERANKER else
                             os.path.basename(os.path.normpath(model_name)) + "-onnx")
        qfile = os.path.join(local, "onnx", "model_qint8_avx2.onnx")
        if not os.path.exists(qfile):
            base = CrossEncoder(model_name, max_length=max_length, device="cpu", backend="onnx")
            base.save_pretrained(local)
            export_dynamic_quantized_onnx_model(base, "avx2", local)
        return CrossEncoder(local, max_length=max_length, device="cpu", backend="onnx",
                            model_kwargs=dict(kwargs, file_name="onnx/model_qint8_avx2.onnx"))
    if backend == "openvino":
        return CrossEncoder(model_name, max_length=max_length, device="cpu", backend="openvino",
                            model_kwargs={"ov_config": {"INFERENCE_NUM_THREADS": str(threads)}})
    raise ValueError(backend)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backends", default="torch,onnx,onnx-int8,openvino")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--latency-sample", type=int, default=60)
    ap.add_argument("--corpus", default=os.path.join(ROOT, "knowledge", "corpus.jsonl"))
    ap.add_argument("--eval", default=os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results_retrieval", "latency"))
    ap.add_argument("--fake", action="store_true")
    a = ap.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", str(a.threads))
    try:
        import torch
        torch.set_num_threads(a.threads)
    except Exception:
        pass
    chunks, items = B.load_jsonl(a.corpus), B.load_jsonl(a.eval)
    os.makedirs(os.path.join(a.out, "ranks"), exist_ok=True)
    sample = random.Random(11).sample(items, min(a.latency_sample, len(items)))   # same sample as Step 5
    qtext = {it["id"]: it["query"] for it in items}

    print("first stage: hybrid bm25 + bge-small-en-v1.5 ...", flush=True)
    bm25 = BM25Retriever(chunks)
    dense = DenseRetriever(chunks, EMBEDDER, encoder=B.FakeEncoder() if a.fake else None)
    hybrid = HybridRetriever(bm25, dense)
    first = {it["id"]: hybrid.search(it["query"], max(DEPTHS)) for it in items}
    first_lat = []
    for it in sample:
        t0 = time.perf_counter()
        hybrid.search(it["query"], max(DEPTHS))
        first_lat.append((time.perf_counter() - t0) * 1000)
    print(f"first stage: {statistics.median(first_lat):.1f} ms median", flush=True)

    variants, skipped, ram = {}, {}, {}
    for backend in a.backends.split(","):
        for max_len in LENGTHS:
            name = f"{backend}-len{max_len}"
            print(f"\n{name}: loading ...", flush=True)
            r0 = B.rss_mb()
            try:
                model = B.FakeCrossEncoder() if a.fake else load_cross_encoder(backend, max_len, a.threads, a.out)
            except Exception as e:
                skipped[name] = f"{type(e).__name__}: {str(e)[:200]}"
                print(f"{name}: SKIPPED ({skipped[name]})", flush=True)
                continue
            if r0 is not None:
                ram[name] = round(B.rss_mb() - r0)
            rr = Reranker(chunks, RERANKER, model=model)
            t = time.perf_counter()
            for i, it in enumerate(items, 1):
                rr.score(it["query"], [cid for cid, _ in first[it["id"]][:max(DEPTHS)]])
                if i % 100 == 0:
                    print(f"  {i}/{len(items)} questions", flush=True)
            print(f"{name}: scored in {time.perf_counter() - t:.0f} s", flush=True)
            for depth in DEPTHS:
                ranks = {it["id"]: rr.rerank(it["query"], first[it["id"]][:depth]) for it in items}
                fresh = Reranker(chunks, RERANKER, model=model)
                lat = []
                for j, it in enumerate(sample):
                    t0 = time.perf_counter()
                    fresh.rerank(it["query"], first[it["id"]][:depth])
                    lat.append((time.perf_counter() - t0) * 1000 + first_lat[j])
                variants[(backend, max_len, depth)] = dict(ranks=ranks, lat=sorted(lat))
                print(f"  depth {depth:2d}: {statistics.median(lat):.0f} ms median (search + re-rank)", flush=True)
            del model, rr, fresh
            gc.collect()

    if BASELINE not in variants:
        sys.exit("The torch baseline did not run, so variants cannot be compared. See the SKIPPED lines above.")

    # ---- score, apply the rule, write ----
    rows = []
    base_dev = B.metrics(items, variants[BASELINE]["ranks"], "dev")
    for key, v in variants.items():
        m = {s: B.metrics(items, v["ranks"], s) for s in ("dev", "test")}
        ids = sorted(base_dev["_hits5"])
        d, lo, hi = B.paired_bootstrap([m["dev"]["_hits5"][i] for i in ids], [base_dev["_hits5"][i] for i in ids])
        lat = v["lat"]
        p50, p95 = statistics.median(lat), lat[min(len(lat) - 1, int(0.95 * len(lat)))]
        rows.append(dict(backend=key[0], max_length=key[1], depth=key[2],
                         dev_recall5=m["dev"]["recall@5"], dev_diff=d, dev_diff_lo=lo, dev_diff_hi=hi,
                         test_recall5=m["test"]["recall@5"], test_recall5_lo=m["test"]["recall@5_lo"],
                         test_recall5_hi=m["test"]["recall@5_hi"], test_mrr10=m["test"]["mrr@10"],
                         test_auroc=m["test"]["auroc_top1"], hinglish_test=m["test"]["by_group"].get("lang:hinglish"),
                         negative_test=m["test"]["by_group"].get("negative"),
                         p50_ms=p50, p95_ms=p95, ram_mb=ram.get(f"{key[0]}-len{key[1]}")))
        name = f"{key[0]}-len{key[1]}-depth{key[2]}"
        with open(os.path.join(a.out, "ranks", f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps({"id": it["id"], "split": it["split"], "top": v["ranks"][it["id"]]}) + "\n")
    for r in rows:
        r["qualifies"] = r["dev_diff_lo"] <= 0 <= r["dev_diff_hi"] and r["dev_diff"] >= -0.02 or \
            (r["backend"], r["max_length"], r["depth"]) == BASELINE
    chosen = min((r for r in rows if r["qualifies"]), key=lambda r: r["p50_ms"])

    import csv
    with open(os.path.join(a.out, "summary.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    pct = lambda x: "-" if x is None else f"{100 * x:.1f}%"
    frac = lambda t: "-" if not t else f"{t[0]}/{t[1]}"
    L = ["# Step 5b: retriever latency variants", "",
         f"First stage: hybrid BM25 + {EMBEDDER} ({statistics.median(first_lat):.0f} ms median). Re-ranker: {RERANKER}. "
         f"CPU threads: {a.threads}. Latency = search + re-rank, one question at a time, {len(sample)} questions."
         + (" **FAKE MODELS (code test only)**" if a.fake else ""), "",
         "Rule: qualifies if dev Recall@5 is tied with the baseline (torch, 512, depth 20) and at most 2 points below; "
         "the fastest qualifying variant is chosen.", "",
         "| Backend | Length | Depth | Dev R@5 | Dev diff [95% CI] | Qualifies | Test R@5 [95% CI] | Test MRR | Test AUROC | "
         "Hinglish (test) | \"No\" answers (test) | p50 / p95 ms | RAM MB |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["p50_ms"]):
        mark = " **chosen**" if r is chosen else ""
        L.append(f"| {r['backend']}{mark} | {r['max_length']} | {r['depth']} | {pct(r['dev_recall5'])} | "
                 f"{100 * r['dev_diff']:+.1f} [{100 * r['dev_diff_lo']:+.1f}, {100 * r['dev_diff_hi']:+.1f}] | "
                 f"{'yes' if r['qualifies'] else 'no'} | {pct(r['test_recall5'])} [{pct(r['test_recall5_lo'])}-"
                 f"{pct(r['test_recall5_hi'])}] | {r['test_mrr10']:.3f} | {r['test_auroc']:.3f} | "
                 f"{frac(r['hinglish_test'])} | {frac(r['negative_test'])} | {r['p50_ms']:.0f} / {r['p95_ms']:.0f} | "
                 f"{r['ram_mb'] if r['ram_mb'] is not None else '-'} |")
    L += ["", f"**Chosen:** {chosen['backend']}, max length {chosen['max_length']}, depth {chosen['depth']}: "
          f"test Recall@5 {pct(chosen['test_recall5'])}, MRR {chosen['test_mrr10']:.3f}, p50 {chosen['p50_ms']:.0f} ms "
          f"({'meets' if chosen['p50_ms'] <= 300 else 'misses'} the 300 ms target)."]
    if skipped:
        L += ["", "Skipped backends:"] + [f"- {k}: {v}" for k, v in skipped.items()]
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    meta = dict(threads=a.threads, fake=a.fake, skipped=skipped, ram_mb=ram, first_stage_ms=statistics.median(first_lat))
    for mod in ("sentence_transformers", "torch", "onnxruntime", "optimum", "openvino"):
        try:
            meta[mod] = __import__(mod).__version__
        except Exception:
            meta[mod] = None
    with open(os.path.join(a.out, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print("\n" + "\n".join(L))
    print("\nWrote " + os.path.join(a.out, "report.md"))


if __name__ == "__main__":
    main()
