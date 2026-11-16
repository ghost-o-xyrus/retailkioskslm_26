"""
Run eval cases against a model served by llama-server and log everything the scorer needs.

One run = one model, one quantization, one backend, one case list. Typical use:

    # terminal 1: start the model
    llama-server.exe -m models\\qwen3.5-4b\\Qwen3.5-4B-Q4_K_M.gguf --jinja -c 8192 --port 8080 -ngl 99 --reasoning-budget 0
    # terminal 2: run the cases
    python harness\\run_eval.py --name qwen35-4b_q4_vulkan --model "Qwen3.5-4B" --quant Q4_K_M --backend vulkan

For unattended multi-model runs, use harness/run_plan.py, which starts and stops the server for you.

Output (results/<name>/):
    cases.jsonl     one line per case (and per repeat): tool calls, replies, timings, tokens, RAM
    run_meta.json   settings, server properties, machine info, start/end time
    server.log      only when started by run_plan.py

Retrieval (Objective 2, Step 7), off by default so Objective 1 runs are unchanged:
    --retrieval oracle   show the case's gold chunks with the customer's message (the ceiling)
    --retrieval always   retrieve on every customer message and show the top-k chunks with it
    --retrieval tool     give the model a search_knowledge tool instead
    --fallback shadow    (default) log what the refusal fallback would do but still run the model, so one run
                         gives both "retrieved" and "retrieved + fallback" in Step 8
    --fallback live      hard fallback: below the threshold, reply with the fixed message and skip the model
    --fallback gate      soft fallback: below the threshold, show the model no chunks ("nothing relevant found"),
                         so it can still use its other tools (needed if shopping requests score low, see Step 7)
Retrieved text is added to the customer's message, not the system prompt, so the system prompt and tool
definitions stay an identical, cacheable prefix. Grounded-mode cases ignore --retrieval.

Design choices (see harness/README.md):
  - Greedy decoding by default (temperature 0, fixed seed); thinking turned off per request.
  - Non-streaming requests: llama-server's `timings` block gives prefill time (prompt_ms), which is
    used as time-to-first-token, plus generation speed and how many prompt tokens came from cache.
  - The system prompt and tool definitions form an identical prefix for every case, so llama-server's
    prompt cache can reuse them; cache reuse is logged per turn (timings.cache_n).
  - Resumable: rerunning the same command skips cases already in cases.jsonl.
"""

import argparse
import json
import os
import platform
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from tools import mock_tools  # noqa: E402
from tools.render import render as render_tool  # noqa: E402
from router.router import Router, RULE_MARGIN, PROTO_MARGIN  # noqa: E402
from harness import discovery  # noqa: E402

ROUTER = {}                                  # the router, built once per process (it encodes its prototypes)
KB_KWARGS = {}                               # the KnowledgeBase arguments of this run (Objective 5: the worker's)
RETRIEVE_ROUTES = {"store", "unclear"}
from harness.ram_monitor import RamMonitor  # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "retrieval"))
from knowledge_base import (KnowledgeBase, SEARCH_KNOWLEDGE_SCHEMA, DEFAULT_FALLBACK,  # noqa: E402
                            load_chunks, format_context, view_tokens, model_text)
from language import is_hinglish  # noqa: E402
from harness import entity, verify  # noqa: E402
from harness import focus as harness_focus  # noqa: E402
from harness.machine import machine_info  # noqa: E402

TOOL_NAMES = set(mock_tools.TOOL_FUNCTIONS)
KNOWLEDGE_TOOL = "search_knowledge"
THINK_RE = re.compile(r"<think>.*?</think>\s*", re.S | re.I)
TOOL_TEXT_RE = re.compile(r"<tool_call>|<\|tool_call|\"name\"\s*:\s*\"(" + "|".join(TOOL_NAMES | {KNOWLEDGE_TOOL}) + r")\"|\[TOOL_CALLS\]"
                          r"|\b(" + "|".join(TOOL_NAMES | {KNOWLEDGE_TOOL}) + r")\s*\("
                          # any JSON-looking call, even with an invented tool name (Phi wrote "search_product")
                          r"|\"name\"\s*:\s*\"[A-Za-z_][\w.]*\"\s*,\s*\"(arguments|parameters)\"\s*:"
                          r"|<\|tool\|>|functools\[")


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

class ServerDown(Exception):
    pass


def http_json(url, payload=None, timeout=600):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"},
                                 method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:2000]
        raise RuntimeError(f"HTTP {e.code}: {body}") from None
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        raise ServerDown(str(e)) from None


def wait_for_server(base_url, timeout_s=300):
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            r = http_json(base_url + "/health", timeout=5)
            if r.get("status") in ("ok", "no slot available"):
                return True
        except (ServerDown, RuntimeError):
            pass
        time.sleep(2)
    return False


# --------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------

def load_cases(path, set_=None, split=None, ids_file=None, category=None, limit=None):
    with open(path, encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]
    if ids_file:
        with open(ids_file, encoding="utf-8") as f:
            data = json.load(f)
        wanted = set(data["ids"] if isinstance(data, dict) else data)
        cases = [c for c in cases if c["id"] in wanted]
    if set_ and set_ != "all":
        cases = [c for c in cases if c.get("set", "core") == set_]
    if split and split != "all":
        cases = [c for c in cases if c["split"] == split]
    if category:
        cases = [c for c in cases if c["category"] in category.split(",")]
    if limit:
        cases = cases[:limit]
    return cases


RAG_RULE = {"always": "rag_always_rule"}   # set from --rag-rule in main()


TOOLS_PROMPT = {"key": "tools"}
ANSWER_RULE = {"on": False}
ANSWER_LENGTH_RULE = ("Keep each reply short: at most 40 words for a fact or policy answer, at most 60 words when "
                      "recommending watches.")


def build_messages(case, prompts, retrieval="none"):
    system = prompts[TOOLS_PROMPT["key"]] if case["mode"] == "tools" else prompts["grounded"]
    if ANSWER_RULE["on"] and case["mode"] == "tools":
        system += "\n- " + ANSWER_LENGTH_RULE          # Step 13
    if case["mode"] == "tools" and retrieval in ("oracle", "always", "routed"):
        system += "\n" + prompts[RAG_RULE["always"]]
    elif case["mode"] == "tools" and retrieval == "tool":
        system += "\n" + prompts["rag_tool_rule"]
    if case.get("context"):
        system += prompts["context_template"].format(context=case["context"])
    return [{"role": "system", "content": system}] + [dict(m) for m in case["messages"]]


def last_user_index(messages):
    return max((i for i, m in enumerate(messages) if m["role"] == "user"), default=None)


def add_context(messages, idx, context, prompts):
    messages[idx] = dict(messages[idx], content=prompts["retrieved_template"].format(
        context=context, message=messages[idx]["content"]))


def parse_tool_calls(msg, names=TOOL_NAMES):
    out = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function", {})
        raw = fn.get("arguments")
        args, ok, err = None, False, None
        if isinstance(raw, dict):
            args, ok = raw, True
        else:
            try:
                args = json.loads(raw or "{}")
                ok = isinstance(args, dict)
                if not ok:
                    err = "arguments are not a JSON object"
            except (json.JSONDecodeError, TypeError) as e:
                err = str(e)
        out.append({"id": tc.get("id"), "name": fn.get("name"), "arguments": args if ok else None,
                    "arguments_raw": raw, "arguments_valid_json": ok, "parse_error": err,
                    "known_tool": fn.get("name") in names})
    return out


def run_case(case, args, prompts, schemas, base_url, ram, kb=None, chunks=None):
    use_tools = case["mode"] == "tools"
    cond = args.retrieval if use_tools else "none"
    messages = build_messages(case, prompts, cond)
    turns, calls, flags = [], [], []
    final, reasoning_chars = None, 0
    t0 = time.time()
    ram.reset_case_peak()
    names = TOOL_NAMES | ({KNOWLEDGE_TOOL} if cond == "tool" else set())
    if cond == "tool":
        schemas = schemas + [SEARCH_KNOWLEDGE_SCHEMA]

    retrieval, retrieval_ms = None, 0.0
    context_text = None   # text added to the customer's message; its real token count is taken after the case
    ui = last_user_index(messages)
    route_info, cond_eff = None, cond
    if cond == "routed" and ui is not None:
        # Objective 3, Step 4: the router decides before any model call; only store questions (and messages it
        # cannot place) get retrieved cards, as in Objective 2
        route_info = ROUTER["r"].route(messages[1:])
        retrieval_ms += route_info["ms"]
        cond_eff = "always" if route_info["route"] in RETRIEVE_ROUTES else "none"
    fup = None
    if (args.followup_retrieval or args.focus_memory) and route_info is not None and ui is not None:
        # Objective 3, Step 11: a follow-up about the watch in focus ("does it come in black?")
        focus = harness_focus.product_in_focus(messages[1:])
        last_text = case["messages"][-1]["content"]
        ordf = harness_focus.ordinal_focus(messages[1:], last_text) if getattr(args, "ordinal_refs", False) else None
        if ordf:                           # Objective 5, Step 9: "the second one" is a follow-up about that watch
            focus = ordf
        if focus and (ordf or harness_focus.is_followup(last_text, route_info)):
            fup = {"focus": focus, "query": harness_focus.retrieval_query(messages[1:], focus), "rerouted_from": None}
            if args.focus_memory:
                forced = harness_focus.own_route(last_text)
                if forced and route_info["route"] != forced:
                    fup["rerouted_from"] = route_info["route"]
                    route_info = dict(route_info, route=forced, source="focus")
                elif route_info["route"] in ("shopping", "unclear", "chat") and route_info.get("source") != "rule":
                    own = ROUTER["r"].route_text(last_text)["route"]
                    if own != "shopping":
                        fup["rerouted_from"] = route_info["route"]
                        route_info = dict(route_info, route=own if own in HARNESS_ROUTES else "store", source="focus")
                if not route_info.get("codes"):
                    # a colour question is about the design (any variant); anything else about the variant named
                    colour_q = harness_focus.COLOUR_Q.search(last_text.lower())
                    route_info = dict(route_info, codes=[focus["style_id"] if colour_q else (focus["code"] or focus["style_id"])])
                cond_eff = "always" if route_info["route"] in RETRIEVE_ROUTES else "none"

    def fixed_reply(reply, flag, retrieval_rec=None, calls_made=()):
        """A reply written by the harness with no model call (Step 8 entity check and store-only fallback)."""
        total_ms = (time.time() - t0) * 1000
        rec = dict(retrieval_rec or {"condition": "none"})
        if route_info is not None:
            rec["route"] = route_info["route"]
            rec["router"] = {k: route_info.get(k) for k in ("source", "margin", "ms", "codes", "named", "not_carried")}
        return {"route": route_info["route"] if route_info else "none", "final_reply": reply,
                "tool_calls": list(calls_made), "flags": [flag], "turns": [], "n_rounds": 0, "reasoning_chars": 0,
                "retrieval": rec, "_token_texts": {"context": None, "tool_results": []},
                "metrics": {"end_to_end_ms": round(total_ms, 1), "retrieval_ms": round(retrieval_ms, 1),
                            "ttft_ms": None, "first_visible_ms": round(total_ms, 1), "first_response_ms": None,
                            "generated_tokens": 0, "tokens_per_s": None, "prompt_tokens_total": 0,
                            "prompt_tokens_processed": 0, "prompt_tokens_cached": 0,
                            "peak_rss_mb": ram.case_peak_mb(), "harness_rss_mb": own_rss_mb()}}

    if args.entity_check and route_info is not None and ui is not None and \
            route_info["route"] in ("store", "unclear", "shopping"):
        # Step 8: another brand, a smartwatch, a non-watch item or a design that does not exist gets a fixed reply
        last_text = case["messages"][-1]["content"]
        ent = entity.reply(last_text, is_hinglish(last_text))
        if ent:
            made = []
            if ent["search"]:
                a_, r_ = ent["search"]
                made.append({"id": "h0", "name": "search_catalogue", "arguments": a_, "arguments_raw": json.dumps(a_),
                             "arguments_valid_json": True, "parse_error": None, "known_tool": True, "by": "harness",
                             "round": -1, "harness_note": "entity check", "result": r_, "result_error": None})
            out = fixed_reply(ent["reply"], "entity_" + ent["kind"], calls_made=made)
            out["entity"] = {"kind": ent["kind"], "name": ent["name"]}
            return out
    if cond == "oracle" and ui is not None:
        oracle_ids = (case.get("expected") or {}).get("oracle_ids")
        if oracle_ids:   # nothing answers the question: the message goes in unchanged, as with the omitted gate
            context_text = format_context(chunks, oracle_ids, args.context_view)
            add_context(messages, ui, context_text, prompts)
        retrieval = {"condition": "oracle", "chunk_ids": oracle_ids, "view": args.context_view,
                     "context_tokens": sum(view_tokens(chunks[c], args.context_view) for c in oracle_ids or [] if c in chunks)}
    elif cond_eff == "always" and ui is not None:
        q = fup["query"] if (fup and args.followup_retrieval) else messages[ui]["content"]
        r = kb.retrieve(q)  # the latest customer message (Step 11 follow-ups: plus the earlier turn and focus)
        retrieval_ms += r["timings_ms"]["total"]
        if fup and args.focus_memory:     # Step 11: the focused watch's card is always shown, as card [1]
            pid = "product:" + fup["focus"]["style_id"]
            if pid in kb.chunks:
                keep = max(0, len(r["chunks"]) - 1)          # same number of cards: the focus card replaces the last
                rest = [c for c in r["chunks"] if c["id"] != pid][:keep]
                r = dict(r, refuse=False, chunks=[{"id": pid, "score": None,
                                                   "tokens": view_tokens(kb.chunks[pid], args.context_view)}] + rest)
                fup["pinned"] = pid
        retrieval = {"condition": "always", "fallback_mode": args.fallback, "query": r["query"],
                     "chunk_ids": [c["id"] for c in r["chunks"]], "scores": [c["score"] for c in r["chunks"]],
                     "retrieved_ids": r["retrieved"], "view": args.context_view, "chunk_gate": args.chunk_gate,
                     "top1": r["top1"], "top10": r["top10"], "hinglish": r["hinglish"],
                     "fallback_would_refuse": r["refuse"], "fallback_applied": False,
                     "fallback_message": r["message"], "context_tokens": r["context_tokens"],
                     "timings_ms": r["timings_ms"]}
        hard_t = float(kb.fallback.get("hard_threshold", kb.threshold)) if kb is not None else None
        hard_refuse = hard_t is not None and r["top1"] is not None and r["top1"] < hard_t and \
            not (kb.bypass and r["hinglish"])
        retrieval["hard_threshold"] = hard_t if args.fallback == "store-live" else None
        if hard_refuse and args.fallback == "store-live" and route_info is not None and \
                not (route_info.get("codes") or route_info.get("named")):
            # Step 8: the hard fallback on the knowledge path only, and never when a code or a catalogue name is
            # in the message (those go to the model and its tools, as with the soft fallback)
            retrieval["fallback_applied"] = True
            return fixed_reply(r["message"], "fallback_refused", retrieval)
        if r["refuse"] and args.fallback == "live":
            retrieval["fallback_applied"] = True
            total_ms = (time.time() - t0) * 1000
            return {"route": route_info["route"] if route_info else "none",
                    "final_reply": r["message"], "tool_calls": [], "flags": ["fallback_refused"], "turns": [],
                    "n_rounds": 0, "reasoning_chars": 0, "retrieval": retrieval,
                    "metrics": {"end_to_end_ms": round(total_ms, 1), "retrieval_ms": retrieval_ms, "ttft_ms": None,
                                "first_response_ms": None, "generated_tokens": 0, "tokens_per_s": None,
                                "prompt_tokens_total": 0, "prompt_tokens_processed": 0, "prompt_tokens_cached": 0,
                                "peak_rss_mb": ram.case_peak_mb(), "harness_rss_mb": own_rss_mb()}}
        if (r["refuse"] and args.fallback in ("gate", "store-live")) or not r["chunks"]:
            retrieval.update(fallback_applied=True, context_tokens=0, gate_style=args.gate_style)
            if args.gate_style == "message":
                add_context(messages, ui, "(nothing relevant found)", prompts)
            # "omit": the customer's message goes in unchanged, exactly as in the kiosk without retrieval
        else:
            context_text = kb.context(r)
            add_context(messages, ui, context_text, prompts)
    elif cond == "tool":
        retrieval = {"condition": "tool", "calls": []}
    if route_info is not None:
        if retrieval is None:
            retrieval = {"condition": "none"}
        retrieval["route"] = route_info["route"]
        retrieval["router"] = {k: route_info.get(k) for k in ("source", "margin", "ms", "codes", "named", "not_carried")}
    shown_cards = set()
    if args.dedupe_shown and retrieval and cond_eff in ("always", "oracle"):
        shown_cards = {c.split(":", 1)[1] for c in (retrieval.get("chunk_ids") or []) if c.startswith("product:")}
        if retrieval.get("fallback_applied"):
            shown_cards = set()

    seen_calls, staff_ticket, shown_texts, staff_checked = set(), None, [], False

    def run_harness_call(name, arguments, note="", prefix=""):
        """Objective 3, Step 5: the harness makes the call itself, shown to the model as an earlier tool round."""
        nonlocal staff_ticket
        cid = f"h{len(calls)}"
        raw = json.dumps(arguments, ensure_ascii=False)
        pc = {"id": cid, "name": name, "arguments": arguments, "arguments_raw": raw, "arguments_valid_json": True,
              "parse_error": None, "known_tool": True, "by": "harness", "round": -1}
        if note:
            pc["harness_note"] = note
        result = mock_tools.call_tool(name, arguments)
        if name == "call_staff" and isinstance(result, dict) and result.get("ticket"):
            staff_ticket = result["ticket"]
        seen_calls.add(call_key(pc))
        pc["result"] = result
        pc["result_error"] = result.get("error") if isinstance(result, dict) else None
        calls.append(pc)
        text = render_tool(name, arguments, result) if args.tool_view == "compact" else json.dumps(result, ensure_ascii=False)
        if prefix:
            text = prefix + "\n" + text
        shown_texts.append(text)
        messages.append({"role": "assistant", "content": "", "tool_calls": [
            {"id": cid, "type": "function", "function": {"name": name, "arguments": raw}}]})
        messages.append({"role": "tool", "tool_call_id": cid, "name": name, "content": text})
        return result

    one_round, route, disc = False, (route_info or {}).get("route"), None
    if use_tools and route and ui is not None:
        text = case["messages"][-1]["content"] if case["messages"] else ""
        if args.harness_tools and route in HARNESS_ROUTES:
            planned = plan_harness_calls(route, text, route_info)
            for name, arguments in planned:
                run_harness_call(name, arguments, note=route)
            one_round = bool(planned)
        if args.store_one_round and route == "store":
            if SERVICE_RE.search(text.lower()):
                code = (route_info.get("codes") or [None])[0]
                run_harness_call("call_staff", dict({"reason": "service"}, **({"product_id": code} if code else {})),
                                 note="service request")
            one_round = True
        if args.discovery != "none" and route == "shopping":
            # Step 6: slots from every customer message so far; ask (at most twice) or search once
            users = [m["content"] for m in case["messages"] if m["role"] == "user"]
            asked = sum(1 for m in case["messages"] if m["role"] == "assistant")   # earlier kiosk turns
            slots = discovery.extract_slots(users)
            disc = {"slots": slots, "decision": discovery.decide(slots, asked), "questions_before": asked,
                    "n_slots": len(discovery.count_slots(slots)), "mode": args.discovery}
            if disc["decision"] == "search":
                sa = discovery.search_args(slots)
                prefix, relaxed = "", []
                if mock_tools.search_catalogue(**sa)["total_matches"] == 0:
                    for looser, label in discovery.relaxations(sa):
                        relaxed.append(label)
                        if mock_tools.search_catalogue(**looser)["total_matches"]:
                            sa = looser
                            break
                    prefix = ("No watch matched every request, so this search leaves out: " + ", ".join(relaxed) +
                              ". Say so before suggesting these.")
                disc.update(search_args=sa, relaxed=relaxed)
                run_harness_call("search_catalogue", sa, note="discovery", prefix=prefix)
                one_round = True
            elif args.discovery == "template":
                key, q = discovery.question(slots, asked, is_hinglish(text))
                disc.update(question_key=key)
                total_ms = (time.time() - t0) * 1000
                return {"route": route, "discovery": disc, "_token_texts": {"context": context_text, "tool_results": []},
                        "final_reply": q, "tool_calls": [], "flags": ["discovery_question"], "turns": [], "n_rounds": 0,
                        "reasoning_chars": 0, "retrieval": retrieval,
                        "metrics": {"end_to_end_ms": round(total_ms, 1), "retrieval_ms": round(retrieval_ms, 1),
                                    "ttft_ms": None, "first_visible_ms": round(total_ms, 1), "first_response_ms": None,
                                    "generated_tokens": 0, "tokens_per_s": None, "prompt_tokens_total": 0,
                                    "prompt_tokens_processed": 0, "prompt_tokens_cached": 0,
                                    "peak_rss_mb": ram.case_peak_mb(), "harness_rss_mb": own_rss_mb()}}
            else:   # model-phrased question: one request, no tools, with a note on what to ask
                key = discovery.question_key(slots, asked)
                disc.update(question_key=key)
                messages[ui] = dict(messages[ui], content=messages[ui]["content"] + "\n\n" + discovery.model_note(slots, asked))
                one_round = True

    for rnd in range(args.max_rounds):
        body = {"model": "local", "messages": messages, "temperature": args.temperature,
                "seed": args.seed, "max_tokens": args.max_tokens, "cache_prompt": True}
        if args.top_k is not None:
            body["top_k"] = args.top_k
        if use_tools:
            body["tools"] = schemas
            if args.parallel_tools:
                body["parallel_tool_calls"] = True     # Step 13: two needed calls in one round
        if args.no_thinking:
            body["chat_template_kwargs"] = {"enable_thinking": False}
        # Step 3 loop guard: the last allowed request may not call tools, so every turn ends in an answer
        last_round = args.loop_guard and use_tools and rnd == args.max_rounds - 1 and rnd > 0
        if one_round and use_tools:           # Step 5: the harness already fetched what this route needs
            last_round = True
        if last_round:
            body["tool_choice"] = "none"
            if args.forced_answer == "recover":
                add_forced_note(messages)
        t_req = time.time()
        try:
            resp = http_json(base_url + "/v1/chat/completions", body, timeout=args.request_timeout)
        except RuntimeError as e:
            if "HTTP 500" in str(e) and body["max_tokens"] < 512:
                # Step 13a2: a tool call cut off by the short reply cap cannot be parsed by the server (HTTP 500);
                # the same request is sent once more with the usual cap, and the case is flagged
                flags.append("http500_retry_max_tokens")
                body["max_tokens"] = 512
                resp = http_json(base_url + "/v1/chat/completions", body, timeout=args.request_timeout)
            elif not last_round:
                raise
            else:
                resp = None
        if resp is None:
            body.pop("tool_choice", None)       # server without tool_choice support: ask again without it
            flags.append("tool_choice_unsupported")
            resp = http_json(base_url + "/v1/chat/completions", body, timeout=args.request_timeout)
        wall_ms = (time.time() - t_req) * 1000
        choice = resp["choices"][0]
        msg = choice.get("message", {})
        content = msg.get("content") or ""
        if msg.get("reasoning_content"):
            reasoning_chars += len(msg["reasoning_content"])
            flags.append("reasoning_content_present")
        if THINK_RE.search(content):
            flags.append("think_tags_in_content")
            reasoning_chars += sum(len(m) for m in THINK_RE.findall(content))
            content = THINK_RE.sub("", content).strip()
        tim = resp.get("timings", {}) or {}
        usage = resp.get("usage", {}) or {}
        parsed = parse_tool_calls(msg, names)
        turns.append({
            "round": rnd, "wall_ms": round(wall_ms, 1), "finish_reason": choice.get("finish_reason"),
            "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
            "prompt_n": tim.get("prompt_n"), "cache_n": tim.get("cache_n"), "prompt_ms": tim.get("prompt_ms"),
            "predicted_n": tim.get("predicted_n"), "predicted_ms": tim.get("predicted_ms"),
            "predicted_per_second": tim.get("predicted_per_second"),
            "draft_n": tim.get("draft_n"), "draft_n_accepted": tim.get("draft_n_accepted"),   # Step 13b
            "content": content, "n_tool_calls": len(parsed),
        })
        if choice.get("finish_reason") == "length":
            flags.append("hit_max_tokens")
        if last_round:
            turns[-1]["forced_final"] = True
        if last_round and parsed:          # tool calls on the forced-answer request are not run
            flags.append("one_round_calls_ignored" if one_round else "guard_final_calls_ignored")
            turns[-1].update(n_tool_calls=0, ignored_tool_calls=len(parsed))
            parsed = []

        if not parsed:
            if use_tools and TOOL_TEXT_RE.search(content):
                flags.append("tool_call_as_text")  # model tried to call a tool but the template/parser missed it
            final = content
            break

        assistant_msg = {"role": "assistant", "content": msg.get("content") or "", "tool_calls": msg["tool_calls"]}
        messages.append(assistant_msg)
        for i, pc in enumerate(parsed):
            if cond == "tool" and pc["name"] == KNOWLEDGE_TOOL:
                q = (pc["arguments"] or {}).get("query") if pc["arguments_valid_json"] else None
                if isinstance(q, str) and q.strip():
                    result, r = kb.tool_result(q)
                    retrieval_ms += r["timings_ms"]["total"]
                    retrieval["calls"].append({"round": rnd, "query": q, "chunk_ids": [c["id"] for c in r["chunks"]],
                                               "scores": [c["score"] for c in r["chunks"]], "top1": r["top1"],
                                               "hinglish": r["hinglish"], "fallback_would_refuse": r["refuse"],
                                               "context_tokens": r["context_tokens"], "timings_ms": r["timings_ms"]})
                else:
                    result = {"error": "invalid_arguments", "message": "search_knowledge needs a 'query' string."}
            elif args.loop_guard and call_key(pc) in seen_calls:
                result = {"note": "This exact call was already made above and its result has not changed. "
                                  "Answer the customer now with what you have."}
                pc["guard"] = "repeat"
            elif args.staff_check and pc["name"] == "call_staff" and not staff_checked and not staff_ticket and \
                    route not in HARNESS_ROUTES and (context_text or shown_texts) and \
                    ((pc["arguments"] or {}).get("reason") if pc["arguments_valid_json"] else None) in \
                    (None, "question_unanswered"):
                # Step 8: before a "can't answer" hand-off runs, the model is asked once to check what it was shown
                staff_checked = True
                result = {"note": STAFF_CHECK_NOTE}
                pc["guard"] = "staff_check"
            elif args.loop_guard and pc["name"] == "call_staff" and staff_ticket:
                result = {"note": f"Staff were already notified for this customer (ticket {staff_ticket}). Do not "
                                  "call again; tell the customer someone is coming."}
                pc["guard"] = "staff_repeat"
            elif shown_cards and pc["name"] == "get_product_details" and pc["arguments_valid_json"] and \
                    shown_style(pc["arguments"].get("product_id")) in shown_cards:
                # Step 7f: the card for this watch is already in the customer's message, so return a short
                # pointer (about 50 tokens) instead of the ~420-token record the model would have to read again
                pid = pc["arguments"].get("product_id")
                result = {"product_id": pid, "note": (f"The full card for this watch (design {shown_style(pid)}) is "
                          "already in the store information above: answer from it. Stock is not on the card; use "
                          "check_inventory for stock.")}
                pc["deduped"] = True
            else:
                result = mock_tools.call_tool(pc["name"], pc["arguments"] if pc["arguments_valid_json"] else (pc["arguments_raw"] or ""))
            if args.loop_guard and pc.get("guard") != "staff_check":
                seen_calls.add(call_key(pc))
                if pc["name"] == "call_staff" and isinstance(result, dict) and result.get("ticket") and not pc.get("guard"):
                    staff_ticket = result["ticket"]
            pc["round"] = rnd
            pc["result"] = result
            pc["result_error"] = result.get("error") if isinstance(result, dict) else None
            calls.append(pc)
            text = render_tool(pc["name"], pc["arguments"], result) if args.tool_view == "compact" \
                else json.dumps(result, ensure_ascii=False)
            shown_texts.append(text)
            messages.append({"role": "tool", "tool_call_id": pc["id"] or f"call_{rnd}_{i}", "name": pc["name"],
                             "content": text})
    else:
        flags.append("max_rounds_reached")
    if args.forced_answer == "recover" and use_tools and final and TOOL_TEXT_RE.search(final):
        # Step 7: a tool call printed as text. Keep the prose around it if there is a real answer; otherwise run the
        # printed call once (read-only tools and call_staff only) and ask once more for the answer
        flags.append("tool_text_seen")
        prose = strip_tool_text(final)
        if len(prose.split()) >= 6:
            final = prose
            flags.append("tool_text_stripped")
        else:
            printed = parse_printed_calls(final)
            pc0 = printed[0] if printed else None
            if pc0 and pc0[0] == "call_staff":
                if not staff_ticket:
                    run_harness_call("call_staff", pc0[1] or {"reason": "other"}, note="printed call")
                final = STAFF_LINE
                flags.append("tool_text_recovered")
            elif pc0 and pc0[0] in RECOVER_TOOLS and call_key({"name": pc0[0], "arguments": pc0[1],
                                                                "arguments_valid_json": True}) not in seen_calls:
                run_harness_call(pc0[0], pc0[1], note="printed call")
                add_forced_note(messages)
                body = {"model": "local", "messages": messages, "temperature": args.temperature, "seed": args.seed,
                        "max_tokens": args.max_tokens, "cache_prompt": True, "tools": schemas, "tool_choice": "none"}
                if args.top_k is not None:
                    body["top_k"] = args.top_k
                if args.no_thinking:
                    body["chat_template_kwargs"] = {"enable_thinking": False}
                t_req = time.time()
                resp = http_json(base_url + "/v1/chat/completions", body, timeout=args.request_timeout)
                choice = resp["choices"][0]
                content = THINK_RE.sub("", (choice.get("message") or {}).get("content") or "").strip()
                tim = resp.get("timings", {}) or {}
                usage = resp.get("usage", {}) or {}
                turns.append({"round": len(turns), "wall_ms": round((time.time() - t_req) * 1000, 1),
                              "finish_reason": choice.get("finish_reason"), "prompt_tokens": usage.get("prompt_tokens"),
                              "completion_tokens": usage.get("completion_tokens"), "prompt_n": tim.get("prompt_n"),
                              "cache_n": tim.get("cache_n"), "prompt_ms": tim.get("prompt_ms"),
                              "predicted_n": tim.get("predicted_n"), "predicted_ms": tim.get("predicted_ms"),
                              "predicted_per_second": tim.get("predicted_per_second"), "content": content,
                              "draft_n": tim.get("draft_n"), "draft_n_accepted": tim.get("draft_n_accepted"),
                              "n_tool_calls": 0, "forced_final": True, "recovery": True})
                final = strip_tool_text(content) if TOOL_TEXT_RE.search(content) else content
                if len(final.split()) < 6 and TOOL_TEXT_RE.search(content):
                    final = ""
                flags.append("tool_text_recovered" if final else "tool_text_replaced")
            else:
                final = ""
                flags.append("tool_text_replaced")
    if args.staff_guard and use_tools and not staff_ticket and final and route not in HARNESS_ROUTES \
            and STAFF_OFFER_RE.search(final.lower()) and not any(c["name"] == "call_staff" for c in calls):
        # Step 7 (Objective 1 rule): telling the customer staff will help means calling staff; the harness makes
        # the call the model only promised
        run_harness_call("call_staff", {"reason": "question_unanswered", "note": case["messages"][-1]["content"][:120]},
                         note="answer offered staff")
        if not STAFF_PROMISE_RE.search(final.lower()):
            final = final.rstrip() + " " + STAFF_LINE
        flags.append("harness_staff_after_answer")
    if one_round and route == "store" and args.store_one_round and not staff_ticket and final and STAFF_OFFER_RE.search(final.lower()):
        # the answer says it does not know or offers staff: the harness makes that offer real (Objective 1 rule:
        # offering staff means calling call_staff)
        run_harness_call("call_staff", {"reason": "question_unanswered", "note": case["messages"][-1]["content"][:120]},
                         note="answer offered staff")
        final = final.rstrip() + " " + STAFF_LINE
        flags.append("harness_staff_after_answer")
    if args.loop_guard and use_tools and final and TOOL_TEXT_RE.search(final):
        # a tool call written as plain text (seen when tool_choice is "none": the 2B prints the call instead of
        # answering) is not an answer; the customer gets the fixed staff line instead of raw markup
        final = ""
        flags.append("tool_text_replaced")
    if args.loop_guard and use_tools and not (final or "").strip():
        final = EMPTY_FALLBACK            # never leave the customer with an empty screen
        flags.append("empty_reply_fallback")
    if args.answer_length and final and turns and turns[-1].get("finish_reason") == "length":
        # Step 13: a reply cut by max_tokens ends at its last full sentence (if that keeps at least 40% of it)
        cut = max(final.rfind(". "), final.rfind("? "), final.rfind("! "), final.rfind("\n"))
        if cut >= 0.4 * len(final):
            final = final[:cut + 1].rstrip()
            flags.append("trimmed_at_sentence")
    verify_info = None
    if args.verify_answers != "off" and use_tools and route in ("store", "unclear") and final and \
            "empty_reply_fallback" not in flags and kb is not None:
        # Objective 3, Step 10: every detail in a knowledge-path answer must be in what the model was shown
        shown_ids = [] if (retrieval or {}).get("fallback_applied") else list((retrieval or {}).get("chunk_ids") or [])
        shown = [model_text(kb.chunks[c], args.context_view, (retrieval or {}).get("query")) for c in shown_ids
                 if c in kb.chunks]
        verify_info = verify.check(final, case["messages"][-1]["content"], shown, verify.tool_text(calls),
                                   args.verify_answers)
        final = verify_info["reply"]
        if verify_info["cited"]:
            flags.append("cited")
        if not verify_info["ok"]:
            final = (retrieval or {}).get("fallback_message") or kb.messages["en"]
            flags.append("verify_failed")

    total_ms = (time.time() - t0) * 1000
    pred_n = sum(t["predicted_n"] or 0 for t in turns)
    pred_ms = sum(t["predicted_ms"] or 0 for t in turns)
    prompt_total = sum(t["prompt_tokens"] or 0 for t in turns)
    prompt_processed = sum(t["prompt_n"] or 0 for t in turns)
    cached = sum(t["cache_n"] or 0 for t in turns)
    return {
        "route": route_info["route"] if route_info else "none", "discovery": disc, "verify": verify_info,
        "followup": fup,
        "_token_texts": {"context": context_text,
                         "tool_results": shown_texts},
        "final_reply": final, "tool_calls": calls, "flags": sorted(set(flags)), "turns": turns,
        "n_rounds": len(turns), "reasoning_chars": reasoning_chars, "retrieval": retrieval,
        "metrics": {
            "end_to_end_ms": round(total_ms, 1),
            "retrieval_ms": round(retrieval_ms, 1) if retrieval else None,
            "ttft_ms": turns[0]["prompt_ms"] if turns else None,  # prefill time of the first request
            # what a customer waits before the first word of the answer appears (all tool rounds, the final
            # prefill and retrieval; with streaming, the final reply's generation then runs while they read)
            "first_visible_ms": round(max(0.0, total_ms - (turns[-1]["predicted_ms"] or 0)), 1) if turns else None,
            "first_response_ms": turns[0]["wall_ms"] if turns else None,
            "generated_tokens": pred_n,
            "tokens_per_s": round(pred_n / (pred_ms / 1000), 2) if pred_ms else None,
            "prompt_tokens_total": prompt_total,
            "prompt_tokens_processed": prompt_processed,
            "prompt_tokens_cached": cached,
            "peak_rss_mb": ram.case_peak_mb(),
            "harness_rss_mb": own_rss_mb(),
        },
    }


EMPTY_FALLBACK = "Sorry, I couldn't finish that. A staff member can help you with it."
STAFF_CHECK_NOTE = ("Not sent yet. First check the store information and tool results above: if they answer the "
                    "customer's question, answer it now and do not call staff. If they do not, call call_staff again.")
FORCED_NOTE = "(No more tool calls this turn. Write the answer to the customer now, from the results above.)"
RECOVER_TOOLS = {"get_product_details", "check_inventory", "get_alternatives", "compare_products", "search_catalogue",
                 "get_offers"}
STAFF_PROMISE_RE = re.compile(r"(i've asked|i have asked|i'll ask|i will ask|i've called|i have called|i'll call|"
                              r"i will call|is coming|will come over|on (their|his|her) way|bula (raha|rahi|diya))")
_PRINTED_BLOCK = re.compile(r"<tool_call>.*?(</tool_call>|$)|<\|tool_call\|?>.*?(<\|/?tool_call\|?>|$)"
                            r"|\[TOOL_CALLS\].*$", re.S)
_PRINTED_JSON = re.compile(r"\{\s*\"name\"\s*:\s*\"[\w.]+\"\s*,\s*\"(arguments|parameters)\"\s*:\s*\{.*?\}\s*\}", re.S)
_PRINTED_FN = re.compile(r"<function=([\w.]+)>(.*?)(</function>|$)", re.S)
_PRINTED_PARAM = re.compile(r"<parameter=([\w.]+)>\s*(.*?)\s*(</parameter>|(?=<parameter=)|$)", re.S)


def add_forced_note(messages):
    """Step 7: on a request that may not call tools, say so at the end of the last tool result (about 20 tokens)."""
    m = messages[-1] if messages else None
    if m and m.get("role") == "tool" and FORCED_NOTE not in (m.get("content") or ""):
        messages[-1] = dict(m, content=(m.get("content") or "") + "\n" + FORCED_NOTE)


def strip_tool_text(text):
    """The reply with any printed tool call removed (Qwen XML, JSON or name(...) forms)."""
    t = _PRINTED_BLOCK.sub(" ", text or "")
    t = _PRINTED_FN.sub(" ", t)
    t = _PRINTED_JSON.sub(" ", t)
    t = re.sub(r"\b(" + "|".join(sorted(TOOL_NAMES | {KNOWLEDGE_TOOL})) + r")\s*\([^)]*\)?", " ", t)
    t = re.sub(r"</?(tool_call|function|parameter)[^>]*>", " ", t)
    return re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n\s*\n+", "\n\n", t)).strip()


def parse_printed_calls(text):
    """[(name, arguments dict)] read from a tool call the model wrote as text."""
    out = []
    for m in _PRINTED_FN.finditer(text or ""):
        args = {}
        for pm in _PRINTED_PARAM.finditer(m.group(2)):
            v = pm.group(2).strip()
            try:
                args[pm.group(1)] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                args[pm.group(1)] = v
        out.append((m.group(1), args))
    if not out:
        for m in _PRINTED_JSON.finditer(text or ""):
            try:
                d = json.loads(m.group(0))
                out.append((d["name"], d.get("arguments") or d.get("parameters") or {}))
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
    return [(n, a) for n, a in out if n in TOOL_NAMES]


def call_key(pc):
    return pc.get("name"), json.dumps(pc.get("arguments"), sort_keys=True) if pc.get("arguments_valid_json") \
        else pc.get("arguments_raw")


# ---- Objective 3, Step 5: the harness runs the tool a route needs ----
HARNESS_ROUTES = {"lookup", "stock", "compare", "staff"}
SERVICE_RE = re.compile(r"(?<![a-z])(repair|servic(e|ing)|stopped working|not working|new battery|battery (change|"
                        r"replacement)|replace (the |my )?(battery|glass|strap)|broke|broken|cracked|band ho gay|"
                        r"kharab)(?![a-z])")
STAFF_OFFER_RE = re.compile(r"(staff|store team|colleague|someone from the store|sales ?person|team member|"
                            r"i don't have (that|this|any|the) information|i do not have (that|this) information|"
                            r"i'm not sure|i am not sure|not able to confirm)")
STAFF_LINE = "I've asked a staff member to come over and help you."
ALT_CHEAPER = re.compile(r"(cheaper|less money|over my budget|above my budget|budget version|costs too much|too "
                         r"(costly|expensive)|spend less|sasta|mehenga|kam (daam|price))")
ALT_OOS = re.compile(r"(out of stock|sold out|not on display|isn't on display|can't see it|cannot see it|don't see it|"
                     r"out of|not available|nahi (hai|mila))")
ALT_ANY = re.compile(r"(similar|like it|like this|like that|watches like|instead|alternatives?|other options?|same "
                     r"style|jaisa|jaise|what else)")
COLOURS = ("rose gold", "midnight blue", "mother-of-pearl", "black", "white", "blue", "green", "red", "grey", "gray",
           "silver", "gold", "brown", "pink", "purple", "yellow", "orange", "navy", "olive", "tan", "cream", "beige",
           "lilac", "lavender", "maroon", "teal", "champagne", "bronze", "copper", "salmon")
_DESIGNS = {}


def _design_index():
    if not _DESIGNS:
        db = mock_tools._load()
        for st in db["styles"].values():
            _DESIGNS[st["style_name"].lower()] = st["style_id"]
    return _DESIGNS


def plan_harness_calls(route, text, info):
    """The calls a routed message needs, with arguments read from the message. [] = leave it to the model."""
    t = text.lower()
    codes = []
    for c in (info or {}).get("codes") or []:
        c = c.upper()
        if c not in codes:
            codes.append(c)
    named = None
    for name, sid in sorted(_design_index().items(), key=lambda kv: -len(kv[0])):
        if name in t:
            named = sid
            break
    target = codes[0] if codes else named
    colour = next((c for c in COLOURS if re.search(r"(?<![a-z])" + re.escape(c) + r"(?![a-z])", t)), None)
    if route == "compare":
        ids = codes[:3] if len(codes) >= 2 else ([codes[0], named] if codes and named and named not in codes else [])
        return [("compare_products", {"product_ids": ids})] if len(ids) >= 2 else []
    if route == "staff":
        if re.search(r"(try|wear|pehen|in person|on my wrist|see how)", t):
            reason = "try_on"
        elif re.search(r"(buy|take|pay|purchase|lena|le lunga|le leta|pack|bill|kharid)", t):
            reason = "purchase"
        elif SERVICE_RE.search(t):
            reason = "service"
        else:
            reason = "other"
        args = {"reason": reason}
        if target:
            args["product_id"] = target
        return [("call_staff", args)]
    if not target:
        return []
    if route == "stock":
        args = {"product_id": target}
        if colour:
            args["colour"] = colour
        return [("check_inventory", args)]
    if route == "lookup":
        if ALT_CHEAPER.search(t):
            return [("get_alternatives", {"product_id": target, "reason": "cheaper"})]
        if ALT_ANY.search(t) or ALT_OOS.search(t):
            return [("get_alternatives", {"product_id": target,
                                          "reason": "out_of_stock" if ALT_OOS.search(t) else "similar_style"})]
        return [("get_product_details", {"product_id": target})]
    return []


def count_tokens(base_url, text):
    """Real token count from llama-server's /tokenize (no special tokens), or None if unavailable."""
    if not text:
        return 0
    try:
        r = http_json(base_url + "/tokenize", {"content": text, "add_special": False}, timeout=30)
        return len(r.get("tokens", []))
    except Exception:  # noqa: BLE001 - optional diagnostic
        return None


def add_token_counts(rec, texts, base_url, enabled):
    """Objective 3, Step 1: real token counts of what the harness added to the conversation. Taken after the
    case has finished, so the extra requests are not inside any measured time."""
    if not texts:
        return
    if not enabled:
        return
    ctx = count_tokens(base_url, texts.get("context"))
    res = [count_tokens(base_url, t) for t in texts.get("tool_results", [])]
    for c, n in zip(rec.get("tool_calls", []), res):
        c["result_tokens"] = n
    rec["tokens"] = {"context": ctx, "tool_results": res,
                     "tool_results_total": None if any(n is None for n in res) else sum(res),
                     "method": "llama-server /tokenize"}


def run_dialogue(profile, args, prompts, schemas, base_url, ram, kb=None, chunks=None, max_turns=4):
    """Objective 3, Step 6: one simulated discovery dialogue. Each kiosk turn is an ordinary run_case on the
    conversation so far; harness/simulator.py answers for the hidden profile until the kiosk shows search results."""
    from harness import simulator
    messages = [dict(m) for m in profile["messages"]]
    revealed = set(profile.get("opening_reveals") or [])
    kturns, all_calls, flags = [], [], []
    total_ms, rec_turn = 0.0, None
    for k in range(max_turns):
        out = run_case(dict(profile, messages=list(messages)), args, prompts, schemas, base_url, ram, kb, chunks)
        out.pop("_token_texts", None)
        searches = [c for c in out.get("tool_calls", []) if c["name"] == "search_catalogue"
                    and isinstance(c.get("result"), dict) and c["result"].get("results")]
        kturns.append({"turn": k, "customer": messages[-1]["content"], "kiosk": out.get("final_reply"),
                       "route": out.get("route"), "discovery": out.get("discovery"), "tool_calls": out.get("tool_calls"),
                       "flags": out.get("flags"), "model_requests": len(out.get("turns") or []),
                       "metrics": out.get("metrics"), "revealed_before": sorted(revealed)})
        all_calls += out.get("tool_calls", [])
        flags += out.get("flags", [])
        total_ms += (out.get("metrics") or {}).get("end_to_end_ms") or 0
        if searches:
            rec_turn = k
            kturns[-1]["recommended"] = [r["product_id"] for r in searches[-1]["result"]["results"]]
            break
        messages.append({"role": "assistant", "content": out.get("final_reply") or ""})
        reply, _ = simulator.answer(profile, out.get("final_reply"), revealed)
        messages.append({"role": "user", "content": reply})
    first = [(t["metrics"] or {}).get("first_visible_ms") for t in kturns]
    return {"final_reply": kturns[-1]["kiosk"], "tool_calls": all_calls, "flags": sorted(set(flags)),
            "dialogue": {"kiosk_turns": len(kturns), "recommended_at": rec_turn, "turns": kturns,
                         "revealed_at_recommendation": sorted(revealed) if rec_turn is not None else None},
            "metrics": {"end_to_end_ms": round(total_ms, 1),
                        "first_visible_ms_per_turn": first,
                        "model_requests": sum(t["model_requests"] for t in kturns)}}


def load_dialogues(path, split=None, ids_file=None, limit=None):
    with open(path, encoding="utf-8") as f:
        ps = [json.loads(line) for line in f if line.strip()]
    if split and split != "all":
        ps = [p for p in ps if p["split"] == split]
    if ids_file:
        with open(ids_file, encoding="utf-8") as f:
            d = json.load(f)
        wanted = set(d["ids"] if isinstance(d, dict) else d)
        ps = [p for p in ps if p["id"] in wanted]
    return ps[:limit] if limit else ps


def shown_style(product_id):
    """Design id (V1003) of a SKU or design id, or None."""
    found = mock_tools._resolve(product_id) if isinstance(product_id, str) else []
    return found[0]["style_id"] if found else None


def own_rss_mb():
    """Memory of this process: with retrieval on, it holds the knowledge base (embedder + re-ranker)."""
    try:
        import psutil
        return round(psutil.Process().memory_info().rss / 1e6)
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------

def make_parser():
    p = argparse.ArgumentParser(description="Run eval cases against llama-server.")
    p.add_argument("--name", required=True, help="Run name; results go to results/<name>/")
    p.add_argument("--model", default="", help="Model label for the record, e.g. Qwen3.5-4B")
    p.add_argument("--quant", default="", help="e.g. Q4_K_M")
    p.add_argument("--backend", default="", help="cpu or vulkan")
    p.add_argument("--url", default="http://127.0.0.1:8080")
    p.add_argument("--eval", default=os.path.join(ROOT, "eval", "eval_set.jsonl"))
    p.add_argument("--set", default="all", choices=["all", "core", "expansion", "rag"])
    p.add_argument("--split", default="all", choices=["all", "test", "dev", "train"])
    p.add_argument("--ids", default=None, help="JSON file with case ids, e.g. eval/speed_subset_ids.json")
    p.add_argument("--category", default=None, help="Comma-separated categories to run")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--repeats", type=int, default=1, help="Runs per case (use 3 for pass^3)")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--top-k", type=int, default=None)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--max-rounds", type=int, default=4)
    p.add_argument("--request-timeout", type=int, default=600)
    p.add_argument("--thinking", dest="no_thinking", action="store_false",
                   help="Allow thinking (default: off via chat_template_kwargs)")
    p.add_argument("--server-pid", type=int, default=None, help="PID of llama-server for RAM tracking")
    p.add_argument("--results-dir", default=os.path.join(ROOT, "results"))
    p.add_argument("--data-dir", default=os.path.join(ROOT, "data", "kiosk"),
                   help="Catalogue the tools read (data_v1/kiosk is the 231-SKU Objective 1 catalogue)")
    p.add_argument("--corpus", default=None, help="Objective 4: the store information to retrieve from "
                   "(default knowledge/corpus.jsonl; finetune/knowledge/corpus.jsonl for the training catalogue)")
    g = p.add_argument_group("retrieval (Objective 2)")
    g.add_argument("--retrieval", default="none", choices=["none", "oracle", "always", "tool", "routed"],
                   help="routed (Objective 3, Step 4): the intent router sends store questions and unclear messages "
                        "down the 'always' path and everything else without retrieval")
    g.add_argument("--fallback", default="shadow", choices=["shadow", "live", "gate", "store-live"],
                   help="store-live (Objective 3, Step 8, with --retrieval routed): below the threshold a store question "
                        "with no product code or catalogue name gets the fixed reply with no model call; otherwise "
                        "as gate")
    g.add_argument("--k-chunks", type=int, default=None, help="Chunks shown (default: k from Step 7a, else 5)")
    g.add_argument("--fallback-config", default=None, help="Default results_retrieval/fallback_bypass/fallback.json")
    g.add_argument("--retriever-threads", type=int, default=4)
    g.add_argument("--reranker-choice", default=None,
                   help="Objective 3, Step 9: choice.json from retrieval/bench_reranker.py (re-ranker and depth)")
    g.add_argument("--fake-retriever", action="store_true", help="Stand-in encoders (tests only)")
    g.add_argument("--context-view", default="full", choices=["full", "compact", "focused"],
                   help="compact: product cards without the marketing description (Step 7d); focused (Objective 3, "
                        "Step 13): compact cards cut to the lines the question is about")
    g.add_argument("--chunk-gate", action="store_true",
                   help="Show only chunks scoring at or above the fallback threshold (Step 7d)")
    g.add_argument("--gate-style", default="message", choices=["message", "omit"],
                   help="When the gate applies: show '(nothing relevant found)' (Step 7 pilot) or add nothing (Step 7e)")
    g.add_argument("--dedupe-shown", action="store_true",
                   help="get_product_details on a product whose card was shown returns a short pointer (Step 7f)")
    g.add_argument("--rag-rule", default="rag_always_rule",
                   help="Key in eval/system_prompts.json for the always/oracle rule (Step 7e variants)")
    p.add_argument("--tool-view", default="json", choices=["json", "compact"],
                   help="compact (Objective 3, Step 3): tool results shown as short honest text (tools/render.py), "
                        "3 search results by default, spec words matched only against spec fields")
    p.add_argument("--loop-guard", action="store_true",
                   help="Step 3: repeated identical calls and repeated call_staff get a note instead of running; the "
                        "last allowed request may not call tools; an empty final reply gets a fixed staff line")
    p.add_argument("--harness-tools", action="store_true",
                   help="Step 5 (with --retrieval routed): for lookup, stock, compare and staff routes the harness "
                        "runs the tool itself and the model only writes the answer, in one request")
    p.add_argument("--store-one-round", action="store_true",
                   help="Step 5: store questions are answered from the cards in one request (no tool calls); a "
                        "service request gets call_staff first, and an answer that offers staff gets a real call")
    p.add_argument("--discovery", default="none", choices=["none", "template", "model"],
                   help="Step 6 (shopping route): read slots from the conversation; ask a slot question (template "
                        "text, or one model request) or run one search and let the model recommend in one request")
    p.add_argument("--forced-answer", default="replace", choices=["replace", "recover"],
                   help="With --loop-guard: what happens when the model prints a tool call as text on a request that "
                        "may not call tools. replace (Step 6c): the fixed staff line. recover (Step 7): a note says "
                        "tools are finished; prose around a printed call is kept; otherwise the printed call is run "
                        "once (read-only tools) and the answer asked for once more")
    p.add_argument("--staff-guard", action="store_true",
                   help="Step 7: on model-driven routes, an answer that offers staff without calling call_staff gets "
                        "a real call from the harness (offering staff means calling staff)")
    p.add_argument("--answer-length", action="store_true",
                   help="Step 13: ask for short replies (40 words for a fact, 60 for a recommendation); a reply cut by "
                        "max_tokens ends at its last full sentence")
    p.add_argument("--parallel-tools", action="store_true",
                   help="Step 13: let the model make two tool calls in one round (parallel_tool_calls)")
    p.add_argument("--followup-retrieval", action="store_true",
                   help="Step 11: a follow-up about the watch in focus is retrieved with the earlier customer turn and "
                        "the watch's name appended (harness/focus.py)")
    p.add_argument("--focus-memory", action="store_true",
                   help="Step 11: for such follow-ups the focused watch's card is shown as card [1], its code goes to "
                        "the harness-run tools, and an inherited shopping route is replaced by the message's own route")
    p.add_argument("--verify-answers", default="off", choices=["off", "shown", "cited"],
                   help="Step 10 (store and unclear routes): a reply with a number, code or spec word not in the cards "
                        "and tool results shown (shown) or in the cards it cites (cited) gets the fixed reply")
    p.add_argument("--entity-check", action="store_true",
                   help="Step 8 (with --retrieval routed): other brands, smartwatches, non-watch items and designs that "
                        "do not exist get a fixed reply plus real Veyra matches, with no model call (harness/entity.py)")
    p.add_argument("--staff-check", action="store_true",
                   help="Step 8: the first call_staff for an unanswered question, when cards or tool results were "
                        "shown, returns a note asking the model to check them; a second call runs")
    p.add_argument("--tools-prompt", default="tools",
                   help="Key in eval/system_prompts.json for the tools system prompt (Step 7: tools_v12)")
    p.add_argument("--dialogues", default=None,
                   help="Step 6: run simulated discovery dialogues from this profile file (eval/o3_dialogues.jsonl) "
                        "instead of single cases; one record per dialogue")
    p.add_argument("--config-label", default="",
                   help="Name of the configuration being measured, e.g. O3-B0 (Objective 3); stored per record")
    p.add_argument("--no-count-tokens", dest="count_tokens", action="store_false",
                   help="Skip the after-case /tokenize requests that count context and tool-output tokens")
    o5 = p.add_argument_group("Objective 5 (kiosk_core)")
    o5.add_argument("--engine", default="legacy", choices=["legacy", "core"],
                    help="core: the turn engine shared with the app (kiosk_core/engine.py), with per-stage timing; "
                         "legacy: this file's own copy, kept until the Step 2 parity run has passed")
    o5.add_argument("--no-stages", dest="stages", action="store_false",
                    help="With --engine core: no per-stage clock (Step 3 measures its cost against this)")
    o5.add_argument("--stage-policy", default="resident", choices=["resident", "sequential"],
                    help="With --engine core: sequential keeps the retrieval models in a worker process that runs "
                         "only from routing to the model's first round (kiosk_core/stage_manager.py)")
    o5.add_argument("--images", action="store_true",
                    help="With --engine core (Step 7): a request to see a watch gets its pictures from the media "
                         "table (show_product_images, run by the harness); URLs are removed from model text")
    o5.add_argument("--ordinal-refs", action="store_true",
                    help="With --focus-memory (Step 9): 'the second one' picks that watch from the kiosk's latest "
                         "list (harness/focus.py ordinal_focus) and is treated as a follow-up about it")
    o5.add_argument("--stream-check", action="store_true",
                    help="With --engine core (Step 4): every model request is also sent streamed and the two replies "
                         "are compared (kiosk_core/stream_check.py); the turn goes on with the non-streamed reply")
    p.add_argument("--warmup", action="store_true",
                   help="Before the cases, send one unlogged request so the system prompt and tools are cached, "
                        "as a kiosk would at start-up")
    return p


def main(argv=None, server_pid=None):
    args = make_parser().parse_args(argv)
    base_url = args.url.rstrip("/")
    out_dir = os.path.join(args.results_dir, args.name)
    os.makedirs(out_dir, exist_ok=True)
    cases_path = os.path.join(out_dir, "cases.jsonl")

    with open(os.path.join(ROOT, "eval", "system_prompts.json"), encoding="utf-8") as f:
        prompts = json.load(f)
    schemas = mock_tools.load_schemas()
    mock_tools.HONEST = args.tool_view == "compact"
    mock_tools.DEFAULT_LIMIT = 3 if args.tool_view == "compact" else 5
    if args.tool_view == "compact":
        schemas = json.loads(json.dumps(schemas))
        for sc in schemas:
            if sc["function"]["name"] == "search_catalogue":
                sc["function"]["parameters"]["properties"]["limit"]["description"] = "Maximum results, default 3, maximum 10."
    mock_tools.reload(args.data_dir)
    mock_tools._TICKET[0] = 0      # Objective 5: staff ticket numbers start at REQ-0001 in every run, so a run's replies
    #                                do not depend on how many runs came before it in the same plan process
    mock_tools.STAFF_LOG = os.path.join(out_dir, "staff_requests.log")
    cases = load_dialogues(args.dialogues, args.split, args.ids, args.limit) if args.dialogues else \
        load_cases(args.eval, args.set, args.split, args.ids, args.category, args.limit)

    done = set()
    if os.path.exists(cases_path):
        with open(cases_path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if not r.get("error"):
                        done.add((r["id"], r["repeat"]))
                except json.JSONDecodeError:
                    pass

    if not wait_for_server(base_url, timeout_s=60):
        print(f"Server at {base_url} is not ready. Start llama-server first.", file=sys.stderr)
        return 2
    props = {}
    try:
        props = http_json(base_url + "/props", timeout=10)
    except Exception:  # noqa: BLE001 - optional endpoint
        pass

    if args.rag_rule not in prompts:
        print(f"Unknown --rag-rule {args.rag_rule}; keys: {', '.join(k for k in prompts if k.startswith('rag_'))}", file=sys.stderr)
        return 2
    RAG_RULE["always"] = args.rag_rule
    if args.tools_prompt not in prompts:
        print(f"Unknown --tools-prompt {args.tools_prompt}", file=sys.stderr)
        return 2
    TOOLS_PROMPT["key"] = args.tools_prompt
    ANSWER_RULE["on"] = args.answer_length
    kb, chunks, kb_meta = None, None, None
    if args.images and args.engine != "core":
        print("--images needs --engine core", file=sys.stderr)
        return 2
    if args.stream_check and args.engine != "core":
        print("--stream-check needs --engine core", file=sys.stderr)
        return 2
    if args.stage_policy != "resident" and args.engine != "core":
        print("--stage-policy sequential needs --engine core", file=sys.stderr)
        return 2
    sequential = args.engine == "core" and args.stage_policy == "sequential"
    if args.retrieval in ("always", "tool", "routed"):
        rss0 = own_rss_mb()
        t = time.time()
        rchoice = {}
        if args.reranker_choice:      # Objective 3, Step 9: the re-ranker and depth chosen by bench_reranker.py
            with open(args.reranker_choice, encoding="utf-8") as f:
                rchoice = json.load(f)
        KB_KWARGS.clear()
        KB_KWARGS.update(**({"corpus_path": args.corpus} if args.corpus else {}),
                         fallback_path=args.fallback_config or DEFAULT_FALLBACK, k=args.k_chunks,
                         **{k: rchoice[k] for k in ("reranker", "depth", "backend", "max_length", "int8", "rerank_view")
                            if k in rchoice},
                         threads=int(rchoice.get("threads", args.retriever_threads)), fake=args.fake_retriever,
                         view=args.context_view, chunk_gate=args.chunk_gate)
        if sequential:
            kb_meta = {}                      # Objective 5: the retrieval worker loads it (below), not this process
        else:
            kb = KnowledgeBase(**KB_KWARGS)
            kb_meta = dict(kb.config, load_s=round(time.time() - t, 1), reused_from_earlier_run=kb.reused,
                           added_rss_mb=(own_rss_mb() - rss0) if rss0 and not kb.reused else None)
            print(f"Knowledge base ready in {kb_meta['load_s']} s (k={kb.k}, threshold {kb.threshold:.3f}, "
                  f"Hinglish bypass {kb.bypass}, +{kb_meta['added_rss_mb']} MB)")
    elif args.retrieval == "oracle":
        chunks = load_chunks()
        kb_meta = {"oracle": True, "corpus": "knowledge/corpus.jsonl"}
    if kb is not None:
        chunks = kb.chunks
    if args.retrieval == "routed" and not sequential:
        if ROUTER.get("key") != id(kb.dense):
            t = time.time()
            ROUTER["r"], ROUTER["key"] = Router(encoder=kb.dense), id(kb.dense)
            print(f"Router ready in {time.time() - t:.1f} s ({sum(len(v) for v in ROUTER['r'].prototypes.values())} prototypes)")
        kb_meta = dict(kb_meta or {}, router={"prototypes": "router/prototypes.json", "rule_margin": RULE_MARGIN,
                                              "proto_margin": PROTO_MARGIN, "retrieve_routes": sorted(RETRIEVE_ROUTES)})

    engine, manager = None, None
    if args.engine == "core":
        from kiosk_core import engine
        from kiosk_core import stages as kstages
        engine.RAG_RULE["always"], engine.TOOLS_PROMPT["key"] = RAG_RULE["always"], TOOLS_PROMPT["key"]
        engine.ANSWER_RULE["on"] = ANSWER_RULE["on"]
        engine.ROUTER.clear()
        engine.ROUTER.update(ROUTER)
        if args.stream_check:
            from kiosk_core import stream_check
            stream_check.install(engine)
        kstages.HOOKS.clear()

    if args.warmup and cases:
        tools_case = next((c for c in cases if c["mode"] == "tools" and not c.get("context")), None)
        if tools_case:
            wm = build_messages(dict(tools_case, messages=[{"role": "user", "content": "Hello"}]), prompts, args.retrieval)
            body = {"model": "local", "messages": wm, "max_tokens": 1, "temperature": 0, "cache_prompt": True,
                    "tools": schemas + ([SEARCH_KNOWLEDGE_SCHEMA] if args.retrieval == "tool" else [])}
            if args.no_thinking:
                body["chat_template_kwargs"] = {"enable_thinking": False}
            try:
                t = time.time()
                http_json(base_url + "/v1/chat/completions", body, timeout=args.request_timeout)
                print(f"Warm-up request: {time.time() - t:.1f} s (not logged)")
            except Exception as e:  # noqa: BLE001
                print(f"Warm-up failed ({e}); continuing")

    ram = RamMonitor(pid=server_pid or args.server_pid)
    ram.start()
    if engine is not None and args.stage_policy == "sequential":
        # Objective 5, Step 3: the retrieval models move to a worker that lives from routing to the first model
        # round of each turn; the in-process copy built above is not used by the turns
        from kiosk_core.stage_manager import StageManager
        from router.router import _catalogue_names
        if args.retrieval not in ("always", "routed"):
            print("--stage-policy sequential needs --retrieval always or routed", file=sys.stderr)
            return 2
        kb_kwargs = dict(KB_KWARGS)
        manager = StageManager("sequential", kb_kwargs, ram=ram,
                               router_names=list(_catalogue_names()) if args.retrieval == "routed" else None)
        kb, chunks = manager.kb, manager.kb.chunks
        if manager.router is not None:
            engine.ROUTER["r"] = manager.router
        kstages.HOOKS.update(manager.hooks())
        kb_meta = dict(kb_meta or {}, **manager.attrs["config"], stage_policy="sequential",
                       worker_first_start_ms=manager.starts[0],
                       router={"prototypes": "router/prototypes.json", "rule_margin": RULE_MARGIN,
                               "proto_margin": PROTO_MARGIN, "retrieve_routes": sorted(RETRIEVE_ROUTES)}
                       if args.retrieval == "routed" else None)
        print(f"Sequential stage policy: retrieval worker start {manager.starts[0]:.0f} ms")
    meta_path = os.path.join(out_dir, "run_meta.json")
    meta = {
        "name": args.name, "model": args.model, "quant": args.quant, "backend": args.backend,
        "eval_file": os.path.relpath(args.dialogues or args.eval, ROOT), "filters": {"set": args.set, "split": args.split,
                                                                   "ids": args.ids, "category": args.category,
                                                                   "limit": args.limit},
        "n_cases": len(cases), "repeats": args.repeats, "config_label": args.config_label,
        "tool_view": args.tool_view, "loop_guard": args.loop_guard,
        "harness_tools": args.harness_tools, "store_one_round": args.store_one_round, "discovery": args.discovery,
        "forced_answer": args.forced_answer, "staff_guard": args.staff_guard, "tools_prompt": args.tools_prompt,
        "entity_check": args.entity_check, "staff_check": args.staff_check, "verify_answers": args.verify_answers,
        "followup_retrieval": args.followup_retrieval, "focus_memory": args.focus_memory,
        "answer_length": args.answer_length, "parallel_tools": args.parallel_tools,
        "engine": args.engine, "stages": args.stages if args.engine == "core" else None,
        "stage_policy": args.stage_policy if args.engine == "core" else None,
        "data_dir": os.path.relpath(args.data_dir, ROOT),
        "warmup": args.warmup,
        
        "retrieval": {"condition": args.retrieval,
                      "fallback": args.fallback if args.retrieval in ("always", "routed") else None,
                      "context_view": args.context_view, "chunk_gate": args.chunk_gate,
                      "gate_style": args.gate_style, "rag_rule": args.rag_rule, "dedupe_shown": args.dedupe_shown,
                      "knowledge_base": kb_meta},
        "decoding": {"temperature": args.temperature, "top_k": args.top_k, "seed": args.seed,
                     "max_tokens": args.max_tokens, "max_rounds": args.max_rounds, "thinking": not args.no_thinking},
        "server_props": {k: props.get(k) for k in ("model_path", "build_info", "total_slots", "chat_template")
                         if k in props} | ({"n_ctx": props.get("default_generation_settings", {}).get("n_ctx")}
                                           if props else {}),
        "ram_tracking": ram.describe(),
        # one "machine" entry: the label (laptop / kaggle-cpu, from harness/machine.py) and the hardware. A second
        # "machine" key used to follow the first and drop the label, so every run read as "local"
        "machine": dict(machine_info(), platform=platform.platform(), processor=platform.processor(),
                        cpu_count=os.cpu_count(), total_ram_gb=ram.total_ram_gb()),
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    if "chat_template" in meta["server_props"] and meta["server_props"]["chat_template"]:
        meta["server_props"]["chat_template"] = meta["server_props"]["chat_template"][:300] + "..."
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    todo = [(c, r) for r in range(args.repeats) for c in cases if (c["id"], r) not in done]
    print(f"{args.name}: {len(cases)} cases x {args.repeats} repeats, {len(done)} already done, {len(todo)} to run")
    down_streak, n_err, t_start = 0, 0, time.time()
    if os.path.exists(cases_path) and os.path.getsize(cases_path):
        with open(cases_path, "rb") as f:          # a run stopped mid-line (Kaggle time budget): start a new line
            f.seek(-1, os.SEEK_END)
            cut = f.read(1) != b"\n"
        if cut:
            with open(cases_path, "a", encoding="utf-8") as f:
                f.write("\n")
    with open(cases_path, "a", encoding="utf-8") as out:
        for i, (case, rep) in enumerate(todo, 1):
            rec = {"id": case["id"], "repeat": rep, "category": case["category"], "subcategory": case["subcategory"],
                   "mode": case["mode"], "language": case["language"], "set": case.get("set", "core"),
                   "split": case["split"], "paired_with": case.get("paired_with"),
                   "model": args.model, "quant": args.quant, "backend": args.backend, "run": args.name,
                   "config": args.config_label, "route": "none",
                   "time": datetime.now().isoformat(timespec="seconds")}
            try:
                if engine is not None:
                    fn = engine.run_dialogue if args.dialogues else engine.run_case
                else:
                    fn = run_dialogue if args.dialogues else run_case
                out_case = fn(case, args, prompts, schemas, base_url, ram, kb, chunks)
                if args.stream_check:
                    out_case["stream_check"] = stream_check.drain()
                texts = out_case.pop("_token_texts", None)
                rec.update(out_case)
                if args.dialogues:
                    rec["route"] = "dialogue"
                add_token_counts(rec, texts, base_url, args.count_tokens)
                down_streak = 0
            except ServerDown as e:
                down_streak += 1
                rec["error"] = f"server_down: {e}"
                n_err += 1
                if down_streak >= 3:
                    out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    print("Server unreachable 3 times in a row; stopping. Rerun to resume.", file=sys.stderr)
                    break
            except Exception as e:  # noqa: BLE001 - record and continue
                rec["error"] = f"{type(e).__name__}: {e}"
                n_err += 1
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            m = rec.get("metrics", {})
            eta = (time.time() - t_start) / i * (len(todo) - i)
            print(f"[{i}/{len(todo)}] {case['id']} r{rep} "
                  f"{'ERROR ' + rec['error'][:60] if rec.get('error') else ''}"
                  f"{len(rec.get('tool_calls', []))} calls, {m.get('end_to_end_ms', 0) / 1000:.1f}s "
                  f"| eta {eta / 60:.0f} min", flush=True)

    ram.stop()
    if manager is not None:
        manager.shutdown()
        meta["stage_manager"] = {"policy": "sequential", "worker_starts": len(manager.starts),
                                 "worker_start_ms_median": sorted(manager.starts)[len(manager.starts) // 2]}
    meta.update({"finished": datetime.now().isoformat(timespec="seconds"), "errors": n_err,
                 "run_peak_rss_mb": ram.run_peak_mb(), "wall_minutes": round((time.time() - t_start) / 60, 1)})
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"Done: {cases_path}  (errors: {n_err}, peak server RAM: {ram.run_peak_mb()} MB)")
    return 0 if n_err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
