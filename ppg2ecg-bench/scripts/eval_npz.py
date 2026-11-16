"""Score an existing results file (N x L segments) with the benchmark metrics.

Works with the files your test_bidmc_cardiogan.py already produced:

    python -m scripts.eval_npz bidmc_01_cardiogan_results.npz --fs 128

Segments are concatenated back into one continuous stream (they were cut
consecutively), then scored exactly like a harness run.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import metrics  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npz")
    ap.add_argument("--fs", type=float, default=128.0)
    ap.add_argument("--pred-key", default="ecg_generated")
    ap.add_argument("--true-key", default="ecg_true")
    ap.add_argument("--window-s", type=float, default=10.0)
    ap.add_argument("--no-band", action="store_true", help="skip the common 0.5-40 Hz eval filter")
    a = ap.parse_args()

    z = np.load(a.npz)
    pred, true = z[a.pred_key].ravel(), z[a.true_key].ravel()
    rows, rec = metrics.evaluate(pred, true, a.fs, window_s=a.window_s,
                                 eval_band=None if a.no_band else (0.5, 40.0))
    df = pd.DataFrame(rows)
    keys = ["hr_ae", "rmse", "pearson", "prd", "fd", "rmse_lag", "pearson_lag", "best_lag_ms",
            "beat_pearson", "beat_rmse", "r_timing_mae_ms"]
    print(f"{a.npz}: {len(pred) / a.fs:.0f} s, {len(df)} windows of {a.window_s:g} s")
    print(df[keys].describe().loc[["mean", "50%", "std"]].round(3).to_string())
    print("\nrecord level:", {k: round(v, 3) for k, v in rec.items()})


if __name__ == "__main__":
    main()
