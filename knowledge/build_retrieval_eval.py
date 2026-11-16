"""
Build the retrieval eval set (Objective 2, Step 4).

    python knowledge/build_retrieval_eval.py      # needs knowledge/corpus.jsonl (run build_corpus.py first)

Writes knowledge/retrieval_eval.jsonl and knowledge/retrieval_eval_overview.csv, then validates every label.

Each query has:
    id, query, language (en | hinglish), subtype, split (dev | test)
    answer_type   fact      - a gold chunk holds the answer
                  negative  - a gold chunk proves the answer is "no" (e.g. the collection has no titanium case)
                  not_listed- the right product card is found but the asked field reads "not listed"
                  none      - nothing in the corpus answers it (off-topic, not sold, unknown policy or attribute)
    gold_ids      chunk IDs that answer it; any one counts as a hit. Empty for answer_type none.
    related_ids   chunks a retriever will likely surface that do NOT answer it (the near-miss context)
    facts         groups of acceptable strings the final answer should contain (used end to end, Step 8)
    near_miss     true when similar products exist but the asked thing does not (the misleading-context case)

Product, collection and near-miss questions are generated from the kiosk data (seeded); FAQ, policy, glossary,
offer, store, Hinglish and unanswerable questions are hand-written in retrieval_eval_handwritten.py.
The dev/test split is stratified by subtype (30% dev), fixed by the seed, and made before any retrieval run.
"""

import argparse
import collections
import csv
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import mock_tools  # noqa: E402
import retrieval_eval_handwritten as H  # noqa: E402
from build_corpus import inr  # noqa: E402

DEV_FRACTION = 0.30
NEG = H.NEG
GENDER_WORD = {"men": "men's", "women": "women's", "unisex": "unisex", "kids": "kids'"}


def money(x):
    return [inr(x).replace("Rs. ", ""), str(x)]


def typo(rng, word):
    """One realistic slip: swap two adjacent letters or drop one, never on the first letter."""
    if len(word) < 5:
        return word
    i = rng.randint(1, len(word) - 3)
    if rng.random() < 0.5:
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    return word[:i] + word[i + 1:]


class Builder:
    def __init__(self, seed, corpus_path, data_dir):
        self.rng = random.Random(seed)
        self.chunks = [json.loads(l) for l in open(corpus_path, encoding="utf-8")]
        self.by_id = {c["id"]: c for c in self.chunks}
        mock_tools.reload(os.path.join(data_dir, "kiosk"))
        db = mock_tools._load()
        self.styles = db["styles"]
        self.skus_by_style = collections.defaultdict(list)
        for k in db["skus"].values():
            self.skus_by_style[k["style_id"]].append(k)
        self.by_coll = collections.defaultdict(list)
        for s in self.styles.values():
            self.by_coll[s["collection"]].append(s)
        self.items = []
        self.seen = set()

    def add(self, subtype, query, gold, facts=None, answer_type="fact", language="en", related=(), near_miss=False):
        if query.lower() in self.seen:
            return False
        self.seen.add(query.lower())
        self.items.append(dict(subtype=subtype, query=query, language=language, answer_type=answer_type,
                               gold_ids=list(gold), related_ids=list(related), facts=facts or [],
                               near_miss=near_miss))
        return True

    def name(self, s):
        return s["style_name"]  # e.g. "Meridian Orion"; unique within the catalogue for each collection + word

    def pick_styles(self, n, pred=lambda s: True):
        pool = sorted([s for s in self.styles.values() if pred(s)], key=lambda s: s["style_id"])
        return self.rng.sample(pool, n)

    # ---------------- generated: products ----------------
    def products_by_name(self, n=40):
        tpl = ["Tell me about the {n}.", "Show me the Veyra {n}.", "What can you tell me about the {n} watch?",
               "I saw the {n} online. What is it like?", "Details of the {n}, please."]
        for s in self.pick_styles(n):
            self.add("product_name", self.rng.choice(tpl).format(n=self.name(s)), [f"product:{s['style_id']}"])

    def products_by_sku(self, n=30):
        tpl = ["What is {c}?", "Tell me about watch {c}.", "Details for product code {c}.", "Price of {c}?",
               "Is {c} a men's or women's watch?"]
        for s in self.pick_styles(n):
            k = self.rng.choice(sorted(self.skus_by_style[s["style_id"]], key=lambda k: k["sku"]))
            q = self.rng.choice(tpl).format(c=k["sku"])
            facts = [money(k["mrp"])] if q.startswith("Price") else []
            self.add("product_sku", q, [f"product:{s['style_id']}"], facts)

    def products_by_description(self, n=35):
        made = 0
        pool = sorted(self.styles.values(), key=lambda s: s["style_id"])
        self.rng.shuffle(pool)
        for s in pool:
            if made >= n:
                break
            k = self.rng.choice(self.skus_by_style[s["style_id"]])
            if not (s.get("case_diameter_mm") and k.get("dial_colour") and k.get("strap_material") and s.get("movement")):
                continue
            def match(t):
                return (t["gender"] == s["gender"] and t["movement"] == s["movement"] and t["style_tag"] == s["style_tag"]
                        and t.get("case_diameter_mm") == s["case_diameter_mm"]
                        and any(v.get("dial_colour") == k["dial_colour"] and v.get("strap_material") == k["strap_material"]
                                for v in self.skus_by_style[t["style_id"]]))
            hits = [t for t in self.styles.values() if match(t)]
            if not 1 <= len(hits) <= 3:
                continue
            strap = "metal bracelet" if k["strap_material"] == "metal" else f"{k['strap_material']} strap"
            q = (f"I want a {GENDER_WORD[s['gender']]} {s['style_tag']} watch, {s['movement']}, "
                 f"{s['case_diameter_mm']} mm, with a {k['dial_colour']} dial and a {strap}.")
            if self.add("product_description", q, [f"product:{t['style_id']}" for t in hits]):
                made += 1

    def product_specs(self, n=55, language="en", subtype="product_spec", typo_names=False):
        specs_en = [
            ("water_resistance_m", "How water resistant is the {n}?", lambda v: [[f"{v} m", f"{v}m", f"{v} metres"]]),
            ("case_diameter_mm", "How big is the case on the {n}?", lambda v: [[f"{v} mm", f"{v}mm"]]),
            ("case_thickness_mm", "How thick is the {n}?", lambda v: [[f"{v} mm", f"{v}mm"]]),
            ("glass", "What glass does the {n} have?", lambda v: [[v]]),
            ("movement", "Is the {n} automatic or quartz?", lambda v: [[v]]),
            ("warranty_movement_months", "What warranty comes with the {n}?", lambda v: [[f"{v} months"]]),
            ("country_of_origin", "Where is the {n} made?", lambda v: [[v]]),
            ("price", "How much is the {n}?", None),
        ]
        specs_hi = [
            ("water_resistance_m", "{n} ki water resistance kitni hai?", specs_en[0][2]),
            ("case_diameter_mm", "{n} ka case kitna bada hai?", specs_en[1][2]),
            ("glass", "{n} mein kaunsa glass hai?", specs_en[3][2]),
            ("movement", "{n} automatic hai ya quartz?", specs_en[4][2]),
            ("warranty_movement_months", "{n} pe kitni warranty milti hai?", specs_en[5][2]),
            ("price", "{n} ki keemat kya hai?", None),
        ]
        specs = specs_hi if language == "hinglish" else specs_en
        for i, s in enumerate(self.pick_styles(n)):
            field, tpl, fact = specs[i % len(specs)]
            nm = self.name(s)
            if typo_names:
                coll = s["collection"].split()[0]
                nm = nm.replace(coll, typo(self.rng, coll), 1)
            q = tpl.format(n=nm)
            gold = [f"product:{s['style_id']}"]
            if field == "price":
                prices = sorted({k["mrp"] for k in self.skus_by_style[s["style_id"]]})
                self.add(subtype, q, gold, [sum((money(p) for p in prices), [])], language=language)
                continue
            v = s.get(field)
            if v in (None, ""):
                self.add("spec_not_listed", q, gold, [["not listed", "not mentioned", "not available", "don't have"]],
                         answer_type="not_listed", language=language, near_miss=True)
            else:
                if isinstance(v, float):
                    facts = [fact(f"{v:g}")[0] + fact(f"{v}")[0]]   # "10 mm" or "10.0 mm"
                else:
                    facts = fact(v)
                self.add(subtype, q, gold, facts, language=language)

    def missing_fields(self):
        """Every style whose kiosk record lacks a field becomes one 'not listed' question (capped)."""
        fields = {"case_thickness_mm": "How thick is the {n}?", "glass": "What glass does the {n} have?",
                  "country_of_origin": "Where is the {n} made?", "case_shape": "What shape is the {n}'s case?"}
        cands = [(s, f) for s in sorted(self.styles.values(), key=lambda s: s["style_id"]) for f in fields
                 if s.get(f) in (None, "")]
        for s, f in self.rng.sample(cands, min(12, len(cands))):
            self.add("spec_not_listed", fields[f].format(n=self.name(s)), [f"product:{s['style_id']}"],
                     [["not listed", "not mentioned", "not available", "don't have"]], answer_type="not_listed",
                     near_miss=True)

    def missing_attributes(self, n=25):
        no_mesh = lambda s: all(k.get("strap_material") != "mesh" for k in self.skus_by_style[s["style_id"]])
        for i, s in enumerate(self.pick_styles(n, no_mesh)):  # the glossary describes mesh-strap clasps
            attr, tpl = H.MISSING_ATTRIBUTE[i % len(H.MISSING_ATTRIBUTE)]
            self.add("missing_attribute", tpl.format(name=self.name(s)), [], [["not listed", "not mentioned", "don't have"]],
                     answer_type="none", related=[f"product:{s['style_id']}"], near_miss=True)

    # ---------------- generated: collections and near misses ----------------
    def collections(self, n=25):
        tpl = [("What is the price range of the {c} collection?", "price"),
               ("Which dial colours does the {c} range come in?", "dials"),
               ("What case sizes are there in {c}?", "sizes"),
               ("How many designs are in the {c} collection?", "count")]
        colls = sorted(self.by_coll)
        for i, c in enumerate(self.rng.sample(colls, n)):
            q, kind = tpl[i % len(tpl)]
            styles = self.by_coll[c]
            skus = [k for s in styles for k in self.skus_by_style[s["style_id"]]]
            if kind == "price":
                facts = [money(min(k["mrp"] for k in skus)), money(max(k["mrp"] for k in skus))]
            elif kind == "dials":
                facts = [[sorted({k["dial_colour"] for k in skus if k.get("dial_colour")})[0]]]
            elif kind == "sizes":
                sizes = [s["case_diameter_mm"] for s in styles if s.get("case_diameter_mm")]
                facts = [[f"{min(sizes)}"], [f"{max(sizes)}"]]
            else:
                facts = [[str(len(styles))]]
            self.add("collection", q.format(c=c), [f"collection:{re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')}"], facts)

    def negatives(self, n=30):
        """Questions whose honest answer is 'no': the collection lacks the asked option, which exists elsewhere."""
        dims = [
            ("case_material", lambda v: f"Is there a {v.lower()} {{c}}?", "style"),
            ("strap_material", lambda v: f"Does the {{c}} come with a {v} strap?" if v != "metal" else "Does the {c} come with a metal bracelet?", "sku"),
            ("movement", lambda v: f"Do you have a {v} {{c}}?", "style"),
            ("gender", lambda v: f"Is there a {{c}} watch for {v}?" if v != "unisex" else "Is there a unisex {c}?", "style"),
            ("display", lambda v: f"Do you have a {v} {{c}}?", "style"),
            ("dial_colour", lambda v: f"Does the {{c}} come with a {v} dial?", "sku"),
        ]
        values = {"case_material": ["Titanium", "Stainless Steel 316L", "Brass", "Resin", "Plastic"],
                  "strap_material": ["leather", "metal", "rubber", "silicone", "mesh", "fabric"],
                  "movement": ["automatic", "solar", "quartz"], "gender": ["men", "women", "kids"],
                  "display": ["digital", "analog"], "dial_colour": ["purple", "red", "green", "orange", "pink", "yellow"]}
        colls = sorted(self.by_coll)
        made, tries = 0, 0
        while made < n and tries < 2000:
            tries += 1
            c = self.rng.choice(colls)
            field, tpl, level = self.rng.choice(dims)
            v = self.rng.choice(values[field])
            if level == "style":
                present = {s.get(field) for s in self.by_coll[c]}
            else:
                present = {k.get(field) for s in self.by_coll[c] for k in self.skus_by_style[s["style_id"]]}
            if v in present:
                continue
            q = tpl(v).format(c=c)
            if any(it["query"] == q for it in self.items):
                continue
            cid = f"collection:{re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')}"
            self.add("negative", q, [cid], [NEG], answer_type="negative",
                     related=[f"product:{s['style_id']}" for s in self.by_coll[c][:3]], near_miss=True)
            made += 1

    def nonexistent(self, n=15, words=None):
        colls = sorted(self.by_coll)
        made = 0
        while made < n:
            c = self.rng.choice(colls)
            used = {s["style_name"].replace(c + " ", "", 1) for s in self.by_coll[c]}
            w = self.rng.choice(sorted(set(words) - used))
            q = self.rng.choice(["Do you have the {c} {w}?", "How much is the {c} {w}?", "Show me the Veyra {c} {w}."]).format(c=c, w=w)
            cid = f"collection:{re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')}"
            self.add("nonexistent_product", q, [], [["couldn't find", "could not find", "don't have", "no such", "not find", "doesn't exist", "not in"]],
                     answer_type="none", related=[cid], near_miss=True)
            made += 1

    # ---------------- hand-written ----------------
    def handwritten(self):
        for cid, q, facts in H.FAQ:
            self.add("faq", q, [cid], facts)
        for cid, q, facts in H.POLICY:
            self.add("policy", q, [cid], facts)
        for cid, q in H.GLOSSARY:
            self.add("glossary", q, [cid])
        for cid, q, facts in H.OFFERS:
            self.add("offer", q, [cid], facts)
        for cid, q, facts in H.STORES:
            self.add("store", q, [cid], facts)
        for cid, q, facts in H.HINGLISH:
            self.add("hinglish_text", q, [cid], facts, language="hinglish")
        for q in H.NOT_SOLD:
            self.add("not_sold", q, [], [["sorry", "don't have", "do not have", "don't sell", "do not sell", "only", "not"]], answer_type="none")
        for q in H.OFF_TOPIC:
            self.add("off_topic", q, [], [["sorry", "can't", "cannot", "only help", "watch"]], answer_type="none")
        for q in H.MISSING_POLICY:
            self.add("missing_policy", q, [], [["not sure", "don't have", "staff", "not listed", "can't confirm"]], answer_type="none")

    # ---------------- gold expansion and checks ----------------
    @staticmethod
    def has_facts(text, facts):
        low = text.lower()
        return all(any(f.lower() in low for f in group) for group in facts)

    def expand_and_validate(self):
        problems = []
        text_types = {"faq", "policy", "glossary", "offer", "store"}
        for it in self.items:
            for g in it["gold_ids"]:
                if g not in self.by_id:
                    problems.append(f"{it['query']!r}: unknown gold id {g}")
            if it["answer_type"] == "fact" and it["facts"] and it["gold_ids"]:
                if not any(self.has_facts(self.by_id[g]["text"], it["facts"]) for g in it["gold_ids"] if g in self.by_id):
                    problems.append(f"{it['query']!r}: facts {it['facts']} not in gold {it['gold_ids']}")
                # other text chunks that state the same facts also answer it
                if all(self.by_id[g]["type"] in text_types for g in it["gold_ids"] if g in self.by_id):
                    extra = [c["id"] for c in self.chunks if c["type"] in text_types and c["id"] not in it["gold_ids"]
                             and self.has_facts(c["text"], it["facts"]) and len(it["facts"][0]) > 0
                             and min(len(f) for grp in it["facts"] for f in grp) >= 4]
                    it["gold_ids"] += extra[:3]
            if it["answer_type"] == "not_listed":
                card = self.by_id[it["gold_ids"][0]]["text"]
                if "not listed" not in card:
                    problems.append(f"{it['query']!r}: card has no 'not listed' field")
        for q in H.NOT_SOLD + H.MISSING_POLICY:
            pass  # absence is checked by keyword in test_retrieval_eval.py
        return problems

    def split(self, seed):
        rng = random.Random(seed + 1)
        by_sub = collections.defaultdict(list)
        for it in self.items:
            by_sub[it["subtype"]].append(it)
        for sub, items in sorted(by_sub.items()):
            idx = list(range(len(items)))
            rng.shuffle(idx)
            n_dev = max(1, round(len(items) * DEV_FRACTION))
            for rank, i in enumerate(idx):
                items[i]["split"] = "dev" if rank < n_dev else "test"
        counters = collections.Counter()
        prefix = {"product_name": "PNM", "product_sku": "SKU", "product_description": "DSC", "product_spec": "SPC",
                  "hinglish_spec": "HSP", "typo_spec": "TYP", "spec_not_listed": "NLS", "collection": "COL",
                  "negative": "NEG", "faq": "FAQ", "policy": "POL", "glossary": "GLO", "offer": "OFR", "store": "STR",
                  "hinglish_text": "HTX", "not_sold": "NSD", "off_topic": "OFF", "missing_policy": "MPO",
                  "missing_attribute": "MAT", "nonexistent_product": "NEX"}
        for it in self.items:
            p = prefix[it["subtype"]]
            counters[p] += 1
            it["id"] = f"R-{p}-{counters[p]:03d}"


STYLE_WORDS = ["Zenith", "Aurora", "Matrix", "Phantom", "Titan", "Eclipse", "Nimbus", "Cosmo", "Vertex", "Spectra",
               "Legend", "Infinity", "Royale", "Mirage", "Velvet", "Quantum", "Saga", "Topaz", "Raven", "Ember"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=2027)
    ap.add_argument("--corpus", default=os.path.join(HERE, "corpus.jsonl"))
    ap.add_argument("--data", default=os.path.join(ROOT, "data"))
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    b = Builder(a.seed, a.corpus, a.data)
    b.products_by_name()
    b.products_by_sku()
    b.products_by_description()
    b.product_specs(55)
    b.product_specs(25, language="hinglish", subtype="hinglish_spec")
    b.product_specs(25, subtype="typo_spec", typo_names=True)
    b.missing_fields()
    b.collections()
    b.negatives()
    b.handwritten()
    b.missing_attributes()
    used_words = {w for s in b.styles.values() for w in s["style_name"].split()}
    b.nonexistent(15, words=[w for w in STYLE_WORDS if w not in used_words])
    problems = b.expand_and_validate()
    if problems:
        print("Label problems:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    b.split(a.seed)
    # exact-duplicate queries are not allowed
    qs = [it["query"].lower() for it in b.items]
    dupes = [q for q, c in collections.Counter(qs).items() if c > 1]
    if dupes:
        sys.exit(f"Duplicate queries: {dupes[:5]}")
    keys = ["id", "query", "language", "subtype", "answer_type", "gold_ids", "related_ids", "facts", "near_miss", "split"]
    with open(os.path.join(a.out, "retrieval_eval.jsonl"), "w", encoding="utf-8") as f:
        for it in b.items:
            f.write(json.dumps({k: it[k] for k in keys}, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "retrieval_eval_overview.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "split", "subtype", "answer_type", "language", "near_miss", "query", "gold_ids"])
        for it in b.items:
            w.writerow([it["id"], it["split"], it["subtype"], it["answer_type"], it["language"], it["near_miss"],
                        it["query"], " ".join(it["gold_ids"])])
    # summary
    print(f"{len(b.items)} queries")
    by = collections.Counter((it["subtype"], it["split"]) for it in b.items)
    for sub in sorted({it["subtype"] for it in b.items}):
        print(f"  {sub:20s} dev {by[(sub, 'dev')]:3d}  test {by[(sub, 'test')]:3d}")
    at = collections.Counter((it["answer_type"], it["split"]) for it in b.items)
    print("  by answer type:", {k: v for k, v in sorted(at.items())})
    print("  near-miss:", sum(it["near_miss"] for it in b.items), " Hinglish:", sum(it["language"] == "hinglish" for it in b.items))


if __name__ == "__main__":
    main()
