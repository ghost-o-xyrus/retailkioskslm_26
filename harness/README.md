# Eval harness (Objective 1, Step 5)

Runs the eval cases against models served by `llama-server` and logs what Step 6 needs to score them:
- every tool call
- every reply
- timings
- token counts
- prompt-cache reuse
- peak RAM

Standard library only, plus `psutil` for RAM (`pip install psutil`). It doesn't need the `openai` package.

## Folder layout it expects

```
slm-kiosk/
  llama-cpu/llama-server.exe
  llama-vulkan/llama-server.exe
  models/qwen3.5-4b/Qwen3.5-4B-Q4_K_M.gguf   (etc.)
  slm-kiosk-catalogue/        <- this project; run commands from here
    harness/  eval/  tools/  data/
    results/                  <- created by the harness
```

Before the first run, check the `model_path` entries in `harness/plans/*.json` against your `models/` folder. They follow the filenames in `model_registry.csv`. `--dry-run` prints every server command without starting anything.

## 1. Pilot first (10 minutes)

Run 10 cases on one model before any overnight run:

```powershell
cd slm-kiosk\slm-kiosk-catalogue
python harness\run_plan.py harness\plans\stage1_screen.json --dry-run
python harness\run_plan.py harness\plans\stage1_screen.json --only qwen35-4b_q4_k_m_vulkan
# after ~10 cases press Ctrl+C, then:
python harness\summarize.py results\qwen35-4b_q4_k_m_vulkan
```

Check four things in the summary:

| Check | Good | If not |
|---|---|---|
| `errors` | 0 | Read `results\<run>\server.log` |
| `prompt_cache_reuse_pct` | well above 50% | Prompt caching isn't working, and every case pays full prefill (~1,400 tokens). Make sure `-np 1` is in `server_args`. Qwen3.5's hybrid architecture may limit caching on older llama.cpp builds, so update llama.cpp. |
| flag `reasoning_content_present` | absent | Thinking is still on. Keep `--reasoning-budget 0` for Qwen models. |
| flag `tool_call_as_text` | absent or rare | The model wrote a tool call as plain text that the server's template didn't parse. Note it for that model; Step 6 scores it as a format failure. |

Then open `results\<run>\cases.jsonl` and read three or four records end to end. Rerunning the same command resumes where it stopped.

## 2. Staged runs

| Stage | Command | Runs | Approx. time |
|---|---|---|---|
| 1. Screen | `python harness\run_plan.py harness\plans\stage1_screen.json` | 6 models at Q4_K_M, Vulkan, 150 core cases | 4–5 h |
| 2. Quantization | `python harness\run_plan.py harness\plans\stage2_quant.json --only <top 3 names>` | Q8_0 of the top 3 | 3–4 h |
| 3. Head-to-head | `python harness\run_plan.py harness\plans\stage3_head_to_head.json --only <4 names>` | 2 finalists × (1 greedy + 3 runs at 0.3) on 292 v1.1 test cases | 6–8 h |
| 4. Speed | `python harness\run_plan.py harness\plans\stage4_speed.json --only <names>` | 30-case subset, finalists × quant × CPU and Vulkan | ~2 h |

`--only` takes comma-separated run names exactly as they appear in the plan file. Each run is skipped automatically once complete, so a plan can be started, stopped and restarted.

- **Stage 1 is greedy** (temperature 0, seed 42). This is the main score.
- **Stage 3's `_t03` runs** use temperature 0.3, the suggested deployment setting, with 3 repeats for pass^3. Change `temperature` in the plan if you deploy at a different value.
- **Stage 4 CPU runs** use 4 threads (Tier A); Vulkan runs offload all layers (Tier B). Close other heavy apps during Stage 4, because RAM and speed are what's being measured.
- **Context is 8,192 tokens everywhere**, so quality runs are comparable. Tool definitions plus a few tool results can exceed 4K.

## Running one model by hand (no plan)

```powershell
# window 1
..\llama-vulkan\llama-server.exe -m ..\models\qwen3.5-4b\Qwen3.5-4B-Q4_K_M.gguf --jinja -c 8192 -np 1 -ngl 99 --reasoning-budget 0 --port 8080
# window 2
python harness\run_eval.py --name qwen35-4b_q4_manual --model Qwen3.5-4B --quant Q4_K_M --backend vulkan
```

| Option | What it does |
|---|---|
| `--eval eval\eval_set_v1.1.jsonl` | Use the v1.1 set (default is the v1.0 core) |
| `--split test` / `--set expansion` | Filter cases |
| `--ids eval\speed_subset_ids.json` | Run only the listed case ids |
| `--category refusal,handoff` | Only these categories |
| `--limit 10` | First 10 cases |
| `--repeats 3 --temperature 0.3` | Repeated sampling for pass^3 |
| `--thinking` | Leave thinking on (off by default) |
| `--server-pid 1234` | RAM tracking if the server isn't found automatically |

## What each record in `cases.jsonl` contains

| Field | Meaning |
|---|---|
| `id`, `repeat`, `category`, `subcategory`, `mode`, `language`, `set`, `split`, `paired_with` | Copied from the eval case, so scoring can group results |
| `model`, `quant`, `backend`, `run` | What produced it |
| `tool_calls[]` | `name`, `arguments` (parsed), `arguments_raw`, `arguments_valid_json`, `known_tool`, `round`, `result` (the mock tool's reply), `result_error` |
| `final_reply` | The model's last message, with any `<think>` text removed |
| `flags` | `tool_call_as_text`, `think_tags_in_content`, `reasoning_content_present`, `hit_max_tokens`, `max_rounds_reached` |
| `turns[]` | Per request: wall time, finish reason, prompt/completion tokens, `prompt_n` (tokens actually computed), `cache_n` (tokens reused from cache), `prompt_ms`, `predicted_n`, `predicted_ms`, content |
| `metrics.end_to_end_ms` | Customer's wait from question to final reply, including tool rounds |
| `metrics.ttft_ms` | Prefill time of the first request: when the first token is ready |
| `metrics.tokens_per_s` | Generation speed across the case |
| `metrics.prompt_tokens_total / _processed / _cached` | Cache effectiveness |
| `metrics.peak_rss_mb` | Highest server memory during this case |
| `error` | Present only if the request failed. Errored cases are retried on resume |

`run_meta.json` records the settings, the server's model path and build, RAM tracking status, machine info, start and finish time, and the run's peak RAM.

## How it works

1. Builds the system prompt from `eval/system_prompts.json` (tools or grounded mode) and appends the case's context, if any.
2. Sends the conversation to `/v1/chat/completions` with the six tool schemas (tools mode only). Uses greedy decoding with a fixed seed, `chat_template_kwargs: {"enable_thinking": false}`, and `cache_prompt: true`.
3. If the model calls tools, runs them with `tools/mock_tools.call_tool` against `data/kiosk`. Appends the results, then asks again, up to 4 rounds.
4. Stops at the first reply without tool calls and records everything.

Requests are non-streaming, so time-to-first-token is taken from the server's own `prompt_ms`. In practice, prefill is nearly all of the wait before the first token.

## Testing the harness without a model

`harness/fake_server.py` imitates `llama-server`'s API with scripted behaviour: tool calls, a tool call written as text, invalid JSON, and `<think>` tags. The tests start it, run the harness and plan runner against it, and check every logged field:

```powershell
python -m unittest harness.test_harness -v
```

All 370 v1.1 cases have also been run through the harness against the fake server, with no errors. These tests prove the plumbing, not any model's quality. The first real check is the pilot in section 1.

## Objective 2: retrieval conditions (Step 7)

`run_eval.py` can now connect the knowledge base (`retrieval/knowledge_base.py`). Everything is off by default, so
Objective 1 runs behave exactly as before.

| Option | What the model gets |
|---|---|
| `--retrieval none` (default) | The v1.1 kiosk: tools only |
| `--retrieval oracle` | The case's gold chunks, shown with the customer's message (the ceiling) |
| `--retrieval always` | The top-k retrieved chunks, shown with every customer message |
| `--retrieval tool` | A `search_knowledge` tool, called when the model decides to |
| `--fallback shadow` (default) | Log what the refusal fallback would do; still run the model |
| `--fallback live` | Hard fallback: below the threshold, fixed "I don't have that" reply, no model call |
| `--fallback gate` | Soft fallback: below the threshold, the model sees "(nothing relevant found)" and can still use tools |
| `--k-chunks N` | Chunks shown (default: the k chosen in Step 7a) |
| `--data-dir data_v1\kiosk` | Catalogue the tools read (default: the scaled `data\kiosk`) |
| `--context-view compact` | Product cards without the marketing description (Step 7d) |
| `--chunk-gate` | Show only chunks scoring at or above the fallback threshold; Hinglish exempt (Step 7d) |
| `--warmup` | One unlogged request first, so the system prompt and tools are cached, as at kiosk start-up |

Design decisions:
- **Retrieved text goes into the customer's message, not the system prompt.** With Qwen's chat template, tool
  definitions sit after the system prompt, so changing the system prompt per question would also stop the ~1,000
  tool-definition tokens being reused from the prompt cache. `cache_n` in the logs checks this.
- **Retrieval runs on the latest customer message only.** That's what the Step 6 threshold was calibrated on.
  Follow-ups such as "and in blue?" are left to the product tools.
- **Prompts:** the v1.1 tools prompt is unchanged. One rule is added for the oracle and always conditions
  (`rag_always_rule`) and one for the tool condition (`rag_tool_rule`) in `eval/system_prompts.json`.
- **Shadow fallback in evaluation runs.** The fallback only replaces the reply. One shadow run therefore gives
  both "retrieved" and "retrieved + fallback" scores, and every threshold can be checked afterwards.
- Grounded-mode cases ignore `--retrieval`. In tool mode, `search_knowledge` returns the top-k chunks with no
  fallback; the score is still logged.

Each record gains a `retrieval` block. It holds the query, chunk ids and scores, the top-10, whether the query is
Hinglish, `fallback_would_refuse`, `fallback_applied`, `context_tokens`, and per-stage `timings_ms`; tool runs log
one entry per `search_knowledge` call instead. `metrics` gains `retrieval_ms` (included in `end_to_end_ms`) and
`harness_rss_mb` (the process holding the knowledge base) and `first_visible_ms` (the wait before the answer's
first word: retrieval, every tool round, and the final prefill). `run_meta.json` records the knowledge-base settings,
load time and added RAM.

Pilot: `python harness\run_plan.py harness\plans\obj2_step7_pilot.json`, then
`python harness\pilot_report.py results_obj2\p7_*`.

Step 7d (Tier A latency): `python retrieval\check_context_view.py`, then
`python harness\run_plan.py harness\plans\obj2_step7d_latency.json`.

Step 7e (the 2B's extra tool rounds): `python harness\run_plan.py harness\plans\obj2_step7e_behaviour.json`, then
`python harness\compare_runs.py results_obj2\p7d_2b_cpu_v11_none results_obj2\p7d_2b_cpu_v11_compact_gate results_obj2\p7e_2b_cpu_v11_omit results_obj2\p7e_2b_cpu_v11_rulec`
(and the same for `rag`). New options: `--gate-style omit` (when the gate applies, the message goes in unchanged)
and `--rag-rule <key>` (which retrieval rule from `eval/system_prompts.json`). Loaded retrieval models are now
shared by every run in one plan, so a run's harness RAM is the real footprint, not one copy per earlier run.

Step 7f: `--dedupe-shown`. When the model calls `get_product_details` for a watch whose card is already in the
customer's message, the tool returns a short pointer instead of the full record. The call itself still happens and
is still scored. Plan: `harness\plans\obj2_step7f_dedupe.json`.

## Objective 2, Step 8: end-to-end evaluation

**Deployed setup** (fixed in Step 7 on dev cases):
- always retrieve, k = 3 compact chunks;
- soft fallback that leaves the message unchanged (`--fallback gate --gate-style omit`), with rule
  `rag_always_rule_b`;
- short reply when a shown card is re-fetched (`--dedupe-shown`);
- a warm-up request at the start of each run.

| Plan | Runs | Time (rough) |
|---|---|---|
| `obj2_step8_core.json` | 4B and 2B on Vulkan. 373 test retrieval questions × {none, oracle, deployed}, and 292 v1.1 test cases × {none, deployed} | 10–12 h |
| `obj2_step8_secondary.json` | Both models, retrieval questions × {no fallback, `search_knowledge` tool} | 5–6 h |
| `obj2_step8_speed.json` | 2B on CPU (Tier A): 40 test retrieval questions + the 30-case speed subset × {none, deployed} | 1 h |

Scoring:
- `eval\score_rag.py` scores the retrieval questions automatically. It also computes hard-fallback rows from the
  logs and the paired comparisons.
- `eval\score.py --mode tools` runs the v1.1 regression check.
- `eval\rag_judge\build_packet.py` builds the blind judging packet. The judge's labels go back into
  `score_rag.py --labels`.
- `eval\rag_judge\agreement.py` checks the 50-item human sample against the judge.

## Objective 3, Step 1: baseline and per-round logging

Nothing about the kiosk changes in this step. It re-measures Objective 2's deployed setup, now called **O3-B0**, on
the dev split, so every later Objective 3 change has a paired baseline. It also records exactly where each turn's
time goes.

**New in `run_eval.py`:**
- `--config-label O3-B0` is stored in `run_meta.json` and on every record (`config`).
- Every record has `route` (`"none"` until the Step 4 router exists).
- After each case, the harness asks the server's `/tokenize` for real token counts of the retrieved context and of
  each tool output. These go in `tokens` and in each tool call's `result_tokens`. The requests run after the case's
  timer stops, so measured times are unchanged. `--no-count-tokens` turns this off.

**New script, `harness/time_split.py`:** per run, it reports:
- rounds per case;
- tokens read and written, split by message, tool outputs, calls and answer;
- the time split;
- read and write speeds, with a per-request overhead fit;
- the plan's first-word formula checked against the measured wait;
- first-word and reply percentiles with bootstrap intervals;
- prompt-cache misses;
- repeat stability;
- waste: repeated calls, extra `call_staff`, re-fetched cards, tool errors, and cases that hit the round limit.

It also works on Objective 2 runs.

**Plans:**

| Plan | Runs | What |
|---|---|---|
| `obj3_step1_baseline.json` | `o3s1_{4b,2b}_rag_{b0,oracle}`, `o3s1_{4b,2b}_v11_{b0,none}` | Dev quality, Vulkan, greedy. The oracle and no-retrieval references stay fixed for all of Objective 3 |
| `obj3_step1_speed.json` | `o3s1sp_a_2b_{rag,v11}_b0` (CPU, 4 threads), `o3s1sp_b_4b_{rag,v11}_b0` (Vulkan) | In-place timing on `eval/o3_dev_speed_ids.json` (40 + 30 dev cases), 3 repeats run as full passes |

Results go to `results_obj3\`.

## Objective 3, Step 2: data and scorer fixes

**Kiosk changes (configuration O3-S2), checked against O3-B0 on dev:**
- **`search_catalogue` matching.** The query is now matched word by word:
  - generic words are dropped (`watch`, `dial`, `strap`, gender words, common Hinglish fillers);
  - plurals are folded;
  - a word must match a whole word of the product text, or from 4 letters the start of one (`chrono` finds `chronograph`);
  - case material, glass, function, movement, display and lume are now searchable;
  - when some products match every word, only those are returned.

  Before, "dress watch" returned all 1,391 active SKUs; now it returns 260, and "titanium watch" returns 27.
- **`query` description** now lists materials, glass, functions and lume, and says to leave out generic words.

**Measurement changes (no rerun needed):**
- **`eval/eval_set_v1.2.jsonl`** is v1.1 with TSL-097/098 fixed (`eval/build_eval_v12.py`). Both are test cases, so
  dev scores are unchanged.
- **`eval/score.py --credit-shown-cards`** counts answers taken from shown product cards: a required
  `get_product_details` counts as made when that watch's card was shown, and naming it counts as grounded. Stock,
  comparison and search calls still have to be made.
- **`harness/time_split.py`** counts cache misses on tool-mode cases only.

**New tools for every later keep rule:**
- `eval/noise_floor.py`: flip rate between greedy repeats, and the noise bound for each model and set.
- `eval/compare_dev.py`: paired dev comparison with a verdict. It reports "better" or "worse" only beyond the noise
  bound and with the bootstrap interval excluding 0.

Plan: `harness/plans/obj3_step2.json` (`o3s2_{4b,2b}_{rag,v12}_s2`).

## Objective 3, Step 3: loop guard and compact, honest tool outputs

**`--loop-guard`:**
- A repeated identical call is not run; the model gets a one-line note instead.
- A second `call_staff` in a turn gets "staff already notified (ticket …)".
- The 4th (last) request goes with `tool_choice: "none"`, so the turn ends in an answer. Any calls on it are ignored
  (flag `guard_final_calls_ignored`).
- An empty final reply becomes a fixed staff line (flag `empty_reply_fallback`). Every scorer counts this as an empty
  reply, so a stuck turn never scores as a correct decline.

**`--tool-view compact`** (`tools/render.py`, plus `mock_tools.HONEST`):
- The model reads short text instead of JSON: one line per watch, and no marketing description.
- Searches say "Showing 3 of N", whether every search word matched, and which brands Veyra does not sell.
- Missing values print as "not listed".
- Searches return 3 results by default.
- Spec words (glass, material, movement, strap, functions, water use, lume) match only the spec fields. The kiosk
  copy's descriptions contradict the spec row on purpose: before this, 7 of the top 10 "sapphire" results had mineral
  glass.
- Logged results stay as full dicts, so scoring is unchanged.

**Plans:**
- `obj3_step3_pilot.json`: 35 loop-prone dev questions, 2B, about 10 minutes. Run it first.
- `obj3_step3.json`: O3-S3 (guard + compact) and O3-S3g (guard only), both models, dev.
- `obj3_step3_speed.json`: Tier A CPU timing of O3-S3.

## Objective 3, Step 4: the intent router

`router/router.py` routes each customer message before any model call. The routes are `lookup`, `stock`, `compare`,
`shopping`, `staff`, `chat` and `store`, or `unclear` when the router can't decide.
1. **Rules:** weighted English and Hinglish cues, plus product codes, catalogue design names and brands Veyra doesn't
   sell. The best route wins if it leads the runner-up by at least 1.
2. **Prototypes:** otherwise, the message is compared with bge-small embeddings of hand-written example sentences
   (`router/prototypes.json`). These embeddings come from the encoder retrieval already loads.
3. **Follow-ups:** a reply with no cue of its own inherits "shopping" from the previous customer message.

`--retrieval routed`: `store` and `unclear` take the Objective 2 retrieval path; all other routes get no cards.
Every record carries `route`, and `retrieval.router` adds the source, margin and time.

Checking the router needs no language model:
- `python eval\route_labels.py` builds the labels (`eval/route_labels.json`) from case categories.
- `python router\check_router.py` reports accuracy, misroutes and the confusion matrix.

Plans: `obj3_step4.json` (dev, both models) and `obj3_step4_speed.json` (Tier A CPU).

## Objective 3, Step 5: tools run by the harness, one-request answers

These need `--retrieval routed`.

**`--harness-tools`:** for the `lookup`, `stock`, `compare` and `staff` routes, `plan_harness_calls` reads what the
tool needs from the message:
- product codes, or a catalogue design name (mapped to its design id);
- a colour, for stock checks;
- the alternatives reason: cheaper, out of stock or similar style;
- the staff reason: try-on, purchase, service or other.

The harness runs the call and shows it to the model as an earlier tool round. The model then answers in one request
with `tool_choice: "none"`. Records mark these calls `"by": "harness"`. If nothing can be read (no code or name), the
turn falls back to the model's own tool use.

**`--store-one-round`:** store questions are answered from the retrieved cards in one request.
- A service request ("stopped working", "repair", "new battery") gets `call_staff(service)` first.
- An answer that says it doesn't know, or offers staff, gets a real `call_staff(question_unanswered)` and a fixed
  line (flag `harness_staff_after_answer`).

Plans: `obj3_step5.json` (O3-S5, and O3-S5h with harness tools only) and `obj3_step5_speed.json`.

## Objective 3, Step 6: guided discovery

`--discovery template|model` applies to the shopping route only (`harness/discovery.py`).
- **Reading slots:** every customer message so far is read for budget, recipient (a child aged 12 or under counts
  as kids), occasion (mapped to a style), strap and size. Concrete features are read too: movement, display, water
  resistance, dial colour, explicit size in mm, and feature words.
- **When to search:** if a concrete feature is known, two or more slots are known, or two kiosk turns have passed,
  the harness runs one `search_catalogue` call.
  - If nothing matches, it drops filters in a fixed order (size, dial colour, features, strap, style…) and tells
    the model what it left out.
  - The model then recommends in one request.
- **Otherwise it asks:**
  - `template`: fixed English or Hinglish questions, with no model call.
  - `model`: one model request with a note on what to ask.

Simulated dialogues (`--dialogues eval/o3_dialogues.jsonl`) give one record per dialogue.
- `eval/build_dialogues.py` writes the hidden customer profiles.
- `harness/simulator.py` answers only the slots the kiosk asked about, until search results are shown (at most 4
  kiosk turns).
- `eval/score_dialogues.py` reports recommendations, questions asked and slots known at the recommendation. It also
  reports fit (shown watches that satisfy what the customer said), model requests and waits. It builds the blind A/B
  packet for the question-phrasing rubric.

Plans: `obj3_step6.json` (single shopping cases and dev dialogues) and `obj3_step6_speed.json` (Tier A dialogues).

## Objective 3, Step 7: forced answers, prompt v1.2 and staff discipline

`--forced-answer recover` (with `--loop-guard`) changes what happens on a request that may not call tools
(`tool_choice` "none": harness-run routes, discovery searches, the loop guard's last round):
- The last tool result ends with a short note that tools are finished and the answer is due (about 20 tokens).
- If the model still prints a tool call as text, the prose around it is kept when it is a real answer (6 words or
  more).
- Otherwise the printed call is read (Qwen XML or JSON). A read-only tool not already run is run once by the
  harness, and the answer is asked for once more. A printed `call_staff` becomes a real call and the fixed staff line.
- Anything left is the fixed staff line, as with `replace` (Step 6c, still the default).

`--tools-prompt tools_v12` selects prompt v1.2 in `eval/system_prompts.json`: two search-now examples, "answer from
results already shown", "say so when no watch matches everything", and the staff rules (offering staff means
calling it, at most once, never after answering).

`--staff-guard`: on routes the model handles itself, a reply that mentions staff without a `call_staff` call gets a
real call from the harness (Objective 1 rule).

`eval/compare_dev.py` adds a table of printed tool calls (shown as the staff line, prose kept, recovered) and staff
discipline (model staff calls, staff calls on answerable questions, staff offered but not called).

Plan: `obj3_step7.json` (O3-S7a and O3-S7 on full dev for both sets and both models, then the dev dialogues).

## Objective 3, Step 8: knowledge path (entity check, store-only hard fallback, staff check)

- `--entity-check` (`harness/entity.py`): on store, unclear and shopping routes, the harness answers some messages
  itself, with no model call:
  - **Not carried:** another brand, a smartwatch or fitness feature, or a non-watch item, asked with a shopping word
    ("sell", "have", "available", "chahiye"…). Watch brands and smart features also get up to 3 real Veyra watches.
  - **Missing design:** a real collection followed by a design name that does not exist ("Veyra Everyday
    Zenith") gets "we don't have a watch called …" plus up to 3 real designs from that collection.
- `--fallback store-live`: a store or unclear question scoring below `hard_threshold` gets the fixed "I don't have
  that" reply with no model call, unless it contains a product code or a catalogue name. Everything else behaves as
  `gate`.
  - `eval/calibrate_store_tau.py` sets `hard_threshold` on dev store questions only, from an O3-S7a run's logged
    scores. The rule is the same as in Objective 2: the highest threshold with at most 5% false refusals.
  - It writes `results_obj3/_tau_step8/fallback.json`, where `threshold` (the soft fallback) keeps the Objective 2
    value.
- `--staff-check`: when cards or tool results were shown, the first model `call_staff` for an unanswered question
  returns a note asking the model to check them first. A second call runs.
- `eval/compare_dev.py` now splits staff offers into "promised, not called" (a violation) and "offer asked as a
  question". It also counts entity replies, fallback replies and staff-check notes.

Plan: `obj3_step8.json` (O3-S8a and O3-S8 on dev store questions, O3-S8 on v1.2 tool cases, both models).

## Objective 3, Step 9: re-ranker trial

These run offline, with no language model:
- `retrieval/build_rerank_train.py` writes training questions generated from the corpus only (English and
  Hinglish templates, design-name typos). It mines hard negatives with the deployed first stage, and drops any
  question too close to an eval question.
- `retrieval/finetune_reranker.py` fine-tunes MiniLM-L6 with fixed settings, in a plain PyTorch loop.
- `retrieval/bench_reranker.py` compares the deployed MiniLM, the fine-tuned MiniLM and a small multilingual
  cross-encoder at depths 20 and 10 on dev. It applies the keep rule and writes `choice.json` if a configuration
  qualifies.
- `retrieval/calibrate_step9.py` re-derives the Hinglish bypass, the soft threshold and the hard threshold for the
  chosen re-ranker, by the rules already fixed.

`--reranker-choice` makes the knowledge base load the chosen re-ranker and depth. Plan: `obj3_step9.json` (the
end-to-end check, only if a re-ranker was chosen).

## Kaggle (CPU jobs off the laptop)

`kaggle/` sends CPU-only jobs to a private Kaggle notebook and brings back only the files they create (see
`kaggle/README.md`).
- Run metadata now records the machine (`machine.label`: `local` or `kaggle-cpu`).
- `compare_dev.py` flags waits measured on different machines.
- `run_plan.py` has `--only-backend cpu`, `--server-exe` and `--models-root`, for running a plan's CPU runs
  with a Linux llama-server.

## Objective 3, Step 10: answer check (cited answers)

`harness/verify.py` lists a reply's checkable details: numbers with a unit or a price, numbers of 11 or more,
product codes, and spec words (glass, movement, material, function, shape, origin, dial colour). It checks that
each one appears in the evidence or in the customer's message. Months/years and 12-hour clock conversions are
accepted.

`--verify-answers` applies to store and unclear routes:
- `shown`: the evidence is every card and tool result from this turn.
- `cited`: the evidence is the cards the reply cites, plus tool results. This mode goes with the
  `rag_always_rule_cite` prompt rule, which asks the model to end its answer with card numbers such as "[1, 3]".

A failed check gives the fixed reply. Citations are removed from what the customer sees.

`eval/replay_verify.py` applies the check to a finished run without the model (O3-S10v from the O3-S8 runs).

`compare_dev.py` adds an independent measure: knowledge-path replies with a detail found in neither the case's
gold card nor the tool results. It also counts replies replaced by the check and replies that cite.

Plan: `obj3_step10.json` (O3-S10c).

## Objective 3, Step 11: follow-ups (product in focus)

`harness/focus.py` finds the watch the conversation is about: the newest product code or design name in the
earlier turns. A follow-up is a latest message that names no product and either refers back ("it", "this one",
"iska", "ye") or has 6 words or fewer.
- `--followup-retrieval`: a follow-up is retrieved with the earlier customer turn and the focused watch's name
  added.
- `--focus-memory`: for a follow-up,
  - the focused watch's card is shown as card [1];
  - its code goes to the harness-run tools: the design for colour questions, the named variant otherwise;
  - stock and colour questions go to the stock route;
  - a shopping route inherited from the earlier turn is replaced by the message's own route.

Single-turn cases are unchanged by construction.

`eval/build_followups.py` writes `eval/rag_followups.jsonl`: 60 dev and 60 test two-turn cases (fact, colour,
stock, topic switch; about a third Hinglish), with designs split between dev and test. Colour and stock answers
are scored by polarity (`score_rag.polarity_correct`). `compare_dev.py` reports them by type.

Plan: `obj3_step11.json`.

## Objective 3, Step 12: retrieval speed and RAM

- `retrieval/export_openvino.py` (run once) exports bge-small and MiniLM to `models/ov/`, plus an 8-bit
  re-ranker.
- `retrieval/ov_runtime.py` runs them with the OpenVINO runtime and `tokenizers` only, so PyTorch is never
  imported. The knowledge base uses it as `backend="ovrt"`.
- `retrieval/check_ov_runtime.py` checks that this runtime gives the deployed pipeline's numbers.
- `retrieval/bench_speed.py` times each configuration in its own fresh process: no-PyTorch runtime, 8-bit
  re-ranker, compact cards at 128 tokens, at 4 and 8 threads. It applies the keep rule and writes
  `results_obj3/_speed_step12/choice.json`.
- `retrieval/calibrate_step9.py --choice ... --out ...` re-derives the thresholds for the chosen configuration.
- `--reranker-choice` now also passes backend, 8-bit, length, re-rank view and threads.

Plan: `obj3_step12.json` (the end-to-end check).

## Objective 3, Step 13: generation speed

- `--context-view focused`: a product card keeps its name and range lines plus only the lines the question is
  about (movement; case, glass and water resistance; warranty and origin; variants and prices). If no topic is
  recognised, the card stays compact. The answer check uses the same text.
- `--answer-length`: asks for replies of at most 40 words for a fact and 60 for a recommendation. With
  `max_tokens` 120, a reply cut short ends at its last full sentence.
- `--parallel-tools`: the model may make two tool calls in one round.
- `compare_dev.py` adds paired per-case waits (first word and total, median change with a bootstrap interval) for
  runs made on the same machine.

Plans: `obj3_step13.json` (quality, Vulkan) and `obj3_step13_speed.json` (Tier A in-place timing on CPU).

### Step 13a2

- Focused cards: the watch's own name and collection words are not read as topics ("Tick Digital Grove ki
  keemat" now keeps the price, not the display line). Hinglish price words were added. When the variant lines
  are dropped, a "Variant codes:" line stays, so a reply that names the code is still supported.
- Scorer (`eval/checks.py`): "meters" counts as "metres"; "Rs. 500 and Rs. 900" counts as "Rs. 500 to Rs. 900";
  "isn't specified", "doesn't specify" and "isn't listed" count wherever "not listed" or "don't have" does. Every
  comparison re-scores both runs, so base and new are judged the same way.

Plans: `obj3_step13a2.json` (quality and the 4B leave-one-out runs, Vulkan) and `obj3_step13a2_speed.json`.

### Step 13b: speculative decoding

- Plans `obj3_step13b_tierA.json` (2B, CPU) and `obj3_step13b_tierB.json` (4B, Vulkan): plain decoding first,
  then n-gram drafts (`ngram-simple`, `ngram-mod`), the model's own extra prediction layers (`draft-mtp`; skipped
  if the server will not start with it), on Tier B a Qwen3.5-0.8B draft model, and plain decoding again last.
  Settings are O3-S12's; the 70-case dev speed subset, greedy, 1 repeat.
- `{base}` in `extra_server_args` is the folder above the project (where `models/` lives); a missing draft model
  file is reported before the server starts.
- `run_eval.py` now records drafted and accepted tokens per model request.
- `eval/compare_spec.py` applies the keep rule (identical replies, ≥ 1.2× writing speed, first word and total time
  not later) and picks the fastest qualifier per tier.
- `compare_dev.py` skips pairs whose runs are not finished and lists them at the end of the report.

## Objective 3, Step 14: confirming run on the test set O3-T

- `eval/build_o3_test.py` builds O3-T once (its outputs are shipped; rerunning it gives the same files):
  - tool cases `eval/eval_set_o3t.jsonl` (192): 117 fresh (new seeds, any wording seen before dropped) plus the
    held-out test halves of the discovery and Hinglish categories;
  - store questions `eval/rag_cases_o3t.jsonl` (463): 311 fresh plus the held-out hand-written types;
  - follow-ups: the test half of `eval/rag_followups.jsonl` (60);
  - dialogues: 60 fresh profiles (seed 202) appended to `eval/o3_dialogues.jsonl` as split `test`;
  - `eval/o3t_speed_ids.json`: 40 store + 30 tool cases for Tier A timing.
- `compare_dev.py` adds subsets by origin (fresh / held-out) and for Hinglish, and saves the paired waits in
  `compare.json`.
- `eval/step14_verdicts.py` applies the pre-registered rules (Holm-adjusted primary family, dialogue targets,
  Tier A timing) and writes `results_obj3/_step14/verdicts.md`.

Plans: `obj3_step14.json` (quality, Vulkan, 19 runs) and `obj3_step14_speed.json` (Tier A timing on CPU).

## Objective 5, Steps 2-3: the shared turn engine and per-stage logs

`--engine core` runs the turn through `kiosk_core/engine.py`, the engine the app uses, and adds per-stage timing
and memory to every record (`stages`, `stage_summary`). `--no-stages` turns the stage clock off, and
`--stage-policy sequential` keeps the retrieval models in a worker process from routing to the first model round.
The plan keys are `engine`, `stages` and `stage_policy`. `run_plan.eval_argv_for(cfg, ...)` builds a run's
arguments; the app uses it too. Staff tickets restart at REQ-0001 in every run. See `kiosk_core/README.md`.
