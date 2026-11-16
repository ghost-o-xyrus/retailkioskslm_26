"""
End-to-end tests of the harness against the fake server (no model needed).

    python -m unittest harness.test_harness -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from harness import run_eval, run_plan, summarize, time_split  # noqa: E402

PORT = 8099


def write_cases(path, cases):
    with open(path, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")


def case(cid, text, mode="tools", context=None):
    return {"id": cid, "category": "tool_selection", "subcategory": "x", "mode": mode, "language": "en",
            "difficulty": "easy", "split": "test", "set": "core", "messages": [{"role": "user", "content": text}],
            "context": context, "expected": {"behaviour": "tool_use"}, "rubric": [], "source": "", "notes": ""}


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = subprocess.Popen([sys.executable, os.path.join(HERE, "fake_server.py"), "--port", str(PORT)])
        assert run_eval.wait_for_server(f"http://127.0.0.1:{PORT}", 20)
        cls.tmp = tempfile.mkdtemp()
        with open(os.path.join(ROOT, "data", "clean", "skus.csv"), encoding="utf-8") as f:
            next(f)
            cls.sku = next(f).split(",")[0]
        cls.cases_file = os.path.join(cls.tmp, "cases.jsonl")
        write_cases(cls.cases_file, [
            case("T1", f"Tell me about {cls.sku}"),
            case("T2", f"Is {cls.sku} in stock?"),
            case("T3", f"Can I try {cls.sku}?"),
            case("T4", "formal watch under 15000"),
            case("T5", "hi there"),
            case("T6", "please astext"),
            case("T7", "please badjson"),
            case("G1", "Is it water resistant? think", mode="grounded", context="water_resistance: 50"),
        ])

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=10)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_eval(self, name, extra=()):
        argv = ["--name", name, "--url", f"http://127.0.0.1:{PORT}", "--eval", self.cases_file,
                "--results-dir", self.tmp, "--model", "fake", "--quant", "Q4", "--backend", "test"] + list(extra)
        return run_eval.main(argv)

    def read(self, name):
        with open(os.path.join(self.tmp, name, "cases.jsonl"), encoding="utf-8") as f:
            return {(r["id"], r["repeat"]): r for r in map(json.loads, f)}

    def test_full_run(self):
        self.assertEqual(self.run_eval("full"), 0)
        rs = self.read("full")
        self.assertEqual(len(rs), 8)
        t1 = rs[("T1", 0)]
        self.assertEqual(t1["tool_calls"][0]["name"], "get_product_details")
        self.assertEqual(t1["tool_calls"][0]["arguments"], {"product_id": self.sku})
        self.assertNotIn("error", t1["tool_calls"][0]["result"])
        self.assertTrue(t1["final_reply"].startswith("Here is what I found"))
        self.assertEqual(t1["n_rounds"], 2)
        self.assertEqual(rs[("T2", 0)]["tool_calls"][0]["name"], "check_inventory")
        self.assertEqual(rs[("T3", 0)]["tool_calls"][0]["arguments"]["reason"], "try_on")
        self.assertEqual(rs[("T4", 0)]["tool_calls"][0]["name"], "search_catalogue")
        self.assertEqual(rs[("T5", 0)]["tool_calls"], [])
        self.assertIn("tool_call_as_text", rs[("T6", 0)]["flags"])
        bad = rs[("T7", 0)]["tool_calls"][0]
        self.assertFalse(bad["arguments_valid_json"])
        self.assertEqual(bad["result"]["error"], "invalid_arguments")
        g = rs[("G1", 0)]
        self.assertIn("think_tags_in_content", g["flags"])
        self.assertNotIn("<think>", g["final_reply"])
        self.assertEqual(g["tool_calls"], [])
        m = t1["metrics"]
        for k in ("end_to_end_ms", "ttft_ms", "tokens_per_s", "prompt_tokens_total", "prompt_tokens_cached"):
            self.assertIsNotNone(m[k], k)
        with open(os.path.join(self.tmp, "full", "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["server_props"]["model_path"], "fake.gguf")
        self.assertIn("finished", meta)

    def test_resume_and_repeats(self):
        self.assertEqual(self.run_eval("rep", ["--repeats", "2", "--limit", "3"]), 0)
        self.assertEqual(len(self.read("rep")), 6)
        self.assertEqual(self.run_eval("rep", ["--repeats", "2", "--limit", "3"]), 0)  # nothing left to do
        with open(os.path.join(self.tmp, "rep", "cases.jsonl"), encoding="utf-8") as f:
            self.assertEqual(sum(1 for _ in f), 6)

    def test_filters(self):
        cases = run_eval.load_cases(self.cases_file, "all", "all", None, None, None)
        self.assertEqual(len(cases), 8)
        ids = os.path.join(self.tmp, "ids.json")
        with open(ids, "w") as f:
            json.dump({"ids": ["T1", "G1"]}, f)
        self.assertEqual([c["id"] for c in run_eval.load_cases(self.cases_file, "all", "all", ids, None, None)], ["T1", "G1"])

    def test_summary(self):
        self.run_eval("sum")
        s = summarize.summarize(os.path.join(self.tmp, "sum"))
        self.assertEqual(s["cases"], 8)
        self.assertEqual(s["errors"], 0)
        self.assertEqual(s["invalid_json_args"], 1)
        self.assertIn("tool_call_as_text", s["flags"])
        self.assertIsNotNone(s["prompt_cache_reuse_pct"])

    def test_real_eval_file_loads_and_builds_prompts(self):
        with open(os.path.join(ROOT, "eval", "system_prompts.json"), encoding="utf-8") as f:
            prompts = json.load(f)
        for f in ("eval_set.jsonl", "eval_set_v1.1.jsonl"):
            for c in run_eval.load_cases(os.path.join(ROOT, "eval", f)):
                msgs = run_eval.build_messages(c, prompts)
                self.assertEqual(msgs[0]["role"], "system")
                if c.get("context"):
                    self.assertIn(c["context"][:30], msgs[0]["content"])

    def test_run_plan_starts_and_stops_server(self):
        plan = {"name": "t", "base_dir": "..", "defaults": {"port": 8098, "eval": os.path.relpath(self.cases_file, ROOT),
                                                             "limit": 3},
                "runs": [{"name": "plan_run", "model": "fake",
                          "server_cmd": [sys.executable, os.path.join(HERE, "fake_server.py")]}]}
        p = os.path.join(self.tmp, "plan.json")
        with open(p, "w") as f:
            json.dump(plan, f)
        cmd = [sys.executable, os.path.join(HERE, "run_plan.py"), p, "--results-dir", self.tmp]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=ROOT)
        self.assertIn("plan_run", out.stdout)
        self.assertEqual(len(self.read("plan_run")), 3)
        out2 = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=ROOT)
        self.assertIn("already complete", out2.stdout)
        time.sleep(1)

    # ---- Objective 2: retrieval conditions (stand-in encoders, so no downloads) ----
    def rag_setup(self):
        fb = os.path.join(self.tmp, "fallback.json")
        with open(fb, "w", encoding="utf-8") as f:
            json.dump({"threshold": 0.3, "hinglish_bypass": True,
                       "messages": {"en": "Sorry, I don't have that.", "hinglish": "Maaf kijiye."}}, f)
        path = os.path.join(self.tmp, "rag.jsonl")
        rag = [case("K1", "Do you offer gift wrapping?"), case("K2", "What's the weather like today?"),
               case("K3", "kbq do you deliver at home?"), case("K4", "Gift wrapping milta hai kya?"),
               case("G2", "Is it water resistant?", mode="grounded", context="water_resistance: 50")]
        rag[0]["expected"]["oracle_ids"] = ["faq:do-you-offer-gift-wrapping"]
        write_cases(path, rag)
        return path, fb

    def test_retrieval_conditions(self):
        path, fb = self.rag_setup()
        base = ["--eval", path, "--fallback-config", fb, "--fake-retriever"]
        argv = lambda name, *x: ["--name", name, "--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp] + base + list(x)
        self.assertEqual(run_eval.main(argv("r_always", "--retrieval", "always", "--k-chunks", "3")), 0)
        rs = self.read("r_always")
        k1 = rs[("K1", 0)]["retrieval"]
        self.assertEqual(k1["condition"], "always")
        self.assertEqual(k1["chunk_ids"][0], "faq:do-you-offer-gift-wrapping")
        self.assertLessEqual(len(k1["chunk_ids"]), 3)
        self.assertFalse(k1["fallback_would_refuse"])
        self.assertTrue(rs[("K2", 0)]["retrieval"]["fallback_would_refuse"])     # off-topic scores low
        self.assertTrue(rs[("K2", 0)]["final_reply"])                            # shadow: the model still ran
        self.assertTrue(rs[("K4", 0)]["retrieval"]["hinglish"])
        self.assertIsNone(rs[("G2", 0)]["retrieval"])                            # grounded cases ignore retrieval
        self.assertIsNotNone(rs[("K1", 0)]["metrics"]["retrieval_ms"])
        with open(os.path.join(self.tmp, "r_always", "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["retrieval"]["knowledge_base"]["k"], 3)

        self.assertEqual(run_eval.main(argv("r_live", "--retrieval", "always", "--fallback", "live")), 0)
        k2 = self.read("r_live")[("K2", 0)]
        self.assertEqual(k2["final_reply"], "Sorry, I don't have that.")
        self.assertEqual(k2["turns"], [])
        self.assertIn("fallback_refused", k2["flags"])

        self.assertEqual(run_eval.main(argv("r_gate", "--retrieval", "always", "--fallback", "gate")), 0)
        g = self.read("r_gate")[("K2", 0)]
        self.assertTrue(g["retrieval"]["fallback_applied"])
        self.assertEqual(g["retrieval"]["context_tokens"], 0)
        self.assertTrue(g["turns"])                                              # the model still ran

        # Step 7d options: compact cards + chunk gate + warm-up
        self.assertEqual(run_eval.main(argv("r_compact", "--retrieval", "always", "--fallback", "gate",
                                            "--context-view", "compact", "--chunk-gate", "--warmup")), 0)
        c = self.read("r_compact")
        self.assertEqual(c[("K1", 0)]["retrieval"]["view"], "compact")
        self.assertTrue(c[("K1", 0)]["retrieval"]["chunk_gate"])
        self.assertTrue(all(sc >= 0.3 for sc in c[("K1", 0)]["retrieval"]["scores"]))   # gate: only strong chunks
        self.assertEqual(c[("K2", 0)]["retrieval"]["context_tokens"], 0)                  # nothing strong: nothing shown
        self.assertIsNotNone(c[("K1", 0)]["metrics"]["first_visible_ms"])

        # Step 7e options: omitted gate, alternative rule, models shared across runs
        self.assertEqual(run_eval.main(argv("r_omit", "--retrieval", "always", "--fallback", "gate", "--chunk-gate",
                                            "--gate-style", "omit", "--rag-rule", "rag_always_rule_c")), 0)
        o2 = self.read("r_omit")[("K2", 0)]
        self.assertEqual(o2["retrieval"]["gate_style"], "omit")
        self.assertEqual(o2["retrieval"]["context_tokens"], 0)
        with open(os.path.join(self.tmp, "r_omit", "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertTrue(meta["retrieval"]["knowledge_base"]["reused_from_earlier_run"])
        self.assertEqual(meta["retrieval"]["rag_rule"], "rag_always_rule_c")
        self.assertEqual(run_eval.main(argv("r_badrule", "--retrieval", "always", "--rag-rule", "nope")), 2)

        # Step 7f: a product whose card was shown gets a short pointer instead of the full record
        path2 = os.path.join(self.tmp, "dedupe.jsonl")
        write_cases(path2, [case("D1", f"Tell me about {self.sku}")])
        a2 = ["--name", "r_dedupe", "--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--eval", path2,
              "--fallback-config", fb, "--fake-retriever", "--retrieval", "always", "--fallback", "gate",
              "--gate-style", "omit", "--dedupe-shown"]
        self.assertEqual(run_eval.main(a2), 0)
        d = self.read("r_dedupe")[("D1", 0)]
        self.assertIn(f"product:{run_eval.shown_style(self.sku)}", d["retrieval"]["chunk_ids"])
        self.assertTrue(d["tool_calls"][0].get("deduped"))
        self.assertIn("already in the store information", d["tool_calls"][0]["result"]["note"])

        self.assertEqual(run_eval.main(argv("r_oracle", "--retrieval", "oracle")), 0)
        o = self.read("r_oracle")
        self.assertEqual(o[("K1", 0)]["retrieval"]["chunk_ids"], ["faq:do-you-offer-gift-wrapping"])
        self.assertIsNone(o[("K2", 0)]["retrieval"]["chunk_ids"])               # no oracle ids: nothing added

        self.assertEqual(run_eval.main(argv("r_tool", "--retrieval", "tool")), 0)
        t = self.read("r_tool")[("K3", 0)]
        self.assertEqual(t["tool_calls"][0]["name"], "search_knowledge")
        self.assertTrue(t["tool_calls"][0]["known_tool"])
        self.assertTrue(t["tool_calls"][0]["result"]["results"])
        self.assertEqual(t["retrieval"]["calls"][0]["query"], "do you deliver at home?")

    def test_omitted_gate_leaves_the_message_unchanged(self):
        with open(os.path.join(ROOT, "eval", "system_prompts.json"), encoding="utf-8") as f:
            prompts = json.load(f)
        for key in ("rag_always_rule_b", "rag_always_rule_c"):
            self.assertTrue(prompts[key].startswith("- Customer messages may come with store information"))

    def test_retrieved_text_goes_in_the_customer_message(self):
        with open(os.path.join(ROOT, "eval", "system_prompts.json"), encoding="utf-8") as f:
            prompts = json.load(f)
        c = case("X", "Do you deliver?")
        msgs = run_eval.build_messages(c, prompts, "always")
        self.assertTrue(msgs[0]["content"].startswith(prompts["tools"]))
        self.assertIn(prompts["rag_always_rule"], msgs[0]["content"])
        run_eval.add_context(msgs, run_eval.last_user_index(msgs), "[1] Delivery is free.", prompts)
        self.assertIn("[1] Delivery is free.", msgs[-1]["content"])
        self.assertTrue(msgs[-1]["content"].endswith("Customer: Do you deliver?"))
        self.assertEqual(run_eval.build_messages(c, prompts)[0]["content"], prompts["tools"])  # Objective 1 unchanged

    # ---- Objective 3, Step 1: token counts, config label, time split ----
    def test_token_counts_and_time_split(self):
        self.assertEqual(self.run_eval("o3s1", ["--config-label", "O3-B0", "--repeats", "2", "--limit", "5"]), 0)
        rs = self.read("o3s1")
        t1 = rs[("T1", 0)]
        self.assertEqual(t1["config"], "O3-B0")
        self.assertEqual(t1["route"], "none")
        n = t1["tool_calls"][0]["result_tokens"]                      # fake /tokenize: 4 characters a token
        self.assertEqual(n, len(json.dumps(t1["tool_calls"][0]["result"], ensure_ascii=False)) // 4)
        self.assertEqual(t1["tokens"]["tool_results_total"], n)
        self.assertEqual(rs[("T5", 0)]["tokens"]["tool_results"], [])   # greeting: no tool
        self.assertEqual(self.run_eval("o3s1_nocount", ["--no-count-tokens", "--limit", "1"]), 0)
        self.assertNotIn("tokens", self.read("o3s1_nocount")[("T1", 0)])

        out = os.path.join(self.tmp, "_ts")
        self.assertEqual(time_split.main([os.path.join(self.tmp, "o3s1"), "--out", out]), 0)
        with open(os.path.join(out, "summary.json"), encoding="utf-8") as f:
            s = json.load(f)["o3s1"]
        self.assertEqual(s["n_records"], 10)
        self.assertEqual(s["n_cases"], 5)
        self.assertGreater(s["rounds_mean"], 1)                        # T1-T4 call a tool, then answer
        self.assertAlmostEqual(sum(s["time_share"].values()), 1.0, places=6)
        self.assertAlmostEqual(s["v_read_tok_s"], 500.0, places=3)      # fake server: 2 ms a prompt token
        self.assertAlmostEqual(s["v_write_tok_s"], 100.0, places=3)     # and 10 ms a generated token
        self.assertEqual(s["repeats_check"]["cases"], 5)
        self.assertGreaterEqual(s["repeats_check"]["identical_replies"], 0.8)   # call_staff quotes a new ticket id
        self.assertIn("formula_median_abs_err", s)   # fake timings are not wall time, so no error is computed here
        self.assertGreater(s["tool_output_tokens_mean"], 0)
        with open(os.path.join(out, "report.md"), encoding="utf-8") as f:
            rep = f.read()
        for heading in ("## Rounds and tokens per case", "## Time split", "## Speeds and the first-word formula",
                        "## Repeat stability", "## By category"):
            self.assertIn(heading, rep)

    def test_time_split_counts_waste_and_fallback(self):
        r = {"id": "X", "repeat": 0, "flags": ["max_rounds_reached"], "metrics": {"end_to_end_ms": 1000, "retrieval_ms": 100,
             "first_visible_ms": 900},
             "turns": [{"prompt_n": 50, "prompt_ms": 100, "predicted_n": 10, "predicted_ms": 100, "n_tool_calls": 2},
                       {"prompt_n": 80, "prompt_ms": 160, "predicted_n": 10, "predicted_ms": 100, "n_tool_calls": 1}],
             "tool_calls": [{"name": "call_staff", "arguments": {"reason": "a"}},
                            {"name": "call_staff", "arguments": {"reason": "a"}},
                            {"name": "get_product_details", "arguments": {"product_id": "1"}, "deduped": True,
                             "result_error": "not_found"}]}
        w = time_split.waste(r)
        self.assertEqual(w, {"dup_calls": 1, "staff_calls_over_1": 1, "deduped_fetches": 1, "tool_errors": 1,
                             "max_rounds": 1, "empty_replies": 1, "guard_notes": 0, "n_calls": 3})
        d = time_split.split_case(r)
        self.assertEqual(d["write_answer"], 0)                          # never answered: the round limit hit
        self.assertEqual(d["write_calls"], 200)
        self.assertEqual(d["read_tool_outputs"], 160)
        self.assertEqual(d["tok_read"], 130)
        self.assertAlmostEqual(d["other"], 1000 - 100 - 100 - 160 - 200)
        hard = time_split.split_case({"turns": [], "metrics": {"end_to_end_ms": 120, "retrieval_ms": 100}})
        self.assertEqual(hard["rounds"], 0)
        self.assertEqual(hard["other"], 20)

    # ---- Objective 3, Step 3: loop guard and compact tool view ----
    def test_loop_guard_and_compact_view(self):
        path = os.path.join(self.tmp, "guard.jsonl")
        write_cases(path, [case("L1", "loopme please"), case("L2", "staffloop please"), case("L3", "emptyreply"),
                           case("C1", f"Tell me about {self.sku}"), case("C2", "formal watch under 15000")])
        base = ["--url", f"http://127.0.0.1:{PORT}", "--eval", path, "--results-dir", self.tmp]
        self.assertEqual(run_eval.main(["--name", "g_off"] + base), 0)
        off = self.read("g_off")
        self.assertIn("max_rounds_reached", off[("L1", 0)]["flags"])
        self.assertFalse(off[("L1", 0)]["final_reply"])
        self.assertEqual(run_eval.main(["--name", "g_on", "--loop-guard", "--tool-view", "compact"] + base), 0)
        on = self.read("g_on")
        l1 = on[("L1", 0)]
        self.assertNotIn("max_rounds_reached", l1["flags"])
        self.assertEqual(l1["final_reply"], "Final answer without tools.")          # last request: tool_choice none
        self.assertEqual([c.get("guard") for c in l1["tool_calls"]], [None, "repeat", "repeat"])
        self.assertEqual(len(l1["turns"]), 4)
        l2 = on[("L2", 0)]
        self.assertEqual([c.get("guard") for c in l2["tool_calls"]], [None, "staff_repeat", "staff_repeat"])
        self.assertEqual(sum(1 for c in l2["tool_calls"] if not c.get("guard")), 1)  # staff notified once
        l3 = on[("L3", 0)]
        self.assertEqual(l3["final_reply"], run_eval.EMPTY_FALLBACK)
        self.assertIn("empty_reply_fallback", l3["flags"])
        from tools.render import render
        c1 = on[("C1", 0)]["tool_calls"][0]
        text = render(c1["name"], c1["arguments"], c1["result"])
        self.assertTrue(text.startswith(self.sku))
        self.assertEqual(c1["result_tokens"], len(text) // 4)                     # counts what the model read
        self.assertNotIn("description", text.lower())
        c2 = on[("C2", 0)]["tool_calls"][0]
        self.assertEqual(len(c2["result"]["results"]), 3)                          # compact: 3 results by default
        self.assertIn("shown", c2["result"])
        self.assertEqual(len(off[("C2", 0)]["tool_calls"][0]["result"]["results"]), 5)
        with open(os.path.join(self.tmp, "g_on", "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual((meta["tool_view"], meta["loop_guard"]), ("compact", True))
        from tools import mock_tools
        self.assertEqual(run_eval.main(["--name", "g_reset"] + base + ["--limit", "1"]), 0)
        self.assertFalse(mock_tools.HONEST)                                        # flags reset per run

    # ---- Objective 3, Step 4: routed retrieval ----
    def test_routed_retrieval(self):
        path, fb = self.rag_setup()
        extra = os.path.join(self.tmp, "routed.jsonl")
        write_cases(extra, [case("K1", "Do you offer gift wrapping?"), case("R1", f"Is {self.sku} in stock?"),
                            case("R2", "Hello!"), case("R3", "Formal watch for my father under 15000")])
        argv = ["--name", "r_routed", "--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--eval", extra,
                "--fallback-config", fb, "--fake-retriever", "--retrieval", "routed", "--fallback", "gate",
                "--gate-style", "omit", "--loop-guard", "--tool-view", "compact"]
        self.assertEqual(run_eval.main(argv), 0)
        rs = self.read("r_routed")
        self.assertEqual(rs[("K1", 0)]["route"], "store")
        self.assertEqual(rs[("K1", 0)]["retrieval"]["condition"], "always")
        self.assertTrue(rs[("K1", 0)]["retrieval"]["chunk_ids"])
        self.assertEqual(rs[("R1", 0)]["route"], "stock")
        self.assertEqual(rs[("R1", 0)]["retrieval"]["condition"], "none")                # no cards for a stock check
        self.assertEqual(rs[("R1", 0)]["tool_calls"][0]["name"], "check_inventory")
        self.assertEqual(rs[("R2", 0)]["route"], "chat")
        self.assertEqual(rs[("R3", 0)]["route"], "shopping")
        self.assertIsNotNone(rs[("R1", 0)]["retrieval"]["router"]["ms"])
        with open(os.path.join(self.tmp, "r_routed", "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["retrieval"]["condition"], "routed")
        self.assertIn("router", meta["retrieval"]["knowledge_base"])
        out = os.path.join(self.tmp, "_ts_routed")
        self.assertEqual(time_split.main([os.path.join(self.tmp, "r_routed"), "--out", out]), 0)
        with open(os.path.join(out, "report.md"), encoding="utf-8") as f:
            self.assertIn("## By route", f.read())

    # ---- Objective 3, Step 5: harness-run tools and one-round store answers ----
    def test_harness_tools_and_store_one_round(self):
        path, fb = self.rag_setup()
        extra = os.path.join(self.tmp, "s5.jsonl")
        write_cases(extra, [case("S1", f"Is {self.sku} in stock?"), case("S2", f"Can I try {self.sku} on?"),
                            case("S3", f"{self.sku} is over my budget, anything similar but cheaper?"),
                            case("S4", "Do you offer gift wrapping?"), case("S5", "My watch stopped working, can you repair it?"),
                            case("S6", "Can I pay with crypto offerstaff?"), case("S7", "Formal watch for my father under 15000")])
        argv = ["--name", "r_s5", "--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--eval", extra,
                "--fallback-config", fb, "--fake-retriever", "--retrieval", "routed", "--fallback", "gate",
                "--gate-style", "omit", "--loop-guard", "--tool-view", "compact", "--harness-tools", "--store-one-round"]
        self.assertEqual(run_eval.main(argv), 0)
        rs = self.read("r_s5")
        s1 = rs[("S1", 0)]
        self.assertEqual([(c["name"], c.get("by")) for c in s1["tool_calls"]], [("check_inventory", "harness")])
        self.assertEqual(s1["tool_calls"][0]["arguments"], {"product_id": self.sku})
        self.assertEqual(len(s1["turns"]), 1)                                       # one model request
        self.assertEqual(s1["final_reply"], "Final answer without tools.")
        self.assertEqual(rs[("S2", 0)]["tool_calls"][0]["arguments"]["reason"], "try_on")
        self.assertEqual(rs[("S3", 0)]["tool_calls"][0]["arguments"]["reason"], "cheaper")
        s4 = rs[("S4", 0)]
        self.assertEqual((s4["route"], len(s4["turns"]), s4["tool_calls"]), ("store", 1, []))
        s5 = rs[("S5", 0)]
        self.assertEqual(s5["tool_calls"][0]["arguments"]["reason"], "service")
        s6 = rs[("S6", 0)]
        self.assertIn("harness_staff_after_answer", s6["flags"])
        self.assertEqual(s6["tool_calls"][-1]["arguments"]["reason"], "question_unanswered")
        self.assertTrue(s6["final_reply"].endswith(run_eval.STAFF_LINE))
        s7 = rs[("S7", 0)]
        self.assertEqual(s7["route"], "shopping")
        self.assertNotEqual(s7["tool_calls"][0].get("by"), "harness")              # shopping stays with the model

    # ---- Objective 3, Step 7: printed tool calls on forced answers, staff guard, prompt v1.2 ----
    def test_forced_answer_recover_and_staff_guard(self):
        path, fb = self.rag_setup()
        extra = os.path.join(self.tmp, "s7.jsonl")
        write_cases(extra, [case("P1", f"Is {self.sku} in stock? printcall"), case("P2", f"Is {self.sku} in stock? printprose"),
                            case("P3", f"Is {self.sku} in stock? printstaff"), case("P4", "Can I pay with crypto offerstaff?")])
        base = ["--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--eval", extra, "--fallback-config", fb,
                "--fake-retriever", "--retrieval", "routed", "--fallback", "gate", "--gate-style", "omit", "--loop-guard",
                "--tool-view", "compact", "--harness-tools"]
        self.assertEqual(run_eval.main(["--name", "r_s7old"] + base), 0)
        old = self.read("r_s7old")
        self.assertIn("tool_text_replaced", old[("P1", 0)]["flags"])                # Step 6c behaviour kept as default
        self.assertIn("tool_text_replaced", old[("P2", 0)]["flags"])
        self.assertEqual(old[("P4", 0)]["tool_calls"], [])
        argv = ["--name", "r_s7"] + base + ["--forced-answer", "recover", "--staff-guard", "--tools-prompt", "tools_v12"]
        self.assertEqual(run_eval.main(argv), 0)
        rs = self.read("r_s7")
        p1 = rs[("P1", 0)]
        self.assertIn("tool_text_recovered", p1["flags"])
        self.assertEqual([c["name"] for c in p1["tool_calls"]], ["check_inventory", "get_product_details"])
        self.assertEqual(p1["final_reply"], "Final answer without tools.")
        self.assertTrue(p1["turns"][-1]["recovery"])
        p2 = rs[("P2", 0)]
        self.assertIn("tool_text_stripped", p2["flags"])
        self.assertEqual(p2["final_reply"], "Here is a good watch for you, it is in stock here today.")
        p3 = rs[("P3", 0)]
        self.assertEqual((p3["final_reply"], p3["tool_calls"][-1]["name"]), (run_eval.STAFF_LINE, "call_staff"))
        p4 = rs[("P4", 0)]
        self.assertIn("harness_staff_after_answer", p4["flags"])
        self.assertEqual(p4["tool_calls"][-1]["arguments"]["reason"], "question_unanswered")
        with open(os.path.join(self.tmp, "r_s7", "run_meta.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["tools_prompt"], "tools_v12")

    # ---- Objective 3, Step 8: entity check, store-only hard fallback, staff check ----
    def test_entity_fallback_and_staff_check(self):
        path, fb = self.rag_setup()
        extra = os.path.join(self.tmp, "s8.jsonl")
        write_cases(extra, [case("E1", "Do you sell Fossil watches?"), case("E2", "Show me the Veyra Everyday Zenith."),
                            case("E3", "Do you sell sunglasses?"), case("F1", "What's the weather like today?"),
                            case("C1", "Do you offer gift wrapping staffask?"), case("N1", "Can I pay by phone?")])
        argv = ["--name", "r_s8", "--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--eval", extra,
                "--fallback-config", fb, "--fake-retriever", "--retrieval", "routed", "--fallback", "store-live",
                "--gate-style", "omit", "--loop-guard", "--tool-view", "compact", "--harness-tools",
                "--forced-answer", "recover", "--entity-check", "--staff-check"]
        self.assertEqual(run_eval.main(argv), 0)
        rs = self.read("r_s8")
        e1 = rs[("E1", 0)]
        self.assertEqual((e1["flags"], e1["n_rounds"]), (["entity_not_carried"], 0))
        self.assertIn("don't sell Fossil", e1["final_reply"])
        self.assertEqual(e1["tool_calls"][0]["by"], "harness")
        e2 = rs[("E2", 0)]
        self.assertEqual(e2["flags"], ["entity_missing_design"])
        self.assertIn("don't have a watch called Everyday Zenith", e2["final_reply"])
        self.assertIn("so we don't have sunglasses", rs[("E3", 0)]["final_reply"])
        f1 = rs[("F1", 0)]
        self.assertEqual((f1["flags"], f1["n_rounds"]), (["fallback_refused"], 0))
        self.assertEqual(f1["final_reply"], "Sorry, I don't have that.")
        self.assertNotIn("entity_not_carried", rs[("N1", 0)]["flags"])           # "phone" without a shopping word
        c1 = rs[("C1", 0)]
        if c1["retrieval"].get("fallback_applied"):
            self.skipTest("fake retriever refused the gift-wrapping question")
        self.assertEqual(c1["tool_calls"][0].get("guard"), "staff_check")
        self.assertIn("Not sent yet", c1["tool_calls"][0]["result"]["note"])
        self.assertEqual([c["name"] for c in c1["tool_calls"]], ["call_staff"])  # answered after the note
        # threshold calibration reads the logged scores
        sys.path.insert(0, os.path.join(ROOT, "eval"))
        import calibrate_store_tau
        self.assertEqual(calibrate_store_tau.main([os.path.join(self.tmp, "r_s8"), "--eval", extra, "--old", fb,
                                                   "--out", os.path.join(self.tmp, "_tau")]), 0)
        with open(os.path.join(self.tmp, "_tau", "fallback.json"), encoding="utf-8") as f:
            self.assertIn("threshold", json.load(f))

    # ---- Objective 3, Step 10: answer check (live and replayed) ----
    def test_verify_answers_live_and_replay(self):
        path, fb = self.rag_setup()
        extra = os.path.join(self.tmp, "s10.jsonl")
        write_cases(extra, [case("V1", "Do you offer gift wrapping inventdetail?"),
                            case("V2", "Do you offer gift wrapping citeone?")])
        base = ["--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--eval", extra, "--fallback-config", fb,
                "--fake-retriever", "--retrieval", "routed", "--fallback", "gate", "--gate-style", "omit",
                "--loop-guard", "--tool-view", "compact", "--harness-tools", "--forced-answer", "recover"]
        self.assertEqual(run_eval.main(["--name", "r_s10off"] + base), 0)
        self.assertEqual(run_eval.main(["--name", "r_s10"] + base + ["--verify-answers", "shown"]), 0)
        off, on = self.read("r_s10off"), self.read("r_s10")
        if on[("V1", 0)]["route"] not in ("store", "unclear"):
            self.skipTest("fake router did not send the question to the knowledge path")
        self.assertIn("verify_failed", on[("V1", 0)]["flags"])
        self.assertEqual(on[("V1", 0)]["verify"]["unsupported"], ["300 m", "ceramic"])
        self.assertEqual(on[("V1", 0)]["final_reply"], "Sorry, I don't have that.")
        v2 = on[("V2", 0)]
        self.assertEqual((v2["final_reply"], v2["verify"]["cited"]), ("Yes, we can help with that.", [1]))
        # replaying the check on the run made without it gives the same replies
        sys.path.insert(0, os.path.join(ROOT, "eval"))
        import replay_verify
        self.assertEqual(replay_verify.main([os.path.join(self.tmp, "r_s10off"), "--mode", "shown", "--name", "r_s10rep"]), 0)
        rep = self.read("r_s10rep")
        for k in (("V1", 0), ("V2", 0)):
            self.assertEqual(rep[k]["final_reply"], on[k]["final_reply"])
        self.assertEqual(off[("V1", 0)]["final_reply"], rep[("V1", 0)]["original_reply"])

    # ---- Objective 3, Step 11: product in focus and follow-up retrieval ----
    def test_focus_and_followups(self):
        from harness import focus as F
        msgs = [{"role": "user", "content": "Tell me about the Meridian Sable."},
                {"role": "assistant", "content": "The Meridian Sable (1027SM02) is a women's formal watch."},
                {"role": "user", "content": "What glass does it have?"}]
        self.assertEqual(F.product_in_focus(msgs), {"style_id": "V1027", "code": "1027SM02", "name": "Meridian Sable"})
        self.assertIsNone(F.product_in_focus(msgs[-1:]))                       # one turn: nothing in focus
        self.assertTrue(F.is_followup("What glass does it have?"))
        self.assertTrue(F.is_followup("Iska glass kaun sa hai?"))
        self.assertFalse(F.is_followup("What glass does the Meridian Atlas have?"))
        self.assertFalse(F.is_followup("Is 1001SL01 water resistant?"))
        for q in ("Gift wrapping milta hai kya?", "Store kab tak khula hai?", "What are your store hours?",
                  "Which payment methods do you accept?"):
            self.assertFalse(F.is_followup(q), q)                              # Step 11b: store questions
        self.assertTrue(F.is_followup("Warranty kitne time ki hai?"))
        self.assertTrue(F.is_followup("Is it covered by the return policy?"))
        self.assertEqual(F.retrieval_query(msgs, F.product_in_focus(msgs)),
                         "What glass does it have? Tell me about the Meridian Sable. Meridian Sable")
        path, fb = self.rag_setup()
        extra = os.path.join(self.tmp, "s11.jsonl")
        c1 = case("F1", "x")
        c1["messages"] = [dict(m) for m in msgs]
        c2 = case("F2", "x")
        c2["messages"] = [dict(m) for m in msgs[:2]] + [{"role": "user", "content": "Is it in stock here?"}]
        write_cases(extra, [c1, c2, case("F3", "What glass does the Meridian Sable have?")])
        base = ["--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--eval", extra, "--fallback-config", fb,
                "--fake-retriever", "--retrieval", "routed", "--fallback", "store-live", "--gate-style", "omit",
                "--loop-guard", "--tool-view", "compact", "--harness-tools", "--forced-answer", "recover"]
        self.assertEqual(run_eval.main(["--name", "r_s11"] + base + ["--followup-retrieval", "--focus-memory"]), 0)
        rs = self.read("r_s11")
        f1 = rs[("F1", 0)]
        self.assertEqual(f1["followup"]["focus"]["style_id"], "V1027")
        if f1["route"] in ("store", "unclear"):
            self.assertEqual(f1["retrieval"]["chunk_ids"][0], "product:V1027")
            self.assertIn("Meridian Sable", f1["retrieval"]["query"])
        f2 = rs[("F2", 0)]
        self.assertEqual(f2["route"], "stock")
        self.assertEqual(f2["tool_calls"][0]["arguments"]["product_id"], "1027SM02")
        self.assertEqual(F.own_route("Does it come with a black dial?"), "stock")
        self.assertIsNone(F.own_route("What glass does it have?"))
        self.assertIsNone(rs[("F3", 0)]["followup"])                          # single turn: unchanged

    def test_http500_retry_with_usual_cap(self):
        extra = os.path.join(self.tmp, "s13.jsonl")
        write_cases(extra, [case("H1", "formal watch fail500")])
        argv = ["--name", "r_500", "--url", f"http://127.0.0.1:{PORT}", "--eval", extra, "--results-dir", self.tmp,
                "--max-tokens", "120", "--answer-length"]
        self.assertEqual(run_eval.main(argv), 0)
        r = self.read("r_500")[("H1", 0)]
        self.assertFalse(r.get("error"))
        self.assertIn("http500_retry_max_tokens", r["flags"])

    def test_printed_call_parsing(self):
        t = "Found it.\n<tool_call>\n<function=check_inventory>\n<parameter=product_id>\n1027SM02\n</parameter>\n</function>\n</tool_call>"
        self.assertEqual(run_eval.strip_tool_text(t), "Found it.")
        self.assertEqual(run_eval.parse_printed_calls(t), [("check_inventory", {"product_id": "1027SM02"})])
        self.assertEqual(run_eval.parse_printed_calls('{"name": "call_staff", "arguments": {"reason": "try_on"}}'),
                         [("call_staff", {"reason": "try_on"})])
        self.assertEqual(run_eval.parse_printed_calls("<function=made_up><parameter=x>1</parameter></function>"), [])

    def test_plan_harness_calls(self):
        info = {"codes": ["1102SL03", "1093SL02"]}
        self.assertEqual(run_eval.plan_harness_calls("compare", "Compare 1102SL03 and 1093SL02", info),
                         [("compare_products", {"product_ids": ["1102SL03", "1093SL02"]})])
        self.assertEqual(run_eval.plan_harness_calls("lookup", "I came for 1354RR02 but I can't see it here",
                                                     {"codes": ["1354RR02"]})[0][1]["reason"], "out_of_stock")
        self.assertEqual(run_eval.plan_harness_calls("stock", "Is it in stock?", {"codes": []}), [])   # nothing to check
        name = next(iter(run_eval._design_index()))
        plan = run_eval.plan_harness_calls("stock", f"Do you have the {name} with a grey dial?", {"codes": []})
        self.assertEqual(plan[0][1]["colour"], "grey")
        self.assertEqual(run_eval.plan_harness_calls("staff", "I want to speak to the manager", {"codes": []}),
                         [("call_staff", {"reason": "other"})])

    # ---- Objective 3, Step 6: discovery policy and simulated dialogues ----
    def test_discovery_cases_and_dialogues(self):
        from harness import discovery as D
        s = D.extract_slots(["I need a gift for my wife.", "Office, around 10,000. Leather please."])
        self.assertEqual(D.search_args(s), {"price_max": 10000, "gender": "women", "style": "formal",
                                            "strap_material": "leather"})
        self.assertEqual(D.decide(D.extract_slots(["I want to buy a watch."]), 0), "ask")
        self.assertEqual(D.decide(D.extract_slots(["Do you have a solar watch?"]), 0), "search")
        self.assertEqual(D.extract_slots(["Koi automatic watch hai 40000 ke neeche, gents ke liye?"])["price_max"], 40000)
        self.assertEqual(D.extract_slots(["Watch for my daughter.", "She's 10. Under 1,500 please."])["gender"], "kids")
        _, fb = self.rag_setup()
        prof = os.path.join(self.tmp, "dlg.jsonl")
        subprocess.run([sys.executable, os.path.join(ROOT, "eval", "build_dialogues.py"), "--n", "4", "--out", prof],
                       check=True, capture_output=True)
        base = ["--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp, "--fallback-config", fb,
                "--fake-retriever", "--retrieval", "routed", "--fallback", "gate", "--gate-style", "omit", "--loop-guard",
                "--tool-view", "compact", "--harness-tools", "--dialogues", prof]
        self.assertEqual(run_eval.main(["--name", "d_tmpl", "--discovery", "template"] + base), 0)
        self.assertEqual(run_eval.main(["--name", "d_none"] + base), 0)
        rs = self.read("d_tmpl")
        self.assertEqual(len(rs), 4)
        for r in rs.values():
            d = r["dialogue"]
            self.assertIsNotNone(d["recommended_at"])                       # every dialogue ends in a search
            self.assertLessEqual(d["recommended_at"], 2)                     # at most two questions
            for t in d["turns"][:d["recommended_at"]]:
                self.assertEqual(t["model_requests"], 0)                     # template questions: no model call
            rec = d["turns"][d["recommended_at"]]
            self.assertEqual(rec["tool_calls"][-1].get("by"), "harness")
            self.assertLessEqual(rec["model_requests"], 1)
        out = os.path.join(self.tmp, "_dlg")
        sys.path.insert(0, os.path.join(ROOT, "eval"))
        import score_dialogues
        self.assertEqual(score_dialogues.main([os.path.join(self.tmp, "d_*"), "--profiles", prof, "--out", out,
                                               "--pair", os.path.join(self.tmp, "d_none"), os.path.join(self.tmp, "d_tmpl")]), 0)
        with open(os.path.join(out, "summary.json"), encoding="utf-8") as f:
            sm = json.load(f)
        self.assertEqual(sm["d_tmpl"]["recommended"], 1.0)
        self.assertEqual(sm["d_tmpl"]["fit_mean"] is None, False)


if __name__ == "__main__":
    unittest.main()
