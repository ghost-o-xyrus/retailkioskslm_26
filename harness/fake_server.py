"""
A tiny stand-in for llama-server, used only to test the harness without a real model.

It answers /health, /props, /tokenize (4 characters a token) and /v1/chat/completions in llama-server's format (including the
`timings` block and `cache_n`), and behaves predictably:
  - grounded requests (no tools): a short answer, wrapped in <think> tags if the question contains "think"
  - tool requests, user turn:
        contains a product ID and "stock"    -> check_inventory call
        contains a product ID and "try"      -> call_staff(reason=try_on)
        contains a product ID                -> get_product_details call
        contains "astext"                    -> tool call written as plain text (a format failure)
        contains "badjson"                   -> tool call with invalid JSON arguments
        contains "kbq" (search_knowledge offered) -> search_knowledge call
        greeting ("hi", "hello", "thanks")   -> plain reply, no tool
        anything else                        -> search_catalogue(price_max=15000)
  - tool requests after a tool result: a reply quoting the start of the result
  - first user message containing "loopme" / "staffloop": the same search / call_staff on every request;
    "emptyreply": an empty reply; tool_choice "none": a plain answer (Step 3 loop guard tests)
  - tool_choice "none" and "printcall" / "printprose" / "printstaff" in the first user message: a tool call printed as
    text, the same with an answer before it, a printed call_staff (Step 7 tests); "offerstaff": offers staff in words

    python harness/fake_server.py --port 8099
"""

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ID_RE = re.compile(r"\b\d{4}[A-Z]{2}\d{2}\b")
STATE = {"last_prompt_chars": 0, "n": 0}


def tool_call(name, args, raw=None):
    STATE["n"] += 1
    return {"id": f"call_{STATE['n']}", "type": "function",
            "function": {"name": name, "arguments": raw if raw is not None else json.dumps(args)}}


DEMO = {"on": False}     # --demo (the app's stand-in mode): forced answers quote what the kiosk was shown


def demo_reply(msgs):
    """A readable stand-in answer: the first lines of the last tool result, or of the store information shown."""
    tool = next((m.get("content") or "" for m in reversed(msgs) if m["role"] == "tool"), None)
    if tool:
        lines = [x.strip() for x in tool.splitlines() if x.strip()][:4]
        return "(stand-in reply) " + " ".join(lines)[:400]
    user = next((m.get("content") or "" for m in reversed(msgs) if m["role"] == "user"), "")
    cards = [x.strip() for x in user.splitlines() if x.strip().startswith("[")][:1]
    if cards:
        return "(stand-in reply) From the store information: " + cards[0][:300]
    return "(stand-in reply) Hello! How can I help you find a watch today?"


def respond(body):
    msgs = body.get("messages", [])
    last = msgs[-1]
    tools = body.get("tools")
    content, calls = "", None
    first_user = next((m.get("content", "") for m in msgs if m["role"] == "user"), "")
    if tools and body.get("tool_choice") == "none":
        content = "Final answer without tools."
        if "offerstaff" in first_user:
            content = "I'm not sure about that; our staff can help."
        last_tool = next((m.get("name") for m in reversed(msgs) if m["role"] == "tool"), None)
        pid = (ID_RE.search(first_user) or ID_RE.search(json.dumps(msgs))).group(0) if ID_RE.search(json.dumps(msgs)) else "1000AA00"
        printed = f"<tool_call>\n<function=get_product_details>\n<parameter=product_id>\n{pid}\n</parameter>\n</function>\n</tool_call>"
        if "printcall" in first_user and last_tool != "get_product_details":
            content = printed                                  # Step 7: a call printed instead of an answer
        elif "printprose" in first_user:
            content = "Here is a good watch for you, it is in stock here today.\n" + printed
        elif "printstaff" in first_user:
            content = '{"name": "call_staff", "arguments": {"reason": "try_on"}}'
        elif DEMO["on"]:
            content = demo_reply(msgs)
    elif tools and "inventdetail" in first_user and last["role"] == "user":  # Step 10: a detail nobody showed
        content = "It has a ceramic case and 300 m water resistance."
    elif tools and "citeone" in first_user and last["role"] == "user":       # Step 10: a cited answer
        content = "Yes, we can help with that. [1]"
    elif tools and "staffask" in first_user and last["role"] == "user":     # Step 8 staff check
        calls = [tool_call("call_staff", {"reason": "question_unanswered", "note": "can't answer"})]
    elif tools and "offerstaff" in first_user and last["role"] == "user":
        content = "I'm not sure about that; a staff member can help you with it."
    elif tools and "loopme" in first_user:          # a model stuck repeating the same call
        calls = [tool_call("search_catalogue", {"query": "loop"})]
    elif tools and "staffloop" in first_user:       # a model calling staff again and again
        calls = [tool_call("call_staff", {"reason": "other", "note": f"help {len(msgs)}"})]
    elif tools and "emptyreply" in first_user:
        content = ""
    elif DEMO["on"] and tools and last["role"] == "user" and "[1]" in (last.get("content") or ""):
        content = demo_reply(msgs)                     # the app's stand-in: a store question with cards shown
    elif not tools:
        q = last.get("content", "")
        content = "It is rated to 50 m and has a mineral glass."
        if "think" in q.lower():
            content = "<think>let me check the spec</think>" + content
    elif last["role"] == "tool":
        content = "Here is what I found: " + last["content"][:160]
    else:
        q = last.get("content", "")
        m = ID_RE.search(q)
        if "astext" in q:
            content = '<tool_call>{"name": "search_catalogue", "arguments": {"price_max": 5000}}</tool_call>'
        elif "badjson" in q:
            calls = [tool_call("search_catalogue", None, raw="{price_max: 5000")]
        elif m and "stock" in q.lower():
            calls = [tool_call("check_inventory", {"product_id": m.group(0)})]
        elif m and "try" in q.lower():
            calls = [tool_call("call_staff", {"reason": "try_on", "product_id": m.group(0)})]
        elif m:
            calls = [tool_call("get_product_details", {"product_id": m.group(0)})]
        elif "kbq" in q.lower() and any(t["function"]["name"] == "search_knowledge" for t in tools):
            calls = [tool_call("search_knowledge", {"query": q.split("Customer:")[-1].replace("kbq", "").strip()})]
        elif re.match(r"^\s*(hi|hello|thanks)", q.lower()):
            content = "Hello! How can I help you find a watch today?"
        else:
            calls = [tool_call("search_catalogue", {"price_max": 15000})]

    prompt_chars = len(json.dumps(msgs)) + len(json.dumps(tools or []))
    prompt_tokens = prompt_chars // 4
    cached = min(STATE["last_prompt_chars"], prompt_chars) // 4 if tools else 0
    STATE["last_prompt_chars"] = prompt_chars
    gen = max(8, len(content) // 4 + (20 if calls else 0))
    msg = {"role": "assistant", "content": content}
    if calls:
        msg["tool_calls"] = calls
    return {
        "id": "chatcmpl-fake", "object": "chat.completion", "model": "fake",
        "choices": [{"index": 0, "message": msg, "finish_reason": "tool_calls" if calls else "stop"}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": gen, "total_tokens": prompt_tokens + gen},
        "timings": {"prompt_n": prompt_tokens - cached, "cache_n": cached, "prompt_ms": 2.0 * (prompt_tokens - cached),
                    "predicted_n": gen, "predicted_ms": gen * 10.0, "predicted_per_second": 100.0},
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send({"status": "ok"})
        elif self.path == "/props":
            self._send({"model_path": "fake.gguf", "build_info": "fake-server", "total_slots": 1,
                        "default_generation_settings": {"n_ctx": 8192}})
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/v1/chat/completions":
            last = next((m.get("content") or "" for m in reversed(body.get("messages", [])) if m.get("role") == "user"), "")
            if "fail500" in str(last) and int(body.get("max_tokens") or 512) < 512:
                self._send({"error": {"code": 500, "message": "Failed to parse tool call"}}, 500)   # Step 13a2
                return
            resp = respond(body)
            if body.get("stream"):
                self._stream(resp, split_args="streamsplit" in str(last))
                return
            self._send(resp)
        elif self.path == "/tokenize":
            self._send({"tokens": list(range(len(body.get("content", "")) // 4))})
        else:
            self._send({"error": "not found"}, 404)

    def _stream(self, resp, split_args=False):
        """Objective 5, Step 4: the same reply as server-sent chunks in llama-server's OpenAI format. Content goes out
        a few characters at a time; each tool call's name first, then its arguments in pieces. 'streamsplit' in the
        question makes the streamed arguments differ (to test the check)."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        msg, fin = resp["choices"][0]["message"], resp["choices"][0]["finish_reason"]

        def chunk(delta, finish=None):
            d = {"choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
            self.wfile.write(("data: " + json.dumps(d) + "\n\n").encode())
        chunk({"role": "assistant"})
        text = msg.get("content") or ""
        for i in range(0, len(text), 7):
            chunk({"content": text[i:i + 7]})
        for k, c in enumerate(msg.get("tool_calls") or []):
            chunk({"tool_calls": [{"index": k, "id": c.get("id"), "type": "function",
                                   "function": {"name": c["function"]["name"], "arguments": ""}}]})
            args = c["function"]["arguments"]
            if split_args:
                args = args.replace("}", ', "x": 1}', 1) if args.strip() not in ("", "{}") else '{"x": 1}'
            for i in range(0, len(args), 5):
                chunk({"tool_calls": [{"index": k, "function": {"arguments": args[i:i + 5]}}]})
        chunk({}, fin)
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--demo", action="store_true", help="forced answers quote the shown information (the app's stand-in)")
    a, _ = ap.parse_known_args()
    DEMO["on"] = a.demo
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()
