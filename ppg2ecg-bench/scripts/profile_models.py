"""Size / speed profile of the models in a config, on CPU with a fixed thread count.

    python scripts/profile_models.py configs/kaggle_track1.yaml --threads 1 --out results/profile_t1.csv

One process per thread count (thread pools are fixed at framework import), GPU hidden.
1 thread ~ a single big core on a phone / Raspberry Pi 5; 4 threads ~ a whole Pi / laptop.
These are PROXY numbers - real edge latency comes from running the exported ONNX/TFLite
model on the device itself (planned after Track 1).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--models", nargs="*")
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    t = str(a.threads)
    os.environ.update(CUDA_VISIBLE_DEVICES="", OMP_NUM_THREADS=t, MKL_NUM_THREADS=t, OPENBLAS_NUM_THREADS=t,
                      TF_NUM_INTRAOP_THREADS=t, TF_NUM_INTEROP_THREADS="1")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import pandas as pd
    import yaml
    from bench import profiler
    from bench.models import build

    cfg = yaml.safe_load(open(a.config))
    rows = []
    for m in cfg["models"]:
        if a.models and m["name"] not in a.models and m.get("label") not in a.models:
            continue
        kw = dict(m.get("kwargs", {}))
        if "device" in kw:
            kw["device"] = "cpu"
        ad = build(m["name"], **kw)
        if m.get("label"):
            ad.name = m["label"]
        ad.load()
        try:
            import torch
            torch.set_num_threads(a.threads)
        except ImportError:
            pass
        r = profiler.profile(ad, n_warmup=3, n_runs=a.runs)
        r["threads"] = a.threads
        rows.append(r)
        print(r, flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out, index=False)


if __name__ == "__main__":
    main()
