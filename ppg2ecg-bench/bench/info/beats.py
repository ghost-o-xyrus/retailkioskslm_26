"""Beat-level pairing of ECG and PPG, block templates, ECG delineation and PPG pulse features.

Everything in bench/info is built on the table this module produces: one row per BLOCK of
`block_beats` consecutive, matched heartbeats, with
  * ECG features of the block's median beat (RR, QRS width, PR, P/T amplitude, ST level, QT, QTc)
  * PPG features of the block's median pulse (timing, morphology), computed WITHOUT the ECG
  * a split-half copy of every ECG feature (odd vs even beats) -> measurement noise ceiling

Median templates over ~10 beats are used because single-beat delineation of P waves and T ends
is unreliable on bedside / wearable data; block templates are the standard compromise.

numpy / scipy only (neurokit2 is not needed), so it runs in Kaggle's base Python and here.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import signal as sps
from scipy.fft import dct

from .. import dsp

FS = 256.0                     # working rate: 3.9 ms resolution for QRS/PR/QT
PRE, POST = 0.35, 0.65         # ECG template window around R (s)
PULSE_N = 64                   # PPG pulse resampled foot-to-foot to this many samples
N_DCT = 12                     # DCT coefficients kept for the pulse shape
ECG_TARGETS = ["rr_ms", "rr_sd_ms", "rr_rmssd_ms", "qrs_ms", "pr_ms", "p_amp", "st_rel", "t_amp",
               "qt_ms", "qtc_f_ms", "r_s_ratio"]


@dataclass
class BeatPairs:
    """Matched heartbeats of one record (indices at FS)."""
    r: np.ndarray            # R peaks
    foot: np.ndarray         # matched PPG pulse onset for each R
    peak: np.ndarray         # matched PPG systolic peak
    ecg: np.ndarray          # filtered ECG at FS
    ppg: np.ndarray          # filtered PPG at FS
    meta: dict = field(default_factory=dict)

    @property
    def pat_ms(self):
        return (self.foot - self.r) / FS * 1000.0


# ------------------------------------------------------------------ pairing
def refine_feet(ppg, peaks, fs=FS):
    """Pulse onset by the intersecting-tangent method (more stable than the minimum for timing):
    the tangent at maximum upslope crosses the horizontal through the preceding minimum."""
    d = np.gradient(ppg)
    feet = []
    for p in peaks:
        a = max(0, p - int(0.4 * fs))
        if p - a < 3:
            feet.append(a)
            continue
        i_min = a + int(np.argmin(ppg[a:p + 1]))
        seg = slice(i_min, p + 1)
        i_up = i_min + int(np.argmax(d[seg]))
        slope = d[i_up]
        if slope <= 0:
            feet.append(i_min)
            continue
        t = i_up - (ppg[i_up] - ppg[i_min]) / slope
        feet.append(int(round(np.clip(t, i_min, i_up))))
    return np.asarray(feet, dtype=int)


def pair_beats(rec, pat_range=(0.05, 0.60), ecg_band=(0.67, 40.0)) -> BeatPairs:
    """Resample to FS, detect R peaks and PPG pulses, and give every R peak the first PPG onset
    that follows it within pat_range seconds (unmatched beats are dropped)."""
    ecg = dsp.resample(rec.ecg, rec.ecg_fs, FS)
    ppg = dsp.resample(rec.ppg, rec.ppg_fs, FS)
    n = min(len(ecg), len(ppg))
    ecg, ppg = ecg[:n], ppg[:n]
    # 0.67 Hz zero-phase high-pass keeps the ST segment usable (AHA allows 0.67 Hz with linear phase)
    ecg = dsp.bandpass(ecg, FS, *ecg_band, order=2)
    ppg = dsp.bandpass(ppg, FS, 0.5, 8.0, order=3)
    r = dsp.detect_rpeaks(ecg, FS)
    # make R positive on average so the template has an upright R
    if len(r) and np.median(ecg[r]) < 0:
        ecg = -ecg
        r = dsp.detect_rpeaks(ecg, FS)
    pk = dsp.detect_ppg_peaks(ppg, FS)
    ft = refine_feet(ppg, pk)
    R, F, P = [], [], []
    j = 0
    for ri in r:
        while j < len(ft) and ft[j] < ri + pat_range[0] * FS:
            j += 1
        if j < len(ft) and ft[j] <= ri + pat_range[1] * FS:
            R.append(ri), F.append(ft[j]), P.append(pk[j])
            j += 1
    return BeatPairs(np.asarray(R, int), np.asarray(F, int), np.asarray(P, int), ecg, ppg,
                     meta=dict(n_r=len(r), n_pulses=len(pk)))


# ------------------------------------------------------------------ ECG delineation
def _first_below(absd, start, stop, thr, step):
    i = start
    while (step < 0 and i > stop) or (step > 0 and i < stop):
        if absd[i] < thr and absd[i + step] < thr:
            return i
        i += step
    return None


def delineate(tmpl, rr_s, fs=FS, pre=PRE):
    """Fiducials of a median ECG beat (R at index pre*fs). Returns dict of features (ms / relative
    amplitude, R amplitude = 1). NaN where a wave is absent or the delineation is implausible."""
    out = {k: np.nan for k in ["qrs_ms", "pr_ms", "p_amp", "st_rel", "t_amp", "qt_ms", "qtc_f_ms", "r_s_ratio"]}
    x = np.asarray(tmpl, float)
    r = int(round(pre * fs))
    ms = lambda k: int(round(k / 1000.0 * fs))
    if r - ms(320) < 0 or r + ms(200) >= len(x):
        return out
    d = np.gradient(x) * fs
    # QRS onset: back from the steepest upstroke before R until the slope is small
    a = r - ms(70)
    i_up = a + int(np.argmax(d[a:r + 1]))
    thr = 0.12 * np.max(np.abs(d[r - ms(70):r + ms(90)]))
    start = i_up
    # a Q wave is a dip before R; the onset is where its DOWNstroke begins, not at its nadir
    q = r - ms(80) + int(np.argmin(x[r - ms(80):r + 1]))
    ref = float(np.median(x[r - ms(160):r - ms(100)]))
    if q < i_up and x[q] < ref - 0.03 * (x[r] - ref):
        start = q - ms(60) + int(np.argmin(d[q - ms(60):q + 1]))
    on = _first_below(np.abs(d), start, r - ms(200), thr, -1)
    # S nadir, then J point: forward from the steepest S->J upstroke until the slope is small
    s = r + int(np.argmin(x[r:r + ms(90)]))
    i_up2 = s + int(np.argmax(d[s:s + ms(60)]))
    off = _first_below(np.abs(d), i_up2, min(len(x) - 2, r + ms(200)), thr, +1)
    if on is None or off is None:
        return out
    iso = float(np.median(x[max(0, on - ms(30)):max(1, on - ms(8))]))
    amp = x[r] - iso
    if amp <= 0:
        return out
    xn = (x - iso) / amp
    qrs = (off - on) / fs * 1000
    if not 40 <= qrs <= 220:
        return out
    out["qrs_ms"] = qrs
    out["r_s_ratio"] = 1.0 / max(abs(xn[s]), 0.02) if xn[s] < 0 else 50.0
    # P wave: largest deflection 30-300 ms before QRS onset
    pa, pb = max(0, on - ms(300)), on - ms(30)
    if pb - pa > ms(40):
        seg = xn[pa:pb]
        ip = pa + int(np.argmax(np.abs(seg)))
        p_amp = xn[ip]
        out["p_amp"] = p_amp
        if abs(p_amp) >= 0.04:  # a P wave is present
            j = ip
            while j > pa and abs(xn[j]) > 0.15 * abs(p_amp):
                j -= 1
            pr = (on - j) / fs * 1000
            out["pr_ms"] = pr if 70 <= pr <= 400 else np.nan
    # ST level at J + 60 ms (relative to R amplitude)
    if off + ms(60) < len(xn):
        out["st_rel"] = xn[off + ms(60)]
    # T wave: largest deflection between J+80 ms and 70% of the RR interval
    ta, tb = off + ms(80), min(len(xn) - 2, r + int(0.70 * rr_s * fs))
    if tb - ta > ms(60):
        it = ta + int(np.argmax(np.abs(xn[ta:tb])))
        t_amp = xn[it]
        out["t_amp"] = t_amp
        if abs(t_amp) >= 0.05:
            # T end, tangent method: steepest return-to-baseline slope after the T peak
            dn = np.gradient(xn) * fs
            seg = slice(it, min(len(xn) - 1, it + ms(200)))
            k = it + (int(np.argmin(dn[seg])) if t_amp > 0 else int(np.argmax(dn[seg])))
            if dn[k] != 0:
                tend = k - xn[k] / dn[k] * fs
                qt = (tend - on) / fs * 1000
                if 200 <= qt <= 700:
                    out["qt_ms"] = qt
                    out["qtc_f_ms"] = qt / rr_s ** (1 / 3)
    return out


# ------------------------------------------------------------------ PPG pulse features
def pulse_features(pulses, pp_s):
    """pulses: (n_beats, PULSE_N) foot-to-foot pulses, time-normalised. pp_s: pulse intervals (s)."""
    m = np.median(pulses, axis=0)
    m = m - m[0]
    amp = m.max()
    out = {}
    if amp <= 0:
        return None
    m = m / amp
    ipk = int(np.argmax(m))
    out["rise_frac"] = ipk / PULSE_N
    for lvl in (0.25, 0.5, 0.75):
        above = np.flatnonzero(m >= lvl)
        out[f"width{int(lvl * 100)}_frac"] = (above[-1] - above[0]) / PULSE_N if len(above) else np.nan
    out["area_sys"] = float(m[:ipk + 1].sum() / PULSE_N)
    out["area_dia"] = float(m[ipk:].sum() / PULSE_N)
    c = dct(m, norm="ortho")[:N_DCT]
    c1 = dct(np.gradient(m), norm="ortho")[:8]
    out.update({f"dct{i}": v for i, v in enumerate(c)})
    out.update({f"ddct{i}": v for i, v in enumerate(c1)})
    out["pulse_sqi"] = float(np.median([np.corrcoef(p - p[0], m)[0, 1] for p in pulses]))
    return out


TIMING_FEATURES = ["pp_ms", "pp_sd_ms", "pp_rmssd_ms", "pp_irreg"]
RATE_FEATURES = ["pp_ms", "hr_ppg"]


def morph_feature_names():
    return (["rise_frac", "width25_frac", "width50_frac", "width75_frac", "area_sys", "area_dia", "amp_rel"]
            + [f"dct{i}" for i in range(N_DCT)] + [f"ddct{i}" for i in range(8)])


# ------------------------------------------------------------------ blocks
def _ecg_template(ecg, rs):
    a, b = int(PRE * FS), int(POST * FS)
    beats = np.stack([ecg[r - a:r + b] for r in rs])
    return np.median(beats, axis=0), beats


def _block_ecg_features(ecg, rs, rr_s):
    tmpl, beats = _ecg_template(ecg, rs)
    f = delineate(tmpl, float(np.median(rr_s)))
    sqi = float(np.median([np.corrcoef(b, tmpl)[0, 1] for b in beats]))
    return f, sqi, tmpl


def block_table(bp: BeatPairs, block_beats=10, min_sqi=0.8, keep_templates=False):
    """One row per block of consecutive matched beats. Returns (rows, templates)."""
    r, ft = bp.r, bp.foot
    a, b = int(PRE * FS), int(POST * FS)
    ok = (r - a >= 0) & (r + b < len(bp.ecg))
    rows, templates = [], []
    # amplitude reference for relative pulse amplitude
    amp_all = bp.ppg[bp.peak] - bp.ppg[ft] if len(ft) else np.array([1.0])
    amp_ref = float(np.median(amp_all)) if len(amp_all) and np.median(amp_all) > 0 else 1.0
    i = 0
    while i + block_beats + 1 <= len(r):
        idx = np.arange(i, i + block_beats + 1)          # +1 beat so every beat has an interval
        i += block_beats
        if not ok[idx[:-1]].all():
            continue
        rr = np.diff(r[idx]) / FS
        pp = np.diff(ft[idx]) / FS
        if (rr < 0.3).any() or (rr > 2.0).any() or (pp < 0.25).any() or (pp > 2.2).any():
            continue
        beats = idx[:-1]
        fe, sqi_e, tmpl = _block_ecg_features(bp.ecg, r[beats], rr)
        # split-half (odd / even beats) -> reliability of each ECG feature
        fo, _, _ = _block_ecg_features(bp.ecg, r[beats[0::2]], rr[0::2])
        fv, _, _ = _block_ecg_features(bp.ecg, r[beats[1::2]], rr[1::2])
        pulses = []
        for k in beats:
            seg = bp.ppg[ft[k]:ft[k + 1] + 1]
            if len(seg) < 8:
                break
            pulses.append(sps.resample(seg - seg[0], PULSE_N))
        if len(pulses) != len(beats):
            continue
        pf = pulse_features(np.asarray(pulses), pp)
        if pf is None:
            continue
        amp_blk = np.median(bp.ppg[bp.peak[beats]] - bp.ppg[ft[beats]])
        row = dict(t_start=r[beats[0]] / FS, n_beats=len(beats), ecg_sqi=sqi_e,
                   rr_ms=rr.mean() * 1000, rr_sd_ms=rr.std() * 1000,
                   rr_rmssd_ms=np.sqrt(np.mean(np.diff(rr) ** 2)) * 1000,
                   pp_ms=pp.mean() * 1000, hr_ppg=60.0 / pp.mean(), pp_sd_ms=pp.std() * 1000,
                   pp_rmssd_ms=np.sqrt(np.mean(np.diff(pp) ** 2)) * 1000,
                   pp_irreg=float(np.median(np.abs(np.diff(pp))) / pp.mean()),
                   pat_ms=float(np.median(bp.pat_ms[beats])), pat_sd_ms=float(np.std(bp.pat_ms[beats])),
                   amp_rel=float(amp_blk / amp_ref))
        row.update(fe)
        row.update({f"{k}__half1": v for k, v in fo.items()})
        row.update({f"{k}__half2": v for k, v in fv.items()})
        row.update(pf)
        if sqi_e < min_sqi or pf["pulse_sqi"] < min_sqi:
            continue
        rows.append(row)
        if keep_templates:
            templates.append((tmpl, np.median(np.asarray(pulses), axis=0)))
    return rows, templates


def interval_series(bp: BeatPairs):
    """Beat-matched RR (ECG) and PP (PPG foot-to-foot) series in ms, plus PAT, for consecutive matched beats."""
    rr = np.diff(bp.r) / FS * 1000
    pp = np.diff(bp.foot) / FS * 1000
    t = bp.r[:-1] / FS
    pat = bp.pat_ms[:-1]
    ok = (rr > 300) & (rr < 2000) & (pp > 250) & (pp < 2200) & (np.abs(pp - rr) < 300)
    return t[ok], rr[ok], pp[ok], pat[ok]
