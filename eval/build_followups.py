"""
Objective 3, Step 11: follow-up cases (two customer turns), generated from the catalogue.

    python eval\\build_followups.py          # writes eval/rag_followups.jsonl (dev and test)

Each case: the customer asks about a watch, the kiosk's earlier reply names it (name, code, price, size, dial,
strap: never the fact asked next), then the customer asks a follow-up that does not name it again:
  followup_fact     glass, water resistance, warranty, origin, case material, movement ("What glass does it have?")
  followup_colour   "Does it come with a black dial?" (yes or no, from the design's variants)
  followup_stock    "Is it in stock here?" (from this store's stock of the SKU named in the earlier reply)
                    (colour and stock are scored by polarity: score_rag.polarity_correct)
  followup_switch   a new, self-contained store question after a product turn (the follow-up path must not hurt it)
English and Hinglish (about a third). Expected answers come from the catalogue fields and the FAQ text, checked the
same way as the store questions (score_rag: every must-include group). Designs are split between dev and test
(no design appears in both); the test half is kept for Step 14. Seed 303.
"""

import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from tools import mock_tools  # noqa: E402

SEED = 303
PER_SPLIT = {"followup_fact": 30, "followup_colour": 10, "followup_stock": 10, "followup_switch": 10}

FACTS = {   # field -> (English questions, Hinglish questions, must-include builder)
    "glass": (["What glass does it have?", "Is the glass sapphire?", "And the glass?"],
              ["Iska glass kaun sa hai?", "Isme kaun sa glass hai?"],
              lambda st: [[st["glass"].lower()]]),
    "water_resistance_m": (["Is it water resistant?", "How water resistant is it?", "Can I swim with it?"],
                           ["Ye waterproof hai kya?", "Iska water resistance kitna hai?"],
                           lambda st: [[str(st["water_resistance_m"])]]),
    "warranty_movement_months": (["What warranty does it have?", "How long is the warranty on it?"],
                                 ["Iski warranty kitni hai?", "Warranty kitne time ki hai?"],
                                 lambda st: [[str(st["warranty_movement_months"]),
                                              str(st["warranty_movement_months"] // 12) + " year"]]),
    "country_of_origin": (["Where is it made?", "Which country is it made in?"],
                          ["Ye kahan bani hai?", "Iska made in kya hai?"],
                          lambda st: [[st["country_of_origin"].lower()]]),
    "case_material": (["What is the case made of?", "What's the case material?"],
                      ["Iska case kis cheez ka hai?"],
                      lambda st: [[w for w in re.findall(r"[a-z]+", st["case_material"].lower()) if len(w) > 3][:1]]),
    "movement": (["Is it automatic or quartz?", "What movement does it use?"],
                 ["Ye automatic hai ya quartz?"],
                 lambda st: [[st["movement"].lower()]]),
}
COLOURS = ["black", "white", "blue", "green", "silver", "grey", "brown", "gold", "pink", "red"]
SWITCH = [  # (question, faq id, must-include)
    ("What are your store hours?", "faq:what-are-the-store-hours", [["22", "10 pm", "10pm", "10:00"]]),
    ("Which payment methods do you accept?", "faq:which-payment-methods-are-accepted", [["upi"]]),
    ("Do you offer gift wrapping?", "faq:do-you-offer-gift-wrapping", [["free", "yes"]]),
    ("Store kab tak khula hai?", "faq:what-are-the-store-hours", [["22", "10 pm", "10pm", "10 baje", "10:00"]]),
    ("Gift wrapping milta hai kya?", "faq:do-you-offer-gift-wrapping", [["free", "haan", "yes", "muft"]]),
]
OPEN_EN = ["Tell me about the {n}.", "I like the {n}.", "Show me the {n}, please.", "What's the price of the {n}?"]
OPEN_HI = ["{n} ke baare mein batao.", "Mujhe {n} pasand hai.", "{n} dikhao."]


def earlier_reply(st, sku):
    strap = f"{sku['strap_colour']} {sku['strap_material']}" if sku.get("strap_colour") else sku["strap_material"]
    who = {"men": "men's", "women": "women's"}.get(st["gender"], st["gender"])
    return (f"The {st['style_name']} ({sku['sku']}) is a {who} {st['style_tag']} watch at Rs {sku['mrp']:,}: "
            f"{st['case_diameter_mm']} mm, {sku['dial_colour']} dial, {strap}. Would you like to know more?")


def case(cid, split, sub, lang, opening, reply, follow, must, gold):
    return {"id": cid, "category": "rag", "subcategory": sub, "mode": "tools", "language": lang, "difficulty": "",
            "messages": [{"role": "user", "content": opening}, {"role": "assistant", "content": reply},
                         {"role": "user", "content": follow}],
            "context": None, "expected": {"behaviour": "answer", "answer_type": "fact", "near_miss": False,
                                          "must_include": must, "gold_ids": gold, "oracle_ids": gold},
            "rubric": [], "source": "eval/build_followups.py", "notes": "", "split": split, "version": "1.0",
            "set": "followup", "paired_with": None}


def main(argv=None):
    rng = random.Random(SEED)
    db = mock_tools._load()
    store = db["this_store"]
    skus_by_style = {}
    for s in db["skus"].values():
        if s["status"] == "active":
            skus_by_style.setdefault(s["style_id"], []).append(s)
    styles = sorted(sid for sid, st in db["styles"].items() if st["status"] == "active" and skus_by_style.get(sid)
                    and st["gender"] != "kids")
    rng.shuffle(styles)
    halves = {"dev": styles[: len(styles) // 2], "test": styles[len(styles) // 2:]}
    out = []
    for split, pool in halves.items():
        it = iter(pool)
        n = 0
        for sub, k in PER_SPLIT.items():
            for i in range(k):
                hi = rng.random() < 0.34
                lang = "hinglish" if hi else "en"
                sid = next(it)
                st, sku = db["styles"][sid], rng.choice(skus_by_style[sid])
                opening = rng.choice(OPEN_HI if hi else OPEN_EN).format(n=st["style_name"])
                reply = earlier_reply(st, sku)
                gold, pol = [f"product:{sid}"], None
                if sub == "followup_fact":
                    field = rng.choice([f for f in FACTS if st.get(f) not in (None, "", "not listed")])
                    en, hq, mk = FACTS[field]
                    follow, must = rng.choice(hq if hi else en), mk(st)
                elif sub == "followup_colour":
                    have = {s["dial_colour"] for s in skus_by_style[sid]}
                    want_yes = rng.random() < 0.5 and bool(have - {sku["dial_colour"]})
                    # a "no" colour appears nowhere on the design (dial, strap or case), so the answer is unambiguous
                    anywhere = " ".join(f"{s['dial_colour']} {s.get('strap_colour') or ''} {s.get('case_finish') or ''}"
                                        for s in skus_by_style[sid]).lower()
                    pick = rng.choice(sorted(have - {sku["dial_colour"]})) if want_yes else \
                        rng.choice([c for c in COLOURS if c not in anywhere])
                    follow = (f"Kya ye {pick} dial mein aati hai?" if hi else f"Does it come with a {pick} dial?")
                    must, pol = [], ("yes", pick) if pick in have else ("no", pick)
                elif sub == "followup_stock":
                    inv = db["inventory"].get((store, sku["sku"]), {"qty_display": 0, "qty_backroom": 0})
                    follow = "Kya ye stock mein hai?" if hi else "Is it in stock here?"
                    must, pol = [], ("in_stock" if inv["qty_display"] + inv["qty_backroom"] > 0 else "out_of_stock", None)
                else:
                    q, faq, must = rng.choice([s for s in SWITCH if (is_hi(s[0]) == hi)])
                    follow, gold = q, [faq]
                n += 1
                c = case(f"FUP-{split[0].upper()}{n:03d}", split, sub, lang, opening, reply, follow, must, gold)
                if pol:
                    c["expected"].update(polarity=pol[0], polarity_word=pol[1])
                out.append(c)
    path = os.path.join(ROOT, "eval", "rag_followups.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"Wrote {len(out)} follow-up cases ({sum(c['split'] == 'dev' for c in out)} dev) to {path}")
    return 0


def is_hi(q):
    return any(w in q.lower().split() for w in ("kab", "kya", "hai", "milta", "khula"))


if __name__ == "__main__":
    sys.exit(main())
