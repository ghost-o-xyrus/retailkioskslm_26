# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s2_4b_rag_s2 | o3s3_4b_rag_s3 | Qwen3.5-4B | all checked | 135 | 79.3% | 81.5% | +2.2 [+0.0, +5.2] | 0 / 3 | 0.250 | ±2.3 | **tie** |
| o3s2_4b_rag_s2 | o3s3_4b_rag_s3 | Qwen3.5-4B | answerable | 96 | 84.4% | 84.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.7 | **tie** |
| o3s2_4b_rag_s2 | o3s3_4b_rag_s3 | Qwen3.5-4B | unanswerable / near-miss | 39 | 66.7% | 74.4% | +7.7 [+0.0, +17.9] | 0 / 3 | 0.250 | ±4.3 | **tie** |
| o3s2_2b_rag_s2 | o3s3_2b_rag_s3 | Qwen3.5-2B | all checked | 135 | 49.6% | 62.2% | +12.6 [+5.2, +20.0] | 6 / 23 | 0.002 | ±2.3 | **better** |
| o3s2_2b_rag_s2 | o3s3_2b_rag_s3 | Qwen3.5-2B | answerable | 96 | 51.0% | 69.8% | +18.8 [+9.4, +28.1] | 3 / 21 | 0.000 | ±2.7 | **better** |
| o3s2_2b_rag_s2 | o3s3_2b_rag_s3 | Qwen3.5-2B | unanswerable / near-miss | 39 | 46.2% | 43.6% | -2.6 [-12.8, +7.7] | 3 / 2 | 1.000 | ±4.3 | **tie** |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | Qwen3.5-4B | tool cases | 60 | 76.7% | 75.0% | -1.7 [-6.7, +3.3] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | Qwen3.5-4B | tool cases: comparison | 2 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | Qwen3.5-4B | tool cases: discovery | 16 | 81.2% | 81.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | Qwen3.5-4B | tool cases: handoff | 6 | 66.7% | 83.3% | +16.7 [+0.0, +50.0] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | Qwen3.5-4B | tool cases: hinglish | 9 | 77.8% | 55.6% | -22.2 [-55.6, +0.0] | 2 / 0 | 0.500 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | Qwen3.5-4B | tool cases: tool_selection | 19 | 73.7% | 73.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | Qwen3.5-2B | tool cases | 60 | 58.3% | 61.7% | +3.3 [-8.3, +15.0] | 5 / 7 | 0.774 | ±0.0 | **tie** |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | Qwen3.5-2B | tool cases: discovery | 16 | 50.0% | 68.8% | +18.8 [-12.5, +50.0] | 2 / 5 | 0.453 | ±0.0 | **tie** |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | Qwen3.5-2B | tool cases: handoff | 6 | 83.3% | 66.7% | -16.7 [-50.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | Qwen3.5-2B | tool cases: hinglish | 9 | 11.1% | 33.3% | +22.2 [+0.0, +55.6] | 0 / 2 | 0.500 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | Qwen3.5-2B | tool cases: refusal | 8 | 75.0% | 50.0% | -25.0 [-62.5, +0.0] | 2 / 0 | 0.500 | ±0.0 | **(small)** |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | Qwen3.5-2B | tool cases: tool_selection | 19 | 68.4% | 68.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|
| o3s2_4b_rag_s2 | o3s3_4b_rag_s3 | 1.25 → 1.23 | 494 → 475 | 169 → 91 | 0 → 0 | 0 → 0 | 7.5 s → 7.3 s |
| o3s2_2b_rag_s2 | o3s3_2b_rag_s3 | 2.56 → 2.47 | 761 → 601 | 168 → 85 | 33 → 0 | 33 → 0 | 7.7 s → 9.0 s |
| o3s2_4b_v12_s2 | o3s3_4b_v12_s3 | 1.42 → 1.45 | 536 → 422 | 395 → 132 | 1 → 0 | 1 → 0 | 7.7 s → 7.7 s |
| o3s2_2b_v12_s2 | o3s3_2b_v12_s3 | 2.14 → 2.09 | 886 → 558 | 419 → 157 | 11 → 0 | 11 → 0 | 7.0 s → 6.1 s |
