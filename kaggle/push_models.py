"""
Upload GGUF model files once as the PRIVATE dataset <user>/slm-kiosk-models (only plan jobs, which run
llama-server on Kaggle, need it). Run on the laptop.

    python kaggle\\push_models.py ..\\models\\qwen3.5-2b\\Qwen3.5-2B-Q8_0.gguf
    python kaggle\\push_models.py <file> <file>            # creates the dataset, or a new version if it exists
    (--update is accepted and ignored: the dataset's own status decides; a new version replaces all its files,
    so list every model file the plan jobs need)

Files are hard-linked into kaggle/_staging/models (no copy on the same drive) and uploaded as they are, so Kaggle
runs use exactly the laptop's files. A 2.5 GB file takes a while on home upload speeds.
"""

import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from push_job import cli, username, wait_ready, STAGING, MODELS_SLUG  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--user")
    ap.add_argument("--update", action="store_true")
    a = ap.parse_args(argv)
    user = username(a.user)
    d = os.path.join(STAGING, "models")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for p in a.files:
        if not p.endswith(".gguf") or not os.path.exists(p):
            raise SystemExit(f"not a GGUF file: {p}")
        dest = os.path.join(d, os.path.basename(p))
        try:
            os.link(p, dest)
        except OSError:
            shutil.copy2(p, dest)
    with open(os.path.join(d, "dataset-metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"title": MODELS_SLUG, "id": f"{user}/{MODELS_SLUG}", "licenses": [{"name": "other"}]}, f)
    ds = f"{user}/{MODELS_SLUG}"
    # Kaggle answers "403 Forbidden" when asked for a new version of a dataset that does not exist yet, so the
    # choice between create and version is made from the dataset's status, not from --update
    exists = cli("datasets", "status", ds, check=False, capture=True).returncode == 0
    if exists:
        r = cli("datasets", "version", "-p", d, "-m", "models", "--dir-mode", "skip", check=False)
        if r.returncode != 0:
            raise SystemExit(f"Kaggle refused a new version of {ds}. Check that it is your dataset "
                             f"(https://www.kaggle.com/datasets/{ds}) and that the user name '{user}' is right.")
    else:
        if a.update:
            print(f"  {ds} does not exist yet, so it is created (not versioned)")
        cli("datasets", "create", "-p", d)          # private by default
    wait_ready(f"{user}/{MODELS_SLUG}", timeout_s=3600)
    print(f"Models dataset ready: https://www.kaggle.com/datasets/{user}/{MODELS_SLUG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
