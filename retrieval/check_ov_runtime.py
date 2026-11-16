"""
Objective 3, Step 12b: check that the no-PyTorch runtime gives the same numbers as the deployed pipeline
(sentence-transformers bge-small on PyTorch + MiniLM on OpenVINO), on 40 dev questions. Seconds to a minute.

    python retrieval\\check_ov_runtime.py

Pass: query embeddings cosine >= 0.999 and re-ranker scores within 0.05 of each other, with the same top-3 order
in at least 95% of questions. Writes results_obj3/_speed_step12/check_runtime.json.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bench_retrieval as B  # noqa: E402
from retrievers import BM25Retriever, DenseRetriever, HybridRetriever  # noqa: E402


def main():
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from bench_latency import load_cross_encoder
    from ov_runtime import OVEncoder, OVCrossEncoder
    ov_dir = os.path.join(ROOT, "models", "ov")
    chunks = B.load_jsonl(os.path.join(ROOT, "knowledge", "corpus.jsonl"))
    text = {c["id"]: c["text"] for c in chunks}
    dev = [it for it in B.load_jsonl(os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl")) if it["split"] == "dev"][:40]
    st = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    ove = OVEncoder(os.path.join(ov_dir, "bge-small"), 4)
    pre = "Represent this sentence for searching relevant passages: "
    qs = [pre + it["query"] for it in dev]
    a = st.encode(qs, normalize_embeddings=True, convert_to_numpy=True)
    b = ove.encode(qs)
    cos = (a * b).sum(1)
    dense = DenseRetriever(chunks, "BAAI/bge-small-en-v1.5", encoder=st)
    hybrid = HybridRetriever(BM25Retriever(chunks), dense)
    ref = load_cross_encoder("openvino", 256, 4, os.path.join(ROOT, "results_retrieval"))
    ovc = OVCrossEncoder(os.path.join(ov_dir, "minilm"), 4, 256)
    diffs, same3 = [], 0
    for it in dev:
        ids = [c for c, _ in hybrid.search(it["query"], 20)]
        pairs = [(it["query"], text[c]) for c in ids]
        s1 = np.asarray(ref.predict(pairs, show_progress_bar=False), dtype="float32")
        s2 = ovc.predict(pairs)
        diffs.append(float(np.max(np.abs(s1 - s2))))
        same3 += list(np.argsort(-s1)[:3]) == list(np.argsort(-s2)[:3])
    out = {"min_cosine": float(cos.min()), "max_score_diff": max(diffs), "same_top3_share": same3 / len(dev)}
    out["pass"] = out["min_cosine"] >= 0.999 and out["max_score_diff"] <= 0.05 and out["same_top3_share"] >= 0.95
    os.makedirs(os.path.join(ROOT, "results_obj3", "_speed_step12"), exist_ok=True)
    with open(os.path.join(ROOT, "results_obj3", "_speed_step12", "check_runtime.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
