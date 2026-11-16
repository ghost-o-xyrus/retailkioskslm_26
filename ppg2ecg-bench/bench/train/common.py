"""Shared helpers for training the code-only models with their authors' recipes.

Principle: run the authors' code as unchanged as possible. We only
  * prepare data in the format their code reads,
  * cap wall-clock time (Kaggle T4 budget) without changing what one training step does,
  * restore removed numpy aliases (np.long, np.int, ...) through a sitecustomize hook instead of
    editing their files,
  * save the weights + a meta.json describing exactly how inputs must be prepared at inference.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

COMPAT_SITE = '''# numpy >= 1.24 removed these aliases; old research code still uses them
import warnings as _w
import numpy as _np
_w.filterwarnings("ignore", category=FutureWarning)
for _k, _v in {"long": int, "int": int, "float": float, "bool": bool, "object": object, "complex": complex}.items():
    if not hasattr(_np, _k):
        setattr(_np, _k, _v)
import matplotlib
matplotlib.use("Agg")
try:  # 2020-era code does `from biosppy import ecg`; newer biosppy keeps it in biosppy.signals
    import sys as _sys, biosppy as _b
    from biosppy.signals import ecg as _e
    # newer biosppy has a top-level `ecg` that is the SYNTHESIZER module (no hamilton_segmenter)
    if not hasattr(getattr(_b, "ecg", None), "hamilton_segmenter"):
        _b.ecg = _e
        _sys.modules["biosppy.ecg"] = _e
except Exception:
    pass
'''


def compat_env(workdir):
    """Environment for running authors' scripts in a subprocess with the numpy-alias hook."""
    d = Path(workdir) / "_compat"
    d.mkdir(parents=True, exist_ok=True)
    (d / "sitecustomize.py").write_text(COMPAT_SITE)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(d) + os.pathsep + env.get("PYTHONPATH", "")
    env["MPLBACKEND"] = "Agg"
    return env


def apply_compat():
    exec(COMPAT_SITE, {})


def run_budgeted(cmd, cwd, budget_s, log_path, env=None):
    """Run an authors' training script; stop it (SIGTERM, then kill) after budget_s seconds.
    Returns (returncode or 'timeout', seconds). stdout+stderr are teed to log_path."""
    import threading
    t0 = time.time()
    log = open(log_path, "wb")
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def pump():  # raw bytes: progress bars use '\r' without newlines for a long time
        last_echo = 0.0
        while True:
            chunk = p.stdout.read1(65536) if hasattr(p.stdout, "read1") else p.stdout.read(4096)
            if not chunk:
                break
            log.write(chunk)
            log.flush()
            if b"\n" in chunk or time.time() - last_echo > 60:      # echo sparsely to the Kaggle log
                sys.stdout.write(chunk.decode(errors="replace").split("\r")[-1])
                sys.stdout.flush()
                last_echo = time.time()

    th = threading.Thread(target=pump, daemon=True)
    th.start()
    status = None
    while p.poll() is None:
        if time.time() - t0 > budget_s:
            status = "timeout"
            print(f"\n[budget] {budget_s / 3600:.2f} h reached - stopping the authors' script", flush=True)
            p.terminate()
            try:
                p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                p.kill()
            break
        time.sleep(5)
    th.join(timeout=30)
    log.close()
    return (status or p.returncode), time.time() - t0


class BudgetLoader:
    """Wraps a DataLoader. Once the wall-clock budget is spent, every epoch yields only ONE batch,
    so the authors' epoch loop (validation, early stopping, checkpointing) still runs and ends
    quickly, and no division by an empty epoch can happen."""

    def __init__(self, loader, deadline):
        self.loader, self.deadline = loader, deadline
        self.exhausted_at_epoch = None
        self._epochs = 0

    def __iter__(self):
        self._epochs += 1
        for i, b in enumerate(self.loader):
            yield b
            if time.time() > self.deadline:
                if self.exhausted_at_epoch is None:
                    self.exhausted_at_epoch = self._epochs
                    print(f"[budget] time budget reached during epoch {self._epochs}; remaining epochs run 1 batch",
                          flush=True)
                break

    def __len__(self):
        return len(self.loader)

    @property
    def dataset(self):
        return self.loader.dataset


def detect_norm(windows):
    """How were training windows normalised? -> 'minmax_window' | 'zscore_window' | 'global'."""
    w = np.asarray(windows, float)
    w = w[: min(len(w), 2000)]
    mn, mx = np.median(w.min(1)), np.median(w.max(1))
    mu, sd = np.median(w.mean(1)), np.median(w.std(1))
    if abs(mn + 1) < 0.05 and abs(mx - 1) < 0.05:
        return "minmax_window"
    if abs(mn) < 0.05 and abs(mx - 1) < 0.05:
        return "minmax01_window"
    if abs(mu) < 0.05 and abs(sd - 1) < 0.1:
        return "zscore_window"
    return "global"


def window_stats(windows):
    w = np.asarray(windows, float)[:2000]
    return dict(n=int(len(windows)), length=int(w.shape[1]), min_median=float(np.median(w.min(1))),
                max_median=float(np.median(w.max(1))), mean_median=float(np.median(w.mean(1))),
                std_median=float(np.median(w.std(1))), norm=detect_norm(w))


def save_meta(out_dir, **meta):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print(json.dumps(meta, indent=2, default=str), flush=True)
