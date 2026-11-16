"""Everything the Kaggle kernels do, in one place.

Each kernel's run.py only finds this code (attached as the private dataset
`ppg2ecg-bench-code`) and calls run_stage("<stage>"). Stages:

  k00  prep-data   download BIDMC / DaLiA / WESAD, read attached CapnoBase / Aurora-BP,
                   convert all to the canonical cache          -> /kaggle/working/cache
  k01  models      clone model repos (commit recorded), download released weights
                                                               -> /kaggle/working/models
  k10  smoke       versions, unit tests, CardioGAN fp32-vs-fp64 check, 2-subject run of every model
  k20  cardiogan   clean      (all data)        k21 cardiogan  robustness subset
  k30  ppgflowecg  clean      (all data)        k31 ppgflowecg robustness subset
  k40  baseline    clean + robustness (CPU)
  k50  profile     CPU size/speed profile, 1 and 4 threads, GPU hidden
  k04  models-rddm  clone RDDM, download its released weights (Google Drive, via gdown)
                   -> /kaggle/working/models_rddm
  k70/k71 rddm     clean / robustness (GPU); k23/k33/k43/k73 score MIMIC PERform AF with every model
  k80  author-eval  each released model run through its AUTHORS' preprocessing + metrics as well as ours
  k03  prep-maf    download MIMIC PERform AF (Zenodo, CC BY 4.0) -> /kaggle/working/cache_maf
  k60  info        Track 1.5 information-transfer analysis (coherence, MI/TE, PRV-HRV, probes,
                   forward-model bounds) on every cached dataset, CPU only

Environments:
  * CardioGAN runs in a uv venv: Python 3.10 + tensorflow[and-cuda] 2.15.1 + tensorflow-addons 0.23.0
    (closest pip-installable stack to the authors' TF 2.2 that still has Keras 2 and CUDA 12 wheels).
  * PPGFlowECG and the baseline run in Kaggle's own Python (3.13, preinstalled torch).
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

WORK = Path("/kaggle/working")
TMP = Path("/tmp")
CODE = Path(__file__).resolve().parents[1]          # .../ppg2ecg-bench
TF_ENV = TMP / "tfenv"
TF_PY = TF_ENV / "bin" / "python"

CARDIOGAN_REPO = "https://github.com/pritamqu/ppg2ecg-cardiogan.git"
CARDIOGAN_WEIGHTS = "https://github.com/pritamqu/ppg2ecg-cardiogan/releases/download/model_weights/cardiogan_ppg2ecg_generator.zip"
PPGFLOW_REPO = "https://github.com/PKUDigitalHealth/PPGFlowECG.git"
PPGFLOW_HF = "https://huggingface.co/XiaochengFang/PPGFlowECG/resolve/main/"
PPGFLOW_FILES = ["checkpoint-10.pt", "VAE-iter-40000.pth"]
RDDM_REPO = "https://github.com/DebadityaQU/RDDM.git"
RDDM_DRIVE = "https://drive.google.com/drive/folders/1Z7JQ5VdTrekx4lbARJNIUiR5D-4Kz7wg"
RDDM_FILES = ["rddm_main_network.pth", "rddm_condition_encoder_1.pth", "rddm_condition_encoder_2.pth"]

MAF_URLS = {f: [f"https://zenodo.org/records/6807403/files/{f}?download=1",
                f"https://zenodo.org/api/records/6807403/files/{f}/content",
                f"https://zenodo.org/record/6807403/files/{f}"]
            for f in ("mimic_perform_af_data.mat", "mimic_perform_non_af_data.mat")}

# Download candidates, tried in order. NOT verified from the dev sandbox (no access) - if all fail,
# download the dataset yourself and attach it as a private Kaggle dataset (see kaggle/README.md).
URLS = {
    "bidmc": ["https://physionet.org/static/published-projects/bidmc/bidmc-ppg-and-respiration-dataset-1.0.0.zip"],
    "dalia": ["https://archive.ics.uci.edu/static/public/495/ppg+dalia.zip"],
    "wesad": ["https://archive.ics.uci.edu/static/public/465/wesad+wearable+stress+and+affect+detection.zip",
              "https://uni-siegen.sciebo.de/s/HGdUkoNlW1Ub0Gx/download"],
}
MARKERS = {  # file that proves a raw dataset is present; the loader root is the marker's top folder
    "bidmc": "bidmc_*_Signals.csv", "capnobase": ["*_8min_signal.csv", "*_8min_signal.tab", "*_8min.mat"],
    "dalia": "S1/S1.pkl",          # DaLiA has S1..S15
    "wesad": "S17/S17.pkl",        # WESAD has S2..S17 (no S1) -> never confused with DaLiA
    "aurora_bp": "participants.tsv",
}


# ------------------------------------------------------------------ helpers
def sh(cmd, **kw):
    print("$", cmd if isinstance(cmd, str) else " ".join(map(str, cmd)), flush=True)
    return subprocess.run(cmd, shell=isinstance(cmd, str), check=True, **kw)


def sh_tail(cmd, n=25, **kw):
    """Like sh(), but keeps the last n output lines and puts them in the error (for summaries)."""
    from collections import deque
    print("$", " ".join(map(str, cmd)), flush=True)
    tail = deque(maxlen=n)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, **kw)
    for line in p.stdout:
        print(line, end="", flush=True)
        tail.append(line.rstrip())
    if p.wait() != 0:
        raise SystemExit(f"exit code {p.returncode}; last lines:\n" + "\n".join(tail))


def log_env(tag):
    info = {"stage": tag, "python": sys.version, "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    for mod in ("numpy", "scipy", "pandas", "torch", "tensorflow"):
        try:
            info[mod] = __import__(mod).__version__
        except Exception:
            info[mod] = None
    try:
        info["nvidia_smi"] = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True).stdout.strip()
    except Exception:
        info["nvidia_smi"] = None
    (WORK / "env").mkdir(parents=True, exist_ok=True)
    (WORK / "env" / f"{tag}_system.json").write_text(json.dumps(info, indent=2))
    print(json.dumps(info, indent=2), flush=True)


SEARCH_ROOTS = ["/kaggle/input/", "/tmp/unpacked/"]


def find_input(pattern, max_depth=6):
    """First file under /kaggle/input (or /tmp/unpacked) matching a glob pattern."""
    for d in range(1, max_depth + 1):
        for root in SEARCH_ROOTS:
            hits = sorted(glob.glob(root + "*/" * d + pattern))
            if hits:
                return Path(hits[0])
    return None


def unpack_inputs():
    """If Kaggle kept uploaded folders as .zip/.tar archives, extract them to /tmp/unpacked/."""
    import tarfile
    for d in range(1, 4):
        for ext in ("*.zip", "*.tar", "*.tar.gz", "*.tgz"):
            for a in glob.glob("/kaggle/input/" + "*/" * d + ext):
                if "ppg2ecg-bench" in a:
                    continue
                dest = Path("/tmp/unpacked") / Path(a).name.split(".")[0]
                if dest.exists():
                    continue
                print(f"[unpack] {a} -> {dest}", flush=True)
                dest.mkdir(parents=True)
                if a.endswith(".zip"):
                    with zipfile.ZipFile(a) as z:
                        z.extractall(dest)
                else:
                    with tarfile.open(a) as t:
                        t.extractall(dest, filter="data")


def find_dir_with(pattern):
    if isinstance(pattern, list):  # several accepted file forms: first one found wins
        for p in pattern:
            r = find_dir_with(p)
            if r is not None:
                return r
        return None
    return _find_dir_with(pattern)


def _find_dir_with(pattern):
    """Folder to use as loader root: the directory holding the marker pattern's first component.

    e.g. pattern "S1/S1.pkl" found at /kaggle/input/x/PPG_FieldStudy/S1/S1.pkl -> .../PPG_FieldStudy
    """
    hit = find_input(pattern)
    if hit is None:
        return None
    return hit.parents[len(Path(pattern).parts) - 1]


def download(urls, dest):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    for u in urls:
        try:
            sh(["curl", "-L", "--fail", "--retry", "2", "--connect-timeout", "30",
                "--speed-limit", "10000", "--speed-time", "120", "-o", str(dest), u])  # give up fast on stalled servers
            if dest.stat().st_size > 1e6:
                return True
        except subprocess.CalledProcessError:
            print(f"   failed: {u}", flush=True)
    return False


def extract_all(path, dest):
    """Extract a zip, then any zips found inside it (DaLiA / WESAD ship nested archives)."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path) as z:
        z.extractall(dest)
    Path(path).unlink()
    while True:
        inner = [p for p in dest.rglob("*.zip")]
        if not inner:
            break
        for p in inner:
            with zipfile.ZipFile(p) as z:
                z.extractall(p.parent)
            p.unlink()


def resolve_config(out_dir, mutate=None, src="configs/kaggle_track1.yaml", need_models=True):
    """Fill path placeholders in the Kaggle config and write a run-specific copy."""
    import yaml
    text = (CODE / src).read_text()
    hit = find_input("cache/inventory.csv")         # written by k00 into /kaggle/working/cache
    cache = hit.parent if hit else None
    models = find_input("models/MANIFEST.json")     # written by k01
    if cache is None or (need_models and models is None):
        raise SystemExit("Attach the outputs of kernels k00 (cache) and k01 (models) to this kernel.")
    subs = {"CACHE": str(cache)}
    if models:
        m = models.parent
        subs.update(CARDIOGAN_REPO=str(m / "ppg2ecg-cardiogan"), CARDIOGAN_WEIGHTS=str(m / "cardiogan_weights"),
                    PPGFLOW_REPO=str(m / "PPGFlowECG"), PPGFLOW_WEIGHTS=str(m / "ppgflowecg_weights"))
    rddm = find_input("models_rddm/MANIFEST.json")  # written by k04 (optional)
    if rddm:
        subs.update(RDDM_REPO=str(rddm.parent / "RDDM"), RDDM_WEIGHTS=str(rddm.parent / "rddm_weights"))
    for k, v in subs.items():
        text = text.replace(k, v)
    cfg = yaml.safe_load(text)
    if not rddm:
        cfg["models"] = [m for m in cfg["models"] if m["name"] != "rddm"]
    for m in list(cfg["models"]):                   # trained code-only models (k90-k93), optional
        tag = "TRAINED_" + m["name"].upper()
        if tag in json.dumps(m):
            hit = find_input(f"trained/{m['name']}/meta.json")
            if hit is None:
                cfg["models"].remove(m)
            else:
                m["kwargs"] = {k: (str(hit.parent) if v == tag else v) for k, v in m["kwargs"].items()}
    cfg["output"] = str(out_dir)
    bidmc_hit = find_input("cache_bidmc/inventory.csv")   # optional separate BIDMC cache from k02
    if bidmc_hit is not None:
        for d in cfg["datasets"]:
            if d["name"] == "bidmc":
                d["root"] = str(bidmc_hit.parent)
        print(f"[config] BIDMC read from {bidmc_hit.parent}", flush=True)
    maf_hit = find_input("cache_maf/inventory.csv")       # optional MIMIC PERform AF cache from k03
    keep = []
    for d in cfg["datasets"]:
        if d["name"] == "mimic_perform_af":
            if maf_hit is None:
                print("[config] mimic_perform_af not attached (k03) - skipped", flush=True)
                continue
            d["root"] = str(maf_hit.parent)
        keep.append(d)
    cfg["datasets"] = keep
    if mutate:
        mutate(cfg)
    p = WORK / f"config_{Path(out_dir).name}.yaml"
    p.write_text(yaml.safe_dump(cfg, sort_keys=False))
    print(p.read_text(), flush=True)
    return p


def setup_tf_env():
    """Python 3.10 + TF 2.15.1 (Keras 2) venv for CardioGAN. Needs internet (~3 min)."""
    if TF_PY.exists():
        return TF_PY
    sh([sys.executable, "-m", "pip", "install", "-q", "uv"])
    sh(["uv", "venv", str(TF_ENV), "--python", "3.10"])
    sh(["uv", "pip", "install", "--python", str(TF_PY),
        "tensorflow[and-cuda]==2.15.1", "tensorflow-addons==0.23.0",
        "numpy==1.26.4", "scipy==1.13.1", "pandas==2.2.3", "pyyaml==6.0.2"])
    out = subprocess.run([str(TF_PY), "-c",
                          "import tensorflow as tf, numpy, sys; print(sys.version.split()[0], tf.__version__, "
                          "numpy.__version__, tf.config.list_physical_devices('GPU'))"],
                         capture_output=True, text=True)
    print("[tfenv]", out.stdout, out.stderr[-2000:], flush=True)
    (WORK / "env").mkdir(parents=True, exist_ok=True)
    (WORK / "env" / "tfenv.txt").write_text(out.stdout + "\n" + subprocess.run(
        ["uv", "pip", "freeze", "--python", str(TF_PY)], capture_output=True, text=True).stdout)
    return TF_PY


def bench(py, cfg, *args):
    sh([str(py), str(CODE / "scripts" / "run_benchmark.py"), str(cfg), *args], cwd=str(CODE))


# ------------------------------------------------------------------ stages
def stage_k00():
    log_env("k00")
    unpack_inputs()
    raw = TMP / "raw"
    roots = {}
    for name in ("bidmc", "dalia", "wesad"):
        attached = find_dir_with(MARKERS[name])   # a manually attached copy wins over downloading
        if attached:
            roots[name] = attached
            continue
        z = raw / f"{name}.zip"
        if download(URLS[name], z):
            extract_all(z, raw / name)
            hit = sorted((raw / name).rglob(MARKERS[name]))
            roots[name] = hit[0].parents[len(Path(MARKERS[name]).parts) - 1] if hit else raw / name
        else:
            print(f"[k00] could not download {name}; attach it as a private dataset instead", flush=True)
    for name in ("capnobase", "aurora_bp"):
        r = find_dir_with(MARKERS[name])
        if r:
            roots[name] = r
        else:
            print(f"[k00] {name} not attached - skipped (see kaggle/README.md)", flush=True)
    args = [sys.executable, str(CODE / "scripts" / "prepare_datasets.py"), "--out", str(WORK / "cache")]
    for k, v in roots.items():
        args += [f"--{k}", str(v)]
    sh(args, cwd=str(CODE))
    shutil.rmtree(raw, ignore_errors=True)


def stage_k01():
    log_env("k01")
    m = WORK / "models"
    m.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for url, d in ((CARDIOGAN_REPO, "ppg2ecg-cardiogan"), (PPGFLOW_REPO, "PPGFlowECG")):
        if not (m / d).exists():
            sh(["git", "clone", "--depth", "1", url, str(m / d)])
        manifest[d] = subprocess.run(["git", "-C", str(m / d), "rev-parse", "HEAD"],
                                     capture_output=True, text=True).stdout.strip()
        shutil.rmtree(m / d / ".git", ignore_errors=True)
    z = TMP / "cg.zip"
    assert download([CARDIOGAN_WEIGHTS], z), "CardioGAN weights download failed"
    with zipfile.ZipFile(z) as f:
        f.extractall(TMP / "cg")
    idx = next((TMP / "cg").rglob("ckpt-1.index"))
    shutil.copytree(idx.parent, m / "cardiogan_weights", dirs_exist_ok=True)
    (m / "ppgflowecg_weights").mkdir(exist_ok=True)
    for f in PPGFLOW_FILES:
        assert download([PPGFLOW_HF + f], m / "ppgflowecg_weights" / f), f"HF download failed: {f}"
    manifest["files"] = {str(p.relative_to(m)): p.stat().st_size for p in m.rglob("*") if p.is_file()
                         and ("weights" in str(p))}
    (m / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


def stage_k10():
    log_env("k10")
    sh([sys.executable, str(CODE / "tests" / "test_pipeline.py")], cwd=str(CODE))
    py = setup_tf_env()

    # 1) CardioGAN: does fp32 reproduce the authors' fp64 output?
    check = WORK / "smoke" / "cardiogan_fp32_check.json"
    check.parent.mkdir(parents=True, exist_ok=True)
    cfg = resolve_config(WORK / "smoke")
    code = f"""
import sys, json, yaml, numpy as np
sys.path.insert(0, {str(CODE)!r})
from bench.models import build
from bench.datasets import LOADERS
from bench import dsp
cfg = yaml.safe_load(open({str(cfg)!r}))
kw = [m for m in cfg['models'] if m['name']=='cardiogan'][0]['kwargs']
ad = build('cardiogan', **{{**kw, 'dtype': 'float32'}}); ad.load()
rec = None
for d in cfg['datasets']:   # first dataset that actually has records in the cache
    rec = next(iter(LOADERS['cache'](d['root'], d['dataset'])), None)
    if rec is not None:
        break
if rec is None:
    raise SystemExit('cache is empty - k00 output not attached or k00 failed')
print('fp32 check on', rec.key)
xx = ad.prepare_record(dsp.resample(rec.ppg, rec.ppg_fs, 128))
nw = max(1, min(32, len(xx) // 512))
x = xx[: 512 * nw].reshape(nw, 512)
err = ad.float32_error(ad.normalize_window(x))
json.dump({{'max_abs_err_fp32_vs_fp64': err, 'versions': ad.versions}}, open({str(check)!r}, 'w'), indent=2)
print('fp32 vs fp64 max abs error:', err)
"""
    sh([str(py), "-c", code], cwd=str(CODE))

    # 2) every model, 2 subjects of each dataset, clean + one perturbation
    def small(c):
        for d in c["datasets"]:
            d["max_subjects"] = 2
        c["eval"]["profile_runs"] = 3
        c["perturbations"] = [{"name": "clean"}, {"name": "gaussian", "snr_db": 10}]
    cfg = resolve_config(WORK / "smoke", small)
    bench(py, cfg, "--models", "cardiogan")
    cfg_b = resolve_config(WORK / "smoke_torch", small)
    bench(sys.executable, cfg_b, "--models", "template_baseline", "ppgflowecg")


LONG = ["bidmc", "capnobase", "dalia", "wesad"]          # few, long recordings
ROBUST_A = ["gaussian", "motion"]                         # 5 conditions
ROBUST_B = ["baseline_wander", "low_rate", "weak_pulse", "time_shift"]   # 6 conditions


MODEL_PIP = {"rddm": ["neurokit2"]}      # imported at the top of the authors' diffusion.py


def pip_for(*models):
    pkgs = sorted({p for m in models for p in MODEL_PIP.get(m, [])})
    if pkgs:
        sh([sys.executable, "-m", "pip", "install", "-q", *pkgs])


def _model_stage(model, tag, use_tf, conditions, datasets=None):
    """Run one slice of the benchmark. Every slice stays well inside Kaggle's 12-h limit;
    results are flushed after every (dataset, condition) block anyway."""
    py = setup_tf_env() if use_tf else sys.executable
    log_env(tag)
    pip_for(model)
    cfg = resolve_config(WORK / "results" / tag)
    args = ["--models", model, "--conditions", *conditions]
    if datasets:
        args += ["--datasets", *datasets]
    bench(py, cfg, *args)


# CardioGAN is cheap (~3 GFLOP / 4-s window) -> runs on CPU jobs, saving the weekly GPU quota.
def stage_k20a(): _model_stage("cardiogan", "cardiogan_clean_long", True, ["clean"], LONG)
def stage_k20b(): _model_stage("cardiogan", "cardiogan_clean_aurora", True, ["clean"], ["aurora_bp"])
def stage_k21a(): _model_stage("cardiogan", "cardiogan_robust_a", True, ROBUST_A)
def stage_k21b(): _model_stage("cardiogan", "cardiogan_robust_b", True, ROBUST_B)

# PPGFlowECG (~70 GFLOP / 10-s window, 10 flow steps) needs the GPU.
def stage_k30a(): _model_stage("ppgflowecg", "ppgflowecg_clean_long", False, ["clean"], LONG)
def stage_k30b(): _model_stage("ppgflowecg", "ppgflowecg_clean_aurora", False, ["clean"], ["aurora_bp"])
def stage_k31a(): _model_stage("ppgflowecg", "ppgflowecg_robust_a", False, ROBUST_A)
def stage_k31b(): _model_stage("ppgflowecg", "ppgflowecg_robust_b", False, ROBUST_B)

# Baseline: all datasets in each job (it calibrates on CapnoBase), split clean / robust.
def stage_k40a(): _model_stage("template_baseline", "baseline_clean", False, ["clean"])
def stage_k40b(): _model_stage("template_baseline", "baseline_robust", False, ROBUST_A + ROBUST_B)


# ---- BIDMC top-up (when k00 ran without BIDMC): k02 builds a BIDMC-only cache, k22/k32/k42 score it.
ALL_CONDITIONS = ["clean"] + ROBUST_A + ROBUST_B


def stage_k02():
    log_env("k02")
    unpack_inputs()
    root = find_dir_with(MARKERS["bidmc"])
    if root is None:
        raise SystemExit("BIDMC not attached: re-run make_kernels.py with --extra-raw <user>/bidmc-raw")
    sh([sys.executable, str(CODE / "scripts" / "prepare_datasets.py"), "--out", str(WORK / "cache_bidmc"),
        "--bidmc", str(root)], cwd=str(CODE))


def stage_k22(): _model_stage("cardiogan", "cardiogan_bidmc", True, ALL_CONDITIONS, ["bidmc"])
def stage_k32(): _model_stage("ppgflowecg", "ppgflowecg_bidmc", False, ALL_CONDITIONS, ["bidmc"])
# the baseline calibrates on CapnoBase, so CapnoBase is loaded too (its rows duplicate k40a/b and are de-duplicated on merge)
def stage_k42(): _model_stage("template_baseline", "baseline_bidmc", False, ALL_CONDITIONS, ["bidmc", "capnobase"])


def stage_k04():
    log_env("k04")
    m = WORK / "models_rddm"
    m.mkdir(parents=True, exist_ok=True)
    sh(["git", "clone", "--depth", "1", RDDM_REPO, str(m / "RDDM")])
    manifest = {"RDDM": subprocess.run(["git", "-C", str(m / "RDDM"), "rev-parse", "HEAD"],
                                       capture_output=True, text=True).stdout.strip()}
    shutil.rmtree(m / "RDDM" / ".git", ignore_errors=True)
    attached = find_input("rddm_main_network.pth")          # manual copy (if Drive refuses) wins
    w = m / "rddm_weights"
    w.mkdir(exist_ok=True)
    if attached:
        for f in RDDM_FILES:
            shutil.copy(attached.parent / f, w / f)
    else:
        sh([sys.executable, "-m", "pip", "install", "-q", "--upgrade", "gdown"])
        for attempt in range(3):                     # Google Drive often throttles automated downloads
            # (gdown >= 5 dropped --remaining-ok; folder downloads need no extra flag)
            r = subprocess.run([sys.executable, "-m", "gdown", "--folder", RDDM_DRIVE, "-O", str(TMP / "rddm_drive")])
            if r.returncode == 0 and all(next((TMP / "rddm_drive").rglob(f), None) for f in RDDM_FILES):
                break
            print(f"[k04] Drive download attempt {attempt + 1} failed; retrying in 60 s", flush=True)
            time.sleep(60)
        for f in RDDM_FILES:
            hit = next((TMP / "rddm_drive").rglob(f), None)
            if hit is None:
                raise SystemExit(f"[k04] could not download {f} from Google Drive (see the gdown messages above). Download the three rddm_*.pth "
                                 f"files by hand from {RDDM_DRIVE}, upload them as a private dataset "
                                 "(README: 'If k04 fails'), and push k04 again.")
            shutil.copy(hit, w / f)
    manifest["files"] = {f: (w / f).stat().st_size for f in RDDM_FILES}
    (m / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))


# ---- RDDM (released weights, GPU) and MIMIC PERform AF for every model
def stage_k70a(): _model_stage("rddm", "rddm_clean_long", False, ["clean"], LONG + ["mimic_perform_af"])
def stage_k70b(): _model_stage("rddm", "rddm_clean_aurora", False, ["clean"], ["aurora_bp"])
def stage_k71a(): _model_stage("rddm", "rddm_robust_a", False, ROBUST_A)
def stage_k71b(): _model_stage("rddm", "rddm_robust_b", False, ROBUST_B)
def stage_k44a(): _model_stage("zhu_dct", "zhu_clean", False, ["clean"])
def stage_k44b(): _model_stage("zhu_dct", "zhu_robust", False, ROBUST_A + ROBUST_B)
def stage_k23(): _model_stage("cardiogan", "cardiogan_maf", True, ALL_CONDITIONS, ["mimic_perform_af"])
def stage_k33(): _model_stage("ppgflowecg", "ppgflowecg_maf", False, ALL_CONDITIONS, ["mimic_perform_af"])
def stage_k43(): _model_stage("template_baseline", "baseline_maf", False, ALL_CONDITIONS, ["mimic_perform_af", "capnobase"])


def stage_k80():
    """Authors' pipelines vs ours for every released model (GPU job; CardioGAN in the TF venv)."""
    log_env("k80")
    sh([sys.executable, "-m", "pip", "install", "-q", "biosppy", "peakutils", "neurokit2"])
    sh([sys.executable, "-c", "import biosppy, neurokit2"])    # fail now, not silently per model
    py_tf = setup_tf_env()
    sh(["uv", "pip", "install", "--python", str(py_tf), "biosppy", "peakutils", "neurokit2", "scikit-learn"])
    sh([str(py_tf), "-c", "import biosppy, neurokit2"])
    cfg = resolve_config(WORK / "results" / "author_eval")
    for model, py in (("rddm", sys.executable), ("ppgflowecg", sys.executable), ("cardiogan", py_tf)):
        try:
            sh([str(py), str(CODE / "scripts" / "author_eval.py"), str(cfg), "--model", model,
                "--out", str(WORK / "results" / "author_eval")], cwd=str(CODE))
        except subprocess.CalledProcessError as e:   # one model failing must not lose the others
            print(f"[k80] {model} failed: {e}", flush=True)


# ---- code-only models: authors' recipe, our training (GPU), then Track 1 evaluation (CPU)
TRAIN_REPOS = {"chiu2020": ("chiu", "https://github.com/james77777778/ppg2ecg-pytorch.git"),
               "clep_gan": ("clep", "https://github.com/Mathematics-Analytics-Data-Science-Lab/CLEP-GAN.git"),
               "p2e_wgan": ("p2e", "https://github.com/khuongav/P2E-WGAN-ecg-ppg-reconstruction.git"),
               "yalcin2026": ("yalcin", "https://github.com/m1237/self-supervised-ppg-to-ecg.git")}
TRAIN_DEPS = ["absl-py", "biosppy", "peakutils", "tensorboard", "tensorboardX", "torch-summary", "joblib", "tqdm", "gdown"]


def _train(model, smoke=False, budget_h=None):
    short, url = TRAIN_REPOS[model]
    base = WORK / ("smoke" if smoke else "trained") / model
    repo = base / "repo"
    if not repo.exists():
        sh(["git", "clone", "--depth", "1", url, str(repo)])
        commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        shutil.rmtree(repo / ".git", ignore_errors=True)
        (base / "REPO_COMMIT.txt").write_text(f"{url}\n{commit}\n")
    args = [sys.executable, str(CODE / "scripts" / "train_model.py"), short, "--repo", str(repo), "--out", str(base),
            "--work", str(TMP / f"work_{model}")]
    if smoke:
        args.append("--smoke")
    if budget_h:
        args += ["--budget-h", str(budget_h)]
    maf = find_input("cache_maf/inventory.csv")
    if maf is not None:
        args += ["--cache-maf", str(maf.parent)]
    if model == "clep_gan":
        unpack_inputs()
        bidmc = find_dir_with(MARKERS["bidmc"])
        if bidmc is None:
            raise SystemExit("CLEP-GAN needs the BIDMC CSVs: re-run make_kernels.py with --extra-raw <user>/bidmc-raw")
        args += ["--bidmc-csv", str(bidmc)]
    sh_tail(args, cwd=str(CODE))


def stage_k89():
    """CPU smoke test of all four training recipes (tiny data, 1-2 epochs) before spending GPU hours."""
    log_env("k89")
    sh([sys.executable, "-m", "pip", "install", "-q", *TRAIN_DEPS])
    sh([sys.executable, "-c", "import biosppy"])       # biosppy imports peakutils without declaring it
    failed, status = [], {}
    for model in TRAIN_REPOS:
        print(f"\n[k89] ===== smoke test: {model} =====", flush=True)
        try:
            _train(model, smoke=True)
            status[model] = "ok"
        except (subprocess.CalledProcessError, SystemExit) as e:
            failed.append(model)
            status[model] = f"failed: {e}"
            print(f"[k89] {model} FAILED: {e}", flush=True)
    # run.py reads this file: models that passed go on to GPU training, the others are skipped
    (WORK / "smoke_status.json").write_text(json.dumps(status, indent=1))
    print(f"[k89] smoke finished; passed: {[m for m, s in status.items() if s == 'ok'] or 'none'}; "
          f"failed: {failed or 'none'}", flush=True)
    if len(failed) == len(TRAIN_REPOS):
        raise SystemExit(f"smoke failures: {failed}")


def _train_stage(model, budget_h):
    log_env(model)
    sh([sys.executable, "-m", "pip", "install", "-q", *TRAIN_DEPS])
    _train(model, budget_h=budget_h)


def stage_k90(): _train_stage("chiu2020", 2.0)
def stage_k91(): _train_stage("clep_gan", 5.0)
def stage_k92(): _train_stage("p2e_wgan", 4.0)
def stage_k93(): _train_stage("yalcin2026", 4.5)


TRAINED_MODELS = list(TRAIN_REPOS)


def _trained_eval(tag, conditions, datasets=None, only=None):
    log_env(tag)
    cfg = resolve_config(WORK / "results" / tag)
    import yaml
    present = [m["name"] for m in yaml.safe_load(open(cfg))["models"]
               if m["name"] in (only or TRAINED_MODELS)]
    print(f"[{tag}] trained models attached: {present}", flush=True)
    for model in present:
        args = ["--models", model, "--conditions", *conditions] + (["--datasets", *datasets] if datasets else [])
        try:
            bench(sys.executable, cfg, *args)
        except subprocess.CalledProcessError as e:
            print(f"[{tag}] {model} failed: {e}", flush=True)


def stage_k95a(): _trained_eval("trained_clean_long", ["clean"], LONG + ["mimic_perform_af"])
def stage_k95b(): _trained_eval("trained_clean_aurora", ["clean"], ["aurora_bp"])
def stage_k95c(): _trained_eval("trained_robust", ROBUST_A + ROBUST_B)


# k96a/b/c, k53: the same evaluations for ONE model trained later (Yalcin), without redoing the others
def stage_k96a(): _trained_eval("trained_clean_long_y", ["clean"], LONG + ["mimic_perform_af"], only=["yalcin2026"])
def stage_k96b(): _trained_eval("trained_clean_aurora_y", ["clean"], ["aurora_bp"], only=["yalcin2026"])
def stage_k96c(): _trained_eval("trained_robust_y", ROBUST_A + ROBUST_B, only=["yalcin2026"])
def stage_k53(): stage_k52(models=["yalcin2026"], tag="profile4")


def stage_k52(models=None, tag="profile3"):
    log_env(tag)
    cfg = resolve_config(WORK / "results" / tag)
    for t in (1, 4):
        for model in (models or TRAINED_MODELS):
            try:
                sh([sys.executable, str(CODE / "scripts" / "profile_models.py"), str(cfg), "--threads", str(t),
                    "--models", model, "--runs", "10",
                    "--out", str(WORK / "results" / tag / f"profile_{model}_t{t}.csv")], cwd=str(CODE))
            except subprocess.CalledProcessError as e:
                print(f"[{tag}] {model} failed: {e}", flush=True)


def stage_k03():
    log_env("k03")
    unpack_inputs()
    attached = find_dir_with("*perform*af*.mat")      # a manually attached copy wins over downloading
    raw = Path(attached) if attached else TMP / "raw_maf"
    if not attached:
        raw.mkdir(parents=True, exist_ok=True)
        failed = [f for f, urls in MAF_URLS.items() if not download(urls, raw / f)]
        if failed:
            raise SystemExit(f"Zenodo download failed for {failed}. Download them from "
                             "https://zenodo.org/records/6807403 and attach them as a private dataset, then "
                             "re-run make_kernels.py with --extra-raw <user>/<that-dataset> and push k03 again.")
    sh([sys.executable, str(CODE / "scripts" / "prepare_datasets.py"), "--out", str(WORK / "cache_maf"),
        "--mimic_perform_af", str(raw)], cwd=str(CODE))


def stage_k60():
    log_env("info")
    cfg = resolve_config(WORK / "results" / "info", need_models=False)
    sh([sys.executable, str(CODE / "scripts" / "info_analysis.py"), str(cfg), "--out", str(WORK / "results" / "info")],
       cwd=str(CODE))


def stage_k50():
    log_env("profile")
    py = setup_tf_env()
    cfg = resolve_config(WORK / "results" / "profile")
    for t in (1, 4):
        for model, interp in (("cardiogan", py), ("ppgflowecg", sys.executable), ("template_baseline", sys.executable)):
            sh([str(interp), str(CODE / "scripts" / "profile_models.py"), str(cfg), "--threads", str(t),
                "--models", model, "--runs", "10", "--out", str(WORK / "results" / "profile" / f"profile_{model}_t{t}.csv")],
               cwd=str(CODE))


def stage_k51():
    """CPU profile of the models added after k50 (RDDM needs the k04 output attached)."""
    log_env("profile2")
    pip_for("rddm")
    cfg = resolve_config(WORK / "results" / "profile2")
    for t in (1, 4):
        for model in ("rddm", "zhu_dct"):
            sh([sys.executable, str(CODE / "scripts" / "profile_models.py"), str(cfg), "--threads", str(t),
                "--models", model, "--runs", "10",
                "--out", str(WORK / "results" / "profile2" / f"profile_{model}_t{t}.csv")], cwd=str(CODE))


# What each job needs attached, checked BEFORE any work so a missing input fails in seconds.
# (Kaggle starts a job even when an input kernel is "not a valid kernel source", e.g. still running.)
INPUT_MARKERS = {"k00": "cache/inventory.csv", "k01": "models/MANIFEST.json", "k02": "cache_bidmc/inventory.csv",
                 "k03": "cache_maf/inventory.csv", "k04": "models_rddm/MANIFEST.json"}
REQUIRES = {
    "k22": ["k00", "k01", "k02"], "k32": ["k00", "k01", "k02"], "k42": ["k00", "k01", "k02"],
    "k23": ["k00", "k01", "k03"], "k33": ["k00", "k01", "k03"], "k43": ["k00", "k01", "k03"],
    "k44a": ["k00", "k01", "k02", "k03"], "k44b": ["k00", "k01", "k02", "k03"],
    "k60": ["k00", "k02", "k03"],
    "k70a": ["k00", "k01", "k02", "k03", "k04"], "k70b": ["k00", "k01", "k04"],
    "k71a": ["k00", "k01", "k02", "k03", "k04"], "k71b": ["k00", "k01", "k02", "k03", "k04"],
    "k80": ["k00", "k01", "k02", "k03", "k04"], "k51": ["k00", "k01", "k04"],
    "k89": ["k03"], "k92": ["k03"], "k93": ["k03"],
    "k95a": ["k00", "k01", "k02", "k03"], "k95b": ["k00", "k01"], "k95c": ["k00", "k01", "k02", "k03"],
    "k52": ["k00", "k01"],
    "k96a": ["k00", "k01", "k02", "k03"], "k96b": ["k00", "k01"], "k96c": ["k00", "k01", "k02", "k03"],
    "k53": ["k00", "k01"],
}
NEEDS_TRAINED = {"k95a", "k95b", "k95c", "k52", "k96a", "k96b", "k96c", "k53"}


def check_inputs(name):
    missing = [k for k in REQUIRES.get(name, []) if find_input(INPUT_MARKERS[k]) is None]
    if name in NEEDS_TRAINED and not any(find_input(f"trained/{m}/meta.json") for m in
                                         ("chiu2020", "clep_gan", "p2e_wgan", "yalcin2026")):
        missing.append("k90-k93 (no trained model attached)")
    if missing:
        raise SystemExit(
            f"[{name}] STOPPED before doing any work: the output of {missing} is not attached.\n"
            f"Most likely that job had not finished (or had failed) when this job was pushed - Kaggle then "
            f"prints 'not valid kernel sources' and runs the job without it.\n"
            f"Fix: let {missing} finish successfully, then push this job again "
            f"(python kaggle/run.py --user YOURNAME {name} does both).")


def run_stage(name):
    if f"stage_{name}" not in globals():
        raise SystemExit(f"STOPPED: the uploaded code has no job {name} - it is older than the job folders. "
                         "Run kaggle/push_code.py and kaggle/make_kernels.py (README section 2), then start it again.")
    check_inputs(name)
    t0 = time.time()
    globals()[f"stage_{name}"]()
    print(f"[{name}] done in {(time.time() - t0) / 60:.1f} min", flush=True)
