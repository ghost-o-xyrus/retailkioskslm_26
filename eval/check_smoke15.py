"""
Objective 3, Step 15: check the two Kaggle smoke jobs before the long ladder.

    python kaggle\\run_queue.py harness\\plans\\obj3_step15_smoke\\*.json
    python eval\\check_smoke15.py
    python eval\\check_smoke15.py --gpu       # the GPU smoke job

For every smoke run (harness/plans/obj3_step15_smoke/*.json, results in results_obj3/_smoke15):
  - it finished every case (3 per run), with no case error;
  - it ran on Kaggle CPU, with the settings of its ladder rung (the run_meta flags match the plan);
  - retrieval used the backend its rung needs (the Step 12 OpenVINO runtime for O3-final and the no-router
    run, optimum's OpenVINO otherwise),
    or none / oracle for the references;
  - the replies are real model replies (not empty), and the model answered within the time budget;
  - the job used the one fixed llama-server build, and that build came back to the laptop
    (kaggle/_llama_build/<tag>-avx2/llama-server), so the ladder jobs reuse it.
Prints PASS or FAIL per check and exits 1 if anything failed.
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FLAGS = ("loop_guard", "harness_tools", "discovery", "forced_answer", "entity_check", "staff_check", "verify_answers",
         "followup_retrieval", "focus_memory", "answer_length", "parallel_tools", "tool_view")


def main():
    gpu = "--gpu" in sys.argv[1:]          # the GPU smoke job (harness/plans/obj3_step15_gpu_smoke)
    bad = 0

    def check(ok, what):
        nonlocal bad
        bad += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {what}")

    plans = sorted(glob.glob(os.path.join(ROOT, "harness", "plans",
                                          "obj3_step15_gpu_smoke" if gpu else "obj3_step15_smoke", "*.json")))
    if not plans:
        sys.exit("no smoke plans: run python eval\\build_o3_ladder.py first")
    for pp in plans:
        plan = json.load(open(pp, encoding="utf-8"))
        res = os.path.join(ROOT, plan["results_dir"])
        job = "plan_" + os.path.splitext(os.path.basename(pp))[0]
        print(f"\n{job}")
        logp = os.path.join(ROOT, "kaggle", "_pulled", job, "job_log.txt")
        log = open(logp, encoding="utf-8", errors="replace").read() if os.path.exists(logp) else ""
        check(bool(log), f"job log pulled ({logp})")
        check("fixed build" in log, "llama-server: the fixed build (" +
              next((x.strip() for x in log.splitlines() if "llama-server:" in x), "no llama-server line") + ")")
        st = os.path.join(ROOT, "kaggle", "_pulled", job, "status.json")
        s = json.load(open(st, encoding="utf-8")) if os.path.exists(st) else {}
        check(s.get("ok") is True, f"job succeeded{'' if s.get('ok') else ': ' + str(s.get('error') or s.get('failed_command'))}"
              + (f" ({s.get('minutes')} min)" if s.get("minutes") else ""))
        for run in plan["runs"]:
            cfg = dict(plan.get("defaults", {}), **run)
            d = os.path.join(res, cfg["name"])
            print(f"  -- {cfg['name']}")
            mp = os.path.join(d, "run_meta.json")
            if not os.path.exists(mp):
                check(False, "results came back")
                continue
            meta = json.load(open(mp, encoding="utf-8"))
            recs = []
            for line in open(os.path.join(d, "cases.jsonl"), encoding="utf-8"):
                try:
                    recs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            ok = [r for r in recs if not r.get("error")]
            check(len(ok) >= cfg["limit"], f"{len(ok)} of {cfg['limit']} cases finished, {len(recs) - len(ok)} errors"
                  + (f" (first error: {next(r['error'] for r in recs if r.get('error'))[:160]})" if len(ok) < len(recs) else ""))
            want_m = "kaggle-gpu" if gpu else "kaggle-cpu"
            check((meta.get("machine") or {}).get("label") == want_m, f"ran on {want_m}")
            if gpu:
                slog = os.path.join(d, "server.log")
                txt = open(slog, encoding="utf-8", errors="replace").read() if os.path.exists(slog) else ""
                check(bool(re.search(r"offloaded \d+/\d+ layers to GPU|CUDA0|using device CUDA", txt)),
                      "the model ran on the GPU (server.log)")
            diff = [k for k in FLAGS if k in cfg and meta.get(k) != cfg[k]]
            check(not diff, "settings match the plan" + (f" (differ: {diff})" if diff else ""))
            r = meta.get("retrieval") or {}
            kb = r.get("knowledge_base") or {}
            want = "ovrt" if cfg.get("reranker_choice") else "openvino"     # Step 12 runtime, else optimum
            if cfg.get("retrieval") in ("none", "oracle"):
                check(r.get("condition") == cfg["retrieval"], f"retrieval {cfg['retrieval']} (reference)")
            else:
                got = kb.get("backend")
                check(got == want, f"retrieval backend {got} (expected {want})")
            if cfg.get("dialogues"):
                filled = sum(1 for x in ok if (x.get("dialogue") or {}).get("turns"))
                check(filled == len(ok), f"dialogues have kiosk turns ({filled}/{len(ok)})")
            else:
                empty = sum(1 for x in ok if not (x.get("final_reply") or "").strip())
                check(empty < len(ok), f"replies not all empty ({len(ok) - empty}/{len(ok)} with text)")
            ms = [((x.get("metrics") or {}).get("end_to_end_ms") or 0) / 1000 for x in ok]
            if ms:
                print(f"         per case on Kaggle: median {sorted(ms)[len(ms) // 2]:.0f} s, max {max(ms):.0f} s")
    cache = glob.glob(os.path.join(ROOT, "kaggle", "_llama_build", "*cuda*" if gpu else "*avx2*", "llama-server"))
    print()
    check(bool(cache), "the fixed llama-server build is on the laptop for the ladder jobs ("
          + (os.path.relpath(cache[0], ROOT) if cache else "kaggle/_llama_build missing") + ")")
    print(f"\n{'All checks passed: start the ladder.' if not bad else f'{bad} check(s) failed: send me this output.'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
