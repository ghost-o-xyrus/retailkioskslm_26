# kiosk_core: the turn engine shared by the harness and the app (Objective 5)

| File | What it is |
|---|---|
| `engine.py` | The turn logic (`run_case`, `run_dialogue` and helpers), moved from `harness/run_eval.py`, with the stage clock and the stage-manager hooks. |
| `stages.py` | `StageClock`: per-stage time and memory of one turn; `STAGES`; `HOOKS` for the stage manager. |
| `stage_manager.py` | The `resident` and `sequential` policies; the retrieval worker process and its stand-ins (`KBProxy`, `RouterProxy`). |
| `turn.py` | The app's entry: `Engine.from_plan_run(run_cfg)`, `Session`, `run_turn(session, message, engine, emit)`. |
| `parity.py` | Step 2: legacy against core, case by case, with where each difference starts. |
| `stage_check.py` | Step 3: stage coverage, stage sums, the clock's cost, per-stage medians. |
| `streaming.py` | The app's streamed model requests: token events, markup held back, the same response rebuilt. |
| `stream_check.py` | Step 4: every model request sent plain and streamed, compared; report and the streaming decision. |
| `build_plans.py` | Writes the Step 2, 3 and 4 plans from O3-final's own run settings. |
| `test_core.py` | Tests against the stand-in llama-server: `python -m unittest kiosk_core.test_core` |

## Harness options

- `--engine legacy|core` (plan key `engine`). `legacy` is `harness/run_eval.py`'s own copy and stays the default
  until the Step 2 parity run passes; then `core` becomes the default and the copy is removed.
- `--no-stages` (plan key `"stages": false`): the stage clock off, to measure its cost.
- `--stage-policy resident|sequential` (plan key `stage_policy`, needs `--engine core`).

Every run now starts its staff tickets at REQ-0001, so a run's replies do not depend on how many runs came before
it in the same plan process. Before this, the ticket number in a staff-call result was the only difference
between two identical configurations run one after the other, and the model sees that number.

## Turn records

With `--engine core`, each record (and each kiosk turn of a dialogue) gains:

- `stages`: a list of `{stage, start_ms, ms, info, sub: [{name, ms, ...}], rss_mb, peak_mb}`. The stages are
  `input`, `route`, `retrieval`, `harness_tools`, `model_round`, `model_tools`, `checks` and `output`, and model
  rounds and model tools repeat. Sub-stages include `router`, `bm25`, `dense`, `fuse`, `rerank`, `reading`,
  `writing`, `tool:<name>`, `recovery_request`, `answer_check`, `before_route` and `release`. Memory is in MB per
  process: `server` is llama-server, `app` is this process, `worker` is the retrieval worker.
- `stage_summary`: `by_stage_ms`, `covered_ms`, `unattributed_ms`, `instrumentation_ms` and `after_reply_ms`. The
  last is a worker stop that happens after a reply that needed no model, so the customer does not wait for it.

## Steps 2 and 3 on the laptop

```
python kiosk_core\build_plans.py
python harness\run_plan.py harness\plans\obj5_step2_parity.json
python kiosk_core\parity.py --plan harness\plans\obj5_step2_parity.json
python harness\run_plan.py harness\plans\obj5_step3_stages.json
python kiosk_core\stage_check.py --plan harness\plans\obj5_step3_stages.json
```
Reports: `results_obj5\_parity_step2\report.md` and `results_obj5\_stages_step3\report.md`.

## Step 4 on the laptop (streaming check)

```
python harness\run_plan.py harness\plans\obj5_step4_stream.json
python kiosk_core\stream_check.py --plan harness\plans\obj5_step4_stream.json
```
Report: `results_obj5\_stream_step4\report.md` and `verdict.json`. The real-model app check is `app\smoke_real.py`
(see `app\README.md`).
