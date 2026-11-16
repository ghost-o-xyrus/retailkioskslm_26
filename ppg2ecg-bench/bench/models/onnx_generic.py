"""Generic ONNX adapter.

Every Track-2 model is exported to ONNX once trained; this adapter then runs it
on any target (laptop CPU, Raspberry Pi, Jetson via onnxruntime-gpu/TensorRT,
phone via onnxruntime-mobile). It is also how edge latency is measured with
one code path for all models.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .. import dsp
from .base import ModelAdapter


class OnnxModel(ModelAdapter):
    framework = "onnx"

    def __init__(self, path: str, name: str = "onnx_model", native_fs: float = 128.0, window_s: float = 4.0,
                 input_norm: str = "minmax", ppg_band=(0.5, 8.0), threads: int | None = None):
        self.path, self.name = str(path), name
        self.native_fs, self.window_s = float(native_fs), float(window_s)
        self.input_norm, self.ppg_band, self.threads = input_norm, ppg_band, threads

    def load(self):
        import onnxruntime as ort
        so = ort.SessionOptions()
        if self.threads:
            so.intra_op_num_threads = self.threads
        self.sess = ort.InferenceSession(self.path, so, providers=ort.get_available_providers())
        inp = self.sess.get_inputs()[0]
        self._in_name, self._in_rank = inp.name, len(inp.shape)
        self._dtype = np.float32 if "float)" in inp.type and "double" not in inp.type else np.float64

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, *self.ppg_band) if self.ppg_band else ppg

    def normalize_window(self, w):
        return dsp.minmax(w, -1, 1, axis=1) if self.input_norm == "minmax" else dsp.zscore(w, axis=1)

    def infer(self, windows):
        x = windows.astype(self._dtype)
        if self._in_rank == 3:
            x = x[:, None, :]
        y = self.sess.run(None, {self._in_name: x})[0]
        return np.asarray(y, dtype=np.float64).reshape(len(windows), -1)

    def weights_bytes(self):
        return Path(self.path).stat().st_size
