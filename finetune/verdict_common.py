"""
Objective 4: shared pieces of the Step 6-8 verdict scripts (reading the comparison files, the no-regression rule,
printed tool calls, running the comparisons).
"""

import csv
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "eval"))
from step14_verdicts import paired_fit  # noqa: E402

SETS = (("rag", "all checked", "store questions"), ("v12", "tool cases", "tool cases"), ("fup", "all checked", "follow-ups"))
ALL_SETS = ("rag", "v12", "fup", "dlg")
PRINTED_FLAGS = {"tool_call_as_text", "tool_text_seen"}
NOISE = os.path.join(ROOT, "results_obj3", "_noise_floor", "noise.json")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def records(R, run, repeat0=True):
    """{(case id, repeat): record} of a run, the last record winning (resumed runs); None if the run is missing."""
    p = os.path.join(R, run, "cases.jsonl")
    if not os.path.exists(p):
        return None
    last = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if repeat0 and r.get("repeat", 0) != 0:
                    continue
                last[(r["id"], r.get("repeat", 0))] = r
    return last


def printed(R, run):
    """Replies of repeat 0 where the model wrote a tool call as text; None if the run is missing."""
    recs = records(R, run)
    if recs is None:
        return None
    return sum(1 for r in recs.values() if not r.get("error") and set(r.get("flags") or []) & PRINTED_FLAGS)


def read_compare(R, sub):
    p = os.path.join(R, sub, "compare.json")
    if not os.path.exists(p):
        return {}, {}, {}
    q = load(p)
    return ({(r["base"], r["new"], r["subset"]): r for r in q["rows"]},
            {(s["base"], s["new"]): s for s in q.get("speed", [])},
            {(w["base"], w["new"]): w for w in q.get("waits", [])})


def read_dialogues(R, sub):
    d = os.path.join(R, sub)
    dsum = load(os.path.join(d, "summary.json")) if os.path.exists(os.path.join(d, "summary.json")) else {}
    drows = []
    if os.path.exists(os.path.join(d, "dialogues.csv")):
        with open(os.path.join(d, "dialogues.csv"), encoding="utf-8-sig") as f:
            drows = list(csv.DictReader(f))
    return dsum, drows


def dialogue_check(dsum, drows, base, new):
    """The Step 6 dialogue targets of Objective 3, and fit not lower than the baseline (paired interval)."""
    fin = dsum.get(new)
    if not fin:
        return "missing", None, None
    if not dsum.get(base):
        return "missing (no baseline)", fin, None
    pf = paired_fit(drows, base, new)
    if pf is None:
        return "missing (no paired dialogues)", fin, None
    ok = (fin["recommended"] or 0) >= 0.95 and (fin["slots2_share"] or 0) >= 0.85 \
        and (fin["questions_max"] if fin["questions_max"] is not None else 99) <= 2 \
        and (fin["fit_mean"] or 0) >= 0.90 and pf[2] >= 0
    return ("met" if ok else "not met"), fin, pf


def no_regression(rows, dsum, drows, base, new):
    """H4-style rule of Step 6, for run prefixes base and new ('o4s6_2b_base' -> o4s6_2b_base_rag, ...).
    Returns (holds, checks, detail)."""
    c, detail, sets_ok = {}, {}, True
    for s, sub, label in SETS:
        r = rows.get((f"{base}_{s}", f"{new}_{s}", sub))
        c[label] = r["verdict"] if r else "missing"
        sets_ok &= bool(r) and r["verdict"] in ("better", "tie")
        detail[label] = r
    dv, fin, pf = dialogue_check(dsum, drows, f"{base}_dlg", f"{new}_dlg")
    c["dialogues"] = dv
    detail["dialogue_fit_change"] = None if pf is None else [round(100 * x, 1) for x in pf[:3]] + [pf[3]]
    hb = hn = hN = have = 0
    for s, _, _ in SETS:
        r = rows.get((f"{base}_{s}", f"{new}_{s}", "language: hinglish"))
        if r:
            have += 1
            hb += r["base_rate"] * r["n"]
            hn += r["new_rate"] * r["n"]
            hN += r["n"]
    if not hN:                         # pooled over the sets that have Hinglish cases
        c["hinglish"] = "missing"
        detail["hinglish_pooled"] = None
    else:
        d = 100 * (hn - hb) / hN
        detail["hinglish_pooled"] = {"n": hN, "base": hb / hN, "new": hn / hN, "diff_pts": d}
        c["hinglish"] = "ok" if d >= -5 else "fell"
    return sets_ok and dv == "met" and c["hinglish"] == "ok", c, detail


def printed_check(R, run_prefix, sets=ALL_SETS):
    """At most 1 printed tool call in each run (H1)."""
    p = {s: printed(R, f"{run_prefix}_{s}") for s in sets}
    if None in p.values():
        return "missing", p
    return ("met" if all(v <= 1 for v in p.values()) else "not met"), p


def run_compare(R, pairs, out_sub, dialogue_runs=(), dialogue_pairs=(), dialogue_out=None):
    """Run eval/compare_dev.py (with --all-hinglish and the Objective 3 noise bounds) and eval/score_dialogues.py."""
    import compare_dev
    argv = []
    for b, n in pairs:
        argv += ["--pair", os.path.join(R, b), os.path.join(R, n)]
    if os.path.exists(NOISE):
        argv += ["--noise", NOISE]
    else:
        print(f"note: {NOISE} not found; verdicts without the noise bound", file=sys.stderr)
    compare_dev.main(argv + ["--all-hinglish", "--out", os.path.join(R, out_sub)])
    if dialogue_runs:
        import score_dialogues
        dargv = [os.path.join(R, d) for d in dialogue_runs]
        for b, n in dialogue_pairs:
            dargv += ["--pair", os.path.join(R, b), os.path.join(R, n)]
        score_dialogues.main(dargv + ["--out", os.path.join(R, dialogue_out)])


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt_rows(rows, base, new, label=None):
    """Markdown rows for the three single-turn sets of one pair of run prefixes."""
    out = []
    for s, sub, lab in SETS:
        r = rows.get((f"{base}_{s}", f"{new}_{s}", sub))
        if r is None:
            out.append(f"| {label or new} | {lab} | – | – | – | not run | – | missing |")
        else:
            out.append(f"| {label or new} | {lab} | {r['n']} | {r['base_rate']:.1%} | {r['new_rate']:.1%} | "
                       f"{r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {r['mcnemar_p']:.3g} | "
                       f"{r['verdict']} |")
    return out
