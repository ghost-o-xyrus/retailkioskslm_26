# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s2_4b_rag_s2 | o3s3g_4b_rag_guard | Qwen3.5-4B | all checked | 135 | 79.3% | 79.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.3 | **tie** |
| o3s2_4b_rag_s2 | o3s3g_4b_rag_guard | Qwen3.5-4B | answerable | 96 | 84.4% | 84.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s2_4b_rag_s2 | o3s3g_4b_rag_guard | Qwen3.5-4B | unanswerable / near-miss | 39 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.3 | **tie** |
| o3s2_2b_rag_s2 | o3s3g_2b_rag_guard | Qwen3.5-2B | all checked | 135 | 49.6% | 57.8% | +8.1 [+3.7, +13.3] | 0 / 11 | 0.001 | ±2.3 | **better** |
| o3s2_2b_rag_s2 | o3s3g_2b_rag_guard | Qwen3.5-2B | answerable | 96 | 51.0% | 61.5% | +10.4 [+5.2, +16.7] | 0 / 10 | 0.002 | ±2.7 | **better** |
| o3s2_2b_rag_s2 | o3s3g_2b_rag_guard | Qwen3.5-2B | unanswerable / near-miss | 39 | 46.2% | 48.7% | +2.6 [+0.0, +7.7] | 0 / 1 | 1.000 | ±4.3 | **tie** |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | Qwen3.5-4B | tool cases | 60 | 76.7% | 76.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | Qwen3.5-4B | tool cases: comparison | 2 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | Qwen3.5-4B | tool cases: discovery | 16 | 81.2% | 81.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | Qwen3.5-4B | tool cases: handoff | 6 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | Qwen3.5-4B | tool cases: hinglish | 9 | 77.8% | 77.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | Qwen3.5-4B | tool cases: tool_selection | 19 | 73.7% | 73.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | Qwen3.5-2B | tool cases | 60 | 58.3% | 60.0% | +1.7 [+0.0, +5.0] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | Qwen3.5-2B | tool cases: discovery | 16 | 50.0% | 56.2% | +6.2 [+0.0, +18.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | Qwen3.5-2B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | Qwen3.5-2B | tool cases: hinglish | 9 | 11.1% | 11.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | Qwen3.5-2B | tool cases: refusal | 8 | 75.0% | 75.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | Qwen3.5-2B | tool cases: tool_selection | 19 | 68.4% | 68.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|
| o3s2_4b_rag_s2 | o3s3g_4b_rag_guard | 1.25 → 1.25 | 494 → 494 | 169 → 169 | 0 → 0 | 0 → 0 | 7.5 s → 7.0 s |
| o3s2_2b_rag_s2 | o3s3g_2b_rag_guard | 2.56 → 2.56 | 761 → 757 | 168 → 177 | 33 → 0 | 33 → 0 | 7.7 s → 7.6 s |
| o3s2_4b_v12_s2 | o3s3g_4b_v12_guard | 1.42 → 1.42 | 536 → 536 | 395 → 394 | 1 → 0 | 1 → 0 | 7.7 s → 7.3 s |
| o3s2_2b_v12_s2 | o3s3g_2b_v12_guard | 2.14 → 2.14 | 886 → 886 | 419 → 441 | 11 → 0 | 11 → 0 | 7.0 s → 6.9 s |
