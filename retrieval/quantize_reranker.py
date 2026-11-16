"""
Objective 3, Step 12a (second try at 8 bits): quantise the OpenVINO MiniLM re-ranker with NNCF directly (it comes
with optimum-intel). About 1-3 minutes, no download.

    python retrieval\\quantize_reranker.py

Writes two 8-bit versions next to models/ov/minilm/openvino/openvino_model.xml:
  openvino_model_int8_static.xml    static post-training quantisation (weights and activations), calibrated on 300
                                    question-card pairs from knowledge/rerank_train.jsonl: generated from the corpus
                                    in Step 9, never from an eval set
  openvino_model_int8_weights.xml   8-bit weights only (no calibration data)
and records what worked in models/ov/quantize.json. bench_speed.py then times both.
"""

import glob
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
MDIR = os.path.join(ROOT, "models", "ov", "minilm")


def main():
    import numpy as np
    import openvino as ov
    import nncf
    from ov_runtime import _find_xml, _tokenizer
    src = _find_xml(MDIR, False)
    out_dir = os.path.dirname(src)
    core = ov.Core()
    info = {"source": os.path.relpath(src, ROOT)}
    tok = _tokenizer(MDIR, 256)
    text = {}
    with open(os.path.join(ROOT, "knowledge", "corpus.jsonl"), encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            text[c["id"]] = c["text"]
    pairs = []
    with open(os.path.join(ROOT, "knowledge", "rerank_train.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            pairs.append((r["query"], text[r["pos"]]))
            if r.get("negs"):
                pairs.append((r["query"], text[r["negs"][0]]))
    random.Random(13).shuffle(pairs)
    pairs = pairs[:300]
    names = {i.get_any_name() for i in core.read_model(src).inputs}

    def feed(pair):
        e = tok.encode_batch([pair])[0]
        d = {"input_ids": np.array([e.ids], dtype=np.int64), "attention_mask": np.array([e.attention_mask], dtype=np.int64)}
        if "token_type_ids" in names:
            d["token_type_ids"] = np.array([e.type_ids], dtype=np.int64)
        return d

    try:
        q = nncf.quantize(core.read_model(src), nncf.Dataset(pairs, feed), model_type=nncf.ModelType.TRANSFORMER,
                          subset_size=len(pairs))
        ov.save_model(q, os.path.join(out_dir, "openvino_model_int8_static.xml"), compress_to_fp16=False)
        info["static"] = f"ok ({len(pairs)} calibration pairs)"
    except Exception as e:  # noqa: BLE001
        info["static"] = f"FAILED: {type(e).__name__}: {str(e)[:300]}"
    try:
        w = nncf.compress_weights(core.read_model(src), mode=nncf.CompressWeightsMode.INT8_ASYM)
        ov.save_model(w, os.path.join(out_dir, "openvino_model_int8_weights.xml"), compress_to_fp16=False)
        info["weights"] = "ok"
    except Exception as e:  # noqa: BLE001
        info["weights"] = f"FAILED: {type(e).__name__}: {str(e)[:300]}"
    info["files"] = sorted(os.path.basename(x) for x in glob.glob(os.path.join(out_dir, "*.xml")))
    with open(os.path.join(ROOT, "models", "ov", "quantize.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info, indent=1))
    return 0 if "ok" in info["static"] or info["weights"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
