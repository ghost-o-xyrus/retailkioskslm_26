"""
Objective 3, Step 15: judged rates on the test set O3-T, from the judge's labels and the packet key.

    python eval\\rag_judge\\summary_o3.py

Reads eval/rag_judge/step15/key.json and every labels*.json there (the judge's, plus labels_auto.json for empty
replies). Writes eval/rag_judge/step15/summary.md and summary.json. Per model and configuration (O3-final, O3-B0):
  hallucination, unanswerable     share of must-decline questions whose reply was labelled unsupported
  hallucination, near-miss        the same for near-miss questions (a close product, a missing attribute...)
  unsupported details (judged)    share of the 60 sampled answerable replies labelled unsupported
  false refusals                  judge-confirmed refusals (refusal candidates labelled declined, or empty) as a
                                  share of all answerable questions (Objective 2's definition)
Wilson 95% intervals; O3-final against O3-B0 paired on the same questions (exact McNemar on "unsupported").
Hinglish is reported separately for the unanswerable and near-miss questions. Targets (Objective 3): <= 5%
hallucination on each, <= 5% unsupported details, <= 10% false refusals.
"""

import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.dirname(HERE)
sys.path.insert(0, EVAL)
import score as S  # noqa: E402

D = os.path.join(HERE, "step15")


def wilson(k, n, z=1.96):
    if not n:
        return None, None, None
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def main(argv=None):
    folder = (argv or sys.argv[1:] or [D])[0]
    with open(os.path.join(folder, "key.json"), encoding="utf-8") as f:
        key = json.load(f)
    lab = {}
    for fp in sorted(glob.glob(os.path.join(folder, "labels*.json"))):
        with open(fp, encoding="utf-8") as f:
            for row in json.load(f):
                lab[row["item"]] = row["label"].strip().lower()
    with open(os.path.join(EVAL, "rag_cases_o3t.jsonl"), encoding="utf-8") as f:
        cases = [json.loads(x) for x in f if x.strip()]
    answerable = sum(1 for c in cases if c["split"] == "test" and c["expected"]["behaviour"] == "answer")
    missing = sorted(i for i in key if i not in lab)
    by = {}
    for item, k in key.items():
        if item not in lab:
            continue
        by.setdefault((k["model"], k["condition"]), []).append(dict(k, label=lab[item]))
    out, L = {}, ["# Judged rates on O3-T (Objective 3, Step 15)", "",
                  f"Labels: {len(lab)} of {len(key)} items" + (f"; {len(missing)} still unlabelled" if missing else "")
                  + ". Empty replies count as declined.", "",
                  "| Model | Configuration | Hallucination, unanswerable | Hallucination, near-miss | "
                  "Hinglish unanswerable + near-miss | Unsupported details (judged sample) | False refusals |",
                  "|---|---|---|---|---|---|---|"]

    def fmt(k, n):
        p, lo, hi = wilson(k, n)
        return "–" if p is None else f"{100 * p:.1f}% ({k}/{n}) [{100 * lo:.1f}, {100 * hi:.1f}]"

    for (model, cond) in sorted(by, key=lambda x: (x[0], x[1] != "final")):
        rows = by[(model, cond)]
        un = lambda r: r["label"] == "unsupported"   # noqa: E731
        u = [r for r in rows if r["source"] == "unanswerable"]
        nm = [r for r in rows if r["source"] == "near_miss"]
        hg = [r for r in u + nm if r.get("language") in ("hinglish", "hindi")]
        fa = [r for r in rows if r["source"] == "faith"]
        refused = [r for r in rows if r["behaviour"] == "answer" and r.get("refusal_candidate")
                   and r["label"] in ("declined", "empty")]
        res = {"unanswerable": (sum(map(un, u)), len(u)), "near_miss": (sum(map(un, nm)), len(nm)),
               "hinglish": (sum(map(un, hg)), len(hg)), "unsupported_sample": (sum(map(un, fa)), len(fa)),
               "false_refusals": (len(refused), answerable)}
        out[f"{model}|{cond}"] = res
        L.append(f"| {model} | {'O3-final' if cond == 'final' else 'O3-B0'} | " + " | ".join(
            fmt(*res[x]) for x in ("unanswerable", "near_miss", "hinglish", "unsupported_sample", "false_refusals"))
            + " |")
    L += ["", "## O3-final against O3-B0 (same questions, unsupported or not)", "",
          "| Model | Set | Questions | O3-B0 | O3-final | Change [95% CI] | McNemar p |", "|---|---|---:|---:|---:|---|---:|"]
    for model in sorted({m for m, _ in by}):
        f_ = {(r["source"], r["case"]): r["label"] == "unsupported" for r in by.get((model, "final"), [])}
        b_ = {(r["source"], r["case"]): r["label"] == "unsupported" for r in by.get((model, "b0"), [])}
        for src, lab_ in (("unanswerable", "unanswerable"), ("near_miss", "near-miss")):
            ids = sorted(k for k in f_ if k[0] == src and k in b_)
            if not ids:
                continue
            x = [int(b_[i]) for i in ids]
            y = [int(f_[i]) for i in ids]
            dd, lo, hi = S.paired_bootstrap(y, x)
            b = sum(1 for i, j in zip(x, y) if i and not j)
            c = sum(1 for i, j in zip(x, y) if j and not i)
            L.append(f"| {model} | {lab_} | {len(ids)} | {100 * sum(x) / len(ids):.1f}% | {100 * sum(y) / len(ids):.1f}% "
                     f"| {100 * dd:+.1f} [{100 * lo:+.1f}, {100 * hi:+.1f}] | {S.mcnemar_exact(b, c):.3g} |")
            out[f"{model}|paired|{src}"] = {"n": len(ids), "b0": sum(x), "final": sum(y), "diff": dd, "ci": [lo, hi]}
    L += ["", "## Unsupported replies of O3-final by question type", "", "| Model | Type | Unsupported | Items |",
          "|---|---|---:|---:|"]
    for model in sorted({m for m, _ in by}):
        t = {}
        for r in by.get((model, "final"), []):
            if r["source"] in ("unanswerable", "near_miss"):
                a = t.setdefault(r["subcategory"], [0, 0])
                a[0] += r["label"] == "unsupported"
                a[1] += 1
        for sub, (k, n) in sorted(t.items(), key=lambda x: -x[1][0]):
            L.append(f"| {model} | {sub} | {k} | {n} |")
    with open(os.path.join(folder, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(folder, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
