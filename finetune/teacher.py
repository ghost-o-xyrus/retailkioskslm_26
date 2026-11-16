"""
Objective 4, Step 3a: the teacher writes each training reply (Qwen3.5-9B, on Kaggle's GPU through llama-server).

    python finetune/teacher.py --servers http://127.0.0.1:8101 http://127.0.0.1:8102 --minutes 150
    python finetune/teacher.py --servers http://127.0.0.1:8101 --limit 100        # pilot: speed and a first look

Reads finetune/examples/wording_tasks.jsonl (export_examples.py) and appends one line per task to
finetune/teacher/replies.jsonl. Tasks already there are skipped, so an interrupted job resumes. It stops cleanly
when --minutes is reached and prints replies per hour.

The teacher sees the customer's question, what the kiosk was shown (the only facts it may use), the correct action
and the oracle's draft (correct, but plain), and writes the reply the kiosk should give. Thinking is off; sampling
at temperature 0.7 with a per-task seed, so wording varies across tasks but a rerun gives the same reply.
"""

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(HERE, "examples", "wording_tasks.jsonl")
OUT = os.path.join(HERE, "teacher", "replies.jsonl")

SYSTEM = """You write replies for the shopping assistant on an in-store kiosk at a Veyra watch store in India.
You are given the customer's message, the store information and tool results the kiosk was shown, the correct action, and a plain draft reply that is correct.
Write the reply the kiosk should give the customer. Rules:
- Use only facts that appear in the shown information. Never add a spec, price, code, number, colour, policy or promise that is not there.
- Keep every fact, product code and price the draft states, exactly as written (Rs amounts, mm, m, months).
- Follow the correct action: answer, say the detail is not listed, decline, confirm that staff are coming, or refuse. Do not change it.
- Offer to call a staff member only when the action says so, and then as a question ("Would you like me to call a staff member?"). Never say staff are coming unless the action is a staff call.
- Reply in the customer's language: English, or Hinglish (Hindi and English mixed, written in Roman letters) if they wrote Hinglish.
- Sound like a friendly, brief shop assistant. No headings, no bullet symbols other than a short numbered list when recommending watches, no emojis, no tool-call syntax, and do not mention "the store information", "cards" or "tool results".
- Do not end an answer by offering a staff member, in any language ("Kya main staff ko bulaun?", "call karun?"). Do not add claims about stock, availability or other models that are not in the shown information.
- Stay within the word limit given.
Return only the reply text."""

ACTION = {
    "answer": "answer the question from the shown information",
    "tools": "answer from the tool results shown (recommend at most 3 watches with code, name and price when there is a list)",
    "not_listed": "say this detail is not listed for this watch, and ask whether they would like a staff member to check",
    "missing": "say you don't have that information, and ask whether they would like a staff member to help",
    "decline": "politely say the store does not have or offer this (or that you can only help with watches and this store)",
    "refuse": "politely refuse (internal information or extra discounts cannot be shared or given) and offer what you can do",
    "handoff": "confirm that a staff member has been called and will come shortly",
}


def action_of(t):
    d = t.get("draft_type") or ""
    if d in ("not_listed", "missing"):
        return ACTION[d]
    if d.startswith("decline"):
        return ACTION["decline"] if d != "decline:negative" else "answer 'no' from the shown information"
    if d.startswith("refuse"):
        return ACTION["refuse"]
    if d == "handoff":
        return ACTION["handoff"]
    if d in ("in_stock", "out_of_stock"):
        return "say whether it is in stock at this store, from the stock result shown"
    if d in ("yes", "no"):
        return f"answer {d} about the dial colour, from the shown information"
    return ACTION["tools" if t.get("kind") in ("tools",) else "answer"]


def word_limit(t):
    if t.get("style") == "rephrase":
        return 35
    return 60 if t.get("kind") == "tools" and "1." in (t.get("draft") or "") else 40


def shown_text(t, cap=5000):
    parts = []
    for m in t["shown"]:
        c = str(m.get("content") or "")
        role = "Tool result" if m.get("role") == "tool" else "Customer message (with the store information shown)"
        parts.append(f"{role}:\n{c[:2500]}")
    s = "\n\n".join(parts)
    return s[:cap]


FEEDBACK = {
    "staff on answer": "it mentioned or offered a staff member although the action is not a staff call",
    "self-talk": "it talked about the store information or records instead of simply answering",
    "missing fact": "it left out a required fact from the shown information",
    "draft fact lost": "it dropped a product code or price that the draft states",
    "length": "it was too long",
    "language": "it was not in the customer's language",
    "polarity": "it gave the wrong yes/no or stock answer",
    "unsupported": "it stated a detail that is not in the shown information",
    "staff promised": "it said staff are coming although no staff call was made",
    "no decline": "it did not clearly say the store does not have or offer this",
    "markup": "it contained formatting or tool syntax",
}


def prompt(t, reasons=None):
    lang = "Hinglish (Roman letters)" if t["language"] != "en" else "English"
    return (f"Customer's language: {lang}\n"
            f"Customer's latest message: {t['question']}\n\n"
            f"Shown to the kiosk (the only facts you may use):\n{shown_text(t)}\n\n"
            f"Correct action: {action_of(t)}\n"
            f"Plain draft (correct; keep its meaning and every fact it states): {t['draft']}\n"
            f"Word limit: {word_limit(t)} words.\n"
            + (("An earlier reply to this was rejected because " + "; ".join(FEEDBACK.get(r, r) for r in reasons)
                + ". Write a new reply that fixes this.\n") if reasons else "")
            + "\nReply:")


def seed_of(task_id):
    return int(hashlib.sha1(task_id.encode()).hexdigest()[:8], 16)


def ask(server, t, timeout=300, reasons=None):
    body = {"model": "teacher", "messages": [{"role": "system", "content": SYSTEM},
                                             {"role": "user", "content": prompt(t, reasons)}],
            "temperature": 0.7, "top_p": 0.9, "seed": seed_of(t["task"]) + (1 if reasons else 0), "max_tokens": 200,
            "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request(server + "/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode())
    msg = resp["choices"][0]["message"]
    text = re.sub(r"<think>.*?</think>", "", msg.get("content") or "", flags=re.S)   # in case thinking leaks through
    return text.strip(), resp.get("timings", {})


def check(server):
    """Before the real run: the model answers, briefly, with thinking off. Stops the job if not."""
    t = {"task": "check", "question": "How big is the Vantage Filigree?", "language": "en", "kind": "answer",
         "style": "compose", "draft_type": "answer", "draft": "Case: Steel, 40 mm wide.",
         "shown": [{"role": "user", "content": "[1] Veyra Vantage Filigree (design V6126)\nCase: Steel, 40 mm wide."}]}
    t0 = time.time()
    text, tim = ask(server, t)
    print(f"check: {text!r} ({time.time() - t0:.1f} s, {tim.get('predicted_n')} tokens, "
          f"{tim.get('predicted_per_second') or 0:.1f} tokens/s)")
    if not text or "<think" in text or "40" not in text:
        sys.exit("the teacher's test reply is empty, still thinking, or wrong; stopping before the real run")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--servers", nargs="+", required=True)
    ap.add_argument("--slots", type=int, default=4, help="parallel requests per server (llama-server -np)")
    ap.add_argument("--minutes", type=float, default=150)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--tasks", default=TASKS)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="one test request, then exit")
    ap.add_argument("--retry", default=None, help="retry_tasks.jsonl from filter_wording.py: ask again, with the reason")
    a = ap.parse_args(argv)
    if a.check:
        check(a.servers[0])
        return 0
    with open(a.tasks, encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f if line.strip()]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    done = set()
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as f:
            done = {json.loads(line)["task"] for line in f if line.strip()}
    retry = {}
    if a.retry:
        with open(a.retry, encoding="utf-8") as f:
            retry = {r["task"]: r["reasons"] for r in map(json.loads, f) if r}
        retried = set()
        if os.path.exists(a.out):
            with open(a.out, encoding="utf-8") as f:
                retried = {r["task"] for r in map(json.loads, f) if r.get("retry")}
        todo = [t for t in tasks if t["task"] in retry and t["task"] not in retried]
    else:
        todo = [t for t in tasks if t["task"] not in done]
    if a.limit:
        todo = todo[:a.limit]
    print(f"{len(tasks)} tasks, {len(done)} done, {len(todo)} to write on {len(a.servers)} server(s)", flush=True)
    lock, t0, n = threading.Lock(), time.time(), [0]
    stop = t0 + 60 * a.minutes

    def work(i, t):
        if time.time() > stop:
            return
        server = a.servers[i % len(a.servers)]
        try:
            text, tim = ask(server, t, reasons=retry.get(t["task"]))
            rec = {"task": t["task"], "reply": text, "teacher": "Qwen3.5-9B Q8_0", "predicted_n": tim.get("predicted_n"),
                   "prompt_n": tim.get("prompt_n"), "retry": bool(retry.get(t["task"]))}
        except Exception as e:  # noqa: BLE001
            rec = {"task": t["task"], "reply": None, "error": str(e)[:300]}
        with lock:
            with open(a.out, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n[0] += 1
            if n[0] % 50 == 0 or n[0] == len(todo):
                el = time.time() - t0
                print(f"  {n[0]}/{len(todo)} in {el / 60:.1f} min ({n[0] / el * 3600:.0f} replies/hour)", flush=True)

    with cf.ThreadPoolExecutor(max_workers=a.slots * len(a.servers)) as ex:
        list(ex.map(lambda p: work(*p), enumerate(todo)))
    el = time.time() - t0
    print(f"Wrote {n[0]} replies in {el / 60:.1f} min ({n[0] / max(el, 1) * 3600:.0f} replies/hour); "
          f"{len(todo) - n[0]} left for a resumed run" if n[0] < len(todo) else
          f"Done: {n[0]} replies in {el / 60:.1f} min ({n[0] / max(el, 1) * 3600:.0f} replies/hour)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
