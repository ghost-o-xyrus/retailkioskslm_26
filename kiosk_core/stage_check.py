"""
Objective 5, Step 3: checks of the per-stage logs, the cost of the stage clock, and a first per-stage breakdown.

    python kiosk_core\\stage_check.py --plan harness\\plans\\obj5_step3_stages.json

Rules (fixed before the run):
  (1) coverage: every turn record has its stages; every model request is a model_round stage (or, for a
      forced-answer recovery, a recovery_request sub-stage of checks); every tool call is a tool sub-stage
      (the entity check's search, made with no model, is exempt)
  (2) stage times add up: |unattributed| <= max(5% of the turn's total, 5 ms) in at least 99% of turns
  (3) cost: stage clock on against off (Tier A on CPU, dev speed subset, 2 repeats, alternating): the median of
      the per-case differences in total reply time is at most 50 ms
Reported: the clock's own measured cost per turn, per-stage medians, the sequential policy's worker start.
Writes <results>/_stages_step3/report.md and stages.json.
"""

import argparse
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from kiosk_core.stages import STAGES  # noqa: E402


def records(run_dir):
    p = os.path.join(run_dir, "cases.jsonl")
    if not os.path.exists(p):
        return None
    last = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                last[(r["id"], r.get("repeat", 0))] = r
    return [r for r in last.values() if not r.get("error")]


def turns_of(rec):
    """(stages, stage_summary, model turns, tool calls, total ms) per kiosk turn; dialogues have several."""
    if rec.get("dialogue"):
        return [(t.get("stages"), t.get("stage_summary"), None, t.get("tool_calls") or [],
                 (t.get("metrics") or {}).get("end_to_end_ms")) for t in rec["dialogue"]["turns"]]
    return [(rec.get("stages"), rec.get("stage_summary"), rec.get("turns") or [], rec.get("tool_calls") or [],
             (rec.get("metrics") or {}).get("end_to_end_ms"))]


def check_turn(stages, summary, model_turns, calls, total):
    problems = []
    if not stages:
        return ["no stages"]
    names = [s["stage"] for s in stages]
    if names[0] != "input" or names[-1] != "output":
        problems.append("does not start with input and end with output")
    if any(n not in STAGES for n in names):
        problems.append("unknown stage")
    if model_turns is not None:
        rounds = names.count("model_round")
        recov = sum(1 for s in stages for x in s.get("sub") or [] if x["name"] == "recovery_request")
        if rounds + recov != len(model_turns):
            problems.append(f"model requests {len(model_turns)} vs stages {rounds} + {recov}")
    tool_subs = sum(1 for s in stages for x in s.get("sub") or [] if x["name"].startswith("tool:"))
    need = sum(1 for c in calls if c.get("harness_note") != "entity check")
    if tool_subs != need:
        problems.append(f"tool calls {need} vs tool sub-stages {tool_subs}")
    un = (summary or {}).get("unattributed_ms")
    if un is None or total is None or abs(un) > max(0.05 * total, 5.0):
        problems.append(f"unattributed {un} ms of {total}")
    return problems


def per_case_totals(recs):
    by = {}
    for r in recs:
        t = (r.get("metrics") or {}).get("end_to_end_ms")
        if t is not None:
            by.setdefault(r["id"], []).append(t)
    return {k: statistics.median(v) for k, v in by.items()}


def paired_median(a, b, n=4000, seed=7):
    ids = sorted(set(a) & set(b))
    if not ids:
        return None
    d = [b[i] - a[i] for i in ids]
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choice(d) for _ in d) for _ in range(n))
    return statistics.median(d), meds[int(0.025 * n)], meds[int(0.975 * n)], len(ids)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=os.path.join(ROOT, "harness", "plans", "obj5_step3_stages.json"))
    ap.add_argument("--results", default=None)
    a = ap.parse_args(argv)
    plan = json.load(open(a.plan, encoding="utf-8"))
    res = a.results or os.path.join(ROOT, plan.get("results_dir", "results"))
    runs = {r["name"]: r for r in plan["runs"]}
    L = ["# Step 3: per-stage logs and the stage clock's cost", ""]
    out = {"runs": {}}
    all_turns = bad_turns = sum_ok = n_sum = 0
    examples = []
    stage_ms = {}
    for name, cfg in runs.items():
        recs = records(os.path.join(res, name))
        if recs is None:
            out["runs"][name] = "missing"
            continue
        if cfg.get("stages") is False:
            continue
        cost = []
        for r in recs:
            for st, sm, mt, cl, tot in turns_of(r):
                all_turns += 1
                pr = check_turn(st, sm, mt, cl, tot)
                if pr:
                    bad_turns += 1
                    if len(examples) < 15:
                        examples.append(f"{name} {r['id']} r{r.get('repeat', 0)}: " + "; ".join(pr))
                if sm:
                    n_sum += 1
                    sum_ok += abs(sm["unattributed_ms"]) <= max(0.05 * (tot or 0), 5.0)
                    cost.append(sm.get("instrumentation_ms") or 0)
                    for k, v in sm["by_stage_ms"].items():
                        stage_ms.setdefault(name, {}).setdefault(k, []).append(v)
        out["runs"][name] = {"records": len(recs), "clock_cost_ms_median": statistics.median(cost) if cost else None,
                             "clock_cost_ms_max": max(cost) if cost else None}
    cov_ok = all_turns > 0 and bad_turns == 0
    sum_share = sum_ok / n_sum if n_sum else 0.0
    L += [f"(1) coverage: {all_turns - bad_turns}/{all_turns} turns complete -> **{'met' if cov_ok else 'NOT met'}**",
          f"(2) stage times add up: {sum_ok}/{n_sum} turns ({sum_share:.1%}) within max(5%, 5 ms); rule 99% -> "
          f"**{'met' if sum_share >= 0.99 else 'NOT met'}**"]
    if examples:
        L += ["", "Incomplete turns (first 15):", ""] + [f"- {e}" for e in examples]
    # (3) cost: on against off, paired by case
    L += ["", "## Cost of the stage clock (on against off)", "",
          "| Set | Cases | Total time change, median of per-case differences [95% CI] | Rule |", "|---|---:|---|---|"]
    cost_ok = []
    for name in runs:
        if not name.endswith("_on") or name[:-3] + "_off" not in runs:
            continue
        on, off = records(os.path.join(res, name)), records(os.path.join(res, name[:-3] + "_off"))
        if on is None or off is None:
            L.append(f"| {name[:-3]} | – | not run | missing |")
            cost_ok.append(False)
            continue
        pm = paired_median(per_case_totals(off), per_case_totals(on))
        ok = pm is not None and pm[0] <= 50
        cost_ok.append(ok)
        out.setdefault("cost", {})[name[:-3]] = pm
        L.append(f"| {name[:-3]} | {pm[3]} | {pm[0]:+.0f} ms [{pm[1]:+.0f}, {pm[2]:+.0f}] | {'met' if ok else 'NOT met'} |")
    L.append("")
    L.append(f"(3) cost -> **{'met' if cost_ok and all(cost_ok) else 'NOT met'}**")
    L += ["", "The clock's own measured cost per turn (median / max, ms): " + ", ".join(
        f"{n} {v['clock_cost_ms_median']:.2f} / {v['clock_cost_ms_max']:.2f}" for n, v in out["runs"].items()
        if isinstance(v, dict) and v.get("clock_cost_ms_median") is not None)]
    # per-stage breakdown
    L += ["", "## Where the time goes (median ms per turn, by stage; a stage absent from a turn counts as 0)", "",
          "| Run | " + " | ".join(STAGES) + " |", "|---|" + "---:|" * len(STAGES)]
    for name, by in stage_ms.items():
        n = len((records(os.path.join(res, name)) or []))
        cells = []
        for s in STAGES:
            v = by.get(s, [])
            v = v + [0.0] * max(0, n - len(v))
            cells.append(f"{statistics.median(v):.0f}" if v else "–")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    seq = [n for n, c in runs.items() if c.get("stage_policy") == "sequential"]
    for n in seq:
        mp = os.path.join(res, n, "run_meta.json")
        if os.path.exists(mp):
            sm = json.load(open(mp, encoding="utf-8")).get("stage_manager") or {}
            L.append(f"\nSequential policy ({n}): {sm.get('worker_starts')} worker starts, median start "
                     f"{sm.get('worker_start_ms_median')} ms (reported; Step 8 chooses the policy).")
    out.update(coverage={"turns": all_turns, "incomplete": bad_turns, "met": cov_ok},
               sums={"turns": n_sum, "ok": sum_ok, "share": sum_share, "met": sum_share >= 0.99},
               cost_met=bool(cost_ok) and all(cost_ok))
    d = os.path.join(res, "_stages_step3")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(d, "stages.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
