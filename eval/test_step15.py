"""
Objective 3, Step 15 tests: the ladder plans, the Kaggle queue, the ladder table, the judge packet and summary,
and the scorecard, on synthetic runs in the harness's record format (no model, no Kaggle).

    python -m unittest eval.test_step15 -v
"""

import json
import os
import random
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "kaggle"))


def jl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def fake_run(root, name, eval_file, model, rng, good=0.7, label="local", route_of=None):
    """A run folder: run_meta.json + cases.jsonl, replies right with probability `good`."""
    cases = [c for c in jl(os.path.join(ROOT, eval_file)) if c["split"] == "test"]
    d = os.path.join(root, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"eval_file": eval_file, "model": model, "machine": {"label": label},
                   "retrieval": {"condition": "always", "fallback": "gate"}}, f)
    with open(os.path.join(d, "cases.jsonl"), "w", encoding="utf-8") as f:
        for c in cases:
            e = c["expected"]
            ok = rng.random() < good
            if "gold_ids" in e:                         # a store question
                reply = (" ".join(x if isinstance(x, str) else x[0] for x in (e.get("must_include") or ["yes"]))
                         if ok and e["behaviour"] == "answer" else
                         ("I'm sorry, I don't have that information." if ok else "It is 42 mm and costs Rs 999."))
                calls = []
                ret = {"condition": "always", "chunk_ids": list(e.get("gold_ids") or [])[:3], "view": "compact",
                       "query": c["messages"][-1]["content"], "fallback_applied": False}
            else:
                rc = (e.get("required_calls") or [[]])[0]
                calls = [{"name": x["name"], "arguments": x.get("arguments", {}), "arguments_valid_json": True,
                          "known_tool": True, "by": "harness" if rng.random() < 0.5 else None, "result": {}}
                         for x in rc] if ok else []
                reply = "Here you go."
                ret = {"condition": "none"}
            rec = {"id": c["id"], "repeat": 0, "route": (route_of or (lambda c: "store"))(c), "final_reply": reply,
                   "tool_calls": calls, "flags": [], "turns": [{"prompt_n": rng.randint(100, 600)}],
                   "retrieval": ret,
                   "metrics": {"first_visible_ms": rng.randint(800, 9000), "end_to_end_ms": rng.randint(2000, 14000),
                               "retrieval_ms": rng.randint(150, 400), "peak_rss_mb": 2600, "harness_rss_mb": 900}}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return d


class LadderPlanTests(unittest.TestCase):
    def test_plans(self):
        import build_o3_ladder as B
        jobs = B.build()
        self.assertEqual(len(jobs), 34)
        names = [r["name"] for v in jobs.values() for r in v]
        self.assertEqual(len(names), len(set(names)))
        for v in jobs.values():
            for r in v:
                self.assertEqual(r["backend"], "cpu")
                self.assertEqual(r["split"], "test")
        r2 = next(r for r in jobs[("r2", "2b", "rag")])
        r1 = next(r for r in jobs[("r1", "2b", "rag")])
        self.assertEqual((r1["retrieval"], r2["retrieval"]), ("always", "routed"))
        self.assertTrue(r1["loop_guard"] and "harness_tools" not in r2)
        nr = jobs[("nr", "4b", "rest")]
        self.assertTrue(all(r["retrieval"] == "always" and r["harness_tools"] for r in nr))
        self.assertTrue(any(r.get("dialogues") for r in jobs[("b0", "2b", "rest")]))
        # every Kaggle job carries a time budget below the 12-hour limit
        from push_job import plan_job
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "x.json")
            with open(p, "w") as f:
                json.dump({"results_dir": "results_obj3", "kaggle_max_minutes": 650, "runs": jobs[("r6", "2b", "rag")]}, f)
            name, job = plan_job(p)
            self.assertEqual(job["max_minutes"], 650)
            self.assertIn("results_obj3/_speed_step12/choice.json", job["inputs"])


class QueueTests(unittest.TestCase):
    def test_queue_pushes_resumes_and_finishes(self):
        import run_queue as Q
        with tempfile.TemporaryDirectory() as t:
            plans = []
            for i in range(3):
                p = os.path.join(t, f"p{i}.json")
                with open(p, "w") as f:
                    json.dump({"runs": [{"name": f"r{i}", "backend": "cpu"}]}, f)
                plans.append(p)
            progress = {p: 0 for p in plans}
            pushed, status = [], {}
            Q.STATE = os.path.join(t, "state.json")
            Q.plan_runs = lambda p: [("r", progress[p], 2)]
            Q.finished = lambda p: progress[p] >= 2

            batches = []

            def push_batch(batch, unfinished, user):     # Kaggle takes at most 2 at once
                batches.append(list(batch))
                live = sum(1 for k, v in status.items() if v == "running")
                done = {}
                for p in batch:
                    if live + len(done) >= 2:
                        return done, True
                    pushed.append(p)
                    status["u/" + Q.job_name(p)] = "running"
                    done[p] = "u/" + Q.job_name(p)
                return done, False

            def pull(name):
                p = next(x for x in plans if Q.job_name(x) == name)
                progress[p] += 1          # each push finishes half: the job is pushed twice
                return 0

            def kst(k):
                s = status[k]
                status[k] = "complete"
                return s
            Q.PUSH, Q.pull, Q.kernel_status = push_batch, pull, kst
            import time
            Q.time.sleep = lambda s: None
            try:
                rc = Q.main(plans + ["--poll", "0"])          # auto: as many as Kaggle accepts
            finally:
                Q.time.sleep = time.sleep
            self.assertEqual(rc, 0)
            self.assertEqual(sorted(pushed), sorted(plans * 2))
            self.assertEqual(len(batches[0]), 3)                  # all three tried at once; Kaggle took two
            st = json.load(open(Q.STATE))
            self.assertTrue(all(v["state"] == "finished" and v["pushes"] == 2 for v in st.values()))


class LadderTableTests(unittest.TestCase):
    def test_ladder_with_partial_runs(self):
        import step15_ladder as L
        with tempfile.TemporaryDirectory() as t:
            rng = random.Random(1)
            files = {"rag": "eval/rag_cases_o3t.jsonl", "v12": "eval/eval_set_o3t.jsonl", "fup": "eval/rag_followups.jsonl"}
            for m, model in (("2b", "Qwen3.5-2B"), ("4b", "Qwen3.5-4B")):
                for k, g in zip(["b0", "r1", "r2", "r3", "r4", "r5", "r6"], [0.5, 0.55, 0.6, 0.7, 0.72, 0.75, 0.75]):
                    for s, ef in files.items():
                        fake_run(t, f"o3l_{k}_{m}_{s}", ef, model, rng, g, "kaggle-cpu")
                for s, ef in files.items():
                    fake_run(t, f"o3t_b0_{m}_{s}", ef, model, rng, 0.5)
                fake_run(t, f"o3l_ref_{m}_oracle", files["rag"], model, rng, 0.8, "kaggle-cpu")
                fake_run(t, f"o3l_ref_{m}_none", files["v12"], model, rng, 0.7, "kaggle-cpu")
            L.R, L.OUT = t, os.path.join(t, "_step15")
            self.assertEqual(L.main(), 0)
            md = open(os.path.join(t, "_step15", "ladder.md"), encoding="utf-8").read()
            self.assertIn("R5 + answer check", md)
            self.assertIn("Whole ladder", md)
            self.assertIn("within 5 points of oracle", md)
            self.assertIn("o3l_nr_2b_rag", md)                     # not run: listed as missing
            out = json.load(open(os.path.join(t, "_step15", "ladder.json")))
            self.assertIn("oracle_2b", out)
            self.assertIn("stage3_4b", out)


class JudgeAndScorecardTests(unittest.TestCase):
    def test_packet_summary_and_scorecard(self):
        sys.path.insert(0, os.path.join(HERE, "rag_judge"))
        import build_packet_o3 as P
        import summary_o3 as SU
        import o3_scorecard as SC
        with tempfile.TemporaryDirectory() as t:
            rng = random.Random(2)
            for m, model in (("2b", "Qwen3.5-2B"), ("4b", "Qwen3.5-4B")):
                for cfg, g in (("final", 0.8), ("b0", 0.6)):
                    fake_run(t, f"o3t_{cfg}_{m}_rag", "eval/rag_cases_o3t.jsonl", model, rng, g)
                    fake_run(t, f"o3t_{cfg}_{m}_v12", "eval/eval_set_o3t.jsonl", model, rng, g,
                             route_of=lambda c: "unclear" if c["category"] == "tool_selection" else "lookup")
                    fake_run(t, f"o3t_{cfg}_{m}_fup", "eval/rag_followups.jsonl", model, rng, g)
            for s in ("rag", "v12"):
                for cfg in ("b0", "final"):
                    fake_run(t, f"o3tsp_a_2b_{s}_{cfg}", "eval/rag_cases_o3t.jsonl" if s == "rag" else
                             "eval/eval_set_o3t.jsonl", "Qwen3.5-2B", rng, 0.8)
            out = os.path.join(t, "step15")
            self.assertEqual(P.main(["--results", t, "--out", out]), 0)
            key = json.load(open(os.path.join(out, "key.json")))
            pk = [x for fn in sorted(os.listdir(out)) if fn.startswith("packet_") for x in jl(os.path.join(out, fn))]
            self.assertTrue(pk and all(set(x) == {"item", "question", "information", "reply"} for x in pk))
            self.assertFalse(any("o3t_" in json.dumps(x) for x in pk))          # blind: no run names in items
            srcs = {k["source"] for k in key.values()}
            self.assertTrue({"unanswerable", "near_miss", "faith"} <= srcs)
            labels = [{"item": x["item"], "label": random.Random(i).choice(["answered", "unsupported", "declined"])}
                      for i, x in enumerate(pk)]
            with open(os.path.join(out, "labels_judge.json"), "w") as f:
                json.dump(labels, f)
            self.assertEqual(SU.main([out]), 0)
            sj = json.load(open(os.path.join(out, "summary.json")))
            self.assertIn("Qwen3.5-2B|final", sj)
            self.assertEqual(sj["Qwen3.5-2B|final"]["unanswerable"][1], 57)
            self.assertEqual(sj["Qwen3.5-2B|final"]["near_miss"][1], 82)
            # scorecard, with the judge summary copied where it reads it
            jdir = os.path.join(ROOT, "eval", "rag_judge", "step15")
            existed = os.path.exists(os.path.join(jdir, "summary.json"))
            SC.R, SC.OUT = t, os.path.join(t, "_step15")
            if not existed:
                os.makedirs(jdir, exist_ok=True)
                shutil.copy(os.path.join(out, "summary.json"), os.path.join(jdir, "summary.json"))
            try:
                self.assertEqual(SC.main(), 0)
            finally:
                if not existed:
                    shutil.rmtree(jdir)
            card = json.load(open(os.path.join(t, "_step15", "scorecard.json")))
            crit = {r["criterion"]: r for r in card["A"]}
            for k in ("Right tool run with valid arguments, whole system", "Router accuracy",
                      "Hallucination on unanswerable questions", "Wait to first word, median / 90th percentile",
                      "Tokens read before the answer, vs Objective 2 deployed", "Model rounds per turn, mean"):
                self.assertIn(k, crit)
            self.assertNotEqual(crit["Hallucination on unanswerable questions"]["value"], "pending")
            self.assertEqual(crit["Answerable store questions within 5 points of oracle cards"]["value"], "pending")


if __name__ == "__main__":
    unittest.main()
