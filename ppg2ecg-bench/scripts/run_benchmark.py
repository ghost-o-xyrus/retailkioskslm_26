"""Run the benchmark from a YAML config.

    python scripts/run_benchmark.py configs/phase1.yaml [--models cardiogan] [--conditions clean]

Writes to <output>/:
    windows.csv   one row per (model, dataset, condition, record, 10-s window)
    records.csv   record-level metrics (R-peak F1, HRV)
    subjects.csv  per-subject means
    summary.csv   per (model, dataset, condition) mean + bootstrap CI
    skin_tone.csv per Fitzpatrick group (only if any dataset carries labels)
    profile.csv   size / speed on this machine
    ranks.json    mean ranks + Friedman test per headline metric
    errors.csv    records that failed (the run continues)
    examples/     a few .npz traces per (model, dataset, condition) for plotting
windows.csv / records.csv are re-written after every (model, dataset, condition)
block, so a run that hits a time limit keeps everything finished so far.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bench import aggregate, metrics, perturb, profiler  # noqa: E402
from bench.datasets import LOADERS  # noqa: E402
from bench.models import build  # noqa: E402
from bench.runner import run_record  # noqa: E402

HEADLINE = ["hr_ae", "r_f1", "r_timing_median_ms", "rmse", "pearson", "prd", "fd",
            "rmse_lag", "pearson_lag", "beat_pearson", "beat_rmse", "rmssd_ae"]


def seen_tag(adapter, dataset):
    scope = getattr(adapter, "trained_on", {}).get(dataset)
    if scope is None:
        return "unseen"
    return "seen" if scope == "all" else "possibly_seen"


def expand_perturbations(specs):
    """Allow list-valued severities: {name: gaussian, snr_db: [20, 10]} -> two conditions."""
    out = []
    for s in specs:
        s = dict(s)
        list_keys = [k for k, v in s.items() if isinstance(v, list)]
        if not list_keys:
            out.append(s)
            continue
        k = list_keys[0]
        for v in s[k]:
            out.append({**s, k: v})
    return out


def first_subjects(recs, n):
    """Keep all records of the first n subjects (records stay in loader order)."""
    if not n:
        return recs
    keep = list(dict.fromkeys(r.subject for r in recs))[:n]
    keep = set(keep)
    return [r for r in recs if r.subject in keep]


def main(cfg_path, only_models=None, only_conditions=None, only_datasets=None):
    cfg = yaml.safe_load(open(cfg_path))
    out = Path(cfg.get("output", "results/run"))
    (out / "examples").mkdir(parents=True, exist_ok=True)
    ev = cfg.get("eval", {})
    eval_fs = ev.get("fs", 128.0)
    psub = ev.get("perturb_subset", {}) or {}

    # models first: a missing package or weight file must fail in seconds, not after an hour of data loading
    adapters = {}
    for m in cfg["models"]:
        if only_models and m["name"] not in only_models and m.get("label") not in only_models:
            continue
        adapter = build(m["name"], **m.get("kwargs", {}))
        if m.get("label"):
            adapter.name = m["label"]
        t0 = time.time()
        adapter.load()
        print(f"[load] {adapter.name} in {time.time() - t0:.1f}s", flush=True)
        adapters[id(m)] = adapter

    # robustness-only runs use just the first perturb_subset.max_subjects subjects: read only those
    robust_only = bool(only_conditions) and "clean" not in only_conditions and psub.get("max_subjects")
    data = {}
    for d in cfg["datasets"]:
        if only_datasets and d["name"] not in only_datasets:
            continue
        kw = {k: v for k, v in d.items() if k not in ("name", "loader", "max_subjects")}
        if robust_only and d.get("loader") == "cache":
            need = [psub["max_subjects"]] + ([d["max_subjects"]] if d.get("max_subjects") else [])
            if any(name == d["name"] for m in cfg["models"] for name in m.get("fit_on", [])
                   if (not only_models or m["name"] in only_models)):
                need = [d.get("max_subjects")] if d.get("max_subjects") else []   # calibration needs the full set
            if need:
                kw["max_subjects"] = min(need)
        recs = list(LOADERS[d.get("loader", d["name"])](**kw))
        data[d["name"]] = first_subjects(recs, d.get("max_subjects"))
        print(f"[data] {d['name']}: {len(data[d['name']])} records, "
              f"{len({r.subject for r in data[d['name']]})} subjects", flush=True)

    conditions = expand_perturbations(cfg.get("perturbations", [{"name": "clean"}]))
    win_rows, rec_rows, prof_rows, errors = [], [], [], []

    def flush():
        pd.DataFrame(win_rows).to_csv(out / "windows.csv", index=False)
        pd.DataFrame(rec_rows).to_csv(out / "records.csv", index=False)
        if errors:
            pd.DataFrame(errors).to_csv(out / "errors.csv", index=False)

    for m in cfg["models"]:
        if id(m) not in adapters:
            continue
        adapter = adapters[id(m)]
        adapter.trained_on = dict(getattr(adapter, "trained_on", {}))
        if "fit_on" in m:  # calibration records -> those datasets become "seen" for this model
            fit_recs = [r for name in m["fit_on"] for r in data.get(name, [])]
            if not fit_recs:
                print(f"[fit] WARNING: no records in {m['fit_on']} - {adapter.name} keeps its default parameters", flush=True)
            else:
                print(f"[fit] {adapter.name} on {len(fit_recs)} records -> {adapter.fit(fit_recs)}", flush=True)
                adapter.trained_on.update({name: "all" for name in m["fit_on"]})
        track = m.get("track", 1)
        if ev.get("profile_runs", 30):
            prof_rows.append(profiler.profile(adapter, n_runs=ev.get("profile_runs", 30)))
            pd.DataFrame(prof_rows).to_csv(out / "profile.csv", index=False)

        for dname, recs_all in data.items():
            if dname in m.get("exclude_datasets", []):
                continue
            for cond in conditions:
                f = perturb.build(cond)
                cname = "clean" if f is None else f.__name__
                if only_conditions and cname not in only_conditions and cond["name"] not in only_conditions:
                    continue
                recs = recs_all
                if f is not None and psub:  # robustness conditions run on a fixed subset
                    recs = [r.crop(psub.get("max_seconds")) for r in first_subjects(recs_all, psub.get("max_subjects"))]
                t0 = time.time()
                n_ex = 0
                for rec in recs:
                    tags = dict(model=adapter.name, track=track, dataset=dname, condition=cname,
                                seen=seen_tag(adapter, dname), subject=rec.subject, record=rec.record_id,
                                fitzpatrick=rec.meta.get("fitzpatrick", np.nan), ppg_site=rec.ppg_site)
                    try:
                        ro = run_record(adapter, rec, eval_fs=eval_fs, overlap=ev.get("overlap", 0.5), perturb=f,
                                        rng=np.random.default_rng(zlib.crc32(f"{rec.key}|{rec.record_id}|{cname}".encode())))
                        wr, rr = metrics.evaluate(ro.pred, ro.true, ro.fs, window_s=ev.get("window_s", 10.0),
                                                  eval_band=tuple(ev.get("band", (0.5, 40.0))),
                                                  compute_fd=ev.get("fd", True),
                                                  fd_max_windows=ev.get("fd_max_windows", 40))
                    except Exception as e:  # keep going; one bad record must not kill a 10-h run
                        errors.append({**tags, "error": repr(e), "trace": traceback.format_exc()[-800:]})
                        continue
                    win_rows += [{**tags, **r} for r in wr]
                    rec_rows.append({**tags, **rr, "infer_seconds": ro.infer_seconds, "n_windows": ro.n_windows})
                    if n_ex < ev.get("n_examples", 2):
                        np.savez_compressed(out / "examples" / f"{adapter.name}__{dname}__{cname}__{rec.record_id}.npz",
                                            pred=ro.pred.astype(np.float32), true=ro.true.astype(np.float32),
                                            ppg=ro.ppg.astype(np.float32), fs=ro.fs)
                        n_ex += 1
                flush()
                print(f"[run] {adapter.name:18s} {dname:10s} {cname:22s} {len(recs):5d} rec "
                      f"{time.time() - t0:7.1f}s  errors={len(errors)}", flush=True)

    if not win_rows:
        print("no results")
        return
    W, R = pd.DataFrame(win_rows), pd.DataFrame(rec_rows)
    flush()
    S = aggregate.subject_table(W, R)
    summ = aggregate.summary(S, HEADLINE)
    S.to_csv(out / "subjects.csv", index=False)
    summ.to_csv(out / "summary.csv", index=False)
    skin = aggregate.by_skin_tone(S, HEADLINE)
    if len(skin):
        skin.to_csv(out / "skin_tone.csv", index=False)
        print(skin[[c for c in ["model", "dataset", "condition", "skin_group", "n_subjects", "hr_ae", "pearson_lag",
                                "beat_pearson", "r_f1"] if c in skin]].round(3).to_string(index=False))
    ranks = [aggregate.mean_ranks(summ, mt) for mt in ("hr_ae", "pearson_lag", "beat_pearson", "rmse")]
    json.dump(ranks, open(out / "ranks.json", "w"), indent=2, default=float)
    cols = ["model", "dataset", "condition", "seen", "n_subjects"] + [c for c in HEADLINE if c in summ]
    print(summ[cols].round(3).to_string(index=False))
    print(f"\nresults -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--models", nargs="*", help="only these model names/labels")
    ap.add_argument("--conditions", nargs="*", help="only these conditions (e.g. clean, gaussian)")
    ap.add_argument("--datasets", nargs="*", help="only these datasets")
    a = ap.parse_args()
    main(a.config, a.models, a.conditions, a.datasets)
