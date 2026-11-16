"""
Objective 3, Step 1: the dev speed subset, timed in place on both tiers with 3 repeats.

    python eval\\build_o3_speed_ids.py

Writes eval/o3_dev_speed_ids.json: 40 dev retrieval questions (eval/rag_cases.jsonl) and 30 dev tool-mode cases
(eval/eval_set_v1.1.jsonl), drawn by stratified sampling (every subcategory of the retrieval questions and every
category of the tool cases keeps its share, at least one case each), seed 93. Dev only: the Objective 2 test speed
subsets (rag_speed_ids.json, speed_subset_ids.json) stay untouched for the final comparison.
One file holds both sets; run_eval.py keeps only the ids that exist in the eval file it is given.
"""

import json
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 93


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def stratified(cases, key, n, rng):
    groups = defaultdict(list)
    for c in cases:
        groups[key(c)].append(c)
    for g in groups.values():
        g.sort(key=lambda c: c["id"])
        rng.shuffle(g)
    total = len(cases)
    quota = {k: max(1, int(n * len(g) / total)) for k, g in groups.items()}
    # largest remainders fill the rest; trim the largest groups if the minimums overshoot
    rest = sorted(groups, key=lambda k: -(n * len(groups[k]) / total - int(n * len(groups[k]) / total)))
    i = 0
    while sum(quota.values()) < n:
        k = rest[i % len(rest)]
        if quota[k] < len(groups[k]):
            quota[k] += 1
        i += 1
    while sum(quota.values()) > n:
        k = max(quota, key=lambda k: quota[k])
        quota[k] -= 1
    picked = [c for k in sorted(groups) for c in groups[k][:quota[k]]]
    return sorted(c["id"] for c in picked), {k: quota[k] for k in sorted(groups)}


def main():
    rng = random.Random(SEED)
    rag = [c for c in load("rag_cases.jsonl") if c["split"] == "dev"]
    v11 = [c for c in load("eval_set_v1.1.jsonl") if c["split"] == "dev" and c["mode"] == "tools"]
    rag_ids, rag_q = stratified(rag, lambda c: c["subcategory"], 40, rng)
    v11_ids, v11_q = stratified(v11, lambda c: c["category"], 30, rng)
    out = {"version": "o3-step1", "seed": SEED, "split": "dev",
           "purpose": "Objective 3 speed subset: in-place timing on both tiers, 3 repeats",
           "rag_ids": rag_ids, "v11_ids": v11_ids, "ids": rag_ids + v11_ids,
           "strata": {"rag_subcategory": rag_q, "v11_category": v11_q}}
    path = os.path.join(HERE, "o3_dev_speed_ids.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(f"{path}: {len(rag_ids)} retrieval questions + {len(v11_ids)} tool cases")
    print("  retrieval strata:", rag_q)
    print("  tool strata:", v11_q)


if __name__ == "__main__":
    main()
