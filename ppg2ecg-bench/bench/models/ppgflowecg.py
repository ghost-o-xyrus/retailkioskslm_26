"""PPGFlowECG adapter (Fang et al., arXiv 2509.19774) - released PyTorch weights.

Pipeline reproduced from the authors' repo (engine/solver.py::sample_shift):
  PPG window (10 s @128 Hz, per-window z-score, Elgendi-cleaned 0.5-8 Hz)
    -> CardioAlign VAE encoder (PPG)  -> latent condition
    -> latent rectified flow, Euler, `sampling_steps` steps (default 10)
    -> CardioAlign VAE decoder (ECG)  -> ECG window

Requirements: clone https://github.com/PKUDigitalHealth/PPGFlowECG, install its
requirements (torch, ema_pytorch, ...), and download from
https://huggingface.co/XiaochengFang/PPGFlowECG
  * VAE-iter-40000.pth   (3.8 GB, CardioAlign VAE)            -> vae_ckpt
  * checkpoint-10.pt     (97 MB, rectified-flow trainer, EMA)  -> flow_ckpt
Only torch + einops + pyyaml + scipy are needed for inference (ema_pytorch is
only used by the authors' trainer, which we do not import).
NOT yet executed in this harness (no torch in the dev sandbox) - the Kaggle
smoke kernel (k10) runs it on 2 subjects first.

Note: the flow sampler starts from Gaussian noise, so outputs are stochastic.
We fix the seed; the profiler counts every sampling step in latency.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from .. import dsp
from .base import ModelAdapter


class PPGFlowECG(ModelAdapter):
    name = "ppgflowecg"
    native_fs = 128.0
    window_s = 10.0
    framework = "pytorch"
    trained_on = {"mcmed": "train", "mimic_perform_af": "80pct", "vitaldb": "80pct", "bidmc": "80pct"}

    def __init__(self, repo_dir: str, vae_ckpt: str, flow_ckpt: str, config: str | None = None,
                 sampling_steps: int = 10, device: str = "auto", seed: int = 0, batch_size: int = 32):
        self.repo_dir = str(Path(repo_dir).resolve())
        self.vae_ckpt, self.flow_ckpt = vae_ckpt, flow_ckpt
        self.config = config or str(Path(self.repo_dir) / "config/latent_rectified_flow.yaml")
        self.sampling_steps, self.device, self.seed, self.batch_size = sampling_steps, device, seed, batch_size

    def load(self):
        import torch
        if self.repo_dir not in sys.path:
            sys.path.insert(0, self.repo_dir)
        from model.cardioalign_encoder.cardioalign_model import VAE_Decoder, VAE_Encoder
        from utils.io_utils import instantiate_from_config, load_yaml_config

        self._torch = torch
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dev = torch.device(self.device)

        def tload(path):
            try:  # torch >= 2.6 defaults to weights_only=True; plain state dicts load fine that way
                return torch.load(path, map_location=dev, weights_only=True)
            except Exception:
                print(f"[ppgflowecg] weights_only load failed for {path}; falling back to full unpickling "
                      "(only do this for files from the official HF repo)", flush=True)
                return torch.load(path, map_location=dev, weights_only=False)
        cfg = load_yaml_config(self.config)
        self.flow = instantiate_from_config(cfg["model"]).to(dev)
        state = tload(self.flow_ckpt)
        # trainer checkpoints store {'model', 'ema', 'opt', ...}; prefer EMA weights
        if "ema" in state:
            ema = {k.replace("ema_model.", "", 1): v for k, v in state["ema"].items() if k.startswith("ema_model.")}
            self.flow.load_state_dict(ema)
        else:
            self.flow.load_state_dict(state.get("model", state))
        self.flow.eval()

        vae = tload(self.vae_ckpt)
        self.enc = VAE_Encoder().to(dev).eval()
        self.dec = VAE_Decoder().to(dev).eval()
        # the authors load the *ECG* encoder weights for the PPG branch (shared aligned encoder)
        self.enc.load_state_dict(vae["encoder_ecg"])
        self.dec.load_state_dict(vae["decoder_ecg"])
        self._dev = dev
        print(f"[ppgflowecg] torch {torch.__version__}, device={dev}, steps={self.sampling_steps}", flush=True)

    def prepare_record(self, ppg):
        return dsp.bandpass(ppg, self.native_fs, 0.5, 8.0, order=3)

    def normalize_window(self, w):
        return dsp.zscore(w, axis=1)

    def infer(self, windows):
        torch = self._torch
        torch.manual_seed(self.seed)
        out = []
        with torch.no_grad():
            for i in range(0, len(windows), self.batch_size):
                x = torch.as_tensor(windows[i:i + self.batch_size], dtype=torch.float32, device=self._dev).unsqueeze(-1)
                cond = self.enc(x)[0]
                z = self.flow.sample_shift(shape=cond.shape, num_steps=self.sampling_steps, cond=cond)
                y = self.dec(z).squeeze(-1).cpu().numpy()
                out.append(y)
        return np.concatenate(out, axis=0)

    def n_params(self):
        try:
            return int(sum(p.numel() for m in (self.flow, self.enc, self.dec) for p in m.parameters()))
        except AttributeError:
            return None

    def weights_bytes(self):
        return sum(Path(p).stat().st_size for p in (self.vae_ckpt, self.flow_ckpt))
