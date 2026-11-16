"""
Objective 5, Step 10: start the kiosk and keep it running. The start scripts (start_kiosk_A.bat, start_kiosk_B.bat)
call this.

  - starts the app (app/server.py) in Kiosk mode for the tier, offline (kiosk_core/offline.py), with the
    model loaded at start-up; the app itself restarts llama-server if that stops
  - restarts the app if it stops (waits 5 s, then 10, 20 ... at most 60 s between tries; logged)
  - opens the browser full-screen once the app answers (Edge in kiosk mode, else Chrome, else the default browser);
    the page shows "Getting ready" until the model is loaded, and starts a new chat after a restart
  - Ctrl+C (or closing its window) stops the app and llama-server

    python app\\kiosk_launcher.py --tier A
    python app\\kiosk_launcher.py --tier B --no-browser

Logs: logs/kiosk/launcher.log, logs/kiosk/app.log, logs/kiosk/offline_guard.jsonl, logs/kiosk/staff_requests.log.

Two kiosks side by side (the repository's start_tier_a.bat and start_tier_b.bat): give each its own ports and log
folder, and open it in a window instead of full-screen:

    python app\\kiosk_launcher.py --tier A --port 8001 --llama-port 8081 --log-dir logs\\tier_a --windowed --window left
    python app\\kiosk_launcher.py --tier B --port 8002 --llama-port 8082 --log-dir logs\\tier_b --windowed --window right

With --log-dir, every log of that kiosk (also llama-server's and the per-turn app logs) goes into that folder.
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOGS = os.path.join(ROOT, "logs", "kiosk")
STOP = {"now": False}


def log(msg):
    os.makedirs(LOGS, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"
    print(line, flush=True)
    with open(os.path.join(LOGS, "launcher.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def answering(url, timeout=2):
    try:
        with urllib.request.urlopen(url + "/api/ready", timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:  # noqa: BLE001 - not up yet
        return None


def screen_size():
    """Usable screen size in the units the browser's --window-size takes (Windows; 1920x1040 elsewhere)."""
    try:
        import ctypes
        u = ctypes.windll.user32
        return int(u.GetSystemMetrics(0)), int(u.GetSystemMetrics(1)) - 48      # minus the taskbar
    except Exception:  # noqa: BLE001 - not Windows
        return 1920, 1040


def window_args(slot):
    """--window-size / --window-position for a windowed kiosk: the left or right half of the screen, or centred."""
    w, h = screen_size()
    if slot in ("left", "right"):
        return [f"--window-size={w // 2},{h}", f"--window-position={0 if slot == 'left' else w // 2},0"]
    ww, hh = min(w, 1100), min(h, 900)
    return [f"--window-size={ww},{hh}", f"--window-position={(w - ww) // 2},{max(0, (h - hh) // 2)}"]


def browser_cmd(url, profile, windowed=False, slot="centre"):
    """Edge or Chrome in kiosk (full-screen, no address bar) mode, with its own profile; None if neither is found.
    windowed: an app window (no address bar, not full-screen) placed by `slot`, so two kiosks fit side by side."""
    pf = [os.environ.get(k) for k in ("ProgramFiles(x86)", "ProgramFiles", "LOCALAPPDATA") if os.environ.get(k)]
    edge = [os.path.join(p, "Microsoft", "Edge", "Application", "msedge.exe") for p in pf] + \
        [shutil.which("msedge") or "", shutil.which("microsoft-edge") or ""]
    chrome = [os.path.join(p, "Google", "Chrome", "Application", "chrome.exe") for p in pf] + \
        [shutil.which("google-chrome") or "", shutil.which("chromium") or ""]
    common = [f"--user-data-dir={profile}", "--no-first-run", "--disable-features=Translate",
              "--overscroll-history-navigation=0", "--disable-pinch"]
    for exe in edge:
        if exe and os.path.exists(exe):
            if windowed:
                return [exe, f"--app={url}"] + window_args(slot) + common
            return [exe, "--kiosk", url, "--edge-kiosk-type=fullscreen"] + common
    for exe in chrome:
        if exe and os.path.exists(exe):
            if windowed:
                return [exe, f"--app={url}"] + window_args(slot) + common
            return [exe, "--kiosk", url] + common
    return None


def app_cmd(a):
    cmd = [sys.executable, os.path.join(HERE, "server.py"), "--mode", a.mode, "--tier", a.tier,
           "--port", str(a.port), "--llama-port", str(a.llama_port)]
    if a.base_dir:
        cmd += ["--base-dir", a.base_dir]
    if a.fake:
        cmd += ["--fake"]
    if not a.online:
        cmd += ["--offline", "--net-log", os.path.join(LOGS, "offline_guard.jsonl")]
    if a.log_dir:
        cmd += ["--log-dir", LOGS]
    return cmd


def kill_tree(proc):
    try:
        import psutil
        p = psutil.Process(proc.pid)
        kids = p.children(recursive=True)
        for k in kids + [p]:
            try:
                k.kill()
            except psutil.NoSuchProcess:
                pass
        psutil.wait_procs(kids + [p], timeout=10)
    except Exception:  # noqa: BLE001 - psutil missing or the process is gone
        try:
            proc.kill()
        except Exception:  # noqa: BLE001
            pass


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", required=True, choices=["A", "B"])
    ap.add_argument("--mode", default="kiosk", choices=["kiosk", "lab"])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--llama-port", type=int, default=8080)
    ap.add_argument("--base-dir", default=None, help="folder with llama-cpu/ or llama-vulkan/ and models/")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--online", action="store_true", help="do not install the offline guard")
    ap.add_argument("--fake", action="store_true", help="stand-in model (tests only)")
    ap.add_argument("--log-dir", default=None,
                    help="folder for every log of this kiosk (default: logs/kiosk for the launcher's own logs, "
                         "logs/app and logs/server for the app's). Give each kiosk its own when two run side by side")
    ap.add_argument("--windowed", action="store_true",
                    help="open the browser in a window instead of full-screen (for running two kiosks side by side)")
    ap.add_argument("--window", default="centre", choices=["left", "right", "centre"],
                    help="with --windowed: which part of the screen the window takes")
    a = ap.parse_args(argv)
    global LOGS
    if a.log_dir:
        LOGS = os.path.abspath(a.log_dir)
    os.makedirs(LOGS, exist_ok=True)
    env = dict(os.environ, SLM_STAFF_LOG=os.environ.get("SLM_STAFF_LOG") or os.path.join(LOGS, "staff_requests.log"),
               HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", PYTHONUNBUFFERED="1")
    url = f"http://127.0.0.1:{a.port}"

    def stop(*_):
        STOP["now"] = True
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, stop)

    if answering(url):
        log(f"something already answers at {url}; close the other kiosk or app first")
        return 2
    opened, starts, wait = False, 0, 5
    proc = None
    try:
        while not STOP["now"]:
            starts += 1
            log(f"start {starts}: {' '.join(app_cmd(a))}")
            out = open(os.path.join(LOGS, "app.log"), "a", encoding="utf-8")
            proc = subprocess.Popen(app_cmd(a), stdout=out, stderr=subprocess.STDOUT, env=env, cwd=ROOT)
            with open(os.path.join(LOGS, "app.pid"), "w") as f:
                f.write(str(proc.pid))
            t0 = time.time()
            ready_logged = False
            while proc.poll() is None and not STOP["now"]:
                r = answering(url)
                if r and not opened and not a.no_browser:
                    cmd = browser_cmd(url, os.path.join(LOGS, "browser_profile"), a.windowed, a.window)
                    if cmd:
                        subprocess.Popen(cmd)
                        log(f"browser: {os.path.basename(cmd[0])} "
                            + ("in a window" if a.windowed else "in kiosk mode (Alt+F4 closes it)"))
                    else:
                        webbrowser.open(url)
                        log("browser: no Edge or Chrome found; opened the default browser (press F11 for full screen)")
                    opened = True
                if r and r.get("state") == "ready" and not ready_logged:
                    log(f"ready in {time.time() - t0:.0f} s: {r.get('label')}")
                    ready_logged, wait = True, 5
                time.sleep(1)
            if STOP["now"]:
                break
            log(f"the app stopped (exit {proc.returncode}); see logs/kiosk/app.log. Restarting in {wait} s")
            for _ in range(wait):
                if STOP["now"]:
                    break
                time.sleep(1)
            wait = min(60, wait * 2)
    finally:
        if proc and proc.poll() is None:
            log("stopping the app")
            kill_tree(proc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
