"""Upload a local folder as a PRIVATE Kaggle dataset (creates it, or adds a new version).

    python kaggle/upload_dataset.py  <folder>  <dataset-slug>  --user YOUR_KAGGLE_USERNAME

Writes dataset-metadata.json for you, keeps sub-folders (--dir-mode tar) and keeps .tsv files
as they are (--keep-tabular; otherwise Kaggle would convert them and break the Aurora loader).
"""
import argparse
import json
import subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("folder")
ap.add_argument("slug")
ap.add_argument("--user", required=True)
a = ap.parse_args()

folder = Path(a.folder)
if "aurora" in a.slug and not any(folder.glob("measurements_*/*/*.tsv")):
    raise SystemExit(f"{folder} has no measurements_*/<pid>/*.tsv recordings - run kaggle/prepare_aurora.py first "
                     "(and check that it reports recordings copied > 0).")
(folder / "dataset-metadata.json").write_text(json.dumps(
    {"title": a.slug, "id": f"{a.user}/{a.slug}", "licenses": [{"name": "other"}]}, indent=2))
exists = subprocess.run(["kaggle", "datasets", "status", f"{a.user}/{a.slug}"],
                        capture_output=True, text=True).returncode == 0
if exists:
    cmd = ["kaggle", "datasets", "version", "-p", str(folder), "-m", "update", "-r", "tar", "-t"]
else:
    cmd = ["kaggle", "datasets", "create", "-p", str(folder), "-r", "tar", "-t"]   # private by default
print("$", " ".join(cmd))
subprocess.run(cmd, check=True)
print(f"done -> https://www.kaggle.com/datasets/{a.user}/{a.slug}  (Kaggle needs a few minutes to process it)")
