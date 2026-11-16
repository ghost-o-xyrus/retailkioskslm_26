# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s12_4b_rag | o3s13a_4b_rag | Qwen3.5-4B | all checked | 134 | 82.8% | 70.9% | -11.9 [-18.7, -5.2] | 20 / 4 | 0.002 | ±2.3 | **worse** |
| o3s12_4b_rag | o3s13a_4b_rag | Qwen3.5-4B | answerable | 96 | 84.4% | 70.8% | -13.5 [-20.8, -6.2] | 14 / 1 | 0.001 | ±2.7 | **worse** |
| o3s12_4b_rag | o3s13a_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 38 | 78.9% | 71.1% | -7.9 [-23.7, +7.9] | 6 / 3 | 0.508 | ±4.3 | **tie** |
| o3s12_2b_rag | o3s13a_2b_rag | Qwen3.5-2B | all checked | 135 | 71.9% | 68.1% | -3.7 [-8.9, +0.7] | 8 / 3 | 0.227 | ±2.3 | **tie** |
| o3s12_2b_rag | o3s13a_2b_rag | Qwen3.5-2B | answerable | 96 | 76.0% | 71.9% | -4.2 [-10.4, +2.1] | 7 / 3 | 0.344 | ±2.7 | **tie** |
| o3s12_2b_rag | o3s13a_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 61.5% | 59.0% | -2.6 [-7.7, +0.0] | 1 / 0 | 1.000 | ±4.3 | **tie** |
| o3s12_4b_v12 | o3s13a_4b_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 83.3% | -8.3 [-16.7, -1.7] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o3s12_4b_v12 | o3s13a_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_v12 | o3s13a_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 57.9% | -26.3 [-47.4, -5.3] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o3s12_2b_v12 | o3s13a_2b_v12 | Qwen3.5-2B | tool cases | 59 | 84.7% | 84.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_2b_v12 | o3s13a_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_2b_v12 | o3s13a_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 62.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 18 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_fup | o3s13a_4b_fup | Qwen3.5-4B | all checked | 60 | 96.7% | 95.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13a_4b_fup | Qwen3.5-4B | answerable | 60 | 96.7% | 95.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13a_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13a_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3s12_4b_fup | o3s13a_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13a_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_2b_fup | o3s13a_2b_fup | Qwen3.5-2B | all checked | 60 | 86.7% | 80.0% | -6.7 [-16.7, +1.7] | 6 / 2 | 0.289 | ±3.4 | **tie** |
| o3s12_2b_fup | o3s13a_2b_fup | Qwen3.5-2B | answerable | 60 | 86.7% | 80.0% | -6.7 [-16.7, +1.7] | 6 / 2 | 0.289 | ±3.4 | **tie** |
| o3s12_2b_fup | o3s13a_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 80.0% | 60.0% | -20.0 [-50.0, +0.0] | 2 / 0 | 0.500 | ±8.4 | **tie** |
| o3s12_2b_fup | o3s13a_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 86.7% | 83.3% | -3.3 [-16.7, +6.7] | 2 / 1 | 1.000 | ±4.9 | **tie** |
| o3s12_2b_fup | o3s13a_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_2b_fup | o3s13a_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 80.0% | 70.0% | -10.0 [-40.0, +20.0] | 2 / 1 | 1.000 | ±8.4 | **tie** |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | Qwen3.5-2B | all checked | 36 | 77.8% | 72.2% | -5.6 [-19.4, +8.3] | 5 / 3 | 0.727 | ±4.4 | **tie** |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | Qwen3.5-2B | answerable | 26 | 80.8% | 69.2% | -11.5 [-26.9, +3.8] | 4 / 1 | 0.375 | ±5.2 | **tie** |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | Qwen3.5-2B | unanswerable / near-miss | 10 | 70.0% | 80.0% | +10.0 [-20.0, +40.0] | 1 / 2 | 1.000 | ±8.4 | **tie** |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | Qwen3.5-2B | tool cases | 30 | 86.7% | 83.3% | -3.3 [-10.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | Qwen3.5-2B | tool cases: comparison | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | Qwen3.5-2B | tool cases: discovery | 8 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | Qwen3.5-2B | tool cases: handoff | 3 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | Qwen3.5-2B | tool cases: hinglish | 4 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | Qwen3.5-2B | tool cases: refusal | 4 | 75.0% | 50.0% | -25.0 [-75.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | Qwen3.5-2B | tool cases: tool_selection | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 0.93 → 1.14 | 397 → 340 | 130 → 114 | 0 → 9 | 0 → 0 | 27/40 → 39/68 | 5.9 s → 4.1 s |
| o3s12_2b_rag | o3s13a_2b_rag | 2.20 → 1.99 | 517 → 416 | 83 → 86 | 0 → 2 | 0 → 0 | 28/227 → 28/195 | 6.6 s → 5.4 s |
| o3s12_4b_v12 | o3s13a_4b_v12 | 0.90 → 0.95 | 243 → 254 | 119 → 122 | 0 → 5 | 0 → 0 | 38/41 → 43/46 | 3.5 s → 3.5 s |
| o3s12_2b_v12 | o3s13a_2b_v12 | 1.00 → 0.97 | 261 → 244 | 112 → 110 | 0 → 0 | 0 → 0 | 38/55 → 38/47 | 1.4 s → 1.6 s |
| o3s12_4b_fup | o3s13a_4b_fup | 1.02 → 1.13 | 469 → 359 | 106 → 111 | 0 → 2 | 0 → 0 | 21/21 → 25/28 | 7.4 s → 5.2 s |
| o3s12_2b_fup | o3s13a_2b_fup | 1.53 → 1.37 | 510 → 369 | 79 → 85 | 0 → 0 | 0 → 0 | 20/52 → 20/42 | 3.3 s → 2.4 s |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | 2.30 → 1.98 | 524 → 401 | 86 → 76 | 0 → 1 | 0 → 0 | 7/64 → 8/51 | 13.8 s → 9.0 s |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | 0.80 → 0.83 | 152 → 159 | 115 → 119 | 0 → 0 | 0 → 0 | 20/20 → 20/21 | 2.8 s → 2.9 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 150 | +0.01 s [-0.04, +0.26] | -0.78 s [-1.47, -0.07] |
| o3s12_2b_rag | o3s13a_2b_rag | 151 | -0.03 s [-0.18, -0.00] | -0.70 s [-1.23, -0.33] |
| o3s12_4b_v12 | o3s13a_4b_v12 | 78 | -0.06 s [-0.12, -0.03] | -0.32 s [-0.91, -0.21] |
| o3s12_2b_v12 | o3s13a_2b_v12 | 77 | +0.17 s [+0.14, +0.22] | +0.00 s [-0.12, +0.02] |
| o3s12_4b_fup | o3s13a_4b_fup | 60 | -0.36 s [-2.25, -0.09] | -1.09 s [-1.86, -0.41] |
| o3s12_2b_fup | o3s13a_2b_fup | 60 | -0.12 s [-0.59, +0.21] | -0.89 s [-1.14, -0.40] |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | 40 | -2.22 s [-3.71, +0.01] | -3.20 s [-5.21, -0.56] |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | 30 | -0.00 s [-0.03, +0.03] | -0.46 s [-1.04, -0.05] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 0 → 14 | 0 → 9 | 0 → 1 | 0 → 4 | 1 → 7 | 0 → 4 | 27 → 24 | 0 → 0 | 22 → 19 | 0 → 0 |
| o3s12_2b_rag | o3s13a_2b_rag | 2 → 3 | 0 → 2 | 1 → 1 | 1 → 0 | 47 → 34 | 24 → 20 | 13 → 13 | 0 → 0 | 10 → 11 | 0 → 0 |
| o3s12_4b_v12 | o3s13a_4b_v12 | 0 → 6 | 0 → 5 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 | 7 → 6 | 0 → 0 | 4 → 4 | 0 → 0 |
| o3s12_2b_v12 | o3s13a_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 5 | 0 → 0 | 6 → 7 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s12_4b_fup | o3s13a_4b_fup | 1 → 5 | 0 → 2 | 0 → 0 | 1 → 3 | 0 → 0 | 0 → 0 | 2 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |
| o3s12_2b_fup | o3s13a_2b_fup | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 1 → 0 | 4 → 8 | 0 → 0 | 2 → 5 | 0 → 0 |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | 0 → 1 | 0 → 1 | 0 → 0 | 0 → 0 | 15 → 11 | 8 → 7 | 4 → 2 | 0 → 0 | 3 → 2 | 0 → 0 |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 10 → 10 | 8 → 8 | 0 → 5 | 0 → 2 |
| o3s12_2b_rag | o3s13a_2b_rag | 10 → 10 | 8 → 8 | 30 → 25 | 4 → 5 |
| o3s12_4b_v12 | o3s13a_4b_v12 | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o3s12_2b_v12 | o3s13a_2b_v12 | 1 → 1 | 0 → 0 | 2 → 2 | 1 → 0 |
| o3s12_4b_fup | o3s13a_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s12_2b_fup | o3s13a_2b_fup | 0 → 0 | 0 → 0 | 4 → 0 | 3 → 0 |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | 3 → 3 | 2 → 2 | 10 → 7 | 2 → 0 |
| o3s13sp_a_2b_v12_s12 | o3s13sp_a_2b_v12_s13a | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 4/131 (3.1%) → 5/129 (3.9%) | 5 → 3 | 0 → 0 |
| o3s12_2b_rag | o3s13a_2b_rag | 10/131 (7.6%) → 7/129 (5.4%) | 2 → 2 | 0 → 0 |
| o3s12_4b_fup | o3s13a_4b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3s12_2b_fup | o3s13a_2b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 4 | 0 → 0 |
| o3s13sp_a_2b_rag_s12 | o3s13sp_a_2b_rag_s13a | 3/35 (8.6%) → 0/34 (0.0%) | 1 → 0 | 0 → 0 |
