"""Each released model's OWN preprocessing, windowing and metrics, re-implemented from the authors'
repositories, so the harness can measure how much of a model's score is the model and how much is
the pipeline around it.

  CardioGAN  (pritamqu/ppg2ecg-cardiogan, codes/test_cardiogan.py + preprocessing.py)
      PPG: linear resample to 128 Hz, biosppy Butterworth order 4, 1-8 Hz (zero-phase)
      ECG reference: biosppy FIR order 0.3*fs, 3-45 Hz
      4-s non-overlapping windows, min-max [-1, 1] per window (both signals)
  RDDM       (DebadityaQU/RDDM, data.py + std_eval.py + metrics.py)
      4-s windows, min-max [-1, 1] per window, THEN per-window neurokit2 ppg_clean (Elgendi) for PPG
      and ecg_clean(method='pantompkins1985', a 5-15 Hz band) for the ECG reference
  PPGFlowECG (PKUDigitalHealth/PPGFlowECG, data_process_to_npz/step1.py + step2.py,
              evaluation/calculate_metric.py)
      at the native rate: PPG MNE-IIR Butterworth order 3 0.5-8 Hz; ECG Butterworth order 5 high-pass
      0.5 Hz + 50 Hz notch; resample_poly to 128 Hz; 10-s windows; Savitzky-Golay (7,2) PPG / (11,2) ECG;
      z-score per window. (The authors' signal-quality rejection is reported as a separate flag:
      we keep every window and count how many their flatness rule would drop.)

Metrics (shared lineage: CardioGAN -> RDDM -> PPGFlowECG):
  rmse / mae            on the normalised windows
  fd_fid                "FD" = Frechet distance between Gaussians fitted to the SET of real and of
                        generated windows (a distribution distance, like FID on raw samples) - NOT the
                        per-pair curve Frechet distance used in our harness
  hr_mae                per window: biosppy Hamilton R peaks on the real ECG; generated ECG cleaned with
                        neurokit2 pantompkins then Hamilton; heart rate = mean of biosppy smoothed HR

Requires biosppy and neurokit2 (installed by the k80 job); everything else is numpy/scipy.
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sps
from scipy.linalg import sqrtm

from . import dsp

FS = 128.0


def _deps():
    try:
        import neurokit2 as nk
        from biosppy.signals import ecg as becg
        from biosppy.signals import tools as btools
    except ImportError as e:  # pragma: no cover
        raise ImportError("author pipelines need `pip install biosppy neurokit2`") from e
    return nk, becg, btools


def _windows(x, L):
    n = len(x) // L
    return np.asarray(x[: n * L], float).reshape(n, L)


def _linear_resample(x, fs_in, fs_out):
    return dsp.resample(x, fs_in, fs_out, method="linear")


# ------------------------------------------------------------------ preprocessing
def prep_cardiogan(rec):
    _, _, bt = _deps()
    ppg = _linear_resample(rec.ppg, rec.ppg_fs, FS)
    ecg = _linear_resample(rec.ecg, rec.ecg_fs, FS)
    n = min(len(ppg), len(ecg))
    ppg = bt.filter_signal(signal=ppg[:n], ftype="butter", band="bandpass", order=4, frequency=[1, 8], sampling_rate=FS)[0]
    ecg = bt.filter_signal(signal=ecg[:n], ftype="FIR", band="bandpass", order=int(0.3 * FS), frequency=[3, 45],
                           sampling_rate=FS)[0]
    L = int(4 * FS)
    return dsp.minmax(_windows(ppg, L), axis=1), dsp.minmax(_windows(ecg, L), axis=1), {}


def prep_rddm(rec):
    nk, _, _ = _deps()
    ppg = dsp.resample(rec.ppg, rec.ppg_fs, FS)
    ecg = dsp.resample(rec.ecg, rec.ecg_fs, FS)
    n = min(len(ppg), len(ecg))
    L = int(4 * FS)
    P = dsp.minmax(_windows(ppg[:n], L), axis=1)
    E = dsp.minmax(_windows(ecg[:n], L), axis=1)
    P = np.stack([nk.ppg_clean(w, sampling_rate=int(FS)) for w in P])
    E = np.stack([nk.ecg_clean(w, sampling_rate=int(FS), method="pantompkins1985") for w in E])
    return P, E, {}


def _flat_ratio(w, win=13, thr=0.001):
    d = np.abs(np.diff(w))
    rate = np.convolve(d, np.ones(win - 1) / (win - 1), mode="valid")
    return float(np.mean(rate < thr))


def prep_ppgflowecg(rec):
    def bw(x, fs, lo=None, hi=None, order=3):
        if lo and hi:
            b, a = sps.butter(order, [lo, hi], btype="band", fs=fs)
        elif lo:
            b, a = sps.butter(order, lo, btype="high", fs=fs)
        else:
            b, a = sps.butter(order, hi, btype="low", fs=fs)
        return sps.filtfilt(b, a, x)
    ppg = bw(np.asarray(rec.ppg, float), rec.ppg_fs, 0.5, min(8.0, 0.45 * rec.ppg_fs), order=3)
    ecg = bw(np.asarray(rec.ecg, float), rec.ecg_fs, lo=0.5, order=5)
    if rec.ecg_fs > 110:
        b, a = sps.iirnotch(50.0, Q=50.0, fs=rec.ecg_fs)
        ecg = sps.filtfilt(b, a, ecg)
    ppg, ecg = dsp.resample(ppg, rec.ppg_fs, FS), dsp.resample(ecg, rec.ecg_fs, FS)
    n = min(len(ppg), len(ecg))
    L = int(10 * FS)
    P, E = _windows(ppg[:n], L), _windows(ecg[:n], L)
    if len(P) == 0:
        return P, E, {}
    P = sps.savgol_filter(P, 7, 2, axis=1)
    E = sps.savgol_filter(E, 11, 2, axis=1)
    z = lambda X: (X - X.mean(1, keepdims=True)) / (X.std(1, keepdims=True) + 1e-8)
    P, E = z(P), z(E)
    flat = np.array([max(_flat_ratio(p), _flat_ratio(e)) for p, e in zip(P, E)])
    return P, E, {"n_would_drop_flat": int((flat > 0.25).sum())}


PREP = {"cardiogan": prep_cardiogan, "rddm": prep_rddm, "ppgflowecg": prep_ppgflowecg}
METRIC_FAMILY = {"cardiogan": "rddm", "rddm": "rddm", "ppgflowecg": "ppgflowecg"}


# ------------------------------------------------------------------ metrics
def fd_fid_rddm(real, fake):
    """RDDM metrics.calculate_FD: Gaussian Frechet distance over the set of windows (eigvals form)."""
    mu1, mu2 = real.mean(0), fake.mean(0)
    s1, s2 = np.cov(real, rowvar=False), np.cov(fake, rowvar=False)
    tr = np.sum(np.sqrt(np.linalg.eigvals(s1 @ s2).astype("complex128")).real)
    return float((mu1 - mu2) @ (mu1 - mu2) + np.trace(s1) + np.trace(s2) - 2 * tr)


def fd_fid_ppgflowecg(real, fake, eps=1e-6, small_pca=32, small_eps=1e-4, n_trials=5):
    """PPGFlowECG calculate_fd (>= 3000 windows) or calculate_fd_for_small_sample (PCA 32, 5 trials)."""
    if len(real) >= 3000:
        A, B, e = real, fake, eps
        reps = [(A, B)]
    else:
        from sklearn.decomposition import PCA
        e = small_eps
        reps = []
        for t in range(n_trials):
            Z = PCA(n_components=min(small_pca, len(real) - 1), random_state=t).fit_transform(np.r_[real, fake])
            reps.append((Z[: len(real)], Z[len(real):]))
    out = []
    for A, B in reps:
        c1 = np.cov(A, rowvar=False) + e * np.eye(A.shape[1])
        c2 = np.cov(B, rowvar=False) + e * np.eye(A.shape[1])
        cm = sqrtm(c1 @ c2)
        cm = cm.real if np.iscomplexobj(cm) else cm
        out.append(float(np.sum((A.mean(0) - B.mean(0)) ** 2) + np.trace(c1) + np.trace(c2) - 2 * np.trace(cm)))
    return float(np.mean(out))


def _bpm(w, clean, nk, becg, btools):
    try:
        if clean:
            w = nk.ecg_clean(w, sampling_rate=int(FS), method="pantompkins1985")
        r, = becg.hamilton_segmenter(signal=w, sampling_rate=FS)
        r, = becg.correct_rpeaks(signal=w, rpeaks=r, sampling_rate=FS, tol=0.05)
        _, r = becg.extract_heartbeats(signal=w, rpeaks=r, sampling_rate=FS, before=0.2, after=0.4)
        if len(r) < 2:
            return -1.0
        _, hr = btools.get_heart_rate(beats=r, sampling_rate=FS, smooth=True, size=3)
        return float(np.mean(hr)) if len(hr) else -1.0
    except Exception:
        return -1.0


def hr_mae(real, fake):
    nk, becg, btools = _deps()
    rb = np.array([_bpm(w, False, nk, becg, btools) for w in real])
    fb = np.array([_bpm(w, True, nk, becg, btools) for w in fake])
    ok = (fb != -1) & (rb != -1) & np.isfinite(fb) & np.isfinite(rb)
    return float(np.mean(np.abs(rb[ok] - fb[ok]))) if ok.any() else np.nan, int(ok.sum()), len(real)


def author_metrics(model, real, fake):
    fam = METRIC_FAMILY[model]
    out = dict(rmse=float(np.sqrt(np.mean((fake - real) ** 2))), mae=float(np.mean(np.abs(fake - real))))
    out["fd_fid"] = fd_fid_rddm(real, fake) if fam == "rddm" else fd_fid_ppgflowecg(real, fake)
    out["hr_mae"], out["hr_n_valid"], out["n_windows"] = hr_mae(real, fake)
    return out
