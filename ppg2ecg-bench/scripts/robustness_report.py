"""Robustness evaluation on the merged Track 1 results.

    python scripts/robustness_report.py results/track1

Reads <dir>/windows.csv (written by merge_results.py) and writes:
  robustness_coverage.csv  subjects per model x dataset x condition (missing blocks are flagged)
  robustness_subjects.csv  per-subject metrics for every condition, incl. the clean_subset reference
  robustness.csv           per model x dataset x condition: mean, paired change vs clean_subset, 95% bootstrap CI

Why "clean_subset": robustness conditions run on a fixed subset (first N subjects, first 600 s),
but "clean" ran on every subject and the whole record. Comparing against full clean mixes subject
differences into the degradation. clean_subset = the clean windows of the SAME subjects inside the
SAME first 600 s, taken from the existing clean run - no re-inference needed.

Metrics are window-level only (hr_ae, beat_pearson, pearson_lag, rmse_lag, R-peak F1 pooled from
window TP/FN/FP). Record-level RMSSD cannot be cropped after the fact and is left out here.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

IDS = {"subject": str, "record": str, "segment": str}
LOWER_IS_BETTER = {"hr_ae": True, "rmse_lag": True, "r_f1": False, "beat_pearson": False, "pearson_lag": False}
GROUP = ["model", "dataset", "condition"]


def subject_metrics(w: pd.DataFrame) -> pd.DataFrame:
    g = w.groupby(GROUP + ["subject"])
    s = g[[m for m in ("hr_ae", "beat_pearson", "pearson_lag", "rmse_lag") if m in w]].mean()
    tp, fn, fp = g["r_tp"].sum(), g["r_fn"].sum(), g["r_fp"].sum()
    s["r_f1"] = 2 * tp / (2 * tp + fn + fp).replace(0, np.nan)
    s["n_windows"] = g.size()
    return s.reset_index()


def boot_ci(x, n=2000, seed=0):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return np.nan, np.nan
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir")
    ap.add_argument("--max-seconds", type=float, default=600, help="eval.perturb_subset.max_seconds of the run")
    ap.add_argument("--window-s", type=float, default=10, help="eval.window_s of the run")
    a = ap.parse_args()
    d = Path(a.results_dir)
    W = pd.read_csv(d / "windows.csv", dtype=IDS, low_memory=False)

    rob = W[W.condition != "clean"]
    if rob.empty:
        raise SystemExit("no robustness rows in windows.csv - were k21/k31/k40b/k22/k32/k42 merged?")
    # clean_subset: same model/dataset/subject as the robustness runs, inside the cropped time span
    keys = rob[["model", "dataset", "subject"]].drop_duplicates()
    clean = W[W.condition == "clean"].merge(keys, on=["model", "dataset", "subject"])
    clean = clean[clean.t_start + a.window_s <= a.max_seconds + 1e-6].assign(condition="clean_subset")
    S = subject_metrics(pd.concat([W[W.condition == "clean"], clean, rob], ignore_index=True))

    # coverage: every model should have every dataset x condition
    cov = S.pivot_table(index=["dataset", "condition"], columns="model", values="subject", aggfunc="count").fillna(0).astype(int)
    cov.to_csv(d / "robustness_coverage.csv")
    missing = [(m, ds, c) for (ds, c), row in cov.iterrows() for m, n in row.items() if n == 0]
    print("== coverage (subjects) ==\n" + cov.to_string())
    print(f"\n{len(missing)} empty blocks" + (": " + ", ".join(f"{m}/{ds}/{c}" for m, ds, c in missing[:20]) if missing else " - complete"))

    # paired change vs clean_subset, per subject
    ref = S[S.condition == "clean_subset"].set_index(["model", "dataset", "subject"])
    rows = []
    metrics = [m for m in LOWER_IS_BETTER if m in S]
    for (m, ds, c), grp in S[S.condition != "clean"].groupby(GROUP):
        row = dict(model=m, dataset=ds, condition=c, n_subjects=grp.subject.nunique())
        g = grp.set_index(["model", "dataset", "subject"])
        for k in metrics:
            row[k] = g[k].mean()
            if c != "clean_subset":
                delta = (g[k] - ref[k].reindex(g.index)).dropna()
                row[f"d_{k}"] = delta.mean() if len(delta) else np.nan
                lo, hi = boot_ci(delta)
                row[f"d_{k}_ci"] = f"[{lo:.3g}, {hi:.3g}]"
        rows.append(row)
    R = pd.DataFrame(rows)
    S.to_csv(d / "robustness_subjects.csv", index=False)
    R.to_csv(d / "robustness.csv", index=False)

    pd.set_option("display.width", 220)
    for k in ("hr_ae", "r_f1", "beat_pearson"):
        print(f"\n== {k}: clean_subset and change under each perturbation (mean over datasets) ==")
        piv = R.pivot_table(index="condition", columns="model", values=k, aggfunc="mean")
        dpiv = R.pivot_table(index="condition", columns="model", values=f"d_{k}", aggfunc="mean")
        print(pd.concat({"value": piv, "change_vs_clean_subset": dpiv}, axis=1).round(3).to_string())
    print(f"\nwrote robustness_coverage.csv, robustness_subjects.csv, robustness.csv -> {d}")
    print("note: time_shift conditions move the PPG against the ECG on purpose; their R-peak F1 change measures"
          " timing sensitivity, not noise robustness.")


if __name__ == "__main__":
    main()
