"""
Objective 4, Step 4b: train one adapter on a Kaggle GPU with Unsloth (run by kaggle_train.sh).

    python finetune/train_lora.py --tier A --model unsloth/Qwen3.5-2B --name lora_2b
    python finetune/train_lora.py --tier A --model unsloth/Qwen3.5-2B --name qlora_2b --qlora
    python finetune/train_lora.py ... --max-steps 30 --limit 400        # the smoke run: errors, speed, memory

Settings fixed before the first run (Objectives doc, Objective 4 Step 4): LoRA rank 16, alpha 32, dropout 0, on the
language layers' q, k, v, o, gate, up and down projections (Qwen3.5's linear-attention layers name their projections
differently and are left as they are); learning rate 2e-4, cosine decay after a 5% warm-up; 2 epochs; effective batch
16 (2 per step x 8 accumulated); maximum length 4,096 tokens; seed 3407. QLoRA: the same, on a 4-bit base. Loss on
the answer only (prepare_sft.py). Thinking stays off, as deployed.
Precision follows what Unsloth loads (the T4 has no bf16): fp16 mixed precision is on when the base weights are
fp16, which the smoke run measured for all three adapters (finite losses), and off if they were ever fp32.
--fit-minutes M --smoke-log <smoke train_log.json>: the number of steps is the smaller of 2 epochs and what fits in M
minutes at the smoke run's measured seconds per step (90% of M, so the time limit is a backstop, not the plan); the
cosine schedule runs over that number of steps. --epochs caps it (the full run uses 1, chosen after the smoke run
for the GPU budget).
Writes finetune/adapters/<name>/ (the adapter, adapter_config.json, train_log.json: loss curve, held-out loss,
tokens, minutes, peak GPU memory, render counts). Stops cleanly at --max-minutes and records that it did.
"""

import argparse
import json
import math
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prepare_sft as P  # noqa: E402

TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
SETTINGS = dict(r=16, alpha=32, dropout=0.0, lr=2e-4, warmup=0.05, epochs=2, batch=2, accum=8, max_len=4096, seed=3407)


def load(model_name, qlora, max_len):
    from unsloth import FastModel
    model, tok = FastModel.from_pretrained(model_name, max_seq_length=max_len, load_in_4bit=qlora, dtype=None,
                                           full_finetuning=False)
    text_tok = getattr(tok, "tokenizer", tok)           # a vision-language processor wraps the text tokenizer
    model = FastModel.get_peft_model(
        model, r=SETTINGS["r"], lora_alpha=SETTINGS["alpha"], lora_dropout=SETTINGS["dropout"], bias="none",
        target_modules=TARGETS, finetune_vision_layers=False, finetune_language_layers=True,
        finetune_attention_modules=True, finetune_mlp_modules=True, use_gradient_checkpointing="unsloth",
        random_state=SETTINGS["seed"])
    return model, text_tok


def main(argv=None):
    try:
        import unsloth  # noqa: F401  (before transformers and peft, so Unsloth's patches apply)
    except ImportError:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", required=True, choices=["A", "B"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--qlora", action="store_true")
    ap.add_argument("--max-steps", type=int, default=-1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-minutes", type=float, default=300)
    ap.add_argument("--fit-minutes", type=float, default=None, help="plan the steps to fit this many minutes")
    ap.add_argument("--smoke-log", default=None, help="the smoke run's train_log.json (its seconds per step)")
    ap.add_argument("--epochs", type=int, default=SETTINGS["epochs"])
    ap.add_argument("--batch", type=int, default=SETTINGS["batch"], choices=[1, 2],
                    help="examples per step; the effective batch stays 16 (1 is the fallback when 2 runs out of memory)")
    a = ap.parse_args(argv)
    if a.smoke_log and os.path.exists(a.smoke_log):        # the full run starts at the batch the smoke run needed
        a.batch = min(a.batch, json.load(open(a.smoke_log, encoding="utf-8"))["settings"].get("batch", a.batch))
    SETTINGS.update(batch=a.batch, accum=16 // a.batch, epochs=a.epochs)
    import torch
    from transformers import Trainer, TrainingArguments, DataCollatorForSeq2Seq, TrainerCallback
    random.seed(SETTINGS["seed"])
    torch.manual_seed(SETTINGS["seed"])
    out = os.path.join(HERE, "adapters", a.name)
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    model, tok = load(a.model, a.qlora, SETTINGS["max_len"])
    train, held, stats = P.build(tok, a.tier, SETTINGS["max_len"], a.limit)
    print(f"[{a.name}] data: {json.dumps(stats)}", flush=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    steps_per_epoch = math.ceil(len(train) / (SETTINGS["batch"] * SETTINGS["accum"]))
    size = {}
    for prm in model.parameters():                     # the base's float dtype, by size (4-bit weights are uint8)
        if prm.is_floating_point():
            size[prm.dtype] = size.get(prm.dtype, 0) + prm.numel()
    dtype = max(size, key=size.get)
    fp16 = dtype == torch.float16
    log = {"name": a.name, "model": a.model, "tier": a.tier, "qlora": a.qlora, "settings": SETTINGS,
           "targets": TARGETS, "data": stats, "steps_per_epoch": steps_per_epoch, "loss": [], "held_out_loss": [],
           "compute_dtype": str(dtype).replace("torch.", ""), "fp16_mixed_precision": fp16, "step_seconds": []}
    max_steps = a.max_steps
    if a.fit_minutes and a.smoke_log:
        smoke = json.load(open(a.smoke_log, encoding="utf-8"))
        sps = smoke.get("seconds_per_step")
        if sps:
            fit = int(0.9 * a.fit_minutes * 60 / sps)
            max_steps = max(1, min(SETTINGS["epochs"] * steps_per_epoch, fit))
            log["planned"] = {"smoke_seconds_per_step": sps, "fit_minutes": a.fit_minutes, "steps": max_steps,
                              "epochs": round(max_steps / steps_per_epoch, 2)}
            print(f"[{a.name}] planned {max_steps} steps ({max_steps / steps_per_epoch:.2f} epochs) at "
                  f"{sps:.0f} s per step from the smoke run", flush=True)
        else:
            print(f"[{a.name}] note: the smoke log has no seconds per step; 2 epochs planned, the time limit stops "
                  "the run", flush=True)
    total_steps = max_steps if max_steps > 0 else SETTINGS["epochs"] * steps_per_epoch

    class Clock(TrainerCallback):
        def on_log(self, args, state, control, logs=None, **kw):
            if logs and "loss" in logs:
                log["loss"].append([state.global_step, round(logs["loss"], 4)])
            if logs and "eval_loss" in logs:
                log["held_out_loss"].append([state.global_step, round(logs["eval_loss"], 4)])
            if state.global_step and state.max_steps:
                el = (time.time() - t_train) / 60
                print(f"[{a.name}] step {state.global_step}/{state.max_steps}, {el:.1f} min, projected "
                      f"{el / state.global_step * state.max_steps:.0f} min" + (f", loss {logs.get('loss')}" if logs and
                                                                                  "loss" in logs else ""), flush=True)

        def on_step_end(self, args, state, control, **kw):
            now = time.time()
            log["step_seconds"].append(round(now - self.last, 1) if hasattr(self, "last") else None)
            self.last = now
            if (now - t0) / 60 > a.max_minutes:
                log["stopped_at_time_limit"] = state.global_step
                control.should_training_stop = True

    from datasets import Dataset
    keep = ["input_ids", "labels", "attention_mask"]
    ds_train = Dataset.from_list([{k: it[k] for k in keep} for it in train])
    ds_held = Dataset.from_list([{k: it[k] for k in keep} for it in held]) if held else None
    kw = dict(
        output_dir=os.path.join("/tmp", "o4ckpt", a.name), per_device_train_batch_size=SETTINGS["batch"],
        gradient_accumulation_steps=SETTINGS["accum"], num_train_epochs=SETTINGS["epochs"], max_steps=max_steps,
        learning_rate=SETTINGS["lr"], lr_scheduler_type="cosine",
        warmup_steps=max(1, math.ceil(SETTINGS["warmup"] * total_steps)), fp16=fp16,
        bf16=False, logging_steps=5, eval_strategy="steps" if ds_held is not None else "no",
        eval_steps=max(10, steps_per_epoch // 2), per_device_eval_batch_size=2, save_strategy="no", seed=SETTINGS["seed"],
        report_to=[], optim="adamw_8bit", weight_decay=0.0, group_by_length=True, remove_unused_columns=False)
    import dataclasses
    known = {f.name for f in dataclasses.fields(TrainingArguments)}
    dropped = sorted(k for k in kw if k not in known)    # an argument this transformers version no longer has
    if dropped:
        print(f"[{a.name}] note: this transformers version has no {', '.join(dropped)}; left out", flush=True)
        log["arguments_left_out"] = dropped
    args = TrainingArguments(**{k: v for k, v in kw.items() if k in known})
    trainer = Trainer(model=model, args=args, train_dataset=ds_train, eval_dataset=ds_held,
                      data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100),
                      callbacks=[Clock()])
    torch.cuda.reset_peak_memory_stats()
    print(f"[{a.name}] compute {log['compute_dtype']}, fp16 mixed precision {'on' if fp16 else 'off'}, "
          f"{total_steps} steps", flush=True)
    t_train = time.time()
    trainer.train()
    if ds_held is not None:
        log["held_out_loss"].append([trainer.state.global_step, round(trainer.evaluate()["eval_loss"], 4)])
    model.save_pretrained(out)
    tok.save_pretrained(out)
    log.update(steps=trainer.state.global_step, train_minutes=round((time.time() - t_train) / 60, 1),
               total_minutes=round((time.time() - t0) / 60, 1),
               peak_gpu_gb=round(torch.cuda.max_memory_allocated() / 1e9, 2),
               seconds_per_step=_median([x for x in log["step_seconds"][1:] if x]),
               examples_seen=min(trainer.state.global_step * SETTINGS["batch"] * SETTINGS["accum"],
                                 SETTINGS["epochs"] * len(train)),
               epochs_done=round(trainer.state.global_step / steps_per_epoch, 2))
    log["tokens_per_second"] = round(log["examples_seen"] * stats["tokens"] / max(1, stats["examples"])
                                     / max(1, time.time() - t_train), 1)
    with open(os.path.join(out, "train_log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=1)
    print(f"[{a.name}] done: {log['steps']} steps in {log['train_minutes']} min ({log['seconds_per_step']} s per step), "
          f"peak GPU {log['peak_gpu_gb']} GB, "
          f"held-out loss {log['held_out_loss'][-1][1] if log['held_out_loss'] else '-'}", flush=True)
    return 0


def _median(xs):
    xs = sorted(xs)
    return None if not xs else (xs[len(xs) // 2] if len(xs) % 2 else (xs[len(xs) // 2 - 1] + xs[len(xs) // 2]) / 2)


if __name__ == "__main__":
    sys.exit(main())
