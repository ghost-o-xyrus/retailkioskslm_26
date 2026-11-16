"""
Objective 4 tests (no model needed).

    python -m unittest finetune.test_finetune
"""

import csv
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)


def rows(p):
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Step1Tests(unittest.TestCase):
    def test_training_catalogue_is_disjoint(self):
        p = os.path.join(ROOT, "data_train", "clean", "styles.csv")
        if not os.path.exists(p):
            self.skipTest("run finetune/build_train_catalogue.py first")
        dep, new = rows(os.path.join(ROOT, "data", "clean", "styles.csv")), rows(p)
        self.assertFalse({r["collection"] for r in dep} & {r["collection"] for r in new})
        self.assertFalse({r["style_name"] for r in dep} & {r["style_name"] for r in new})
        self.assertFalse({r["style_id"] for r in dep} & {r["style_id"] for r in new})
        self.assertTrue(all(int(r["style_id"][1:]) > 6000 for r in new))

    def test_policy_numbers_moved(self):
        import build_train_catalogue as B
        self.assertEqual(B.perturb("Rs. 250 to Rs. 450 | 5 to 7 days"), "Rs. 300 to Rs. 550 | 7 to 9 days")
        self.assertEqual(B.rename("Workday and Neon Digital"), "Officeline and Lumen Digital")


class Step3Tests(unittest.TestCase):
    def test_reply_checks(self):
        import filter_wording as F
        t = {"question": "How big is the Vantage Filigree?", "language": "en", "draft_type": "answer", "kind": "answer",
             "style": "compose", "draft": "Case: Steel, 40 mm wide.", "evidence": [["40 mm"]],
             "shown": [{"role": "user", "content": "[1] Veyra Vantage Filigree (design V6126)\nCase: Steel, 40 mm wide."}]}
        self.assertEqual(F.checks(t, "The Vantage Filigree has a 40 mm steel case.", None), [])
        self.assertIn("unsupported", F.checks(t, "It has a 42 mm case.", None))
        self.assertIn("missing fact", F.checks(t, "It is a steel watch.", None))
        self.assertIn("staff on answer", F.checks(t, "It is 40 mm wide. Shall I call a staff member to help?", None))
        self.assertIn("language", F.checks(dict(t, language="hinglish"), "The Vantage Filigree has a 40 mm steel case.", None))
        nl = dict(t, draft_type="not_listed", evidence=[], draft="Sorry, that detail isn't listed.")
        self.assertEqual(F.checks(nl, "Sorry, that isn't listed for this watch. Would you like me to call a staff member?", None), [])
        self.assertIn("no decline", F.checks(nl, "It weighs 80 grams.", None))
        self.assertIn("staff promised", F.checks(nl, "Sorry, that isn't listed. A staff member is coming.", None))

    def test_teacher_prompt(self):
        import teacher as T
        t = {"task": "x", "question": "Price of 6126BL01?", "language": "hinglish", "kind": "answer", "style": "compose",
             "draft_type": "answer", "draft": "MRP Rs. 4,995.", "shown": [{"role": "user", "content": "card"}]}
        p = T.prompt(t)
        self.assertIn("Hinglish", p)
        self.assertIn("MRP Rs. 4,995.", p)
        self.assertIn("Word limit: 40 words", p)
        self.assertEqual(T.seed_of("x"), T.seed_of("x"))


class Step4Tests(unittest.TestCase):
    class Tok:
        """Qwen-like template: the generation prompt adds an empty thinking block; earlier turns do not."""
        def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=False, tools=None, enable_thinking=True):
            s = "<|im_start|>system\ntools<|im_end|>\n" if tools else ""
            for m in msgs:
                c = m.get("content") or ""
                for t in m.get("tool_calls") or []:
                    c += "<tool_call>\n" + json.dumps({"name": t["function"]["name"],
                                                       "arguments": t["function"]["arguments"]}) + "\n</tool_call>"
                s += f"<|im_start|>{m['role']}\n{c}<|im_end|>\n"
            return s + ("<|im_start|>assistant\n" + ("" if enable_thinking else "<think>\n\n</think>\n\n")
                        if add_generation_prompt else "")

        def __call__(self, text, add_special_tokens=False):
            return {"input_ids": [ord(ch) for ch in text]}

    def test_answer_only_split(self):
        import prepare_sft as P
        tok = self.Tok()
        ex = {"messages": [{"role": "user", "content": "Is it in stock?"}], "target": {"role": "assistant", "content": "Yes."}}
        prompt, answer, how = P.render(tok, ex, None)
        self.assertEqual((answer, how), ("Yes.<|im_end|>\n", "joined"))
        self.assertTrue(prompt.endswith("<think>\n\n</think>\n\n"))
        call = {"role": "assistant", "content": "", "tool_calls": [{"id": "c", "type": "function", "function": {
            "name": "check_inventory", "arguments": "{\"product_id\": \"6126BL01\"}"}}]}
        prompt, answer, how = P.render(tok, dict(ex, target=call), [{"type": "function"}])
        self.assertIn('"arguments": {"product_id": "6126BL01"}', answer)      # arguments passed as an object
        self.assertTrue(P.held_out("x") == P.held_out("x"))


class Step2Tests(unittest.TestCase):
    def test_no_training_question_copies_an_eval_question(self):
        import build_train_questions as Q
        leak = Q.Leak()
        for name in ("tools", "store", "followups"):
            p = os.path.join(HERE, "train", f"{name}.jsonl")
            if not os.path.exists(p):
                self.skipTest("run finetune/build_train_questions.py first")
            for c in Q.load_jsonl(p):
                self.assertNotIn(Q.norm(c["messages"][-1]["content"]), leak.norm, c["id"])
                self.assertEqual(c["split"], "train")

    def test_oracle_next_action(self):
        import oracle_server as O
        case = {"id": "X1", "language": "en", "subcategory": "details", "messages": [{"role": "user", "content": "Tell me about 6126BL01."}],
                "o4": {"kind": "tools", "calls": [{"name": "get_product_details", "args": {"product_id": "6126BL01"}}],
                       "evidence": []}}
        card = {"id": "X2", "language": "en", "subcategory": "product_spec",
                "messages": [{"role": "user", "content": "How big is the Vantage Filigree?"}],
                "o4": {"kind": "answer", "evidence": [["40 mm"]], "gold_ids": ["product:V6126"]}}
        O.STATE["cases"] = [case, card]
        tools = [{"type": "function", "function": {"name": "get_product_details"}}]
        msg, c, act = O.decide({"messages": [{"role": "system", "content": "s"}, {"role": "user", "content": "Tell me about 6126BL01."}],
                                "tools": tools})
        self.assertEqual((c["id"], act, msg["tool_calls"][0]["function"]["name"]), ("X1", "call", "get_product_details"))
        after = [{"role": "system", "content": "s"}, {"role": "user", "content": "Tell me about 6126BL01."},
                 {"role": "assistant", "content": "", "tool_calls": msg["tool_calls"]},
                 {"role": "tool", "content": "6126BL01 Vantage Filigree | Rs 4,995"}]
        msg, c, act = O.decide({"messages": after, "tools": tools})
        self.assertEqual(act, "reply")
        self.assertIn("Vantage Filigree", msg["content"])
        shown = "Store information:\n\n[1] Veyra Vantage Filigree (design V6126)\nCase: Steel, 40 mm wide.\n\n[2] Veyra Other (design V6999)\nCase: 38 mm wide.\n\nHow big is the Vantage Filigree?"
        msg, c, act = O.decide({"messages": [{"role": "user", "content": shown}], "tools": tools, "tool_choice": "none"})
        self.assertEqual((c["id"], act, msg.get("draft")), ("X2", "reply", "answer"))
        self.assertIn("40 mm", msg["content"])
        wrong = shown.replace("40 mm wide.\n\n[2]", "39 mm wide.\n\n[2]").replace("38 mm", "40 mm")
        msg, c, act = O.decide({"messages": [{"role": "user", "content": wrong}], "tools": tools})
        self.assertEqual(act, "fetch")                       # 40 mm is on another watch's card, not this one's

    def test_export_gaps(self):
        import export_examples as E
        case = {"o4": {"kind": "answer"}}
        rec = {"response": {"content": "x"}, "draft": "answer",
               "request": {"tool_choice": "none", "messages": [{"role": "tool", "content": "r"}]}}
        self.assertEqual(E.gaps_of(rec, case), ["format", "ordinary", "staff_discipline"])
        rec = {"response": {"tool_calls": [{}]}, "draft": None, "request": {"messages": []}}
        self.assertEqual(E.gaps_of(rec, case), ["tool_choice"])


FAKE_LLAMA = r"""#!/usr/bin/env python3
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
argv = sys.argv[1:]
if "--help" in argv:
    print("--lora FNAME  --lora-init-without-apply  --reasoning-budget N"); sys.exit(0)
port = int(argv[argv.index("--port") + 1])
lora = argv[argv.index("--lora") + 1] if "--lora" in argv else None
if lora:
    print("llama_adapter_lora_init_impl: loaded 252 tensors from lora file", flush=True)

def template(b):
    s = "<|im_start|>system\ntools<|im_end|>\n" if b.get("tools") else ""
    for m in b["messages"]:
        s += "<|im_start|>" + m["role"] + "\n" + (m.get("content") or "") + "<|im_end|>\n"
    return s + "<|im_start|>assistant\n<think>\n\n</think>\n\n"

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, obj):
        d = json.dumps(obj).encode(); self.send_response(200)
        self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(d)))
        self.end_headers(); self.wfile.write(d)
    def do_GET(self):
        if self.path == "/health": self.send({"status": "ok"})
        elif self.path == "/lora-adapters": self.send([{"id": 0, "path": lora, "scale": 0.0}] if lora else [])
    def do_POST(self):
        b = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/apply-template": return self.send({"prompt": template(b)})
        scale = (b.get("lora") or [{"scale": 0}])[0]["scale"] if lora else 0
        text = "Yes, it is." if scale else "plain reply"
        self.send({"choices": [{"message": {"content": text}, "finish_reason": "stop"}]})

HTTPServer(("127.0.0.1", port), H).serve_forever()
"""


class Step5Tests(unittest.TestCase):
    def test_step5_checks_on_a_fake_server(self):
        import tempfile
        import types
        import step5_check as S
        tmp = tempfile.mkdtemp()
        for d in ("adapters/lora_2b", "examples", "models"):
            os.makedirs(os.path.join(tmp, d))
        json.dump({"tier": "A", "model": "unsloth/Qwen3.5-2B", "qlora": False},
                  open(os.path.join(tmp, "adapters/lora_2b/train_log.json"), "w"))
        os.makedirs(os.path.join(tmp, "adapters/lora_4b"))
        json.dump({"tier": "B", "model": "unsloth/Qwen3.5-4B", "qlora": False},
                  open(os.path.join(tmp, "adapters/lora_4b/train_log.json"), "w"))
        for n in ("lora_2b", "lora_4b"):
            open(os.path.join(tmp, f"adapters/{n}/adapter_model.safetensors"), "w").close()
        json.dump({"t": [{"type": "function"}]}, open(os.path.join(tmp, "examples/tools.json"), "w"))
        with open(os.path.join(tmp, "examples/tierA_final.jsonl"), "w") as f:
            for i in range(6):
                f.write(json.dumps({"id": f"e{i}", "case_id": f"c{i}", "tools": "t" if i % 2 else None,
                                    "messages": [{"role": "user", "content": f"Is {i} in stock?"}],
                                    "target": {"role": "assistant", "content": "Yes, it is."}}) + "\n")
        open(os.path.join(tmp, "models/Qwen3.5-2B-Q8_0.gguf"), "w").close()
        open(os.path.join(tmp, "models/Qwen3.5-4B-Q4_K_M.gguf"), "w").close()
        with open(os.path.join(tmp, "examples/tierB_final.jsonl"), "w") as f:
            f.write(open(os.path.join(tmp, "examples/tierA_final.jsonl")).read())
        exe, conv = os.path.join(tmp, "llama-server"), os.path.join(tmp, "convert.py")
        open(exe, "w").write(FAKE_LLAMA)
        os.chmod(exe, 0o755)
        open(conv, "w").write("import sys\nopen(sys.argv[sys.argv.index('--outfile') + 1], 'wb').write(b'x' * 1000)\n")
        fake = types.ModuleType("transformers")
        fake.AutoTokenizer = types.SimpleNamespace(from_pretrained=lambda *_a, **_k: Step4Tests.Tok())
        old = sys.modules.get("transformers"), S.HERE, S.OUT
        sys.modules["transformers"], S.HERE, S.OUT = fake, tmp, os.path.join(tmp, "adapters_gguf")
        try:
            rc = S.main(["--server", exe, "--convert", conv, "--adapters", "lora_2b", "qlora_4b", "lora_4b", "--models",
                         os.path.join(tmp, "models"), "--n", "3", "--n-template", "6"])
        finally:
            if old[0] is None:
                sys.modules.pop("transformers")
            else:
                sys.modules["transformers"] = old[0]
            S.HERE, S.OUT = old[1], old[2]
        r = json.load(open(os.path.join(tmp, "adapters_gguf/step5_report.json")))["lora_2b"]
        self.assertEqual(rc, 0, r)
        self.assertEqual(r["template_identical"], [6, 6])
        self.assertEqual(r["scale0_identical"], [3, 3])
        self.assertEqual(r["scale1"]["exact"], 3)
        self.assertTrue(r["load_ok"] and r["passed"])

    def test_plan_lora_key(self):
        src = open(os.path.join(ROOT, "harness", "run_plan.py"), encoding="utf-8").read()
        self.assertIn('"--lora-scaled"', src)


class Step6Tests(unittest.TestCase):
    def test_plan_copies_o3_final(self):
        import build_step6_plan as B
        plan = B.build()
        runs = {r["name"]: r for r in plan["runs"]}
        self.assertEqual(len(runs), 20)
        base, ad = runs["o4s6_2b_base_rag"], runs["o4s6_2b_qlora_rag"]
        self.assertEqual({k: v for k, v in base.items() if k not in ("name", "config_label")},
                         {k: v for k, v in ad.items() if k not in ("name", "config_label", "lora")})
        self.assertEqual(base["split"], "dev")
        self.assertFalse(runs["o4s6_4b_base_v12"].get("answer_length"))      # Tier B: no short-reply rule
        self.assertEqual(runs["o4s6_4b_lora_dlg"]["lora"], "finetune/adapters_gguf/lora_4b.gguf")
        q = {r["name"]: r for r in B.build("qlora_4b")["runs"]}
        self.assertEqual(q["o4s6_4b_qlora_rag"]["lora"], "finetune/adapters_gguf/qlora_4b.gguf")
        import step6_verdicts as V
        tmp = os.path.join(__import__("tempfile").mkdtemp(), "p.json")
        json.dump(B.build("qlora_4b"), open(tmp, "w"))
        self.assertEqual(V.adapters(tmp)["qlora_4b"], ("B", "4b", "qlora"))
        B.build()                                           # leave the shipped plan (lora_4b) in place
        self.assertEqual(V.adapters()["lora_4b"], ("B", "4b", "lora"))

    def test_verdicts(self):
        import tempfile
        import step6_verdicts as V
        tmp = tempfile.mkdtemp()

        def row(b, n, sub, nn, br, nr, lo, hi, verdict):
            return {"base": b, "new": n, "subset": sub, "n": nn, "base_rate": br, "new_rate": nr,
                    "diff_pts": 100 * (nr - br), "ci": [lo, hi], "mcnemar_p": 0.5, "verdict": verdict}
        rows, speed = [], []
        for m, tags in (("2b", ("lora", "qlora")), ("4b", ("lora",))):
            for t in tags:
                for s, sub in (("rag", "all checked"), ("v12", "tool cases"), ("fup", "all checked")):
                    b, n = f"o4s6_{m}_base_{s}", f"o4s6_{m}_{t}_{s}"
                    rows.append(row(b, n, sub, 100, 0.6, 0.62, -3, 7, "tie"))
                    rows.append(row(b, n, "language: hinglish", 10, 0.6, 0.5 if t == "qlora" and m == "2b" else 0.6,
                                    -30, 10, "(small)"))
                b, n = f"o4s6_{m}_base_rag", f"o4s6_{m}_{t}_rag"
                rows.append(row(b, n, "answerable", 90, 0.7, 0.7, -5, 5, "tie"))
                rows.append(row(b, n, "unanswerable / near-miss", 60, 0.55, 0.65, 1, 19, "better"))
                speed.append({"base": b, "new": n, "base_speed": {"first_p50_s": 3.0}, "new_speed": {"first_p50_s": 3.1},
                              "base_disc": {"staff_on_answerable": 10}, "new_disc": {"staff_on_answerable": 4},
                              "base_unsup": [5, 100], "new_unsup": [4, 100]})
        for s in ("rag", "v12", "fup"):
            rows.append(row(f"o4s6_2b_lora_{s}", f"o4s6_2b_qlora_{s}", "all checked" if s != "v12" else "tool cases",
                            100, 0.62, 0.6, -6, 2, "tie"))
        os.makedirs(os.path.join(tmp, "_compare_step6"))
        json.dump({"rows": rows, "speed": speed}, open(os.path.join(tmp, "_compare_step6", "compare.json"), "w"))
        os.makedirs(os.path.join(tmp, "_dialogues_step6"))
        summ, lines = {}, ["run,dialogue,fit"]
        for m, tags in (("2b", ("base", "lora", "qlora")), ("4b", ("base", "lora"))):
            for t in tags:
                summ[f"o4s6_{m}_{t}_dlg"] = {"recommended": 1.0, "slots2_share": 1.0, "questions_max": 2, "fit_mean": 0.95}
                lines += [f"o4s6_{m}_{t}_dlg,d{i},0.95" for i in range(5)]
        json.dump(summ, open(os.path.join(tmp, "_dialogues_step6", "summary.json"), "w"))
        open(os.path.join(tmp, "_dialogues_step6", "dialogues.csv"), "w").write("\n".join(lines) + "\n")
        for m, tags in (("2b", ("base", "lora", "qlora")), ("4b", ("base", "lora"))):
            for t in tags:
                for s in ("rag", "v12", "fup", "dlg"):
                    d = os.path.join(tmp, f"o4s6_{m}_{t}_{s}")
                    os.makedirs(d)
                    k = 3 if (t == "base" and m == "2b" and s == "rag") else 0
                    with open(os.path.join(d, "cases.jsonl"), "w") as f:
                        for i in range(5):
                            f.write(json.dumps({"id": f"c{i}", "flags": ["tool_call_as_text"] if i < k else []}) + "\n")
        V.main(["--results", tmp])
        res = json.load(open(os.path.join(tmp, "_step6", "verdicts.json")))
        self.assertEqual(res["lora_2b"]["status"], "kept")
        self.assertEqual(res["lora_2b"]["checks"]["H1"], "gain")
        self.assertEqual(res["lora_2b"]["checks"]["H2"], "met")
        self.assertEqual(res["lora_2b"]["checks"]["H3"], "met")
        self.assertEqual(res["qlora_2b"]["checks"]["hinglish"], "fell")             # pooled -10 points
        self.assertEqual(res["qlora_2b"]["status"], "not kept")
        self.assertEqual(res["lora_4b"]["status"], "provisional (decided in Step 7)")   # 4B printed nothing before
        self.assertEqual(res["H6"]["tier_A_carried"], "lora_2b")


def _row(b, n, sub, nn, br, nr, lo, hi, verdict):
    return {"base": b, "new": n, "subset": sub, "n": nn, "base_rate": br, "new_rate": nr, "diff_pts": 100 * (nr - br),
            "ci": [lo, hi], "mcnemar_p": 0.5, "verdict": verdict}


def _fake_runs(tmp, prefixes, printed=None, tps=None, meta_ram=None, sets=("rag", "v12", "fup", "dlg"), repeats=1):
    for pre in prefixes:
        for s in sets:
            d = os.path.join(tmp, f"{pre}_{s}")
            os.makedirs(d, exist_ok=True)
            k = (printed or {}).get((pre, s), 0)
            with open(os.path.join(d, "cases.jsonl"), "w") as f:
                for rep in range(repeats):
                    for i in range(5):
                        f.write(json.dumps({"id": f"c{i}", "repeat": rep,
                                            "flags": ["tool_call_as_text"] if i < k and rep == 0 else [],
                                            "metrics": {"tokens_per_s": (tps or {}).get(pre, 10.0)}}) + "\n")
            json.dump({"run_peak_rss_mb": (meta_ram or {}).get(pre, 3000)}, open(os.path.join(d, "run_meta.json"), "w"))


def _fake_dialogues(tmp, sub, runs):
    os.makedirs(os.path.join(tmp, sub), exist_ok=True)
    json.dump({r: {"recommended": 1.0, "slots2_share": 1.0, "questions_max": 2, "fit_mean": 0.95} for r in runs},
              open(os.path.join(tmp, sub, "summary.json"), "w"))
    lines = ["run,dialogue,fit"] + [f"{r},d{i},0.95" for r in runs for i in range(5)]
    open(os.path.join(tmp, sub, "dialogues.csv"), "w").write("\n".join(lines) + "\n")


class Step7Tests(unittest.TestCase):
    def test_plan(self):
        import build_step78_plans as B
        plan = B.build_step7("lora_2b", "lora_4b")
        runs = {r["name"]: r for r in plan["runs"]}
        s6 = B.step6_runs()
        self.assertEqual(len(runs), 20)
        off, src = runs["o4s7_2b_lora_off_rag"], s6["o4s6_2b_lora_rag"]
        self.assertEqual((off["forced_answer"], off["staff_check"], src["forced_answer"], src["staff_check"]),
                         ("replace", False, "recover", True))
        diff = {k for k in set(off) | set(src) if off.get(k) != src.get(k)}
        self.assertEqual(diff, {"name", "config_label", "forced_answer", "staff_check", "staff_guard"})
        sh = runs["o4s7_4b_lora_short_v12"]
        self.assertEqual((sh["answer_length"], sh["max_tokens"], sh["forced_answer"]), (True, 120, "recover"))
        self.assertEqual(runs["o4s7_4b_base_short_dlg"].get("lora"), None)
        self.assertEqual([r["name"] for r in plan["runs"]][-1], "o4s7_4b_base_short_dlg")    # controls last
        self.assertEqual(B.build_step7("none", "none")["runs"], [])

    def test_carried_from_real_step6_shape(self):
        import build_step78_plans as B
        v = {"lora_2b": {"status": "kept"}, "lora_4b": {"status": "kept"},
             "H6": {"qlora_vs_lora": {}, "tier_A_carried": "lora_2b"}, "tier_B_carried": "lora_4b"}
        self.assertEqual((B.carried(v, "A"), B.carried(v, "B")), ("lora_2b", "lora_4b"))
        self.assertEqual(B.carried({"H6": {"tier_A_carried": None}}, "A"), None)

    def test_verdicts(self):
        import tempfile
        import step7_verdicts as V
        import build_step78_plans as B
        tmp = tempfile.mkdtemp()
        plan = B.build_step7("lora_2b", "lora_4b")
        pp = os.path.join(tmp, "plan.json")
        json.dump(plan, open(pp, "w"))
        os.makedirs(os.path.join(tmp, "_step6"))
        json.dump({"lora_4b": {"status": "provisional (decided in Step 7)"}},
                  open(os.path.join(tmp, "_step6", "verdicts.json"), "w"))
        news = {"o4s7_2b_lora_off": "o4s6_2b_base", "o4s7_2b_base_off": "o4s6_2b_base",
                "o4s7_4b_lora_short": "o4s6_4b_base", "o4s7_4b_lora_shortoff": "o4s6_4b_base",
                "o4s7_4b_base_short": "o4s6_4b_base"}
        rows = []
        for n, b in news.items():
            for s, sub in (("rag", "all checked"), ("v12", "tool cases"), ("fup", "all checked")):
                worse = n == "o4s7_4b_lora_shortoff" and s == "v12"
                rows.append(_row(f"{b}_{s}", f"{n}_{s}", sub, 60, 0.7, 0.55 if worse else 0.7,
                                 -25 if worse else -5, -5 if worse else 5, "worse" if worse else "tie"))
                rows.append(_row(f"{b}_{s}", f"{n}_{s}", "language: hinglish", 12, 0.6, 0.6, -10, 10, "(small)"))
        os.makedirs(os.path.join(tmp, "_compare_step7"))
        json.dump({"rows": rows, "speed": []}, open(os.path.join(tmp, "_compare_step7", "compare.json"), "w"))
        _fake_dialogues(tmp, "_dialogues_step7", [f"{x}_dlg" for x in list(news) + ["o4s6_2b_base", "o4s6_4b_base"]])
        _fake_runs(tmp, list(news), printed={("o4s7_4b_base_short", "rag"): 4})
        V.main(["--results", tmp, "--plan", pp])
        res = json.load(open(os.path.join(tmp, "_step7", "verdicts.json")))
        self.assertEqual(res["deployed"]["A"], {"adapter": "lora_2b", "patches": "off", "short_reply": True})
        self.assertEqual(res["deployed"]["B"], {"adapter": "lora_4b", "patches": "on", "short_reply": True})
        self.assertEqual(res["checks"]["o4s7_4b_base_short"]["printed"], "not met")     # control: 4 printed
        self.assertFalse(res["H5"]["B"])


class Step8Tests(unittest.TestCase):
    def test_plan(self):
        import build_step78_plans as B
        plan = B.build_step8("qlora_2b")
        names = [r["name"] for r in plan["runs"]]
        self.assertEqual(names, ["o4s8_2b_base_rag", "o4s8_2b_qlora_rag", "o4s8_2b_base_v12", "o4s8_2b_qlora_v12"])
        r = plan["runs"][1]
        self.assertEqual((r["backend"], r["repeats"], r["ids"], r["server_args"][-1], r["lora"]),
                         ("cpu", 2, "eval/o3_dev_speed_ids.json", "4", "finetune/adapters_gguf/qlora_2b.gguf"))
        import tempfile
        tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmp, "_step7"))
        json.dump({"deployed": {"A": {"adapter": "lora_2b", "patches": "off"}}},
                  open(os.path.join(tmp, "_step7", "verdicts.json"), "w"))
        old, B.R = B.R, tmp
        try:
            names = [r["name"] for r in B.build_step8()["runs"]]
        finally:
            B.R = old
        self.assertIn("o4s8_2b_lora_off_v12", names)
        self.assertEqual(len(names), 6)

    def test_verdicts(self):
        import tempfile
        import step8_verdicts as V
        import build_step78_plans as B
        tmp = tempfile.mkdtemp()
        plan = B.build_step8("lora_2b")
        plan["adapters"]["patches_off"] = True
        pp = os.path.join(tmp, "plan.json")
        json.dump(plan, open(pp, "w"))
        os.makedirs(os.path.join(tmp, "_step7"))
        json.dump({"deployed": {"B": {"adapter": "lora_4b", "patches": "on", "short_reply": True}}},
                  open(os.path.join(tmp, "_step7", "verdicts.json"), "w"))
        _fake_runs(tmp, ["o4s8_2b_base", "o4s8_2b_lora", "o4s8_2b_lora_off"], sets=("rag", "v12"), repeats=2,
                   tps={"o4s8_2b_base": 20.0, "o4s8_2b_lora": 18.5, "o4s8_2b_lora_off": 18.4},
                   meta_ram={"o4s8_2b_base": 3000, "o4s8_2b_lora": 3060})
        _fake_runs(tmp, ["o4s6_4b_base", "o4s7_4b_lora_short"], sets=("rag", "v12", "fup"))
        waits = []
        for s in ("rag", "v12"):
            waits.append({"base": f"o4s8_2b_base_{s}", "new": f"o4s8_2b_lora_off_{s}", "n": 35,
                          "first_word_s": [-0.2, -0.5, 0.1], "total_s": [0.3 if s == "v12" else -1.0,
                                                                         0.1 if s == "v12" else -2.0, 0.9]})
        os.makedirs(os.path.join(tmp, "_compare_step8"))
        json.dump({"rows": [], "speed": [], "waits": waits}, open(os.path.join(tmp, "_compare_step8", "compare.json"), "w"))
        V.main(["--results", tmp, "--plan", pp])
        res = json.load(open(os.path.join(tmp, "_step8", "verdicts.json")))
        self.assertTrue(res["tier_A"]["checks"]["rag"]["writing_speed"])              # 18.5 / 20 = 0.925
        self.assertTrue(res["tier_A"]["checks"]["rag"]["total_time"])
        self.assertFalse(res["tier_A"]["checks"]["v12"]["total_time"])               # interval wholly above 0
        self.assertFalse(res["tier_A"]["speed_rules_met"])
        self.assertEqual(res["tier_A"]["peak_ram_mb"], [3000, 3060])
        self.assertEqual(res["tier_B"]["candidate"], "o4s7_4b_lora_short")


if __name__ == "__main__":
    unittest.main()
