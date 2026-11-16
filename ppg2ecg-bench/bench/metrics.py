"""Evaluation metrics (objective D).

Four families, so that "gets the rhythm right" is never confused with
"reproduces the ECG":

  timing-free   hr_mae, rpeak sensitivity / ppv / f1, rpeak timing error, RMSSD error
  waveform-raw  rmse, mae, pearson, prd, fd, dtw          (sample-by-sample, as most papers report)
  waveform-lag  rmse_lag, pearson_lag, best_lag_ms        (best global shift within +-max_lag per window)
  morphology    beat_pearson, beat_rmse                   (matched beats, each centred on its own R peak)

Conventions (all configurable, all recorded in the results):
  * both signals are band-passed with the SAME filter (eval_band) before scoring;
  * waveform metrics use per-window min-max to [-1, 1] (CardioGAN / RDDM convention);
  * R peaks come from the same detector for pred and true (dsp.detect_rpeaks);
  * FD uses curves (sample index, amplitude), matching how values ~3-7 are reported in RDDM.
"""
from __future__ import annotations

import numpy as np

from . import dsp


# ------------------------------------------------------------------ DP distances
def _antidiag_dp(a, b, mode):
    """Discrete Frechet ('max') or DTW ('sum') with vectorised anti-diagonals."""
    n, m = len(a), len(b)
    if mode == "frechet":  # 2-D curves (index, value)
        ia, ib = np.arange(n, dtype=float), np.arange(m, dtype=float)
        d = np.sqrt((ia[:, None] - ib[None, :]) ** 2 + (a[:, None] - b[None, :]) ** 2)
    else:
        d = np.abs(a[:, None] - b[None, :])
    C = np.full((n, m), np.inf)
    for k in range(n + m - 1):
        i = np.arange(max(0, k - m + 1), min(n, k + 1))
        j = k - i
        if k == 0:
            C[0, 0] = d[0, 0]
            continue
        up = np.where(i > 0, C[np.maximum(i - 1, 0), j], np.inf)
        left = np.where(j > 0, C[i, np.maximum(j - 1, 0)], np.inf)
        diag = np.where((i > 0) & (j > 0), C[np.maximum(i - 1, 0), np.maximum(j - 1, 0)], np.inf)
        best = np.minimum(np.minimum(up, left), diag)
        C[i, j] = np.maximum(best, d[i, j]) if mode == "frechet" else best + d[i, j]
    return C[-1, -1]


def frechet(a, b):
    return float(_antidiag_dp(np.asarray(a, float), np.asarray(b, float), "frechet"))


def dtw(a, b, band=None):
    return float(_antidiag_dp(np.asarray(a, float), np.asarray(b, float), "dtw") / len(a))


# ------------------------------------------------------------------ helpers
def _pearson(a, b):
    a, b = a - a.mean(), b - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else np.nan


def match_peaks(ref, est, tol):
    """Greedy one-to-one matching within tol samples. Returns (pairs, fn, fp)."""
    ref, est = np.asarray(ref), np.asarray(est)
    used = np.zeros(len(est), bool)
    pairs = []
    for r in ref:
        if len(est) == 0:
            break
        d = np.abs(est - r).astype(float)
        d[used] = np.inf
        k = int(np.argmin(d))
        if d[k] <= tol:
            used[k] = True
            pairs.append((r, est[k]))
    return pairs, len(ref) - len(pairs), int((~used).sum())


def best_lag(a, b, max_lag):
    """Lag (samples) that maximises corr(a shifted, b); positive = a is late."""
    best, best_r = 0, -np.inf
    for L in range(-max_lag, max_lag + 1):
        if L >= 0:
            x, y = a[L:], b[:len(b) - L]
        else:
            x, y = a[:L], b[-L:]
        r = _pearson(x, y)
        if r > best_r:
            best, best_r = L, r
    return best


# ------------------------------------------------------------------ main entry
def evaluate(pred, true, fs, window_s=10.0, eval_band=(0.5, 40.0), max_lag_s=0.3, rpeak_tol_s=0.15,
             compute_fd=True, compute_dtw=False, fd_max_windows=40):
    """Score one continuous prediction against its reference.

    Returns (window_rows, record_row): a list of per-window dicts and one dict
    of record-level metrics (R-peak detection totals, HRV).
    """
    pred = np.asarray(pred, float)
    true = np.asarray(true, float)
    if eval_band:
        pred = dsp.bandpass(pred, fs, *eval_band, order=2)
        true = dsp.bandpass(true, fs, *eval_band, order=2)

    rp = dsp.detect_rpeaks(pred, fs)
    rt = dsp.detect_rpeaks(true, fs)
    tol = int(round(rpeak_tol_s * fs))
    pairs, fn, fp = match_peaks(rt, rp, tol)
    errs_ms = np.array([(e - r) / fs * 1000 for r, e in pairs]) if pairs else np.array([])

    L = int(round(window_s * fs))
    max_lag = int(round(max_lag_s * fs))
    half_pre, half_post = int(0.25 * fs), int(0.45 * fs)
    rows = []
    n_win = max(1, (len(true) - L) // L + 1)
    fd_stride = 1 if not fd_max_windows else max(1, int(np.ceil(n_win / fd_max_windows)))
    for wi, w0 in enumerate(range(0, len(true) - L + 1, L)):
        sl = slice(w0, w0 + L)
        p = dsp.minmax(pred[sl])
        t = dsp.minmax(true[sl])
        row = dict(t_start=w0 / fs)

        # timing-free
        rt_w = rt[(rt >= w0) & (rt < w0 + L)]
        rp_w = rp[(rp >= w0) & (rp < w0 + L)]
        hr_t = 60.0 * fs / np.mean(np.diff(rt_w)) if len(rt_w) > 1 else np.nan
        hr_p = 60.0 * fs / np.mean(np.diff(rp_w)) if len(rp_w) > 1 else np.nan
        row.update(hr_true=hr_t, hr_pred=hr_p, hr_ae=abs(hr_p - hr_t))
        pw, fnw, fpw = match_peaks(rt_w, rp_w, tol)
        row.update(r_tp=len(pw), r_fn=fnw, r_fp=fpw,
                   r_timing_mae_ms=float(np.mean([abs(e - r) for r, e in pw]) / fs * 1000) if pw else np.nan)

        # waveform raw
        diff = p - t
        row.update(rmse=float(np.sqrt(np.mean(diff ** 2))), mae=float(np.mean(np.abs(diff))),
                   pearson=_pearson(p, t),
                   prd=float(100 * np.sqrt(np.sum(diff ** 2) / max(np.sum(t ** 2), 1e-12))))
        # FD/DTW are O(L^2): evaluated on evenly spaced windows (<= fd_max_windows per record)
        if compute_fd and wi % fd_stride == 0:
            row["fd"] = frechet(p, t)
        if compute_dtw and wi % fd_stride == 0:
            row["dtw"] = dtw(p, t)

        # waveform after best shift
        lag = best_lag(p, t, max_lag)
        if lag >= 0:
            x, y = p[lag:], t[:L - lag]
        else:
            x, y = p[:lag], t[-lag:]
        row.update(best_lag_ms=lag / fs * 1000, rmse_lag=float(np.sqrt(np.mean((x - y) ** 2))),
                   pearson_lag=_pearson(x, y))

        # morphology: matched beats, each centred on its own R peak
        bc, br = [], []
        for r, e in pw:
            if r - half_pre < 0 or e - half_pre < 0 or r + half_post > len(true) or e + half_post > len(pred):
                continue
            bt = dsp.minmax(true[r - half_pre:r + half_post])
            bp = dsp.minmax(pred[e - half_pre:e + half_post])
            bc.append(_pearson(bp, bt))
            br.append(float(np.sqrt(np.mean((bp - bt) ** 2))))
        row.update(beat_pearson=float(np.mean(bc)) if bc else np.nan,
                   beat_rmse=float(np.mean(br)) if br else np.nan)
        rows.append(row)

    # record level
    tp = len(pairs)
    sens = tp / max(tp + fn, 1)
    ppv = tp / max(tp + fp, 1)
    rr_t = np.diff(rt) / fs * 1000
    rr_p = np.diff(rp) / fs * 1000

    def rmssd(rr):
        rr = rr[(rr > 300) & (rr < 2000)]
        return float(np.sqrt(np.mean(np.diff(rr) ** 2))) if len(rr) > 2 else np.nan

    rec = dict(r_sens=sens, r_ppv=ppv, r_f1=2 * sens * ppv / max(sens + ppv, 1e-12),
               r_timing_median_ms=float(np.median(errs_ms)) if len(errs_ms) else np.nan,
               r_timing_iqr_ms=float(np.subtract(*np.percentile(errs_ms, [75, 25]))) if len(errs_ms) else np.nan,
               rmssd_true=rmssd(rr_t), rmssd_pred=rmssd(rr_p))
    rec["rmssd_ae"] = abs(rec["rmssd_pred"] - rec["rmssd_true"])
    return rows, rec
