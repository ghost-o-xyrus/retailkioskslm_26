"""
Checks for the retrieval corpus.   python -m unittest knowledge.test_corpus -v

Builds the corpus in memory from data/ (and data_v1/ where present) and checks coverage, IDs, leaks of
internal data, normalisation, retained defects and chunk sizes.
"""

import csv
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_corpus  # noqa: E402

DATA = os.path.join(ROOT, "data")


def text(*parts):
    with open(os.path.join(DATA, *parts), encoding="utf-8") as f:
        return f.read()


def rows(*parts):
    with open(os.path.join(DATA, *parts), encoding="utf-8") as f:
        return list(csv.DictReader(f))


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chunks, cls.meta = build_corpus.build(DATA)
        cls.by_id = {c["id"]: c for c in cls.chunks}
        cls.clean_styles = rows("clean", "styles.csv")
        cls.clean_skus = rows("clean", "skus.csv")
        cls.kiosk_styles = {r["style_id"]: r for r in rows("kiosk", "styles.csv")}
        cls.defects = rows("defects.csv")

    def test_ids_unique_and_stable(self):
        ids = [c["id"] for c in self.chunks]
        self.assertEqual(len(ids), len(set(ids)))
        again, _ = build_corpus.build(DATA)
        self.assertEqual([json.dumps(c, sort_keys=True) for c in again],
                         [json.dumps(c, sort_keys=True) for c in self.chunks], "build is not deterministic")

    def test_coverage(self):
        style_ids = {r["style_id"] for r in self.clean_styles}
        self.assertEqual({c["meta"]["style_id"] for c in self.chunks if c["type"] == "product"}, style_ids)
        product_skus = {s for c in self.chunks if c["type"] == "product" for s in c["meta"]["skus"]}
        self.assertEqual(product_skus, {r["sku"] for r in self.clean_skus})
        for k in self.clean_skus:  # every variant line is in its card
            self.assertIn(f"- {k['sku']}:", self.by_id[f"product:{k['style_id']}"]["text"])
        colls = {r["collection"] for r in self.clean_styles}
        self.assertEqual(len([c for c in self.chunks if c["type"] == "collection"]), len(colls))
        faq = text("docs", "faq.md")
        self.assertEqual(len([c for c in self.chunks if c["type"] == "faq"]), len(re.findall(r"\*\*[^*]+\?\*\*", faq)))
        self.assertEqual(len([c for c in self.chunks if c["type"] == "offer"]), len(rows("kiosk", "prices_promos.csv")))
        self.assertEqual(len([c for c in self.chunks if c["type"] == "store"]), len(rows("kiosk", "stores.csv")))
        if os.path.exists(os.path.join(DATA, "docs", "glossary.md")):
            gl = text("docs", "glossary.md")
            self.assertEqual(len([c for c in self.chunks if c["type"] == "glossary"]), len(re.findall(r"^- \*\*", gl, re.M)))

    def test_prices_match_clean_data(self):
        for k in self.clean_skus[::7]:
            self.assertIn(f"MRP {build_corpus.inr(k['mrp'])}", self.by_id[f"product:{k['style_id']}"]["text"])

    def test_no_internal_data(self):
        corpus = "\n".join(c["text"] for c in self.chunks)
        notes = {r["staff_notes"] for r in self.clean_styles if r["staff_notes"]}
        for n in notes:
            self.assertNotIn(n, corpus, "staff note leaked")
        for k in self.clean_skus:
            text = self.by_id[f"product:{k['style_id']}"]["text"]
            self.assertNotIn(k["ean"], corpus)
            self.assertNotIn(build_corpus.inr(k["cost_price"]), text, f"cost price leaked for {k['sku']}")
        for word in ("HSN", "cost price", "backroom", "qty_", "staff note"):
            self.assertNotIn(word.lower(), corpus.lower().replace("cost prices", ""), word)

    def test_specs_normalised(self):
        abbrevs = ["SS 316L", "P3H", "SAPH", "CHRONO+D", "LTHR", "SIL ", "FKM", " MIN.", " ATM", " bar"]
        for c in self.chunks:
            if c["type"] != "product":
                continue
            spec = c["text"].split("\nDescription:")[0]
            for a in abbrevs:
                self.assertNotIn(a, spec, f"{c['id']} keeps abbreviation {a!r}")

    def test_defects_retained(self):
        contradictions = [d for d in self.defects if d["defect_type"] == "contradiction"]
        self.assertGreaterEqual(len(contradictions), 4)
        claims = {"description claims sapphire crystal": "sapphire crystal resists everyday scratches",
                  "description claims steel bracelet": "solid-link steel bracelet",
                  "description claims swim/snorkel suitable": "Suitable for swimming and snorkelling"}
        sku_style = {k["sku"]: k["style_id"] for k in self.clean_skus}
        for d in contradictions:
            self.assertIn(claims[d["kiosk_value"]], self.by_id[f"product:{sku_style[d['key']]}"]["text"])
        missing = [d for d in self.defects if d["defect_type"] == "missing" and d["file"] == "styles.csv"
                   and d["field"] in ("case_thickness_mm", "case_shape", "glass", "lume", "country_of_origin")]
        self.assertTrue(missing)
        for d in missing:
            self.assertIn("not listed", self.by_id[f"product:{d['key']}"]["text"])

    def test_sizes(self):
        for c in self.chunks:
            self.assertGreater(c["tokens"], 5, c["id"])
            limit = 450 if c["type"] == "product" else 300
            self.assertLessEqual(c["tokens"], limit, c["id"])

    def test_v1_catalogue_builds(self):
        v1 = os.path.join(ROOT, "data_v1")
        if not os.path.exists(v1):
            self.skipTest("data_v1 not present")
        chunks, meta = build_corpus.build(v1)
        self.assertEqual(len([c for c in chunks if c["type"] == "product"]), meta["n_styles"])
        self.assertTrue(all(c["meta"]["in_v1"] for c in self.chunks if c["type"] == "product"
                            and c["meta"]["style_id"] in {x["meta"]["style_id"] for x in chunks if x["type"] == "product"}))


if __name__ == "__main__":
    unittest.main()
