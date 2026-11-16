"""Method 4: agreement between pulse-rate variability (PPG) and heart-rate variability (ECG).

Per segment (default 5 min, the HRV standard; shorter records use the whole record and are
flagged 'ultra_short') we compute the usual HRV indices from RR (ECG) and from PP (PPG foot-to-foot)
on the SAME matched beats, then summarise agreement per dataset with Bland-Altman bias, 95% limits
of agreement, relative error and ICC(3,1). PP - RR = PAT(n+1) - PAT(n), so the pulse-arrival-time
jitter is reported alongside: it is the physical reason PRV differs from HRV.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import signal as sps

HRV_METRICS = ["mean_nn", "sdnn", "rmssd", "pnn50", "lf", "hf", "lf_hf"]


def hrv(nn_ms, t_s=None):
    nn = np.asarray(nn_ms, float)
    out = dict(mean_nn=nn.mean(), sdnn=nn.std(ddof=1), rmssd=np.sqrt(np.mean(np.diff(nn) ** 2)),
               pnn50=100 * np.mean(np.abs(np.diff(nn)) > 50))
    # frequency domain: 4 Hz cubic resampling of the tachogram, Welch PSD
    t = np.cumsum(nn) / 1000.0 if t_s is None else np.asarray(t_s, float)
    if t[-1] - t[0] >= 60:
        from scipy.interpolate import CubicSpline
        tt = np.arange(t[0], t[-1], 0.25)
        x = CubicSpline(t, nn)(tt)
        x = sps.detrend(x)
        f, p = sps.welch(x, fs=4.0, nperseg=min(len(x), 256))
        lf = np.trapezoid(p[(f >= 0.04) & (f < 0.15)], f[(f >= 0.04) & (f < 0.15)])
        hf = np.trapezoid(p[(f >= 0.15) & (f < 0.40)], f[(f >= 0.15) & (f < 0.40)])
        out.update(lf=lf, hf=hf, lf_hf=lf / hf if hf > 0 else np.nan)
    else:
        out.update(lf=np.nan, hf=np.nan, lf_hf=np.nan)
    return out


def segment_agreement(t, rr, pp, pat, seg_s=300.0, min_s=60.0):
    """Rows of HRV (ECG) vs PRV (PPG) per segment of one record."""
    rows = []
    if len(t) < 10:
        return rows
    dur = t[-1] - t[0]
    edges = [t[0]] if dur < seg_s else list(np.arange(t[0], t[-1] - seg_s + 1e-9, seg_s))
    for e in edges:
        m = (t >= e) & (t < e + (seg_s if dur >= seg_s else dur + 1))
        if m.sum() < 10 or (t[m][-1] - t[m][0]) < min_s * 0.9:
            continue
        a, b = hrv(rr[m], t[m]), hrv(pp[m], t[m])
        row = dict(seg_start=e, seg_s=t[m][-1] - t[m][0], n_beats=int(m.sum()), ultra_short=bool(dur < seg_s),
                   pat_mean=pat[m].mean(), pat_sd=pat[m].std(), pat_rmssd=np.sqrt(np.mean(np.diff(pat[m]) ** 2)),
                   interval_diff_sd=np.std(pp[m] - rr[m]), interval_corr=np.corrcoef(rr[m], pp[m])[0, 1])
        row.update({f"{k}_ecg": v for k, v in a.items()})
        row.update({f"{k}_ppg": v for k, v in b.items()})
        rows.append(row)
    return rows


def icc31(x, y):
    """ICC(3,1), two-way mixed, consistency, single measures."""
    d = np.c_[x, y]
    d = d[np.isfinite(d).all(1)]
    n = len(d)
    if n < 3:
        return np.nan
    gm = d.mean()
    ss_r = 2 * ((d.mean(1) - gm) ** 2).sum()
    ss_c = n * ((d.mean(0) - gm) ** 2).sum()
    ss_e = ((d - gm) ** 2).sum() - ss_r - ss_c
    ms_r, ms_e = ss_r / (n - 1), ss_e / ((n - 1) * 1)
    return (ms_r - ms_e) / (ms_r + ms_e)


def bland_altman(df: pd.DataFrame, by="dataset", log_metrics=("lf", "hf", "lf_hf")):
    """Agreement summary per group and metric. Spectral powers are compared on log scale."""
    out = []
    for g, d in df.groupby(by):
        for m in HRV_METRICS:
            a, b = d[f"{m}_ecg"].to_numpy(float), d[f"{m}_ppg"].to_numpy(float)
            ok = np.isfinite(a) & np.isfinite(b) & ((a > 0) & (b > 0) if m in log_metrics else True)
            a, b = a[ok], b[ok]
            if len(a) < 3:
                continue
            if m in log_metrics:
                a, b = np.log(a), np.log(b)
            diff = b - a
            bias, sd = diff.mean(), diff.std(ddof=1)
            out.append(dict(group=g, metric=m + ("(log)" if m in log_metrics else ""), n_segments=len(a),
                            ecg_mean=a.mean(), bias=bias, loa_low=bias - 1.96 * sd, loa_high=bias + 1.96 * sd,
                            rel_bias_pct=100 * bias / a.mean() if m not in log_metrics else 100 * (np.exp(bias) - 1),
                            icc=icc31(a, b), pearson=np.corrcoef(a, b)[0, 1],
                            pat_sd_ms=d["pat_sd"].median(), interval_diff_sd_ms=d["interval_diff_sd"].median()))
    return pd.DataFrame(out)
