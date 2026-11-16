"""
Objective 5, Step 2: the app's entry to the turn engine.

    eng = Engine.from_plan_run(run_cfg, base_url="http://127.0.0.1:8080")   # a run from a plan file (O3-final...)
    session = Session()
    rec = run_turn(session, "Do you have a gift for my father around 15k?", eng, emit=print)
    rec["final_reply"], rec["tool_calls"], rec["stages"]

A configuration is the same set of settings a plan run uses: Engine.from_plan_run builds the harness/run_eval.py
arguments with harness/run_plan.eval_argv_for and parses them with run_eval's own parser, so defaults match the
evaluated runs exactly. The set-up below mirrors run_eval.main() (prompts, tool schemas, the catalogue, the
knowledge base, the router, the stage policy); kiosk_core/test_core.py checks that a turn through Engine gives the
same record as the harness on the same case.

The returned record is the harness's turn record (final_reply, tool_calls, flags, turns, retrieval, metrics,
stages, stage_summary), so the existing scorers and summaries read app logs unchanged.
"""

import json
import os
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "retrieval"))

from kiosk_core import engine as E  # noqa: E402
from kiosk_core import stages as S  # noqa: E402



class Session:
    """One customer's conversation: the messages so far (customer and kiosk only; tool rounds are rebuilt by the
    engine each turn, as in the eval cases)."""

    def __init__(self, session_id=None, language="en"):
        self.id = session_id or uuid.uuid4().hex[:12]
        self.messages, self.language, self.records = [], language, []

    def case(self):
        last = self.messages[-1]["content"] if self.messages else ""
        from language import is_hinglish
        return {"id": f"{self.id}-{len(self.records) + 1}", "mode": "tools", "messages": [dict(m) for m in self.messages],
                "context": None, "category": "live", "subcategory": "live", "split": "live", "set": "live",
                "language": "hinglish" if is_hinglish(last) else "en", "expected": {}}


class Engine:
    """Everything one configuration needs: arguments, prompts, tool schemas, knowledge base, router, RAM monitor."""

    def __init__(self, argv, server_pid=None):
        from harness import run_eval
        from harness.ram_monitor import RamMonitor
        from tools import mock_tools
        self.args = a = run_eval.make_parser().parse_args(argv)
        self.base_url = a.url.rstrip("/")
        with open(os.path.join(ROOT, "eval", "system_prompts.json"), encoding="utf-8") as f:
            self.prompts = json.load(f)
        schemas = mock_tools.load_schemas()
        if a.tool_view == "compact":
            schemas = json.loads(json.dumps(schemas))
            for sc in schemas:
                if sc["function"]["name"] == "search_catalogue":
                    sc["function"]["parameters"]["properties"]["limit"]["description"] = "Maximum results, default 3, maximum 10."
        self.schemas = schemas
        if a.rag_rule not in self.prompts or a.tools_prompt not in self.prompts:
            raise ValueError(f"unknown prompt key {a.rag_rule} / {a.tools_prompt}")
        self.ram = RamMonitor(pid=server_pid or a.server_pid)
        self.ram.start()
        self.kb, self.chunks, self.manager, self.router = None, None, None, None
        self.hooks = {}
        if a.retrieval in ("always", "tool", "routed"):
            from knowledge_base import KnowledgeBase, DEFAULT_FALLBACK
            rchoice = {}
            if a.reranker_choice:
                with open(a.reranker_choice, encoding="utf-8") as f:
                    rchoice = json.load(f)
            kw = dict(**({"corpus_path": a.corpus} if a.corpus else {}),
                      fallback_path=a.fallback_config or DEFAULT_FALLBACK, k=a.k_chunks,
                      **{k: rchoice[k] for k in ("reranker", "depth", "backend", "max_length", "int8", "rerank_view")
                         if k in rchoice},
                      threads=int(rchoice.get("threads", a.retriever_threads)), fake=a.fake_retriever,
                      view=a.context_view, chunk_gate=a.chunk_gate)
            if a.stage_policy == "sequential":
                from kiosk_core.stage_manager import StageManager
                from router.router import _catalogue_names
                self.manager = StageManager("sequential", kw, ram=self.ram,
                                            router_names=list(_catalogue_names()) if a.retrieval == "routed" else None)
                self.kb, self.router = self.manager.kb, self.manager.router
                self.hooks = self.manager.hooks()
            else:
                self.kb = KnowledgeBase(**kw)
                if a.retrieval == "routed":
                    if E.ROUTER.get("key") != id(self.kb.dense):
                        from router.router import Router
                        E.ROUTER["r"], E.ROUTER["key"] = Router(encoder=self.kb.dense), id(self.kb.dense)
                    self.router = E.ROUTER["r"]
            self.chunks = self.kb.chunks
        elif a.retrieval == "oracle":
            from knowledge_base import load_chunks
            self.chunks = load_chunks()
        self.activate()

    def activate(self):
        """Put this configuration's settings into the process-wide state the engine reads (prompt keys, tool view,
        catalogue, router, stage hooks). Called before every turn, so several configurations can share a process
        (compare mode) one turn at a time."""
        from tools import mock_tools
        a = self.args
        mock_tools.HONEST = a.tool_view == "compact"
        mock_tools.DEFAULT_LIMIT = 3 if a.tool_view == "compact" else 5
        if os.path.abspath(mock_tools.DATA_DIR) != os.path.abspath(a.data_dir) or mock_tools._DB is None:
            mock_tools.reload(a.data_dir)
        E.RAG_RULE["always"], E.TOOLS_PROMPT["key"], E.ANSWER_RULE["on"] = a.rag_rule, a.tools_prompt, a.answer_length
        if self.router is not None:
            E.ROUTER["r"] = self.router
        S.HOOKS.clear()
        S.HOOKS.update(self.hooks)

    @classmethod
    def from_plan_run(cls, run_cfg, base_url="http://127.0.0.1:8080", plan_defaults=None, results_dir=None,
                      server_pid=None):
        """A configuration from a plan file's run entry (harness/plans/*.json), e.g. O3-final for one tier."""
        from harness import run_plan
        cfg = dict(plan_defaults or {})
        cfg.update(run_cfg)
        port = int(base_url.rsplit(":", 1)[1].split("/")[0])
        argv = run_plan.eval_argv_for(cfg, port, os.path.join(ROOT, cfg.get("eval", "eval/eval_set.jsonl")),
                                      results_dir or os.path.join(ROOT, "results_obj5", "_app"))
        argv += ["--engine", "core"]
        return cls(argv, server_pid=server_pid)

    def warmup(self):
        """The harness's warm-up request: the system prompt and tools go into llama-server's cache."""
        msgs = E.build_messages({"mode": "tools", "messages": [{"role": "user", "content": "Hello"}], "context": None},
                                self.prompts, self.args.retrieval)
        body = {"model": "local", "messages": msgs, "max_tokens": 1, "temperature": 0, "cache_prompt": True,
                "tools": self.schemas}
        if getattr(self.args, "parallel_tools", False):
            body["parallel_tool_calls"] = True
        if self.args.no_thinking:
            body["chat_template_kwargs"] = {"enable_thinking": False}
        if E.REQUEST_EXTRA:
            body.update(E.REQUEST_EXTRA)          # the adapter scales of this setup (a change empties the cache)
        t = time.time()
        E.http_json(self.base_url + "/v1/chat/completions", body, timeout=self.args.request_timeout)
        if getattr(self.args, "harness_tools", False):
            # O3-final answers most turns in one request with tools off (the kiosk ran the tools); that request can
            # render differently, so it is warmed last and its prefix is the one left in the cache
            E.http_json(self.base_url + "/v1/chat/completions", dict(body, tool_choice="none"),
                        timeout=self.args.request_timeout)
        return round((time.time() - t) * 1000, 1)

    def close(self):
        if self.manager is not None:
            self.manager.shutdown()
        self.ram.stop()


def run_turn(session, message, engine, emit=None, stream=False):
    """Add the customer's message, run one kiosk turn, add the kiosk's reply. Returns the turn record.
    stream=True (the app, Objective 5 Step 4): model rounds stream, and their text goes out as 'token' events."""
    session.messages.append({"role": "user", "content": message})
    case = session.case()
    if emit:
        emit({"type": "turn_start", "session": session.id, "turn": case["id"]})
    engine.activate()
    plain = E.http_json
    if stream and emit:
        from kiosk_core.streaming import make_http_json
        E.http_json = make_http_json(plain, emit)
    try:
        rec = E.run_case(case, engine.args, engine.prompts, engine.schemas, engine.base_url, engine.ram, engine.kb,
                         engine.chunks, emit=emit)
    finally:
        E.http_json = plain
    rec.pop("_token_texts", None)
    rec.update(id=case["id"], session=session.id, turn=len(session.records) + 1, language=case["language"],
               config=engine.args.config_label, engine="core", time=time.strftime("%Y-%m-%dT%H:%M:%S"))
    session.messages.append({"role": "assistant", "content": rec.get("final_reply") or ""})
    session.records.append(rec)
    if emit:
        emit({"type": "final", "reply": rec.get("final_reply"), "flags": rec.get("flags")})
        emit({"type": "metrics", **(rec.get("metrics") or {})})
    return rec
