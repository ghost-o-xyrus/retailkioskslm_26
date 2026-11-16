"""
Objective 5, Step 9: the walkthrough. The six design scenarios (design doc, "Key scenarios"), on one tier, through
the app's own API, with every trace kept.

    python app\\walkthrough.py --tier A          # about 10 minutes
    python app\\walkthrough.py --tier B
    python app\\walkthrough.py --report          # the summary of both tiers

Stop any running app and llama-server first; this script starts and stops its own. It starts the app in Kiosk mode
(the tier's Deployed setup, loaded at start-up) for scenarios 1, 2, 3, 4 and 6, then in Lab mode for scenario 5
(compare is a Lab feature by design).

Scenarios and pass rules (fixed before the run):
  K  Kiosk lock     /api/configs says kiosk; changing the setup and opening compare are refused (403).
  1  Shopping       "I need a gift for my father, around 15k". At most two slot questions (each answered with a
                    scripted reply), then 1-3 product cards, each with code, name, price and image, each from this
                    turn's catalogue results. Then "Is the second one in stock here?": check_inventory on the
                    second watch the reply named, and the reply agrees with the tool's in-stock answer.
  2  Store question "What does the warranty cover?" (fresh chat): the retrieval stage ran, and the reply is either
                    the fixed decline, or passed the answer check (or, with the check off, shares most of its
                    content words with the retrieved text).
  3  Hinglish       After "Tell me about 1024SL01" (brown strap; the design has a black-strap variant, 1024SL03):
                    "Kya ye black strap mein milta hai?" The reply is Hinglish, and right: it names 1024SL03, or says
                    black is available without a negation. It never names a code from another design.
  4  Images         Same chat: "Show me the back of it". show_product_images on a Meridian Atlas variant, the back
                    view first, every picture of that one SKU; or a reply that says there is no picture.
  5  Compare (Lab)  "What colour is the strap on 1003SM02?" to O3-final and to Model only (true: rose gold metal).
                    Both columns end with a reply and a full stage list (stages cover the turn). O3-final names
                    rose gold, or declines / offers staff. The bare model's answer is recorded (the design expects
                    an invented colour; that is a finding, not a pass condition).
  6  Hand-off       Same chat as 3-4: "Can someone help me try it on?" call_staff (try_on) returns a ticket, the
                    reply tells the customer someone is coming, and the ticket is in the staff log.
Every turn also: no error event, a non-empty reply, the stages cover the turn, the brand name never reaches the
client.

Step 10 (--offline, run from the kiosk package; results_obj5/_walkthrough_step10/): the Kiosk app is started by
the kiosk launcher (as start_kiosk.bat does) and every app process refuses and logs connections that leave the
machine. Added:
  R1 llama-server   killed; the app's watchdog loads it again: ready and answering within 2 x load time + 60 s
  R2 App            killed; the launcher starts it again: ready and answering within the same limit
  N  Network        no connection attempt left the machine (the offline guard logs of both modes are empty)
  P  Same replies   the replies of scenarios 1-5 equal this project's Step 9 run (the package copies it)

    python app\\walkthrough.py --tier A --only 3     # rerun one scenario (3, 4 and 6 share one chat)

Writes results_obj5/_walkthrough_step9/<tier>/S<n>.json (full traces), <tier>.json, and report.md.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
from smoke_real import BRAND, check_turn, get, post, turn  # noqa: E402
from measure import stop_app  # noqa: E402

OUT = os.path.join(ROOT, "results_obj5", "_walkthrough_step9")
CODE_RE = re.compile(r"\b(\d{4}[A-Z]{2}\d{2})\b")
NEG = re.compile(r"(?<![a-z])(not|no|isn't|isnt|aren't|unavailable|out of stock|sold out|nahi|nahin|nahi hai|"
                 r"don't|doesn't|only)(?![a-z])")
STAFF_WORDS = re.compile(r"(?<![a-z])(staff|team member|colleague|someone|somebody|associate|assistant|"
                         r"on (the|their|his|her) way|coming|will be with you|aa rahe|aayenge)(?![a-z])")
DECLINE = re.compile(r"(?<![a-z])(i don't have|i do not have|don't have that|not sure|can't confirm|cannot confirm|"
                     r"staff member|call (a )?staff|nahi pata|maaf)(?![a-z])")
SLOT_ANSWERS = ["Formal, for the office.", "Just show me a few."]


# ---- the app --------------------------------------------------------------------------------------------------
def start(mode, tier, port, llama_port, base_dir, fake, staff_log, offline=False, net_log=None):
    """The app in Lab or Kiosk mode. Offline (Step 10): Kiosk mode goes through the kiosk launcher, as the start
    scripts do (so it is offline and restarted if it stops); Lab mode runs the server with the offline guard."""
    if offline and mode == "kiosk":
        cmd = [sys.executable, os.path.join(HERE, "kiosk_launcher.py"), "--tier", tier, "--port", str(port),
               "--llama-port", str(llama_port), "--no-browser"]
    else:
        cmd = [sys.executable, os.path.join(HERE, "server.py"), "--mode", mode, "--tier", tier, "--port", str(port),
               "--llama-port", str(llama_port)]
        if offline:
            cmd += ["--offline", "--net-log", net_log]
    cmd += (["--fake"] if fake else []) + (["--base-dir", base_dir] if base_dir else [])
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, f"app_{tier}_{mode}.log"), "a", encoding="utf-8")
    env = dict(os.environ, SLM_STAFF_LOG=staff_log)
    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
    base = f"http://127.0.0.1:{port}"
    r = wait_ready(base, proc, 900)
    if r.get("state") != "ready":
        stop_app(proc)
        sys.exit(r.get("text") or f"the app did not become ready; see {log.name}")
    return proc, base, r


def wait_ready(base, proc=None, limit=900, want="ready"):
    t = time.time()
    r = {}
    while time.time() - t < limit:
        if proc is not None and proc.poll() is not None:
            return {"state": "stopped", "text": "the app stopped"}
        try:
            r = get(base, "/api/ready")
            if r.get("state") == want or r.get("state") == "error":
                return dict(r, waited_s=round(time.time() - t, 1))
        except Exception:  # noqa: BLE001 - not up yet
            r = {"state": "down"}
        time.sleep(1)
    return dict(r, state=r.get("state") or "timeout", text=f"not {want} in {limit} s")


def say(base, sid, message):
    """One turn: the general checks, the trace, timings."""
    ev, first, total = turn(base, f"/api/sessions/{sid}/turns", message)
    r = check_turn(base, ev, first, total, {})
    tr = get(base, f"/api/turns/{r['turn_id']}/trace") if r.get("turn_id") else {}
    cards = next((e.get("cards") for e in ev if e.get("type") == "cards"), []) or []
    return {"message": message, "reply": r.get("reply") or "", "errors": r["errors"], "cards": cards,
            "first_word_s": round((r.get("first_word_ms") or 0) / 1000, 2), "total_s": round(total / 1000, 2),
            "stages": r.get("stages"), "trace": tr}


def calls(t, name=None):
    return [c for c in (t["trace"].get("tool_calls") or []) if name is None or c.get("name") == name]


def order_named(reply, cards):
    """Cards in the order the reply names them (by code, else by design name)."""
    low = reply.lower()

    def pos(c):
        ps = [low.find(c["product_id"].lower()), low.find((c.get("design") or "\0").lower())]
        ps = [p for p in ps if p >= 0]
        return min(ps) if ps else 10 ** 6
    return sorted(cards, key=pos)


# ---- the scenarios ------------------------------------------------------------------------------------------------
def s_lock(base):
    probs = []
    if get(base, "/api/configs").get("mode") != "kiosk":
        probs.append("not in Kiosk mode")
    s = post(base, "/api/sessions", {"selection": {"pipeline": "model_only"}})
    if s.get("selection", {}).get("pipeline") != "deployed":
        probs.append(f"a kiosk chat took pipeline {s.get('selection', {}).get('pipeline')}")
    for path, body in ((f"/api/sessions/{s['id']}/config", {"selection": {"pipeline": "model_only"}}),
                       ("/api/compare", {"a": {}, "b": {}})):
        try:
            post(base, path, body)
            probs.append(f"{path} was allowed")
        except Exception as e:  # noqa: BLE001 - urllib raises on 403
            if "403" not in str(e):
                probs.append(f"{path}: {e}")
    return {"label": s.get("label"), "turns": [], "problems": probs}


def s_shopping(base):
    from tools import mock_tools
    db = mock_tools._load()
    s = post(base, "/api/sessions", {})
    turns, probs = [say(base, s["id"], "I need a gift for my father, around 15k")], []
    asked = 0
    while not turns[-1]["cards"] and asked < 2 and not turns[-1]["errors"]:
        asked += 1                                        # a slot question: answer it
        turns.append(say(base, s["id"], SLOT_ANSWERS[asked - 1]))
    rec = turns[-1]
    cards = rec["cards"]
    found = set()
    for c in calls(rec):
        for k in ("results", "alternatives"):
            found |= {x.get("product_id") for x in (c.get("result") or {}).get(k) or [] if isinstance(x, dict)}
    if not cards:
        probs.append(f"no product cards after {asked} slot question(s)")
    if len(cards) > 3:
        probs.append(f"{len(cards)} cards (rule: 1-3)")
    for c in cards:
        miss = [k for k in ("product_id", "name", "mrp", "image") if not c.get(k)]
        if miss:
            probs.append(f"card {c.get('product_id')} lacks {', '.join(miss)}")
        if c["product_id"] not in found:
            probs.append(f"card {c['product_id']} is not from this turn's catalogue results")
    named = order_named(rec["reply"], cards)
    stock = {}
    if len(named) < 2:
        probs.append("fewer than two recommendations, so 'the second one' has no answer")
    else:
        second = named[1]["product_id"]
        t = say(base, s["id"], "Is the second one in stock here?")
        turns.append(t)
        inv = calls(t, "check_inventory")
        asked_for = [(c.get("arguments") or {}).get("product_id") for c in inv]
        stock = {"second": second, "checked": asked_for}
        if second not in asked_for:
            probs.append(f"check_inventory on {asked_for or 'nothing'}, expected {second}")
        else:
            res = next(c.get("result") or {} for c in inv if (c.get("arguments") or {}).get("product_id") == second)
            rows = [x for x in res.get("results") or [] if x.get("product_id") == second] or res.get("results") or []
            here = any(x.get("in_stock") for x in rows) if rows else res.get("in_stock")
            stock["in_stock"] = here
            neg = bool(NEG.search(t["reply"].lower()))
            if here is True and re.search(r"out of stock|not in stock|not available|isn't available|nahi hai", t["reply"].lower()):
                probs.append("the tool says in stock; the reply says not")
            if here is False and not neg:
                probs.append("the tool says not in stock; the reply does not say so")
    return {"turns": turns, "problems": probs, "slot_questions": asked, "n_cards": len(cards), "stock": stock}


def s_store(base):
    s = post(base, "/api/sessions", {})
    t = say(base, s["id"], "What does the warranty cover?")
    tr, probs = t["trace"], []
    if "retrieval" not in (t["stages"] or []):
        probs.append("no retrieval stage")
    v = tr.get("verify") or {}
    flags = tr.get("flags") or []
    declined = bool(DECLINE.search(t["reply"].lower())) or any(f.startswith("fallback_refus") for f in flags)
    how = "decline" if declined else None
    if not declined:
        if v:
            how = "answer check passed" if v.get("ok") else None
            if not v.get("ok"):
                probs.append(f"the answer check failed: {v.get('unsupported')}")
        else:
            words = {w for w in re.findall(r"[a-z]{4,}", t["reply"].lower())}
            text = json.dumps(tr.get("retrieval") or {}, ensure_ascii=False).lower() + " " + \
                json.dumps(tr.get("turns") or [], ensure_ascii=False).lower()
            share = sum(w in text for w in words) / max(1, len(words))
            how = f"{share:.0%} of content words in the retrieved text"
            if share < 0.5:
                probs.append(f"only {share:.0%} of the reply's content words are in the retrieved text")
    return {"turns": [t], "problems": probs, "how": how,
            "chunks": (tr.get("retrieval") or {}).get("chunk_ids")}


def s_focus_chat(base, staff_log):
    """Scenarios 3, 4 and 6 in one chat about the watch in focus."""
    from tools import mock_tools
    from kiosk_core import media
    from retrieval.language import is_hinglish
    db = mock_tools._load()
    s = post(base, "/api/sessions", {})
    t0 = say(base, s["id"], "Tell me about 1024SL01")
    # 3 Hinglish
    t3 = say(base, s["id"], "Kya ye black strap mein milta hai?")
    p3 = []
    low = t3["reply"].lower()
    if not is_hinglish(t3["reply"]):
        p3.append("the reply is not Hinglish")
    codes = set(CODE_RE.findall(t3["reply"]))
    other = [c for c in codes if db["skus"].get(c, {}).get("style_id") != "V1024"]
    if other:
        p3.append(f"names codes from other designs: {sorted(other)}")
    right = "1024SL03" in codes or ("black" in low and not NEG.search(low))
    if not right:
        p3.append("does not say the black-strap variant (1024SL03) exists")
    # 4 Images
    t4 = say(base, s["id"], "Show me the back of it")
    p4 = []
    img = t4["trace"].get("images") or {}
    shown = img.get("product_id")
    if shown:
        if db["skus"].get(shown, {}).get("style_id") != "V1024":
            p4.append(f"pictures of {shown}, not a Meridian Atlas")
        back = media.url(media.lookup(shown, "back"))
        urls = img.get("urls") or []
        if back and (not urls or urls[0] != back):
            p4.append(f"first picture {urls[:1]}, expected the back view {back}")
        if not back and not re.search(r"no picture|nahi hai|not available", t4["reply"].lower()):
            p4.append("no back view exists and the reply does not say so")
        mine = {media.url(media.lookup(shown, v)) for v in ("front", "side", "back")}
        stray = [u for u in urls if u not in mine]
        if stray:
            p4.append(f"pictures of another SKU: {stray}")
    else:
        p4.append("no pictures shown" + ("" if calls(t4, "show_product_images") else " and no image tool call"))
    # 6 Hand-off
    t6 = say(base, s["id"], "Can someone help me try it on?")
    p6, ticket = [], None
    st = calls(t6, "call_staff")
    if not st:
        p6.append("no call_staff")
    else:
        a = st[-1].get("arguments") or {}
        ticket = (st[-1].get("result") or {}).get("ticket")
        if a.get("reason") != "try_on":
            p6.append(f"reason {a.get('reason')}, expected try_on")
        if not ticket:
            p6.append(f"no ticket: {st[-1].get('result')}")
    if not STAFF_WORDS.search(t6["reply"].lower()):
        p6.append("the reply does not tell the customer someone is coming")
    logged = False
    if ticket and os.path.exists(staff_log):
        with open(staff_log, encoding="utf-8") as f:
            logged = any(json.loads(x).get("ticket") == ticket for x in f if x.strip())
    if ticket and not logged:
        p6.append(f"ticket {ticket} not in the staff log")
    return ({"turns": [t0, t3], "problems": p3},
            {"turns": [t4], "problems": p4, "images": img},
            {"turns": [t6], "problems": p6, "ticket": ticket, "ticket_in_reply": bool(ticket and ticket in t6["reply"]),
             "logged": logged})


def s_compare(base, tier):
    msg = "What colour is the strap on 1003SM02?"
    c = post(base, "/api/compare", {"a": {"tier": tier, "pipeline": "o3_final"},
                                    "b": {"tier": tier, "pipeline": "model_only"}})
    ev, first, total = turn(base, f"/api/compare/{c['id']}/turns", msg)
    probs, sides = [], {}
    if BRAND.lower() in json.dumps(ev, ensure_ascii=False).lower():
        probs.append("the brand name reached the client")
    for e in ev:
        if e.get("type") == "error":
            probs.append(f"error: {e.get('message')}")
    for e in ev:
        if e.get("type") != "turn_end":
            continue
        tr = get(base, f"/api/turns/{e['turn_id']}/trace")
        ss = tr.get("stage_summary") or {}
        tot = ss.get("covered_ms", 0) + (ss.get("unattributed_ms") or 0)
        sides[e["side"]] = {"label": e.get("label"), "reply": tr.get("final_reply") or "", "trace": tr,
                            "stages": [x.get("stage") for x in tr.get("stages") or []],
                            "by_stage_ms": ss.get("by_stage_ms"), "covered": not tot or
                            (ss.get("unattributed_ms") or 0) <= max(0.05 * tot, 5)}
    for k in ("a", "b"):
        if k not in sides:
            probs.append(f"column {k.upper()} did not finish")
            continue
        if not sides[k]["reply"].strip():
            probs.append(f"column {k.upper()}: empty reply")
        if not sides[k]["stages"] or not sides[k]["covered"]:
            probs.append(f"column {k.upper()}: stages missing or not covering the turn")
    if "a" in sides:
        low = sides["a"]["reply"].lower()
        if "rose gold" not in low and not DECLINE.search(low):
            probs.append("O3-final neither names rose gold nor declines")
    bare = None
    if "b" in sides:
        low = sides["b"]["reply"].lower()
        bare = "right (rose gold)" if "rose gold" in low else "declined" if DECLINE.search(low) else "invented"
    return {"message": msg, "total_s": round(total / 1000, 2), "sides": sides, "problems": probs, "bare_model": bare}


# ---- Step 10: restarts and the network --------------------------------------------------------------------------
def _children(pid):
    import psutil
    try:
        return psutil.Process(pid).children(recursive=True)
    except psutil.NoSuchProcess:
        return []


def _kill(procs):
    import psutil
    for p in procs:
        try:
            p.kill()
        except (psutil.NoSuchProcess, ProcessLookupError):
            pass
    psutil.wait_procs(procs, timeout=15)


def _answers(base):
    s = post(base, "/api/sessions", {})
    t = say(base, s["id"], "What does the warranty cover?")
    return t


def s_restart(base, launcher, what, limit):
    """R1: llama-server is killed; the app's watchdog loads it again. R2: the app is killed; the launcher starts it
    again. Either way the kiosk is ready again within the limit and answers a store question."""
    probs = []
    import psutil

    def info(p):
        try:
            return p.name().lower(), p.cmdline() or []
        except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError, ProcessLookupError):
            return "", []
    kids = [(p,) + info(p) for p in _children(launcher.pid)]
    if what == "llama":
        victims = [p for p, n, c in kids if "llama-server" in n or any("fake_server" in x for x in c)]
    else:
        victims = [p for p, n, c in kids if any(x.endswith("server.py") for x in c)]
        victims = victims[:1] + (_children(victims[0].pid) if victims else [])
    if not victims:
        return {"turns": [], "problems": [f"no {what} process found under the launcher"], "recover_s": None}
    names = [info(p)[0] or str(p.pid) for p in victims]
    t0 = time.time()
    _kill(victims)
    r = wait_ready(base, None, 120, want="loading") if what == "llama" else {"state": "down"}
    r = wait_ready(base, None, limit)
    rec = round(time.time() - t0, 1)
    if r.get("state") != "ready":
        probs.append(f"not ready again in {limit} s ({r.get('state')}: {r.get('text')})")
        return {"turns": [], "problems": probs, "recover_s": rec}
    t = _answers(base)
    if not t["reply"].strip():
        probs.append("no reply after the restart")
    return {"turns": [t], "problems": probs, "recover_s": rec, "killed": names}


def s_network(logs):
    seen = [x for lg in logs for x in offline_attempts(lg)]
    return {"turns": [], "problems": [f"{len(seen)} connection attempt(s) left the machine: "
                                      f"{sorted({x['target'] for x in seen})[:5]}"] if seen else [],
            "attempts": len(seen), "logs": logs}


def s_same(sc, ref):
    """P: the package gives the replies this project gave in Step 9 (same code, data and model; temperature 0).
    Scenarios 1-5; scenario 6 is left out (its ticket number depends on earlier staff calls)."""
    probs, n = [], 0
    for k in ("1", "2", "3", "4"):
        old = [t["reply"] for t in (ref["scenarios"].get(k) or {}).get("turns") or []]
        new = [t["reply"] for t in (sc.get(k) or {}).get("turns") or []]
        for i, (o, w) in enumerate(zip(old, new)):
            n += 1
            if o != w:
                probs.append(f"{k} turn {i + 1} differs: was {o[:80]!r}, now {w[:80]!r}")
        if len(old) != len(new):
            probs.append(f"{k}: {len(old)} turns in Step 9, {len(new)} now")
    for side in ("a", "b"):
        o = ((ref["scenarios"].get("5") or {}).get("sides") or {}).get(side, {}).get("reply")
        w = ((sc.get("5") or {}).get("sides") or {}).get(side, {}).get("reply")
        if o is not None and w is not None:
            n += 1
            if o != w:
                probs.append(f"5 column {side.upper()} differs: was {o[:80]!r}, now {w[:80]!r}")
    return {"turns": [], "problems": probs, "compared": n}


def offline_attempts(path):
    from kiosk_core import offline
    return offline.attempts(path)


# ---- run and report --------------------------------------------------------------------------------------------
KIOSK_KEYS = ("K", "1", "2", "3", "4", "6", "R1", "R2")


def run(a):
    od = os.path.join(OUT, a.tier)
    os.makedirs(od, exist_ok=True)
    staff_log = os.path.join(od, "staff_requests.log")
    if os.path.exists(staff_log):
        os.remove(staff_log)
    keys = list(KIOSK_KEYS if a.offline else KIOSK_KEYS[:-2]) + ["5"] + (["N"] if a.offline else [])
    if a.only:
        want = {x.strip().upper() for x in a.only.split(",") if x.strip()}
        if want & {"3", "4", "6"}:
            want |= {"3", "4", "6"}                  # one chat
        keys = [k for k in keys if k in want]
    net_logs = [os.path.join(ROOT, "logs", "kiosk", "offline_guard.jsonl"), os.path.join(od, "offline_guard_lab.jsonl")]
    if a.offline:
        for lg in net_logs:
            if os.path.exists(lg):
                os.remove(lg)
    res = {"tier": a.tier, "fake": a.fake, "offline": a.offline, "scenarios": {}}
    sc = res["scenarios"]
    if any(k in KIOSK_KEYS for k in keys):
        proc, base, ready = start("kiosk", a.tier, a.port, a.llama_port, a.base_dir, a.fake, staff_log, a.offline)
        res["kiosk_load_s"], res["label"] = ready.get("load_s"), ready.get("label")
        print(f"Tier {a.tier}, Kiosk mode ready in {ready.get('load_s')} s ({ready.get('label')})"
              + ("; offline, through the kiosk launcher" if a.offline else ""))
        try:
            if "K" in keys:
                sc["K"] = s_lock(base)
                report_line("K", TITLES["K"], sc["K"])
            if "1" in keys:
                sc["1"] = s_shopping(base)
                report_line("1", TITLES["1"], sc["1"])
            if "2" in keys:
                sc["2"] = s_store(base)
                report_line("2", TITLES["2"], sc["2"])
            if "3" in keys:
                sc["3"], sc["4"], sc["6"] = s_focus_chat(base, staff_log)
                for k in ("3", "4", "6"):
                    report_line(k, TITLES[k], sc[k])
            limit = int(2 * (ready.get("load_s") or 300) + 60)
            for k, what in (("R1", "llama"), ("R2", "app")):
                if k in keys:
                    sc[k] = s_restart(base, proc, what, limit)
                    sc[k]["limit_s"] = limit
                    report_line(k, TITLES[k], sc[k])
        finally:
            stop_app(proc)
    if "5" in keys:
        proc, base, ready = start("lab", a.tier, a.port, a.llama_port, a.base_dir, a.fake, staff_log, a.offline,
                                  net_logs[1])
        try:
            res["lab_load_s"] = ready.get("load_s")
            sc["5"] = s_compare(base, a.tier)
            report_line("5", TITLES["5"], sc["5"])
        finally:
            stop_app(proc)
    if "N" in keys:
        sc["N"] = s_network(net_logs)
        report_line("N", TITLES["N"], sc["N"])
    ref = os.path.join(ROOT, "results_obj5", "_walkthrough_step9", f"{a.tier}.json")
    if a.offline and not a.only and os.path.exists(ref):
        sc["P"] = s_same(sc, json.load(open(ref, encoding="utf-8")))
        report_line("P", TITLES["P"], sc["P"])
    prev_path = os.path.join(OUT, f"{a.tier}.json")
    prev = json.load(open(prev_path, encoding="utf-8")) if a.only and os.path.exists(prev_path) else None
    for k, v in sc.items():
        v["problems"] = v["problems"] + [f"turn {i + 1}: {e}" for i, t in enumerate(v.get("turns") or [])
                                         for e in t["errors"]]
        v["passed"] = not v["problems"]
        f_now = os.path.join(od, f"S{k}.json")
        if prev and os.path.exists(f_now):
            os.replace(f_now, os.path.join(od, f"S{k}_earlier.json"))
        with open(f_now, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=1, ensure_ascii=False, default=str)
    slim = json.loads(json.dumps(res, default=str))
    for v in slim["scenarios"].values():
        for t in v.get("turns") or []:
            t.pop("trace", None)
        for s in (v.get("sides") or {}).values():
            s.pop("trace", None)
    if prev:                                         # a rerun of some scenarios: keep the rest, note the earlier result
        earlier = prev.get("earlier", {})
        for k in slim["scenarios"]:
            if k in prev["scenarios"]:
                earlier.setdefault(k, []).append({"passed": prev["scenarios"][k]["passed"],
                                                  "problems": prev["scenarios"][k]["problems"]})
        merged = dict(prev, earlier=earlier)
        merged["scenarios"] = dict(prev["scenarios"], **slim["scenarios"])
        for key in ("kiosk_load_s", "lab_load_s", "label"):
            if slim.get(key) is not None:
                merged[key] = slim[key]
        slim = merged
    with open(prev_path, "w", encoding="utf-8") as f:
        json.dump(slim, f, indent=1, ensure_ascii=False)
    report()
    return 0 if all(v["passed"] for v in sc.values()) else 1


def report_line(k, title, v):
    errs = v["problems"] + [e for t in v.get("turns") or [] for e in t["errors"]]
    print(f"[{k}] {title}: {'PASS' if not errs else 'FAIL  ' + '; '.join(errs)}", flush=True)


TITLES = {"K": "Kiosk lock", "1": "Shopping", "2": "Store question", "3": "Hinglish", "4": "Images",
          "5": "Compare (Lab)", "6": "Hand-off", "R1": "llama-server restarted", "R2": "App restarted",
          "N": "No network use", "P": "Same replies as the project"}
ORDER = ("K", "1", "2", "3", "4", "5", "6", "R1", "R2", "N", "P")


def report():
    tiers = [t for t in ("A", "B") if os.path.exists(os.path.join(OUT, f"{t}.json"))]
    if not tiers:
        return
    data = {t: json.load(open(os.path.join(OUT, f"{t}.json"), encoding="utf-8")) for t in tiers}
    off = any(d.get("offline") for d in data.values())
    L = [f"# Objective 5, Step {10 if off else 9}: walkthrough of the design scenarios"
         + (" (offline, from the kiosk package)" if off else ""), "",
         "Kiosk mode (the tier's Deployed setup, loaded at start-up) for K, 1-4 and 6; Lab mode for 5. "
         + ("Offline: the Kiosk app is started by the kiosk launcher, as the start scripts do, and every app process "
            "refuses and logs any connection that leaves the machine (N). R1/R2: llama-server, then the app, are "
            "killed and must come back by themselves. " if off else "")
         + "Full traces: `<tier>/S<n>.json`. Rules: see `app/walkthrough.py`.", ""]
    L += ["| Scenario | " + " | ".join(f"Tier {t}" for t in tiers) + " |", "|---|" + "---|" * len(tiers)]
    for k in ORDER:
        if not any(k in data[t]["scenarios"] for t in tiers):
            continue
        L.append(f"| {k} {TITLES[k]} | " + " | ".join(
            ("pass" if data[t]["scenarios"][k]["passed"] else "**FAIL**") if k in data[t]["scenarios"] else "–"
            for t in tiers) + " |")
    for t in tiers:
        d = data[t]
        sc = d["scenarios"]
        n = sum(v["passed"] for v in sc.values())
        L += ["", f"## Tier {t}: {n}/{len(sc)} passed" + (" (stand-in model)" if d.get("fake") else ""), "",
              f"{d.get('label')}; Kiosk ready in {d.get('kiosk_load_s')} s, Lab in {d.get('lab_load_s')} s.", "",
              "| # | Customer | Kiosk (first 160 characters) | First word | Total | Cards |", "|---|---|---|---:|---:|---:|"]
        for k in ("1", "2", "3", "4", "6"):
            for tt in sc.get(k, {}).get("turns") or []:
                rep = tt["reply"].replace("\n", " ").replace("|", "/")[:160]
                L.append(f"| {k} | {tt['message']} | {rep} | {tt['first_word_s']:.1f} s | {tt['total_s']:.1f} s | "
                         f"{len(tt['cards'])} |")
        c = sc.get("5") or {}
        for side in ("a", "b"):
            s = (c.get("sides") or {}).get(side)
            if s:
                rep = s["reply"].replace("\n", " ").replace("|", "/")[:160]
                L.append(f"| 5{side.upper()} | {c['message']} | {rep} | – | – | – |")
        g = {k: sc.get(k) or {} for k in ORDER}
        L += [""]
        if g["1"]:
            L.append(f"- 1: {g['1'].get('slot_questions')} slot question(s), {g['1'].get('n_cards')} cards; "
                     f"stock: {g['1'].get('stock')}")
        if g["2"]:
            L.append(f"- 2: {g['2'].get('how')}; retrieved {g['2'].get('chunks')}")
        if g["4"]:
            L.append(f"- 4: {(g['4'].get('images') or {}).get('product_id')} {(g['4'].get('images') or {}).get('view')}")
        if g["5"]:
            L.append(f"- 5: the bare model's strap colour: {c.get('bare_model')}")
        if g["6"]:
            L.append(f"- 6: ticket {g['6'].get('ticket')} (in the reply: {g['6'].get('ticket_in_reply')}; "
                     f"in the staff log: {g['6'].get('logged')})")
        for k in ("R1", "R2"):
            if g[k]:
                L.append(f"- {k}: ready again and answering {g[k].get('recover_s')} s after the kill "
                         f"(limit {g[k].get('limit_s')} s; killed {g[k].get('killed')})")
        if g["N"]:
            L.append(f"- N: {g['N'].get('attempts')} connection attempts left the machine")
        if g["P"]:
            L.append(f"- P: {g['P'].get('compared')} replies compared with the project's Step 9 run")
        for k, runs in (d.get("earlier") or {}).items():
            for r in runs:
                L.append(f"- {k} {TITLES[k]}, earlier run: {'pass' if r['passed'] else 'FAIL'}"
                         + (f" ({'; '.join(r['problems'])})" if r["problems"] else "") + "; rerun above")
        for k in ORDER:
            for p in (sc.get(k) or {}).get("problems") or []:
                L.append(f"- **{k} {TITLES[k]}**: {p}")
    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["A", "B"])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--llama-port", type=int, default=8080)
    ap.add_argument("--base-dir", default=None)
    ap.add_argument("--fake", action="store_true", help="stand-in model (tests the script only)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--only", default=None, help="rerun some scenarios, e.g. 3 (3, 4 and 6 share one chat)")
    ap.add_argument("--offline", action="store_true",
                    help="Step 10: the kiosk through the launcher, offline guard on, restart checks R1/R2, network N")
    a = ap.parse_args(argv)
    global OUT
    if a.out:
        OUT = a.out
    elif a.offline:
        OUT = os.path.join(ROOT, "results_obj5", "_walkthrough_step10")
    if a.report:
        report()
        return 0
    if not a.tier:
        sys.exit("--tier A or B")
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
