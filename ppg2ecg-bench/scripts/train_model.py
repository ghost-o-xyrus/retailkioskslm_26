"""Train one code-only model with its authors' recipe (Track 1, "authors' recipe, our training").

    python scripts/train_model.py chiu   --repo REPO --out OUT --work WORK [--budget-h 2] [--smoke]
    python scripts/train_model.py clep   --repo REPO --bidmc-csv DIR --out OUT --work WORK [--budget-h 5]
    python scripts/train_model.py p2e    --repo REPO --out OUT --work WORK [--cache-maf DIR] [--budget-h 4]
    python scripts/train_model.py yalcin --repo REPO --cache-maf DIR --out OUT [--budget-h 4.5]

OUT receives weights.pth, meta.json (inference recipe, data stats, budget info) and train_log.txt.
REPO is a clone of the authors' repository (the Kaggle job clones it and records the commit).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=["chiu", "clep", "p2e", "yalcin"])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", default=None)
    ap.add_argument("--budget-h", type=float, default=None)
    ap.add_argument("--smoke", action="store_true", help="tiny data, 1-2 epochs: checks the plumbing only")
    ap.add_argument("--bidmc-csv", default=None, help="folder with bidmc_XX_Signals.csv (CLEP-GAN)")
    ap.add_argument("--cache-maf", default=None, help="MIMIC PERform AF cache (Yalcin, P2E fallback)")
    a = ap.parse_args()
    work = Path(a.work or Path(a.out) / "_work")
    budget = a.budget_h or {"chiu": 2.0, "clep": 5.0, "p2e": 4.0, "yalcin": 4.5}[a.model]
    if a.smoke:
        budget = min(budget, 0.15)

    def maf():
        from bench.datasets import load_from_cache
        return list(load_from_cache(a.cache_maf, "mimic_perform_af"))

    if a.model == "chiu":
        from bench.train import chiu
        chiu.train(a.repo, a.out, work, budget_h=budget, smoke=a.smoke)
    elif a.model == "clep":
        from bench.train import clep
        clep.train(a.repo, a.bidmc_csv, a.out, work, budget_h=budget, smoke=a.smoke)
    elif a.model == "p2e":
        from bench.train import p2e
        p2e.train(a.repo, a.out, work, budget_h=budget, smoke=a.smoke, fallback_records=maf() if a.cache_maf else None)
    else:
        from bench.train import yalcin
        yalcin.train(a.repo, maf(), a.out, budget_h=budget, smoke=a.smoke)


if __name__ == "__main__":
    main()
