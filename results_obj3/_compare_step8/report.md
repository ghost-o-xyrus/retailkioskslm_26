# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s8a_4b_rag | o3s8_4b_rag | Qwen3.5-4B | all checked | 135 | 82.2% | 82.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.3 | **tie** |
| o3s8a_4b_rag | o3s8_4b_rag | Qwen3.5-4B | answerable | 96 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s8a_4b_rag | o3s8_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 79.5% | 79.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s8a_2b_rag | o3s8_2b_rag | Qwen3.5-2B | all checked | 135 | 65.9% | 68.9% | +3.0 [+0.7, +5.9] | 0 / 4 | 0.125 | ±2.3 | **better** |
| o3s8a_2b_rag | o3s8_2b_rag | Qwen3.5-2B | answerable | 96 | 69.8% | 74.0% | +4.2 [+1.0, +8.3] | 0 / 4 | 0.125 | ±2.7 | **better** |
| o3s8a_2b_rag | o3s8_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 56.4% | 56.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s7a_4b_v12 | o3s8_4b_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 91.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s7a_4b_v12 | o3s8_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s8_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s7a_4b_v12 | o3s8_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s8_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s8_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s8_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 84.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s7a_2b_v12 | o3s8_2b_v12 | Qwen3.5-2B | tool cases | 60 | 81.7% | 83.3% | +1.7 [+0.0, +5.0] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3s7a_2b_v12 | o3s8_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s8_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s7a_2b_v12 | o3s8_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s8_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s8_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 50.0% | 62.5% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s8_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 19 | 63.2% | 63.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s8a_4b_rag | o3s8_4b_rag | 0.93 → 0.93 | 400 → 400 | 130 → 130 | 0 → 0 | 0 → 0 | 27/40 → 27/40 | 6.1 s → 6.1 s |
| o3s8a_2b_rag | o3s8_2b_rag | 1.98 → 2.21 | 501 → 517 | 86 → 78 | 0 → 0 | 0 → 0 | 27/198 → 27/233 | 8.4 s → 9.0 s |
| o3s7a_4b_v12 | o3s8_4b_v12 | 0.91 → 0.90 | 244 → 243 | 120 → 120 | 1 → 1 | 0 → 0 | 37/40 → 38/41 | 3.3 s → 4.2 s |
| o3s7a_2b_v12 | o3s8_2b_v12 | 1.00 → 1.00 | 260 → 261 | 113 → 112 | 0 → 0 | 0 → 0 | 37/53 → 38/55 | 1.4 s → 1.8 s |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3s8a_4b_rag | o3s8_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 0 | 23 → 23 | 0 → 0 | 19 → 19 | 0 → 0 |
| o3s8a_2b_rag | o3s8_2b_rag | 4 → 1 | 0 → 0 | 0 → 1 | 4 → 0 | 48 → 52 | 27 → 26 | 9 → 11 | 0 → 0 | 8 → 8 | 0 → 0 |
| o3s7a_4b_v12 | o3s8_4b_v12 | 1 → 1 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 7 | 0 → 0 | 4 → 4 | 0 → 0 |
| o3s7a_2b_v12 | o3s8_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 4 | 0 → 0 | 6 → 6 | 0 → 0 | 0 → 0 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3s8a_4b_rag | o3s8_4b_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o3s8a_2b_rag | o3s8_2b_rag | 10 → 10 | 8 → 8 | 0 → 31 | 0 → 3 |
| o3s7a_4b_v12 | o3s8_4b_v12 | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s7a_2b_v12 | o3s8_2b_v12 | 0 → 1 | 0 → 0 | 0 → 2 | 0 → 1 |
