"""Upload (or update) the harness as the PRIVATE Kaggle dataset <user>/ppg2ecg-bench-code.

    python kaggle/push_code.py YOUR_KAGGLE_USERNAME "what changed"

Cross-platform (no bash needed). Requires the `kaggle` CLI to be installed and authenticated.
"""
import json
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from codehash import code_hash  # noqa: E402

user, msg = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "update")
repo = Path(__file__).resolve().parents[1]
# Ship ONLY code: an allowlist of folders and file types, so results, downloads, zips or environments
# lying around in the project folder can never be uploaded (Aurora's DUA forbids redistribution).
CODE_DIRS = ["bench", "scripts", "kaggle", "configs", "registry", "tests"]
CODE_EXT = {".py", ".yaml", ".yml", ".md", ".txt", ".toml", ".cfg", ".json"}
SKIP_PARTS = {"kernels", "__pycache__", ".git", "upload", "out", ".venv", "venv", "data", "results"}


def code_files(repo):
    files = [p for p in repo.glob("*") if p.is_file() and p.suffix in CODE_EXT]
    for d in CODE_DIRS:
        files += [p for p in (repo / d).rglob("*") if p.is_file() and p.suffix in CODE_EXT
                  and not (SKIP_PARTS & set(p.relative_to(repo).parts)) and p.stat().st_size < 2e6]
    return sorted(files)

h = code_hash(repo)
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    (tmp / "CODE_HASH.txt").write_text(h)
    with tarfile.open(tmp / "ppg2ecg-bench.tar.gz", "w:gz") as t:
        files = code_files(repo)
        for f in files:
            t.add(f, arcname=f"ppg2ecg-bench/{f.relative_to(repo).as_posix()}")
        t.add(tmp / "CODE_HASH.txt", arcname="ppg2ecg-bench/CODE_HASH.txt")
    (tmp / "CODE_HASH.txt").unlink()
    mb = (tmp / "ppg2ecg-bench.tar.gz").stat().st_size / 1e6
    print(f"code archive: {len(files)} files, {mb:.2f} MB")
    if mb > 5:
        big = sorted(files, key=lambda f: -f.stat().st_size)[:10]
        print("largest files:\n" + "\n".join(f"  {f.stat().st_size / 1e6:7.2f} MB  {f.relative_to(repo)}" for f in big))
        sys.exit("code archive is unexpectedly large (>5 MB); not uploading - move the files above out of the project")
    (tmp / "dataset-metadata.json").write_text(json.dumps(
        {"title": "ppg2ecg-bench-code", "id": f"{user}/ppg2ecg-bench-code", "licenses": [{"name": "other"}]}))
    exists = subprocess.run(["kaggle", "datasets", "status", f"{user}/ppg2ecg-bench-code"],
                            capture_output=True, text=True).returncode == 0
    cmd = (["kaggle", "datasets", "version", "-p", str(tmp), "-m", msg] if exists
           else ["kaggle", "datasets", "create", "-p", str(tmp)])          # private by default
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True)

(repo / "kaggle" / ".pushed_hash").write_text(h)
print(f"code version {h} uploaded; waiting until Kaggle has processed it ...", flush=True)
for _ in range(60):
    out = subprocess.run(["kaggle", "datasets", "status", f"{user}/ppg2ecg-bench-code"], capture_output=True, text=True)
    if "ready" in (out.stdout + out.stderr).lower():
        print("ready. Next: python kaggle/make_kernels.py ... (README section 2), then kaggle/run.py")
        break
    time.sleep(10)
else:
    print("still processing after 10 min - check `kaggle datasets status` before starting jobs")
