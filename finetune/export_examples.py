"""
Objective 4, Step 2c: turn the oracle logs into training examples and the teacher's wording tasks.

    python finetune\\export_examples.py

Reads results_o4/traj_a/*.jsonl and results_o4/traj_b/*.jsonl (written by oracle_server.py while the harness ran
finetune/plans/o4_traj_tier{A,B}.json) and the training questions (finetune/train/*.jsonl).

One example per model request: the request exactly as the harness sent it (messages, tool choice, parallel calls,
template settings; the tool schemas are stored once in tools.json) and the correct answer. Loss in Step 4 goes on the
answer only. Gaps per example:
    tool_choice       the answer is a tool call
    format            the answer is prose on a request where tools were not allowed (after tool results or a note)
    staff_discipline  an answerable question answered without calling staff
    not_listed        "that detail isn't listed" / "I don't have that"
    decline           not sold, off-topic, unknown policy, no such design, refusal, a near-miss "no"
    ordinary          an answer from the shown information that needs nothing special
Writes finetune/examples/tier{A,B}.jsonl, tools.json, wording_tasks.jsonl (one task per distinct reply, shared by
both tiers: the same question and the same shown information get the same reply wording) and mix_report.md.
A tier's set is capped at --max examples (whole cases, sampled with a fixed seed) so the teacher budget is known.
"""

import argparse
import collections
import hashlib
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TRAJ = os.path.join(ROOT, "results_o4")
OUT = os.path.join(HERE, "examples")
FIXED = ("not_listed", "missing", "decline:", "refuse:", "handoff", "in_stock", "out_of_stock", "yes", "no")


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def h(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def gaps_of(rec, case):
    resp, req = rec["response"], rec["request"]
    draft = rec.get("draft") or ""
    out = set()
    if resp.get("tool_calls"):
        out.add("tool_choice")
        return sorted(out)
    if req.get("tool_choice") == "none" and any(m.get("role") == "tool" for m in req["messages"]):
        out.add("format")
    if draft in ("not_listed", "missing"):
        out.add("not_listed")
    elif draft.startswith(("decline", "refuse")):
        out.add("decline")
    elif draft in ("answer", "tools", "in_stock", "out_of_stock", "yes", "no"):
        out.add("ordinary")
        if case["o4"]["kind"] == "answer":
            out.add("staff_discipline")
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=3000, help="examples per tier (whole cases are kept or dropped)")
    ap.add_argument("--seed", type=int, default=4405)
    a = ap.parse_args(argv)
    cases = {}
    for name in ("tools", "store", "followups"):
        p = os.path.join(HERE, "train", f"{name}.jsonl")
        if os.path.exists(p):
            cases.update({c["id"]: c for c in load_jsonl(p)})
    os.makedirs(OUT, exist_ok=True)
    tools, tasks, L = {}, {}, ["# Objective 4 training examples", ""]
    for tier in ("a", "b"):
        d = os.path.join(TRAJ, f"traj_{tier}")
        if not os.path.isdir(d):
            L += [f"Tier {tier.upper()}: no oracle logs in {d}", ""]
            continue
        seen, by_case = set(), collections.defaultdict(list)
        for f in sorted(os.listdir(d)):
            if not f.endswith(".jsonl"):
                continue
            for rec in load_jsonl(os.path.join(d, f)):
                key = h([rec["case_id"], rec["request"]["messages"], rec["request"].get("tool_choice")])
                if key in seen or rec["case_id"] not in cases:
                    continue                                  # a resumed run logs the same request again
                seen.add(key)
                case = cases[rec["case_id"]]
                tk = h(rec.get("tools_schema"))
                if rec.get("tools_schema"):
                    tools[tk] = rec["tools_schema"]
                ex = {"id": f"{tier.upper()}-{key}", "tier": tier.upper(), "case_id": rec["case_id"],
                      "language": case["language"], "kind": case["o4"]["kind"], "subcategory": case["subcategory"],
                      "gaps": gaps_of(rec, case), "messages": rec["request"]["messages"],
                      "tools": tk if rec.get("tools_schema") else None, "tool_choice": rec["request"].get("tool_choice"),
                      "parallel_tool_calls": rec["request"].get("parallel_tool_calls"),
                      "chat_template_kwargs": rec["request"].get("chat_template_kwargs"),
                      "max_tokens": rec["request"].get("max_tokens"), "target": rec["response"], "draft": rec.get("draft")}
                if not rec["response"].get("tool_calls"):
                    # the wording task: same question, same shown information -> one task for both tiers
                    shown = [m for m in rec["request"]["messages"] if m.get("role") in ("user", "tool")]
                    tkey = h([rec["case_id"], shown])
                    ex["wording_task"] = tkey
                    tasks.setdefault(tkey, {"task": tkey, "case_id": rec["case_id"], "language": case["language"],
                                            "kind": case["o4"]["kind"], "draft_type": rec.get("draft"),
                                            "style": "rephrase" if (rec.get("draft") or "").startswith(FIXED) else "compose",
                                            "question": case["messages"][-1]["content"], "shown": shown,
                                            "draft": rec["response"].get("content"),
                                            "evidence": case["o4"].get("evidence") or [], "tiers": []})
                    tasks[tkey]["tiers"] = sorted(set(tasks[tkey]["tiers"]) | {tier.upper()})
                by_case[rec["case_id"]].append(ex)
        ids = sorted(by_case)
        random.Random(a.seed).shuffle(ids)
        kept, n = [], 0
        for cid in ids:
            if n >= a.max:
                break
            kept += by_case[cid]
            n += len(by_case[cid])
        with open(os.path.join(OUT, f"tier{tier.upper()}.jsonl"), "w", encoding="utf-8") as f:
            for ex in kept:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        g = collections.Counter(x for ex in kept for x in ex["gaps"])
        lang = collections.Counter(ex["language"] for ex in kept)
        kinds = collections.Counter(ex["kind"] for ex in kept)
        L += [f"## Tier {tier.upper()}: {len(kept)} examples from {len({e['case_id'] for e in kept})} questions "
              f"({sum(len(v) for v in by_case.values())} before the cap)", "",
              "| Gap | Examples | Share | Rule (each target gap at least 10%) |", "|---|---:|---:|---|"]
        for k in ("format", "tool_choice", "staff_discipline", "not_listed", "decline", "ordinary"):
            share = g[k] / max(1, len(kept))
            rule = "" if k == "ordinary" else ("met" if share >= 0.10 else "**below 10%**")
            L.append(f"| {k} | {g[k]} | {share:.0%} | {rule} |")
        hi = sum(v for k, v in lang.items() if k != "en") / max(1, len(kept))
        L += ["", f"- Hinglish: {hi:.0%} (target about a third)", f"- by kind: {dict(kinds)}",
              f"- tool-call answers: {sum(1 for e in kept if e['target'].get('tool_calls'))}; replies: "
              f"{sum(1 for e in kept if not e['target'].get('tool_calls'))}", ""]
    with open(os.path.join(OUT, "tools.json"), "w", encoding="utf-8") as f:
        json.dump(tools, f, ensure_ascii=False)
    used = set()
    for tier in ("A", "B"):
        p = os.path.join(OUT, f"tier{tier}.jsonl")
        if os.path.exists(p):
            used |= {e.get("wording_task") for e in load_jsonl(p)}
    with open(os.path.join(OUT, "wording_tasks.jsonl"), "w", encoding="utf-8") as f:
        for t in tasks.values():
            if t["task"] in used:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
    st = collections.Counter(t["style"] for t in tasks.values() if t["task"] in used)
    L += ["## Teacher wording tasks", "", f"- {sum(st.values())} distinct replies to word ({dict(st)}); shared by both "
          "tiers where the question and the shown information are the same"]
    with open(os.path.join(OUT, "mix_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
