"""Streaming inference: whole record in, continuous ECG out, on a common eval grid.

Steps for one (model, record):
  1. (optional) perturb raw PPG at its ORIGINAL sampling rate  - sensor-level corruption
  2. resample PPG to the model's native rate
  3. adapter.prepare_record()  - authors' whole-record preprocessing (filtering)
  4. cut overlapping windows (hop = window * (1 - overlap)), pad the tail
  5. per-window normalisation -> infer -> postprocess
  6. stitch with a tapered overlap-add (or plain concatenation if overlap = 0)
  7. resample prediction and reference ECG to eval_fs and trim to equal length
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np
from scipy.signal.windows import tukey

from . import dsp
from .models.base import ModelAdapter
from .record import Record


@dataclass
class RunOutput:
    pred: np.ndarray          # predicted ECG at eval_fs
    true: np.ndarray          # reference ECG at eval_fs
    ppg: np.ndarray           # (perturbed) PPG at eval_fs, for plots
    fs: float
    n_windows: int
    infer_seconds: float      # pure model time (excl. resampling / stitching)
    info: dict = field(default_factory=dict)


def _windows(x, L, hop):
    n = len(x)
    if n <= L:
        starts = [0]
    else:
        starts = list(range(0, n - L + 1, hop))
        if starts[-1] + L < n:          # cover the tail
            starts.append(n - L)
    pad = max(0, L - n)
    xp = np.pad(x, (0, pad), mode="reflect") if pad else x
    return np.stack([xp[s:s + L] for s in starts]), np.asarray(starts)


def stitch(windows, starts, n, taper=0.5):
    L = windows.shape[1]
    w =tukey(L, taper) + 1e-3 if taper > 0 else np.ones(L)
    acc = np.zeros(max(n, starts[-1] + L))
    wsum = np.zeros_like(acc)
    for y, s in zip(windows, starts):
        acc[s:s + L] += y * w
        wsum[s:s + L] += w
    return (acc / np.maximum(wsum, 1e-9))[:n]


def run_record(adapter: ModelAdapter, rec: Record, eval_fs: float = 128.0, overlap: float = 0.5,
               perturb=None, rng=None) -> RunOutput:
    rng = np.random.default_rng(0) if rng is None else rng
    ppg_raw = rec.ppg
    if perturb is not None:
        ppg_raw = perturb(ppg_raw, rec.ppg_fs, rng)

    fs_m = adapter.native_fs
    ppg_m = dsp.resample(ppg_raw, rec.ppg_fs, fs_m)
    x = adapter.prepare_record(ppg_m)

    L = adapter.window_len
    hop = max(1, int(round(L * (1.0 - overlap))))
    W, starts = _windows(x, L, hop)
    W = adapter.normalize_window(W)

    t0 = time.perf_counter()
    Y = adapter.infer(W)
    infer_s = time.perf_counter() - t0
    Y = adapter.postprocess(np.asarray(Y, dtype=np.float64))
    if Y.shape[1] != L:  # model emits a different length -> map back onto the window
        Y = np.stack([dsp.resample(y, Y.shape[1] / adapter.window_s, fs_m) for y in Y])[:, :L]

    pred_m = stitch(Y, starts, len(x), taper=0.5 if overlap > 0 else 0.0)

    pred = dsp.resample(pred_m, fs_m, eval_fs)
    true = dsp.resample(rec.ecg, rec.ecg_fs, eval_fs)
    ppg_e = dsp.resample(ppg_raw, rec.ppg_fs, eval_fs)
    n = min(len(pred), len(true), len(ppg_e))
    return RunOutput(pred[:n], true[:n], ppg_e[:n], eval_fs, len(W), infer_s,
                     info=dict(model=adapter.name, record=rec.key, window_s=adapter.window_s, overlap=overlap))
