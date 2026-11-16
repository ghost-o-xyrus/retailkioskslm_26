"""
Objective 4, Step 2b: the oracle. A stand-in for llama-server that answers every request the harness sends with the
CORRECT next action for that training question, and logs request and answer. Run through the real harness
(run_eval.py with O3-final's settings), it turns the training questions into training examples whose text is exactly
what the model sees at run time: system prompt, tools, shown cards, harness-run tool rounds and notes.

    python finetune\\oracle_server.py --cases finetune\\train\\store.jsonl --log results_o4\\traj\\x.jsonl --port 8080
    (run_plan.py starts it through a plan's "server_cmd")

Which case a request belongs to: the case whose customer turns all appear, in order, in the request's user messages.
The next action, from the case's "o4" label (see build_train_questions.py) and what the request shows:
    tools allowed and expected calls not yet made           -> the next call (two at once when parallel tool calls
                                                               are on and both have their arguments)
    an answer whose evidence is not in what was shown, a
    product code is visible, details not yet fetched        -> get_product_details for it (tools allowed)
    otherwise                                               -> a reply: answer, "not listed", decline, confirmation
                                                               of the staff call, or refusal
Replies here are drafts from templates (the "draft" field says which). Step 3 replaces each draft with the
teacher's wording and filters it; the template text is the fallback when no teacher is used.
"""

import argparse
import json
import os
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "eval"))
from checks import text_has  # noqa: E402

CODE_RE = re.compile(r"\b\d{4}[A-Z]{2}\d{2}\b")
LOCK = threading.Lock()
STATE = {"cases": [], "log": None, "n": 0}

T = {
    "not_listed": ("Sorry, that detail isn't listed for this watch. Would you like me to call a staff member to check?",
                   "Maaf kijiye, yeh detail listed nahi hai. Kya main staff member ko bula doon?"),
    "missing": ("Sorry, I don't have that information here. Would you like me to call a staff member?",
                "Maaf kijiye, mere paas yeh jaankari nahi hai. Kya main staff member ko bula doon?"),
    "not_sold": ("Sorry, we don't sell that here. This store sells Veyra watches only.",
                 "Maaf kijiye, yeh hum nahi bechte. Is store mein sirf Veyra watches milti hain."),
    "off_topic": ("Sorry, I can only help with watches and this store. Is there a watch I can help you find?",
                  "Maaf kijiye, main sirf watches aur is store ke baare mein madad kar sakta hoon."),
    "missing_policy": ("I'm not sure about that; it isn't in the store information. Would you like me to call a "
                       "staff member?", "Iske baare mein jaankari nahi hai. Kya main staff member ko bula doon?"),
    "nonexistent_product": ("Sorry, I couldn't find a watch by that name. Would you like me to show similar watches?",
                            "Maaf kijiye, is naam ki koi watch nahi mili. Kya main milti-julti watches dikhaun?"),
    "internal_info": ("Sorry, I can't share internal information such as cost prices. I can tell you the MRP and the "
                      "current offers.", "Maaf kijiye, cost price jaisi andar ki jaankari main nahi bata sakta. MRP "
                      "aur current offers bata sakta hoon."),
    "discount": ("Sorry, I can't give discounts beyond the current offers. Would you like me to check the offers on "
                 "this watch?", "Maaf kijiye, current offers ke alawa discount nahi de sakta. Offers check karun?"),
    "not_found": ("Sorry, I couldn't find a watch with that code. Could you check the code on the tag?",
                  "Maaf kijiye, is code ki koi watch nahi mili. Tag pe code ek baar check karenge?"),
    "out_of_database": ("Sorry, we don't have that here. This store sells Veyra watches only.",
                        "Maaf kijiye, yeh yahan nahi milta. Is store mein sirf Veyra watches hain."),
    "promise": ("Sorry, I can't promise that. A staff member can tell you what's possible.",
                "Maaf kijiye, iska wada main nahi kar sakta. Staff member bata payenge."),
    "false_presupposition": ("Sorry, that isn't right according to the store information.",
                             "Maaf kijiye, store ki jaankari ke hisaab se aisa nahi hai."),
    "handoff": ("I've asked a staff member to come and help you. They'll be with you in a few minutes.",
                "Maine staff member ko bula diya hai. Woh kuch minute mein aa jayenge."),
    "in_stock": ("Yes, it's in stock at this store.", "Haan, yeh is store mein stock mein hai."),
    "out_of_stock": ("Sorry, it isn't in stock at this store right now.", "Maaf kijiye, abhi yeh is store mein stock mein nahi hai."),
    "yes": ("Yes, it comes with a {w} dial.", "Haan, yeh {w} dial mein aati hai."),
    "no": ("No, it doesn't come with a {w} dial.", "Nahi, yeh {w} dial mein nahi aati."),
}


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def user_turns(messages):
    return [m["content"] for m in messages if m.get("role") == "user" and isinstance(m.get("content"), str)]


def find_case(messages):
    users = user_turns(messages)
    if not users:
        return None
    best = None
    for c in STATE["cases"]:
        want = user_turns(c["messages"])
        if len(want) > len(users) or want[-1] not in users[len(want) - 1]:
            continue
        if all(w in u for w, u in zip(want, users[:len(want)])):
            if best is None or len(want) > len(user_turns(best["messages"])):
                best = c
    return best


def made_calls(messages):
    out = []
    for m in messages:
        for tc in m.get("tool_calls") or []:
            f = tc.get("function") or {}
            try:
                a = json.loads(f.get("arguments") or "{}")
            except json.JSONDecodeError:
                a = {}
            out.append((f.get("name"), a))
    return out


def same_call(spec, made):
    name, args = made
    if spec["name"] != name:
        return False
    key = spec["args"].get("product_id") or spec["args"].get("product_ids")
    return key is None or key == args.get("product_id") or key == args.get("product_ids")


def gold_text(msgs, o4):
    """The parts of what was shown that belong to the case's own product: its card (from "(design Vxxxx)" to the
    next card) and any tool result naming it. Evidence for a product question counts only there, so a fact that
    happens to appear on another watch's card is not mistaken for the answer."""
    ids = [g.split(":V")[1] for g in o4.get("gold_ids") or [] if g.startswith("product:V")]
    if not ids:
        return "\n".join(str(m.get("content") or "") for m in msgs if m.get("role") in ("user", "tool"))
    parts = []
    for m in msgs:
        t = str(m.get("content") or "")
        if m.get("role") == "user":
            for seg in re.split(r"\n(?=\[\d+\] )", t):
                if any(f"(design V{i})" in seg for i in ids):
                    parts.append(seg)
        elif m.get("role") == "tool" and any(re.search(rf"\b(V{i}|{i}[A-Z]{{2}}\d{{2}})\b", t) for i in ids):
            parts.append(t)
    return "\n".join(parts)


def snippet(text, groups):
    """The clause of the shown text that holds the evidence (for the draft answer)."""
    alts = [a for g in groups for a in g][:6]
    for part in re.split(r"(?<=[.!?])\s+|\n", text):
        if any(a.lower() in part.lower() for a in alts):
            return part.strip()[:220]
    low = text.lower()                                # the evidence spans a sentence break: a window around it
    for a in alts:
        i = low.find(a.lower())
        if i >= 0:
            return text[max(0, i - 80): i + len(a) + 80].strip()
    return ""


def reply_for(case, kind, shown, lang, results):
    h = 1 if lang != "en" else 0
    o4 = case["o4"]
    if o4.get("polarity"):
        key = o4["polarity"]
        return T[key][h].format(w=o4.get("word", "")), key
    if kind == "handoff":
        return T["handoff"][h], "handoff"
    if kind == "refuse":
        return T.get(case["subcategory"], T["promise"])[h], "refuse:" + case["subcategory"]
    if kind == "not_listed":
        return T["not_listed"][h], "not_listed"
    if kind == "decline":
        ev = o4.get("evidence") or []
        if ev and all(text_has(shown, g) for g in ev) and case["subcategory"] == "negative":
            s = snippet(shown, ev)
            return (("No. " if not h else "Nahi. ") + s).strip(), "decline:negative"
        return T.get(case["subcategory"], T["missing_policy"])[h], "decline:" + case["subcategory"]
    ev = o4.get("evidence") or []
    if kind == "tools":
        last = results[-1] if results else ""
        lines = [x.strip() for x in last.splitlines() if x.strip()][:4]
        lead = "Here's what I found:" if not h else "Yeh mila:"
        return (lead + " " + " ".join(lines))[:400], "tools"
    if ev and all(text_has(shown, g) for g in ev):
        s = snippet(shown, ev)
        if s:
            return (s if not h else "Store ki jaankari ke hisaab se: " + s), "answer"
    return T["missing"][h], "missing"


def decide(body):
    msgs = body.get("messages") or []
    case = find_case(msgs)
    if case is None:
        return {"role": "assistant", "content": "Hello! How can I help you today?"}, None, None
    o4 = case["o4"]
    kind = o4["kind"]
    lang = case.get("language", "en")
    tools_ok = bool(body.get("tools")) and body.get("tool_choice") != "none"
    made = made_calls(msgs)
    results = [m["content"] for m in msgs if m.get("role") == "tool"]
    shown = gold_text(msgs, o4)
    if tools_ok and kind in ("tools", "handoff"):
        left = [c for c in o4.get("calls") or [] if not any(same_call(c, m) for m in made)]
        if left:
            take = left[:2] if body.get("parallel_tool_calls") and len(left) > 1 and \
                all(c["args"] for c in left[:2]) else left[:1]
            return {"role": "assistant", "content": "", "tool_calls": [tool_call(c["name"], c["args"]) for c in take]}, \
                case, "call"
    ev = o4.get("evidence") or []
    if tools_ok and kind == "answer" and ev and not all(text_has(shown, g) for g in ev):
        gold = [g.split(":")[1] for g in o4.get("gold_ids") or [] if g.startswith("product:")]
        if gold and not any(n == "get_product_details" for n, _ in made):
            return {"role": "assistant", "content": "",
                    "tool_calls": [tool_call("get_product_details", {"product_id": gold[0]})]}, case, "fetch"
    text, draft = reply_for(case, kind, shown, lang, results)
    return {"role": "assistant", "content": text, "draft": draft}, case, "reply"


def tool_call(name, args):
    with LOCK:
        STATE["n"] += 1
        n = STATE["n"]
    return {"id": f"call_{n}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}


def respond(body):
    msg, case, action = decide(body)
    draft = msg.pop("draft", None)
    if case is not None and STATE["log"]:
        rec = {"case_id": case["id"], "action": action, "draft": draft,
               "request": {k: body.get(k) for k in ("messages", "tool_choice", "parallel_tool_calls", "max_tokens",
                                                    "chat_template_kwargs")},
               "tools": [t["function"]["name"] for t in body.get("tools") or []],
               "tools_schema": body.get("tools"), "response": msg}
        with LOCK, open(STATE["log"], "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    prompt_chars = sum(len(json.dumps(m)) for m in body.get("messages") or [])
    gen = max(1, len(msg.get("content") or "") // 4)
    return {"choices": [{"index": 0, "message": msg, "finish_reason": "tool_calls" if msg.get("tool_calls") else "stop"}],
            "usage": {"prompt_tokens": prompt_chars // 4, "completion_tokens": gen, "total_tokens": prompt_chars // 4 + gen},
            "timings": {"prompt_n": prompt_chars // 4, "cache_n": 0, "prompt_ms": 1.0, "predicted_n": gen,
                        "predicted_ms": 1.0, "predicted_per_second": 1000.0}}


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
            self._send({"model_path": "oracle", "build_info": "oracle-server", "total_slots": 1,
                        "default_generation_settings": {"n_ctx": 8192}})
        else:
            self._send({"error": "not found"}, 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/v1/chat/completions":
            self._send(respond(body))
        elif self.path == "/tokenize":
            self._send({"tokens": list(range(len(body.get("content", "")) // 4))})
        else:
            self._send({"error": "not found"}, 404)

    def log_message(self, *a):
        pass


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", nargs="+", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    a, _ = ap.parse_known_args(argv)
    for p in a.cases:
        STATE["cases"] += load_jsonl(p)
    os.makedirs(os.path.dirname(os.path.abspath(a.log)), exist_ok=True)
    STATE["log"] = a.log
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
