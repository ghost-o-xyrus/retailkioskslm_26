"""Dataset adapters -> canonical Records.

Each loader is a generator `load_<name>(root, **kw) -> Iterator[Record]` that reads
the dataset in the layout it is distributed in (no manual conversion needed).
Register new loaders in LOADERS.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd

from ..record import Record, finite_segments


def _find_col(df, *needles):
    for c in df.columns:
        lc = c.strip().lower()
        if any(n in lc for n in needles):
            return c
    raise KeyError(f"none of {needles} in columns {list(df.columns)}")


# ------------------------------------------------------------------ BIDMC
def load_bidmc(root, **_) -> Iterator[Record]:
    """PhysioNet BIDMC, CSV flavour: <root>/bidmc_csv/bidmc_XX_Signals.csv (125 Hz)."""
    root = Path(root)
    files = sorted(root.rglob("bidmc_*_Signals.csv"))
    if not files:
        raise FileNotFoundError(f"no bidmc_*_Signals.csv under {root}")
    for f in files:
        df = pd.read_csv(f)
        sid = f.name.split("_")[1]
        yield Record("bidmc", sid, df[_find_col(df, "pleth")].to_numpy(), 125.0,
                     df[_find_col(df, " ii", "ii")].to_numpy(), 125.0, ppg_site="finger", ecg_lead="II")


# ------------------------------------------------------------------ CapnoBase
CAPNO_FS = 300.0
CAPNO_SECONDS = 480.0


def _capno_from_table(f):
    """*_8min_signal.csv (original) or *_8min_signal.tab (Borealis/Dataverse tab-separated copy)."""
    df = pd.read_csv(f, sep="\t" if f.suffix == ".tab" else ",")
    if df.shape[1] == 1:  # wrong delimiter guess -> let pandas sniff it
        df = pd.read_csv(f, sep=None, engine="python")
    return df[_find_col(df, "pleth")].to_numpy(float), df[_find_col(df, "ecg")].to_numpy(float)


def _mat_get(node, *path):
    for p in path:
        node = node[p] if isinstance(node, dict) or hasattr(node, "keys") else getattr(node, p)
    return node


def _capno_from_mat(f):
    """*_8min.mat: struct signal.pleth.y / signal.ecg.y, param.samplingrate.{pleth,ecg}.
    MATLAB v5/v7 via scipy; v7.3 (HDF5) via h5py."""
    try:
        from scipy.io import loadmat
        m = loadmat(f, squeeze_me=True, struct_as_record=False)
        get = lambda *p: np.asarray(_mat_get(m, *p), dtype=float).ravel()  # noqa: E731
    except NotImplementedError:  # v7.3
        import h5py
        h = h5py.File(f, "r")
        get = lambda *p: np.asarray(_mat_get(h, *p)[()], dtype=float).ravel()  # noqa: E731
    ppg, ecg = get("signal", "pleth", "y"), get("signal", "ecg", "y")
    try:
        fs_p, fs_e = float(get("param", "samplingrate", "pleth")[0]), float(get("param", "samplingrate", "ecg")[0])
    except Exception:
        fs_p = fs_e = CAPNO_FS
    return ppg, fs_p, ecg, fs_e


def load_capnobase(root, **_) -> Iterator[Record]:
    """CapnoBase IEEE TBME RR benchmark (42 x 8 min, 300 Hz), in whichever form you downloaded it:
    XXXX_8min_signal.csv (original), XXXX_8min_signal.tab (Borealis copy) or XXXX_8min.mat.
    One file per subject is used, in that order of preference."""
    root = Path(root)
    by_subject = {}
    for pattern in ("*_8min_signal.csv", "*_8min_signal.tab", "*_8min.mat"):
        for f in sorted(root.rglob(pattern)):
            by_subject.setdefault(f.name.split("_")[0], f)
    if not by_subject:
        raise FileNotFoundError(f"no *_8min_signal.csv / *_8min_signal.tab / *_8min.mat under {root}")
    for sid, f in sorted(by_subject.items()):
        if f.suffix == ".mat":
            ppg, fs_p, ecg, fs_e = _capno_from_mat(f)
        else:
            ppg, ecg = _capno_from_table(f)
            fs_p = fs_e = CAPNO_FS
        for name, x, fs in (("PPG", ppg, fs_p), ("ECG", ecg, fs_e)):  # every recording is 8 min
            if abs(len(x) / fs - CAPNO_SECONDS) > 5:
                print(f"[capnobase] warning {f.name}: {name} lasts {len(x) / fs:.1f}s at {fs} Hz (expected 480 s)")
        yield Record("capnobase", sid, ppg, fs_p, ecg, fs_e, ppg_site="finger", ecg_lead="unspecified",
                     meta={"source_file": f.name})


# ------------------------------------------------------------------ DaLiA / WESAD (same pickle layout)
def _load_e4_pickles(root, name, pattern) -> Iterator[Record]:
    root = Path(root)
    files = sorted(root.rglob(pattern), key=lambda p: int(p.stem[1:]))
    if not files:
        raise FileNotFoundError(f"no {pattern} under {root}")
    for f in files:
        with open(f, "rb") as fh:
            d = pickle.load(fh, encoding="latin1")
        ecg = np.asarray(d["signal"]["chest"]["ECG"]).ravel()
        bvp = np.asarray(d["signal"]["wrist"]["BVP"]).ravel()
        n = min(len(ecg) / 700.0, len(bvp) / 64.0)  # trim to common duration
        extras = {"acc_wrist": {"data": np.asarray(d["signal"]["wrist"]["ACC"])[: int(n * 32)], "fs": 32.0}}
        if "activity" in d:  # DaLiA, 4 Hz
            extras["activity"] = {"data": np.asarray(d["activity"]).ravel()[: int(n * 4)], "fs": 4.0}
        if "label" in d:     # WESAD, 700 Hz
            extras["label"] = {"data": np.asarray(d["label"]).ravel()[: int(n * 700)].astype(np.int8), "fs": 700.0}
        meta = {}
        q = d.get("questionnaire", {}) or {}
        for k, v in q.items():  # DaLiA stores Fitzpatrick skin type per subject in the questionnaire
            if "skin" in str(k).lower():
                try:
                    meta["fitzpatrick"] = float(v)
                except (TypeError, ValueError):
                    pass
            elif str(k).lower() in ("age", "gender", "height", "weight"):
                meta[str(k).lower()] = v if isinstance(v, (int, float, str)) else str(v)
        yield Record(name, f.stem, bvp[: int(n * 64)], 64.0, ecg[: int(n * 700)], 700.0,
                     ppg_site="wrist", ecg_lead="chest", extras=extras, meta=meta)


def load_dalia(root, **_):
    return _load_e4_pickles(root, "dalia", "S*.pkl")


def load_wesad(root, **_):
    return _load_e4_pickles(root, "wesad", "S*.pkl")


# ------------------------------------------------------------------ Aurora-BP (Microsoft, skin-tone labelled)
def load_aurora_bp(root, min_seconds=10.0, protocols=("oscillometric", "auscultatory"), phases=None,
                   max_records_per_subject=None, **_):
    """Aurora-BP: <root>/participants.tsv + measurements_<protocol>/<pid>/<pid>.<phase>.<name>.tsv

    Each 30-s measurement file is one Record (subject = pid). Streams are on a common
    500 Hz timebase. ECG = Lead I (not lead II!). PPG = green (527-537 nm) reflective
    sensor on the anterior forearm; the raw 'optical' channel is INVERTED relative to
    pleth convention (verified: inverted -> R-to-PPG-peak ~190 ms, sd ~4 ms).
    meta['fitzpatrick'] carries the participant's Fitzpatrick class (NaN if missing).
    """
    root = Path(root)
    part = pd.read_csv(root / "participants.tsv", sep="\t").set_index("pid")
    for proto in protocols:
        base = root / f"measurements_{proto}"
        if not base.exists():
            continue
        for sdir in sorted(p for p in base.iterdir() if p.is_dir()):
            pid = sdir.name
            info = part.loc[pid] if pid in part.index else None
            n = 0
            for f in sorted(sdir.glob("*.tsv")):
                phase = f.name.split(".")[1]
                if phases and phase not in phases:
                    continue
                d = pd.read_csv(f, sep="\t", usecols=["t", "ekg", "optical"])
                if len(d) < min_seconds * 500 or d["optical"].std() == 0 or d["ekg"].std() == 0:
                    continue
                meta = {"segment": f.stem, "phase": phase, "protocol": proto}
                if info is not None:
                    fz = info.get("fitzpatrick_scale")
                    meta.update(fitzpatrick=float(fz) if pd.notna(fz) else float("nan"),
                                age=float(info.get("age")) if pd.notna(info.get("age")) else None,
                                sex=str(info.get("gender")))
                yield Record("aurora_bp", pid, -d["optical"].to_numpy(dtype=float), 500.0,
                             d["ekg"].to_numpy(dtype=float), 500.0, ppg_site="forearm_green",
                             ecg_lead="I", meta=meta)
                n += 1
                if max_records_per_subject and n >= max_records_per_subject:
                    break


# ------------------------------------------------------------------ generic CSV (e.g. your bidmc_all_128Hz_linear.csv)
# ------------------------------------------------------------------ MIMIC PERform AF (Zenodo 6807403)
MIMIC_AF_FS = 125.0


def _mimic_af_label(path):
    n = str(path).lower()
    return 0 if ("non_af" in n or "nonaf" in n or "non-af" in n) else 1


def _struct_fields(s):
    return list(getattr(s, "_fieldnames", []) or [])


def _sig_from_struct(el, names):
    for f in _struct_fields(el):
        if any(k in f.lower() for k in names):
            node = getattr(el, f)
            v = getattr(node, "v", None) if _struct_fields(node) else node
            fs = getattr(node, "fs", None) if _struct_fields(node) else None
            if v is not None:
                return np.asarray(v, float).ravel(), float(fs) if fs is not None else MIMIC_AF_FS
    return None, None


def _mimic_af_from_mat(f):
    from scipy.io import loadmat
    m = loadmat(f, squeeze_me=True, struct_as_record=False)
    keys = [k for k in m if not k.startswith("__")]
    out = []
    for k in keys:
        arr = np.atleast_1d(m[k])
        if not len(arr) or not _struct_fields(arr[0]):
            continue
        for i, el in enumerate(arr):
            ppg, fs_p = _sig_from_struct(el, ("ppg", "pleth"))
            ecg, fs_e = _sig_from_struct(el, ("ekg", "ecg"))
            if ppg is not None and ecg is not None:
                out.append((i, ppg, fs_p, ecg, fs_e))
        if out:
            return out
    raise ValueError(f"{f.name}: no struct with PPG/PLETH and EKG/ECG fields; top-level variables: {keys}, "
                     f"fields of first: {_struct_fields(np.atleast_1d(m[keys[0]])[0]) if keys else []}")


def _mimic_af_from_csv(f):
    df = pd.read_csv(f)
    ppg = df[_find_col(df, "ppg", "pleth")].to_numpy(float)
    ecg = df[_find_col(df, "ekg", "ecg", "ii")].to_numpy(float)
    fs = MIMIC_AF_FS
    tcols = [c for c in df.columns if "time" in c.lower()]
    if tcols:
        dt = np.median(np.diff(df[tcols[0]].to_numpy(float)))
        if dt > 0:
            fs = round(1.0 / dt, 3)
    return ppg, fs, ecg, fs


def load_mimic_perform_af(root, **_) -> Iterator[Record]:
    """MIMIC PERform AF (Charlton et al., CC BY 4.0): 35 ICU patients, 19 in AF and 16 in sinus rhythm,
    20 min of PPG + ECG at 125 Hz. Reads whichever download is present - the .mat files, the extracted
    CSV zips or the WFDB zips - and labels each record af=1/0 from the file name (`non_af` = 0)."""
    root = Path(root)
    mats = sorted(root.rglob("*perform*af*.mat")) or sorted(root.rglob("*af*data*.mat"))
    seen = set()
    if mats:
        for f in mats:
            af = _mimic_af_label(f)
            for i, ppg, fs_p, ecg, fs_e in _mimic_af_from_mat(f):
                sid = f"{'af' if af else 'sr'}{i + 1:02d}"
                seen.add(sid)
                yield from finite_segments(Record("mimic_perform_af", sid, ppg, fs_p, ecg, fs_e, ppg_site="finger",
                                                  ecg_lead="II", meta={"af": af, "source_file": f.name}))
        return
    csvs = [f for f in sorted(root.rglob("*.csv")) if "af" in str(f).lower()]
    if csvs:
        for f in csvs:
            af = _mimic_af_label(f)
            ppg, fs_p, ecg, fs_e = _mimic_af_from_csv(f)
            sid = f"{'af' if af else 'sr'}_{f.stem}"
            yield from finite_segments(Record("mimic_perform_af", sid, ppg, fs_p, ecg, fs_e, ppg_site="finger",
                                              ecg_lead="II", meta={"af": af, "source_file": f.name}))
        return
    heas = sorted(root.rglob("*.hea"))
    if heas:
        import wfdb  # pip install wfdb
        for h in heas:
            r = wfdb.rdrecord(str(h.with_suffix("")))
            names = [n.lower() for n in r.sig_name]
            ip = next(i for i, n in enumerate(names) if "pleth" in n or "ppg" in n)
            ie = next(i for i, n in enumerate(names) if n in ("ii", "ecg", "ekg") or "ii" in n or "ecg" in n)
            af = _mimic_af_label(h)
            yield Record("mimic_perform_af", f"{'af' if af else 'sr'}_{h.stem}", r.p_signal[:, ip], float(r.fs),
                         r.p_signal[:, ie], float(r.fs), ppg_site="finger", ecg_lead="II",
                         meta={"af": af, "source_file": h.name})
        return
    raise FileNotFoundError(f"no MIMIC PERform AF .mat / .csv / .hea files under {root}")


def load_generic_csv(path, name="custom", fs=128.0, subject_col="Subject", ppg_col="PPG", ecg_col="ECG_II", **_):
    df = pd.read_csv(path)
    for sid, g in df.groupby(subject_col, sort=True):
        yield Record(name, str(sid).zfill(2), g[ppg_col].to_numpy(), fs, g[ecg_col].to_numpy(), fs)


# ------------------------------------------------------------------ synthetic (tests / sanity)
def synth_beat(t, rr):
    """McSharry-like PQRST built from Gaussians; t in seconds relative to R peak."""
    s = np.sqrt(rr / 0.8)  # QT scales with sqrt(RR) (Bazett)
    comps = [(-0.20 * s, 0.025, 0.12), (-0.035, 0.010, -0.15), (0.0, 0.011, 1.0),
             (0.035, 0.010, -0.25), (0.26 * s, 0.045 * s, 0.30)]
    return sum(a * np.exp(-0.5 * ((t - mu) / sd) ** 2) for mu, sd, a in comps)


def make_synthetic(subject="00", duration=120.0, fs=256.0, hr=72.0, hrv=0.04, pat=0.25,
                   noise=0.01, seed=0) -> Record:
    rng = np.random.default_rng(seed)
    n = int(duration * fs)
    t = np.arange(n) / fs
    beats, tt = [], 0.5
    while tt < duration:
        beats.append(tt)
        tt += 60.0 / hr * (1 + hrv * rng.standard_normal())
    beats = np.array(beats)
    ecg = np.zeros(n)
    ppg = np.zeros(n)
    for i, b in enumerate(beats):
        rr = np.diff(beats)[min(i, len(beats) - 2)]
        m = (t > b - 0.4) & (t < b + 0.7)
        ecg[m] += synth_beat(t[m] - b, rr)
        # PPG pulse: systolic + dicrotic Gaussian, arriving pat seconds after R
        m2 = (t > b) & (t < b + 1.2)
        tp = t[m2] - b - pat
        ppg[m2] += np.exp(-0.5 * ((tp - 0.12) / 0.06) ** 2) + 0.35 * np.exp(-0.5 * ((tp - 0.35) / 0.08) ** 2)
    ecg += noise * rng.standard_normal(n) + 0.05 * np.sin(2 * np.pi * 0.25 * t)
    ppg += noise * rng.standard_normal(n) + 0.1 * np.sin(2 * np.pi * 0.2 * t)
    return Record("synthetic", subject, ppg, fs, ecg, fs, ppg_site="sim", meta={"r_times": beats.tolist(), "pat": pat})


def load_synthetic(root=None, n_subjects=3, **kw):
    for i in range(n_subjects):
        yield make_synthetic(subject=f"{i:02d}", hr=60 + 15 * i, pat=0.2 + 0.05 * i, seed=i, **kw)


def load_from_cache(root, dataset, max_records_per_subject=None, max_subjects=None, **filters):
    """Read the canonical cache written by scripts/prepare_datasets.py (fast, used on Kaggle).
    Files are read in sorted order (<subject>__<segment>.npz), so a subject's records are contiguous and
    max_subjects can stop early with exactly the subjects first_subjects() would keep."""
    from ..record import load_cache
    counts = {}
    for r in load_cache(root, dataset, **filters):
        if max_subjects and r.subject not in counts and len(counts) >= max_subjects:
            break
        counts[r.subject] = counts.get(r.subject, 0) + 1
        if max_records_per_subject and counts[r.subject] > max_records_per_subject:
            continue
        yield r


LOADERS = {
    "cache": load_from_cache,
    "bidmc": load_bidmc,
    "capnobase": load_capnobase,
    "dalia": load_dalia,
    "wesad": load_wesad,
    "aurora_bp": load_aurora_bp,
    "mimic_perform_af": load_mimic_perform_af,
    "generic_csv": load_generic_csv,
    "synthetic": load_synthetic,
}
