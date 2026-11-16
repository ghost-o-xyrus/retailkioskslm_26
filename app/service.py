"""
Objective 5, Step 4: the kiosk service behind the HTTP API. Sessions, configurations, one turn at a time, events,
product cards, the brand placeholder, traces and logs.

Turns run one at a time (one model is resident; compare mode runs its two configurations one after the other).
Every event and every response passes through brand(): the fictional brand name is shown as a placeholder (the
design rule from Step 1); records and logs keep the data unchanged.
"""

import collections
import datetime
import json
import os
import re
import sys
import threading
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from kiosk_core import engine as E  # noqa: E402
from kiosk_core.turn import Engine, Session, run_turn  # noqa: E402
from app.config import TIERS  # noqa: E402

BRAND_WORD = re.compile(r"\bveyra\b", re.I)
CODE_RE = re.compile(r"\b(\d{4}[A-Z]{2}\d{2})\b")
MAX_ENGINES, MAX_TRACES = 4, 500
IDLE_RESET_S = 120


def brand(obj, mark):
    """The brand placeholder in every string of an event or response."""
    if isinstance(obj, str):
        return BRAND_WORD.sub(mark, obj)
    if isinstance(obj, list):
        return [brand(x, mark) for x in obj]
    if isinstance(obj, dict):
        return {k: brand(v, mark) for k, v in obj.items()}
    return obj


def _products_in(result):
    if not isinstance(result, dict):
        return []
    out = []
    for key in ("results", "alternatives", "comparison"):
        for x in result.get(key) or []:
            if isinstance(x, dict) and x.get("product_id"):
                out.append(x)
    if result.get("product_id") and result.get("name"):
        out.append(result)
    return out


def cards_for(rec):
    """Products the reply names that this turn's tools returned or showed (design doc, 'How images reach the chat').
    A product is named by its code or by its design name."""
    from tools import mock_tools
    from kiosk_core import media
    reply = (rec.get("final_reply") or "")
    low = reply.lower()
    db = mock_tools._load()
    seen, cards = set(), []
    stock = {}
    for c in rec.get("tool_calls") or []:
        if c.get("name") == "check_inventory":
            for x in (c.get("result") or {}).get("results") or []:
                stock[x.get("product_id")] = x.get("in_stock")
    found = []
    for c in rec.get("tool_calls") or []:
        found += _products_in(c.get("result"))
    for code in CODE_RE.findall(reply):          # a code the reply names, even if a card showed it, not a tool
        if code in db["skus"] and code not in {p["product_id"] for p in found}:
            sku = db["skus"][code]
            found.append({"product_id": code, "name": sku["product_name"], "mrp": sku["mrp"]})
    for p in found:
        pid = p["product_id"]
        if pid in seen or pid not in db["skus"]:
            continue
        sku = db["skus"][pid]
        style = db["styles"].get(sku["style_id"], {})
        named = pid.lower() in low or (style.get("style_name") and style["style_name"].lower() in low)
        if not named:
            continue
        seen.add(pid)
        cards.append({"product_id": pid, "style_id": sku["style_id"], "name": sku["product_name"],
                      "design": style.get("style_name"), "mrp": sku["mrp"], "dial_colour": sku.get("dial_colour"),
                      "strap": f"{sku.get('strap_colour', '')} {sku.get('strap_material', '')}".strip(),
                      "in_stock_here": stock.get(pid, p.get("in_stock_here")),
                      "image": media.url(media.lookup(pid, "front")),
                      "image_alt": (media.lookup(pid, "front") or {}).get("alt"),
                      "images": p.get("images")})   # an image request: every view, the asked one first
        if p.get("images"):
            cards[-1]["image"], cards[-1]["image_alt"] = p["images"][0]["url"], p["images"][0]["alt"]
    return cards[:6]


class KioskService:
    def __init__(self, registry, model_server, mode="lab", kiosk_tier="A", brand_mark="◇ ◇ ◇",
                 log_dir=None):
        self.reg, self.ms, self.mode, self.kiosk_tier, self.mark = registry, model_server, mode, kiosk_tier, brand_mark
        self.log_dir = log_dir or os.path.join(ROOT, "logs", "app")
        self.sessions, self.compares = collections.OrderedDict(), {}
        self.traces = collections.OrderedDict()
        self.engines = collections.OrderedDict()
        self.turn_lock = threading.Lock()
        self.last = {}
        self.readiness = {"state": "idle", "text": ""}
        self.stream = True
        self.stage_policy = "resident"        # Step 4: streamed and plain replies were identical on every dev tool case
        self._closing = False

    # ---- sessions ----
    def _selection(self, sel):
        if self.mode == "kiosk" or not sel:
            return self.reg.default_selection(self.kiosk_tier)
        return sel

    def create_session(self, selection=None, title=None):
        sel = self._selection(selection)
        cfg, server, sel, untested = self.reg.resolve(sel)       # fails early on an impossible selection
        sid = uuid.uuid4().hex[:10]
        self.sessions[sid] = {"id": sid, "title": title or "New chat", "selection": sel, "label": cfg["config_label"],
                              "untested": untested, "session": Session(sid), "turns": [],
                              "created": time.time(), "last_active": time.time()}
        return self.public_session(sid)

    def set_selection(self, sid, selection):
        if self.mode == "kiosk":
            raise PermissionError("the configuration is fixed in Kiosk mode")
        s = self.sessions[sid]
        cfg, server, sel, untested = self.reg.resolve(selection)
        s.update(selection=sel, label=cfg["config_label"], untested=untested)
        return self.public_session(sid)

    def create_compare(self, sel_a, sel_b):
        if self.mode == "kiosk":
            raise PermissionError("compare mode is not available in Kiosk mode")
        a = self.create_session(sel_a, title="Compare A")
        b = self.create_session(sel_b, title="Compare B")
        cid = uuid.uuid4().hex[:10]
        self.compares[cid] = {"id": cid, "a": a["id"], "b": b["id"]}
        return {"id": cid, "a": a, "b": b}

    def public_session(self, sid):
        s = self.sessions[sid]
        return brand({"id": sid, "title": s["title"], "selection": s["selection"], "label": s["label"],
                      "untested": s["untested"], "turns": s["turns"]}, self.mark)

    def list_sessions(self):
        return [brand({"id": s["id"], "title": s["title"], "label": s["label"], "n_turns": len(s["turns"])}, self.mark)
                for s in reversed(self.sessions.values()) if not s["title"].startswith("Compare ") and s["turns"]]

    def reset_idle(self):
        """Kiosk mode: a conversation with no input for IDLE_RESET_S is cleared."""
        now = time.time()
        for sid, s in list(self.sessions.items()):
            if now - s["last_active"] > IDLE_RESET_S and s["turns"]:
                s["session"], s["turns"] = Session(sid), []

    # ---- engines ----
    def _engine(self, cfg, emit):
        if self.stage_policy != "resident":
            cfg = dict(cfg, stage_policy=self.stage_policy)    # Step 8: the retrieval models in a worker
        key = json.dumps(cfg, sort_keys=True) + f"|{self.ms.pid()}"
        if key in self.engines:
            self.engines.move_to_end(key)
            return self.engines[key]
        emit({"type": "status", "text": "Getting ready…"})
        eng = Engine.from_plan_run(cfg, base_url=self.ms.url, server_pid=self.ms.pid(),
                                   results_dir=os.path.join(ROOT, "results_obj5", "_app"))
        self.engines[key] = eng
        while len(self.engines) > MAX_ENGINES:
            _, old = self.engines.popitem(last=False)
            old.close()
        return eng

    def _drop_engines(self):
        for e in self.engines.values():
            e.close()
        self.engines.clear()

    # ---- loading (start-up and every turn) ----
    def _ready(self, cfg, server, out):
        """Model server up with this setup, engine built, prompt cached, retrieval models loaded. Called with the
        turn lock held; costs nothing when everything is already loaded."""
        if not self.ms.alive() or self.ms._key(server) != self.ms._key(self.ms.spec or {}):
            out({"type": "status", "text": "Loading the model…", "model": os.path.basename(server["model"] or "")
                 if not server.get("fake") else "stand-in"})
            info = self.ms.ensure(server)
            if info.get("started"):
                self._drop_engines()
                out({"type": "model_loaded", "load_ms": info["load_ms"]})
        eng = self._engine(cfg, out)
        E.REQUEST_EXTRA.clear()
        if server.get("loras"):
            E.REQUEST_EXTRA["lora"] = [{"id": i, "scale": 1.0 if i == server.get("lora_index") else 0.0}
                                       for i in range(len(server["loras"]))]
        if not getattr(eng, "warmed", False):
            out({"type": "status", "text": "Warming up…"})
            try:
                eng.warmed_ms = eng.warmup()
            except Exception as e:  # noqa: BLE001 - a failed warm-up only costs speed
                eng.warmed_ms = None
                out({"type": "status", "text": f"Warm-up failed ({e}); continuing"})
            if eng.kb is not None:                 # the first query loads and compiles the retrieval models
                try:
                    eng.kb.retrieve("warm up")
                except Exception:  # noqa: BLE001
                    pass
            eng.warmed = True
        return eng

    def prepare(self, selection=None):
        """Load and warm a setup (default: the deployed one for this mode and tier) before any customer arrives.
        A turn that comes in meanwhile waits on the turn lock, then runs at full speed."""
        sel = self._selection(selection)
        self.readiness = {"state": "loading", "text": "Getting ready…", "since": time.time()}
        t = time.time()
        try:
            cfg, server, sel, _ = self.reg.resolve(sel)
            with self.turn_lock:
                self._ready(cfg, server, lambda ev: ev.get("text") and self.readiness.update(text=ev["text"]))
            self.readiness = {"state": "ready", "text": "", "load_s": round(time.time() - t, 1),
                              "label": cfg["config_label"]}
        except Exception as e:  # noqa: BLE001 - shown on screen; the first turn tries again
            self.readiness = {"state": "error", "text": f"The kiosk could not load its model: {e}"}
        return self.readiness

    def keep_loaded(self, every_s=30):
        """Kiosk mode: if llama-server stops (crash, killed), load and warm it again without waiting for a
        customer."""
        def loop():
            while not self._closing:
                time.sleep(every_s)
                if self._closing:
                    break
                if self.readiness.get("state") != "loading" and not self.ms.alive():
                    self._drop_engines()
                    self.prepare()
        threading.Thread(target=loop, daemon=True).start()

    # ---- one turn ----
    def run(self, sid, message, emit, side=None):
        """Run one turn; every event goes to emit (already with the brand placeholder)."""
        s = self.sessions[sid]

        def out(ev):
            if side:
                ev = dict(ev, side=side)
            emit(brand(ev, self.mark))

        cfg, server, sel, _ = self.reg.resolve(s["selection"])
        t_wait = time.time()
        with self.turn_lock:
            waited = round((time.time() - t_wait) * 1000)
            eng = self._ready(cfg, server, out)
            E.REQUEST_EXTRA.clear()
            if server.get("loras"):
                E.REQUEST_EXTRA["lora"] = [{"id": i, "scale": 1.0 if i == server.get("lora_index") else 0.0}
                                           for i in range(len(server["loras"]))]
            status_for = {"route": "Reading your question…", "retrieval": "Looking up the store information…",
                          "harness_tools": "Checking the catalogue…", "model_round": "Writing a reply…",
                          "model_tools": "Checking the catalogue…", "checks": "Checking the reply…"}

            def on_event(ev):
                if ev.get("type") == "stage_start" and ev.get("stage") in status_for:
                    out({"type": "status", "text": status_for[ev["stage"]]})
                out(ev)

            try:
                rec = run_turn(s["session"], message, eng, emit=on_event, stream=self.stream)
            except Exception as e:  # noqa: BLE001 - the customer gets a plain message
                out({"type": "error", "message": f"Sorry, something went wrong. A staff member can help. ({e})"})
                if s["session"].messages and s["session"].messages[-1]["role"] == "user":
                    s["session"].messages.pop()
                return None
            finally:
                E.REQUEST_EXTRA.clear()
            rec["queue_ms"] = waited
            rec["selection"] = sel
            cards = cards_for(rec)
            rec["cards"] = cards
            tid = f"{sid}-{rec['turn']}"
            rec["turn_id"] = tid
            self.traces[tid] = rec
            while len(self.traces) > MAX_TRACES:
                self.traces.popitem(last=False)
            s["turns"].append({"turn_id": tid, "user": message, "reply": rec.get("final_reply"), "cards": cards,
                               "flags": rec.get("flags"), "metrics": rec.get("metrics"), "label": s["label"]})
            s["last_active"] = time.time()
            if s["title"] == "New chat":
                s["title"] = message[:40]
            self._log(sid, rec)
            self.last = {"turn_id": tid, "peak_mb": [x.get("peak_mb") for x in rec.get("stages") or []]}
            out({"type": "cards", "cards": cards})
            out({"type": "turn_end", "turn_id": tid, "label": s["label"]})
            return rec

    def run_compare(self, cid, message, emit):
        c = self.compares[cid]
        self.run(c["a"], message, emit, side="a")
        self.run(c["b"], message, emit, side="b")

    def _log(self, sid, rec):
        d = os.path.join(self.log_dir, datetime.date.today().isoformat())
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"{sid}.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")

    # ---- inspection ----
    def trace(self, tid):
        return brand(self.traces[tid], self.mark)

    def stages_status(self):
        try:
            import psutil
            app_mb = round(psutil.Process().memory_info().rss / 2**20, 1)
            workers = [round(c.memory_info().rss / 2**20, 1) for c in psutil.Process().children()
                       if "fake_server" not in " ".join(c.cmdline()) and "llama-server" not in c.name()]
        except Exception:  # noqa: BLE001
            app_mb, workers = None, []
        return brand({"model_server": self.ms.status(), "app_rss_mb": app_mb, "workers_rss_mb": workers,
                      "engines": [json.loads(k.rsplit("|", 1)[0]).get("config_label") for k in self.engines],
                      "stage_policy": next((e.args.stage_policy for e in self.engines.values()), "resident"),
                      "tiers": {k: v["ram_budget_gb"] for k, v in TIERS.items()},
                      "last_turn": self.last}, self.mark)

    def close(self):
        self._closing = True
        self._drop_engines()
        self.ms.stop()
