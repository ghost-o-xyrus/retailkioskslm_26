"""
Objective 5, Step 4: the kiosk app's backend. Python standard library only (no web framework to install, so the
kiosk runs offline with the project's existing environment); localhost only.

    python app\\server.py                       # Lab mode, Tier A, real models (llama-server started by the app)
    python app\\server.py --mode kiosk --tier B # Kiosk mode: one fixed deployed configuration
    python app\\server.py --fake                # the stand-in model and retrieval: the whole app without a model
    then open http://127.0.0.1:8000

API (design doc, "Backend architecture"):
    GET  /api/configs                     tiers, models, pipelines, toggles, evidence notes, the default
    GET  /api/sessions                    conversations (sidebar)
    POST /api/sessions                    {"selection": {...}} -> a new conversation
    GET  /api/sessions/{id}               its turns
    POST /api/sessions/{id}/config        {"selection": {...}} (Lab only)
    POST /api/sessions/{id}/turns         {"message": "..."} -> server-sent events (stage, tool_call, status, final,
                                          metrics, cards, turn_end, error)
    POST /api/compare                     {"a": {...}, "b": {...}} -> two conversations (Lab only)
    POST /api/compare/{id}/turns          {"message": "..."} -> events for side "a", then side "b"
    GET  /api/turns/{turn_id}/trace       the full turn record
    GET  /api/stages/status               the model server, resident engines, memory
    POST /api/voice/transcribe, GET /api/voice/speak   501 (voice is planned)
    GET  /media/{asset}                   404 until Step 7 (product images)
"""

import argparse
import json
import mimetypes
import os
import re
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app.config import Registry  # noqa: E402
from app.model_server import ModelServer  # noqa: E402
from app.service import KioskService  # noqa: E402

STATIC = os.path.join(HERE, "static")
SERVICE = {}


class Handler(BaseHTTPRequestHandler):
    server_version = "KioskApp/0.1"

    def log_message(self, fmt, *args):            # quiet; errors still print
        if os.environ.get("KIOSK_HTTP_LOG"):
            super().log_message(fmt, *args)

    # ---- helpers ----
    def _json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def _sse(self, run):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        gone = [False]

        def emit(ev):
            if gone[0]:
                return
            try:
                self.wfile.write(("data: " + json.dumps(ev, ensure_ascii=False, default=str) + "\n\n").encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, OSError):
                gone[0] = True               # the browser left; the turn still finishes and is logged

        try:
            run(emit)
        except Exception as e:  # noqa: BLE001
            emit({"type": "error", "message": f"Sorry, something went wrong. ({e})"})
        emit({"type": "done"})

    def _media(self, name):
        """Step 7: a product image from the media table's folder (names only; no paths)."""
        from kiosk_core import media
        if not re.fullmatch(r"[\w.-]+\.(svg|png|jpe?g|webp)", name or ""):
            return self._json(404, {"error": "not found"})
        full = os.path.join(media.media_dir(), name)
        if not os.path.exists(full):
            return self._json(404, {"error": "not found"})
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml" if name.endswith(".svg") else
                         (mimetypes.guess_type(name)[0] or "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "max-age=86400")
        self.end_headers()
        self.wfile.write(data)

    def _static(self, path):
        rel = "index.html" if path in ("/", "") else path.lstrip("/").removeprefix("static/")
        full = os.path.normpath(os.path.join(STATIC, rel))
        if not full.startswith(STATIC) or not os.path.isfile(full):
            return self._json(404, {"error": "not found"})
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", (mimetypes.guess_type(full)[0] or "application/octet-stream")
                         + ("; charset=utf-8" if full.endswith((".html", ".js", ".css")) else ""))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    # ---- routes ----
    def do_GET(self):
        svc = SERVICE["svc"]
        p = self.path.split("?", 1)[0]
        try:
            if p == "/api/configs":
                d = svc.reg.describe(svc.mode, svc.kiosk_tier)
                d["brand"] = svc.mark
                return self._json(200, d)
            if p == "/api/sessions":
                return self._json(200, svc.list_sessions())
            m = re.fullmatch(r"/api/sessions/(\w+)", p)
            if m:
                return self._json(200, svc.public_session(m.group(1)))
            m = re.fullmatch(r"/api/turns/([\w-]+)/trace", p)
            if m:
                return self._json(200, svc.trace(m.group(1)))
            if p == "/api/ready":
                return self._json(200, svc.readiness)
            if p == "/api/stages/status":
                return self._json(200, svc.stages_status())
            if p == "/api/voice/speak":
                return self._json(501, {"error": "voice is planned, not built (design doc, Voice)"})
            if p.startswith("/media/"):
                return self._media(p[len("/media/"):])
            if p.startswith("/api/"):
                return self._json(404, {"error": "unknown endpoint"})
            return self._static(p)
        except KeyError:
            return self._json(404, {"error": "not found"})

    def do_POST(self):
        svc = SERVICE["svc"]
        p = self.path.split("?", 1)[0]
        body = self._body()
        try:
            if p == "/api/sessions":
                return self._json(200, svc.create_session(body.get("selection")))
            m = re.fullmatch(r"/api/sessions/(\w+)/config", p)
            if m:
                return self._json(200, svc.set_selection(m.group(1), body.get("selection") or {}))
            m = re.fullmatch(r"/api/sessions/(\w+)/turns", p)
            if m:
                sid, msg = m.group(1), (body.get("message") or "").strip()
                if sid not in svc.sessions:
                    return self._json(404, {"error": "no such conversation"})
                if not msg:
                    return self._json(400, {"error": "empty message"})
                return self._sse(lambda emit: svc.run(sid, msg, emit))
            if p == "/api/compare":
                return self._json(200, svc.create_compare(body.get("a") or {}, body.get("b") or {}))
            m = re.fullmatch(r"/api/compare/(\w+)/turns", p)
            if m:
                cid, msg = m.group(1), (body.get("message") or "").strip()
                if cid not in svc.compares:
                    return self._json(404, {"error": "no such comparison"})
                if not msg:
                    return self._json(400, {"error": "empty message"})
                return self._sse(lambda emit: svc.run_compare(cid, msg, emit))
            if p == "/api/lab/next_ticket":             # Step 6 check only: the next staff ticket number
                if svc.mode != "lab":
                    return self._json(403, {"error": "Lab mode only"})
                from tools import mock_tools
                n = int(body.get("next") or 1)
                mock_tools._TICKET[0] = max(0, n - 1)
                return self._json(200, {"next": n})
            if p == "/api/voice/transcribe":
                return self._json(501, {"error": "voice is planned, not built (design doc, Voice)"})
            return self._json(404, {"error": "unknown endpoint"})
        except PermissionError as e:
            return self._json(403, {"error": str(e)})
        except (ValueError, FileNotFoundError) as e:
            return self._json(400, {"error": str(e)})
        except KeyError:
            return self._json(404, {"error": "not found"})


def make_service(mode="lab", tier="A", fake=False, base_dir=None, llama_port=8080, log_dir=None):
    reg = Registry(base_dir=base_dir, fake=fake)
    ms = ModelServer(port=llama_port, log_dir=os.path.join(log_dir, "server") if log_dir else None)
    return KioskService(reg, ms, mode=mode, kiosk_tier=tier, log_dir=os.path.join(log_dir, "app") if log_dir else None)


def serve(svc, host="127.0.0.1", port=8000):
    SERVICE["svc"] = svc
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.daemon_threads = True
    if svc.mode == "kiosk":
        def idle():
            while True:
                time.sleep(30)
                svc.reset_idle()
        threading.Thread(target=idle, daemon=True).start()
    return httpd


def main(argv=None):
    ap = argparse.ArgumentParser(description="The kiosk app (Objective 5).")
    ap.add_argument("--mode", default="lab", choices=["lab", "kiosk"])
    ap.add_argument("--tier", default="A", choices=["A", "B"], help="the kiosk's tier (Kiosk mode; Lab default)")
    ap.add_argument("--fake", action="store_true", help="stand-in model server and retrieval (no model needed)")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--llama-port", type=int, default=8080)
    ap.add_argument("--base-dir", default=None, help="folder with llama-cpu/, llama-vulkan/, models/ (default: plans)")
    ap.add_argument("--open", action="store_true", help="open the browser")
    ap.add_argument("--no-stream", action="store_true", help="show each reply only when it is complete")
    ap.add_argument("--stage-policy", default="resident", choices=["resident", "sequential"],
                    help="resident: everything loaded; sequential: retrieval models in a worker stopped before the model")
    ap.add_argument("--no-preload", action="store_true",
                    help="do not load and warm the model at start-up (it then loads on the first message)")
    ap.add_argument("--offline", action="store_true",
                    help="Step 10: refuse (and log) any connection that leaves this machine (kiosk_core/offline.py)")
    ap.add_argument("--net-log", default=os.path.join(ROOT, "logs", "offline_guard.jsonl"),
                    help="with --offline: where refused attempts are written")
    ap.add_argument("--log-dir", default=None,
                    help="folder for this instance's logs (app/ and server/ inside it; default: logs/). Give each "
                         "instance its own when several run side by side")
    a = ap.parse_args(argv)
    if a.offline:
        from kiosk_core import offline
        offline.install(a.net_log)
        print(f"Offline: only this machine can be reached; any other attempt is refused and logged to {a.net_log}")
    svc = make_service(a.mode, a.tier, a.fake, a.base_dir, a.llama_port, log_dir=a.log_dir)
    svc.stream = not a.no_stream
    svc.stage_policy = a.stage_policy
    httpd = serve(svc, port=a.port)
    if not a.no_preload:
        print("Loading and warming the model; the page shows 'Getting ready' until it is done…")
        threading.Thread(target=lambda: print(f"Ready: {svc.prepare()}", flush=True), daemon=True).start()
        if a.mode == "kiosk":
            svc.keep_loaded()
    url = f"http://127.0.0.1:{a.port}"
    print(f"Kiosk app ({a.mode} mode, Tier {a.tier}{', stand-in model' if a.fake else ''}) at {url}  (Ctrl+C stops)")
    if a.open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        svc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
