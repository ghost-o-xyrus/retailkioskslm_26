"""Track 1.5 - how much ECG information does the PPG carry? Runs the five methods of bench/info on
every dataset of a benchmark config (same cache, same loaders as Track 1).

    python scripts/info_analysis.py configs/kaggle_track1.yaml --out results/info [--datasets bidmc capnobase]
    python scripts/info_analysis.py --synthetic --out results/info_synth        # self-test

Per record (written as it goes, so a crash keeps what is done):
  blocks.csv        one row per 10-beat block: ECG features (+ split halves), PPG features, ids, labels
  templates_<ds>.npz  block-median ECG beats and PPG pulses (to re-run regional analyses without the cache)
  agreement_segments.csv  HRV vs PRV per 5-min segment (method 4)
  coherence.csv     per-record coherence bands, linear explainable fraction, Wiener R^2 (method 1)
  intervals_info.csv per-record MI / transfer entropy of RR and PP series (method 2)
Per dataset, at the end:
  agreement_summary.csv  Bland-Altman + ICC (method 4)
  regional_r2.csv        R^2 of every ECG beat region from the PPG pulse, rate-only vs PPG (method 1)
  probes.csv, probes_af.csv  feature probes and the AF screening probe (method 5)
  forward_crlb.csv, forward_sensitivity.csv, forward_sweeps.csv  (method 3) at each dataset's PPG SNR
"""
from __future__ import annotations

import argparse
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.datasets import LOADERS, make_synthetic  # noqa: E402
from bench.info import agreement, beats, coherence, forward, infotheory, probes  # noqa: E402

LABEL_KEYS = ("af", "rhythm", "fitzpatrick", "phase", "activity")


def iter_records(cfg, only):
    for d in cfg["datasets"]:
        if only and d["name"] not in only:
            continue
        kw = {k: v for k, v in d.items() if k not in ("name", "loader", "max_subjects")}
        try:
            recs = list(LOADERS[d.get("loader", d["name"])](**kw))
        except Exception as e:
            print(f"[data] {d['name']}: FAILED {e!r}", flush=True)
            continue
        print(f"[data] {d['name']}: {len(recs)} records", flush=True)
        yield d["name"], recs


def synthetic_records(n=12):
    recs = []
    rng = np.random.default_rng(0)
    for i in range(n):
        recs.append(make_synthetic(subject=f"s{i:02d}", duration=360, fs=256, hr=float(rng.uniform(55, 95)),
                                   hrv=float(rng.uniform(0.02, 0.08)), pat=float(rng.uniform(0.18, 0.3)),
                                   noise=0.02, seed=i))
        recs[-1].meta["af"] = int(i % 3 == 0)
    return [("synthetic", recs)]


def analyse_record(ds, rec, keep_templates=True):
    bp = beats.pair_beats(rec)
    ids = dict(dataset=ds, subject=str(rec.subject), record=rec.record_id, ppg_site=rec.ppg_site,
               duration_s=rec.duration, n_r=bp.meta["n_r"], n_pulses=bp.meta["n_pulses"], n_matched=len(bp.r))
    for k in LABEL_KEYS:
        if k in rec.meta:
            ids[k] = rec.meta[k]
    rows, tmpls = beats.block_table(bp, keep_templates=keep_templates)
    blocks = [{**ids, **r} for r in rows]
    t, rr, pp, pat = beats.interval_series(bp)
    agree = [{**ids, **r} for r in agreement.segment_agreement(t, rr, pp, pat)]
    coh = None
    c = coherence.record_coherence(bp)
    if c is not None:
        coh = {**ids, **c[0]}
        w = coherence.wiener_r2(bp)
        if w:
            coh.update(w)
    mi = None
    if len(rr) >= 150:
        mi = {**ids, **infotheory.interval_coupling(rr, pp, n_surr=10)}
    return blocks, tmpls, agree, coh, mi


def snr_from_sqi(sqi):
    """Beat-level SNR implied by the median beat-to-template correlation r: r^2/(1-r^2)."""
    r = float(np.clip(sqi, 0.5, 0.9995))
    return 10 * np.log10(r ** 2 / (1 - r ** 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", nargs="?")
    ap.add_argument("--out", required=True)
    ap.add_argument("--datasets", nargs="*")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--max-records", type=int, default=None, help="per dataset (quick runs)")
    ap.add_argument("--n-boot", type=int, default=300)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sources = synthetic_records() if a.synthetic else iter_records(yaml.safe_load(open(a.config)), a.datasets)

    B, A, C, M, errors = [], [], [], [], []
    for ds, recs in sources:
        if a.max_records:
            recs = recs[: a.max_records]
        t0 = time.time()
        E, P, Bid = [], [], []
        for i, rec in enumerate(recs):
            try:
                blocks, tmpls, agree, coh, mi = analyse_record(ds, rec)
            except Exception as e:
                errors.append(dict(dataset=ds, record=rec.record_id, error=repr(e), trace=traceback.format_exc()[-600:]))
                continue
            for b, (te, tp) in zip(blocks, tmpls):
                b["block_id"] = len(B)
                E.append(te.astype(np.float32)), P.append(tp.astype(np.float32)), Bid.append(b["block_id"])
                B.append(b)
            A += agree
            C += [coh] if coh else []
            M += [mi] if mi else []
            if (i + 1) % 50 == 0 or i + 1 == len(recs):
                print(f"[{ds}] {i + 1}/{len(recs)} records, {len(B)} blocks so far, {time.time() - t0:.0f}s", flush=True)
                pd.DataFrame(B).to_csv(out / "blocks.csv", index=False)
                pd.DataFrame(A).to_csv(out / "agreement_segments.csv", index=False)
                pd.DataFrame(C).to_csv(out / "coherence.csv", index=False)
                pd.DataFrame(M).to_csv(out / "intervals_info.csv", index=False)
                if errors:
                    pd.DataFrame(errors).to_csv(out / "errors.csv", index=False)
        if E:
            np.savez_compressed(out / f"templates_{ds}.npz", ecg=np.stack(E), ppg=np.stack(P), block_id=np.asarray(Bid))

    blocks = pd.DataFrame(B)
    if blocks.empty:
        raise SystemExit("no usable blocks - check the data / errors.csv")
    # ------------------------------------------------ dataset-level analyses
    agree_sum = agreement.bland_altman(pd.DataFrame(A)) if A else pd.DataFrame()
    agree_sum.to_csv(out / "agreement_summary.csv", index=False)
    PR, PAF, RR2, FW, FS_, FSW = [], [], [], [], [], []
    for ds, d in blocks.groupby("dataset"):
        d = d.sort_values(["subject", "record", "t_start"]).reset_index(drop=True)
        print(f"[probes] {ds}: {len(d)} blocks, {d.subject.nunique()} subjects", flush=True)
        if d.subject.nunique() >= 3:
            p = probes.run_probes(d, n_boot=a.n_boot)
            PR.append(p.assign(dataset=ds))
            if "af" in d:
                PAF.append(probes.run_class_probe(d, "af", n_boot=a.n_boot).assign(dataset=ds))
        tz = np.load(out / f"templates_{ds}.npz")
        bid = blocks.set_index("block_id").loc[tz["block_id"]]
        tm = list(zip(tz["ecg"], tz["ppg"]))
        for within in (False, True):
            r = coherence.regional_r2(tm, bid["subject"].astype(str).to_numpy(), bid["pp_ms"].to_numpy(), within=within)
            if r:
                row = {k: v for k, v in r.items() if not k.startswith(("r2_t", "t_ms"))}
                RR2.append(dict(dataset=ds, scheme="personalized" if within else "between", **row))
                np.savez_compressed(out / f"regional_r2_curve_{ds}_{'within' if within else 'between'}.npz",
                                    t_ms=r["t_ms"], r2_ppg=r["r2_t_ppg"], r2_rate=r["r2_t_rate"])
        snr = snr_from_sqi(d["pulse_sqi"].median())
        grid, sens, sw = forward.default_report(snr_db=snr)
        FW.append(grid.assign(dataset=ds, snr_db=snr)), FS_.append(sens.assign(dataset=ds, snr_db=snr))
        FSW.append(sw.assign(dataset=ds, snr_db=snr))
    for name, parts in (("probes", PR), ("probes_af", PAF), ("regional_r2", RR2 and [pd.DataFrame(RR2)]),
                        ("forward_crlb", FW), ("forward_sensitivity", FS_), ("forward_sweeps", FSW)):
        if parts:
            pd.concat(parts, ignore_index=True).to_csv(out / f"{name}.csv", index=False)
    print(f"\nwrote {out}  ({len(blocks)} blocks, {len(errors)} record errors)", flush=True)
    if PR:
        P = pd.concat(PR)
        show = P[(P.model == "hgb") & P.features.isin(["rate", "full", "gain:full-timing"])]
        print(show.pivot_table(index=["dataset", "target"], columns=["scheme", "features"], values="r2").round(2).to_string())


if __name__ == "__main__":
    main()
