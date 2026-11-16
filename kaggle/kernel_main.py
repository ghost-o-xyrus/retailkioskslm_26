"""
Runs ON KAGGLE as the script of a private notebook made by kaggle/push_job.py. Do not run it on the laptop.

What it does:
  1. finds the project bundle (project.zip, from the private dataset <user>/slm-kiosk-code) and unzips it to /tmp/proj
  2. installs the job's Python packages (the laptop's versions first, then unpinned if those fail)
  3. for llama jobs: downloads the Linux CPU build of llama.cpp matching the laptop's build number
  4. runs the job's commands in order, with SLM_MACHINE=kaggle-cpu (or kaggle-gpu), stopping at the first failure
  5. packs every new or changed file under the job's output paths into /kaggle/working/job_output.zip, with
     job_log.txt and status.json beside it (kaggle/pull_job.py downloads and unpacks them on the laptop)

JOB (below) is filled in by push_job.py.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile

JOB = {}   # replaced by push_job.py

INPUT = os.environ.get("KAGGLE_INPUT_DIR", "/kaggle/input")
WORK = os.environ.get("KAGGLE_WORKING_DIR", "/kaggle/working")
PROJ = os.environ.get("SLM_PROJ_DIR", "/tmp/proj")
LOG = os.path.join(WORK, "job_log.txt")


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def find(name):
    for dp, _, fs in os.walk(INPUT):
        if name in fs:
            return os.path.join(dp, name)
    return None


def run(cmd, env=None, cwd=None, deadline=None):
    """Run a shell command, logging its output. With a deadline (time.time() value), the command and everything it
    started (llama-server) is stopped at that moment, so a long job still packs its partial results before
    Kaggle's own time limit ends the session; the return code is then TIMED_OUT."""
    log(f"$ {cmd}")
    timer, hit = None, []
    with open(LOG, "a", encoding="utf-8") as f:
        p = subprocess.Popen(cmd, shell=True, cwd=cwd or PROJ, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, errors="replace", start_new_session=True)
        if deadline is not None:
            import signal
            import threading

            def stop():
                hit.append(1)
                log("time budget reached: stopping the command (its finished cases are kept)")
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(p.pid, sig)
                    except OSError:
                        pass
                    time.sleep(20)
            timer = threading.Timer(max(1.0, deadline - time.time()), stop)
            timer.daemon = True
            timer.start()
        for line in p.stdout:
            sys.stdout.write(line)
            f.write(line)
        p.wait()
    if timer:
        timer.cancel()
    return TIMED_OUT if hit else p.returncode


TIMED_OUT = -999


def install(job):
    if os.environ.get("SLM_SKIP_PIP") or not job.get("pip"):
        return
    if job.get("uninstall"):     # preinstalled packages that break the job's imports (e.g. diffusers via optimum)
        run(f"{sys.executable} -m pip uninstall -y -q " + " ".join(job["uninstall"]))
    # a package given with a version rule ("transformers>=5") is installed as given, never pinned to the laptop's
    names = {p.lower() for p in job["pip"] if re.fullmatch(r"[A-Za-z0-9_.\-]+", p)}
    pinned = [r for r in job.get("requirements", []) if r.split("==")[0].lower() in names]
    rest = [p for p in job["pip"] if p.lower() not in {r.split("==")[0].lower() for r in pinned}]
    if pinned and run(f"{sys.executable} -m pip install -q " + " ".join(f'"{r}"' for r in pinned)) != 0:
        log("pinned install failed; installing those unpinned")
        rest = list(job["pip"])
    if rest:
        run(f"{sys.executable} -m pip install -q " + " ".join(f'"{p}"' for p in rest))


LLAMA_SKIP = ("vulkan", "cuda", "rocm", "hip", "sycl", "openvino", "arm64", "aarch64", "musa", "s390", "kompute",
              "opencl", "cann", "macos", "win", "xcframework")


def _release_assets(api_url):
    with urllib.request.urlopen(urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"}),
                                timeout=30) as r:
        rel = json.load(r)
    return rel.get("tag_name"), [(a["name"], a["browser_download_url"]) for a in rel.get("assets", [])]


def _pick_linux_cpu(assets):
    """The plain Linux x64 CPU build, whatever the release calls it (.zip or .tar.gz)."""
    ok = [(n, u) for n, u in assets if re.search(r"(ubuntu|linux)", n, re.I) and re.search(r"x64|x86_64|amd64", n, re.I)
          and n.endswith((".zip", ".tar.gz", ".tgz")) and not any(k in n.lower() for k in LLAMA_SKIP)]
    return sorted(ok, key=lambda nu: len(nu[0]))           # the shortest name is the plain build


def _unpack(path, dest):
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            z.extractall(dest)
    else:
        import tarfile
        with tarfile.open(path) as t:
            try:
                t.extractall(dest, filter="data")
            except TypeError:                       # Python without extraction filters
                t.extractall(dest)


def _found_server(dest):
    exe = next(iter(sorted(glob.glob(os.path.join(dest, "**", "llama-server"), recursive=True), key=len)), None)
    if exe:
        os.chmod(exe, 0o755)
        d = os.path.dirname(exe)
        os.environ["LD_LIBRARY_PATH"] = d + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
    return exe


def _build_from_source(ver):
    """Last resort: build llama-server for this CPU from the same release tag (about 5-10 minutes)."""
    src = "/tmp/llama-src"
    if shutil.which("cmake") is None:
        run(f"{sys.executable} -m pip install -q cmake")
    if not os.path.isdir(src):
        branch = f"--branch {ver} " if ver and ver != "latest" else ""
        if run(f"git clone --depth 1 {branch}https://github.com/ggml-org/llama.cpp {src}", cwd="/tmp") != 0 and branch:
            run(f"git clone --depth 1 https://github.com/ggml-org/llama.cpp {src}", cwd="/tmp")
    if run("cmake -B build -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DGGML_NATIVE=ON "
           "-DCMAKE_BUILD_TYPE=Release", cwd=src) != 0:
        return None
    if run(f"cmake --build build --target llama-server -j {os.cpu_count() or 4}", cwd=src) != 0:
        return None
    return _found_server(os.path.join(src, "build"))


LLAMA_CACHE = "kaggle/_llama_build"      # inside the project: a build made once comes back with the results
BUILT = []                                # files to pack with the results (a build made in this session)
FIXED_FLAGS = ("-DGGML_NATIVE=OFF -DGGML_AVX=ON -DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_F16C=ON -DGGML_AVX512=OFF "
               "-DBUILD_SHARED_LIBS=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF "
               "-DCMAKE_BUILD_TYPE=Release")


def get_llama_fixed(job):
    """Plan jobs (Objective 3, Step 15 ladder): one llama-server build for every job, so every rung's replies come
    from the same code and the same arithmetic whatever CPU a Kaggle session lands on. Built from source at the
    laptop's release tag with fixed AVX2 flags (no per-CPU choice, unlike the release files), once; the first job
    sends the binary back with its results, and every later upload carries it, so later jobs skip the build."""
    tag = job.get("llama_version")
    if not tag:
        raise SystemExit("no llama.cpp tag for this job (push_job.py reads it from llama-cpu\\llama-server --version)")
    key = f"{tag}-avx2"
    cached = os.path.join(PROJ, LLAMA_CACHE, key, "llama-server")
    if os.path.exists(cached):
        os.chmod(cached, 0o755)
        log(f"llama-server: {cached} (fixed build {key}, made by an earlier job)")
        return cached
    src = "/tmp/llama-src"
    if shutil.which("cmake") is None:
        run(f"{sys.executable} -m pip install -q cmake")
    shutil.rmtree(src, ignore_errors=True)
    if run(f"git clone --depth 1 --branch {tag} https://github.com/ggml-org/llama.cpp {src}", cwd="/tmp") != 0:
        raise SystemExit(f"llama.cpp tag {tag} could not be cloned; no other version is used, so the ladder stays on "
                         "one build")
    log(f"building llama-server {key} from source (about 5-10 minutes, once for the whole ladder)")
    if run(f"cmake -B build {FIXED_FLAGS}", cwd=src) != 0 or \
            run(f"cmake --build build --target llama-server -j {os.cpu_count() or 4}", cwd=src) != 0:
        raise SystemExit("building llama-server failed (see the log above)")
    exe = next(iter(sorted(glob.glob(os.path.join(src, "build", "**", "llama-server"), recursive=True), key=len)), None)
    if not exe:
        raise SystemExit("the build made no llama-server")
    os.makedirs(os.path.dirname(cached), exist_ok=True)
    shutil.copy2(exe, cached)
    os.chmod(cached, 0o755)
    BUILT.append(cached)
    log(f"llama-server: {cached} (fixed build {key}, built in this session; sent back with the results)")
    return cached


def get_llama_fixed_cuda(job):
    """GPU plan jobs: one CUDA llama-server for every job, built from source at the laptop's tag for the T4
    (compute capability 7.5) only, once; it comes back with the first job's results like the CPU build. A session
    that is not on T4s stops before any run, so every GPU rung runs on the same card and build."""
    tag = job.get("llama_version")
    if not tag:
        raise SystemExit("no llama.cpp tag for this job")
    try:
        caps = subprocess.run("nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader", shell=True,
                              capture_output=True, text=True, timeout=60).stdout.strip().splitlines()
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"no GPU visible ({e})")
    log(f"GPUs: {caps}")
    if not caps or any(c.split(",")[-1].strip() != "7.5" for c in caps):
        raise SystemExit(f"this session is not on T4 GPUs ({caps}); the GPU ladder runs on T4s only")
    key = f"{tag}-cuda75"
    cached = os.path.join(PROJ, LLAMA_CACHE, key, "llama-server")
    if os.path.exists(cached):
        os.chmod(cached, 0o755)
        log(f"llama-server: {cached} (fixed build {key}, made by an earlier job)")
        return cached
    src = "/tmp/llama-src"
    # Kaggle's CMake does not know CUDA 13's library layout (finetune/kaggle_teacher.sh); CMake 4.1+ does
    run(f"{sys.executable} -m pip install -q -U 'cmake>=4.1'")
    shutil.rmtree(src, ignore_errors=True)
    if run(f"git clone --depth 1 --branch {tag} https://github.com/ggml-org/llama.cpp {src}", cwd="/tmp") != 0:
        raise SystemExit(f"llama.cpp tag {tag} could not be cloned")
    libcuda = next((c for c in ("/usr/local/cuda/targets/x86_64-linux/lib/stubs/libcuda.so",
                                "/usr/local/cuda/lib64/stubs/libcuda.so", "/usr/lib/x86_64-linux-gnu/libcuda.so",
                                "/usr/lib/x86_64-linux-gnu/libcuda.so.1", "/usr/local/nvidia/lib64/libcuda.so.1")
                    if os.path.exists(c)), None)
    extra = f"-DCUDA_cuda_driver_LIBRARY={libcuda}" if libcuda else ""
    log(f"building CUDA llama-server {key} from source (about 15-25 minutes, once for the whole GPU ladder)")
    flags = ("-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=75 -DGGML_NATIVE=OFF -DGGML_AVX=ON -DGGML_AVX2=ON "
             "-DGGML_FMA=ON -DGGML_F16C=ON -DGGML_AVX512=OFF -DBUILD_SHARED_LIBS=OFF -DLLAMA_CURL=OFF "
             "-DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DCMAKE_BUILD_TYPE=Release")
    if run(f"cmake -B build {flags} {extra}", cwd=src) != 0 or \
            run(f"cmake --build build --target llama-server -j {os.cpu_count() or 4}", cwd=src) != 0:
        raise SystemExit("building the CUDA llama-server failed (see the log above)")
    exe = next(iter(sorted(glob.glob(os.path.join(src, "build", "**", "llama-server"), recursive=True), key=len)), None)
    if not exe:
        raise SystemExit("the build made no llama-server")
    os.makedirs(os.path.dirname(cached), exist_ok=True)
    shutil.copy2(exe, cached)
    os.chmod(cached, 0o755)
    BUILT.append(cached)
    log(f"llama-server: {cached} (fixed build {key}, built in this session; sent back with the results)")
    return cached


def get_llama(job):
    """A Linux CPU llama-server: the laptop's release if Kaggle can get it, else the latest release, else built
    from source. The log says which, so a mismatch with the laptop's build is visible."""
    ver = job.get("llama_version") or "latest"
    dest = "/tmp/llama"
    os.makedirs(dest, exist_ok=True)
    # 1. the release file by its usual name, with no GitHub API call (Kaggle's shared addresses often hit the
    #    API's hourly limit); the latest release's tag comes from the /releases/latest redirect
    tag = ver
    if tag == "latest":
        try:
            with urllib.request.urlopen("https://github.com/ggml-org/llama.cpp/releases/latest", timeout=30) as r:
                tag = r.geturl().rstrip("/").rsplit("/", 1)[-1]
        except Exception as e:  # noqa: BLE001
            log(f"could not find the latest llama.cpp tag: {e}")
            tag = None
    for ext in (".tar.gz", ".zip"):
        if not tag:
            break
        name = f"llama-{tag}-bin-ubuntu-x64{ext}"
        url = f"https://github.com/ggml-org/llama.cpp/releases/download/{tag}/{name}"
        try:
            log(f"downloading {name}")
            path = os.path.join(dest, name)
            urllib.request.urlretrieve(url, path)
            _unpack(path, dest)
            exe = _found_server(dest)
            if exe:
                log(f"llama-server: {exe} ({'same build as the laptop' if tag == ver else 'NOT the laptop build: ' + tag})")
                return exe
        except Exception as e:  # noqa: BLE001
            log(f"{name}: {e}")
    # 2. the GitHub API (any asset naming), 3. built from source
    tries = []
    if ver != "latest":
        tries.append(f"https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/{ver}")
    tries.append("https://api.github.com/repos/ggml-org/llama.cpp/releases/latest")
    for api_url in tries:
        try:
            tag, assets = _release_assets(api_url)
        except Exception as e:  # noqa: BLE001
            log(f"could not list {api_url}: {e}")
            continue
        picks = _pick_linux_cpu(assets)
        if not picks:
            log(f"release {tag}: no Linux x64 CPU build among {len(assets)} assets: "
                + ", ".join(n for n, _ in assets[:40]))
            continue
        for name, url in picks[:2]:
            try:
                log(f"downloading {name} (release {tag})")
                path = os.path.join(dest, name)
                urllib.request.urlretrieve(url, path)
                _unpack(path, dest)
                exe = _found_server(dest)
                if exe:
                    same = ver != "latest" and tag == ver
                    log(f"llama-server: {exe} ({'same build as the laptop' if same else 'NOT the laptop build: ' + str(tag)})")
                    return exe
                log(f"{name}: no llama-server inside")
            except Exception as e:  # noqa: BLE001
                log(f"failed: {e}")
    log("no usable release download; building llama-server from source")
    exe = _build_from_source(ver)
    if exe:
        log(f"llama-server: {exe} (built from source, {ver})")
        return exe
    raise SystemExit("could not get a Linux llama-server")


def snapshot(paths):
    out = {}
    for rel in paths:
        p = os.path.join(PROJ, rel)
        files = [p] if os.path.isfile(p) else [os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in fs]
        for fp in files:
            out[fp] = os.path.getmtime(fp)
    return out


def main():
    os.makedirs(WORK, exist_ok=True)
    t0 = time.time()
    job = JOB or json.load(open(find("job.json"), encoding="utf-8"))
    # the push this run belongs to: pull_job.py checks it, because Kaggle can serve the previous run's output for a
    # while after a new run ends
    status = {"job": job["name"], "ok": False, "failed_command": None, "bundle_id": job.get("bundle_id")}
    try:
        bundle = find("project.zip")
        if os.path.exists(PROJ):
            shutil.rmtree(PROJ)
        if bundle:
            with zipfile.ZipFile(bundle) as z:
                z.extractall(PROJ)
        else:   # Kaggle may have unpacked the archive itself: find the project folder by one of its files
            hit = next((dp for dp, _, fs in os.walk(INPUT) if "run_eval.py" in fs and dp.endswith("harness")), None)
            if not hit:
                raise SystemExit("project not found under " + INPUT + " (is the slm-kiosk-code dataset attached?)")
            shutil.copytree(os.path.dirname(hit), PROJ)
        got = open(os.path.join(PROJ, "bundle_id.txt"), encoding="utf-8").read().strip() \
            if os.path.exists(os.path.join(PROJ, "bundle_id.txt")) else None
        # a newer upload is fine (the queue's uploads all carry every queued job's inputs); an older one is not
        if job.get("bundle_id") and got and got < job["bundle_id"]:
            raise SystemExit(f"Kaggle attached an older upload of the code (bundle {got}, this job needs "
                             f"{job['bundle_id']}). Push the job again.")
        log(f"project unpacked to {PROJ} (bundle {got or job.get('bundle_id', '?')})")
        for rel in job.get("inputs", []):        # what arrived of the files the job asked for
            p = os.path.join(PROJ, rel)
            log(f"  input {rel}: {'present' if os.path.exists(p) else 'MISSING'}")
        install(job)
        env = dict(os.environ, SLM_MACHINE="kaggle-gpu" if job.get("gpu") else "kaggle-cpu", PYTHONUNBUFFERED="1",
                   SLM_FILE_HASHES=json.dumps(job.get("file_hashes") or {}))
        getter = {"fixed": get_llama_fixed, "fixed-cuda": get_llama_fixed_cuda}.get(job.get("llama_build"), get_llama)
        llama = getter(job) if job.get("needs_llama") else ""
        if llama:
            env["LD_LIBRARY_PATH"] = os.path.dirname(llama) + ":" + env.get("LD_LIBRARY_PATH", "")
        before = snapshot(job.get("outputs", []))
        # Kaggle ends a session after 12 hours; a job with max_minutes stops its commands in time to pack
        deadline = t0 + 60 * float(job["max_minutes"]) if job.get("max_minutes") else None
        for cmd in job["commands"]:
            cmd = cmd.replace("{LLAMA_SERVER}", llama).replace("{INPUT}", INPUT) \
                .replace("{LLAMA_VERSION}", job.get("llama_version") or "master").replace("python ", f'"{sys.executable}" ', 1)
            rc = run(cmd, env=env, deadline=deadline)
            if rc == TIMED_OUT:
                status.update(failed_command=cmd, timed_out=True)
                break
            if rc != 0:
                status["failed_command"] = cmd
                break
        else:
            status["ok"] = True
    except BaseException as e:  # noqa: BLE001 - always pack what exists
        log(f"ERROR: {type(e).__name__}: {e}")
        status["error"] = f"{type(e).__name__}: {e}"
        before = locals().get("before", {})
    after = snapshot(job.get("outputs", [])) if os.path.exists(PROJ) else {}
    changed = sorted(set(p for p, m in after.items() if before.get(p) != m) | {p for p in BUILT if os.path.exists(p)})
    with zipfile.ZipFile(os.path.join(WORK, "job_output.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for p in changed:
            z.write(p, os.path.relpath(p, PROJ).replace(os.sep, "/"))
    status.update(minutes=round((time.time() - t0) / 60, 1),
                  files=[os.path.relpath(p, PROJ).replace(os.sep, "/") for p in changed])
    with open(os.path.join(WORK, "status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f, indent=1)
    log(f"done: ok={status['ok']}, {len(changed)} files packed, {status['minutes']} min")


if __name__ == "__main__":
    main()
