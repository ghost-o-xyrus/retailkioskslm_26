"""
Quick operational summary of one or more runs (not the quality score; that is Step 6).

    python harness\\summarize.py results\\qwen35-4b_q4_vulkan
    python harness\\summarize.py results\\*            # every run, one table

Reports, per run: cases done, errors, format problems (tool call written as text, invalid JSON
arguments, unknown tool names, hitting max tokens or max rounds), tool calls per case, median and
p90 end-to-end latency, median time to first token, generation speed, prompt-cache reuse, and peak RAM.
Writes summary.json next to cases.jsonl.
"""

import glob
import json
import os
import statistics
import sys


def pct(xs, q):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def summarize(run_dir):
    path = os.path.join(run_dir, "cases.jsonl")
    if not os.path.exists(path):
        return None
    recs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            recs[(r["id"], r["repeat"])] = r  # last record wins (resumed runs)
    rs = list(recs.values())
    ok = [r for r in rs if not r.get("error")]
    flags = {}
    for r in ok:
        for fl in r.get("flags", []):
            flags[fl] = flags.get(fl, 0) + 1
    calls = [c for r in ok for c in r.get("tool_calls", [])]
    m = lambda key: [r["metrics"].get(key) for r in ok]  # noqa: E731
    gen_tok = sum(r["metrics"]["generated_tokens"] or 0 for r in ok)
    gen_ms = sum(t.get("predicted_ms") or 0 for r in ok for t in r["turns"])
    p_total = sum(r["metrics"]["prompt_tokens_total"] or 0 for r in ok)
    p_cached = sum(r["metrics"]["prompt_tokens_cached"] or 0 for r in ok)
    meta = {}
    if os.path.exists(os.path.join(run_dir, "run_meta.json")):
        with open(os.path.join(run_dir, "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
    s = {
        "run": os.path.basename(run_dir.rstrip("/\\")), "model": meta.get("model"), "quant": meta.get("quant"),
        "backend": meta.get("backend"), "cases": len(rs), "errors": len(rs) - len(ok),
        "tool_calls_per_case": round(len(calls) / len(ok), 2) if ok else None,
        "invalid_json_args": sum(not c["arguments_valid_json"] for c in calls),
        "unknown_tool_names": sum(not c["known_tool"] for c in calls),
        "tool_errors_returned": sum(bool(c.get("result_error")) for c in calls),
        "flags": flags,
        "end_to_end_s_median": round(pct(m("end_to_end_ms"), 0.5) / 1000, 2) if ok else None,
        "end_to_end_s_p90": round(pct(m("end_to_end_ms"), 0.9) / 1000, 2) if ok else None,
        "ttft_ms_median": round(pct(m("ttft_ms"), 0.5), 1) if ok and pct(m("ttft_ms"), 0.5) is not None else None,
        "tokens_per_s": round(gen_tok / (gen_ms / 1000), 2) if gen_ms else None,
        "prompt_cache_reuse_pct": round(100 * p_cached / p_total, 1) if p_total else None,
        "peak_rss_mb": meta.get("run_peak_rss_mb") or (max((x for x in m("peak_rss_mb") if x), default=None) if ok else None),
        "wall_minutes": meta.get("wall_minutes"),
    }
    with open(os.path.join(run_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2)
    return s


def main():
    dirs = []
    for a in sys.argv[1:] or [os.path.join(os.path.dirname(__file__), "..", "results", "*")]:
        dirs += [d for d in glob.glob(a) if os.path.isdir(d)]
    rows = [s for s in (summarize(d) for d in sorted(dirs)) if s]
    if not rows:
        print("No runs found.")
        return
    cols = ["run", "cases", "errors", "tool_calls_per_case", "invalid_json_args", "end_to_end_s_median",
            "end_to_end_s_p90", "ttft_ms_median", "tokens_per_s", "prompt_cache_reuse_pct", "peak_rss_mb"]
    widths = [max(len(c), *(len(str(r.get(c))) for r in rows)) for c in cols]
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  ".join(str(r.get(c)).ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        if r["flags"]:
            print(f"{r['run']} flags: {r['flags']}")


if __name__ == "__main__":
    main()
