"""
Objective 5, Step 2: parity of the shared turn engine with the harness's own code.

    python kiosk_core\\parity.py --results results_obj5 --pair o5s2_2b_rag_legacy o5s2_2b_rag_core ...
    python kiosk_core\\parity.py --plan harness\\plans\\obj5_step2_parity.json      # every legacy/core pair in the plan

For each case (and repeat) in both runs: the reply, the tool-call sequence (name, arguments, who made it) and the
flags. For dialogues, every kiosk turn's reply and calls. A difference is reported with where the two first part:
the first model round whose output differs (or "before the model" when the requests themselves differ, e.g. a
different route or retrieval).

Rule (fixed before the run): pooled over all pairs, at least 95% of cases have the same reply and the same
tool-call sequence, and every difference is traced (the report lists each one with its first divergence).
Writes <results>/_parity_step2/report.md and parity.json.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(run_dir):
    out = {}
    p = os.path.join(run_dir, "cases.jsonl")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[(r["id"], r.get("repeat", 0))] = r
    return out


def calls(rec):
    return [(c.get("name"), json.dumps(c.get("arguments"), sort_keys=True, ensure_ascii=False), c.get("by") or "model",
             c.get("guard")) for c in rec.get("tool_calls") or []]


def requests(rec):
    """What was sent and received per model round (prompt size and the model's output)."""
    return [(t.get("prompt_tokens"), (t.get("content") or "").strip(), t.get("n_tool_calls")) for t in rec.get("turns") or []]


def first_divergence(a, b):
    if a.get("route") != b.get("route"):
        return f"route {a.get('route')} vs {b.get('route')}"
    ra, rb = (a.get("retrieval") or {}).get("chunk_ids"), (b.get("retrieval") or {}).get("chunk_ids")
    if ra != rb:
        return "retrieved chunks differ"
    qa, qb = requests(a), requests(b)
    for i, (x, y) in enumerate(zip(qa, qb)):
        if x[0] != y[0]:
            return f"round {i}: prompt differs ({x[0]} vs {y[0]} tokens)"
        if x[1:] != y[1:]:
            return f"round {i}: same prompt, different model output (decoding)"
    if len(qa) != len(qb):
        return f"different number of model rounds ({len(qa)} vs {len(qb)})"
    if calls(a) != calls(b):
        return "same model outputs, different tool calls (harness logic)"
    return "after the model (checks)"


def compare(a_dir, b_dir):
    A, B = load(a_dir), load(b_dir)
    if A is None or B is None:
        return None
    keys = sorted(set(A) & set(B))
    same, diffs = 0, []
    for k in keys:
        a, b = A[k], B[k]
        if a.get("error") or b.get("error"):
            diffs.append({"case": k[0], "repeat": k[1], "what": "error", "where": a.get("error") or b.get("error")})
            continue
        if a.get("dialogue") or b.get("dialogue"):
            ta, tb = (a.get("dialogue") or {}).get("turns") or [], (b.get("dialogue") or {}).get("turns") or []
            ok = len(ta) == len(tb) and all(x.get("kiosk") == y.get("kiosk") and calls(x) == calls(y)
                                            for x, y in zip(ta, tb))
            if ok:
                same += 1
            else:
                i = next((j for j, (x, y) in enumerate(zip(ta, tb)) if x.get("kiosk") != y.get("kiosk")
                          or calls(x) != calls(y)), min(len(ta), len(tb)))
                diffs.append({"case": k[0], "repeat": k[1], "what": "dialogue", "where": f"kiosk turn {i}",
                              "a": (ta[i].get("kiosk") if i < len(ta) else None),
                              "b": (tb[i].get("kiosk") if i < len(tb) else None)})
            continue
        ok = a.get("final_reply") == b.get("final_reply") and calls(a) == calls(b)
        if ok:
            same += 1
            if sorted(a.get("flags") or []) != sorted(b.get("flags") or []):
                diffs.append({"case": k[0], "repeat": k[1], "what": "flags only", "where": "flags",
                              "a": a.get("flags"), "b": b.get("flags"), "counts": False})
        else:
            what = "reply" if a.get("final_reply") != b.get("final_reply") else "tool calls"
            diffs.append({"case": k[0], "repeat": k[1], "what": what, "where": first_divergence(a, b),
                          "a": (a.get("final_reply") or "")[:300], "b": (b.get("final_reply") or "")[:300]})
    return {"a": os.path.basename(a_dir), "b": os.path.basename(b_dir), "n": len(keys), "same": same,
            "only_in_one": len(set(A) ^ set(B)), "diffs": diffs}


def pairs_from_plan(path):
    plan = json.load(open(path, encoding="utf-8"))
    names = [r["name"] for r in plan["runs"]]
    out = []
    for n in names:
        if n.endswith("_legacy") and n[:-7] + "_core" in names:
            out.append((n, n[:-7] + "_core"))
    return out, os.path.join(ROOT, plan.get("results_dir", "results"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=None)
    ap.add_argument("--results", default=None)
    ap.add_argument("--pair", nargs=2, action="append", default=[])
    a = ap.parse_args(argv)
    pairs, res = list(map(tuple, a.pair)), a.results
    if a.plan:
        p, r = pairs_from_plan(a.plan)
        pairs += p
        res = res or r
    res = res or os.path.join(ROOT, "results_obj5")
    rows = [c for c in (compare(os.path.join(res, x), os.path.join(res, y)) for x, y in pairs) if c]
    n = sum(r["n"] for r in rows)
    same = sum(r["same"] for r in rows)
    share = same / n if n else 0.0
    ok = n > 0 and share >= 0.95
    L = ["# Step 2: shared engine against the harness's own code", "",
         f"Pooled: {same}/{n} cases identical ({share:.1%}); rule: at least 95% -> **{'met' if ok else 'NOT met'}**.", "",
         "| Legacy run | Core run | Cases | Identical | Not in both |", "|---|---|---:|---:|---:|"]
    L += [f"| {r['a']} | {r['b']} | {r['n']} | {r['same']} ({r['same'] / max(1, r['n']):.0%}) | {r['only_in_one']} |"
          for r in rows]
    missing = [f"{x} / {y}" for x, y in pairs if not any(r["a"] == x and r["b"] == y for r in rows)]
    if missing:
        L += ["", "Not compared (a run is missing): " + "; ".join(missing)]
    L += ["", "## Differences (each to be traced)", ""]
    any_d = False
    for r in rows:
        for d in r["diffs"]:
            any_d = True
            L.append(f"- {r['a']} vs {r['b']}, {d['case']} r{d['repeat']}: {d['what']}, {d['where']}"
                     + (f"\n  - legacy: {d.get('a')!r}\n  - core: {d.get('b')!r}" if d.get("a") is not None or
                        d.get("b") is not None else ""))
    if not any_d:
        L.append("None.")
    out = os.path.join(res, "_parity_step2")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(out, "parity.json"), "w", encoding="utf-8") as f:
        json.dump({"pooled": {"n": n, "same": same, "share": share, "met": ok}, "pairs": rows}, f, indent=1,
                  default=str)
    print("\n".join(L))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
