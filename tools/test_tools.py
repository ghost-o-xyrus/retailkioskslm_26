"""
Unit tests for the mock kiosk tools.

Run from the project folder:
    python -m unittest tools.test_tools -v

Expected values are computed from data/clean (the ground truth), so the tests
also check that the tools' normalisation of the noisy kiosk data is correct.
"""

import csv
import json
import os
import unittest

from tools import mock_tools as mt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CLEAN = os.path.join(ROOT, "data", "clean")


def read(name):
    with open(os.path.join(CLEAN, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


class ToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mt.reload(os.path.join(ROOT, "data", "kiosk"))
        mt.STAFF_LOG = os.devnull
        cls.styles = {s["style_id"]: s for s in read("styles.csv")}
        cls.skus = read("skus.csv")
        cls.inv = {(r["store_id"], r["sku"]): r for r in read("inventory.csv")}
        cls.active = [k for k in cls.skus if k["status"] == "active"]

    # ---- normalisation ----
    def test_kiosk_values_normalise_to_clean(self):
        db = mt._load()
        for sid, clean in self.styles.items():
            s = db["styles"][sid]
            if s["water_resistance_m"] is not None:
                self.assertEqual(s["water_resistance_m"], int(clean["water_resistance_m"]), sid)
            for f in ("case_material", "glass", "function"):
                if s[f] is not None:
                    self.assertEqual(s[f], clean[f], f"{sid} {f}")
        for k in self.skus:
            kk = db["skus"][k["sku"]]
            self.assertEqual(kk["strap_material"], k["strap_material"], k["sku"])
            self.assertEqual(kk["dial_colour"], k["dial_colour"], k["sku"])

    def test_parse_water_resistance(self):
        for raw, m in [("100", 100), ("100M", 100), ("10 ATM", 100), ("200 m / 20 bar", 200), ("", None)]:
            self.assertEqual(mt.parse_water_resistance(raw), m)

    # ---- search_catalogue ----
    def test_search_filters_are_respected(self):
        r = mt.search_catalogue(gender="men", style="formal", price_max=15000, strap_material="metal", limit=10)
        self.assertGreater(r["total_matches"], 0)
        for x in r["results"]:
            self.assertLessEqual(x["mrp"], 15000)
            self.assertIn(x["gender"], ("men", "unisex"))
            self.assertEqual(x["style"], "formal")
            self.assertTrue(x["strap"].endswith("metal"))

    def test_search_excludes_discontinued(self):
        r = mt.search_catalogue(limit=10)
        self.assertTrue(all(x["status"] != "discontinued" for x in r["results"]))
        disc = {k["sku"] for k in self.skus if k["status"] == "discontinued"}
        total_ok = len(self.skus) - len(disc)
        self.assertEqual(r["total_matches"], total_ok)

    def test_search_water_resistance_and_query(self):
        r = mt.search_catalogue(water_resistance_min_m=200, limit=10)
        for x in r["results"]:
            self.assertGreaterEqual(x["water_resistance_m"], 200)
        r = mt.search_catalogue(query="Tidewater", limit=10)
        self.assertTrue(r["results"])
        self.assertTrue(all(x["collection"] == "Tidewater" for x in r["results"]))

    def test_search_query_words(self):
        """Objective 3, Step 2: generic words no longer match everything."""
        everything = mt.search_catalogue(limit=1)["total_matches"]
        self.assertEqual(mt.search_catalogue(query="watch", limit=1)["total_matches"], everything)   # no content words
        self.assertLess(mt.search_catalogue(query="dress watch", limit=1)["total_matches"], everything / 2)
        self.assertEqual(mt.query_tokens("Men's titanium watches for women"), ["titanium"])
        self.assertEqual(mt.query_tokens("green dial watches"), ["green"])
        db = mt._load()
        r = mt.search_catalogue(query="titanium watch", limit=10)
        self.assertTrue(r["results"])
        for x in r["results"]:
            self.assertEqual(db["styles"][db["skus"][x["product_id"]]["style_id"]]["case_material"], "Titanium")
        self.assertEqual(mt.search_catalogue(query="chrono")["total_matches"],
                         mt.search_catalogue(query="chronograph")["total_matches"])          # prefix from 4 letters
        both = mt.search_catalogue(query="sapphire titanium", limit=10)                     # all words preferred
        for x in both["results"]:
            st = db["styles"][db["skus"][x["product_id"]]["style_id"]]
            self.assertEqual((st["case_material"], st["glass"]), ("Titanium", "Sapphire"))

    def test_honest_search_and_compact_render(self):
        """Objective 3, Step 3: spec words match spec fields only; honest headers; compact text."""
        from tools import render
        db = mt._load()
        try:
            mt.HONEST = True
            r = mt.search_catalogue(query="sapphire", limit=10)
            for x in r["results"]:
                self.assertEqual(db["styles"][db["skus"][x["product_id"]]["style_id"]]["glass"], "Sapphire")
            rolex = mt.search_catalogue(query="rolex submariner")
            self.assertEqual(rolex["not_carried_brands"], ["rolex"])
            self.assertEqual(rolex["query_words"], ["submariner"])
            text = render.render("search_catalogue", {"query": "rolex submariner"}, rolex)
            self.assertIn("No watches match", text)
            self.assertIn("does not sell Rolex", text)
            partial = mt.search_catalogue(query="titanium moonphase")
            self.assertFalse(partial["all_words_matched"])
            self.assertIn("closest matches, not exact", render.render("search_catalogue", {}, partial))
            k = r["results"][0]["product_id"]
            d = render.render("get_product_details", {"product_id": k}, mt.get_product_details(k))
            self.assertNotIn(db["skus"][k]["description"][:30], d)
            self.assertIn("use check_inventory", d)
            self.assertIn("Showing 3 of", render.render("search_catalogue", {}, mt.search_catalogue(limit=3)))
            self.assertIn("not listed", render._v(None))
            self.assertTrue(render.render("call_staff", {}, mt.call_staff("other")).startswith("Staff notified"))
        finally:
            mt.HONEST = False
        self.assertNotIn("query_words", mt.search_catalogue(query="sapphire"))      # off by default

    def test_search_one_result_per_style_and_limit(self):
        r = mt.search_catalogue(limit=50)
        self.assertLessEqual(len(r["results"]), mt.MAX_LIMIT)
        ids = [mt._load()["skus"][x["product_id"]]["style_id"] for x in r["results"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_search_no_results(self):
        r = mt.search_catalogue(price_max=10)
        self.assertEqual(r["total_matches"], 0)
        self.assertEqual(r["results"], [])

    # ---- get_product_details ----
    def test_details_by_sku_and_style(self):
        k = self.active[0]
        d = mt.get_product_details(k["sku"])
        self.assertEqual(d["product_id"], k["sku"])
        self.assertEqual(d["mrp"], int(k["mrp"]))
        d2 = mt.get_product_details(k["style_id"])
        self.assertEqual(d2["style_id"], k["style_id"])
        self.assertTrue(d2["variants"])

    def test_details_never_leak_internal_fields(self):
        for k in self.skus[:40]:
            text = json.dumps(mt.get_product_details(k["sku"]))
            self.assertNotIn("cost_price", text)
            self.assertNotIn(k["ean"], text)
            notes = self.styles[k["style_id"]]["staff_notes"]
            if notes:
                self.assertNotIn(notes, text)

    def test_details_unknown_id(self):
        self.assertEqual(mt.get_product_details("NOPE")["error"], "not_found")

    # ---- compare_products ----
    def test_compare(self):
        a, b = self.active[0]["sku"], self.active[-1]["sku"]
        r = mt.compare_products([a, b], ["mrp", "water_resistance_m"])
        self.assertEqual([x["product_id"] for x in r["comparison"]], [a, b])
        self.assertEqual(mt.compare_products([a])["error"], "invalid_arguments")
        self.assertEqual(mt.compare_products([a, "NOPE"])["error"], "not_found")
        self.assertEqual(mt.compare_products([a, b], ["colour_of_box"])["error"], "invalid_arguments")

    # ---- check_inventory ----
    def test_inventory_matches_ground_truth(self):
        for k in self.active[:30]:
            r = mt.check_inventory(k["sku"])["results"][0]
            inv = self.inv[("ST01", k["sku"])]
            self.assertEqual(r["on_display"], int(inv["qty_display"]))
            self.assertEqual(r["in_backroom"], int(inv["qty_backroom"]))

    def test_inventory_colour_resolution(self):
        k = self.active[0]
        r = mt.check_inventory(k["style_id"], colour=k["dial_colour"])
        self.assertTrue(any(x["product_id"] == k["sku"] for x in r["results"]))
        r = mt.check_inventory(k["style_id"], colour="fuchsia-polka-dot")
        self.assertFalse(r["available"])
        self.assertTrue(r["available_colours"])

    def test_inventory_flags_stale_data(self):
        with open(os.path.join(ROOT, "data", "defects.csv"), encoding="utf-8") as f:
            defects = list(csv.DictReader(f))
        stale = [d for d in defects if d["defect_type"] == "stale_stock" and d["key"].startswith("ST01|")]
        if not stale:
            self.skipTest("no stale ST01 rows in this seed")
        sku = stale[0]["key"].split("|")[1]
        r = mt.check_inventory(sku)["results"][0]
        self.assertTrue(r["stock_data_may_be_outdated"])

    # ---- get_alternatives ----
    def test_alternatives_rules(self):
        base = max(self.active, key=lambda k: int(k["mrp"]))
        r = mt.get_alternatives(base["sku"], "cheaper")
        for x in r["alternatives"]:
            self.assertLess(x["mrp"], int(base["mrp"]))
            self.assertTrue(x["in_stock_here"])
            self.assertEqual(x["style"], self.styles[base["style_id"]]["style_tag"])
        self.assertEqual(mt.get_alternatives(base["sku"], "because")["error"], "invalid_arguments")

    # ---- call_staff, get_offers, dispatcher ----
    def test_call_staff(self):
        r = mt.call_staff("try_on", self.active[0]["sku"])
        self.assertEqual(r["status"], "notified")
        self.assertTrue(r["ticket"].startswith("REQ-"))
        self.assertEqual(mt.call_staff("dance")["error"], "invalid_arguments")

    def test_offers_only_current_and_capped(self):
        veyra = [k for k in self.active if self.styles[k["style_id"]]["sub_brand"] == "Veyra" and int(k["mrp"]) >= 15000]
        if veyra:
            r = mt.get_offers(veyra[0]["sku"])
            fest = [o for o in r["offers"] if o["offer"] == "Festive 10% off"]
            self.assertTrue(fest)
            self.assertLessEqual(fest[0]["discount"], 1500)
        nitya = [k for k in self.active if self.styles[k["style_id"]]["sub_brand"] == "Veyra Nitya"]
        r = mt.get_offers(nitya[0]["sku"])
        self.assertFalse(any("Monsoon" in o["offer"] for o in r["offers"]))  # expired

    def test_dispatcher_handles_json_strings_and_bad_input(self):
        r = mt.call_tool("search_catalogue", '{"gender": "women", "limit": 2}')
        self.assertLessEqual(len(r["results"]), 2)
        self.assertEqual(mt.call_tool("fly_to_moon", {})["error"], "unknown_tool")
        self.assertEqual(mt.call_tool("search_catalogue", "{not json")["error"], "invalid_arguments")
        self.assertEqual(mt.call_tool("get_product_details", {"wrong_arg": 1})["error"], "invalid_arguments")
        self.assertEqual(mt.call_tool("search_catalogue", {"price_max": "cheap"})["error"], "invalid_arguments")

    def test_schemas_match_functions(self):
        for sch in mt.load_schemas(include_optional=True):
            name = sch["function"]["name"]
            self.assertIn(name, mt.TOOL_FUNCTIONS)
            fn = mt.TOOL_FUNCTIONS[name]
            params = set(sch["function"]["parameters"]["properties"])
            self.assertTrue(params <= set(fn.__code__.co_varnames[:fn.__code__.co_argcount]), name)


if __name__ == "__main__":
    unittest.main()
