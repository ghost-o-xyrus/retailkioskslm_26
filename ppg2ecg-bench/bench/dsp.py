"""Signal utilities shared by the whole harness (numpy/scipy only).

The SAME R-peak detector is used for every model and dataset so that HR / R-peak
metrics are comparable. It is a Pan-Tompkins style detector; if biosppy is
installed you can switch to Hamilton via detect_rpeaks(method="hamilton").
"""
from __future__ import annotations

from fractions import Fraction

import numpy as np
from scipy import signal as sps


# ----------------------------------------------------------------- filtering
def bandpass(x, fs, lo, hi, order=4):
    nyq = fs / 2.0
    hi = min(hi, 0.95 * nyq)
    sos = sps.butter(order, [lo / nyq, hi / nyq], btype="band", output="sos")
    return sps.sosfiltfilt(sos, x, axis=-1)


def highpass(x, fs, lo, order=4):
    sos = sps.butter(order, lo / (fs / 2.0), btype="high", output="sos")
    return sps.sosfiltfilt(sos, x, axis=-1)


def fir_bandpass(x, fs, lo, hi, order=None):
    """Equivalent of CardioGAN's biosppy FIR filter_ecg (order = 0.3*fs)."""
    order = int(0.3 * fs) if order is None else order
    numtaps = order + 1 if order % 2 == 0 else order  # odd taps for bandpass
    b = sps.firwin(numtaps, [lo, hi], pass_zero=False, fs=fs)
    return sps.filtfilt(b, [1.0], x, axis=-1, padlen=min(3 * numtaps, x.shape[-1] - 1))


# ----------------------------------------------------------------- resampling
def resample(x, fs_in, fs_out, method="poly"):
    """Resample a 1-D signal. 'poly' (anti-aliased, default) or 'linear'."""
    x = np.asarray(x, dtype=np.float64)
    if abs(fs_in - fs_out) < 1e-9:
        return x.copy()
    if method == "linear":
        n_out = int(round(len(x) * fs_out / fs_in))
        t_in = np.arange(len(x)) / fs_in
        t_out = np.arange(n_out) / fs_out
        return np.interp(t_out, t_in, x)
    frac = Fraction(fs_out / fs_in).limit_denominator(1000)
    # padtype='line': default zero-padding creates huge edge steps on signals with a DC
    # offset (e.g. raw optical counts ~ -19000), which then dominate peak detection.
    return sps.resample_poly(x, frac.numerator, frac.denominator, padtype="line")


# ----------------------------------------------------------------- normalisation
def minmax(x, lo=-1.0, hi=1.0, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    mn = x.min(axis=axis, keepdims=True)
    mx = x.max(axis=axis, keepdims=True)
    rng = np.where(mx - mn < 1e-12, 1.0, mx - mn)
    return lo + (x - mn) * (hi - lo) / rng


def zscore(x, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    sd = x.std(axis=axis, keepdims=True)
    return (x - x.mean(axis=axis, keepdims=True)) / np.where(sd < 1e-12, 1.0, sd)


# ----------------------------------------------------------------- peaks
def detect_rpeaks(ecg, fs, method="pantompkins"):
    """Return R-peak sample indices of a single-lead ECG."""
    ecg = np.asarray(ecg, dtype=np.float64)
    if method == "hamilton":
        from biosppy.signals import ecg as becg  # optional dependency
        r, = becg.hamilton_segmenter(ecg, sampling_rate=fs)
        r, = becg.correct_rpeaks(ecg, r, sampling_rate=fs, tol=0.05)
        return np.asarray(r, dtype=int)

    if len(ecg) < int(fs):
        return np.array([], dtype=int)
    f = bandpass(ecg, fs, 5.0, 15.0, order=2)
    # polarity: generated ECGs can be inverted; use the dominant deflection
    if np.abs(f.min()) > 1.5 * np.abs(f.max()):
        f = -f
    d = np.gradient(f) ** 2
    win = max(1, int(0.12 * fs))
    integ = np.convolve(d, np.ones(win) / win, mode="same")
    thr = 0.3 * np.percentile(integ, 98)
    cand, _ = sps.find_peaks(integ, height=thr, distance=int(0.30 * fs))
    # refine to local max of filtered signal within +-75 ms
    half = int(0.075 * fs)
    peaks = []
    for c in cand:
        a, b = max(0, c - half), min(len(f), c + half + 1)
        peaks.append(a + int(np.argmax(f[a:b])))
    peaks = np.unique(np.asarray(peaks, dtype=int))
    # enforce refractory period after refinement
    keep = []
    for p in peaks:
        if keep and p - keep[-1] < int(0.25 * fs):
            if f[p] > f[keep[-1]]:
                keep[-1] = p
            continue
        keep.append(p)
    return np.asarray(keep, dtype=int)


def detect_ppg_peaks(ppg, fs):
    """Systolic peaks (Elgendi-style two moving averages)."""
    x = bandpass(np.asarray(ppg, dtype=np.float64), fs, 0.5, 8.0, order=2)
    x = np.clip(x, 0, None) ** 2
    w1, w2 = max(1, int(0.111 * fs)), max(1, int(0.667 * fs))
    ma_peak = np.convolve(x, np.ones(w1) / w1, mode="same")
    ma_beat = np.convolve(x, np.ones(w2) / w2, mode="same")
    blocks = ma_peak > (ma_beat + 0.02 * x.mean())
    peaks = []
    edges = np.flatnonzero(np.diff(blocks.astype(int)))
    starts, ends = edges[::2] + 1, edges[1::2] + 1
    if blocks[0]:
        starts = np.r_[0, starts]
    for s, e in zip(starts, ends):
        if e - s >= w1:
            peaks.append(s + int(np.argmax(x[s:e])))
    peaks = np.asarray(peaks, dtype=int)
    if len(peaks) > 1:  # refractory
        keep = [peaks[0]]
        for p in peaks[1:]:
            if p - keep[-1] >= int(0.3 * fs):
                keep.append(p)
        peaks = np.asarray(keep)
    return peaks


def detect_ppg_feet(ppg, fs, peaks=None):
    """Pulse onsets: minimum of the filtered PPG in the 400 ms before each systolic peak."""
    x = bandpass(np.asarray(ppg, dtype=np.float64), fs, 0.5, 8.0, order=2)
    peaks = detect_ppg_peaks(ppg, fs) if peaks is None else peaks
    look = int(0.4 * fs)
    return np.asarray([max(0, p - look) + int(np.argmin(x[max(0, p - look):p + 1])) for p in peaks], dtype=int)
