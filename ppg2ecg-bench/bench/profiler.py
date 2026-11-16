"""Size / speed profiling (the 'size' axis).

Reports, per model and per machine:
  params, weights_mb, mflops_per_s_ecg   - static cost
  latency_ms (mean / p50 / p95)          - one window, batch 1, after warm-up
  rtf                                    - latency / window duration (<1 = faster than real time)
  algorithmic_latency_s                  - minimum delay before the first output: the window length.
                                           A 64-s-window model cannot answer in under 64 s,
                                           however fast it computes.
  peak_rss_mb                            - process peak resident memory after the runs
Run the same script on laptop, Raspberry Pi, Jetson, phone (via ONNX) to fill the edge table.
"""
from __future__ import annotations

import platform
import time

try:  # Unix only; Windows has no `resource` module
    import resource
except ImportError:
    resource = None

import numpy as np

from .models.base import ModelAdapter


def _peak_rss_mb():
    if resource is not None:
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    try:
        import psutil
        return psutil.Process().memory_info().peak_wset / 1e6  # Windows
    except Exception:
        return None


def profile(adapter: ModelAdapter, n_warmup: int = 5, n_runs: int = 50, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    L = adapter.window_len
    t = np.arange(L) / adapter.native_fs
    x = np.sin(2 * np.pi * 1.2 * t)[None, :] + 0.05 * rng.standard_normal((1, L))
    x = adapter.normalize_window(adapter.prepare_record(x[0])[None, :])
    for _ in range(n_warmup):
        adapter.infer(x)
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        adapter.infer(x)
        times.append(time.perf_counter() - t0)
    times = np.asarray(times) * 1000
    flops = adapter.flops_per_window()
    wb = adapter.weights_bytes()
    lat = float(np.mean(times))
    return dict(
        model=adapter.name,
        machine=f"{platform.node()} | {platform.machine()} | {platform.processor() or platform.system()}",
        framework=adapter.framework,
        params=adapter.n_params(),
        weights_mb=None if wb is None else wb / 1e6,
        mflops_per_s_ecg=None if flops is None else flops / 1e6 / adapter.window_s,
        window_s=adapter.window_s,
        algorithmic_latency_s=adapter.window_s,
        latency_ms_mean=lat,
        latency_ms_p50=float(np.percentile(times, 50)),
        latency_ms_p95=float(np.percentile(times, 95)),
        rtf=lat / 1000.0 / adapter.window_s,
        peak_rss_mb=_peak_rss_mb(),
    )
