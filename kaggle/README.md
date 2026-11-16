# Running CPU jobs on Kaggle

Heavy CPU-only work (training, retrieval benchmarks, llama.cpp CPU runs) can run on a free Kaggle CPU session instead
of the laptop. Vulkan (Iris Xe) runs stay on the laptop.

**Timing rule:** latency, tokens per second and RAM only count when measured on the laptop, the kiosk's machine.
- Every run records which machine it ran on (`machine` in `run_meta.json`; Kaggle runs say `kaggle-cpu`).
- `eval/compare_dev.py` marks waits from different machines as not comparable.
- `retrieval/bench_reranker.py` makes no choice from Kaggle latency.

Quality numbers (pass rates, recall) do not depend on the machine.

## One-time setup

1. **Kaggle account.** On kaggle.com, open Settings → Phone verification and verify your phone. Notebooks need
   this to reach the internet, which the job uses to download Hugging Face models and llama.cpp.
2. **API token.** On kaggle.com, open Settings → API → "Create New Token". This downloads `kaggle.json`.
   ```powershell
   mkdir $env:USERPROFILE\.kaggle -Force
   move $env:USERPROFILE\Downloads\kaggle.json $env:USERPROFILE\.kaggle\kaggle.json
   ```
   If the page shows a token to copy instead of downloading a file, set it up the way that page says. Then add
   `--user <your Kaggle user name>` to `push_job.py` and `push_models.py`, or set it once with
   `setx KAGGLE_USERNAME <name>` and open a new terminal.
3. **Kaggle command-line tool**, inside `slm-env`:
   ```powershell
   pip install kaggle
   kaggle datasets list -m        # should print a table (maybe empty), not an error
   ```
4. **First job, to check the whole path** (about 5 minutes on Kaggle):
   ```powershell
   python kaggle\push_job.py selftest
   python kaggle\pull_job.py selftest --wait
   ```
   It should end with "Job succeeded".
5. **Only for jobs that run llama-server on Kaggle** (`--plan`): upload the CPU model once. It is a 2.5 GB upload.
   ```powershell
   python kaggle\push_models.py ..\models\qwen3.5-2b\Qwen3.5-2B-Q8_0.gguf
   ```

## Every job

```powershell
python kaggle\push_job.py <job>                      # a job from kaggle/jobs.json, e.g. step9_train
python kaggle\push_job.py --plan harness\plans\X.json   # only the plan's CPU runs
python kaggle\pull_job.py <job> --wait               # waits, downloads, unpacks the results into the project
```

- **What is uploaded:** the project's code and data as a **private** dataset (`<user>/slm-kiosk-code`, about
  1 MB), plus the job's listed inputs.
- **What is left out:** results folders, models, llama.cpp builds and virtual environments.
- **Where it runs:** a **private** notebook, `<user>/slm-kiosk-<job>`. You can watch it on kaggle.com while it
  runs.
- **What comes back:** only the files the job created or changed under its output paths. Nothing else in
  `results_*` is touched. The full log is in `kaggle\_pulled\<job>\job_log.txt`.
- **Packages:** installed at the laptop's versions where possible, falling back to unpinned versions.
- **llama.cpp:** the Linux CPU build with the same build number as `llama-cpu\llama-server.exe`. If that build has
  no Linux download, the log says so.

Kaggle CPU sessions have 4 cores, about 30 GB RAM and a 12-hour limit per run. `--gpu` asks for a GPU session
instead (off by default; it counts against Kaggle's weekly GPU hours).

## Many plan jobs at once (`run_queue.py`)

```powershell
python kaggle\run_queue.py harness\plans\obj3_step15\*.json              # as many at once as Kaggle allows
python kaggle\run_queue.py harness\plans\obj3_step15\*.json --parallel 5 # or a fixed number
python kaggle\run_queue.py --status                                          # progress, no Kaggle calls
```

Pushes every waiting job with ONE code upload, then one kernel per job. If Kaggle refuses a push (or a job never
starts), the number running is taken as Kaggle's limit; the rest go in as slots free up, and the limit is probed
again every 30 minutes. Each job is pulled when it ends and pushed again if some of its runs are unfinished
(resumes). Plan jobs stop themselves after
`kaggle_max_minutes` (default 650) and pack what they have, so Kaggle's 12-hour limit never loses a run. Stop it
with Ctrl+C at any time; the same command picks up where it was (state in `kaggle\_queue\state.json`).
