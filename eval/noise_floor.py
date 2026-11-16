"""
Objective 3, Step 2: how much do scores move between identical greedy repeats?

    python eval\\noise_floor.py results_obj3\\o3s1sp_*

Step 1 found that greedy repeats of the same case gave a different reply 7-30% of the time (server-side numerics,
e.g. prompt-cache splits). A later dev comparison is only meaningful if its difference is bigger than this noise.
For every run with 2+ repeats, each record is scored with the normal automatic checks:
  v1.1 / v1.2 tool cases   eval/score.py's pass/fail
  retrieval questions      eval/score_rag.py's automatic check (answer facts, decline, or no/not-listed)
and the report gives:
  flip rate        share of cases whose pass/fail is not the same in every repeat
  discordance d    share of cases that differ between two repeats (mean over repeat pairs)
  noise bound      1.96 * sqrt(d / n) in points: the largest pass-rate difference that pure repeat noise would
                   produce 95% of the time between two runs of n cases (normal approximation to the paired
                   difference when each case flips independently). Given for the subset size and the full dev sizes.
Pre-registered use (Objective 3 experiment design): a dev change is "better" or "worse" only if its paired
difference is larger than the noise bound for that set and model AND its paired bootstrap interval excludes 0.
Writes <out>/report.md and <out>/noise.json.
"""

import argparse
import glob
import itertools
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import score as S          # noqa: E402
import score_rag as SR     # noqa: E402

DEV_SIZES = {"rag": 151, "tools": 60}   # dev store questions; dev v1.1 tool-mode cases


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def outcomes(run_dir, chunks, eval_cache):
    meta = {}
    with open(os.path.join(run_dir, "run_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    ef = os.path.join(ROOT, meta.get("eval_file", "").replace("\\", "/"))
    if ef not in eval_cache:
        eval_cache[ef] = {c["id"]: c for c in load_jsonl(ef)}
    cases = eval_cache[ef]
    kind = "rag" if os.path.basename(ef).startswith("rag_cases") else "tools"
    by_case = {}
    replies = {}
    for r in load_jsonl(os.path.join(run_dir, "cases.jsonl")):
        if r.get("error") or r["id"] not in cases:
            continue
        c = cases[r["id"]]
        if kind == "rag":
            a = SR.auto(c, SR.scored_reply(r), chunks)
            if not a["checked"]:
                continue
            ok = bool(a["correct"])
        else:
            if c["mode"] != "tools":
                continue
            ok = bool(S.score_case(c, r)["passed"])
        by_case.setdefault(r["id"], {})[r["repeat"]] = ok
        replies.setdefault(r["id"], {})[r["repeat"]] = r.get("final_reply") or ""
    reps = sorted({k for v in by_case.values() for k in v})
    full = {cid: v for cid, v in by_case.items() if len(v) == len(reps)}
    return meta, kind, reps, full, {cid: replies[cid] for cid in full}


def analyse(run_dir, chunks, eval_cache):
    meta, kind, reps, cases, replies = outcomes(run_dir, chunks, eval_cache)
    n = len(cases)
    if len(reps) < 2 or n == 0:
        return None
    flips = sum(1 for v in cases.values() if len(set(v.values())) > 1)
    pair_d = []
    for a, b in itertools.combinations(reps, 2):
        pair_d.append(sum(1 for v in cases.values() if v[a] != v[b]) / n)
    d = sum(pair_d) / len(pair_d)
    rates = [sum(v[r] for v in cases.values()) / n for r in reps]
    text_changed = sum(1 for v in replies.values() if len(set(v.values())) > 1) / n
    bound = lambda m: 196 * math.sqrt(d / m) if m else None   # noqa: E731  (points)
    return {"run": os.path.basename(os.path.normpath(run_dir)), "model": meta.get("model"),
            "backend": meta.get("backend"), "kind": kind, "cases": n, "repeats": len(reps),
            "pass_by_repeat": rates, "flip_rate": flips / n, "discordance": d,
            "reply_text_changed": text_changed, "noise_bound_pts_subset": bound(n),
            "noise_bound_pts_full_dev": bound(DEV_SIZES[kind])}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", default=None, help="Default: <first run's parent>/_noise_floor")
    a = ap.parse_args(argv)
    dirs = sorted({d for p in a.runs for d in glob.glob(p)
                   if os.path.isdir(d) and os.path.exists(os.path.join(d, "cases.jsonl"))})
    if not dirs:
        print("No run folders found.")
        return 1
    out = a.out or os.path.join(os.path.dirname(os.path.normpath(dirs[0])), "_noise_floor")
    os.makedirs(out, exist_ok=True)
    chunks = {c["id"]: c for c in load_jsonl(os.path.join(ROOT, "knowledge", "corpus.jsonl"))}
    res, cache = [], {}
    for d in dirs:
        r = analyse(d, chunks, cache)
        if r is None:
            print(f"  skipped (fewer than 2 repeats): {d}")
            continue
        res.append(r)
        print(f"  {r['run']}: flip rate {r['flip_rate']:.1%}, noise bound on full dev "
              f"{r['noise_bound_pts_full_dev']:.1f} points")
    if not res:
        return 1
    L = ["# Noise floor: identical greedy repeats (Objective 3, Step 2)", "",
         "Pass/fail from the automatic checks. Flip rate = cases whose outcome is not the same in every repeat. "
         "Noise bound = 1.96 × √(d / n): the pass-rate difference that repeat noise alone stays under 95% of the "
         "time, for n cases with discordance d.", "",
         "| Run | Model | Set | Cases × repeats | Pass rate per repeat | Reply text changed | Flip rate "
         "| Discordance d | Noise bound, this subset | Noise bound, full dev |",
         "|---|---|---|---:|---|---:|---:|---:|---:|---:|"]
    for r in res:
        L.append(f"| {r['run']} | {r['model']} | {r['kind']} | {r['cases']} × {r['repeats']} | "
                 + " / ".join(f"{x:.1%}" for x in r["pass_by_repeat"])
                 + f" | {r['reply_text_changed']:.0%} | {r['flip_rate']:.1%} | {r['discordance']:.1%} "
                 f"| ±{r['noise_bound_pts_subset']:.1f} pts | ±{r['noise_bound_pts_full_dev']:.1f} pts "
                 f"(n={DEV_SIZES[r['kind']]}) |")
    L += ["", "Rule for later steps: a dev difference counts only if it is larger than the full-dev noise bound for "
          "that model and set, and its paired bootstrap interval excludes 0.", ""]
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(out, "noise.json"), "w", encoding="utf-8") as f:
        json.dump({r["run"]: r for r in res}, f, indent=1)
    print(f"Wrote {os.path.join(out, 'report.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
