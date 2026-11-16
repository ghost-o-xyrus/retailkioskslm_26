"""CardioGAN adapter (Sarkar & Etemad, AAAI 2021) - released TF2 weights.

Needs the original repo's `codes/` directory (module.py, layers.py, tflib.py)
and TensorFlow. TensorFlow is imported lazily so the rest of the harness runs
without it.

Environment (see kaggle/README.md):
  * Recommended: Python 3.10 + tensorflow 2.15.1 (+ tensorflow-addons 0.23.0).
    2.15 is the last TF whose tf.keras is Keras 2; the authors' module.py calls
    tf.expand_dims on symbolic Keras inputs, which Keras 3 (TF >= 2.16) rejects.
  * Fallback on a newer TF: `pip install tf-keras==<same minor as TF>`; this
    adapter sets TF_USE_LEGACY_KERAS=1 before importing TensorFlow.
  * tensorflow_addons is only imported (never used: the generator uses
    layer_norm), so if it is missing we register an empty stub module.

dtype:
  "float64" - exactly the authors' setting (set_floatx('float64')).
  "float32" - the float64 checkpoint is restored, then the weights are cast into
              an identical float32 graph. ~20-30x faster on GPU; the smoke kernel
              reports max |float64 - float32| so you can confirm it is negligible.

Differences from the first BIDMC run (test_bidmc_cardiogan.py):
  * PPG is band-pass filtered over the WHOLE record before windowing.
  * Overlapping windows are stitched by the runner (configurable).
  * Output is filtered with the authors' FIR 3-45 Hz (filter_output=True),
    as in their realtime demo.
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import numpy as np

from .. import dsp
from .base import ModelAdapter


def _ensure_tfa_importable():
    try:
        import tensorflow_addons  # noqa: F401
    except Exception:
        stub = types.ModuleType("tensorflow_addons")
        stub.layers = types.SimpleNamespace(
            InstanceNormalization=lambda *a, **k: (_ for _ in ()).throw(
                RuntimeError("tensorflow_addons stub: instance_norm is not available")))
        sys.modules["tensorflow_addons"] = stub


class CardioGAN(ModelAdapter):
    name = "cardiogan"
    native_fs = 128.0
    window_s = 4.0
    framework = "tensorflow"
    trained_on = {"bidmc": "all", "capnobase": "all", "dalia": "all", "wesad": "all"}

    def __init__(self, repo_codes_dir: str, weights_dir: str, filter_output: bool = True, dtype: str = "float64",
                 batch_size: int = 256):
        self.repo_codes_dir = str(Path(repo_codes_dir).resolve())
        self.weights_dir = str(Path(weights_dir).resolve())
        self.filter_output = filter_output
        self.dtype = dtype
        self.batch_size = batch_size
        self.model = None

    def load(self):
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
        # Legacy Keras is only needed (and only exists as `tf_keras`) on TF >= 2.16. On TF <= 2.15,
        # setting TF_USE_LEGACY_KERAS makes tf.keras point to a missing tf_keras -> "No module named tensorflow.keras".
        try:
            from importlib.metadata import version
            major, minor = (int(v) for v in version("tensorflow").split(".")[:2])
            if (major, minor) >= (2, 16):
                os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")
            else:
                os.environ.pop("TF_USE_LEGACY_KERAS", None)
        except Exception:
            pass
        _ensure_tfa_importable()
        import tensorflow as tf
        if self.repo_codes_dir not in sys.path:
            sys.path.insert(0, self.repo_codes_dir)
        import module  # noqa: E402  (from the CardioGAN repo)
        import tflib   # noqa: E402

        keras = tf.keras
        keras.backend.set_floatx("float64")
        m64 = module.generator_attention()
        status = tflib.Checkpoint(dict(Gen_PPG2ECG=m64), self.weights_dir).restore()
        status.assert_existing_objects_matched()  # fails loudly if the weights did not load
        if self.dtype == "float32":
            keras.backend.set_floatx("float32")
            m32 = module.generator_attention()
            m32.set_weights([w.astype(np.float32) for w in m64.get_weights()])
            self.model, self._np_dtype, self._ref64 = m32, np.float32, m64
        else:
            self.model, self._np_dtype, self._ref64 = m64, np.float64, None
        self._tf = tf
        self._fn = tf.function(lambda x: self.model(x, training=False))
        self.versions = dict(tensorflow=tf.__version__, keras=getattr(keras, "__version__", "?"),
                             gpus=len(tf.config.list_physical_devices("GPU")))
        print(f"[cardiogan] TF {tf.__version__}, dtype={self.dtype}, GPUs={self.versions['gpus']}", flush=True)

    def float32_error(self, windows):
        """Max abs difference float32 vs float64 output on the given windows (None if dtype=float64)."""
        if self._ref64 is None:
            return None
        y32 = self.infer(windows)
        y64 = self._ref64(windows.astype(np.float64), training=False).numpy()
        return float(np.max(np.abs(y32 - y64)))

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, 1.0, 8.0, order=4)

    def normalize_window(self, w):
        return dsp.minmax(w, -1.0, 1.0, axis=1)

    def infer(self, windows):
        out = []
        for i in range(0, len(windows), self.batch_size):
            out.append(self._fn(windows[i:i + self.batch_size].astype(self._np_dtype)).numpy())
        return np.concatenate(out, axis=0).astype(np.float64)

    def postprocess(self, y):
        if self.filter_output:
            y = dsp.fir_bandpass(y, self.native_fs, 3.0, 45.0)
        return y

    def n_params(self):
        return int(self.model.count_params()) if self.model is not None else None

    def weights_bytes(self):
        return sum(f.stat().st_size for f in Path(self.weights_dir).glob("*.data-*"))

    def flops_per_window(self):
        try:
            tf = self._tf
            from tensorflow.python.profiler.model_analyzer import profile
            from tensorflow.python.profiler.option_builder import ProfileOptionBuilder
            f = tf.function(lambda x: self.model(x, training=False))
            spec = tf.TensorSpec([1, self.window_len], tf.float32 if self._np_dtype == np.float32 else tf.float64)
            g = f.get_concrete_function(spec).graph
            info = profile(g, options=ProfileOptionBuilder.float_operation())
            return float(info.total_float_ops)
        except Exception:
            return None
