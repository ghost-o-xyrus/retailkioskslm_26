"""
Un-blind the judge's rubric scores and compare the two runs.

    python eval/rubric/analyze_rubric.py eval/rubric/stage3

Reads packet.json, key.json and scores*.json in that folder; writes rubric_report.md and rubric_scores.csv.
Per reply, the case score is the mean of its rubric lines (nulls left out). Runs are compared on the same cases with a
paired bootstrap 95% CI of the mean difference and a Wilcoxon signed-rank test.
"""
import csv, glob, json, os, random, statistics, sys


def boot(diffs, n=10000, seed=7):
    rng = random.Random(seed)
    m = [statistics.mean(rng.choices(diffs, k=len(diffs))) for _ in range(n)]
    m.sort()
    return statistics.mean(diffs), m[int(0.025 * n)], m[int(0.975 * n)]


def wilcoxon_p(diffs):
    try:
        from scipy.stats import wilcoxon
        d = [x for x in diffs if x != 0]
        return float(wilcoxon(d).pvalue) if d else 1.0
    except Exception:
        return None


def main(folder):
    packet = {p["item"]: p for p in json.load(open(os.path.join(folder, "packet.json"), encoding="utf-8"))}
    key = json.load(open(os.path.join(folder, "key.json"), encoding="utf-8"))
    scores = {}
    for f in sorted(glob.glob(os.path.join(folder, "scores*.json"))):
        for s in json.load(open(f, encoding="utf-8")):
            scores[s["item"]] = s
    missing = sorted(set(packet) - set(scores))
    runs = key["runs"]
    rows = []
    for item, s in scores.items():
        k = key["items"][item]
        for label in "XY":
            vals = s[label]
            for i, v in enumerate(vals):
                rows.append({"item": item, "case_id": k["case_id"], "category": k["category"], "run": k[label],
                             "line": i + 1, "rubric": packet[item]["rubric"][i], "score": v,
                             "note": s.get(f"note_{label}", "")})
    with open(os.path.join(folder, "rubric_scores.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def case_mean(run, item):
        v = [r["score"] for r in rows if r["item"] == item and r["run"] == run and r["score"] is not None]
        return statistics.mean(v) if v else None

    out = ["# Rubric scores (blind LLM judge, test split)", "",
           f"Items: {len(scores)} of {len(packet)}" + (f" (missing: {', '.join(missing)})" if missing else ""), "",
           "Mean score 1–5 per case (mean of its rubric lines). Brackets: paired bootstrap 95% CI.", "",
           "| Run | Mean case score | Cases scoring ≤ 2.5 | Lines scored 1–2 |", "|---|---|---|---|"]
    for run in runs:
        cm = [case_mean(run, i) for i in scores]
        cm = [x for x in cm if x is not None]
        low_lines = [r for r in rows if r["run"] == run and r["score"] is not None and r["score"] <= 2]
        allines = [r for r in rows if r["run"] == run and r["score"] is not None]
        out.append(f"| {run} | {statistics.mean(cm):.2f} | {sum(x <= 2.5 for x in cm)} of {len(cm)} | "
                   f"{100 * len(low_lines) / len(allines):.0f}% |")
    a, b = runs
    diffs = [case_mean(a, i) - case_mean(b, i) for i in scores if case_mean(a, i) is not None and case_mean(b, i) is not None]
    d, lo, hi = boot(diffs)
    p = wilcoxon_p(diffs)
    out += ["", f"**{a} − {b}: {d:+.2f} points [{lo:+.2f}, {hi:+.2f}]**, Wilcoxon p = "
            f"{p:.4f}" if p is not None else "n/a", ""]
    out += [f"Cases where {a} scored higher: {sum(x > 0 for x in diffs)}; lower: {sum(x < 0 for x in diffs)}; "
            f"tied: {sum(x == 0 for x in diffs)}.", ""]
    out += ["## By category", "", "| Category | n | " + " | ".join(runs) + " |", "|---|---|" + "---|" * len(runs)]
    for cat in sorted({k["category"] for k in key["items"].values()}):
        items = [i for i in scores if key["items"][i]["category"] == cat]
        cells = []
        for run in runs:
            v = [case_mean(run, i) for i in items]
            v = [x for x in v if x is not None]
            cells.append(f"{statistics.mean(v):.2f}" if v else "-")
        out.append(f"| {cat} | {len(items)} | " + " | ".join(cells) + " |")
    out += ["", "## By rubric line (most common lines)", "", "| Rubric line | n | " + " | ".join(runs) + " |",
            "|---|---|" + "---|" * len(runs)]
    lines = {}
    for r in rows:
        if r["score"] is not None:
            lines.setdefault(r["rubric"], {}).setdefault(r["run"], []).append(r["score"])
    for text, by in sorted(lines.items(), key=lambda kv: -sum(len(v) for v in kv[1].values()))[:12]:
        n = len(next(iter(by.values())))
        out.append(f"| {text} | {n} | " + " | ".join(f"{statistics.mean(by.get(run, [0])):.2f}" for run in runs) + " |")
    nulls = sum(1 for r in rows if r["score"] is None)
    out += ["", f"Lines marked not applicable: {nulls} of {len(rows)}."]
    open(os.path.join(folder, "rubric_report.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
