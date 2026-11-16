"""
Objective 3, Step 8: recalibrate the hard-fallback threshold on dev store questions only.

    python eval\\calibrate_store_tau.py results_obj3\\o3s7a_4b_rag

Reads the retrieval scores already logged by an O3-S7a store-question run (retrieval does not depend on the model)
and keeps only the questions the Step 8 fallback can act on:
  - routed to store or unclear (only those are retrieved),
  - no product code and no catalogue name in the message (those always go to the model and its tools),
  - not caught first by the entity check (other brands, smartwatches, non-watch items, designs that do not exist),
  - not Hinglish (the Hinglish bypass stays on: the English re-ranker under-scores Hinglish questions).
Roles come from eval/rag_cases.jsonl: must answer (behaviour "answer"), must refuse ("decline"), either.

Rule (the same as Objective 2, fixed before looking at these scores): the HIGHEST threshold whose false-refusal rate
on the must-answer questions above is at most 5%. Dev only; the test split is not read.
Writes <out>/fallback.json and <out>/report.md. In fallback.json, "threshold" keeps the Objective 2 value (the soft
fallback, which decides whether cards are shown, is unchanged) and "hard_threshold" is the new value used only by
the Step 8 hard fallback.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "retrieval"))
from bench_retrieval import wilson  # noqa: E402
from harness import entity  # noqa: E402
from tools import mock_tools  # noqa: E402

MAX_FALSE_REFUSAL_DEV = 0.05
ROLE = {"answer": "answer", "decline": "refuse", "either": "either"}
OLD_FALLBACK = os.path.join(ROOT, "results_retrieval", "fallback_bypass", "fallback.json")


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def rows_from_run(run_dir, cases, scores=None):
    """scores: {question id: top-1 score} to use instead of the logged one (Step 9: another re-ranker), with
    route, codes and names still taken from the log (they do not depend on the re-ranker)."""
    rows = []
    for r in load_jsonl(os.path.join(run_dir, "cases.jsonl")):
        if r.get("repeat", 0) != 0 or r.get("error") or r["id"] not in cases:
            continue
        c = cases[r["id"]]
        if c.get("split") != "dev":
            continue
        ret = r.get("retrieval") or {}
        router = ret.get("router") or {}
        if ret.get("route") not in ("store", "unclear") or ret.get("top1") is None:
            continue
        text = c["messages"][-1]["content"]
        sc = ret["top1"] if scores is None else scores.get(r["id"])
        if sc is None:
            continue
        rows.append({"id": r["id"], "role": ROLE[c["expected"]["behaviour"]], "score": sc,
                     "hinglish": bool(ret.get("hinglish")), "named": bool(router.get("codes") or router.get("named")),
                     "entity": entity.reply(text) is not None, "subcategory": c.get("subcategory")})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run", help="an O3-S7a store-question run directory (o3s7a_4b_rag or o3s7a_2b_rag)")
    ap.add_argument("--eval", default=os.path.join(ROOT, "eval", "rag_cases.jsonl"))
    ap.add_argument("--old", default=OLD_FALLBACK, help="the Objective 2 fallback.json (messages are copied)")
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj3", "_tau_step8"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    mock_tools.HONEST = True
    cases = {c["id"]: c for c in load_jsonl(a.eval)}
    rows = rows_from_run(a.run, cases)
    with open(a.old, encoding="utf-8") as f:
        old = json.load(f)
    act = [r for r in rows if not r["named"] and not r["entity"] and not (old.get("hinglish_bypass") and r["hinglish"])]
    ans = [r for r in act if r["role"] == "answer"]
    ref = [r for r in act if r["role"] == "refuse"]
    eit = [r for r in act if r["role"] == "either"]

    def rates(t):
        return (sum(r["score"] < t for r in ans), sum(r["score"] < t for r in ref), sum(r["score"] < t for r in eit))

    cands = sorted({r["score"] for r in act} | {float("-inf")})
    ok = [t for t in cands if ans and rates(t)[0] / len(ans) <= MAX_FALSE_REFUSAL_DEV]
    t = max(ok) if ok else float("-inf")
    L = ["# Step 8: hard-fallback threshold on dev store questions", "",
         f"Run read: `{os.path.basename(os.path.normpath(a.run))}`. Store or unclear questions with a logged score: "
         f"{len(rows)}; the fallback can act on {len(act)} (no code or catalogue name, not caught by the entity "
         f"check, not Hinglish): {len(ans)} must answer, {len(ref)} must refuse, {len(eit)} either.", "",
         f"Rule: highest threshold with false refusals on must-answer at most {MAX_FALSE_REFUSAL_DEV:.0%}.", "",
         "| Threshold | False refusals (must answer) [95% CI] | Refused (must refuse) | Refused (either) |",
         "|---|---|---|---|"]
    for name, th in (("Objective 2", float(old["threshold"])), ("chosen", t)):
        fr, tr, er = rates(th)
        p, lo, hi = wilson(fr, len(ans)) if ans else (None, None, None)
        frs = f"{fr}/{len(ans)} = {p:.1%} [{lo:.1%}, {hi:.1%}]" if ans else "–"
        L.append(f"| {name} {th:.3f} | {frs} | {tr}/{len(ref)} | {er}/{len(eit)} |")
    L += ["", "Questions refused at the chosen threshold:", ""]
    for r in sorted(act, key=lambda r: r["score"]):
        if r["score"] < t:
            L.append(f"- {r['id']} ({r['role']}, {r['subcategory']}) score {r['score']:.3f}")
    # "threshold" stays the Objective 2 value, so the soft fallback (which cards are shown) is unchanged; only the
    # Step 8 hard fallback (run_eval --fallback store-live) uses hard_threshold
    cfg = {"threshold": float(old["threshold"]), "hard_threshold": t, "hinglish_bypass": bool(old.get("hinglish_bypass")), "messages": old["messages"],
           "source": "Objective 3, Step 8: dev store questions only (eval/calibrate_store_tau.py)",
           "run": os.path.basename(os.path.normpath(a.run)), "n_must_answer": len(ans)}
    with open(os.path.join(a.out, "fallback.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    print(f"Wrote {os.path.join(a.out, 'fallback.json')} (threshold {t:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
