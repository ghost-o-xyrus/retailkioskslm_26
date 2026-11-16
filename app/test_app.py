"""
Objective 5, Steps 4-5 tests: the backend API and the frontend in a browser, against the stand-in model server
(harness/fake_server.py --demo) and the stand-in retrieval. No model needed.

    python -m unittest app.test_app -v
The browser tests need Playwright with Chromium (pip install playwright, then playwright install chromium); they are
skipped without it.
"""

import json
import os
import socket
import sys
import tempfile
import threading
import unittest
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app import server as app_server  # noqa: E402


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def call(base, path, body=None):
    req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw, code = r.read().decode(), r.status
    except urllib.error.HTTPError as e:
        raw, code = e.read().decode(), e.code
    if raw.startswith("data: "):
        return code, [json.loads(x[6:]) for x in raw.split("\n\n") if x.startswith("data: ")]
    try:
        return code, json.loads(raw) if raw else None
    except ValueError:
        return code, raw                         # a page, not JSON


class AppTests(unittest.TestCase):
    mode = "lab"

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.svc = app_server.make_service(cls.mode, "A", fake=True, llama_port=free_port(), log_dir=cls.tmp)
        cls.port = free_port()
        cls.httpd = app_server.serve(cls.svc, port=cls.port)
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.svc.close()

    def new_session(self, sel=None):
        code, s = call(self.base, "/api/sessions", {"selection": sel})
        self.assertEqual(code, 200, s)
        return s


class PreloadTests(AppTests):
    mode = "kiosk"

    def test_preload_then_first_turn_needs_no_loading(self):
        code, r = call(self.base, "/api/ready")
        self.assertEqual(code, 200)
        self.assertIn(r["state"], ("idle", "ready"))
        r = self.svc.prepare()
        self.assertEqual(r["state"], "ready", r)
        self.assertTrue(self.svc.ms.alive())
        code, r = call(self.base, "/api/ready")
        self.assertEqual(r["state"], "ready")
        s = self.new_session()
        code, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "Do you offer gift wrapping?"})
        kinds = [e["type"] for e in ev]
        texts = [e.get("text") for e in ev if e["type"] == "status"]
        self.assertNotIn("model_loaded", kinds)
        self.assertNotIn("Warming up…", texts)
        self.assertNotIn("Loading the model…", texts)
        self.assertIn("final", kinds)

    def test_keep_loaded_restarts_a_stopped_server(self):
        self.svc.prepare()
        self.svc.keep_loaded(every_s=0.5)
        self.svc.ms.stop()
        import time as _t
        for _ in range(60):
            _t.sleep(0.5)
            if self.svc.ms.alive() and self.svc.readiness.get("state") == "ready":
                break
        self.assertTrue(self.svc.ms.alive())
        self.assertEqual(self.svc.readiness["state"], "ready")


class LabApiTests(AppTests):
    def test_streaming_tokens_match_the_final_reply(self):
        for msg in ("Do you offer gift wrapping?", "formal watch under 15000", "Tell me about watches please"):
            self.svc.stream = True
            s = self.new_session()
            code, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": msg})
            kinds = [e["type"] for e in ev]
            final = next(e for e in ev if e["type"] == "final")["reply"]
            toks = [e for e in ev if e["type"] == "token"]
            last_round = max((e["round"] for e in toks), default=None)
            streamed = "".join(e["text"] for e in toks if e["round"] == last_round)
            if toks:
                import re as _re          # the engine tidies the reply after the model (card numbers removed)
                self.assertEqual(_re.sub(r"\[\d+\]\s*", "", streamed).strip(), final.strip(), msg)
                self.assertLess(kinds.index("token"), kinds.index("final"))
            self.assertNotIn("veyra", json.dumps(ev).lower())
            for e in toks:
                self.assertFalse(e["text"].lstrip().startswith(("<", "{")), e)
            # the same turn without streaming gives the same reply and tool calls
            self.svc.stream = False
            s2 = self.new_session()
            code, ev2 = call(self.base, f"/api/sessions/{s2['id']}/turns", {"message": msg})
            self.assertEqual(final, next(e for e in ev2 if e["type"] == "final")["reply"])
            self.assertNotIn("token", [e["type"] for e in ev2])
        self.svc.stream = True

    def test_images_turn_media_and_cards(self):
        from kiosk_core import media
        if not os.path.exists(media.table_path()):
            media.build()
        s = self.new_session()
        code, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "Can I see the back of 1001SL01?"})
        cards = next(e for e in ev if e["type"] == "cards")["cards"]
        self.assertEqual(cards[0]["product_id"], "1001SL01")
        self.assertEqual([i["view"] for i in cards[0]["images"]], ["back", "front", "side"])
        code, body = call(self.base, cards[0]["image"])
        self.assertEqual(code, 200)
        self.assertIn("<svg", body if isinstance(body, str) else "")
        self.assertNotIn("veyra", (body or "").lower())               # no brand name in the pictures
        self.assertEqual(call(self.base, "/media/..%2F..%2Fapp%2Fconfig.py")[0], 404)
        self.assertEqual(call(self.base, "/media/nothing_1.svg")[0], 404)
        # an ordinary product card carries its main picture too
        s2 = self.new_session()
        code, ev = call(self.base, f"/api/sessions/{s2['id']}/turns", {"message": "formal watch under 15000"})
        cards = next(e for e in ev if e["type"] == "cards")["cards"]
        self.assertTrue(cards and all(c["image"] and c["image"].endswith("_1.svg") for c in cards))

    def test_release_holds_markup_and_half_words(self):
        from kiosk_core.streaming import _Release
        got = []
        r = _Release(got.append, 0)
        for p in ("The Vey", "ra Loop is ", "Rs 3,795."):
            r.add(p)
        r.end()
        self.assertEqual([g["text"] for g in got], ["The ", "Veyra Loop is ", "Rs ", "3,795."])
        got.clear()
        r = _Release(got.append, 1)
        for p in ("<tool_", "call>{\"name\": 1}"):
            r.add(p)
        r.end()
        self.assertEqual(got, [])

    def test_configs(self):
        code, c = call(self.base, "/api/configs")
        self.assertEqual(code, 200)
        self.assertEqual([t["id"] for t in c["tiers"]], ["A", "B"])
        self.assertEqual([p["id"] for p in c["pipelines"]], ["model_only", "retrieval", "o3_final", "deployed", "custom"])
        self.assertEqual(len(c["toggles"]), 7)
        self.assertTrue(all(t.get("evidence") for t in c["toggles"]))
        self.assertEqual(c["default"]["pipeline"], "deployed")
        self.assertEqual((c["deployed"]["A"]["adapter"], c["deployed"]["B"]["adapter"]), ("none", "lora"))
        self.assertFalse(c["toggle_defaults_by_model"]["qwen35-4b"]["short_replies"])
        self.assertNotIn("veyra", json.dumps(c).lower())

    def test_turn_events_cards_trace_and_brand(self):
        s = self.new_session()
        code, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "formal watch under 15000"})
        self.assertEqual(code, 200)
        kinds = [e["type"] for e in ev]
        for k in ("turn_start", "stage_start", "stage_end", "tool_call", "final", "metrics", "cards", "turn_end", "done"):
            self.assertIn(k, kinds)
        self.assertLess(kinds.index("final"), kinds.index("cards"))
        self.assertEqual(kinds[-1], "done")
        cards = next(e for e in ev if e["type"] == "cards")["cards"]
        self.assertTrue(cards and all(c["product_id"] in next(e for e in ev if e["type"] == "final")["reply"]
                                      for c in cards))
        self.assertNotIn("veyra", json.dumps(ev).lower())                       # the brand placeholder everywhere
        tid = next(e for e in ev if e["type"] == "turn_end")["turn_id"]
        code, tr = call(self.base, f"/api/turns/{tid}/trace")
        self.assertEqual(code, 200)
        self.assertTrue(tr["stages"] and tr["tool_calls"])
        self.assertEqual(tr["stages"][0]["stage"], "input")
        # the log keeps the data unchanged
        logs = [os.path.join(dp, f) for dp, _, fs in os.walk(self.tmp) for f in fs if f.endswith(".jsonl")]
        texts = []
        for p in logs:
            with open(p, encoding="utf-8") as f:
                texts.append(f.read())
        self.assertTrue(any("Veyra" in t for t in texts))
        code, st = call(self.base, "/api/stages/status")
        self.assertTrue(st["model_server"]["running"])
        code, sess = call(self.base, f"/api/sessions/{s['id']}")
        self.assertEqual(len(sess["turns"]), 1)

    def test_store_question_and_entity_reply(self):
        s = self.new_session()
        _, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "Do you offer gift wrapping?"})
        tr = call(self.base, f"/api/turns/{next(e for e in ev if e['type'] == 'turn_end')['turn_id']}/trace")[1]
        self.assertEqual(tr["route"], "store")
        self.assertIn("retrieval", [x["stage"] for x in tr["stages"]])
        _, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "Do you sell Fossil watches?"})
        final = next(e for e in ev if e["type"] == "final")["reply"]
        self.assertIn("don't sell Fossil", final)

    def test_config_change_custom_and_untested(self):
        s = self.new_session()
        sel = dict(s["selection"], pipeline="custom", toggles=dict(s["selection"]["toggles"], retrieval=False))
        code, r = call(self.base, f"/api/sessions/{s['id']}/config", {"selection": sel})
        self.assertEqual(code, 200, r)
        self.assertTrue(r["untested"])
        _, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "Do you offer gift wrapping?"})
        tr = call(self.base, f"/api/turns/{next(e for e in ev if e['type'] == 'turn_end')['turn_id']}/trace")[1]
        self.assertNotIn("retrieval", [x["stage"] for x in tr["stages"]])
        code, r = call(self.base, f"/api/sessions/{s['id']}/config", {"selection": dict(sel, tier="A", model="qwen35-4b")})
        self.assertEqual(code, 400)                                              # the 4B does not run on Tier A
        code, r = call(self.base, f"/api/sessions/{s['id']}/config", {"selection": dict(sel, adapter="lora")})
        self.assertEqual(code, 400)                                              # no adapter file yet

    def test_compare_runs_both_sides(self):
        code, c = call(self.base, "/api/compare", {"a": {"tier": "A", "model": "qwen35-2b", "pipeline": "o3_final"},
                                                   "b": {"tier": "A", "model": "qwen35-2b", "pipeline": "model_only"}})
        self.assertEqual(code, 200, c)
        _, ev = call(self.base, f"/api/compare/{c['id']}/turns", {"message": "Do you offer gift wrapping?"})
        ends = [e for e in ev if e["type"] == "turn_end"]
        self.assertEqual([e["side"] for e in ends], ["a", "b"])
        ta = call(self.base, f"/api/turns/{ends[0]['turn_id']}/trace")[1]
        tb = call(self.base, f"/api/turns/{ends[1]['turn_id']}/trace")[1]
        self.assertEqual((ta["route"], tb["route"]), ("store", "none"))

    def test_errors_and_reserved(self):
        self.assertEqual(call(self.base, "/api/voice/transcribe", {})[0], 501)
        self.assertEqual(call(self.base, "/api/voice/speak")[0], 501)
        self.assertEqual(call(self.base, "/media/x.jpg")[0], 404)
        self.assertEqual(call(self.base, "/api/sessions/nope/turns", {"message": "hi"})[0], 404)
        s = self.new_session()
        self.assertEqual(call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "  "})[0], 400)
        code, _ = call(self.base, "/")
        self.assertEqual(code, 200)


class KioskApiTests(AppTests):
    mode = "kiosk"

    def test_kiosk_locks_the_configuration(self):
        code, c = call(self.base, "/api/configs")
        self.assertEqual(([p["id"] for p in c["pipelines"]], c["toggles"]), (["deployed"], []))
        s = self.new_session({"tier": "A", "model": "qwen35-2b", "pipeline": "model_only"})
        self.assertEqual(s["selection"]["pipeline"], "deployed")                 # the request is ignored
        self.assertEqual(call(self.base, f"/api/sessions/{s['id']}/config", {"selection": {"pipeline": "custom"}})[0], 403)
        self.assertEqual(call(self.base, "/api/compare", {"a": {}, "b": {}})[0], 403)
        _, ev = call(self.base, f"/api/sessions/{s['id']}/turns", {"message": "hi there"})
        self.assertIn("final", [e["type"] for e in ev])


try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None


@unittest.skipIf(sync_playwright is None, "Playwright is not installed")
class BrowserTests(AppTests):
    def test_scenarios_in_the_browser(self):
        with sync_playwright() as p:
            try:
                b = p.chromium.launch()
            except Exception as e:  # noqa: BLE001
                self.skipTest(f"Chromium not available: {e}")
            pg = b.new_page(viewport={"width": 1280, "height": 860})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(self.base + "/")
            pg.wait_for_selector(".welcome")
            self.assertIn("◇", pg.inner_text(".brand"))
            # 1 shopping: cards and quick replies
            pg.fill("#input", "formal watch under 15000")
            pg.keyboard.press("Enter")
            pg.wait_for_selector(".msg.bot .meta button", timeout=30000)
            self.assertGreaterEqual(pg.locator(".card").count(), 1)
            self.assertNotIn("Veyra", pg.inner_text("body"))
            # drawers
            pg.click("#tab-stages")
            pg.wait_for_selector(".wf")
            pg.click("#dtab-tools")
            pg.wait_for_selector(".call")
            pg.click("#drawer-close")
            # 2 store question
            pg.fill("#input", "Do you offer gift wrapping?")
            pg.keyboard.press("Enter")
            pg.wait_for_function("document.querySelectorAll('.msg.bot .meta button').length >= 4", timeout=30000)
            # 3 another brand: the entity check's fixed reply
            pg.fill("#input", "Do you sell Fossil watches?")
            pg.keyboard.press("Enter")
            pg.wait_for_function("document.querySelectorAll('.msg.bot .meta button').length >= 6", timeout=30000)
            self.assertNotIn("Veyra", pg.inner_text("body"))
            # custom pipeline: switches and the untested label
            pg.click("#chip-pipeline")
            pg.click("#menu-pipeline button:has-text('Custom')")
            pg.wait_for_selector("#custom-panel .toggle")
            pg.uncheck("#tg-retrieval")
            pg.wait_for_selector("#untested", state="visible")
            # compare
            pg.click("#chip-compare")
            pg.wait_for_selector(".compare .col-label:not(:empty)")
            pg.fill("#input", "Do you offer gift wrapping?")
            pg.keyboard.press("Enter")
            pg.wait_for_function("document.querySelectorAll('.compare .msg.bot .meta button').length >= 4",
                                 timeout=60000)
            self.assertTrue(pg.is_visible("#strip"))
            # the mic is shown but disabled
            self.assertTrue(pg.is_disabled(".mic"))
            self.assertEqual(errors, [])
            b.close()


class KioskBrowserTests(AppTests):
    mode = "kiosk"

    def test_kiosk_mode_in_the_browser(self):
        """Scenario 6: Kiosk mode shows only the chat, with the brand placeholder, and answers."""
        self.svc.prepare()
        with sync_playwright() as p:
            try:
                b = p.chromium.launch()
            except Exception as e:  # noqa: BLE001
                self.skipTest(f"Chromium not available: {e}")
            pg = b.new_page(viewport={"width": 1080, "height": 1600})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(self.base + "/")
            pg.wait_for_selector(".welcome")
            self.assertFalse(pg.is_visible(".picker"))
            self.assertFalse(pg.is_visible(".sidebar"))
            self.assertFalse(pg.is_visible(".drawer-tabs"))
            pg.wait_for_function("!document.querySelector('#input').disabled")
            pg.fill("#input", "Formal watch for my father under 15000")
            pg.keyboard.press("Enter")
            pg.wait_for_selector(".card", timeout=30000)
            pg.fill("#input", "Do you offer gift wrapping?")
            pg.keyboard.press("Enter")
            pg.wait_for_function("document.querySelectorAll('.msg.bot').length >= 2", timeout=30000)
            self.assertNotIn("Veyra", pg.inner_text("body"))
            self.assertIn("◇", pg.inner_text(".brand"))
            self.assertEqual(errors, [])
            b.close()


class CompareCheckTests(AppTests):
    def test_compare_columns_equal_single_runs(self):
        from app import compare_check
        out = os.path.join(self.tmp, "cmp6")
        self.assertEqual(compare_check.main(["--app", self.base, "--pairs", "P1,P2", "--out", out]), 0)
        r = json.load(open(os.path.join(out, "report.json"), encoding="utf-8"))
        self.assertEqual((r["columns"], r["identical"]), (40, 40))


class AccessibilityTests(unittest.TestCase):
    def test_scan_has_no_serious_issue(self):
        try:
            from playwright.sync_api import sync_playwright as _sp  # noqa: F401
        except ImportError:
            self.skipTest("Playwright not installed")
        from app import a11y_check
        self.assertEqual(a11y_check.main(["--no-axe"]), 0)


if __name__ == "__main__":
    unittest.main()
