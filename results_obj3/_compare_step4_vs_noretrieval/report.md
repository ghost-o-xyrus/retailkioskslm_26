# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases | 60 | 85.0% | 80.0% | -5.0 [-11.7, +1.7] | 4 / 1 | 0.375 | ±0.0 | **tie** |
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: discovery | 16 | 81.2% | 87.5% | +6.2 [+0.0, +18.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 50.0% | -33.3 [-66.7, +0.0] | 2 / 0 | 0.500 | ±0.0 | **(small)** |
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: hinglish | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 73.7% | -10.5 [-26.3, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases | 60 | 70.0% | 70.0% | +0.0 [-11.7, +11.7] | 7 / 7 | 1.000 | ±0.0 | **tie** |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: discovery | 16 | 62.5% | 87.5% | +25.0 [+6.2, +50.0] | 0 / 4 | 0.125 | ±0.0 | **better** |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: handoff | 6 | 16.7% | 16.7% | +0.0 [-50.0, +50.0] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: hinglish | 9 | 77.8% | 88.9% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: refusal | 8 | 75.0% | 50.0% | -25.0 [-50.0, +0.0] | 2 / 0 | 0.500 | ±0.0 | **(small)** |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | Qwen3.5-2B | tool cases: tool_selection | 19 | 84.2% | 68.4% | -15.8 [-36.8, +5.3] | 4 / 1 | 0.375 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|
| o3s1_4b_v11_none | o3s4_4b_v12_s4 | 1.49 → 1.51 | 345 → 237 | 407 → 151 | 1 → 0 | 1 → 0 | 6.1 s → 7.2 s |
| o3s1_2b_v11_none | o3s4_2b_v12_s4 | 1.64 → 1.63 | 463 → 275 | 481 → 167 | 2 → 0 | 2 → 0 | 4.2 s → 4.1 s |
