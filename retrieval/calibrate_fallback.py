"""
Step 6 of Objective 2: calibrate the refusal fallback on the dev split, then measure it once on test.

    python retrieval\\calibrate_fallback.py
    python retrieval\\calibrate_fallback.py --ranks results_retrieval\\latency\\ranks\\openvino-len256-depth20.jsonl

The fallback looks only at the re-ranker score of the best chunk. Below the threshold the kiosk does not call the
language model: it gives a fixed "I don't have that" reply and offers a staff member.

Which questions should it refuse? (from knowledge/retrieval_eval.jsonl)
    must answer   answer_type "fact": the corpus answers it. Refusing it is a false refusal.
    must refuse   answer_type "none" and not near-miss: off-topic, not sold here, unknown policy. Nothing
                  relevant exists, so the model should never see it.
    either        near-miss questions (negative, not_listed, missing_attribute, nonexistent_product). A relevant
                  chunk exists but the honest answer is "no" or "not listed"; refusing is acceptable and so is a
                  correct "no" from the model. Reported separately, not used to set the threshold.

Rule (fixed before looking at any score): choose the HIGHEST threshold whose dev false-refusal rate on must-answer
questions is at most 5%. That spends half of the 10% false-refusal budget here and leaves half for the model in
Step 8. The threshold is set on the 112 dev must-answer questions, which is far more stable than the 14 dev
must-refuse questions. The test split is then scored once with that threshold.

Writes results_retrieval\\fallback\\report.md, curve.csv, fallback.json (threshold + messages, for Step 7),
and curve.png if matplotlib is installed.

--hinglish-bypass (added AFTER the first test run, so its test numbers are post-hoc): the first run showed the
English-only re-ranker refusing 19% of answerable Hinglish questions against 0.4% of English ones. With the flag,
questions that retrieval/language.py detects as Hinglish are never refused by the fallback; they go to the model,
which must decline them itself if nothing answers them. The threshold is re-chosen with the SAME rule on dev, for
the new system. Outputs go to results_retrieval\\fallback_bypass\\ so the first run is kept.
"""

import argparse
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from bench_retrieval import wilson, auroc, load_jsonl  # noqa: E402
from language import is_hinglish  # noqa: E402

MAX_FALSE_REFUSAL_DEV = 0.05
MESSAGES = {
    "en": "Sorry, I don't have information about that. Would you like me to call a staff member to help?",
    "hinglish": "Maaf kijiye, iske baare mein mere paas jaankari nahi hai. Kya main staff member ko bula doon?",
}


def role(it):
    if it["answer_type"] == "fact":
        return "answer"
    if it["answer_type"] == "none" and not it["near_miss"]:
        return "refuse"
    return "either"


def refused(r, t):
    return not r["bypass"] and r["score"] < t


def rates(rows, t):
    ans = [r for r in rows if r["role"] == "answer"]
    ref = [r for r in rows if r["role"] == "refuse"]
    fr = sum(refused(r, t) for r in ans)
    tr = sum(refused(r, t) for r in ref)
    return fr, len(ans), tr, len(ref)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranks", default=os.path.join(ROOT, "results_retrieval", "latency", "ranks", "openvino-len256-depth20.jsonl"))
    ap.add_argument("--eval", default=os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--hinglish-bypass", action="store_true",
                    help="never refuse questions detected as Hinglish (post-hoc fix, see the docstring)")
    a = ap.parse_args()
    a.out = a.out or os.path.join(ROOT, "results_retrieval", "fallback_bypass" if a.hinglish_bypass else "fallback")
    if not os.path.exists(a.ranks):
        sys.exit(f"Ranks file not found: {a.ranks}\nRun Step 5b first, or pass --ranks.")
    items = {it["id"]: it for it in load_jsonl(a.eval)}
    rows = []
    for r in load_jsonl(a.ranks):
        it = items[r["id"]]
        rows.append(dict(id=r["id"], split=it["split"], subtype=it["subtype"], language=it["language"],
                         role=role(it), detected_hinglish=is_hinglish(it["query"]),
                         bypass=a.hinglish_bypass and is_hinglish(it["query"]), score=r["top"][0][1] if r["top"] else float("-inf"),
                         top_id=r["top"][0][0] if r["top"] else None, gold=it["gold_ids"]))
    dev = [r for r in rows if r["split"] == "dev"]
    test = [r for r in rows if r["split"] == "test"]

    # ---- the curve on dev: every distinct score is a candidate threshold ----
    cands = sorted({r["score"] for r in dev} | {float("-inf")})
    curve = []
    for t in cands:
        fr, na, tr, nr = rates(dev, t)
        curve.append(dict(threshold=t, dev_false_refusal=fr / na, dev_refusal_recall=tr / nr if nr else None))
    ok = [c for c in curve if c["dev_false_refusal"] <= MAX_FALSE_REFUSAL_DEV]
    chosen = max(ok, key=lambda c: c["threshold"])
    t = chosen["threshold"]

    # ---- test, once ----
    fr, na, tr, nr = rates(test, t)
    fr_p, fr_lo, fr_hi = wilson(fr, na)
    tr_p, tr_lo, tr_hi = wilson(tr, nr)
    au = {s: auroc([r["score"] for r in rs if r["role"] == "answer"], [r["score"] for r in rs if r["role"] == "refuse"])
          for s, rs in (("dev", dev), ("test", test))}

    def group(rs, key):
        out = {}
        for r in rs:
            g = out.setdefault(r[key], [0, 0])
            g[0] += refused(r, t)
            g[1] += 1
        return out

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "curve.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["threshold", "dev_false_refusal", "dev_refusal_recall"])
        w.writeheader()
        w.writerows(curve)
    lang = {r["language"] for r in rows}
    with open(os.path.join(a.out, "fallback.json"), "w", encoding="utf-8") as f:
        json.dump(dict(signal="top-1 re-ranker score (cross-encoder/ms-marco-MiniLM-L-6-v2, OpenVINO, 256 tokens)",
                       threshold=t, rule=f"highest threshold with dev false refusal <= {MAX_FALSE_REFUSAL_DEV:.0%}",
                       hinglish_bypass=a.hinglish_bypass,
                       hinglish_detector="retrieval/language.py is_hinglish" if a.hinglish_bypass else None,
                       messages=MESSAGES, ranks_file=os.path.basename(a.ranks)), f, indent=2, ensure_ascii=False)

    pct = lambda x: "-" if x is None else f"{100 * x:.1f}%"
    title = "# Step 6: refusal fallback calibration" + (" (with Hinglish bypass)" if a.hinglish_bypass else "")
    L = [title, "",
         f"Signal: top-1 re-ranker score from `{os.path.basename(a.ranks)}`. Rule: the highest threshold with dev "
         f"false refusal at most {MAX_FALSE_REFUSAL_DEV:.0%}. Chosen on dev only; test scored once.", ""]
    if a.hinglish_bypass:
        L += ["**Post-hoc variant.** Added after the first test run showed Hinglish questions being refused. Questions "
              "detected as Hinglish are never refused here and go to the model. Same rule, re-applied on dev. "
              "The eval set has no unanswerable Hinglish questions, so the cost of the bypass (Hinglish off-topic "
              "questions reaching the model) is not measured here; Step 8 must add some.", ""]
    L += [
         f"**Threshold: {t:.4f}**", "",
         "| Split | False refusals (must answer) | Correct refusals (must refuse) | AUROC |", "|---|---|---|---|",
         f"| dev | {rates(dev, t)[0]}/{rates(dev, t)[1]} = {pct(rates(dev, t)[0] / rates(dev, t)[1])} | "
         f"{rates(dev, t)[2]}/{rates(dev, t)[3]} = {pct(rates(dev, t)[2] / max(1, rates(dev, t)[3]))} | {au['dev']:.3f} |",
         f"| test | {fr}/{na} = {pct(fr_p)} [{pct(fr_lo)}-{pct(fr_hi)}] | {tr}/{nr} = {pct(tr_p)} [{pct(tr_lo)}-{pct(tr_hi)}] "
         f"| {au['test']:.3f} |", "",
         "False refusal = a question the corpus answers, refused by the fallback (target for the whole system: at most "
         "10%; this step may use half). Correct refusal = an off-topic, not-sold or unknown-policy question stopped "
         "before the model. The rest reach the model, which must decline them itself (measured end to end in Step 8).", "",
         "## Test: share refused, by question type", "", "| Subtype | Role | Refused |", "|---|---|---|"]
    roles = {r["subtype"]: r["role"] for r in rows}
    for sub, (k, n) in sorted(group(test, "subtype").items(), key=lambda kv: (roles[kv[0]], kv[0])):
        L.append(f"| {sub} | {roles[sub]} | {k}/{n} = {pct(k / n)} |")
    L += ["", "## Test: false refusals by language (must-answer questions only)", "", "| Language | Refused |", "|---|---|"]
    for lg, (k, n) in sorted(group([r for r in test if r["role"] == "answer"], "language").items()):
        L.append(f"| {lg} | {k}/{n} = {pct(k / n)} |")
    ok_h = sum(r["detected_hinglish"] for r in rows if r["language"] == "hinglish")
    n_h = sum(r["language"] == "hinglish" for r in rows)
    fp_h = [r for r in rows if r["detected_hinglish"] and r["language"] != "hinglish"]
    L += ["", "## Hinglish detector (retrieval/language.py), all 500 questions", "",
          f"Hinglish questions detected: {ok_h}/{n_h}. English questions wrongly detected: {len(fp_h)}/{len(rows) - n_h}"
          + (" (" + ", ".join(r["id"] for r in fp_h) + ")" if fp_h else "") + "."]
    if a.hinglish_bypass:
        byp = [r for r in test if r["bypass"] and r["role"] == "refuse"]
        L.append(f"Test must-refuse questions let through by the bypass: {len(byp)}.")
    L += ["", "## Dev curve (selected points)", "", "| Threshold | Dev false refusal | Dev correct refusal |", "|---|---|---|"]
    step = max(1, len(curve) // 25)
    for c in curve[::step] + [chosen]:
        mark = " **chosen**" if c is chosen else ""
        L.append(f"| {c['threshold']:.3f}{mark} | {pct(c['dev_false_refusal'])} | {pct(c['dev_refusal_recall'])} |")
    L += ["", "## Test questions the fallback got wrong", "", "Refused although answerable:", ""]
    for r in sorted((r for r in test if r["role"] == "answer" and refused(r, t)), key=lambda r: r["score"]):
        L.append(f"- {r['id']} ({r['subtype']}, {r['language']}, score {r['score']:.2f})")
    L += ["", "Passed to the model although nothing answers them:", ""]
    for r in sorted((r for r in test if r["role"] == "refuse" and not refused(r, t)), key=lambda r: -r["score"]):
        L.append(f"- {r['id']} ({r['subtype']}, score {r['score']:.2f}, top chunk {r['top_id']})")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xs = [100 * c["dev_false_refusal"] for c in curve]
        ys = [100 * (c["dev_refusal_recall"] or 0) for c in curve]
        fig, ax = plt.subplots(figsize=(5, 3.6))
        ax.plot(xs, ys, color="#2a78d6", lw=2)
        ax.scatter([100 * chosen["dev_false_refusal"]], [100 * (chosen["dev_refusal_recall"] or 0)], color="#eb6834", zorder=3)
        ax.axvline(100 * MAX_FALSE_REFUSAL_DEV, color="#8a8984", ls="--", lw=1)
        ax.set_xlabel("Answerable questions refused (dev, %)")
        ax.set_ylabel("Unanswerable questions refused (dev, %)")
        ax.set_title("Fallback threshold trade-off (dev)", loc="left", fontsize=10)
        ax.set_xlim(0, 60)
        ax.set_ylim(0, 102)
        ax.grid(color="#e6e5e0")
        fig.tight_layout()
        fig.savefig(os.path.join(a.out, "curve.png"), dpi=160)
        L += ["", "Plot: `curve.png`."]
    except Exception:
        L += ["", "(Install matplotlib to also get `curve.png`.)"]

    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L[:12]))
    print("\nWrote " + os.path.join(a.out, "report.md") + " and fallback.json")


if __name__ == "__main__":
    main()
