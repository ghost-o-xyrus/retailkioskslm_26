"""
Step 7 pilot report: does each retrieval condition work, and what does it cost? Not the Step 8 score.

    python harness\\pilot_report.py results_obj2\\p7_*

Per run: cases, errors, format flags, latency (end to end; first word of the answer, i.e. everything before
the final reply starts streaming; retrieval; time to first token of the first request), prompt tokens and
cache reuse, context tokens shown, search_knowledge use, how many cases the refusal fallback would refuse, and
peak RAM of llama-server plus the harness process (which holds the knowledge base).
For the retrieval questions it adds a ROUGH reply check, by phrase matching only:
    answer   every expected fact appears in the reply (cases that list facts)
    decline  the reply contains a decline or staff-offer phrase
Step 8 scores replies properly; these numbers only show whether something is badly wrong.
Writes <first run's parent>\\_pilot\\report.md.
"""

import glob
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DECLINE = ("don't have", "do not have", "not sure", "not listed", "staff", "sorry", "can't", "cannot", "unable",
           "only help", "not available", "nahi", "nahin", "maaf", "don't sell", "do not sell", "not able")


def pctl(xs, q):
    xs = sorted(x for x in xs if x is not None)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))] if xs else None


def load_cases():
    out = {}
    for f in ("rag_cases.jsonl", "eval_set_v1.1.jsonl"):
        with open(os.path.join(ROOT, "eval", f), encoding="utf-8") as fh:
            for line in fh:
                c = json.loads(line)
                out[c["id"]] = c
    return out


def first_visible(r):
    """Wait before the first word of the answer: everything except the final reply's own generation."""
    m = r["metrics"]
    if m.get("first_visible_ms") is not None:
        return m["first_visible_ms"]
    t = r.get("turns") or []
    return max(0.0, m["end_to_end_ms"] - (t[-1].get("predicted_ms") or 0)) if t else m["end_to_end_ms"]


def facts_ok(reply, groups):
    r = (reply or "").lower()
    return all(any(p.lower() in r for p in g) for g in groups)


def summarize(run_dir, cases):
    path = os.path.join(run_dir, "cases.jsonl")
    if not os.path.exists(path):
        return None
    recs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                recs[(r["id"], r["repeat"])] = r
            except json.JSONDecodeError:
                pass
    rs = list(recs.values())
    ok = [r for r in rs if not r.get("error")]
    m = lambda k: [r["metrics"].get(k) for r in ok]
    tot, cached = sum(x or 0 for x in m("prompt_tokens_total")), sum(x or 0 for x in m("prompt_tokens_cached"))
    ret = [r.get("retrieval") or {} for r in ok]
    flags = {}
    for r in ok:
        for fl in r.get("flags", []):
            flags[fl] = flags.get(fl, 0) + 1
    ctx = [x.get("context_tokens") for x in ret if x.get("condition") in ("oracle", "always")]
    tool_runs = [x for x in ret if x.get("condition") == "tool"]
    s = {"run": os.path.basename(run_dir), "cases": len(rs), "errors": len(rs) - len(ok),
         "e2e_p50_s": pctl(m("end_to_end_ms"), .5), "e2e_p90_s": pctl(m("end_to_end_ms"), .9),
         "ttft_p50_s": pctl(m("ttft_ms"), .5), "retrieval_p50_ms": pctl(m("retrieval_ms"), .5),
         "vis_p50_s": pctl([first_visible(r) for r in ok], .5), "vis_p90_s": pctl([first_visible(r) for r in ok], .9),
         "prompt_tokens_mean": statistics.mean(x or 0 for x in m("prompt_tokens_total")) if ok else None,
         "cache_reuse_pct": 100 * cached / tot if tot else None,
         "context_tokens_mean": statistics.mean(ctx) if ctx else None,
         "search_knowledge_pct": 100 * sum(1 for x in tool_runs if x["calls"]) / len(tool_runs) if tool_runs else None,
         "would_refuse": sum(1 for x in ret if x.get("fallback_would_refuse")),
         "gated_or_refused": sum(1 for x in ret if x.get("fallback_applied")),
         "flags": flags,
         "peak_ram_gb": max(((r["metrics"].get("peak_rss_mb") or 0) + (r["metrics"].get("harness_rss_mb") or 0)
                             for r in ok), default=0) / 1000 or None}
    for k in ("e2e_p50_s", "e2e_p90_s", "ttft_p50_s", "vis_p50_s", "vis_p90_s"):
        s[k] = s[k] / 1000 if s[k] is not None else None
    ans = [r for r in ok if (cases.get(r["id"], {}).get("expected") or {}).get("behaviour") == "answer"
           and cases[r["id"]]["expected"]["must_include"]]
    dec = [r for r in ok if (cases.get(r["id"], {}).get("expected") or {}).get("behaviour") == "decline"]
    s["rough_answer"] = (sum(facts_ok(r["final_reply"], cases[r["id"]]["expected"]["must_include"]) for r in ans), len(ans))
    s["rough_decline"] = (sum(any(p in (r["final_reply"] or "").lower() for p in DECLINE) for r in dec), len(dec))
    return s


def main():
    dirs = sorted({d for a in sys.argv[1:] for d in glob.glob(a) if os.path.isdir(d)})
    if not dirs:
        sys.exit("usage: python harness\\pilot_report.py results_obj2\\p7_*")
    cases = load_cases()
    rows = [s for s in (summarize(d, cases) for d in dirs) if s]
    f1 = lambda x, d=1: "-" if x is None else f"{x:.{d}f}"
    frac = lambda t: "-" if not t[1] else f"{t[0]}/{t[1]}"
    L = ["# Step 7 pilot (dev cases only; rough checks, not the Step 8 score)", "",
         "| Run | Cases | Errors | E2E p50 / p90 s | First word p50 / p90 s | TTFT p50 s | Retrieval p50 ms | Prompt tokens | Cache reuse | "
         "Context tokens | search_knowledge used | Fallback would refuse | Rough: facts | Rough: declines | "
         "Peak RAM GB (server + harness) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in rows:
        L.append(f"| {s['run']} | {s['cases']} | {s['errors']} | {f1(s['e2e_p50_s'])} / {f1(s['e2e_p90_s'])} | "
                 f"{f1(s['vis_p50_s'])} / {f1(s['vis_p90_s'])} | "
                 f"{f1(s['ttft_p50_s'], 2)} | {f1(s['retrieval_p50_ms'], 0)} | {f1(s['prompt_tokens_mean'], 0)} | "
                 f"{f1(s['cache_reuse_pct'], 0)}% | {f1(s['context_tokens_mean'], 0)} | "
                 f"{'-' if s['search_knowledge_pct'] is None else f1(s['search_knowledge_pct'], 0) + '%'} | "
                 f"{s['would_refuse']} | {frac(s['rough_answer'])} | {frac(s['rough_decline'])} | {f1(s['peak_ram_gb'], 2)} |")
    L += ["", "Flags per run (format problems): " + "; ".join(f"{s['run']}: {s['flags'] or 'none'}" for s in rows)]
    out = os.path.join(os.path.dirname(dirs[0]), "_pilot")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nWrote {os.path.join(out, 'report.md')}")


if __name__ == "__main__":
    main()
