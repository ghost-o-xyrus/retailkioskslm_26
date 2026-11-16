"""
Objective 3, Step 12a: export both retrieval models to OpenVINO files once (needs sentence-transformers and
optimum-intel, which you already have; about 2-5 minutes, downloads a small calibration set once).

    python retrieval\\export_openvino.py

Writes models/ov/bge-small/ and models/ov/minilm/ (openvino/*.xml + tokenizer.json), which retrieval/ov_runtime.py
runs without PyTorch. Also writes an 8-bit re-ranker into models/ov/minilm/openvino/:
  - static post-training quantisation (sentence-transformers' export_static_quantized_openvino_model, calibrated on
    its default general-English sentence set), or, if that fails,
  - 8-bit weights only (optimum-intel OVWeightQuantizationConfig(bits=8)), which needs no calibration data.
Which one was made is written to models/ov/export.json.
"""

import glob
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "models", "ov")
EMBEDDER = "BAAI/bge-small-en-v1.5"
RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def main():
    from sentence_transformers import SentenceTransformer, CrossEncoder
    os.makedirs(OUT, exist_ok=True)
    info = {}
    st = SentenceTransformer(EMBEDDER, backend="openvino", device="cpu")
    edir = os.path.join(OUT, "bge-small")
    st.save_pretrained(edir)
    ce = CrossEncoder(RERANKER, backend="openvino", device="cpu")
    mdir = os.path.join(OUT, "minilm")
    ce.save_pretrained(mdir)
    # some sentence-transformers versions save only the PyTorch weights: export with optimum-intel directly then
    for d, name, cls in ((edir, EMBEDDER, "OVModelForFeatureExtraction"), (mdir, RERANKER, "OVModelForSequenceClassification")):
        if not glob.glob(os.path.join(d, "**", "*.xml"), recursive=True):
            import optimum.intel as oi
            from transformers import AutoTokenizer
            print(f"{os.path.basename(d)}: no OpenVINO file after saving; exporting with optimum-intel")
            getattr(oi, cls).from_pretrained(name, export=True).save_pretrained(os.path.join(d, "openvino"))
            AutoTokenizer.from_pretrained(name).save_pretrained(d)
        if not os.path.exists(os.path.join(d, "tokenizer.json")) and not glob.glob(os.path.join(d, "**", "tokenizer.json"), recursive=True):
            from transformers import AutoTokenizer
            AutoTokenizer.from_pretrained(name).save_pretrained(d)
    info["fp32"] = sorted(os.path.relpath(x, OUT) for x in glob.glob(os.path.join(OUT, "**", "*.xml"), recursive=True))
    try:
        from sentence_transformers import export_static_quantized_openvino_model
        from optimum.intel import OVQuantizationConfig
        export_static_quantized_openvino_model(ce, OVQuantizationConfig(), mdir)
        info["int8"] = "static post-training quantisation (default calibration set)"
    except Exception as e:  # noqa: BLE001
        print(f"static 8-bit export failed ({type(e).__name__}: {str(e)[:200]}); trying 8-bit weights only")
        try:
            from optimum.intel import OVModelForSequenceClassification, OVWeightQuantizationConfig
            src = os.path.dirname(next(iter(glob.glob(os.path.join(mdir, "**", "openvino_model.xml"), recursive=True))))
            tmp = os.path.join(OUT, "_w8")
            m = OVModelForSequenceClassification.from_pretrained(src, quantization_config=OVWeightQuantizationConfig(bits=8))
            m.save_pretrained(tmp)
            for ext in (".xml", ".bin"):
                shutil.copy(os.path.join(tmp, "openvino_model" + ext), os.path.join(src, "openvino_model_int8_weights" + ext))
            shutil.rmtree(tmp, ignore_errors=True)
            info["int8"] = "8-bit weights only"
        except Exception as e2:  # noqa: BLE001
            info["int8"] = f"FAILED: {type(e2).__name__}: {str(e2)[:200]}"
    info["files"] = sorted(os.path.relpath(x, OUT) for x in glob.glob(os.path.join(OUT, "**", "*.xml"), recursive=True))
    missing = [d for d in ("bge-small", "minilm") if not glob.glob(os.path.join(OUT, d, "**", "*.xml"), recursive=True)]
    info["ok"] = not missing
    if missing:
        print("ERROR: no OpenVINO model for " + ", ".join(missing) + "; send the output above")
    with open(os.path.join(OUT, "export.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info, indent=1))
    return 0 if info["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
