"""
Objective 5, Step 4: streaming the reply to the screen.

The Step 4 check found streamed and non-streamed replies identical on every dev tool case for both models
(results_obj5/_stream_step4), so by the pre-registered rule every model round streams. During a kiosk turn the
engine's chat requests go out with "stream": true; the text arrives a few words at a time as "token" events, and the
pieces are put back together into the exact response the engine expects (content, tool calls, finish reason, usage
and timings), so the turn's logic and record are unchanged.

What the customer never sees:
  - tool-call markup: a round whose text starts like a tool call or JSON ('<', '{', '[') is held back, not streamed;
  - half a word: text is released only up to the last space, so a name such as the brand never reaches the screen
    split in two (the brand placeholder is applied per event).
The checks still run after the model: the "final" event carries the reply the customer keeps, and replaces the
streamed text if a check changed it.

Used only by the app (kiosk_core.turn.run_turn with stream=True); the harness never streams.
"""
import json
import time
import urllib.error
import urllib.request

HOLD = ("<", "{", "[", "```")


class _Release:
    """Decides what part of one round's text can go to the screen."""

    def __init__(self, emit, round_no):
        self.emit, self.round, self.buf, self.sent, self.held = emit, round_no, "", 0, None

    def add(self, piece):
        self.buf += piece
        if self.held is None:
            head = self.buf.lstrip()
            if not head:
                return
            if head.startswith(HOLD) or (len(head) < 4 and any(h.startswith(head) for h in HOLD)):
                self.held = head.startswith(HOLD)
                if not self.held:
                    self.held = None              # not decided yet ('`' could start a code fence)
                return
            self.held = False
        if self.held:
            return
        cut = max(self.buf.rfind(" "), self.buf.rfind("\n"))
        if cut + 1 > self.sent:
            self.emit({"type": "token", "round": self.round, "text": self.buf[self.sent:cut + 1]})
            self.sent = cut + 1

    def end(self):
        if self.held is False and len(self.buf) > self.sent:
            self.emit({"type": "token", "round": self.round, "text": self.buf[self.sent:]})
            self.sent = len(self.buf)


def make_http_json(plain, emit):
    """A drop-in for kiosk_core.engine.http_json that streams chat requests and emits 'token' events."""
    state = {"round": 0}

    def http_json(url, payload=None, timeout=600):
        if payload is None or not url.endswith("/v1/chat/completions") or (payload.get("max_tokens") or 0) <= 1:
            return plain(url, payload, timeout)
        body = dict(payload, stream=True, stream_options={"include_usage": True})
        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        rel = _Release(emit, state["round"])
        state["round"] += 1
        emit({"type": "round_start", "round": rel.round})
        content, calls, finish, usage, timings, first_ms = [], {}, None, None, None, None
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                for raw in r:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    ev = json.loads(data)
                    if "error" in ev:
                        raise RuntimeError(f"HTTP 500: {json.dumps(ev['error'])[:500]}")
                    usage = ev.get("usage") or usage
                    timings = ev.get("timings") or timings
                    for ch in ev.get("choices") or []:
                        d = ch.get("delta") or {}
                        if d.get("content"):
                            if first_ms is None:
                                first_ms = round((time.time() - t0) * 1000, 1)
                            content.append(d["content"])
                            rel.add(d["content"])
                        for tc in d.get("tool_calls") or []:
                            c = calls.setdefault(tc.get("index", 0), {"id": None, "name": "", "arguments": ""})
                            c["id"] = tc.get("id") or c["id"]
                            f = tc.get("function") or {}
                            c["name"] += f.get("name") or ""
                            c["arguments"] += f.get("arguments") or ""
                        if ch.get("finish_reason"):
                            finish = ch["finish_reason"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:2000]}") from None
        rel.end()
        text = "".join(content)
        msg = {"role": "assistant", "content": text if text or not calls else None}
        if calls:
            msg["tool_calls"] = [{"id": c["id"] or f"call_{k}", "type": "function",
                                  "function": {"name": c["name"], "arguments": c["arguments"]}}
                                 for k, c in sorted(calls.items())]
        out = {"choices": [{"index": 0, "message": msg, "finish_reason": finish or ("tool_calls" if calls else "stop")}]}
        if usage:
            out["usage"] = usage
        if timings:
            out["timings"] = timings
        out["_stream"] = {"first_token_ms": first_ms, "streamed_chars": rel.sent, "held": bool(rel.held)}
        return out

    return http_json
