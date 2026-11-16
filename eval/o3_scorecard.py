"""
Objective 3, Step 15: the success-criteria scorecard for O3-final, per tier, on the test set O3-T.

    python eval\\o3_scorecard.py

Reads only existing results (no model runs):
    results_obj3/o3t_{final,b0}_{2b,4b}_{rag,v12,fup}     Step 14 quality runs (laptop, Vulkan)
    results_obj3/_dialogues_step14/summary.json           Step 14 dialogues
    results_obj3/o3tsp_a_2b_{rag,v12}_{b0,final}          Step 14 Tier A in-place timing (laptop CPU, 2 repeats)
    results_obj3/_step15/ladder.json                      oracle and no-retrieval references (eval/step15_ladder.py)
    eval/rag_judge/step15/summary.json                    judged rates (eval/rag_judge/summary_o3.py)
Rows whose source is not there yet say "pending". Writes results_obj3/_step15/scorecard.md and scorecard.json.

Definitions (as in the Objective 3 success criteria):
  whole-system tool accuracy   tool cases passed (right tool run with valid arguments and a grounded reply)
  model alone                  tool cases the router left "unclear" (the model chose the tool), passed
  valid arguments              model-written calls (not the kiosk's own) with valid JSON for a known tool
  router                       route = the case's intended route (eval/route_labels.py), single-message store
                               questions and tool cases; store questions sent down a no-retrieval route
  staff hand-off               hand-off cases passed; model staff calls on answerable store questions; turns
                               with more than one staff call
  rounds, tokens read          mean model requests and prompt tokens per case over store questions, tool cases
                               and follow-ups; tokens read as a share of O3-B0 (Objective 2's deployed setup)
  waits                        Tier A: in place on the laptop CPU (every repeat); Tier B: the Vulkan quality runs
                               on the laptop (one repeat, the same 70-case speed subset)
  retrieval                    retrieval time of store-route turns in the Tier A in-place runs
  RAM                          peak of the model server plus the assistant process, and the assistant's growth
                               over O3-B0 (the added retrieval and routing stack)
"""

import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
R = os.path.join(ROOT, "results_obj3")
OUT = os.path.join(R, "_step15")
TIERS = (("A", "2b", "Qwen3.5-2B"), ("B", "4b", "Qwen3.5-4B"))
RETRIEVE = {"store", "unclear"}


def recs(name):
    p = os.path.join(R, name, "cases.jsonl")
    if not os.path.exists(p):
        return None
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not r.get("error"):
                out.append(r)
    return out


def rep0(rs):
    return {r["id"]: r for r in rs if r.get("repeat", 0) == 0} if rs is not None else None


def cases(fn):
    with open(os.path.join(HERE, fn), encoding="utf-8") as f:
        return {c["id"]: c for c in (json.loads(x) for x in f if x.strip())}


def pctl(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def load_json(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def main(argv=None):
    import score as S
    import route_labels as RL
    from compare_dev import unsupported_gold, discipline
    os.makedirs(OUT, exist_ok=True)
    tool_cases, rag_cases = cases("eval_set_o3t.jsonl"), cases("rag_cases_o3t.jsonl")
    chunks = {c["id"]: c for c in (json.loads(x) for x in open(os.path.join(ROOT, "knowledge", "corpus.jsonl"),
                                                                 encoding="utf-8") if x.strip())}
    dlg = load_json(os.path.join(R, "_dialogues_step14", "summary.json")) or {}
    ladder = load_json(os.path.join(R, "_step15", "ladder.json")) or {}
    judge = load_json(os.path.join(ROOT, "eval", "rag_judge", "step15", "summary.json")) or {}
    card = {}
    for tier, m, model in TIERS:
        rows = []
        add = lambda crit, target, value, met, note="": rows.append(  # noqa: E731
            {"criterion": crit, "target": target, "value": value, "met": met, "note": note})
        fin = {s: rep0(recs(f"o3t_final_{m}_{s}")) for s in ("rag", "v12", "fup")}
        b0 = {s: rep0(recs(f"o3t_b0_{m}_{s}")) for s in ("rag", "v12", "fup")}
        v = fin["v12"]
        if v is not None:
            tc = [(c, v.get(i)) for i, c in tool_cases.items() if c["mode"] == "tools" and i in v]
            passed = [S.score_case(c, r)["passed"] for c, r in tc]
            rate = sum(passed) / len(passed)
            add("Right tool run with valid arguments, whole system", "≥ 90%", f"{rate:.1%} ({sum(passed)}/{len(passed)})",
                rate >= 0.90)
            un = [S.score_case(c, r)["passed"] for c, r in tc if r.get("route") == "unclear"]
            add("Right tool chosen by the model alone (unclear turns)", "≥ 80%",
                f"{sum(un) / len(un):.1%} ({sum(un)}/{len(un)})" if un else "no unclear turns",
                (sum(un) / len(un) >= 0.8) if len(un) >= 10 else None,
                "not measurable on O3-final: the router left only "
                f"{len(un)} tool case(s) unclear; every other one went to the kiosk's own tools or a fixed reply")
        allc = [r for s in ("rag", "v12", "fup") if fin[s] for r in fin[s].values()]
        mcalls = [c for r in allc for c in r.get("tool_calls") or [] if c.get("by") != "harness" and c.get("guard") != "staff_check"]
        if mcalls:
            ok = sum(1 for c in mcalls if c.get("arguments_valid_json") and c.get("known_tool"))
            add("Valid arguments in model-written calls", "≥ 98%", f"{ok / len(mcalls):.1%} ({ok}/{len(mcalls)})",
                ok / len(mcalls) >= 0.98)
        lab_ok = lab_n = store_n = store_bad = 0
        for s, cs in (("rag", rag_cases), ("v12", tool_cases)):
            if fin[s] is None:
                continue
            for i, r in fin[s].items():
                c = cs.get(i)
                if not c or len(c["messages"]) != 1:          # single-message cases only (as in Step 4)
                    continue
                lab = RL.label(dict(c, set="rag") if s == "rag" else c)
                if not lab or r.get("route") in (None, "none"):
                    continue
                lab_n += 1
                lab_ok += r["route"] == lab or (lab == "store" and r["route"] == "unclear")
                if lab == "store":
                    store_n += 1
                    store_bad += r["route"] not in RETRIEVE
        if lab_n:
            add("Router accuracy", "≥ 95%", f"{lab_ok / lab_n:.1%} ({lab_ok}/{lab_n})", lab_ok / lab_n >= 0.95,
                "unclear counts as right for a store question (it is retrieved)")
            add("Store questions sent down a tool path", "≤ 3%", f"{store_bad / store_n:.1%} ({store_bad}/{store_n})",
                store_bad / store_n <= 0.03)
        ds = dlg.get(f"o3t_final_{m}_dlg")
        if ds:
            add("Slots known before the first recommendation (≥ 2 of 4)", "≥ 85% of dialogues",
                f"{ds['slots2_share']:.0%}", ds["slots2_share"] >= 0.85)
            add("Questions before the recommendation", "≤ 2", f"max {ds['questions_max']}, mean {ds['questions_mean']:.2f}",
                ds["questions_max"] <= 2)
            add("Shown watches fit what the customer said", "≥ 90%", f"{ds['fit_mean']:.0%}", ds["fit_mean"] >= 0.90)
        if v is not None:
            ho = [(c, v.get(i)) for i, c in tool_cases.items() if c["mode"] == "tools" and i in v and c["category"] == "handoff"]
            hp = [S.score_case(c, r)["passed"] for c, r in ho]
            if hp:
                add("Staff called when asked or needed", "≥ 90%", f"{sum(hp) / len(hp):.0%} ({sum(hp)}/{len(hp)})",
                    sum(hp) / len(hp) >= 0.9, "hand-off tool cases")
        if fin["rag"] is not None:
            dd = discipline(fin["rag"], rag_cases)
            n_ans = sum(1 for i in fin["rag"] if rag_cases.get(i, {}).get("expected", {}).get("behaviour") == "answer")
            add("Unneeded staff calls", "≤ 5%", f"{dd['staff_on_answerable'] / n_ans:.1%} ({dd['staff_on_answerable']}/{n_ans})",
                dd["staff_on_answerable"] / n_ans <= 0.05, "model staff calls on answerable store questions")
        # a staff call counts when it raised a ticket; a repeated call is answered "already notified" by the
        # loop guard (no second ticket) and the staff check's note is not a call
        tick = lambda c: isinstance(c.get("result"), dict) and bool(c["result"].get("ticket"))  # noqa: E731
        multi = sum(1 for r in allc if sum(1 for c in r.get("tool_calls") or [] if c.get("name") == "call_staff"
                                           and tick(c)) > 1)
        repeats = sum(1 for r in allc for c in r.get("tool_calls") or [] if c.get("name") == "call_staff"
                      and c.get("guard") in ("repeat", "staff_repeat"))
        if allc:
            add("Staff calls per turn", "at most 1", f"{multi} turns with more than one ticket", multi == 0,
                f"{repeats} repeated calls were stopped by the loop guard (no second ticket)")
        st3 = ladder.get(f"stage3_{m}")
        add("No regression on tool cases (vs no retrieval, Stage 3)", "not significantly below",
            f"{st3['diff_pts']:+.1f} [{st3['ci'][0]:+.1f}, {st3['ci'][1]:+.1f}] ({st3['verdict']})" if st3 else "pending",
            (st3["verdict"] != "worse") if st3 else None, "Step 15 reference run (Kaggle CPU)")
        orc = ladder.get(f"oracle_{m}")
        add("Answerable store questions within 5 points of oracle cards", "≥ −5 points",
            f"{orc['diff_pts']:+.1f} [{orc['ci'][0]:+.1f}, {orc['ci'][1]:+.1f}]" if orc else "pending",
            (orc["diff_pts"] >= -5) if orc else None, "Step 15 reference run (Kaggle CPU)")
        jf = judge.get(f"{model}|final")
        for key, crit, tgt, lim in (("unanswerable", "Hallucination on unanswerable questions", "≤ 5%", 0.05),
                                    ("near_miss", "Hallucination on near-miss questions", "≤ 5%", 0.05),
                                    ("false_refusals", "False refusals", "≤ 10%", 0.10)):
            if jf and jf[key][1]:
                k, n = jf[key]
                add(crit, tgt, f"{k / n:.1%} ({k}/{n})", k / n <= lim, "blind judge")
            else:
                add(crit, tgt, "pending", None, "blind judge")
        if jf and jf["hinglish"][1]:
            k, n = jf["hinglish"]
            add("Hallucination, Hinglish (unanswerable + near-miss)", "reported", f"{k / n:.1%} ({k}/{n})", None, "blind judge")
        if fin["rag"] is not None:
            bad, n = unsupported_gold(fin["rag"], rag_cases, chunks)
            add("Unsupported details in answers (automatic)", "≤ 5%", f"{bad / n:.1%} ({bad}/{n})", bad / n <= 0.05,
                "knowledge-path replies with a detail in neither the gold card nor the tool results")
        if jf and jf["unsupported_sample"][1]:
            k, n = jf["unsupported_sample"]
            add("Unsupported details in answers (judged sample)", "≤ 5%", f"{k / n:.1%} ({k}/{n})", k / n <= 0.05, "blind judge")
        # waits
        if tier == "A":
            sp = [r for s in ("rag", "v12") for r in (recs(f"o3tsp_a_2b_{s}_final") or [])]
            src = "in place, laptop CPU, every repeat"
        else:
            ids = set((load_json(os.path.join(HERE, "o3t_speed_ids.json")) or {}).get("ids") or [])
            sp = [r for s in ("rag", "v12") if fin[s] for r in fin[s].values() if not ids or r["id"] in ids]
            src = "laptop Vulkan quality runs, speed subset, one repeat"
        fw = [r["metrics"]["first_visible_ms"] / 1000 for r in sp if (r.get("metrics") or {}).get("first_visible_ms") is not None]
        tt = [r["metrics"]["end_to_end_ms"] / 1000 for r in sp if (r.get("metrics") or {}).get("end_to_end_ms") is not None]
        lim = (6, 12) if tier == "A" else (4, 9)
        if fw:
            p50, p90 = statistics.median(fw), pctl(fw, 0.9)
            add("Wait to first word, median / 90th percentile", f"≤ {lim[0]} s / ≤ {lim[1]} s", f"{p50:.1f} s / {p90:.1f} s",
                p50 <= lim[0] and p90 <= lim[1], src)
        if tt:
            add("Full reply, median", "≤ 11 s", f"{statistics.median(tt):.1f} s", statistics.median(tt) <= 11, src)
        rounds = [len(r.get("turns") or []) for r in allc]
        if rounds:
            add("Model rounds per turn, mean", "≤ 1.3", f"{statistics.mean(rounds):.2f}", statistics.mean(rounds) <= 1.3,
                "store questions, tool cases and follow-ups")
        rd = lambda rs: [sum(t.get("prompt_n") or 0 for t in r.get("turns") or []) for r in rs]  # noqa: E731
        allb = [r for s in ("rag", "v12", "fup") if b0[s] for r in b0[s].values()]
        if allc and allb:
            share = statistics.mean(rd(allc)) / statistics.mean(rd(allb))
            add("Tokens read before the answer, vs Objective 2 deployed", "≤ 50%",
                f"{share:.0%} ({statistics.mean(rd(allc)):.0f} vs {statistics.mean(rd(allb)):.0f})", share <= 0.5)
        sp_store = [r for r in (recs("o3tsp_a_2b_rag_final") or []) if r.get("route") in RETRIEVE
                    and (r.get("retrieval") or {}).get("chunk_ids")]
        if tier == "A" and sp_store:
            ms = [r["metrics"]["retrieval_ms"] for r in sp_store if (r.get("metrics") or {}).get("retrieval_ms") is not None]
            if ms:
                add("Retrieval latency p50 (CPU)", "≤ 300 ms", f"{statistics.median(ms):.0f} ms",
                    statistics.median(ms) <= 300, "store-route turns, in place")
        ramsrc = (sp if tier == "A" else allc)
        bsrc = ([r for s in ("rag", "v12") for r in (recs(f"o3tsp_a_2b_{s}_b0") or [])] if tier == "A" else allb)
        tot = [((r.get("metrics") or {}).get("peak_rss_mb") or 0) + ((r.get("metrics") or {}).get("harness_rss_mb") or 0)
               for r in ramsrc]
        hf = [(r.get("metrics") or {}).get("harness_rss_mb") for r in ramsrc]
        hb = [(r.get("metrics") or {}).get("harness_rss_mb") for r in bsrc]
        hf, hb = [x for x in hf if x], [x for x in hb if x]
        if tot and max(tot):
            cap = 5 if tier == "A" else 10
            add("Peak RAM, model server plus assistant", f"≤ {cap} GB", f"{max(tot) / 1000:.2f} GB", max(tot) / 1000 <= cap)
        if hf and hb:
            dmb = max(hf) - max(hb)
            add("RAM added over O3-B0 (assistant process)", "≤ 0.8 GB", f"{dmb / 1000:+.2f} GB", dmb / 1000 <= 0.8,
                "both include the retrieval stack; O3-final's re-ranker is the 8-bit one")
        card[tier] = rows
    L = ["# Objective 3 success criteria: O3-final on the test set O3-T", ""]
    for tier, m, model in TIERS:
        L += [f"## Tier {tier} ({model})", "", "| Criterion | Target | O3-final | Met | Note |", "|---|---|---|---|---|"]
        for r in card.get(tier, []):
            met = {True: "yes", False: "**no**", None: "–"}[r["met"]]
            L.append(f"| {r['criterion']} | {r['target']} | {r['value']} | {met} | {r['note']} |")
        n_met = sum(1 for r in card.get(tier, []) if r["met"] is True)
        n_dec = sum(1 for r in card.get(tier, []) if r["met"] is not None)
        L += ["", f"Met {n_met} of {n_dec} decided criteria.", ""]
    with open(os.path.join(OUT, "scorecard.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(OUT, "scorecard.json"), "w", encoding="utf-8") as f:
        json.dump(card, f, indent=1, ensure_ascii=False)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
