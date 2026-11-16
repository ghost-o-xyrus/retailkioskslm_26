"""Canonical per-subject record. Every dataset adapter must produce these.

One Record = one continuous, synchronised recording of one subject.
Signals keep their ORIGINAL sampling rates; resampling happens in the runner,
so that each model receives data prepared exactly the way its authors specify.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class Record:
    dataset: str
    subject: str
    ppg: np.ndarray
    ppg_fs: float
    ecg: np.ndarray
    ecg_fs: float
    ppg_site: str = "unknown"          # finger | wrist | ...
    ecg_lead: str = "II"
    # optional side channels, each a dict {"data": array, "fs": float}
    extras: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)  # age, sex, condition, device ...

    def __post_init__(self):
        self.ppg = np.asarray(self.ppg, dtype=np.float64).ravel()
        self.ecg = np.asarray(self.ecg, dtype=np.float64).ravel()
        dp, de = len(self.ppg) / self.ppg_fs, len(self.ecg) / self.ecg_fs
        if abs(dp - de) > 1.0:
            raise ValueError(f"{self.dataset}/{self.subject}: PPG {dp:.1f}s vs ECG {de:.1f}s differ by >1 s")

    @property
    def key(self) -> str:
        return f"{self.dataset}/{self.subject}"

    @property
    def duration(self) -> float:
        return min(len(self.ppg) / self.ppg_fs, len(self.ecg) / self.ecg_fs)

    @property
    def record_id(self) -> str:
        seg = self.meta.get("segment")
        return f"{self.subject}__{seg}" if seg else self.subject

    def crop(self, max_seconds: float | None) -> "Record":
        """First `max_seconds` of the record (used for the perturbation subset)."""
        if not max_seconds or self.duration <= max_seconds:
            return self
        return Record(self.dataset, self.subject, self.ppg[: int(max_seconds * self.ppg_fs)], self.ppg_fs,
                      self.ecg[: int(max_seconds * self.ecg_fs)], self.ecg_fs, self.ppg_site, self.ecg_lead,
                      {k: {"data": v["data"][: int(max_seconds * v["fs"])], "fs": v["fs"]} for k, v in self.extras.items()},
                      dict(self.meta))

    # ---- persistence (single .npz per record, no extra deps) ----
    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        arrays = {"ppg": self.ppg.astype(np.float32), "ecg": self.ecg.astype(np.float32)}  # float32 halves cache size
        extra_fs = {}
        for k, v in self.extras.items():
            arrays[f"extra__{k}"] = np.asarray(v["data"])
            extra_fs[k] = v["fs"]
        header = dict(dataset=self.dataset, subject=self.subject, ppg_fs=self.ppg_fs,
                      ecg_fs=self.ecg_fs, ppg_site=self.ppg_site, ecg_lead=self.ecg_lead,
                      extra_fs=extra_fs, meta=self.meta)
        np.savez_compressed(path, header=json.dumps(header), **arrays)
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Record":
        z = np.load(path, allow_pickle=False)
        h = json.loads(str(z["header"]))
        extras = {k: {"data": z[f"extra__{k}"], "fs": fs} for k, fs in h.pop("extra_fs").items()}
        return cls(ppg=z["ppg"], ecg=z["ecg"], extras=extras, **h)


def load_cache(cache_dir: str | Path, dataset: Optional[str] = None, **filters):
    """Yield Records from a cache directory written by scripts/prepare_datasets.py.

    filters: optional meta filters, e.g. phase="initial" for Aurora-BP.
    """
    root = Path(cache_dir)
    pattern = f"{dataset}/*.npz" if dataset else "*/*.npz"
    for p in sorted(root.glob(pattern)):
        r = Record.load(p)
        if all(r.meta.get(k) == v or (isinstance(v, list) and r.meta.get(k) in v) for k, v in filters.items()):
            yield from finite_segments(r)        # e.g. MIMIC PERform AF has NaN gaps


def _fill_short_gaps(x, fs, max_gap_s):
    """Linearly interpolate runs of non-finite samples no longer than max_gap_s; longer runs stay NaN."""
    x = np.asarray(x, float).copy()
    bad = ~np.isfinite(x)
    if not bad.any():
        return x
    x[bad] = np.nan
    good = np.flatnonzero(~bad)
    if not len(good):
        return x
    edges = np.flatnonzero(np.diff(np.r_[0, bad.astype(np.int8), 0]))
    for a, b in zip(edges[::2], edges[1::2]):               # run [a, b)
        if (b - a) / fs <= max_gap_s and a > 0 and b < len(x):
            x[a:b] = np.interp(np.arange(a, b), [a - 1, b], [x[a - 1], x[b]])
    return x


def finite_segments(r: "Record", min_seconds: float = 30.0, max_gap_s: float = 1.0, bin_s: float = 0.1):
    """Split a record at missing data (NaN/inf). Short gaps (<= max_gap_s) are interpolated; the record is
    cut at longer gaps and pieces shorter than min_seconds are dropped. A record without missing data is
    returned unchanged, so datasets without gaps give exactly the same records as before."""
    if np.isfinite(r.ppg).all() and np.isfinite(r.ecg).all():
        return [r]
    ppg, ecg = _fill_short_gaps(r.ppg, r.ppg_fs, max_gap_s), _fill_short_gaps(r.ecg, r.ecg_fs, max_gap_s)
    nb = int(np.floor(r.duration / bin_s))
    ok = np.ones(nb, bool)
    for x, fs in ((ppg, r.ppg_fs), (ecg, r.ecg_fs)):
        b = np.flatnonzero(~np.isfinite(x)) / fs / bin_s
        ok[np.clip(b.astype(int), 0, nb - 1)] = False
    edges = np.flatnonzero(np.diff(np.r_[0, ok.astype(np.int8), 0]))
    out = []
    for k, (a, b) in enumerate(zip(edges[::2], edges[1::2])):
        t0, t1 = a * bin_s, b * bin_s
        if t1 - t0 < min_seconds:
            continue
        sl = lambda x, fs: x[int(np.ceil(t0 * fs)): int(np.floor(t1 * fs))]
        meta = dict(r.meta)
        meta["segment"] = f"{meta['segment']}f{k}" if meta.get("segment") else f"f{k}"
        meta["t_offset_s"] = round(float(t0), 3)
        out.append(Record(r.dataset, r.subject, sl(ppg, r.ppg_fs), r.ppg_fs, sl(ecg, r.ecg_fs), r.ecg_fs,
                          r.ppg_site, r.ecg_lead,
                          {n: {"data": sl(np.asarray(v["data"]), v["fs"]), "fs": v["fs"]} for n, v in r.extras.items()},
                          meta))
    return out
