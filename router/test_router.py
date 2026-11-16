"""
Tests for the Step 4 router (no models).   python -m unittest router.test_router -v
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from router.router import Router  # noqa: E402
from router import check_router  # noqa: E402


class RouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Router()

    def route(self, text, history=()):
        msgs = [{"role": "user", "content": h} for h in history] + [{"role": "user", "content": text}]
        return self.r.route(msgs)["route"]

    def test_examples(self):
        self.assertEqual(self.route("Is 1356AL01 available in this store?"), "stock")
        self.assertEqual(self.route("Give me details of watch 1356AL01."), "lookup")
        self.assertEqual(self.route("Compare 1102SL03 and 1093SL02 for me."), "compare")
        self.assertEqual(self.route("Formal watch for my father with a metal bracelet, budget around 15,000."), "shopping")
        self.assertEqual(self.route("Papa ke liye formal watch chahiye, metal strap wali, 15000 tak."), "shopping")
        self.assertEqual(self.route("Can I try 1452RR03 on?"), "staff")
        self.assertEqual(self.route("Hi!"), "chat")
        self.assertEqual(self.route("How long is the warranty?"), "store")
        self.assertEqual(self.route("Do you sell Rolex watches?"), "store")
        self.assertEqual(self.route("What can you tell me about the Sovereign Orion watch?"), "store")
        self.assertEqual(self.route("Office, around 10,000. He likes leather straps.",
                                    ["I want a gift for my husband."]), "shopping")

    def test_labels_and_dev_check(self):
        subprocess.run([sys.executable, os.path.join(ROOT, "eval", "route_labels.py")], check=True, capture_output=True)
        with open(os.path.join(ROOT, "eval", "route_labels.json"), encoding="utf-8") as f:
            labels = json.load(f)
        self.assertTrue(all(v["route"] for v in labels.values()))
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(check_router.main(["--rules-only", "--out", t]), 0)
            with open(os.path.join(t, "report.md"), encoding="utf-8") as f:
                rep = f.read()
            self.assertIn("**Verdict: PASS**", rep)                     # rules alone pass on dev
            self.assertEqual(check_router.main(["--fake-encoder", "--out", t]), 0)   # prototype stage runs


if __name__ == "__main__":
    unittest.main()
