# Objective 4: LoRA adaptation (prototype on fictional data)

Steps 1-2 build the training examples; no model and no GPU are involved.

| Step | Script | Output |
|---|---|---|
| 1 Training catalogue | `python finetune\build_train_catalogue.py` | `data_train/`, `finetune/knowledge/corpus.jsonl` |
| 2a Training questions | `python finetune\build_train_questions.py` | `finetune/train/{tools,store,followups}.jsonl`, `questions_report.md` |
| 2b Run them through the harness against the oracle | `python harness\run_plan.py finetune\plans\o4_traj_tierA.json` (and `tierB`) | `results_o4/traj_{a,b}/*.jsonl` |
| 2c Export | `python finetune\export_examples.py` | `finetune/examples/tier{A,B}.jsonl`, `tools.json`, `wording_tasks.jsonl`, `mix_report.md` |

- **Training catalogue:** the deployed generator with a new seed. Collections, style names, design codes (V6000+),
  store names and hours are all new. Service prices, service times and return windows are moved, so learnt policy
  facts never match the deployed store's. The brand architecture stays.
- **Questions:** the eval generators re-run on the training catalogue with their own seeds, plus new templates for
  "not listed", unlisted policies, made-up designs, refusals and follow-ups. A question is dropped if it copies an
  eval question, or if a hand-written one is close to one (Jaccard 0.6). Template questions are reworded.
- **Oracle** (`oracle_server.py`): stands in for llama-server and gives the correct next action for each request,
  so the training text is exactly the text the harness builds at run time. That includes the system prompt, the
  tools, the shown cards, the harness-run tool rounds and the notes. A product fact counts as shown only on that
  product's own card or tool result. Replies are template drafts; Step 3 rewrites them.
- The harness options `--corpus` (plan key `corpus`) and `--data-dir` point retrieval and the tools at the training
  catalogue. `SLM_DATA_ROOT` points the eval generators at it.

Tests: `python -m unittest finetune.test_finetune`.

## On Kaggle (while the laptop is busy)

Steps 1-2 run as one Kaggle CPU job; no GPU hours are used. The job uploads the laptop's retrieval models
(`models/ov/bge-small`, `models/ov/minilm`) and the Step 12 retrieval settings, so retrieval is the deployed one.

    python kaggle\push_job.py o4_step2
    python kaggle\pull_job.py o4_step2 --wait

The pull brings back `data_train/`, `finetune/knowledge/`, `finetune/train/`, `finetune/examples/` and `results_o4/`.
Step 3's teacher job (`o4_teacher_pilot`, then `o4_teacher`, both with `--gpu`) then uploads `finetune/examples/`.

## Step 4: training (Kaggle GPU)

- `prepare_sft.py`: renders each example with the model's own chat template (tools included, thinking off) and
  puts the loss on the answer only. Examples that cannot be split or are over 4,096 tokens are counted and dropped.
  5% of the questions are held out for the loss check.
- `train_lora.py`: one adapter with Unsloth and the pre-registered settings (rank 16, alpha 32, lr 2e-4 cosine with
  5% warm-up, effective batch 16, seed 3407). `--qlora` uses a 4-bit base. Precision follows what Unsloth loads (the
  T4 has no bf16): fp16 mixed precision is on when the base weights are fp16, as the smoke run measured.
  `--fit-minutes M --smoke-log ...` plans the number of steps from the smoke run's seconds per step (90% of M; the
  time limit is only a backstop), so the cosine schedule finishes; `--epochs` caps it. If 2 examples per step run
  out of GPU memory, the run is repeated once at 1 per step with 16 accumulated.
- `kaggle_train.sh smoke|full`: two runs at a time, one per T4. Smoke (`o4_train_smoke`): 8 steps of each on 200
  examples, the 4B as QLoRA. Full (`o4_train`, needs the smoke run's `train_log.json` files): 1 epoch of each, chosen
  after the smoke run for the GPU budget. GPU 0: `lora_4b` (16-bit, as pre-registered), or `qlora_4b` if the LoRA
  fails even at 1 example per step; GPU 1: `lora_2b`, then `qlora_2b`. Time limits `O4_MIN_4B` 335, `O4_MIN_2B` 145,
  `O4_MIN_Q2B` 145 minutes (about 5.7 hours). The adapters land in `finetune/adapters/<name>/`, each with
  `train_log.json`. Steps 5-8 use whichever 4B adapter exists (`build_step6_plan.py` picks it, LoRA first).

## Step 5: the adapters on the deployed model files (Kaggle CPU, route a)

- `step5_check.py`: for each adapter, converts it to a GGUF LoRA file with the laptop's llama.cpp build
  (`convert_lora_to_gguf.py`, f16, into `finetune/adapters_gguf/`), loads it next to the tier's deployed GGUF in
  llama-server (`--lora`, not merged), and checks it. Pre-registered rules, all must hold:
  1. the file converts and loads (listed by `/lora-adapters`, no LoRA error in the log);
  2. template: at least 95% of 40 prompts that llama-server builds from the harness's request (`/apply-template`)
     are identical to the training prompts;
  3. scale 0: greedy replies with the adapter at scale 0 match plain decoding at least as often as plain decoding
     matches itself (8 examples, held-out questions first).
  Scale 1 is a first look only (exact answers, tool calls, printed markup, replies that end by themselves).
  Writes `step5_report.md` and `step5_report.json`.
- `kaggle_step5.sh`: gets the converter at the laptop's build tag, downloads the deployed GGUFs and compares their
  sha256 with the laptop's copies (hashed once by `push_job.py`, cached), then runs the checks.
  Jobs: `o4_step5_smoke` (the smoke adapters, to test the path early), then `o4_step5` (CPU, no GPU hours).
  The Linux llama-server comes from the release matching the laptop's `llama-server --version` (`bNNNNN` or
  `v0.x.y` tags; release files are `.tar.gz`), else the latest release, else it is built from source; the job log
  says which, and whether it matches the laptop build. These jobs install `transformers>=5` (Qwen3.5 configs and the
  tokenizers saved with the adapters need it), not the laptop's pinned version.
- On the laptop (Step 6), a plan entry takes `"lora": "finetune/adapters_gguf/lora_2b.gguf"` (and optionally
  `"lora_scale"`); `run_plan.py` adds `--lora` / `--lora-scaled` and stops that run if the file is missing.

## Step 6: dev comparison (laptop, Vulkan)

- `build_step6_plan.py` writes `harness/plans/obj4_step6.json` from O3-final's own run settings (the Step 14 plan),
  so each adapter run differs from its baseline only in the `lora` key: 20 runs on dev (store questions, v1.2 tool
  cases, follow-ups, the 40 dev dialogues) for O3-final, + `lora_2b`, + `qlora_2b` (Tier A) and O3-final,
  + `lora_4b` (or `qlora_4b`) (Tier B). Results go to `results_obj4/`.
- `eval/compare_dev.py --all-hinglish` adds the Hinglish subset on the dev sets.
- `step6_verdicts.py --run-compare` runs the paired comparisons (`compare_dev.py --all-hinglish` with the Objective 3
  noise bounds, `score_dialogues.py`), then applies the pre-registered rules (H1-H4, keep rule, H6, what goes on to
  Step 7) and writes `results_obj4/_step6/verdicts.md`.
- `verdict_common.py`: the pieces Steps 6-8 share (no-regression rule, printed tool calls, running the comparisons).

## Step 7: patches removed, and the 4B's short replies with the adapter (laptop, Vulkan)

- `build_step78_plans.py step7` writes `harness/plans/obj4_step7.json` for the adapters Step 6 carries
  (`--tier-a` / `--tier-b` override). Patches off = forced-answer recovery off (a printed call still never reaches
  the customer as markup; it becomes the fixed staff line) and the staff check off; the staff guard is already off
  in O3-final; the entity check, answer check and fallback stay. Runs: Tier A adapter with patches off; Tier B
  adapter with short replies, and with short replies and patches off; then two control sets (O3-final with patches
  off; O3-final's 4B with short replies), reported only. The Step 6 O3-final runs are the baselines.
- `step7_verdicts.py --run-compare` applies the rules (H5 per tier; the 4B's short-reply check, which decides a
  provisional Tier B adapter) and writes `results_obj4/_step7/verdicts.md`, with the deployed candidate per tier.

## Step 8: speed and RAM

- `build_step78_plans.py step8` writes `harness/plans/obj4_step8.json`: Tier A in place (2B Q8_0 on CPU, 4 threads,
  the 70-case dev speed subset, 2 repeats, alternating): O3-final, O3-final + adapter, and the Step 7 candidate if it
  switched the patches off.
- `step8_verdicts.py --run-compare`: writing speed (the adapter's own cost, at least 90% of O3-final's), total reply
  time of the candidate (not significantly longer), peak RAM, and Tier B from the Vulkan runs of Steps 6-7.
  Writes `results_obj4/_step8/verdicts.md`.
