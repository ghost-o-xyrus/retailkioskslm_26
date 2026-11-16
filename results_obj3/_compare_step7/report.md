# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s7a_4b_rag | o3s7_4b_rag | Qwen3.5-4B | all checked | 135 | 80.7% | 81.5% | +0.7 [-4.4, +6.7] | 7 / 8 | 1.000 | ±2.3 | **tie** |
| o3s7a_4b_rag | o3s7_4b_rag | Qwen3.5-4B | answerable | 96 | 83.3% | 87.5% | +4.2 [-1.0, +10.4] | 2 / 6 | 0.289 | ±2.7 | **tie** |
| o3s7a_4b_rag | o3s7_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 74.4% | 66.7% | -7.7 [-20.5, +5.1] | 5 / 2 | 0.453 | ±4.3 | **tie** |
| o3s7a_2b_rag | o3s7_2b_rag | Qwen3.5-2B | all checked | 135 | 64.4% | 68.9% | +4.4 [-0.7, +9.6] | 4 / 10 | 0.180 | ±2.3 | **tie** |
| o3s7a_2b_rag | o3s7_2b_rag | Qwen3.5-2B | answerable | 96 | 69.8% | 76.0% | +6.2 [+1.0, +12.5] | 1 / 7 | 0.070 | ±2.7 | **better** |
| o3s7a_2b_rag | o3s7_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 51.3% | 51.3% | +0.0 [-12.8, +12.8] | 3 / 3 | 1.000 | ±4.3 | **tie** |
| o3s7a_4b_v12 | o3s7_4b_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 88.3% | -3.3 [-10.0, +3.3] | 3 / 1 | 0.625 | ±0.0 | **tie** |
| o3s7a_4b_v12 | o3s7_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s7_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s7a_4b_v12 | o3s7_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 100.0% | +16.7 [+0.0, +50.0] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s7_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s7_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 75.0% | -12.5 [-37.5, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_4b_v12 | o3s7_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 73.7% | -10.5 [-26.3, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3s7a_2b_v12 | o3s7_2b_v12 | Qwen3.5-2B | tool cases | 60 | 81.7% | 88.3% | +6.7 [+1.7, +13.3] | 0 / 4 | 0.125 | ±0.0 | **better** |
| o3s7a_2b_v12 | o3s7_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s7_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s7a_2b_v12 | o3s7_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s7_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s7_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 50.0% | 62.5% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s7a_2b_v12 | o3s7_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 19 | 63.2% | 78.9% | +15.8 [+0.0, +31.6] | 0 / 3 | 0.250 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s7a_4b_rag | o3s7_4b_rag | 1.09 → 1.07 | 420 → 420 | 113 → 89 | 0 → 0 | 0 → 0 | 19/38 → 39/55 | 6.9 s → 6.6 s |
| o3s7a_2b_rag | o3s7_2b_rag | 2.21 → 1.99 | 532 → 523 | 86 → 100 | 0 → 0 | 0 → 0 | 19/206 → 22/173 | 6.2 s → 5.9 s |
| o3s7a_4b_v12 | o3s7_4b_v12 | 0.91 → 0.96 | 244 → 250 | 120 → 114 | 1 → 2 | 0 → 0 | 37/40 → 41/46 | 3.3 s → 3.4 s |
| o3s7a_2b_v12 | o3s7_2b_v12 | 1.00 → 0.97 | 260 → 248 | 113 → 111 | 0 → 0 | 0 → 0 | 37/53 → 38/46 | 1.4 s → 1.4 s |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|
| o3s7a_4b_rag | o3s7_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 5 → 6 | 2 → 3 | 18 → 0 | 0 → 20 |
| o3s7a_2b_rag | o3s7_2b_rag | 6 → 0 | 0 → 0 | 0 → 0 | 6 → 0 | 50 → 30 | 27 → 28 | 4 → 0 | 0 → 3 |
| o3s7a_4b_v12 | o3s7_4b_v12 | 1 → 3 | 1 → 2 | 0 → 0 | 0 → 1 | 0 → 2 | 0 → 0 | 7 → 6 | 0 → 1 |
| o3s7a_2b_v12 | o3s7_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 4 | 0 → 0 | 6 → 5 | 0 → 1 |
