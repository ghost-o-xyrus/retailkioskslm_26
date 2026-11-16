"""
Objective 4, Step 7: patches removed (H5) and the 4B's short-reply rule with the adapter; the pre-registered rules.

    python finetune\\step7_verdicts.py --run-compare     # runs the comparisons first, then the rules

Reads harness/plans/obj4_step7.json (which adapters ran), results_obj4/_step6/verdicts.json, and writes, with
--run-compare, results_obj4/_compare_step7 and _dialogues_step7 (eval/compare_dev.py --all-hinglish and
eval/score_dialogues.py, every run against the Step 6 baseline of its tier). Writes results_obj4/_step7/verdicts.md
and verdicts.json, whose "deployed" entry is what Step 8 times.

Rules (made exact before any Step 7 run). "No regression" is Step 6's H4 rule against O3-final on dev (no
single-turn set worse; dialogue targets met and fit not lower; pooled Hinglish at most 5 points lower). "Printed" is
H1: at most 1 printed tool call in each of the four runs.
  Tier A, H5: <adapter>, patches off (o4s7_2b_<tag>_off) shows no regression and printed holds. Then the patches
     (forced-answer recovery, staff check) are switched off for Tier A; otherwise they stay on.
  Tier B, short replies: <adapter> + short replies (o4s7_4b_<tag>_short) shows no regression and printed holds.
     This decides a 4B adapter that Step 6 left provisional: kept with the short-reply rule back on if it holds,
     not kept otherwise. An adapter Step 6 already kept stays kept; the short-reply rule comes back only if this
     holds.
  Tier B, H5: the same with the patches off too (o4s7_4b_<tag>_shortoff). Counted only if the short-reply check
     holds.
  Controls (reported): O3-final with the patches off (Tier A) and O3-final with short replies (Tier B), each against
     O3-final, show what the patches and the short-reply rule do without an adapter.
Deployed candidate per tier: no adapter (O3-final), or the adapter with or without the patches and, for Tier B,
with or without short replies.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import verdict_common as C  # noqa: E402

R = os.path.join(ROOT, "results_obj4")
TAG = {"lora_2b": "lora", "qlora_2b": "qlora", "lora_4b": "lora", "qlora_4b": "qlora"}


def pairs_for(a, b):
    """(base prefix, new prefix, label, decisive) for the adapters that ran."""
    out = []
    if a:
        t = TAG[a]
        out += [("o4s6_2b_base", f"o4s7_2b_{t}_off", f"{a}, patches off", True),
                ("o4s6_2b_base", "o4s7_2b_base_off", "O3-final, patches off (control)", False)]
    if b:
        t = TAG[b]
        out += [("o4s6_4b_base", f"o4s7_4b_{t}_short", f"{b} + short replies", True),
                ("o4s6_4b_base", f"o4s7_4b_{t}_shortoff", f"{b} + short replies, patches off", True),
                ("o4s6_4b_base", "o4s7_4b_base_short", "O3-final + short replies (control)", False)]
    return out


def main(argv=None):
    global R
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=R)
    ap.add_argument("--plan", default=os.path.join(ROOT, "harness", "plans", "obj4_step7.json"))
    ap.add_argument("--run-compare", action="store_true")
    args = ap.parse_args(argv)
    R = args.results
    plan = C.load(args.plan)
    a, b = plan["adapters"].get("A"), plan["adapters"].get("B")
    v6p = os.path.join(R, "_step6", "verdicts.json")
    v6 = C.load(v6p) if os.path.exists(v6p) else {}
    if v6 and ("H6" in v6 or "tier_B_carried" in v6):
        import build_step78_plans as B
        want = {"A": B.carried(v6, "A"), "B": B.carried(v6, "B")}
        if want != {"A": a, "B": b}:
            sys.exit(f"{args.plan} runs adapters A={a}, B={b}, but Step 6 carried A={want['A']}, B={want['B']}. "
                     "Rebuild it (python finetune\\build_step78_plans.py step7), run the missing runs, then rerun this.")
    pairs = pairs_for(a, b)
    if args.run_compare:
        sp = [(f"{bp}_{s}", f"{np_}_{s}") for bp, np_, _, _ in pairs for s in ("rag", "v12", "fup")]
        druns = sorted({f"{x}_dlg" for bp, np_, _, _ in pairs for x in (bp, np_)})
        dp = [(f"{bp}_dlg", f"{np_}_dlg") for bp, np_, _, _ in pairs]
        C.run_compare(R, sp, "_compare_step7", druns, dp, "_dialogues_step7")
    if not os.path.exists(os.path.join(R, "_compare_step7", "compare.json")):
        sys.exit(f"{os.path.join(R, '_compare_step7', 'compare.json')} not found: run this with --run-compare")
    rows, disc, _ = C.read_compare(R, "_compare_step7")
    dsum, drows = C.read_dialogues(R, "_dialogues_step7")
    res = {"adapters": {"A": a, "B": b}, "checks": {}}
    L = ["# Step 7: patches removed and short replies with the adapter (pre-registered rules)", "",
         f"Tier A adapter: {a or 'none'}; Tier B adapter: {b or 'none'} "
         f"(Step 6 status: {v6.get(b, {}).get('status', '–') if b else '–'}). Baselines: the Step 6 O3-final runs.", "",
         "## Sets against O3-final", "",
         "| Run | Set | Cases | O3-final | Run | Difference [95% CI] | McNemar p | Verdict |", "|---|---|---:|---:|---:|---|---:|---|"]
    for bp, np_, label, decisive in pairs:
        holds, c, detail = C.no_regression(rows, dsum, drows, bp, np_)
        pr, counts = C.printed_check(R, np_)
        res["checks"][np_] = {"label": label, "decisive": decisive, "no_regression": holds, "sets": c,
                              "printed": pr, "printed_counts": counts,
                              "hinglish_pooled": detail["hinglish_pooled"],
                              "dialogue_fit_change": detail["dialogue_fit_change"],
                              "holds": holds and pr == "met"}
        L += C.fmt_rows(rows, bp, np_, label)
    # decisions
    dep = {"A": {"adapter": None, "patches": "on", "short_reply": True},
           "B": {"adapter": None, "patches": "on", "short_reply": False}}
    if a:
        dep["A"]["adapter"] = a
        if res["checks"][f"o4s7_2b_{TAG[a]}_off"]["holds"]:
            dep["A"]["patches"] = "off"
    if b:
        t = TAG[b]
        short_ok = res["checks"][f"o4s7_4b_{t}_short"]["holds"]
        off_ok = res["checks"][f"o4s7_4b_{t}_shortoff"]["holds"]
        status6 = v6.get(b, {}).get("status", "")
        if short_ok:
            dep["B"].update(adapter=b, short_reply=True, patches="off" if off_ok else "on")
            res["tier_B"] = "kept, short replies back on" + (", patches off" if off_ok else "")
        elif status6 == "kept":
            dep["B"].update(adapter=b, short_reply=False)
            res["tier_B"] = "kept (Step 6), short replies stay off"
        else:
            res["tier_B"] = "not kept (provisional in Step 6; the short-reply check does not hold)"
    res["H5"] = {"A": (dep["A"]["patches"] == "off") if a else None, "B": (dep["B"]["patches"] == "off") if b else None}
    res["deployed"] = dep

    L += ["", "## Printed tool calls (runs, repeat 0)", "", "| Run | Store | Tool cases | Follow-ups | Dialogues | Rule |",
          "|---|---:|---:|---:|---:|---|"]
    for np_, c in res["checks"].items():
        p = c["printed_counts"]
        L.append(f"| {c['label']} | " + " | ".join("–" if p[s] is None else str(p[s]) for s in C.ALL_SETS)
                 + f" | {c['printed']} |")
    L += ["", "## Checks", ""]
    for np_, c in res["checks"].items():
        hp = c["hinglish_pooled"]
        L.append(f"- {c['label']}{'' if c['decisive'] else ' (reported only)'}: no regression "
                 f"**{'holds' if c['no_regression'] else 'does not hold'}** ("
                 + ", ".join(f"{k}: {v}" for k, v in c["sets"].items()) + f"); printed {c['printed']}"
                 + (f"; Hinglish pooled {hp['diff_pts']:+.1f} points" if hp else "")
                 + (f"; dialogue fit {c['dialogue_fit_change'][0]:+.1f} points" if c["dialogue_fit_change"] else ""))
    L += ["", "## Decisions", "",
          f"- H5, Tier A: " + ("not tested (no adapter)" if not a else
                              "holds: the patches are switched off" if res["H5"]["A"] else "does not hold: the patches stay on"),
          f"- Tier B: {res.get('tier_B', 'no adapter')}"
          + ("" if not b else f"; H5 {'holds' if res['H5']['B'] else 'does not hold'}"),
          "- Deployed candidate (timed in Step 8 for Tier A): "
          + "; ".join(f"Tier {t}: " + ("O3-final" if not d["adapter"] else
                                         f"O3-final + {d['adapter']}, patches {d['patches']}"
                                         + (", short replies" if t == "B" and d["short_reply"] else ""))
                      for t, d in dep.items())]
    L += ["", "## Staff discipline and waits on store questions (reported)", "",
          "| Run | Model staff calls on answerable | Offered, not called | First word p50 |", "|---|---|---|---|"]
    for bp, np_, label, _ in pairs:
        sp = disc.get((f"{bp}_rag", f"{np_}_rag"))
        if sp:
            bd, nd = sp["base_disc"], sp["new_disc"]
            fb, fn = sp["base_speed"].get("first_p50_s"), sp["new_speed"].get("first_p50_s")
            L.append(f"| {label} | {bd['staff_on_answerable']} → {nd['staff_on_answerable']} | "
                     f"{bd['offer_no_call']} → {nd['offer_no_call']} | "
                     + (f"{fb:.1f} s → {fn:.1f} s" if fb is not None and fn is not None else "–") + " |")
    os.makedirs(os.path.join(R, "_step7"), exist_ok=True)
    with open(os.path.join(R, "_step7", "verdicts.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(R, "_step7", "verdicts.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
