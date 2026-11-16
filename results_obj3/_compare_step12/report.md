# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s10v_4b_rag | o3s12_4b_rag | Qwen3.5-4B | all checked | 135 | 83.0% | 83.0% | +0.0 [-3.0, +3.0] | 2 / 2 | 1.000 | ±2.3 | **tie** |
| o3s10v_4b_rag | o3s12_4b_rag | Qwen3.5-4B | answerable | 96 | 83.3% | 84.4% | +1.0 [-2.1, +4.2] | 1 / 2 | 1.000 | ±2.7 | **tie** |
| o3s10v_4b_rag | o3s12_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 82.1% | 79.5% | -2.6 [-7.7, +0.0] | 1 / 0 | 1.000 | ±4.3 | **tie** |
| o3s10v_2b_rag | o3s12_2b_rag | Qwen3.5-2B | all checked | 135 | 70.4% | 71.9% | +1.5 [+0.0, +3.7] | 0 / 2 | 0.500 | ±2.3 | **tie** |
| o3s10v_2b_rag | o3s12_2b_rag | Qwen3.5-2B | answerable | 96 | 74.0% | 76.0% | +2.1 [+0.0, +5.2] | 0 / 2 | 0.500 | ±2.7 | **tie** |
| o3s10v_2b_rag | o3s12_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 61.5% | 61.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s11b_4b_v12 | o3s12_4b_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 91.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s11b_4b_v12 | o3s12_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_4b_v12 | o3s12_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s11b_4b_v12 | o3s12_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_4b_v12 | o3s12_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_4b_v12 | o3s12_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_4b_v12 | o3s12_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 84.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s11b_2b_v12 | o3s12_2b_v12 | Qwen3.5-2B | tool cases | 60 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s11b_2b_v12 | o3s12_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_2b_v12 | o3s12_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s11b_2b_v12 | o3s12_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_2b_v12 | o3s12_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_2b_v12 | o3s12_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 62.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s11b_2b_v12 | o3s12_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 19 | 63.2% | 63.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s11b_4b_fup | o3s12_4b_fup | Qwen3.5-4B | all checked | 60 | 98.3% | 96.7% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s11b_4b_fup | o3s12_4b_fup | Qwen3.5-4B | answerable | 60 | 98.3% | 96.7% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s11b_4b_fup | o3s12_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s11b_4b_fup | o3s12_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3s11b_4b_fup | o3s12_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s11b_4b_fup | o3s12_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 90.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3s11b_2b_fup | o3s12_2b_fup | Qwen3.5-2B | all checked | 60 | 86.7% | 86.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3s11b_2b_fup | o3s12_2b_fup | Qwen3.5-2B | answerable | 60 | 86.7% | 86.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3s11b_2b_fup | o3s12_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s11b_2b_fup | o3s12_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 86.7% | 86.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3s11b_2b_fup | o3s12_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s11b_2b_fup | o3s12_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s10v_4b_rag | o3s12_4b_rag | 0.93 → 0.93 | 400 → 397 | 130 → 130 | 0 → 0 | 0 → 0 | 27/40 → 27/40 | 6.1 s → 5.9 s |
| o3s10v_2b_rag | o3s12_2b_rag | 2.21 → 2.20 | 517 → 517 | 78 → 83 | 0 → 0 | 0 → 0 | 27/233 → 28/227 | 9.0 s → 6.6 s |
| o3s11b_4b_v12 | o3s12_4b_v12 | 0.90 → 0.90 | 243 → 243 | 120 → 119 | 1 → 0 | 0 → 0 | 38/41 → 38/41 | 3.0 s → 3.5 s |
| o3s11b_2b_v12 | o3s12_2b_v12 | 1.00 → 1.00 | 261 → 261 | 112 → 112 | 0 → 0 | 0 → 0 | 38/55 → 38/55 | 1.4 s → 1.4 s |
| o3s11b_4b_fup | o3s12_4b_fup | 1.02 → 1.02 | 474 → 469 | 106 → 106 | 0 → 0 | 0 → 0 | 21/21 → 21/21 | 6.7 s → 7.4 s |
| o3s11b_2b_fup | o3s12_2b_fup | 1.50 → 1.53 | 513 → 510 | 80 → 79 | 0 → 0 | 0 → 0 | 20/50 → 20/52 | 3.5 s → 3.3 s |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3s10v_4b_rag | o3s12_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 0 | 28 → 27 | 0 → 0 | 24 → 22 | 0 → 0 |
| o3s10v_2b_rag | o3s12_2b_rag | 1 → 2 | 0 → 0 | 1 → 1 | 0 → 1 | 52 → 47 | 26 → 24 | 13 → 13 | 0 → 0 | 10 → 10 | 0 → 0 |
| o3s11b_4b_v12 | o3s12_4b_v12 | 1 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 7 | 0 → 0 | 4 → 4 | 0 → 0 |
| o3s11b_2b_v12 | o3s12_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 4 | 0 → 0 | 6 → 6 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s11b_4b_fup | o3s12_4b_fup | 1 → 1 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 | 1 → 2 | 0 → 0 | 1 → 1 | 0 → 0 |
| o3s11b_2b_fup | o3s12_2b_fup | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 | 1 → 1 | 1 → 1 | 4 → 4 | 0 → 0 | 2 → 2 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3s10v_4b_rag | o3s12_4b_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o3s10v_2b_rag | o3s12_2b_rag | 10 → 10 | 8 → 8 | 31 → 30 | 3 → 4 |
| o3s11b_4b_v12 | o3s12_4b_v12 | 1 → 1 | 0 → 0 | 0 → 1 | 0 → 1 |
| o3s11b_2b_v12 | o3s12_2b_v12 | 1 → 1 | 0 → 0 | 2 → 2 | 1 → 1 |
| o3s11b_4b_fup | o3s12_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s11b_2b_fup | o3s12_2b_fup | 0 → 0 | 0 → 0 | 4 → 4 | 3 → 3 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3s10v_4b_rag | o3s12_4b_rag | 4/131 (3.1%) → 4/131 (3.1%) | 5 → 5 | 0 → 0 |
| o3s10v_2b_rag | o3s12_2b_rag | 12/131 (9.2%) → 10/131 (7.6%) | 2 → 2 | 1 → 0 |
| o3s11b_4b_fup | o3s12_4b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3s11b_2b_fup | o3s12_2b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 1 → 0 |
