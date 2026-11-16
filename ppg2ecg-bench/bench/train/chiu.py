"""Chiu, Shuai & Chao (IEEE Sensors J. 2020) "Reconstructing QRS Complex From PPG by Transformed
Attentional Neural Networks" - repo james77777778/ppg2ecg-pytorch (authors' weights were lost).

Recipe = the repo's own `train.py --flagfile config/BIDMC.cfg`, run unchanged:
  data      the authors' released preprocessed BIDMC windows (dataset.zip, GitHub release), their
            train/test split; 512-sample windows at 125 Hz, random 256-sample crops (+-64 shift aug)
  model     PPG2ECG(input_size=256, conv + STN + attention), Tanh output
  loss      QRS-enhanced L1 (note: the repo hard-codes beta=5 inside QRSLoss), Adam 1e-4, batch 256,
            300 epochs, best checkpoint by test QRS-L1 (their selection rule)
BIDMC is used (not their main UQ Vital Signs set) because BIDMC is in the Track 1 evaluation; the
UQVIT config can be trained the same way with --config UQVIT.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

from .common import compat_env, run_budgeted, save_meta, window_stats

REPO = "https://github.com/james77777778/ppg2ecg-pytorch.git"
DATA_URLS = ["https://github.com/james77777778/ppg2ecg-pytorch/releases/download/dataset/dataset.zip"]
DATA_DRIVE_ID = "1UwuHRKkC0YPbDAFIYvFJlFmU6_3zgjcJ"
CONFIG_FS = {"BIDMC": (125.0, 256), "UQVIT": (100.0, 200)}


def _download(work):
    z = work / "dataset.zip"
    for u in DATA_URLS:
        r = subprocess.run(["curl", "-L", "--fail", "--retry", "2", "-o", str(z), u])
        if r.returncode == 0 and z.stat().st_size > 1e6:
            return z
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gdown"], check=True)
    subprocess.run([sys.executable, "-m", "gdown", DATA_DRIVE_ID, "-O", str(z)], check=True)
    return z


def train(repo_dir, out_dir, work_dir, budget_h=2.0, smoke=False, config="BIDMC"):
    repo, out, work = Path(repo_dir), Path(out_dir), Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    data = work / "data"
    if not (data / "bidmc").exists():
        with zipfile.ZipFile(_download(work)) as zf:
            zf.extractall(data)
        # tolerate an extra top-level folder inside the zip
        inner = [p for p in data.iterdir() if p.is_dir() and (p / "bidmc").exists()]
        if inner:
            for sub in inner[0].iterdir():
                shutil.move(str(sub), data / sub.name)
    split = "bidmc/bidmc-filtered" if config == "BIDMC" else "uqvitalsigns/uqvitalsignsdata"
    tr = sorted((data / f"{split}-train").glob("*.npy"))
    if not tr:
        raise FileNotFoundError(f"no training windows under {data / (split + '-train')} ; zip layout: "
                                f"{[str(p.relative_to(data)) for p in data.rglob('*')][:20]}")
    pairs = np.stack([np.load(p) for p in tr[:2000]])
    flags = ["--flagfile", str(repo / "config" / f"{config}.cfg"), f"--logdir={work / 'logs'}", f"--run_name={config}"]
    if smoke:
        flags += ["--epoch=1", "--eval_step=1", "--save_step=1"]
    t0 = time.time()
    status, secs = run_budgeted([sys.executable, str(repo / "train.py"), *flags], cwd=str(work),
                                budget_s=budget_h * 3600, log_path=out / "train_log.txt", env=compat_env(work))
    mdir = work / "logs" / config / "model"
    best = mdir / "model_best.pth"
    if not best.exists():
        cands = sorted(mdir.glob("model_*.pth"), key=lambda p: int(p.stem.split("_")[1]) if p.stem.split("_")[1].isdigit() else -1)
        if not cands:
            raise RuntimeError(f"Chiu training produced no checkpoint (status {status}); see {out / 'train_log.txt'}")
        best = cands[-1]
    shutil.copy(best, out / "weights.pth")
    fs, L = CONFIG_FS[config]
    save_meta(out, model="chiu2020", config=config, status=status, train_seconds=round(secs),
              checkpoint=best.name, fs=fs, window=L, input_size=L, use_stn=True, use_attention=True,
              ppg_stats=window_stats(pairs[:, 0]), ecg_stats=window_stats(pairs[:, 1]),
              trained_on={"bidmc": "possibly"} if config == "BIDMC" else {}, smoke=smoke,
              n_train_files=len(tr), n_test_files=len(list((data / f"{split}-test").glob("*.npy"))))
    return out
