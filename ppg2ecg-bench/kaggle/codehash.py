"""Fingerprint of the benchmark code, so a Kaggle job can tell whether the code it runs is the code it was
created for (the classic mistake: new job folders, old uploaded code -> KeyError: 'stage_k60')."""
import hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP = {"results", "kernels", "__pycache__", "third_party", ".git", "upload", "out", ".venv", "venv", "data", "tests"}
SUFFIX = {".py", ".yaml", ".yml"}
# tools that only ever run on the laptop: changing them must not force a code re-upload
LAPTOP_ONLY = {"run.py", "wait.py", "fetch.py", "push_code.py", "codehash.py", "upload_dataset.py",
               "prepare_aurora.py", "prepare_capnobase.py"}


CODE_DIRS = ["bench", "scripts", "kaggle", "configs", "registry"]


def code_hash(repo=REPO):
    h = hashlib.sha1()
    files = [p for d in CODE_DIRS for p in (repo / d).rglob("*")]
    for p in sorted(files):
        rel = p.relative_to(repo)
        if p.is_file() and p.suffix in SUFFIX and not (SKIP & set(rel.parts)) \
                and not (rel.parts[0] == "kaggle" and p.name in LAPTOP_ONLY):
            h.update(str(rel.as_posix()).encode())
            h.update(p.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:12]


if __name__ == "__main__":
    print(code_hash())
