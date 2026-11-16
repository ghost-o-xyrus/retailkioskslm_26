"""Yalcin & Latoschik (Front. Physiol. 2026) "End-to-end non-invasive ECG signal generation from PPG
signal: a self-supervised learning approach" - official repo m1237/self-supervised-ppg-to-ecg.

The official repo ships its training as code/train.py (models, preprocessing helpers, datasets,
train_ssl_pretraining, train_wgan_gp, transfer_pretrained_discriminator_backbone, loso_split) and the
six ECG transformations as code/self_supervised_transformation (a Python file without the .py
extension). Its main() is a demo on random arrays and never saves a model, so this wrapper feeds real
data through the same functions, in the same order, and saves the generator.

  data      paper: MIMIC-III and Who-is-Alyx. Here: MIMIC PERform AF (an open MIMIC-III subset).
            Their data.py works at 128 Hz with 4 s windows; train.py's helpers: cubic resampling,
            ECG FIR 0.5-45 Hz (401 taps, zero-phase), PPG Butterworth 0.5-8 Hz order 4 (zero-phase),
            windows with 20% overlap, min-max to [-1, 1] (applied per window, as at inference)
  split     their main(): loso_split (one held-out subject), 10% of the remaining windows for validation
  model     ModelConfig defaults (UNet + Transformer generator; CNN + Transformer critic with CLS token)
  train     1) self-supervised pretraining of the critic on the six transformations (labels generated
               once per window with their apply_transformation, as their README describes)
            2) WGAN-GP (n_critic 5, lambda_gp 10), backbone transferred and frozen, early stopping
               (patience 12) on validation L1, best generator kept
            ModelConfig defaults batch 128, 90 + 90 epochs; capped here by the wall-clock budget.
Upstream bug handled: their transformation labels are 1..6 (0 = "original" is excluded) but the SSL
head has 6 outputs, so labels are shifted to 0..5.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import random
import sys
import time
from pathlib import Path

import numpy as np

from .common import BudgetLoader, apply_compat, save_meta, window_stats

REPO = "https://github.com/m1237/self-supervised-ppg-to-ecg.git"
FS, WIN_S, OVERLAP = 128, 4.0, 0.2


def _import(path, name):
    """Import a Python source file, also one without the .py extension."""
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


def load_modules(repo_dir):
    code = Path(repo_dir) / "code"
    yt = _import(code / "train.py", "yalcin_train")
    tr = code / "self_supervised_transformation"
    if not tr.exists():
        tr = code / "self_supervised_transformation.py"
    ssl = _import(tr, "yalcin_ssl")
    return yt, ssl


def segments_from_records(records, yt, sampling_rate=FS, window_seconds=WIN_S, overlap_ratio=OVERLAP):
    """-> ppg (N,T), ecg (N,T), subject_ids (N,), each window min-max normalised to [-1, 1]."""
    W = int(round(window_seconds * sampling_rate))
    P, E, S = [], [], []
    for r in records:
        ecg = yt.resample_signal_cubic(np.asarray(r.ecg, float), float(r.ecg_fs), float(sampling_rate))
        ppg = yt.resample_signal_cubic(np.asarray(r.ppg, float), float(r.ppg_fs), float(sampling_rate))
        n = min(len(ecg), len(ppg))
        if n < max(W, 1204):                     # filtfilt with 401 taps needs > 3 * 401 samples
            continue
        ecg = yt.fir_bandpass_ecg(ecg[:n], sampling_rate)
        ppg = yt.butter_bandpass_ppg(ppg[:n], sampling_rate)
        ew = yt.segment_with_overlap(ecg, W, overlap_ratio)
        pw = yt.segment_with_overlap(ppg, W, overlap_ratio)
        ok = (np.ptp(ew, axis=1) > 1e-8) & (np.ptp(pw, axis=1) > 1e-8)
        ew, pw = ew[ok], pw[ok]
        if not len(ew):
            continue
        norm = lambda w: np.stack([yt.minmax_normalize_minus1_1(x)[0] for x in w]).astype(np.float32)
        P.append(norm(pw)), E.append(norm(ew)), S.extend([str(r.subject)] * len(ew))
    if not P:
        raise SystemExit("[yalcin] no usable windows in the training records")
    return np.concatenate(P), np.concatenate(E), np.asarray(S)


def ssl_arrays(ecg, ssl, seed):
    """One transformed copy per window with their apply_transformation; labels shifted to 0..5."""
    random.seed(seed), np.random.seed(seed)
    names = [n for n in ssl.TRANSFORMATION_LABELS if n != "original"]
    lab0 = min(ssl.TRANSFORMATION_LABELS[n] for n in names)
    X, Y = [], []
    for x in ecg:
        name = random.choice(names)
        y, _ = ssl.apply_transformation(x, name)
        X.append(np.asarray(y, np.float32)), Y.append(ssl.TRANSFORMATION_LABELS[name] - lab0)
    return np.stack(X), np.asarray(Y, np.int64)


def train(repo_dir, records, out_dir, budget_h=4.5, ssl_share=0.33, smoke=False, seed=42):
    apply_compat()
    import torch
    from torch.utils.data import DataLoader
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    yt, ssl = load_modules(repo_dir)                       # both set seed 42 on import
    yt.set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        # WGAN-GP differentiates the critic's gradient (double backward). On CUDA, nn.MultiheadAttention
        # picks the flash / memory-efficient attention kernels, which have no double backward
        # ("derivative for aten::_scaled_dot_product_efficient_attention_backward is not implemented").
        # The plain math kernel - the one the CPU smoke test used - supports it.
        torch.backends.cuda.enable_flash_sdp(False)
        torch.backends.cuda.enable_mem_efficient_sdp(False)
        torch.backends.cuda.enable_math_sdp(True)
        if hasattr(torch.backends.cuda, "enable_cudnn_sdp"):
            torch.backends.cuda.enable_cudnn_sdp(False)
    ppg, ecg, sid = segments_from_records(records, yt)
    if smoke:   # 4 subjects x 75 windows (a plain [:300] would keep only the first subject)
        keep = np.concatenate([np.flatnonzero(sid == s)[:75] for s in np.unique(sid)[:4]])
        ppg, ecg, sid = ppg[keep], ecg[keep], sid[keep]
    kw = dict(sampling_rate=FS, device=device)
    if smoke:
        kw.update(batch_size=8, epochs_pretrain=1, epochs_gan=1)
    cfg = yt.ModelConfig(**kw)

    # their main(): LOSO with the first subject held out, 10% of the rest (random windows) for validation
    held_out = sid[0]
    train_idx, test_idx = yt.loso_split(sid, held_out)
    perm = np.random.RandomState(seed).permutation(train_idx)
    n_val = max(1, int(0.1 * len(train_idx)))
    va, tr = perm[:n_val], perm[n_val:]
    if len(tr) < cfg.batch_size:                           # drop_last=True would leave no batch at all
        cfg.batch_size = max(2, len(tr) // 2)
    print(f"[yalcin] windows train {len(tr)} val {len(va)} test {len(test_idx)}; subjects {len(np.unique(sid))}; "
          f"batch {cfg.batch_size}; device {device}", flush=True)

    t0, total = time.time(), budget_h * 3600
    xs, ys = ssl_arrays(ecg[tr], ssl, seed)
    xv, yv = ssl_arrays(ecg[va], ssl, seed + 1)
    ssl_loader = BudgetLoader(DataLoader(yt.SSLTransformationDataset(xs, ys), batch_size=cfg.batch_size, shuffle=True),
                              t0 + ssl_share * total)
    ssl_val = DataLoader(yt.SSLTransformationDataset(xv, yv), batch_size=cfg.batch_size, shuffle=False)
    pre = yt.train_ssl_pretraining(yt.ECGTransformerDiscriminator(cfg), ssl_loader, ssl_val, cfg)
    t_ssl = time.time() - t0

    gen, disc = yt.PPGtoECGGenerator(cfg), yt.ECGTransformerDiscriminator(cfg)
    disc = yt.transfer_pretrained_discriminator_backbone(pre, disc, freeze_backbone=True)
    gan_loader = BudgetLoader(DataLoader(yt.PairedPPGECGDataset(ppg[tr], ecg[tr]), batch_size=cfg.batch_size,
                                         shuffle=True, drop_last=True), t0 + total)
    val_loader = DataLoader(yt.PairedPPGECGDataset(ppg[va], ecg[va]), batch_size=cfg.batch_size, shuffle=False)
    gen, disc, hist = yt.train_wgan_gp(gen, disc, gan_loader, val_loader, cfg)
    torch.save({"generator": gen.state_dict()}, out / "weights.pth")
    cfg_d = {k: getattr(cfg, k) for k in cfg.__dataclass_fields__ if k != "device"}
    save_meta(out, model="yalcin2026", train_seconds=round(time.time() - t0), ssl_seconds=round(t_ssl),
              ssl_budget_hit_epoch=ssl_loader.exhausted_at_epoch, gan_budget_hit_epoch=gan_loader.exhausted_at_epoch,
              fs=float(FS), window=int(WIN_S * FS), norm="minmax_window", model_config=cfg_d,
              val_l1=hist.get("val_l1"), held_out_subjects=[str(held_out)],
              ppg_stats=window_stats(ppg), ecg_stats=window_stats(ecg),
              trained_on={"mimic_perform_af": "possibly"}, smoke=smoke)
    return out
