# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s3_4b_rag_s3 | o3s4_4b_rag_s4 | Qwen3.5-4B | all checked | 135 | 81.5% | 81.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.3 | **tie** |
| o3s3_4b_rag_s3 | o3s4_4b_rag_s4 | Qwen3.5-4B | answerable | 96 | 84.4% | 84.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s3_4b_rag_s3 | o3s4_4b_rag_s4 | Qwen3.5-4B | unanswerable / near-miss | 39 | 74.4% | 74.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s3_2b_rag_s3 | o3s4_2b_rag_s4 | Qwen3.5-2B | all checked | 135 | 62.2% | 62.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.3 | **tie** |
| o3s3_2b_rag_s3 | o3s4_2b_rag_s4 | Qwen3.5-2B | answerable | 96 | 69.8% | 69.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s3_2b_rag_s3 | o3s4_2b_rag_s4 | Qwen3.5-2B | unanswerable / near-miss | 39 | 43.6% | 43.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases | 60 | 75.0% | 80.0% | +5.0 [-5.0, +15.0] | 3 / 6 | 0.508 | ±0.0 | **tie** |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: comparison | 2 | 50.0% | 100.0% | +50.0 [+0.0, +100.0] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: discovery | 16 | 81.2% | 87.5% | +6.2 [+0.0, +18.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 50.0% | -33.3 [-66.7, +0.0] | 2 / 0 | 0.500 | ±0.0 | **(small)** |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: hinglish | 9 | 55.6% | 88.9% | +33.3 [+0.0, +66.7] | 0 / 3 | 0.250 | ±0.0 | **(small)** |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: tool_selection | 19 | 73.7% | 73.7% | +0.0 [-15.8, +15.8] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases | 60 | 61.7% | 70.0% | +8.3 [-1.7, +18.3] | 3 / 8 | 0.227 | ±0.0 | **tie** |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: discovery | 16 | 68.8% | 87.5% | +18.8 [+0.0, +37.5] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: handoff | 6 | 66.7% | 16.7% | -50.0 [-83.3, -16.7] | 3 / 0 | 0.250 | ±0.0 | **worse** |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: hinglish | 9 | 33.3% | 88.9% | +55.6 [+22.2, +88.9] | 0 / 5 | 0.062 | ±0.0 | **better** |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: refusal | 8 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: tool_selection | 19 | 68.4% | 68.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s3sp_a_2b_rag_s3 | o3s4sp_a_2b_rag_s4 | Qwen3.5-2B | all checked | 36 | 55.6% | 55.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.4 | **tie** |
| o3s3sp_a_2b_rag_s3 | o3s4sp_a_2b_rag_s4 | Qwen3.5-2B | answerable | 26 | 61.5% | 61.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3s3sp_a_2b_rag_s3 | o3s4sp_a_2b_rag_s4 | Qwen3.5-2B | unanswerable / near-miss | 10 | 40.0% | 40.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | Qwen3.5-2B | tool cases | 30 | 63.3% | 73.3% | +10.0 [-10.0, +30.0] | 3 / 6 | 0.508 | ±0.0 | **tie** |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | Qwen3.5-2B | tool cases: comparison | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | Qwen3.5-2B | tool cases: discovery | 8 | 75.0% | 100.0% | +25.0 [+0.0, +62.5] | 0 / 2 | 0.500 | ±0.0 | **(small)** |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | Qwen3.5-2B | tool cases: handoff | 3 | 100.0% | 0.0% | -100.0 [-100.0, -100.0] | 3 / 0 | 0.250 | ±0.0 | **worse** |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | Qwen3.5-2B | tool cases: hinglish | 4 | 0.0% | 100.0% | +100.0 [+100.0, +100.0] | 0 / 4 | 0.125 | ±0.0 | **better** |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | Qwen3.5-2B | tool cases: refusal | 4 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | Qwen3.5-2B | tool cases: tool_selection | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|
| o3s3_4b_rag_s3 | o3s4_4b_rag_s4 | 1.23 → 1.31 | 475 → 422 | 91 → 119 | 0 → 0 | 0 → 0 | 7.3 s → 6.8 s |
| o3s3_2b_rag_s3 | o3s4_2b_rag_s4 | 2.47 → 2.33 | 601 → 525 | 85 → 92 | 0 → 0 | 0 → 0 | 9.0 s → 7.0 s |
| o3s3_4b_v12_s3 | o3s4_4b_v12_s4 | 1.45 → 1.51 | 422 → 237 | 132 → 151 | 0 → 0 | 0 → 0 | 7.7 s → 7.2 s |
| o3s3_2b_v12_s3 | o3s4_2b_v12_s4 | 2.09 → 1.63 | 558 → 275 | 157 → 167 | 0 → 0 | 0 → 0 | 6.1 s → 4.1 s |
| o3s3sp_a_2b_rag_s3 | o3s4sp_a_2b_rag_s4 | 2.60 → 2.40 | 608 → 518 | 85 → 90 | 0 → 0 | 0 → 0 | 16.5 s → 13.9 s |
| o3s3sp_a_2b_v12_s3 | o3s4sp_a_2b_v12_s4 | 2.37 → 1.67 | 526 → 170 | 151 → 182 | 0 → 0 | 0 → 0 | 9.4 s → 4.4 s |
