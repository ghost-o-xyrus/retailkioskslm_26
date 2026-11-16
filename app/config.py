"""
Objective 5, Step 4: the configuration registry. Everything the picker offers comes from the plan files that
produced the results, so a configuration in the app is a configuration that was evaluated.

    reg = Registry(base_dir, fake=False)
    reg.describe()                      # what GET /api/configs returns
    run_cfg, server = reg.resolve({"tier": "A", "model": "qwen35-2b", "pipeline": "o3_final",
                                   "adapter": "none", "toggles": {...}})

Picker categories (design doc, "Configuration picker"):
  tier      A: CPU, 4 threads (the deployed Tier A) - B: integrated GPU, Vulkan
  model     the tier's model files from the plans; a model whose file is missing is listed as unavailable
  pipeline  model_only (no retrieval) -> retrieval (Objective 2 deployed, O3-B0) -> o3_final -> custom
  adapter   none / lora / qlora, when finetune/adapters_gguf/<name>.gguf exists for that model
  toggles   with pipeline "custom": seven switches applied on top of O3-final
"""

import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLANS = os.path.join(ROOT, "harness", "plans")

TIERS = {
    "A": {"label": "Tier A", "hint": "CPU, 4 threads, 5 GB budget", "backend": "cpu",
          "server_exe": "llama-cpu/llama-server.exe", "server_args": ["--jinja", "-c", "8192", "-np", "1", "-ngl", "0",
                                                                       "-t", "4"], "ram_budget_gb": 5.0},
    "B": {"label": "Tier B", "hint": "integrated GPU (Vulkan)", "backend": "vulkan",
          "server_exe": "llama-vulkan/llama-server.exe", "server_args": ["--jinja", "-c", "8192", "-np", "1", "-ngl", "99"],
          "ram_budget_gb": None},
}
MODELS = {
    "qwen35-2b": {"label": "Qwen3.5-2B Q8_0", "short": "2b", "tiers": ["A", "B"], "deployed_on": "A"},
    "qwen35-4b": {"label": "Qwen3.5-4B Q4_K_M", "short": "4b", "tiers": ["B"], "deployed_on": "B"},
}
ADAPTERS = {"2b": {"lora": "lora_2b", "qlora": "qlora_2b"}, "4b": {"lora": "lora_4b", "qlora": "qlora_4b"}}
PIPELINES = [
    {"id": "model_only", "label": "Model only", "hint": "no retrieval; the model and its six tools",
     "source": "O3-B0 without retrieval (Objective 2, the no-retrieval condition)"},
    {"id": "retrieval", "label": "+ Retrieval", "hint": "store information retrieved for every message (Objective 2)",
     "source": "O3-B0 (harness/plans/obj3_step14.json)"},
    {"id": "o3_final", "label": "O3-final", "hint": "router, harness-run tools, checks (Objective 3)",
     "source": "O3-final (harness/plans/obj3_step14.json)"},
    {"id": "deployed", "label": "Deployed", "hint": "what the kiosk runs: O3-final, plus the Objective 4 adapter on Tier B",
     "source": "Objective 4, Steps 7-8: Tier A O3-final; Tier B O3-final + lora_4b, short replies, patches off"},
    {"id": "custom", "label": "Custom", "hint": "O3-final with the switches below", "source": "O3-final + toggles"},
]
# Objective 4's decision per tier (Step 8: Tier A keeps O3-final; Tier B deploys lora_4b with short replies and the
# behaviour patches off). Kiosk mode always runs this.
DEPLOYED = {"A": {"model": "qwen35-2b", "adapter": "none", "toggles": {}},
            "B": {"model": "qwen35-4b", "adapter": "lora", "toggles": {"patches": False, "short_replies": True}}}

TOGGLES = [
    {"id": "retrieval", "label": "Retrieval", "kind": "bool",
     "hint": "Retrieve store information for store questions"},
    {"id": "fallback", "label": "Refusal fallback", "kind": "choice", "choices": ["soft", "hard", "off"],
     "hint": "Below the score threshold: show no cards (soft) or give the fixed reply (hard)"},
    {"id": "harness_tools", "label": "Router and harness tools", "kind": "bool",
     "hint": "The router picks the path; lookups, stock, compare and staff run without the model choosing"},
    {"id": "answer_check", "label": "Answer check", "kind": "bool",
     "hint": "A reply with a detail not in what was shown gets the fixed reply"},
    {"id": "patches", "label": "Behaviour patches", "kind": "bool",
     "hint": "Forced-answer recovery and the staff check"},
    {"id": "short_replies", "label": "Short replies", "kind": "bool", "hint": "At most 40/60 words, 120 tokens"},
    {"id": "thinking", "label": "Thinking", "kind": "bool", "hint": "Let the model think first (off when deployed)"},
]


def _load(name):
    p = os.path.join(PLANS, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


class Registry:
    def __init__(self, base_dir=None, fake=False, evidence_path=os.path.join(HERE, "evidence.json")):
        self.fake = fake
        plan = _load("obj3_step14.json") or {}
        self.base_dir = os.path.abspath(base_dir or os.environ.get("SLM_BASE_DIR")
                                        or os.path.join(ROOT, plan.get("base_dir", "..")))
        self.defaults = plan.get("defaults", {})
        runs = {r["name"]: r for r in plan.get("runs", [])}
        self.final = {m: runs.get(f"o3t_final_{m}_rag") for m in ("2b", "4b")}
        self.b0 = {m: runs.get(f"o3t_b0_{m}_rag") for m in ("2b", "4b")}
        self.evidence = {}
        if os.path.exists(evidence_path):
            with open(evidence_path, encoding="utf-8") as f:
                self.evidence = json.load(f)

    # ---- what exists on this machine ----
    def model_file(self, model_id):
        m = MODELS[model_id]["short"]
        run = self.final.get(m) or {}
        return os.path.join(self.base_dir, run.get("model_path", "")) if run else None

    def model_available(self, model_id):
        return self.fake or bool(self.model_file(model_id) and os.path.exists(self.model_file(model_id)))

    def adapter_file(self, model_id, adapter):
        if adapter in (None, "none"):
            return None
        name = ADAPTERS[MODELS[model_id]["short"]].get(adapter)
        p = os.path.join(ROOT, "finetune", "adapters_gguf", f"{name}.gguf") if name else None
        return p if p and os.path.exists(p) else None

    def default_selection(self, tier="A"):
        model = DEPLOYED[tier]["model"]
        return {"tier": tier, "model": model, "pipeline": "deployed", "adapter": "none",
                "toggles": self.toggle_defaults(model)}

    @staticmethod
    def toggle_defaults(model="qwen35-2b"):
        """O3-final's own settings for the model: the 4B ran without the short-reply rule."""
        return {"retrieval": True, "fallback": "hard", "harness_tools": True, "answer_check": True, "patches": True,
                "short_replies": MODELS.get(model, {}).get("short") != "4b", "thinking": False}

    def describe(self, mode="lab", kiosk_tier="A"):
        out = {"mode": mode, "tiers": [dict(id=k, **{x: v[x] for x in ("label", "hint", "ram_budget_gb")})
                                       for k, v in TIERS.items()],
               "models": [dict(id=k, label=v["label"], tiers=v["tiers"], deployed_on=v["deployed_on"],
                               available=self.model_available(k),
                               adapters=[a for a in ("lora", "qlora") if self.adapter_file(k, a)])
                          for k, v in MODELS.items()],
               "pipelines": [dict(p, evidence=self.evidence.get("pipeline:" + p["id"])) for p in PIPELINES],
               "toggles": [dict(t, evidence=self.evidence.get("toggle:" + t["id"])) for t in TOGGLES],
               "toggle_defaults": self.toggle_defaults(),
               "toggle_defaults_by_model": {k: self.toggle_defaults(k) for k in MODELS},
               "deployed": {t: {"model": d["model"], "adapter": d["adapter"],
                                "adapter_available": d["adapter"] == "none" or bool(self.adapter_file(d["model"], d["adapter"]))}
                            for t, d in DEPLOYED.items()},
               "default": self.default_selection(kiosk_tier),
               "fake": self.fake}
        if mode == "kiosk":
            out["pipelines"] = [p for p in out["pipelines"] if p["id"] == "deployed"]
            out["toggles"] = []
        return out

    # ---- a selection -> a plan run + the llama-server it needs ----
    def resolve(self, sel):
        sel = dict(self.default_selection(sel.get("tier", "A")), **{k: v for k, v in sel.items() if v is not None})
        tier, model, pipe = sel["tier"], sel["model"], sel["pipeline"]
        dep_note = ""
        if pipe == "deployed":                    # the tier's deployed setup, whatever was asked
            d = DEPLOYED[tier]
            model = d["model"]
            adapter = d["adapter"]
            if adapter != "none" and model in MODELS and not self.adapter_file(model, adapter):
                adapter, dep_note = "none", " (adapter file missing: running without it)"
            sel = dict(sel, model=model, adapter=adapter,
                       toggles=dict(self.toggle_defaults(model), **d["toggles"]))
        if tier not in TIERS or model not in MODELS:
            raise ValueError("unknown tier or model")
        if tier not in MODELS[model]["tiers"]:
            raise ValueError(f"{MODELS[model]['label']} does not run on {TIERS[tier]['label']}")
        m = MODELS[model]["short"]
        base = self.final.get(m) if pipe in ("o3_final", "custom", "deployed") else self.b0.get(m)
        if base is None:
            raise ValueError("harness/plans/obj3_step14.json is missing the run for this configuration")
        cfg = copy.deepcopy(dict(self.defaults, **base))
        cfg.pop("eval", None)
        label = {"model_only": "Model only", "retrieval": "+ Retrieval (O3-B0)", "o3_final": "O3-final",
                 "custom": "Custom", "deployed": "Deployed" + dep_note}[pipe]
        untested = False
        if pipe == "model_only":
            cfg.update(retrieval="none")
            for k in ("fallback", "context_view", "gate_style", "rag_rule", "dedupe_shown"):
                cfg.pop(k, None)
        if pipe in ("custom", "deployed"):
            t = dict(self.toggle_defaults(model), **(sel.get("toggles") or {}))
            untested = pipe == "custom" and t != self.toggle_defaults(model)
            if not t["retrieval"]:
                cfg["retrieval"] = "none"
                t["answer_check"] = False
            if t["fallback"] == "soft":
                cfg["fallback"] = "gate"
            elif t["fallback"] == "off":
                cfg["fallback"] = "shadow"
            if not t["harness_tools"]:
                cfg["harness_tools"] = False
                cfg["entity_check"] = False
                cfg["discovery"] = "none"
                if cfg.get("retrieval") == "routed":
                    cfg["retrieval"] = "always"
                    if cfg.get("fallback") == "store-live":
                        cfg["fallback"] = "gate"
            if not t["answer_check"]:
                cfg["verify_answers"] = "off"
            if not t["patches"]:
                cfg["forced_answer"] = "replace"
                cfg["staff_check"] = False
            cfg["answer_length"] = bool(t["short_replies"])
            if t["short_replies"]:
                cfg["max_tokens"] = 120
            else:
                cfg.pop("max_tokens", None)
            if t["thinking"]:
                cfg["thinking"] = True
            sel["toggles"] = t
        adapter = self.adapter_file(model, sel.get("adapter"))
        if sel.get("adapter") not in (None, "none") and adapter is None:
            raise ValueError(f"no {sel['adapter']} adapter file for {MODELS[model]['label']} yet")
        loras = [f for f in (self.adapter_file(model, "lora"), self.adapter_file(model, "qlora")) if f]
        tr = TIERS[tier]
        cfg["images"] = True                   # Step 7: product pictures from the media table, in every setup
        if cfg.get("focus_memory"):
            cfg["ordinal_refs"] = True         # Step 9: "the second one" (with the watch-in-focus memory)
        cfg.update(name=f"app_{tier}_{m}_{pipe}", backend=tr["backend"], engine="core",
                   config_label=f"{label} · {TIERS[tier]['label']} · {MODELS[model]['label']}"
                   + (f" + {sel['adapter']}" if sel.get("adapter") not in (None, "none") else ""))
        if self.fake:
            cfg["fake_retriever"] = True
            cfg.pop("reranker_choice", None)
            fb = os.path.join(HERE, "fake_fallback.json")
            cfg["fallback_config"] = fb
        server = {"exe": os.path.join(self.base_dir, tr["server_exe"]), "model": self.model_file(model),
                  "args": list(tr["server_args"]) + list(cfg.get("extra_server_args", [])), "loras": loras,
                  "lora_index": loras.index(adapter) if adapter else None, "fake": self.fake}
        return cfg, server, sel, untested
