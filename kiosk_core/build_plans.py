"""
Objective 5: write the Step 2 and Step 3 plans from O3-final's own run settings (harness/plans/obj3_step14.json and
obj3_step14_speed.json), so the runs differ from the evaluated configuration only in the engine settings.

    python kiosk_core\\build_plans.py

Step 2 (harness/plans/obj5_step2_parity.json): O3-final for both models on Vulkan, temperature 0, dev split: the
  dev speed subset (eval/o3_dev_speed_ids.json: 40 store questions, 30 tool cases) and the first 10 dev dialogues,
  each run with --engine legacy and then --engine core in the same sitting (alternating). 12 runs.
Step 3 (harness/plans/obj5_step3_stages.json): Tier A in place (2B Q8_0 on CPU, 4 threads), the same subset,
  2 repeats, the stage clock off and on (alternating), then the sequential stage policy on the first 10 cases of
  each set (1 repeat; reported, not decided here). 6 runs.
"""

import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLANS = os.path.join(ROOT, "harness", "plans")
DEV = {"rag": "eval/rag_cases.jsonl", "v12": "eval/eval_set_v1.2.jsonl"}


def load(name):
    with open(os.path.join(PLANS, name), encoding="utf-8") as f:
        return json.load(f)


def build():
    q = load("obj3_step14.json")
    sp = load("obj3_step14_speed.json")
    final = {r["name"]: r for r in q["runs"]}
    runs = []
    for m in ("2b", "4b"):
        for s in ("rag", "v12", "dlg"):
            for eng in ("legacy", "core"):
                r = copy.deepcopy(final[f"o3t_final_{m}_{s}"])
                r.update(name=f"o5s2_{m}_{s}_{eng}", split="dev", engine=eng,
                         config_label=r["config_label"] + f", engine {eng}")
                if s == "dlg":
                    r["limit"] = 10
                else:
                    r.update(eval=DEV[s], ids="eval/o3_dev_speed_ids.json")
                runs.append(r)
    step2 = {"name": "obj5_step2_parity",
             "description": "Objective 5, Step 2: the shared turn engine (kiosk_core) against the harness's own code. "
                            "O3-final, both models on Vulkan, dev speed subset and 10 dev dialogues, legacy then core "
                            "for each set. 12 runs, about 1-1.5 hours; resumable.",
             "base_dir": q.get("base_dir", ".."), "results_dir": "results_obj5", "defaults": q.get("defaults", {}),
             "runs": runs}
    tier_a = {r["name"]: r for r in sp["runs"]}
    runs3 = []
    for s in ("rag", "v12"):
        src = tier_a[f"o3tsp_a_2b_{s}_final"]
        fin = final[f"o3t_final_2b_{s}"]
        for tag, extra in (("off", {"stages": False}), ("on", {})):
            r = copy.deepcopy(fin)
            r.update({k: src[k] for k in ("backend", "server_exe", "server_args", "repeats")})
            r.update(name=f"o5s3_2b_{s}_{tag}", split="dev", eval=DEV[s], ids="eval/o3_dev_speed_ids.json",
                     engine="core", config_label="O3-final (Tier A timing), stage clock " + tag, **extra)
            runs3.append(r)
    for s in ("rag", "v12"):
        r = copy.deepcopy(next(x for x in runs3 if x["name"] == f"o5s3_2b_{s}_on"))
        r.update(name=f"o5s3_2b_{s}_seq", stage_policy="sequential", repeats=1, limit=10,
                 config_label="O3-final (Tier A timing), sequential stage policy")
        runs3.append(r)
    step3 = {"name": "obj5_step3_stages",
             "description": "Objective 5, Step 3: Tier A in place (2B Q8_0 on CPU, 4 threads), dev speed subset, "
                            "2 repeats: the stage clock off and on, alternating; then the sequential stage policy on "
                            "10 cases per set. On the laptop, other apps closed, mains power. About 2-2.5 hours.",
             "base_dir": sp.get("base_dir", ".."), "results_dir": "results_obj5", "defaults": sp.get("defaults", {}),
             "runs": runs3}
    runs4 = []
    for m in ("2b", "4b"):
        r = copy.deepcopy(final[f"o3t_final_{m}_v12"])
        r.update(name=f"o5s4_{m}_v12_stream", split="dev", eval=DEV["v12"], ids="eval/o3_dev_speed_ids.json",
                 engine="core", stream_check=True, config_label=r["config_label"] + ", streaming check")
        runs4.append(r)
    step4 = {"name": "obj5_step4_stream",
             "description": "Objective 5, Step 4: the streaming check. O3-final, both models on Vulkan, the 30 dev "
                            "tool cases of the speed subset; every model request is sent plain and streamed and the "
                            "two are compared. 2 runs, about 15-25 minutes; resumable.",
             "base_dir": q.get("base_dir", ".."), "results_dir": "results_obj5", "defaults": q.get("defaults", {}),
             "runs": runs4}
    runs7 = []
    for split in ("dev", "test"):
        for m in ("2b", "4b"):
            r = copy.deepcopy(final[f"o3t_final_{m}_rag"])
            r.pop("ids", None)
            r.update(name=f"o5s7_{m}_img_{split}", split=split, eval="eval/image_cases.jsonl", engine="core",
                     images=True, config_label=r["config_label"] + ", product images")
            runs7.append(r)
    step7 = {"name": "obj5_step7_images",
             "description": "Objective 5, Step 7: image requests (eval/image_cases.jsonl), O3-final with product "
                            "images, both models on Vulkan. Run the two dev runs first; the two test runs once, after "
                            "the dev runs meet the targets. 4 runs, a few minutes each; resumable.",
             "base_dir": q.get("base_dir", ".."), "results_dir": "results_obj5", "defaults": q.get("defaults", {}),
             "runs": runs7}
    for name, plan in (("obj5_step2_parity.json", step2), ("obj5_step3_stages.json", step3),
                       ("obj5_step4_stream.json", step4), ("obj5_step7_images.json", step7)):
        with open(os.path.join(PLANS, name), "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=1)
    return step2, step3, step4, step7


if __name__ == "__main__":
    a, b, c, d = build()
    print(f"Wrote obj5_step2_parity.json ({len(a['runs'])} runs), obj5_step3_stages.json ({len(b['runs'])} runs), "
          f"obj5_step4_stream.json ({len(c['runs'])} runs) and obj5_step7_images.json ({len(d['runs'])} runs)")
