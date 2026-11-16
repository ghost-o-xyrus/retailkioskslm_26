"""Run released models through their AUTHORS' pipeline and through ours, on the same records.

    python scripts/author_eval.py <resolved config.yaml> --model rddm --out results/author_eval \
        [--datasets bidmc capnobase dalia wesad mimic_perform_af aurora_bp] [--max-subjects 100]

For every (model, dataset) three numbers families are produced from ONE set of records:
  A  authors' preprocessing + authors' metrics          ("as the paper would report it")
  B  authors' preprocessing + our metrics               (same predictions, our scoring)
  C  our preprocessing + our metrics                    (= Track 1; read from the Track 1 results)
A vs B isolates the effect of the METRIC definitions; B vs C the effect of PREPROCESSING/windowing.
Seen datasets (the model's own training data) vs unseen ones gives the zero-shot drop under both
pipelines. Published numbers for comparison are in registry/published_results.yaml.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import author_pipelines as ap_, dsp, metrics  # noqa: E402
from bench.datasets import LOADERS  # noqa: E402
from bench.models import build  # noqa: E402
from scripts.run_benchmark import first_subjects, seen_tag  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("config")
    p.add_argument("--model", required=True, choices=sorted(ap_.PREP))
    p.add_argument("--out", required=True)
    p.add_argument("--datasets", nargs="*")
    p.add_argument("--max-subjects", type=int, default=100, help="per dataset (Aurora-BP has 1,209)")
    a = p.parse_args()
    cfg = yaml.safe_load(open(a.config))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    m = next(x for x in cfg["models"] if x["name"] == a.model)
    adapter = build(m["name"], **m.get("kwargs", {}))
    adapter.load()
    prep = ap_.PREP[a.model]
    rows, rec_rows = [], []
    for d in cfg["datasets"]:
        if a.datasets and d["name"] not in a.datasets:
            continue
        kw = {k: v for k, v in d.items() if k not in ("name", "loader", "max_subjects")}
        recs = first_subjects(list(LOADERS[d.get("loader", d["name"])](**kw)), a.max_subjects)
        t0 = time.time()
        R, F, extra = [], [], {}
        for rec in recs:
            P, E, info = prep(rec)
            if len(P) == 0:
                continue
            Y = adapter.infer(P.astype(np.float32))
            R.append(E), F.append(Y)
            for k, v in info.items():
                extra[k] = extra.get(k, 0) + v
            # B: our metrics on the same predictions (windows concatenated, our reference ECG)
            pred = Y.reshape(-1)
            true = dsp.resample(rec.ecg, rec.ecg_fs, ap_.FS)[: len(pred)]
            wr, rr = metrics.evaluate(pred[: len(true)], true, ap_.FS, compute_fd=False)
            wdf = pd.DataFrame(wr)
            rec_rows.append(dict(model=a.model, dataset=d["name"], subject=rec.subject, record=rec.record_id,
                                 seen=seen_tag(adapter, d["name"]), r_f1=rr["r_f1"],
                                 r_timing_median_ms=rr["r_timing_median_ms"], rmssd_ae=rr["rmssd_ae"],
                                 hr_ae=wdf.hr_ae.mean(), pearson_lag=wdf.pearson_lag.mean(),
                                 beat_pearson=wdf.beat_pearson.mean(), rmse=wdf.rmse.mean()))
        if not R:
            continue
        R, F = np.concatenate(R), np.concatenate(F)
        am = ap_.author_metrics(a.model, R, F)                      # A
        ours = pd.DataFrame([r for r in rec_rows if r["dataset"] == d["name"]])
        subj = ours.groupby("subject")[["hr_ae", "r_f1", "beat_pearson", "pearson_lag", "rmssd_ae"]].mean().mean()
        rows.append(dict(model=a.model, dataset=d["name"], seen=seen_tag(adapter, d["name"]), n_records=len(ours),
                         n_subjects=ours.subject.nunique(),
                         **{f"A_{k}": v for k, v in am.items()}, **{f"B_{k}": v for k, v in subj.items()}, **extra))
        print(f"[{a.model}/{d['name']}] {len(R)} windows in {time.time() - t0:.0f}s  A={am}", flush=True)
        pd.DataFrame(rows).to_csv(out / f"author_eval_{a.model}.csv", index=False)
        pd.DataFrame(rec_rows).to_csv(out / f"author_eval_{a.model}_records.csv", index=False)
    print(pd.DataFrame(rows).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
