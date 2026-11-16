"""
Objective 5, Step 4: the model server manager. One llama-server at a time, started with the same command a plan run
uses (the tier's CPU or Vulkan build, the model file, the server arguments) plus the adapter, loaded but not applied
(every adapter of the model with --lora, and --lora-init-without-apply), so the Adapter switch costs no
reload: each request sets the scales.

    ms = ModelServer(port=8080)
    ms.ensure(server_spec)          # starts or swaps the server; returns {"started": bool, "load_ms": ...}
    ms.status()
    ms.stop()

With server_spec["fake"] the stand-in server (harness/fake_server.py) is started instead, so the whole app can be
tried without a model.
"""

import os
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from kiosk_core.engine import wait_for_server, http_json  # noqa: E402


def _port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


class ModelServer:
    def __init__(self, port=8080, log_dir=None, load_timeout=300):
        self.port, self.load_timeout = port, load_timeout
        self.log_dir = log_dir or os.path.join(ROOT, "logs", "server")
        self.proc, self.spec, self.log, self.loaded_at, self.load_ms = None, None, None, None, None
        self.lock = threading.Lock()
        self.restarts = 0

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}"

    def command(self, spec):
        if spec.get("fake"):
            return [sys.executable, os.path.join(ROOT, "harness", "fake_server.py"), "--port", str(self.port), "--demo"]
        if not spec.get("model") or not os.path.exists(spec["model"]):
            raise FileNotFoundError(f"model file not found: {spec.get('model')}")
        if not os.path.exists(spec["exe"]):
            raise FileNotFoundError(f"llama-server not found: {spec['exe']}")
        cmd = [spec["exe"], "-m", spec["model"], "--host", "127.0.0.1", "--port", str(self.port)] + list(spec["args"])
        for f in spec.get("loras") or []:        # every adapter of this model, loaded at scale 0
            cmd += ["--lora", f]
        if spec.get("loras"):
            cmd += ["--lora-init-without-apply"]
        return cmd

    @staticmethod
    def _key(spec):
        return (spec.get("fake"), spec.get("exe"), spec.get("model"), tuple(spec.get("args") or ()),
                tuple(spec.get("loras") or ()))

    def ensure(self, spec):
        with self.lock:
            if self.proc is not None and self.proc.poll() is None and self._key(spec) == self._key(self.spec or {}):
                return {"started": False}
            self._stop_locked()
            if not _port_free(self.port):
                raise RuntimeError(f"port {self.port} is in use (another llama-server?); stop it or use --llama-port")
            os.makedirs(self.log_dir, exist_ok=True)
            self.log = open(os.path.join(self.log_dir, "llama-server.log"), "a", encoding="utf-8")
            cmd = self.command(spec)
            self.log.write(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} {' '.join(cmd)}\n")
            self.log.flush()
            t = time.time()
            self.proc = subprocess.Popen(cmd, stdout=self.log, stderr=subprocess.STDOUT)
            self.spec = dict(spec)
            ready = False
            while time.time() - t < self.load_timeout:
                if self.proc.poll() is not None:
                    break
                if wait_for_server(self.url, timeout_s=3):
                    ready = True
                    break
            if not ready:
                self._stop_locked()
                raise RuntimeError("llama-server did not start; see logs/server/llama-server.log")
            self.load_ms = round((time.time() - t) * 1000)
            self.loaded_at = time.time()
            self.restarts += 1
            return {"started": True, "load_ms": self.load_ms}

    def alive(self):
        return self.proc is not None and self.proc.poll() is None

    def pid(self):
        return self.proc.pid if self.alive() else None

    def lora_adapters(self):
        try:
            return http_json(self.url + "/lora-adapters", timeout=5)
        except Exception:  # noqa: BLE001 - older or stand-in servers
            return None

    def status(self):
        rss = None
        try:
            import psutil
            if self.alive():
                rss = round(psutil.Process(self.proc.pid).memory_info().rss / 2**20, 1)
        except Exception:  # noqa: BLE001
            pass
        s = self.spec or {}
        return {"running": self.alive(), "pid": self.pid(), "fake": bool(s.get("fake")),
                "model": os.path.basename(s.get("model") or "") if s else None,
                "exe": os.path.basename(s.get("exe") or "") if s else None,
                "adapters": [os.path.basename(f) for f in s.get("loras") or []], "load_ms": self.load_ms, "rss_mb": rss, "port": self.port}

    def _stop_locked(self):
        if self.proc is not None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=10)
        self.proc = None
        if self.log:
            self.log.close()
            self.log = None
        time.sleep(0.5)

    def stop(self):
        with self.lock:
            self._stop_locked()
