"""
Objective 5, Steps 2-3 tests against the stand-in llama-server (no model needed).

    python -m unittest kiosk_core.test_core -v
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from harness import run_eval, run_plan  # noqa: E402
from kiosk_core import parity, stage_check  # noqa: E402

PORT = 8098


def case(cid, text, mode="tools", context=None, messages=None):
    return {"id": cid, "category": "tool_selection", "subcategory": "x", "mode": mode, "language": "en",
            "difficulty": "easy", "split": "dev", "set": "core",
            "messages": messages or [{"role": "user", "content": text}],
            "context": context, "expected": {"behaviour": "answer"}, "rubric": [], "source": "", "notes": ""}


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = subprocess.Popen([sys.executable, os.path.join(ROOT, "harness", "fake_server.py"),
                                       "--port", str(PORT)])
        assert run_eval.wait_for_server(f"http://127.0.0.1:{PORT}", 20)
        cls.tmp = tempfile.mkdtemp()
        with open(os.path.join(ROOT, "data", "clean", "skus.csv"), encoding="utf-8") as f:
            next(f)
            cls.sku = next(f).split(",")[0]
        cls.fb = os.path.join(cls.tmp, "fallback.json")
        with open(cls.fb, "w", encoding="utf-8") as f:
            json.dump({"threshold": 0.3, "hinglish_bypass": True,
                       "messages": {"en": "Sorry, I don't have that.", "hinglish": "Maaf kijiye."}}, f)
        sku = cls.sku
        cls.cases = os.path.join(cls.tmp, "cases.jsonl")
        cs = [case("T1", f"Tell me about {sku}"), case("T2", f"Is {sku} in stock?"), case("T3", f"Can I try {sku}?"),
              case("T4", "formal watch under 15000"), case("T5", "hi there"), case("T6", "please astext"),
              case("T7", "please badjson"), case("K1", "Do you offer gift wrapping?"),
              case("K2", "Do you offer gift wrapping inventdetail?"), case("E1", "Do you sell Fossil watches?"),
              case("F1", "What's the weather like today?"), case("P1", "Do you have a strap printcall"),
              case("C1", "Do you offer gift wrapping staffask?"),
              case("S7", "Formal watch for my father under 15000"),
              case("M1", "", messages=[{"role": "user", "content": f"Tell me about {sku}"},
                                       {"role": "assistant", "content": "It is a fine watch."},
                                       {"role": "user", "content": "does it come in black?"}]),
              case("G1", "Is it water resistant? think", mode="grounded", context="water_resistance: 50")]
        with open(cls.cases, "w", encoding="utf-8") as f:
            for c in cs:
                f.write(json.dumps(c) + "\n")
        cls.o3 = ["--fallback-config", cls.fb, "--fake-retriever", "--retrieval", "routed", "--fallback", "store-live",
                  "--gate-style", "omit", "--loop-guard", "--tool-view", "compact", "--harness-tools",
                  "--forced-answer", "recover", "--entity-check", "--staff-check", "--verify-answers", "shown",
                  "--discovery", "template", "--followup-retrieval", "--focus-memory", "--dedupe-shown",
                  "--context-view", "focused", "--answer-length", "--max-tokens", "120"]

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=10)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_eval(self, name, extra=(), eval_file=None):
        argv = ["--name", name, "--url", f"http://127.0.0.1:{PORT}", "--eval", eval_file or self.cases,
                "--results-dir", self.tmp, "--model", "fake", "--quant", "Q4", "--backend", "test"] + list(extra)
        return run_eval.main(argv)

    def read(self, name):
        with open(os.path.join(self.tmp, name, "cases.jsonl"), encoding="utf-8") as f:
            return {(r["id"], r["repeat"]): r for r in map(json.loads, f)}

    # ---- Step 2: parity ----
    def test_parity_plain_and_o3_final_settings(self):
        for tag, extra in (("plain", []), ("o3", self.o3)):
            self.assertEqual(self.run_eval(f"p_{tag}_legacy", extra), 0)
            self.assertEqual(self.run_eval(f"p_{tag}_core", list(extra) + ["--engine", "core"]), 0)
            c = parity.compare(os.path.join(self.tmp, f"p_{tag}_legacy"), os.path.join(self.tmp, f"p_{tag}_core"))
            real = [d for d in c["diffs"] if d.get("counts", True)]
            self.assertEqual((c["n"], c["same"], real), (16, 16, []), c["diffs"])
        rs = self.read("p_o3_core")
        self.assertEqual(rs[("E1", 0)]["flags"], ["entity_not_carried"])           # the paths really ran
        self.assertTrue(any(c.get("by") == "harness" for c in rs[("T2", 0)]["tool_calls"]))
        with open(os.path.join(self.tmp, "p_o3_core", "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual((meta["engine"], meta["stages"], meta["stage_policy"]), ("core", True, "resident"))
        self.assertEqual(parity.main(["--results", self.tmp, "--pair", "p_o3_legacy", "p_o3_core"]), 0)

    # ---- Step 3: stages ----
    def test_stages_logged_and_add_up(self):
        self.assertEqual(self.run_eval("s_core", self.o3 + ["--engine", "core"]), 0)
        rs = self.read("s_core")
        for k, r in rs.items():
            for st, sm, mt, cl, tot in stage_check.turns_of(r):
                self.assertEqual(stage_check.check_turn(st, sm, mt, cl, tot), [], (k, st))
        k1 = rs[("K1", 0)]
        names = [s["stage"] for s in k1["stages"]]
        self.assertEqual(names[:3], ["input", "route", "retrieval"])
        self.assertIn("model_round", names)
        sub = {x["name"] for s in k1["stages"] for x in s.get("sub") or []}
        self.assertTrue({"router", "bm25", "dense", "rerank", "reading", "writing"} <= sub, sub)
        self.assertIn("rss_mb", k1["stages"][0])
        t2 = rs[("T2", 0)]
        self.assertIn("harness_tools", [s["stage"] for s in t2["stages"]])
        self.assertIsNotNone(t2["stage_summary"]["instrumentation_ms"])
        # the clock off: no stages, same replies
        self.assertEqual(self.run_eval("s_off", self.o3 + ["--engine", "core", "--no-stages"]), 0)
        off = self.read("s_off")
        self.assertNotIn("stages", off[("K1", 0)])
        self.assertEqual({k: r["final_reply"] for k, r in off.items()}, {k: r["final_reply"] for k, r in rs.items()})

    def test_sequential_policy_matches_resident(self):
        self.assertEqual(self.run_eval("q_res", self.o3 + ["--engine", "core"]), 0)
        self.assertEqual(self.run_eval("q_seq", self.o3 + ["--engine", "core", "--stage-policy", "sequential"]), 0)
        c = parity.compare(os.path.join(self.tmp, "q_res"), os.path.join(self.tmp, "q_seq"))
        self.assertEqual(c["same"], c["n"], c["diffs"])
        seq = self.read("q_seq")
        k1 = seq[("K1", 0)]
        route = next(s for s in k1["stages"] if s["stage"] == "route")
        self.assertIn("before_route", {x["name"] for x in route.get("sub") or []})          # worker started
        released = [x for s in k1["stages"] for x in s.get("sub") or [] if x["name"] == "release"]
        self.assertEqual(len(released), 1)
        with open(os.path.join(self.tmp, "q_seq", "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["stage_manager"]["policy"], "sequential")
        self.assertGreaterEqual(meta["stage_manager"]["worker_starts"], 10)
        import multiprocessing
        self.assertEqual(multiprocessing.active_children(), [])                    # no worker left behind
        self.assertEqual(self.run_eval("q_bad", ["--stage-policy", "sequential"]), 2)  # needs --engine core

    def test_dialogues_through_core(self):
        args = self.o3 + ["--dialogues", os.path.join(ROOT, "eval", "o3_dialogues.jsonl"), "--split", "dev",
                          "--limit", "2"]
        self.assertEqual(self.run_eval("d_legacy", args), 0)
        self.assertEqual(self.run_eval("d_core", args + ["--engine", "core"]), 0)
        c = parity.compare(os.path.join(self.tmp, "d_legacy"), os.path.join(self.tmp, "d_core"))
        self.assertEqual(c["same"], c["n"], c["diffs"])
        r = next(iter(self.read("d_core").values()))
        self.assertTrue(all(t.get("stages") for t in r["dialogue"]["turns"]))

    # ---- the app entry ----
    def test_run_turn_matches_harness(self):
        from kiosk_core.turn import Engine, Session, run_turn
        self.assertEqual(self.run_eval("t_core", self.o3 + ["--engine", "core", "--no-count-tokens"]), 0)
        h = self.read("t_core")
        argv = ["--name", "app", "--url", f"http://127.0.0.1:{PORT}", "--results-dir", self.tmp,
                "--engine", "core"] + self.o3
        eng = Engine(argv)
        try:
            self.assertIsNotNone(eng.warmup())
            events = []
            s = Session()
            rec = run_turn(s, f"Is {self.sku} in stock?", eng, emit=events.append)
            self.assertEqual(rec["final_reply"], h[("T2", 0)]["final_reply"])
            self.assertEqual(parity.calls(rec), parity.calls(h[("T2", 0)]))
            kinds = [e["type"] for e in events]
            self.assertEqual(kinds[0], "turn_start")
            self.assertIn("stage_start", kinds)
            self.assertIn("tool_call", kinds)
            self.assertEqual(kinds[-2:], ["final", "metrics"])
            self.assertEqual(len(s.messages), 2)
            rec2 = run_turn(s, "hi there", eng)
            self.assertEqual(rec2["turn"], 2)
            self.assertEqual(len(s.messages), 4)
        finally:
            eng.close()

    def test_stream_check(self):
        from kiosk_core import stream_check
        sku = self.sku
        cs = os.path.join(self.tmp, "stream_cases.jsonl")
        with open(cs, "w", encoding="utf-8") as f:
            for c in (case("T1", f"Tell me about {sku}"), case("T4", "formal watch under 15000"),
                      case("K1", "Do you offer gift wrapping?"), case("T5", "hi there")):
                f.write(json.dumps(c) + "\n")
        self.assertEqual(self.run_eval("st_same", self.o3 + ["--engine", "core", "--stream-check"], cs), 0)
        plain = list(self.read("st_same").values())
        self.assertTrue(all("stream_check" in r for r in plain))
        n = sum(len(r["stream_check"]) for r in plain)
        self.assertGreater(n, 0)
        s = stream_check.summarise(os.path.join(self.tmp, "st_same", "cases.jsonl"))
        self.assertEqual((s["different"], s["cases_identical"]), ([], 4))
        # the turn itself is unchanged by the check
        self.assertEqual(self.run_eval("st_off", self.o3 + ["--engine", "core"], cs), 0)
        def key(r):
            return (r.get("final_reply"), [(c.get("name"), json.dumps(c.get("arguments"), sort_keys=True))
                                           for c in r.get("tool_calls") or []])
        a = {r["id"]: key(r) for r in plain}
        b = {r["id"]: key(r) for r in self.read("st_off").values()}
        self.assertEqual(a, b)
        self.assertEqual(self.run_eval("st_x", ["--stream-check"], cs), 2)          # needs --engine core
        # a streamed tool call that parses differently is caught
        msgs = [{"role": "user", "content": "formal watch under 15000 streamsplit"}]
        resp = run_eval.http_json(f"http://127.0.0.1:{PORT}/v1/chat/completions",
                                  {"messages": msgs, "tools": [{"type": "function", "function": {"name": "search_catalogue"}}]})
        import urllib.request
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/chat/completions",
                                     data=json.dumps({"messages": msgs, "stream": True, "tools": [
                                         {"type": "function", "function": {"name": "search_catalogue"}}]}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as r:
            st = stream_check.parse_stream(r)
        c = stream_check.compare(resp, st)
        if resp["choices"][0]["message"].get("tool_calls"):
            self.assertFalse(c["calls_same"])
        # report over a plan
        plan = {"results_dir": self.tmp, "runs": [{"name": "st_same"}]}
        pp = os.path.join(self.tmp, "p4.json")
        json.dump(plan, open(pp, "w"))
        stream_check.main(["--plan", pp, "--results", self.tmp])
        v = json.load(open(os.path.join(self.tmp, "_stream_step4", "verdict.json"), encoding="utf-8"))
        self.assertTrue(v["stream_all_rounds"])

    def test_images_route_and_score(self):
        from kiosk_core import media
        if not os.path.exists(media.table_path()):
            media.build()
        self.assertEqual(self.run_eval("img_dev", self.o3 + ["--engine", "core", "--images", "--split", "dev"],
                                       os.path.join(ROOT, "eval", "image_cases.jsonl")), 0)
        recs = self.read("img_dev")
        self.assertEqual(len(recs), 40)
        r = next(v for (k, _), v in recs.items() if k == "IMG-D001")
        self.assertEqual(r["route"], "images")
        self.assertEqual(r["tool_calls"][0]["name"], "show_product_images")
        from eval import score_images
        self.assertEqual(score_images.main(["--runs", "img_dev", "--results", self.tmp, "--cards-runs"]), 0)
        # never on an ordinary question, and URLs never pass through from model text
        self.assertFalse(media.wants_images("Does the Desk Saffron have a see-through caseback?"))
        self.assertTrue(media.wants_images("1546SL01 ki photo dikhao"))
        from kiosk_core.engine import URL_RE
        self.assertEqual(URL_RE.sub("", "See ![x](/media/a_1.svg) or https://x.com/p.png here"), "See  or  here")

    def test_plan_keys_and_built_plans(self):
        argv = run_plan.eval_argv_for({"name": "x", "engine": "core", "stages": False, "stage_policy": "sequential"},
                                      8080, "e.jsonl", "r")
        self.assertIn("--no-stages", argv)
        self.assertEqual(argv[argv.index("--engine") + 1], "core")
        self.assertEqual(argv[argv.index("--stage-policy") + 1], "sequential")
        from kiosk_core import build_plans
        s2, s3, s4, s7 = build_plans.build()
        self.assertEqual(len(s7["runs"]), 4)
        self.assertTrue(all(r["images"] and r["engine"] == "core" for r in s7["runs"]))
        self.assertEqual([r["name"] for r in s4["runs"]], ["o5s4_2b_v12_stream", "o5s4_4b_v12_stream"])
        self.assertTrue(all(r["stream_check"] and r["engine"] == "core" for r in s4["runs"]))
        self.assertIn("--stream-check", run_plan.eval_argv_for(s4["runs"][0], 8080, "e.jsonl", "r"))
        self.assertEqual(len(s2["runs"]), 12)
        a, b = s2["runs"][0], s2["runs"][1]
        self.assertEqual({k for k in set(a) | set(b) if a.get(k) != b.get(k)}, {"name", "engine", "config_label"})
        names = [r["name"] for r in s3["runs"]]
        self.assertEqual(names[:2], ["o5s3_2b_rag_off", "o5s3_2b_rag_on"])
        self.assertEqual(s3["runs"][0]["server_args"][-2:], ["-t", "4"])


if __name__ == "__main__":
    unittest.main()
