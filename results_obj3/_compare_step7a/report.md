# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s5h_4b_rag_ht | o3s7a_4b_rag | Qwen3.5-4B | all checked | 135 | 81.5% | 80.7% | -0.7 [-2.2, +0.0] | 1 / 0 | 1.000 | ±2.3 | **tie** |
| o3s5h_4b_rag_ht | o3s7a_4b_rag | Qwen3.5-4B | answerable | 96 | 84.4% | 83.3% | -1.0 [-3.1, +0.0] | 1 / 0 | 1.000 | ±2.7 | **tie** |
| o3s5h_4b_rag_ht | o3s7a_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 74.4% | 74.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s5h_2b_rag_ht | o3s7a_2b_rag | Qwen3.5-2B | all checked | 135 | 61.5% | 64.4% | +3.0 [+0.7, +5.9] | 0 / 4 | 0.125 | ±2.3 | **better** |
| o3s5h_2b_rag_ht | o3s7a_2b_rag | Qwen3.5-2B | answerable | 96 | 68.8% | 69.8% | +1.0 [+0.0, +3.1] | 0 / 1 | 1.000 | ±2.7 | **tie** |
| o3s5h_2b_rag_ht | o3s7a_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 43.6% | 51.3% | +7.7 [+0.0, +17.9] | 0 / 3 | 0.250 | ±4.3 | **tie** |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | Qwen3.5-4B | tool cases | 60 | 83.3% | 91.7% | +8.3 [+1.7, +16.7] | 0 / 5 | 0.062 | ±0.0 | **better** |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 87.5% | 100.0% | +12.5 [+0.0, +31.2] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 88.9% | 100.0% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 73.7% | 84.2% | +10.5 [+0.0, +26.3] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | Qwen3.5-2B | tool cases | 60 | 78.3% | 81.7% | +3.3 [-3.3, +10.0] | 1 / 3 | 0.625 | ±0.0 | **tie** |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 87.5% | 100.0% | +12.5 [+0.0, +31.2] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 88.9% | 100.0% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 19 | 68.4% | 63.2% | -5.3 [-15.8, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3s6c_4b_rag_s6 | o3s7a_4b_rag | Qwen3.5-4B | all checked | 11 | 27.3% | 81.8% | +54.5 [+27.3, +81.8] | 0 / 6 | 0.031 | ±8.0 | **better** |
| o3s6c_4b_rag_s6 | o3s7a_4b_rag | Qwen3.5-4B | answerable | 11 | 27.3% | 81.8% | +54.5 [+27.3, +81.8] | 0 / 6 | 0.031 | ±8.0 | **better** |
| o3s6c_2b_rag_s6 | o3s7a_2b_rag | Qwen3.5-2B | all checked | 11 | 72.7% | 81.8% | +9.1 [+0.0, +27.3] | 0 / 1 | 1.000 | ±8.0 | **tie** |
| o3s6c_2b_rag_s6 | o3s7a_2b_rag | Qwen3.5-2B | answerable | 11 | 72.7% | 81.8% | +9.1 [+0.0, +27.3] | 0 / 1 | 1.000 | ±8.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s5h_4b_rag_ht | o3s7a_4b_rag | 1.25 → 1.09 | 423 → 420 | 119 → 113 | 0 → 0 | 0 → 0 | 9/50 → 19/38 | 6.4 s → 6.9 s |
| o3s5h_2b_rag_ht | o3s7a_2b_rag | 2.28 → 2.21 | 527 → 532 | 91 → 86 | 0 → 0 | 0 → 0 | 9/207 → 19/206 | 6.3 s → 6.2 s |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | 1.21 → 0.91 | 237 → 244 | 155 → 120 | 0 → 1 | 0 → 0 | 21/37 → 37/40 | 3.0 s → 3.3 s |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | 1.37 → 1.00 | 279 → 260 | 158 → 113 | 0 → 0 | 0 → 0 | 21/56 → 37/53 | 2.0 s → 1.4 s |
| o3s6c_4b_rag_s6 | o3s7a_4b_rag | 0.91 → 1.09 | 224 → 420 | 84 → 113 | 6 → 0 | 0 → 0 | 10/10 → 19/38 | 3.1 s → 6.9 s |
| o3s6c_2b_rag_s6 | o3s7a_2b_rag | 0.91 → 2.21 | 224 → 532 | 84 → 86 | 1 → 0 | 0 → 0 | 10/10 → 19/206 | 1.6 s → 6.2 s |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|
| o3s5h_4b_rag_ht | o3s7a_4b_rag | 2 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 5 → 5 | 2 → 2 | 21 → 18 | 0 → 0 |
| o3s5h_2b_rag_ht | o3s7a_2b_rag | 11 → 6 | 0 → 0 | 0 → 0 | 0 → 6 | 46 → 50 | 27 → 27 | 5 → 4 | 0 → 0 |
| o3s5h_4b_v12_ht | o3s7a_4b_v12 | 2 → 1 | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 7 | 0 → 0 |
| o3s5h_2b_v12_ht | o3s7a_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 4 | 0 → 0 | 6 → 6 | 0 → 0 |
| o3s6c_4b_rag_s6 | o3s7a_4b_rag | 6 → 0 | 6 → 0 | 0 → 0 | 0 → 0 | 0 → 5 | 0 → 2 | 1 → 18 | 0 → 0 |
| o3s6c_2b_rag_s6 | o3s7a_2b_rag | 1 → 6 | 1 → 0 | 0 → 0 | 0 → 6 | 0 → 50 | 0 → 27 | 0 → 4 | 0 → 0 |
