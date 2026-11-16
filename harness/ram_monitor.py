"""
Background sampler for llama-server's memory use (resident set size, including child processes).

If no PID is given, it looks for a running process whose name contains "llama-server".
Samples every 0.25 s; keeps a per-case peak (reset at the start of each case) and a run peak.
If psutil is missing or no process is found, RAM fields are reported as None.
"""

import threading
import time

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


class RamMonitor:
    def __init__(self, pid=None, interval=0.25, name_hint="llama-server"):
        self.interval = interval
        self.proc = None
        self._case_peak = 0
        self._run_peak = 0
        self._stop = threading.Event()
        self._thread = None
        # Objective 5, Step 3: the last sample and the peak since mark(), per process (server, this process, and any
        # watched worker), read by kiosk_core/stages.py at each stage boundary without a new system call
        self._others = {}
        self._last, self._stage_peak = {}, {}
        try:
            self._others["app"] = psutil.Process() if psutil else None
        except (psutil.Error, OSError):  # pragma: no cover
            pass
        if psutil is None:
            return
        try:
            if pid:
                self.proc = psutil.Process(pid)
            else:
                for p in psutil.process_iter(["name", "cmdline"]):
                    text = (p.info.get("name") or "") + " " + " ".join(p.info.get("cmdline") or [])
                    if name_hint in text and "run_eval" not in text and "run_plan" not in text:
                        self.proc = p
                        break
        except (psutil.Error, OSError):
            self.proc = None

    def _rss(self):
        try:
            total = self.proc.memory_info().rss
            for c in self.proc.children(recursive=True):
                try:
                    total += c.memory_info().rss
                except psutil.Error:
                    pass
            return total
        except (psutil.Error, OSError):
            return 0

    def _loop(self):
        while not self._stop.is_set():
            rss = self._rss() if self.proc is not None else 0
            self._case_peak = max(self._case_peak, rss)
            self._run_peak = max(self._run_peak, rss)
            self._sample_others(rss)
            time.sleep(self.interval)

    def _sample_others(self, server_rss):
        vals = {"server": server_rss}
        for name, p in list(self._others.items()):
            try:
                vals[name] = p.memory_info().rss if p is not None else 0
            except (psutil.Error, OSError):
                vals[name] = 0
        self._last = vals
        for k, v in vals.items():
            self._stage_peak[k] = max(self._stage_peak.get(k, 0), v)

    def watch(self, name, pid):
        """Also sample another process (the retrieval worker); pid None stops watching it."""
        if psutil is None:
            return
        if pid is None:
            self._others.pop(name, None)
            return
        try:
            self._others[name] = psutil.Process(pid)
        except (psutil.Error, OSError):
            self._others.pop(name, None)

    def mark(self):
        """Start a new stage: its peak starts from the last sample."""
        self._stage_peak = dict(self._last)

    def snapshot(self):
        return {k: round(v / 2**20, 1) for k, v in self._last.items()} if self._last else None

    def stage_peaks(self):
        return {k: round(v / 2**20, 1) for k, v in self._stage_peak.items()} if self._stage_peak else None

    def start(self):
        if self.proc is not None or self._others:
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def reset_case_peak(self):
        self._case_peak = self._rss() if self.proc else 0

    def case_peak_mb(self):
        return round(self._case_peak / 2**20, 1) if self.proc else None

    def run_peak_mb(self):
        return round(self._run_peak / 2**20, 1) if self.proc else None

    def describe(self):
        if psutil is None:
            return "disabled (pip install psutil)"
        if self.proc is None:
            return "disabled (llama-server process not found; pass --server-pid)"
        return f"pid {self.proc.pid}"

    @staticmethod
    def total_ram_gb():
        return round(psutil.virtual_memory().total / 2**30, 1) if psutil else None
