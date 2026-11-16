"""
Objective 4, Step 6: apply the pre-registered keep rules to the dev comparison of each adapter against O3-final.

    python finetune\\step6_verdicts.py --run-compare     # runs the comparisons below first, then the rules

Reads (written by the Step 6 commands):
    results_obj4/_compare_step6/compare.json          eval/compare_dev.py --all-hinglish, the pairs below
    results_obj4/_dialogues_step6/{summary.json, dialogues.csv}   eval/score_dialogues.py
    results_obj4/o4s6_*/cases.jsonl                   printed tool calls, counted per run
Writes results_obj4/_step6/verdicts.md and verdicts.json.

Runs (harness/plans/obj4_step6.json): o4s6_<model>_<base|lora|qlora>_<rag|v12|fup|dlg>. Adapters: lora_2b and
qlora_2b on Tier A (2B), lora_4b on Tier B (4B; qlora_4b if training fell back to it: read from the plan), each
against O3-final of its own tier on dev.

Rules (made exact before any Step 6 run; "set verdict" = compare_dev's verdict, the Objective 3 dev rule: better or
worse only if the bootstrap interval excludes 0 and the difference exceeds the noise bound):
  H4, no regression (all must hold):
     (a) store questions (all checked), tool cases and follow-ups: no set verdict "worse";
     (b) dialogues: the Step 6 targets (>= 95% end in a recommendation; >= 2 of 4 slots known in >= 85%; at most 2
         questions; fit >= 90%), and fit not lower than O3-final (paired interval not wholly below 0);
     (c) Hinglish: pooled over the three single-turn sets, new - base >= -5 points (the per-set Hinglish subsets
         have 10-22 cases, where one case is 5-10 points, so they are reported, not used to decide).
  H1, format: printed tool calls (the model wrote a call as text) at most 1 in each of the four runs. It counts as a
     gain only if O3-final printed more than 1 in at least one set.
  H2, staff discipline (Tier A): model staff calls on answerable store questions at most half of O3-final's, and the
     answerable subset not "worse". Testable only if O3-final made at least 4 such calls.
  H3, honest declines (Tier A): unanswerable and near-miss store questions +5 points or more with the interval
     excluding 0, and the unsupported-detail rate not higher than O3-final's.
  Keep an adapter: H4 holds and at least one of H1 (as a gain), H2, H3 holds.
     Tier B has only H1. If O3-final already prints at most 1 per set, H1 cannot show a gain here: an adapter that
     passes H4 is then "provisional", and Step 7 decides (H1 with the 4B's short-reply rule switched back on).
  H6, LoRA vs QLoRA (Tier A, reported): QLoRA against LoRA on each set. Carried to Step 7: lora_2b if kept;
     otherwise qlora_2b if kept and not worse than lora_2b on any set; otherwise none.
"""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "eval"))
sys.path.insert(0, HERE)
from step14_verdicts import paired_fit  # noqa: E402

R = os.path.join(ROOT, "results_obj4")
PLAN = os.path.join(ROOT, "harness", "plans", "obj4_step6.json")


def adapters(plan_path=PLAN):
    """{adapter: (tier, model, tag)} from the plan's runs (the 4B adapter is lora_4b or qlora_4b)."""
    out = {}
    for r in json.load(open(plan_path, encoding="utf-8"))["runs"]:
        if r.get("lora") and r["name"].endswith("_rag"):
            m, tag = r["name"].split("_")[1:3]
            out[os.path.splitext(os.path.basename(r["lora"]))[0]] = ("A" if m == "2b" else "B", m, tag)
    return out


ADAPTERS = {}
SETS = (("rag", "all checked", "store questions"), ("v12", "tool cases", "tool cases"), ("fup", "all checked", "follow-ups"))
ALL_SETS = ("rag", "v12", "fup", "dlg")
PRINTED_FLAGS = {"tool_call_as_text", "tool_text_seen"}


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def printed(run):
    """Records of repeat 0 whose model output contained a printed tool call; None if the run is missing."""
    p = os.path.join(R, run, "cases.jsonl")
    if not os.path.exists(p):
        return None
    last = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r.get("repeat", 0) == 0:
                    last[r["id"]] = r                 # last record wins (resumed runs)
    return sum(1 for r in last.values() if not r.get("error") and set(r.get("flags") or []) & PRINTED_FLAGS)


from verdict_common import dialogue_check, run_compare  # noqa: E402,F401  (dialogue_check: baseline required)


def main(argv=None):
    global R
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=R)
    ap.add_argument("--plan", default=PLAN)
    ap.add_argument("--run-compare", action="store_true",
                    help="first run eval/compare_dev.py and eval/score_dialogues.py on the Step 6 pairs")
    a = ap.parse_args(argv)
    R = a.results
    global ADAPTERS
    ADAPTERS = adapters(a.plan)
    b4 = next(n for n, v in ADAPTERS.items() if v[0] == "B")
    t4 = ADAPTERS[b4][2]
    if a.run_compare:
        pairs = [(f"o4s6_{m}_{b}_{s}", f"o4s6_{m}_{n}_{s}") for m, b, n in
                 (("2b", "base", "lora"), ("2b", "base", "qlora"), ("2b", "lora", "qlora"), ("4b", "base", t4))
                 for s in ("rag", "v12", "fup")]
        run_compare(R, pairs, "_compare_step6", [f"o4s6_{m}_{t}_dlg" for m, t in (("2b", "base"), ("2b", "lora"),
                    ("2b", "qlora"), ("4b", "base"), ("4b", t4))],
                    [("o4s6_2b_base_dlg", "o4s6_2b_lora_dlg"), ("o4s6_2b_base_dlg", "o4s6_2b_qlora_dlg"),
                     ("o4s6_4b_base_dlg", f"o4s6_4b_{t4}_dlg")], "_dialogues_step6")
    cp = os.path.join(R, "_compare_step6", "compare.json")
    if not os.path.exists(cp):
        sys.exit(f"{cp} not found: run this with --run-compare (after the Step 6 plan has run)")
    q = load(cp)
    rows = {(r["base"], r["new"], r["subset"]): r for r in q["rows"]}
    disc = {(s["base"], s["new"]): s for s in q.get("speed", [])}
    dl_dir = os.path.join(R, "_dialogues_step6")
    dsum = load(os.path.join(dl_dir, "summary.json")) if os.path.exists(os.path.join(dl_dir, "summary.json")) else {}
    drows = []
    if os.path.exists(os.path.join(dl_dir, "dialogues.csv")):
        with open(os.path.join(dl_dir, "dialogues.csv"), encoding="utf-8-sig") as f:
            drows = list(csv.DictReader(f))
    res, L = {}, ["# Step 6: adapters against O3-final on dev (pre-registered rules)", ""]

    L += ["## Sets", "", "| Adapter | Set | Cases | O3-final | + adapter | Difference [95% CI] | McNemar p | Verdict |",
          "|---|---|---:|---:|---:|---|---:|---|"]
    for name, (tier, m, tag) in ADAPTERS.items():
        c = {}
        res[name] = {"tier": tier, "checks": c}
        sets_ok = True
        for s, sub, label in SETS:
            r = rows.get((f"o4s6_{m}_base_{s}", f"o4s6_{m}_{tag}_{s}", sub))
            if r is None:
                c[label] = "missing"
                sets_ok = False
                L.append(f"| {name} | {label} | – | – | – | not run | – | missing |")
                continue
            c[label] = r["verdict"]
            sets_ok &= r["verdict"] in ("better", "tie")
            L.append(f"| {name} | {label} | {r['n']} | {r['base_rate']:.1%} | {r['new_rate']:.1%} | {r['diff_pts']:+.1f} "
                     f"[{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {r['mcnemar_p']:.3g} | {r['verdict']} |")
        # dialogues
        dv, fin, pf = dialogue_check(dsum, drows, f"o4s6_{m}_base_dlg", f"o4s6_{m}_{tag}_dlg")
        c["dialogues"] = dv
        res[name]["dialogue_fit_change"] = None if pf is None else [round(100 * x, 1) for x in pf[:3]] + [pf[3]]
        # Hinglish, pooled over the single-turn sets
        hb = hn = hN = 0
        have = 0
        for s, _, _ in SETS:
            r = rows.get((f"o4s6_{m}_base_{s}", f"o4s6_{m}_{tag}_{s}", "language: hinglish"))
            if r:
                have += 1
                hb += r["base_rate"] * r["n"]
                hn += r["new_rate"] * r["n"]
                hN += r["n"]
        if not hN:                         # pooled over the sets that have Hinglish cases
            c["hinglish"] = "missing"
            res[name]["hinglish_pooled"] = None
        else:
            d = 100 * (hn - hb) / hN
            res[name]["hinglish_pooled"] = {"n": hN, "base": hb / hN, "new": hn / hN, "diff_pts": d}
            c["hinglish"] = "ok" if d >= -5 else "fell"
        h4 = sets_ok and dv == "met" and c["hinglish"] == "ok"
        # H1
        pb = {s: printed(f"o4s6_{m}_base_{s}") for s in ALL_SETS}
        pn = {s: printed(f"o4s6_{m}_{tag}_{s}") for s in ALL_SETS}
        res[name]["printed"] = {"O3-final": pb, "adapter": pn}
        h1_holds = all(v is not None and v <= 1 for v in pn.values())
        room = any(v is not None and v > 1 for v in pb.values())
        h1 = "missing" if None in pn.values() or None in pb.values() else \
            ("gain" if h1_holds and room else "held already" if h1_holds else "not met")
        c["H1"] = h1
        # H2, H3 (Tier A)
        h2 = h3 = None
        if tier == "A":
            sp = disc.get((f"o4s6_{m}_base_rag", f"o4s6_{m}_{tag}_rag"))
            ans = rows.get((f"o4s6_{m}_base_rag", f"o4s6_{m}_{tag}_rag", "answerable"))
            if sp is None or ans is None:
                h2 = "missing"
            else:
                b, n = sp["base_disc"]["staff_on_answerable"], sp["new_disc"]["staff_on_answerable"]
                res[name]["staff_on_answerable"] = [b, n]
                h2 = "not testable" if b < 4 else \
                    ("met" if n <= b / 2 and ans["verdict"] in ("better", "tie") else "not met")
            un = rows.get((f"o4s6_{m}_base_rag", f"o4s6_{m}_{tag}_rag", "unanswerable / near-miss"))
            if sp is None or un is None or not sp.get("base_unsup") or not sp.get("new_unsup"):
                h3 = "missing"
            else:
                (bb, bn), (nb, nn) = sp["base_unsup"], sp["new_unsup"]
                res[name]["unsupported"] = [[bb, bn], [nb, nn]]
                rate_ok = nb / max(1, nn) <= bb / max(1, bn)
                h3 = "met" if un["diff_pts"] >= 5 and un["ci"][0] > 0 and rate_ok else "not met"
            c["H2"], c["H3"] = h2, h3
        c["H4"] = "met" if h4 else "not met"
        gain = h1 == "gain" or h2 == "met" or h3 == "met"
        if h4 and gain:
            status = "kept"
        elif h4 and tier == "B" and h1 == "held already":
            status = "provisional (decided in Step 7)"
        else:
            status = "not kept"
        res[name]["status"] = status

    # H6: QLoRA against LoRA (Tier A)
    h6 = {}
    for s, sub, label in SETS:
        r = rows.get(("o4s6_2b_lora_" + s, "o4s6_2b_qlora_" + s, sub))
        h6[label] = r["verdict"] if r else "missing"
    q_not_worse = all(v in ("better", "tie") for v in h6.values())
    carried = "lora_2b" if res["lora_2b"]["status"] == "kept" else \
        ("qlora_2b" if res["qlora_2b"]["status"] == "kept" and q_not_worse else None)
    res["H6"] = {"qlora_vs_lora": h6, "qlora_not_worse": q_not_worse,
                 "qlora_better_somewhere": any(v == "better" for v in h6.values()), "tier_A_carried": carried}
    res["tier_B_carried"] = b4 if res[b4]["status"] != "not kept" else None

    L += ["", "## Dialogues (40 dev profiles)", "",
          "| Run | Recommended | ≥2 slots known | Questions max | Fit (mean) | Fit vs O3-final [95% CI] |",
          "|---|---:|---:|---:|---:|---|"]
    for run in sorted(k for k in dsum if k.startswith("o4s6_")):
        s_ = dsum[run]
        m = run.split("_")[1]
        pf = paired_fit(drows, f"o4s6_{m}_base_dlg", run) if "_base_" not in run and dsum.get(f"o4s6_{m}_base_dlg") else None
        L.append(f"| {run} | {s_['recommended']:.0%} | {(s_['slots2_share'] or 0):.0%} | {s_['questions_max']} "
                 f"| {(s_['fit_mean'] or 0):.0%} | "
                 + (f"{100 * pf[0]:+.1f} [{100 * pf[1]:+.1f}, {100 * pf[2]:+.1f}]" if pf else "") + " |")
    L += ["", "## Printed tool calls (runs, repeat 0)", "", "| Adapter | | Store | Tool cases | Follow-ups | Dialogues |",
          "|---|---|---:|---:|---:|---:|"]
    for name in ADAPTERS:
        for who in ("O3-final", "adapter"):
            p = res[name]["printed"][who]
            L.append(f"| {name} | {who} | " + " | ".join("–" if p[s] is None else str(p[s]) for s in ALL_SETS) + " |")
    L += ["", "## Hypotheses and verdicts", ""]
    for name in ADAPTERS:
        r = res[name]
        hp = r.get("hinglish_pooled")
        extra = []
        if hp:
            extra.append(f"Hinglish pooled {hp['base']:.1%} → {hp['new']:.1%} ({hp['diff_pts']:+.1f} points, {hp['n']} cases)")
        if r.get("staff_on_answerable"):
            extra.append("staff on answerable {} → {}".format(*r["staff_on_answerable"]))
        if r.get("unsupported"):
            (bb, bn), (nb, nn) = r["unsupported"]
            extra.append(f"unsupported {bb}/{bn} → {nb}/{nn}")
        L.append(f"- **{name}** (Tier {r['tier']}): **{r['status']}**. "
                 + ", ".join(f"{k}: {v}" for k, v in r["checks"].items()) + (". " + "; ".join(extra) if extra else ""))
    h = res["H6"]
    L += [f"- **H6, QLoRA vs LoRA (2B):** " + ", ".join(f"{k}: {v}" for k, v in h["qlora_vs_lora"].items())
          + (". QLoRA is not worse than LoRA on any set" if h['qlora_not_worse'] else
             ". QLoRA is worse than LoRA on at least one set")
          + ("; it is better on at least one, against the expectation." if h["qlora_better_somewhere"] else "."),
          f"- Carried to Step 7: Tier A {h['tier_A_carried'] or 'none'}; Tier B {res['tier_B_carried'] or 'none'}."]

    L += ["", "## Reported, not used to decide", "",
          "| Base | New | Subset | Cases | Base | New | Difference [95% CI] | Verdict |", "|---|---|---|---:|---:|---:|---|---|"]
    for r in q["rows"]:
        if r["subset"] in ("all checked", "tool cases") or (r["subset"].startswith("tool cases:") and r["n"] < 10):
            continue
        L.append(f"| {r['base']} | {r['new']} | {r['subset']} | {r['n']} | {r['base_rate']:.1%} | {r['new_rate']:.1%} "
                 f"| {r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] | {r['verdict']} |")
    L += ["", "First-word wait p50 on the quality runs (Vulkan; Step 8 measures Tier A in place):", ""]
    for s_ in q.get("speed", []):
        b, n = s_["base_speed"].get("first_p50_s"), s_["new_speed"].get("first_p50_s")
        if b is not None and n is not None:
            L.append(f"- {s_['base']} → {s_['new']}: {b:.1f} s → {n:.1f} s")
    os.makedirs(os.path.join(R, "_step6"), exist_ok=True)
    with open(os.path.join(R, "_step6", "verdicts.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(R, "_step6", "verdicts.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
