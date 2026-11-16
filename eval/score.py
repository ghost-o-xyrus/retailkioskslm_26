"""
Score harness runs against the eval set (Objective 1, Step 6).

    python eval\\score.py results\\*_q4_k_m_vulkan                 # Stage 1, test split (default)
    python eval\\score.py results\\*_q4_k_m_vulkan --split all
    python eval\\score.py results\\a results\\b --eval eval\\eval_set_v1.1.jsonl   # Stage 3

Writes to results/_scores/:
    report.md              the tables below, ready to paste into the write-up
    summary.csv            one row per run: every metric with its 95% confidence interval
    by_category.csv        pass rate per run x category
    cases_<run>.csv        every case: which checks applied, which passed, the reply (for reading failures)
    audit_<run>.csv        a random sample of failed cases to read by hand before trusting the numbers
    pairwise.csv           every pair of runs: difference in pass rate, paired bootstrap CI, McNemar p-value

Checks per case (only the ones that apply to that case are counted):
    tool_ok          the required tool call(s) were made with matching arguments (eval/checks.calls_satisfy)
    no_tool_ok       no tool was called when none should be
    format_ok        every tool call was valid JSON naming a real tool, and no tool call was written as text
    facts_ok         every must_include group appears in the final reply
    forbidden_ok     no must_not_include phrase appears
    clarify_ok       the reply asks a question about at least one missing slot
    grounded_ok      the reply names a product returned by the tools
A case passes when every applicable check passes. Errored cases fail.
"""

import argparse
import csv
import glob
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

from checks import (calls_satisfy, call_matches, check_must_include, check_must_not_include,  # noqa: E402
                    asks_about_slots, text_has)

CHECKS = ["tool_ok", "no_tool_ok", "format_ok", "facts_ok", "forbidden_ok", "clarify_ok", "grounded_ok"]
ID_RE_WORDS = 3


# --------------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------------

def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value from discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired_bootstrap(a, b, n_boot=4000, seed=0):
    """a, b: lists of 0/1 for the same cases. Returns (diff, lo, hi) of mean(a) - mean(b)."""
    rng = random.Random(seed)
    n = len(a)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        diffs.append(sum(a[i] - b[i] for i in idx) / n)
    diffs.sort()
    return (sum(a) - sum(b)) / n, diffs[int(0.025 * n_boot)], diffs[int(0.975 * n_boot) - 1]


# --------------------------------------------------------------------------
# Per-case scoring
# --------------------------------------------------------------------------

def result_products(tool_calls):
    """Product IDs and short names the tools returned (for the grounded_ok check)."""
    ids, names = set(), set()

    def walk(o):
        if isinstance(o, dict):
            if "product_id" in o and isinstance(o["product_id"], str):
                ids.add(o["product_id"])
            if "name" in o and isinstance(o["name"], str) and o["name"].startswith("Veyra "):
                words = o["name"].split()
                names.add(" ".join(words[1:ID_RE_WORDS]))  # e.g. "Classique Atlas"
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for c in tool_calls:
        walk(c.get("result"))
    return ids, names


def shown_styles(rec):
    """Design ids whose product cards were actually shown with the customer's message (Objective 2 retrieval)."""
    ret = (rec or {}).get("retrieval") or {}
    if ret.get("condition") not in ("always", "oracle") or ret.get("fallback_applied"):
        return set()
    return {c.split(":", 1)[1] for c in (ret.get("chunk_ids") or []) if c.startswith("product:")}


_TOOLS = []


def _mock_tools():
    if not _TOOLS:
        sys.path.insert(0, ROOT)
        from tools import mock_tools  # noqa: E402
        _TOOLS.append(mock_tools)
    return _TOOLS[0]


def card_satisfies(spec, shown):
    """A required get_product_details call counts as done when that watch's card was already shown."""
    if spec["name"] != "get_product_details" or not shown:
        return False
    m = spec.get("args", {}).get("product_id") or {}
    mt = _mock_tools()
    for v in m.get("equals_any", []):
        if any(k["style_id"] in shown for k in mt._resolve(str(v)) or []):
            return True
    return False


def card_names(shown):
    """Ids and short names of the watches on the shown cards (for grounded_ok with credit)."""
    ids, names = set(shown), set()
    for k in _mock_tools()._load()["skus"].values():
        if k["style_id"] in shown:
            ids.add(k["sku"])
            words = k["product_name"].split()
            if words and words[0] == "Veyra":
                names.add(" ".join(words[1:ID_RE_WORDS]))
    return ids, names


def score_case(case, rec, credit_shown=False):
    """credit_shown (Objective 3, Step 2): an answer taken from a product card shown with the message counts. A
    required get_product_details call is treated as made when that watch's card was shown, and naming a watch from
    a shown card satisfies grounded_ok. Stock, comparison and search calls still have to be made."""
    e = case["expected"]
    out = {c: None for c in CHECKS}
    if rec is None or rec.get("error"):
        out["passed"] = False
        out["error"] = (rec or {}).get("error", "missing")
        return out
    reply = "" if "empty_reply_fallback" in (rec.get("flags") or []) else (rec.get("final_reply") or "")
    calls = [{"name": c["name"], "arguments": c["arguments"]} for c in rec.get("tool_calls", [])]

    if case["mode"] == "tools":
        out["format_ok"] = (all(c["arguments_valid_json"] and c["known_tool"] for c in rec.get("tool_calls", []))
                            and "tool_call_as_text" not in rec.get("flags", []))
    shown = shown_styles(rec) if credit_shown else set()
    out["credited"] = []
    if e.get("required_calls"):
        out["tool_ok"] = calls_satisfy(calls, e["required_calls"]) is not None
        if not out["tool_ok"] and shown and any(
                all(any(call_matches(c, sp) for c in calls) or card_satisfies(sp, shown) for sp in opt)
                for opt in e["required_calls"]):
            out["tool_ok"] = True
            out["credited"].append("tool_ok")
    if e.get("no_tool_calls"):
        out["no_tool_ok"] = len(calls) == 0
    if e.get("must_include"):
        got, total, _ = check_must_include(reply, e["must_include"])
        out["facts_ok"] = got == total
    if e.get("must_not_include"):
        out["forbidden_ok"] = not check_must_not_include(reply, e["must_not_include"])
    if e.get("clarify_slots"):
        out["clarify_ok"], _ = asks_about_slots(reply, e["clarify_slots"])
    if e.get("must_mention_tool_result"):
        ids, names = result_products(rec.get("tool_calls", []))
        out["grounded_ok"] = bool(ids or names) and (any(text_has(reply, [i]) for i in ids)
                                                     or any(text_has(reply, [n]) for n in names if n))
        if not out["grounded_ok"] and shown:
            ids, names = card_names(shown)
            if any(text_has(reply, [i]) for i in ids) or any(text_has(reply, [n]) for n in names if n):
                out["grounded_ok"] = True
                out["credited"].append("grounded_ok")
    if not reply.strip() and e["behaviour"] != "handoff":
        out["facts_ok"] = False if out["facts_ok"] is not None or e["behaviour"] in ("answer", "refuse") else out["facts_ok"]
    applicable = [out[c] for c in CHECKS if out[c] is not None]
    out["passed"] = bool(applicable) and all(applicable)
    if not applicable:  # e.g. a plain greeting with no checks: pass if it replied at all
        out["passed"] = bool(reply.strip())
    return out


# --------------------------------------------------------------------------

def load_run(run_dir):
    recs = {}
    with open(os.path.join(run_dir, "cases.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            recs[(r["id"], r["repeat"])] = r
    meta = {}
    mp = os.path.join(run_dir, "run_meta.json")
    if os.path.exists(mp):
        with open(mp, encoding="utf-8") as f:
            meta = json.load(f)
    return recs, meta


def fmt_ci(p, lo, hi):
    if p is None:
        return "-"
    return f"{100 * p:.0f}% [{100 * lo:.0f}-{100 * hi:.0f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="Run folders (globs allowed)")
    ap.add_argument("--eval", default=None, help="Eval file (default: the one recorded in each run's run_meta.json)")
    ap.add_argument("--split", default="test", choices=["test", "dev", "all"])
    ap.add_argument("--mode", default="all", choices=["all", "tools", "grounded"],
                    help="Only cases of this mode (Objective 2's regression check uses the tools cases)")
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "_scores"))
    ap.add_argument("--audit", type=int, default=15, help="Failed cases per run to sample for reading")
    ap.add_argument("--credit-shown-cards", action="store_true",
                    help="Objective 3: count answers taken from product cards shown with the message (see score_case)")
    a = ap.parse_args()

    dirs = []
    for pattern in a.runs:
        dirs += [d for d in glob.glob(pattern) if os.path.isdir(d) and os.path.exists(os.path.join(d, "cases.jsonl"))]
    dirs = sorted(set(dirs))
    if not dirs:
        print("No run folders with cases.jsonl found.")
        return 1
    os.makedirs(a.out, exist_ok=True)

    eval_cache, runs = {}, []
    for d in dirs:
        recs, meta = load_run(d)
        ef = a.eval or os.path.join(ROOT, meta.get("eval_file", "eval/eval_set.jsonl").replace("\\", "/"))
        if ef not in eval_cache:
            with open(ef, encoding="utf-8") as f:
                eval_cache[ef] = {c["id"]: c for c in map(json.loads, f)}
        cases = eval_cache[ef]
        repeats = sorted({rep for (_, rep) in recs}) or [0]
        wanted = [cid for cid in {cid for (cid, _) in recs} if (a.split == "all" or cases[cid]["split"] == a.split)
                  and (a.mode == "all" or cases[cid]["mode"] == a.mode)]
        wanted.sort()
        rows = []
        for cid in wanted:
            for rep in repeats:
                s = score_case(cases[cid], recs.get((cid, rep)), a.credit_shown_cards)
                s["credited"] = ",".join(s.get("credited") or [])
                rows.append({"id": cid, "repeat": rep, "category": cases[cid]["category"],
                             "subcategory": cases[cid]["subcategory"], "behaviour": cases[cid]["expected"]["behaviour"],
                             "language": cases[cid]["language"], "paired_with": cases[cid].get("paired_with"), **s,
                             "user": cases[cid]["messages"][-1]["content"],
                             "tool_calls": json.dumps([{"name": c["name"], "arguments": c["arguments"]}
                                                       for c in (recs.get((cid, rep)) or {}).get("tool_calls", [])],
                                                      ensure_ascii=False),
                             "reply": ((recs.get((cid, rep)) or {}).get("final_reply") or "")[:600],
                             "flags": ",".join((recs.get((cid, rep)) or {}).get("flags", []))})
        runs.append({"name": os.path.basename(d.rstrip("/\\")), "meta": meta, "rows": rows, "repeats": repeats})

    # ---- per-run metrics ----
    summary = []
    for r in runs:
        rows0 = [x for x in r["rows"] if x["repeat"] == r["repeats"][0]]
        n = len(rows0)
        m = {"run": r["name"], "model": r["meta"].get("model"), "quant": r["meta"].get("quant"),
             "backend": r["meta"].get("backend"), "cases": n, "repeats": len(r["repeats"])}
        k = sum(x["passed"] for x in rows0)
        m["pass"] = wilson(k, n)
        for c in CHECKS:
            app = [x[c] for x in rows0 if x[c] is not None]
            m[c] = wilson(sum(app), len(app)) + (len(app),)
        m["errors"] = sum(1 for x in rows0 if x.get("error"))
        if len(r["repeats"]) > 1:
            by_case = {}
            for x in r["rows"]:
                by_case.setdefault(x["id"], []).append(x["passed"])
            all_pass = sum(all(v) for v in by_case.values())
            m["pass_hat_k"] = wilson(all_pass, len(by_case))
            m["pass_avg_over_repeats"] = sum(x["passed"] for x in r["rows"]) / len(r["rows"])
        summary.append(m)

    # ---- write per-case and audit files ----
    for r in runs:
        fields = ["id", "repeat", "category", "subcategory", "behaviour", "language", "passed"] + CHECKS + \
                 ["credited", "error", "flags", "user", "tool_calls", "reply"]
        with open(os.path.join(a.out, f"cases_{r['name']}.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(r["rows"])
        fails = [x for x in r["rows"] if not x["passed"]]
        random.Random(1).shuffle(fails)
        with open(os.path.join(a.out, f"audit_{r['name']}.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields + ["your_verdict (scorer right? y/n)"], extrasaction="ignore")
            w.writeheader()
            w.writerows(fails[:a.audit])

    with open(os.path.join(a.out, "summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        head = ["run", "model", "quant", "backend", "cases", "errors", "pass", "pass_lo", "pass_hi"]
        for c in CHECKS:
            head += [c, c + "_lo", c + "_hi", c + "_n"]
        head += ["pass_hat_k", "pass_avg_over_repeats"]
        w.writerow(head)
        for m in summary:
            row = [m["run"], m["model"], m["quant"], m["backend"], m["cases"], m["errors"], *m["pass"]]
            for c in CHECKS:
                row += list(m[c])
            row += [m.get("pass_hat_k", (None,))[0], m.get("pass_avg_over_repeats")]
            w.writerow([round(v, 4) if isinstance(v, float) else v for v in row])

    cats = sorted({x["category"] for r in runs for x in r["rows"]})
    with open(os.path.join(a.out, "by_category.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run"] + [f"{c} (n)" for c in cats])
        for r in runs:
            rows0 = [x for x in r["rows"] if x["repeat"] == r["repeats"][0]]
            line = [r["name"]]
            for c in cats:
                xs = [x["passed"] for x in rows0 if x["category"] == c]
                line.append(f"{100 * sum(xs) / len(xs):.0f}% ({len(xs)})" if xs else "-")
            w.writerow(line)

    # ---- pairwise comparisons (repeat 0, shared cases) ----
    pair_rows = []
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            A = {x["id"]: int(x["passed"]) for x in runs[i]["rows"] if x["repeat"] == runs[i]["repeats"][0]}
            B = {x["id"]: int(x["passed"]) for x in runs[j]["rows"] if x["repeat"] == runs[j]["repeats"][0]}
            shared = sorted(set(A) & set(B))
            if not shared:
                continue
            a_, b_ = [A[s] for s in shared], [B[s] for s in shared]
            d, lo, hi = paired_bootstrap(a_, b_)
            bb = sum(1 for x, y in zip(a_, b_) if x and not y)
            cc = sum(1 for x, y in zip(a_, b_) if y and not x)
            pair_rows.append([runs[i]["name"], runs[j]["name"], len(shared), round(100 * d, 1), round(100 * lo, 1),
                              round(100 * hi, 1), bb, cc, round(mcnemar_exact(bb, cc), 4),
                              "yes" if lo > 0 or hi < 0 else "no (tie)"])
    with open(os.path.join(a.out, "pairwise.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["run_a", "run_b", "shared_cases", "diff_pct_points", "ci_lo", "ci_hi", "a_only_pass", "b_only_pass",
                    "mcnemar_p", "different?"])
        w.writerows(pair_rows)

    # ---- report ----
    summary.sort(key=lambda m: -(m["pass"][0] or 0))
    lines = [f"# Scores ({a.split} split{'' if a.mode == 'all' else ', ' + a.mode + ' cases'})", "",
             "Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).", "",
             *([("Shown-card credit ON: a required get_product_details call counts as made, and naming a watch "
                 "counts as grounded, when that watch's card was shown with the message. Cases changed by the "
                 "credit, per run: " + ", ".join(f"{r['name']} {sum(1 for x in r['rows'] if x.get('credited') and x['repeat'] == r['repeats'][0])}"
                                                 for r in runs)), ""] if a.credit_shown_cards else []),
             "| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in summary:
        cell = lambda c: fmt_ci(*m[c][:3]) + f" (n={m[c][3]})" if m[c][3] else "-"  # noqa: E731
        lines.append(f"| {m['run']} | {m['cases']} | **{fmt_ci(*m['pass'])}** | {cell('tool_ok')} | {cell('format_ok')} | "
                     f"{cell('no_tool_ok')} | {cell('facts_ok')} | {cell('forbidden_ok')} | {cell('clarify_ok')} | "
                     f"{cell('grounded_ok')} | {m['errors']} |")
    if any("pass_hat_k" in m for m in summary):
        lines += ["", "| Run | Repeats | Mean pass over repeats | pass^k (all repeats pass) |", "|---|---|---|---|"]
        for m in summary:
            if "pass_hat_k" in m:
                lines.append(f"| {m['run']} | {m['repeats']} | {100 * m['pass_avg_over_repeats']:.0f}% | {fmt_ci(*m['pass_hat_k'])} |")
    lines += ["", "## Pass rate by category", ""]
    with open(os.path.join(a.out, "by_category.csv"), encoding="utf-8") as f:
        cat_rows = list(csv.reader(f))
    lines.append("| " + " | ".join(cat_rows[0]) + " |")
    lines.append("|" + "---|" * len(cat_rows[0]))
    for row in cat_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    if pair_rows:
        lines += ["", "## Pairwise differences (same cases)", "",
                  "Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. "
                  "If the CI includes 0, treat the two as tied.", "",
                  "| A | B | Cases | A − B | 95% CI | McNemar p | Different? |", "|---|---|---|---|---|---|---|"]
        for p in sorted(pair_rows, key=lambda p: -abs(p[3])):
            lines.append(f"| {p[0]} | {p[1]} | {p[2]} | {p[3]:+.1f} | [{p[4]:+.1f}, {p[5]:+.1f}] | {p[8]} | {p[9]} |")
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nFiles written to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
