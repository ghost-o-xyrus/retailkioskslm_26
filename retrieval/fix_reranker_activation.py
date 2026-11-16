"""
Objective 3, Step 9: make a saved re-ranker return raw scores, like the deployed MiniLM.

    python retrieval\\fix_reranker_activation.py                      # models/reranker-veyra-minilm
    python retrieval\\fix_reranker_activation.py <model folder>

Why: the fine-tuned model was saved from the underlying Hugging Face model, so its config lost the base model's
"no activation" setting. sentence-transformers then applies a sigmoid, which (a) puts scores on a 0-1 scale while
the fallback thresholds are raw scores, and (b) squeezes all strong matches towards 1.0, where near-ties can no
longer be ranked. The training itself is unaffected: this only restores the setting in config.json, then checks
that predict() equals the raw model output. Takes seconds; no retraining.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IDENTITY = "torch.nn.modules.linear.Identity"


def raw_and_predict(path, q="What glass does the Meridian Sable have?", p="Veyra Meridian Sable. Glass: Sapphire."):
    import torch
    from sentence_transformers import CrossEncoder
    m = CrossEncoder(path, max_length=256, device="cpu")
    with torch.no_grad():
        raw = m.model(**m.tokenizer([q], [p], truncation=True, max_length=256, return_tensors="pt")).logits.item()
    return raw, float(m.predict([(q, p)], show_progress_bar=False)[0])


def patch(path):
    cfg_path = os.path.join(path, "config.json")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["sbert_ce_default_activation_function"] = IDENTITY                 # older sentence-transformers
    st = cfg.get("sentence_transformers") or {}
    st["activation_fn"] = IDENTITY                                         # newer sentence-transformers
    cfg["sentence_transformers"] = st
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def ensure_raw(path):
    raw, pred = raw_and_predict(path)
    if abs(raw - pred) < 1e-3:
        return True, raw, pred, "already raw"
    patch(path)
    raw, pred = raw_and_predict(path)
    return abs(raw - pred) < 1e-3, raw, pred, "config patched"


def main(argv=None):
    path = (argv or sys.argv[1:] or [os.path.join(ROOT, "models", "reranker-veyra-minilm")])[0]
    ok, raw, pred, how = ensure_raw(path)
    print(f"{path}: raw {raw:.4f}, predict {pred:.4f} ({how}) -> {'OK' if ok else 'STILL DIFFERENT'}")
    meta = os.path.join(ROOT, "results_obj3", "_rerank_step9", "train_meta.json")
    if ok and os.path.exists(meta):
        with open(meta, encoding="utf-8") as f:
            m = json.load(f)
        m["raw_score_check_after_fix"] = {"logit": raw, "predict": pred, "same_scale": True, "how": how}
        with open(meta, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
