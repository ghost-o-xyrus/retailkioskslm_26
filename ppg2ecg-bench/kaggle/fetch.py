"""Download the useful outputs (results, logs, environment info - NOT the big cache/weights) of kernels.

    python kaggle/fetch.py --user YOUR_KAGGLE_USERNAME k10
    python kaggle/fetch.py --user YOUR_KAGGLE_USERNAME k20 k21 k30 k31 k40 k50

Files land in out/<short name>/ .
"""
import argparse
import re
import subprocess

from wait import SLUGS  # same folder

PATTERN = r"(results/.*|smoke[^/]*/(?!.*\.(pth|pt|npy)$)(?!.*/repo/).*|trained/[^/]+/(meta\.json|train_log\.txt|REPO_COMMIT\.txt)|env/.*|smoke_status\.json|.*inventory\.csv|.*MANIFEST\.json|.*\.log)$"

ap = argparse.ArgumentParser()
ap.add_argument("--user", required=True)
ap.add_argument("kernels", nargs="+")
a = ap.parse_args()
for k in a.kernels:
    token = None
    for _ in range(100):  # outputs are paginated (k00 writes thousands of cache files)
        cmd = ["kaggle", "kernels", "output", f"{a.user}/{SLUGS.get(k, k)}", "-p", f"out/{k}", "-o",
               "--file-pattern", PATTERN, "--page-size", "200"] + (["--page-token", token] if token else [])
        print("$", " ".join(cmd), flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout[-1500:], r.stderr[-1500:], flush=True)
        m = re.search(r"(?i)page[ _-]?token\W+([A-Za-z0-9_\-=]+)", r.stdout + r.stderr)
        if not m or m.group(1) == token:
            break
        token = m.group(1)
