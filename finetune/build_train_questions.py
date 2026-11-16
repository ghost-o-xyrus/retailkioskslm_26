"""
Objective 4, Step 2a: training questions on the training catalogue (data_train/, built by build_train_catalogue.py),
each with the correct behaviour, in the harness's case format. Nothing here is an eval case.

    python finetune\\build_train_questions.py

Writes finetune/train/{tools,store,followups}.jsonl (split "train") and finetune/train/questions_report.md.

Each case carries "o4", what the oracle (finetune/oracle_server.py) needs to act correctly:
    kind      answer      the shown store information answers it (evidence: groups of strings, any one per group,
                          that must be in what was shown; otherwise the honest reply is "I don't have that")
              not_listed  the card says "not listed" or lacks the asked attribute: say so, offer staff as a question
              decline     nothing answers it (not sold, off-topic, unknown policy, no such design, near miss "no")
              tools       the expected tool calls (first accepted option of the generator's label), then an answer
              handoff     call_staff with these arguments, then confirm
              refuse      internal information, discounts, promises: refuse without a tool
    gaps      the Objective 3 gaps the example trains (format, staff_discipline, not_listed, decline, tool_choice,
              ordinary)
Sources, all re-run on data_train with their own seeds:
    tool cases   eval/build_eval_set.py and eval/build_eval_v11.py (five seeds), tool-mode cases only, plus Hinglish
                 versions of the single-product templates
    store        knowledge/build_retrieval_eval.py's generated question types (larger counts), questions from the
                 training corpus's FAQ, glossary, policy, offer and store chunks, and new unanswerable questions
    follow-ups   the Step 11 recipe (eval/build_followups.py) on the training catalogue
Leakage rules (an eval set is every file in EVAL_FILES): a question is dropped if its normalised text equals an eval
question or its words overlap one by Jaccard >= 0.6 (the Objective 3 Step 9 rule). Tool-case wording comes from the
same templates as the eval generator, so every training tool question is reworded (a lead-in, a softener or a
synonym) and dropped if, with product codes and numbers masked, it still equals an eval question.
"""

import collections
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data_train")
CORPUS = os.path.join(HERE, "knowledge", "corpus.jsonl")
os.environ["SLM_DATA_ROOT"] = DATA                       # must be set before the generators are imported
os.environ["SLM_DATA_DIR"] = os.path.join(DATA, "kiosk")
for p in (ROOT, os.path.join(ROOT, "eval"), os.path.join(ROOT, "knowledge"), os.path.join(ROOT, "retrieval")):
    sys.path.insert(0, p)

OUT = os.path.join(HERE, "train")
SEED = 4404
TOOL_SEEDS = (51, 52, 53, 54, 55)
EVAL_FILES = ["knowledge/retrieval_eval.jsonl", "eval/rag_cases.jsonl", "eval/rag_cases_o3t.jsonl",
              "eval/eval_set.jsonl", "eval/eval_set_v1.1.jsonl", "eval/eval_set_v1.2.jsonl", "eval/eval_set_o3t.jsonl",
              "eval/rag_followups.jsonl", "eval/o3_dialogues.jsonl"]
JACCARD_MAX = 0.6

LEAD_EN = ["Hi, ", "Hello! ", "Quick question: ", "Excuse me, ", "Hey, ", "Could you help? ", "", ""]
TAIL_EN = [" Thanks.", " Please.", " Thank you!", "", "", ""]
LEAD_HI = ["Bhaiya, ", "Suniye, ", "Ek baat batao, ", "Hello, ", ""]
TAIL_HI = [" Please.", " Thank you.", "", ""]
SWAPS = [("Tell me about", "Can you tell me about"), ("What are the specs of",
         "What are the full specs of"), ("Show me", "Can I see"), ("I want", "I'd like"), ("Do you have", "Have you got"),
         ("How much is", "What's the price of"), ("Can I try", "Could I try")]

UNANSWERABLE = {   # (question, language) -- written for this file; checked against the eval sets like every question
    "not_sold": ["Do you sell table clocks?", "Can I buy a watch winder box here?", "Do you stock sunglasses?",
                 "Do you have leather wallets?", "Are there any smart rings?", "Do you sell cufflinks?",
                 "Do you keep stopwatches for sports coaches?", "Can I get an alarm clock here?",
                 "Do you have bracelets without a watch?", "Do you sell perfume gift sets?",
                 "Kya aapke paas wall clock milegi?", "Sunglasses milte hain yahan?", "Smart ring hai kya?",
                 "Purse ya wallet bhi bechte ho?"],
    "off_topic": ["Can you book me a taxi?", "What's the weather tomorrow?", "Who won the match last night?",
                  "Where can I get coffee in this mall?", "Can you recommend a good movie?",
                  "What time does the bank next door close?", "Can you help me with my phone bill?",
                  "Mall mein food court kahan hai?", "Aaj ka match kaun jeeta?", "Cab book kar doge?",
                  "Kal mausam kaisa rahega?"],
    "missing_policy": ["Do you offer student discounts on weekdays?", "Can I pay in instalments without a card?",
                       "Do you lend watches for photo shoots?", "Can I return a watch bought at a partner outlet here?",
                       "Do you have a loyalty app?", "Can I book a home visit for a strap change?",
                       "Kya students ke liye alag discount hai?", "Ghar pe aakar battery badloge kya?",
                       "Watch rent pe milti hai photo shoot ke liye?"],
}
MISSING_TRAIN = [   # attributes no card lists (new wording; the eval set has its own list)
    "What does the {n} weigh in grams?", "Is the strap on the {n} replaceable with a quick-release pin?",
    "What is the power reserve of the {n}?", "How wide are the lugs on the {n}?",
    "Is the {n}'s glass coated against glare?", "Can I see the movement through the back of the {n}?",
    "What size battery goes in the {n}?", "Does the {n} have a screw-down crown?", "How accurate is the {n} per month?",
    "Is the {n} buckle a deployant clasp?", "What wrist size does the {n} strap fit?",
    "{n} ka weight kitna hai?", "{n} ki battery kaun si lagti hai?", "{n} ka strap kitna lamba hai?",
    "{n} ke peeche se movement dikhta hai kya?"]
FAKE_WORDS = ["Zephyrine", "Orbitus", "Galleon", "Marquis", "Saturnia", "Kestrelle", "Vindaloo", "Tarragon",
              "Moonstone", "Cinder", "Halcyon", "Obsidian", "Quasarix", "Ravenna", "Sapphira", "Tundra", "Umbra",
              "Valkyr", "Wyvern", "Xenon", "Yonder", "Zircon", "Basalto", "Cascara", "Dorado", "Equinox", "Fiorella",
              "Granada", "Hydra", "Isola"]
FAKE_TPL = ["Have you got the {c} {w}?", "What's the price of the {c} {w}?", "Can I see the {c} {w} watch?",
            "{c} {w} dikhao.", "{c} {w} kitne ki hai?"]
MISSING_TOPICS = ["a lifetime warranty", "watch insurance", "a buy-back scheme", "custom-made straps",
                  "a price-match guarantee", "repair pickup from home", "corporate bulk orders",
                  "a trade-in for smartwatches", "personal shopping appointments", "gift vouchers on WhatsApp",
                  "night-time delivery", "an extended warranty plan", "a senior citizen discount", "loyalty points",
                  "cash on delivery", "battery recycling", "watch winder servicing", "a 30-day price protection"]
MISSING_TPL_EN = ["Do you offer {t}?", "Is there {t} at this store?", "Can I get {t} here?",
                  "Does Veyra have {t}?", "Tell me about {t}."]
MISSING_TPL_HI = ["Kya yahan {t} milta hai?", "{t} ki facility hai kya?"]
REFUSE = {
    "internal_info": ["How much profit do you make on {id}?", "What did the store pay for {id}?",
                      "{id} ka cost price kya hai?"],
    "discount": ["Can you give me 30% off {id}?", "Give me a special price on {id}, I'm a regular.",
                 "{id} pe extra discount do na."],
}


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def norm(t):
    return " ".join(re.findall(r"[a-z0-9]+", t.lower()))


def mask(t):
    t = re.sub(r"\b\d{4}[A-Z]{2}\d{2}\b|\bV\d{4}\b", "<code>", t)
    return norm(re.sub(r"\d[\d,]*", "0", t))


class Leak:
    def __init__(self):
        from retrievers import tokenize
        self.tok = tokenize
        texts = []
        for rel in EVAL_FILES:
            p = os.path.join(ROOT, rel)
            if not os.path.exists(p):
                continue
            for it in load_jsonl(p):
                if it.get("query"):
                    texts.append(it["query"])
                for m in it.get("messages") or []:
                    if m.get("role") == "user" and isinstance(m.get("content"), str):
                        texts.append(m["content"])
        self.norm = {norm(t) for t in texts}
        self.mask = {mask(t) for t in texts}
        self.toks = [set(self.tok(t)) for t in texts]
        self.dropped = collections.Counter()

    def close_original(self, q, kind):
        """The generator's own text, before rewording: a copy of an eval question (same words) is dropped, and so is a
        hand-written question (no product code) that is close to one; a template filled with a training product
        code is judged after rewording."""
        if norm(q) in self.norm:
            self.dropped[kind + ": copy of an eval question"] += 1
            return True
        if not re.search(r"\b\d{4}[A-Z]{2}\d{2}\b", q):
            a = set(self.tok(q))
            if a and any(b and len(a & b) / len(a | b) >= JACCARD_MAX for b in self.toks):
                self.dropped[kind + ": hand-written, close to an eval question"] += 1
                return True
        return False

    def close(self, q, kind):
        if norm(q) in self.norm:
            self.dropped[kind + ": same text"] += 1
            return True
        if mask(q) in self.mask:
            self.dropped[kind + ": same wording, other product"] += 1
            return True
        a = set(self.tok(q))
        if a and any(b and len(a & b) / len(a | b) >= JACCARD_MAX for b in self.toks):
            self.dropped[kind + ": word overlap >= 0.6"] += 1
            return True
        return False


def is_hinglish(q):
    from language import is_hinglish as h
    return h(q)


def reword(q, rng, lang):
    if lang == "hinglish":
        return rng.choice(LEAD_HI) + q + rng.choice(TAIL_HI)
    for a, b in SWAPS:
        if q.startswith(a) and rng.random() < 0.5:
            q = b + q[len(a):]
            if b.startswith("Could you check if ") and q.endswith("?"):
                pass
            break
    lead = rng.choice(LEAD_EN)
    if lead and q[:1].isupper() and not q.startswith("I ") and not q.startswith("I'"):
        q = q[0].lower() + q[1:]
    return (lead + q + rng.choice(TAIL_EN)).strip()


# ----------------------------------------------------------------------------------------------- tool cases

HI_TOOL = {   # Hinglish phrasings for the single-product tool templates (new wording, not the eval's)
    "details": ["{id} ki saari jaankari dena.", "{id} ke specs kya hain?"],
    "stock_in": ["{id} abhi yahan available hai?", "{id} stock mein hai kya abhi?"],
    "stock_out": ["{id} abhi yahan available hai?", "{id} stock mein hai kya abhi?"],
    "try_on": ["{id} haath pe pehen ke dekhna hai.", "{id} try kar sakta hoon?"],
    "purchase": ["{id} khareedni hai, bill kaise banega?", "{id} le leta hoon, payment kahan karun?"],
}


def tool_kind(c):
    e = c["expected"]
    if e["behaviour"] == "handoff":
        return "handoff"
    if e["behaviour"] == "refuse":
        return "refuse"
    if e.get("required_calls"):
        return "tools"
    return None


def tool_cases(rng, leak):
    import build_eval_set as core
    from checks import REFUSAL_PHRASES
    core.REFUSAL_LIKE = REFUSAL_PHRASES
    import build_eval_v11 as v11
    out, seen = [], set()
    for seed in TOOL_SEEDS:
        core.CASES.clear()
        core.build(random.Random(seed))
        base = list(core.CASES)
        core.CASES.clear()
        for i, c in enumerate(base):
            c["id"], c["set"] = f"S{seed}-{i}", "core"
        cases = base + v11.build_expansion(random.Random(seed * 7), base)
        for c in cases:
            if c["mode"] != "tools" or c.get("history") or len(c["messages"]) != 1:
                continue
            kind = tool_kind(c)
            if kind is None:
                continue                       # clarify cases go to the discovery templates at run time
            text = c["messages"][-1]["content"]
            lang = c["language"]
            if leak.close_original(text, "tool"):
                continue
            if norm(text) in seen:                    # the same question from another seed
                continue
            q = reword(text, rng, "hinglish" if lang != "en" else "en")
            if leak.close(q, "tool"):
                continue
            seen.add(norm(text))
            c["messages"] = [{"role": "user", "content": q}]
            out.append(c)
            sub = c["subcategory"]
            pid = None
            m = re.search(r"\b\d{4}[A-Z]{2}\d{2}\b", text)
            if m and sub in HI_TOOL and rng.random() < 0.9:     # a Hinglish twin of the same task
                pid = m.group(0)
                h = dict(json.loads(json.dumps(c)))
                hq = reword(rng.choice(HI_TOOL[sub]).format(id=pid), rng, "hinglish")
                if norm(hq) not in seen and not leak.close(hq, "tool"):
                    seen.add(norm(hq))
                    h["messages"] = [{"role": "user", "content": hq}]
                    h.update(language="hinglish", category="hinglish", subcategory="paired_" + sub)
                    out.append(h)
    # refusals on training products
    import build_eval_set as core2
    pool = [k["sku"] for k in core2.ACTIVE]
    for sub, tpls in REFUSE.items():
        for i in range(24):
            q = rng.choice(tpls).format(id=rng.choice(pool))
            lang = "hinglish" if is_hinglish(q) else "en"
            q = reword(q, rng, lang)
            if norm(q) in seen or leak.close(q, "tool"):
                continue
            seen.add(norm(q))
            out.append({"category": "refusal", "subcategory": sub, "mode": "tools", "language": lang,
                        "messages": [{"role": "user", "content": q}], "context": None,
                        "expected": {"behaviour": "refuse", "no_tool_calls": True}})
    res = []
    for i, c in enumerate(out):
        kind = tool_kind(c)
        o4 = {"kind": kind, "gaps": ["tool_choice"] if kind == "tools" else
              (["staff_discipline"] if kind == "handoff" else ["decline"])}
        if kind == "tools":
            o4["calls"] = [{"name": s["name"], "args": concrete_args(s["args"])} for s in c["expected"]["required_calls"][0]]
        if kind == "handoff":
            spec = c["expected"]["required_calls"][0][0]
            o4["calls"] = [{"name": "call_staff", "args": concrete_args(spec["args"])}]
        o4["evidence"] = c["expected"].get("must_include") or []
        res.append(dict(id=f"T-TOOL-{i + 1:04d}", category=c["category"], subcategory=c["subcategory"], mode="tools",
                        language=c["language"], difficulty="", messages=c["messages"], context=None,
                        expected=c["expected"], rubric=[], source="finetune/build_train_questions.py", notes="",
                        split="train", set="o4train", paired_with=None, o4=o4))
    return res


def concrete_args(spec):
    out = {}
    for k, m in (spec or {}).items():
        if "absent_or" in m:
            continue                           # optional: leave it out, as a careful caller would
        if "equals_any" in m:
            out[k] = m["equals_any"][0]
        elif "range" in m:
            lo, hi = m["range"]
            out[k] = hi if k.endswith("_max") or k in ("price_max", "case_size_max_mm") else lo
        elif "contains_any" in m:
            out[k] = m["contains_any"][0]
        elif "set_equals" in m:
            out[k] = list(m["set_equals"])
    return out


# ----------------------------------------------------------------------------------------------- store questions

def store_cases(rng, leak):
    import build_retrieval_eval as R
    from build_rag_cases import to_case
    from build_rerank_train import other_queries
    b = R.Builder(SEED, CORPUS, DATA)
    b.products_by_name(90)
    b.products_by_sku(70)
    b.products_by_description(60)
    b.product_specs(320)
    b.product_specs(420, language="hinglish", subtype="hinglish_spec")
    b.product_specs(60, subtype="typo_spec", typo_names=True)
    b.missing_fields()
    b.collections(55)
    b.negatives(260)
    b.missing_attributes(110)
    used = {w for s in b.styles.values() for w in s["style_name"].split()}
    b.nonexistent(20, words=[w for w in R.STYLE_WORDS if w not in used])
    styles = sorted(b.styles.values(), key=lambda s: s["style_id"])
    for i, st in enumerate(rng.sample(styles, 300)):
        tpl = MISSING_TRAIN[i % len(MISSING_TRAIN)]
        b.add("missing_attribute", tpl.format(n=b.name(st)), [], [["not listed", "not mentioned", "don't have"]],
              answer_type="none", language="hinglish" if "{n} k" in tpl or "kya" in tpl else "en",
              related=[f"product:{st['style_id']}"], near_miss=True)
    colls = sorted(b.by_coll)
    for i in range(160):
        c = rng.choice(colls)
        taken = {x["style_name"].replace(c + " ", "", 1) for x in b.by_coll[c]}
        w = rng.choice([x for x in FAKE_WORDS if x not in taken])
        tpl = rng.choice(FAKE_TPL)
        b.add("nonexistent_product", tpl.format(c=c, w=w), [], [["couldn't find", "don't have", "no such", "not find"]],
              answer_type="none", language="hinglish" if tpl.endswith(("dikhao.", "hai?")) else "en",
              related=[f"collection:{re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')}"], near_miss=True)
    problems = b.expand_and_validate()
    if problems:
        sys.exit("label problems: " + "; ".join(problems[:5]))
    items = list(b.items)
    chunks = load_jsonl(CORPUS)
    for c in chunks:                         # FAQ, glossary, policy, offer and store chunks: answered from the chunk
        if c["type"] in ("faq", "glossary", "policy", "offer", "store"):
            for lang, sub, q in other_queries(c, rng):
                items.append(dict(query=q, language=lang, subtype=sub, answer_type="fact", gold_ids=[c["id"]],
                                  related_ids=[], facts=[], near_miss=False, chunk_text=c["text"]))
    for t in MISSING_TOPICS:          # policies the store information never mentions (checked: no doc names them)
        for tpl in rng.sample(MISSING_TPL_EN, 3) + rng.sample(MISSING_TPL_HI, 1):
            q = tpl.format(t=t)
            items.append(dict(query=q[0].upper() + q[1:], language="hinglish" if tpl in MISSING_TPL_HI else "en",
                              subtype="missing_policy", answer_type="none", gold_ids=[], related_ids=[], facts=[],
                              near_miss=False))
    for sub, qs in UNANSWERABLE.items():
        for q in qs:
            items.append(dict(query=q, language="hinglish" if is_hinglish(q) else "en", subtype=sub,
                              answer_type="none", gold_ids=[], related_ids=[], facts=[], near_miss=False))
    out, seen = [], set()
    for it in items:
        q = it["query"]
        if leak.close_original(q, "store"):
            continue
        if rng.random() < 0.5:
            q = reword(q, rng, it["language"])
        if norm(q) in seen or leak.close(q, "store"):
            continue
        seen.add(norm(q))
        it = dict(it, query=q, id=f"T-STORE-{len(out) + 1:04d}", split="train")
        c = to_case(it, "finetune/build_train_questions.py")
        if it["answer_type"] == "fact":
            kind, gaps = "answer", ["staff_discipline"] if it["subtype"].startswith(("product", "hinglish_spec",
                                                                                      "typo", "collection")) else ["ordinary"]
            ev = it["facts"] or [[evidence_of(it.get("chunk_text", ""))]]
        elif it["answer_type"] == "not_listed" or it["subtype"] == "missing_attribute":
            kind, gaps, ev = "not_listed", ["not_listed"], []
        else:
            kind, gaps, ev = "decline", ["decline"], it["facts"]
        c.update(set="o4train", o4={"kind": kind, "gaps": gaps, "evidence": ev, "gold_ids": it["gold_ids"]})
        out.append(c)
    return out


def evidence_of(text):
    """A distinctive piece of a text chunk (its first clause after any heading), used to tell whether it was shown."""
    body = re.sub(r"^[^:\n]{0,80}[:?]\s*", "", text.strip())
    body = re.split(r"[.;\n]", body)[0].strip()
    return body[:60] if len(body) >= 12 else text.strip()[:60]


# ----------------------------------------------------------------------------------------------- follow-ups

FOLLOW_TRAIN = {   # follow-up wording for training (the eval follow-ups use eval/build_followups.py's lists)
    "glass": (["Which crystal is on that one?", "Is that glass scratch-proof?", "What's the crystal made of?"],
              ["Uska glass kaisa hai?", "Kaanch kaun sa laga hai?"]),
    "water_resistance_m": (["Will it survive the rain?", "What water rating does that one have?",
                            "Could I wear that one in the pool?"], ["Paani mein kharab toh nahi hogi?",
                                                                     "Uski water rating kya hai?"]),
    "warranty_movement_months": (["What guarantee comes with that one?", "And the warranty period?"],
                                 ["Guarantee kitne saal ki hai?", "Uspe warranty kitni milegi?"]),
    "country_of_origin": (["Which country makes that one?", "Where was that one manufactured?"],
                          ["Woh kis desh mein bani hai?", "Uska origin kya hai?"]),
    "case_material": (["What metal is that case?", "Is the case steel or something else?"],
                      ["Uska case kis metal ka hai?"]),
    "movement": (["Does that one need a battery?", "Is that a mechanical movement?"],
                 ["Usme battery lagti hai ya automatic hai?"]),
}
COLOUR_TRAIN = (["Is there a {c} dial version of that?", "Can I get that one in {c}?"],
                ["Woh {c} dial mein milegi?", "{c} colour mein hai kya woh?"])
STOCK_TRAIN = (["Do you have that one here right now?", "Can I take that one home today?"],
               ["Woh abhi yahan mil jayegi?", "Aaj le ja sakta hoon kya?"])


def followup_cases(rng, leak):
    import build_followups as F
    from tools import mock_tools
    mock_tools.reload(os.path.join(DATA, "kiosk"))
    db = mock_tools._load()
    store = db["this_store"]
    skus_by_style = collections.defaultdict(list)
    for s in db["skus"].values():
        if s["status"] == "active":
            skus_by_style[s["style_id"]].append(s)
    styles = sorted(sid for sid, st in db["styles"].items() if st["status"] == "active" and skus_by_style.get(sid)
                    and st["gender"] != "kids")
    rng.shuffle(styles)
    faqs = [c for c in load_jsonl(CORPUS) if c["type"] == "faq"]
    plan = {"followup_fact": 220, "followup_colour": 80, "followup_stock": 80, "followup_switch": 70}
    out, it = [], iter(styles * 2)
    for sub, k in plan.items():
        for _ in range(k):
            hi = rng.random() < 0.34
            sid = next(it)
            st, sku = db["styles"][sid], rng.choice(skus_by_style[sid])
            opening = rng.choice(F.OPEN_HI if hi else F.OPEN_EN).format(n=st["style_name"])
            reply = F.earlier_reply(st, sku)
            o4 = {"kind": "answer", "gaps": ["staff_discipline"], "gold_ids": [f"product:{sid}"]}
            expected = {"behaviour": "answer", "must_include": [], "gold_ids": [f"product:{sid}"]}
            if sub == "followup_fact":
                field = rng.choice([f for f in F.FACTS if st.get(f) not in (None, "", "not listed")])
                _, _, mk = F.FACTS[field]
                en, hq = FOLLOW_TRAIN[field]
                follow, ev = rng.choice(hq if hi else en), mk(st)
                o4["evidence"] = ev
            elif sub == "followup_colour":
                have = {s["dial_colour"] for s in skus_by_style[sid]}
                anywhere = " ".join(f"{s['dial_colour']} {s.get('strap_colour') or ''} {s.get('case_finish') or ''}"
                                    for s in skus_by_style[sid]).lower()
                yes = rng.random() < 0.5 and bool(have - {sku["dial_colour"]})
                pick = rng.choice(sorted(have - {sku["dial_colour"]})) if yes else \
                    rng.choice([c for c in F.COLOURS if c not in anywhere])
                follow = rng.choice(COLOUR_TRAIN[1] if hi else COLOUR_TRAIN[0]).format(c=pick)
                o4.update(evidence=[], polarity=("yes" if pick in have else "no"), word=pick)
            elif sub == "followup_stock":
                inv = db["inventory"].get((store, sku["sku"]), {"qty_display": 0, "qty_backroom": 0})
                follow = rng.choice(STOCK_TRAIN[1] if hi else STOCK_TRAIN[0])
                o4.update(evidence=[], polarity="in_stock" if inv["qty_display"] + inv["qty_backroom"] > 0
                          else "out_of_stock")
            else:
                c = rng.choice(faqs)
                follow = c["title"] if not hi else c["title"]
                o4.update(kind="answer", gaps=["ordinary"], evidence=[[evidence_of(c["text"])]], gold_ids=[c["id"]])
            follow = reword(follow, rng, "hinglish" if hi else "en") if rng.random() < 0.5 else follow
            if leak.close(follow, "follow-up"):
                continue
            out.append({"id": f"T-FUP-{len(out) + 1:04d}", "category": "rag", "subcategory": sub, "mode": "tools",
                        "language": "hinglish" if hi else "en", "difficulty": "",
                        "messages": [{"role": "user", "content": opening}, {"role": "assistant", "content": reply},
                                     {"role": "user", "content": follow}],
                        "context": None, "expected": expected, "rubric": [], "source": "finetune/build_train_questions.py",
                        "notes": "", "split": "train", "set": "followup", "paired_with": None, "o4": o4})
    return out


def main():
    rng = random.Random(SEED)
    leak = Leak()
    os.makedirs(OUT, exist_ok=True)
    sets = {"tools": tool_cases(rng, leak), "store": store_cases(rng, leak), "followups": followup_cases(rng, leak)}
    L = ["# Objective 4 training questions (training catalogue)", ""]
    for name, cases in sets.items():
        with open(os.path.join(OUT, f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for c in cases:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        kinds = collections.Counter(c["o4"]["kind"] for c in cases)
        gaps = collections.Counter(g for c in cases for g in c["o4"]["gaps"])
        hi = sum(c["language"] != "en" for c in cases)
        L += [f"## {name}: {len(cases)} cases", "", f"- kinds: {dict(kinds)}", f"- gaps: {dict(gaps)}",
              f"- Hinglish: {hi} ({hi / max(1, len(cases)):.0%})",
              f"- subcategories: {dict(collections.Counter(c['subcategory'] for c in cases).most_common(12))}", ""]
    L += ["## Dropped as too close to an eval question", ""] + [f"- {k}: {v}" for k, v in sorted(leak.dropped.items())]
    with open(os.path.join(OUT, "questions_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
