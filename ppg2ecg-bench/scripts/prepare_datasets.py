"""Convert raw datasets (as distributed) into the canonical Record cache.

    python scripts/prepare_datasets.py --out cache \
        --bidmc data/bidmc --capnobase data/capnobase --dalia data/PPG_FieldStudy \
        --wesad data/WESAD --aurora_bp data/aurora-bp

Writes  <out>/<dataset>/<subject>[__<segment>].npz  plus  <out>/inventory.csv
(one row per record: duration, rates, site, lead, Fitzpatrick) and prints a
per-dataset summary including the Fitzpatrick distribution.
Datasets whose path is not given are skipped.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.datasets import LOADERS  # noqa: E402

NAMES = ["bidmc", "capnobase", "dalia", "wesad", "aurora_bp", "mimic_perform_af"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    for n in NAMES:
        ap.add_argument(f"--{n}", default=None, help=f"raw root folder of {n}")
    ap.add_argument("--aurora-max-records", type=int, default=None,
                    help="cap 30-s Aurora files per subject (None = all)")
    a = ap.parse_args()
    out = Path(a.out)
    rows = []
    for n in NAMES:
        root = getattr(a, n)
        if not root:
            continue
        kw = {"max_records_per_subject": a.aurora_max_records} if n == "aurora_bp" else {}
        t0, k = time.time(), 0
        try:
            for rec in LOADERS[n](root, **kw):
                rec.save(out / n / f"{rec.record_id}.npz")
                rows.append(dict(dataset=n, subject=rec.subject, record=rec.record_id, seconds=round(rec.duration, 1),
                                 ppg_fs=rec.ppg_fs, ecg_fs=rec.ecg_fs, ppg_site=rec.ppg_site, ecg_lead=rec.ecg_lead,
                                 fitzpatrick=rec.meta.get("fitzpatrick", np.nan), phase=rec.meta.get("phase"),
                                 af=rec.meta.get("af")))
                k += 1
        except FileNotFoundError as e:
            print(f"[skip] {n}: {e}")
            continue
        print(f"[ok] {n}: {k} records in {time.time() - t0:.0f}s")

    inv = pd.DataFrame(rows)
    out.mkdir(parents=True, exist_ok=True)
    inv.to_csv(out / "inventory.csv", index=False)
    if len(inv):
        g = inv.groupby("dataset").agg(subjects=("subject", "nunique"), records=("record", "size"),
                                       hours=("seconds", lambda s: round(s.sum() / 3600, 1)))
        print(g.to_string())
        fz = inv.drop_duplicates(["dataset", "subject"]).dropna(subset=["fitzpatrick"])
        if len(fz):
            print("\nFitzpatrick distribution (subjects):")
            print(fz.groupby(["dataset", "fitzpatrick"]).size().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()
