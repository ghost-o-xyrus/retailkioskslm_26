# Reproducing the evaluation

The kiosk itself needs only `setup.bat`. This page is for rerunning the measurements behind the reports.

Every run in the project was started from a **plan file** (`harness/plans/*.json`, `finetune/plans/*.json`): the
models, settings, case files and output folder of each run are written there, so a run is one command. The
step-by-step record, with the reason for each run, is in [`harness/README.md`](../harness/README.md).

## Before you start

```powershell
setup.bat                                   # llama.cpp, models, retrieval models, .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt         # scoring, retrieval benchmarks, figures
$env:SLM_BASE_DIR = "$PWD\runtime"          # where setup.bat put llama-cpu\, llama-vulkan\, models\
```

`SLM_BASE_DIR` tells the harness where llama.cpp and the model files are. Without it, plans look in the folder
above the repository, which is how the project was laid out on the test laptop. Only the two deployed model files
are downloaded by `setup.bat`; Objective 1 compared six models, and its plans name the other files
(`harness/plans/stage1_screen.json`), which you download from their Hugging Face pages into `runtime\models\`.

Check everything without a model first:

```powershell
python -m unittest discover -s . -p "test_*.py"      # 95 tests, about 2 minutes, no model needed
python harness\run_plan.py harness\plans\obj3_step14.json --dry-run     # prints every command a plan would run
```

## The runs, by objective

| Objective | What | Command | Results go to |
|---|---|---|---|
| 1 | Screening, number format, head-to-head, speed | `python harness\run_plan.py harness\plans\stage1_screen.json` (then `stage2_quant`, `stage3_head_to_head`, `stage4_speed`) | `results/` |
| 1 | Scores | `python eval\score.py` | `results/_scores/` |
| 2 | Retrieval benchmark | `python retrieval\bench_retrieval.py --configs all` | `results_retrieval/` |
| 2 | Fallback calibration | `python retrieval\calibrate_fallback.py` | `results_retrieval/fallback/` |
| 2 | Model with retrieval, confirming run | `python harness\run_plan.py harness\plans\obj2_step8_core.json` (and `_secondary`, `_speed`) | `results_obj2/` |
| 3 | Each of the thirteen changes | `python harness\run_plan.py harness\plans\obj3_step<N>.json` | `results_obj3/` |
| 3 | Confirming run on the test set | `python harness\run_plan.py harness\plans\obj3_step14.json` then `python eval\step14_verdicts.py` | `results_obj3/_step14/` |
| 3 | One part removed at a time | plans in `harness/plans/obj3_step15/` then `python eval\step15_ladder.py` | `results_obj3/_step15/` |
| 4 | Training data from the second catalogue | `python finetune\build_train_catalogue.py`, `build_train_questions.py`, `export_examples.py` | `data_train/`, `finetune/` |
| 4 | Training (Kaggle GPU) | `python kaggle\push_job.py o4_train` then `python kaggle\pull_job.py o4_train --wait` | `finetune/adapters*/` |
| 4 | Adapter comparisons | `python harness\run_plan.py harness\plans\obj4_step6.json`, then `finetune\step6_verdicts.py` | `results_obj4/` |
| 5 | App equals harness | `python harness\run_plan.py harness\plans\obj5_step2_parity.json` | `results_obj5/` |
| 5 | Time and memory through the app | `python app\measure.py --tier A --subset test` (and `--tier B`) | `results_obj5/_measure_step8/` |
| 5 | Scenario walkthrough | `python app\walkthrough.py --tier A` (add `--offline` from a package) | `results_obj5/_walkthrough_step9/` |

Runs skip themselves once complete, so a plan can be stopped and restarted. `--only <run names>` runs part of a plan.

## What will and will not match

- **Quality runs are greedy** (temperature 0, seed 42). With the same llama.cpp build and the same model files
  (`scripts/assets.json` records the build and the SHA-256 of each file) replies repeat closely, but not always
  word for word, between runs. The reports measure that run-to-run noise from repeated runs and only call a
  difference real when it is larger.
- **Timing and memory** depend on the machine. The reports' numbers are from the laptop in
  [`ENVIRONMENT.md`](ENVIRONMENT.md), with one model server running and other heavy programs closed.
- **A newer llama.cpp build** or a re-uploaded model file can change replies. `setup.bat` says so when it cannot
  get the recorded build or when a downloaded file's SHA-256 differs.
- **The blind judge** (reply quality on unanswerable and store questions) was a language model from a different
  family than the two candidates, checked against the author's own labels. The packets it saw and its labels are in
  `eval/rag_judge/`; rerunning the judging needs a judge model of your own.

## Kaggle jobs

Long processor-only runs and the adapter training ran as private Kaggle notebooks (`kaggle/README.md`). They need
your own Kaggle account and key (`kaggle.json`, never committed). The log and returned files of every job the
project ran are under `kaggle/_pulled/`.
