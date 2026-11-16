"""
Tests for the retrieval code. No model downloads needed.   python -m unittest retrieval.test_retrieval -v
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
from retrievers import BM25Retriever, DenseRetriever, HybridRetriever, Reranker, tokenize  # noqa: E402
import bench_retrieval as B  # noqa: E402

CHUNKS = [
    {"id": "product:V1003", "text": "Veyra Meridian Orion (design V1003)\n- 1003SL01: blue dial. MRP Rs. 57,995."},
    {"id": "product:V1004", "text": "Veyra Meridian Prism (design V1004)\n- 1004SM01: white dial. Watches for men."},
    {"id": "faq:hours", "text": "Store FAQ. What are the store hours? Central Mall store: 10:00 to 22:00 every day."},
    {"id": "glossary:chronograph", "text": "Watch glossary. Chronograph: a watch with a built-in stopwatch."},
]


class RetrievalTests(unittest.TestCase):
    def test_tokenize(self):
        self.assertIn("1003sl01", tokenize("Is 1003SL01 a men's or women's watch?"))
        self.assertNotIn("s", tokenize("men's watch"))          # the possessive 's is not a word
        self.assertEqual(tokenize("Watches"), ["watch"])         # plural folding
        self.assertEqual(tokenize("batteries glass straps"), ["battery", "glass", "strap"])
        self.assertNotIn("kya", tokenize("kya hai"))

    def test_bm25(self):
        r = BM25Retriever(CHUNKS)
        self.assertEqual(r.search("Tell me about 1003SL01", 2)[0][0], "product:V1003")
        self.assertEqual(r.search("when does the store close? hours", 1)[0][0], "faq:hours")
        self.assertEqual(r.search("zzzz", 3), [])

    def test_dense_hybrid_rerank(self):
        dense = DenseRetriever(CHUNKS, "BAAI/bge-small-en-v1.5", encoder=B.FakeEncoder())
        self.assertTrue(dense.q_prefix.startswith("Represent"))
        top = dense.search("stopwatch chronograph", 2)
        self.assertEqual(top[0][0], "glossary:chronograph")
        self.assertGreaterEqual(top[0][1], top[1][1])
        hyb = HybridRetriever(BM25Retriever(CHUNKS), dense)
        self.assertEqual(hyb.search("Meridian Orion blue", 1)[0][0], "product:V1003")
        fused = HybridRetriever.fuse([[("a", 9), ("b", 8)], [("b", 1), ("c", 0)]], 3)
        self.assertEqual(fused[0][0], "b")                      # ranked by both lists
        rr = Reranker(CHUNKS, model=B.FakeCrossEncoder())
        out = rr.rerank("store hours", [("product:V1003", 1.0), ("faq:hours", 0.5)], 2)
        self.assertEqual(out[0][0], "faq:hours")
        self.assertIn(("store hours", "faq:hours"), rr.cache)

    def test_metrics(self):
        items = [dict(id="q1", split="dev", gold_ids=["a"], answer_type="fact", subtype="x", language="en", near_miss=False),
                 dict(id="q2", split="dev", gold_ids=["b"], answer_type="fact", subtype="x", language="en", near_miss=False),
                 dict(id="q3", split="dev", gold_ids=[], answer_type="none", subtype="y", language="en", near_miss=False)]
        ranks = {"q1": [("a", 0.9), ("b", 0.1)], "q2": [("c", 0.8), ("b", 0.7)], "q3": [("a", 0.2)]}
        m = B.metrics(items, ranks, "dev")
        self.assertEqual(m["recall@1"], 0.5)
        self.assertEqual(m["recall@5"], 1.0)
        self.assertAlmostEqual(m["mrr@10"], 0.75)
        self.assertEqual(m["auroc_top1"], 1.0)                 # both answerable top scores beat the unanswerable one

    def test_full_fake_run(self):
        for need in ("corpus.jsonl", "retrieval_eval.jsonl"):
            if not os.path.exists(os.path.join(ROOT, "knowledge", need)):
                self.fail(f"knowledge\\{need} is missing: unzip the Step 3 and Step 4 packages first")
        with tempfile.TemporaryDirectory() as out:
            cmd = [sys.executable, os.path.join(HERE, "bench_retrieval.py"), "--configs",
                   "bm25,hybrid-bge-small-en-v1.5+minilm", "--fake", "--latency-sample", "5", "--out", out]
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(p.returncode, 0, "benchmark failed:\n" + p.stdout[-1500:] + "\n" + p.stderr[-3000:])
            self.assertTrue(os.path.exists(os.path.join(out, "report.md")))
            ranks = os.path.join(out, "ranks", "hybrid-bge-small-en-v1.5+minilm.jsonl")
            with open(ranks, encoding="utf-8") as f:
                rows = [json.loads(l) for l in f]
            self.assertEqual(len(rows), 500)
            self.assertLessEqual(len(rows[0]["top"]), 10)


    def test_latency_fake_run(self):
        with tempfile.TemporaryDirectory() as out:
            cmd = [sys.executable, os.path.join(HERE, "bench_latency.py"), "--fake", "--backends", "torch,onnx",
                   "--latency-sample", "5", "--out", out]
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(p.returncode, 0, "latency benchmark failed:\n" + p.stdout[-1500:] + "\n" + p.stderr[-3000:])
            with open(os.path.join(out, "report.md"), encoding="utf-8") as f:
                self.assertIn("**Chosen:**", f.read())

    def test_calibrate_fallback_fake(self):
        with tempfile.TemporaryDirectory() as out:
            run = lambda args: subprocess.run([sys.executable] + args, capture_output=True, text=True,
                                              encoding="utf-8", errors="replace")
            p = run([os.path.join(HERE, "bench_latency.py"), "--fake", "--backends", "torch,openvino",
                     "--latency-sample", "5", "--out", out])
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            p = run([os.path.join(HERE, "calibrate_fallback.py"), "--ranks",
                     os.path.join(out, "ranks", "openvino-len256-depth20.jsonl"), "--out", os.path.join(out, "fb")])
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            with open(os.path.join(out, "fb", "fallback.json"), encoding="utf-8") as f:
                cfg = json.load(f)
            self.assertIn("threshold", cfg)
            self.assertIn("hinglish", cfg["messages"])
            self.assertFalse(cfg["hinglish_bypass"])
            p = run([os.path.join(HERE, "calibrate_fallback.py"), "--hinglish-bypass", "--ranks",
                     os.path.join(out, "ranks", "openvino-len256-depth20.jsonl"), "--out", os.path.join(out, "fb2")])
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            with open(os.path.join(out, "fb2", "fallback.json"), encoding="utf-8") as f:
                self.assertTrue(json.load(f)["hinglish_bypass"])
            with open(os.path.join(out, "fb2", "report.md"), encoding="utf-8") as f:
                self.assertIn("Post-hoc variant", f.read())

    def test_knowledge_base_and_integration_check(self):
        with tempfile.TemporaryDirectory() as out:
            run = lambda args: subprocess.run([sys.executable] + args, capture_output=True, text=True,
                                              encoding="utf-8", errors="replace")
            p = run([os.path.join(HERE, "bench_latency.py"), "--fake", "--backends", "torch,openvino",
                     "--latency-sample", "5", "--out", out])
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            ranks = os.path.join(out, "ranks", "openvino-len256-depth20.jsonl")
            p = run([os.path.join(HERE, "calibrate_fallback.py"), "--hinglish-bypass", "--ranks", ranks,
                     "--out", os.path.join(out, "fb")])
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            fb = os.path.join(out, "fb", "fallback.json")
            p = run([os.path.join(HERE, "check_integration.py"), "--fake", "--ranks", ranks, "--fallback", fb,
                     "--out", os.path.join(out, "int"), "--limit", "60"])
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            with open(os.path.join(out, "int", "integration.json"), encoding="utf-8") as f:
                self.assertIn(json.load(f)["k"], (1, 2, 3, 4, 5))
            with open(os.path.join(out, "int", "report.md"), encoding="utf-8") as f:
                self.assertIn("Same top-1 chunk: 60/60", f.read())     # same code path as Step 5b
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase(fallback_path=fb, fake=True, k=3)
            r = kb.retrieve("Gift card milta hai kya?")
            self.assertTrue(r["hinglish"])
            self.assertFalse(r["refuse"])                               # Hinglish bypass
            self.assertLessEqual(len(r["chunks"]), 3)
            self.assertEqual(set(r["timings_ms"]), {"bm25", "dense", "fuse", "rerank", "total"})
            self.assertTrue(kb.context(r).startswith("[1] "))
            res, _ = kb.tool_result("store hours")
            self.assertTrue(res["results"])
            p = run([os.path.join(HERE, "check_context_view.py"), "--ranks", ranks, "--fallback", fb,
                     "--out", os.path.join(out, "int")])
            self.assertEqual(p.returncode, 0, p.stderr[-2000:])
            with open(os.path.join(out, "int", "context_view.json"), encoding="utf-8") as f:
                self.assertIn(json.load(f)["view"], ("full", "compact"))

    def test_compact_view(self):
        from knowledge_base import load_chunks, model_text, view_tokens
        ch = load_chunks()
        card = ch["product:V1003"]
        self.assertIn("Description:", model_text(card))
        short = model_text(card, "compact")
        self.assertNotIn("Description:", short)
        self.assertIn("1003SL01", short)                                  # variants and prices stay
        self.assertLess(view_tokens(card, "compact"), view_tokens(card))
        faq = next(c for c in ch.values() if c["type"] == "faq")
        self.assertEqual(model_text(faq, "compact"), faq["text"])         # only product cards change

    def test_rag_cases_file(self):
        path = os.path.join(ROOT, "eval", "rag_cases.jsonl")
        with open(path, encoding="utf-8") as f:
            cases = [json.loads(l) for l in f]
        self.assertEqual(len(cases), 524)
        new = [c for c in cases if c["id"].startswith("R-HUN-")]
        self.assertEqual(len(new), 24)
        self.assertTrue(all(c["split"] == "test" and c["expected"]["behaviour"] == "decline" for c in new))
        with open(os.path.join(ROOT, "eval", "rag_pilot_ids.json"), encoding="utf-8") as f:
            pilot = set(json.load(f)["ids"])
        self.assertTrue(all(c["split"] == "dev" for c in cases if c["id"] in pilot))   # pilot never touches test

    def test_hinglish_detector(self):
        from language import is_hinglish
        for q in ("Gift card milta hai kya?", "Store kitne baje band hota hai?", "Namaste",
                  "Battery badalne ka kitna lagega?", "Corsair Ridge automatic hai ya quartz?"):
            self.assertTrue(is_hinglish(q), q)
        for q in ("Do you sell perfume?", "Tell me a joke.", "Show me 1247SP02.", "What do you recommend?",
                  "Is the band on V1003 leather?", "When does the store close?"):
            self.assertFalse(is_hinglish(q), q)


class Step9Tests(unittest.TestCase):
    def test_training_data_and_trial_code_paths(self):
        import build_rerank_train as BT
        import finetune_reranker as FT
        import bench_reranker as BR
        with tempfile.TemporaryDirectory() as t:
            tr, va = os.path.join(t, "train.jsonl"), os.path.join(t, "val.jsonl")
            self.assertEqual(BT.main(["--fake", "--out-train", tr, "--out-val", va, "--report", os.path.join(t, "r.md")]), 0)
            rows = B.load_jsonl(tr)
            self.assertGreater(len(rows), 1000)
            self.assertTrue(all(r["pos"] not in r["negs"] and len(r["negs"]) >= 1 for r in rows))
            self.assertTrue(any(r["lang"] == "hinglish" for r in rows))
            # no generated question repeats an eval question
            ev = {BT.norm(x) for x in BT.eval_texts()}
            self.assertFalse(any(BT.norm(r["query"]) in ev for r in rows))
            self.assertEqual(FT.main(["--train", tr, "--val", va, "--dry-run"]), 0)
            self.assertEqual(BR.main(["--fake", "--out", os.path.join(t, "trial"), "--latency-sample", "5"]), 0)
            with open(os.path.join(t, "trial", "summary.json")) as f:
                s = json.load(f)
            self.assertEqual(len(s["rows"]), 6)
            self.assertIsNone(s["choice"])               # identical fake scores: nothing beats the baseline
            # recall on Kaggle, latency re-measured locally
            os.environ["SLM_MACHINE"] = "kaggle-cpu"
            try:
                self.assertEqual(BR.main(["--fake", "--out", os.path.join(t, "k"), "--latency-sample", "5"]), 0)
            finally:
                del os.environ["SLM_MACHINE"]
            with open(os.path.join(t, "k", "summary.json")) as f:
                self.assertTrue(json.load(f)["latency_remote"])
            with open(os.path.join(t, "k", "report.md"), encoding="utf-8") as f:
                self.assertIn("--latency-only", f.read())
            self.assertEqual(BR.main(["--fake", "--out", os.path.join(t, "k"), "--latency-sample", "5", "--latency-only"]), 0)
            with open(os.path.join(t, "k", "summary.json")) as f:
                s2 = json.load(f)
            self.assertFalse(s2["latency_remote"])
            self.assertEqual({r["recall_machine"] for r in s2["rows"]}, {"kaggle-cpu"})
            self.assertEqual(len(s2["rows"]), 6)
            base = {"r3": 0.80, "r3_hinglish": 0.5}
            self.assertTrue(BR.qualifies({"p50_ms": 250, "r3": 0.83, "r3_hinglish": 0.5}, base))
            self.assertFalse(BR.qualifies({"p50_ms": 350, "r3": 0.90, "r3_hinglish": 0.9}, base))   # too slow
            self.assertTrue(BR.qualifies({"p50_ms": 250, "r3": 0.80, "r3_hinglish": 0.58}, base))
            self.assertFalse(BR.qualifies({"p50_ms": 250, "r3": 0.79, "r3_hinglish": 0.7}, base))   # overall lower


class Step12Tests(unittest.TestCase):
    def test_speed_bench_code_path(self):
        import bench_speed as BS
        with tempfile.TemporaryDirectory() as t:
            fb = os.path.join(t, "fb.json")
            with open(fb, "w") as f:
                json.dump({"threshold": 0.3, "hinglish_bypass": True, "messages": {"en": "x", "hinglish": "y"}}, f)
            self.assertEqual(BS.main(["--fake", "--out", t, "--fallback", fb, "--configs", "base,rt-fp32-l128-compact",
                                      "--threads", "4"]), 0)
            with open(os.path.join(t, "summary.json")) as f:
                s = json.load(f)
            self.assertEqual(len(s["rows"]), 2)
            with open(os.path.join(t, "choice.json")) as f:
                ch = json.load(f)
            self.assertEqual(set(ch) >= {"backend", "int8", "max_length", "rerank_view", "threads", "ranks"}, True)
            self.assertTrue(os.path.exists(os.path.join(ROOT, ch["ranks"])))


class Step13Tests(unittest.TestCase):
    def test_focused_cards(self):
        from knowledge_base import load_chunks, focused_text, model_text
        ch = load_chunks()
        c = ch["product:V1027"]
        g = focused_text(c, "What glass does the Meridian Sable have?")
        self.assertIn("Glass: Sapphire", g)
        self.assertNotIn("MRP", g)
        self.assertLess(len(g), len(model_text(c, "compact")))
        self.assertIn("MRP Rs. 38,895", focused_text(c, "How much is it?"))
        self.assertIn("Made in: Switzerland", focused_text(c, "Ye kahan bani hai?"))
        self.assertEqual(focused_text(c, "Tell me about it"), model_text(c, "compact"))     # no topic: whole card
        faq = next(x for x in ch.values() if x["type"] == "faq")
        self.assertEqual(focused_text(faq, "What glass?"), faq["text"])                    # only product cards

    def test_focused_cards_13a2(self):
        from knowledge_base import load_chunks, focused_text
        ch = load_chunks()
        g = focused_text(ch["product:V3890"], "Tick Digital Grove ki keemat kya hai?")   # "Digital" is the name
        self.assertIn("MRP Rs. 1,895", g)
        self.assertNotIn("Movement:", g)
        g = focused_text(ch["product:V2950"], "Is it automatic or quartz?")
        self.assertIn("Movement: quartz", g)
        self.assertIn("Variant codes: 2950PF01.", g)                                    # codes always kept
        self.assertNotIn("MRP", g)


if __name__ == "__main__":
    unittest.main()
