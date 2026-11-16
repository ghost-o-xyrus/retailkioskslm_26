"""P2E-WGAN (Vo et al., ACM SAC 2021) - repo khuongav/P2E-WGAN-ecg-ppg-reconstruction.

Recipe = the repo's own script `p2e_wgan_gp.py`, run unchanged:
  data      the authors' "sampled dataset" (MIMIC, Google Drive link in their README) in their .npy layout:
            ppg/ecg _train/_eval + ECG fiducial arrays; 375-sample windows (3 s at 125 Hz)
            Fallback if Drive refuses: the same layout built from MIMIC PERform AF (also MIMIC-III,
            125 Hz), 3-s windows min-max normalised to [-1, 1], subjects split 80/20.
  model     1-D U-Net generator (Tanh) + PatchGAN critic, WGAN-GP (lambda 10, 3 critic steps per
            generator step), sample-wise L2 x50, moving-average smoother on the output
  train     Adam 2e-4 (0.5, 0.999), batch 192, n_epochs 10,000 (open-ended), checkpoint + validation
            RMSE/Pearson every 30 epochs
The script is stopped at the time budget; the checkpoint with the lowest validation RMSE that the
script itself printed is kept (their own validation, not ours).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np

from .common import compat_env, run_budgeted, save_meta, window_stats

REPO = "https://github.com/khuongav/P2E-WGAN-ecg-ppg-reconstruction.git"
DRIVE_ID = "1lLTerHpAx0w3Xg2QxZCuI6wAxpuC0TCH"
FILES = ["ppg_train.npy", "ecg_train.npy", "ppg_eval.npy", "ecg_eval.npy",
         "ecg_opeaks_train.npy", "ecg_rpeaks_train.npy", "ecg_opeaks_eval.npy", "ecg_rpeaks_eval.npy"]
L, FS = 375, 125.0


def _fetch_drive(work):
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "gdown"], check=False)
    dl = work / "drive"
    dl.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, "-m", "gdown", DRIVE_ID, "-O", str(dl) + "/"])
    if r.returncode != 0:
        return None
    for z in list(dl.rglob("*.zip")) + list(dl.rglob("*.tar*")):
        try:
            if z.suffix == ".zip":
                zipfile.ZipFile(z).extractall(dl)
            else:
                shutil.unpack_archive(str(z), str(dl))
        except Exception as e:
            print(f"[p2e] could not unpack {z.name}: {e}", flush=True)
    hits = list(dl.rglob("ppg_train.npy"))
    if hits and all((hits[0].parent / f).exists() for f in FILES):
        return hits[0].parent
    print(f"[p2e] Drive download lacks the expected files; found {[p.name for p in dl.rglob('*')][:30]}", flush=True)
    return None


def _build_from_cache(cache_records, work):
    """Fallback: their layout from MIMIC PERform AF records (bench Records)."""
    from .. import dsp
    rng = np.random.default_rng(0)
    recs = list(cache_records)
    subj = sorted({r.subject for r in recs})
    test = set(rng.choice(subj, max(1, len(subj) // 5), replace=False))
    out = {k: [] for k in ("tr_p", "tr_e", "te_p", "te_e")}
    for r in recs:
        p = dsp.bandpass(dsp.resample(r.ppg, r.ppg_fs, FS), FS, 0.5, 8.0, order=3)
        e = dsp.bandpass(dsp.resample(r.ecg, r.ecg_fs, FS), FS, 0.5, 40.0, order=3)
        n = min(len(p), len(e)) // L
        P, E = p[: n * L].reshape(n, L), e[: n * L].reshape(n, L)
        P, E = dsp.minmax(P, axis=1), dsp.minmax(E, axis=1)
        k = "te" if r.subject in test else "tr"
        out[f"{k}_p"].append(P), out[f"{k}_e"].append(E)
    d = work / "p2e_data"
    d.mkdir(parents=True, exist_ok=True)
    for split, tag in (("train", "tr"), ("eval", "te")):
        P, E = np.concatenate(out[f"{tag}_p"]).astype(np.float32), np.concatenate(out[f"{tag}_e"]).astype(np.float32)
        np.save(d / f"ppg_{split}.npy", P), np.save(d / f"ecg_{split}.npy", E)
        rp = np.zeros_like(E)
        for i, w in enumerate(E):                      # R-peak amplitude at R-peak positions, 0 elsewhere
            idx = dsp.detect_rpeaks(w, FS) if len(w) >= FS else []
            rp[i, idx] = w[idx]
        np.save(d / f"ecg_rpeaks_{split}.npy", rp), np.save(d / f"ecg_opeaks_{split}.npy", np.zeros_like(E))
    return d, sorted(test)


def train(repo_dir, out_dir, work_dir, budget_h=4.0, smoke=False, fallback_records=None):
    repo, out, work = Path(repo_dir), Path(out_dir), Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    data, source, test_subjects = _fetch_drive(work), "authors_drive_sample", None
    if data is None:
        if fallback_records is None:
            raise RuntimeError("P2E-WGAN data: Drive download failed and no fallback records given")
        data, test_subjects = _build_from_cache(fallback_records, work)
        source = "fallback_mimic_perform_af"
    ppg_tr = np.load(data / "ppg_train.npy", mmap_mode="r")
    length = ppg_tr.shape[1]
    if smoke:  # tiny copy of the data, 2 epochs, checkpoint every epoch
        sd = work / "p2e_smoke"
        sd.mkdir(exist_ok=True)
        for f in FILES:
            np.save(sd / f, np.load(data / f, mmap_mode="r")[:400])
        data = sd
    exp = "p2e_wgan_gp_bench"
    cmd = [sys.executable, str(repo / "p2e_wgan_gp.py"), f"--experiment_name={exp}", f"--dataset_prefix={data}/",
           f"--signal_length={length}"]
    if smoke:
        cmd += ["--n_epochs=2", "--checkpoint_interval=1", "--batch_size=32"]
    status, secs = run_budgeted(cmd, cwd=str(work), budget_s=budget_h * 3600, log_path=out / "train_log.txt",
                                env=compat_env(work))
    # pick the checkpoint with the lowest validation RMSE the script printed
    log = (out / "train_log.txt").read_text(errors="replace")
    evals = [(int(e), float(r)) for e, r in re.findall(r"epoch:\s+(\d+)\s*\n\s*rmse_mean:\s*([\d.eE+-]+)", log)]
    ck = {int(p.stem.split("_")[-1]): p for p in (work / "saved_models" / exp).glob("multi_models_*.pth")}
    if not ck:
        raise RuntimeError(f"P2E-WGAN produced no checkpoint (status {status}); see {out / 'train_log.txt'}")
    scored = [(r, e) for e, r in evals if e in ck]
    best_epoch = min(scored)[1] if scored else max(ck)
    import torch
    state = torch.load(ck[best_epoch], map_location="cpu", weights_only=False)
    torch.save({"generator": state["generator_state_dict"]}, out / "weights.pth")
    save_meta(out, model="p2e_wgan", data_source=source, status=status, train_seconds=round(secs),
              best_epoch=best_epoch, val_rmse_by_epoch=evals, fs=FS, window=int(length),
              ppg_stats=window_stats(np.asarray(ppg_tr[:2000])),
              ecg_stats=window_stats(np.load(data / "ecg_train.npy", mmap_mode="r")[:2000]),
              trained_on={"mimic_perform_af": "possibly"},
              fallback_test_subjects=test_subjects, smoke=smoke)
    return out
