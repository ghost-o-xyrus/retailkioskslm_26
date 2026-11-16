"""
Objective 4: write the Step 7 and Step 8 plans from the Step 6 plan and the verdicts so far.

    python finetune\\build_step78_plans.py step7      # after finetune\\step6_verdicts.py
    python finetune\\build_step78_plans.py step8      # after finetune\\step7_verdicts.py

Which adapter each tier carries comes from results_obj4/_step6/verdicts.json (Step 7) and the deployed candidate
from results_obj4/_step7/verdicts.json (Step 8); --tier-a / --tier-b override that (e.g. --tier-a lora_2b, or
--tier-a none). Every run is a Step 6 run with only the listed changes, so the Step 6 baselines (o4s6_*_base_*)
stay the comparison and are not run again.

Step 7, "patches removed" (H5), on dev, Vulkan:
  patches off = forced-answer recovery off (forced_answer "replace": a printed tool call still never reaches the
  customer as markup, it becomes the fixed staff line and counts as printed) and the staff check off. The staff
  guard is already off in O3-final. Kept: the entity check, the answer check and the fallback, which are
  deployment safeguards rather than behaviour patches. short reply = the 4B's short-reply rule (answer_length,
  max_tokens 120), as in O3-S13a2.
  Tier A:  o4s7_2b_<tag>_off        adapter, patches off
  Tier B:  o4s7_4b_<tag>_short      adapter, short replies, patches on   (decides a provisional 4B adapter)
           o4s7_4b_<tag>_shortoff   adapter, short replies, patches off
  Controls (reported, not used to decide; last in the plan, so they can be left out with --only):
           o4s7_2b_base_off         O3-final, patches off
           o4s7_4b_base_short       O3-final + short replies (O3-S13a2's 4B)

Step 8, speed and RAM: Tier A in place (2B Q8_0 on CPU, 4 threads), the 70-case dev speed subset
(eval/o3_dev_speed_ids.json), 2 repeats, alternating, as in Objective 3 Step 13a2:
  o4s8_2b_base_<set>     O3-final
  o4s8_2b_<tag>_<set>    O3-final + the adapter (the adapter's own cost)
  o4s8_2b_<tag>_off_<set>  the deployed candidate, if Step 7 switched the patches off
Tier B is read from the Vulkan quality runs of Steps 6 and 7 (no new runs).
"""

import argparse
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLANS = os.path.join(ROOT, "harness", "plans")
R = os.path.join(ROOT, "results_obj4")
SETS = ("rag", "v12", "fup", "dlg")
TAG = {"lora_2b": "lora", "qlora_2b": "qlora", "lora_4b": "lora", "qlora_4b": "qlora"}


def patches_off(r):
    r["forced_answer"] = "replace"
    r["staff_check"] = False
    r["staff_guard"] = False
    return r


def short_reply(r):
    r["answer_length"] = True
    r["max_tokens"] = 120
    return r


def step6_runs():
    return {r["name"]: r for r in json.load(open(os.path.join(PLANS, "obj4_step6.json"), encoding="utf-8"))["runs"]}


def pick(override, from_verdicts):
    if override is not None:
        return None if override.lower() == "none" else override
    return from_verdicts


def carried(v, tier):
    """What Step 6 carries to Step 7. step6_verdicts.py writes Tier A's choice inside the H6 entry (it is H6's
    outcome) and Tier B's at the top level; read both places so neither tier is silently dropped."""
    key = f"tier_{tier}_carried"
    if v.get(key) is not None:
        return v[key]
    return (v.get("H6") or {}).get(key)


def verdicts(path):
    if not os.path.exists(path):
        sys.exit(f"{path} not found: run the previous step's verdicts first, or pass --tier-a / --tier-b")
    return json.load(open(path, encoding="utf-8"))


def variant(src, name, label, *changes):
    r = copy.deepcopy(src)
    r["name"] = name
    r["config_label"] = r["config_label"] + label
    for ch in changes:
        ch(r)
    return r


def build_step7(tier_a=None, tier_b=None):
    s6 = step6_runs()
    v = verdicts(os.path.join(R, "_step6", "verdicts.json")) if tier_a is None or tier_b is None else {}
    a, b = pick(tier_a, carried(v, "A")), pick(tier_b, carried(v, "B"))
    for x in (a, b):
        if x is not None and x not in TAG:
            sys.exit(f"unknown adapter {x!r} (lora_2b, qlora_2b, lora_4b, qlora_4b or none)")
    main_runs, controls = [], []
    for s in SETS:
        if a:
            t = TAG[a]
            main_runs.append(variant(s6[f"o4s6_2b_{t}_{s}"], f"o4s7_2b_{t}_off_{s}", ", patches off", patches_off))
            controls.append(variant(s6[f"o4s6_2b_base_{s}"], f"o4s7_2b_base_off_{s}", ", patches off (control)",
                                    patches_off))
        if b:
            t = TAG[b]
            main_runs.append(variant(s6[f"o4s6_4b_{t}_{s}"], f"o4s7_4b_{t}_short_{s}", ", short replies", short_reply))
            main_runs.append(variant(s6[f"o4s6_4b_{t}_{s}"], f"o4s7_4b_{t}_shortoff_{s}", ", short replies, patches off",
                                     short_reply, patches_off))
            controls.append(variant(s6[f"o4s6_4b_base_{s}"], f"o4s7_4b_base_short_{s}", ", short replies (control)",
                                    short_reply))
    runs = main_runs + controls
    plan = {"name": "obj4_step7",
            "description": "Objective 4, Step 7: patches removed (H5), and the 4B's short-reply rule back on with the "
                           f"adapter. Tier A adapter: {a or 'none'}; Tier B adapter: {b or 'none'}. Dev, Vulkan; the "
                           f"Step 6 baselines are the comparison. {len(main_runs)} runs, then {len(controls)} "
                           "control runs (reported only; leave them out with --only if time is short). About "
                           f"{round(len(runs) * 12 / 60, 1)} hours; resumable.",
            "base_dir": "..", "results_dir": "results_obj4", "defaults": {"port": 8080, "set": "all", "repeats": 1,
                                                                         "temperature": 0},
            "adapters": {"A": a, "B": b}, "runs": runs}
    return plan


def build_step8(tier_a=None):
    s6 = step6_runs()
    v7 = os.path.join(R, "_step7", "verdicts.json")
    if tier_a is not None:
        a, off = pick(tier_a, None), False
    else:
        cand = verdicts(v7).get("deployed", {}).get("A") or {}
        a, off = cand.get("adapter"), cand.get("patches") == "off"
    if a is not None and a not in ("lora_2b", "qlora_2b"):
        sys.exit(f"unknown Tier A adapter {a!r} (lora_2b, qlora_2b or none)")
    if not a:
        sys.exit("Tier A carries no adapter: there is no Tier A speed comparison to make")
    t = TAG[a]

    def speed(src, name, label, *changes):
        r = variant(src, name, label + " (Tier A timing)", *changes)
        r.update(backend="cpu", server_exe="llama-cpu/llama-server.exe",
                 server_args=["--jinja", "-c", "8192", "-np", "1", "-ngl", "0", "-t", "4"],
                 ids="eval/o3_dev_speed_ids.json", repeats=2, split="dev")
        return r
    runs = []
    for s in ("rag", "v12"):
        runs.append(speed(s6[f"o4s6_2b_base_{s}"], f"o4s8_2b_base_{s}", ""))
        runs.append(speed(s6[f"o4s6_2b_{t}_{s}"], f"o4s8_2b_{t}_{s}", ""))
        if off:
            runs.append(speed(s6[f"o4s6_2b_{t}_{s}"], f"o4s8_2b_{t}_off_{s}", ", patches off", patches_off))
    plan = {"name": "obj4_step8",
            "description": "Objective 4, Step 8: Tier A in place: Qwen3.5-2B Q8_0 on CPU, 4 threads, the 70-case dev "
                           f"speed subset, 2 repeats, O3-final against O3-final + {a}"
                           + (" and the deployed candidate (patches off)" if off else "")
                           + ", alternating. On the laptop; close other apps; mains power. About "
                           f"{round(len(runs) * 0.3, 1)}-{round(len(runs) * 0.4, 1)} hours.",
            "base_dir": "..", "results_dir": "results_obj4", "defaults": {"port": 8080, "set": "all", "repeats": 1,
                                                                         "temperature": 0},
            "adapters": {"A": a, "patches_off": off}, "runs": runs}
    return plan


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["step7", "step8"])
    ap.add_argument("--tier-a", default=None, help="lora_2b, qlora_2b or none (default: from the verdicts)")
    ap.add_argument("--tier-b", default=None, help="lora_4b, qlora_4b or none (Step 7 only; default: from the verdicts)")
    a = ap.parse_args(argv)
    plan = build_step7(a.tier_a, a.tier_b) if a.step == "step7" else build_step8(a.tier_a)
    if not plan["runs"]:
        print("No adapter is carried on either tier: Step 7 has nothing to run.")
        return 0
    out = os.path.join(PLANS, f"obj4_{a.step}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=1)
    print(f"Wrote {out}: {len(plan['runs'])} runs. {plan['description']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
