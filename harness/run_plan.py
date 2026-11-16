"""
Run a staged plan unattended: for each run, start llama-server with the right model and flags,
wait until it is ready, run the eval cases, stop the server, and move on.

    python harness\\run_plan.py harness\\plans\\stage1_screen.json
    python harness\\run_plan.py harness\\plans\\stage1_screen.json --only qwen35-4b_q4_vulkan
    python harness\\run_plan.py harness\\plans\\stage1_screen.json --dry-run    # print commands only

Safe to stop and restart: finished runs are skipped, and an interrupted run resumes where it stopped.

Plan format (JSON):
{
  "name": "stage1_screen",
  "base_dir": "..",                     # folder that contains llama-cpu/, llama-vulkan/, models/ (relative to the plan file's project root;
                                        # the environment variable SLM_BASE_DIR, if set, is used instead)
  "defaults": {
    "server_exe": "llama-vulkan/llama-server.exe",
    "server_args": ["--jinja", "-c", "8192", "-ngl", "99"],
    "port": 8080,
    "eval": "eval/eval_set.jsonl", "set": "all", "split": "all", "repeats": 1, "temperature": 0
  },
  "runs": [
    {"name": "qwen35-4b_q4_vulkan", "model": "Qwen3.5-4B", "quant": "Q4_K_M", "backend": "vulkan",
     "model_path": "models/qwen3.5-4b/Qwen3.5-4B-Q4_K_M.gguf", "extra_server_args": ["--reasoning-budget", "0"]}
  ]
}
Optional plan key "results_dir" (default "results"). Objective 2 run keys: "retrieval", "fallback", "k_chunks",
"fallback_config", "data_dir", "retriever_threads", "context_view", "chunk_gate", "warmup", "gate_style", "rag_rule", "dedupe_shown" (passed to run_eval.py).
Objective 3 keys: "config_label" (e.g. "O3-B0"), "count_tokens" (false to skip /tokenize counts), "tool_view"
("json" or "compact"), "loop_guard" (true/false).
Objective 5 keys: "engine" ("legacy" or "core"), "stages" (false: no stage clock), "stage_policy" ("resident" or
"sequential").
Any default can be overridden per run. "server_cmd" (a full command list) replaces exe+args (used by tests).
"""

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from harness import run_eval  # noqa: E402


def port_free(port, host="127.0.0.1"):
    """True when nothing accepts connections on the port (a stale llama-server would answer for the wrong model)."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sk:
        sk.settimeout(1)
        return sk.connect_ex((host, port)) != 0


def eval_argv_for(cfg, port, eval_path, results_dir):
    """The harness/run_eval.py arguments for one plan run (also used by kiosk_core to build an app setup)."""
    eval_argv = ["--name", cfg["name"], "--model", cfg.get("model", ""), "--quant", cfg.get("quant", ""),
                 "--backend", cfg.get("backend", ""), "--url", f"http://127.0.0.1:{port}",
                 "--eval", eval_path, "--set", cfg.get("set", "all"), "--split", cfg.get("split", "all"),
                 "--repeats", str(cfg.get("repeats", 1)), "--temperature", str(cfg.get("temperature", 0)),
                 "--max-tokens", str(cfg.get("max_tokens", 512)), "--results-dir", results_dir]
    if cfg.get("ids"):
        eval_argv += ["--ids", os.path.join(ROOT, cfg["ids"])]
    if cfg.get("dialogues"):
        eval_argv += ["--dialogues", os.path.join(ROOT, cfg["dialogues"])]
    if cfg.get("category"):
        eval_argv += ["--category", cfg["category"]]
    if cfg.get("limit"):
        eval_argv += ["--limit", str(cfg["limit"])]
    if cfg.get("thinking"):
        eval_argv += ["--thinking"]
    # Objective 2 options (see run_eval.py); absent keys keep the Objective 1 behaviour
    for key, flag in (("retrieval", "--retrieval"), ("fallback", "--fallback"), ("k_chunks", "--k-chunks"),
                      ("fallback_config", "--fallback-config"), ("retriever_threads", "--retriever-threads"),
                      ("reranker_choice", "--reranker-choice")):
        if cfg.get(key) is not None:
            v = str(cfg[key])
            if key in ("fallback_config", "reranker_choice") and not os.path.isabs(v):
                v = os.path.join(ROOT, v)      # Step 8: a fallback.json inside the project
            eval_argv += [flag, v]
    if cfg.get("data_dir"):
        eval_argv += ["--data-dir", os.path.join(ROOT, cfg["data_dir"])]
    if cfg.get("corpus"):                     # Objective 4: the training catalogue's store information
        eval_argv += ["--corpus", os.path.join(ROOT, cfg["corpus"])]
    for key, flag in (("fake_retriever", "--fake-retriever"), ("chunk_gate", "--chunk-gate"), ("warmup", "--warmup"),
                      ("dedupe_shown", "--dedupe-shown"), ("loop_guard", "--loop-guard"),
                      ("harness_tools", "--harness-tools"), ("store_one_round", "--store-one-round"),
                      ("staff_guard", "--staff-guard"), ("entity_check", "--entity-check"),
                      ("staff_check", "--staff-check"), ("followup_retrieval", "--followup-retrieval"),
                      ("focus_memory", "--focus-memory"), ("answer_length", "--answer-length"),
                      ("parallel_tools", "--parallel-tools"), ("stream_check", "--stream-check"), ("images", "--images"), ("ordinal_refs", "--ordinal-refs")):
        if cfg.get(key):
            eval_argv += [flag]
    if cfg.get("count_tokens") is False:
        eval_argv += ["--no-count-tokens"]
    if cfg.get("stages") is False:           # Objective 5, Step 3: the stage clock off (its cost is measured)
        eval_argv += ["--no-stages"]
    for key, flag in (("context_view", "--context-view"), ("gate_style", "--gate-style"), ("rag_rule", "--rag-rule"),
                      ("config_label", "--config-label"), ("tool_view", "--tool-view"),
                      ("discovery", "--discovery"), ("forced_answer", "--forced-answer"),
                      ("tools_prompt", "--tools-prompt"), ("verify_answers", "--verify-answers"),
                      ("engine", "--engine"), ("stage_policy", "--stage-policy")):
        if cfg.get(key):
            eval_argv += [flag, cfg[key]]

    return eval_argv


def is_complete(results_dir, name, expected):
    meta = os.path.join(results_dir, name, "run_meta.json")
    path = os.path.join(results_dir, name, "cases.jsonl")
    if not (os.path.exists(meta) and os.path.exists(path)):
        return False
    ok = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not r.get("error"):
                ok.add((r["id"], r["repeat"]))
    return len(ok) >= expected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--only", default=None, help="Comma-separated run names to execute")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--results-dir", default=None, help="Default: the plan's results_dir, else results/")
    ap.add_argument("--only-backend", default=None,
                    help="Run only runs whose backend is this (e.g. cpu on Kaggle; Vulkan runs stay on the laptop)")
    ap.add_argument("--server-exe", default=None,
                    help="llama-server to use for every run instead of the plan's (e.g. a Linux build on Kaggle)")
    ap.add_argument("--port", type=int, default=None,
                    help="Port for every run instead of the plan's (two runs at once, one per GPU, need two)")
    ap.add_argument("--models-root", default=None,
                    help="Find each model file by name anywhere under this folder (e.g. /kaggle/input)")
    a = ap.parse_args()
    model_index = {}
    if a.models_root:
        for dp, _, fs in os.walk(a.models_root):
            for fn in fs:
                if fn.endswith(".gguf"):
                    model_index.setdefault(fn, os.path.join(dp, fn))

    with open(a.plan, encoding="utf-8") as f:
        plan = json.load(f)
    a.results_dir = a.results_dir or os.path.join(ROOT, plan.get("results_dir", "results"))
    base = os.path.abspath(os.environ.get("SLM_BASE_DIR") or os.path.join(ROOT, plan.get("base_dir", "..")))
    only = set(a.only.split(",")) if a.only else None
    summary = []

    for run in plan["runs"]:
        cfg = dict(plan.get("defaults", {}))
        cfg.update(run)
        name = cfg["name"]
        if only and name not in only:
            continue
        if a.only_backend and cfg.get("backend") != a.only_backend:
            print(f"== {name}: backend {cfg.get('backend')}, skipped (--only-backend {a.only_backend})")
            continue
        port = int(a.port or cfg.get("port", 8080))
        eval_path = os.path.join(ROOT, cfg.get("eval", "eval/eval_set.jsonl"))
        if cfg.get("dialogues"):
            cases = run_eval.load_dialogues(os.path.join(ROOT, cfg["dialogues"]), cfg.get("split", "all"),
                                            os.path.join(ROOT, cfg["ids"]) if cfg.get("ids") else None, cfg.get("limit"))
        else:
            cases = run_eval.load_cases(eval_path, cfg.get("set", "all"), cfg.get("split", "all"),
                                        os.path.join(ROOT, cfg["ids"]) if cfg.get("ids") else None,
                                        cfg.get("category"), cfg.get("limit"))
        expected = len(cases) * int(cfg.get("repeats", 1))
        if is_complete(a.results_dir, name, expected):
            print(f"== {name}: already complete, skipping")
            summary.append((name, "skipped (complete)"))
            continue

        if cfg.get("server_cmd"):
            cmd = list(cfg["server_cmd"]) + ["--port", str(port)]
        else:
            exe = a.server_exe or os.path.join(base, cfg["server_exe"])
            model = os.path.join(base, cfg["model_path"])
            if a.models_root:
                model = model_index.get(os.path.basename(cfg["model_path"]), model)
            if "*" in model:                 # Step 13b: "models/qwen3.5-4b-mtp/*Q4_K_M.gguf" (name as downloaded)
                import glob
                model = (sorted(glob.glob(model)) or [model])[0]
            if not os.path.exists(model):  # checked on dry runs too, so a wrong path shows up before the real run
                print(f"== {name}: model file not found: {os.path.abspath(model)}")
                summary.append((name, "MODEL MISSING - fix model_path"))
                continue
            extra = [str(x).replace("{base}", base) for x in cfg.get("extra_server_args", [])]
            # Step 13b: a draft model ("-md {base}/models/...") must exist too
            drafts = [extra[i + 1] for i, x in enumerate(extra[:-1]) if x in ("-md", "--model-draft", "--spec-draft-model")]
            if any(not os.path.exists(d) for d in drafts):
                print(f"== {name}: draft model file not found: {', '.join(os.path.abspath(d) for d in drafts)}")
                summary.append((name, "DRAFT MODEL MISSING"))
                continue
            # Objective 4 (route a): a GGUF LoRA adapter loaded next to the deployed model file
            if cfg.get("lora"):
                lora = os.path.join(ROOT, cfg["lora"])      # inside the project (finetune/adapters_gguf/...)
                if not os.path.exists(lora):
                    print(f"== {name}: LoRA adapter file not found: {os.path.abspath(lora)}")
                    summary.append((name, "LORA ADAPTER MISSING"))
                    continue
                scale = cfg.get("lora_scale")
                extra += ["--lora", lora] if scale is None else ["--lora-scaled", lora, str(scale)]
            cmd = [exe, "-m", model, "--host", "127.0.0.1", "--port", str(port)] + list(cfg.get("server_args", [])) \
                + extra

        eval_argv = eval_argv_for(cfg, port, eval_path, a.results_dir)
        print(f"\n== {name}\n   server: {' '.join(cmd)}\n   cases: {len(cases)} x {cfg.get('repeats', 1)}")
        if a.dry_run:
            summary.append((name, "dry run"))
            continue

        if not port_free(port):
            print(f"== {name}: something is already listening on port {port} (an earlier llama-server?). Stop it "
                  f"first (Task Manager: llama-server.exe), or use --port. Not running, so this run cannot be "
                  f"answered by the wrong model.")
            summary.append((name, f"port {port} busy"))
            continue
        out_dir = os.path.join(a.results_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        log = open(os.path.join(out_dir, "server.log"), "a", encoding="utf-8")
        log.write(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} {' '.join(cmd)}\n")
        log.flush()
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
        try:
            ready, t_wait = False, time.time()
            while time.time() - t_wait < int(cfg.get("load_timeout", 300)):
                if proc.poll() is not None:          # the server quit (bad option, model it cannot load...)
                    break
                if run_eval.wait_for_server(f"http://127.0.0.1:{port}", timeout_s=5):
                    ready = True
                    break
            if ready and proc.poll() is not None:     # answered by some other server; ours has quit
                ready = False
            if ready and cfg.get("lora") and not a.dry_run:
                try:
                    la = run_eval.http_json(f"http://127.0.0.1:{port}/lora-adapters", timeout=10)
                    if not la:
                        ready = False
                        log.write("\n[run_plan] the adapter was not loaded\n")
                except Exception:  # noqa: BLE001 - an older server without the endpoint
                    pass
            if not ready:
                log.flush()
                try:
                    with open(os.path.join(out_dir, "server.log"), encoding="utf-8", errors="replace") as f:
                        tail = [x.rstrip() for x in f.readlines()[-15:]]
                except OSError:
                    tail = []
                print(f"   server did not become ready; last lines of {out_dir}/server.log:")
                for x in tail:
                    print("     | " + x)
                summary.append((name, "server failed to start"))
                continue
            code = run_eval.main(eval_argv, server_pid=proc.pid)
            summary.append((name, "ok" if code == 0 else f"finished with errors (code {code})"))
        except KeyboardInterrupt:
            print("\nInterrupted. Rerun the same command to resume.")
            summary.append((name, "interrupted"))
            break
        except Exception:  # noqa: BLE001 - one broken run must not hide the others (the summary says which)
            import traceback
            traceback.print_exc()
            summary.append((name, "FAILED (traceback above)"))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                proc.kill()
            log.close()
            time.sleep(3)  # let the OS release the port and memory before the next model

    print("\nPlan summary:")
    for name, status in summary:
        print(f"  {name:40s} {status}")
    return 1 if any(st.startswith(("FAILED", "server failed", "MODEL", "DRAFT", "LORA")) or "errors" in st
                    for _, st in summary) else 0


if __name__ == "__main__":
    sys.exit(main())
