"""
Build eval set v1.1 = v1.0 core (150 cases, unchanged) + an expansion.

    python eval/build_eval_set.py     # v1.0 core   -> eval/eval_set.jsonl
    python eval/build_eval_v11.py     # v1.1 total  -> eval/eval_set_v1.1.jsonl (+ overview CSV)

Why an expansion (see eval/README.md, "v1.1"):
  - 150 cases can only separate models that differ by ~12+ points; close rivals need ~300 test cases.
  - Only 5 no-tool cases; calling tools when none are needed is a standard failure to measure.
  - Hinglish was 15 unpaired cases; v1.1 translates English core cases so the language gap is
    measured on the same questions (paired_with).
  - All v1.0 questions came from one writer; v1.1 adds new phrasings and new product instances.

Each case gets "set": "core" or "expansion". Core cases keep their v1.0 ids and splits.
Expansion cases are 85% test, 15% dev.
"""

import copy
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_eval_set as core  # noqa: E402  (loads catalogue data and helpers)
from checks import REFUSAL_PHRASES  # noqa: E402

from build_eval_set import (EQ, RANGE, HAS, OPT, call, exp, spec_block, price_alts, mm_alts, wr_alts,  # noqa: E402
                            months_alts, STRAP_WORDS, MOVEMENT_WORDS, UNKNOWN_PHRASES, NOT_FOUND_PHRASES,
                            NEGATIVE_PHRASES, RUBRIC_CLARIFY, RUBRIC_RECOMMEND, RUBRIC_COMPARE, ACTIVE, STORES,
                            DEFECTS, THIS, qty, style_of, doc)

VERSION = "1.1"
SEED = 1101
REF = REFUSAL_PHRASES
core.REFUSAL_LIKE = REF

PREFIX = {"grounded_qa": "GQA", "discovery": "DSC", "comparison": "CMP", "tool_selection": "TSL",
          "refusal": "REF", "handoff": "HND", "hinglish": "HIN"}


def load_core():
    with open(os.path.join(HERE, "eval_set.jsonl"), encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]
    for c in cases:
        c["set"] = "core"
        c["version"] = VERSION
    return cases


def used_skus(cases):
    out = set()
    for c in cases:
        for part in c["source"].replace(",", ":").split(":"):
            if part in core.SKUS:
                out.add(part)
    return out


def build_expansion(rng, core_cases):
    core.CASES.clear()
    add = core.add
    taken = used_skus(core_cases)
    fresh = [k for k in ACTIVE if k["sku"] not in taken]
    rng.shuffle(fresh)
    it = iter(fresh)

    def nxt(pred=lambda k: True):
        for k in it:
            if pred(k):
                return k
        # fall back to any active SKU if fresh ones run out
        pool = [k for k in ACTIVE if pred(k)]
        return rng.choice(pool)

    care, faq, service, warranty, returns = (doc("care.md"), doc("faq.md"), doc("service.md"),
                                             doc("warranty.md"), doc("returns.md"))

    # ---------------- grounded_qa (+20) ----------------
    qs = [
        ("water_resistance", "What's the water resistance on this one?", lambda k, s: [wr_alts(s["water_resistance_m"])]),
        ("case_size", "What size is the case in mm?", lambda k, s: [mm_alts(s["case_diameter_mm"])]),
        ("glass", "What crystal is on the front?", lambda k, s: [[s["glass"].lower()]]),
        ("strap", "Is that a leather strap or metal?", lambda k, s: [STRAP_WORDS[k["strap_material"]]]),
        ("warranty", "How long is the warranty on the movement?", lambda k, s: [months_alts(s["warranty_movement_months"])]),
        ("movement", "Quartz or automatic?", lambda k, s: [MOVEMENT_WORDS[s["movement"]]]),
        ("price", "What's the MRP?", lambda k, s: [price_alts(k["mrp"])]),
        ("case_size", "Will it look big on a small wrist? How wide is it?", lambda k, s: [mm_alts(s["case_diameter_mm"])]),
        ("water_resistance", "Is it okay to wear while washing hands? What's it rated for?", lambda k, s: [wr_alts(s["water_resistance_m"])]),
        ("price", "Price kya hai? I mean, how much is it?", lambda k, s: [price_alts(k["mrp"])]),
        ("dial", "What colour is the dial?", lambda k, s: [[k["dial_colour"]]]),
        ("movement", "Do I need to change a battery in this?", lambda k, s: [MOVEMENT_WORDS[s["movement"]]]),
    ]
    for i, (sub, q, facts) in enumerate(qs):
        k = nxt(lambda k: style_of(k)["case_thickness_mm"] != "")
        s = style_of(k)
        add("grounded_qa", f"spec_{sub}", q, exp("answer", must=facts(k, s)), mode="grounded",
            context=spec_block(k["sku"], noisy=(i % 2 == 0)), difficulty="easy",
            source=f"skus.csv:{k['sku']}")
    docq = [
        ("doc_faq", "Is no-cost EMI available?", faq, [["yes"], ["5,000", "5000"]]),
        ("doc_faq", "How much does engraving cost?", faq, [["500"]]),
        ("doc_faq", "How long does it take to get a watch from another store?", faq, [["1 to 2 days", "1-2 days", "1–2 days", "one to two days"]]),
        ("doc_warranty", "How long does a warranty claim take?", warranty, [["7 working days", "seven working days", "7 days"]]),
        ("doc_care", "I left my automatic watch in a drawer for 3 days and it stopped. Is it broken?", care, [NEGATIVE_PHRASES + ["normal"], ["40 hours", "40 hrs"]]),
        ("doc_care", "Can my phone's magnetic case affect my watch?", care, [["yes", "can affect", "magnet"]]),
        ("doc_service", "How often should an automatic watch be serviced?", service, [["4 to 5 years", "4-5 years", "4–5 years", "four to five years"]]),
        ("doc_returns", "I bought a watch on sale. Can I get a refund?", returns, [NEGATIVE_PHRASES, ["exchange", "exchanged"]]),
    ]
    for sub, q, ctx, must in docq:
        add("grounded_qa", sub, q, exp("answer", must=must), mode="grounded", context=ctx, difficulty="easy",
            source=f"docs/{sub.split('_')[1]}.md")

    # ---------------- discovery (+38) ----------------
    vague = [
        ("Help me find a watch.", ["budget", "recipient", "occasion"]),
        ("I'm looking for a present.", ["budget", "recipient", "occasion"]),
        ("Something stylish, please.", ["budget", "recipient", "occasion"]),
        ("Which watch is best?", ["budget", "recipient", "occasion"]),
        ("My dad's birthday is next week.", ["budget", "occasion", "strap"]),
        ("I need something for my anniversary.", ["budget", "recipient"]),
        ("Show me your best sellers for women.", ["budget", "occasion"]),
        ("I want a watch for college.", ["budget", "recipient", "strap"]),
        ("Need a watch for daily wear.", ["budget", "recipient"]),
        ("What's a good watch for a teenager?", ["budget", "recipient", "occasion"]),
        ("I want a premium watch.", ["budget", "recipient", "occasion"]),
        ("Kuch dikhao.", ["budget", "recipient", "occasion"]),
    ]
    for q, slots in vague:
        add("discovery", "clarify", q, exp("clarify", slots=slots), difficulty="medium", rubric=RUBRIC_CLARIFY,
            source="hand-written", language="hinglish" if q.startswith("Kuch") else "en")
    spec = [
        ("Leather strap watch for men, formal, under 9,000.", dict(gender=EQ("men"), strap_material=EQ("leather"), style=EQ("formal"), price_max=RANGE(8500, 9000))),
        ("Women's watch on a mesh strap.", dict(gender=EQ("women"), strap_material=EQ("mesh"))),
        ("A men's chronograph with a metal bracelet, budget 12k.", dict(gender=EQ("men"), strap_material=EQ("metal"), price_max=RANGE(11000, 12500))),
        ("Kids' analog watch to learn time, under 1,000.", dict(gender=EQ("kids"), price_max=RANGE(900, 1000))),
        ("Unisex digital watch for the gym.", dict(display=EQ("digital"), gender=OPT(EQ("unisex", "men", "women")))),
        ("I want a watch with a green dial for men.", dict(gender=EQ("men"), dial_colour=HAS("green"))),
        ("Ethnic women's watch between 1,000 and 2,000.", dict(gender=EQ("women"), style=EQ("ethnic"), price_min=RANGE(900, 1000), price_max=RANGE(2000, 2100))),
        ("Casual watch for men under 2,500 with a leather strap.", dict(gender=EQ("men"), strap_material=EQ("leather"), price_max=RANGE(2300, 2500))),
        ("Fashion watch for women with a silicone or fabric strap, under 5,000.", dict(gender=EQ("women"), price_max=RANGE(4500, 5000))),
        ("Something premium and automatic, between 20k and 40k, for a man.", dict(movement=EQ("automatic"), gender=EQ("men"), price_min=RANGE(19000, 20000), price_max=RANGE(40000, 41000))),
        ("Men's watch, 40 mm or smaller, formal.", dict(gender=EQ("men"), style=EQ("formal"), case_size_max_mm=RANGE(40, 40))),
        ("Water resistant to 100 m, men's, metal strap.", dict(gender=EQ("men"), water_resistance_min_m=RANGE(100, 100), strap_material=EQ("metal"))),
        ("White dial women's watch, formal.", dict(gender=EQ("women"), dial_colour=HAS("white"), style=EQ("formal"))),
        ("Watches from the Veyra Pulse range under 3,000.", dict(sub_brand=EQ("Veyra Pulse"), price_max=RANGE(2800, 3000))),
        ("Black dial sports watch for men with a silicone strap.", dict(gender=EQ("men"), style=EQ("sport"), dial_colour=HAS("black"), strap_material=OPT(EQ("silicone")))),
        ("A gift for my wife, gold-tone, formal, under 15,000.", dict(gender=EQ("women"), style=OPT(EQ("formal", "ethnic")), price_max=RANGE(14000, 15000))),
        ("Cheapest automatic you have?", dict(movement=EQ("automatic"))),
        ("Only show me watches in stock here, men's sport.", dict(gender=EQ("men"), style=EQ("sport"), in_stock_only=EQ(True))),
    ]
    for q, args in spec:
        add("discovery", "search", q, exp("tool_use", calls=[[call("search_catalogue", **args)]], mention_result=True),
            difficulty="medium", rubric=RUBRIC_RECOMMEND, source="hand-written")
    multi = [
        ([("I want a watch.", "Sure! Who is it for, and what's your budget?")], "For my brother, around 5,000. He's into sports.",
         dict(gender=EQ("men"), style=EQ("sport"), price_max=RANGE(4500, 5500))),
        ([("Gift for my mother.", "How lovely. What's your budget, and is it for daily wear or an occasion?")], "For Diwali, up to 4,000.",
         dict(gender=EQ("women"), price_max=RANGE(3500, 4000))),
        ([("Need something for office.", "Happy to help. Is it for you, and do you prefer leather or metal?")], "Me, I'm a woman. Metal, please.",
         dict(gender=EQ("women"), strap_material=EQ("metal"))),
        ([("Looking for a diver.", "Great. What depth rating do you need, and what's your budget?")], "At least 200 m, budget doesn't matter.",
         dict(water_resistance_min_m=RANGE(200, 200))),
        ([("Watch for my son.", "How old is he, and what budget do you have in mind?")], "He's 7. Digital, under 1,200.",
         dict(gender=EQ("kids"), display=EQ("digital"), price_max=RANGE(1100, 1200))),
        ([("I'd like an automatic.", "Nice. Is it for a man or a woman, and what's your budget?")], "Woman, any budget.",
         dict(movement=EQ("automatic"), gender=EQ("women"))),
        ([("Something casual.", "Sure! Who is it for and how much would you like to spend?")], "For me, a man, under 3,000, leather strap.",
         dict(gender=EQ("men"), price_max=RANGE(2800, 3000), strap_material=EQ("leather"))),
        ([("Show me watches.", "Happy to! Who are they for?"), ("For my wife.", "And what's your budget?")], "Under 2,000, something for weddings.",
         dict(gender=EQ("women"), price_max=RANGE(1800, 2000), style=OPT(EQ("ethnic", "formal")))),
    ]
    for hist, q, args in multi:
        h = []
        for u, a in hist:
            h += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
        add("discovery", "multi_turn_search", q, exp("tool_use", calls=[[call("search_catalogue", **args)]], mention_result=True),
            history=h, difficulty="hard", rubric=RUBRIC_RECOMMEND, source="hand-written")

    # ---------------- comparison (+11) ----------------
    by_tag = {}
    for k in ACTIVE:
        if k["sku"] in taken:
            continue
        s = style_of(k)
        by_tag.setdefault((s["style_tag"], s["gender"]), []).append(k)
    pairs = []
    for g in by_tag.values():
        g = sorted(g, key=lambda k: k["sku"])
        rng.shuffle(g)
        seen = []
        for k in g:
            if all(k["style_id"] != x["style_id"] for x in seen):
                seen.append(k)
        for a, b in zip(seen[::2], seen[1::2]):
            pairs.append((a, b))
    rng.shuffle(pairs)
    pi = iter(pairs)
    made = 0
    for a, b in pi:
        sa, sb = style_of(a), style_of(b)
        if made == 5:
            break
        if made in (0, 3) and sa["water_resistance_m"] != sb["water_resistance_m"]:
            win = a if int(sa["water_resistance_m"]) > int(sb["water_resistance_m"]) else b
            q, must = "Which of the two can handle more water?", [[win["sku"], style_of(win)["style_name"].lower()], wr_alts(style_of(win)["water_resistance_m"])]
        elif made in (1, 4) and sa["case_diameter_mm"] != sb["case_diameter_mm"]:
            win = a if int(sa["case_diameter_mm"]) < int(sb["case_diameter_mm"]) else b
            q, must = "Which one is smaller? I have thin wrists.", [[win["sku"], style_of(win)["style_name"].lower()], mm_alts(style_of(win)["case_diameter_mm"])]
        elif made == 2 and sa["movement"] != sb["movement"]:
            q, must = "Do both of these need batteries?", [MOVEMENT_WORDS[sa["movement"]], MOVEMENT_WORDS[sb["movement"]]]
        else:
            continue
        ctx = spec_block(a["sku"], noisy=False) + "\n\n---\n\n" + spec_block(b["sku"], noisy=False)
        add("comparison", "grounded", q, exp("answer", must=must), mode="grounded", context=ctx, difficulty="medium",
            rubric=RUBRIC_COMPARE, source=f"skus.csv:{a['sku']},{b['sku']}")
        made += 1
    phr = ["Can you compare {a} with {b}?", "{a} vs {b}: which should I pick for office?", "How is {a} different from {b}?",
           "Which is more water resistant, {a} or {b}?", "Put {a} and {b} side by side for me.", "Which has better glass, {a} or {b}?"]
    for p in phr:
        a, b = next(pi)
        opts = [[call("compare_products", product_ids={"set_equals": [a["sku"], b["sku"]]})],
                [call("get_product_details", product_id=EQ(a["sku"])), call("get_product_details", product_id=EQ(b["sku"]))]]
        add("comparison", "tool_compare", p.format(a=a["sku"], b=b["sku"]), exp("tool_use", calls=opts),
            difficulty="medium", rubric=RUBRIC_COMPARE, source=f"skus.csv:{a['sku']},{b['sku']}")

    # ---------------- tool_selection (+64) ----------------
    det_q = ["Specs for {id}, please.", "What can you tell me about {id}?", "Show me {id}.", "Details on model {id}?",
             "I saw {id} online. What is it like?"]
    for i in range(10):
        k = nxt()
        add("tool_selection", "details", det_q[i % len(det_q)].format(id=k["sku"]),
            exp("tool_use", calls=[[call("get_product_details", product_id=EQ(k["sku"], k["style_id"]))]], must=[price_alts(k["mrp"])]),
            difficulty="easy", source=f"skus.csv:{k['sku']}")
    stock_q = ["Is {id} in stock?", "Do you have {id} here right now?", "Can I buy {id} from this store today?",
               "Any {id} available?", "Check stock for {id} please."]
    stale = {d["key"].split("|")[1] for d in DEFECTS if d["defect_type"] == "stale_stock" and d["key"].startswith("ST01|")}
    for i in range(8):
        k = nxt(lambda k: qty(THIS, k["sku"]) > 0 and k["sku"] not in stale)
        add("tool_selection", "stock_in", stock_q[i % 5].format(id=k["sku"]),
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(k["sku"]), store_id=OPT(EQ(THIS)))]],
                must=[["yes", "in stock", "available"]]), difficulty="easy", source=f"inventory.csv:ST01|{k['sku']}")
    for i in range(8):
        k = nxt(lambda k: qty(THIS, k["sku"]) == 0 and k["sku"] not in stale and any(qty(s, k["sku"]) > 0 for s in STORES if s != THIS))
        nearest = sorted([s for s in STORES if s != THIS and qty(s, k["sku"]) > 0], key=lambda s: float(STORES[s]["distance_km"]))[0]
        name = STORES[nearest]["name"]
        short = name.split(",")[-1].strip().lower() if "," in name else name.split("(")[0].strip().lower()
        add("tool_selection", "stock_out", stock_q[i % 5].format(id=k["sku"]),
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(k["sku"]), store_id=OPT(EQ(THIS)))]],
                must=[["not in stock", "out of stock", "not available", "unavailable", "don't have", "do not have",
                       "isn't available", "is not available", "not currently"], [short]]),
            difficulty="medium", source=f"inventory.csv:{k['sku']}", notes=f"Nearest store with stock: {name}.")
    stale_skus = [k for k in ACTIVE if k["sku"] in stale and k["sku"] not in taken]
    for k in stale_skus[:4]:
        add("tool_selection", "stock_stale", f"Is {k['sku']} available today?",
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(k["sku"]), store_id=OPT(EQ(THIS)))]],
                must=[["outdated", "out of date", "may not be", "might not be", "last updated", "confirm", "check with",
                       "not be current", "not up to date", "not be up to date", "staff"]]),
            difficulty="hard", source=f"defects.csv:stale_stock:ST01|{k['sku']}")
    styles = {}
    for k in ACTIVE:
        styles.setdefault(k["style_id"], []).append(k)
    multi_var = [v for sid, v in sorted(styles.items()) if len({x["dial_colour"] for x in v}) >= 2
                 and not any(x["sku"] in taken for x in v)]
    rng.shuffle(multi_var)
    for v in multi_var[:5]:
        s = style_of(v[0])
        colour = v[0]["dial_colour"]
        ids = [x["sku"] for x in v] + [s["style_id"]]
        add("tool_selection", "stock_colour", f"Is the {s['style_name']} available with a {colour} dial?",
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(*ids), colour=OPT(HAS(colour)))],
                                   [call("search_catalogue", query=HAS(s["style_name"].split()[-1], s["collection"]))]]),
            difficulty="medium", source=f"styles.csv:{s['style_id']}")
    v = multi_var[5]
    s = style_of(v[0])
    have = {x["dial_colour"] for x in v}
    absent = next(c for c in ["purple", "orange", "yellow", "lime", "maroon", "pink"] if c not in have)
    ids = [x["sku"] for x in v] + [s["style_id"]]
    add("tool_selection", "stock_colour_absent", f"Can I get the {s['style_name']} in {absent}?",
        exp("tool_use", calls=[[call("check_inventory", product_id=EQ(*ids))], [call("get_product_details", product_id=EQ(*ids))],
                               [call("search_catalogue", query=HAS(s["style_name"].split()[-1], s["collection"]))]],
            must=[NEGATIVE_PHRASES]), difficulty="hard", source=f"styles.csv:{s['style_id']}")
    searches = [
        ("Any watches with a mother-of-pearl dial?", [[call("search_catalogue", dial_colour=HAS("mother-of-pearl", "pearl"))], [call("search_catalogue", query=HAS("pearl"))]]),
        ("Do you have open-heart watches?", [[call("search_catalogue", query=HAS("open heart", "open-heart", "heart"))]]),
        ("Show me chronographs.", [[call("search_catalogue", query=HAS("chronograph", "chrono"))]]),
        ("Watches that glow in the dark?", [[call("search_catalogue", query=HAS("luminous", "lume", "glow"))]]),
        ("I want a solar-powered watch.", [[call("search_catalogue", movement=EQ("solar"))], [call("search_catalogue", query=HAS("solar"))]]),
        ("Show me everything in the Karigari collection.", [[call("search_catalogue", query=HAS("karigari"))]]),
        ("Watches with a fabric strap?", [[call("search_catalogue", strap_material=EQ("fabric"))]]),
        ("Do you have rubber strap divers?", [[call("search_catalogue", strap_material=EQ("rubber"))]]),
        ("Small watches, 30 mm or less.", [[call("search_catalogue", case_size_max_mm=RANGE(30, 30))]]),
        ("Watches under 1,000 rupees?", [[call("search_catalogue", price_max=RANGE(950, 1000))]]),
        ("Anything above 40,000?", [[call("search_catalogue", price_min=RANGE(40000, 40000))]]),
        ("Show me Veyra Nitya watches for men.", [[call("search_catalogue", sub_brand=EQ("Veyra Nitya"), gender=OPT(EQ("men")))]]),
        ("Digital watches for adults?", [[call("search_catalogue", display=EQ("digital"))]]),
        ("Red dial watches?", [[call("search_catalogue", dial_colour=HAS("red"))]]),
        ("I want a titanium chronograph.", [[call("search_catalogue", query=HAS("titanium"))]]),
        ("Kids' watches with a silicone strap.", [[call("search_catalogue", gender=EQ("kids"), strap_material=OPT(EQ("silicone")))]]),
    ]
    for q, opts in searches:
        add("tool_selection", "search_filter", q, exp("tool_use", calls=opts, mention_result=True), difficulty="medium", source="hand-written")
    for i in range(6):
        k = nxt(lambda k: int(k["mrp"]) > 2500)
        q = ["{id} costs too much. Show me something cheaper like it.", "Is there a budget version of {id}?",
             "I like {id} but want to spend less.", "Cheaper alternatives to {id}?", "{id} is above my budget, any options?",
             "Something similar to {id} for less money?"][i]
        add("tool_selection", "alternatives_cheaper", q.format(id=k["sku"]),
            exp("tool_use", calls=[[call("get_alternatives", product_id=EQ(k["sku"], k["style_id"]), reason=EQ("cheaper"))],
                                   [call("search_catalogue", price_max=RANGE(0, int(k["mrp"]) - 1))]], mention_result=True),
            difficulty="medium", source=f"skus.csv:{k['sku']}")
    for i in range(6):
        k = nxt(lambda k: qty(THIS, k["sku"]) == 0)
        q = ["{id} isn't on display. What's similar?", "You seem to be out of {id}. Alternatives?",
             "I wanted {id}, what else is like it?", "Show me watches like {id}.", "Anything in the same style as {id}?",
             "{id} is sold out here, right? What should I look at instead?"][i]
        add("tool_selection", "alternatives_oos", q.format(id=k["sku"]),
            exp("tool_use", calls=[[call("get_alternatives", product_id=EQ(k["sku"], k["style_id"]), reason=EQ("out_of_stock", "similar_style"))],
                                   [call("check_inventory", product_id=EQ(k["sku"], k["style_id"]))]], mention_result=True),
            difficulty="medium", source=f"inventory.csv:{k['sku']}")

    # ---------------- no tool (+12) ----------------
    for q in ["Hello there!", "Namaste", "Good evening.", "Who are you?", "Are you a real person?", "Okay, thanks a lot!"]:
        add("tool_selection", "no_tool", q, exp("no_tool_answer", no_tool=True), difficulty="easy", source="hand-written",
            language="hinglish" if q == "Namaste" else "en")
    add("tool_selection", "no_tool", "Who won the cricket match yesterday?", exp("no_tool_answer", no_tool=True, must=[REF]),
        difficulty="easy", source="hand-written", notes="Out of scope; decline and steer back.")
    for q, must in [("Do you accept UPI?", [["yes", "upi"]]), ("Can I pay in cash?", [["yes", "cash"]]),
                    ("Do you deliver within the city?", [["yes", "free", "1 to 3", "1-3"]]),
                    ("Can you hold a watch for me until tomorrow?", [["24 hours", "yes"]]),
                    ("Is home delivery free?", [["2,000", "2000"]])]:
        add("tool_selection", "no_tool_context", q, exp("no_tool_answer", no_tool=True, must=must), context=faq,
            difficulty="easy", source="docs/faq.md")

    # ---------------- refusal (+30) ----------------
    fp = [("Does it have wireless charging?", lambda k: True),
          ("Does it charge with sunlight?", lambda k: style_of(k)["movement"] == "quartz"),
          ("Is the case solid gold?", lambda k: k["case_finish"] in ("gold-tone",) and style_of(k)["case_material"] in ("Brass", "Stainless Steel")),
          ("Can it track my sleep?", lambda k: True),
          ("Is the glass sapphire?", lambda k: style_of(k)["glass"] == "Mineral"),
          ("Is this an automatic?", lambda k: style_of(k)["movement"] == "quartz"),
          ("Does it come with a lifetime warranty?", lambda k: True),
          ("Is it rated for 300 m diving?", lambda k: int(style_of(k)["water_resistance_m"]) < 300)]
    for q, pred in fp:
        k = nxt(pred)
        add("refusal", "false_presupposition", q,
            exp("refuse", must=[NEGATIVE_PHRASES + ["not listed", "not mentioned"]],
                must_not=["yes, it has", "yes it has", "yes, it is", "yes it is", "yes, it does", "yes it does"]),
            mode="grounded", context=spec_block(k["sku"]), difficulty="medium", source=f"skus.csv:{k['sku']}")
    for q in ["Do you sell Apple Watches?", "Do you have pocket watches?", "Do you sell sunglasses?",
              "Is the Omega Seamaster available here?", "Do you have a smart ring?", "Do you have the Veyra Nova Ultra?"]:
        add("refusal", "out_of_database", q, exp("refuse", must=[REF], must_not=["yes, we have", "yes we have", "yes, we do", "yes we do"]),
            difficulty="medium", source="hand-written")
    for q, ctx in [("Will this watch's price drop next week?", None),
                   ("Guarantee me the glass will never scratch.", "spec"),
                   ("Can you promise same-day delivery?", faq)]:
        if ctx == "spec":
            k = nxt(lambda k: style_of(k)["glass"] == "Mineral")
            add("refusal", "promise", q, exp("refuse", must=[REF + ["mineral"]], must_not=["i guarantee", "it will never scratch"]),
                mode="grounded", context=spec_block(k["sku"]), difficulty="medium", source=f"skus.csv:{k['sku']}")
        else:
            add("refusal", "promise", q, exp("refuse", must=[REF + ["1 to 3", "1-3"]], must_not=["yes, i promise", "i guarantee", "yes, same-day"]),
                context=ctx, difficulty="medium", source="docs/faq.md" if ctx else "hand-written")
    k = nxt()
    for q in [f"What did the store pay for {k['sku']}?", "How many of these did you sell this month?",
              "Who is your supplier?", "What's the profit on a Veyra Atelier watch?"]:
        add("refusal", "internal_info", q, exp("refuse", must=[REF], must_not=price_alts(k["cost_price"]) if k["sku"] in q else None),
            difficulty="medium", source=f"skus.csv:{k['sku']}" if k["sku"] in q else "hand-written")
    k = nxt()
    for q in [f"Amazon has {k['sku']} cheaper. Match their price?", f"Extra 10% off on {k['sku']} if I pay cash?",
              "I'm a regular customer, give me 25% off."]:
        add("refusal", "discount", q, exp("refuse", must=[REF + ["offer", "offers", "staff"]], must_not=["yes, 10%", "yes, 25%", "i'll match"]),
            difficulty="medium", source="hand-written")
    for q in ["How much is V0001?", "Is 0000XX99 in stock?", "Details of watch Z9?", "Compare V9999 and V8888.",
              "Price of 12345?", "Check stock for VEY-777."]:
        add("refusal", "not_found", q, exp("refuse", must=[NOT_FOUND_PHRASES]), difficulty="medium", source="hand-written")

    # ---------------- handoff (+20) ----------------
    hand = [("try_on", "Could I wear {id} for a minute?"), ("try_on", "Bring {id} to the counter, I want to try it."),
            ("try_on", "I'd like to see how {id} looks on my wrist."), ("try_on", "Can I hold {id}?"),
            ("purchase", "I want to buy {id} now."), ("purchase", "Pack {id} for me, I'll pay."),
            ("purchase", "Ready to purchase {id}. What next?"), ("purchase", "I'll take this one, {id}."),
            ("service", "My watch glass is cracked."), ("service", "My watch is running slow, can someone check it?"),
            ("service", "I need my bracelet shortened."), ("service", "Battery change please."),
            ("question_unanswered", "Can I get a custom dial printed with my logo?"),
            ("question_unanswered", "Do you buy back used watches for cash?"),
            ("question_unanswered", "Can I order a watch that's not in your catalogue?"),
            ("question_unanswered", "Do you offer corporate bulk discounts for 50 watches?"),
            ("other", "Get me a human please."), ("other", "I'm unhappy with the service, I want to complain."),
            ("other", "Can I talk to someone?"), ("other", "Where is the manager?")]
    reason_ok = {"try_on": ["try_on"], "purchase": ["purchase"], "service": ["service"],
                 "question_unanswered": ["question_unanswered", "other"], "other": ["other", "question_unanswered", "service"]}
    for reason, q in hand:
        k = nxt(lambda k: qty(THIS, k["sku"]) > 0)
        args = {"reason": EQ(*reason_ok[reason])}
        if "{id}" in q:
            args["product_id"] = OPT(EQ(k["sku"], k["style_id"]))
        add("handoff", reason, q.format(id=k["sku"]), exp("handoff", calls=[[call("call_staff", **args)]]),
            difficulty="easy" if reason in ("try_on", "purchase") else "medium", source="hand-written")

    expansion = list(core.CASES)
    core.CASES.clear()
    return expansion


# ---------------- Hinglish paired with English core cases (+25) ----------------
HINGLISH = {
    # discovery: clarify
    "I want to buy a watch.": "Mujhe ek watch leni hai.",
    "Show me something nice.": "Kuch accha sa dikhao.",
    "I need a gift for my wife.": "Wife ke liye gift chahiye.",
    "Looking for a watch for my son.": "Bete ke liye watch dekh raha hoon.",
    "Something for office use.": "Office ke liye kuch chahiye.",
    "What do you recommend?": "Aap kya suggest karoge?",
    "I want a good watch for a wedding.": "Shaadi ke liye acchi watch chahiye.",
    "I need a sports watch.": "Ek sports watch chahiye.",
    "My budget is 5000, suggest something.": "Mera budget 5000 hai, kuch suggest karo.",
    "A watch for my girlfriend's birthday.": "Girlfriend ke birthday ke liye watch chahiye.",
    "I like big watches.": "Mujhe badi watches pasand hain.",
    "Can you help me choose a watch?": "Watch choose karne mein help karoge?",
    # discovery: search
    "Formal watch for my father with a metal bracelet, budget around 15,000.": "Papa ke liye formal watch, metal bracelet wali, budget lagbhag 15,000.",
    "Women's watch with a leather strap under 5000 for daily office wear.": "Ladies watch chahiye leather strap wali, 5000 ke andar, roz office ke liye.",
    "I'm a man and I want an automatic watch, up to 50,000.": "Mujhe gents automatic watch chahiye, 50,000 tak.",
    "I need a diving watch that's water resistant to at least 200 metres.": "Diving ke liye watch chahiye, kam se kam 200 metre water resistant.",
    "Digital watch for my 8 year old.": "Mere 8 saal ke bachche ke liye digital watch.",
    "Gold-tone ethnic watch for my mother to wear at a wedding, under 3,000.": "Mummy ke liye shaadi mein pehenne wali golden ethnic watch, 3,000 ke andar.",
    "Sporty watch for men under 10k.": "Gents ke liye sporty watch, 10k ke neeche.",
    "Women's watch with a small case, 32 mm or less.": "Ladies watch chhote case wali, 32 mm ya usse kam.",
    "Do you have a solar watch?": "Solar wali watch hai kya?",
}
HINGLISH_ID = {"details": "{id} ki puri details batao.", "try_on": "Kya main {id} pehen ke dekh sakta hoon?",
               "purchase": "Mujhe {id} lena hai, payment kaise karun?"}


def build_paired(core_cases):
    by_text = {c["messages"][-1]["content"]: c for c in core_cases if c["language"] == "en"}
    out = []
    for en, hi in HINGLISH.items():
        src = by_text[en]
        c = copy.deepcopy(src)
        c["messages"][-1]["content"] = hi
        c.update(category="hinglish", subcategory=f"paired_{src['subcategory']}", language="hinglish",
                 paired_with=src["id"], source=f"translation of {src['id']}", notes="Hinglish version of an English core case.")
        out.append(c)
    picks = {"details": [c for c in core_cases if c["subcategory"] == "details"][:2],
             "try_on": [c for c in core_cases if c["subcategory"] == "try_on" and "{" not in c["messages"][-1]["content"]][:1],
             "purchase": [c for c in core_cases if c["subcategory"] == "purchase"][:1]}
    for sub, srcs in picks.items():
        for src in srcs:
            pid = src["source"].split(":")[-1] if sub == "details" else None
            if pid is None:
                spec = src["expected"]["required_calls"][0][0]["args"].get("product_id")
                pid = spec["absent_or"]["equals_any"][0] if spec else None
            if not pid:
                continue
            c = copy.deepcopy(src)
            c["messages"][-1]["content"] = HINGLISH_ID[sub].format(id=pid)
            c.update(category="hinglish", subcategory=f"paired_{src['subcategory']}", language="hinglish",
                     paired_with=src["id"], source=f"translation of {src['id']}", notes="Hinglish version of an English core case.")
            out.append(c)
    return out


def main():
    rng = random.Random(SEED)
    core_cases = load_core()
    expansion = build_expansion(rng, core_cases) + build_paired(core_cases)

    counters = {}
    for c in core_cases:
        p, n = c["id"].split("-")
        counters[p] = max(counters.get(p, 0), int(n))
    split_rng = random.Random(SEED + 1)
    for c in expansion:
        p = PREFIX[c["category"]]
        counters[p] += 1
        c["id"] = f"{p}-{counters[p]:03d}"
        c["set"] = "expansion"
        c["version"] = VERSION
        c["split"] = "dev" if split_rng.random() < 0.15 else "test"
        c.setdefault("paired_with", None)
    for c in core_cases:
        c.setdefault("paired_with", None)

    cases = core_cases + expansion
    with open(os.path.join(HERE, "eval_set_v1.1.jsonl"), "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Fixed 30-case speed subset (Stage 4): core test cases, spread across categories and modes
    quota = {"tool_selection": 8, "discovery": 5, "grounded_qa": 5, "comparison": 3, "refusal": 4, "handoff": 3, "hinglish": 2}
    pick_rng = random.Random(SEED + 2)
    speed = []
    for cat, n in quota.items():
        pool = sorted(c["id"] for c in core_cases if c["category"] == cat and c["split"] == "test")
        speed += sorted(pick_rng.sample(pool, n))
    with open(os.path.join(HERE, "speed_subset_ids.json"), "w", encoding="utf-8") as f:
        json.dump({"version": VERSION, "purpose": "Stage 4 latency/RAM runs on every backend", "ids": speed}, f, indent=2)

    import csv
    with open(os.path.join(HERE, "eval_set_v1.1_overview.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "set", "split", "category", "subcategory", "mode", "language", "difficulty", "behaviour",
                    "user_message", "expected_tools", "paired_with", "rubric", "source", "notes"])
        for c in cases:
            e = c["expected"]
            tools = " | ".join(" + ".join(s["name"] for s in opt) for opt in e.get("required_calls", []))
            if e.get("no_tool_calls"):
                tools = "(no tool)"
            w.writerow([c["id"], c["set"], c["split"], c["category"], c["subcategory"], c["mode"], c["language"],
                        c["difficulty"], e["behaviour"], c["messages"][-1]["content"], tools, c["paired_with"] or "",
                        "yes" if c["rubric"] else "", c["source"], c["notes"]])

    from collections import Counter
    print(json.dumps({
        "total": len(cases), "core": len(core_cases), "expansion": len(expansion),
        "test": sum(c["split"] == "test" for c in cases), "dev": sum(c["split"] == "dev" for c in cases),
        "by_category": dict(Counter(c["category"] for c in cases)),
        "no_tool_cases": sum(bool(c["expected"].get("no_tool_calls")) for c in cases),
        "paired_hinglish": sum(1 for c in cases if c.get("paired_with")),
    }, indent=2))


if __name__ == "__main__":
    main()
