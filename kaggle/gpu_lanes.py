"""
Run a plan's GPU runs on a Kaggle T4 x2 session, two at a time: one lane per GPU (Objective 3, Step 15 ladder).

    python kaggle/gpu_lanes.py <plan> --server-exe <llama-server> --models-root /kaggle/input

Each run names its lane ("lane": 0 or 1, set by eval/build_o3_ladder.py). Lane i runs its runs in order with
CUDA_VISIBLE_DEVICES=i and its own port, through harness/run_plan.py (which resumes finished cases). Both lanes
start together; the output is printed with a [gpuN] prefix. Exits non-zero if either lane failed.
"""

import argparse
import json
import os
import subprocess
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--server-exe", required=True)
    ap.add_argument("--models-root", required=True)
    ap.add_argument("--backend", default="cuda")
    a = ap.parse_args(argv)
    with open(a.plan, encoding="utf-8") as f:
        plan = json.load(f)
    lanes = {}
    for r in plan["runs"]:
        cfg = dict(plan.get("defaults", {}), **r)
        if cfg.get("backend") == a.backend:
            lanes.setdefault(int(cfg.get("lane", 0)), []).append(cfg["name"])
    procs, codes = [], {}

    def pump(i, p):
        for line in p.stdout:
            sys.stdout.write(f"[gpu{i}] {line}")
            sys.stdout.flush()
        codes[i] = p.wait()

    threads = []
    for i, names in sorted(lanes.items()):
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(i))
        cmd = [sys.executable, os.path.join(ROOT, "harness", "run_plan.py"), a.plan, "--only", ",".join(names),
               "--only-backend", a.backend, "--server-exe", a.server_exe, "--models-root", a.models_root,
               "--port", str(8090 + i)]
        print(f"[gpu{i}] {len(names)} runs: {', '.join(names)}", flush=True)
        p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             errors="replace")
        procs.append(p)
        t = threading.Thread(target=pump, args=(i, p), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    bad = {i: c for i, c in codes.items() if c}
    print(f"lanes done: {codes}" + (f"; failed lanes: {sorted(bad)}" if bad else ""), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
