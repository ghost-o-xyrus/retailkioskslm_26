"""CLEP-GAN (Mathematics-Analytics-Data-Science-Lab/CLEP-GAN, BMC Bioinformatics 2025 / arXiv 2502.17536).

Recipe = the repo's own code:
  data      data_processing.py on the BIDMC CSVs with the authors' per-subject noise intervals and
            sync settings (preprocessing_config.yaml): ECG detrend + Butterworth 0.4-45 Hz order 6,
            PPG detrend + 0.3-8 Hz order 3, 128-sample segments each min-max normalised to [-1, 1];
            then their __main__ assembly: 32 subjects, test = 07, 16, 22, 42; 4 consecutive
            segments joined into 512-sample windows with a 2-segment stride (utils.overlap)
  model     two attention U-Nets (PPG and ECG) + time- and frequency-domain discriminators, CLIP-style
            contrastive loss between the PPG and ECG latents, QRS-weighted L1 (beta 0.5)
  train     Adam 1e-4, batch 128, 200 epochs, final epoch kept (their test() uses epoch 199)
Imported from the repo unchanged. Two necessities: the Trainer reads a module-level `device`
(defined only under `__main__` in their file) which we set, and per-item R-peak detection
(biosppy) in their Dataset is cached because it is deterministic (speed only).
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml

from .common import BudgetLoader, apply_compat, save_meta, window_stats

REPO = "https://github.com/Mathematics-Analytics-Data-Science-Lab/CLEP-GAN.git"
IDS = (['07', '08', '09', '16', '22', '30', '34', '37', '42', '43', '50', '51']
       + ['01', '02', '05', '11', '18', '19', '20', '21', '24', '29', '46']
       + ['12', '14', '17', '27', '35', '38', '40', '47', '48'])
TEST_IDS = ['07', '16', '22', '42']
SEG = 128


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def prepare(repo, bidmc_csv_dir, work):
    cfg = yaml.safe_load(open(repo / "preprocessing_config.yaml"))
    cfg["global_settings"]["data_dir"] = str(bidmc_csv_dir)
    cfg["global_settings"]["out_root"] = str(work / "processed")
    cfg_path = work / "preprocessing_config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    if not (work / "processed" / TEST_IDS[0]).exists():
        from .common import compat_env
        subprocess.run([sys.executable, str(repo / "data_processing.py"), "--config", str(cfg_path)],
                       cwd=str(repo), env=compat_env(work), check=True)
    return work / "processed"


def train(repo_dir, bidmc_csv_dir, out_dir, work_dir, budget_h=5.0, smoke=False, epochs=200, batch_size=128):
    apply_compat()
    import torch
    from torch.utils.data import BatchSampler, DataLoader, RandomSampler
    repo, out, work = Path(repo_dir), Path(out_dir), Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    proc = prepare(repo, Path(bidmc_csv_dir), work)
    sys.path.insert(0, str(repo))
    utils = _load_module(repo / "utils.py", "utils")
    unet = _load_module(repo / "unet.py", "unet")
    clep = _load_module(repo / "CLEP-GAN.py", "clep_gan_main")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    clep.device = device                                  # their Trainer reads a module-level `device`

    # ---- their __main__ data assembly (verbatim logic)
    X_train, Y_train, Tr_l, X_test, Y_test, Te_l = [], [], [], [], [], []
    for sid in IDS:
        d = proc / sid / f"seg{SEG}"
        if not (d / "real_ppg.npy").exists():
            print(f"[clep] subject {sid}: not produced by data_processing.py - skipped", flush=True)
            continue
        X_ = np.load(d / "real_ppg.npy", allow_pickle=True)
        Y_ = np.load(d / "real_ecg.npy", allow_pickle=True)
        lab = np.load(d / "labels.npy", allow_pickle=True)   # their __main__ reads labels_real.npy, which
        (X_test if sid in TEST_IDS else X_train).extend(X_)  # data_processing.py writes as labels.npy
        (Y_test if sid in TEST_IDS else Y_train).extend(Y_)
        (Te_l if sid in TEST_IDS else Tr_l).extend(lab)

    def assemble(X, Y, L):
        xs, ys, ls = [], [], []
        for i in range(len(X)):
            Xi, Yi = np.asarray(X[i], dtype=np.float32), np.asarray(Y[i], dtype=np.float32)  # saved as object arrays
            n = int(len(Xi) / 2) * 2
            xo, yo = utils.overlap(Xi[:n], Yi[:n])
            xs.extend(xo), ys.extend(yo), ls.extend(np.asarray(L[i])[:int(n / 2) - 1])
        return np.asarray(xs, dtype=np.float32), np.asarray(ys, dtype=np.float32), np.asarray(ls)

    x_tr, y_tr, l_tr = assemble(X_train, Y_train, Tr_l)
    x_te, y_te, l_te = assemble(X_test, Y_test, Te_l)
    if smoke:
        x_tr, y_tr, l_tr = x_tr[:512], y_tr[:512], l_tr[:512]
        x_te, y_te, l_te = x_te[:128], y_te[:128], l_te[:128]
        epochs = 1
    print(f"[clep] train windows {x_tr.shape}, test windows {x_te.shape}", flush=True)

    class Cached(utils.ECGDataset):            # deterministic per item -> memoise (speed only)
        _cache = {}

        def __getitem__(self, idx):
            if idx not in self._cache:
                self._cache[idx] = super().__getitem__(idx)
            return self._cache[idx]

    tr_ds = Cached(torch.from_numpy(x_tr).float(), torch.from_numpy(y_tr).float(), l_tr)
    te_ds = Cached(torch.from_numpy(x_te).float(), torch.from_numpy(y_te).float(), l_te)
    te_ds._cache = {}
    train_loader = DataLoader(tr_ds, batch_sampler=BatchSampler(RandomSampler(tr_ds), batch_size=batch_size,
                                                                drop_last=True))
    test_loader = DataLoader(te_ds, batch_size=batch_size, shuffle=False)
    deadline = time.time() + budget_h * 3600
    budget_loader = BudgetLoader(train_loader, deadline)

    class Args:
        pass
    args = Args()
    args.batch_size, args.num_epochs = batch_size, epochs
    args.chk_pth = str(work / "ckpt") + "/"
    Path(args.chk_pth).mkdir(parents=True, exist_ok=True)
    fs_, ks_ = [64, 128, 256, 512, 512, 512], [31] * 6
    GP = unet.generator_atten_unet(device, input_channel=1, filter_size=fs_, kernel_size=ks_, norm=False)
    GE = unet.generator_atten_unet(device, input_channel=1, filter_size=fs_, kernel_size=ks_, norm=False)
    trainer = clep.Trainer(device, budget_loader, next(iter(test_loader)), args, generator_ppg=GP, generator_ecg=GE,
                           discriminator_ecg_time=unet.TimeDomainDiscriminator(),
                           discriminator_ecg_freq=unet.FrequencyDomainDiscriminator(),
                           discriminator_ppg_time=unet.TimeDomainDiscriminator(),
                           discriminator_ppg_freq=unet.FrequencyDomainDiscriminator(), gene_loss=utils.smoothl1_loss)
    t0 = time.time()
    trainer.run(test_loader)
    torch.save({"GP": trainer.netGP.state_dict(), "GE": trainer.netGE.state_dict()}, out / "weights.pth")
    save_meta(out, model="clep_gan", train_seconds=round(time.time() - t0), epochs=epochs,
              budget_hit_epoch=budget_loader.exhausted_at_epoch, fs=125.0, window=512, segment=SEG,
              norm="minmax_per_128_segment", filter_size=fs_, kernel_size=ks_,
              ppg_stats=window_stats(x_tr), ecg_stats=window_stats(y_tr), train_subjects=sorted(set(IDS) - set(TEST_IDS)),
              test_subjects=TEST_IDS, trained_on={"bidmc": "possibly"}, smoke=smoke,
              test_ge_errors=[float(e) for e in trainer.test_ge_errors])
    shutil.copy(work / "preprocessing_config.yaml", out / "preprocessing_config.yaml")
    return out
