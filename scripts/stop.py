"""
Stop every process started from this copy of the repository: the kiosk launchers first (so nothing is restarted),
then the apps, then llama-server. stop_all.bat runs this. Browser windows are left open.

    python scripts\\stop.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    try:
        import psutil
    except ImportError:
        print("psutil is missing: run setup.bat first.")
        return 1
    root = os.path.normcase(ROOT)
    scripts = {os.path.normcase(os.path.join(ROOT, "app", "kiosk_launcher.py")): "launcher",
               os.path.normcase(os.path.join(ROOT, "app", "server.py")): "app",
               os.path.normcase(os.path.join(ROOT, "harness", "fake_server.py")): "llama-server"}
    groups = {"launcher": [], "app": [], "llama-server": []}
    for p in psutil.process_iter(["pid", "name", "cmdline", "exe"]):
        if p.info["pid"] == os.getpid():
            continue
        name = (p.info.get("name") or "").lower()
        exe = os.path.normcase(p.info.get("exe") or "")
        if name.startswith("llama-server") and exe.startswith(root + os.sep):
            groups["llama-server"].append(p)
            continue
        if not name.startswith("python"):
            continue
        script = next((a for a in (p.info.get("cmdline") or [])[1:] if a.lower().endswith(".py")), None)
        if not script:
            continue
        if not os.path.isabs(script):
            try:
                script = os.path.join(p.cwd(), script)
            except Exception:  # noqa: BLE001 - no access to that process
                continue
        kind = scripts.get(os.path.normcase(os.path.abspath(script)))
        if kind:
            groups[kind].append(p)
    n = 0
    for kind in ("launcher", "app", "llama-server"):
        for p in groups[kind]:
            try:
                p.kill()
                n += 1
                print(f"stopped {kind} (process {p.pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"could not stop {kind} (process {p.pid}): {type(e).__name__}")
        psutil.wait_procs(groups[kind], timeout=5)
    print(f"{n} process(es) stopped." if n else "Nothing from this folder is running.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
