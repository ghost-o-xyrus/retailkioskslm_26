"""Zhu, Tian, Wong & Wu (2019) "ECG Reconstruction via PPG: A Pilot Study" (arXiv 1904.10481) -
the classical linear method: map the DCT of each PPG cycle to the DCT of the matching ECG cycle
with ridge regression.

Paper recipe (R2R scheme): cycles are cut ECG R-peak to R-peak and PPG foot to foot, time-scaled to
a fixed length, DCT; the first 12 PPG coefficients predict the first 100 ECG coefficients with ridge
regression (lambda = 500); inverse DCT gives the ECG cycle. The paper trains and tests WITHIN each
recording (first 80% -> last 20%). Here it is trained ONCE on CapnoBase (the paper's dataset) and
applied zero-shot like every other model, which is the deployment question; the personalized variant
is what scripts/info_analysis.py measures as `personalized` R^2.

Inference without an ECG: PPG feet are detected in the window, each foot-to-foot interval gets a
predicted ECG cycle of the same length, placed `pat` seconds earlier (median R->foot delay learned
in fit). 1,200 weights (12 x 100) - the smallest learned model in the benchmark.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sps
from scipy.fft import dct, idct

from .. import dsp
from .base import ModelAdapter

N_CYCLE = 300


class ZhuDCT(ModelAdapter):
    name = "zhu_dct"
    native_fs = 128.0
    window_s = 10.0
    framework = "numpy"

    def __init__(self, n_ppg=12, n_ecg=100, alpha=500.0, pat=0.25):
        self.n_ppg, self.n_ecg, self.alpha, self.pat = n_ppg, n_ecg, float(alpha), float(pat)
        self.W = np.zeros((n_ppg, n_ecg))   # unfitted = flat output (only useful for timing/profiling)
        self.b = np.zeros(n_ecg)
        self.fitted = False

    @staticmethod
    def _cycle(x):
        x = sps.resample(np.asarray(x, float) - x[0], N_CYCLE)
        rng = x.max() - x.min()
        return (x - x.min()) / rng * 2 - 1 if rng > 0 else None

    def fit(self, records):
        from ..info.beats import pair_beats, FS
        X, Y, delays = [], [], []
        for rec in records:
            bp = pair_beats(rec)
            for i in range(len(bp.r) - 1):
                e = bp.ecg[bp.r[i]:bp.r[i + 1]]
                p = bp.ppg[bp.foot[i]:bp.foot[i + 1]]
                if not (0.3 * FS < len(e) < 2.0 * FS and 0.3 * FS < len(p) < 2.2 * FS):
                    continue
                ce, cp = self._cycle(e), self._cycle(p)
                if ce is None or cp is None:
                    continue
                X.append(dct(cp, norm="ortho")[: self.n_ppg]), Y.append(dct(ce, norm="ortho")[: self.n_ecg])
                delays.append((bp.foot[i] - bp.r[i]) / FS)
        X, Y = np.asarray(X), np.asarray(Y)
        if len(X) < 50:
            raise ValueError(f"zhu_dct.fit: only {len(X)} usable cycles")
        mx, my = X.mean(0), Y.mean(0)
        Xc, Yc = X - mx, Y - my
        self.W = np.linalg.solve(Xc.T @ Xc + self.alpha * np.eye(X.shape[1]), Xc.T @ Yc)
        self.b = my - mx @ self.W
        self.pat = float(np.median(delays))
        self.fitted = True
        return dict(n_cycles=len(X), pat=self.pat)

    def _predict_cycle(self, p, n_out):
        cp = self._cycle(p)
        if cp is None:
            return np.zeros(n_out)
        c = np.zeros(N_CYCLE)
        c[: self.n_ecg] = dct(cp, norm="ortho")[: self.n_ppg] @ self.W + self.b
        return sps.resample(idct(c, norm="ortho"), n_out)

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, 0.5, 8.0, order=3)

    def infer(self, windows):
        if not self.fitted and not getattr(self, "_warned", False):
            print("[zhu_dct] WARNING: not fitted (config: fit_on: [capnobase]) - output is flat", flush=True)
            self._warned = True
        fs = self.native_fs
        out = np.zeros_like(windows, dtype=np.float64)
        shift = int(round(self.pat * fs))
        for i, w in enumerate(windows):
            feet = dsp.detect_ppg_feet(w, fs)
            for a, b in zip(feet[:-1], feet[1:]):
                if not (0.3 * fs < b - a < 2.2 * fs):
                    continue
                cyc = self._predict_cycle(w[a:b + 1], b - a)
                s = a - shift
                lo, hi = max(0, s), min(len(w), s + len(cyc))
                if hi > lo:
                    out[i, lo:hi] = cyc[lo - s:hi - s]
        return out

    def n_params(self):
        return self.n_ppg * self.n_ecg + self.n_ecg

    def flops_per_window(self):
        return 2.0 * self.n_ppg * self.n_ecg * 15 + 15 * 2 * N_CYCLE * np.log2(N_CYCLE)
