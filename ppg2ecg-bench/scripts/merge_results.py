"""Merge result folders from several runs (e.g. one Kaggle kernel per model) and
recompute every summary table.

    python scripts/merge_results.py --out results/track1 results/k20 results/k21 results/k30 ...

Reads windows.csv / records.csv / profile.csv from every input folder
(searched recursively), concatenates them, and writes subjects.csv,
summary.csv, skin_tone.csv, ranks.json, profile.csv into --out.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import aggregate  # noqa: E402
from scripts.run_benchmark import HEADLINE  # noqa: E402


def expand(inputs):
    """Accept folders or glob patterns (PowerShell does not expand `out/k*` itself)."""
    import glob
    out = []
    for x in inputs:
        out += sorted(glob.glob(x)) if any(c in x for c in "*?[") else [x]
    return [d for d in out if Path(d).is_dir()]


def collect(dirs, name):
    # ids as strings: CapnoBase "0009" would otherwise become 9 in some files and escape de-duplication
    ids = {"subject": str, "record": str, "segment": str}
    # smoke-test folders (k10, k89) hold 2-subject trial runs: never merge them
    frames = [pd.read_csv(p, dtype=ids) for d in dirs for p in Path(d).rglob(name)
              if p.stat().st_size > 1 and "smoke" not in p.parts]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("inputs", nargs="+")
    a = ap.parse_args()
    a.inputs = expand(a.inputs)
    print(f"merging {len(a.inputs)} folders: {' '.join(Path(d).name for d in a.inputs)}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    W, R, P = collect(a.inputs, "windows.csv"), collect(a.inputs, "records.csv"), collect(a.inputs, "profile*.csv")
    keys = aggregate.KEYS + ["subject"] + (["record"] if "record" in W else []) + ["t_start"]
    examples = [p for d in a.inputs for p in Path(d).rglob("examples/*.npz")]
    if examples:
        (out / "examples").mkdir(exist_ok=True)
        for p in examples:
            target = out / "examples" / p.name
            if not target.exists():
                target.write_bytes(p.read_bytes())
    W = W.drop_duplicates(subset=[k for k in keys if k in W])
    R = R.drop_duplicates(subset=[k for k in aggregate.KEYS + ["subject", "record"] if k in R])
    S = aggregate.subject_table(W, R)
    summ = aggregate.summary(S, HEADLINE)
    skin = aggregate.by_skin_tone(S, HEADLINE)
    W.to_csv(out / "windows.csv", index=False)
    R.to_csv(out / "records.csv", index=False)
    S.to_csv(out / "subjects.csv", index=False)
    summ.to_csv(out / "summary.csv", index=False)
    if len(skin):
        skin.to_csv(out / "skin_tone.csv", index=False)
    if len(P):
        P.to_csv(out / "profile.csv", index=False)
    ranks = [aggregate.mean_ranks(summ[summ.condition == "clean"], m) for m in ("hr_ae", "pearson_lag", "beat_pearson", "rmse")]
    json.dump(ranks, open(out / "ranks.json", "w"), indent=2, default=float)
    print(summ[["model", "dataset", "condition", "seen", "n_subjects", "hr_ae", "pearson_lag", "beat_pearson"]]
          .round(3).to_string(index=False))
    print(f"\nmerged {len(W)} windows from {len(a.inputs)} folders -> {out}")


if __name__ == "__main__":
    main()
