"""Check your CapnoBase download and copy just the needed files into an upload folder.

    python kaggle/prepare_capnobase.py  "PATH/TO/CAPNOBASE/DOWNLOAD"  upload/capnobase-raw

Accepts any mix of XXXX_8min_signal.csv, XXXX_8min_signal.tab (Borealis) and XXXX_8min.mat.
It actually reads every file, so problems show up here on your laptop, not 30 minutes into a Kaggle job.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.datasets import load_capnobase  # noqa: E402

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
n, total = 0, 0.0
for rec in load_capnobase(src):
    f = next(src.rglob(rec.meta["source_file"]))
    shutil.copy2(f, dst / f.name)
    n += 1
    total += f.stat().st_size
    print(f"  {rec.subject}: {f.name:28s} PPG {len(rec.ppg) / rec.ppg_fs:6.1f}s @ {rec.ppg_fs:g} Hz | "
          f"ECG {len(rec.ecg) / rec.ecg_fs:6.1f}s @ {rec.ecg_fs:g} Hz")
print(f"\n{n} subjects copied to {dst} ({total / 1e6:.0f} MB). Expected: 42 subjects, 480 s each.")
if n != 42:
    print("WARNING: not 42 subjects - check that you downloaded every file of the benchmark.")
