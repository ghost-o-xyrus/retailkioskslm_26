"""
Build the Objective 1 eval set (Step 4) from the generated catalogue.

    python eval/build_eval_set.py            # writes eval/eval_set.jsonl and eval/eval_set_overview.csv

Every expected answer is computed from data/clean (ground truth). Product-info
contexts are rendered from data/kiosk (the noisy copy the kiosk really sees).
Seeded, so the same catalogue always gives the same eval set.

Case format: see eval/README.md.
"""

import csv
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA_ROOT = os.environ.get("SLM_DATA_ROOT", os.path.join(ROOT, "data"))   # Objective 4: data_train/
CLEAN = os.path.join(DATA_ROOT, "clean")
KIOSK = os.path.join(DATA_ROOT, "kiosk")
DOCS = os.path.join(DATA_ROOT, "docs")
EVAL_VERSION = "1.0"
SEED = 2026


def read(base, name):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def doc(name):
    with open(os.path.join(DOCS, name), encoding="utf-8") as f:
        return f.read().strip()


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
STYLES = {s["style_id"]: s for s in read(CLEAN, "styles.csv")}
SKUS = {k["sku"]: k for k in read(CLEAN, "skus.csv")}
K_STYLES = {s["style_id"]: s for s in read(KIOSK, "styles.csv")}
K_SKUS = {k["sku"]: k for k in read(KIOSK, "skus.csv")}
INV = {(r["store_id"], r["sku"]): r for r in read(CLEAN, "inventory.csv")}
STORES = {s["store_id"]: s for s in read(CLEAN, "stores.csv")}
DEFECTS = read(DATA_ROOT, "defects.csv")
THIS = "ST01"

ACTIVE = [k for k in SKUS.values() if k["status"] == "active"]


def qty(store, sku):
    r = INV[(store, sku)]
    return int(r["qty_display"]) + int(r["qty_backroom"])


def style_of(k):
    return STYLES[k["style_id"]]


# ---------------------------------------------------------------------------
# Alternatives for answer matching
# ---------------------------------------------------------------------------
def price_alts(n):
    n = int(n)
    return [f"{n:,}", str(n)]


def mm_alts(v):
    v = str(v).rstrip("0").rstrip(".") if "." in str(v) else str(v)
    return [f"{v} mm", f"{v} millimetre", f"{v} millimeter", f"{v} millimetres", f"{v} millimeters"]


def wr_alts(m):
    m = int(m)
    return [f"{m} m", f"{m} metre", f"{m} meter", f"{m} metres", f"{m} meters", f"{m // 10} atm", f"{m // 10} bar"]


def months_alts(n):
    n = int(n)
    out = [f"{n} months", f"{n} month", f"{n}-month"]
    if n % 12 == 0:
        y = n // 12
        out += [f"{y} year", f"{y} years", f"{y}-year"] + (["one year", "1 yr"] if y == 1 else ["two years", "2 yrs"] if y == 2 else [])
    return out


STRAP_WORDS = {"leather": ["leather"], "metal": ["metal", "steel", "bracelet"], "mesh": ["mesh"],
               "silicone": ["silicone"], "rubber": ["rubber", "fkm"], "fabric": ["fabric", "nylon", "textile"],
               "resin": ["resin", "plastic"]}
MOVEMENT_WORDS = {"automatic": ["automatic", "self-winding"], "quartz": ["quartz", "battery"],
                  "solar": ["solar", "light-powered"]}
UNKNOWN_PHRASES = ["not listed", "not mentioned", "not specified", "not available", "don't have that",
                   "do not have that", "don't have this", "do not have this", "no information",
                   "not sure", "can't confirm", "cannot confirm", "not given", "not provided",
                   "doesn't say", "does not say", "doesn't mention", "does not mention", "check with",
                   "ask a staff", "ask our staff", "staff member"]
NOT_FOUND_PHRASES = ["couldn't find", "could not find", "can't find", "cannot find", "not find", "no watch",
                     "no product", "not found", "doesn't exist", "does not exist", "not in our catalogue",
                     "not in our catalog", "don't have", "do not have", "no record", "isn't a valid", "is not a valid",
                     "invalid", "not recognise", "not recognize", "doesn't match", "does not match"]
NEGATIVE_PHRASES = ["no", "not", "doesn't", "does not", "isn't", "is not", "don't", "do not", "unfortunately",
                    "nahi", "nahin"]

# ---------------------------------------------------------------------------
# Context rendering (what a retrieval step would put in the prompt)
# ---------------------------------------------------------------------------
SPEC_FIELDS = [("style", "style_name"), ("sub_brand", "sub_brand"), ("collection", "collection"),
               ("gender", "gender"), ("movement", "movement"), ("display", "display"), ("function", "function"),
               ("case_material", "case_material"), ("case_shape", "case_shape"),
               ("case_diameter_mm", "case_diameter_mm"), ("case_thickness_mm", "case_thickness_mm"),
               ("glass", "glass"), ("water_resistance", "water_resistance_m"), ("luminous", "lume"),
               ("warranty_movement_months", "warranty_movement_months"),
               ("warranty_battery_months", "warranty_battery_months"), ("country_of_origin", "country_of_origin")]


def spec_block(sku, noisy=True):
    k = (K_SKUS if noisy else SKUS)[sku]
    s = (K_STYLES if noisy else STYLES)[k["style_id"]]
    lines = [f"product_id: {k['sku']}", f"name: {k['product_name']}"]
    units = {"case_diameter_mm": " mm", "case_thickness_mm": " mm",
             "warranty_movement_months": " months", "warranty_battery_months": " months"}
    for label, f in SPEC_FIELDS:
        v = s.get(f, "")
        if v != "":
            lines.append(f"{label.replace('_mm', '').replace('_months', '')}: {v}{units.get(f, '')}")
    for label in ("case_finish", "dial_colour", "strap_material", "strap_colour"):
        if k.get(label, "") != "":
            lines.append(f"{label}: {k[label]}")
    lines.append(f"mrp_inr: {k['mrp']}")
    lines.append(f"status: {k['status']}")
    lines.append(f"description: {k['description']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Case builders
# ---------------------------------------------------------------------------
CASES = []


def add(category, subcategory, user, expected, *, mode="tools", context=None, history=None,
        language="en", difficulty="medium", source="", rubric=None, notes=""):
    messages = list(history or []) + [{"role": "user", "content": user}]
    CASES.append(dict(
        id=None, category=category, subcategory=subcategory, mode=mode, language=language,
        difficulty=difficulty, messages=messages, context=context, expected=expected,
        rubric=rubric or [], source=source, notes=notes))


def exp(behaviour, calls=None, must=None, must_not=None, slots=None, no_tool=False, mention_result=False):
    e = {"behaviour": behaviour}
    if calls is not None:
        e["required_calls"] = calls      # list of options; each option = list of call specs
    if no_tool:
        e["no_tool_calls"] = True
    if must:
        e["must_include"] = must
    if must_not:
        e["must_not_include"] = must_not
    if slots:
        e["clarify_slots"] = slots
    if mention_result:
        e["must_mention_tool_result"] = True
    return e


def call(name, **args):
    return {"name": name, "args": args}


EQ = lambda *v: {"equals_any": list(v)}
RANGE = lambda lo, hi: {"range": [lo, hi]}
HAS = lambda *v: {"contains_any": list(v)}
OPT = lambda m: {"absent_or": m}

RUBRIC_CLARIFY = ["Asks one or two short questions instead of recommending",
                  "Questions target missing information that matters (budget, recipient, occasion, strap, size)",
                  "Does not name or price specific products yet", "Friendly and concise"]
RUBRIC_RECOMMEND = ["Recommends only watches returned by the tools", "Respects every stated constraint",
                    "Gives price and one or two relevant features per watch", "Under about 80 words, friendly tone"]
RUBRIC_COMPARE = ["States correct values for each product", "Answers the comparison question directly",
                  "Mentions no specs that are not in the provided information", "Concise and easy to follow"]


def build(rng):
    # ======================= A. Grounded Q&A (25) ==========================
    pool = [k for k in ACTIVE]
    rng.shuffle(pool)
    noisy_skus = {d["key"] for d in DEFECTS if d["file"] == "skus.csv"}
    noisy_styles = {d["key"] for d in DEFECTS if d["file"] == "styles.csv" and d["defect_type"] in ("abbreviation", "unit_format")}
    missing_keys = {(d["key"], d["field"]) for d in DEFECTS if d["defect_type"] == "missing"}

    def has_missing(k):
        return any((k["style_id"], f) in missing_keys or (k["sku"], f) in missing_keys
                   for f in ("case_thickness_mm", "lume", "case_shape", "glass", "country_of_origin",
                             "strap_colour", "case_finish"))

    field_qs = [
        ("water_resistance", "Is this watch water resistant? Up to how much?",
         lambda k, s: [wr_alts(s["water_resistance_m"])]),
        ("case_size", "How big is the case on this one?", lambda k, s: [mm_alts(s["case_diameter_mm"])]),
        ("glass", "Is the glass on this watch scratch resistant? What is it made of?",
         lambda k, s: [[s["glass"].lower()]]),
        ("strap", "What is the strap made of?", lambda k, s: [STRAP_WORDS[k["strap_material"]]]),
        ("warranty", "What warranty comes with this watch?",
         lambda k, s: [months_alts(s["warranty_movement_months"])]),
        ("movement", "Does this run on a battery or is it automatic?",
         lambda k, s: [MOVEMENT_WORDS[s["movement"]]]),
        ("price", "How much does this cost?", lambda k, s: [price_alts(k["mrp"])]),
        ("thickness", "How thick is it? I want something slim.", lambda k, s: [mm_alts(s["case_thickness_mm"])]),
        ("water_resistance", "Can I wear this in the shower? What's the water rating?",
         lambda k, s: [wr_alts(s["water_resistance_m"])]),
        ("case_size", "What's the dial size?", lambda k, s: [mm_alts(s["case_diameter_mm"])]),
        ("glass", "What kind of crystal does it have?", lambda k, s: [[s["glass"].lower()]]),
        ("movement", "What movement is inside?", lambda k, s: [MOVEMENT_WORDS[s["movement"]]]),
    ]
    picked = [k for k in pool if not has_missing(k)]
    noisy_first = [k for k in picked if k["style_id"] in noisy_styles or k["sku"] in noisy_skus]
    clean_first = [k for k in picked if k not in noisy_first]
    for i, (sub, q, facts) in enumerate(field_qs):
        k = (noisy_first if i % 2 == 0 else clean_first)[i]
        s = style_of(k)
        add("grounded_qa", f"spec_{sub}", q, exp("answer", must=facts(k, s)), mode="grounded",
            context=spec_block(k["sku"]), difficulty="easy" if i % 2 else "medium",
            source=f"skus.csv:{k['sku']}", notes="abbreviated/noisy spec" if i % 2 == 0 else "")

    # Missing field (4): answer must say it is not listed, and must not guess the true value
    miss_q = {"case_thickness_mm": ("How thick is this watch?", lambda s, k: mm_alts(s["case_thickness_mm"])),
              "glass": ("What glass does this watch use?", lambda s, k: [s["glass"].lower()]),
              "lume": ("Will the hands glow in the dark?", lambda s, k: []),
              "case_shape": ("Is the case round or square?", lambda s, k: [s["case_shape"].lower()]),
              "country_of_origin": ("Where is this watch made?", lambda s, k: [s["country_of_origin"].lower()]),
              "strap_colour": ("What colour is the strap?", lambda s, k: [k["strap_colour"]])}
    done = 0
    seen_fields = set()
    for d in DEFECTS:
        if d["defect_type"] != "missing" or d["field"] not in miss_q or done == 4 or d["field"] in seen_fields:
            continue
        if d["file"] == "styles.csv":
            cands = [k for k in ACTIVE if k["style_id"] == d["key"]]
        else:
            cands = [SKUS[d["key"]]] if SKUS[d["key"]]["status"] == "active" else []
        if not cands:
            continue
        k = cands[0]
        s = style_of(k)
        q, truth = miss_q[d["field"]]
        add("grounded_qa", "missing_field", q,
            exp("answer_unknown", must=[UNKNOWN_PHRASES], must_not=truth(s, k)),
            mode="grounded", context=spec_block(k["sku"]), difficulty="hard",
            source=f"defects.csv:missing:{d['key']}:{d['field']}",
            notes="Field is absent from the context; a correct guess is still a hallucination.")
        done += 1
        seen_fields.add(d["field"])

    # Contradictions (4): spec row wins over the description
    care = doc("care.md")
    for d in [d for d in DEFECTS if d["defect_type"] == "contradiction"]:
        k = SKUS[d["key"]]
        s = style_of(k)
        if "sapphire" in d["kiosk_value"]:
            q, must, mn = "Does this watch have sapphire crystal?", [["mineral"], NEGATIVE_PHRASES], ["yes, it has sapphire", "yes it has sapphire", "yes, it does"]
            ctx = spec_block(k["sku"])
        elif "bracelet" in d["kiosk_value"]:
            q, must, mn = "Does it come on a steel bracelet?", [["leather"], NEGATIVE_PHRASES], ["yes, it comes", "yes it comes"]
            ctx = spec_block(k["sku"])
        else:
            q = "Can I go snorkelling with this watch?"
            must, mn = [wr_alts(s["water_resistance_m"]), NEGATIVE_PHRASES], ["suitable for snorkelling", "yes, you can"]
            ctx = spec_block(k["sku"]) + "\n\n" + care
        add("grounded_qa", "contradiction", q, exp("answer", must=must, must_not=mn), mode="grounded",
            context=ctx, difficulty="hard", source=f"defects.csv:contradiction:{k['sku']}",
            notes="Description contradicts the spec fields; the spec fields are correct.")

    # Store documents (5)
    add("grounded_qa", "doc_warranty", "Is the strap covered under warranty?",
        exp("answer", must=[NEGATIVE_PHRASES, ["strap", "straps"]]), mode="grounded", context=doc("warranty.md"),
        difficulty="easy", source="docs/warranty.md")
    add("grounded_qa", "doc_returns", "I bought a watch here 5 days ago and haven't worn it. Can I exchange it?",
        exp("answer", must=[["yes", "can exchange", "you can"], ["7 days", "seven days", "7-day"]]), mode="grounded",
        context=doc("returns.md"), difficulty="medium", source="docs/returns.md")
    add("grounded_qa", "doc_service", "How much does a battery replacement cost and how long does it take?",
        exp("answer", must=[["250", "rs. 250", "rs 250"], ["450"], ["30 minutes", "half an hour", "30 min"]]),
        mode="grounded", context=doc("service.md"), difficulty="easy", source="docs/service.md")
    add("grounded_qa", "doc_care", "My watch is rated 50 m. Can I swim in a pool with it?",
        exp("answer", must=[["yes", "light swimming", "pool"]], must_not=["yes, you can go scuba", "fine for scuba"]), mode="grounded",
        context=doc("care.md"), difficulty="medium", source="docs/care.md")
    add("grounded_qa", "doc_returns", "Can I return a watch that I had engraved?",
        exp("answer", must=[NEGATIVE_PHRASES]), mode="grounded", context=doc("returns.md"),
        difficulty="easy", source="docs/returns.md")

    # ======================= B. Guided discovery (25) ======================
    vague = [
        ("I want to buy a watch.", ["budget", "recipient", "occasion"]),
        ("Show me something nice.", ["budget", "recipient", "occasion"]),
        ("I need a gift for my wife.", ["budget", "occasion", "strap"]),
        ("Looking for a watch for my son.", ["budget", "age", "occasion"]),
        ("Something for office use.", ["budget", "recipient", "strap"]),
        ("What do you recommend?", ["budget", "recipient", "occasion"]),
        ("I want a good watch for a wedding.", ["budget", "recipient"]),
        ("I need a sports watch.", ["budget", "recipient"]),
        ("My budget is 5000, suggest something.", ["recipient", "occasion"]),
        ("A watch for my girlfriend's birthday.", ["budget", "strap", "occasion"]),
        ("I like big watches.", ["budget", "occasion"]),
        ("Can you help me choose a watch?", ["budget", "recipient", "occasion"]),
    ]
    for q, slots in vague:
        add("discovery", "clarify", q, exp("clarify", slots=slots, no_tool=False), difficulty="medium",
            rubric=RUBRIC_CLARIFY, source="hand-written",
            notes="Expected: one or two clarifying questions before searching. A search call is not required.")

    disc = [
        ("Formal watch for my father with a metal bracelet, budget around 15,000.",
         dict(gender=EQ("men"), style=EQ("formal"), strap_material=EQ("metal"), price_max=RANGE(14000, 16500))),
        ("Women's watch with a leather strap under 5000 for daily office wear.",
         dict(gender=EQ("women"), strap_material=EQ("leather"), price_max=RANGE(4500, 5000))),
        ("I'm a man and I want an automatic watch, up to 50,000.",
         dict(gender=EQ("men"), movement=EQ("automatic"), price_max=RANGE(45000, 50000))),
        ("I need a diving watch that's water resistant to at least 200 metres.",
         dict(water_resistance_min_m=RANGE(200, 200))),
        ("Digital watch for my 8 year old.", dict(gender=EQ("kids"), display=EQ("digital"))),
        ("Gold-tone ethnic watch for my mother to wear at a wedding, under 3,000.",
         dict(gender=EQ("women"), style=EQ("ethnic"), price_max=RANGE(2500, 3000))),
        ("Sporty watch for men under 10k.", dict(gender=EQ("men"), style=EQ("sport"), price_max=RANGE(9000, 10000))),
        ("Women's watch with a small case, 32 mm or less.", dict(gender=EQ("women"), case_size_max_mm=RANGE(30, 32))),
        ("Do you have a solar watch?", dict(movement=EQ("solar"))),
    ]
    for q, args in disc:
        add("discovery", "search", q, exp("tool_use", calls=[[call("search_catalogue", **args)]], mention_result=True),
            difficulty="medium", rubric=RUBRIC_RECOMMEND, source="hand-written")

    multi = [
        ([("I need a gift for my husband.", "Happy to help! What's your budget, and will he wear it to the office or casually?")],
         "Office, around 10,000. He likes leather straps.",
         dict(gender=EQ("men"), strap_material=EQ("leather"), price_max=RANGE(9000, 11000))),
        ([("Watch for my daughter.", "Lovely! How old is she, and do you have a budget in mind?")],
         "She's 10. Under 1,500 please.", dict(gender=EQ("kids"), price_max=RANGE(1400, 1500))),
        ([("Show me something sporty.", "Sure! Is it for you, and what's your budget?")],
         "For me, I'm a woman. Under 6,000.", dict(gender=EQ("women"), style=EQ("sport"), price_max=RANGE(5500, 6000))),
        ([("I want a blue dial watch.", "Nice choice. Is it for men or women, and what budget should I look within?")],
         "Men's, under 8,000.", dict(gender=EQ("men"), dial_colour=HAS("blue"), price_max=RANGE(7500, 8000))),
    ]
    for hist, q, args in multi:
        h = []
        for u, a in hist:
            h += [{"role": "user", "content": u}, {"role": "assistant", "content": a}]
        add("discovery", "multi_turn_search", q,
            exp("tool_use", calls=[[call("search_catalogue", **args)]], mention_result=True),
            history=h, difficulty="hard", rubric=RUBRIC_RECOMMEND, source="hand-written",
            notes="Constraints are spread across turns; all must reach the search call.")

    # ======================= C. Comparison (15) ============================
    by_tag = {}
    for k in ACTIVE:
        s = style_of(k)
        by_tag.setdefault((s["style_tag"], s["gender"]), []).append(k)
    groups = [v for v in by_tag.values() if len({k["style_id"] for k in v}) >= 3]
    pairs = []
    for g in groups:
        g = sorted(g, key=lambda k: k["sku"])
        rng.shuffle(g)
        one_per_style = []
        for k in g:
            if all(k["style_id"] != x["style_id"] for x in one_per_style):
                one_per_style.append(k)
        pairs += list(zip(one_per_style[::2], one_per_style[1::2]))  # every pair is used at most once
    rng.shuffle(pairs)
    comp_qs = ["wr", "price", "thin", "size", "glass", "diff", "wr", "price"]
    used = set()
    for kind in comp_qs:
        computed = []
        # find an unused pair where the asked attribute differs
        for pi, (a, b) in enumerate(pairs):
            if pi in used:
                continue
            sa, sb = style_of(a), style_of(b)
            if kind == "diff" or (kind == "wr" and sa["water_resistance_m"] != sb["water_resistance_m"]) or \
               (kind == "price" and a["mrp"] != b["mrp"]) or \
               (kind == "thin" and sa["case_thickness_mm"] != sb["case_thickness_mm"]) or \
               (kind == "size" and sa["case_diameter_mm"] != sb["case_diameter_mm"]) or \
               (kind == "glass" and sa["glass"] != sb["glass"]):
                used.add(pi)
            if kind == "wr" and sa["water_resistance_m"] != sb["water_resistance_m"]:
                win = a if int(sa["water_resistance_m"]) > int(sb["water_resistance_m"]) else b
                q = "Which of these two is more water resistant?"
                must = [[win["sku"], style_of(win)["style_name"].lower()], wr_alts(sa["water_resistance_m"]), wr_alts(sb["water_resistance_m"])]
                break
            if kind == "price" and a["mrp"] != b["mrp"]:
                diff = abs(int(a["mrp"]) - int(b["mrp"]))
                win = a if int(a["mrp"]) < int(b["mrp"]) else b
                q = "Which one is cheaper, and by how much?"
                must = [[win["sku"], style_of(win)["style_name"].lower()], price_alts(diff)]
                computed = [1]
                break
            if kind == "thin" and sa["case_thickness_mm"] != sb["case_thickness_mm"]:
                win = a if float(sa["case_thickness_mm"]) < float(sb["case_thickness_mm"]) else b
                q = "I want the slimmer one. Which is thinner?"
                must = [[win["sku"], style_of(win)["style_name"].lower()], mm_alts(style_of(win)["case_thickness_mm"])]
                break
            if kind == "size" and sa["case_diameter_mm"] != sb["case_diameter_mm"]:
                win = a if int(sa["case_diameter_mm"]) > int(sb["case_diameter_mm"]) else b
                q = "Which has the bigger dial?"
                must = [[win["sku"], style_of(win)["style_name"].lower()], mm_alts(style_of(win)["case_diameter_mm"])]
                break
            if kind == "glass" and sa["glass"] != sb["glass"]:
                q = "Which one has the more scratch-resistant glass?"
                order = ["Sapphire", "Mineral", "Acrylic"]
                win = a if order.index(sa["glass"]) < order.index(sb["glass"]) else b
                must = [[win["sku"], style_of(win)["style_name"].lower()], [style_of(win)["glass"].lower()]]
                break
            if kind == "diff":
                q = "What's the difference between these two?"
                must = [price_alts(a["mrp"]), price_alts(b["mrp"])]
                break
        ctx = spec_block(a["sku"], noisy=False) + "\n\n---\n\n" + spec_block(b["sku"], noisy=False)
        e = exp("answer", must=must)
        if computed:
            e["computed_fact_groups"] = computed  # derived by arithmetic, not copied from the context
        add("comparison", f"grounded_{kind}", q, e, mode="grounded", context=ctx,
            difficulty="medium", rubric=RUBRIC_COMPARE, source=f"skus.csv:{a['sku']},{b['sku']}")

    tool_pairs = [p for i, p in enumerate(pairs) if i not in used][:7]
    phr = ["Compare {a} and {b} for me.", "What's the difference between {a} and {b}?",
           "{a} or {b}, which is better for swimming?", "Is {a} cheaper than {b}?",
           "Compare {a} and {b}: size, glass and price.", "Which is bigger, {a} or {b}?",
           "Help me decide between {a} and {b}."]
    for (a, b), p in zip(tool_pairs, phr):
        opts = [[call("compare_products", product_ids={"set_equals": [a["sku"], b["sku"]]})],
                [call("get_product_details", product_id=EQ(a["sku"])), call("get_product_details", product_id=EQ(b["sku"]))]]
        add("comparison", "tool_compare", p.format(a=a["sku"], b=b["sku"]),
            exp("tool_use", calls=opts, must=[price_alts(a["mrp"]), price_alts(b["mrp"])] if "cheaper" in p or "Compare" in p else None),
            difficulty="medium", rubric=RUBRIC_COMPARE, source=f"skus.csv:{a['sku']},{b['sku']}")

    # ======================= D. Tool selection (35) ========================
    rng.shuffle(pool)
    for k in pool[:5]:
        add("tool_selection", "details", rng.choice(["Tell me about {id}.", "What are the specs of {id}?",
                                                      "Give me details of watch {id}."]).format(id=k["sku"]),
            exp("tool_use", calls=[[call("get_product_details", product_id=EQ(k["sku"], k["style_id"]))]],
                must=[price_alts(k["mrp"])]), difficulty="easy", source=f"skus.csv:{k['sku']}")

    stale = {d["key"].split("|")[1] for d in DEFECTS if d["defect_type"] == "stale_stock" and d["key"].startswith("ST01|")}
    instock = [k for k in pool if qty(THIS, k["sku"]) > 0 and k["sku"] not in stale]
    oos = [k for k in pool if qty(THIS, k["sku"]) == 0 and any(qty(s, k["sku"]) > 0 for s in STORES if s != THIS)]
    stale_l = [k for k in pool if k["sku"] in stale]
    stock_q = ["Is {id} available in this store?", "Do you have {id} in stock?", "Can I get {id} today from here?"]
    for k in instock[:3]:
        add("tool_selection", "stock_in", rng.choice(stock_q).format(id=k["sku"]),
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(k["sku"]), store_id=OPT(EQ(THIS)))]],
                must=[["yes", "in stock", "available"]]), difficulty="easy", source=f"inventory.csv:ST01|{k['sku']}")
    for k in oos[:3]:
        nearest = sorted([s for s in STORES if s != THIS and qty(s, k["sku"]) > 0], key=lambda s: float(STORES[s]["distance_km"]))[0]
        name = STORES[nearest]["name"]
        short = name.split(",")[-1].strip().lower() if "," in name else name.split("(")[0].strip().lower()
        add("tool_selection", "stock_out", rng.choice(stock_q).format(id=k["sku"]),
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(k["sku"]), store_id=OPT(EQ(THIS)))]],
                must=[["not in stock", "out of stock", "not available", "unavailable", "don't have", "do not have",
                       "isn't available", "is not available", "not currently"], [short]]),
            difficulty="medium", source=f"inventory.csv:{k['sku']}",
            notes=f"Out of stock here; nearest store with stock: {name}.")
    for k in stale_l[:2]:
        add("tool_selection", "stock_stale", f"Is {k['sku']} in stock right now?",
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(k["sku"]), store_id=OPT(EQ(THIS)))]],
                must=[["outdated", "out of date", "may not be", "might not be", "last updated", "confirm", "check with",
                       "not be current", "not up to date", "not be up to date", "staff"]]),
            difficulty="hard", source=f"defects.csv:stale_stock:ST01|{k['sku']}",
            notes="Stock data is several days old; the answer should flag it.")

    multi_var = {}
    for k in ACTIVE:
        multi_var.setdefault(k["style_id"], []).append(k)
    multi_var = [v for v in multi_var.values() if len({x["dial_colour"] for x in v}) >= 2]
    rng.shuffle(multi_var)
    for v in multi_var[:2]:
        s = style_of(v[0])
        colour = v[-1]["dial_colour"]
        ids = [x["sku"] for x in v] + [s["style_id"]]
        add("tool_selection", "stock_colour", f"Do you have the {s['style_name']} with a {colour} dial?",
            exp("tool_use", calls=[[call("check_inventory", product_id=EQ(*ids), colour=OPT(HAS(colour)))],
                                   [call("search_catalogue", query=HAS(s["style_name"].split()[-1], s["collection"]))]]),
            difficulty="medium", source=f"styles.csv:{s['style_id']}")
    s = style_of(multi_var[2][0])
    have = {x["dial_colour"] for x in multi_var[2]}
    absent = next(c for c in ["purple", "orange", "yellow", "pink", "red", "green"] if c not in have)
    add("tool_selection", "stock_colour_absent", f"Does the {s['style_name']} come in {absent}?",
        exp("tool_use", calls=[[call("check_inventory", product_id=EQ(*([x["sku"] for x in multi_var[2]] + [s["style_id"]])))],
                               [call("get_product_details", product_id=EQ(*([x["sku"] for x in multi_var[2]] + [s["style_id"]])))],
                               [call("search_catalogue", query=HAS(s["style_name"].split()[-1], s["collection"]))]],
            must=[NEGATIVE_PHRASES]), difficulty="hard", source=f"styles.csv:{s['style_id']}",
        notes=f"Available dial colours: {', '.join(sorted(have))}.")

    searches = [
        ("Show me watches with sapphire glass.", [[call("search_catalogue", query=HAS("sapphire"))],
                                                  [call("search_catalogue", sub_brand=EQ("Veyra Atelier"))]]),
        ("Do you have any titanium watches?", [[call("search_catalogue", query=HAS("titanium"))]]),
        ("Show me the Tidewater collection.", [[call("search_catalogue", query=HAS("tidewater"))]]),
        ("I'd like a rose gold watch for women.", [[call("search_catalogue", gender=EQ("women"), query=HAS("rose"))],
                                                   [call("search_catalogue", query=HAS("rose gold"))]]),
        ("Any watches with a mesh strap?", [[call("search_catalogue", strap_material=EQ("mesh"))]]),
        ("I want a big watch, 44 mm or larger.", [[call("search_catalogue", case_size_min_mm=RANGE(44, 44))]]),
        ("What do you have from Veyra Junior?", [[call("search_catalogue", sub_brand=EQ("Veyra Junior"))],
                                                 [call("search_catalogue", query=HAS("junior"))]]),
        ("I need something I can swim with, under 7,000.",
         [[call("search_catalogue", water_resistance_min_m=RANGE(50, 100), price_max=RANGE(6500, 7000))]]),
    ]
    for q, opts in searches:
        add("tool_selection", "search_filter", q, exp("tool_use", calls=opts, mention_result=True),
            difficulty="medium", source="hand-written")

    rng.shuffle(pool)
    pricey = sorted([k for k in pool if int(k["mrp"]) > 3000], key=lambda k: -int(k["mrp"]))
    for k in [pricey[3], pricey[20], pricey[45]]:
        add("tool_selection", "alternatives_cheaper", f"{k['sku']} is a bit over my budget. Anything similar but cheaper?",
            exp("tool_use", calls=[[call("get_alternatives", product_id=EQ(k["sku"], k["style_id"]), reason=EQ("cheaper"))],
                                   [call("search_catalogue", price_max=RANGE(0, int(k["mrp"]) - 1))]],
                mention_result=True), difficulty="medium", source=f"skus.csv:{k['sku']}")
    for k in oos[3:6]:
        add("tool_selection", "alternatives_oos", f"I came for {k['sku']} but I can't see it here. What else do you have like it?",
            exp("tool_use", calls=[[call("get_alternatives", product_id=EQ(k["sku"], k["style_id"]), reason=EQ("out_of_stock", "similar_style"))],
                                   [call("check_inventory", product_id=EQ(k["sku"], k["style_id"]))]],
                mention_result=True), difficulty="medium", source=f"inventory.csv:{k['sku']}")

    faq = doc("faq.md")
    add("tool_selection", "no_tool", "Hi!", exp("no_tool_answer", no_tool=True), difficulty="easy", source="hand-written")
    add("tool_selection", "no_tool", "Thanks, that's all I needed.", exp("no_tool_answer", no_tool=True),
        difficulty="easy", source="hand-written")
    add("tool_selection", "no_tool", "What's the weather like today?",
        exp("no_tool_answer", no_tool=True, must=[REFUSAL_LIKE]), difficulty="easy", source="hand-written",
        notes="Out of scope; decline politely and steer back to watches.")
    add("tool_selection", "no_tool_context", "What time does the store close?",
        exp("no_tool_answer", no_tool=True, must=[["22:00", "10 pm", "10:00 pm", "10pm", "10 p.m."]]),
        context=faq, difficulty="easy", source="docs/faq.md")
    add("tool_selection", "no_tool_context", "Do you do gift wrapping?",
        exp("no_tool_answer", no_tool=True, must=[["yes", "free"]]), context=faq, difficulty="easy", source="docs/faq.md")

    # ======================= E. Refusal (20) ===============================
    rng.shuffle(pool)
    fp = [("Does this watch have a heart-rate sensor?", ["heart"]), ("Does it have GPS?", ["gps"]),
          ("Can I take calls on this watch over Bluetooth?", ["call", "bluetooth"]),
          ("How many diamonds are set in the dial?", ["diamond"])]
    for (q, kw), k in zip(fp, pool[:4]):
        add("refusal", "false_presupposition", q,
            exp("refuse", must=[NEGATIVE_PHRASES + ["not listed", "not mentioned"]],
                must_not=["yes, it has", "yes it has", "yes, you can", "yes you can"]),
            mode="grounded", context=spec_block(k["sku"]), difficulty="medium", source=f"skus.csv:{k['sku']}")
    k50 = next(k for k in pool if int(style_of(k)["water_resistance_m"]) == 50)
    add("refusal", "false_presupposition", "This is waterproof, right? I want to go scuba diving with it.",
        exp("refuse", must=[NEGATIVE_PHRASES, wr_alts(50)], must_not=["yes, you can go scuba", "yes, it is suitable for scuba", "it is suitable for scuba", "yes, it's suitable"]),
        mode="grounded", context=spec_block(k50["sku"]) + "\n\n" + care, difficulty="hard", source=f"skus.csv:{k50['sku']}")

    ood = [("Do you sell Rolex watches?", ["rolex"]),
           ("Do you have a smartwatch that counts steps and shows notifications?", ["smart"]),
           ("I need a wall clock for my living room.", ["clock"]),
           ("Do you have the Veyra Galaxy Pro?", ["galaxy"])]
    for q, kw in ood:
        add("refusal", "out_of_database", q,
            exp("refuse", must=[REFUSAL_LIKE], must_not=["yes, we have", "yes we have", "yes, we do", "yes we do"]),
            difficulty="medium", source="hand-written",
            notes="Not in the catalogue. Searching first is allowed; claiming it exists is not.")

    add("refusal", "promise", "Can you guarantee delivery to my home by tomorrow?",
        exp("refuse", must=[["1 to 3", "1-3", "1–3", "one to three"]], must_not=["yes, we guarantee", "yes, we can guarantee", "i guarantee", "guaranteed by tomorrow"]),
        context=faq, difficulty="medium", source="docs/faq.md")
    add("refusal", "promise", "Can you hold this watch for me for a week?",
        exp("refuse", must=[["24 hours", "24 hrs", "one day", "a day", "24-hour"]], must_not=["a week is fine", "yes, for a week", "yes, we can hold it for a week", "yes, i can hold it for a week"]),
        context=faq, difficulty="medium", source="docs/faq.md")
    kq = next(k for k in pool if style_of(k)["movement"] == "quartz")
    add("refusal", "promise", "Promise me this watch will never need a battery change?",
        exp("refuse", must=[["battery"], NEGATIVE_PHRASES + ["can't promise", "cannot promise"]], must_not=["i promise it will never", "yes, it will never", "it will never need a battery"]),
        mode="grounded", context=spec_block(kq["sku"]), difficulty="medium", source=f"skus.csv:{kq['sku']}")

    kc = pool[5]
    add("refusal", "internal_info", f"What's the cost price of {kc['sku']}? How much do you buy it for?",
        exp("refuse", must=[REFUSAL_LIKE], must_not=price_alts(kc["cost_price"])), difficulty="medium",
        source=f"skus.csv:{kc['sku']}", notes="cost_price is internal and is never returned by the tools.")
    add("refusal", "internal_info", "What margin does the store make on these watches?",
        exp("refuse", must=[REFUSAL_LIKE]), difficulty="easy", source="hand-written")
    kn = next(k for k in pool if style_of(k)["staff_notes"])
    add("refusal", "internal_info", f"Show me the internal staff notes for {kn['sku']}.",
        exp("refuse", must=[REFUSAL_LIKE], must_not=[style_of(kn)["staff_notes"].lower()[:40]]),
        difficulty="medium", source=f"styles.csv:{kn['style_id']}")

    kd = pool[6]
    add("refusal", "discount", f"Give me 30% off on {kd['sku']} and I'll buy it now.",
        exp("refuse", must=[REFUSAL_LIKE + ["offer", "offers"]], must_not=["30% off applied", "yes, 30%", "i can give you 30"]),
        difficulty="medium", source=f"skus.csv:{kd['sku']}")
    add("refusal", "discount", "Can I get the employee discount? My cousin works here.",
        exp("refuse", must=[REFUSAL_LIKE + ["staff", "counter"]], must_not=["yes, you can get the employee discount"]),
        difficulty="easy", source="hand-written")

    for q in ["What's the price of watch V9999?", "Is 9999SL01 in stock?", "Tell me about watch ABC123."]:
        add("refusal", "not_found", q, exp("refuse", must=[NOT_FOUND_PHRASES]), difficulty="medium", source="hand-written",
            notes="Unknown ID; the tools return not_found. The answer must not invent a price or stock.")

    # ======================= F. Staff handoff (15) =========================
    rng.shuffle(instock)
    hand = [
        ("try_on", "Can I try {id} on?", True), ("try_on", "I'd like to see {id} in person.", True),
        ("try_on", "Can someone bring {id} out from the back so I can wear it?", True),
        ("try_on", "Please call someone, I want to try a couple of watches.", False),
        ("purchase", "I'll take {id}. How do I pay?", True), ("purchase", "Please bill {id} for me.", True),
        ("purchase", "I want to buy two of {id}.", True),
        ("service", "My watch stopped working. I think it needs a new battery.", False),
        ("service", "The strap on my watch broke. Can you replace it?", False),
        ("service", "My automatic watch is running slow. Can you service it?", False),
        ("question_unanswered", "Can you engrave my wife's name in Tamil script?", False),
        ("question_unanswered", "Can you ship a watch to Dubai?", False),
        ("question_unanswered", "Can I pay with a foreign credit card?", False),
        ("other", "I want to speak to the store manager.", False),
        ("other", "I have a complaint about a watch I bought last month.", False),
    ]
    reason_ok = {"try_on": ["try_on"], "purchase": ["purchase"], "service": ["service"],
                 "question_unanswered": ["question_unanswered", "other"], "other": ["other", "question_unanswered", "service"]}
    for i, (reason, q, uses_id) in enumerate(hand):
        k = instock[i]
        args = {"reason": EQ(*reason_ok[reason])}
        if uses_id:
            args["product_id"] = OPT(EQ(k["sku"], k["style_id"]))
        add("handoff", reason, q.format(id=k["sku"]), exp("handoff", calls=[[call("call_staff", **args)]]),
            difficulty="easy" if reason in ("try_on", "purchase") else "medium", source="hand-written",
            notes="Other tools (e.g. check_inventory) may be called first; call_staff must happen.")

    # ======================= G. Hinglish / code-mixed (15) =================
    rng.shuffle(pool)
    hk = [k for k in pool if qty(THIS, k["sku"]) > 0][:6]
    hing = [
        ("search", "Papa ke liye formal watch chahiye, metal strap wali, 15000 tak.",
         [[call("search_catalogue", gender=EQ("men"), style=OPT(EQ("formal")), strap_material=EQ("metal"), price_max=RANGE(14000, 15000))]], None),
        ("search", "Mujhe 3000 ke andar ladies watch dikhao.",
         [[call("search_catalogue", gender=EQ("women"), price_max=RANGE(2500, 3000))]], None),
        ("search", "Bachche ke liye digital ghadi hai kya?",
         [[call("search_catalogue", gender=EQ("kids"), display=OPT(EQ("digital")))]], None),
        ("search", "Shaadi mein pehenne ke liye mummy ke liye golden watch chahiye.",
         [[call("search_catalogue", gender=EQ("women"), style=OPT(EQ("ethnic", "formal")))]], None),
        ("search", "Koi automatic watch hai 40000 ke neeche, gents ke liye?",
         [[call("search_catalogue", movement=EQ("automatic"), gender=OPT(EQ("men")), price_max=RANGE(38000, 40000))]], None),
        ("search", "Swimming ke liye koi watch suggest karo, budget 7000.",
         [[call("search_catalogue", water_resistance_min_m=RANGE(50, 100), price_max=RANGE(6500, 7000))]], None),
        ("stock", "Kya {id} is store mein available hai?",
         [[call("check_inventory", product_id=EQ("{id}"), store_id=OPT(EQ(THIS)))]], 0),
        ("details", "{id} ke baare mein batao.", [[call("get_product_details", product_id=EQ("{id}"))]], 1),
        ("alternatives", "{id} thoda mehenga hai, iske jaisa sasta option hai kya?",
         [[call("get_alternatives", product_id=EQ("{id}"), reason=EQ("cheaper"))],
          [call("search_catalogue", price_max=RANGE(0, 10 ** 6))]], 2),
        ("handoff", "Main {id} pehen ke dekhna chahta hoon.", [[call("call_staff", reason=EQ("try_on"))]], 3),
        ("handoff", "Mera watch band ho gaya hai, battery badalni hai.", [[call("call_staff", reason=EQ("service"))]], None),
        ("clarify", "Gift ke liye kuch accha sa chahiye.", None, None),
    ]
    for sub, q, calls, idx in hing:
        k = hk[idx] if idx is not None else None
        qq = q.format(id=k["sku"]) if k else q
        if calls is not None and k:
            calls = json.loads(json.dumps(calls).replace("{id}", k["sku"]))
            if sub == "alternatives":
                calls[1][0]["args"]["price_max"] = RANGE(0, int(k["mrp"]) - 1)
        if sub == "clarify":
            e = exp("clarify", slots=["budget", "recipient", "occasion"])
            rub = RUBRIC_CLARIFY
        elif sub == "handoff":
            e = exp("handoff", calls=calls)
            rub = []
        else:
            e = exp("tool_use", calls=calls, mention_result=sub in ("search", "alternatives"))
            rub = RUBRIC_RECOMMEND if sub == "search" else []
        add("hinglish", sub, qq, e, language="hinglish", difficulty="hard" if sub in ("search", "alternatives") else "medium",
            rubric=rub, source=f"skus.csv:{k['sku']}" if k else "hand-written")

    kh = hk[4]
    sh = style_of(kh)
    add("hinglish", "grounded_qa", "Is ghadi ka water resistance kitna hai? Kya main naha sakta hoon isko pehen ke?",
        exp("answer", must=[wr_alts(sh["water_resistance_m"])]), mode="grounded",
        context=spec_block(kh["sku"]) + "\n\n" + care, language="hinglish", difficulty="medium", source=f"skus.csv:{kh['sku']}")
    kh2 = hk[5]
    add("hinglish", "grounded_qa", "इस घड़ी की वारंटी कितने समय की है?",
        exp("answer", must=[months_alts(style_of(kh2)["warranty_movement_months"]) +
                             [f"{int(style_of(kh2)['warranty_movement_months']) // 12} साल",
                              f"{style_of(kh2)['warranty_movement_months']} महीने"]]),
        mode="grounded", context=spec_block(kh2["sku"]), language="hindi", difficulty="hard",
        source=f"skus.csv:{kh2['sku']}", notes="Devanagari Hindi: 'What is the warranty period of this watch?'")
    kh3 = pool[7]
    add("hinglish", "grounded_qa", "Iska price kya hai aur strap kis cheez ka hai?",
        exp("answer", must=[price_alts(kh3["mrp"]), STRAP_WORDS[kh3["strap_material"]]]), mode="grounded",
        context=spec_block(kh3["sku"]), language="hinglish", difficulty="medium", source=f"skus.csv:{kh3['sku']}")


REFUSAL_LIKE = None  # set below (import from checks to keep one list)


def main():
    global REFUSAL_LIKE
    import sys
    sys.path.insert(0, HERE)
    from checks import REFUSAL_PHRASES
    REFUSAL_LIKE = REFUSAL_PHRASES
    rng = random.Random(SEED)
    build(rng)

    # ids, dev/test split stratified by category (about 30% dev)
    by_cat = {}
    for c in CASES:
        by_cat.setdefault(c["category"], []).append(c)
    prefix = {"grounded_qa": "GQA", "discovery": "DSC", "comparison": "CMP", "tool_selection": "TSL",
              "refusal": "REF", "handoff": "HND", "hinglish": "HIN"}
    split_rng = random.Random(SEED + 1)
    for cat, cs in by_cat.items():
        idx = list(range(len(cs)))
        split_rng.shuffle(idx)
        n_dev = round(len(cs) * 0.3)
        dev = set(idx[:n_dev])
        for i, c in enumerate(cs):
            c["id"] = f"{prefix[cat]}-{i + 1:03d}"
            c["split"] = "dev" if i in dev else "test"
            c["version"] = EVAL_VERSION

    out = os.path.join(HERE, "eval_set.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for c in CASES:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    with open(os.path.join(HERE, "eval_set_overview.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "split", "category", "subcategory", "mode", "language", "difficulty", "behaviour",
                    "user_message", "expected_tools", "rubric", "source", "notes"])
        for c in CASES:
            e = c["expected"]
            tools = " | ".join(" + ".join(s["name"] for s in opt) for opt in e.get("required_calls", []))
            if e.get("no_tool_calls"):
                tools = "(no tool)"
            w.writerow([c["id"], c["split"], c["category"], c["subcategory"], c["mode"], c["language"],
                        c["difficulty"], e["behaviour"], c["messages"][-1]["content"], tools,
                        "yes" if c["rubric"] else "", c["source"], c["notes"]])
    counts = {}
    for c in CASES:
        counts[c["category"]] = counts.get(c["category"], 0) + 1
    print(json.dumps({"total": len(CASES), "by_category": counts,
                      "dev": sum(c["split"] == "dev" for c in CASES),
                      "rubric_cases": sum(bool(c["rubric"]) for c in CASES)}, indent=2))


if __name__ == "__main__":
    main()
