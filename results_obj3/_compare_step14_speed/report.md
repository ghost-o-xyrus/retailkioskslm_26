# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | Qwen3.5-2B | all checked | 38 | 55.3% | 71.1% | +15.8 [-2.6, +34.2] | 3 / 9 | 0.146 | ±4.3 | **tie** |
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | Qwen3.5-2B | answerable | 27 | 51.9% | 74.1% | +22.2 [+3.7, +40.7] | 1 / 7 | 0.070 | ±5.1 | **better** |
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | Qwen3.5-2B | unanswerable / near-miss | 11 | 63.6% | 63.6% | +0.0 [-36.4, +36.4] | 2 / 2 | 1.000 | ±8.0 | **tie** |
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | Qwen3.5-2B | language: hinglish | 4 | 50.0% | 50.0% | +0.0 [-75.0, +75.0] | 1 / 1 | 1.000 | ±13.3 | **(small)** |
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | Qwen3.5-2B | origin: fresh | 25 | 56.0% | 68.0% | +12.0 [-12.0, +36.0] | 3 / 6 | 0.508 | ±5.3 | **tie** |
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | Qwen3.5-2B | origin: held-out | 13 | 53.8% | 76.9% | +23.1 [+0.0, +46.2] | 0 / 3 | 0.250 | ±7.4 | **tie** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | tool cases | 30 | 56.7% | 63.3% | +6.7 [-20.0, +33.3] | 8 / 10 | 0.815 | ±0.0 | **tie** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | language: hinglish | 6 | 33.3% | 66.7% | +33.3 [-33.3, +83.3] | 1 / 3 | 0.625 | ±0.0 | **(small)** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | origin: fresh | 18 | 77.8% | 61.1% | -16.7 [-50.0, +16.7] | 6 / 3 | 0.508 | ±0.0 | **tie** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | origin: held-out | 12 | 25.0% | 66.7% | +41.7 [-8.3, +83.3] | 2 / 7 | 0.180 | ±0.0 | **tie** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | tool cases: discovery | 7 | 28.6% | 57.1% | +28.6 [-42.9, +85.7] | 2 / 4 | 0.688 | ±0.0 | **(small)** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | tool cases: handoff | 2 | 50.0% | 100.0% | +50.0 [+0.0, +100.0] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | tool cases: hinglish | 6 | 33.3% | 66.7% | +33.3 [-33.3, +83.3] | 1 / 3 | 0.625 | ±0.0 | **(small)** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | tool cases: refusal | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | Qwen3.5-2B | tool cases: tool_selection | 12 | 75.0% | 50.0% | -25.0 [-66.7, +16.7] | 5 / 2 | 0.453 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | 2.52 → 1.70 | 854 → 386 | 249 → 102 | 11 → 0 | 11 → 0 | 0/72 → 11/44 | 14.8 s → 8.2 s |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | 2.97 → 0.90 | 1281 → 211 | 317 → 121 | 10 → 0 | 10 → 0 | 0/69 → 27/27 | 24.7 s → 4.4 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | 40 | -3.86 s [-12.69, -1.31] | -4.42 s [-10.73, -2.92] |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | 30 | -19.14 s [-24.67, -13.56] | -22.27 s [-29.71, -17.52] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 1 | 14 → 2 | 6 → 1 | 3 → 4 | 0 → 0 | 0 → 4 | 0 → 0 |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 6 → 0 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | 0 → 3 | 0 → 3 | 0 → 2 | 0 → 1 |
| o3tsp_a_2b_v12_b0 | o3tsp_a_2b_v12_final | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3tsp_a_2b_rag_b0 | o3tsp_a_2b_rag_final | 0/0 (0.0%) → 1/32 (3.1%) | 0 → 1 | 0 → 0 |
