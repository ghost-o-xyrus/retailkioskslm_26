"""
Objective 3, Step 15: the ablation ladder table on the test set O3-T (runs from eval/build_o3_ladder.py).

    python eval\\step15_ladder.py

Reads results_obj3/o3l_* (Kaggle CPU) and, for the cross-check, the Step 14 runs results_obj3/o3t_* (laptop).
Writes results_obj3/_step15/ladder.md and ladder.json, and the paired comparisons under
results_obj3/_step15/compare (eval/compare_dev.py) and results_obj3/_step15/dialogues.

What it reports (descriptive: the confirming decision was Step 14; nothing here is Holm-adjusted):
  - per model, each rung's pass rate per set and its step against the rung below it (paired, automatic checks,
    the compare_dev verdict: noise bound and bootstrap interval), and the whole ladder (O3-B0 -> R6);
  - the router's own effect: O3-final against O3-final without the router;
  - reading per rung: model rounds, tokens read before the answer, empty replies, printed tool calls;
  - two success criteria that need a reference: answerable store questions within 5 points of oracle cards
    (O3-final - oracle >= -5 points), and tool cases not significantly below no retrieval (Stage 3);
  - the cross-check: O3-B0 and O3-final on Kaggle CPU against the same configurations in Step 14 (laptop,
    Vulkan). Agreement here means the CPU ladder speaks for the deployed runs.
Waits on Kaggle are not the kiosk's machine, so no latency appears here (the laptop numbers are in Step 14).
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
R = os.path.join(ROOT, "results_obj3")
OUT = os.path.join(R, "_step15")
P = "o3l_"            # the ladder's runs: o3l_ (Kaggle CPU) or, with --gpu, o3g_ (Kaggle T4 GPU)
LADDER = ["b0", "r1", "r2", "r3", "r4", "r5", "r6"]
LABEL = {"b0": "O3-B0", "r1": "R1 + tool output v2, loop guard", "r2": "R2 + router",
         "r3": "R3 + harness tools, discovery, forced answers", "r4": "R4 + fallback, entity and staff checks",
         "r5": "R5 + answer check, follow-up retrieval", "r6": "R6 = O3-final (speed work)",
         "nr": "O3-final without router"}
SETS = [("rag", "all checked", "Store questions"), ("rag", "answerable", "answerable"),
        ("rag", "unanswerable / near-miss", "unanswerable / near-miss"), ("v12", "tool cases", "Tool cases"),
        ("fup", "all checked", "Follow-ups")]
MODELS = (("2b", "Tier A (2B)"), ("4b", "Tier B (4B)"))


def d(name):
    return os.path.join(R, name)


def have(name):
    return os.path.exists(os.path.join(d(name), "run_meta.json"))


def main(argv=None):
    global P, OUT
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--gpu" in argv:                  # the GPU ladder; references and the CPU runs stay as they are
        P, OUT = "o3g_", os.path.join(R, "_step15_gpu")
    import compare_dev
    import score_dialogues as SD
    os.makedirs(OUT, exist_ok=True)
    pairs = []
    for m, _ in MODELS:
        for s in ("rag", "v12", "fup"):
            for a, b in zip(LADDER, LADDER[1:]):
                pairs.append((f"{P}{a}_{m}_{s}", f"{P}{b}_{m}_{s}"))
            pairs += [(f"{P}b0_{m}_{s}", f"{P}r6_{m}_{s}"), (f"{P}nr_{m}_{s}", f"{P}r6_{m}_{s}"),
                      (f"o3t_b0_{m}_{s}", f"{P}b0_{m}_{s}"), (f"o3t_final_{m}_{s}", f"{P}r6_{m}_{s}")]
            if P != "o3l_":              # GPU ladder: the CPU runs of the same configurations, as a second check
                pairs += [(f"o3l_b0_{m}_{s}", f"{P}b0_{m}_{s}"), (f"o3l_r6_{m}_{s}", f"{P}r6_{m}_{s}")]
        pairs += [(f"o3l_ref_{m}_oracle", f"o3l_r6_{m}_rag"), (f"o3l_ref_{m}_none", f"o3l_r6_{m}_v12")]
    ok = [(a, b) for a, b in pairs if have(a) and have(b)]
    missing = sorted({x for p in pairs for x in p if not have(x)})
    noise = os.path.join(R, "_noise_floor", "noise.json")
    argv_c = [x for a, b in ok for x in ("--pair", d(a), d(b))] + (["--noise", noise] if os.path.exists(noise) else []) \
        + ["--out", os.path.join(OUT, "compare")]
    rows, speed = [], []
    if ok:
        compare_dev.main(argv_c)
        with open(os.path.join(OUT, "compare", "compare.json"), encoding="utf-8") as f:
            cj = json.load(f)
        rows, speed = cj["rows"], cj["speed"]
    row = {(r["base"], r["new"], r["subset"]): r for r in rows}
    sp = {(s["base"], s["new"]): s for s in speed}
    rate = {}
    for r in rows:
        rate[(r["base"], r["subset"])] = (r["base_rate"], r["n"])
        rate[(r["new"], r["subset"])] = (r["new_rate"], r["n"])

    # dialogues
    prof = SD.profiles(os.path.join(HERE, "o3_dialogues.jsonl"))
    dlg = {}
    for m, _ in MODELS:
        for k in LADDER + ["nr"]:
            n = f"{P}{k}_{m}_dlg"
            if have(n):
                meta, res = SD.score_run(d(n), prof)
                if res:
                    dlg[n] = (SD.summary(n, meta, res), res)
        for n in (f"o3t_b0_{m}_dlg", f"o3t_final_{m}_dlg"):
            if have(n):
                meta, res = SD.score_run(d(n), prof)
                if res:
                    dlg[n] = (SD.summary(n, meta, res), res)
    if not dlg and have(f"{P}r6_2b_dlg"):
        missing.append(f"{P}*_dlg (no dialogue scored)")

    def dfit(a, b):
        if a not in dlg or b not in dlg:
            return None
        A, B = dlg[a][1], dlg[b][1]
        both = [i for i in sorted(set(A) & set(B)) if A[i]["fit"] is not None and B[i]["fit"] is not None]
        return SD.boot([A[i]["fit"] for i in both], [B[i]["fit"] for i in both]) if both else None

    def cell(name, prev, subset):
        if (name, subset) not in rate:
            return "–"
        v, _ = rate[(name, subset)]
        txt = f"{100 * v:.1f}%"
        r = row.get((prev, name, subset)) if prev else None
        if r:
            mark = {"better": " ▲", "worse": " ▼"}.get(r["verdict"], "")
            txt += f" ({r['diff_pts']:+.1f}{mark})"
        return txt

    L = [f"# Step 15: ablation ladder on the test set O3-T ({'Kaggle T4 GPU' if P == 'o3g_' else 'Kaggle CPU'})", "",
         "Each rung adds the changes kept on dev, in the order they were kept. Cells: pass rate (automatic checks), "
         "then in brackets the step from the rung above in points; ▲/▼ = better/worse by compare_dev's rule "
         "(beyond the noise bound, bootstrap interval excludes 0), unadjusted and descriptive. Dialogues: fit of "
         "shown watches (mean) and share that reached a recommendation.", ""]
    out = {"rows": rows, "dialogues": {k: v[0] for k, v in dlg.items()}, "missing": missing}
    for m, tier in MODELS:
        L += [f"## {tier}", "",
              "| Rung | " + " | ".join(x[2] for x in SETS) + " | Dialogues: fit / recommended |",
              "|---|" + "---:|" * (len(SETS) + 1)]
        for i, k in enumerate(LADDER + ["nr"]):
            prev = None if k == "b0" else (LADDER[i - 1] if k != "nr" else None)
            cells = []
            for s, sub, _ in SETS:
                cells.append(cell(f"{P}{k}_{m}_{s}", f"{P}{prev}_{m}_{s}" if prev else None, sub))
            dn = f"{P}{k}_{m}_dlg"
            if dn in dlg:
                sm = dlg[dn][0]
                dc = f"{100 * (sm['fit_mean'] or 0):.0f}% / {100 * (sm['recommended'] or 0):.0f}%"
                if prev:
                    df = dfit(f"{P}{prev}_{m}_dlg", dn)
                    if df:
                        dc += f" ({100 * df[0]:+.1f}{' ▲' if df[1] > 0 else ' ▼' if df[2] < 0 else ''})"
            else:
                dc = "–"
            L.append(f"| {LABEL[k]} | " + " | ".join(cells) + f" | {dc} |")
        # whole ladder and router effect
        L += ["", "| Comparison | Set | Cases | Base | New | New − base [95% CI] | McNemar p | Verdict |",
              "|---|---|---:|---:|---:|---|---:|---|"]
        for a, b, what in ((f"{P}b0_{m}", f"{P}r6_{m}", "Whole ladder: O3-final − O3-B0"),
                           (f"{P}nr_{m}", f"{P}r6_{m}", "Router's effect: O3-final − without router")):
            for s, sub, lab in SETS:
                r = row.get((f"{a}_{s}", f"{b}_{s}", sub))
                if r:
                    L.append(f"| {what} | {lab} | {r['n']} | {r['base_rate']:.1%} | {r['new_rate']:.1%} "
                             f"| {r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {r['mcnemar_p']:.3g} "
                             f"| {r['verdict']} |")
            df = dfit(f"{a}_dlg", f"{b}_dlg")
            if df:
                L.append(f"| {what} | dialogue fit | {len(dlg[f'{b}_dlg'][1])} | – | – | {100 * df[0]:+.1f} "
                         f"[{100 * df[1]:+.1f}, {100 * df[2]:+.1f}] | – | – |")
        # reading per rung
        L += ["", "Reading per rung (same runs; machine-independent counts):", "",
              "| Rung | Set | Model rounds | Tokens read | Tokens per tool output | Empty replies | Printed tool calls "
              "| Calls run by the harness |", "|---|---|---:|---:|---:|---:|---:|---|"]
        for i, k in enumerate(LADDER + ["nr"]):
            for s in ("rag", "v12", "fup"):
                n = f"{P}{k}_{m}_{s}"
                hit = next(((x["new_speed"], x["new_disc"]) for (bb, nn), x in sp.items() if nn == n), None) or \
                    next(((x["base_speed"], x["base_disc"]) for (bb, nn), x in sp.items() if bb == n), None)
                if not hit:
                    continue
                sv, dv = hit
                f = lambda v, nd=2: "–" if v is None else f"{v:.{nd}f}"   # noqa: E731
                L.append(f"| {LABEL[k]} | {s} | {f(sv['rounds'])} | {f(sv['tok_read'], 0)} | "
                         f"{f(sv['tok_per_tool_output'], 0)} | {sv['empty_replies']} | {dv['printed']} | "
                         f"{sv['harness_calls']}/{sv['calls']} |")
        # references
        L += ["", "Criteria that need a reference (Kaggle CPU, paired):", "",
              "| Criterion | Cases | Reference | O3-final | O3-final − reference [95% CI] | Met |", "|---|---:|---:|---:|---|---|"]
        r = row.get((f"o3l_ref_{m}_oracle", f"o3l_r6_{m}_rag", "answerable"))
        if r:
            met = "yes" if r["diff_pts"] >= -5 else "no"
            L.append(f"| Answerable store questions within 5 points of oracle cards | {r['n']} | {r['base_rate']:.1%} "
                     f"| {r['new_rate']:.1%} | {r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {met} |")
            out[f"oracle_{m}"] = r
        r = row.get((f"o3l_ref_{m}_none", f"o3l_r6_{m}_v12", "tool cases"))
        if r:
            met = "no" if r["verdict"] == "worse" else "yes"
            L.append(f"| Tool cases not significantly below no retrieval (Stage 3) | {r['n']} | {r['base_rate']:.1%} "
                     f"| {r['new_rate']:.1%} | {r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {met} |")
            out[f"stage3_{m}"] = r
        # cross-check
        L += ["", "Cross-check against Step 14 (laptop, Vulkan → Kaggle CPU, same configuration):", "",
              "| Configuration | Set | Cases | Laptop | Kaggle | Kaggle − laptop [95% CI] | Cases that flipped | Verdict |",
              "|---|---|---:|---:|---:|---|---:|---|"]
        checks = [(f"o3t_b0_{m}", f"{P}b0_{m}", "O3-B0"), (f"o3t_final_{m}", f"{P}r6_{m}", "O3-final")]
        if P != "o3l_":
            checks += [(f"o3l_b0_{m}", f"{P}b0_{m}", "O3-B0, Kaggle CPU → GPU"),
                       (f"o3l_r6_{m}", f"{P}r6_{m}", "O3-final, Kaggle CPU → GPU")]
        for a, b, lab in checks:
            for s, sub, slab in SETS:
                r = row.get((f"{a}_{s}", f"{b}_{s}", sub))
                if r:
                    L.append(f"| {lab} | {slab} | {r['n']} | {r['base_rate']:.1%} | {r['new_rate']:.1%} "
                             f"| {r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {r['lost'] + r['gained']} "
                             f"| {r['verdict']} |")
            if f"{a}_dlg" in dlg and f"{b}_dlg" in dlg:
                sa, sb = dlg[f"{a}_dlg"][0], dlg[f"{b}_dlg"][0]
                L.append(f"| {lab} | dialogue fit | {sb['dialogues']} | {100 * (sa['fit_mean'] or 0):.0f}% "
                         f"| {100 * (sb['fit_mean'] or 0):.0f}% | – | – | – |")
        L.append("")
    if missing:
        L += ["## Not yet available", "", "Runs with no results yet (the ladder table fills in as they arrive):", ""] \
            + [f"- {x}" for x in missing]
    with open(os.path.join(OUT, "ladder.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(OUT, "ladder.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"Wrote {os.path.join(OUT, 'ladder.md')}" + (f" ({len(missing)} runs not available yet)" if missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
