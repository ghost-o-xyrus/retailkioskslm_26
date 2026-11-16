"""
Case-by-case comparison of runs on the same cases: what changed, and where the time went.

    python harness\\compare_runs.py results_obj2\\p7d_2b_cpu_v11_none results_obj2\\p7e_2b_cpu_v11_*
    python harness\\compare_runs.py results_obj2\\p7d_2b_cpu_rag_compact_gate results_obj2\\p7e_2b_cpu_rag_*

The first run is the reference. For each case and run: pass (v1.1 cases, eval/score.py checks) or a rough
fact/decline check (retrieval cases, as in pilot_report.py), tool rounds, the wait before the answer's first
word, whether the gate applied, and the tool calls. Then a summary per run, including RAM split between the
model server and the harness process. Writes <parent>\\_compare\\<first run>_vs.md.
"""

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "eval"))
sys.path.insert(0, HERE)
from score import score_case  # noqa: E402
from pilot_report import DECLINE, facts_ok, first_visible, load_cases  # noqa: E402


def read(run_dir):
    recs = {}
    with open(os.path.join(run_dir, "cases.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                recs[r["id"]] = r
            except json.JSONDecodeError:
                pass
    return recs


def verdict(case, rec):
    if rec is None or rec.get("error"):
        return False
    e = case["expected"]
    if case.get("category") != "rag":
        return bool(score_case(case, rec)["passed"])
    reply = (rec.get("final_reply") or "").lower()
    if e["behaviour"] == "decline":
        return any(p in reply for p in DECLINE)
    if e["must_include"]:
        return facts_ok(reply, e["must_include"])
    return bool(reply.strip())


def main():
    dirs = [d for d in sys.argv[1:] if os.path.isdir(d)]
    if len(dirs) < 2:
        sys.exit("usage: python harness\\compare_runs.py <reference run> <run> [<run> ...]")
    cases = load_cases()
    runs = [(os.path.basename(d.rstrip("\\/")), read(d)) for d in dirs]
    ids = [i for i in runs[0][1] if all(i in r for _, r in runs)]
    names = [n for n, _ in runs]
    L = [f"# Case comparison (reference: {names[0]})", "",
         "Per run: pass (v1.1 checks; rough check for retrieval questions) / tool rounds / seconds before the "
         "answer's first word / G if the gate applied. Calls are listed for the reference and the last run.", "",
         "| Case | " + " | ".join(names) + f" | Calls ({names[0]}) | Calls ({names[-1]}) |",
         "|---|" + "---|" * (len(names) + 2)]
    for i in ids:
        cells = []
        for _, R in runs:
            r = R[i]
            g = " G" if (r.get("retrieval") or {}).get("fallback_applied") else ""
            cells.append(f"{'pass' if verdict(cases[i], r) else 'FAIL'} / {r.get('n_rounds', 0)} / "
                         f"{first_visible(r) / 1000:.1f}{g}")
        calls = lambda r: ", ".join(c["name"] for c in r.get("tool_calls", [])) or "-"
        L.append(f"| {i} | " + " | ".join(cells) + f" | {calls(runs[0][1][i])} | {calls(runs[-1][1][i])} |")
    L += ["", "| Run | Pass | First word p50 / p90 s | Mean rounds | Hit round limit | Empty replies | "
          "Peak server RAM GB | Peak harness RAM GB | Peak total GB |", "|---|---|---|---|---|---|---|---|---|"]
    for n, R in runs:
        rs = [R[i] for i in ids]
        vis = sorted(first_visible(r) / 1000 for r in rs)
        tot = max((r["metrics"].get("peak_rss_mb") or 0) + (r["metrics"].get("harness_rss_mb") or 0) for r in rs)
        L.append(f"| {n} | {sum(verdict(cases[i], R[i]) for i in ids)}/{len(ids)} | {statistics.median(vis):.1f} / "
                 f"{vis[int(0.9 * (len(vis) - 1))]:.1f} | {statistics.mean(r.get('n_rounds', 0) for r in rs):.1f} | "
                 f"{sum('max_rounds_reached' in r.get('flags', []) for r in rs)} | "
                 f"{sum(not (r.get('final_reply') or '').strip() for r in rs)} | "
                 f"{max(r['metrics'].get('peak_rss_mb') or 0 for r in rs) / 1000:.2f} | "
                 f"{max(r['metrics'].get('harness_rss_mb') or 0 for r in rs) / 1000:.2f} | {tot / 1000:.2f} |")
    out = os.path.join(os.path.dirname(os.path.abspath(dirs[0])), "_compare")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f"{names[0]}_vs.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
