"""
Objective 4, Step 3b: check every teacher reply, put the kept ones into the training examples, and draw the sample
for the review.

    python finetune\\filter_wording.py

Reads finetune/teacher/replies.jsonl, finetune/examples/{wording_tasks,tierA,tierB}.jsonl and the training questions.
A teacher reply is kept only if it passes every check. Otherwise a fixed reply (not listed, decline, refusal, staff
call, stock or colour yes/no) keeps the oracle's template if that passes the same checks; a composed answer (an extract
of the shown text, not a reply) is dropped. Rejected tasks are listed for one retry with the teacher:
    empty / error      no reply
    length             more words than the task's limit + 10
    markup             tool-call syntax, headings, <think>, emojis
    unsupported        a number, code or spec word not in what was shown (harness/verify.py, the run-time check)
    missing fact       an answer that leaves out a required fact (every evidence group, any one alternative)
    draft fact lost    a product code or Rs amount in the draft that the reply drops
    polarity           a yes/no or stock reply with the wrong polarity (score_rag.polarity_correct)
    no decline         a "not listed" / decline / refusal without a decline phrase
    staff on answer    an answer, tool reply or refusal that mentions or offers staff (tightened in review)
    self-talk          talks about "the store information" / "our records" instead of answering (tightened)
    staff promised     says staff are coming when the action is not a staff call
    handoff unconfirmed  a staff call that does not say someone is coming
    language           Hinglish task answered in English, or the reverse
Writes finetune/examples/tier{A,B}_final.jsonl (target content = kept reply, or the draft; "wording" = teacher |
template), finetune/teacher/filter_report.md and finetune/teacher/review_sample.csv (200 kept replies, stratified
by kind and language, seed 3; blank "verdict" and "note" columns). The rule (pre-registered): if more than 10% of
the sample is rejected in review, the checks are tightened and the sample is redrawn.
"""

import collections
import csv
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, os.path.join(ROOT, "eval"), os.path.join(ROOT, "retrieval")):
    sys.path.insert(0, p)
from checks import text_has  # noqa: E402
from harness import verify  # noqa: E402

EX = os.path.join(HERE, "examples")
TEACH = os.path.join(HERE, "teacher")
STAFF_OFFER = re.compile(r"((call|get|ask|bring|fetch) (a |one of our |our |the )?(staff|store team|team member|colleague|"
                         r"sales ?person)|(staff|team) member (to|will|can|could) (help|check|come|assist)|"
                         r"bula (doon|dun|du)|bulaun|bulau)", re.I)
STAFF_PROMISE = re.compile(r"(i've asked|i have asked|i've called|i have called|i've notified|is coming|are coming|"
                           r"will be with you|will come over|on (their|his|her) way|bula (diya|liya|raha|rahi)|"
                           r"aa (rahe|raha|rahi|jayenge|jayega))", re.I)
# Tightened after the first review (Step 3c): any mention of staff on a reply whose action is not about staff (the
# Hinglish offers "bulwaun", "call karun" slipped past the offer pattern), and replies that talk about the kiosk's own
# information ("store ki jaankari", "our records") instead of answering.
STAFF_ANY = re.compile(r"(staff|team member|colleague|sales ?person|\bbul(a|aa|w|v)\w*|call kar\w*|call karw\w*)", re.I)
SELF_TALK = re.compile(r"(store information|store ki jaankari|tool result|\bjai ho\b)", re.I)
STAFF_ACTIONS = ("not_listed", "missing", "decline:missing_policy", "decline:not_sold", "decline:off_topic",
                 "decline:nonexistent_product", "handoff")
MARKUP = re.compile(r"<tool_call>|<function=|\"name\"\s*:|^#|<think|\[TOOL_CALLS\]|[\U0001F300-\U0001FAFF]", re.M)
CODE_OR_RS = re.compile(r"\b\d{4}[A-Z]{2}\d{2}\b|Rs\.? ?\d[\d,]*")
DECLINE_KINDS = ("not_listed", "missing", "decline", "refuse")


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def word_limit(t):
    import teacher
    return teacher.word_limit(t)


def checks(t, reply, case):
    import score_rag as SR
    from language import is_hinglish
    bad = []
    if not reply or not reply.strip():
        return ["empty / error"]
    words = len(reply.split())
    if words > word_limit(t) + 10:
        bad.append("length")
    if MARKUP.search(reply):
        bad.append("markup")
    shown = [str(m.get("content") or "") for m in t["shown"]]
    v = verify.check(reply, t["question"], shown, "", "shown")
    if v["unsupported"]:
        bad.append("unsupported")
    d = t.get("draft_type") or ""
    if d == "answer":
        for g in t.get("evidence") or []:
            if not text_has(reply, g):
                bad.append("missing fact")
                break
    lost = [x for x in CODE_OR_RS.findall(t.get("draft") or "") if re.sub(r"\D", "", x) not in re.sub(r"\D", "", reply)
            and x not in reply]
    if lost and d in ("answer", "tools", "decline:negative"):
        bad.append("draft fact lost")
    o4 = (case or {}).get("o4") or {}
    if o4.get("polarity"):
        if not SR.polarity_correct(reply, o4["polarity"], o4.get("word")):
            bad.append("polarity")
    if d.startswith(DECLINE_KINDS) and d != "decline:negative" and not text_has(reply, SR.DECLINE):
        bad.append("no decline")
    if d in ("answer", "tools", "in_stock", "out_of_stock", "yes", "no", "decline:negative") and STAFF_OFFER.search(reply):
        bad.append("staff on answer")
    elif d not in STAFF_ACTIONS and STAFF_ANY.search(reply) and not STAFF_ANY.search(t.get("draft") or ""):
        bad.append("staff on answer")            # e.g. "Kya main kisi staff ko bulwaun?" after an answer or a refusal
    if SELF_TALK.search(reply) and d not in STAFF_ACTIONS:      # the Hinglish drafts start with this phrase themselves
        bad.append("self-talk")
    if d != "handoff" and STAFF_PROMISE.search(reply):
        bad.append("staff promised")
    if d == "handoff" and not STAFF_PROMISE.search(reply) and not re.search(r"(called|asked|notified|bula)", reply, re.I):
        bad.append("handoff unconfirmed")
    hi_task, hi_reply = t["language"] != "en", is_hinglish(reply)
    if hi_task != hi_reply and words > 4:
        bad.append("language")
    return bad


def main(argv=None):
    tasks = {t["task"]: t for t in load_jsonl(os.path.join(EX, "wording_tasks.jsonl"))}
    cases = {}
    for n in ("tools", "store", "followups"):
        cases.update({c["id"]: c for c in load_jsonl(os.path.join(HERE, "train", f"{n}.jsonl"))})
    replies = {}
    rp = os.path.join(TEACH, "replies.jsonl")
    if os.path.exists(rp):
        for r in load_jsonl(rp):
            replies[r["task"]] = r                       # last one wins (a resumed or repeated task)
    verdict, why = {}, collections.Counter()
    reasons = collections.defaultdict(collections.Counter)
    by_kind = collections.defaultdict(collections.Counter)
    for k, t in tasks.items():
        r = replies.get(k)
        if r is None:
            verdict[k] = None
            why["not written yet"] += 1
            continue
        bad = checks(t, r.get("reply"), cases.get(t["case_id"]))
        verdict[k] = (r["reply"].strip() if not bad else None, bad)
        for b in bad or ["kept"]:
            why[b] += 1
            reasons[t.get("draft_type") or "?"][b] += 1
        by_kind[t.get("draft_type") or "?"]["kept" if not bad else "rejected"] += 1
    L = ["# Step 3: teacher replies, checks", "",
         f"{len(tasks)} tasks; {sum(1 for v in verdict.values() if v and v[0])} replies kept, "
         f"{sum(1 for v in verdict.values() if v and not v[0])} rejected (template kept), "
         f"{sum(1 for v in verdict.values() if v is None)} not written yet.", "",
         "| Check | Replies |", "|---|---:|"] + [f"| {k} | {n} |" for k, n in why.most_common()]
    L += ["", "| Draft type | Kept | Rejected | Reasons |", "|---|---:|---:|---|"] + \
        [f"| {k} | {c['kept']} | {c['rejected']} | " + ", ".join(f"{r} {n}" for r, n in reasons[k].most_common()
                                                               if r != "kept") + " |" for k, c in sorted(by_kind.items())]
    retry = [{"task": k, "reasons": v[1]} for k, v in verdict.items() if v and not v[0]]
    with open(os.path.join(TEACH, "retry_tasks.jsonl"), "w", encoding="utf-8") as f:
        for r in retry:
            f.write(json.dumps(r) + "\n")
    L += ["", f"Rejected replies to ask the teacher for again (job o4_teacher_retry): {len(retry)} "
              "-> finetune/teacher/retry_tasks.jsonl"]
    for tier in ("A", "B"):
        p = os.path.join(EX, f"tier{tier}.jsonl")
        if not os.path.exists(p):
            continue
        out, src = [], collections.Counter()
        template_ok = {}
        for ex in load_jsonl(p):
            k = ex.get("wording_task")
            if k:
                v = verdict.get(k)
                if v and v[0]:
                    ex["target"] = dict(ex["target"], content=v[0])
                    ex["wording"] = "teacher"
                elif tasks[k].get("style") != "rephrase" or \
                        not template_ok.setdefault(k, not checks(tasks[k], tasks[k]["draft"], cases.get(tasks[k]["case_id"]))):
                    # a composed draft is an extract of the shown text ("40,395.", a tool result), not a reply:
                    # it is never used as a training answer
                    src["dropped (no acceptable reply)"] += 1
                    continue                      # neither the teacher's reply nor the draft passes: no example
                else:
                    ex["wording"] = "template"
                src[ex["wording"]] += 1
            out.append(ex)
        with open(os.path.join(EX, f"tier{tier}_final.jsonl"), "w", encoding="utf-8") as f:
            for ex in out:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        L += ["", f"Tier {tier}: {len(out)} examples; replies from the teacher {src['teacher']}, from templates "
                  f"{src['template']}, dropped (neither passes the checks) {src['dropped (no acceptable reply)']}; "
                  f"tool-call answers {len(out) - src['teacher'] - src['template']}."]
    kept = [k for k, v in verdict.items() if v and v[0]]
    strata = collections.defaultdict(list)
    for k in sorted(kept):
        t = tasks[k]
        strata[(t.get("draft_type") or "?").split(":")[0], t["language"] != "en"].append(k)
    rng, sample = random.Random(3), []
    total = max(1, len(kept))
    for key, ks in sorted(strata.items()):
        rng.shuffle(ks)
        sample += ks[:max(1, round(200 * len(ks) / total))]
    sample = sample[:200]
    os.makedirs(TEACH, exist_ok=True)
    with open(os.path.join(TEACH, "review_sample.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["task", "draft_type", "language", "question", "shown (start)", "draft", "reply", "verdict", "note"])
        for k in sample:
            t = tasks[k]
            shown = " | ".join(str(m.get("content") or "")[:600] for m in t["shown"])[:1500]
            w.writerow([k, t.get("draft_type"), t["language"], t["question"], shown, t["draft"], verdict[k][0], "", ""])
    L += ["", f"Review sample: {len(sample)} kept replies -> finetune/teacher/review_sample.csv (verdict: ok / reject)."]
    with open(os.path.join(TEACH, "filter_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
