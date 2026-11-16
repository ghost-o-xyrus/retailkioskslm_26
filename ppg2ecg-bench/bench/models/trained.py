"""Adapters for the four code-only models trained with their authors' recipes (bench/train/*).

Each training output folder holds weights.pth, meta.json and a copy of the authors' repo (repo/).
meta.json fixes the inference recipe: sampling rate, window, how training windows were normalised.
Authors' modules are loaded from their files under unique names, so repos that reuse module names
(`models`, `utils`) cannot collide.

  chiu2020    PPG2ECG (conv + STN + attention), 2.05-s windows at 125 Hz, min-max [-1, 1]
  clep_gan    attention U-Net pair; PPG encoder -> ECG decoder; 4.1-s windows at 125 Hz made of four
              128-sample segments, EACH min-max normalised (their training format)
  p2e_wgan    1-D U-Net generator + their moving-average smoother; 3-s windows at 125 Hz
  yalcin2026  UNet + Transformer generator; 4-s windows at 128 Hz, min-max [-1, 1]
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np
from scipy import signal as sps

from .. import dsp
from .base import ModelAdapter


def _load(path, name, stub=()):
    for s in stub:                       # optional imports the authors use only for printing summaries
        m = sys.modules.get(s)
        if m is None or not hasattr(m, "summary"):   # a broken/namespace install counts as missing
            m = types.ModuleType(s)
            m.summary = lambda *a, **k: None
            sys.modules[s] = m
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _norm(w, how):
    if how in ("zscore_window",):
        return dsp.zscore(w, axis=1)
    if how == "minmax01_window":
        return dsp.minmax(w, 0.0, 1.0, axis=1)
    return dsp.minmax(w, -1.0, 1.0, axis=1)   # minmax_window (and the fallback for 'global')


class _Trained(ModelAdapter):
    framework = "pytorch"
    repo_subdir = "repo"

    def __init__(self, trained_dir: str, device: str = "auto", batch_size: int = 256):
        self.dir = Path(trained_dir)
        self.meta = json.loads((self.dir / "meta.json").read_text())
        self.native_fs = float(self.meta["fs"])
        self.window_s = float(self.meta["window"]) / self.native_fs
        self.trained_on = dict(self.meta.get("trained_on", {}))
        self.device, self.batch_size = device, batch_size
        self.repo = self.dir / self.repo_subdir

    def _setup(self):
        import torch
        self._torch = torch
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._dev = torch.device(self.device)
        return torch

    def _state(self):
        return self._torch.load(self.dir / "weights.pth", map_location=self._dev, weights_only=False)

    @staticmethod
    def _strip(sd):
        return {k[7:] if k.startswith("module.") else k: v for k, v in sd.items()}

    def _forward(self, x):
        raise NotImplementedError

    def infer(self, windows):
        torch = self._torch
        out = []
        with torch.no_grad():
            for i in range(0, len(windows), self.batch_size):
                x = torch.as_tensor(np.ascontiguousarray(windows[i:i + self.batch_size]), dtype=torch.float32,
                                    device=self._dev)
                out.append(self._forward(x).reshape(len(x), -1).cpu().numpy())
        return np.concatenate(out)[:, : windows.shape[1]]

    def n_params(self):
        try:
            return int(sum(p.numel() for m in self._nets for p in m.parameters()))
        except AttributeError:
            return None

    def weights_bytes(self):
        return (self.dir / "weights.pth").stat().st_size


class Chiu2020(_Trained):
    name = "chiu2020"

    def load(self):
        torch = self._setup()
        mods = _load(self.repo / "modules" / "models.py", "chiu_models")
        m = self.meta
        self.net = mods.PPG2ECG(m["input_size"], use_stn=m.get("use_stn", True),
                                use_attention=m.get("use_attention", True)).to(self._dev).eval()
        st = self._state()
        self.net.load_state_dict(self._strip(st.get("net", st)))
        self._nets = [self.net]

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, 0.5, 10.0, order=3)

    def normalize_window(self, w):
        return _norm(w, self.meta.get("ppg_stats", {}).get("norm", "minmax_window"))

    def _forward(self, x):
        return self.net(x.unsqueeze(1))["output"]


class ClepGAN(_Trained):
    name = "clep_gan"

    def load(self):
        torch = self._setup()
        unet = _load(self.repo / "unet.py", "clep_unet")
        m = self.meta
        mk = lambda: unet.generator_atten_unet(self.device, input_channel=1, filter_size=m["filter_size"],
                                               kernel_size=m["kernel_size"], norm=False).to(self._dev).eval()
        self.GP, self.GE = mk(), mk()
        st = self._state()
        self.GP.load_state_dict(st["GP"])
        self.GE.load_state_dict(st["GE"])
        self._nets = [self.GP, self.GE]

    def prepare_record(self, ppg):
        x = sps.detrend(np.asarray(ppg, float))
        b, a = sps.butter(3, [0.3 / (self.native_fs / 2), 8.0 / (self.native_fs / 2)], btype="band")
        return sps.filtfilt(b, a, x)

    def normalize_window(self, w):
        seg = int(self.meta.get("segment", 128))
        n, L = w.shape
        return dsp.minmax(w.reshape(n, L // seg, seg), -1.0, 1.0, axis=-1).reshape(n, L)

    def _forward(self, x):
        conn, _ = self.GP.encode(x)
        y, _ = self.GE.generate(conn)
        return y


class P2EWGAN(_Trained):
    name = "p2e_wgan"

    def load(self):
        torch = self._setup()
        mods = _load(self.repo / "models.py", "p2e_models", stub=("torchsummary",))
        sys.modules["torchsummary"].summary = lambda *a, **k: None
        self.net = mods.GeneratorUNet().to(self._dev).eval()
        self.net.load_state_dict(self._strip(self._state()["generator"]))
        # their output smoother (utils.smoother): 4-tap moving average + replication pad
        self.mean_conv = torch.nn.Conv1d(1, 1, 4, bias=False, padding_mode="replicate", padding=1).to(self._dev)
        self.mean_conv.weight.data.fill_(0.25)
        self.pad = torch.nn.ReplicationPad1d((0, 1))
        self._nets = [self.net]

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, 0.5, 8.0, order=3)

    def normalize_window(self, w):
        return _norm(w, self.meta.get("ppg_stats", {}).get("norm", "minmax_window"))

    def _forward(self, x):
        y = self.net(x.unsqueeze(1))
        return self.pad(self.mean_conv(y))


class Yalcin2026(_Trained):
    name = "yalcin2026"

    def load(self):
        torch = self._setup()
        code = self.repo / "code"
        sys.path.insert(0, str(code))
        yt = _load(code / "train.py", "yalcin_train")
        cfg = yt.ModelConfig(**{k: (tuple(v) if isinstance(v, list) else v) for k, v in self.meta["model_config"].items()},
                             device=self.device)
        self.net = yt.PPGtoECGGenerator(cfg).to(self._dev).eval()
        self.net.load_state_dict(self._strip(self._state()["generator"]))
        self._nets = [self.net]

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, 0.5, 8.0, order=4)

    def normalize_window(self, w):
        return dsp.minmax(w, -1.0, 1.0, axis=1)

    def _forward(self, x):
        return self.net(x.unsqueeze(1))


TRAINED = {"chiu2020": Chiu2020, "clep_gan": ClepGAN, "p2e_wgan": P2EWGAN, "yalcin2026": Yalcin2026}
