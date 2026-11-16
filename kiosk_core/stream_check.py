"""
Objective 5, Step 4: the streaming check.

The app would like to show the reply word by word. llama-server can stream a reply, but it then sends tool calls in
pieces, and the streamed pieces must parse to exactly what the same request returns without streaming. The rule,
fixed before the run: if streamed and non-streamed tool calls (and text) are identical on all 30 tool cases of the
dev speed subset, for both models, every model round streams. Otherwise only rounds that cannot call tools stream
(the last round, run with tools off).

How it runs: a plan run with "stream_check": true runs the harness with --engine core as usual. Each model request
is sent twice, first as the harness always sends it and then the same body with "stream": true; the turn continues
with the non-streamed reply, so the run's behaviour is unchanged. Every request's comparison is stored in the case
record ("stream_check": [...]).

    python kiosk_core\\build_plans.py
    python harness\\run_plan.py harness\\plans\\obj5_step4_stream.json
    python kiosk_core\\stream_check.py --plan harness\\plans\\obj5_step4_stream.json

Report: results_obj5\\_stream_step4\\report.md and verdict.json.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG = []          # comparisons of the current case, drained by the harness after each case


def parse_stream(lines):
    """Rebuild a chat message from llama-server's server-sent chunks (OpenAI format)."""
    content, calls, finish, n = [], {}, None, 0
    for raw in lines:
        line = raw.decode("utf-8", "replace").strip() if isinstance(raw, bytes) else raw.strip()
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        ev = json.loads(data)
        if "error" in ev:
            raise RuntimeError(f"stream error: {ev['error']}")
        n += 1
        for ch in ev.get("choices") or []:
            d = ch.get("delta") or {}
            if d.get("content"):
                content.append(d["content"])
            for tc in d.get("tool_calls") or []:
                c = calls.setdefault(tc.get("index", 0), {"name": "", "arguments": ""})
                f = tc.get("function") or {}
                c["name"] += f.get("name") or ""
                c["arguments"] += f.get("arguments") or ""
            if ch.get("finish_reason"):
                finish = ch["finish_reason"]
    return {"content": "".join(content), "tool_calls": [calls[k] for k in sorted(calls)], "finish": finish,
            "chunks": n}


def _args(s):
    try:
        return json.loads(s) if s else {}
    except ValueError:
        return {"_unparsed": s}


def normal(msg, finish=None):
    calls = [{"name": (c.get("function") or c).get("name"),
              "arguments": _args((c.get("function") or c).get("arguments"))} for c in msg.get("tool_calls") or []]
    return {"content": (msg.get("content") or "").strip(), "tool_calls": calls, "finish": finish}


def compare(plain_resp, streamed):
    ch = plain_resp["choices"][0]
    a = normal(ch.get("message") or {}, ch.get("finish_reason"))
    b = normal({"content": streamed["content"],
                "tool_calls": [{"function": c} for c in streamed["tool_calls"]]}, streamed["finish"])
    out = {"tools_on": None, "plain_calls": len(a["tool_calls"]), "stream_calls": len(b["tool_calls"]),
           "calls_same": a["tool_calls"] == b["tool_calls"], "text_same": a["content"] == b["content"],
           "finish_same": a["finish"] == b["finish"], "chunks": streamed.get("chunks")}
    if not (out["calls_same"] and out["text_same"]):
        out["plain"], out["stream"] = a, b
    return out


def install(engine):
    """Wrap engine.http_json so every chat request is also sent streamed and the two are compared."""
    plain = engine.http_json

    def http_json(url, payload=None, timeout=600):
        resp = plain(url, payload, timeout)
        if payload is None or not url.endswith("/v1/chat/completions"):
            return resp
        body = dict(payload, stream=True)
        tools_on = bool(body.get("tools")) and body.get("tool_choice") != "none"
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res = compare(resp, parse_stream(r))
        except urllib.error.HTTPError as e:
            res = {"error": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}", "calls_same": False,
                   "text_same": False}
        except Exception as e:  # noqa: BLE001 - recorded as a failed comparison
            res = {"error": f"{type(e).__name__}: {e}", "calls_same": False, "text_same": False}
        res["tools_on"] = tools_on
        LOG.append(res)
        return resp

    engine.http_json = http_json


def drain():
    out = list(LOG)
    LOG.clear()
    return out


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def summarise(path):
    cases, reqs, bad = 0, 0, []
    tool_reqs = tool_same = notool_reqs = notool_same = 0
    missing = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            cases += 1
            sc = r.get("stream_check")
            if sc is None:
                missing += 1
                continue
            same_case = True
            for q in sc:
                reqs += 1
                ok = q.get("calls_same") and q.get("text_same") and not q.get("error")
                if q.get("tools_on"):
                    tool_reqs += 1
                    tool_same += bool(ok)
                else:
                    notool_reqs += 1
                    notool_same += bool(ok)
                if not ok:
                    same_case = False
            if not same_case:
                bad.append({"id": r["id"], "diffs": [q for q in sc if not (q.get("calls_same") and q.get("text_same")
                                                                         and not q.get("error"))]})
    return {"cases": cases, "missing": missing, "requests": reqs, "cases_identical": cases - missing - len(bad),
            "tool_requests": tool_reqs, "tool_identical": tool_same, "notool_requests": notool_reqs,
            "notool_identical": notool_same, "different": bad}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=os.path.join(ROOT, "harness", "plans", "obj5_step4_stream.json"))
    ap.add_argument("--results", default=None)
    a = ap.parse_args(argv)
    plan = json.load(open(a.plan, encoding="utf-8"))
    rd = a.results or os.path.join(ROOT, plan.get("results_dir", "results_obj5"))
    L = ["# Objective 5, Step 4: streamed against non-streamed replies", "",
         "Each model request was sent both ways; the turn went on with the non-streamed reply.", "",
         "| Run | Cases | Identical cases | Requests with tools on: identical | Last rounds (tools off): identical | "
         "Different cases |", "|---|---:|---:|---:|---:|---|"]
    out, all_ok, all_text_ok = {}, True, True
    for run in plan["runs"]:
        p = os.path.join(rd, run["name"], "cases.jsonl")
        if not os.path.exists(p):
            L.append(f"| {run['name']} | missing | | | | |")
            all_ok = all_text_ok = False
            continue
        s = summarise(p)
        out[run["name"]] = s
        ok = s["cases"] > 0 and not s["missing"] and not s["different"]
        all_ok &= ok
        all_text_ok &= s["notool_identical"] == s["notool_requests"] and not s["missing"]
        L.append(f"| {run['name']} | {s['cases']} | {s['cases_identical']} | {s['tool_identical']}/{s['tool_requests']}"
                 f" | {s['notool_identical']}/{s['notool_requests']} | "
                 f"{', '.join(d['id'] for d in s['different']) or '–'} |")
    if all_ok:
        decision = "every model round streams"
    elif all_text_ok:
        decision = "only rounds that cannot call tools stream (the last round, tools off)"
    else:
        decision = "no streaming: even rounds with tools off differ (see the differences)"
    L += ["", f"**Rule:** identical on every tool case for both models → every round streams; otherwise only rounds "
              f"that cannot call tools stream.", "", f"**Decision:** {decision}."]
    for name, s in out.items():
        for d in s["different"][:10]:
            L += ["", f"### {name}: {d['id']}", ""]
            for q in d["diffs"][:3]:
                if q.get("error"):
                    L.append(f"- error: {q['error']}")
                else:
                    L.append(f"- tools {'on' if q.get('tools_on') else 'off'}; calls same: {q['calls_same']}; "
                             f"text same: {q['text_same']}")
                    L.append(f"  - non-streamed: `{json.dumps(q.get('plain'), ensure_ascii=False)[:400]}`")
                    L.append(f"  - streamed: `{json.dumps(q.get('stream'), ensure_ascii=False)[:400]}`")
    od = os.path.join(rd, "_stream_step4")
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(od, "verdict.json"), "w", encoding="utf-8") as f:
        json.dump({"stream_all_rounds": all_ok, "stream_last_round_only": (not all_ok) and all_text_ok,
                   "decision": decision, "runs": out}, f, indent=1, ensure_ascii=False)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
