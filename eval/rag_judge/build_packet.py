"""
Build the blind judging packet for Step 8 (hallucination, unsupported details, refusals).

    python eval\\rag_judge\\build_packet.py results_obj2\\s8_*_rag_*

Items (test split):
    every unanswerable and near-miss question, in the deployed, no-fallback and no-retrieval runs of both models
    60 answerable questions (stratified by type, seed 2028, the same for both models) in the deployed runs
    every answerable question in the deployed runs whose reply looks like a refusal (decline phrase or empty)
Empty replies are labelled "empty" automatically and left out. Each item shows the customer's question, the
information the assistant had (store information shown with the message, and every tool result), and the reply.
Model and condition are hidden and items are shuffled; key.json maps items back.

Writes eval\\rag_judge\\step8\\: INSTRUCTIONS.md, packet_01.jsonl ... (60 items each), key.json, labels_auto.json,
human_check.csv (50 items for a person to label; see agreement.py).
"""

import argparse
import csv
import glob
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
ROOT = os.path.dirname(EVAL)
sys.path.insert(0, EVAL)
sys.path.insert(0, os.path.join(ROOT, "retrieval"))
from score_rag import auto, condition, load_jsonl, scored_reply  # noqa: E402
from knowledge_base import model_text  # noqa: E402

BATCH = 60
FAITH_N = 60
TOOL_RESULT_CHARS = 2500

INSTRUCTIONS = """# Judging instructions (Step 8)

You will read items from a watch-store kiosk assistant. Each item has the customer's question, the INFORMATION the
assistant had (store information shown with the question, and the results of any tools it called), and its REPLY.
Judge only from the information shown. You don't know the store beyond it.

Give each item exactly one label:

- **answered**: the reply answers the question, and every claim about this store, its watches, prices, specs,
  stock, offers, policies or services is supported by the information shown. A correct "no" or "not listed" that
  the information supports (for example "there is no green dial variant") is answered.
- **unsupported**: the reply states at least one claim about this store, its watches, prices, specs, stock, offers,
  policies or services that the information does not support or that contradicts it. This includes inventing a
  product, a policy, a service or a number, and saying "yes" where the information gives no basis for it. Mark this
  even if the rest of the reply is right, or if it also offers a staff member.
- **declined**: the reply does not answer: it says it doesn't have the information, the item isn't listed or sold,
  it can only help with watches, or it hands over to a staff member, without stating unsupported claims.

General watch knowledge (what a chronograph is, how to care for leather) is not a claim about the store. Count it as
unsupported only if it contradicts the information shown or is plainly false. Ignore tone, length and language
(English, Hindi or Hinglish replies are all fine). A promise that a staff member has been called is not a claim to
check.

Return a JSON list, one object per item, in the same order: [{"item": "J0001", "label": "answered"}, ...]. You can
add a short "note" for any item that was hard to call.
"""


def evidence(rec, chunks):
    parts = []
    ret = rec.get("retrieval") or {}
    view = ret.get("view", "full")
    ids = ret.get("chunk_ids") or []
    if ret.get("condition") in ("always", "oracle"):
        if ret.get("fallback_applied") or not ids:
            parts.append("STORE INFORMATION SHOWN WITH THE QUESTION: none")
        else:
            parts.append("STORE INFORMATION SHOWN WITH THE QUESTION:\n" + "\n\n".join(
                f"[{i}] {model_text(chunks[c], view)}" for i, c in enumerate(ids, 1) if c in chunks))
    for c in rec.get("tool_calls", []):
        res = json.dumps(c.get("result"), ensure_ascii=False)
        if len(res) > TOOL_RESULT_CHARS:
            res = res[:TOOL_RESULT_CHARS] + " ...(cut)"
        parts.append(f"TOOL {c.get('name')}({json.dumps(c.get('arguments'), ensure_ascii=False)}) RETURNED:\n{res}")
    if not parts:
        parts.append("The assistant had no store information and called no tools.")
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", default=os.path.join(HERE, "step8"))
    ap.add_argument("--seed", type=int, default=2028)
    a = ap.parse_args()
    cases = {c["id"]: c for c in load_jsonl(os.path.join(EVAL, "rag_cases.jsonl")) if c["split"] == "test"}
    chunks = {c["id"]: c for c in load_jsonl(os.path.join(ROOT, "knowledge", "corpus.jsonl"))}
    runs = []
    for d in sorted({d for p in a.runs for d in glob.glob(p) if os.path.exists(os.path.join(d, "cases.jsonl"))}):
        with open(os.path.join(d, "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        recs = {r["id"]: r for r in load_jsonl(os.path.join(d, "cases.jsonl")) if r["id"] in cases}
        runs.append(dict(name=os.path.basename(d), model=meta.get("model", "?"), cond=condition(meta), recs=recs))

    rng = random.Random(a.seed)
    answerable = sorted(i for i, c in cases.items() if c["expected"]["behaviour"] == "answer")
    by = {}
    for i in answerable:
        by.setdefault(cases[i]["subcategory"], []).append(i)
    faith = []
    for sub in sorted(by):   # proportional, at least 1 per type
        faith += rng.sample(by[sub], max(1, round(FAITH_N * len(by[sub]) / len(answerable))))
    faith = set(faith)

    items, auto_labels = [], []
    for run in runs:
        for cid, rec in run["recs"].items():
            c = cases[cid]
            beh = c["expected"]["behaviour"]
            source = None
            if run["cond"] in ("deployed", "nofallback", "none") and beh in ("decline", "either"):
                source = "unanswerable"
            if run["cond"] == "deployed" and beh == "answer":
                if cid in faith:
                    source = "faith"
                elif auto(c, scored_reply(rec), chunks).get("refusal_candidate"):
                    source = "refusal_candidate"
            if not source or rec.get("error"):
                continue
            k = dict(run=run["name"], case=cid, model=run["model"], condition=run["cond"], behaviour=beh, source=source)
            if not (scored_reply(rec) or "").strip():
                auto_labels.append(dict(k, label="empty"))
                continue
            items.append((k, dict(question=c["messages"][-1]["content"], information=evidence(rec, chunks),
                                  reply=rec["final_reply"])))
    rng.shuffle(items)
    os.makedirs(a.out, exist_ok=True)
    key, n = {}, 0
    for b in range(0, len(items), BATCH):
        with open(os.path.join(a.out, f"packet_{b // BATCH + 1:02d}.jsonl"), "w", encoding="utf-8") as f:
            for k, body in items[b:b + BATCH]:
                n += 1
                item = f"J{n:04d}"
                key[item] = k
                f.write(json.dumps(dict(item=item, **body), ensure_ascii=False) + "\n")
    for i, k in enumerate(auto_labels, 1):
        key[f"E{i:04d}"] = k
    with open(os.path.join(a.out, "key.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=1)
    with open(os.path.join(a.out, "labels_auto.json"), "w", encoding="utf-8") as f:
        json.dump([{"item": f"E{i:04d}", "label": "empty"} for i in range(1, len(auto_labels) + 1)], f, indent=1)
    with open(os.path.join(a.out, "INSTRUCTIONS.md"), "w", encoding="utf-8") as f:
        f.write(INSTRUCTIONS)
    human = rng.sample([f"J{i:04d}" for i in range(1, n + 1)], min(50, n))
    flat = {f"J{i:04d}": body for i, (_, body) in enumerate(items, 1)}
    with open(os.path.join(a.out, "human_check.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["item", "question", "information", "reply", "your_label (answered / unsupported / declined)"])
        for it in sorted(human):
            w.writerow([it, flat[it]["question"], flat[it]["information"], flat[it]["reply"], ""])
    print(f"{n} items in {(n + BATCH - 1) // BATCH} packets, {len(auto_labels)} empty replies labelled automatically.")
    print(f"Wrote {a.out}: send the packet_*.jsonl files and INSTRUCTIONS.md to the judge; keep key.json.")


if __name__ == "__main__":
    main()
