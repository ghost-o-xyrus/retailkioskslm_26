# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s4_4b_rag_s4 | o3s5_4b_rag_s5 | Qwen3.5-4B | all checked | 135 | 81.5% | 79.3% | -2.2 [-5.9, +0.7] | 4 / 1 | 0.375 | ±2.3 | **tie** |
| o3s4_4b_rag_s4 | o3s5_4b_rag_s5 | Qwen3.5-4B | answerable | 96 | 84.4% | 85.4% | +1.0 [+0.0, +3.1] | 0 / 1 | 1.000 | ±2.7 | **tie** |
| o3s4_4b_rag_s4 | o3s5_4b_rag_s5 | Qwen3.5-4B | unanswerable / near-miss | 39 | 74.4% | 64.1% | -10.3 [-20.5, -2.6] | 4 / 0 | 0.125 | ±4.3 | **worse** |
| o3s4_2b_rag_s4 | o3s5_2b_rag_s5 | Qwen3.5-2B | all checked | 135 | 62.2% | 27.4% | -34.8 [-43.0, -26.7] | 48 / 1 | 0.000 | ±2.3 | **worse** |
| o3s4_2b_rag_s4 | o3s5_2b_rag_s5 | Qwen3.5-2B | answerable | 96 | 69.8% | 28.1% | -41.7 [-51.0, -31.2] | 40 / 0 | 0.000 | ±2.7 | **worse** |
| o3s4_2b_rag_s4 | o3s5_2b_rag_s5 | Qwen3.5-2B | unanswerable / near-miss | 39 | 43.6% | 25.6% | -17.9 [-33.3, -5.1] | 8 / 1 | 0.039 | ±4.3 | **worse** |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | Qwen3.5-4B | tool cases | 60 | 80.0% | 85.0% | +5.0 [-1.7, +11.7] | 1 / 4 | 0.375 | ±0.0 | **tie** |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | Qwen3.5-4B | tool cases: discovery | 16 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | Qwen3.5-4B | tool cases: handoff | 6 | 50.0% | 100.0% | +50.0 [+16.7, +83.3] | 0 / 3 | 0.250 | ±0.0 | **better** |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | Qwen3.5-4B | tool cases: hinglish | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | Qwen3.5-4B | tool cases: tool_selection | 19 | 73.7% | 73.7% | +0.0 [-15.8, +15.8] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | Qwen3.5-2B | tool cases | 60 | 70.0% | 76.7% | +6.7 [+0.0, +15.0] | 1 / 5 | 0.219 | ±0.0 | **tie** |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | Qwen3.5-2B | tool cases: discovery | 16 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | Qwen3.5-2B | tool cases: handoff | 6 | 16.7% | 100.0% | +83.3 [+50.0, +100.0] | 0 / 5 | 0.062 | ±0.0 | **better** |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | Qwen3.5-2B | tool cases: hinglish | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | Qwen3.5-2B | tool cases: refusal | 8 | 50.0% | 37.5% | -12.5 [-37.5, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | Qwen3.5-2B | tool cases: tool_selection | 19 | 68.4% | 68.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s4sp_a_2b_rag_s4 | o3s5sp_a_2b_rag_s5 | Qwen3.5-2B | all checked | 36 | 55.6% | 25.0% | -30.6 [-44.4, -16.7] | 11 / 0 | 0.001 | ±4.4 | **worse** |
| o3s4sp_a_2b_rag_s4 | o3s5sp_a_2b_rag_s5 | Qwen3.5-2B | answerable | 26 | 61.5% | 23.1% | -38.5 [-57.7, -19.2] | 10 / 0 | 0.002 | ±5.2 | **worse** |
| o3s4sp_a_2b_rag_s4 | o3s5sp_a_2b_rag_s5 | Qwen3.5-2B | unanswerable / near-miss | 10 | 40.0% | 30.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | Qwen3.5-2B | tool cases | 30 | 73.3% | 83.3% | +10.0 [+0.0, +20.0] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | Qwen3.5-2B | tool cases: comparison | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | Qwen3.5-2B | tool cases: discovery | 8 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | Qwen3.5-2B | tool cases: handoff | 3 | 0.0% | 100.0% | +100.0 [+100.0, +100.0] | 0 / 3 | 0.250 | ±0.0 | **better** |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | Qwen3.5-2B | tool cases: hinglish | 4 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | Qwen3.5-2B | tool cases: refusal | 4 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | Qwen3.5-2B | tool cases: tool_selection | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s4_4b_rag_s4 | o3s5_4b_rag_s5 | 1.31 → 1.15 | 422 → 410 | 119 → 88 | 0 → 0 | 0 → 0 | 0/51 → 30/52 | 6.8 s → 7.0 s |
| o3s4_2b_rag_s4 | o3s5_2b_rag_s5 | 2.33 → 1.10 | 525 → 406 | 92 → 78 | 0 → 0 | 0 → 0 | 0/205 → 41/56 | 7.0 s → 3.3 s |
| o3s4_4b_v12_s4 | o3s5_4b_v12_s5 | 1.51 → 1.17 | 237 → 233 | 151 → 152 | 0 → 0 | 0 → 0 | 0/43 → 23/36 | 7.2 s → 3.6 s |
| o3s4_2b_v12_s4 | o3s5_2b_v12_s5 | 1.63 → 1.26 | 275 → 259 | 167 → 163 | 0 → 0 | 0 → 0 | 0/56 → 26/46 | 4.1 s → 2.0 s |
| o3s4sp_a_2b_rag_s4 | o3s5sp_a_2b_rag_s5 | 2.40 → 1.07 | 518 → 389 | 90 → 63 | 0 → 0 | 0 → 0 | 0/56 → 12/15 | 13.9 s → 9.7 s |
| o3s4sp_a_2b_v12_s4 | o3s5sp_a_2b_v12_s5 | 1.67 → 1.30 | 170 → 168 | 182 → 161 | 0 → 0 | 0 → 0 | 0/21 → 12/21 | 4.4 s → 3.0 s |
