"""Copy only what Track 1 needs from the full Aurora-BP download into a small upload folder.

    python kaggle/prepare_aurora.py  <folder you downloaded from Zenodo>  upload/aurora-bp-raw

* Works whatever the folder layout is: it searches the whole download for the in-lab
  ("initial") 30-s recordings, e.g. o004.initial.Supine_2.tsv.
* If the download still contains .zip archives, they are opened automatically.
* Writes them in the layout the loader expects:
      participants.tsv
      measurements_oscillometric/<pid>/<pid>.initial.<name>.tsv   (pid starts with 'o')
      measurements_auscultatory/<pid>/<pid>.initial.<name>.tsv    (pid starts with 'a')
* Stops with an error (and shows what it found) if there are no recordings - so you never
  upload an empty dataset again.
Works on Windows/macOS/Linux.
"""
import shutil
import sys
import tarfile
import zipfile
from collections import Counter
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
if not src.exists():
    sys.exit(f"{src} does not exist")


def wanted(name):
    return name.endswith(".tsv") and ".initial." in name


# 1) participants.tsv (loose file or inside a zip)
parts = sorted(src.rglob("participants.tsv"))
dst.mkdir(parents=True, exist_ok=True)
for old in dst.glob("measurements_*"):          # start clean if re-run
    shutil.rmtree(old)
if parts:
    shutil.copy2(parts[0], dst / "participants.tsv")


def target_for(file_name):
    pid = file_name.split(".")[0]
    proto = "auscultatory" if pid.startswith("a") else "oscillometric"
    return dst / f"measurements_{proto}" / pid / file_name


# 2) loose .tsv recordings anywhere under src
n = 0
for f in src.rglob("*.tsv"):
    if wanted(f.name):
        t = target_for(f.name)
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, t)
        n += 1

# 3) recordings still inside .zip archives
zips = sorted(src.rglob("*.zip"))
for z in zips:
    try:
        with zipfile.ZipFile(z) as zf:
            for info in zf.infolist():
                name = Path(info.filename).name
                if name == "participants.tsv" and not (dst / "participants.tsv").exists():
                    (dst / "participants.tsv").write_bytes(zf.read(info))
                elif wanted(name):
                    t = target_for(name)
                    if not t.exists():
                        t.parent.mkdir(parents=True, exist_ok=True)
                        t.write_bytes(zf.read(info))
                        n += 1
    except zipfile.BadZipFile:
        print(f"  (could not open {z.name} - not a valid zip)")

# 3b) recordings inside .tar / .tar.gz / .tgz archives
tars = sorted(p for p in src.rglob("*") if p.is_file() and (p.name.endswith((".tar", ".tar.gz", ".tgz"))))
for tpath in tars:
    try:
        with tarfile.open(tpath) as tf:
            for m in tf.getmembers():
                name = Path(m.name).name
                if not m.isfile():
                    continue
                if name == "participants.tsv" and not (dst / "participants.tsv").exists():
                    (dst / "participants.tsv").write_bytes(tf.extractfile(m).read())
                elif wanted(name):
                    t = target_for(name)
                    if not t.exists():
                        t.parent.mkdir(parents=True, exist_ok=True)
                        t.write_bytes(tf.extractfile(m).read())
                        n += 1
    except tarfile.TarError:
        print(f"  (could not open {tpath.name} - not a valid tar)")
zips = zips + tars

# 4) report / sanity checks
has_part = (dst / "participants.tsv").exists()
subjects = {p.name for p in dst.glob("measurements_*/*")}
size = sum(p.stat().st_size for p in dst.rglob("*") if p.is_file()) / 1e9
print(f"participants.tsv: {'found' if has_part else 'NOT FOUND'}")
print(f"in-lab recordings copied: {n}  from {len(subjects)} participants  ->  {dst}  ({size:.2f} GB)")
if not has_part or n == 0:
    tsv = list(src.rglob("*.tsv"))
    kinds = Counter(".".join(p.name.split(".")[1:2]) for p in tsv)
    print("\nNOTHING TO UPLOAD - please send Claude this information:")
    print(f"  .tsv files found: {len(tsv)}   archives (.zip/.tar) found: {len(zips)}")
    print("  -> if you only see participants/features/measurements_*.tsv, the per-participant recordings")
    print("     (the big archive files on the Zenodo page) were not downloaded yet.")
    print(f"  most common phase names in file names: {kinds.most_common(8)}")
    print("  first 15 files under your folder:")
    for p in sorted(x for x in src.rglob("*") if x.is_file())[:15]:
        print("   ", p.relative_to(src))
    sys.exit(1)
print("OK - now run upload_dataset.py on this folder.")
