"""
Checks for the retrieval eval set.   python -m unittest knowledge.test_retrieval_eval -v

Reads knowledge/retrieval_eval.jsonl and knowledge/corpus.jsonl (build both first).
"""

import collections
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return [json.loads(l) for l in f]


# Words whose presence in the corpus would mean an "unanswerable" question is in fact answerable.
ABSENT_TERMS = {
    "not_sold": ["rolex", "casio", "g-shock", "apple watch", "smartwatch", "heart rate", "heart-rate", "fitness band",
                 "wall clock", "pocket watch", "sunglasses", "smart ring", "omega", "solid gold",
                 "diamond", "alarm clock", "winder", "gps", "fossil", "wallet", "wooden watch"],  # not "perfume": see below
    "missing_policy": ["singapore", "student", "foreign", "designer", "mumbai", "price-match", "price match", "logo",
                       "bulk", "same-day", "same day delivery", "loyalty", "ceo", "try-on service", "home try",
                       "rent", "dubai", "special order", "not in the catalogue"],
    "missing_attribute": ["grams", "weighs", "weight", "battery model", "sr626", "see-through",
                          "anti-reflective", "strap length"],
}
# Words that do appear, but never as an answer: lexical traps, kept on purpose.
#   perfume  - care guide: "avoid perfume ... on leather straps" (does not mean the store sells perfume)
#   clasp    - glossary: mesh straps have an adjustable clasp (so clasp questions skip mesh-strap watches)
#   caseback - FAQ: engraving is done on the caseback (says nothing about see-through casebacks)


class RetrievalEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = load("retrieval_eval.jsonl")
        cls.chunks = {c["id"]: c for c in load("corpus.jsonl")}
        cls.corpus = "\n".join(c["text"] for c in cls.chunks.values()).lower()

    def test_ids_and_queries_unique(self):
        self.assertEqual(len({i["id"] for i in self.items}), len(self.items))
        qs = [i["query"].lower() for i in self.items]
        self.assertEqual(len(set(qs)), len(qs))

    def test_gold_exists_and_answer_types_consistent(self):
        for it in self.items:
            for g in it["gold_ids"] + it["related_ids"]:
                self.assertIn(g, self.chunks, it["id"])
            if it["answer_type"] == "none":
                self.assertEqual(it["gold_ids"], [], it["id"])
            else:
                self.assertTrue(it["gold_ids"], it["id"])
            self.assertFalse(set(it["gold_ids"]) & set(it["related_ids"]), it["id"])

    def test_facts_in_gold(self):
        for it in self.items:
            if it["answer_type"] != "fact" or not it["facts"]:
                continue
            ok = any(all(any(f.lower() in self.chunks[g]["text"].lower() for f in grp) for grp in it["facts"])
                     for g in it["gold_ids"])
            self.assertTrue(ok, f"{it['id']}: facts not in any gold chunk")

    def test_not_listed_cards(self):
        for it in self.items:
            if it["answer_type"] == "not_listed":
                self.assertIn("not listed", self.chunks[it["gold_ids"][0]]["text"], it["id"])

    def test_unanswerable_really_absent(self):
        for sub, terms in ABSENT_TERMS.items():
            for t in terms:
                found = re.search(r"\b" + re.escape(t) + r"\b", self.corpus)
                self.assertIsNone(found, f"'{t}' appears in the corpus, so {sub} questions may be answerable")

    def test_clasp_questions_avoid_mesh(self):
        for it in self.items:
            if "clasp" in it["query"]:
                card = self.chunks[it["related_ids"][0]]["text"]
                self.assertNotIn("mesh strap", card, it["id"])

    def test_nonexistent_products_absent(self):
        names = {c["title"].lower() for c in self.chunks.values() if c["type"] == "product"}
        for it in self.items:
            if it["subtype"] == "nonexistent_product":
                m = re.search(r"the (?:veyra )?(.+?)[?.]$", it["query"], re.I)
                self.assertNotIn("veyra " + m.group(1).lower(), names, it["id"])

    def test_negatives_proved_by_collection_chunk(self):
        for it in self.items:
            if it["subtype"] != "negative":
                continue
            text = self.chunks[it["gold_ids"][0]]["text"]
            m = re.search(r"with an? (.+?) dial\?$", it["query"])
            if m:
                dials = re.search(r"Dial colours: (.+?)\.", text).group(1).split(", ")
                self.assertNotIn(m.group(1), dials, it["id"])
            m = re.search(r"with an? (\w+) strap\?$", it["query"])
            if m:
                straps = re.search(r"Straps: (.+?)\.", text).group(1).split(", ")
                self.assertNotIn(m.group(1), straps, it["id"])

    def test_split(self):
        by = collections.defaultdict(collections.Counter)
        for it in self.items:
            by[it["subtype"]][it["split"]] += 1
        for sub, c in by.items():
            self.assertGreaterEqual(c["dev"], 1, sub)
            self.assertGreaterEqual(c["test"], 1, sub)
        dev = sum(c["dev"] for c in by.values()) / len(self.items)
        self.assertTrue(0.25 <= dev <= 0.35, dev)

    def test_coverage_targets(self):
        test = [i for i in self.items if i["split"] == "test"]
        self.assertGreaterEqual(sum(1 for i in test if i["gold_ids"]), 250, "too few answerable test queries")
        self.assertGreaterEqual(sum(1 for i in test if i["answer_type"] == "none"), 50, "too few unanswerable")
        self.assertGreaterEqual(sum(1 for i in test if i["near_miss"]), 50, "too few near-miss")
        self.assertGreaterEqual(sum(1 for i in self.items if i["language"] == "hinglish"), 40)


if __name__ == "__main__":
    unittest.main()
