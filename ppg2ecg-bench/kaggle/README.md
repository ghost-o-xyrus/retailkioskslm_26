# Running the benchmark on Kaggle

Everything heavy runs on Kaggle. Your laptop only sends commands and downloads small result
tables, and you can close it while jobs run.

In every command, replace **YOURNAME** with your Kaggle username. All commands are run from inside
the `ppg2ecg-bench` folder with the virtual environment active (your prompt starts with `(.venv)`).
They are the same in Windows PowerShell, macOS and Linux.

**The one rule:** start jobs with `kaggle/run.py`, not `kaggle kernels push`. Most jobs read the
output of other jobs. If a job starts before its inputs have finished, Kaggle prints
*"not valid kernel sources"* and runs it **without** them. `run.py` waits for the inputs and respects
Kaggle's limits (5 CPU jobs and 2 GPU jobs at once). It shows the error when a job fails and
downloads the results at the end.

---

## 1. One-time setup (already done, kept for reference)

<details><summary>Click to expand</summary>

```
python -m venv .venv
.venv\Scripts\activate              # macOS/Linux: source .venv/bin/activate
pip install --upgrade kaggle pyyaml numpy scipy pandas
kaggle auth login                   # approve in the browser; your account must be phone-verified
```
Private datasets Kaggle cannot download itself (uploaded once):
```
python kaggle/prepare_capnobase.py "PATH/TO/CAPNOBASE" upload/capnobase-raw
python kaggle/upload_dataset.py upload/capnobase-raw capnobase-raw --user YOURNAME
python kaggle/prepare_aurora.py "PATH/TO/AURORA" upload/aurora-bp-raw
python kaggle/upload_dataset.py upload/aurora-bp-raw aurora-bp-raw --user YOURNAME   # never make it public
python kaggle/upload_dataset.py "PATH/TO/bidmc_csv_folder" bidmc-raw --user YOURNAME
```
</details>

---

## 2. After every new code version (2 commands, always both)

Unpack the new `ppg2ecg-bench.tar.gz` over your folder, then:
```
python kaggle/push_code.py YOURNAME "new version"
python kaggle/make_kernels.py --user YOURNAME --capnobase-dataset YOURNAME/capnobase-raw --aurora-dataset YOURNAME/aurora-bp-raw --extra-raw YOURNAME/bidmc-raw
```
- **`push_code.py`** uploads the code and waits until Kaggle says `ready`.
- **`make_kernels.py`** rewrites the job folders on your laptop. It starts nothing.

Jobs run whatever code is uploaded on Kaggle, not the code on your laptop. If you skip
`push_code.py`, every new job dies in one second (`KeyError: 'stage_k60'`). This is now caught twice:
- `run.py` refuses to start anything until both commands have been run for the current code.
- Each job stops at once with `STOPPED: the uploaded code ... is not the code this job was created for`.

---

## 3. Run the jobs: one command per stage

Each stage is one command. It keeps printing progress until every job of the stage has finished.
Every 10 minutes it prints a `still running: ... | waiting: ...` line, so a quiet screen is never
a hang; long jobs (k70b ~3–6 h, training jobs up to 5 h) simply take that long.
Ctrl-C only stops the printing; the jobs keep running on Kaggle, and running the same command again
picks up where it left off. Completed jobs are never repeated unless you add `--rerun`.

To see where everything stands at any time:
```
python kaggle/run.py --user YOURNAME --status
```

### Stage A: original Track 1 (done)
k00 to k50, k02/k22/k32/k42. Nothing to do.

### Stage B: new inputs (CPU, ~10 min)
```
python kaggle/run.py --user YOURNAME --phase inputs
```
- k03 downloads MIMIC PERform AF from Zenodo.
- k04 downloads RDDM's weights from Google Drive.

If either fails, see section 5. Everything after this stage needs k03, and the RDDM jobs need k04.

### Stage C: RDDM, Zhu DCT, MIMIC PERform AF runs, authors' pipelines, information analysis (~10 h)
```
python kaggle/run.py --user YOURNAME --phase expansion
```
12 jobs. The CPU jobs run five at a time and the GPU jobs two at a time, automatically. If k04
failed, the RDDM jobs (k70a/b, k71a/b, k51) are skipped and the rest still run.

### Stage D: train the four code-only models, then evaluate them (~16 GPU-h + ~6 h CPU)
```
python kaggle/run.py --user YOURNAME --phase trained
```
- **k89 (CPU, ~20 min)** runs first. It is a short smoke test of all four training recipes.
- **k90–k93 (GPU, two at a time)**: a model trains only if its own smoke test passed. A model that
  failed is skipped and its error is printed (e.g. `k90 skipped: the smoke test of chiu2020 failed`);
  the others go ahead.
- **k95a/b/c and k52 (CPU)** evaluate and profile the trained models. They start once every training
  job has ended, and run if at least one model trained.

Yalcin alone (training, then only its own evaluation and profile, so the others are not redone):
```
python kaggle/run.py --user YOURNAME --phase yalcin
```

When another model is fixed later, run its smoke test and training again, then the evaluation:
```
python kaggle/run.py --user YOURNAME k89 k90 --rerun
python kaggle/run.py --user YOURNAME k95a k95b k95c k52 --rerun
```

Stages C and D can run at the same time in two terminals. They share Kaggle's limits, so some
jobs will simply wait their turn.

---

## 4. Combine the results and send them to me

`run.py` has already downloaded each finished job into `out/<job>`. Then:
```
python scripts/merge_results.py --out results/track1 "out/k*"
python scripts/robustness_report.py results/track1
```
Send me:
- `results/track1` (without `windows.csv`)
- `out/k60/results/info` (without `templates_*.npz`)
- `out/k80/results/author_eval`
- the `out/<job>` folder of any job that failed

---

## 5. When something fails

`run.py` prints the last 40 lines of a failed job's log, and the full log is in `out/<job>/`.
Common messages:

| Message | Meaning | What to do |
|---|---|---|
| `not valid kernel sources ... k03` | This job was started before k03 had finished, so it ran without that input | Nothing extra: `run.py` never does this. Jobs now also stop within seconds with `STOPPED before doing any work` instead of running hours without their input |
| `STOPPED before doing any work: the output of [...] is not attached` | Same as above, caught by the job itself | Run the stage command again; it waits for the inputs |
| `KeyError: 'stage_k60'` (any job name) | The job ran old uploaded code that doesn't know this job | Run both commands of section 2, then the stage command again |
| `STOPPED: the uploaded code (version ...) is not the code this job was created for` | Same, caught by the job itself | Same |
| `run.py: error: not starting anything` | Your code isn't uploaded, or the job folders are stale | Do what the message says (section 2) |
| `Maximum batch CPU session count of 5 reached` / `GPU session count of 2` | Kaggle's limit on jobs at once | `run.py` waits and retries by itself |
| `Connection aborted`, `Failed to resolve 'api.kaggle.com'` | Your internet dropped | Nothing; it retries. If the window closed, run the command again |
| `KeyboardInterrupt` after Ctrl-C | You stopped watching | Jobs keep running; run the command again |

**If k03 fails (Zenodo download):**
1. Download `mimic_perform_af_data.mat` and `mimic_perform_non_af_data.mat` from
   <https://zenodo.org/records/6807403> in your browser, into a folder `upload/maf-raw`.
2. Upload them:
   ```
   python kaggle/upload_dataset.py upload/maf-raw maf-raw --user YOURNAME
   ```
3. Re-run `make_kernels.py` from section 2 with `--extra-raw YOURNAME/bidmc-raw YOURNAME/maf-raw`.
4. Run:
   ```
   python kaggle/run.py --user YOURNAME k03
   ```

**If k04 fails (Google Drive refuses automated downloads, which happens often):**
1. Open <https://drive.google.com/drive/folders/1Z7JQ5VdTrekx4lbARJNIUiR5D-4Kz7wg>.
2. Download `rddm_main_network.pth`, `rddm_condition_encoder_1.pth` and `rddm_condition_encoder_2.pth`
   into a folder `upload/rddm-weights`.
3. Upload them:
   ```
   python kaggle/upload_dataset.py upload/rddm-weights rddm-weights --user YOURNAME
   ```
4. Re-run `make_kernels.py` with `--extra-raw YOURNAME/bidmc-raw YOURNAME/rddm-weights`, adding
   `YOURNAME/maf-raw` if you made it.
5. Run:
   ```
   python kaggle/run.py --user YOURNAME k04
   ```

**Anything else:** send me the `out/<job>` folder.

---

## 6. Reference: all jobs

| Job | What | HW | ~Time | Reads output of |
|---|---|---|---|---|
| k00 | prepare CapnoBase, DaLiA, WESAD, Aurora-BP | CPU | 3.5 h | – |
| k01 | download CardioGAN + PPGFlowECG weights | CPU | 10 min | – |
| k02 | prepare BIDMC | CPU | 5 min | – |
| k03 | prepare MIMIC PERform AF | CPU | 5 min | – |
| k04 | RDDM code + weights | CPU | 5 min | – |
| k10 | smoke test of the original models | GPU | 45 min | k00 k01 |
| k20a/b, k21a/b, k22 | CardioGAN clean / robustness / BIDMC | CPU | 0.5–2.5 h | k00 k01 (k02) |
| k30a/b, k31a/b, k32 | PPGFlowECG clean / robustness / BIDMC | GPU | 0.3–2 h | k00 k01 (k02) |
| k40a/b, k42 | template baseline | CPU | 0.5–2 h | k00 k01 (k02) |
| k50 | CPU profile, original models | CPU | 5 min | k00 k01 |
| k23 / k33 / k43 | CardioGAN / PPGFlowECG / baseline on MIMIC PERform AF | CPU/GPU/CPU | 0.5–1 h | k00 k01 k03 |
| k44a / k44b | Zhu DCT clean / robustness | CPU | 1–2 h | k00 k01 k02 k03 |
| k70a / k70b | RDDM clean (long datasets + MAF / Aurora-BP) | GPU | 1 h / 3–6 h | k00 k01 k02 k03 k04 |
| k71a / k71b | RDDM robustness | GPU | 1 h | k00 k01 k02 k03 k04 |
| k51 | CPU profile, RDDM + Zhu | CPU | 10 min | k00 k01 k04 |
| k80 | authors' pipelines vs ours (RDDM, PPGFlowECG, CardioGAN) | GPU | 2–3 h | k00 k01 k02 k03 k04 |
| k60 | Track 1.5 information analysis | CPU | 1–3 h | k00 k02 k03 |
| k89 | smoke test of the four training recipes | CPU | 20 min | k03 |
| k90 / k91 / k92 / k93 | train Chiu / CLEP-GAN / P2E-WGAN / Yalcin (hard caps 2 / 5 / 4 / 4.5 h) | GPU | ≤ cap | (k89) k03 for k92, k93 |
| k95a / k95b / k95c | evaluate the trained models: clean long+MAF / clean Aurora-BP / robustness | CPU | 2–5 h | k00 k01 (k02 k03) k90–k93 |
| k52 | CPU profile, trained models | CPU | 15 min | k00 k01 k90–k93 |
| k96a / k96b / k96c, k53 | the same evaluations and profile for Yalcin only | CPU | 1–3 h / 10 min | k00 k01 (k02 k03) k93 |

Low-level tools `run.py` uses, if you ever need them by hand:
- `kaggle/wait.py --user YOURNAME k03` watches jobs.
- `kaggle/fetch.py --user YOURNAME k03` downloads a job's results and log into `out/k03`.
