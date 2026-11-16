# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s5h_4b_rag_ht | o3s6_4b_rag_s6 | Qwen3.5-4B | all checked | 11 | 90.9% | 63.6% | -27.3 [-54.5, -9.1] | 3 / 0 | 0.250 | ±8.0 | **worse** |
| o3s5h_4b_rag_ht | o3s6_4b_rag_s6 | Qwen3.5-4B | answerable | 11 | 90.9% | 63.6% | -27.3 [-54.5, -9.1] | 3 / 0 | 0.250 | ±8.0 | **worse** |
| o3s5h_2b_rag_ht | o3s6_2b_rag_s6 | Qwen3.5-2B | all checked | 11 | 81.8% | 63.6% | -18.2 [-45.5, +0.0] | 2 / 0 | 0.500 | ±8.0 | **tie** |
| o3s5h_2b_rag_ht | o3s6_2b_rag_s6 | Qwen3.5-2B | answerable | 11 | 81.8% | 63.6% | -18.2 [-45.5, +0.0] | 2 / 0 | 0.500 | ±8.0 | **tie** |
| o3s5h_4b_v12_ht | o3s6_4b_v12_s6 | Qwen3.5-4B | tool cases | 27 | 85.2% | 96.3% | +11.1 [-3.7, +25.9] | 1 / 4 | 0.375 | ±0.0 | **tie** |
| o3s5h_4b_v12_ht | o3s6_4b_v12_s6 | Qwen3.5-4B | tool cases: discovery | 16 | 87.5% | 100.0% | +12.5 [+0.0, +31.2] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3s5h_4b_v12_ht | o3s6_4b_v12_s6 | Qwen3.5-4B | tool cases: hinglish | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_4b_v12_ht | o3s6_4b_v12_s6 | Qwen3.5-4B | tool cases: refusal | 1 | 100.0% | 0.0% | -100.0 [-100.0, -100.0] | 1 / 0 | 1.000 | ±0.0 | **worse** |
| o3s5h_4b_v12_ht | o3s6_4b_v12_s6 | Qwen3.5-4B | tool cases: tool_selection | 2 | 50.0% | 100.0% | +50.0 [+0.0, +100.0] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s6_2b_v12_s6 | Qwen3.5-2B | tool cases | 27 | 81.5% | 92.6% | +11.1 [+0.0, +25.9] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3s5h_2b_v12_ht | o3s6_2b_v12_s6 | Qwen3.5-2B | tool cases: discovery | 16 | 87.5% | 100.0% | +12.5 [+0.0, +31.2] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3s5h_2b_v12_ht | o3s6_2b_v12_s6 | Qwen3.5-2B | tool cases: hinglish | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s6_2b_v12_s6 | Qwen3.5-2B | tool cases: refusal | 1 | 0.0% | 0.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s6_2b_v12_s6 | Qwen3.5-2B | tool cases: tool_selection | 2 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s5h_4b_rag_ht | o3s6_4b_rag_s6 | 1.25 → 0.91 | 423 → 247 | 119 → 111 | 0 → 0 | 0 → 0 | 9/50 → 10/10 | 6.4 s → 3.6 s |
| o3s5h_2b_rag_ht | o3s6_2b_rag_s6 | 2.28 → 0.91 | 527 → 247 | 91 → 111 | 0 → 0 | 0 → 0 | 9/207 → 10/10 | 6.3 s → 1.6 s |
| o3s5h_4b_v12_ht | o3s6_4b_v12_s6 | 1.21 → 0.59 | 237 → 143 | 155 → 145 | 0 → 0 | 0 → 0 | 21/37 → 16/16 | 3.0 s → 3.1 s |
| o3s5h_2b_v12_ht | o3s6_2b_v12_s6 | 1.37 → 0.59 | 279 → 143 | 158 → 145 | 0 → 0 | 0 → 0 | 21/56 → 16/16 | 2.0 s → 1.4 s |
