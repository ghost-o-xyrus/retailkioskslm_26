"""Physiology-free reference baseline.

Detect PPG pulses, place one fixed synthetic PQRST beat per pulse, shifted
earlier by a delay `pat` (pulse arrival time). `fit()` calibrates `pat` as the
median delay between true R peaks and PPG systolic peaks on training records.

If a learned model does not beat this on morphology metrics, it is only
transferring heart rate, not ECG information.
"""
from __future__ import annotations

import numpy as np

from .. import dsp
from ..datasets import synth_beat
from .base import ModelAdapter


class TemplateBaseline(ModelAdapter):
    name = "template_baseline"
    native_fs = 128.0
    window_s = 10.0
    framework = "numpy"

    def __init__(self, pat: float = 0.25):
        self.pat = float(pat)

    def fit(self, records):
        delays = []
        for rec in records:
            ppg = dsp.resample(rec.ppg, rec.ppg_fs, self.native_fs)
            ecg = dsp.resample(rec.ecg, rec.ecg_fs, self.native_fs)
            r = dsp.detect_rpeaks(ecg, self.native_fs)
            p = dsp.detect_ppg_peaks(ppg, self.native_fs)
            for q in p:
                prev = r[r < q]
                if len(prev):
                    d = (q - prev[-1]) / self.native_fs
                    if 0.05 < d < 1.0:
                        delays.append(d)
        if delays:
            self.pat = float(np.median(delays))
        return self.pat

    def infer(self, windows):
        fs = self.native_fs
        out = np.zeros_like(windows, dtype=np.float64)
        t = np.arange(windows.shape[1]) / fs
        for i, w in enumerate(windows):
            peaks = dsp.detect_ppg_peaks(w, fs)
            if len(peaks) < 2:
                continue
            rr = float(np.median(np.diff(peaks))) / fs
            for p in peaks:
                r_t = p / fs - self.pat
                m = (t > r_t - 0.4) & (t < r_t + 0.7)
                out[i, m] += synth_beat(t[m] - r_t, rr)
            # extrapolate one beat past the window edge so the last beat is not lost
            r_t = peaks[-1] / fs - self.pat + rr
            m = (t > r_t - 0.4) & (t < r_t + 0.7)
            out[i, m] += synth_beat(t[m] - r_t, rr)
        return out

    def n_params(self):
        return 1

    def flops_per_window(self):
        return 50.0 * self.window_len  # rough: filtering + peak search
