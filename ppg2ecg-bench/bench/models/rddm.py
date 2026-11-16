"""RDDM adapter (Shome, Sarkar, Etemad - "Region-Disentangled Diffusion Model for High-Fidelity
PPG-to-ECG Translation", AAAI 2024) - released PyTorch weights.

Repo:    https://github.com/DebadityaQU/RDDM  (model.py, diffusion.py are imported unchanged)
Weights: Google Drive folder linked from the README:
         rddm_main_network.pth, rddm_condition_encoder_1.pth, rddm_condition_encoder_2.pth
Trained on BIDMC, CapnoBase, DaLiA, WESAD and MIMIC-AFib (train splits of the authors' .npy files,
which were never released -> every one of those datasets is tagged `possibly_seen`).

Authors' pipeline (data.py / std_eval.py):
  4-s windows at 128 Hz (512 samples), min-max to [-1, 1] per window, then neurokit2 ppg_clean
  (Elgendi: Butterworth order 3, 0.5-8 Hz, zero-phase); conditioning U-Nets on the PPG window,
  10-step region-disentangled reverse diffusion from Gaussian noise -> ECG window in ~[-1, 1].
In the harness the 0.5-8 Hz filter is applied once to the whole record (no per-window edge
effects) and min-max per window; the authors' exact per-window order is reproduced by
scripts/author_eval.py.

Sampling is stochastic (Gaussian start + noise at every step); the seed is fixed per call.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from .. import dsp
from .base import ModelAdapter


class RDDM(ModelAdapter):
    name = "rddm"
    native_fs = 128.0
    window_s = 4.0
    framework = "pytorch"
    trained_on = {"bidmc": "possibly", "capnobase": "possibly", "dalia": "possibly", "wesad": "possibly",
                  "mimic_perform_af": "possibly"}

    def __init__(self, repo_dir: str, weights_dir: str, n_steps: int = 10, device: str = "auto", seed: int = 0,
                 batch_size: int = 128):
        self.repo_dir = str(Path(repo_dir).resolve())
        self.weights_dir = Path(weights_dir)
        self.n_steps, self.device, self.seed, self.batch_size = n_steps, device, seed, batch_size

    def load(self):
        import torch
        if self.repo_dir not in sys.path:
            sys.path.insert(0, self.repo_dir)
        from diffusion import RDDM as _RDDM, freeze_model  # authors' code, unchanged
        from model import ConditionNet, DiffusionUNetCrossAttention

        self._torch = torch
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dev = torch.device(self.device)

        def tload(name):
            p = next(self.weights_dir.rglob(name))
            try:
                return torch.load(p, map_location=dev, weights_only=True)
            except Exception:
                print(f"[rddm] weights_only load failed for {p}; full unpickling (official Drive files only)", flush=True)
                return torch.load(p, map_location=dev, weights_only=False)

        self.dpm = _RDDM(eps_model=DiffusionUNetCrossAttention(512, 1, self.device),
                         region_model=DiffusionUNetCrossAttention(512, 1, self.device),
                         betas=(1e-4, 0.2), n_T=self.n_steps).to(dev)
        self.dpm.load_state_dict(tload("rddm_main_network.pth"))
        self.c1, self.c2 = ConditionNet().to(dev), ConditionNet().to(dev)
        self.c1.load_state_dict(tload("rddm_condition_encoder_1.pth"))
        self.c2.load_state_dict(tload("rddm_condition_encoder_2.pth"))
        for m in (self.dpm, self.c1, self.c2):
            freeze_model(m)
        self._dev = dev
        print(f"[rddm] torch {torch.__version__}, device={dev}, steps={self.n_steps}", flush=True)

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, 0.5, 8.0, order=3)

    def normalize_window(self, w):
        return dsp.minmax(w, -1.0, 1.0, axis=1)

    def infer(self, windows):
        torch = self._torch
        torch.manual_seed(self.seed)
        out = []
        with torch.no_grad():
            for i in range(0, len(windows), self.batch_size):
                x = torch.as_tensor(windows[i:i + self.batch_size], dtype=torch.float32, device=self._dev).unsqueeze(1)
                y = self.dpm(cond1=self.c1(x), cond2=self.c2(x), mode="sample", window_size=x.shape[-1])
                out.append(y.squeeze(1).cpu().numpy())
        return np.concatenate(out, axis=0)

    def n_params(self):
        try:
            return int(sum(p.numel() for m in (self.dpm, self.c1, self.c2) for p in m.parameters()))
        except AttributeError:
            return None

    def weights_bytes(self):
        return sum(p.stat().st_size for p in self.weights_dir.rglob("rddm_*.pth"))
