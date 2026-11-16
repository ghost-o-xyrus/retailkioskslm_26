"""
Objective 3, Step 15: the ablation ladder on the test set O3-T, written as Kaggle CPU plan jobs.

    python eval\\build_o3_ladder.py            # the ladder jobs (and the smoke jobs)
    python kaggle\\run_queue.py harness\\plans\\obj3_step15_smoke\\*.json   # first: 2 short jobs, about 30 min
    python eval\\check_smoke15.py                                           # every check must pass
    python kaggle\\run_queue.py harness\\plans\\obj3_step15\\*.json

The ladder adds the changes Steps 2-13 kept, in the order they were kept, so each rung answers one question
(amended before any ladder run, from the pre-registered R1-R6 to the changes actually kept: the re-ranker trial,
cited answers and prompt v1.2 were not kept, and the tool output and loop guard came before the router):

    b0   O3-B0: Objective 2's deployed setup (always retrieve, soft fallback)           baseline
    r1   + tool output v2 and loop guard (Step 3)                                        honest, compact outputs
    r2   + intent router; only store questions are retrieved (Step 4)                   tool-case regression
    r3   + harness-run tools, guided discovery, forced-answer recovery (Steps 5-7)      rounds, dialogues
    r4   + hard fallback, entity check, staff check (Step 8)                            unanswerable questions
    r5   + answer check, follow-up retrieval and product in focus (Steps 10-11)         grounding, follow-ups
    r6   + retrieval and generation speed work (Steps 12-13) = O3-final                 speed, quality unchanged
    nr   O3-final without the router (every message on the always-retrieve path)       the router's own effect
    ref  references: oracle cards on store questions; no retrieval on tool cases (Stage 3), for two criteria

Each rung's settings are copied from the dev run that kept it (r6 from the Step 14 run); only the cases (the test
split), the machine (Kaggle CPU, 4 threads) and the run name change. O3-B0 and O3-final are rerun on Kaggle too,
so the whole ladder is paired on one machine; their Step 14 runs (laptop, Vulkan) give a cross-check.
Sets per rung and model: store questions (463), tool cases (192), follow-ups (60), dialogues (60).
One Kaggle job per rung, model and part (store questions; the other three sets), so each fits in a session;
a job that runs out of time packs what it has and is pushed again (it resumes).
Every job uses one llama-server build: built from source at the laptop's release tag with fixed AVX2 flags, once,
then reused (kaggle/kernel_main.py, get_llama_fixed), so no rung differs from another by build or CPU features.
Writes harness/plans/obj3_step15/*.json (the jobs), harness/plans/obj3_step15_ladder.json (every run) and
harness/plans/obj3_step15_smoke/*.json: two short jobs (3 cases per run, results in results_obj3/_smoke15) that
cover every kind of run in the ladder, to check the whole path on Kaggle before the long jobs.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLANS = os.path.join(ROOT, "harness", "plans")
OUT = os.path.join(PLANS, "obj3_step15")

RUNGS = [  # (rung, source run of its settings, with {m} for the model; None = built below)
    ("b0", "obj3_step14.json", "o3t_b0_{m}_rag", "O3-B0"),
    ("r1", "obj3_step3.json", "o3s3_{m}_rag_s3", "R1: + tool output v2, loop guard"),
    ("r2", "obj3_step4.json", "o3s4_{m}_rag_s4", "R2: + router"),
    ("r3", "obj3_step7.json", "o3s7a_{m}_rag", "R3: + harness tools, discovery, forced answers"),
    ("r4", "obj3_step8.json", "o3s8_{m}_rag", "R4: + fallback, entity check, staff check"),
    ("r5", "obj3_step11b.json", "o3s11b_{m}_fup", "R5: + answer check, follow-up retrieval"),
    ("r6", "obj3_step14.json", "o3t_final_{m}_rag", "R6 = O3-final"),
    ("nr", "obj3_step14.json", "o3t_final_{m}_rag", "O3-final without router"),
]
KAGGLE = {"kaggle_max_minutes": 650, "kaggle_llama_build": "fixed", "kaggle_llama_tag": "b12110"}
SMOKE = {"2b": [("r1", "rag"), ("r3", "dlg"), ("r5", "fup"), ("r6", "rag"), ("nr", "v12"), ("ref", "none")],
         "4b": [("r6", "rag"), ("r6", "fup"), ("r6", "dlg"), ("b0", "v12"), ("r2", "v12"), ("ref", "oracle")]}
ORDER = ["r6", "b0", "ref", "r5", "r4", "r3", "r2", "r1", "nr"]       # push order: the cross-check first
SETS = {"rag": "o3t_b0_{m}_rag", "v12": "o3t_b0_{m}_v12", "fup": "o3t_b0_{m}_fup", "dlg": "o3t_b0_{m}_dlg"}
# fields that describe where and on what a run happens; everything else is the configuration
WHERE = {"name", "eval", "split", "set", "ids", "dialogues", "config_label", "model", "quant", "model_path",
         "server_exe", "server_args", "extra_server_args", "backend", "port", "repeats", "temperature", "limit",
         "category", "results_dir"}
CPU = {"backend": "cpu", "server_exe": "llama-cpu/llama-server.exe",
       "server_args": ["--jinja", "-c", "8192", "-np", "1", "-ngl", "0", "-t", "4"],
       "extra_server_args": ["--reasoning-budget", "0"]}
MODELS = ("2b", "4b")


def runs_of(plan):
    with open(os.path.join(PLANS, plan), encoding="utf-8") as f:
        p = json.load(f)
    return {r["name"]: dict(p.get("defaults", {}), **r) for r in p["runs"]}


def config(src):
    return {k: v for k, v in src.items() if k not in WHERE}


def build():
    s14 = runs_of("obj3_step14.json")
    by_plan = {}
    jobs = {}
    for rung, plan, src_name, label in RUNGS:
        src = by_plan.setdefault(plan, runs_of(plan))
        for m in MODELS:
            cfg = config(src[src_name.format(m=m)])
            if rung == "nr":
                cfg["retrieval"] = "always"            # no router: every message takes the Objective 2 path
            for s, where_name in SETS.items():
                w = s14[where_name.format(m=m)]
                run = {k: w[k] for k in ("model", "quant", "model_path", "eval", "split", "dialogues") if k in w}
                run.update(CPU, name=f"o3l_{rung}_{m}_{s}", config_label=f"{label} ({'Tier A' if m == '2b' else 'Tier B'})")
                run.update(cfg)
                part = "rag" if s == "rag" else "rest"
                jobs.setdefault((rung, m, part), []).append(run)
    for m in MODELS:   # the rebuilt baseline and final must equal the Step 14 settings exactly
        for rung, s14name in (("r6", "o3t_final_{m}_{s}"), ("b0", "o3t_b0_{m}_{s}")):
            for s in SETS:
                mine = next(r for r in jobs[(rung, m, "rag" if s == "rag" else "rest")] if r["name"].endswith("_" + s))
                theirs = s14[s14name.format(m=m, s=s)]
                a, b = config(mine), config(theirs)
                diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
                if diff:
                    raise SystemExit(f"{mine['name']}: settings differ from {theirs['name']} in {diff}")
    for m in MODELS:   # references, as in Step 1: the B0 settings with oracle cards, and with no retrieval at all
        b0r, b0t = s14[f"o3t_b0_{m}_rag"], s14[f"o3t_b0_{m}_v12"]
        o = {k: b0r[k] for k in ("model", "quant", "model_path", "eval", "split")}
        o.update(CPU, name=f"o3l_ref_{m}_oracle", config_label="ref-oracle", retrieval="oracle",
                 context_view="compact", rag_rule="rag_always_rule_b", dedupe_shown=True, warmup=True)
        n = {k: b0t[k] for k in ("model", "quant", "model_path", "eval", "split")}
        n.update(CPU, name=f"o3l_ref_{m}_none", config_label="ref-none (Stage 3)", retrieval="none", warmup=True)
        jobs[("ref", m, "all")] = [o, n]
    return jobs


GPU = {"backend": "cuda", "server_exe": "llama-cuda/llama-server",
       "server_args": ["--jinja", "-c", "8192", "-np", "1", "-ngl", "99"],
       "extra_server_args": ["--reasoning-budget", "0"]}
GPU_KAGGLE = {"kaggle_backend": "cuda", "kaggle_max_minutes": 650, "kaggle_llama_build": "fixed-cuda",
              "kaggle_llama_tag": "b12110"}
LANE = {("4b", "rag"): 0, ("2b", "v12"): 0, ("2b", "fup"): 0, ("2b", "dlg"): 0,
        ("2b", "rag"): 1, ("4b", "v12"): 1, ("4b", "fup"): 1, ("4b", "dlg"): 1}
GPU_SMOKE = [("r6", "4b", "rag", 0), ("b0", "4b", "v12", 0), ("r1", "2b", "rag", 1), ("r3", "2b", "dlg", 1)]


def write_gpu(every):
    """The same ladder on Kaggle GPU sessions (T4 x2, one run per GPU at a time): one job per rung, 8 runs in two
    lanes (eval/step15_ladder.py --gpu reads it). Amended before any GPU run: the CPU ladder was too slow, so the
    ladder moves to the GPU whole, O3-B0 and O3-final included, and stays paired on one machine and one build.
    The CPU runs already made (O3-B0, O3-final, the references, R5 store questions) are kept: the references pair
    with the CPU O3-final, and the CPU and GPU O3-B0 and O3-final give a cross-check."""
    gdir = os.path.join(PLANS, "obj3_step15_gpu")
    sdir = os.path.join(PLANS, "obj3_step15_gpu_smoke")
    for d in (gdir, sdir):
        os.makedirs(d, exist_ok=True)
        for fn in os.listdir(d):
            if fn.endswith(".json"):
                os.remove(os.path.join(d, fn))
    by = {r["name"]: r for r in every}
    defaults = {"port": 8080, "set": "all", "repeats": 1, "temperature": 0}
    order = ["r6", "b0", "r5", "r4", "r3", "r2", "r1", "nr"]
    for i, rung in enumerate(order, 1):
        runs = []
        for m in MODELS:
            for s_ in SETS:
                src = by[f"o3l_{rung}_{m}_{s_}"]
                runs.append(dict(src, **GPU, name=f"o3g_{rung}_{m}_{s_}", lane=LANE[(m, s_)],
                                 config_label=src["config_label"] + " [GPU]"))
        plan = {"name": f"obj3_step15_gpu_{rung}", "description": f"Step 15 ladder on Kaggle T4 x2: {LABEL_OF[rung]}.",
                "base_dir": "..", "results_dir": "results_obj3", **GPU_KAGGLE, "defaults": defaults, "runs": runs}
        with open(os.path.join(gdir, f"o3g_{i:02d}_{rung}.json"), "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=1, ensure_ascii=False)
    runs = [dict(by[f"o3l_{rung}_{m}_{s_}"], **GPU, name=f"o3gs_{rung}_{m}_{s_}", lane=lane, limit=3)
            for rung, m, s_, lane in GPU_SMOKE]
    plan = {"name": "obj3_step15_gpu_smoke", "description": "Step 15 GPU smoke test: 3 cases per run, both GPUs; "
            "also builds the CUDA llama-server once for the ladder.", "base_dir": "..",
            "results_dir": "results_obj3/_smoke15g", **GPU_KAGGLE, "kaggle_max_minutes": 150, "defaults": defaults,
            "runs": runs}
    with open(os.path.join(sdir, "o3gs.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=1, ensure_ascii=False)
    print(f"Wrote {len(order)} GPU jobs to {gdir} and the GPU smoke job to {sdir}")


LABEL_OF = {r: lab for r, _, _, lab in RUNGS}


def main():
    jobs = build()
    os.makedirs(OUT, exist_ok=True)
    for fn in os.listdir(OUT):
        if fn.endswith(".json"):
            os.remove(os.path.join(OUT, fn))
    every = []
    keys = sorted(jobs, key=lambda k: (ORDER.index(k[0]), k[2] != "rag", k[1]))
    for i, (rung, m, part) in enumerate(keys, 1):
        runs = jobs[(rung, m, part)]
        every += runs
        plan = {"name": f"obj3_step15_{rung}_{m}_{part}",
                "description": f"Objective 3, Step 15 ladder on O3-T, Kaggle CPU: {runs[0]['config_label']}, "
                               f"{', '.join(r['name'] for r in runs)}.",
                "base_dir": "..", "results_dir": "results_obj3", **KAGGLE,
                "defaults": {"port": 8080, "set": "all", "repeats": 1, "temperature": 0}, "runs": runs}
        with open(os.path.join(OUT, f"o3l_{i:02d}_{rung}_{m}_{part}.json"), "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=1, ensure_ascii=False)
    with open(os.path.join(PLANS, "obj3_step15_ladder.json"), "w", encoding="utf-8") as f:
        json.dump({"name": "obj3_step15_ladder", "description": "Every run of the Step 15 ladder (Kaggle CPU); "
                   "the jobs are in obj3_step15/.", "base_dir": "..", "results_dir": "results_obj3",
                   "defaults": {"port": 8080, "set": "all", "repeats": 1, "temperature": 0}, "runs": every},
                  f, indent=1, ensure_ascii=False)
    smoke_dir = os.path.join(PLANS, "obj3_step15_smoke")
    os.makedirs(smoke_dir, exist_ok=True)
    for fn in os.listdir(smoke_dir):
        if fn.endswith(".json"):
            os.remove(os.path.join(smoke_dir, fn))
    by_name = {r["name"]: r for r in every}
    for m, picks in SMOKE.items():
        runs = []
        for rung, s in picks:
            src = by_name[f"o3l_{rung}_{m}_{s}"]
            runs.append(dict(src, name=src["name"].replace("o3l_", "o3ls_", 1), limit=3))
        plan = {"name": f"obj3_step15_smoke_{m}", "description": f"Step 15 smoke test on Kaggle ({m}): 3 cases per run.",
                "base_dir": "..", "results_dir": "results_obj3/_smoke15", **KAGGLE, "kaggle_max_minutes": 120,
                "defaults": {"port": 8080, "set": "all", "repeats": 1, "temperature": 0}, "runs": runs}
        with open(os.path.join(smoke_dir, f"o3ls_{m}.json"), "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=1, ensure_ascii=False)
    print(f"Wrote {len(keys)} Kaggle jobs ({len(every)} runs) to {OUT}, and 2 smoke jobs to {smoke_dir}")
    write_gpu(every)
    print("Next: python kaggle\\run_queue.py harness\\plans\\obj3_step15_smoke\\*.json, then eval\\check_smoke15.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
