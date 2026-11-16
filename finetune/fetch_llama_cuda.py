"""
Fallback for kaggle_teacher.sh: fetch a Linux CUDA llama-server from llama.cpp's latest GitHub release, if the
release publishes one (used only when building on Kaggle fails).

    python finetune/fetch_llama_cuda.py /tmp/o4/prebuilt     # writes <dir>/server_path.txt
"""

import glob
import json
import os
import sys
import tarfile
import urllib.request
import zipfile


def main(dest):
    os.makedirs(dest, exist_ok=True)
    with urllib.request.urlopen("https://api.github.com/repos/ggml-org/llama.cpp/releases/latest", timeout=30) as r:
        rel = json.load(r)
    names = lambda a: a["name"].lower()  # noqa: E731
    assets = [a for a in rel.get("assets", []) if "cuda" in names(a) and ("ubuntu" in names(a) or "linux" in names(a))
              and "x64" in names(a) and names(a).endswith((".zip", ".tar.gz"))]
    if not assets:
        sys.exit(f"no Linux CUDA build in llama.cpp release {rel.get('tag_name', '?')}")
    a = assets[0]
    path = os.path.join(dest, a["name"])
    urllib.request.urlretrieve(a["browser_download_url"], path)
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            z.extractall(dest)
    else:
        with tarfile.open(path) as t:
            t.extractall(dest)
    exe = next(iter(glob.glob(os.path.join(dest, "**", "llama-server"), recursive=True)), None)
    if not exe:
        sys.exit("no llama-server in " + a["name"])
    os.chmod(exe, 0o755)
    with open(os.path.join(dest, "server_path.txt"), "w") as f:
        f.write(exe)
    print(f"llama.cpp {rel.get('tag_name')} prebuilt: {a['name']}")


if __name__ == "__main__":
    main(sys.argv[1])
