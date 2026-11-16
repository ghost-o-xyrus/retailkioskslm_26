"""
Objective 5, Step 3: the stage manager. Two policies for the retrieval models (query encoder and re-ranker, with
the router that shares the encoder):

  resident     everything is loaded once and stays loaded (what every Objective 2-4 run did)
  sequential   the retrieval models live in a worker process that is started at the start of a turn's route stage
               and stopped before the model's first round, so the model never shares RAM with them. A process is
               used because freeing a model inside Python does not reliably give its memory back; ending a process
               does. Every turn pays the worker's start-up (it shows as a sub-stage, "before_route").

The worker caches the corpus and prototype embeddings it computes at start-up (results_obj5/_cache), so a start
re-encodes nothing; queries are never cached, so retrieval itself costs the same as resident.

    mgr = StageManager("sequential", kb_kwargs, ram=ram, router_names=names)
    kb, router = mgr.kb, mgr.router          # stand-ins with the methods the engine calls
    ...                                      # each turn: the engine fires "before_route" and "release"
    mgr.shutdown()
"""

import hashlib
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE_DIR = os.path.join(ROOT, "results_obj5", "_cache")


# --------------------------------------------------------------------------
# the worker process
# --------------------------------------------------------------------------

def _install_encode_cache(path, state):
    """Cache DenseRetriever batch encodings (corpus, router prototypes) while state['on'] is true."""
    import numpy as np
    from retrievers import DenseRetriever
    store = {}
    if os.path.exists(path):
        try:
            with np.load(path) as z:
                store = {k: z[k] for k in z.files}
        except Exception:  # noqa: BLE001 - a broken cache is rebuilt
            store = {}
    orig = DenseRetriever._encode

    def cached(self, texts, batch_size=16):
        if not state["on"]:
            return orig(self, texts, batch_size)
        keys = [hashlib.sha1((self.model_name + "\x00" + t).encode("utf-8")).hexdigest() for t in texts]
        miss = [i for i, k in enumerate(keys) if k not in store]
        if miss:
            v = orig(self, [texts[i] for i in miss], batch_size)
            for j, i in enumerate(miss):
                store[keys[i]] = v[j]
            state["new"] = True
        return np.stack([store[k] for k in keys]).astype("float32")

    DenseRetriever._encode = cached
    return store


def _worker_main(conn, kb_kwargs, router_names, cache_path):
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "retrieval"))
    state = {"on": True, "new": False}
    t0 = time.perf_counter()
    store = _install_encode_cache(cache_path, state)
    from knowledge_base import KnowledgeBase
    kb = KnowledgeBase(**kb_kwargs)
    router = None
    if router_names is not None:
        from router.router import Router
        router = Router(encoder=kb.dense, names=tuple(router_names))
    state["on"] = False
    if state["new"]:
        import numpy as np
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        tmp = cache_path + ".tmp.npz"
        np.savez(tmp, **store)
        os.replace(tmp, cache_path)
    conn.send(("ready", {"load_ms": round((time.perf_counter() - t0) * 1000, 1), "config": kb.config,
                         "fallback": kb.fallback, "threshold": kb.threshold, "bypass": kb.bypass,
                         "messages": kb.messages, "k": kb.k}))
    while True:
        try:
            method, a = conn.recv()
        except EOFError:
            break
        if method == "stop":
            break
        try:
            if method == "retrieve":
                res = kb.retrieve(*a)
            elif method == "context":
                res = kb.context(*a)
            elif method == "route":
                res = router.route(*a)
            elif method == "route_text":
                res = router.route_text(*a)
            else:
                raise ValueError(f"unknown method {method}")
            conn.send(("ok", res))
        except Exception as e:  # noqa: BLE001 - the caller re-raises
            conn.send(("err", f"{type(e).__name__}: {e}"))


# --------------------------------------------------------------------------
# the manager and the stand-ins the engine sees
# --------------------------------------------------------------------------

class StageManager:
    def __init__(self, policy, kb_kwargs, ram=None, router_names=None, cache_path=None):
        if policy not in ("resident", "sequential"):
            raise ValueError(policy)
        self.policy, self.kb_kwargs, self.ram = policy, dict(kb_kwargs), ram
        self.router_names = router_names
        key = json.dumps({k: str(v) for k, v in sorted(self.kb_kwargs.items())}, sort_keys=True)
        self.cache_path = cache_path or os.path.join(CACHE_DIR, "encode_" + hashlib.sha1(key.encode()).hexdigest()[:12]
                                                     + ".npz")
        self.proc, self.conn, self.attrs, self.starts = None, None, None, []
        self.kb, self.router = None, None
        if policy == "sequential":
            self.kb = KBProxy(self)
            self.router = RouterProxy(self) if router_names is not None else None
            self.start()                      # once, so the attributes (threshold, messages...) are known
            self.stop()

    # ---- worker life cycle ----
    def start(self):
        if self.proc is not None:
            return {"started": False}
        t = time.perf_counter()
        ctx = mp.get_context("spawn")
        parent, child = ctx.Pipe()
        self.proc = ctx.Process(target=_worker_main, args=(child, self.kb_kwargs, self.router_names, self.cache_path),
                                daemon=True)
        self.proc.start()
        self.conn = parent
        kind, attrs = self.conn.recv()
        if kind != "ready":
            raise RuntimeError(f"retrieval worker failed: {attrs}")
        self.attrs = attrs
        if self.ram is not None and hasattr(self.ram, "watch"):
            self.ram.watch("worker", self.proc.pid)
        ms = round((time.perf_counter() - t) * 1000, 1)
        self.starts.append(ms)
        return {"started": True, "worker_load_ms": attrs["load_ms"]}

    def stop(self):
        if self.proc is None:
            return {"stopped": False}
        try:
            self.conn.send(("stop", None))
        except (OSError, BrokenPipeError):
            pass
        self.proc.join(timeout=20)
        if self.proc.is_alive():
            self.proc.kill()
            self.proc.join(timeout=5)
        self.conn.close()
        self.proc, self.conn = None, None
        if self.ram is not None and hasattr(self.ram, "watch"):
            self.ram.watch("worker", None)
        return {"stopped": True}

    def call(self, method, *a):
        if self.proc is None:
            self.start()                     # a call outside the route-to-model window (should not happen)
        self.conn.send((method, a))
        kind, res = self.conn.recv()
        if kind != "ok":
            raise RuntimeError(f"retrieval worker: {res}")
        return res

    def hooks(self):
        """For kiosk_core.stages.HOOKS: start before routing, stop before the model."""
        if self.policy != "sequential":
            return {}
        return {"before_route": self.start, "release": self.stop}

    def shutdown(self):
        self.stop()


class KBProxy:
    """The parts of KnowledgeBase the engine uses, served by the worker. Chunks are plain data, loaded here."""

    def __init__(self, mgr):
        self.mgr = mgr
        from knowledge_base import DEFAULT_CORPUS
        path = mgr.kb_kwargs.get("corpus_path", DEFAULT_CORPUS)
        with open(path, encoding="utf-8") as f:
            self.chunks = {c["id"]: c for c in (json.loads(l) for l in f if l.strip())}
        self.dense, self.reused = None, False

    def __getattr__(self, name):
        if name in ("config", "fallback", "threshold", "bypass", "messages", "k"):
            return self.mgr.attrs[name]
        raise AttributeError(name)

    def retrieve(self, query, k=None):
        return self.mgr.call("retrieve", query, k)

    def context(self, ids_or_result):
        return self.mgr.call("context", ids_or_result)

    def tool_result(self, query):
        raise NotImplementedError("search_knowledge (retrieval 'tool') is not supported with the sequential policy")


class RouterProxy:
    def __init__(self, mgr):
        self.mgr = mgr
        with open(os.path.join(ROOT, "router", "prototypes.json"), encoding="utf-8") as f:
            self.prototypes = json.load(f)

    def route(self, messages):
        return self.mgr.call("route", messages)

    def route_text(self, text):
        return self.mgr.call("route_text", text)
