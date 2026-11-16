# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s8_4b_rag | o3s10v_4b_rag | Qwen3.5-4B | all checked | 135 | 82.2% | 83.0% | +0.7 [+0.0, +2.2] | 0 / 1 | 1.000 | ±2.3 | **tie** |
| o3s8_4b_rag | o3s10v_4b_rag | Qwen3.5-4B | answerable | 96 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s8_4b_rag | o3s10v_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 79.5% | 82.1% | +2.6 [+0.0, +7.7] | 0 / 1 | 1.000 | ±4.3 | **tie** |
| o3s8_2b_rag | o3s10v_2b_rag | Qwen3.5-2B | all checked | 135 | 68.9% | 70.4% | +1.5 [+0.0, +3.7] | 0 / 2 | 0.500 | ±2.3 | **tie** |
| o3s8_2b_rag | o3s10v_2b_rag | Qwen3.5-2B | answerable | 96 | 74.0% | 74.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s8_2b_rag | o3s10v_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 56.4% | 61.5% | +5.1 [+0.0, +12.8] | 0 / 2 | 0.500 | ±4.3 | **tie** |
| o3s8_4b_v12 | o3s10v_4b_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 91.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_4b_v12 | o3s10v_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10v_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_4b_v12 | o3s10v_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10v_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10v_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10v_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 84.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_2b_v12 | o3s10v_2b_v12 | Qwen3.5-2B | tool cases | 60 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_2b_v12 | o3s10v_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10v_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_2b_v12 | o3s10v_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10v_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10v_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 62.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10v_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 19 | 63.2% | 63.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_4b_rag | o3s10c_4b_rag | Qwen3.5-4B | all checked | 135 | 82.2% | 54.1% | -28.1 [-37.8, -18.5] | 46 / 8 | 0.000 | ±2.3 | **worse** |
| o3s8_4b_rag | o3s10c_4b_rag | Qwen3.5-4B | answerable | 96 | 83.3% | 36.5% | -46.9 [-57.3, -36.5] | 46 / 1 | 0.000 | ±2.7 | **worse** |
| o3s8_4b_rag | o3s10c_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 79.5% | 97.4% | +17.9 [+7.7, +30.8] | 0 / 7 | 0.016 | ±4.3 | **better** |
| o3s8_2b_rag | o3s10c_2b_rag | Qwen3.5-2B | all checked | 135 | 68.9% | 42.2% | -26.7 [-37.8, -15.6] | 51 / 15 | 0.000 | ±2.3 | **worse** |
| o3s8_2b_rag | o3s10c_2b_rag | Qwen3.5-2B | answerable | 96 | 74.0% | 20.8% | -53.1 [-62.5, -42.7] | 51 / 0 | 0.000 | ±2.7 | **worse** |
| o3s8_2b_rag | o3s10c_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 56.4% | 94.9% | +38.5 [+23.1, +53.8] | 0 / 15 | 0.000 | ±4.3 | **better** |
| o3s8_4b_v12 | o3s10c_4b_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 90.0% | -1.7 [-8.3, +3.3] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3s8_4b_v12 | o3s10c_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10c_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_4b_v12 | o3s10c_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10c_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10c_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [-37.5, +37.5] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s8_4b_v12 | o3s10c_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 78.9% | -5.3 [-15.8, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_2b_v12 | o3s10c_2b_v12 | Qwen3.5-2B | tool cases | 60 | 83.3% | 88.3% | +5.0 [-1.7, +11.7] | 1 / 4 | 0.375 | ±0.0 | **tie** |
| o3s8_2b_v12 | o3s10c_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10c_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s8_2b_v12 | o3s10c_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10c_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10c_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 75.0% | +12.5 [-25.0, +50.0] | 1 / 2 | 1.000 | ±0.0 | **(small)** |
| o3s8_2b_v12 | o3s10c_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 19 | 63.2% | 73.7% | +10.5 [+0.0, +26.3] | 0 / 2 | 0.500 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s8_4b_rag | o3s10v_4b_rag | 0.93 → 0.93 | 400 → 400 | 130 → 130 | 0 → 0 | 0 → 0 | 27/40 → 27/40 | 6.1 s → 6.1 s |
| o3s8_2b_rag | o3s10v_2b_rag | 2.21 → 2.21 | 517 → 517 | 78 → 78 | 0 → 0 | 0 → 0 | 27/233 → 27/233 | 9.0 s → 9.0 s |
| o3s8_4b_v12 | o3s10v_4b_v12 | 0.90 → 0.90 | 243 → 243 | 120 → 120 | 1 → 1 | 0 → 0 | 38/41 → 38/41 | 4.2 s → 4.2 s |
| o3s8_2b_v12 | o3s10v_2b_v12 | 1.00 → 1.00 | 261 → 261 | 112 → 112 | 0 → 0 | 0 → 0 | 38/55 → 38/55 | 1.8 s → 1.8 s |
| o3s8_4b_rag | o3s10c_4b_rag | 0.93 → 1.05 | 400 → 401 | 130 → 84 | 0 → 0 | 0 → 0 | 27/40 → 27/54 | 6.1 s → 5.8 s |
| o3s8_2b_rag | o3s10c_2b_rag | 2.21 → 2.28 | 517 → 525 | 78 → 79 | 0 → 2 | 0 → 0 | 27/233 → 29/244 | 9.0 s → 7.5 s |
| o3s8_4b_v12 | o3s10c_4b_v12 | 0.90 → 0.91 | 243 → 244 | 120 → 118 | 1 → 0 | 0 → 0 | 38/41 → 38/42 | 4.2 s → 3.3 s |
| o3s8_2b_v12 | o3s10c_2b_v12 | 1.00 → 0.99 | 261 → 260 | 112 → 109 | 0 → 0 | 0 → 0 | 38/55 → 38/56 | 1.8 s → 1.6 s |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3s8_4b_rag | o3s10v_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 0 | 23 → 28 | 0 → 0 | 19 → 24 | 0 → 0 |
| o3s8_2b_rag | o3s10v_2b_rag | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 | 52 → 52 | 26 → 26 | 11 → 13 | 0 → 0 | 8 → 10 | 0 → 0 |
| o3s8_4b_v12 | o3s10v_4b_v12 | 1 → 1 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 7 | 0 → 0 | 4 → 4 | 0 → 0 |
| o3s8_2b_v12 | o3s10v_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 4 | 0 → 0 | 6 → 6 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s8_4b_rag | o3s10c_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 11 | 0 → 5 | 23 → 77 | 0 → 0 | 19 → 75 | 0 → 0 |
| o3s8_2b_rag | o3s10c_2b_rag | 1 → 4 | 0 → 2 | 1 → 1 | 0 → 1 | 52 → 60 | 26 → 30 | 11 → 77 | 0 → 0 | 8 → 75 | 0 → 0 |
| o3s8_4b_v12 | o3s10c_4b_v12 | 1 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 0 → 1 | 0 → 0 | 7 → 10 | 0 → 0 | 4 → 8 | 0 → 0 |
| o3s8_2b_v12 | o3s10c_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 4 | 0 → 0 | 6 → 10 | 0 → 0 | 0 → 4 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3s8_4b_rag | o3s10v_4b_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o3s8_2b_rag | o3s10v_2b_rag | 10 → 10 | 8 → 8 | 31 → 31 | 3 → 3 |
| o3s8_4b_v12 | o3s10v_4b_v12 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s8_2b_v12 | o3s10v_2b_v12 | 1 → 1 | 0 → 0 | 2 → 2 | 1 → 1 |
| o3s8_4b_rag | o3s10c_4b_rag | 10 → 10 | 8 → 8 | 0 → 10 | 0 → 3 |
| o3s8_2b_rag | o3s10c_2b_rag | 10 → 10 | 8 → 8 | 31 → 33 | 3 → 2 |
| o3s8_4b_v12 | o3s10c_4b_v12 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s8_2b_v12 | o3s10c_2b_v12 | 1 → 1 | 0 → 0 | 2 → 1 | 1 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3s8_4b_rag | o3s10v_4b_rag | 9/131 (6.9%) → 4/131 (3.1%) | 0 → 5 | 0 → 0 |
| o3s8_2b_rag | o3s10v_2b_rag | 14/131 (10.7%) → 12/131 (9.2%) | 0 → 2 | 0 → 1 |
| o3s8_4b_rag | o3s10c_4b_rag | 9/131 (6.9%) → 1/131 (0.8%) | 0 → 70 | 0 → 36 |
| o3s8_2b_rag | o3s10c_2b_rag | 14/131 (10.7%) → 1/129 (0.8%) | 0 → 89 | 0 → 9 |
