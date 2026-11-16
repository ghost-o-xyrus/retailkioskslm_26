#!/usr/bin/env bash
# Objective 4, Step 3a on a Kaggle GPU session: build llama-server with CUDA, fetch the teacher, write the replies.
# Run by kaggle/kernel_main.py from the project folder (jobs o4_teacher_pilot and o4_teacher in kaggle/jobs.json).
#   bash finetune/kaggle_teacher.sh [teacher.py options...]
set -euo pipefail
mkdir -p /tmp/o4
W=/tmp/o4   # not /kaggle/working, which Kaggle keeps as job output (the model is 9.5 GB)
nvidia-smi --query-gpu=index,name,memory.total --format=csv
NGPU=$(nvidia-smi -L | wc -l)

# A recent CMake: Kaggle's (3.31) does not know CUDA 13's library layout, so it cannot find the CUDA driver
# library (the "CUDA::cuda_driver ... target was not found" error); CMake 4.x does.
python3 -m pip install -q -U "cmake>=4.1"
hash -r
cmake --version | head -1

# 1. llama-server with CUDA for the GPU this session got (T4 = 75, P100 = 60), read from the driver: Kaggle's CUDA
#    toolkit no longer builds for every older card, so only the card in use is targeted. Server target only.
ARCH=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1 | tr -d ' .')
echo "CUDA architecture: $ARCH; $(nvcc --version | tail -1)"
# the driver library to link against: the toolkit's stub if there is one, else the driver's own copy
LIBCUDA=""
for c in /usr/local/cuda/targets/x86_64-linux/lib/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so \
         /usr/lib/x86_64-linux-gnu/libcuda.so /usr/lib/x86_64-linux-gnu/libcuda.so.1 /usr/local/nvidia/lib64/libcuda.so.1; do
  if [ -e "$c" ]; then LIBCUDA=$c; break; fi
done
echo "CUDA driver library: ${LIBCUDA:-not found}"
SERVER_BIN="$W/llama.cpp/build/bin/llama-server"

build_llama() {
  [ -d "$W/llama.cpp" ] || git clone --depth 1 https://github.com/ggml-org/llama.cpp "$W/llama.cpp"
  local extra=()
  [ -n "$LIBCUDA" ] && extra=(-DCUDA_cuda_driver_LIBRARY="$LIBCUDA")
  cmake -S "$W/llama.cpp" -B "$W/llama.cpp/build" -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="$ARCH" "${extra[@]}" \
        -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF -DCMAKE_BUILD_TYPE=Release > "$W/cmake.log" 2>&1 \
        || { tail -40 "$W/cmake.log"; return 1; }
  cmake --build "$W/llama.cpp/build" --target llama-server -j "$(nproc)" > "$W/build.log" 2>&1 \
        || { tail -40 "$W/build.log"; return 1; }
  git -C "$W/llama.cpp" log -1 --format="llama.cpp %h %cd (built here)"
}

prebuilt_llama() {   # fallback: a Linux CUDA build from llama.cpp's latest release, if it publishes one
  python3 finetune/fetch_llama_cuda.py "$W/prebuilt" || return 1
  SERVER_BIN=$(cat "$W/prebuilt/server_path.txt")
  export LD_LIBRARY_PATH="$(dirname "$SERVER_BIN"):${LD_LIBRARY_PATH:-}"
}

if [ ! -x "$SERVER_BIN" ]; then
  build_llama || { echo "building llama.cpp failed; trying a prebuilt CUDA release"; prebuilt_llama; }
fi
"$SERVER_BIN" --version 2>&1 | tail -2 || true
RB=()
if "$SERVER_BIN" --help 2>&1 | grep -q -- "--reasoning-budget"; then RB=(--reasoning-budget 0); fi

# 2. the teacher model, Qwen3.5-9B Q8_0 (9.5 GB), from Hugging Face
python3 -c "from huggingface_hub import hf_hub_download as d; print('model:', d('unsloth/Qwen3.5-9B-GGUF', 'Qwen3.5-9B-Q8_0.gguf', local_dir='$W/models'))"

# 3. one server per GPU, 4 parallel slots each
SERVERS=()
PIDS=()
for ((i = 0; i < NGPU; i++)); do
  PORT=$((8101 + i))
  CUDA_VISIBLE_DEVICES=$i "$SERVER_BIN" -m "$W/models/Qwen3.5-9B-Q8_0.gguf" \
      --host 127.0.0.1 --port $PORT -ngl 99 -c 16384 -np 4 --jinja "${RB[@]}" > "$W/server$i.log" 2>&1 &
  PIDS[$i]=$!
  SERVERS+=("http://127.0.0.1:$PORT")
done
for ((i = 0; i < NGPU; i++)); do
  s=${SERVERS[$i]}
  for _ in $(seq 1 120); do
    curl -sf "$s/health" > /dev/null && break
    kill -0 "${PIDS[$i]}" 2> /dev/null || break          # the server quit: stop waiting
    sleep 5
  done
  curl -sf "$s/health" > /dev/null || { echo "server $i did not start:"; tail -30 "$W/server$i.log"; exit 1; }
  grep -m2 -iE "offloaded|using device CUDA" "$W/server$i.log" || true   # shows the model is on the GPU
done
# a quick test: the model answers and thinking is off
python3 finetune/teacher.py --servers "${SERVERS[0]}" --check

# 4. the replies
python3 finetune/teacher.py --servers "${SERVERS[@]}" --slots 4 "$@"
pkill -f llama-server || true
