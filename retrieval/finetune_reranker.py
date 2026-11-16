"""
Objective 3, Step 9b: fine-tune the MiniLM-L6 re-ranker on the generated Veyra pairs (CPU, about 15-30 minutes).

    python retrieval\\finetune_reranker.py
    python retrieval\\finetune_reranker.py --dry-run      # counts only, no torch needed

Settings fixed before the run (not tuned on any eval set): cross-encoder/ms-marco-MiniLM-L-6-v2 as the start,
1 epoch, batch 16, AdamW lr 2e-5, weight decay 0.01, 10% linear warm-up then linear decay, gradient clipping 1.0,
max 256 tokens per pair (the deployed length), binary cross-entropy on the raw score, seed 13. Each training
question gives 1 positive and 4 negative pairs.

A plain PyTorch loop over the CrossEncoder's own model and tokenizer, so it does not depend on the
sentence-transformers training API (which changed between versions).

Sanity check only (not an eval set): on the held-out generated questions, how often the positive outscores every
negative, before and after training. Writes models/reranker-veyra-minilm/ and
results_obj3/_rerank_step9/train_meta.json.
"""

import argparse
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bench_retrieval as B  # noqa: E402

BASE = "cross-encoder/ms-marco-MiniLM-L-6-v2"
HP = dict(epochs=1, batch_size=16, lr=2e-5, weight_decay=0.01, warmup=0.10, clip=1.0, max_length=256, seed=13)


def pairs(rows, text):
    out = []
    for r in rows:
        out.append((r["query"], text[r["pos"]], 1.0))
        out += [(r["query"], text[n], 0.0) for n in r["negs"]]
    return out


def genval_accuracy(model, rows, text):
    """Share of held-out generated questions whose positive outscores all its negatives."""
    ok = 0
    for r in rows:
        ids = [r["pos"]] + r["negs"]
        s = model.predict([(r["query"], text[i]) for i in ids], batch_size=16, show_progress_bar=False)
        ok += all(float(s[0]) > float(x) for x in s[1:])
    return ok / max(1, len(rows))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default=os.path.join(ROOT, "knowledge", "rerank_train.jsonl"))
    ap.add_argument("--val", default=os.path.join(ROOT, "knowledge", "rerank_genval.jsonl"))
    ap.add_argument("--corpus", default=os.path.join(ROOT, "knowledge", "corpus.jsonl"))
    ap.add_argument("--out", default=os.path.join(ROOT, "models", "reranker-veyra-minilm"))
    ap.add_argument("--meta", default=os.path.join(ROOT, "results_obj3", "_rerank_step9", "train_meta.json"))
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    text = {c["id"]: c["text"] for c in B.load_jsonl(a.corpus)}
    train, val = B.load_jsonl(a.train), B.load_jsonl(a.val)
    data = pairs(train, text)
    random.Random(HP["seed"]).shuffle(data)
    steps = math.ceil(len(data) / HP["batch_size"]) * HP["epochs"]
    print(f"{len(train)} training questions -> {len(data)} pairs, {steps} steps; {len(val)} gen-val questions")
    if a.dry_run:
        return 0

    import torch
    from sentence_transformers import CrossEncoder
    torch.manual_seed(HP["seed"])
    torch.set_num_threads(a.threads)
    model = CrossEncoder(BASE, max_length=HP["max_length"], device="cpu")
    before = genval_accuracy(model, val, text)
    print(f"gen-val before: {before:.1%}", flush=True)
    net, tok = model.model, model.tokenizer
    net.train()
    opt = torch.optim.AdamW(net.parameters(), lr=HP["lr"], weight_decay=HP["weight_decay"])
    warm = int(HP["warmup"] * steps)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: (s + 1) / max(1, warm) if s < warm else max(0.0, (steps - s) / max(1, steps - warm)))
    lossf = torch.nn.BCEWithLogitsLoss()
    t0, step, run = time.time(), 0, 0.0
    for _ in range(HP["epochs"]):
        for i in range(0, len(data), HP["batch_size"]):
            b = data[i:i + HP["batch_size"]]
            enc = tok([q for q, _, _ in b], [p for _, p, _ in b], truncation=True, max_length=HP["max_length"],
                      padding=True, return_tensors="pt")
            logits = net(**enc).logits.view(-1)
            loss = lossf(logits, torch.tensor([y for _, _, y in b], dtype=torch.float32))
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), HP["clip"])
            opt.step()
            sched.step()
            step += 1
            run = 0.98 * run + 0.02 * loss.item() if step > 1 else loss.item()
            if step % 50 == 0 or step == steps:
                el = time.time() - t0
                print(f"  step {step}/{steps}  loss {run:.3f}  {el / 60:.1f} min, about "
                      f"{el / step * (steps - step) / 60:.0f} min left", flush=True)
    net.eval()
    os.makedirs(a.out, exist_ok=True)
    net.save_pretrained(a.out)
    tok.save_pretrained(a.out)
    from fix_reranker_activation import ensure_raw     # keep the base model's raw scores (no sigmoid)
    ensure_raw(a.out)
    tuned = CrossEncoder(a.out, max_length=HP["max_length"], device="cpu")
    # the saved model must give raw scores like the base model (the fallback thresholds are on that scale)
    q, p = val[0]["query"], text[val[0]["pos"]]
    with torch.no_grad():
        raw = net(**tok([q], [p], truncation=True, max_length=HP["max_length"], return_tensors="pt")).logits.item()
    pred = float(tuned.predict([(q, p)], show_progress_bar=False)[0])
    after = genval_accuracy(tuned, val, text)
    meta = dict(base=BASE, hyperparameters=HP, n_train_questions=len(train), n_pairs=len(data), steps=steps,
                minutes=round((time.time() - t0) / 60, 1), genval_before=before, genval_after=after,
                raw_score_check={"logit": raw, "predict": pred, "same_scale": abs(raw - pred) < 1e-3},
                output=os.path.relpath(a.out, ROOT))
    os.makedirs(os.path.dirname(a.meta), exist_ok=True)
    with open(a.meta, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1))
    if not meta["raw_score_check"]["same_scale"]:
        print("WARNING: predict() does not return the raw score; send train_meta.json before going on.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
