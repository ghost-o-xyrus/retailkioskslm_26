"""
Objective 4, Step 6: write the dev comparison plan (harness/plans/obj4_step6.json) from O3-final's own run settings.

    python finetune\\build_step6_plan.py

The O3-final settings are copied from the Step 14 plan (obj3_step14.json, runs o3t_final_*), so the baseline and
the adapter runs differ only in the adapter: dev split instead of test, the dev eval files, and a "lora" key. 20 runs,
all on Vulkan as in every quality run:
  Tier A (2B Q8_0): O3-final, + lora_2b, + qlora_2b
  Tier B (4B Q4_K_M): O3-final, + lora_4b (or + qlora_4b, if training had to fall back to it: the 4B adapter whose
  GGUF file is in finetune/adapters_gguf/, LoRA first; --tier-b-adapter overrides)
  each on dev store questions (151), tool cases (v1.2, 60), follow-ups (60) and dialogues (40).
"""

import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "harness", "plans", "obj3_step14.json")
OUT = os.path.join(ROOT, "harness", "plans", "obj4_step6.json")
DEV_EVAL = {"rag": "eval/rag_cases.jsonl", "v12": "eval/eval_set_v1.2.jsonl", "fup": "eval/rag_followups.jsonl",
            "dlg": None}
GGUF = os.path.join(HERE, "adapters_gguf")


def adapters(tier_b=None):
    if tier_b is None:
        tier_b = next((n for n in ("lora_4b", "qlora_4b") if os.path.exists(os.path.join(GGUF, f"{n}.gguf"))), "lora_4b")
    if tier_b not in ("lora_4b", "qlora_4b"):
        raise SystemExit(f"unknown Tier B adapter {tier_b!r} (lora_4b or qlora_4b)")
    return {"2b": [("base", None), ("lora", "lora_2b"), ("qlora", "qlora_2b")],
            "4b": [("base", None), (tier_b.split("_")[0], tier_b)]}


def build(tier_b=None):
    ADAPTERS = adapters(tier_b)
    src = json.load(open(SRC, encoding="utf-8"))
    final = {r["name"]: r for r in src["runs"] if r["name"].startswith("o3t_final_")}
    runs = []
    for s, ev in DEV_EVAL.items():                # set by set, so a partial plan already pairs up
        for m, ads in ADAPTERS.items():
            for tag, adapter in ads:
                r = copy.deepcopy(final[f"o3t_final_{m}_{s}"])
                r["name"] = f"o4s6_{m}_{tag}_{s}"
                r["split"] = "dev"
                if ev:
                    r["eval"] = ev
                if adapter:
                    r["lora"] = f"finetune/adapters_gguf/{adapter}.gguf"
                    r["config_label"] = r["config_label"] + f" + {adapter}"
                runs.append(r)
    plan = {"name": "obj4_step6",
            "description": "Objective 4, Step 6: dev comparison. O3-final with each adapter (route a: loaded next to "
                           "the deployed GGUF) against O3-final, same settings otherwise; both models on Vulkan as in "
                           "every quality run. Dev store questions, v1.2 tool cases, follow-ups and the 40 dev "
                           "dialogues. 20 runs, about 4 hours; resumable.",
            "base_dir": src.get("base_dir", ".."), "results_dir": "results_obj4", "defaults": src.get("defaults", {}),
            "runs": runs}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=1)
    return plan


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier-b-adapter", default=None, choices=["lora_4b", "qlora_4b"])
    p = build(ap.parse_args().tier_b_adapter)
    print(f"Wrote {OUT}: {len(p['runs'])} runs")
