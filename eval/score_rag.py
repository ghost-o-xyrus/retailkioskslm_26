"""
Score Objective 2's end-to-end runs on the retrieval questions (Step 8).

    python eval\\score_rag.py results_obj2\\s8_*_rag_*
    python eval\\score_rag.py results_obj2\\s8_*_rag_* --labels eval\\rag_judge\\step8      # after judging

Each run is identified from its run_meta.json: model, and condition
    none        the v1.1 kiosk, tools only                 oracle      the gold chunks shown
    deployed    always retrieve + soft fallback (gate)     nofallback  always retrieve, no fallback
    tool        search_knowledge tool
"Hard fallback" rows are computed from the deployed / nofallback logs: where the fallback would have refused, the
reply is replaced by the fixed "I don't have that" message (the model is skipped), as in a pure Q&A kiosk.

AUTOMATIC checks (every case):
    answerable questions   correct = every expected fact appears in the reply (whole-word match, as in Objective 1);
                           for product-name and description questions with no listed facts, the reply must name the
                           gold design (its name, design code or a variant code). FAQ/glossary questions without
                           listed facts have no automatic check.
                           refusal candidate = a decline or staff-offer phrase, or an empty reply, and not correct
    unanswerable           decline phrase present (a proxy; the judge decides hallucination)
    near miss              the expected "no / not listed" phrase present (proxy)
JUDGED (with --labels; see eval/rag_judge/build_packet.py): hallucination on unanswerable and near-miss questions,
unsupported details in answers, and confirmed false refusals.

Paired comparisons per model on the answerable questions with an automatic check (bootstrap CI, exact McNemar):
    oracle - deployed   retrieval loss; target: at most 5 points
    deployed - none     what retrieval adds to the v1.1 kiosk
    deployed - nofallback, tool - deployed
Writes results_obj2\\_scores_step8\\report.md, summary.csv, cases_<run>.csv.
"""

import argparse
import csv
import glob
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from checks import check_must_include, text_has  # noqa: E402
from score import wilson, mcnemar_exact, paired_bootstrap  # noqa: E402

DECLINE = ["don't have", "do not have", "not sure", "not listed", "not mentioned", "sorry", "can't", "cannot",
           "unable", "only help", "not available", "don't sell", "do not sell", "couldn't find", "could not find",
           "no such", "not able", "can't confirm", "staff", "nahi", "nahin", "maaf", "not in our", "isn't listed",
           "is not listed", "doesn't exist", "does not exist", "not something we", "no information"]
NAMED_SUBTYPES = ("product_name", "product_description")
CONDITIONS = ("none", "oracle", "deployed", "nofallback", "tool")


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def condition(meta):
    r = meta.get("retrieval") or {}
    c = r.get("condition", "none")
    if c == "always":
        return "deployed" if r.get("fallback") == "gate" else ("hardfallback" if r.get("fallback") == "live" else "nofallback")
    return c


def gold_names(case, chunks):
    out = []
    for g in case["expected"]["gold_ids"]:
        ch = chunks.get(g)
        if not ch or ch.get("type") != "product":
            continue
        m = re.match(r"Veyra (.+?) \(design (V\d+)\)", ch["text"])
        if m:
            out += [m.group(1), m.group(2)]
        out += ch.get("meta", {}).get("skus", [])
    return out


def scored_reply(rec):
    """The reply as scored. The Step 3 loop guard's fixed line for an empty reply counts as an empty reply, so a
    stuck turn never scores as a correct decline."""
    if "empty_reply_fallback" in ((rec or {}).get("flags") or []):
        return ""
    return (rec or {}).get("final_reply")


POL_NEG = ["not in stock", "out of stock", "not available", "isn't in stock", "is not in stock", "no stock",
           "doesn't come", "does not come", "isn't available", "is not available", "only comes", "only available",
           "not offered", "nahi hai", "nahi aati", "nahi milti", "nahi milega", "unfortunately", "sorry"]
POL_POS = {"in_stock": ["in stock", "on display", "available here", "available at this store", "stock mein",
                        "in the back room", "in the backroom", "available in store"],
           "yes": ["yes", "haan", "comes in", "available in", "we have", "do have", "milti hai", "aati hai", "available"]}


def polarity_correct(reply, polarity, word=None):
    """in_stock / out_of_stock / yes / no for a yes-no follow-up. A negative phrase anywhere makes the reply
    negative; a positive reply also needs a positive phrase (and, for colours, the colour)."""
    t = (reply or "").lower()
    neg = any(p in t for p in POL_NEG)
    if polarity in ("out_of_stock", "no"):
        return neg
    pos = any(p in t for p in POL_POS["in_stock" if polarity == "in_stock" else "yes"])
    return pos and not neg and (not word or word.lower() in t)


def auto(case, reply, chunks):
    """Returns dict: checked (bool), correct (bool|None), declined (bool), empty (bool)."""
    e = case["expected"]
    reply = reply or ""
    empty = not reply.strip()
    declined = empty or text_has(reply, DECLINE)
    out = dict(empty=empty, declined=declined, checked=False, correct=None)
    if e.get("polarity"):                 # Objective 3, Step 11: yes/no follow-ups (stock, colour)
        out.update(checked=True, correct=polarity_correct(reply, e["polarity"], e.get("polarity_word")))
        out["refusal_candidate"] = declined and not out["correct"]
        return out
    if e["behaviour"] == "answer":
        if e["must_include"]:
            got, total, _ = check_must_include(reply, e["must_include"])
            out.update(checked=True, correct=got == total)
        elif case["subcategory"] in NAMED_SUBTYPES:
            names = gold_names(case, chunks)
            if names:
                out.update(checked=True, correct=text_has(reply, names))
        out["refusal_candidate"] = declined and not out["correct"]
    elif e["behaviour"] == "either":
        out.update(checked=True, correct=bool(e["must_include"]) and check_must_include(reply, e["must_include"])[0] ==
                   len(e["must_include"]))
    else:
        out.update(checked=True, correct=declined and not empty)
    return out


def first_visible(r):
    m = r.get("metrics") or {}
    if m.get("first_visible_ms") is not None:
        return m["first_visible_ms"]
    t = r.get("turns") or []
    return max(0.0, (m.get("end_to_end_ms") or 0) - ((t[-1].get("predicted_ms") or 0) if t else 0))


def pctl(xs, q):
    xs = sorted(x for x in xs if x is not None)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))] if xs else None


def load_labels(path):
    """Judge labels: {key: {"run", "case", ...}} and labels_*.json files [{"item", "label"}]."""
    if not path:
        return {}
    with open(os.path.join(path, "key.json"), encoding="utf-8") as f:
        key = json.load(f)
    labels = {}
    for fp in sorted(glob.glob(os.path.join(path, "labels*.json"))):
        with open(fp, encoding="utf-8") as f:
            for row in json.load(f):
                labels[row["item"]] = row["label"]
    out = {}
    for item, k in key.items():
        if item in labels:
            out[(k["run"], k["case"])] = (labels[item], k.get("source"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--cases", default=os.path.join(HERE, "rag_cases.jsonl"))
    ap.add_argument("--split", default="test", choices=["test", "dev", "all"])
    ap.add_argument("--labels", default=None, help="Folder with key.json and labels*.json from the judge")
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj2", "_scores_step8"))
    ap.add_argument("--fallback", default=os.path.join(ROOT, "results_retrieval", "fallback_bypass", "fallback.json"))
    a = ap.parse_args()

    cases = {c["id"]: c for c in load_jsonl(a.cases) if a.split == "all" or c["split"] == a.split}
    chunks = {c["id"]: c for c in load_jsonl(os.path.join(ROOT, "knowledge", "corpus.jsonl"))}
    with open(a.fallback, encoding="utf-8") as f:
        fb_msgs = json.load(f)["messages"]
    labels = load_labels(a.labels)
    dirs = sorted({d for p in a.runs for d in glob.glob(p) if os.path.exists(os.path.join(d, "cases.jsonl"))})
    runs = []
    for d in dirs:
        with open(os.path.join(d, "run_meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
        recs = {}
        for r in load_jsonl(os.path.join(d, "cases.jsonl")):
            if r["id"] in cases:
                recs[r["id"]] = r
        if recs:
            runs.append(dict(name=os.path.basename(d), model=meta.get("model", "?"), cond=condition(meta), recs=recs))
    if not runs:
        sys.exit("No runs with retrieval-question cases found.")
    os.makedirs(a.out, exist_ok=True)

    def variants(run):
        yield run["cond"], False
        if run["cond"] in ("deployed", "nofallback"):
            yield run["cond"] + "+hard", True

    rows, per_case = [], {}
    for run in runs:
        for label, hard in variants(run):
            res = {}
            for cid, r in run["recs"].items():
                c = cases[cid]
                ret = r.get("retrieval") or {}
                reply = scored_reply(r) or ""
                if hard and ret.get("fallback_would_refuse"):
                    reply = fb_msgs["hinglish" if ret.get("hinglish") else "en"]
                lab = labels.get((run["name"], cid))
                hard_refused = bool(hard and ret.get("fallback_would_refuse"))
                res[cid] = dict(auto(c, reply, chunks), error=bool(r.get("error")),
                                judged=None if (hard_refused or lab is None) else lab[0],
                                source=None if lab is None else lab[1], hard_refused=hard_refused)
            per_case[(run["name"], label)] = res
            rows.append(summarise(run, label, res, cases, hard))

    # ---- report ----
    pct = lambda x: "-" if x is None else f"{100 * x:.1f}%"
    ci = lambda k, n: "-" if not n else f"{k}/{n} = {pct(k / n)} [{pct(wilson(k, n)[1])}-{pct(wilson(k, n)[2])}]"
    L = ["# Step 8: end-to-end results on the test retrieval questions", "",
         f"Split: {a.split}. Automatic checks unless marked judged. Hard-fallback rows replace the reply with the "
         "fixed message wherever the fallback would refuse.", "",
         "## Answerable questions", "",
         "| Run | Model | Condition | Correct (auto-checked) | Refusal candidates (auto) | Judged: unsupported details (random sample) | Judged: false refusals (all answerable) |",
         "|---|---|---|---|---|---|---|"]
    for s in rows:
        L.append(f"| {s['run']} | {s['model']} | {s['label']} | {ci(*s['ans_correct'])} | {ci(*s['ans_refusal'])} | "
                 f"{ci(*s['j_unsupported'])} | {ci(*s['j_refused'])} |")
    L += ["", "## Unanswerable and near-miss questions", "",
          "| Run | Condition | Unanswerable: decline phrase (auto) | Unanswerable: hallucinated (judged) | "
          "Near miss: expected no/not-listed (auto) | Near miss: hallucinated (judged) | Hinglish unanswerable: hallucinated (judged) |",
          "|---|---|---|---|---|---|---|"]
    for s in rows:
        L.append(f"| {s['run']} | {s['label']} | {ci(*s['dec_auto'])} | {ci(*s['dec_halluc'])} | {ci(*s['nm_auto'])} | "
                 f"{ci(*s['nm_halluc'])} | {ci(*s['hun_halluc'])} |")
    L += ["", "## Speed, size and tool use", "",
          "| Run | First word p50 / p90 s | End to end p50 / p90 s | Retrieval p50 / p90 ms | Context tokens mean | "
          "Peak RAM GB server / harness / total | search_knowledge used | Errors |", "|---|---|---|---|---|---|---|---|"]
    for s in rows:
        if s["label"].endswith("+hard"):
            continue
        f1 = lambda x, d=1: "-" if x is None else f"{x:.{d}f}"
        L.append(f"| {s['run']} | {f1(s['vis50'])} / {f1(s['vis90'])} | {f1(s['e2e50'])} / {f1(s['e2e90'])} | "
                 f"{f1(s['ret50'], 0)} / {f1(s['ret90'], 0)} | {f1(s['ctx'], 0)} | {f1(s['ram_srv'], 2)} / "
                 f"{f1(s['ram_h'], 2)} / {f1(s['ram_tot'], 2)} | {s['tool_use']} | {s['errors']} |")

    # ---- paired comparisons ----
    L += ["", "## Paired comparisons (answerable questions with an automatic check)", "",
          "| Model | A | B | Cases | A - B (points) | 95% CI | McNemar p |", "|---|---|---|---|---|---|---|"]
    by_model = {}
    for run in runs:
        by_model.setdefault(run["model"], {})[run["cond"]] = run["name"]
    pairs = [("oracle", "deployed"), ("deployed", "none"), ("deployed", "nofallback"), ("tool", "deployed")]
    for model, conds in sorted(by_model.items()):
        for x, y in pairs:
            if x in conds and y in conds:
                A, B = per_case[(conds[x], x)], per_case[(conds[y], y)]
                ids = [i for i in A if i in B and cases[i]["expected"]["behaviour"] == "answer" and A[i]["checked"]]
                av = [1 if A[i]["correct"] else 0 for i in ids]
                bv = [1 if B[i]["correct"] else 0 for i in ids]
                d, lo, hi = paired_bootstrap(av, bv)
                b_ = sum(1 for p, q in zip(av, bv) if p and not q)
                c_ = sum(1 for p, q in zip(av, bv) if q and not p)
                L.append(f"| {model} | {x} | {y} | {len(ids)} | {100 * d:+.1f} | [{100 * lo:+.1f}, {100 * hi:+.1f}] | "
                         f"{mcnemar_exact(b_, c_):.4f} |")
    L += ["", "Retrieval loss target: oracle - deployed at most 5 points. Judged rates appear once "
          "eval\\rag_judge labels are passed with --labels."]

    # ---- by question type, deployed vs oracle vs none ----
    L += ["", "## Correct by question type (answerable, auto-checked)", ""]
    subs = sorted({c["subcategory"] for c in cases.values() if c["expected"]["behaviour"] == "answer"})
    show = [(s["run"], s["label"]) for s in rows if not s["label"].endswith("+hard")]
    L += ["| Type | " + " | ".join(r for r, _ in show) + " |", "|---|" + "---|" * len(show)]
    for sub in subs:
        cells = []
        for r, lab in show:
            res = per_case[(r, lab)]
            ids = [i for i in res if cases[i]["subcategory"] == sub and res[i]["checked"]]
            cells.append(f"{sum(res[i]['correct'] for i in ids)}/{len(ids)}" if ids else "-")
        L.append(f"| {sub} | " + " | ".join(cells) + " |")

    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "summary.csv"), "w", newline="", encoding="utf-8-sig") as f:
        keys = [k for k in rows[0] if not isinstance(rows[0][k], tuple)]
        w = csv.writer(f)
        w.writerow(keys + ["ans_correct_k", "ans_correct_n", "dec_halluc_k", "dec_halluc_n", "nm_halluc_k", "nm_halluc_n"])
        for s in rows:
            w.writerow([s[k] for k in keys] + list(s["ans_correct"]) + list(s["dec_halluc"]) + list(s["nm_halluc"]))
    for (run, lab), res in per_case.items():
        with open(os.path.join(a.out, f"cases_{run}{'_hard' if lab.endswith('+hard') else ''}.csv"), "w",
                  newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["id", "subtype", "language", "behaviour", "checked", "correct", "declined", "empty",
                        "hard_refused", "judged", "question"])
            for cid, x in res.items():
                c = cases[cid]
                w.writerow([cid, c["subcategory"], c["language"], c["expected"]["behaviour"], x["checked"],
                            x["correct"], x["declined"], x["empty"], x["hard_refused"], x["judged"] or "",
                            c["messages"][-1]["content"]])
    print("\n".join(L[:40]))
    print(f"\nWrote {os.path.join(a.out, 'report.md')}")


def summarise(run, label, res, cases, hard):
    recs = run["recs"]
    beh = lambda cid: cases[cid]["expected"]["behaviour"]
    ans = [i for i in res if beh(i) == "answer"]
    chk = [i for i in ans if res[i]["checked"]]
    dec = [i for i in res if beh(i) == "decline"]
    nm = [i for i in res if beh(i) == "either"]
    hun = [i for i in dec if i.startswith("R-HUN-")]

    any_labels = any(x["source"] is not None for x in res.values())

    def refusals(ids):
        """False refusals on all answerable questions: judged declined/empty (only refusal-looking replies and the
        sample were judged; the rest answered), plus hard-fallback refusals."""
        if not any(res[i]["source"] in ("faith", "refusal_candidate") for i in ids):
            return 0, 0      # answerable replies were judged only for the deployed runs
        return sum(1 for i in ids if res[i]["hard_refused"] or res[i]["judged"] in ("declined", "empty")), len(ids)

    def judged(ids, bad, hard_is_bad=False):
        """Judge-labelled share. A hard-refused item showed the fixed message: it is not a hallucination or an
        unsupported detail, but on an answerable question it is a refusal."""
        if not any_labels:
            return 0, 0
        js = [i for i in ids if res[i]["judged"] is not None or res[i]["hard_refused"]]
        k = sum(1 for i in js if (res[i]["hard_refused"] and hard_is_bad) or
                (not res[i]["hard_refused"] and res[i]["judged"] in bad))
        return k, len(js)

    rs = [recs[i] for i in res]
    m = lambda k: [(r.get("metrics") or {}).get(k) for r in rs]
    ret = [(r.get("retrieval") or {}) for r in rs]
    tool_runs = [x for x in ret if x.get("condition") == "tool"]
    sec = lambda xs: [x / 1000 for x in xs if x is not None]
    return dict(
        run=run["name"], model=run["model"], label=label,
        ans_correct=(sum(res[i]["correct"] for i in chk), len(chk)),
        ans_refusal=(sum(1 for i in ans if res[i].get("refusal_candidate")), len(ans)),
        j_unsupported=judged([i for i in ans if res[i]["source"] == "faith"], ("unsupported",)),
        j_refused=refusals(ans),
        dec_auto=(sum(res[i]["correct"] for i in dec), len(dec)), dec_halluc=judged(dec, ("unsupported",)),
        nm_auto=(sum(res[i]["correct"] for i in nm), len(nm)), nm_halluc=judged(nm, ("unsupported",)),
        hun_halluc=judged(hun, ("unsupported",)),
        vis50=pctl(sec([first_visible(r) for r in rs]), .5), vis90=pctl(sec([first_visible(r) for r in rs]), .9),
        e2e50=pctl(sec(m("end_to_end_ms")), .5), e2e90=pctl(sec(m("end_to_end_ms")), .9),
        ret50=pctl(m("retrieval_ms"), .5), ret90=pctl(m("retrieval_ms"), .9),
        ctx=statistics.mean([x.get("context_tokens") or 0 for x in ret]) if any(x.get("condition") in ("always", "oracle") for x in ret) else None,
        ram_srv=(max(x or 0 for x in m("peak_rss_mb")) / 1000) or None,
        ram_h=(max(x or 0 for x in m("harness_rss_mb")) / 1000) or None,
        ram_tot=max(((r.get("metrics") or {}).get("peak_rss_mb") or 0) + ((r.get("metrics") or {}).get("harness_rss_mb") or 0) for r in rs) / 1000 or None,
        tool_use=(f"{sum(1 for x in tool_runs if x.get('calls'))}/{len(tool_runs)}" if tool_runs else "-"),
        errors=sum(1 for i in res if res[i]["error"]))


if __name__ == "__main__":
    main()
