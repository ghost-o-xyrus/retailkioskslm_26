"""
Tests for the Step 8 scorer and judging packet (no model needed).   python -m unittest eval.test_score_rag
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import score_rag as S  # noqa: E402


def load(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


class ScoreRagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {c["id"]: c for c in load(os.path.join(HERE, "rag_cases.jsonl"))}
        cls.chunks = {c["id"]: c for c in load(os.path.join(ROOT, "knowledge", "corpus.jsonl"))}

    def test_auto_checks(self):
        spc = self.cases["R-SPC-001"]                      # water resistance 50 m
        self.assertTrue(S.auto(spc, "It is water resistant to 50 m.", self.chunks)["correct"])
        a = S.auto(spc, "Sorry, I don't have that information.", self.chunks)
        self.assertFalse(a["correct"])
        self.assertTrue(a["refusal_candidate"])
        pnm = self.cases["R-PNM-001"]                      # named product, no facts listed
        name = S.gold_names(pnm, self.chunks)[0]
        self.assertTrue(S.auto(pnm, f"The {name} is a lovely watch.", self.chunks)["correct"])
        dec = self.cases["R-NSD-001"]
        self.assertTrue(S.auto(dec, "Sorry, we don't sell Rolex.", self.chunks)["correct"])
        self.assertFalse(S.auto(dec, "Yes, we have three Rolex models.", self.chunks)["correct"])
        self.assertTrue(S.auto(dec, "", self.chunks)["empty"])
        self.assertEqual(S.condition({"retrieval": {"condition": "always", "fallback": "gate"}}), "deployed")
        self.assertEqual(S.condition({"retrieval": {"condition": "always", "fallback": "shadow"}}), "nofallback")

    def test_score_and_packet_end_to_end(self):
        with tempfile.TemporaryDirectory() as t:
            ids = ["R-SPC-001", "R-NSD-001", "R-NEG-001", "R-HUN-001"]
            replies = {"R-SPC-001": "50 m.", "R-NSD-001": "Yes, we have Rolex.", "R-NEG-001": "No, there isn't.",
                       "R-HUN-001": ""}
            for cond, fb in (("deployed", "gate"), ("none", None)):
                d = os.path.join(t, f"s8_x_rag_{cond}")
                os.makedirs(d)
                with open(os.path.join(d, "run_meta.json"), "w") as f:
                    json.dump({"model": "M", "retrieval": {"condition": "always" if fb else "none", "fallback": fb}}, f)
                with open(os.path.join(d, "cases.jsonl"), "w", encoding="utf-8") as f:
                    for i in ids:
                        ret = {"condition": "always", "chunk_ids": ["faq:do-you-deliver"], "view": "compact",
                               "fallback_would_refuse": i == "R-NSD-001", "hinglish": False} if fb else None
                        f.write(json.dumps({"id": i, "repeat": 0, "final_reply": replies[i], "tool_calls": [],
                                            "retrieval": ret, "metrics": {"end_to_end_ms": 1000}}) + "\n")
            fbp = os.path.join(t, "fb.json")
            with open(fbp, "w") as f:
                json.dump({"messages": {"en": "Sorry, I don't have information about that.", "hinglish": "Maaf"}}, f)
            jdir = os.path.join(t, "judge")
            p = subprocess.run([sys.executable, os.path.join(HERE, "rag_judge", "build_packet.py"),
                                os.path.join(t, "s8_*"), "--out", jdir], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            with open(os.path.join(jdir, "key.json")) as f:
                key = json.load(f)
            self.assertTrue(any(k["case"] == "R-HUN-001" and i.startswith("E") for i, k in key.items()))  # empty
            with open(os.path.join(jdir, "labels_01.json"), "w") as f:
                json.dump([{"item": i, "label": "unsupported" if k["case"] == "R-NSD-001" else "answered"}
                           for i, k in key.items() if i.startswith("J")], f)
            out = os.path.join(t, "scores")
            p = subprocess.run([sys.executable, os.path.join(HERE, "score_rag.py"), os.path.join(t, "s8_*"),
                                "--fallback", fbp, "--out", out, "--labels", jdir], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            with open(os.path.join(out, "report.md"), encoding="utf-8") as f:
                rep = f.read()
            self.assertIn("| s8_x_rag_deployed | deployed | 0/2", rep)       # Rolex "yes" and an empty reply: no decline
            self.assertIn("| 1/2 = 50.0%", rep)                               # judged: the Rolex reply is a hallucination
            self.assertIn("deployed+hard", rep)                               # hard fallback replaces the Rolex reply
            row = next(l for l in rep.splitlines() if l.startswith("| s8_x_rag_deployed | deployed+hard |"))
            self.assertIn("0/2 = 0.0%", row)                                  # no judged hallucination with hard fallback


if __name__ == "__main__":
    unittest.main()
