"""Method 1: linear transfer from PPG to ECG.

record_coherence   magnitude-squared coherence C(f) between the continuous PPG and ECG, per band,
                   and the ECG-power-weighted mean coherence = the fraction of ECG power a linear
                   time-invariant filter of the PPG could explain ("linear explainable fraction").
wiener_r2          the same question in the time domain: a non-causal FIR (Wiener) filter from PPG to
                   ECG fitted on the first 70% of a record, R^2 on the last 30%, overall and per band.
regional_r2        beat-synchronous version: predict every sample of the block-median ECG beat from
                   the block-median PPG pulse (Zhu et al. 2019 style), across subjects (GroupKFold)
                   and within subjects, giving R^2(t) along the beat and per ECG region (P, QRS, ST, T),
                   compared with a rate-only predictor.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sps
from scipy.fft import dct
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold

from .. import dsp
from .beats import FS, PRE

BANDS = {"0.5-3Hz": (0.5, 3.0), "3-8Hz": (3.0, 8.0), "8-15Hz": (8.0, 15.0), "15-40Hz": (15.0, 40.0)}
REGIONS_MS = {"P": (-250, -80), "PR": (-80, -50), "QRS": (-50, 60), "ST": (60, 160), "T": (160, 450)}


def _to128(x):
    return sps.decimate(x, 2, ftype="fir", zero_phase=True)  # FS 256 -> 128


def record_coherence(bp, nperseg_s=8.0):
    fs = FS / 2
    e, p = _to128(bp.ecg), _to128(bp.ppg)
    if len(e) < 4 * nperseg_s * fs:
        return None
    f, c = sps.coherence(p, e, fs=fs, nperseg=int(nperseg_s * fs))
    _, pee = sps.welch(e, fs=fs, nperseg=int(nperseg_s * fs))
    out = {}
    for name, (lo, hi) in BANDS.items():
        m = (f >= lo) & (f < hi)
        out[f"coh_{name}"] = float(c[m].mean())
        out[f"ecg_power_frac_{name}"] = float(pee[m].sum() / pee[(f >= 0.5) & (f < 40)].sum())
    m = (f >= 0.5) & (f < 40)
    out["linear_explainable_frac"] = float((c[m] * pee[m]).sum() / pee[m].sum())
    return out, (f, c)


def wiener_r2(bp, lag_s=(-0.3, 0.8), train_frac=0.7, alpha=1.0, max_n=40000, max_seconds=600.0):
    """Non-causal FIR ridge regression ECG(t) ~ sum_k h_k PPG(t + k). Positive lags = future PPG
    (the pulse arrives after the R peak)."""
    fs = FS / 2
    n_max = int(max_seconds * FS)                      # long ambulatory records: first max_seconds only
    e, p = dsp.zscore(_to128(bp.ecg[:n_max])), dsp.zscore(_to128(bp.ppg[:n_max]))
    lags = np.arange(int(lag_s[0] * fs), int(lag_s[1] * fs) + 1)
    lo, hi = -lags.min(), len(p) - lags.max()
    if hi - lo < 30 * fs:
        return None
    idx = np.arange(lo, hi)
    X = np.stack([p[idx + k] for k in lags], axis=1)
    y = e[idx]
    n_tr = int(train_frac * len(idx))
    tr = np.arange(n_tr)
    if len(tr) > max_n:
        tr = np.linspace(0, n_tr - 1, max_n).astype(int)
    model = Ridge(alpha=alpha).fit(X[tr], y[tr])
    yt, yh = y[n_tr:], model.predict(X[n_tr:])
    out = {"wiener_r2": 1 - np.mean((yt - yh) ** 2) / np.var(yt)}
    for name, (blo, bhi) in BANDS.items():
        a, b = dsp.bandpass(yt, fs, blo, bhi, order=2), dsp.bandpass(yh, fs, blo, bhi, order=2)
        out[f"wiener_r2_{name}"] = 1 - np.mean((a - b) ** 2) / max(np.var(a), 1e-12)
    return out


def _norm_ecg_template(t):
    iso = np.median(t[: int(0.04 * FS)])
    r = int(PRE * FS)
    amp = t[r] - iso
    return (t - iso) / amp if amp > 0 else None


def regional_r2(templates, groups, pp_ms, n_dct=16, alpha=1.0, n_splits=5, within=False):
    """templates: list of (ecg_template, ppg_pulse); groups: subject id per block; pp_ms: block PP.
    Returns dict with r2_t (per template sample) for 'ppg' and 'rate' inputs, and per-region means."""
    E, P, keep = [], [], []
    for i, (te, tp) in enumerate(templates):
        en = _norm_ecg_template(te)
        if en is None:
            continue
        tp = tp - tp[0]
        if tp.max() <= 0:
            continue
        E.append(en), P.append(dct(tp / tp.max(), norm="ortho")[:n_dct]), keep.append(i)
    if len(E) < 50:
        return None
    E, P = np.asarray(E), np.asarray(P)
    g = np.asarray(groups)[keep]
    pp = np.asarray(pp_ms, float)[keep][:, None] / 1000.0
    X = {"rate": np.c_[pp, pp ** 2], "ppg": np.c_[pp, pp ** 2, P]}
    res = {}
    for name, Xi in X.items():
        pred = np.full_like(E, np.nan)
        if within:   # per subject: first 70% of its blocks -> last 30%
            for s in np.unique(g):
                ids = np.flatnonzero(g == s)
                if len(ids) < 10:
                    continue
                k = int(0.7 * len(ids))
                m = Ridge(alpha=alpha).fit(Xi[ids[:k]], E[ids[:k]])
                pred[ids[k:]] = m.predict(Xi[ids[k:]])
        else:
            n_g = len(np.unique(g))
            if n_g < 3:
                return None
            for tr, te in GroupKFold(n_splits=min(n_splits, n_g)).split(Xi, E, g):
                m = Ridge(alpha=alpha).fit(Xi[tr], E[tr])
                pred[te] = m.predict(Xi[te])
        ok = np.isfinite(pred[:, 0])
        if ok.sum() < 20:
            return None
        resid = ((E[ok] - pred[ok]) ** 2).mean(0)
        r2_t = 1 - resid / E[ok].var(0).clip(1e-12)
        res[f"r2_t_{name}"] = r2_t
        t_ms = (np.arange(E.shape[1]) / FS - PRE) * 1000
        for reg, (a, b) in REGIONS_MS.items():
            m = (t_ms >= a) & (t_ms < b)
            # region R^2 = 1 - pooled residual / pooled variance within the region
            res[f"r2_{reg}_{name}"] = 1 - resid[m].sum() / E[ok][:, m].var(0).sum()
        res[f"n_blocks_{name}"] = int(ok.sum())
    res["t_ms"] = (np.arange(E.shape[1]) / FS - PRE) * 1000
    return res
