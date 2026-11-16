"""
Send a CPU job to Kaggle (run on the laptop). Uses the official `kaggle` command-line tool.

    python kaggle\\push_job.py selftest                           # first time: checks the whole path
    python kaggle\\push_job.py step9_train                        # a job from kaggle/jobs.json
    python kaggle\\push_job.py --plan harness\\plans\\X.json      # the plan's CPU runs (llama-server on Kaggle)
    python kaggle\\push_job.py step9_train --dry-run              # build everything, upload nothing

Steps:
  1. packs the project's code and data into kaggle/_staging/code/project.zip. Left out: results folders (except
     the job's listed inputs), models, llama.cpp builds, GGUF files, virtual environments, caches. Notes the
     laptop's package versions and llama.cpp build number.
  2. uploads it as a new version of the PRIVATE dataset <user>/slm-kiosk-code (created the first time) and
     waits until Kaggle has processed it
  3. pushes a PRIVATE script notebook <user>/slm-kiosk-<job> (CPU, internet on) that runs kaggle/kernel_main.py
     with this job filled in, with the code dataset attached (and <user>/slm-kiosk-models for plan jobs)
Then: python kaggle\\pull_job.py <job> --wait
"""

import argparse
import importlib.metadata as md
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STAGING = os.path.join(HERE, "_staging")
CODE_SLUG, MODELS_SLUG = "slm-kiosk-code", "slm-kiosk-models"
EXCLUDE_DIRS = {"__pycache__", ".git", ".idea", ".vscode", "models", "llama-cpu", "llama-vulkan", "node_modules",
                ".ipynb_checkpoints"}
EXCLUDE_FILES = {".kaggle_user", ".hash_cache.json"}
EXCLUDE_EXT = {".gguf", ".bin", ".safetensors", ".onnx", ".zip", ".pyc", ".log", ".xml"}
PACKAGES = ["sentence-transformers", "transformers", "tokenizers", "huggingface-hub", "openvino", "optimum",
            "optimum-intel", "onnxruntime", "numpy", "psutil", "scikit-learn"]
MAX_BUNDLE_MB = 600     # Objective 4 Step 2 uploads the retrieval models (models/ov) with the job


def kaggle_cmd():
    exe = shutil.which("kaggle")
    return [exe] if exe else [sys.executable, "-m", "kaggle"]


def cli(*args, check=True, capture=False):
    cmd = kaggle_cmd() + list(args)
    print("  > kaggle " + " ".join(args), flush=True)
    # UTF-8 for the tool's own printing: on a Windows console it otherwise crashes on characters such as "−"
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    r = subprocess.run(cmd, capture_output=capture, text=True, encoding="utf-8", errors="replace", env=env)
    if check and r.returncode != 0:
        raise SystemExit(f"kaggle command failed ({r.returncode}): {' '.join(args)}\n{(r.stderr or '') if capture else ''}")
    return r


USER_FILE = os.path.join(HERE, ".kaggle_user")     # remembered after the first --user


def username(explicit=None):
    if explicit:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            f.write(explicit.strip())
        return explicit
    if os.environ.get("KAGGLE_USERNAME"):
        return os.environ["KAGGLE_USERNAME"]
    if os.path.exists(USER_FILE):
        with open(USER_FILE, encoding="utf-8") as f:
            return f.read().strip()
    for d in (os.environ.get("KAGGLE_CONFIG_DIR"), os.path.join(os.path.expanduser("~"), ".kaggle")):
        p = os.path.join(d, "kaggle.json") if d else None
        if p and os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)["username"]
    r = cli("config", "view", check=False, capture=True)      # newer tokens: the tool knows the user name
    m = re.search(r"username:\s*(\S+)", r.stdout or "")
    if m and m.group(1).lower() not in ("none", "null"):
        return m.group(1)
    raise SystemExit("Kaggle user name not found: pass --user <name> once (it is remembered), or put kaggle.json in "
                     "%USERPROFILE%\\.kaggle\\ (see kaggle/README.md)")


def is_venv(path):
    return os.path.exists(os.path.join(path, "pyvenv.cfg"))


def bundle_files(inputs=()):
    """(absolute path, archive name) for the project's code and data, plus the job's input paths."""
    out = []
    for dp, dirs, fs in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        top = rel.split(os.sep)[0]
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith("results") and
                   not is_venv(os.path.join(dp, d)) and
                   not (top == "kaggle" and d in ("_staging", "_pulled"))]
        for fn in fs:
            if os.path.splitext(fn)[1].lower() in EXCLUDE_EXT or fn in EXCLUDE_FILES:
                continue
            p = os.path.join(dp, fn)
            out.append((p, os.path.relpath(p, ROOT)))
    for rel in inputs:
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            out.append((p, rel))
        elif os.path.isdir(p):
            for dp, _, fs in os.walk(p):
                for fn in fs:
                    fp = os.path.join(dp, fn)
                    out.append((fp, os.path.relpath(fp, ROOT)))
        else:
            print(f"  note: input {rel} does not exist on this laptop; skipped")
    seen, uniq = set(), []
    for p, a in out:
        a = a.replace(os.sep, "/")
        if a not in seen:
            seen.add(a)
            uniq.append((p, a))
    return uniq


def requirements():
    out = []
    for p in PACKAGES:
        try:
            out.append(f"{p}=={md.version(p)}")
        except md.PackageNotFoundError:
            pass
    return out


def parse_llama_version(text):
    """The release tag of a llama-server from its --version output, or None if it cannot be told.
    Older builds print 'version: 6123 (abc1234)' (tag b6123); newer ones may print 'version: 0.9.0 (abc1234)'
    (tag v0.9.0). A build made from source without version information prints 'version: 0 (unknown)': None."""
    m = re.search(r"version:[^\n]*\bbuild\s+(\d+)", text or "")     # "version: 0.9.0 (build 12110, commit ...)"
    if m and int(m.group(1)) > 1:
        return "b" + m.group(1)
    m = re.search(r"version:\s*v?(\d+\.\d+\.\d+)", text or "")
    if m:
        return "v" + m.group(1)
    m = re.search(r"version:\s*(\d+)\b", text or "")
    if m and int(m.group(1)) > 0:
        return "b" + m.group(1)
    return None


def llama_build():
    """The laptop's CPU llama-server release tag ('b6123' or 'v0.9.0'), or None (Kaggle then uses the latest)."""
    for exe in (os.path.join(os.path.dirname(ROOT), "llama-cpu", "llama-server.exe"),
                os.path.join(os.path.dirname(ROOT), "llama-cpu", "llama-server")):
        if os.path.exists(exe):
            try:
                r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=30)
                out = (r.stdout or "") + (r.stderr or "")
                tag = parse_llama_version(out)
                if tag is None:
                    line = next((x for x in out.splitlines() if "version" in x), out.strip()[:80])
                    print(f"  note: could not read a release tag from llama-server --version ({line!r}); Kaggle uses "
                          "the latest llama.cpp")
                return tag
            except Exception:  # noqa: BLE001
                pass
    return None


def file_hashes(rels):
    """sha256 of laptop files the job wants to compare with (e.g. the deployed GGUFs), cached by size and time."""
    import hashlib
    cache_p = os.path.join(HERE, ".hash_cache.json")
    try:
        with open(cache_p, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    out = {}
    for rel in rels:
        p = os.path.abspath(os.path.join(ROOT, rel))
        if not os.path.exists(p):
            print(f"  note: {p} not found; its hash is not sent")
            continue
        key = f"{p}|{os.path.getsize(p)}|{int(os.path.getmtime(p))}"
        if key not in cache:
            print(f"  hashing {os.path.basename(p)} (once) ...", flush=True)
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for block in iter(lambda: f.read(1 << 24), b""):
                    h.update(block)
            cache[key] = h.hexdigest()
        out[os.path.basename(p)] = cache[key]
    with open(cache_p, "w", encoding="utf-8") as f:
        json.dump(cache, f)
    return out


def plan_job(plan_path):
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    backend = plan.get("kaggle_backend", "cpu")          # "cuda": a T4 x2 GPU session, two runs at once
    cpu = [r for r in plan["runs"] if dict(plan.get("defaults", {}), **r).get("backend") == backend]
    if not cpu:
        raise SystemExit(f"{plan_path} has no {backend} runs; Vulkan runs stay on the laptop.")
    res = plan.get("results_dir", "results")
    inputs = ["results_retrieval/fallback_bypass/fallback.json", "results_retrieval/integration/integration.json"]
    for r in cpu:
        inputs.append(f"{res}/{r['name']}")                    # lets an interrupted run resume
        for k in ("fallback_config", "reranker_choice"):
            if r.get(k):
                inputs.append(r[k].replace("\\", "/"))
        if r.get("reranker_choice") and os.path.exists(os.path.join(ROOT, r["reranker_choice"])):
            with open(os.path.join(ROOT, r["reranker_choice"]), encoding="utf-8") as f:
                ch = json.load(f)
            if str(ch.get("reranker", "")).replace("\\", "/").startswith("models/"):
                inputs.append(ch["reranker"].replace("\\", "/"))
            if ch.get("backend") == "ovrt":            # Step 12: the OpenVINO encoder and re-ranker folders
                rr = str(ch.get("reranker", ""))
                rname = "minilm" if rr in ("", "cross-encoder/ms-marco-MiniLM-L-6-v2") else \
                    os.path.basename(os.path.normpath(rr))
                inputs += ["models/ov/bge-small", f"models/ov/{rname}"]
    for x in inputs:                                   # a model folder the laptop lacks would fail on Kaggle
        if x.startswith("models/") and not os.path.exists(os.path.join(ROOT, x)):
            raise SystemExit(f"{plan_path} needs {x}, which is not on this laptop (run retrieval\\export_openvino.py)")
    rel = os.path.relpath(plan_path, ROOT).replace("\\", "/")
    name = "plan_" + os.path.splitext(os.path.basename(plan_path))[0]
    return name, {"description": f"CPU runs of {rel}", "needs_llama": True, "needs_models": True,
                  "llama_build": plan.get("kaggle_llama_build", "release"),   # "fixed": one source build for all
                  "llama_tag_fallback": plan.get("kaggle_llama_tag"),
                  "max_minutes": float(plan.get("kaggle_max_minutes", 650)),   # packs before the 12-hour limit
                  "gpu": backend == "cuda",
                  "commands": [f"python kaggle/gpu_lanes.py {rel} --server-exe {{LLAMA_SERVER}} --models-root {{INPUT}}"
                               if backend == "cuda" else
                               f"python harness/run_plan.py {rel} --only-backend cpu --server-exe {{LLAMA_SERVER}} "
                               f"--models-root {{INPUT}}"],
                  "pip": ["sentence-transformers", "openvino", "optimum-intel", "psutil"],
                  # Kaggle's preinstalled diffusers needs a newer huggingface-hub than these pins bring, and
                  # optimum-intel imports it whenever it is installed; nothing here uses it (as in step9_train)
                  "uninstall": ["diffusers"],
                  "inputs": sorted(set(inputs)), "outputs": [f"{res}/{r['name']}" for r in cpu]}


def build_code(inputs, required=()):
    """The code dataset folder: project.zip with the code, data and the given inputs, and a fresh bundle id."""
    code = os.path.join(STAGING, "code")
    shutil.rmtree(code, ignore_errors=True)
    os.makedirs(code)
    missing = [r for r in required if not os.path.exists(os.path.join(ROOT, r))]
    if missing:
        raise SystemExit("These files the job needs are not on this laptop, so nothing was uploaded:\n  "
                         + "\n  ".join(os.path.join(ROOT, r) for r in missing))
    files = bundle_files(inputs)
    zpath = os.path.join(code, "project.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p, a in files:
            z.write(p, a)
    mb = os.path.getsize(zpath) / 1e6
    if mb > MAX_BUNDLE_MB:
        raise SystemExit(f"project.zip is {mb:.0f} MB (> {MAX_BUNDLE_MB}); something large is being packed")
    bundle_id = time.strftime("%Y%m%d-%H%M%S")
    with zipfile.ZipFile(zpath, "a") as z:              # the kernel checks it got this upload, not an older one
        z.writestr("bundle_id.txt", bundle_id)
    with open(os.path.join(code, f"bundle_{bundle_id}.txt"), "w", encoding="utf-8") as f:
        f.write(bundle_id)
    for rel in inputs:
        p = os.path.join(ROOT, rel)
        size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fs in os.walk(p) for fn in fs) if os.path.isdir(p) \
            else (os.path.getsize(p) if os.path.exists(p) else None)
        if len(inputs) <= 40:
            print(f"  input {rel}: " + (f"{size / 1e6:.1f} MB" if size is not None else "NOT FOUND"))
    return code, bundle_id, len(files), mb


def build_kernel(name, job, user, bundle_id, gpu=False):
    """The kernel folder for one job, tied to a code upload (bundle_id)."""
    kern = os.path.join(STAGING, "kernel-" + name)
    shutil.rmtree(kern, ignore_errors=True)
    os.makedirs(kern)
    gpu = bool(gpu or job.get("gpu"))
    full = dict(job, name=name, gpu=gpu, bundle_id=bundle_id, requirements=requirements(),
                llama_version=(llama_build() or job.get("llama_tag_fallback")) if job.get("needs_llama") else None,
                file_hashes=file_hashes(job.get("hash_files", [])))
    with open(os.path.join(HERE, "kernel_main.py"), encoding="utf-8") as f:
        src = f.read()
    src = src.replace("JOB = {}   # replaced by push_job.py", "JOB = json.loads(" + repr(json.dumps(full)) + ")", 1)
    with open(os.path.join(kern, "run_job.py"), "w", encoding="utf-8") as f:
        f.write(src)
    slug = "slm-kiosk-" + name.replace("_", "-").lower()
    sources = [f"{user}/{CODE_SLUG}"] + ([f"{user}/{MODELS_SLUG}"] if job.get("needs_models") else [])
    with open(os.path.join(kern, "kernel-metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"id": f"{user}/{slug}", "title": slug, "code_file": "run_job.py", "language": "python",
                   "kernel_type": "script", "is_private": True, "enable_gpu": bool(gpu), "enable_internet": True,
                   **({"machine_shape": "NvidiaTeslaT4"} if gpu else {}),          # GPU T4 x2
                   "dataset_sources": sources, "competition_sources": [], "kernel_sources": []}, f, indent=1)
    with open(os.path.join(kern, "push_record.json"), "w", encoding="utf-8") as f:
        json.dump({"kernel": f"{user}/{slug}", "bundle_id": bundle_id}, f)
    return kern, f"{user}/{slug}"


SLOT_FULL = "maximum batch"          # "Kernel push error: Maximum batch CPU session count of 5 reached."


def push_kernel(name, kern, wait_slot_min=0):
    """Push a kernel; True only if Kaggle accepted it (the tool exits 0 even when it refuses, so its words are read).
    Only an accepted push becomes the job's last push (kaggle/_staging/last_<job>.json, which pull_job.py reads).
    With wait_slot_min, a refusal for Kaggle's session limit is retried every 5 minutes for that long."""
    t = time.time()
    while True:
        r = cli("kernels", "push", "-p", kern, check=False, capture=True)
        text = ((r.stdout or "") + (r.stderr or "")).strip()
        print("  " + "\n  ".join(x for x in text.splitlines() if "outdated" not in x), flush=True)
        ok = r.returncode == 0 and "error" not in text.lower()
        if ok:
            shutil.copy(os.path.join(kern, "push_record.json"), os.path.join(STAGING, f"last_{name}.json"))
            return True, text
        if SLOT_FULL in text.lower() and time.time() - t < 60 * wait_slot_min:
            print(f"  Kaggle's {SLOT_FULL} session limit is reached; trying again in 5 minutes "
                  f"({(time.time() - t) / 60:.0f} of {wait_slot_min} min waited) ...", flush=True)
            time.sleep(300)
            continue
        return False, text


def write_code_metadata(code, user):
    with open(os.path.join(code, "dataset-metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"title": CODE_SLUG, "id": f"{user}/{CODE_SLUG}", "licenses": [{"name": "CC0-1.0"}]}, f, indent=1)


def upload_code(code, user, message):
    """A new version of the code dataset (created the first time), waited for until Kaggle serves it."""
    ds = f"{user}/{CODE_SLUG}"
    exists = cli("datasets", "status", ds, check=False, capture=True).returncode == 0
    if exists:
        cli("datasets", "version", "-p", code, "-m", message)
    else:
        cli("datasets", "create", "-p", code)          # private by default
    wait_ready(ds)
    wait_version(ds, next(f for f in os.listdir(code) if f.startswith("bundle_")))


def build(name, job, user, gpu=False):
    code, bundle_id, n, mb = build_code(job.get("inputs", []), job.get("required_inputs", []))
    write_code_metadata(code, user)
    kern, kernel_id = build_kernel(name, job, user, bundle_id, gpu)
    print(f"Packed {n} files, {mb:.1f} MB; job '{name}': {len(job['commands'])} command(s)")
    return code, kern, kernel_id


def wait_ready(ds, timeout_s=900):
    t = time.time()
    while time.time() - t < timeout_s:
        r = cli("datasets", "status", ds, check=False, capture=True)
        out = (r.stdout or "").strip().lower()
        if "ready" in out:
            return
        print(f"  dataset status: {out or r.stderr.strip()}; waiting ...", flush=True)
        time.sleep(15)
    raise SystemExit("the code dataset was not ready after 15 minutes; try again later")


def wait_version(ds, marker, timeout_s=900):
    """"datasets status" can say ready while Kaggle still serves the previous version; wait until the new version's
    marker file is listed, so the job never runs older code."""
    t = time.time()
    while time.time() - t < timeout_s:
        r = cli("datasets", "files", ds, "--page-size", "1000", check=False, capture=True)
        if r.returncode != 0:                      # an older CLI without --page-size
            r = cli("datasets", "files", ds, check=False, capture=True)
        if marker in (r.stdout or ""):
            time.sleep(10)
            return
        print(f"  waiting for Kaggle to serve the new upload ({int(time.time() - t)} s) ...", flush=True)
        time.sleep(20)
    raise SystemExit("Kaggle did not serve the new upload within 15 minutes; push again later")


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="replace")      # a log line with "−" must not crash a Windows console
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("job", nargs="?", help="a job name from kaggle/jobs.json")
    ap.add_argument("--plan", help="run this plan's CPU runs on Kaggle instead")
    ap.add_argument("--user", help="Kaggle user name (default: from kaggle.json)")
    ap.add_argument("--gpu", action="store_true", help="ask for a GPU session (off by default)")
    ap.add_argument("--dry-run", action="store_true", help="build the staging folders, upload nothing")
    ap.add_argument("--wait-slot", type=float, default=0, metavar="MIN",
                    help="if all Kaggle sessions are busy, keep trying every 5 minutes for up to MIN minutes")
    a = ap.parse_args(argv)
    if a.plan:
        name, job = plan_job(os.path.abspath(a.plan))
    else:
        with open(os.path.join(HERE, "jobs.json"), encoding="utf-8") as f:
            jobs = json.load(f)
        if a.job not in jobs:
            raise SystemExit(f"unknown job {a.job!r}; jobs: {', '.join(jobs)}")
        name, job = a.job, jobs[a.job]
    user = a.user or ("dryrun" if a.dry_run else username())
    code, kern, kernel_id = build(name, job, user, a.gpu)
    if a.dry_run:
        print(f"Dry run: staging in {STAGING}; nothing uploaded.")
        return 0
    upload_code(code, user, f"job {name}")
    ok, text = push_kernel(name, kern, a.wait_slot)
    if not ok:
        hint = (" All Kaggle CPU sessions are in use (5 at most): wait for one to end, or add --wait-slot 360 to "
                "keep trying for up to 6 hours. If kaggle\\run_queue.py is running, restart it with --parallel 4 "
                "to leave a session free.") if SLOT_FULL in text.lower() else ""
        print(f"\nKaggle did NOT start the job.{hint}")
        return 1
    print(f"\nRunning on Kaggle: https://www.kaggle.com/code/{kernel_id}")
    print(f"Next: python kaggle\\pull_job.py {name} --wait")
    return 0


if __name__ == "__main__":
    sys.exit(main())
