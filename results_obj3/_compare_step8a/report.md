# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s7a_4b_rag | o3s8a_4b_rag | Qwen3.5-4B | all checked | 135 | 80.7% | 82.2% | +1.5 [+0.0, +3.7] | 0 / 2 | 0.500 | ±2.3 | **tie** |
| o3s7a_4b_rag | o3s8a_4b_rag | Qwen3.5-4B | answerable | 96 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s7a_4b_rag | o3s8a_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 74.4% | 79.5% | +5.1 [+0.0, +12.8] | 0 / 2 | 0.500 | ±4.3 | **tie** |
| o3s7a_2b_rag | o3s8a_2b_rag | Qwen3.5-2B | all checked | 135 | 64.4% | 65.9% | +1.5 [-1.5, +4.4] | 1 / 3 | 0.625 | ±2.3 | **tie** |
| o3s7a_2b_rag | o3s8a_2b_rag | Qwen3.5-2B | answerable | 96 | 69.8% | 69.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s7a_2b_rag | o3s8a_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 51.3% | 56.4% | +5.1 [-5.1, +15.4] | 1 / 3 | 0.625 | ±4.3 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s7a_4b_rag | o3s8a_4b_rag | 1.09 → 0.93 | 420 → 400 | 113 → 130 | 0 → 0 | 0 → 0 | 19/38 → 27/40 | 6.9 s → 6.1 s |
| o3s7a_2b_rag | o3s8a_2b_rag | 2.21 → 1.98 | 532 → 501 | 86 → 86 | 0 → 0 | 0 → 0 | 19/206 → 27/198 | 6.2 s → 8.4 s |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3s7a_4b_rag | o3s8a_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 5 → 1 | 2 → 0 | 18 → 23 | 0 → 0 | 14 → 19 | 0 → 0 |
| o3s7a_2b_rag | o3s8a_2b_rag | 6 → 4 | 0 → 0 | 0 → 0 | 6 → 4 | 50 → 48 | 27 → 27 | 4 → 9 | 0 → 0 | 0 → 8 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3s7a_4b_rag | o3s8a_4b_rag | 0 → 10 | 0 → 8 | 0 → 0 | 0 → 0 |
| o3s7a_2b_rag | o3s8a_2b_rag | 0 → 10 | 0 → 8 | 0 → 0 | 0 → 0 |
