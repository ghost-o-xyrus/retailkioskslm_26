"""
Objective 4, Step 8: speed and RAM with the adapter; the pre-registered rules.

    python finetune\\step8_verdicts.py --run-compare     # runs the paired comparisons first, then the rules

Reads harness/plans/obj4_step8.json (Tier A adapter, patches), results_obj4/_step7/verdicts.json (Tier B candidate),
the runs' cases.jsonl and run_meta.json, and with --run-compare writes results_obj4/_compare_step8
(eval/compare_dev.py: paired per-case waits). Writes results_obj4/_step8/verdicts.md and verdicts.json.

Rules (made exact before any Step 8 run), Tier A in place (2B Q8_0 on CPU, dev speed subset, 2 repeats):
  (1) writing speed: the adapter's own cost (O3-final + adapter against O3-final, same patches): the median
      tokens per second over all replies and repeats is at least 90% of O3-final's, on store questions and on tool
      cases;
  (2) total reply time: the deployed candidate (from Step 7) against O3-final: the median per-case change is not
      significantly longer (the bootstrap interval is not wholly above 0), on both sets.
  The Tier A adapter is deployed only if (1) and (2) hold; otherwise O3-final stays deployed for Tier A and the
  quality gain is reported with its speed cost.
Reported: first word, peak server RAM with and without the adapter (expected under 0.2 GB more), and Tier B from
the Vulkan quality runs of Steps 6-7 (its deployed candidate against O3-final: first word, total time, writing
speed).
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
LABEL = {"rag": "store questions", "v12": "tool cases", "fup": "follow-ups"}


def writing_speed(run):
    recs = C.records(R, run, repeat0=False)
    if recs is None:
        return None
    return C.median([(r.get("metrics") or {}).get("tokens_per_s") for r in recs.values() if not r.get("error")])


def peak_ram(run):
    p = os.path.join(R, run, "run_meta.json")
    return C.load(p).get("run_peak_rss_mb") if os.path.exists(p) else None


def tier_b_prefix(dep):
    b = dep.get("adapter")
    if not b:
        return None
    t = TAG[b]
    if dep.get("short_reply"):
        return f"o4s7_4b_{t}_shortoff" if dep.get("patches") == "off" else f"o4s7_4b_{t}_short"
    return f"o4s6_4b_{t}"


def main(argv=None):
    global R
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=R)
    ap.add_argument("--plan", default=os.path.join(ROOT, "harness", "plans", "obj4_step8.json"))
    ap.add_argument("--run-compare", action="store_true")
    args = ap.parse_args(argv)
    R = args.results
    plan = C.load(args.plan)
    a, off = plan["adapters"]["A"], plan["adapters"].get("patches_off")
    t = TAG[a]
    v7p = os.path.join(R, "_step7", "verdicts.json")
    depB = (C.load(v7p).get("deployed", {}).get("B") or {}) if os.path.exists(v7p) else {}
    bpre = tier_b_prefix(depB)
    cand = f"o4s8_2b_{t}_off" if off else f"o4s8_2b_{t}"
    pairs = []
    for s in ("rag", "v12"):
        pairs.append((f"o4s8_2b_base_{s}", f"o4s8_2b_{t}_{s}"))
        if off:
            pairs.append((f"o4s8_2b_base_{s}", f"{cand}_{s}"))
    if bpre:
        pairs += [(f"o4s6_4b_base_{s}", f"{bpre}_{s}") for s in ("rag", "v12", "fup")]
    if args.run_compare:
        C.run_compare(R, pairs, "_compare_step8")
    if not os.path.exists(os.path.join(R, "_compare_step8", "compare.json")):
        sys.exit(f"{os.path.join(R, '_compare_step8', 'compare.json')} not found: run this with --run-compare")
    _, _, waits = C.read_compare(R, "_compare_step8")
    res = {"tier_A": {"adapter": a, "patches_off": off, "checks": {}}, "tier_B": {"candidate": bpre}}
    L = ["# Step 8: speed and RAM (pre-registered rules)", "",
         f"Tier A: O3-final against O3-final + {a}" + (f" and the deployed candidate ({a}, patches off)" if off else "")
         + "; 2B Q8_0 on CPU, 4 threads, dev speed subset, 2 repeats.", "",
         "## Tier A in place", "",
         "| Set | Writing speed tokens/s: O3-final → + adapter (ratio) | Rule (1) | Total time change, candidate s "
         "[95% CI] | Rule (2) | First word change, candidate s [95% CI] |",
         "|---|---|---|---|---|---|"]
    ok1, ok2 = [], []
    for s in ("rag", "v12"):
        wb, wa = writing_speed(f"o4s8_2b_base_{s}"), writing_speed(f"o4s8_2b_{t}_{s}")
        ratio = wa / wb if wa and wb else None
        r1 = ratio is not None and ratio >= 0.90
        ok1.append(r1)
        w = waits.get((f"o4s8_2b_base_{s}", f"{cand}_{s}"))
        r2 = w is not None and w["total_s"][1] <= 0
        ok2.append(r2)
        res["tier_A"]["checks"][s] = {"tokens_per_s": [wb, wa], "ratio": ratio, "writing_speed": r1,
                                      "total_s": w["total_s"] if w else None,
                                      "first_word_s": w["first_word_s"] if w else None, "total_time": r2}
        f2 = lambda x: "–" if x is None else f"{x:.1f}"      # noqa: E731
        L.append(f"| {LABEL[s]} | {f2(wb)} → {f2(wa)}" + (f" ({ratio:.2f})" if ratio else "") +
                 f" | {'met' if r1 else 'not met' if ratio else 'missing'} | "
                 + (f"{w['total_s'][0]:+.2f} [{w['total_s'][1]:+.2f}, {w['total_s'][2]:+.2f}] | "
                    f"{'met' if r2 else 'not met'} | {w['first_word_s'][0]:+.2f} [{w['first_word_s'][1]:+.2f}, "
                    f"{w['first_word_s'][2]:+.2f}] |" if w else "not run | missing | |"))
    res["tier_A"]["speed_rules_met"] = all(ok1) and all(ok2)
    rb = max(filter(None, [peak_ram(f"o4s8_2b_base_{s}") for s in ("rag", "v12")]), default=None)
    ra = max(filter(None, [peak_ram(f"o4s8_2b_{t}_{s}") for s in ("rag", "v12")]), default=None)
    res["tier_A"]["peak_ram_mb"] = [rb, ra]
    L += ["", f"Peak server RAM: O3-final {rb or '–'} MB, + adapter {ra or '–'} MB"
          + (f" ({ra - rb:+.0f} MB; expected under +200 MB)" if rb and ra else "") + ".", "",
          f"**Tier A speed rules: {'met' if res['tier_A']['speed_rules_met'] else 'not met'}** -> deployed: "
          + (f"O3-final + {a}" + (", patches off" if off else "") if res["tier_A"]["speed_rules_met"]
             else "O3-final (the adapter's quality gain is reported with its speed cost)")]
    L += ["", "## Tier B (Vulkan quality runs, reported)", ""]
    if not bpre:
        L.append("No Tier B adapter is deployed; nothing to time.")
    else:
        L += [f"O3-final against {bpre} (single runs, per-case medians).", "",
              "| Set | Writing speed tokens/s | First word change s [95% CI] | Total time change s [95% CI] |",
              "|---|---|---|---|"]
        for s in ("rag", "v12", "fup"):
            wb, wa = writing_speed(f"o4s6_4b_base_{s}"), writing_speed(f"{bpre}_{s}")
            w = waits.get((f"o4s6_4b_base_{s}", f"{bpre}_{s}"))
            res["tier_B"][s] = {"tokens_per_s": [wb, wa], "first_word_s": w["first_word_s"] if w else None,
                                "total_s": w["total_s"] if w else None}
            L.append(f"| {LABEL[s]} | " + ("–" if not (wb and wa) else f"{wb:.1f} → {wa:.1f} ({wa / wb:.2f})") + " | "
                     + (f"{w['first_word_s'][0]:+.2f} [{w['first_word_s'][1]:+.2f}, {w['first_word_s'][2]:+.2f}] | "
                        f"{w['total_s'][0]:+.2f} [{w['total_s'][1]:+.2f}, {w['total_s'][2]:+.2f}] |" if w else "– | – |"))
    os.makedirs(os.path.join(R, "_step8"), exist_ok=True)
    with open(os.path.join(R, "_step8", "verdicts.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(R, "_step8", "verdicts.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
