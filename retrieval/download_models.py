"""
Download the Step 5 models once, so the benchmark itself never waits on the network.

    python retrieval\\download_models.py

Models go to the Hugging Face cache (by default C:\\Users\\<you>\\.cache\\huggingface). To keep them inside the
project instead, set HF_HOME first, e.g.  $env:HF_HOME = "..\\hf_cache"  (set it again before each benchmark run).
About 2.3 GB in total. Already-downloaded files are skipped.
"""

import os
import time

MODELS = [
    ("BAAI/bge-small-en-v1.5", "embedding, 33M parameters"),
    ("BAAI/bge-base-en-v1.5", "embedding, 110M parameters"),
    ("intfloat/multilingual-e5-small", "embedding, 118M parameters, multilingual"),
    ("BAAI/bge-reranker-base", "re-ranker, 278M parameters, multilingual"),
    ("cross-encoder/ms-marco-MiniLM-L-6-v2", "re-ranker, 22M parameters, English"),
]


def folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def main():
    from huggingface_hub import snapshot_download
    for name, what in MODELS:
        t = time.time()
        print(f"{name}  ({what}) ...", flush=True)
        path = snapshot_download(name, allow_patterns=["*.json", "*.txt", "*.safetensors", "*.model",
                                                       "sentencepiece*", "tokenizer*", "1_Pooling/*", "modules.json"])
        print(f"   ok: {folder_size(path) / 1e6:.0f} MB in {time.time() - t:.0f} s -> {path}", flush=True)
    print("\nAll models ready.")


if __name__ == "__main__":
    main()
