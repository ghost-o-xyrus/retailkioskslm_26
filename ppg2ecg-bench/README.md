# ppg2ecg-bench

A common benchmark for PPG → ECG translation models, judged on **accuracy, robustness and size**.

```
registry/      models.yaml (A)  datasets.yaml (B)  - what exists, what is runnable, who trained on what
bench/
  record.py    canonical per-subject Record (ppg, ecg, native rates, extras, meta)
  datasets/    loaders: bidmc, capnobase, dalia, wesad, aurora_bp, generic_csv, synthetic
  models/      adapters: cardiogan (TF), ppgflowecg (torch), onnx_generic, template_baseline
  runner.py    whole-record streaming inference -> continuous ECG on a common 128 Hz grid
  metrics.py   timing-free / waveform-raw / waveform-lag / morphology metrics
  perturb.py   noise, motion bursts, baseline wander, low sample rate, PPG-ECG shift, dropout, inversion
  profiler.py  params, MB, MFLOPs, latency, real-time factor, algorithmic latency floor
  aggregate.py subject-level means, bootstrap CIs, mean ranks + Friedman / Nemenyi CD,
               per-Fitzpatrick-group results (skin_tone.csv: I-II / III-IV / V-VI, gap, Kruskal-Wallis p)
scripts/
  prepare_datasets.py raw datasets -> canonical cache (+ inventory.csv with Fitzpatrick counts)
  run_benchmark.py    python scripts/run_benchmark.py <config> [--models ..] [--datasets ..] [--conditions ..]
  profile_models.py   CPU size/speed profile at a fixed thread count
  merge_results.py    merge result folders from several runs and recompute all tables
  eval_npz.py         score an existing N x L results file (e.g. your bidmc_01_cardiogan_results.npz)
kaggle/        common.py (all Kaggle stages), make_kernels.py, push_code.py, README.md = the Track-1 runbook
configs/       kaggle_track1.yaml (Track 1 on Kaggle), phase1.yaml (local), smoke_synthetic.yaml, smoke_aurora.yaml
tests/         python tests/test_pipeline.py
```

## Two tracks

| Track | What | Why |
|---|---|---|
| 1 – as released | each model with its own weights + its authors' preprocessing, tested on every dataset; every result tagged `seen` / `possibly_seen` / `unseen` from `trained_on` | "what you get if you download it today" |
| 2 – same protocol | every model with code (or a reimplementation) retrained on one open training set with fixed subject splits, exported to ONNX | the only fair architecture comparison; same ONNX path gives edge latency |

## Design rules (each one fixes something seen in the first BIDMC run)

1. **Preprocess the whole record, then window.** Per-window filtering left half the missed beats in the first 0.5 s of each window.
2. **Overlapping windows + tapered stitching** (`eval.overlap`, 0 reproduces the original protocol).
3. **Same eval filter and same R-peak detector for pred and true.**
4. **Report timing and morphology separately.** Sample-wise RMSE/Pearson punish a 30-ms beat offset as hard as a wrong waveform. `pearson_lag` (best shift) and `beat_pearson` (each beat centred on its own R peak) separate the two.
5. **Subject-level aggregation** (long DaLiA subjects don't dominate) with bootstrap CIs.
6. **Leakage tags**: CardioGAN's released weights saw all of BIDMC/CapnoBase/DaLiA/WESAD.
7. **A trivial baseline** (`template_baseline`: a fixed PQRST beat at each PPG pulse, delay calibrated on training subjects). A model that doesn't beat it isn't adding ECG information beyond heart rate.
8. **Algorithmic latency** (= window length) is reported next to compute latency.

## Running

```bash
pip install numpy scipy pandas pyyaml           # core
pip install tensorflow tensorflow-addons        # CardioGAN adapter
git clone https://github.com/pritamqu/ppg2ecg-cardiogan third_party/ppg2ecg-cardiogan
# weights: https://github.com/pritamqu/ppg2ecg-cardiogan/releases/download/model_weights/cardiogan_ppg2ecg_generator.zip
#   unzip -> weights/cardiogan/{checkpoint, ckpt-1.*}
python tests/test_pipeline.py
python scripts/run_benchmark.py configs/smoke_synthetic.yaml
python scripts/run_benchmark.py configs/phase1.yaml          # edit dataset paths first
```

FD note: `fd` uses discrete Fréchet on (sample index, amplitude) after per-window min-max. Papers differ
in how they compute FD, so compare FD only inside this benchmark, not against published numbers.
