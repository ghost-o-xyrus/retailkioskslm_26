"""
Objective 4, Step 5: turn each adapter into a GGUF LoRA file and check it on the deployed model file with
llama-server, before any eval (route (a): the adapter is loaded next to the deployed GGUF; the deployed weights are
not changed). Run on Kaggle's CPU by kaggle_step5.sh; nothing here needs a GPU.

    python finetune/step5_check.py --server /tmp/llama/llama-server --convert /tmp/o4/llama.cpp/convert_lora_to_gguf.py \
        --adapters lora_2b qlora_2b lora_4b qlora_4b      # a missing adapter is skipped

For each adapter (finetune/adapters/<name>/, base model and tier from its train_log.json):
  1. convert: llama.cpp's convert_lora_to_gguf.py (the laptop's llama.cpp build), f16 ->
     finetune/adapters_gguf/<name>.gguf
  2. load: llama-server with the tier's deployed GGUF, the adapter loaded but not applied (--lora-init-without-apply);
     the adapter must be listed by /lora-adapters and the log must show no LoRA error
  3. template: for N examples, the prompt llama-server builds from the request as the harness sends it
     (/apply-template, tools and thinking-off included) must equal the training prompt (prepare_sft.render with the
     model's Hugging Face tokenizer). Rule: at least 95% identical.
  4. scale 0: with the adapter at scale 0, greedy replies must equal plain decoding (no adapter) as often as plain
     decoding agrees with itself (two runs on a server without the adapter).
  5. scale 1 (a look, not a rule): how often the reply equals the training answer, how often a tool-call answer
     comes back as a real tool call, printed tool-call markup, and whether replies end by themselves (finish "stop").
Writes finetune/adapters_gguf/step5_report.md and step5_report.json.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import prepare_sft as P  # noqa: E402

OUT = os.path.join(HERE, "adapters_gguf")
PRINTED = re.compile(r"<tool_call>|<function=|\"name\"\s*:\s*\"(search_catalogue|get_product_details|check_inventory|"
                     r"get_alternatives|call_staff|compare_products)")


def http(url, body=None, timeout=900):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"},
                                 method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def supports(exe, flag, _seen={}):
    """Whether this llama-server build knows a flag (older builds stop on an unknown one)."""
    if exe not in _seen:
        try:
            _seen[exe] = subprocess.run([exe, "--help"], capture_output=True, text=True, timeout=60).stdout
        except Exception:  # noqa: BLE001
            _seen[exe] = ""
    return flag in _seen[exe]


class Server:
    def __init__(self, exe, model, port, lora=None, threads=4, log=None):
        cmd = [exe, "-m", model, "--host", "127.0.0.1", "--port", str(port), "-c", "8192", "-np", "1", "-t", str(threads),
               "--jinja"] + (["--reasoning-budget", "0"] if supports(exe, "--reasoning-budget") else [])
        if lora:
            cmd += ["--lora", lora, "--lora-init-without-apply"]
        self.url, self.log = f"http://127.0.0.1:{port}", log
        self.fh = open(log, "w", encoding="utf-8")
        self.proc = subprocess.Popen(cmd, stdout=self.fh, stderr=subprocess.STDOUT)
        for _ in range(240):
            if self.proc.poll() is not None:
                break
            try:
                if http(self.url + "/health", timeout=5).get("status") == "ok":
                    return
            except Exception:  # noqa: BLE001
                pass
            time.sleep(2)
        self.stop()
        raise RuntimeError("llama-server did not start:\n" + "".join(open(log, encoding="utf-8").readlines()[-25:]))

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.fh.close()

    def chat(self, ex, tools, lora_scale=None, cache=True):
        body = {"messages": ex["messages"], "temperature": 0, "seed": 42, "max_tokens": 120, "cache_prompt": cache,
                "chat_template_kwargs": {"enable_thinking": False}}
        if tools:
            body["tools"] = tools
        if ex.get("tool_choice"):
            body["tool_choice"] = ex["tool_choice"]
        if lora_scale is not None:
            body["lora"] = [{"id": 0, "scale": lora_scale}]
        r = http(self.url + "/v1/chat/completions", body)
        m = r["choices"][0]["message"]
        calls = [(c["function"]["name"], c["function"].get("arguments")) for c in m.get("tool_calls") or []]
        return {"content": (m.get("content") or "").strip(), "calls": calls, "finish": r["choices"][0].get("finish_reason")}


def same(a, b):
    return a["content"] == b["content"] and a["calls"] == b["calls"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", required=True)
    ap.add_argument("--convert", required=True)
    ap.add_argument("--adapters", nargs="+", required=True)
    ap.add_argument("--models", default="/tmp/o4/models", help="folder with the deployed GGUF files")
    ap.add_argument("--n", type=int, default=8, help="examples per adapter for the reply checks")
    ap.add_argument("--n-template", type=int, default=40)
    a = ap.parse_args(argv)
    from transformers import AutoTokenizer
    os.makedirs(OUT, exist_ok=True)
    base_file = {"A": os.path.join(a.models, "Qwen3.5-2B-Q8_0.gguf"), "B": os.path.join(a.models, "Qwen3.5-4B-Q4_K_M.gguf")}
    tools_by_key = json.load(open(os.path.join(HERE, "examples", "tools.json"), encoding="utf-8"))
    report, L = {}, ["# Step 5: adapters on the deployed model files (route a)", ""]
    for name in a.adapters:
        src = os.path.join(HERE, "adapters", name)
        if not os.path.exists(os.path.join(src, "adapter_model.safetensors")):
            # the job lists both 4B adapters; training makes lora_4b, or qlora_4b if it had to fall back
            print(f"{name}: not trained (no adapter_model.safetensors); skipped", flush=True)
            continue
        log = json.load(open(os.path.join(src, "train_log.json"), encoding="utf-8"))
        tier, base_id = log["tier"], log["model"]
        res = {"tier": tier, "base": base_id}
        report[name] = res
        sec = len(L)
        L += [f"## {name} (Tier {tier}, {base_id}{', QLoRA' if log.get('qlora') else ''})", ""]
        # 1. convert
        dst = os.path.join(OUT, f"{name}.gguf")
        r = subprocess.run([sys.executable, a.convert, src, "--base-model-id", base_id, "--outtype", "f16",
                            "--outfile", dst], capture_output=True, text=True)
        res["convert_ok"] = r.returncode == 0 and os.path.exists(dst)
        if not res["convert_ok"]:
            L += ["Conversion FAILED:", "", "```", (r.stdout + r.stderr)[-3000:], "```", ""]
            continue
        res["gguf_mb"] = round(os.path.getsize(dst) / 1e6, 1)
        L.append(f"- converted: {res['gguf_mb']} MB")
        # examples: the held-out questions first (never trained on), then others
        exs = P.load_jsonl(os.path.join(HERE, "examples", f"tier{tier}_final.jsonl"))
        exs = sorted(exs, key=lambda e: (not P.held_out(e["case_id"]), e["id"]))
        try:
            tok = AutoTokenizer.from_pretrained(src)          # saved with the adapter by train_lora.py
        except Exception:  # noqa: BLE001
            tok = AutoTokenizer.from_pretrained(base_id)
        tok = getattr(tok, "tokenizer", tok)
        plain, lsrv = None, None
        try:
            # 2. load
            print(f"  {name}: converted; loading it next to {os.path.basename(base_file[tier])}", flush=True)
            lsrv = Server(a.server, base_file[tier], 8301, lora=dst, log=os.path.join(OUT, f"{name}_server.log"))
            listed = http(lsrv.url + "/lora-adapters")
            text = open(lsrv.log, encoding="utf-8", errors="replace").read()
            res["load_ok"] = bool(listed) and not re.search(r"(failed to (load|apply) lora|lora.*error)", text, re.I)
            n_loaded = re.search(r"loaded (\d+) tensors from lora", text, re.I)
            L.append(f"- loads on {os.path.basename(base_file[tier])}: {'yes' if res['load_ok'] else 'NO'}"
                     + (f" ({n_loaded.group(1)} tensors)" if n_loaded else "") + f"; /lora-adapters: {listed}")
            # 3. template
            match, first_diff = 0, None
            sample = exs[:a.n_template]
            for ex in sample:
                tools = tools_by_key.get(ex["tools"]) if ex.get("tools") else None
                body = {"messages": ex["messages"], "chat_template_kwargs": {"enable_thinking": False}}
                if tools:
                    body["tools"] = tools
                try:
                    srv_prompt = http(lsrv.url + "/apply-template", body)["prompt"]
                    hf_prompt, _, _ = P.render(tok, ex, tools)
                except Exception as e:  # noqa: BLE001
                    res.setdefault("template_errors", []).append(f"{ex['id']}: {str(e)[:200]}")
                    continue
                if hf_prompt == srv_prompt:
                    match += 1
                elif first_diff is None:
                    i = next((k for k, (x, y) in enumerate(zip(hf_prompt or "", srv_prompt)) if x != y),
                             min(len(hf_prompt or ""), len(srv_prompt)))
                    first_diff = {"example": ex["id"], "training": (hf_prompt or "")[max(0, i - 120):i + 120],
                                  "server": srv_prompt[max(0, i - 120):i + 120]}
            res["template_identical"] = [match, len(sample)]
            res["template_ok"] = match >= 0.95 * len(sample)
            L.append(f"- template: {match}/{len(sample)} prompts identical (rule: at least 95%) -> "
                     f"{'met' if res['template_ok'] else 'NOT met'}")
            if res.get("template_errors"):
                L.append(f"  ({len(res['template_errors'])} prompts could not be built, counted as not identical; "
                         f"first: {res['template_errors'][0]})")
            if first_diff:
                L += ["", "  First difference (training | server):", "", "```",
                      first_diff["training"], "-----", first_diff["server"], "```"]
            # 4. scale 0 against plain decoding, and 5. scale 1
            print(f"  {name}: template check done ({match}/{len(sample)}); starting plain decoding", flush=True)
            plain = Server(a.server, base_file[tier], 8302, log=os.path.join(OUT, f"{name}_plain.log"))
            agree = zero = 0
            got = {"exact": 0, "calls_ok": 0, "calls_wanted": 0, "printed": 0, "stop": 0}
            for i_ex, ex in enumerate(exs[:a.n], 1):
                print(f"  {name}: scale-0 and scale-1 replies, example {i_ex}/{min(a.n, len(exs))} ...", flush=True)
                tools = tools_by_key.get(ex["tools"]) if ex.get("tools") else None
                try:
                    # every reply in this comparison recomputes the whole prompt (no prompt cache), so plain decoding's
                    # agreement with itself is measured the same way as the adapter at scale 0. (Before, the second
                    # plain reply reused the first one's cached prompt, which made plain decoding look perfectly
                    # repeatable while the scale-0 reply had to recompute: an unfair baseline.)
                    p1, p2 = plain.chat(ex, tools, cache=False), plain.chat(ex, tools, cache=False)
                    z = lsrv.chat(ex, tools, lora_scale=0.0, cache=False)
                    o = lsrv.chat(ex, tools, lora_scale=1.0, cache=False)
                except Exception as e:  # noqa: BLE001  (left out of both counts)
                    res.setdefault("reply_errors", []).append(f"{ex['id']}: {str(e)[:200]}")
                    continue
                agree += same(p1, p2)
                zero += same(p1, z)
                want = ex["target"]
                got["exact"] += o["content"] == (want.get("content") or "").strip() and not want.get("tool_calls")
                if want.get("tool_calls"):
                    got["calls_wanted"] += 1
                    got["calls_ok"] += bool(o["calls"]) and o["calls"][0][0] == want["tool_calls"][0]["function"]["name"]
                got["printed"] += bool(PRINTED.search(o["content"]))
                got["stop"] += o["finish"] in ("stop", "tool_calls")
                res.setdefault("examples", []).append({"id": ex["id"], "plain": p1, "scale0": z, "scale1": o,
                                                       "target": want})
            n = min(a.n, len(exs))
            if res.get("reply_errors"):
                L.append(f"- {len(res['reply_errors'])} examples skipped, a request failed: "
                         f"{res['reply_errors'][0]}")
            res.update(plain_self_agreement=[agree, n], scale0_identical=[zero, n], scale0_ok=zero >= agree, scale1=got)
            L += [f"- scale 0: {zero}/{n} replies identical to plain decoding; plain decoding agrees with itself "
                  f"{agree}/{n} -> {'met' if res['scale0_ok'] else 'NOT met'}",
                  f"- scale 1 (a look): {got['exact']}/{n} replies equal the training answer word for word; tool calls "
                  f"{got['calls_ok']}/{got['calls_wanted']}; printed markup {got['printed']}; ended by themselves "
                  f"{got['stop']}/{n}"]
        except Exception as e:  # noqa: BLE001
            res["error"] = str(e)[:2000]
            L += ["", "ERROR:", "", "```", str(e)[:2000], "```"]
        finally:
            for s in (plain, lsrv):
                if s is not None:
                    s.stop()
        res["passed"] = all(res.get(k) for k in ("convert_ok", "load_ok", "template_ok", "scale0_ok"))
        L += ["", f"**{name}: {'passed' if res['passed'] else 'NOT passed'}**", ""]
        print("\n".join(L[sec:]), flush=True)          # this adapter's section, as it finishes
    if not report:
        L.append("No adapter was found.")
    elif os.environ.get("STEP5_ONE_TIER") != "1" and (
            not any(r["tier"] == "B" for r in report.values()) or not any(r["tier"] == "A" for r in report.values())):
        L.append("A tier has no adapter: Step 5 is not passed.")
        report["_missing_tier"] = {"passed": False}
    name_ = os.environ.get("STEP5_REPORT", "step5_report")     # a partial rerun keeps the full report's files
    with open(os.path.join(OUT, f"{name_}.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT, f"{name_}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0 if report and all(r.get("passed") for r in report.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
