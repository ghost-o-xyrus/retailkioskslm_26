"""
Objective 3, Step 15: the blind judging packet for the test set O3-T (hallucination, unsupported details and
false refusals), from the Step 14 runs. The same protocol and instructions as Objective 2, Step 8.

    python eval\\rag_judge\\build_packet_o3.py

Items, from the store-question runs of Step 14 (laptop, Vulkan), both models:
    every unanswerable (must decline) and near-miss question, in O3-final and in O3-B0
    60 answerable questions (stratified by type, seed 2031, the same for both models and both configurations)
    every other answerable question whose reply looks like a refusal (decline phrase or empty), in both configurations
Empty replies are labelled "empty" automatically and left out. Each item shows the customer's question, the
information the assistant had (the store information shown with the message, in the view the model saw, and every
tool result, including tools the kiosk ran itself) and the reply the customer saw. Model, configuration and run
are hidden and items are shuffled; key.json maps items back.

Writes eval/rag_judge/step15/: INSTRUCTIONS.md, packet_01.jsonl ... (60 items each), key.json, labels_auto.json,
human_check.csv (50 items for a person to label). Then:
    the judge labels every packet  ->  labels_*.json in the same folder
    python eval\\rag_judge\\agreement.py eval\\rag_judge\\step15\\human_check_filled.csv
    python eval\\rag_judge\\summary_o3.py
"""

import argparse
import csv
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
ROOT = os.path.dirname(EVAL)
sys.path.insert(0, HERE)
sys.path.insert(0, EVAL)
sys.path.insert(0, os.path.join(ROOT, "retrieval"))
from build_packet import INSTRUCTIONS, BATCH, FAITH_N, TOOL_RESULT_CHARS  # noqa: E402
from score_rag import auto, load_jsonl, scored_reply  # noqa: E402
from knowledge_base import model_text  # noqa: E402

RUNS = {"o3t_final_2b_rag": ("Qwen3.5-2B", "final"), "o3t_b0_2b_rag": ("Qwen3.5-2B", "b0"),
        "o3t_final_4b_rag": ("Qwen3.5-4B", "final"), "o3t_b0_4b_rag": ("Qwen3.5-4B", "b0")}


def evidence(rec, chunks):
    """What the model had: the cards shown with the message (in its view) and every tool result."""
    parts = []
    ret = rec.get("retrieval") or {}
    view, q = ret.get("view", "full"), ret.get("query")
    ids = ret.get("chunk_ids") or []
    if ret.get("condition") in ("always", "oracle"):
        if ret.get("fallback_applied") or not ids:
            parts.append("STORE INFORMATION SHOWN WITH THE QUESTION: none")
        else:
            parts.append("STORE INFORMATION SHOWN WITH THE QUESTION:\n" + "\n\n".join(
                f"[{i}] {model_text(chunks[c], view, q)}" for i, c in enumerate(ids, 1) if c in chunks))
    for c in rec.get("tool_calls") or []:
        res = json.dumps(c.get("result"), ensure_ascii=False)
        if len(res) > TOOL_RESULT_CHARS:
            res = res[:TOOL_RESULT_CHARS] + " ...(cut)"
        parts.append(f"TOOL {c.get('name')}({json.dumps(c.get('arguments'), ensure_ascii=False)}) RETURNED:\n{res}")
    if not parts:
        parts.append("The assistant had no store information and called no tools.")
    return "\n\n".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(ROOT, "results_obj3"))
    ap.add_argument("--out", default=os.path.join(HERE, "step15"))
    ap.add_argument("--seed", type=int, default=2031)
    a = ap.parse_args(argv)
    cases = {c["id"]: c for c in load_jsonl(os.path.join(EVAL, "rag_cases_o3t.jsonl")) if c["split"] == "test"}
    chunks = {c["id"]: c for c in load_jsonl(os.path.join(ROOT, "knowledge", "corpus.jsonl"))}
    runs = []
    for name, (model, cond) in RUNS.items():
        p = os.path.join(a.results, name, "cases.jsonl")
        if not os.path.exists(p):
            raise SystemExit(f"missing {p}: the Step 14 runs are needed")
        recs = {}
        for line in open(p, encoding="utf-8"):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("repeat", 0) == 0 and r["id"] in cases:
                recs[r["id"]] = r
        runs.append(dict(name=name, model=model, cond=cond, recs=recs))

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
            if rec.get("error"):
                continue
            cand = beh == "answer" and bool(auto(c, scored_reply(rec), chunks).get("refusal_candidate"))
            if beh in ("decline", "either"):
                source = "unanswerable" if beh == "decline" else "near_miss"
            elif cid in faith:
                source = "faith"
            elif cand:
                source = "refusal_candidate"
            else:
                continue
            k = dict(run=run["name"], case=cid, model=run["model"], condition=run["cond"], behaviour=beh,
                     subcategory=c["subcategory"], language=c.get("language"), source=source,
                     route=rec.get("route"), flags=rec.get("flags") or [],
                     refusal_candidate=cand)
            if not (scored_reply(rec) or "").strip():
                auto_labels.append(dict(k, label="empty"))
                continue
            items.append((k, dict(question=c["messages"][-1]["content"], information=evidence(rec, chunks),
                                  reply=rec["final_reply"])))
    rng.shuffle(items)
    os.makedirs(a.out, exist_ok=True)
    for fn in os.listdir(a.out):
        if fn.startswith("packet_") and fn.endswith(".jsonl"):
            os.remove(os.path.join(a.out, fn))
    key, n = {}, 0
    for b in range(0, len(items), BATCH):
        with open(os.path.join(a.out, f"packet_{b // BATCH + 1:02d}.jsonl"), "w", encoding="utf-8") as f:
            for k, body in items[b:b + BATCH]:
                n += 1
                item = f"J{n:04d}"
                key[item] = k
                f.write(json.dumps(dict(item=item, **body), ensure_ascii=False) + "\n")
    auto_rows = []
    for i, k in enumerate(auto_labels, 1):
        key[f"E{i:04d}"] = k
        auto_rows.append({"item": f"E{i:04d}", "label": "empty"})
    with open(os.path.join(a.out, "key.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out, "labels_auto.json"), "w", encoding="utf-8") as f:
        json.dump(auto_rows, f, indent=1)
    with open(os.path.join(a.out, "INSTRUCTIONS.md"), "w", encoding="utf-8") as f:
        f.write(INSTRUCTIONS.replace("(Step 8)", "(Objective 3, Step 15)"))
    human = rng.sample([f"J{i:04d}" for i in range(1, n + 1)], min(50, n))
    flat = {f"J{i:04d}": body for i, (_, body) in enumerate(items, 1)}
    with open(os.path.join(a.out, "human_check.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["item", "question", "information", "reply", "your_label (answered / unsupported / declined)"])
        for it in sorted(human):
            w.writerow([it, flat[it]["question"], flat[it]["information"], flat[it]["reply"], ""])
    src = {}
    for k, _ in items:
        src[k["source"]] = src.get(k["source"], 0) + 1
    print(f"{n} items in {(n + BATCH - 1) // BATCH} packets ({', '.join(f'{v} {k}' for k, v in sorted(src.items()))}); "
          f"{len(auto_labels)} empty replies labelled automatically.")
    print(f"Wrote {a.out}. Send the whole step15 folder except key.json; keep key.json and human_check.csv here.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
