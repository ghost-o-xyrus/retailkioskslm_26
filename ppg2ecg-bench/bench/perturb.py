"""PPG perturbations for robustness testing (applied at the sensor's original rate).

Each factory returns f(ppg, fs, rng) -> ppg. Severity is expressed in physically
meaningful units (dB SNR, seconds, Hz) so results read directly on a slide.
Real-motion robustness comes from DaLiA/WildPPG activity slices; these synthetic
corruptions add controlled, repeatable stress on every dataset.
"""
from __future__ import annotations

import numpy as np

from . import dsp


def _power(x):
    x = x - np.mean(x)
    return float(np.mean(x ** 2))


def gaussian(snr_db: float):
    def f(x, fs, rng):
        p = _power(x) / 10 ** (snr_db / 10)
        return x + rng.normal(0, np.sqrt(p), len(x))
    f.__name__ = f"gaussian_{snr_db}dB"
    return f


def baseline_wander(rel_amp: float = 1.0, freq: float = 0.15):
    def f(x, fs, rng):
        t = np.arange(len(x)) / fs
        ph = rng.uniform(0, 2 * np.pi)
        return x + rel_amp * np.std(x) * (np.sin(2 * np.pi * freq * t + ph) + 0.5 * np.sin(2 * np.pi * 2.3 * freq * t))
    f.__name__ = f"wander_{rel_amp}"
    return f


def motion(rate_per_min: float = 4, rel_amp: float = 2.0, dur=(1.0, 5.0)):
    """Bursts of band-limited (0.5-4 Hz, i.e. inside the PPG band) noise."""
    def f(x, fs, rng):
        y = x.copy()
        n_ev = rng.poisson(rate_per_min * len(x) / fs / 60)
        sd = np.std(x)
        for _ in range(n_ev):
            d = int(rng.uniform(*dur) * fs)
            s = rng.integers(0, max(1, len(x) - d))
            burst = dsp.bandpass(rng.standard_normal(d + int(2 * fs)), fs, 0.5, 4.0, order=2)[int(fs):int(fs) + d]
            burst *= rel_amp * sd / (np.std(burst) + 1e-12) * np.hanning(d)
            y[s:s + d] += burst
        return y
    f.__name__ = f"motion_{rate_per_min}pm_{rel_amp}x"
    return f


def time_shift(seconds: float):
    """Delay (+) or advance (-) the PPG relative to the ECG: probes PAT sensitivity."""
    def f(x, fs, rng):
        k = int(round(seconds * fs))
        if k > 0:
            return np.r_[np.full(k, x[0]), x[:-k]]
        if k < 0:
            return np.r_[x[-k:], np.full(-k, x[-1])]
        return x
    f.__name__ = f"shift_{seconds}s"
    return f


def low_rate(fs_low: float):
    """Simulate a low-rate wearable sensor (e.g. 25 Hz smartwatch): down- then up-sample."""
    def f(x, fs, rng):
        return dsp.resample(dsp.resample(x, fs, fs_low), fs_low, fs)[: len(x)]
    f.__name__ = f"lowrate_{fs_low}Hz"
    return f


def dropout(frac: float = 0.05, seg_s: float = 2.0):
    """Sensor dropouts: random segments replaced by the last valid value."""
    def f(x, fs, rng):
        y = x.copy()
        seg = int(seg_s * fs)
        n_seg = int(frac * len(x) / max(seg, 1))
        for _ in range(n_seg):
            s = rng.integers(1, max(2, len(x) - seg))
            y[s:s + seg] = y[s - 1]
        return y
    f.__name__ = f"dropout_{frac}"
    return f


def invert():
    def f(x, fs, rng):
        return -x
    f.__name__ = "invert"
    return f


def weak_pulse(ac_factor: float = 0.3, noise_floor: float = 0.05):
    """Low-signal PROXY: shrink the pulsatile (AC) part and add a fixed sensor noise floor.

    Mimics what lower perfusion or higher melanin absorption does to green reflective PPG
    (smaller AC amplitude at a constant electronic noise level). It is NOT a model of skin
    tone: use it to stress-test SNR, and use Fitzpatrick-labelled data for skin-tone claims.
    """
    def f(x, fs, rng):
        dc = dsp.bandpass(x, fs, 0.01, 0.5, order=2) if len(x) > 3 * fs else np.full_like(x, x.mean())
        ac = x - dc
        y = dc + ac_factor * ac
        return y + rng.normal(0, noise_floor * np.std(ac), len(x))
    f.__name__ = f"weakpulse_{ac_factor}"
    return f


REGISTRY = dict(weak_pulse=weak_pulse, gaussian=gaussian, baseline_wander=baseline_wander, motion=motion,
                time_shift=time_shift, low_rate=low_rate, dropout=dropout, invert=invert)


def build(spec: dict):
    """{'name': 'gaussian', 'snr_db': 10} -> callable (or None for 'clean')."""
    spec = dict(spec)
    name = spec.pop("name")
    if name == "clean":
        return None
    return REGISTRY[name](**spec)
