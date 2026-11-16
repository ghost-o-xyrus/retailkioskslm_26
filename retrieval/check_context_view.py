"""
Step 7d, part 1: how much prompt text can the model be spared without losing the right chunk? No model needed.

    python retrieval\\check_context_view.py

The Step 7 pilot showed Tier A's wait is prompt processing: Qwen3.5-2B on 4 CPU threads reads about 60 tokens
a second, so three retrieved chunks (about 600 real tokens) cost 10-14 s before the first word. Two cuts that
leave retrieval itself untouched:
    compact      product cards without the marketing description (repeats the spec lines; ~43% of a card)
    chunk gate   show only chunks whose re-ranker score is at or above the fallback threshold; Hinglish
                 questions are exempt (the bypass), and with nothing left the model is told so
Rule, fixed before the run: a variant is acceptable if its dev "gold shown" rate (an answerable question's
gold chunk is among the chunks the model sees) is at most 2 points below the current setup (full cards, k
chunks, no gate). Among acceptable variants, the one with the fewest dev context tokens is chosen. Test rates
are shown for the record. The model runs in harness\\plans\\obj2_step7d_latency.json then check the replies.

Writes results_retrieval\\integration\\context_view.md and context_view.json.
"""

import argparse
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import bench_retrieval as B  # noqa: E402
from knowledge_base import DEFAULT_CORPUS, DEFAULT_FALLBACK, load_integration_k, view_tokens  # noqa: E402
from language import is_hinglish  # noqa: E402

TOLERANCE = 0.02
MAX_CONTEXT_TOKENS = 1500
VARIANTS = [("full", False), ("compact", False), ("full", True), ("compact", True)]


def shown(ranked, chunks, k, view, gate, threshold, exempt):
    chosen, used = [], 0
    for cid, s in ranked[:k]:
        tok = view_tokens(chunks[cid], view)
        if chosen and used + tok > MAX_CONTEXT_TOKENS:
            break
        chosen.append((cid, s, tok))
        used += tok
    if gate and not exempt:
        chosen = [c for c in chosen if c[1] >= threshold]
    return [c[0] for c in chosen], sum(c[2] for c in chosen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ranks", default=os.path.join(ROOT, "results_retrieval", "latency", "ranks", "openvino-len256-depth20.jsonl"))
    ap.add_argument("--eval", default=os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    ap.add_argument("--fallback", default=DEFAULT_FALLBACK)
    ap.add_argument("--out", default=os.path.join(ROOT, "results_retrieval", "integration"))
    a = ap.parse_args()
    with open(a.fallback, encoding="utf-8") as f:
        fb = json.load(f)
    T, bypass = float(fb["threshold"]), bool(fb.get("hinglish_bypass"))
    k = load_integration_k(os.path.join(a.out, "integration.json"))
    chunks = {c["id"]: c for c in B.load_jsonl(DEFAULT_CORPUS)}
    items = B.load_jsonl(a.eval)
    ranks = {r["id"]: [tuple(x) for x in r["top"]] for r in B.load_jsonl(a.ranks)}

    res = {}
    for view, gate in VARIANTS:
        for split in ("dev", "test"):
            hit, toks, toks_all = [], [], []
            for it in items:
                if it["split"] != split:
                    continue
                ids, t = shown(ranks[it["id"]], chunks, k, view, gate, T, bypass and is_hinglish(it["query"]))
                toks_all.append(t)
                if it["gold_ids"] and it["answer_type"] == "fact":
                    hit.append(1 if set(ids) & set(it["gold_ids"]) else 0)
                    toks.append(t)
            res[(view, gate, split)] = dict(gold_shown=sum(hit) / len(hit), n=len(hit),
                                            tokens_mean=statistics.mean(toks_all),
                                            tokens_p90=sorted(toks_all)[int(0.9 * (len(toks_all) - 1))])
    base = res[("full", False, "dev")]["gold_shown"]
    ok = [(v, g) for v, g in VARIANTS if res[(v, g, "dev")]["gold_shown"] >= base - TOLERANCE - 1e-9]
    choice = min(ok, key=lambda vg: res[(vg[0], vg[1], "dev")]["tokens_mean"])

    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "context_view.json"), "w", encoding="utf-8") as f:
        json.dump(dict(view=choice[0], chunk_gate=choice[1], k=k, threshold=T,
                       rule=f"fewest dev context tokens with dev gold-shown rate >= current - {TOLERANCE:.0%}",
                       results={f"{v}{'+gate' if g else ''}/{s}": r for (v, g, s), r in res.items()}), f, indent=2)
    pct = lambda x: f"{100 * x:.1f}%"
    L = ["# Step 7d, part 1: what the model is shown", "",
         f"k = {k}, threshold {T:.3f}, Hinglish exempt from the gate: {bypass}. Tokens are the corpus estimate; "
         "Qwen's real count is about 1.25 times higher (fitted on the Step 7 pilot).", "",
         "| Variant | Dev gold shown | Dev tokens mean / p90 (all questions) | Test gold shown | Test tokens mean |",
         "|---|---|---|---|---|"]
    for v, g in VARIANTS:
        d, t = res[(v, g, "dev")], res[(v, g, "test")]
        name = v + (" + chunk gate" if g else "") + (" **chosen**" if (v, g) == choice else "")
        L.append(f"| {name} | {pct(d['gold_shown'])} | {d['tokens_mean']:.0f} / {d['tokens_p90']} | "
                 f"{pct(t['gold_shown'])} | {t['tokens_mean']:.0f} |")
    L += ["", f"Rule: fewest dev tokens among variants within {TOLERANCE * 100:.0f} points of the current setup's dev "
          f"gold-shown rate ({pct(base)}). Chosen: **{choice[0]}{' + chunk gate' if choice[1] else ''}**.",
          "Test numbers did not choose. The model runs (obj2_step7d_latency.json) check that replies hold up."]
    with open(os.path.join(a.out, "context_view.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
