#!/usr/bin/env bash
# Objective 4, Step 4 on a Kaggle GPU session (2 x T4): train the three adapters, two at a time, one per GPU.
#   bash finetune/kaggle_train.sh smoke    # 8 steps of each on 200 examples: errors, seconds per step, memory
#   bash finetune/kaggle_train.sh full     # GPU 0: 4B LoRA (Tier B); GPU 1: 2B LoRA, then 2B QLoRA (Tier A)
# The full run is 1 epoch of each adapter (chosen after the smoke run, for the GPU budget), with the steps planned
# from the smoke run's seconds per step so each run fits its time limit. Time limits, in minutes:
#   O4_MIN_4B (default 335), O4_MIN_2B (145), O4_MIN_Q2B (145)
# The smoke run trained the 4B on a 4-bit base; it measured fp16 weights and 5.1 GB, so the 16-bit 4B LoRA (about
# 9 GB of weights) is expected to fit a T4. If it fails even at 1 example per step, GPU 0 trains the 4B QLoRA
# (qlora_4b) instead, and the Step 5-8 scripts use whichever 4B adapter exists.
set -euo pipefail
MODE=${1:-smoke}
nvidia-smi --query-gpu=index,name,memory.total --format=csv
python3 -m pip install -q -U unsloth unsloth_zoo 2>&1 | grep -vE "dependency resolver|requires|incompatible" || true
python3 -c "import unsloth, torch, transformers; print('torch', torch.__version__, '| CUDA', torch.version.cuda, '| transformers', transformers.__version__, '| unsloth', unsloth.__version__, '| GPUs', torch.cuda.device_count())"
for f in finetune/examples/tierA_final.jsonl finetune/examples/tierB_final.jsonl finetune/examples/tools.json; do
  [ -s "$f" ] || { echo "missing $f (run Step 3's filter_wording.py on the laptop before pushing)"; exit 1; }
done

if [ "$MODE" = smoke ]; then
  S=(--max-steps 8 --limit 200 --max-minutes 45)
  M4=(--name smoke_qlora_4b)
  M2=(--name smoke_lora_2b)
  Q2=(--name smoke_qlora_2b)
else
  T4=${O4_MIN_4B:-335}; T2=${O4_MIN_2B:-145}; TQ=${O4_MIN_Q2B:-145}
  for n in smoke_qlora_4b smoke_lora_2b smoke_qlora_2b; do
    [ -s "finetune/adapters/$n/train_log.json" ] || { echo "missing finetune/adapters/$n/train_log.json (pull o4_train_smoke first)"; exit 1; }
  done
  S=(--epochs 1)
  # 10 minutes of each limit are left for loading, data and the final held-out check
  # the 4B LoRA has no smoke run of its own: the 4B QLoRA's seconds per step plan it (the 2B ran LoRA and QLoRA at the
  # same speed)
  M4=(--name lora_4b --max-minutes "$T4" --fit-minutes $((T4 - 10)) --smoke-log finetune/adapters/smoke_qlora_4b/train_log.json)
  M4Q=(--name qlora_4b --qlora --max-minutes "$T4" --fit-minutes $((T4 - 10)) --smoke-log finetune/adapters/smoke_qlora_4b/train_log.json)
  M2=(--name lora_2b --max-minutes "$T2" --fit-minutes $((T2 - 10)) --smoke-log finetune/adapters/smoke_lora_2b/train_log.json)
  Q2=(--name qlora_2b --max-minutes "$TQ" --fit-minutes $((TQ - 10)) --smoke-log finetune/adapters/smoke_qlora_2b/train_log.json)
fi

# one training run; if it runs out of GPU memory at 2 examples per step, once more at 1 (effective batch still 16)
run() {   # run <gpu> <label> <args...>
  local gpu=$1 label=$2; shift 2
  local out=/tmp/o4_${label}.log
  if CUDA_VISIBLE_DEVICES=$gpu python3 finetune/train_lora.py "$@" 2>&1 | tee "$out" | sed -u "s/^/[gpu$gpu] /"; then
    return 0
  fi
  if grep -qE "OutOfMemoryError|CUDA out of memory" "$out"; then
    echo "[gpu$gpu] $label ran out of GPU memory at 2 examples per step; again at 1"
    CUDA_VISIBLE_DEVICES=$gpu python3 finetune/train_lora.py "$@" --batch 1 2>&1 | sed -u "s/^/[gpu$gpu] /" && return 0
  fi
  echo "[gpu$gpu] the $label run failed"
  return 1
}

if [ "$MODE" = smoke ]; then
  ( run 0 4B-QLoRA --tier B --model unsloth/Qwen3.5-4B --qlora "${M4[@]}" "${S[@]}" || true ) &
else
  ( run 0 4B-LoRA --tier B --model unsloth/Qwen3.5-4B "${M4[@]}" "${S[@]}" \
      || { echo "[gpu0] the 4B LoRA failed; training the 4B QLoRA instead"; rm -rf finetune/adapters/lora_4b;
           run 0 4B-QLoRA --tier B --model unsloth/Qwen3.5-4B "${M4Q[@]}" "${S[@]}"; } || true ) &
fi
P0=$!
( run 1 2B-LoRA --tier A --model unsloth/Qwen3.5-2B "${M2[@]}" "${S[@]}" || true
  run 1 2B-QLoRA --tier A --model unsloth/Qwen3.5-2B --qlora "${Q2[@]}" "${S[@]}" || true ) &
P1=$!
wait $P0 $P1 || true
python3 - "$MODE" <<'EOF' || true
import glob, json, sys
smoke = sys.argv[1] == "smoke"
for p in sorted(glob.glob("finetune/adapters/*/train_log.json")):
    if ("/smoke_" in p) != smoke:
        continue                                   # the full run prints only its own adapters
    try:
        g = json.load(open(p))
        ho = g.get("held_out_loss") or []
        print(f"{g.get('name')}: {g.get('steps')} steps ({g.get('epochs_done')} epochs, {g.get('seconds_per_step')} s per "
              f"step), {g.get('train_minutes')} min, peak GPU {g.get('peak_gpu_gb')} GB, compute {g.get('compute_dtype')}, "
              f"held-out loss {ho[-1][1] if ho else '-'}"
              + (f", planned {g['planned']['steps']} steps" if g.get("planned") else "")
              + (f", STOPPED at the time limit (step {g['stopped_at_time_limit']})" if g.get("stopped_at_time_limit") else ""))
    except Exception as e:  # noqa: BLE001
        print(f"{p}: could not read ({e})")
EOF
has() { [ -s "finetune/adapters/$1/adapter_model.safetensors" ]; }   # (ls on a missing file would stop the script)
N=0
if [ "$MODE" = smoke ]; then
  for n in smoke_qlora_4b smoke_lora_2b smoke_qlora_2b; do has "$n" && N=$((N + 1)); done
else
  for n in lora_2b qlora_2b; do has "$n" && N=$((N + 1)); done
  { has lora_4b || has qlora_4b; } && N=$((N + 1))
fi
echo "$N of 3 adapters saved"
[ "$N" -eq 3 ] || exit 1
