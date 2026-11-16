#!/usr/bin/env bash
# Objective 4, Step 5 on Kaggle's CPU: convert the adapters to GGUF with the laptop's llama.cpp build and check them
# on the deployed model files (finetune/step5_check.py). Run by kaggle/kernel_main.py (jobs o4_step5_smoke, o4_step5).
#   bash finetune/kaggle_step5.sh <llama-server> <llama.cpp build tag> <adapter names...>
set -euo pipefail
SERVER=$1; TAG=$2; shift 2
W=/tmp/o4
mkdir -p "$W/models"
echo "llama-server: $SERVER; llama.cpp build $TAG"

# the converter from the same llama.cpp build as the laptop's llama-server
if [ ! -d "$W/llama.cpp" ]; then
  git clone --depth 1 --branch "$TAG" https://github.com/ggml-org/llama.cpp "$W/llama.cpp" 2> /dev/null \
    || { echo "tag $TAG not found; using the latest llama.cpp for the converter"; git clone --depth 1 https://github.com/ggml-org/llama.cpp "$W/llama.cpp"; }
fi
git -C "$W/llama.cpp" log -1 --format="converter: llama.cpp %h %cd"
python3 -m pip install -q "$W/llama.cpp/gguf-py" sentencepiece safetensors protobuf 2>&1 | grep -vE "dependency resolver|requires|incompatible" || true

# the deployed model files (Unsloth's GGUFs), checked against the laptop's copies when their hashes came with the job
python3 - <<'EOF'
import hashlib, json, os
from huggingface_hub import hf_hub_download
want = json.loads(os.environ.get("SLM_FILE_HASHES") or "{}")
for repo, fn in (("unsloth/Qwen3.5-2B-GGUF", "Qwen3.5-2B-Q8_0.gguf"), ("unsloth/Qwen3.5-4B-GGUF", "Qwen3.5-4B-Q4_K_M.gguf")):
    p = hf_hub_download(repo, fn, local_dir="/tmp/o4/models")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    lap = want.get(fn)
    print(f"{fn}: sha256 {h.hexdigest()[:16]}...", "| laptop:", ("same file" if lap == h.hexdigest() else
          ("DIFFERENT file (checks below use Unsloth's copy)" if lap else "hash not sent")))
EOF

python3 finetune/step5_check.py --server "$SERVER" --convert "$W/llama.cpp/convert_lora_to_gguf.py" --adapters "$@"
