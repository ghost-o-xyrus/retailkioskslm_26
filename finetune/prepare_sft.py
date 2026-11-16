"""
Objective 4, Step 4a: turn the training examples into token sequences for training, with the model's own chat
template, and loss on the answer only.

Used by train_lora.py (on Kaggle, where the tokenizer is downloaded); `python finetune/prepare_sft.py --report` on a
machine with transformers prints the render counts without training.

For each example (finetune/examples/tier{A,B}_final.jsonl):
    prompt = the template applied to the request's messages, with its tools, thinking off, generation prompt on
    full   = the template applied to the messages plus the correct answer (generation prompt off)
    answer = full minus prompt; tokens = tokens(prompt) + tokens(answer); labels = -100 on the prompt
If the template renders the answer's turn so that full does not start with prompt (Qwen-style templates add an empty
thinking block to the generation prompt only), the answer is taken after the common start and the prompt's own
generation prompt is kept, so the model learns exactly what it writes at run time; an example that still cannot be
split is dropped and counted. Examples longer than --max-len tokens are dropped and counted (not cut).
Hold-out: 5% of questions (by a hash of the question id, the same for both tiers), for the loss check only.
"""

import argparse
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "examples")
THINK_EMPTY = re.compile(r"<think>\s*</think>\s*")


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def held_out(case_id, share=0.05):
    return int(hashlib.sha1(case_id.encode()).hexdigest()[:8], 16) % 10000 < share * 10000


def clean_messages(msgs):
    """The request as the template expects it: tool-call arguments as objects, only the standard keys."""
    out = []
    for m in msgs:
        n = {"role": m["role"], "content": m.get("content") if m.get("content") is not None else ""}
        if m.get("tool_calls"):
            calls = []
            for tc in m["tool_calls"]:
                f = dict(tc.get("function") or {})
                try:
                    f["arguments"] = json.loads(f.get("arguments") or "{}") if isinstance(f.get("arguments"), str) \
                        else (f.get("arguments") or {})
                except json.JSONDecodeError:
                    f["arguments"] = {}
                calls.append({"id": tc.get("id"), "type": "function", "function": f})
            n["tool_calls"] = calls
        if m["role"] == "tool":
            if m.get("tool_call_id"):
                n["tool_call_id"] = m["tool_call_id"]
            if m.get("name"):
                n["name"] = m["name"]
        out.append(n)
    return out


def render(tok, ex, tools):
    msgs = clean_messages(ex["messages"])
    target = clean_messages([dict(ex["target"], role="assistant")])[0]
    kw = {"tools": tools} if tools else {}
    kw2 = dict(kw, **{"enable_thinking": False})
    try:
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw2)
        full = tok.apply_chat_template(msgs + [target], tokenize=False, add_generation_prompt=False, **kw2)
    except TypeError:                                   # a template without enable_thinking
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, **kw)
        full = tok.apply_chat_template(msgs + [target], tokenize=False, add_generation_prompt=False, **kw)
    if full.startswith(prompt):
        return prompt, full[len(prompt):], "exact"
    i = 0
    while i < min(len(prompt), len(full)) and prompt[i] == full[i]:
        i += 1
    i = prompt.rfind("\n", 0, i) + 1                    # back to a line start, never inside a tag
    gen, answer = prompt[i:], full[i:]
    if not gen.startswith("<think>") and "<think>" in gen:   # the shared start ended before the assistant header
        head = gen[:gen.index("<think>")]
        if answer.startswith(head):
            gen, answer = gen[len(head):], answer[len(head):]
    # the generation prompt's extra part is only an empty thinking block (thinking off): the model writes the
    # answer after it at run time, so the answer is the rest of `full` without any thinking block of its own
    if THINK_EMPTY.fullmatch(gen):
        return prompt, re.sub(r"^\s*<think>\s*</think>\s*", "", answer), "joined"
    return None, None, "unsplittable"


def build(tok, tier, max_len=4096, limit=None):
    tools_by_key = json.load(open(os.path.join(EX, "tools.json"), encoding="utf-8"))
    path = os.path.join(EX, f"tier{tier}_final.jsonl")
    exs = load_jsonl(path)
    if limit:
        exs = exs[:limit]
    train, held, counts, lengths = [], [], {"exact": 0, "joined": 0, "unsplittable": 0, "too long": 0}, []
    for ex in exs:
        prompt, answer, how = render(tok, ex, tools_by_key.get(ex["tools"]) if ex.get("tools") else None)
        counts[how] += 1
        if prompt is None:
            continue
        p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
        a_ids = tok(answer, add_special_tokens=False)["input_ids"]
        if len(p_ids) + len(a_ids) > max_len:
            counts["too long"] += 1
            continue
        item = {"input_ids": p_ids + a_ids, "labels": [-100] * len(p_ids) + a_ids,
                "attention_mask": [1] * (len(p_ids) + len(a_ids)), "id": ex["id"]}
        lengths.append(len(item["input_ids"]))
        (held if held_out(ex["case_id"]) else train).append(item)
    stats = dict(counts, examples=len(exs), train=len(train), held_out=len(held),
                 tokens=sum(lengths), longest=max(lengths) if lengths else 0,
                 answer_tokens=sum(sum(1 for x in it["labels"] if x != -100) for it in train + held))
    return train, held, stats


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="unsloth/Qwen3.5-2B")
    ap.add_argument("--tier", default="A")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args(argv)
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model)
    _, _, stats = build(tok, a.tier)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
