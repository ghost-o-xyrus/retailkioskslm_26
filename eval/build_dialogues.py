"""
Objective 3, Step 6: hidden customer profiles for simulated discovery dialogues.

    python eval\\build_dialogues.py                     # 40 dev dialogues, seed 101 -> eval/o3_dialogues.jsonl
    python eval\\build_dialogues.py --split test --n 60 --seed 202 --append    # Step 14, fresh

Each profile: recipient (and age for a son or daughter), budget, occasion, strap preference, language (English 70%,
Hinglish 30%) and an opening message that is vague (no slots), partial (one slot) or detailed (three or more).
A profile is kept only if the catalogue has at least 3 watches that satisfy its gender, budget, style and strap, so
every dialogue can end in a good recommendation. The kiosk never sees the profile; harness/simulator.py answers for it.
"""

import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from tools import mock_tools  # noqa: E402

RECIPIENTS = ["wife", "husband", "father", "mother", "son", "daughter", "friend_m", "friend_f", "self_m", "self_f"]
GENDER = {"wife": "women", "husband": "men", "father": "men", "mother": "women", "friend_m": "men",
          "friend_f": "women", "self_m": "men", "self_f": "women"}
OCC_STYLE = {"office": ["formal"], "daily": ["casual"], "wedding": ["ethnic", "formal"], "sport": ["sport"],
             "party": ["fashion"]}
BUDGETS = [2500, 3000, 5000, 7000, 8000, 10000, 12000, 15000, 20000, 25000, 40000]
KID_BUDGETS = [1000, 1500, 2000, 2500]

VAGUE_EN = ["I want to buy a watch.", "Can you help me pick a watch?", "I'm looking for a watch.", "I need a gift."]
VAGUE_HI = ["Mujhe ek watch leni hai.", "Ek achhi watch dikhao.", "Watch lene aaya hoon, help karo."]
REL_EN = {"wife": "my wife", "husband": "my husband", "father": "my father", "mother": "my mother", "son": "my son",
          "daughter": "my daughter", "friend_m": "a male friend", "friend_f": "a female friend", "self_m": "myself",
          "self_f": "myself"}
REL_HI = {"wife": "Wife", "husband": "Husband", "father": "Papa", "mother": "Mummy", "son": "Bete", "daughter": "Beti",
          "friend_m": "Dost", "friend_f": "Saheli", "self_m": "Apne", "self_f": "Apne"}
OCC_EN = {"office": "for office wear", "daily": "for daily wear", "wedding": "for a wedding", "sport": "for the gym",
          "party": "for parties"}
OCC_HI = {"office": "office ke liye", "daily": "roz pehenne ke liye", "wedding": "shaadi ke liye", "sport": "gym ke liye",
          "party": "party ke liye"}
STRAP_EN = {"leather": "with a leather strap", "metal": "with a metal bracelet", "silicone": "with a silicone strap",
            "none": ""}
STRAP_HI = {"leather": "leather strap wali", "metal": "metal chain wali", "silicone": "silicone strap wali", "none": ""}


def gender_of(p):
    if p["recipient"] in ("son", "daughter"):
        return "kids" if p["age"] <= 12 else ("men" if p["recipient"] == "son" else "women")
    return GENDER[p["recipient"]]


def feasible(p):
    n = 0
    for style in OCC_STYLE[p["occasion"]]:
        args = {"gender": gender_of(p), "price_max": p["budget"], "limit": 10}
        if gender_of(p) != "kids":
            args["style"] = style
        if p["strap"] != "none":
            args["strap_material"] = p["strap"]
        n += mock_tools.search_catalogue(**args)["styles_matched"]
    return n >= 3


def opening(p, rng):
    hi = p["language"] == "hinglish"
    kind = p["opening"]
    if kind == "vague":
        return rng.choice(VAGUE_HI if hi else VAGUE_EN), []
    if kind == "partial":
        if rng.random() < 0.6:
            return (f"{REL_HI[p['recipient']]} ke liye watch chahiye." if hi else
                    rng.choice([f"I need a gift for {REL_EN[p['recipient']]}.",
                                f"I'm looking for a watch for {REL_EN[p['recipient']]}."])), ["recipient"]
        return (f"Budget {p['budget']} hai, kuch suggest karo." if hi else f"My budget is around {p['budget']:,}."), ["budget"]
    strap = (STRAP_HI if hi else STRAP_EN)[p["strap"]]
    if hi:
        text = f"{REL_HI[p['recipient']]} ke liye {OCC_HI[p['occasion']]} watch chahiye{', ' + strap if strap else ''}, {p['budget']} tak."
    else:
        text = f"A watch for {REL_EN[p['recipient']]} {OCC_EN[p['occasion']]}{', ' + strap if strap else ''}, under {p['budget']:,}."
    revealed = ["recipient", "occasion", "budget"] + (["strap"] if strap else [])
    if p["recipient"] in ("son", "daughter"):
        text += f" {'Umar' if hi else 'Age'} {p['age']}."
        revealed.append("age")
    return text, revealed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=101)
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "o3_dialogues.jsonl"))
    a = ap.parse_args()
    rng = random.Random(a.seed)
    out, tries = [], 0
    while len(out) < a.n and tries < 5000:
        tries += 1
        rec = rng.choice(RECIPIENTS)
        p = {"recipient": rec, "age": rng.choice([8, 10, 12, 16, 22]) if rec in ("son", "daughter") else None,
             "occasion": rng.choice(list(OCC_STYLE)), "strap": rng.choice(["leather", "metal", "silicone", "none"]),
             "language": "hinglish" if rng.random() < 0.3 else "en",
             "opening": rng.choice(["vague", "vague", "partial", "partial", "detailed"])}
        p["budget"] = rng.choice(KID_BUDGETS if p["age"] is not None and p["age"] <= 12 else BUDGETS)
        if p["age"] is not None and p["age"] <= 12:
            p["occasion"] = rng.choice(["daily", "sport"])
        if not feasible(p):
            continue
        p["gender"] = gender_of(p)
        p["styles"] = OCC_STYLE[p["occasion"]]
        text, revealed = opening(p, rng)
        p.update(id=f"DLG-{a.split[0].upper()}{len(out) + 1:03d}", split=a.split, category="dialogue",
                 subcategory=p["opening"], mode="tools", set="dialogue", context=None, expected={"behaviour": "dialogue"},
                 messages=[{"role": "user", "content": text}], opening_reveals=revealed, seed=a.seed)
        out.append(p)
    mode = "a" if a.append else "w"
    with open(a.out, mode, encoding="utf-8") as f:
        for p in out:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"{a.out}: {len(out)} {a.split} dialogues ({tries} drawn); openings {dict(Counter(p['opening'] for p in out))}, "
          f"languages {dict(Counter(p['language'] for p in out))}")


if __name__ == "__main__":
    main()
