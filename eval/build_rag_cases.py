"""
Turn the retrieval questions into assistant cases for Steps 7 and 8 of Objective 2.

    python eval\\build_rag_cases.py

Reads knowledge/retrieval_eval.jsonl (500 questions, split fixed in Step 4) and adds 24 new Hinglish questions that
nothing in the store information answers. Step 6 exempted Hinglish questions from the refusal fallback, and the
retrieval set had no unanswerable Hinglish questions, so these measure what that exemption costs. They were
written after Step 6 and are all on the test split; nothing has been tuned on them.

Writes:
    eval/rag_cases.jsonl          one case per question, in the harness's case format (mode "tools")
    eval/rag_pilot_ids.json       24 DEV cases for the Step 7 pilot, one or two per question type
    eval/v11_pilot_ids.json       20 DEV v1.1 tool cases for the Step 7 pilot (regression path)
    eval/rag_speed_ids.json       40 TEST cases for the Step 8 Tier A timing runs

Each case's "expected" block carries what Step 8 scores:
    behaviour     answer (the store information answers it), decline (nothing answers it: off-topic, not sold,
                  unknown policy), either (near miss: the honest answer is "no" or "not listed")
    must_include  the fact groups from the retrieval set (any phrase in a group counts)
    gold_ids      chunks that answer it; oracle_ids = what the oracle condition shows (gold, or the related
                  chunks for near misses, or nothing)
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "retrieval"))
from language import is_hinglish  # noqa: E402

DECLINE_HI = [["nahi", "nahin", "maaf", "sorry", "staff", "don't", "do not", "not", "sirf", "only"]]
NEW_HINGLISH = [
    # (subtype, query)
    ("off_topic", "Aaj baarish hogi kya?"),
    ("off_topic", "Kal ka cricket match kaun jeeta?"),
    ("off_topic", "Yahan paas mein accha khana kahan milega?"),
    ("off_topic", "Mujhe ek joke sunao na."),
    ("off_topic", "Railway station kaise jaana hai yahan se?"),
    ("off_topic", "Aaj petrol ka rate kya hai?"),
    ("off_topic", "Mera maths ka homework kar doge?"),
    ("off_topic", "Wi-Fi ka password kya hai?"),
    ("not_sold", "Rolex ki watch milegi kya?"),
    ("not_sold", "Kya aapke paas Apple Watch hai?"),
    ("not_sold", "Heart rate wali smartwatch dikhao."),
    ("not_sold", "Deewar wali ghadi bechte ho kya?"),
    ("not_sold", "Pocket watch milti hai kya?"),
    ("not_sold", "Sunglasses bhi milte hain kya yahan?"),
    ("not_sold", "Asli sone ki watch hai kya, solid gold wali?"),
    ("not_sold", "Fitness band chahiye, hai kya?"),
    ("missing_policy", "Kya aap Singapore mein delivery karte ho?"),
    ("missing_policy", "Students ke liye koi discount hai kya?"),
    ("missing_policy", "Foreign credit card se payment ho jayega?"),
    ("missing_policy", "Mumbai mein aapka store hai kya?"),
    ("missing_policy", "Online sasta mil raha hai, price match karoge?"),
    ("missing_policy", "Dial pe company ka logo lagwa sakte hain kya?"),
    ("missing_policy", "Shaadi ke liye watch kiraye pe milegi?"),
    ("missing_policy", "Veyra ka CEO kaun hai?"),
]


def behaviour(q):
    if q["answer_type"] == "fact":
        return "answer"
    if q["answer_type"] == "none" and not q["near_miss"]:
        return "decline"
    return "either"


def to_case(q, source, notes=""):
    oracle = q["gold_ids"] or q.get("related_ids", [])
    return {"id": q["id"], "category": "rag", "subcategory": q["subtype"], "mode": "tools",
            "language": q["language"], "difficulty": "", "messages": [{"role": "user", "content": q["query"]}],
            "context": None,
            "expected": {"behaviour": behaviour(q), "answer_type": q["answer_type"], "near_miss": q["near_miss"],
                         "must_include": q["facts"], "gold_ids": q["gold_ids"], "oracle_ids": oracle},
            "rubric": [], "source": source, "notes": notes, "split": q["split"], "version": "2.0", "set": "rag",
            "paired_with": None}


def main():
    with open(os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"), encoding="utf-8") as f:
        qs = [json.loads(l) for l in f if l.strip()]
    cases = [to_case(q, "knowledge/retrieval_eval.jsonl") for q in qs]
    seen = {q["query"].lower() for q in qs}
    for i, (sub, text) in enumerate(NEW_HINGLISH, 1):
        assert text.lower() not in seen, text
        assert is_hinglish(text), f"not detected as Hinglish: {text}"
        q = dict(id=f"R-HUN-{i:03d}", query=text, language="hinglish", subtype=sub, answer_type="none",
                 gold_ids=[], related_ids=[], facts=DECLINE_HI, near_miss=False, split="test")
        cases.append(to_case(q, "eval/build_rag_cases.py", "new after Step 6: measures the Hinglish bypass"))

    out = os.path.join(HERE, "rag_cases.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Pilot: dev only, so the test split stays untouched until Step 8.
    rng = random.Random(77)
    dev = [c for c in cases if c["split"] == "dev"]
    by = {}
    for c in dev:
        by.setdefault(c["subcategory"], []).append(c["id"])
    pilot = [rng.choice(sorted(v)) for _, v in sorted(by.items())]
    rest = sorted({c["id"] for c in dev} - set(pilot))
    pilot += rng.sample(rest, max(0, 24 - len(pilot)))
    with open(os.path.join(HERE, "rag_pilot_ids.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "Step 7 pilot: dev cases only, one per question type, topped up to 24 (seed 77)",
                   "ids": sorted(pilot)}, f, indent=1)

    with open(os.path.join(HERE, "eval_set_v1.1.jsonl"), encoding="utf-8") as f:
        v11 = [json.loads(l) for l in f if l.strip()]
    tdev = [c for c in v11 if c["split"] == "dev" and c["mode"] == "tools"]
    by = {}
    for c in tdev:
        by.setdefault(c["category"], []).append(c["id"])
    vp = []
    for _, v in sorted(by.items()):
        vp += rng.sample(sorted(v), min(3, len(v)))
    vp += rng.sample(sorted({c["id"] for c in tdev} - set(vp)), max(0, 20 - len(vp)))
    with open(os.path.join(HERE, "v11_pilot_ids.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "Step 7 pilot: 20 dev v1.1 tool cases, up to 3 per category (seed 77)",
                   "ids": sorted(vp[:20])}, f, indent=1)

    # Step 8 speed subset: 40 TEST cases for the Tier A CPU timing runs, stratified by expected behaviour
    srng = random.Random(91)
    test = [c for c in cases if c["split"] == "test"]
    sp = []
    for beh, n in (("answer", 26), ("decline", 7), ("either", 7)):
        sp += srng.sample(sorted(c["id"] for c in test if c["expected"]["behaviour"] == beh), n)
    with open(os.path.join(HERE, "rag_speed_ids.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "Step 8 Tier A timing subset: 40 test cases (26 answer, 7 decline, 7 near miss; seed 91)",
                   "ids": sorted(sp)}, f, indent=1)

    from collections import Counter
    n = Counter((c["split"], c["expected"]["behaviour"]) for c in cases)
    print(f"Wrote {out}: {len(cases)} cases ({len(NEW_HINGLISH)} new Hinglish unanswerable).")
    print("  " + ", ".join(f"{s} {b}: {k}" for (s, b), k in sorted(n.items())))
    print(f"Pilot: {len(pilot)} RAG dev cases, {len(vp[:20])} v1.1 dev tool cases.")


if __name__ == "__main__":
    main()
