# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s5h_4b_rag_ht | o3s6c_4b_rag_s6 | Qwen3.5-4B | all checked | 11 | 90.9% | 27.3% | -63.6 [-90.9, -36.4] | 7 / 0 | 0.016 | ±8.0 | **worse** |
| o3s5h_4b_rag_ht | o3s6c_4b_rag_s6 | Qwen3.5-4B | answerable | 11 | 90.9% | 27.3% | -63.6 [-90.9, -36.4] | 7 / 0 | 0.016 | ±8.0 | **worse** |
| o3s5h_2b_rag_ht | o3s6c_2b_rag_s6 | Qwen3.5-2B | all checked | 11 | 81.8% | 72.7% | -9.1 [-27.3, +0.0] | 1 / 0 | 1.000 | ±8.0 | **tie** |
| o3s5h_2b_rag_ht | o3s6c_2b_rag_s6 | Qwen3.5-2B | answerable | 11 | 81.8% | 72.7% | -9.1 [-27.3, +0.0] | 1 / 0 | 1.000 | ±8.0 | **tie** |
| o3s5h_4b_v12_ht | o3s6c_4b_v12_s6 | Qwen3.5-4B | tool cases | 27 | 85.2% | 100.0% | +14.8 [+3.7, +29.6] | 0 / 4 | 0.125 | ±0.0 | **better** |
| o3s5h_4b_v12_ht | o3s6c_4b_v12_s6 | Qwen3.5-4B | tool cases: discovery | 16 | 87.5% | 100.0% | +12.5 [+0.0, +31.2] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3s5h_4b_v12_ht | o3s6c_4b_v12_s6 | Qwen3.5-4B | tool cases: hinglish | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_4b_v12_ht | o3s6c_4b_v12_s6 | Qwen3.5-4B | tool cases: refusal | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_4b_v12_ht | o3s6c_4b_v12_s6 | Qwen3.5-4B | tool cases: tool_selection | 2 | 50.0% | 100.0% | +50.0 [+0.0, +100.0] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s6c_2b_v12_s6 | Qwen3.5-2B | tool cases | 27 | 81.5% | 92.6% | +11.1 [+0.0, +25.9] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3s5h_2b_v12_ht | o3s6c_2b_v12_s6 | Qwen3.5-2B | tool cases: discovery | 16 | 87.5% | 100.0% | +12.5 [+0.0, +31.2] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3s5h_2b_v12_ht | o3s6c_2b_v12_s6 | Qwen3.5-2B | tool cases: hinglish | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s6c_2b_v12_s6 | Qwen3.5-2B | tool cases: refusal | 1 | 0.0% | 0.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s5h_2b_v12_ht | o3s6c_2b_v12_s6 | Qwen3.5-2B | tool cases: tool_selection | 2 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s5h_4b_rag_ht | o3s6c_4b_rag_s6 | 1.25 → 0.91 | 423 → 224 | 119 → 84 | 0 → 6 | 0 → 0 | 9/50 → 10/10 | 6.4 s → 3.1 s |
| o3s5h_2b_rag_ht | o3s6c_2b_rag_s6 | 2.28 → 0.91 | 527 → 224 | 91 → 84 | 0 → 1 | 0 → 0 | 9/207 → 10/10 | 6.3 s → 1.6 s |
| o3s5h_4b_v12_ht | o3s6c_4b_v12_s6 | 1.21 → 0.63 | 237 → 144 | 155 → 145 | 0 → 0 | 0 → 0 | 21/37 → 16/16 | 3.0 s → 3.4 s |
| o3s5h_2b_v12_ht | o3s6c_2b_v12_s6 | 1.37 → 0.67 | 279 → 145 | 158 → 137 | 0 → 0 | 0 → 0 | 21/56 → 16/17 | 2.0 s → 1.5 s |
