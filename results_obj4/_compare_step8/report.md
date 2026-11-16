# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o4s8_2b_base_rag | o4s8_2b_lora_rag | Qwen3.5-2B | all checked | 36 | 75.0% | 86.1% | +11.1 [-2.8, +25.0] | 2 / 6 | 0.289 | ±4.4 | **tie** |
| o4s8_2b_base_rag | o4s8_2b_lora_rag | Qwen3.5-2B | answerable | 26 | 73.1% | 80.8% | +7.7 [-11.5, +26.9] | 2 / 4 | 0.688 | ±5.2 | **tie** |
| o4s8_2b_base_rag | o4s8_2b_lora_rag | Qwen3.5-2B | unanswerable / near-miss | 10 | 80.0% | 100.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±8.4 | **tie** |
| o4s8_2b_base_rag | o4s8_2b_lora_rag | Qwen3.5-2B | language: hinglish | 4 | 75.0% | 50.0% | -25.0 [-75.0, +0.0] | 1 / 0 | 1.000 | ±13.3 | **(small)** |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | Qwen3.5-2B | all checked | 36 | 75.0% | 86.1% | +11.1 [-2.8, +25.0] | 2 / 6 | 0.289 | ±4.4 | **tie** |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | Qwen3.5-2B | answerable | 26 | 73.1% | 80.8% | +7.7 [-11.5, +26.9] | 2 / 4 | 0.688 | ±5.2 | **tie** |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | Qwen3.5-2B | unanswerable / near-miss | 10 | 80.0% | 100.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±8.4 | **tie** |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | Qwen3.5-2B | language: hinglish | 4 | 75.0% | 50.0% | -25.0 [-75.0, +0.0] | 1 / 0 | 1.000 | ±13.3 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | tool cases | 30 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | language: hinglish | 5 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | tool cases: comparison | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | tool cases: discovery | 8 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | tool cases: handoff | 3 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | tool cases: hinglish | 4 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | tool cases: refusal | 4 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | Qwen3.5-2B | tool cases: tool_selection | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | tool cases | 29 | 82.8% | 86.2% | +3.4 [-6.9, +13.8] | 1 / 2 | 1.000 | ±0.0 | **tie** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | language: hinglish | 5 | 100.0% | 80.0% | -20.0 [-60.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | tool cases: comparison | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | tool cases: discovery | 8 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | tool cases: handoff | 3 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | tool cases: hinglish | 4 | 100.0% | 75.0% | -25.0 [-75.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | tool cases: refusal | 3 | 33.3% | 66.7% | +33.3 [+0.0, +100.0] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | Qwen3.5-2B | tool cases: tool_selection | 10 | 70.0% | 80.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | all checked | 135 | 85.2% | 86.7% | +1.5 [-4.4, +7.4] | 7 / 9 | 0.804 | ±2.3 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | answerable | 96 | 85.4% | 81.2% | -4.2 [-10.4, +2.1] | 7 / 3 | 0.344 | ±2.7 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 84.6% | 100.0% | +15.4 [+5.1, +28.2] | 0 / 6 | 0.031 | ±4.3 | **better** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 95.0% | +3.3 [+0.0, +8.3] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 89.5% | +5.3 [+0.0, +15.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | all checked | 60 | 93.3% | 88.3% | -5.0 [-13.3, +3.3] | 5 / 2 | 0.453 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | answerable | 60 | 93.3% | 88.3% | -5.0 [-13.3, +3.3] | 5 / 2 | 0.453 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | language: hinglish | 22 | 86.4% | 86.4% | +0.0 [-18.2, +18.2] | 2 / 2 | 1.000 | ±5.7 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 40.0% | -50.0 [-80.0, -20.0] | 5 / 0 | 0.062 | ±8.4 | **worse** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o4s8_2b_base_rag | o4s8_2b_lora_rag | 2.02 → 0.88 | 427 → 314 | 82 → 154 | 1 → 0 | 0 → 0 | 8/53 → 7/7 | 9.2 s → 5.2 s |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | 2.02 → 0.88 | 427 → 311 | 82 → 154 | 1 → 0 | 0 → 0 | 8/53 → 7/7 | 9.2 s → 5.1 s |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | 0.83 → 0.83 | 159 → 161 | 119 → 119 | 0 → 0 | 0 → 0 | 20/21 → 20/21 | 3.7 s → 6.2 s |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | 0.83 → 0.83 | 159 → 209 | 119 → 119 | 0 → 0 | 0 → 0 | 20/21 → 20/21 | 3.7 s → 8.9 s |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 0.94 → 0.88 | 326 → 311 | 132 → 130 | 0 → 0 | 0 → 0 | 27/41 → 27/28 | 4.3 s → 5.4 s |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 0.90 → 0.86 | 243 → 228 | 119 → 121 | 0 → 0 | 0 → 0 | 38/41 → 38/38 | 3.6 s → 3.8 s |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 1.13 → 1.02 | 374 → 354 | 102 → 109 | 2 → 0 | 0 → 0 | 22/28 → 20/21 | 5.6 s → 6.5 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o4s8_2b_base_rag | o4s8_2b_lora_rag | 40 | -2.51 s [-6.52, -0.02] | -2.25 s [-6.45, -0.10] |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | 40 | -2.24 s [-5.96, -0.06] | -2.01 s [-5.80, -0.40] |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | 30 | -0.77 s [-1.58, -0.01] | -0.87 s [-2.00, -0.00] |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | 30 | +3.31 s [+0.01, +3.97] | +2.65 s [+0.01, +4.17] |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 151 | +0.52 s [+0.38, +0.81] | -0.86 s [-1.56, -0.05] |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 78 | +0.23 s [+0.10, +0.33] | -0.19 s [-0.82, +0.00] |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 60 | +0.81 s [+0.69, +0.99] | +1.31 s [+0.63, +2.09] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o4s8_2b_base_rag | o4s8_2b_lora_rag | 1 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 11 → 0 | 7 → 0 | 3 → 9 | 0 → 0 | 3 → 9 | 0 → 0 |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | 1 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 11 → 0 | 7 → 0 | 3 → 10 | 0 → 0 | 3 → 10 | 0 → 0 |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 1 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 27 → 32 | 0 → 0 | 22 → 32 | 0 → 0 |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 9 | 0 → 0 | 4 → 9 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 3 → 0 | 2 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 2 → 5 | 0 → 0 | 1 → 5 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o4s8_2b_base_rag | o4s8_2b_lora_rag | 3 → 3 | 2 → 2 | 8 → 0 | 1 → 0 |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | 3 → 3 | 2 → 2 | 8 → 0 | 1 → 0 |
| o4s8_2b_base_v12 | o4s8_2b_lora_v12 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s8_2b_base_v12 | o4s8_2b_lora_off_v12 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o4s8_2b_base_rag | o4s8_2b_lora_rag | 0/34 (0.0%) → 0/35 (0.0%) | 1 → 0 | 0 → 0 |
| o4s8_2b_base_rag | o4s8_2b_lora_off_rag | 0/34 (0.0%) → 0/35 (0.0%) | 1 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 3/131 (2.3%) → 0/131 (0.0%) | 3 → 0 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 0/38 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
