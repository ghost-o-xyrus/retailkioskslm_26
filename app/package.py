"""
Objective 5, Step 10: build the kiosk package for one tier, a folder that runs on its own with no network.

    python app\\package.py --tier A
    python app\\package.py --tier B
    python app\\package.py --tier A --dest D:\\kiosk_release --zip

Default destination: kiosk_release\\kiosk_tier<T>\\ next to this project (the same folder that holds llama-cpu\\,
llama-vulkan\\ and models\\). Inside it:

    slm-kiosk-catalogue\\        the code and data the app needs (no training data, no results except below)
    llama-cpu\\ or llama-vulkan\\ the tier's llama-server, copied whole
    models\\...\\*.gguf           the tier's model (and its adapters are under slm-kiosk-catalogue\\finetune)
    start_kiosk.bat             the kiosk: offline, full-screen browser, restarted if it stops
    start_lab.bat               Lab mode (offline) for staff and testing
    check_install.bat           app\\verify_install.py: every file against the manifest, packages, ports, offline
    walkthrough_offline.bat     the Step 10 walkthrough from this folder
    install_autostart.bat       start the kiosk when Windows signs in (remove_autostart.bat undoes it)
    manifest.json               every file with its size and SHA-256
    requirements_runtime.txt    the Python packages the code imports, at the versions installed here
    README_KIOSK.md             for whoever runs the kiosk

Every file the deployed setup reads (fallback thresholds, re-ranker choice, retrieval depth, the plan) is copied;
a file the setup names that is missing here stops the build, so the package can never fall back to a default
silently. The Step 9 walkthrough results are copied too, so the offline walkthrough can check that the package
gives the same replies as this project did.
"""
import argparse
import ast
import hashlib
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

CODE_DIRS = ["app", "kiosk_core", "harness", "tools", "retrieval", "router", "knowledge", "data/kiosk", "models",
             "eval"]   # eval: the system prompts and shared helpers (small)
CODE_FILES = ["data/meta.json", "README.md", "data_dictionary.md"]
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache", "node_modules"}
SKIP_EXT = {".pyc", ".pyo", ".log"}
NAME = os.path.basename(ROOT)


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def walk(src):
    for d, dirs, files in os.walk(src):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() not in SKIP_EXT:
                yield os.path.join(d, f)


def referenced(cfg, server):
    """Files the deployed setup reads, inside the project (must exist) and outside it (llama-server, model)."""
    from retrieval.knowledge_base import DEFAULT_INTEGRATION, DEFAULT_FALLBACK
    inside, must = [], []
    for key in ("fallback_config", "reranker_choice", "corpus", "fallback_config_hinglish"):
        v = cfg.get(key)
        if v:
            p = v if os.path.isabs(v) else os.path.join(ROOT, v)
            must.append(p)
            if key == "reranker_choice" and os.path.exists(p):
                rr = json.load(open(p, encoding="utf-8")).get("reranker")
                if rr and not os.path.isabs(rr) and os.path.isdir(os.path.join(ROOT, rr)):
                    inside.append(os.path.join(ROOT, rr))              # a fine-tuned re-ranker folder
    for p in (DEFAULT_INTEGRATION, DEFAULT_FALLBACK):
        if os.path.exists(p):
            inside.append(p)                                           # read when present (k for retrieval)
    for p in server.get("loras") or []:
        must.append(p)
    plans = os.path.join(ROOT, "harness", "plans")
    inside.append(plans)
    must = [os.path.abspath(p) for p in must]
    missing = [p for p in must if not os.path.exists(p)]
    return inside + must, missing


ENTRY = ["app/server.py", "app/kiosk_launcher.py", "app/walkthrough.py", "app/verify_install.py"]
SEARCH = ["", "app", "retrieval", "harness", "router", "tools", "kiosk_core", "eval"]


def runtime_imports(proj):
    """Third-party modules reachable from the kiosk's entry points (following the project's own imports, also those
    inside functions), so requirements_runtime.txt lists what the kiosk can import and nothing from other tools."""
    std = set(getattr(sys, "stdlib_module_names", ()))

    def local(name):
        parts = name.split(".")
        for d in SEARCH:
            base = os.path.join(proj, d, *parts)
            for c in (base + ".py", os.path.join(base, "__init__.py")):
                if os.path.exists(c):
                    return c
        return None
    seen, todo, third = set(), [os.path.join(proj, e) for e in ENTRY], set()
    while todo:
        f = todo.pop()
        if f in seen or not os.path.exists(f):
            continue
        seen.add(f)
        try:
            tree = ast.parse(open(f, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError):
            continue
        names = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                names += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
                names += [n.module] + [f"{n.module}.{a.name}" for a in n.names]
        for name in names:
            top = name.split(".")[0]
            if top in std or top.startswith("_"):
                continue
            hit = local(name)
            if hit:
                todo.append(hit)
            elif not local(top) and not os.path.isdir(os.path.join(proj, top)):
                third.add(top)
    return sorted(third), sorted(os.path.relpath(x, proj) for x in seen)


def requirements(mods):
    import importlib.metadata as md
    import importlib.util
    dist = md.packages_distributions()
    lines, absent = [], []
    for m in mods:
        if importlib.util.find_spec(m) is None:
            absent.append(m)
            continue
        for d in dist.get(m, []):
            try:
                lines.append(f"{d}=={md.version(d)}")
            except md.PackageNotFoundError:
                pass
    return sorted(set(lines), key=str.lower), absent


BAT_HEAD = """@echo off
setlocal
cd /d "%~dp0{name}"
set "PY={py}"
if not exist "%PY%" set "PY=python"
"""


def scripts(tier, label):
    py = sys.executable
    h = BAT_HEAD.format(name=NAME, py=py)
    startup = r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    return {
        "start_kiosk.bat": h + f'title Kiosk (Tier {tier})\n"%PY%" app\\kiosk_launcher.py --tier {tier}\n',
        "start_lab.bat": h + f'title Kiosk app, Lab mode (Tier {tier})\n'
                             f'"%PY%" app\\server.py --mode lab --tier {tier} --offline --open\n',
        "check_install.bat": h + '"%PY%" app\\verify_install.py\npause\n',
        "walkthrough_offline.bat": h + f'"%PY%" app\\verify_install.py --quick || goto :end\n'
                                       f'"%PY%" app\\walkthrough.py --tier {tier} --offline\n:end\npause\n',
        "install_autostart.bat": "@echo off\n"
                                 f'echo @call "%~dp0start_kiosk.bat" > "{startup}\\kiosk_tier{tier}.bat"\n'
                                 f'echo The kiosk (Tier {tier}) will start when Windows signs in.\npause\n',
        "remove_autostart.bat": "@echo off\n"
                                f'del "{startup}\\kiosk_tier{tier}.bat" 2>nul\n'
                                f'echo Autostart removed.\npause\n',
    }


README = """# Kiosk package: {label}

This folder runs the store kiosk on its own. It needs no network: the app refuses any connection that would leave
this computer and logs the attempt (`slm-kiosk-catalogue/logs/kiosk/offline_guard.jsonl`).

## Every day

- **Start:** double-click `start_kiosk.bat`. A small window shows the launcher's log; the browser opens full-screen
  and shows "Getting ready" for about three minutes while the model loads. Then the kiosk is ready.
- **Stop:** close the browser with Alt+F4, then press Ctrl+C in the launcher window (or close it).
- **If something stops:** nothing to do. If the model server stops, the app loads it again; if the app stops, the
  launcher starts it again within a minute. The page shows "Getting ready" meanwhile and then starts a new chat.
- **Staff calls** from the kiosk are written to `slm-kiosk-catalogue/logs/kiosk/staff_requests.log` (one line per
  ticket).

## Once

- `check_install.bat` checks every file against `manifest.json`, the Python packages, the ports (8000 and 8080 must
  be free) and the offline settings. Run it after copying this folder to another computer.
- `install_autostart.bat` makes the kiosk start when Windows signs in; `remove_autostart.bat` undoes it.
- Python packages: `requirements_runtime.txt` lists the versions this package was built with. On a new computer,
  install them while still online (`pip install -r requirements_runtime.txt`), then disconnect.

## For staff and testing

- `start_lab.bat`: Lab mode (setup picker, compare, stage and tool drawers), also offline.
- `walkthrough_offline.bat`: the full walkthrough (all design scenarios, restarts, no network use); about 15
  minutes; report in `slm-kiosk-catalogue/results_obj5/_walkthrough_step10/report.md`.

## What runs

{label}. Model: `{model}`. Server: `{exe}`. The app binds 127.0.0.1:8000 and llama-server 127.0.0.1:8080; nothing
listens on the network.
"""


def build(tier, dest, base_dir=None, with_models=True, make_zip=False):
    from config import Registry
    reg = Registry(base_dir)
    cfg, server, sel, _ = reg.resolve({"tier": tier, "pipeline": "deployed"})
    label = cfg.get("config_label", f"Deployed · Tier {tier}")
    out = os.path.join(dest, f"kiosk_tier{tier}")
    proj = os.path.join(out, NAME)
    refs, missing = referenced(cfg, server)
    ext = [os.path.dirname(server["exe"]), server["model"]]
    if with_models:
        missing += [p for p in ext if not os.path.exists(p)]
    if missing:
        sys.exit("The deployed setup reads files that are not here, so a package would not behave the same:\n  "
                 + "\n  ".join(missing))
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(proj)
    copied = []

    def put(src, dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(dst)

    for d in CODE_DIRS:
        src = os.path.join(ROOT, d)
        if os.path.isdir(src):
            for f in walk(src):
                put(f, os.path.join(proj, os.path.relpath(f, ROOT)))
    for f in CODE_FILES:
        if os.path.exists(os.path.join(ROOT, f)):
            put(os.path.join(ROOT, f), os.path.join(proj, f))
    for r in refs:
        srcs = list(walk(r)) if os.path.isdir(r) else [r]
        for f in srcs:
            dst = os.path.join(proj, os.path.relpath(f, ROOT))
            if dst not in copied:
                put(f, dst)
    adapters = os.path.join(ROOT, "finetune", "adapters_gguf")
    if os.path.isdir(adapters):                     # the tier model's adapters (Lab mode can switch them)
        short = {"A": "2b", "B": "4b"}[tier]
        for f in os.listdir(adapters):
            if f.endswith(".gguf") and short in f.lower():
                dst = os.path.join(proj, "finetune", "adapters_gguf", f)
                if dst not in copied:
                    put(os.path.join(adapters, f), dst)
    for f in ("A.json", "B.json"):                  # Step 9 results, for the package's same-replies check
        p = os.path.join(ROOT, "results_obj5", "_walkthrough_step9", f)
        if os.path.exists(p) and f[0] == tier:
            put(p, os.path.join(proj, "results_obj5", "_walkthrough_step9", f))
    if with_models:
        exe_dir = os.path.dirname(server["exe"])
        for f in walk(exe_dir):
            put(f, os.path.join(out, os.path.relpath(f, reg.base_dir)))
        put(server["model"], os.path.join(out, os.path.relpath(server["model"], reg.base_dir)))
    mods, reached = runtime_imports(proj)
    reqs, absent = requirements(mods)
    with open(os.path.join(out, "requirements_runtime.txt"), "w", encoding="utf-8") as f:
        f.write("# Python packages imported by the kiosk code, at the versions installed where it was packaged\n")
        f.write("\n".join(reqs) + "\n")
        if absent:
            f.write("# imported somewhere in the kiosk code but not installed here (paths the deployed setup does "
                    "not take): " + ", ".join(absent) + "\n")
    for name, text in scripts(tier, label).items():
        with open(os.path.join(out, name), "w", encoding="utf-8", newline="\r\n") as f:
            f.write(text)
    with open(os.path.join(out, "README_KIOSK.md"), "w", encoding="utf-8") as f:
        f.write(README.format(label=label, model=os.path.relpath(server["model"], reg.base_dir).replace("\\", "/"),
                              exe=os.path.relpath(server["exe"], reg.base_dir).replace("\\", "/")))
    files = {}
    for f in walk(out):
        rel = os.path.relpath(f, out).replace("\\", "/")
        if rel != "manifest.json":
            files[rel] = {"size": os.path.getsize(f), "sha256": sha256(f)}
    man = {"tier": tier, "label": label, "project": NAME, "with_models": with_models,
           "model": os.path.relpath(server["model"], reg.base_dir).replace("\\", "/"),
           "server_exe": os.path.relpath(server["exe"], reg.base_dir).replace("\\", "/"),
           "selection": sel, "n_files": len(files), "bytes": sum(v["size"] for v in files.values()),
           "requirements": reqs, "files": files}
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1, ensure_ascii=False)
    print(f"Tier {tier}: {len(files)} files, {man['bytes'] / 1e9:.2f} GB -> {out}")
    print(f"  {label}; model {man['model']}; {len(reqs)} Python packages in requirements_runtime.txt")
    if absent:
        print(f"  (imported on paths the deployed setup does not take, not installed here: {', '.join(absent)})")
    print(f"  {len(reached)} project modules reachable from the kiosk's entry points")
    if make_zip:
        z = out + ".zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for f in walk(out):
                zf.write(f, os.path.join(os.path.basename(out), os.path.relpath(f, out)))
        print(f"  zip: {z}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", required=True, choices=["A", "B"])
    ap.add_argument("--dest", default=None, help="default: kiosk_release next to this project")
    ap.add_argument("--base-dir", default=None, help="folder with llama-cpu/, llama-vulkan/, models/")
    ap.add_argument("--no-models", action="store_true", help="code and data only (tests)")
    ap.add_argument("--zip", action="store_true")
    a = ap.parse_args(argv)
    from config import Registry
    dest = a.dest or os.path.join(Registry(a.base_dir).base_dir, "kiosk_release")
    build(a.tier, dest, a.base_dir, with_models=not a.no_models, make_zip=a.zip)
    return 0


if __name__ == "__main__":
    sys.exit(main())
