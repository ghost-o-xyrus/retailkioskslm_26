"""
Objective 5, Step 3: per-stage timing and memory of one turn.

A turn is a sequence of stages; entering a stage closes the one before, so the stages cover the turn from its start
to its end with no gaps and no overlap (anything outside them is reported as "unattributed"). Stages may repeat
(model_round, model_tools). Each stage can carry sub-stages measured inside it (retrieval parts, prompt reading and
writing, a worker start) and records the memory of llama-server, of this process and of a retrieval worker:
the last background sample at its end and the peak while it ran (harness/ram_monitor.py samples every 0.25 s).

    clock = StageClock(ram, enabled=True, emit=print)
    clock.begin(t0)                 # the turn's own start time (time.time())
    clock.enter("route")
    clock.sub("bm25", 12.3)
    stages = clock.finish()         # list of dicts, or None when disabled

STAGES lists the stage names in their usual order (the Objective 5 design doc, section "Per-stage management").
emit(event) receives {"type": "stage_start" | "stage_end" | "tool_call" | ..., ...} for the app; the harness passes
none. The clock also measures its own cost (instrumentation_ms).
"""

import time

STAGES = ("input", "route", "retrieval", "harness_tools", "model_round", "model_tools", "checks", "output")
HOOKS = {}        # name -> callable(); the stage manager registers "before_route" and "before_model" (Step 3)


class StageClock:
    def __init__(self, ram=None, enabled=True, emit=None):
        self.ram, self.enabled, self.emit = ram, enabled, emit
        self.stages, self.cur, self.t0, self.cost = [], None, None, 0.0
        self.fired = set()

    # ---- the turn ----
    def begin(self, t0=None):
        if not self.enabled:
            return
        c = time.perf_counter()
        self.t0 = t0 if t0 is not None else time.time()
        self.cost += time.perf_counter() - c

    def _now_ms(self):
        return (time.time() - self.t0) * 1000

    def _ram(self):
        if self.ram is None or not hasattr(self.ram, "snapshot"):
            return None, None
        return self.ram.snapshot(), self.ram.stage_peaks()

    def _close(self, now_ms):
        s = self.cur
        if s is None:
            return
        s["ms"] = round(now_ms - s["start_ms"], 1)
        last, peaks = self._ram()
        if last is not None:
            s["rss_mb"], s["peak_mb"] = last, peaks
        self.stages.append(s)
        self.cur = None
        if self.emit:
            self.emit({"type": "stage_end", "stage": s["stage"], "ms": s["ms"], "info": s.get("info"),
                       "sub": s.get("sub"), "rss_mb": s.get("rss_mb")})

    def enter(self, name, **info):
        if not self.enabled:
            return
        c = time.perf_counter()
        now = self._now_ms()
        self._close(now)
        self.cur = {"stage": name, "start_ms": round(now, 1)}
        if info:
            self.cur["info"] = info
        if self.ram is not None and hasattr(self.ram, "mark"):
            self.ram.mark()
        if self.emit:
            self.emit({"type": "stage_start", "stage": name, "info": info or None, "start_ms": round(now, 1)})
        self.cost += time.perf_counter() - c

    def note(self, **info):
        """Add facts to the current stage (route chosen, chunks shown...)."""
        if not self.enabled or self.cur is None:
            return
        self.cur.setdefault("info", {}).update(info)

    def sub(self, name, ms, **info):
        """A part of the current stage, measured by the code that ran it."""
        if not self.enabled or self.cur is None:
            return
        d = {"name": name, "ms": None if ms is None else round(float(ms), 1)}
        d.update({k: v for k, v in info.items() if v is not None})
        self.cur.setdefault("sub", []).append(d)

    def fire(self, hook):
        """Run a stage-manager hook once per turn (e.g. start or stop the retrieval worker) and time it."""
        fn = HOOKS.get(hook)
        if fn is None or hook in self.fired:
            return
        self.fired.add(hook)
        t = time.perf_counter()
        res = fn()
        if self.enabled and self.cur is not None:
            self.sub(hook, (time.perf_counter() - t) * 1000, **(res if isinstance(res, dict) else {}))

    def event(self, kind, **data):
        """Pass a tool call or other event to the app (not stored: the turn record already has the calls)."""
        if self.emit:
            self.emit(dict(data, type=kind))

    def finish(self):
        if not self.enabled:
            return None
        c = time.perf_counter()
        self._close(self._now_ms())
        self.cost += time.perf_counter() - c
        return self.stages

    def summary(self, total_ms):
        """Stage totals and the time no stage covers, for the turn record."""
        if not self.enabled:
            return None
        covered = sum(s["ms"] for s in self.stages)
        by = {}
        for s in self.stages:
            by[s["stage"]] = round(by.get(s["stage"], 0.0) + s["ms"], 1)
        return {"by_stage_ms": by, "covered_ms": round(covered, 1),
                "unattributed_ms": round(total_ms - covered, 1) if total_ms is not None else None,
                "instrumentation_ms": round(self.cost * 1000, 2)}
