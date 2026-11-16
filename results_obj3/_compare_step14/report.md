# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3t_b0_4b_rag | o3t_final_4b_rag | Qwen3.5-4B | all checked | 424 | 78.3% | 81.4% | +3.1 [-0.2, +6.4] | 19 / 32 | 0.092 | ±1.3 | **tie** |
| o3t_b0_4b_rag | o3t_final_4b_rag | Qwen3.5-4B | answerable | 285 | 80.0% | 83.2% | +3.2 [+0.0, +6.7] | 8 / 17 | 0.108 | ±1.6 | **tie** |
| o3t_b0_4b_rag | o3t_final_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 74.8% | 77.7% | +2.9 [-4.3, +10.1] | 11 / 15 | 0.557 | ±2.3 | **tie** |
| o3t_b0_4b_rag | o3t_final_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 58.1% | 54.8% | -3.2 [-12.9, +6.5] | 5 / 3 | 0.727 | ±3.4 | **tie** |
| o3t_b0_4b_rag | o3t_final_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 80.3% | 86.2% | +5.9 [+1.7, +10.0] | 11 / 28 | 0.009 | ±1.6 | **better** |
| o3t_b0_4b_rag | o3t_final_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 73.9% | 70.9% | -3.0 [-8.2, +2.2] | 8 / 4 | 0.388 | ±2.3 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | tool cases | 192 | 78.1% | 83.3% | +5.2 [-2.1, +12.5] | 22 / 32 | 0.220 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 83.8% | 81.1% | -2.7 [-18.9, +13.5] | 5 / 4 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 81.2% | 85.5% | +4.3 [-4.3, +12.8] | 11 / 16 | 0.442 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 73.3% | 80.0% | +6.7 [-8.0, +20.0] | 11 / 16 | 0.442 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 76.9% | 100.0% | +23.1 [+0.0, +46.2] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 70.2% | 80.9% | +10.6 [-6.4, +27.7] | 7 / 12 | 0.359 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 64.3% | -28.6 [-57.1, -7.1] | 4 / 0 | 0.125 | ±0.0 | **worse** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 83.3% | 80.6% | -2.8 [-19.4, +13.9] | 5 / 4 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 77.8% | 66.7% | -11.1 [-44.4, +22.2] | 2 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 78.1% | 89.0% | +11.0 [+1.4, +21.9] | 4 / 12 | 0.077 | ±0.0 | **better** |
| o3t_b0_4b_fup | o3t_final_4b_fup | Qwen3.5-4B | all checked | 60 | 66.7% | 90.0% | +23.3 [+8.3, +38.3] | 5 / 19 | 0.007 | ±3.4 | **better** |
| o3t_b0_4b_fup | o3t_final_4b_fup | Qwen3.5-4B | answerable | 60 | 66.7% | 90.0% | +23.3 [+8.3, +38.3] | 5 / 19 | 0.007 | ±3.4 | **better** |
| o3t_b0_4b_fup | o3t_final_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 61.5% | 76.9% | +15.4 [-11.5, +42.3] | 5 / 9 | 0.424 | ±5.2 | **tie** |
| o3t_b0_4b_fup | o3t_final_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 40.0% | 100.0% | +60.0 [+30.0, +90.0] | 0 / 6 | 0.031 | ±8.4 | **better** |
| o3t_b0_4b_fup | o3t_final_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 56.7% | 100.0% | +43.3 [+26.7, +60.0] | 0 / 13 | 0.000 | ±4.9 | **better** |
| o3t_b0_4b_fup | o3t_final_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_4b_fup | o3t_final_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 60.0% | -40.0 [-70.0, -10.0] | 4 / 0 | 0.125 | ±8.4 | **worse** |
| o3t_b0_2b_rag | o3t_final_2b_rag | Qwen3.5-2B | all checked | 424 | 51.9% | 69.6% | +17.7 [+12.7, +22.6] | 22 / 97 | 0.000 | ±1.3 | **better** |
| o3t_b0_2b_rag | o3t_final_2b_rag | Qwen3.5-2B | answerable | 285 | 61.1% | 77.2% | +16.1 [+10.5, +21.8] | 16 / 62 | 0.000 | ±1.6 | **better** |
| o3t_b0_2b_rag | o3t_final_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 33.1% | 54.0% | +20.9 [+12.9, +28.8] | 6 / 35 | 0.000 | ±2.3 | **better** |
| o3t_b0_2b_rag | o3t_final_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 50.0% | +0.0 [-8.1, +8.1] | 3 / 3 | 1.000 | ±3.4 | **tie** |
| o3t_b0_2b_rag | o3t_final_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 56.2% | 75.9% | +19.7 [+13.8, +25.2] | 13 / 70 | 0.000 | ±1.6 | **better** |
| o3t_b0_2b_rag | o3t_final_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 42.5% | 56.0% | +13.4 [+5.2, +21.6] | 9 / 27 | 0.004 | ±2.3 | **better** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | tool cases | 192 | 62.5% | 77.6% | +15.1 [+7.3, +22.9] | 17 / 46 | 0.000 | ±0.0 | **better** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 45.9% | 83.8% | +37.8 [+18.9, +56.8] | 2 / 16 | 0.001 | ±0.0 | **better** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 75.2% | 74.4% | -0.9 [-8.5, +6.8] | 11 / 10 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 42.7% | 82.7% | +40.0 [+25.3, +53.3] | 6 / 36 | 0.000 | ±0.0 | **better** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 92.3% | 100.0% | +7.7 [+0.0, +23.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 46.8% | 83.0% | +36.2 [+17.0, +55.3] | 5 / 22 | 0.002 | ±0.0 | **better** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 50.0% | 64.3% | +14.3 [-14.3, +42.9] | 1 / 3 | 0.625 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 47.2% | 83.3% | +36.1 [+16.7, +55.6] | 2 / 15 | 0.002 | ±0.0 | **better** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 66.7% | +0.0 [-33.3, +33.3] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 76.7% | 71.2% | -5.5 [-15.1, +2.7] | 8 / 4 | 0.388 | ±0.0 | **tie** |
| o3t_b0_2b_fup | o3t_final_2b_fup | Qwen3.5-2B | all checked | 60 | 80.0% | 90.0% | +10.0 [+0.0, +20.0] | 2 / 8 | 0.109 | ±3.4 | **tie** |
| o3t_b0_2b_fup | o3t_final_2b_fup | Qwen3.5-2B | answerable | 60 | 80.0% | 90.0% | +10.0 [+0.0, +20.0] | 2 / 8 | 0.109 | ±3.4 | **tie** |
| o3t_b0_2b_fup | o3t_final_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 65.4% | 80.8% | +15.4 [+0.0, +34.6] | 1 / 5 | 0.219 | ±5.2 | **tie** |
| o3t_b0_2b_fup | o3t_final_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3t_final_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 80.0% | 96.7% | +16.7 [+3.3, +30.0] | 0 / 5 | 0.062 | ±4.9 | **better** |
| o3t_b0_2b_fup | o3t_final_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3t_final_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 40.0% | 50.0% | +10.0 [-30.0, +50.0] | 2 / 3 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_rag | o3t_final12_2b_rag | Qwen3.5-2B | all checked | 424 | 69.6% | 73.8% | +4.2 [+1.2, +7.5] | 16 / 34 | 0.015 | ±1.3 | **better** |
| o3t_final_2b_rag | o3t_final12_2b_rag | Qwen3.5-2B | answerable | 285 | 77.2% | 80.7% | +3.5 [+0.4, +6.7] | 6 / 16 | 0.052 | ±1.6 | **better** |
| o3t_final_2b_rag | o3t_final12_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 54.0% | 59.7% | +5.8 [-1.4, +13.7] | 10 / 18 | 0.185 | ±2.3 | **tie** |
| o3t_final_2b_rag | o3t_final12_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 53.2% | +3.2 [-4.8, +11.3] | 2 / 4 | 0.688 | ±3.4 | **tie** |
| o3t_final_2b_rag | o3t_final12_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 75.9% | 81.7% | +5.9 [+2.1, +10.0] | 10 / 27 | 0.008 | ±1.6 | **better** |
| o3t_final_2b_rag | o3t_final12_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 56.0% | 56.7% | +0.7 [-4.5, +6.0] | 6 / 7 | 1.000 | ±2.3 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | tool cases | 192 | 77.6% | 76.0% | -1.6 [-4.7, +1.6] | 6 / 3 | 0.508 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 83.8% | 81.1% | -2.7 [-8.1, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 74.4% | 74.4% | +0.0 [-4.3, +4.3] | 3 / 3 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 82.7% | 78.7% | -4.0 [-9.3, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 83.0% | 78.7% | -4.3 [-10.6, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 83.3% | 80.6% | -2.8 [-8.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 66.7% | +0.0 [-33.3, +33.3] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 71.2% | 71.2% | +0.0 [-5.5, +5.5] | 2 / 2 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_fup | o3t_final12_2b_fup | Qwen3.5-2B | all checked | 60 | 90.0% | 90.0% | +0.0 [-5.0, +5.0] | 1 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_final_2b_fup | o3t_final12_2b_fup | Qwen3.5-2B | answerable | 60 | 90.0% | 90.0% | +0.0 [-5.0, +5.0] | 1 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_final_2b_fup | o3t_final12_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 80.8% | 80.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3t_final_2b_fup | o3t_final12_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 100.0% | 90.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3t_final12_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 96.7% | 96.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3t_final_2b_fup | o3t_final12_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3t_final12_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 50.0% | 60.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±8.4 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3t_b0_4b_rag | o3t_final_4b_rag | 1.27 → 1.05 | 554 → 375 | 258 → 130 | 4 → 3 | 4 → 0 | 0/135 → 93/188 | 7.3 s → 5.3 s |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | 1.88 → 0.96 | 746 → 257 | 312 → 133 | 3 → 7 | 3 → 0 | 0/174 → 154/164 | 13.3 s → 3.5 s |
| o3t_b0_4b_fup | o3t_final_4b_fup | 1.30 → 1.13 | 527 → 381 | 238 → 62 | 1 → 0 | 1 → 0 | 0/19 → 20/28 | 7.6 s → 4.8 s |
| o3t_b0_2b_rag | o3t_final_2b_rag | 2.51 → 1.91 | 846 → 442 | 214 → 94 | 98 → 8 | 98 → 0 | 0/815 → 97/565 | 7.9 s → 5.8 s |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | 2.78 → 1.06 | 1056 → 260 | 296 → 121 | 42 → 0 | 42 → 0 | 0/399 → 144/183 | 10.3 s → 1.6 s |
| o3t_b0_2b_fup | o3t_final_2b_fup | 1.88 → 1.15 | 743 → 388 | 312 → 78 | 1 → 0 | 1 → 0 | 0/54 → 20/29 | 6.5 s → 2.3 s |
| o3t_final_2b_rag | o3t_final12_2b_rag | 1.91 → 1.65 | 442 → 413 | 94 → 98 | 8 → 1 | 0 → 0 | 97/565 → 91/442 | 5.8 s → 4.6 s |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | 1.06 → 0.99 | 260 → 254 | 121 → 125 | 0 → 0 | 0 → 0 | 144/183 → 144/171 | 1.6 s → 1.3 s |
| o3t_final_2b_fup | o3t_final12_2b_fup | 1.15 → 1.10 | 388 → 379 | 78 → 70 | 0 → 0 | 0 → 0 | 20/29 → 20/26 | 2.3 s → 2.6 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o3t_b0_4b_rag | o3t_final_4b_rag | 463 | -1.72 s [-1.91, -1.40] | -1.87 s [-2.27, -1.43] |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | 192 | -9.70 s [-10.69, -8.10] | -11.06 s [-12.58, -10.12] |
| o3t_b0_4b_fup | o3t_final_4b_fup | 60 | -2.29 s [-4.29, -0.28] | -2.76 s [-4.96, -1.38] |
| o3t_b0_2b_rag | o3t_final_2b_rag | 463 | -1.35 s [-2.01, -1.07] | -2.52 s [-3.24, -1.81] |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | 192 | -8.12 s [-9.09, -7.23] | -11.13 s [-12.80, -9.56] |
| o3t_b0_2b_fup | o3t_final_2b_fup | 60 | -4.07 s [-4.88, -3.33] | -4.28 s [-5.56, -3.33] |
| o3t_final_2b_rag | o3t_final12_2b_rag | 463 | -0.68 s [-0.94, -0.56] | -1.12 s [-1.25, -0.95] |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | 192 | -0.28 s [-0.30, -0.27] | -0.51 s [-0.60, -0.43] |
| o3t_final_2b_fup | o3t_final12_2b_fup | 60 | +0.45 s [+0.42, +0.52] | +0.54 s [+0.45, +0.67] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3t_b0_4b_rag | o3t_final_4b_rag | 0 → 5 | 0 → 3 | 0 → 2 | 0 → 0 | 20 → 13 | 9 → 3 | 61 → 76 | 0 → 0 | 33 → 59 | 0 → 0 |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | 0 → 12 | 0 → 7 | 0 → 1 | 0 → 4 | 21 → 0 | 0 → 0 | 22 → 18 | 0 → 0 | 12 → 14 | 0 → 0 |
| o3t_b0_4b_fup | o3t_final_4b_fup | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 2 → 3 | 1 → 2 | 3 → 3 | 0 → 0 | 3 → 2 | 0 → 0 |
| o3t_b0_2b_rag | o3t_final_2b_rag | 0 → 15 | 0 → 8 | 0 → 5 | 0 → 2 | 135 → 58 | 60 → 33 | 7 → 36 | 0 → 0 | 0 → 29 | 0 → 0 |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 54 → 14 | 0 → 0 | 6 → 10 | 0 → 0 | 4 → 5 | 0 → 0 |
| o3t_b0_2b_fup | o3t_final_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 6 → 0 | 3 → 0 | 0 → 4 | 0 → 0 | 0 → 3 | 0 → 0 |
| o3t_final_2b_rag | o3t_final12_2b_rag | 15 → 6 | 8 → 1 | 5 → 5 | 2 → 0 | 58 → 12 | 33 → 7 | 36 → 36 | 0 → 0 | 29 → 29 | 0 → 0 |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 | 14 → 2 | 0 → 0 | 10 → 3 | 0 → 0 | 5 → 2 | 0 → 0 |
| o3t_final_2b_fup | o3t_final12_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 2 | 0 → 0 | 3 → 1 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3t_b0_4b_rag | o3t_final_4b_rag | 0 → 25 | 0 → 20 | 0 → 10 | 0 → 3 |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | 0 → 0 | 0 → 1 | 0 → 1 | 0 → 1 |
| o3t_b0_4b_fup | o3t_final_4b_fup | 0 → 0 | 0 → 0 | 0 → 2 | 0 → 0 |
| o3t_b0_2b_rag | o3t_final_2b_rag | 0 → 25 | 0 → 20 | 0 → 45 | 0 → 8 |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | 0 → 0 | 0 → 1 | 0 → 7 | 0 → 1 |
| o3t_b0_2b_fup | o3t_final_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_rag | o3t_final12_2b_rag | 25 → 25 | 20 → 20 | 45 → 47 | 8 → 40 |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | 0 → 0 | 1 → 1 | 7 → 8 | 1 → 8 |
| o3t_final_2b_fup | o3t_final12_2b_fup | 0 → 0 | 0 → 0 | 0 → 1 | 0 → 1 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3t_b0_4b_rag | o3t_final_4b_rag | 0/0 (0.0%) → 19/384 (4.9%) | 0 → 2 | 0 → 0 |
| o3t_b0_4b_fup | o3t_final_4b_fup | 0/0 (0.0%) → 1/40 (2.5%) | 0 → 0 | 0 → 0 |
| o3t_b0_2b_rag | o3t_final_2b_rag | 0/0 (0.0%) → 11/378 (2.9%) | 0 → 6 | 0 → 1 |
| o3t_b0_2b_fup | o3t_final_2b_fup | 0/0 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_2b_rag | o3t_final12_2b_rag | 11/378 (2.9%) → 18/385 (4.7%) | 6 → 8 | 1 → 2 |
| o3t_final_2b_fup | o3t_final12_2b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 1 | 0 → 0 |
