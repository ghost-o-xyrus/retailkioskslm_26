"""
Objective 5, Step 10: the offline guard. With it installed, this Python process can only connect to its own machine
(127.0.0.0/8, ::1, localhost). Any other connection, or a name lookup for another host, is refused with an OSError
and written to a log (one JSON line each), so a test can show the kiosk made no network attempt.

    from kiosk_core import offline; offline.install(log_path)

The server installs it with --offline; the start scripts and the offline walkthrough use that. It also sets the
model libraries' offline switches (HF_HUB_OFFLINE, TRANSFORMERS_OFFLINE). llama-server is a separate program; it
binds 127.0.0.1 only and is started by this process.
"""
import ipaddress
import json
import os
import socket
import threading
import time
import traceback

_LOCK = threading.Lock()
STATE = {"installed": False, "log": None, "attempts": 0}
LOCAL_NAMES = {"localhost", "localhost.localdomain", "ip6-localhost", ""}


def _is_local(host):
    if host is None:
        return True
    if isinstance(host, bytes):
        host = host.decode("ascii", "ignore")
    h = str(host).strip("[]").lower()
    if h in LOCAL_NAMES:
        return True
    try:
        ip = ipaddress.ip_address(h.split("%")[0])
        return ip.is_loopback or (ip.version == 6 and ip.ipv4_mapped is not None and ip.ipv4_mapped.is_loopback)
    except ValueError:
        return False


def _record(kind, target):
    with _LOCK:
        STATE["attempts"] += 1
        if STATE["log"]:
            try:
                with open(STATE["log"], "a", encoding="utf-8") as f:
                    f.write(json.dumps({"t": round(time.time(), 3), "kind": kind, "target": str(target)[:200],
                                        "where": "".join(traceback.format_stack(limit=6)[:-2])[-600:]}) + "\n")
            except OSError:
                pass


def install(log_path=None):
    if STATE["installed"]:
        return
    STATE.update(installed=True, log=log_path)
    if log_path:
        os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
    for k in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_DATASETS_OFFLINE"):
        os.environ[k] = "1"

    real_connect, real_connect_ex = socket.socket.connect, socket.socket.connect_ex
    real_getaddrinfo, real_gethostbyname = socket.getaddrinfo, socket.gethostbyname

    def host_of(address):
        if isinstance(address, tuple) and address:
            return address[0]
        return None                                   # a Unix socket path: local

    def connect(self, address):
        if self.family in (socket.AF_INET, socket.AF_INET6) and not _is_local(host_of(address)):
            _record("connect", address)
            raise OSError(f"offline: connection to {address} refused")
        return real_connect(self, address)

    def connect_ex(self, address):
        if self.family in (socket.AF_INET, socket.AF_INET6) and not _is_local(host_of(address)):
            _record("connect", address)
            return 111                                # ECONNREFUSED
        return real_connect_ex(self, address)

    def getaddrinfo(host, *a, **k):
        if not _is_local(host):
            _record("lookup", host)
            raise socket.gaierror(f"offline: no lookup of {host}")
        return real_getaddrinfo(host, *a, **k)

    def gethostbyname(host):
        if not _is_local(host):
            _record("lookup", host)
            raise socket.gaierror(f"offline: no lookup of {host}")
        return real_gethostbyname(host)

    socket.socket.connect, socket.socket.connect_ex = connect, connect_ex
    socket.getaddrinfo, socket.gethostbyname = getaddrinfo, gethostbyname


def attempts(log_path):
    """The attempts written to a guard log."""
    if not log_path or not os.path.exists(log_path):
        return []
    with open(log_path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]
