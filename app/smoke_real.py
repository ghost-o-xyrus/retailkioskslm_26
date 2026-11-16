"""
Objective 5, Step 4: the app with the real models, through its own API (the same calls the browser makes).

Start the app first, in another terminal, in Lab mode:
    python app\\server.py
Then:
    python app\\smoke_real.py --tier A
    python app\\smoke_real.py --tier B

For the tier, it runs the first five design scenarios. The sixth, Kiosk mode, is checked by hand (see the
instructions). The scenarios are:
  1 a shopping question (product cards expected)
  2 a store question (a retrieval stage expected)
  3 another brand (the entity check's fixed reply, no model round)
  4 Custom with retrieval off (no retrieval stage, untested label)
  5 compare: the same question to O3-final and to Model only
It checks that every turn ends with a reply and no error, every stage adds up, product cards appear where expected,
and the brand name never reaches the client. It also records the load time, the first status, the first word (the
reply event) and the total. Report: results_obj5/_app_step4/smoke_<tier>.md and .json.
"""
import argparse
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BRAND = "Veyra"


def post(base, path, body, stream=False, timeout=900):
    req = urllib.request.Request(base + path, data=json.dumps(body).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    r = urllib.request.urlopen(req, timeout=timeout)
    if not stream:
        return json.loads(r.read().decode("utf-8"))
    return r


def get(base, path):
    with urllib.request.urlopen(base + path, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def turn(base, path, message):
    t0 = time.time()
    events, first = [], {}
    r = post(base, path, {"message": message}, stream=True)
    for raw in r:
        line = raw.decode("utf-8").strip()
        if not line.startswith("data:"):
            continue
        ev = json.loads(line[5:])
        ev["_t"] = round((time.time() - t0) * 1000)
        events.append(ev)
        first.setdefault(ev.get("type"), ev["_t"])
        if ev.get("type") == "done":
            break
    return events, first, round((time.time() - t0) * 1000)


def check_turn(base, events, first, total, expect):
    out = {"total_ms": total, "first_status_ms": first.get("status"), "load_ms": None, "errors": [],
           "reply": None, "cards": 0, "stages": [], "unattributed_ms": None, "turn_id": None}
    for ev in events:
        t = ev.get("type")
        if t == "error":
            out["errors"].append(ev.get("message"))
        elif t == "model_loaded":
            out["load_ms"] = ev.get("load_ms")
        elif t == "cards":
            out["cards"] += len(ev.get("cards") or [])
        elif t == "turn_end":
            out["turn_id"] = ev.get("turn_id")
    raw = json.dumps(events, ensure_ascii=False)
    if BRAND.lower() in raw.lower():
        out["errors"].append("the brand name reached the client")
    if out["turn_id"]:
        tr = get(base, f"/api/turns/{out['turn_id']}/trace")
        if BRAND.lower() in json.dumps(tr, ensure_ascii=False).lower():
            out["errors"].append("the brand name reached the client (trace)")
        out["reply"] = tr.get("final_reply")
        out["stages"] = [s.get("stage") for s in tr.get("stages") or []]
        ss = tr.get("stage_summary") or {}
        out["unattributed_ms"] = ss.get("unattributed_ms")
        m = tr.get("metrics") or {}
        out["first_word_ms"] = m.get("first_visible_ms")
        peaks = [sum(v for v in (x.get("peak_mb") or {}).values() if isinstance(v, (int, float)))
                 if isinstance(x.get("peak_mb"), dict) else (x.get("peak_mb") or 0) for x in tr.get("stages") or []]
        out["peak_mb"] = round(max(peaks or [0])) or None
        tot = ss.get("covered_ms", 0) + (ss.get("unattributed_ms") or 0)
        if tot and (ss.get("unattributed_ms") or 0) > max(0.05 * tot, 5):
            out["errors"].append(f"stages leave {ss['unattributed_ms']} ms of {tot} ms uncovered")
    else:
        out["errors"].append("no turn_end event")
    if not (out["reply"] or "").strip():
        out["errors"].append("empty reply")
    if expect.get("cards") and not out["cards"]:
        out["errors"].append("no product cards")
    if expect.get("stage") and expect["stage"] not in out["stages"]:
        out["errors"].append(f"no {expect['stage']} stage")
    if expect.get("no_stage") and expect["no_stage"] in out["stages"]:
        out["errors"].append(f"a {expect['no_stage']} stage ran")
    out["ok"] = not out["errors"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["A", "B"], default="A")
    ap.add_argument("--app", default="http://127.0.0.1:8000")
    a = ap.parse_args(argv)
    base = a.app
    cfgs = get(base, "/api/configs")
    if cfgs.get("mode") != "lab":
        sys.exit("start the app in Lab mode: python app\\server.py")
    t_wait = time.time()
    while True:                                   # the app loads and warms its model at start-up
        try:
            rd = get(base, "/api/ready")
        except Exception:  # noqa: BLE001 - an app without the endpoint
            rd = {"state": "ready"}
        if rd.get("state") != "loading":
            break
        time.sleep(2)
    if time.time() - t_wait > 3:
        print(f"Waited {time.time() - t_wait:.0f} s for the app to finish loading.")
    if cfgs.get("fake"):
        print("Note: the app is in stand-in mode (--fake); this checks the plumbing, not the real models.")
    default = {"tier": a.tier}
    res = []

    def scenario(n, title, message, expect, selection=None):
        s = post(base, "/api/sessions", {"selection": selection or default})
        ev, first, total = turn(base, f"/api/sessions/{s['id']}/turns", message)
        r = check_turn(base, ev, first, total, expect)
        r["first_shown_ms"] = first.get("token")
        if expect.get("untested") is not None and bool(s.get("untested")) != expect["untested"]:
            r["errors"].append(f"untested label is {s.get('untested')}")
            r["ok"] = False
        r.update(n=n, title=title, message=message, label=s.get("label"))
        res.append(r)
        print(f"[{n}] {title}: {'PASS' if r['ok'] else 'FAIL'}  total {total / 1000:.1f} s"
              + (f", model load {r['load_ms'] / 1000:.1f} s" if r.get("load_ms") else "")
              + ("" if r["ok"] else "  " + "; ".join(r["errors"])))

    scenario(1, "Shopping question with cards", "Formal watch for my father under 15000",
             {"cards": True})
    scenario(2, "Store question", "Do you offer gift wrapping?", {"stage": "retrieval"})
    scenario(3, "Another brand", "Do you sell Fossil watches?", {"no_stage": "model_round"})
    toggles = dict(cfgs["toggle_defaults"], retrieval=False)
    scenario(4, "Custom, retrieval off", "Do you offer gift wrapping?",
             {"no_stage": "retrieval", "untested": True},
             selection={"tier": a.tier, "pipeline": "custom", "toggles": toggles})
    # 5: compare
    c = post(base, "/api/compare", {"a": {"tier": a.tier, "pipeline": "o3_final"},
                                    "b": {"tier": a.tier, "pipeline": "model_only"}})
    ev, first, total = turn(base, f"/api/compare/{c['id']}/turns", "Is the store open on Sunday?")
    ends = [e for e in ev if e.get("type") == "turn_end"]
    sides = sorted({e.get("side") for e in ends})
    errs = [e.get("message") for e in ev if e.get("type") == "error"]
    if sides != ["a", "b"]:
        errs.append(f"turn_end for sides {sides}, expected a and b")
    if BRAND.lower() in json.dumps(ev, ensure_ascii=False).lower():
        errs.append("the brand name reached the client")
    r = {"n": 5, "title": "Compare O3-final and Model only", "message": "Is the store open on Sunday?",
         "total_ms": total, "errors": errs, "ok": not errs}
    res.append(r)
    print(f"[5] {r['title']}: {'PASS' if r['ok'] else 'FAIL'}  total {total / 1000:.1f} s"
          + ("" if r["ok"] else "  " + "; ".join(errs)))

    od = os.path.join(ROOT, "results_obj5", "_app_step4")
    os.makedirs(od, exist_ok=True)
    L = [f"# Objective 5, Step 4: the app with the real models, Tier {a.tier}", "",
         f"Stand-in mode: {bool(cfgs.get('fake'))}", "",
         "| # | Scenario | Result | Total | First word | First text on screen | First status | Model load | Stages | Cards | Peak MB | Problems |",
         "|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|"]
    for r in res:
        L.append(f"| {r['n']} | {r['title']} | {'pass' if r['ok'] else 'FAIL'} | {r['total_ms'] / 1000:.1f} s | "
                 f"{(r.get('first_word_ms') or 0) / 1000:.1f} s | "
                 f"{(r['first_shown_ms'] / 1000) if r.get('first_shown_ms') else 0:.1f} s | "
                 f"{(r.get('first_status_ms') or 0) / 1000:.2f} s | "
                 f"{(r['load_ms'] / 1000) if r.get('load_ms') else 0:.1f} s | {' '.join(r.get('stages') or [])} | "
                 f"{r.get('cards', '')} | {r.get('peak_mb') or ''} | {'; '.join(r['errors']) or '–'} |")
    L += ["", "Scenario 6 (Kiosk mode) is checked by hand; see the instructions."]
    with open(os.path.join(od, f"smoke_{a.tier}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(od, f"smoke_{a.tier}.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, ensure_ascii=False, default=str)
    print(f"Wrote {os.path.join(od, f'smoke_{a.tier}.md')}")
    return 0 if all(r["ok"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
