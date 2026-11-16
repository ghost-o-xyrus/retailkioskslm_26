"""Model adapter interface.

An adapter wraps ONE model and hides everything model-specific: framework,
native sampling rate, window length, the authors' preprocessing, normalisation
and post-processing. The runner only ever calls:

    adapter.load()                                   # once
    x = adapter.prepare_record(ppg_native)           # whole-record preprocessing (e.g. filtering)
    y = adapter.infer(windows)                       # (N, L_in) -> (N, L_out) at native_fs
    y = adapter.postprocess(y)                       # optional, per window

Whole-record preprocessing is separate from per-window inference on purpose:
filtering each short window independently causes edge artefacts (this was the
source of most missed beats in the first BIDMC run).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class ModelAdapter(ABC):
    name: str = "base"
    native_fs: float = 128.0
    window_s: float = 4.0
    framework: str = "numpy"
    # Set by adapters that know it; used for leakage tagging.
    trained_on: dict = {}

    @property
    def window_len(self) -> int:
        return int(round(self.window_s * self.native_fs))

    def load(self) -> None:  # pragma: no cover - trivial default
        pass

    def prepare_record(self, ppg: np.ndarray) -> np.ndarray:
        """Preprocessing applied once to the full PPG stream at native_fs."""
        return ppg

    def normalize_window(self, w: np.ndarray) -> np.ndarray:
        """Per-window input normalisation, (N, L) -> (N, L)."""
        return w

    @abstractmethod
    def infer(self, windows: np.ndarray) -> np.ndarray:
        """(N, window_len) float array -> (N, window_len) ECG at native_fs."""

    def postprocess(self, ecg_windows: np.ndarray) -> np.ndarray:
        return ecg_windows

    # ----- optional hooks for the size/speed profiler
    def n_params(self) -> int | None:
        return None

    def weights_bytes(self) -> int | None:
        return None

    def flops_per_window(self) -> float | None:
        return None

    def fit(self, records) -> None:
        """Optional calibration on training records (used by baselines / Track 2)."""
        pass
