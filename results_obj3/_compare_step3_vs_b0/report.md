# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s1_2b_rag_b0 | o3s3_2b_rag_s3 | Qwen3.5-2B | all checked | 135 | 54.8% | 62.2% | +7.4 [+0.7, +14.1] | 7 / 17 | 0.064 | ±2.3 | **better** |
| o3s1_2b_rag_b0 | o3s3_2b_rag_s3 | Qwen3.5-2B | answerable | 96 | 59.4% | 69.8% | +10.4 [+2.1, +18.8] | 4 / 14 | 0.031 | ±2.7 | **better** |
| o3s1_2b_rag_b0 | o3s3_2b_rag_s3 | Qwen3.5-2B | unanswerable / near-miss | 39 | 43.6% | 43.6% | +0.0 [-12.8, +12.8] | 3 / 3 | 1.000 | ±4.3 | **tie** |
| o3s1sp_a_2b_rag_b0 | o3s3sp_a_2b_rag_s3 | Qwen3.5-2B | all checked | 36 | 44.4% | 55.6% | +11.1 [+0.0, +25.0] | 1 / 5 | 0.219 | ±4.4 | **tie** |
| o3s1sp_a_2b_rag_b0 | o3s3sp_a_2b_rag_s3 | Qwen3.5-2B | answerable | 26 | 42.3% | 61.5% | +19.2 [+3.8, +34.6] | 0 / 5 | 0.062 | ±5.2 | **better** |
| o3s1sp_a_2b_rag_b0 | o3s3sp_a_2b_rag_s3 | Qwen3.5-2B | unanswerable / near-miss | 10 | 50.0% | 40.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | Qwen3.5-2B | tool cases | 30 | 56.7% | 63.3% | +6.7 [-6.7, +20.0] | 1 / 3 | 0.625 | ±0.0 | **tie** |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | Qwen3.5-2B | tool cases: comparison | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | Qwen3.5-2B | tool cases: discovery | 8 | 37.5% | 75.0% | +37.5 [+12.5, +75.0] | 0 / 3 | 0.250 | ±0.0 | **better** |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | Qwen3.5-2B | tool cases: handoff | 3 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | Qwen3.5-2B | tool cases: hinglish | 4 | 0.0% | 0.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | Qwen3.5-2B | tool cases: refusal | 4 | 75.0% | 50.0% | -25.0 [-75.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | Qwen3.5-2B | tool cases: tool_selection | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|
| o3s1_2b_rag_b0 | o3s3_2b_rag_s3 | 2.40 → 2.47 | 742 → 601 | 185 → 85 | 23 → 0 | 23 → 0 | 6.8 s → 9.0 s |
| o3s1sp_a_2b_rag_b0 | o3s3sp_a_2b_rag_s3 | 2.65 → 2.60 | 788 → 608 | 181 → 85 | 12 → 0 | 12 → 0 | 14.8 s → 16.5 s |
| o3s1sp_a_2b_v11_b0 | o3s3sp_a_2b_v12_s3 | 2.47 → 2.37 | 884 → 526 | 352 → 151 | 8 → 0 | 8 → 0 | 12.8 s → 9.4 s |
