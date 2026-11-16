# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s4_4b_rag_s4 | o3s5h_4b_rag_ht | Qwen3.5-4B | all checked | 135 | 81.5% | 81.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.3 | **tie** |
| o3s4_4b_rag_s4 | o3s5h_4b_rag_ht | Qwen3.5-4B | answerable | 96 | 84.4% | 84.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s4_4b_rag_s4 | o3s5h_4b_rag_ht | Qwen3.5-4B | unanswerable / near-miss | 39 | 74.4% | 74.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s4_2b_rag_s4 | o3s5h_2b_rag_ht | Qwen3.5-2B | all checked | 135 | 62.2% | 61.5% | -0.7 [-2.2, +0.0] | 1 / 0 | 1.000 | ±2.3 | **tie** |
| o3s4_2b_rag_s4 | o3s5h_2b_rag_ht | Qwen3.5-2B | answerable | 96 | 69.8% | 68.8% | -1.0 [-3.1, +0.0] | 1 / 0 | 1.000 | ±2.7 | **tie** |
| o3s4_2b_rag_s4 | o3s5h_2b_rag_ht | Qwen3.5-2B | unanswerable / near-miss | 39 | 43.6% | 43.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | Qwen3.5-4B | tool cases | 60 | 80.0% | 83.3% | +3.3 [-3.3, +10.0] | 1 / 3 | 0.625 | ±0.0 | **tie** |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | Qwen3.5-4B | tool cases: discovery | 16 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | Qwen3.5-4B | tool cases: handoff | 6 | 50.0% | 83.3% | +33.3 [+0.0, +66.7] | 0 / 2 | 0.500 | ±0.0 | **(small)** |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | Qwen3.5-4B | tool cases: hinglish | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | Qwen3.5-4B | tool cases: tool_selection | 19 | 73.7% | 73.7% | +0.0 [-15.8, +15.8] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | Qwen3.5-2B | tool cases | 60 | 70.0% | 78.3% | +8.3 [+1.7, +15.0] | 0 / 5 | 0.062 | ±0.0 | **better** |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | Qwen3.5-2B | tool cases: discovery | 16 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | Qwen3.5-2B | tool cases: handoff | 6 | 16.7% | 100.0% | +83.3 [+50.0, +100.0] | 0 / 5 | 0.062 | ±0.0 | **better** |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | Qwen3.5-2B | tool cases: hinglish | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | Qwen3.5-2B | tool cases: refusal | 8 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | Qwen3.5-2B | tool cases: tool_selection | 19 | 68.4% | 68.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s4_4b_rag_s4 | o3s5h_4b_rag_ht | 1.31 → 1.25 | 422 → 423 | 119 → 119 | 0 → 0 | 0 → 0 | 0/51 → 9/50 | 6.8 s → 6.4 s |
| o3s4_2b_rag_s4 | o3s5h_2b_rag_ht | 2.33 → 2.28 | 525 → 527 | 92 → 91 | 0 → 0 | 0 → 0 | 0/205 → 9/207 | 7.0 s → 6.3 s |
| o3s4_4b_v12_s4 | o3s5h_4b_v12_ht | 1.51 → 1.21 | 237 → 237 | 151 → 155 | 0 → 0 | 0 → 0 | 0/43 → 21/37 | 7.2 s → 3.0 s |
| o3s4_2b_v12_s4 | o3s5h_2b_v12_ht | 1.63 → 1.37 | 275 → 279 | 167 → 158 | 0 → 0 | 0 → 0 | 0/56 → 21/56 | 4.1 s → 2.0 s |
