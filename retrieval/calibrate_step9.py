"""
Objective 3, Step 9d (only if bench_reranker.py chose a new re-ranker): fallback thresholds for it, by the rules
already fixed, on dev only, from its saved ranks (no models needed).

    python retrieval\\calibrate_step9.py

1. Hinglish bypass. Without the bypass, take the Objective 2 rule's threshold (highest with at most 5% false
   refusals on all dev must-answer questions). The bypass is retired if that threshold refuses at most 1 of the
   dev answerable Hinglish questions (14; one is 7%); otherwise it stays.
2. Soft threshold ("threshold": whether cards are shown): the Objective 2 rule, with the bypass as decided.
3. Hard threshold ("hard_threshold", Step 8): the Step 8 rule on dev store questions only (eval/calibrate_store_tau.py
   logic), with the new scores and the route, codes and names logged by the O3-S7a run.
Writes results_obj3/_rerank_step9/fallback.json and calibration.md.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "eval"))
import bench_retrieval as B  # noqa: E402
from language import is_hinglish  # noqa: E402
import calibrate_store_tau as T  # noqa: E402

MAX_FR = 0.05
MAX_HINGLISH_REFUSED = 1


def soft_threshold(items, top1, bypass):
    ans = [it for it in items if it["answer_type"] == "fact"]
    cand = sorted({top1[it["id"]] for it in items} | {float("-inf")})

    def fr(t):
        return sum(1 for it in ans if top1[it["id"]] < t and not (bypass and is_hinglish(it["query"]))) / len(ans)
    return max(t for t in cand if fr(t) <= MAX_FR)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--choice", default=os.path.join(ROOT, "results_obj3", "_rerank_step9", "choice.json"))
    ap.add_argument("--eval", default=os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    ap.add_argument("--rag", default=os.path.join(ROOT, "eval", "rag_cases.jsonl"))
    ap.add_argument("--run", default=os.path.join(ROOT, "results_obj3", "o3s7a_4b_rag"))
    ap.add_argument("--old", default=os.path.join(ROOT, "results_obj3", "_tau_step8", "fallback.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj3", "_rerank_step9"))
    a = ap.parse_args(argv)
    if not os.path.exists(a.choice):
        print("No choice.json: bench_reranker.py kept the deployed re-ranker, so there is nothing to calibrate.")
        return 0
    with open(a.choice, encoding="utf-8") as f:
        choice = json.load(f)
    with open(a.old, encoding="utf-8") as f:
        old = json.load(f)
    ranks = {r["id"]: r["top"] for r in B.load_jsonl(os.path.join(ROOT, choice["ranks"]))}
    top1 = {i: (t[0][1] if t else float("-inf")) for i, t in ranks.items()}
    dev = [it for it in B.load_jsonl(a.eval) if it["split"] == "dev" and it["id"] in top1]
    hi_ans = [it for it in dev if it["answer_type"] == "fact" and it["language"] == "hinglish"]

    t_nobypass = soft_threshold(dev, top1, bypass=False)
    hi_refused = sum(1 for it in hi_ans if top1[it["id"]] < t_nobypass)
    bypass = hi_refused > MAX_HINGLISH_REFUSED
    t_soft = soft_threshold(dev, top1, bypass)

    cases = {c["id"]: c for c in B.load_jsonl(a.rag)}
    rows = T.rows_from_run(a.run, cases, scores=top1)
    act = [r for r in rows if not r["named"] and not r["entity"] and not (bypass and r["hinglish"])]
    ans = [r for r in act if r["role"] == "answer"]
    ref = [r for r in act if r["role"] == "refuse"]
    cand = sorted({r["score"] for r in act} | {float("-inf")})
    t_hard = max(t for t in cand if not ans or sum(r["score"] < t for r in ans) / len(ans) <= MAX_FR)

    cfg = {"threshold": t_soft, "hard_threshold": t_hard, "hinglish_bypass": bypass, "messages": old["messages"],
           "source": "Objective 3, Step 9: re-ranker " + choice["config"] + " (retrieval/calibrate_step9.py)"}
    with open(os.path.join(a.out, "fallback.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=1, ensure_ascii=False)
    L = ["# Step 9: fallback thresholds for the chosen re-ranker (dev)", "",
         f"Re-ranker: {choice['config']}.", "",
         f"- Without the Hinglish bypass, the 5% rule gives {t_nobypass:.3f}, which refuses {hi_refused} of "
         f"{len(hi_ans)} answerable dev Hinglish questions: bypass **{'kept' if bypass else 'retired'}** "
         f"(retired if at most {MAX_HINGLISH_REFUSED}).",
         f"- Soft threshold (cards shown): {t_soft:.3f} (was {old['threshold']}).",
         f"- Hard threshold (Step 8, store questions): {t_hard:.3f} (was {old.get('hard_threshold')}); refuses "
         f"{sum(r['score'] < t_hard for r in ans)}/{len(ans)} must-answer and {sum(r['score'] < t_hard for r in ref)}/"
         f"{len(ref)} must-refuse dev store questions it can act on."]
    with open(os.path.join(a.out, "calibration.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
