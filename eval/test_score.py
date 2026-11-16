"""
Tests for eval/score.py.   python -m unittest eval.test_score -v
"""

import json
import os
import tempfile
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import score  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rec(reply="", calls=(), flags=()):
    return {"final_reply": reply, "flags": list(flags),
            "tool_calls": [{"name": n, "arguments": a, "arguments_valid_json": a is not None, "known_tool": True,
                            "result": r} for n, a, r in calls]}


SEARCH_RESULT = {"results": [{"product_id": "1110SM01", "name": "Veyra Classique Atlas White Dial Watch"}]}


class ScoreTests(unittest.TestCase):
    def test_stats(self):
        p, lo, hi = score.wilson(80, 100)
        self.assertAlmostEqual(p, 0.8)
        self.assertTrue(0.70 < lo < 0.72 and 0.86 < hi < 0.88)
        self.assertEqual(score.mcnemar_exact(0, 0), 1.0)
        self.assertLess(score.mcnemar_exact(0, 10), 0.01)
        d, lo, hi = score.paired_bootstrap([1] * 50, [0] * 50)
        self.assertEqual(d, 1.0)

    def test_tool_case(self):
        case = {"mode": "tools", "expected": {"behaviour": "tool_use", "must_mention_tool_result": True,
                "required_calls": [[{"name": "search_catalogue", "args": {"price_max": {"range": [14000, 15000]}}}]]}}
        good = score.score_case(case, rec("Try the Classique Atlas at 12,795.",
                                          [("search_catalogue", {"price_max": 15000}, SEARCH_RESULT)]))
        self.assertTrue(good["passed"])
        wrong_arg = score.score_case(case, rec("Try the Classique Atlas.", [("search_catalogue", {"price_max": 50000}, SEARCH_RESULT)]))
        self.assertFalse(wrong_arg["tool_ok"])
        ungrounded = score.score_case(case, rec("Try our Galaxy model.", [("search_catalogue", {"price_max": 15000}, SEARCH_RESULT)]))
        self.assertFalse(ungrounded["grounded_ok"])
        as_text = score.score_case(case, rec("<tool_call>...", [], ["tool_call_as_text"]))
        self.assertFalse(as_text["format_ok"])
        self.assertFalse(as_text["passed"])

    def test_no_tool_clarify_facts_forbidden(self):
        no_tool = {"mode": "tools", "expected": {"behaviour": "no_tool_answer", "no_tool_calls": True}}
        self.assertTrue(score.score_case(no_tool, rec("Hello!"))["passed"])
        self.assertFalse(score.score_case(no_tool, rec("Hi", [("search_catalogue", {}, SEARCH_RESULT)]))["passed"])
        clarify = {"mode": "tools", "expected": {"behaviour": "clarify", "clarify_slots": ["budget"]}}
        self.assertTrue(score.score_case(clarify, rec("Sure! What's your budget?"))["passed"])
        self.assertFalse(score.score_case(clarify, rec("Here is a watch."))["passed"])
        g = {"mode": "grounded", "expected": {"behaviour": "answer", "must_include": [["50 m"]], "must_not_include": ["yes, it has"]}}
        self.assertTrue(score.score_case(g, rec("It is rated to 50m."))["passed"])
        self.assertFalse(score.score_case(g, rec("It is rated to 150 m."))["passed"])
        self.assertFalse(score.score_case(g, rec("Yes, it has 50 m."))["passed"])

    def test_errors_fail(self):
        case = {"mode": "tools", "expected": {"behaviour": "tool_use"}}
        self.assertFalse(score.score_case(case, None)["passed"])
        self.assertFalse(score.score_case(case, {"error": "server_down"})["passed"])


class Objective3Step2Tests(unittest.TestCase):
    def test_credit_for_shown_cards(self):
        sys.path.insert(0, os.path.dirname(HERE))
        from tools import mock_tools as mt
        k = next(iter(mt._load()["skus"].values()))
        short = " ".join(k["product_name"].split()[1:3])
        case = {"mode": "tools", "expected": {"behaviour": "tool_use", "must_mention_tool_result": True,
                "required_calls": [[{"name": "get_product_details", "args": {"product_id": {"equals_any": [k["sku"]]}}}]]}}
        r = rec(f"The {short} has a {k['dial_colour']} dial.")
        r["retrieval"] = {"condition": "always", "chunk_ids": [f"product:{k['style_id']}"], "fallback_applied": False}
        self.assertFalse(score.score_case(case, r)["passed"])                       # default: unchanged
        c = score.score_case(case, r, credit_shown=True)
        self.assertTrue(c["passed"])
        self.assertEqual(c["credited"], ["tool_ok", "grounded_ok"])
        r["retrieval"]["fallback_applied"] = True                                   # gate: card not shown
        self.assertFalse(score.score_case(case, r, credit_shown=True)["passed"])
        stock = {"mode": "tools", "expected": {"behaviour": "tool_use",
                 "required_calls": [[{"name": "check_inventory", "args": {"product_id": {"equals_any": [k["sku"]]}}}]]}}
        r["retrieval"]["fallback_applied"] = False
        self.assertFalse(score.score_case(stock, r, credit_shown=True)["passed"])  # cards carry no stock

    def test_eval_v12_label_fix(self):
        import json
        import subprocess
        subprocess.run([sys.executable, os.path.join(HERE, "build_eval_v12.py")], check=True, capture_output=True)
        with open(os.path.join(HERE, "eval_set_v1.2.jsonl"), encoding="utf-8") as f:
            v12 = {c["id"]: c for c in map(json.loads, f)}
        with open(os.path.join(HERE, "eval_set_v1.1.jsonl"), encoding="utf-8") as f:
            v11 = {c["id"]: c for c in map(json.loads, f)}
        self.assertEqual(len(v12), len(v11))
        changed = [i for i in v11 if v11[i]["expected"] != v12[i]["expected"]]
        self.assertEqual(sorted(changed), ["TSL-097", "TSL-098"])
        stock_only = rec("It is out of stock here.", [("check_inventory", {"product_id": "x"}, {})])
        opts = v12["TSL-097"]["expected"]["required_calls"]
        self.assertEqual([[s["name"] for s in o] for o in opts], [["get_alternatives"]])
        self.assertTrue(all(c["split"] == "test" for i, c in v12.items() if i in changed))   # dev unaffected
        self.assertIsNotNone(stock_only)

    def test_noise_floor(self):
        import json
        import tempfile
        import noise_floor
        with tempfile.TemporaryDirectory() as t:
            d = os.path.join(t, "o3s1sp_x_rag_b0")
            os.makedirs(d)
            with open(os.path.join(d, "run_meta.json"), "w") as f:
                json.dump({"model": "M", "eval_file": "eval/rag_cases.jsonl"}, f)
            with open(os.path.join(d, "cases.jsonl"), "w", encoding="utf-8") as f:
                for rep in range(3):
                    # R-SPC-001 needs "50 m"; it flips in repeat 2. R-NSD-001 (not sold) always declines.
                    f.write(json.dumps({"id": "R-SPC-001", "repeat": rep,
                                        "final_reply": "50 m." if rep < 2 else "Not sure."}) + "\n")
                    f.write(json.dumps({"id": "R-NSD-001", "repeat": rep, "final_reply": "Sorry, we don't sell that."}) + "\n")
            out = os.path.join(t, "nf")
            self.assertEqual(noise_floor.main([d, "--out", out]), 0)
            with open(os.path.join(out, "noise.json")) as f:
                r = json.load(f)["o3s1sp_x_rag_b0"]
            self.assertEqual(r["cases"], 2)
            self.assertAlmostEqual(r["flip_rate"], 0.5)
            self.assertAlmostEqual(r["discordance"], (0 + 0.5 + 0.5) / 3)
            self.assertAlmostEqual(r["noise_bound_pts_full_dev"], 196 * (r["discordance"] / 151) ** 0.5)

    def test_compare_dev(self):
        import json
        import tempfile
        import compare_dev
        with open(os.path.join(HERE, "rag_cases.jsonl"), encoding="utf-8") as f:
            spc = [c for c in map(json.loads, f) if c["subcategory"] == "product_spec" and c["expected"]["must_include"]][:30]
        with tempfile.TemporaryDirectory() as t:
            def run(name, good):
                d = os.path.join(t, name)
                os.makedirs(d)
                with open(os.path.join(d, "run_meta.json"), "w") as f:
                    json.dump({"model": "M", "eval_file": "eval/rag_cases.jsonl"}, f)
                with open(os.path.join(d, "cases.jsonl"), "w", encoding="utf-8") as f:
                    for i, c in enumerate(spc):
                        ans = " ".join(g[0] for g in c["expected"]["must_include"]) if i < good else "No idea."
                        f.write(json.dumps({"id": c["id"], "repeat": 0, "final_reply": ans, "turns": [
                            {"prompt_n": 100, "n_tool_calls": 0}], "metrics": {"first_visible_ms": 1000}}) + "\n")
                return d
            base, new = run("b", 10), run("n", 30)
            out = os.path.join(t, "cmp")
            self.assertEqual(compare_dev.main(["--pair", base, new, "--out", out]), 0)
            with open(os.path.join(out, "compare.json")) as f:
                rows = json.load(f)["rows"]
            r = next(x for x in rows if x["subset"] == "all checked")
            self.assertEqual((r["n"], r["gained"], r["lost"]), (30, 20, 0))
            self.assertEqual(r["verdict"], "better")
            with open(os.path.join(out, "report.md"), encoding="utf-8") as f:
                self.assertIn("Printed tool calls and staff discipline", f.read())

    def test_calibrate_store_tau(self):
        import calibrate_store_tau as C
        with tempfile.TemporaryDirectory() as t:
            cases, recs = [], []
            for i in range(40):                       # 40 must-answer scores 0.20..0.59, 4 must-refuse, 1 named
                cases.append({"id": f"A{i}", "split": "dev", "messages": [{"role": "user", "content": f"Policy question {i}?"}],
                              "expected": {"behaviour": "answer"}, "subcategory": "faq"})
                recs.append({"id": f"A{i}", "repeat": 0, "retrieval": {"route": "store", "top1": 0.2 + i / 100,
                                                                         "hinglish": False, "router": {}}})
            for i in range(4):
                cases.append({"id": f"R{i}", "split": "dev", "messages": [{"role": "user", "content": "Tell me a joke."}],
                              "expected": {"behaviour": "decline"}, "subcategory": "off_topic"})
                recs.append({"id": f"R{i}", "repeat": 0, "retrieval": {"route": "unclear", "top1": 0.05 * i,
                                                                         "hinglish": False, "router": {}}})
            cases.append({"id": "N0", "split": "dev", "messages": [{"role": "user", "content": "Heritage Tribute glass?"}],
                          "expected": {"behaviour": "answer"}, "subcategory": "spec"})
            recs.append({"id": "N0", "repeat": 0, "retrieval": {"route": "store", "top1": 0.0, "hinglish": False,
                                                                  "router": {"named": True}}})
            ev, run = os.path.join(t, "cases.jsonl"), os.path.join(t, "run")
            os.makedirs(run)
            for pth, rows in ((ev, cases), (os.path.join(run, "cases.jsonl"), recs)):
                with open(pth, "w", encoding="utf-8") as f:
                    f.write("\n".join(json.dumps(r) for r in rows) + "\n")
            old = os.path.join(t, "old.json")
            with open(old, "w", encoding="utf-8") as f:
                json.dump({"threshold": 0.3, "hinglish_bypass": True, "messages": {"en": "x", "hinglish": "y"}}, f)
            self.assertEqual(C.main([run, "--eval", ev, "--old", old, "--out", os.path.join(t, "out")]), 0)
            with open(os.path.join(t, "out", "fallback.json"), encoding="utf-8") as f:
                cfg = json.load(f)
            self.assertAlmostEqual(cfg["hard_threshold"], 0.22)
            self.assertEqual(cfg["threshold"], 0.3)    # refuses 2 of 40 must-answer (5%); the named one is exempt
            self.assertEqual(cfg["n_must_answer"], 40)

    def test_calibrate_step9(self):
        sys.path.insert(0, os.path.join(ROOT, "retrieval"))
        import calibrate_step9 as C9
        with tempfile.TemporaryDirectory() as t:
            items, ranks, rag, recs = [], [], [], []
            for i in range(40):
                q = f"What is the policy number {i}?"
                items.append({"id": f"A{i}", "query": q, "split": "dev", "answer_type": "fact", "language": "en"})
                ranks.append({"id": f"A{i}", "top": [["faq:x", round(0.2 + i / 100, 2)]]})
                rag.append({"id": f"A{i}", "split": "dev", "messages": [{"role": "user", "content": q}],
                            "expected": {"behaviour": "answer"}, "subcategory": "faq"})
                recs.append({"id": f"A{i}", "repeat": 0, "retrieval": {"route": "store", "top1": 9.9, "router": {}}})
            for i, sc in enumerate((0.195, 0.199, 0.5)):   # two Hinglish questions score lowest of all
                q = f"warranty kitni hai kya mera {i}"
                items.append({"id": f"H{i}", "query": q, "split": "dev", "answer_type": "fact", "language": "hinglish"})
                ranks.append({"id": f"H{i}", "top": [["faq:x", sc]]})
            def dump(path, rows):
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(json.dumps(r) for r in rows) + "\n")
            os.makedirs(os.path.join(t, "run"))
            dump(os.path.join(t, "ev.jsonl"), items); dump(os.path.join(t, "ranks.jsonl"), ranks)
            dump(os.path.join(t, "rag.jsonl"), rag); dump(os.path.join(t, "run", "cases.jsonl"), recs)
            with open(os.path.join(t, "choice.json"), "w") as f:
                json.dump({"config": "x-d10", "ranks": os.path.join(t, "ranks.jsonl")}, f)
            with open(os.path.join(t, "old.json"), "w") as f:
                json.dump({"threshold": 0.3, "hard_threshold": 0.1, "messages": {"en": "x", "hinglish": "y"}}, f)
            self.assertEqual(C9.main(["--choice", os.path.join(t, "choice.json"), "--eval", os.path.join(t, "ev.jsonl"),
                                      "--rag", os.path.join(t, "rag.jsonl"), "--run", os.path.join(t, "run"),
                                      "--old", os.path.join(t, "old.json"), "--out", t]), 0)
            with open(os.path.join(t, "fallback.json")) as f:
                cfg = json.load(f)
            self.assertTrue(cfg["hinglish_bypass"])          # without it, 2 Hinglish refused (> 1): kept
            self.assertAlmostEqual(cfg["threshold"], 0.22)
            self.assertAlmostEqual(cfg["hard_threshold"], 0.22)

    def test_answer_check(self):
        sys.path.insert(0, ROOT)
        from harness import verify as V
        card = ("Veyra Meridian Sable (design V1027). Movement: quartz. Glass: Sapphire. 33 mm wide. Made in: Switzerland. "
                "Warranty: 24 months on the movement. - 1027SM02: blue dial, silver metal bracelet. MRP Rs. 38,895.")
        ok = V.check("The Meridian Sable (1027SM02) is Rs 38,895, 33 mm, quartz, sapphire glass, Swiss made? No: "
                     "made in Switzerland, with a 2 years warranty.", "Tell me about it", [card], "", "shown")
        self.assertEqual(ok["unsupported"], ["swiss"])           # 'Swiss' is not in the card
        bad = V.check("It has a ceramic case and 100 m water resistance.", "q", [card], "", "shown")
        self.assertEqual(bad["unsupported"], ["100 m", "ceramic"])
        self.assertTrue(V.check("Here are 3 options:\n1. Meridian Sable", "q", [card], "", "shown")["ok"])
        self.assertTrue(V.check("Open until 10 PM.", "q", ["10:00 to 22:00 every day."], "", "shown")["ok"])
        cited = V.check("It has sapphire glass. [2]", "q", ["Glass: Mineral.", card], "", "cited")
        self.assertEqual((cited["ok"], cited["reply"], cited["cited"]), (True, "It has sapphire glass.", [2]))
        self.assertFalse(V.check("It has sapphire glass. [1]", "q", ["Glass: Mineral.", card], "", "cited")["ok"])
        self.assertTrue(V.check("It has sapphire glass.", "q", [card], "", "cited")["uncited"])
        self.assertTrue(V.check("Sorry, I don't have that information.", "q", [], "", "cited")["ok"])
        self.assertTrue(V.check("It is in stock here (2 on display).", "q", [], '{"in_stock_here": true, "display": 2}', "shown")["ok"])

    def test_scorer_variants_13(self):
        from checks import text_has
        self.assertTrue(text_has("It has 50 meters water resistance.", ["50 m", "50m", "50 metres"]))
        self.assertFalse(text_has("150 meters", ["50 m", "50 metres"]))
        self.assertTrue(text_has("between Rs. 500 and Rs. 900", ["Rs. 500 to Rs. 900"]))
        self.assertTrue(text_has("The clasp isn't specified.", ["not listed", "not mentioned", "don't have"]))
        self.assertFalse(text_has("It has a round case.", ["not listed", "not mentioned", "don't have"]))

    def test_compare_spec(self):
        import compare_spec as CS
        with tempfile.TemporaryDirectory() as t:
            def run(name, speed_ms, reply_b="b"):
                d = os.path.join(t, name)
                os.makedirs(d)
                with open(os.path.join(d, "run_meta.json"), "w") as f:
                    json.dump({"machine": {"label": "local"}}, f)
                with open(os.path.join(d, "cases.jsonl"), "w") as f:
                    for i in range(6):
                        f.write(json.dumps({"id": f"C{i}", "final_reply": "a" if i else reply_b,
                                            "turns": [{"predicted_n": 50, "predicted_ms": speed_ms, "draft_n": 30,
                                                       "draft_n_accepted": 15}],
                                            "metrics": {"first_visible_ms": 1000, "end_to_end_ms": 1000 + speed_ms}}) + "\n")
            for s_ in ("rag", "v12"):
                run(f"p_{s_}_none", 2000)
                run(f"p_{s_}_fast", 1000)
                run(f"p_{s_}_wrong", 1000, reply_b="different")
                run(f"p_{s_}_none2", 2000)
                run(f"p_{s_}_mtpfile", 2000, reply_b="other file")
                run(f"p_{s_}_mtp2", 500, reply_b="other file")
            CS.main(["--prefix", "p", "--results", t, "--out", os.path.join(t, "out")])
            with open(os.path.join(t, "out", "summary.json")) as f:
                got = json.load(f)["p"]
        self.assertEqual(got["choice"], "fast")
        rows = {r["config"]: r for r in got["rows"]}
        self.assertAlmostEqual(rows["fast"]["ratio"][0], 2.0)
        self.assertFalse(rows["wrong"]["qualifies"])         # one reply changed: not identical
        self.assertEqual(rows["fast"]["acceptance"], 0.5)
        self.assertFalse(rows["mtp2"]["qualifies"])          # faster, but the MTP file changes a reply

    def test_step14_verdicts(self):
        import step14_verdicts as V
        self.assertEqual([round(x, 3) for x in V.holm([0.01, 0.04, 0.03])], [0.03, 0.06, 0.06])
        with tempfile.TemporaryDirectory() as t:
            rows = []
            for m in ("2b", "4b"):
                for s_, sub, d in (("rag", "all checked", 1.0), ("v12", "tool cases", 0.0), ("fup", "all checked", 30.0)):
                    rows.append({"base": f"o3t_b0_{m}_{s_}", "new": f"o3t_final_{m}_{s_}", "subset": sub, "n": 60,
                                 "base_rate": 0.6, "new_rate": 0.6 + d / 100, "diff_pts": d,
                                 "ci": [d - 5, d + 5] if d < 20 else [15.0, 45.0], "mcnemar_p": 0.0001 if d > 20 else 0.5,
                                 "noise_bound_pts": 3.0, "verdict": "tie"})
            os.makedirs(os.path.join(t, "_compare_step14"))
            with open(os.path.join(t, "_compare_step14", "compare.json"), "w") as f:
                json.dump({"rows": rows}, f)
            os.makedirs(os.path.join(t, "_dialogues_step14"))
            summ = {f"o3t_final_{m}_dlg": {"recommended": 1.0, "slots2_share": 1.0, "questions_max": 2, "fit_mean": 0.95}
                    for m in ("2b", "4b")}
            with open(os.path.join(t, "_dialogues_step14", "summary.json"), "w") as f:
                json.dump(summ, f)
            os.makedirs(os.path.join(t, "_compare_step14_speed"))
            with open(os.path.join(t, "_compare_step14_speed", "compare.json"), "w") as f:
                json.dump({"waits": [{"base": f"o3tsp_a_2b_{s_}_b0", "new": f"o3tsp_a_2b_{s_}_final", "n": 40,
                                      "first_word_s": [-1, -2, -0.5], "total_s": [-2, -3, -1]} for s_ in ("rag", "v12")]}, f)
            V.main(["--results", t])
            with open(os.path.join(t, "_step14", "verdicts.json")) as f:
                got = json.load(f)
        self.assertTrue(got["A"]["confirmed"] and got["B"]["confirmed"])
        self.assertEqual(got["A"]["checks"]["follow-ups"], "better")

    def test_followup_polarity(self):
        import score_rag as R
        self.assertTrue(R.polarity_correct("Yes, it is in stock here (1 on display).", "in_stock"))
        self.assertFalse(R.polarity_correct("Sorry, it is not in stock here.", "in_stock"))
        self.assertTrue(R.polarity_correct("It is not in stock here, but City Centre Mall has 6.", "out_of_stock"))
        self.assertTrue(R.polarity_correct("Yes, it comes in a black dial too.", "yes", "black"))
        self.assertFalse(R.polarity_correct("It doesn't come in black; it comes in blue.", "yes", "black"))
        self.assertTrue(R.polarity_correct("No, it doesn't come in green.", "no", "green"))


if __name__ == "__main__":
    unittest.main()
