"""
Objective 3, Step 14: apply the pre-registered confirming rules to the test-set comparisons.

    python eval\\step14_verdicts.py

Reads (all written by the Step 14 commands):
    results_obj3/_compare_step14/compare.json         O3-final against O3-B0 on O3-T (quality runs, both tiers)
    results_obj3/_compare_step14_speed/compare.json   Tier A in-place timing (2B on CPU)
    results_obj3/_dialogues_step14/{summary.json, dialogues.csv}
Writes results_obj3/_step14/verdicts.md and verdicts.json.

Rules (written before any Step 14 run), for each tier, O3-final against O3-B0:
  Primary family: store questions (all checked), tool cases and follow-ups, for both tiers (6 tests). McNemar p
  values are Holm-adjusted across the family. A set is "better" or "worse" only if the Holm-adjusted p < 0.05, the
  bootstrap interval excludes 0 and the difference exceeds the noise bound; otherwise "tie".
    (1) no primary set is worse;
    (2) follow-ups are better;
    (3) dialogues meet the Step 6 targets (>= 95% end in a recommendation; >= 2 of 4 slots known before it in
        >= 85%; at most 2 questions; >= 90% of shown watches fit) and fit is not lower than O3-B0 (paired
        interval not wholly below 0);
    (4) Tier A only, in place on CPU: the median per-case total reply time falls (interval wholly below 0) on
        store questions and on tool cases, and the first word is not later (interval not wholly above 0).
  A tier is confirmed if (1)-(3), and for Tier A (4), all hold. Everything else (unanswerable and answerable
  store questions, origin and Hinglish subsets, unsupported replies, Tier B waits, the Tier A prompt v1.2
  candidate) is reported, not used to decide.
"""

import csv
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R = os.path.join(ROOT, "results_obj3")
TIERS = {"A": "2b", "B": "4b"}
PRIMARY = (("rag", "all checked", "store questions"), ("v12", "tool cases", "tool cases"),
           ("fup", "all checked", "follow-ups"))


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def holm(ps):
    """Holm-adjusted p values, in the input order."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [None] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


def paired_fit(rows, base, new, n=4000, seed=7):
    b = {r["dialogue"]: float(r["fit"]) for r in rows if r["run"] == base and r["fit"] not in ("", None)}
    w = {r["dialogue"]: float(r["fit"]) for r in rows if r["run"] == new and r["fit"] not in ("", None)}
    ids = sorted(set(b) & set(w))
    if not ids:
        return None
    d = [w[i] - b[i] for i in ids]
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choice(d) for _ in d) for _ in range(n))
    return statistics.mean(d), means[int(0.025 * n)], means[int(0.975 * n)], len(ids)


def main(argv=None):
    global R
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=R)
    R = ap.parse_args(argv).results
    q = load(os.path.join(R, "_compare_step14", "compare.json"))
    rows = {(r["base"], r["new"], r["subset"]): r for r in q["rows"]}
    L = ["# Step 14: confirming run on O3-T (pre-registered rules)", ""]
    fam = []
    for t, m in TIERS.items():
        for s, sub, label in PRIMARY:
            r = rows.get((f"o3t_b0_{m}_{s}", f"o3t_final_{m}_{s}", sub))
            fam.append((t, label, r))
    adj = holm([r["mcnemar_p"] if r else 1.0 for _, _, r in fam])
    res = {t: {"checks": {}} for t in TIERS}
    L += ["## Primary sets (Holm-adjusted across 6 tests)", "",
          "| Tier | Set | Cases | O3-B0 | O3-final | Difference [95% CI] | McNemar p | Holm p | Verdict |",
          "|---|---|---:|---:|---:|---|---:|---:|---|"]
    for (t, label, r), pa in zip(fam, adj):
        if r is None:
            L.append(f"| {t} | {label} | – | – | – | not run | – | – | missing |")
            res[t]["checks"][label] = "missing"
            continue
        nb = r.get("noise_bound_pts")
        sig = pa < 0.05 and (r["ci"][0] > 0 or r["ci"][1] < 0) and (nb is None or abs(r["diff_pts"]) > nb)
        v = ("better" if r["diff_pts"] > 0 else "worse") if sig else "tie"
        res[t]["checks"][label] = v
        L.append(f"| {t} | {label} | {r['n']} | {r['base_rate']:.1%} | {r['new_rate']:.1%} | {r['diff_pts']:+.1f} "
                 f"[{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {r['mcnemar_p']:.3g} | {pa:.3g} | **{v}** |")

    dl_dir = os.path.join(R, "_dialogues_step14")
    dsum = load(os.path.join(dl_dir, "summary.json")) if os.path.exists(os.path.join(dl_dir, "summary.json")) else {}
    drows = []
    if os.path.exists(os.path.join(dl_dir, "dialogues.csv")):
        with open(os.path.join(dl_dir, "dialogues.csv"), encoding="utf-8-sig") as f:
            drows = list(csv.DictReader(f))
    L += ["", "## Dialogues (60 fresh profiles)", "",
          "| Tier | Run | Recommended | ≥2 slots known | Questions max | Fit (mean) | Fit vs O3-B0 [95% CI] | Targets |",
          "|---|---|---:|---:|---:|---:|---|---|"]
    for t, m in TIERS.items():
        fin, base = dsum.get(f"o3t_final_{m}_dlg"), dsum.get(f"o3t_b0_{m}_dlg")
        if not fin:
            res[t]["checks"]["dialogues"] = "missing"
            L.append(f"| {t} | o3t_final_{m}_dlg | not run | | | | | missing |")
            continue
        pf = paired_fit(drows, f"o3t_b0_{m}_dlg", f"o3t_final_{m}_dlg") if base else None
        ok = fin["recommended"] >= 0.95 and fin["slots2_share"] >= 0.85 and fin["questions_max"] <= 2 \
            and fin["fit_mean"] >= 0.90 and (pf is None or pf[2] >= 0)
        res[t]["checks"]["dialogues"] = "met" if ok else "not met"
        for name, s_ in (("O3-B0", base), ("O3-final", fin)):
            if s_:
                L.append(f"| {t} | {name} | {s_['recommended']:.0%} | {s_['slots2_share']:.0%} | {s_['questions_max']} "
                         f"| {s_['fit_mean']:.0%} | "
                         + (f"{100 * pf[0]:+.1f} [{100 * pf[1]:+.1f}, {100 * pf[2]:+.1f}]" if pf and name == "O3-final" else "")
                         + f" | {('met' if ok else 'not met') if name == 'O3-final' else ''} |")

    sp_path = os.path.join(R, "_compare_step14_speed", "compare.json")
    L += ["", "## Tier A in place (2B on CPU, test speed subset, 2 repeats)", "",
          "| Set | Cases | First word change s [95% CI] | Total reply time change s [95% CI] | Rule |", "|---|---:|---|---|---|"]
    if os.path.exists(sp_path):
        w = {(x["base"], x["new"]): x for x in load(sp_path).get("waits", [])}
        oks = []
        for s, label in (("rag", "store questions"), ("v12", "tool cases")):
            x = w.get((f"o3tsp_a_2b_{s}_b0", f"o3tsp_a_2b_{s}_final"))
            if not x:
                oks.append(False)
                L.append(f"| {label} | – | not run | | missing |")
                continue
            ok = x["total_s"][2] < 0 and x["first_word_s"][1] <= 0
            oks.append(ok)
            fw, tt = x["first_word_s"], x["total_s"]
            L.append(f"| {label} | {x['n']} | {fw[0]:+.2f} [{fw[1]:+.2f}, {fw[2]:+.2f}] | {tt[0]:+.2f} [{tt[1]:+.2f}, "
                     f"{tt[2]:+.2f}] | {'met' if ok else 'not met'} |")
        res["A"]["checks"]["timing"] = "met" if all(oks) else "not met"
    else:
        res["A"]["checks"]["timing"] = "missing"
        L.append("| – | – | not run | | missing |")

    L += ["", "## Verdicts", ""]
    for t in TIERS:
        c = res[t]["checks"]
        ok = all(c.get(l) in ("better", "tie") for _, _, l in PRIMARY) and c.get("follow-ups") == "better" \
            and c.get("dialogues") == "met" and (t != "A" or c.get("timing") == "met")
        res[t]["confirmed"] = ok
        L.append(f"- Tier {t}: **{'confirmed' if ok else 'not confirmed'}** ({', '.join(f'{k}: {v}' for k, v in c.items())})")

    L += ["", "## Reported, not used to decide", "",
          "| Base | New | Subset | Cases | Base | New | Difference [95% CI] | Verdict (unadjusted) |", "|---|---|---|---:|---:|---:|---|---|"]
    for r in q["rows"]:
        primary = any(r["base"].endswith(f"_{s}") and r["subset"] == sub for s, sub, _ in PRIMARY) and "final12" not in r["new"]
        if primary or r["subset"].startswith("tool cases:") and r["n"] < 10:
            continue
        L.append(f"| {r['base']} | {r['new']} | {r['subset']} | {r['n']} | {r['base_rate']:.1%} | {r['new_rate']:.1%} "
                 f"| {r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {r['verdict']} |")
    os.makedirs(os.path.join(R, "_step14"), exist_ok=True)
    with open(os.path.join(R, "_step14", "verdicts.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(R, "_step14", "verdicts.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
