"""
Objective 5, Step 10: check a kiosk package before running it (check_install.bat runs this).

    python app\\verify_install.py            # every file's SHA-256 (about a minute with the model)
    python app\\verify_install.py --quick    # sizes only for files over 50 MB

Checks (all must pass):
  files      every file in manifest.json is present with its size (and SHA-256)
  packages   every package in requirements_runtime.txt is installed (a different version is a warning)
  ports      127.0.0.1:8000 and :8080 are free (no other kiosk or llama-server running)
  offline    the page loads nothing from the network (no http(s) address in app/static); the app and
             llama-server bind 127.0.0.1 only; the start scripts run the app offline
  browser    Edge or Chrome is found for kiosk mode (a warning only: the default browser is used otherwise)
Writes logs/kiosk/verify.json.
"""
import argparse
import hashlib
import json
import os
import re
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PKG = os.path.dirname(ROOT)
sys.path.insert(0, HERE)


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def check_files(man, quick):
    bad = []
    for rel, v in man["files"].items():
        p = os.path.join(PKG, rel)
        if not os.path.exists(p):
            bad.append(f"missing: {rel}")
        elif os.path.getsize(p) != v["size"]:
            bad.append(f"size differs: {rel}")
        elif not (quick and v["size"] > 50e6) and sha256(p) != v["sha256"]:
            bad.append(f"content differs: {rel}")
    return bad, []


def check_packages(man):
    import importlib.metadata as md
    bad, warn = [], []
    for line in man.get("requirements") or []:
        name, _, ver = line.partition("==")
        try:
            have = md.version(name)
            if ver and have != ver:
                warn.append(f"{name} {have} installed, packaged with {ver}")
        except md.PackageNotFoundError:
            bad.append(f"not installed: {name} (pip install {line})")
    return bad, warn


def check_ports(ports=(8000, 8080)):
    bad = []
    for p in ports:
        s = socket.socket()
        s.settimeout(0.5)
        if s.connect_ex(("127.0.0.1", p)) == 0:
            bad.append(f"port {p} is in use (close any running kiosk, app or llama-server)")
        s.close()
    return bad, []


def check_offline():
    bad = []
    url = re.compile(r"https?://(?!127\.0\.0\.1|localhost)[^\s\"'<>)]+", re.I)
    static = os.path.join(ROOT, "app", "static")
    for d, _, files in os.walk(static):
        for f in files:
            if f.lower().endswith((".html", ".js", ".css", ".svg", ".json")):
                txt = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
                hits = [u for u in url.findall(txt) if "www.w3.org" not in u]
                bad += [f"app/static/{f} refers to {u}" for u in hits]
    srv = open(os.path.join(ROOT, "app", "server.py"), encoding="utf-8").read()
    if 'host="127.0.0.1"' not in srv:
        bad.append("app/server.py does not bind 127.0.0.1")
    svc = open(os.path.join(ROOT, "harness", "run_plan.py"), encoding="utf-8").read()
    if '"--host", "127.0.0.1"' not in svc:
        bad.append("llama-server is not started with --host 127.0.0.1")
    launcher = open(os.path.join(ROOT, "app", "kiosk_launcher.py"), encoding="utf-8").read()
    if '"--offline"' not in launcher:
        bad.append("the kiosk launcher does not run the app offline")
    for name in ("start_kiosk.bat", "start_lab.bat"):
        p = os.path.join(PKG, name)
        if os.path.exists(p):
            t = open(p, encoding="utf-8").read()
            if "--online" in t or ("server.py" in t and "--offline" not in t):
                bad.append(f"{name} does not run offline")
    return bad, []


def check_browser():
    from kiosk_launcher import browser_cmd
    c = browser_cmd("http://127.0.0.1:8000", os.path.join(ROOT, "logs", "kiosk", "browser_profile"))
    return [], ([] if c else ["no Edge or Chrome found: the default browser opens (F11 for full screen)"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args(argv)
    mp = os.path.join(PKG, "manifest.json")
    if not os.path.exists(mp):
        sys.exit("No manifest.json next to this project: run this inside a kiosk package (app\\package.py builds one).")
    man = json.load(open(mp, encoding="utf-8"))
    print(f"Kiosk package: {man['label']} ({man['n_files']} files, {man['bytes'] / 1e9:.2f} GB)")
    res, ok = {}, True
    for name, fn in (("files", lambda: check_files(man, a.quick)), ("packages", lambda: check_packages(man)),
                     ("ports", check_ports), ("offline", check_offline), ("browser", check_browser)):
        bad, warn = fn()
        res[name] = {"problems": bad, "warnings": warn}
        ok &= not bad
        print(f"  {name:9s} {'ok' if not bad else 'FAIL'}" + "".join(f"\n      - {x}" for x in bad[:20])
              + "".join(f"\n      (warning) {x}" for x in warn[:10]))
    os.makedirs(os.path.join(ROOT, "logs", "kiosk"), exist_ok=True)
    with open(os.path.join(ROOT, "logs", "kiosk", "verify.json"), "w", encoding="utf-8") as f:
        json.dump({"ok": ok, "quick": a.quick, "checks": res}, f, indent=1)
    print("All checks passed." if ok else "Some checks failed; see above.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
