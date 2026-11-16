# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s1_4b_rag_b0 | o3s2_4b_rag_s2 | Qwen3.5-4B | all checked | 135 | 80.7% | 79.3% | -1.5 [-5.2, +2.2] | 5 / 3 | 0.727 | ±2.3 | **tie** |
| o3s1_4b_rag_b0 | o3s2_4b_rag_s2 | Qwen3.5-4B | answerable | 96 | 84.4% | 84.4% | +0.0 [-3.1, +3.1] | 1 / 1 | 1.000 | ±2.7 | **tie** |
| o3s1_4b_rag_b0 | o3s2_4b_rag_s2 | Qwen3.5-4B | unanswerable / near-miss | 39 | 71.8% | 66.7% | -5.1 [-17.9, +7.7] | 4 / 2 | 0.688 | ±4.3 | **tie** |
| o3s1_2b_rag_b0 | o3s2_2b_rag_s2 | Qwen3.5-2B | all checked | 135 | 54.8% | 49.6% | -5.2 [-11.1, +0.7] | 12 / 5 | 0.143 | ±2.3 | **tie** |
| o3s1_2b_rag_b0 | o3s2_2b_rag_s2 | Qwen3.5-2B | answerable | 96 | 59.4% | 51.0% | -8.3 [-15.6, -1.0] | 11 / 3 | 0.057 | ±2.7 | **worse** |
| o3s1_2b_rag_b0 | o3s2_2b_rag_s2 | Qwen3.5-2B | unanswerable / near-miss | 39 | 43.6% | 46.2% | +2.6 [-5.1, +12.8] | 1 / 2 | 1.000 | ±4.3 | **tie** |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | Qwen3.5-4B | tool cases | 60 | 75.0% | 76.7% | +1.7 [-5.0, +8.3] | 2 / 3 | 1.000 | ±0.0 | **tie** |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | Qwen3.5-4B | tool cases: comparison | 2 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | Qwen3.5-4B | tool cases: discovery | 16 | 81.2% | 81.2% | +0.0 [-18.8, +18.8] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 66.7% | -16.7 [-50.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | Qwen3.5-4B | tool cases: hinglish | 9 | 55.6% | 77.8% | +22.2 [+0.0, +55.6] | 0 / 2 | 0.500 | ±0.0 | **(small)** |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | Qwen3.5-4B | tool cases: tool_selection | 19 | 73.7% | 73.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | Qwen3.5-2B | tool cases | 60 | 56.7% | 58.3% | +1.7 [+0.0, +5.0] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | Qwen3.5-2B | tool cases: discovery | 16 | 43.8% | 50.0% | +6.2 [+0.0, +18.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | Qwen3.5-2B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | Qwen3.5-2B | tool cases: hinglish | 9 | 11.1% | 11.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | Qwen3.5-2B | tool cases: refusal | 8 | 75.0% | 75.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | Qwen3.5-2B | tool cases: tool_selection | 19 | 68.4% | 68.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | First word p50 base → new |
|---|---|---|---|---|
| o3s1_4b_rag_b0 | o3s2_4b_rag_s2 | 1.20 → 1.25 | 485 → 494 | 7.3 s → 7.5 s |
| o3s1_2b_rag_b0 | o3s2_2b_rag_s2 | 2.40 → 2.56 | 742 → 761 | 6.8 s → 7.7 s |
| o3s1_4b_v11_b0 | o3s2_4b_v12_s2 | 1.40 → 1.42 | 515 → 536 | 7.4 s → 7.7 s |
| o3s1_2b_v11_b0 | o3s2_2b_v12_s2 | 2.13 → 2.14 | 868 → 886 | 6.3 s → 7.0 s |
