"""
Objective 3, Step 1: where each turn's time goes, and the baseline every later step is compared with.

    python harness\\time_split.py results_obj3\\o3s1_*                     # all Step 1 runs
    python harness\\time_split.py results_obj3\\o3s1sp_* --out results_obj3\\_time_split_speed
    python harness\\time_split.py results_obj2\\s8sp_*                       # works on Objective 2 runs too

Per run, from the per-request `turns` that run_eval.py already logs:
  rounds        model requests per case (1 = answered straight away), and how they are distributed
  tokens        read in total (prompt tokens actually computed, i.e. not from cache); read with the customer's
                message (round 1, including any retrieved cards); read back from tool outputs (rounds 2+);
                written as tool calls; written as the answer. Real context and tool-output token counts too,
                when the run has them (run_eval.py --count-tokens, on by default from Objective 3).
  time split    shares of the summed case time: retrieval, reading the message, reading tool outputs, writing
                tool calls, writing the answer, and everything else (tool execution, HTTP, template rendering)
  speeds        v_read and v_write over all requests, plus a least-squares fit  ms = a + n / v  that separates
                the fixed cost per request (a) from the per-token cost
  formula       the plan's first-word model
                    T = t_fetch + sum over tool rounds (w / v_write + n / v_read) + n_final / v_read
                evaluated per case with the run's own speeds, against the measured wait (median absolute error)
  waits         first word and full reply, p50 / p90, with a bootstrap 95% interval on the median
  repeats       when a run has repeats: per-case spread of the first-word wait, and whether greedy replies matched
  cache         share of first requests that did not reuse the cached system + tools prefix
  waste         repeated identical tool calls, more than one call_staff in a case, re-fetches of shown cards,
                tool errors, cases that hit the round limit
Writes <out>/report.md, <out>/summary.json (the numbers later steps compare against) and <out>/cases_split.csv.
"""

import argparse
import csv
import glob
import json
import os
import random
import statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PARTS = ["retrieval", "read_message", "read_tool_outputs", "write_calls", "write_answer", "other"]
PART_LABEL = {"retrieval": "Retrieval", "read_message": "Read message (+ cards)",
              "read_tool_outputs": "Read tool outputs", "write_calls": "Write tool calls",
              "write_answer": "Write answer", "other": "Other (tools, HTTP, template)"}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def pctl(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    pos = q * (len(xs) - 1)
    lo, hi = int(pos), min(int(pos) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def boot_median_ci(xs, n_boot=2000, seed=0):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return (None, None)
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choices(xs, k=len(xs))) for _ in range(n_boot))
    return meds[int(0.025 * n_boot)], meds[int(0.975 * n_boot) - 1]


def ols(xs, ys):
    """y = a + b x. Returns (a, b) or (None, None)."""
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pts) < 3:
        return None, None
    mx = sum(x for x, _ in pts) / len(pts)
    my = sum(y for _, y in pts) / len(pts)
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None, None
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    return my - b * mx, b


def f1(x, nd=1):
    return "–" if x is None else f"{x:,.{nd}f}"


def sec(ms):
    return "–" if ms is None else f"{ms / 1000:.1f} s"


def call_key(c):
    return c.get("name"), json.dumps(c.get("arguments"), sort_keys=True) if c.get("arguments") is not None \
        else c.get("arguments_raw")


# --------------------------------------------------------------------------
# Per case
# --------------------------------------------------------------------------

def split_case(r):
    turns = r.get("turns") or []
    m = r.get("metrics") or {}
    retrieval_ms = m.get("retrieval_ms") or 0.0
    total = m.get("end_to_end_ms") or 0.0
    if not turns:   # hard fallback answered without the model
        return {"rounds": 0, "retrieval": retrieval_ms, "read_message": 0, "read_tool_outputs": 0,
                "write_calls": 0, "write_answer": 0, "other": max(0.0, total - retrieval_ms),
                "tok_read": 0, "tok_read_message": 0, "tok_read_tools": 0, "tok_write_calls": 0, "tok_answer": 0,
                "total_ms": total, "first_ms": m.get("first_visible_ms") or total, "answered": False,
                "requests": []}
    final_is_answer = (turns[-1].get("n_tool_calls") or 0) == 0
    d = {"rounds": len(turns), "retrieval": retrieval_ms, "answered": final_is_answer, "requests": []}
    d["read_message"] = turns[0].get("prompt_ms") or 0.0
    d["read_tool_outputs"] = sum(t.get("prompt_ms") or 0.0 for t in turns[1:])
    d["write_calls"] = sum(t.get("predicted_ms") or 0.0 for t in turns if t.get("n_tool_calls"))
    d["write_answer"] = (turns[-1].get("predicted_ms") or 0.0) if final_is_answer else 0.0
    d["tok_read_message"] = turns[0].get("prompt_n") or 0
    d["tok_read_tools"] = sum(t.get("prompt_n") or 0 for t in turns[1:])
    d["tok_read"] = d["tok_read_message"] + d["tok_read_tools"]
    d["tok_write_calls"] = sum(t.get("predicted_n") or 0 for t in turns if t.get("n_tool_calls"))
    d["tok_answer"] = (turns[-1].get("predicted_n") or 0) if final_is_answer else 0
    known = d["retrieval"] + d["read_message"] + d["read_tool_outputs"] + d["write_calls"] + d["write_answer"]
    d["other"] = max(0.0, total - known)
    d["total_ms"] = total
    d["first_ms"] = m.get("first_visible_ms")
    d["cache_n0"] = turns[0].get("cache_n")
    for t in turns:
        d["requests"].append((t.get("prompt_n"), t.get("prompt_ms"), t.get("predicted_n"), t.get("predicted_ms")))
    return d


def formula_first_word(r, d, v_read, v_write):
    """The plan's model, with the run's own speeds (tokens per ms)."""
    turns = r.get("turns") or []
    if not turns or not v_read or not v_write:
        return None
    t = d["retrieval"]
    for x in turns[:-1]:
        t += (x.get("predicted_n") or 0) / v_write + (x.get("prompt_n") or 0) / v_read
    t += (turns[-1].get("prompt_n") or 0) / v_read
    if turns[-1].get("n_tool_calls"):   # round limit reached: the last request also wrote calls
        t += (turns[-1].get("predicted_n") or 0) / v_write
    return t


def waste(r):
    calls = r.get("tool_calls") or []
    keys = Counter(call_key(c) for c in calls)
    return {"dup_calls": sum(n - 1 for n in keys.values() if n > 1),
            "staff_calls_over_1": max(0, sum(1 for c in calls if c.get("name") == "call_staff") - 1),
            "deduped_fetches": sum(1 for c in calls if c.get("deduped")),
            "tool_errors": sum(1 for c in calls if c.get("result_error")),
            "max_rounds": int("max_rounds_reached" in (r.get("flags") or [])),
            "empty_replies": int(not (r.get("final_reply") or "").strip()
                                 or "empty_reply_fallback" in (r.get("flags") or [])),
            "guard_notes": sum(1 for c in calls if c.get("guard")),
            "n_calls": len(calls)}


# --------------------------------------------------------------------------
# Per run
# --------------------------------------------------------------------------

def load_run(run_dir):
    path = os.path.join(run_dir, "cases.jsonl")
    if not os.path.exists(path):
        return None, []
    meta = {}
    mp = os.path.join(run_dir, "run_meta.json")
    if os.path.exists(mp):
        with open(mp, encoding="utf-8") as f:
            meta = json.load(f)
    recs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("error"):
                continue
            recs[(r["id"], r["repeat"])] = r   # the last record of a resumed case wins
    return meta, list(recs.values())


def analyse(run_dir, prefix_tokens):
    meta, recs = load_run(run_dir)
    if not recs:
        return None
    name = os.path.basename(os.path.normpath(run_dir))
    splits = [(r, split_case(r)) for r in recs]
    reqs = [q for _, d in splits for q in d["requests"]]
    pn, pm, gn, gm = zip(*reqs) if reqs else ([], [], [], [])
    sum_pn, sum_pm = sum(x or 0 for x in pn), sum(x or 0 for x in pm)
    sum_gn, sum_gm = sum(x or 0 for x in gn), sum(x or 0 for x in gm)
    v_read = sum_pn / sum_pm if sum_pm else None      # tokens per ms
    v_write = sum_gn / sum_gm if sum_gm else None
    a_read, b_read = ols(pn, pm)
    a_write, b_write = ols(gn, gm)

    errs, rows = [], []
    for r, d in splits:
        pred = formula_first_word(r, d, v_read, v_write)
        meas = d["first_ms"]
        if pred is not None and meas:
            errs.append(abs(pred - meas) / meas)
        tk = r.get("tokens") or {}
        ret = r.get("retrieval") or {}
        rows.append({"run": name, "id": r["id"], "repeat": r["repeat"], "category": r.get("category"),
                     "subcategory": r.get("subcategory"), "language": r.get("language"), "rounds": d["rounds"],
                     **{p + "_ms": round(d[p], 1) for p in PARTS},
                     "first_word_ms": meas, "reply_ms": d["total_ms"],
                     "formula_first_word_ms": None if pred is None else round(pred, 1),
                     "tok_read_message": d["tok_read_message"], "tok_read_tools": d["tok_read_tools"],
                     "tok_write_calls": d["tok_write_calls"], "tok_answer": d["tok_answer"],
                     "context_tokens_real": tk.get("context"), "context_tokens_est": ret.get("context_tokens"),
                     "tool_output_tokens": tk.get("tool_results_total"),
                     "cache_n_first": d.get("cache_n0"), **waste(r)})

    n = len(splits)
    totals = {p: sum(d[p] for _, d in splits) for p in PARTS}
    all_ms = sum(totals.values())
    rounds = Counter(d["rounds"] for _, d in splits)
    first = [d["first_ms"] for _, d in splits]
    reply = [d["total_ms"] for _, d in splits]
    # grounded-mode cases have their own system prompt (no tools), so they never share the cached prefix
    cache_known = [d.get("cache_n0") for r, d in splits
                   if d.get("cache_n0") is not None and r.get("mode", "tools") == "tools"]
    real_ctx = [row["context_tokens_real"] for row in rows if row["context_tokens_real"]]
    est_ctx = [row["context_tokens_est"] for row in rows if row["context_tokens_real"] and row["context_tokens_est"]]
    tool_out = [row["tool_output_tokens"] for row in rows if row["tool_output_tokens"] is not None]
    w = Counter()
    for row in rows:
        for k in ("dup_calls", "staff_calls_over_1", "deduped_fetches", "tool_errors", "max_rounds", "empty_replies",
                  "guard_notes", "n_calls"):
            w[k] += row[k]

    # repeats: same case, several timings
    by_case = defaultdict(list)
    for r, d in splits:
        by_case[r["id"]].append((d["first_ms"], r.get("final_reply"), [call_key(c) for c in r.get("tool_calls") or []]))
    rep = None
    multi = {k: v for k, v in by_case.items() if len(v) > 1}
    if multi:
        cvs, same_reply, same_calls = [], 0, 0
        for v in multi.values():
            xs = [x for x, _, _ in v if x]
            if len(xs) > 1 and statistics.mean(xs) > 0:
                cvs.append(statistics.pstdev(xs) / statistics.mean(xs))
            same_reply += len({rp for _, rp, _ in v}) == 1
            same_calls += len({json.dumps(c) for _, _, c in v}) == 1
        rep = {"cases": len(multi), "median_cv_first_word": statistics.median(cvs) if cvs else None,
               "p90_cv_first_word": pctl(cvs, 0.9), "identical_replies": same_reply / len(multi),
               "identical_calls": same_calls / len(multi)}

    by_route = defaultdict(list)
    for r, d in splits:
        if r.get("route") and r.get("route") != "none":
            by_route[r["route"]].append(d)
    route_tab = {k: {"n": len(v), "rounds": statistics.mean(d["rounds"] for d in v),
                     "tok_read": statistics.mean(d["tok_read"] for d in v),
                     "first_p50_ms": pctl([d["first_ms"] for d in v], 0.5)} for k, v in sorted(by_route.items())}
    cats = defaultdict(list)
    for r, d in splits:
        key = r.get("category") if r.get("category") != "rag" else f"rag/{r.get('subcategory')}"
        cats[key].append(d)
    by_cat = {k: {"n": len(v), "rounds": statistics.mean(d["rounds"] for d in v),
                  "tok_read": statistics.mean(d["tok_read"] for d in v),
                  "first_p50_ms": pctl([d["first_ms"] for d in v], 0.5)} for k, v in sorted(cats.items())}

    s = {
        "run": name, "model": meta.get("model"), "backend": meta.get("backend"), "config": meta.get("config_label"),
        "retrieval": (meta.get("retrieval") or {}).get("condition"), "eval": meta.get("eval_file"),
        "n_records": n, "n_cases": len(by_case), "repeats": meta.get("repeats"),
        "rounds_mean": statistics.mean(d["rounds"] for _, d in splits),
        "rounds_dist": {str(k): rounds[k] for k in sorted(rounds)},
        "share_multi_round": sum(v for k, v in rounds.items() if k > 1) / n,
        "tok_read_mean": statistics.mean(d["tok_read"] for _, d in splits),
        "tok_read_message_mean": statistics.mean(d["tok_read_message"] for _, d in splits),
        "tok_read_tools_mean": statistics.mean(d["tok_read_tools"] for _, d in splits),
        "tok_write_calls_mean": statistics.mean(d["tok_write_calls"] for _, d in splits),
        "tok_answer_mean": statistics.mean(d["tok_answer"] for _, d in splits),
        "context_tokens_real_mean": statistics.mean(real_ctx) if real_ctx else None,
        "context_real_over_estimate": (sum(real_ctx[:len(est_ctx)]) / sum(est_ctx)) if est_ctx and sum(est_ctx) else None,
        "tool_output_tokens_mean": statistics.mean(tool_out) if tool_out else None,
        "tool_output_tokens_per_call": (sum(tool_out) / sum(row["n_calls"] for row in rows if row["tool_output_tokens"] is not None))
        if tool_out and sum(row["n_calls"] for row in rows if row["tool_output_tokens"] is not None) else None,
        "tool_calls_mean": statistics.mean(row["n_calls"] for row in rows),
        "time_share": {p: (totals[p] / all_ms if all_ms else None) for p in PARTS},
        "time_mean_ms": {p: totals[p] / n for p in PARTS},
        "v_read_tok_s": v_read * 1000 if v_read else None, "v_write_tok_s": v_write * 1000 if v_write else None,
        "fit_read": {"overhead_ms": a_read, "tok_s": 1000 / b_read if b_read else None},
        "fit_write": {"overhead_ms": a_write, "tok_s": 1000 / b_write if b_write else None},
        "formula_median_abs_err": statistics.median(errs) if errs else None,
        "formula_p90_abs_err": pctl(errs, 0.9),
        "first_word_p50_ms": pctl(first, 0.5), "first_word_p50_ci": boot_median_ci(first),
        "first_word_p90_ms": pctl(first, 0.9),
        "reply_p50_ms": pctl(reply, 0.5), "reply_p50_ci": boot_median_ci(reply), "reply_p90_ms": pctl(reply, 0.9),
        "forced_final_requests": sum(1 for r in recs for t in r.get("turns") or [] if t.get("forced_final")),
        "forced_final_read_mean": (lambda xs: statistics.mean(xs) if xs else None)(
            [t.get("prompt_n") or 0 for r in recs for t in r.get("turns") or [] if t.get("forced_final")]),
        "other_tool_round_read_mean": (lambda xs: statistics.mean(xs) if xs else None)(
            [t.get("prompt_n") or 0 for r in recs for t in (r.get("turns") or [])[1:] if not t.get("forced_final")]),
        "cache_miss_share": (sum(1 for c in cache_known if c < 0.9 * prefix_tokens) / len(cache_known))
        if cache_known else None,
        "waste": dict(w), "repeats_check": rep, "by_category": by_cat, "by_route": route_tab,
        "run_peak_rss_mb": meta.get("run_peak_rss_mb"),
        "harness_rss_mb_max": max((r.get("metrics", {}).get("harness_rss_mb") or 0) for r in recs) or None,
    }
    return s, rows


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def report(summaries, out_dir):
    L = ["# Where the time goes (Objective 3, Step 1)", "",
         "Times are summed over every case of a run, so the shares say where the run's total waiting went. "
         "\"First word\" is the wait before the answer starts: retrieval, every tool round and the final prompt "
         "reading. Tokens \"read\" are prompt tokens the server actually computed (cached prefix excluded).", ""]

    L += ["## Rounds and tokens per case", "",
          "| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls "
          "| Written: answer | Context (real) | Tool outputs (real) | Tool calls | Tokens per tool output |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summaries:
        L.append(f"| {s['run']} | {s['n_records']} | {s['rounds_mean']:.2f} | {s['share_multi_round']:.0%} "
                 f"| {f1(s['tok_read_message_mean'], 0)} | {f1(s['tok_read_tools_mean'], 0)} "
                 f"| {f1(s['tok_write_calls_mean'], 0)} | {f1(s['tok_answer_mean'], 0)} "
                 f"| {f1(s['context_tokens_real_mean'], 0)} | {f1(s['tool_output_tokens_mean'], 0)} "
                 f"| {f1(s['tool_calls_mean'], 2)} | {f1(s['tool_output_tokens_per_call'], 0)} |")
    L += [""]

    L += ["## Time split (share of all case time)", "",
          "| Run | " + " | ".join(PART_LABEL[p] for p in PARTS) + " |",
          "|---|" + "---:|" * len(PARTS)]
    for s in summaries:
        L.append(f"| {s['run']} | " + " | ".join(
            f"{s['time_share'][p]:.0%} ({sec(s['time_mean_ms'][p])})" if s['time_share'][p] is not None else "–"
            for p in PARTS) + " |")
    L += ["", "Each cell: share of the run's total, then the mean per case.", ""]

    L += ["## Waits", "",
          "| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |",
          "|---|---:|---:|---:|---:|---:|"]
    for s in summaries:
        lo, hi = s["first_word_p50_ci"]
        rlo, rhi = s["reply_p50_ci"]
        L.append(f"| {s['run']} | {sec(s['first_word_p50_ms'])} [{sec(lo)}–{sec(hi)}] | {sec(s['first_word_p90_ms'])} "
                 f"| {sec(s['reply_p50_ms'])} [{sec(rlo)}–{sec(rhi)}] | {sec(s['reply_p90_ms'])} "
                 f"| {f1(s['run_peak_rss_mb'], 0)} MB |")
    L += [""]

    L += ["## Speeds and the first-word formula", "",
          "| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s "
          "| Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |",
          "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summaries:
        fr, fw = s["fit_read"], s["fit_write"]
        me, pe = s["formula_median_abs_err"], s["formula_p90_abs_err"]
        L.append(f"| {s['run']} | {f1(s['v_read_tok_s'])} | {f1(s['v_write_tok_s'])} | {f1(fr['overhead_ms'], 0)} ms "
                 f"| {f1(fr['tok_s'])} | {f1(fw['overhead_ms'], 0)} ms | {f1(fw['tok_s'])} "
                 f"| {'–' if me is None else f'{me:.0%}'} / {'–' if pe is None else f'{pe:.0%}'} |")
    L += ["", "Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's "
          "own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median "
          "absolute error is at most 15% on the speed runs.", ""]

    L += ["## Checks", "",
          "| Run | Cache misses (first request, tool-mode cases) | Context real / estimate | Repeated identical calls "
          "| call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit | Empty replies (incl. fallback) "
          "| Loop-guard notes |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summaries:
        w = s["waste"]
        cm = s["cache_miss_share"]
        ratio = s["context_real_over_estimate"]
        L.append(f"| {s['run']} | {'–' if cm is None else f'{cm:.0%}'} | {'–' if ratio is None else f'{ratio:.2f}'} "
                 f"| {w.get('dup_calls', 0)} | {w.get('staff_calls_over_1', 0)} | {w.get('deduped_fetches', 0)} "
                 f"| {w.get('tool_errors', 0)} | {w.get('max_rounds', 0)} | {w.get('empty_replies', 0)} "
                 f"| {w.get('guard_notes', 0)} |")
    L += [""]

    if any(s.get("forced_final_requests") for s in summaries):
        L += ["**Loop guard, forced final requests** (tool_choice none). If these read far more tokens than other tool "
              "rounds, the server dropped the tool list from the prompt and lost the prompt cache.", "",
              "| Run | Forced final requests | Mean tokens read: forced final | Mean tokens read: other tool rounds |",
              "|---|---:|---:|---:|"]
        for s in summaries:
            if s.get("forced_final_requests"):
                L.append(f"| {s['run']} | {s['forced_final_requests']} | {f1(s['forced_final_read_mean'], 0)} "
                         f"| {f1(s['other_tool_round_read_mean'], 0)} |")
        L += [""]
    reps = [s for s in summaries if s["repeats_check"]]
    if reps:
        L += ["## Repeat stability", "",
              "| Run | Cases | First-word spread across repeats (CV), median / p90 | Identical replies | Identical tool calls |",
              "|---|---:|---:|---:|---:|"]
        for s in reps:
            r = s["repeats_check"]
            med = "–" if r["median_cv_first_word"] is None else f"{r['median_cv_first_word']:.0%}"
            p90 = "–" if r["p90_cv_first_word"] is None else f"{r['p90_cv_first_word']:.0%}"
            L.append(f"| {s['run']} | {r['cases']} | {med} / {p90} "
                     f"| {r['identical_replies']:.0%} | {r['identical_calls']:.0%} |")
        L += ["", "Greedy decoding should repeat itself; if replies differ, paired comparisons in later steps "
              "carry that noise too.", ""]

    if any(s.get("by_route") for s in summaries):
        L += ["## By route (Step 4 router)", ""]
        for s in summaries:
            if s.get("by_route"):
                L += [f"**{s['run']}**", "", "| Route | Cases | Rounds | Tokens read | First word p50 |",
                      "|---|---:|---:|---:|---:|"]
                for k, v in s["by_route"].items():
                    L.append(f"| {k} | {v['n']} | {v['rounds']:.2f} | {v['tok_read']:.0f} | {sec(v['first_p50_ms'])} |")
                L += [""]
    L += ["## By category", ""]
    for s in summaries:
        L += [f"**{s['run']}**", "", "| Category | Cases | Rounds | Tokens read | First word p50 |", "|---|---:|---:|---:|---:|"]
        for k, v in s["by_category"].items():
            L.append(f"| {k} | {v['n']} | {v['rounds']:.2f} | {v['tok_read']:.0f} | {sec(v['first_p50_ms'])} |")
        L += [""]

    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("runs", nargs="+", help="Run folders (globs allowed)")
    ap.add_argument("--out", default=None, help="Default: <first run's parent>/_time_split")
    ap.add_argument("--prefix-tokens", type=int, default=1764,
                    help="Cached system + tools prefix length; a first request reusing less than 90%% is a miss")
    a = ap.parse_args(argv)
    dirs = sorted({d for pat in a.runs for d in glob.glob(pat) if os.path.isdir(d)})
    dirs = [d for d in dirs if not os.path.basename(os.path.normpath(d)).startswith("_")]
    if not dirs:
        print("No run folders matched.")
        return 1
    out = a.out or os.path.join(os.path.dirname(os.path.normpath(dirs[0])), "_time_split")
    os.makedirs(out, exist_ok=True)
    summaries, rows = [], []
    for d in dirs:
        res = analyse(d, a.prefix_tokens)
        if res is None:
            print(f"  skipped (no cases): {d}")
            continue
        s, r = res
        summaries.append(s)
        rows += r
        print(f"  {s['run']}: {s['n_records']} records, rounds {s['rounds_mean']:.2f}, "
              f"first word p50 {sec(s['first_word_p50_ms'])}")
    if not summaries:
        return 1
    report(summaries, out)
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({s["run"]: s for s in summaries}, f, indent=1)
    with open(os.path.join(out, "cases_split.csv"), "w", newline="", encoding="utf-8") as f:
        wtr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"Wrote {os.path.join(out, 'report.md')}, summary.json, cases_split.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
