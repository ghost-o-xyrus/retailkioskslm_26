"""
Objective 5, Step 6: compare mode gives the same replies as running each setup alone.

Rule (fixed before the run): on 10 dev cases, each compare column's reply and tool calls equal the same
configuration's single-run reply and tool calls.

Two pairs, through the app's own API (start the app first, in Lab mode: python app\\server.py):
  P1  Tier A: O3-final | Model only            (one llama-server, two pipelines)
  P2  Tier B: O3-final | Deployed (lora_4b)    (one llama-server, the adapter switched on and off per request)
Cases: 10 dev cases from the speed subset (5 store questions, 5 tool cases), single customer messages.
For each case and pair: the compare turn (column A, then B), then each configuration alone in a fresh chat.

    python app\\compare_check.py                 # both pairs (about 30-45 minutes)
    python app\\compare_check.py --pairs P1      # one pair

Report: results_obj5/_compare_step6/report.md and report.json.
"""
import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from smoke_real import get, post, turn  # noqa: E402



PAIRS = {
    "P1": ("Tier A: O3-final vs Model only", {"tier": "A", "model": "qwen35-2b", "pipeline": "o3_final"},
           {"tier": "A", "model": "qwen35-2b", "pipeline": "model_only"}),
    "P2": ("Tier B: O3-final vs Deployed", {"tier": "B", "model": "qwen35-4b", "pipeline": "o3_final"},
           {"tier": "B", "pipeline": "deployed"}),
}


def pick_cases(n_store=5, n_tool=5, seed=606):
    ids = json.load(open(os.path.join(ROOT, "eval", "o3_dev_speed_ids.json"), encoding="utf-8"))

    def load(path, want):
        out = {}
        with open(os.path.join(ROOT, path), encoding="utf-8") as f:
            for line in f:
                c = json.loads(line)
                users = [m for m in c.get("messages", []) if m.get("role") == "user"]
                if c["id"] in want and len(users) == 1 and len(c["messages"]) == 1:
                    out[c["id"]] = (users[0]["content"], c.get("category"))
        return out
    rng = random.Random(seed)
    store = load("eval/rag_cases.jsonl", set(ids["rag_ids"]))
    tool = load("eval/eval_set_v1.2.jsonl", set(ids["v11_ids"]))
    s = sorted(store)
    rng.shuffle(s)
    by_cat = {}                                  # tool cases: one per category, so each tool path is used
    for i in sorted(tool):
        by_cat.setdefault(tool[i][1], []).append(i)
    t = []
    for cat in sorted(by_cat):
        rng.shuffle(by_cat[cat])
        t.append(by_cat[cat][0])
    rng.shuffle(t)
    return [(i, store[i][0], "store question") for i in sorted(s[:n_store])] + \
           [(i, tool[i][0], "tool case") for i in sorted(t[:n_tool])]


def outcome(base, tid):
    tr = get(base, f"/api/turns/{tid}/trace")
    calls = [(c.get("name"), json.dumps(c.get("arguments"), sort_keys=True, ensure_ascii=False), c.get("by") or "model")
             for c in tr.get("tool_calls") or []]
    tickets = [((c.get("result") or {}).get("ticket")) for c in tr.get("tool_calls") or []
               if c.get("name") == "call_staff" and isinstance(c.get("result"), dict)]
    return {"reply": tr.get("final_reply") or "", "calls": calls, "label": tr.get("config"),
            "tickets": [t for t in tickets if t]}


def set_next_ticket(base, ticket):
    """Lab mode: the next staff ticket the app issues (so a single run sees the same ticket its column saw)."""
    post(base, "/api/lab/next_ticket", {"next": int(ticket.split("-")[1])})


def single(base, sel, message):
    s = post(base, "/api/sessions", {"selection": sel})
    ev, first, total = turn(base, f"/api/sessions/{s['id']}/turns", message)
    end = next((e for e in ev if e.get("type") == "turn_end"), None)
    err = [e.get("message") for e in ev if e.get("type") == "error"]
    if not end:
        return {"error": "; ".join(err) or "no turn_end"}, total
    return outcome(base, end["turn_id"]), total


def compared(base, a, b, message):
    c = post(base, "/api/compare", {"a": a, "b": b})
    ev, first, total = turn(base, f"/api/compare/{c['id']}/turns", message)
    ends = {e.get("side"): e for e in ev if e.get("type") == "turn_end"}
    out = {}
    for side in ("a", "b"):
        out[side] = outcome(base, ends[side]["turn_id"]) if side in ends else {"error": "no turn_end for " + side}
    return out, total


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--app", default="http://127.0.0.1:8000")
    ap.add_argument("--pairs", default="P1,P2")
    ap.add_argument("--only", default=None, help="comma-separated case ids (a rerun of some cases)")
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj5", "_compare_step6"))
    a = ap.parse_args(argv)
    base = a.app
    cfgs = get(base, "/api/configs")
    if cfgs.get("mode") != "lab":
        sys.exit("start the app in Lab mode: python app\\server.py")
    while (get(base, "/api/ready") or {}).get("state") == "loading":
        time.sleep(2)
    cases = pick_cases()
    if a.only:
        keep = {x.strip() for x in a.only.split(",")}
        cases = [c for c in cases if c[0] in keep]
    rows, n, same = [], 0, 0
    for pk in [x.strip() for x in a.pairs.split(",") if x.strip()]:
        title, sa, sb = PAIRS[pk]
        print(f"\n== {pk} {title}")
        for cid, msg, kind in cases:
            col, t_cmp = compared(base, sa, sb, msg)
            # staff tickets are numbered across chats; the model reads the number, so each single run is given the
            # ticket its compare column got (a different number is a different prompt, not a compare-mode effect)
            if col["a"].get("tickets"):
                set_next_ticket(base, col["a"]["tickets"][0])
            alone_a, ta = single(base, sa, msg)
            if col["b"].get("tickets"):
                set_next_ticket(base, col["b"]["tickets"][0])
            alone_b, tb = single(base, sb, msg)
            for side, alone in (("a", alone_a), ("b", alone_b)):
                x = col[side]
                ok = "error" not in x and "error" not in alone and x["reply"] == alone["reply"] \
                    and x["calls"] == alone["calls"]
                n += 1
                same += ok
                rows.append({"pair": pk, "case": cid, "kind": kind, "side": side, "label": x.get("label"),
                             "same": ok, "compare": x, "alone": alone})
            r = [w for w in rows[-2:]]
            print(f"  {cid:12s} {kind:15s} A {'same' if r[0]['same'] else 'DIFFERENT'}  "
                  f"B {'same' if r[1]['same'] else 'DIFFERENT'}   ({t_cmp / 1000:.0f} s compare, "
                  f"{(ta + tb) / 1000:.0f} s alone)")
    met = n > 0 and same == n
    L = ["# Objective 5, Step 6: compare mode against single runs", "",
         f"Cases: {len(cases)} dev cases ({sum(k == 'store question' for _, _, k in cases)} store questions, "
         f"{sum(k == 'tool case' for _, _, k in cases)} tool cases): {', '.join(c for c, _, _ in cases)}.", "",
         f"**{same}/{n} columns identical to the single run** (reply and tool calls; each single run "
         f"given the staff ticket number its column got); rule: all -> "
         f"**{'met' if met else 'NOT met'}**", "",
         "| Pair | Columns | Identical |", "|---|---:|---:|"]
    for pk in [x.strip() for x in a.pairs.split(",") if x.strip()]:
        rr = [r for r in rows if r["pair"] == pk]
        L.append(f"| {pk} {PAIRS[pk][0]} | {len(rr)} | {sum(r['same'] for r in rr)} |")
    bad = [r for r in rows if not r["same"]]
    if bad:
        L += ["", "## Differences", ""]
        for r in bad:
            L += [f"- {r['pair']} {r['case']} column {r['side'].upper()} ({r['label']})",
                  f"  - compare: `{json.dumps(r['compare'], ensure_ascii=False)[:400]}`",
                  f"  - alone: `{json.dumps(r['alone'], ensure_ascii=False)[:400]}`"]
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "report.json"), "w", encoding="utf-8") as f:
        json.dump({"met": met, "identical": same, "columns": n, "rows": rows}, f, indent=1, ensure_ascii=False)
    print("\n" + "\n".join(L))
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
