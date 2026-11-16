# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3g_b0_2b_rag | o3g_r1_2b_rag | Qwen3.5-2B | all checked | 424 | 50.7% | 63.2% | +12.5 [+8.3, +16.7] | 19 / 72 | 0.000 | ±1.3 | **better** |
| o3g_b0_2b_rag | o3g_r1_2b_rag | Qwen3.5-2B | answerable | 285 | 58.2% | 76.8% | +18.6 [+13.3, +23.5] | 8 / 61 | 0.000 | ±1.6 | **better** |
| o3g_b0_2b_rag | o3g_r1_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 35.3% | 35.3% | +0.0 [-6.5, +6.5] | 11 / 11 | 1.000 | ±2.3 | **tie** |
| o3g_b0_2b_rag | o3g_r1_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 51.6% | 53.2% | +1.6 [-3.2, +6.5] | 1 / 2 | 1.000 | ±3.4 | **tie** |
| o3g_b0_2b_rag | o3g_r1_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 55.2% | 67.9% | +12.8 [+7.2, +18.3] | 16 / 53 | 0.000 | ±1.6 | **better** |
| o3g_b0_2b_rag | o3g_r1_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 41.0% | 53.0% | +11.9 [+5.2, +18.7] | 3 / 19 | 0.001 | ±2.3 | **better** |
| o3g_r1_2b_rag | o3g_r2_2b_rag | Qwen3.5-2B | all checked | 424 | 63.2% | 64.4% | +1.2 [-0.5, +2.8] | 4 / 9 | 0.267 | ±1.3 | **tie** |
| o3g_r1_2b_rag | o3g_r2_2b_rag | Qwen3.5-2B | answerable | 285 | 76.8% | 78.9% | +2.1 [+0.0, +4.2] | 2 / 8 | 0.109 | ±1.6 | **tie** |
| o3g_r1_2b_rag | o3g_r2_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 35.3% | 34.5% | -0.7 [-2.9, +1.4] | 2 / 1 | 1.000 | ±2.3 | **tie** |
| o3g_r1_2b_rag | o3g_r2_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 53.2% | 50.0% | -3.2 [-9.7, +3.2] | 3 / 1 | 0.625 | ±3.4 | **tie** |
| o3g_r1_2b_rag | o3g_r2_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 67.9% | 70.7% | +2.8 [+1.0, +4.8] | 0 / 8 | 0.008 | ±1.6 | **better** |
| o3g_r1_2b_rag | o3g_r2_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 53.0% | 50.7% | -2.2 [-6.0, +0.7] | 4 / 1 | 0.375 | ±2.3 | **tie** |
| o3g_r2_2b_rag | o3g_r3_2b_rag | Qwen3.5-2B | all checked | 424 | 64.4% | 67.2% | +2.8 [+1.2, +4.7] | 2 / 14 | 0.004 | ±1.3 | **better** |
| o3g_r2_2b_rag | o3g_r3_2b_rag | Qwen3.5-2B | answerable | 285 | 78.9% | 81.1% | +2.1 [+0.7, +3.9] | 0 / 6 | 0.031 | ±1.6 | **better** |
| o3g_r2_2b_rag | o3g_r3_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 34.5% | 38.8% | +4.3 [+0.0, +8.6] | 2 / 8 | 0.109 | ±2.3 | **tie** |
| o3g_r2_2b_rag | o3g_r3_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 56.5% | +6.5 [+1.6, +12.9] | 0 / 4 | 0.125 | ±3.4 | **better** |
| o3g_r2_2b_rag | o3g_r3_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 70.7% | 72.8% | +2.1 [+0.3, +4.1] | 1 / 7 | 0.070 | ±1.6 | **better** |
| o3g_r2_2b_rag | o3g_r3_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 50.7% | 55.2% | +4.5 [+0.7, +9.0] | 1 / 7 | 0.070 | ±2.3 | **better** |
| o3g_r3_2b_rag | o3g_r4_2b_rag | Qwen3.5-2B | all checked | 424 | 67.2% | 70.8% | +3.5 [+1.2, +5.9] | 5 / 20 | 0.004 | ±1.3 | **better** |
| o3g_r3_2b_rag | o3g_r4_2b_rag | Qwen3.5-2B | answerable | 285 | 81.1% | 81.1% | +0.0 [-1.1, +1.1] | 1 / 1 | 1.000 | ±1.6 | **tie** |
| o3g_r3_2b_rag | o3g_r4_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 38.8% | 49.6% | +10.8 [+4.3, +17.3] | 4 / 19 | 0.003 | ±2.3 | **better** |
| o3g_r3_2b_rag | o3g_r4_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 56.5% | 54.8% | -1.6 [-9.7, +4.8] | 3 / 2 | 1.000 | ±3.4 | **tie** |
| o3g_r3_2b_rag | o3g_r4_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 72.8% | 76.6% | +3.8 [+1.4, +6.6] | 2 / 13 | 0.007 | ±1.6 | **better** |
| o3g_r3_2b_rag | o3g_r4_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 55.2% | 58.2% | +3.0 [-1.5, +7.5] | 3 / 7 | 0.344 | ±2.3 | **tie** |
| o3g_r4_2b_rag | o3g_r5_2b_rag | Qwen3.5-2B | all checked | 424 | 70.8% | 71.0% | +0.2 [-0.7, +1.2] | 2 / 3 | 1.000 | ±1.3 | **tie** |
| o3g_r4_2b_rag | o3g_r5_2b_rag | Qwen3.5-2B | answerable | 285 | 81.1% | 80.4% | -0.7 [-1.8, +0.0] | 2 / 0 | 0.500 | ±1.6 | **tie** |
| o3g_r4_2b_rag | o3g_r5_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 49.6% | 51.8% | +2.2 [+0.0, +5.0] | 0 / 3 | 0.250 | ±2.3 | **tie** |
| o3g_r4_2b_rag | o3g_r5_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 54.8% | 54.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r4_2b_rag | o3g_r5_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 76.6% | 76.9% | +0.3 [-0.7, +1.7] | 1 / 2 | 1.000 | ±1.6 | **tie** |
| o3g_r4_2b_rag | o3g_r5_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 58.2% | 58.2% | +0.0 [-2.2, +2.2] | 1 / 1 | 1.000 | ±2.3 | **tie** |
| o3g_r5_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | all checked | 424 | 71.0% | 69.6% | -1.4 [-4.5, +1.9] | 28 / 22 | 0.480 | ±1.3 | **tie** |
| o3g_r5_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 80.4% | 77.5% | -2.8 [-6.3, +0.7] | 17 / 9 | 0.169 | ±1.6 | **tie** |
| o3g_r5_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 51.8% | 53.2% | +1.4 [-5.8, +8.6] | 11 / 13 | 0.839 | ±2.3 | **tie** |
| o3g_r5_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 54.8% | 48.4% | -6.5 [-16.1, +1.6] | 6 / 2 | 0.289 | ±3.4 | **tie** |
| o3g_r5_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 76.9% | 76.9% | +0.0 [-3.8, +3.8] | 16 / 16 | 1.000 | ±1.6 | **tie** |
| o3g_r5_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 58.2% | 53.7% | -4.5 [-10.4, +1.5] | 12 / 6 | 0.238 | ±2.3 | **tie** |
| o3g_b0_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | all checked | 424 | 50.7% | 69.6% | +18.9 [+13.9, +23.6] | 22 / 102 | 0.000 | ±1.3 | **better** |
| o3g_b0_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 58.2% | 77.5% | +19.3 [+13.7, +24.9] | 13 / 68 | 0.000 | ±1.6 | **better** |
| o3g_b0_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 35.3% | 53.2% | +18.0 [+9.4, +26.6] | 9 / 34 | 0.000 | ±2.3 | **better** |
| o3g_b0_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 51.6% | 48.4% | -3.2 [-11.3, +4.8] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o3g_b0_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 55.2% | 76.9% | +21.7 [+15.9, +27.6] | 15 / 78 | 0.000 | ±1.6 | **better** |
| o3g_b0_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 41.0% | 53.7% | +12.7 [+5.2, +20.9] | 7 / 24 | 0.003 | ±2.3 | **better** |
| o3g_nr_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | all checked | 413 | 65.4% | 68.8% | +3.4 [+1.0, +6.1] | 8 / 22 | 0.016 | ±1.3 | **better** |
| o3g_nr_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | answerable | 274 | 77.0% | 76.6% | -0.4 [-2.6, +1.8] | 6 / 5 | 1.000 | ±1.6 | **tie** |
| o3g_nr_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 42.4% | 53.2% | +10.8 [+5.0, +16.5] | 2 / 17 | 0.001 | ±2.3 | **better** |
| o3g_nr_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 48.4% | -1.6 [-9.7, +4.8] | 3 / 2 | 1.000 | ±3.4 | **tie** |
| o3g_nr_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: fresh | 279 | 71.3% | 76.0% | +4.7 [+1.4, +7.9] | 4 / 17 | 0.007 | ±1.6 | **better** |
| o3g_nr_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 53.0% | 53.7% | +0.7 [-3.7, +5.2] | 4 / 5 | 1.000 | ±2.3 | **tie** |
| o3t_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | all checked | 424 | 51.9% | 50.7% | -1.2 [-3.5, +1.2] | 16 / 11 | 0.442 | ±1.3 | **tie** |
| o3t_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | answerable | 285 | 61.1% | 58.2% | -2.8 [-5.6, +0.0] | 12 / 4 | 0.077 | ±1.6 | **tie** |
| o3t_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 33.1% | 35.3% | +2.2 [-2.2, +6.5] | 4 / 7 | 0.549 | ±2.3 | **tie** |
| o3t_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 51.6% | +1.6 [-3.2, +6.5] | 1 / 2 | 1.000 | ±3.4 | **tie** |
| o3t_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 56.2% | 55.2% | -1.0 [-3.8, +1.4] | 8 / 5 | 0.581 | ±1.6 | **tie** |
| o3t_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 42.5% | 41.0% | -1.5 [-7.5, +4.5] | 8 / 6 | 0.791 | ±2.3 | **tie** |
| o3t_final_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | all checked | 424 | 69.6% | 69.6% | +0.0 [-2.4, +2.4] | 13 / 13 | 1.000 | ±1.3 | **tie** |
| o3t_final_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 77.2% | 77.5% | +0.4 [-2.5, +3.2] | 8 / 9 | 1.000 | ±1.6 | **tie** |
| o3t_final_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 54.0% | 53.2% | -0.7 [-5.0, +3.6] | 5 / 4 | 1.000 | ±2.3 | **tie** |
| o3t_final_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 48.4% | -1.6 [-6.5, +3.2] | 2 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_final_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 75.9% | 76.9% | +1.0 [-1.7, +4.1] | 8 / 11 | 0.648 | ±1.6 | **tie** |
| o3t_final_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 56.0% | 53.7% | -2.2 [-6.0, +1.5] | 5 / 2 | 0.453 | ±2.3 | **tie** |
| o3l_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | all checked | 424 | 53.1% | 50.7% | -2.4 [-5.0, +0.0] | 19 / 9 | 0.087 | ±1.3 | **tie** |
| o3l_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | answerable | 285 | 60.4% | 58.2% | -2.1 [-5.3, +0.7] | 12 / 6 | 0.238 | ±1.6 | **tie** |
| o3l_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 38.1% | 35.3% | -2.9 [-7.2, +1.4] | 7 / 3 | 0.344 | ±2.3 | **tie** |
| o3l_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 56.5% | 51.6% | -4.8 [-11.3, +1.6] | 4 / 1 | 0.375 | ±3.4 | **tie** |
| o3l_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 56.9% | 55.2% | -1.7 [-4.5, +1.0] | 11 / 6 | 0.332 | ±1.6 | **tie** |
| o3l_b0_2b_rag | o3g_b0_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 44.8% | 41.0% | -3.7 [-9.0, +0.7] | 8 / 3 | 0.227 | ±2.3 | **tie** |
| o3l_r6_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | all checked | 423 | 68.8% | 69.5% | +0.7 [-1.2, +2.6] | 7 / 10 | 0.629 | ±1.3 | **tie** |
| o3l_r6_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 76.8% | 77.5% | +0.7 [-1.4, +2.8] | 4 / 6 | 0.754 | ±1.6 | **tie** |
| o3l_r6_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 138 | 52.2% | 52.9% | +0.7 [-2.9, +4.3] | 3 / 4 | 1.000 | ±2.3 | **tie** |
| o3l_r6_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 48.4% | -1.6 [-4.8, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3l_r6_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: fresh | 289 | 75.4% | 76.8% | +1.4 [-0.7, +3.5] | 3 / 7 | 0.344 | ±1.6 | **tie** |
| o3l_r6_2b_rag | o3g_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 54.5% | 53.7% | -0.7 [-4.5, +3.0] | 4 / 3 | 1.000 | ±2.3 | **tie** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | tool cases | 192 | 61.5% | 64.6% | +3.1 [-3.1, +9.4] | 16 / 22 | 0.418 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 48.6% | 32.4% | -16.2 [-29.7, -2.7] | 7 / 1 | 0.070 | ±0.0 | **worse** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.1% | 73.5% | -2.6 [-10.3, +5.1] | 11 / 8 | 0.648 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 38.7% | 50.7% | +12.0 [+1.3, +22.7] | 5 / 14 | 0.064 | ±0.0 | **better** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 84.6% | -15.4 [-38.5, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 38.3% | 63.8% | +25.5 [+12.8, +38.3] | 1 / 13 | 0.002 | ±0.0 | **better** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 57.1% | 42.9% | -14.3 [-35.7, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 50.0% | 33.3% | -16.7 [-30.6, -2.8] | 7 / 1 | 0.070 | ±0.0 | **worse** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 55.6% | -11.1 [-44.4, +22.2] | 2 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 75.3% | 82.2% | +6.8 [-1.4, +15.1] | 2 / 7 | 0.180 | ±0.0 | **tie** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | tool cases | 192 | 64.6% | 71.4% | +6.8 [+0.5, +13.0] | 14 / 27 | 0.060 | ±0.0 | **better** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 32.4% | 59.5% | +27.0 [+8.1, +45.9] | 3 / 13 | 0.021 | ±0.0 | **better** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 73.5% | 70.9% | -2.6 [-8.5, +4.3] | 9 / 6 | 0.607 | ±0.0 | **tie** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 50.7% | 72.0% | +21.3 [+9.3, +34.7] | 5 / 21 | 0.002 | ±0.0 | **better** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 84.6% | 100.0% | +15.4 [+0.0, +38.5] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 63.8% | 76.6% | +12.8 [+0.0, +27.7] | 3 / 9 | 0.146 | ±0.0 | **tie** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 42.9% | 21.4% | -21.4 [-42.9, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 33.3% | 61.1% | +27.8 [+8.3, +47.2] | 3 / 13 | 0.021 | ±0.0 | **better** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 55.6% | 55.6% | +0.0 [-33.3, +33.3] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 82.2% | 79.5% | -2.7 [-9.6, +4.1] | 4 / 2 | 0.688 | ±0.0 | **tie** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | tool cases | 192 | 71.4% | 78.6% | +7.3 [+0.0, +15.1] | 20 / 34 | 0.076 | ±0.0 | **tie** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 59.5% | 83.8% | +24.3 [+5.4, +43.2] | 3 / 12 | 0.035 | ±0.0 | **better** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 70.9% | 76.1% | +5.1 [-3.4, +12.8] | 10 / 16 | 0.327 | ±0.0 | **tie** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 72.0% | 82.7% | +10.7 [-2.7, +24.0] | 10 / 18 | 0.185 | ±0.0 | **tie** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 76.6% | 83.0% | +6.4 [-10.6, +23.4] | 7 / 10 | 0.629 | ±0.0 | **tie** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 21.4% | 64.3% | +42.9 [+7.1, +71.4] | 1 / 7 | 0.070 | ±0.0 | **better** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 61.1% | 83.3% | +22.2 [+2.8, +41.7] | 3 / 11 | 0.057 | ±0.0 | **better** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 55.6% | 55.6% | +0.0 [-33.3, +33.3] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 79.5% | 75.3% | -4.1 [-13.7, +5.5] | 8 / 5 | 0.581 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | tool cases | 192 | 78.6% | 78.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 83.8% | 83.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.1% | 76.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 82.7% | 82.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 83.0% | 83.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 55.6% | 55.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 75.3% | 75.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | tool cases | 192 | 78.6% | 79.2% | +0.5 [+0.0, +1.6] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 83.8% | 83.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.1% | 76.9% | +0.9 [+0.0, +2.6] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 82.7% | 82.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 83.0% | 83.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 55.6% | 66.7% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 75.3% | 75.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases | 192 | 79.2% | 76.0% | -3.1 [-6.2, +0.0] | 8 / 2 | 0.109 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 83.8% | 75.7% | -8.1 [-18.9, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.9% | 74.4% | -2.6 [-6.8, +1.7] | 5 / 2 | 0.453 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 82.7% | 78.7% | -4.0 [-9.3, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 83.0% | 83.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 83.3% | 75.0% | -8.3 [-19.4, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 77.8% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 75.3% | 69.9% | -5.5 [-12.3, +0.0] | 5 / 1 | 0.219 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases | 192 | 61.5% | 76.0% | +14.6 [+6.8, +22.9] | 20 / 48 | 0.001 | ±0.0 | **better** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 48.6% | 75.7% | +27.0 [+2.7, +48.6] | 5 / 15 | 0.041 | ±0.0 | **better** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.1% | 74.4% | -1.7 [-9.4, +6.0] | 11 / 9 | 0.824 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 38.7% | 78.7% | +40.0 [+24.0, +56.0] | 9 / 39 | 0.000 | ±0.0 | **better** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 38.3% | 83.0% | +44.7 [+25.5, +63.8] | 5 / 26 | 0.000 | ±0.0 | **better** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 57.1% | 64.3% | +7.1 [-21.4, +35.7] | 2 / 3 | 1.000 | ±0.0 | **tie** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 50.0% | 75.0% | +25.0 [+2.8, +47.2] | 5 / 14 | 0.064 | ±0.0 | **better** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 77.8% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 75.3% | 69.9% | -5.5 [-15.1, +4.1] | 8 / 4 | 0.388 | ±0.0 | **tie** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases | 189 | 61.4% | 75.7% | +14.3 [+5.8, +22.2] | 20 / 47 | 0.001 | ±0.0 | **better** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 35 | 48.6% | 74.3% | +25.7 [+2.9, +48.6] | 5 / 14 | 0.064 | ±0.0 | **better** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 65.0% | 74.4% | +9.4 [+0.9, +17.9] | 8 / 19 | 0.052 | ±0.0 | **better** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 72 | 55.6% | 77.8% | +22.2 [+5.6, +38.9] | 12 / 28 | 0.017 | ±0.0 | **better** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 84.6% | 100.0% | +15.4 [+0.0, +38.5] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 45 | 60.0% | 82.2% | +22.2 [+0.0, +42.2] | 7 / 17 | 0.064 | ±0.0 | **tie** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 35.7% | 64.3% | +28.6 [+7.1, +50.0] | 0 / 4 | 0.125 | ±0.0 | **better** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 35 | 48.6% | 74.3% | +25.7 [+2.9, +48.6] | 5 / 14 | 0.064 | ±0.0 | **better** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 77.8% | 77.8% | +0.0 [-33.3, +33.3] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 67.1% | 69.9% | +2.7 [-8.2, +13.7] | 7 / 9 | 0.804 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases | 192 | 62.5% | 61.5% | -1.0 [-4.7, +2.1] | 7 / 5 | 0.774 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 45.9% | 48.6% | +2.7 [+0.0, +8.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 75.2% | 76.1% | +0.9 [-2.6, +4.3] | 2 / 3 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 42.7% | 38.7% | -4.0 [-10.7, +2.7] | 5 / 2 | 0.453 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 92.3% | 100.0% | +7.7 [+0.0, +23.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 46.8% | 38.3% | -8.5 [-19.1, +0.0] | 5 / 1 | 0.219 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 50.0% | 57.1% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 47.2% | 50.0% | +2.8 [+0.0, +8.3] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 76.7% | 75.3% | -1.4 [-5.5, +2.7] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases | 192 | 77.6% | 76.0% | -1.6 [-4.2, +0.5] | 4 / 1 | 0.375 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 83.8% | 75.7% | -8.1 [-18.9, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 74.4% | 74.4% | +0.0 [-2.6, +2.6] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 82.7% | 78.7% | -4.0 [-9.3, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 83.0% | 83.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 83.3% | 75.0% | -8.3 [-19.4, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 77.8% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 71.2% | 69.9% | -1.4 [-4.1, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases | 192 | 64.1% | 61.5% | -2.6 [-6.2, +1.0] | 9 / 4 | 0.267 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 45.9% | 48.6% | +2.7 [+0.0, +8.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.9% | 76.1% | -0.9 [-5.1, +2.6] | 3 / 2 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 44.0% | 38.7% | -5.3 [-13.3, +1.3] | 6 / 2 | 0.289 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 48.9% | 38.3% | -10.6 [-21.3, +0.0] | 6 / 1 | 0.125 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 57.1% | 57.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 47.2% | 50.0% | +2.8 [+0.0, +8.3] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 55.6% | 66.7% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 78.1% | 75.3% | -2.7 [-8.2, +2.7] | 3 / 1 | 0.625 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases | 192 | 76.6% | 76.0% | -0.5 [-2.6, +1.6] | 3 / 2 | 1.000 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 81.1% | 75.7% | -5.4 [-13.5, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 73.5% | 74.4% | +0.9 [-1.7, +4.3] | 1 / 2 | 1.000 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 81.3% | 78.7% | -2.7 [-6.7, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 83.0% | 83.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 80.6% | 75.0% | -5.6 [-13.9, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 77.8% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 69.9% | 69.9% | +0.0 [-4.1, +4.1] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_b0_2b_fup | o3g_r1_2b_fup | Qwen3.5-2B | all checked | 60 | 76.7% | 76.7% | +0.0 [-10.0, +10.0] | 5 / 5 | 1.000 | ±3.4 | **tie** |
| o3g_b0_2b_fup | o3g_r1_2b_fup | Qwen3.5-2B | answerable | 60 | 76.7% | 76.7% | +0.0 [-10.0, +10.0] | 5 / 5 | 1.000 | ±3.4 | **tie** |
| o3g_b0_2b_fup | o3g_r1_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 61.5% | 73.1% | +11.5 [+0.0, +26.9] | 0 / 3 | 0.250 | ±5.2 | **tie** |
| o3g_b0_2b_fup | o3g_r1_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 70.0% | 40.0% | -30.0 [-70.0, +10.0] | 4 / 1 | 0.375 | ±8.4 | **tie** |
| o3g_b0_2b_fup | o3g_r1_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_b0_2b_fup | o3g_r1_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_b0_2b_fup | o3g_r1_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 40.0% | 70.0% | +30.0 [-10.0, +70.0] | 1 / 4 | 0.375 | ±8.4 | **tie** |
| o3g_r1_2b_fup | o3g_r2_2b_fup | Qwen3.5-2B | all checked | 60 | 76.7% | 76.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r1_2b_fup | o3g_r2_2b_fup | Qwen3.5-2B | answerable | 60 | 76.7% | 76.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r1_2b_fup | o3g_r2_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 73.1% | 73.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3g_r1_2b_fup | o3g_r2_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 40.0% | 40.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r1_2b_fup | o3g_r2_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_r1_2b_fup | o3g_r2_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r1_2b_fup | o3g_r2_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r2_2b_fup | o3g_r3_2b_fup | Qwen3.5-2B | all checked | 60 | 76.7% | 75.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r2_2b_fup | o3g_r3_2b_fup | Qwen3.5-2B | answerable | 60 | 76.7% | 75.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r2_2b_fup | o3g_r3_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 73.1% | 69.2% | -3.8 [-11.5, +0.0] | 1 / 0 | 1.000 | ±5.2 | **tie** |
| o3g_r2_2b_fup | o3g_r3_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 40.0% | 40.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r2_2b_fup | o3g_r3_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_r2_2b_fup | o3g_r3_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r2_2b_fup | o3g_r3_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 60.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r3_2b_fup | o3g_r4_2b_fup | Qwen3.5-2B | all checked | 60 | 75.0% | 75.0% | +0.0 [-5.0, +5.0] | 1 / 1 | 1.000 | ±3.4 | **tie** |
| o3g_r3_2b_fup | o3g_r4_2b_fup | Qwen3.5-2B | answerable | 60 | 75.0% | 75.0% | +0.0 [-5.0, +5.0] | 1 / 1 | 1.000 | ±3.4 | **tie** |
| o3g_r3_2b_fup | o3g_r4_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 69.2% | 73.1% | +3.8 [+0.0, +11.5] | 0 / 1 | 1.000 | ±5.2 | **tie** |
| o3g_r3_2b_fup | o3g_r4_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 40.0% | 40.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r3_2b_fup | o3g_r4_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 83.3% | 80.0% | -3.3 [-10.0, +0.0] | 1 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_r3_2b_fup | o3g_r4_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r3_2b_fup | o3g_r4_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 60.0% | 70.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±8.4 | **tie** |
| o3g_r4_2b_fup | o3g_r5_2b_fup | Qwen3.5-2B | all checked | 60 | 75.0% | 90.0% | +15.0 [+3.3, +26.7] | 2 / 11 | 0.022 | ±3.4 | **better** |
| o3g_r4_2b_fup | o3g_r5_2b_fup | Qwen3.5-2B | answerable | 60 | 75.0% | 90.0% | +15.0 [+3.3, +26.7] | 2 / 11 | 0.022 | ±3.4 | **better** |
| o3g_r4_2b_fup | o3g_r5_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 73.1% | 84.6% | +11.5 [-3.8, +26.9] | 1 / 4 | 0.375 | ±5.2 | **tie** |
| o3g_r4_2b_fup | o3g_r5_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 40.0% | 100.0% | +60.0 [+30.0, +90.0] | 0 / 6 | 0.031 | ±8.4 | **better** |
| o3g_r4_2b_fup | o3g_r5_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 80.0% | 93.3% | +13.3 [+0.0, +30.0] | 1 / 5 | 0.219 | ±4.9 | **tie** |
| o3g_r4_2b_fup | o3g_r5_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 90.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r4_2b_fup | o3g_r5_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r5_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | all checked | 60 | 90.0% | 91.7% | +1.7 [-5.0, +8.3] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3g_r5_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | answerable | 60 | 90.0% | 91.7% | +1.7 [-5.0, +8.3] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3g_r5_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 84.6% | 80.8% | -3.8 [-19.2, +7.7] | 2 / 1 | 1.000 | ±5.2 | **tie** |
| o3g_r5_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r5_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 93.3% | 96.7% | +3.3 [+0.0, +10.0] | 0 / 1 | 1.000 | ±4.9 | **tie** |
| o3g_r5_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 90.0% | 100.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±8.4 | **tie** |
| o3g_r5_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 60.0% | -10.0 [-40.0, +20.0] | 2 / 1 | 1.000 | ±8.4 | **tie** |
| o3g_b0_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | all checked | 60 | 76.7% | 91.7% | +15.0 [+6.7, +25.0] | 0 / 9 | 0.004 | ±3.4 | **better** |
| o3g_b0_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | answerable | 60 | 76.7% | 91.7% | +15.0 [+6.7, +25.0] | 0 / 9 | 0.004 | ±3.4 | **better** |
| o3g_b0_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 61.5% | 80.8% | +19.2 [+3.8, +34.6] | 0 / 5 | 0.062 | ±5.2 | **better** |
| o3g_b0_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 70.0% | 100.0% | +30.0 [+0.0, +60.0] | 0 / 3 | 0.250 | ±8.4 | **tie** |
| o3g_b0_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 83.3% | 96.7% | +13.3 [+3.3, +26.7] | 0 / 4 | 0.125 | ±4.9 | **better** |
| o3g_b0_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_b0_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 40.0% | 60.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±8.4 | **tie** |
| o3g_nr_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | all checked | 60 | 63.3% | 91.7% | +28.3 [+16.7, +40.0] | 0 / 17 | 0.000 | ±3.4 | **better** |
| o3g_nr_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | answerable | 60 | 63.3% | 91.7% | +28.3 [+16.7, +40.0] | 0 / 17 | 0.000 | ±3.4 | **better** |
| o3g_nr_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 50.0% | 80.8% | +30.8 [+15.4, +50.0] | 0 / 8 | 0.008 | ±5.2 | **better** |
| o3g_nr_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 0.0% | 100.0% | +100.0 [+100.0, +100.0] | 0 / 10 | 0.002 | ±8.4 | **better** |
| o3g_nr_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 73.3% | 96.7% | +23.3 [+10.0, +40.0] | 0 / 7 | 0.016 | ±4.9 | **better** |
| o3g_nr_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_nr_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 60.0% | 60.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | all checked | 60 | 80.0% | 76.7% | -3.3 [-11.7, +5.0] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o3t_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | answerable | 60 | 80.0% | 76.7% | -3.3 [-11.7, +5.0] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o3t_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 65.4% | 61.5% | -3.8 [-15.4, +7.7] | 2 / 1 | 1.000 | ±5.2 | **tie** |
| o3t_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 100.0% | 70.0% | -30.0 [-60.0, +0.0] | 3 / 0 | 0.250 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 80.0% | 83.3% | +3.3 [+0.0, +10.0] | 0 / 1 | 1.000 | ±4.9 | **tie** |
| o3t_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 40.0% | 40.0% | +0.0 [-30.0, +30.0] | 1 / 1 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | all checked | 60 | 90.0% | 91.7% | +1.7 [+0.0, +5.0] | 0 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_final_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | answerable | 60 | 90.0% | 91.7% | +1.7 [+0.0, +5.0] | 0 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_final_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 80.8% | 80.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3t_final_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 96.7% | 96.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3t_final_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 50.0% | 60.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±8.4 | **tie** |
| o3l_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | all checked | 60 | 75.0% | 76.7% | +1.7 [-5.0, +8.3] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3l_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | answerable | 60 | 75.0% | 76.7% | +1.7 [-5.0, +8.3] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3l_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 61.5% | 61.5% | +0.0 [-11.5, +11.5] | 1 / 1 | 1.000 | ±5.2 | **tie** |
| o3l_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 80.0% | 70.0% | -10.0 [-40.0, +20.0] | 2 / 1 | 1.000 | ±8.4 | **tie** |
| o3l_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 80.0% | 83.3% | +3.3 [+0.0, +10.0] | 0 / 1 | 1.000 | ±4.9 | **tie** |
| o3l_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_b0_2b_fup | o3g_b0_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 30.0% | 40.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±8.4 | **tie** |
| o3l_r6_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | all checked | 60 | 86.7% | 91.7% | +5.0 [+0.0, +11.7] | 0 / 3 | 0.250 | ±3.4 | **tie** |
| o3l_r6_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | answerable | 60 | 86.7% | 91.7% | +5.0 [+0.0, +11.7] | 0 / 3 | 0.250 | ±3.4 | **tie** |
| o3l_r6_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 80.8% | 80.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3l_r6_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 90.0% | 100.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±8.4 | **tie** |
| o3l_r6_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 96.7% | 96.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3l_r6_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_r6_2b_fup | o3g_r6_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 40.0% | 60.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±8.4 | **tie** |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | Qwen3.5-2B | all checked | 423 | 61.5% | 68.8% | +7.3 [+2.4, +12.3] | 45 / 76 | 0.006 | ±1.3 | **better** |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 71.2% | 76.8% | +5.6 [-0.4, +11.2] | 28 / 44 | 0.076 | ±1.6 | **tie** |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 138 | 41.3% | 52.2% | +10.9 [+1.4, +21.0] | 17 / 32 | 0.044 | ±2.3 | **better** |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 46.8% | 50.0% | +3.2 [-9.7, +14.5] | 6 / 8 | 0.791 | ±3.4 | **tie** |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | Qwen3.5-2B | origin: fresh | 289 | 67.8% | 75.4% | +7.6 [+1.7, +13.5] | 28 / 50 | 0.017 | ±1.6 | **better** |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 47.8% | 54.5% | +6.7 [-3.0, +16.4] | 17 / 26 | 0.222 | ±2.3 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases | 192 | 76.6% | 76.6% | +0.0 [-7.8, +7.8] | 30 / 30 | 1.000 | ±0.0 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 73.0% | 81.1% | +8.1 [-10.8, +27.0] | 5 / 8 | 0.581 | ±0.0 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.1% | 73.5% | -2.6 [-11.1, +6.8] | 17 / 14 | 0.720 | ±0.0 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 77.3% | 81.3% | +4.0 [-10.7, +18.7] | 13 / 16 | 0.711 | ±0.0 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 76.6% | 83.0% | +6.4 [-10.6, +25.5] | 8 / 11 | 0.648 | ±0.0 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 28.6% | 64.3% | +35.7 [+7.1, +64.3] | 1 / 6 | 0.125 | ±0.0 | **better** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 75.0% | 80.6% | +5.6 [-13.9, +25.0] | 5 / 7 | 0.774 | ±0.0 | **tie** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 55.6% | 66.7% | +11.1 [-22.2, +44.4] | 1 / 2 | 1.000 | ±0.0 | **(small)** |
| o3l_ref_2b_none | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 84.9% | 69.9% | -15.1 [-26.0, -4.1] | 15 / 4 | 0.019 | ±0.0 | **worse** |
| o3g_b0_4b_rag | o3g_r1_4b_rag | Qwen3.5-4B | all checked | 424 | 80.4% | 82.1% | +1.7 [-0.9, +4.2] | 12 / 19 | 0.281 | ±1.3 | **tie** |
| o3g_b0_4b_rag | o3g_r1_4b_rag | Qwen3.5-4B | answerable | 285 | 85.3% | 84.6% | -0.7 [-2.8, +1.1] | 5 / 3 | 0.727 | ±1.6 | **tie** |
| o3g_b0_4b_rag | o3g_r1_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 70.5% | 77.0% | +6.5 [+0.0, +12.9] | 7 / 16 | 0.093 | ±2.3 | **tie** |
| o3g_b0_4b_rag | o3g_r1_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 59.7% | 56.5% | -3.2 [-11.3, +4.8] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o3g_b0_4b_rag | o3g_r1_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 82.1% | 86.2% | +4.1 [+1.0, +7.2] | 5 / 17 | 0.017 | ±1.6 | **better** |
| o3g_b0_4b_rag | o3g_r1_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 76.9% | 73.1% | -3.7 [-8.2, +0.7] | 7 / 2 | 0.180 | ±2.3 | **tie** |
| o3g_r1_4b_rag | o3g_r2_4b_rag | Qwen3.5-4B | all checked | 424 | 82.1% | 82.3% | +0.2 [-0.7, +1.2] | 2 / 3 | 1.000 | ±1.3 | **tie** |
| o3g_r1_4b_rag | o3g_r2_4b_rag | Qwen3.5-4B | answerable | 285 | 84.6% | 84.6% | +0.0 [-1.1, +1.1] | 1 / 1 | 1.000 | ±1.6 | **tie** |
| o3g_r1_4b_rag | o3g_r2_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 77.0% | 77.7% | +0.7 [-1.4, +2.9] | 1 / 2 | 1.000 | ±2.3 | **tie** |
| o3g_r1_4b_rag | o3g_r2_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 56.5% | 56.5% | +0.0 [-6.5, +6.5] | 2 / 2 | 1.000 | ±3.4 | **tie** |
| o3g_r1_4b_rag | o3g_r2_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 86.2% | 86.6% | +0.3 [+0.0, +1.0] | 0 / 1 | 1.000 | ±1.6 | **tie** |
| o3g_r1_4b_rag | o3g_r2_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 73.1% | 73.1% | +0.0 [-3.0, +3.0] | 2 / 2 | 1.000 | ±2.3 | **tie** |
| o3g_r2_4b_rag | o3g_r3_4b_rag | Qwen3.5-4B | all checked | 424 | 82.3% | 81.1% | -1.2 [-2.6, +0.0] | 6 / 1 | 0.125 | ±1.3 | **tie** |
| o3g_r2_4b_rag | o3g_r3_4b_rag | Qwen3.5-4B | answerable | 285 | 84.6% | 84.6% | +0.0 [-1.1, +1.1] | 1 / 1 | 1.000 | ±1.6 | **tie** |
| o3g_r2_4b_rag | o3g_r3_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 77.7% | 74.1% | -3.6 [-7.2, -0.7] | 5 / 0 | 0.062 | ±2.3 | **worse** |
| o3g_r2_4b_rag | o3g_r3_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 56.5% | 54.8% | -1.6 [-6.5, +3.2] | 2 / 1 | 1.000 | ±3.4 | **tie** |
| o3g_r2_4b_rag | o3g_r3_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 86.6% | 86.9% | +0.3 [+0.0, +1.0] | 0 / 1 | 1.000 | ±1.6 | **tie** |
| o3g_r2_4b_rag | o3g_r3_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 73.1% | 68.7% | -4.5 [-8.2, -1.5] | 6 / 0 | 0.031 | ±2.3 | **worse** |
| o3g_r3_4b_rag | o3g_r4_4b_rag | Qwen3.5-4B | all checked | 424 | 81.1% | 82.3% | +1.2 [-0.2, +2.8] | 3 / 8 | 0.227 | ±1.3 | **tie** |
| o3g_r3_4b_rag | o3g_r4_4b_rag | Qwen3.5-4B | answerable | 285 | 84.6% | 83.5% | -1.1 [-2.5, +0.0] | 3 / 0 | 0.250 | ±1.6 | **tie** |
| o3g_r3_4b_rag | o3g_r4_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 74.1% | 79.9% | +5.8 [+2.2, +10.1] | 0 / 8 | 0.008 | ±2.3 | **better** |
| o3g_r3_4b_rag | o3g_r4_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 54.8% | 58.1% | +3.2 [+0.0, +8.1] | 0 / 2 | 0.500 | ±3.4 | **tie** |
| o3g_r3_4b_rag | o3g_r4_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 86.9% | 87.9% | +1.0 [-0.3, +2.8] | 1 / 4 | 0.375 | ±1.6 | **tie** |
| o3g_r3_4b_rag | o3g_r4_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 68.7% | 70.1% | +1.5 [-2.2, +5.2] | 2 / 4 | 0.688 | ±2.3 | **tie** |
| o3g_r4_4b_rag | o3g_r5_4b_rag | Qwen3.5-4B | all checked | 424 | 82.3% | 82.5% | +0.2 [+0.0, +0.7] | 0 / 1 | 1.000 | ±1.3 | **tie** |
| o3g_r4_4b_rag | o3g_r5_4b_rag | Qwen3.5-4B | answerable | 285 | 83.5% | 83.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±1.6 | **tie** |
| o3g_r4_4b_rag | o3g_r5_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 79.9% | 80.6% | +0.7 [+0.0, +2.2] | 0 / 1 | 1.000 | ±2.3 | **tie** |
| o3g_r4_4b_rag | o3g_r5_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 58.1% | 58.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r4_4b_rag | o3g_r5_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 87.9% | 88.3% | +0.3 [+0.0, +1.0] | 0 / 1 | 1.000 | ±1.6 | **tie** |
| o3g_r4_4b_rag | o3g_r5_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 70.1% | 70.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±2.3 | **tie** |
| o3g_r5_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 82.5% | 82.3% | -0.2 [-2.1, +1.7] | 9 / 8 | 1.000 | ±1.3 | **tie** |
| o3g_r5_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 83.5% | 84.2% | +0.7 [-0.7, +2.1] | 1 / 3 | 0.625 | ±1.6 | **tie** |
| o3g_r5_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 80.6% | 78.4% | -2.2 [-7.2, +2.9] | 8 / 5 | 0.581 | ±2.3 | **tie** |
| o3g_r5_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 58.1% | 56.5% | -1.6 [-8.1, +3.2] | 2 / 1 | 1.000 | ±3.4 | **tie** |
| o3g_r5_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 88.3% | 88.3% | +0.0 [-2.4, +2.4] | 6 / 6 | 1.000 | ±1.6 | **tie** |
| o3g_r5_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 70.1% | 69.4% | -0.7 [-3.7, +2.2] | 3 / 2 | 1.000 | ±2.3 | **tie** |
| o3g_b0_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 80.4% | 82.3% | +1.9 [-0.9, +4.5] | 15 / 23 | 0.256 | ±1.3 | **tie** |
| o3g_b0_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 85.3% | 84.2% | -1.1 [-3.5, +1.4] | 8 / 5 | 0.581 | ±1.6 | **tie** |
| o3g_b0_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 70.5% | 78.4% | +7.9 [+0.7, +15.1] | 7 / 18 | 0.043 | ±2.3 | **better** |
| o3g_b0_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 59.7% | 56.5% | -3.2 [-9.7, +3.2] | 3 / 1 | 0.625 | ±3.4 | **tie** |
| o3g_b0_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 82.1% | 88.3% | +6.2 [+3.1, +9.7] | 4 / 22 | 0.001 | ±1.6 | **better** |
| o3g_b0_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 76.9% | 69.4% | -7.5 [-12.7, -3.0] | 11 / 1 | 0.006 | ±2.3 | **worse** |
| o3g_nr_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 82.1% | 82.3% | +0.2 [-1.7, +2.1] | 7 / 8 | 1.000 | ±1.3 | **tie** |
| o3g_nr_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 84.9% | 84.2% | -0.7 [-2.1, +0.7] | 3 / 1 | 0.625 | ±1.6 | **tie** |
| o3g_nr_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 76.3% | 78.4% | +2.2 [-2.2, +7.2] | 4 / 7 | 0.549 | ±2.3 | **tie** |
| o3g_nr_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 58.1% | 56.5% | -1.6 [-8.1, +3.2] | 2 / 1 | 1.000 | ±3.4 | **tie** |
| o3g_nr_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 86.9% | 88.3% | +1.4 [+0.0, +3.1] | 1 / 5 | 0.219 | ±1.6 | **tie** |
| o3g_nr_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 71.6% | 69.4% | -2.2 [-6.7, +2.2] | 6 / 3 | 0.508 | ±2.3 | **tie** |
| o3t_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | all checked | 424 | 78.3% | 80.4% | +2.1 [-0.7, +5.2] | 16 / 25 | 0.211 | ±1.3 | **tie** |
| o3t_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | answerable | 285 | 80.0% | 85.3% | +5.3 [+2.5, +8.1] | 2 / 17 | 0.001 | ±1.6 | **better** |
| o3t_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 74.8% | 70.5% | -4.3 [-10.8, +2.2] | 14 / 8 | 0.286 | ±2.3 | **tie** |
| o3t_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 58.1% | 59.7% | +1.6 [-4.8, +8.1] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3t_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 80.3% | 82.1% | +1.7 [-2.1, +5.9] | 14 / 19 | 0.487 | ±1.6 | **tie** |
| o3t_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 73.9% | 76.9% | +3.0 [-0.7, +7.5] | 2 / 6 | 0.289 | ±2.3 | **tie** |
| o3t_final_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 81.4% | 82.3% | +0.9 [-1.4, +3.1] | 10 / 14 | 0.541 | ±1.3 | **tie** |
| o3t_final_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 83.2% | 84.2% | +1.1 [-1.1, +3.2] | 3 / 6 | 0.508 | ±1.6 | **tie** |
| o3t_final_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 77.7% | 78.4% | +0.7 [-4.3, +6.5] | 7 / 8 | 1.000 | ±2.3 | **tie** |
| o3t_final_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 54.8% | 56.5% | +1.6 [-4.8, +8.1] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3t_final_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 86.2% | 88.3% | +2.1 [-0.7, +4.8] | 6 / 12 | 0.238 | ±1.6 | **tie** |
| o3t_final_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 70.9% | 69.4% | -1.5 [-5.2, +2.2] | 4 / 2 | 0.688 | ±2.3 | **tie** |
| o3l_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | all checked | 424 | 79.7% | 80.4% | +0.7 [-2.1, +3.8] | 18 / 21 | 0.749 | ±1.3 | **tie** |
| o3l_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | answerable | 285 | 83.5% | 85.3% | +1.8 [-0.7, +4.2] | 4 / 9 | 0.267 | ±1.6 | **tie** |
| o3l_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 71.9% | 70.5% | -1.4 [-8.6, +5.8] | 14 / 12 | 0.845 | ±2.3 | **tie** |
| o3l_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 50.0% | 59.7% | +9.7 [+1.6, +19.4] | 1 / 7 | 0.070 | ±3.4 | **better** |
| o3l_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 84.5% | 82.1% | -2.4 [-5.9, +1.0] | 17 / 10 | 0.248 | ±1.6 | **tie** |
| o3l_b0_4b_rag | o3g_b0_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 69.4% | 76.9% | +7.5 [+3.0, +12.7] | 1 / 11 | 0.006 | ±2.3 | **better** |
| o3l_r6_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 82.3% | 82.3% | +0.0 [-2.1, +2.1] | 11 / 11 | 1.000 | ±1.3 | **tie** |
| o3l_r6_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 83.9% | 84.2% | +0.4 [-1.1, +1.8] | 2 / 3 | 1.000 | ±1.6 | **tie** |
| o3l_r6_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 79.1% | 78.4% | -0.7 [-6.5, +5.0] | 9 / 8 | 1.000 | ±2.3 | **tie** |
| o3l_r6_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 50.0% | 56.5% | +6.5 [+0.0, +14.5] | 1 / 5 | 0.219 | ±3.4 | **tie** |
| o3l_r6_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 88.6% | 88.3% | -0.3 [-3.1, +2.4] | 9 / 8 | 1.000 | ±1.6 | **tie** |
| o3l_r6_4b_rag | o3g_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 68.7% | 69.4% | +0.7 [-2.2, +3.7] | 2 / 3 | 1.000 | ±2.3 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | tool cases | 192 | 79.7% | 78.1% | -1.6 [-5.2, +2.1] | 8 / 5 | 0.581 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 83.8% | 78.4% | -5.4 [-13.5, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 82.1% | 81.2% | -0.9 [-6.0, +4.3] | 5 / 4 | 1.000 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 76.0% | 73.3% | -2.7 [-8.0, +2.7] | 3 / 1 | 0.625 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 76.9% | 92.3% | +15.4 [+0.0, +38.5] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 74.5% | 74.5% | +0.0 [-6.4, +6.4] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 92.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 83.3% | 77.8% | -5.6 [-13.9, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 78.1% | 74.0% | -4.1 [-11.0, +2.7] | 5 / 2 | 0.453 | ±0.0 | **tie** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | tool cases | 192 | 78.1% | 86.5% | +8.3 [+3.1, +13.5] | 6 / 22 | 0.004 | ±0.0 | **better** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 78.4% | 86.5% | +8.1 [-2.7, +21.6] | 1 / 4 | 0.375 | ±0.0 | **tie** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 81.2% | 85.5% | +4.3 [-2.6, +11.1] | 6 / 11 | 0.332 | ±0.0 | **tie** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 73.3% | 88.0% | +14.7 [+6.7, +22.7] | 0 / 11 | 0.001 | ±0.0 | **better** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 92.3% | 100.0% | +7.7 [+0.0, +23.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 74.5% | 89.4% | +14.9 [+6.4, +25.5] | 0 / 7 | 0.016 | ±0.0 | **better** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 85.7% | -7.1 [-28.6, +14.3] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 77.8% | 86.1% | +8.3 [-2.8, +19.4] | 1 / 4 | 0.375 | ±0.0 | **tie** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 74.0% | 82.2% | +8.2 [-1.4, +17.8] | 3 / 9 | 0.146 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | tool cases | 192 | 86.5% | 83.9% | -2.6 [-8.9, +3.6] | 22 / 17 | 0.522 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 86.5% | 81.1% | -5.4 [-21.6, +8.1] | 5 / 3 | 0.727 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 85.5% | 86.3% | +0.9 [-6.8, +8.5] | 11 / 12 | 1.000 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 88.0% | 80.0% | -8.0 [-18.7, +2.7] | 11 / 5 | 0.210 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 89.4% | 80.9% | -8.5 [-21.3, +4.3] | 7 / 3 | 0.344 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 85.7% | 64.3% | -21.4 [-57.1, +14.3] | 5 / 2 | 0.453 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 86.1% | 80.6% | -5.6 [-22.2, +11.1] | 5 / 3 | 0.727 | ±0.0 | **tie** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 88.9% | 77.8% | -11.1 [-33.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 82.2% | 89.0% | +6.8 [-2.7, +16.4] | 4 / 9 | 0.267 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | tool cases | 192 | 83.9% | 83.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 81.1% | 81.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 86.3% | 86.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 80.9% | 80.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 80.6% | 80.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 77.8% | 77.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 89.0% | 89.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | tool cases | 192 | 83.9% | 83.3% | -0.5 [-1.6, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 81.1% | 81.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 86.3% | 85.5% | -0.9 [-2.6, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 80.9% | 80.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 80.6% | 80.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 77.8% | 66.7% | -11.1 [-33.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 89.0% | 89.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 83.3% | 83.3% | +0.0 [-2.1, +2.1] | 2 / 2 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 81.1% | 81.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 85.5% | 85.5% | +0.0 [-2.6, +2.6] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 80.0% | 80.0% | +0.0 [-4.0, +4.0] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 80.9% | 80.9% | +0.0 [-6.4, +6.4] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 80.6% | 80.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 66.7% | 77.8% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 89.0% | 87.7% | -1.4 [-4.1, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 79.7% | 83.3% | +3.6 [-3.6, +10.9] | 22 / 29 | 0.401 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 83.8% | 81.1% | -2.7 [-18.9, +13.5] | 5 / 4 | 1.000 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 82.1% | 85.5% | +3.4 [-5.1, +11.1] | 11 / 15 | 0.557 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 76.0% | 80.0% | +4.0 [-9.3, +17.3] | 11 / 14 | 0.690 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 76.9% | 100.0% | +23.1 [+0.0, +46.2] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 74.5% | 80.9% | +6.4 [-10.6, +23.4] | 7 / 10 | 0.629 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 64.3% | -28.6 [-57.1, -7.1] | 4 / 0 | 0.125 | ±0.0 | **worse** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 83.3% | 80.6% | -2.8 [-19.4, +13.9] | 5 / 4 | 1.000 | ±0.0 | **tie** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 88.9% | 77.8% | -11.1 [-33.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 78.1% | 87.7% | +9.6 [-1.4, +20.5] | 5 / 12 | 0.143 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 81.8% | 83.3% | +1.6 [-5.2, +8.3] | 21 / 24 | 0.766 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 78.4% | 81.1% | +2.7 [-13.5, +18.9] | 4 / 5 | 1.000 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 82.1% | 85.5% | +3.4 [-4.3, +11.1] | 9 / 13 | 0.523 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 81.3% | 80.0% | -1.3 [-14.7, +10.7] | 12 / 11 | 1.000 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 92.3% | 100.0% | +7.7 [+0.0, +23.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 85.1% | 80.9% | -4.3 [-19.1, +10.6] | 8 / 6 | 0.791 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 64.3% | -28.6 [-57.1, -7.1] | 4 / 0 | 0.125 | ±0.0 | **worse** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 77.8% | 80.6% | +2.8 [-13.9, +19.4] | 4 / 5 | 1.000 | ±0.0 | **tie** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 77.8% | 77.8% | +0.0 [-33.3, +33.3] | 1 / 1 | 1.000 | ±0.0 | **(small)** |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 78.1% | 87.7% | +9.6 [+0.0, +19.2] | 4 / 11 | 0.118 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases | 192 | 78.1% | 79.7% | +1.6 [-2.6, +5.7] | 6 / 9 | 0.607 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 83.8% | 83.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 81.2% | 82.1% | +0.9 [-4.3, +6.0] | 4 / 5 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 73.3% | 76.0% | +2.7 [-4.0, +9.3] | 2 / 4 | 0.688 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 76.9% | 76.9% | +0.0 [-23.1, +23.1] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 70.2% | 74.5% | +4.3 [-6.4, +14.9] | 2 / 4 | 0.688 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 92.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 77.8% | 88.9% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 78.1% | 78.1% | +0.0 [-6.8, +6.8] | 3 / 3 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 83.3% | 83.3% | +0.0 [-1.6, +1.6] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 81.1% | 81.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 85.5% | 85.5% | +0.0 [-2.6, +2.6] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 80.9% | 80.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 80.6% | 80.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 66.7% | 77.8% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 89.0% | 87.7% | -1.4 [-4.1, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases | 192 | 79.2% | 79.7% | +0.5 [-3.1, +4.2] | 6 / 7 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 78.4% | 83.8% | +5.4 [+0.0, +13.5] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 81.2% | 82.1% | +0.9 [-4.3, +6.0] | 4 / 5 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 76.0% | 76.0% | +0.0 [-5.3, +5.3] | 2 / 2 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 76.9% | 76.9% | +0.0 [-23.1, +23.1] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 76.6% | 74.5% | -2.1 [-8.5, +4.3] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 85.7% | 92.9% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 77.8% | 83.3% | +5.6 [+0.0, +13.9] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 88.9% | 88.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 79.5% | 78.1% | -1.4 [-8.2, +4.1] | 3 / 2 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 83.9% | 83.3% | -0.5 [-2.1, +1.0] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 81.1% | 81.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 86.3% | 85.5% | -0.9 [-4.3, +1.7] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 80.9% | 80.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 80.6% | 80.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 77.8% | 77.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 89.0% | 87.7% | -1.4 [-6.8, +2.7] | 2 / 1 | 1.000 | ±0.0 | **tie** |
| o3g_b0_4b_fup | o3g_r1_4b_fup | Qwen3.5-4B | all checked | 60 | 68.3% | 65.0% | -3.3 [-8.3, +0.0] | 2 / 0 | 0.500 | ±3.4 | **tie** |
| o3g_b0_4b_fup | o3g_r1_4b_fup | Qwen3.5-4B | answerable | 60 | 68.3% | 65.0% | -3.3 [-8.3, +0.0] | 2 / 0 | 0.500 | ±3.4 | **tie** |
| o3g_b0_4b_fup | o3g_r1_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 61.5% | 57.7% | -3.8 [-11.5, +0.0] | 1 / 0 | 1.000 | ±5.2 | **tie** |
| o3g_b0_4b_fup | o3g_r1_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 40.0% | 30.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_b0_4b_fup | o3g_r1_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 60.0% | 56.7% | -3.3 [-10.0, +0.0] | 1 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_b0_4b_fup | o3g_r1_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_b0_4b_fup | o3g_r1_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r1_4b_fup | o3g_r2_4b_fup | Qwen3.5-4B | all checked | 60 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r1_4b_fup | o3g_r2_4b_fup | Qwen3.5-4B | answerable | 60 | 65.0% | 65.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r1_4b_fup | o3g_r2_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 57.7% | 57.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3g_r1_4b_fup | o3g_r2_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 30.0% | 30.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r1_4b_fup | o3g_r2_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 56.7% | 56.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_r1_4b_fup | o3g_r2_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r1_4b_fup | o3g_r2_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r2_4b_fup | o3g_r3_4b_fup | Qwen3.5-4B | all checked | 60 | 65.0% | 66.7% | +1.7 [+0.0, +5.0] | 0 / 1 | 1.000 | ±3.4 | **tie** |
| o3g_r2_4b_fup | o3g_r3_4b_fup | Qwen3.5-4B | answerable | 60 | 65.0% | 66.7% | +1.7 [+0.0, +5.0] | 0 / 1 | 1.000 | ±3.4 | **tie** |
| o3g_r2_4b_fup | o3g_r3_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 57.7% | 61.5% | +3.8 [+0.0, +11.5] | 0 / 1 | 1.000 | ±5.2 | **tie** |
| o3g_r2_4b_fup | o3g_r3_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 30.0% | 30.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r2_4b_fup | o3g_r3_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 56.7% | 60.0% | +3.3 [+0.0, +10.0] | 0 / 1 | 1.000 | ±4.9 | **tie** |
| o3g_r2_4b_fup | o3g_r3_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r2_4b_fup | o3g_r3_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r3_4b_fup | o3g_r4_4b_fup | Qwen3.5-4B | all checked | 60 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r3_4b_fup | o3g_r4_4b_fup | Qwen3.5-4B | answerable | 60 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3g_r3_4b_fup | o3g_r4_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 61.5% | 61.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3g_r3_4b_fup | o3g_r4_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 30.0% | 30.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r3_4b_fup | o3g_r4_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 60.0% | 60.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_r3_4b_fup | o3g_r4_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r3_4b_fup | o3g_r4_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r4_4b_fup | o3g_r5_4b_fup | Qwen3.5-4B | all checked | 60 | 66.7% | 96.7% | +30.0 [+18.3, +41.7] | 1 / 19 | 0.000 | ±3.4 | **better** |
| o3g_r4_4b_fup | o3g_r5_4b_fup | Qwen3.5-4B | answerable | 60 | 66.7% | 96.7% | +30.0 [+18.3, +41.7] | 1 / 19 | 0.000 | ±3.4 | **better** |
| o3g_r4_4b_fup | o3g_r5_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 61.5% | 92.3% | +30.8 [+11.5, +50.0] | 1 / 9 | 0.021 | ±5.2 | **better** |
| o3g_r4_4b_fup | o3g_r5_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 30.0% | 100.0% | +70.0 [+40.0, +100.0] | 0 / 7 | 0.016 | ±8.4 | **better** |
| o3g_r4_4b_fup | o3g_r5_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 60.0% | 100.0% | +40.0 [+23.3, +56.7] | 0 / 12 | 0.000 | ±4.9 | **better** |
| o3g_r4_4b_fup | o3g_r5_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r4_4b_fup | o3g_r5_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r5_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | all checked | 60 | 96.7% | 90.0% | -6.7 [-13.3, -1.7] | 4 / 0 | 0.125 | ±3.4 | **worse** |
| o3g_r5_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | answerable | 60 | 96.7% | 90.0% | -6.7 [-13.3, -1.7] | 4 / 0 | 0.125 | ±3.4 | **worse** |
| o3g_r5_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 92.3% | 76.9% | -15.4 [-30.8, -3.8] | 4 / 0 | 0.125 | ±5.2 | **worse** |
| o3g_r5_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r5_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3g_r5_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_r5_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 60.0% | -40.0 [-70.0, -10.0] | 4 / 0 | 0.125 | ±8.4 | **worse** |
| o3g_b0_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | all checked | 60 | 68.3% | 90.0% | +21.7 [+6.7, +36.7] | 5 / 18 | 0.011 | ±3.4 | **better** |
| o3g_b0_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | answerable | 60 | 68.3% | 90.0% | +21.7 [+6.7, +36.7] | 5 / 18 | 0.011 | ±3.4 | **better** |
| o3g_b0_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 61.5% | 76.9% | +15.4 [-11.5, +42.3] | 5 / 9 | 0.424 | ±5.2 | **tie** |
| o3g_b0_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 40.0% | 100.0% | +60.0 [+30.0, +90.0] | 0 / 6 | 0.031 | ±8.4 | **better** |
| o3g_b0_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 60.0% | 100.0% | +40.0 [+23.3, +56.7] | 0 / 12 | 0.000 | ±4.9 | **better** |
| o3g_b0_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_b0_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 60.0% | -40.0 [-70.0, -10.0] | 4 / 0 | 0.125 | ±8.4 | **worse** |
| o3g_nr_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | all checked | 60 | 61.7% | 90.0% | +28.3 [+16.7, +40.0] | 1 / 18 | 0.000 | ±3.4 | **better** |
| o3g_nr_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | answerable | 60 | 61.7% | 90.0% | +28.3 [+16.7, +40.0] | 1 / 18 | 0.000 | ±3.4 | **better** |
| o3g_nr_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 38.5% | 76.9% | +38.5 [+19.2, +57.7] | 1 / 11 | 0.006 | ±5.2 | **better** |
| o3g_nr_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 40.0% | 100.0% | +60.0 [+30.0, +90.0] | 0 / 6 | 0.031 | ±8.4 | **better** |
| o3g_nr_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 60.0% | 100.0% | +40.0 [+23.3, +56.7] | 0 / 12 | 0.000 | ±4.9 | **better** |
| o3g_nr_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3g_nr_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 60.0% | 60.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | all checked | 60 | 66.7% | 68.3% | +1.7 [-5.0, +10.0] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3t_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | answerable | 60 | 66.7% | 68.3% | +1.7 [-5.0, +10.0] | 2 / 3 | 1.000 | ±3.4 | **tie** |
| o3t_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 61.5% | 61.5% | +0.0 [-11.5, +11.5] | 1 / 1 | 1.000 | ±5.2 | **tie** |
| o3t_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 40.0% | 40.0% | +0.0 [-30.0, +30.0] | 1 / 1 | 1.000 | ±8.4 | **tie** |
| o3t_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 56.7% | 60.0% | +3.3 [-6.7, +16.7] | 1 / 2 | 1.000 | ±4.9 | **tie** |
| o3t_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | all checked | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3t_final_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | answerable | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3t_final_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 76.9% | 76.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3t_final_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3t_final_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 60.0% | 60.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | all checked | 60 | 66.7% | 68.3% | +1.7 [-6.7, +10.0] | 3 / 4 | 1.000 | ±3.4 | **tie** |
| o3l_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | answerable | 60 | 66.7% | 68.3% | +1.7 [-6.7, +10.0] | 3 / 4 | 1.000 | ±3.4 | **tie** |
| o3l_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 65.4% | 61.5% | -3.8 [-15.4, +7.7] | 2 / 1 | 1.000 | ±5.2 | **tie** |
| o3l_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 50.0% | 40.0% | -10.0 [-40.0, +20.0] | 2 / 1 | 1.000 | ±8.4 | **tie** |
| o3l_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 53.3% | 60.0% | +6.7 [-6.7, +20.0] | 1 / 3 | 0.625 | ±4.9 | **tie** |
| o3l_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_b0_4b_fup | o3g_b0_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_r6_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | all checked | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3l_r6_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | answerable | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3l_r6_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 76.9% | 76.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3l_r6_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_r6_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3l_r6_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_r6_4b_fup | o3g_r6_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 60.0% | 60.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 84.4% | 82.3% | -2.1 [-5.9, +1.7] | 36 / 27 | 0.314 | ±1.3 | **tie** |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 87.7% | 83.9% | -3.9 [-7.0, -0.7] | 17 / 6 | 0.035 | ±1.6 | **worse** |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 77.7% | 79.1% | +1.4 [-7.2, +10.1] | 19 / 21 | 0.875 | ±2.3 | **tie** |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 58.1% | 50.0% | -8.1 [-21.0, +4.8] | 11 / 6 | 0.332 | ±3.4 | **tie** |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 87.6% | 88.6% | +1.0 [-2.8, +4.8] | 14 / 17 | 0.720 | ±1.6 | **tie** |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 77.6% | 68.7% | -9.0 [-17.2, -0.7] | 22 / 10 | 0.050 | ±2.3 | **worse** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 88.5% | 83.9% | -4.7 [-10.9, +1.6] | 23 / 14 | 0.188 | ±0.0 | **tie** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 83.8% | 81.1% | -2.7 [-18.9, +13.5] | 5 / 4 | 1.000 | ±0.0 | **tie** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 94.0% | 86.3% | -7.7 [-13.7, -1.7] | 12 / 3 | 0.035 | ±0.0 | **worse** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 80.0% | 80.0% | +0.0 [-12.0, +12.0] | 11 / 11 | 1.000 | ±0.0 | **tie** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 80.9% | 80.9% | +0.0 [-14.9, +14.9] | 7 / 7 | 1.000 | ±0.0 | **tie** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 64.3% | -28.6 [-57.1, -7.1] | 4 / 0 | 0.125 | ±0.0 | **worse** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 83.3% | 80.6% | -2.8 [-19.4, +13.9] | 5 / 4 | 1.000 | ±0.0 | **tie** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 88.9% | 77.8% | -11.1 [-33.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3l_ref_4b_none | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 93.2% | 89.0% | -4.1 [-12.3, +2.7] | 6 / 3 | 0.508 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3g_b0_2b_rag | o3g_r1_2b_rag | 2.54 → 2.33 | 852 → 638 | 207 → 98 | 108 → 39 | 108 → 0 | 0/842 → 0/632 | 2.1 s → 2.3 s |
| o3g_r1_2b_rag | o3g_r2_2b_rag | 2.33 → 2.20 | 638 → 545 | 98 → 108 | 39 → 30 | 0 → 0 | 0/632 → 0/564 | 2.3 s → 2.1 s |
| o3g_r2_2b_rag | o3g_r3_2b_rag | 2.20 → 2.03 | 545 → 553 | 108 → 102 | 30 → 4 | 0 → 0 | 0/564 → 72/564 | 2.1 s → 1.8 s |
| o3g_r3_2b_rag | o3g_r4_2b_rag | 2.03 → 1.97 | 553 → 528 | 102 → 94 | 4 → 4 | 0 → 0 | 72/564 → 94/599 | 1.8 s → 1.8 s |
| o3g_r4_2b_rag | o3g_r5_2b_rag | 1.97 → 1.97 | 528 → 528 | 94 → 94 | 4 → 4 | 0 → 0 | 94/599 → 94/599 | 1.8 s → 1.7 s |
| o3g_r5_2b_rag | o3g_r6_2b_rag | 1.97 → 1.73 | 528 → 427 | 94 → 101 | 4 → 4 | 0 → 0 | 94/599 → 92/479 | 1.7 s → 1.4 s |
| o3g_b0_2b_rag | o3g_r6_2b_rag | 2.54 → 1.73 | 852 → 427 | 207 → 101 | 108 → 4 | 108 → 0 | 0/842 → 92/479 | 2.1 s → 1.4 s |
| o3g_nr_2b_rag | o3g_r6_2b_rag | 2.21 → 1.73 | 527 → 427 | 98 → 101 | 4 → 4 | 0 → 0 | 3/545 → 92/479 | 1.9 s → 1.4 s |
| o3t_b0_2b_rag | o3g_b0_2b_rag | 2.51 → 2.54 | 846 → 852 | 214 → 207 | 98 → 108 | 98 → 108 | 0/815 → 0/842 | 7.9 s → 2.1 s (different machines: local vs kaggle-gpu; not comparable) |
| o3t_final_2b_rag | o3g_r6_2b_rag | 1.91 → 1.73 | 442 → 427 | 94 → 101 | 8 → 4 | 0 → 0 | 97/565 → 92/479 | 5.8 s → 1.4 s (different machines: local vs kaggle-gpu; not comparable) |
| o3l_b0_2b_rag | o3g_b0_2b_rag | 2.45 → 2.54 | 837 → 852 | 220 → 207 | 90 → 108 | 90 → 108 | 0/778 → 0/842 | 33.2 s → 2.1 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_r6_2b_rag | o3g_r6_2b_rag | 1.85 → 1.73 | 437 → 427 | 96 → 101 | 5 → 4 | 0 → 0 | 96/535 → 92/479 | 12.8 s → 1.4 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | 2.82 → 2.67 | 1066 → 716 | 295 → 124 | 42 → 24 | 42 → 0 | 0/408 → 0/363 | 2.3 s → 2.6 s |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | 2.67 → 2.09 | 716 → 286 | 124 → 153 | 24 → 4 | 0 → 0 | 0/363 → 0/220 | 2.6 s → 0.8 s |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | 2.09 → 1.04 | 286 → 268 | 153 → 123 | 4 → 0 | 0 → 0 | 0/220 → 144/179 | 0.8 s → 0.1 s |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | 1.04 → 1.07 | 268 → 270 | 123 → 120 | 0 → 0 | 0 → 0 | 144/179 → 144/186 | 0.1 s → 0.1 s |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | 1.07 → 1.07 | 270 → 270 | 120 → 120 | 0 → 0 | 0 → 0 | 144/186 → 144/186 | 0.1 s → 0.1 s |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | 1.07 → 1.04 | 270 → 259 | 120 → 123 | 0 → 0 | 0 → 0 | 144/186 → 144/180 | 0.1 s → 0.1 s |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | 2.82 → 1.04 | 1066 → 259 | 295 → 123 | 42 → 0 | 42 → 0 | 0/408 → 144/180 | 2.3 s → 0.1 s |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | 2.60 → 1.04 | 610 → 259 | 123 → 123 | 5 → 0 | 0 → 0 | 3/314 → 144/180 | 2.2 s → 0.1 s |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | 2.78 → 2.82 | 1056 → 1066 | 296 → 295 | 42 → 42 | 42 → 42 | 0/399 → 0/408 | 10.3 s → 2.3 s (different machines: local vs kaggle-gpu; not comparable) |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | 1.06 → 1.04 | 260 → 259 | 121 → 123 | 0 → 0 | 0 → 0 | 144/183 → 144/180 | 1.6 s → 0.1 s (different machines: local vs kaggle-gpu; not comparable) |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | 2.77 → 2.82 | 1067 → 1066 | 305 → 295 | 37 → 42 | 37 → 42 | 0/392 → 0/408 | 39.4 s → 2.3 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | 1.06 → 1.04 | 260 → 259 | 121 → 123 | 0 → 0 | 0 → 0 | 144/184 → 144/180 | 8.5 s → 0.1 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3g_b0_2b_fup | o3g_r1_2b_fup | 1.90 → 1.83 | 745 → 585 | 299 → 147 | 3 → 0 | 3 → 0 | 0/57 → 0/50 | 1.7 s → 2.0 s |
| o3g_r1_2b_fup | o3g_r2_2b_fup | 1.83 → 1.83 | 585 → 585 | 147 → 147 | 0 → 0 | 0 → 0 | 0/50 → 0/50 | 2.0 s → 2.1 s |
| o3g_r2_2b_fup | o3g_r3_2b_fup | 1.83 → 1.83 | 585 → 585 | 147 → 147 | 0 → 0 | 0 → 0 | 0/50 → 0/50 | 2.1 s → 1.8 s |
| o3g_r3_2b_fup | o3g_r4_2b_fup | 1.83 → 1.85 | 585 → 587 | 147 → 144 | 0 → 0 | 0 → 0 | 0/50 → 0/52 | 1.8 s → 1.9 s |
| o3g_r4_2b_fup | o3g_r5_2b_fup | 1.85 → 1.40 | 587 → 510 | 144 → 83 | 0 → 0 | 0 → 0 | 0/52 → 20/44 | 1.9 s → 1.4 s |
| o3g_r5_2b_fup | o3g_r6_2b_fup | 1.40 → 1.20 | 510 → 394 | 83 → 82 | 0 → 0 | 0 → 0 | 20/44 → 20/32 | 1.4 s → 1.1 s |
| o3g_b0_2b_fup | o3g_r6_2b_fup | 1.90 → 1.20 | 745 → 394 | 299 → 82 | 3 → 0 | 3 → 0 | 0/57 → 20/32 | 1.7 s → 1.1 s |
| o3g_nr_2b_fup | o3g_r6_2b_fup | 1.53 → 1.20 | 423 → 394 | 133 → 82 | 0 → 0 | 0 → 0 | 0/32 → 20/32 | 1.5 s → 1.1 s |
| o3t_b0_2b_fup | o3g_b0_2b_fup | 1.88 → 1.90 | 743 → 745 | 312 → 299 | 1 → 3 | 1 → 3 | 0/54 → 0/57 | 6.5 s → 1.7 s (different machines: local vs kaggle-gpu; not comparable) |
| o3t_final_2b_fup | o3g_r6_2b_fup | 1.15 → 1.20 | 388 → 394 | 78 → 82 | 0 → 0 | 0 → 0 | 20/29 → 20/32 | 2.3 s → 1.1 s (different machines: local vs kaggle-gpu; not comparable) |
| o3l_b0_2b_fup | o3g_b0_2b_fup | 1.88 → 1.90 | 733 → 745 | 296 → 299 | 2 → 3 | 2 → 3 | 0/55 → 0/57 | 28.4 s → 1.7 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_r6_2b_fup | o3g_r6_2b_fup | 1.28 → 1.20 | 402 → 394 | 79 → 82 | 0 → 0 | 0 → 0 | 20/37 → 20/32 | 16.2 s → 1.1 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 2.20 → 1.85 | 495 → 437 | 216 → 96 | 52 → 5 | 52 → 0 | 0/609 → 96/535 | 17.9 s → 12.8 s |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 2.07 → 1.06 | 592 → 260 | 446 → 121 | 7 → 0 | 7 → 0 | 0/223 → 144/184 | 25.2 s → 8.5 s |
| o3g_b0_4b_rag | o3g_r1_4b_rag | 1.30 → 1.29 | 563 → 516 | 238 → 95 | 6 → 3 | 6 → 0 | 0/164 → 0/153 | 1.6 s → 1.8 s |
| o3g_r1_4b_rag | o3g_r2_4b_rag | 1.29 → 1.37 | 516 → 447 | 95 → 120 | 3 → 2 | 0 → 0 | 0/153 → 0/189 | 1.8 s → 1.8 s |
| o3g_r2_4b_rag | o3g_r3_4b_rag | 1.37 → 1.14 | 447 → 452 | 120 → 119 | 2 → 0 | 0 → 0 | 0/189 → 68/160 | 1.8 s → 1.4 s |
| o3g_r3_4b_rag | o3g_r4_4b_rag | 1.14 → 1.02 | 452 → 429 | 119 → 118 | 0 → 0 | 0 → 0 | 68/160 → 90/168 | 1.4 s → 1.5 s |
| o3g_r4_4b_rag | o3g_r5_4b_rag | 1.02 → 1.02 | 429 → 429 | 118 → 118 | 0 → 0 | 0 → 0 | 90/168 → 90/168 | 1.5 s → 1.5 s |
| o3g_r5_4b_rag | o3g_r6_4b_rag | 1.02 → 1.07 | 429 → 363 | 118 → 125 | 0 → 0 | 0 → 0 | 90/168 → 90/203 | 1.5 s → 1.2 s |
| o3g_b0_4b_rag | o3g_r6_4b_rag | 1.30 → 1.07 | 563 → 363 | 238 → 125 | 6 → 0 | 6 → 0 | 0/164 → 90/203 | 1.6 s → 1.2 s |
| o3g_nr_4b_rag | o3g_r6_4b_rag | 1.35 → 1.07 | 439 → 363 | 108 → 125 | 0 → 0 | 0 → 0 | 0/193 → 90/203 | 1.5 s → 1.2 s |
| o3t_b0_4b_rag | o3g_b0_4b_rag | 1.27 → 1.30 | 554 → 563 | 258 → 238 | 4 → 6 | 4 → 6 | 0/135 → 0/164 | 7.3 s → 1.6 s (different machines: local vs kaggle-gpu; not comparable) |
| o3t_final_4b_rag | o3g_r6_4b_rag | 1.05 → 1.07 | 375 → 363 | 130 → 125 | 3 → 0 | 0 → 0 | 93/188 → 90/203 | 5.3 s → 1.2 s (different machines: local vs kaggle-gpu; not comparable) |
| o3l_b0_4b_rag | o3g_b0_4b_rag | 1.24 → 1.30 | 541 → 563 | 231 → 238 | 6 → 6 | 6 → 6 | 0/125 → 0/164 | 38.8 s → 1.6 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_r6_4b_rag | o3g_r6_4b_rag | 0.98 → 1.07 | 346 → 363 | 135 → 125 | 0 → 0 | 0 → 0 | 90/140 → 90/203 | 28.8 s → 1.2 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | 1.85 → 1.90 | 754 → 592 | 327 → 129 | 3 → 5 | 3 → 0 | 0/170 → 0/185 | 2.8 s → 3.0 s |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | 1.90 → 2.08 | 592 → 273 | 129 → 138 | 5 → 9 | 0 → 0 | 0/185 → 0/227 | 3.0 s → 1.6 s |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | 2.08 → 0.94 | 273 → 261 | 138 → 132 | 9 → 5 | 0 → 0 | 0/227 → 154/160 | 1.6 s → 0.3 s |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | 0.94 → 0.94 | 261 → 261 | 132 → 132 | 5 → 5 | 0 → 0 | 154/160 → 154/160 | 0.3 s → 0.3 s |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | 0.94 → 0.94 | 261 → 261 | 132 → 132 | 5 → 5 | 0 → 0 | 154/160 → 154/160 | 0.3 s → 0.3 s |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | 0.94 → 0.95 | 261 → 258 | 132 → 136 | 5 → 6 | 0 → 0 | 154/160 → 154/163 | 0.3 s → 0.3 s |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | 1.85 → 0.95 | 754 → 258 | 327 → 136 | 3 → 6 | 3 → 0 | 0/170 → 154/163 | 2.8 s → 0.3 s |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | 1.91 → 0.95 | 522 → 258 | 135 → 136 | 1 → 6 | 0 → 0 | 1/185 → 154/163 | 2.5 s → 0.3 s |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | 1.88 → 1.85 | 746 → 754 | 312 → 327 | 3 → 3 | 3 → 3 | 0/174 → 0/170 | 13.3 s → 2.8 s (different machines: local vs kaggle-gpu; not comparable) |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | 0.96 → 0.95 | 257 → 258 | 133 → 136 | 7 → 6 | 0 → 0 | 154/164 → 154/163 | 3.5 s → 0.3 s (different machines: local vs kaggle-gpu; not comparable) |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | 1.78 → 1.85 | 747 → 754 | 354 → 327 | 1 → 3 | 1 → 3 | 0/153 → 0/170 | 65.0 s → 2.8 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | 0.96 → 0.95 | 259 → 258 | 135 → 136 | 7 → 6 | 0 → 0 | 155/165 → 154/163 | 11.2 s → 0.3 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3g_b0_4b_fup | o3g_r1_4b_fup | 1.37 → 1.35 | 549 → 493 | 248 → 111 | 2 → 2 | 2 → 0 | 0/24 → 0/21 | 1.8 s → 2.0 s |
| o3g_r1_4b_fup | o3g_r2_4b_fup | 1.35 → 1.35 | 493 → 493 | 111 → 111 | 2 → 2 | 0 → 0 | 0/21 → 0/21 | 2.0 s → 2.1 s |
| o3g_r2_4b_fup | o3g_r3_4b_fup | 1.35 → 1.35 | 493 → 493 | 111 → 111 | 2 → 0 | 0 → 0 | 0/21 → 0/21 | 2.1 s → 1.8 s |
| o3g_r3_4b_fup | o3g_r4_4b_fup | 1.35 → 1.33 | 493 → 492 | 111 → 111 | 0 → 0 | 0 → 0 | 0/21 → 0/21 | 1.8 s → 1.9 s |
| o3g_r4_4b_fup | o3g_r5_4b_fup | 1.33 → 1.02 | 492 → 467 | 111 → 71 | 0 → 0 | 0 → 0 | 0/21 → 20/21 | 1.9 s → 1.5 s |
| o3g_r5_4b_fup | o3g_r6_4b_fup | 1.02 → 1.07 | 467 → 377 | 71 → 72 | 0 → 0 | 0 → 0 | 20/21 → 21/24 | 1.5 s → 1.3 s |
| o3g_b0_4b_fup | o3g_r6_4b_fup | 1.37 → 1.07 | 549 → 377 | 248 → 72 | 2 → 0 | 2 → 0 | 0/24 → 21/24 | 1.8 s → 1.3 s |
| o3g_nr_4b_fup | o3g_r6_4b_fup | 1.40 → 1.07 | 398 → 377 | 120 → 72 | 0 → 0 | 0 → 0 | 0/24 → 21/24 | 1.6 s → 1.3 s |
| o3t_b0_4b_fup | o3g_b0_4b_fup | 1.30 → 1.37 | 527 → 549 | 238 → 248 | 1 → 2 | 1 → 2 | 0/19 → 0/24 | 7.6 s → 1.8 s (different machines: local vs kaggle-gpu; not comparable) |
| o3t_final_4b_fup | o3g_r6_4b_fup | 1.13 → 1.07 | 381 → 377 | 62 → 72 | 0 → 0 | 0 → 0 | 20/28 → 21/24 | 4.8 s → 1.3 s (different machines: local vs kaggle-gpu; not comparable) |
| o3l_b0_4b_fup | o3g_b0_4b_fup | 1.25 → 1.37 | 507 → 549 | 210 → 248 | 1 → 2 | 1 → 2 | 0/16 → 0/24 | 45.8 s → 1.8 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_r6_4b_fup | o3g_r6_4b_fup | 1.03 → 1.07 | 375 → 377 | 69 → 72 | 0 → 0 | 0 → 0 | 20/22 → 21/24 | 19.5 s → 1.3 s (different machines: kaggle-cpu vs kaggle-gpu; not comparable) |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 1.29 → 0.98 | 283 → 346 | 240 → 135 | 4 → 0 | 4 → 0 | 0/140 → 90/140 | 15.9 s → 28.8 s |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 1.96 → 0.96 | 404 → 259 | 328 → 135 | 5 → 7 | 5 → 0 | 0/194 → 155/165 | 34.1 s → 11.2 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o3g_b0_2b_rag | o3g_r1_2b_rag | 463 | +0.14 s [+0.10, +0.20] | +0.21 s [+0.15, +0.29] |
| o3g_r1_2b_rag | o3g_r2_2b_rag | 463 | -0.13 s [-0.19, -0.10] | -0.18 s [-0.23, -0.13] |
| o3g_r2_2b_rag | o3g_r3_2b_rag | 463 | -0.26 s [-0.32, -0.21] | -0.22 s [-0.26, -0.18] |
| o3g_r3_2b_rag | o3g_r4_2b_rag | 463 | +0.01 s [+0.00, +0.04] | -0.04 s [-0.07, -0.00] |
| o3g_r4_2b_rag | o3g_r5_2b_rag | 463 | -0.04 s [-0.07, -0.01] | -0.04 s [-0.07, -0.02] |
| o3g_r5_2b_rag | o3g_r6_2b_rag | 463 | -0.11 s [-0.16, -0.08] | -0.21 s [-0.26, -0.15] |
| o3g_b0_2b_rag | o3g_r6_2b_rag | 463 | -0.62 s [-0.72, -0.51] | -0.72 s [-0.85, -0.63] |
| o3g_nr_2b_rag | o3g_r6_2b_rag | 452 | -0.13 s [-0.20, -0.10] | -0.15 s [-0.23, -0.12] |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | 192 | +0.08 s [+0.01, +0.19] | +0.12 s [-0.01, +0.25] |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | 192 | -1.50 s [-1.69, -1.41] | -1.38 s [-1.48, -1.27] |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | 192 | -0.53 s [-0.63, -0.50] | -0.67 s [-0.80, -0.56] |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | 192 | +0.00 s [+0.00, +0.00] | +0.00 s [-0.00, +0.00] |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | 192 | -0.00 s [-0.00, -0.00] | -0.02 s [-0.02, -0.01] |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | 192 | +0.00 s [-0.00, +0.00] | -0.12 s [-0.20, -0.06] |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | 192 | -2.06 s [-2.20, -1.93] | -2.53 s [-2.81, -2.33] |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | 189 | -1.98 s [-2.06, -1.85] | -2.18 s [-2.30, -2.05] |
| o3g_b0_2b_fup | o3g_r1_2b_fup | 60 | +0.25 s [+0.11, +0.42] | +0.29 s [+0.12, +0.35] |
| o3g_r1_2b_fup | o3g_r2_2b_fup | 60 | +0.20 s [-0.04, +0.36] | +0.21 s [-0.01, +0.36] |
| o3g_r2_2b_fup | o3g_r3_2b_fup | 60 | -0.30 s [-0.41, -0.20] | -0.30 s [-0.46, -0.22] |
| o3g_r3_2b_fup | o3g_r4_2b_fup | 60 | +0.03 s [-0.05, +0.08] | +0.03 s [-0.05, +0.09] |
| o3g_r4_2b_fup | o3g_r5_2b_fup | 60 | -0.39 s [-0.72, -0.27] | -0.53 s [-0.79, -0.31] |
| o3g_r5_2b_fup | o3g_r6_2b_fup | 60 | -0.04 s [-0.28, -0.00] | -0.24 s [-0.31, -0.10] |
| o3g_b0_2b_fup | o3g_r6_2b_fup | 60 | -0.65 s [-1.10, -0.45] | -0.83 s [-1.01, -0.47] |
| o3g_nr_2b_fup | o3g_r6_2b_fup | 60 | -0.36 s [-0.78, -0.18] | -0.57 s [-0.84, -0.33] |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 462 | -4.74 s [-6.49, -3.43] | -6.85 s [-8.84, -5.85] |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 192 | -15.38 s [-17.47, -14.48] | -23.43 s [-27.42, -17.87] |
| o3g_b0_4b_rag | o3g_r1_4b_rag | 463 | +0.17 s [+0.13, +0.20] | +0.03 s [-0.02, +0.08] |
| o3g_r1_4b_rag | o3g_r2_4b_rag | 463 | -0.01 s [-0.06, +0.02] | +0.03 s [-0.03, +0.07] |
| o3g_r2_4b_rag | o3g_r3_4b_rag | 463 | -0.29 s [-0.34, -0.26] | -0.28 s [-0.33, -0.24] |
| o3g_r3_4b_rag | o3g_r4_4b_rag | 463 | +0.02 s [+0.01, +0.05] | -0.07 s [-0.11, -0.01] |
| o3g_r4_4b_rag | o3g_r5_4b_rag | 463 | -0.05 s [-0.07, -0.02] | -0.10 s [-0.13, -0.07] |
| o3g_r5_4b_rag | o3g_r6_4b_rag | 463 | -0.10 s [-0.14, -0.07] | -0.10 s [-0.14, -0.08] |
| o3g_b0_4b_rag | o3g_r6_4b_rag | 463 | -0.38 s [-0.44, -0.33] | -0.62 s [-0.70, -0.54] |
| o3g_nr_4b_rag | o3g_r6_4b_rag | 463 | -0.24 s [-0.32, -0.17] | -0.80 s [-0.87, -0.70] |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | 192 | +0.28 s [+0.18, +0.34] | +0.44 s [+0.35, +0.55] |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | 192 | -1.52 s [-1.61, -1.42] | -1.88 s [-2.13, -1.67] |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | 192 | -0.98 s [-1.20, -0.91] | -1.08 s [-1.52, -0.82] |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | 192 | -0.01 s [-0.01, -0.00] | -0.65 s [-0.83, -0.51] |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | 192 | -0.00 s [-0.01, +0.00] | +0.04 s [+0.03, +0.05] |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | 192 | +0.01 s [+0.00, +0.01] | +0.18 s [+0.14, +0.23] |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | 192 | -2.30 s [-2.60, -2.02] | -2.97 s [-3.24, -2.60] |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | 192 | -1.97 s [-2.20, -1.78] | -2.17 s [-2.44, -1.97] |
| o3g_b0_4b_fup | o3g_r1_4b_fup | 60 | +0.23 s [+0.11, +0.29] | +0.32 s [+0.24, +0.45] |
| o3g_r1_4b_fup | o3g_r2_4b_fup | 60 | +0.09 s [-0.02, +0.17] | -0.07 s [-0.17, +0.02] |
| o3g_r2_4b_fup | o3g_r3_4b_fup | 60 | -0.20 s [-0.31, -0.10] | +0.02 s [-0.03, +0.12] |
| o3g_r3_4b_fup | o3g_r4_4b_fup | 60 | -0.02 s [-0.09, +0.09] | -0.32 s [-0.45, -0.22] |
| o3g_r4_4b_fup | o3g_r5_4b_fup | 60 | -0.43 s [-1.19, -0.12] | -0.69 s [-1.45, -0.30] |
| o3g_r5_4b_fup | o3g_r6_4b_fup | 60 | -0.09 s [-0.17, -0.03] | +0.01 s [-0.08, +0.06] |
| o3g_b0_4b_fup | o3g_r6_4b_fup | 60 | -0.65 s [-1.16, -0.21] | -0.79 s [-1.40, -0.50] |
| o3g_nr_4b_fup | o3g_r6_4b_fup | 60 | -0.27 s [-0.84, +0.02] | -0.58 s [-0.98, -0.01] |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 463 | +12.16 s [+10.30, +14.02] | +13.10 s [+11.63, +14.58] |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 192 | -17.35 s [-24.07, -15.18] | -24.68 s [-29.36, -22.18] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3g_b0_2b_rag | o3g_r1_2b_rag | 0 → 39 | 0 → 39 | 0 → 0 | 0 → 0 | 165 → 74 | 68 → 45 | 6 → 15 | 0 → 0 | 2 → 2 | 0 → 0 |
| o3g_r1_2b_rag | o3g_r2_2b_rag | 39 → 30 | 39 → 30 | 0 → 0 | 0 → 0 | 74 → 71 | 45 → 42 | 15 → 14 | 0 → 0 | 2 → 2 | 0 → 0 |
| o3g_r2_2b_rag | o3g_r3_2b_rag | 30 → 8 | 30 → 4 | 0 → 0 | 0 → 4 | 71 → 70 | 42 → 42 | 14 → 17 | 0 → 0 | 2 → 4 | 0 → 0 |
| o3g_r3_2b_rag | o3g_r4_2b_rag | 8 → 6 | 4 → 4 | 0 → 1 | 4 → 1 | 70 → 66 | 42 → 30 | 17 → 36 | 0 → 0 | 4 → 23 | 0 → 0 |
| o3g_r4_2b_rag | o3g_r5_2b_rag | 6 → 6 | 4 → 4 | 1 → 1 | 1 → 1 | 66 → 66 | 30 → 30 | 36 → 45 | 0 → 0 | 23 → 32 | 0 → 0 |
| o3g_r5_2b_rag | o3g_r6_2b_rag | 6 → 9 | 4 → 4 | 1 → 5 | 1 → 0 | 66 → 34 | 30 → 21 | 45 → 34 | 0 → 0 | 32 → 26 | 0 → 0 |
| o3g_b0_2b_rag | o3g_r6_2b_rag | 0 → 9 | 0 → 4 | 0 → 5 | 0 → 0 | 165 → 34 | 68 → 21 | 6 → 34 | 0 → 0 | 2 → 26 | 0 → 0 |
| o3g_nr_2b_rag | o3g_r6_2b_rag | 7 → 9 | 4 → 4 | 2 → 5 | 1 → 0 | 42 → 34 | 25 → 21 | 15 → 34 | 0 → 0 | 1 → 26 | 0 → 0 |
| o3t_b0_2b_rag | o3g_b0_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 135 → 165 | 60 → 68 | 7 → 6 | 0 → 0 | 0 → 2 | 0 → 0 |
| o3t_final_2b_rag | o3g_r6_2b_rag | 15 → 9 | 8 → 4 | 5 → 5 | 2 → 0 | 58 → 34 | 33 → 21 | 36 → 34 | 0 → 0 | 29 → 26 | 0 → 0 |
| o3l_b0_2b_rag | o3g_b0_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 125 → 165 | 57 → 68 | 9 → 6 | 0 → 0 | 0 → 2 | 0 → 0 |
| o3l_r6_2b_rag | o3g_r6_2b_rag | 12 → 9 | 5 → 4 | 4 → 5 | 3 → 0 | 51 → 34 | 30 → 21 | 35 → 34 | 0 → 0 | 29 → 26 | 0 → 0 |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | 0 → 24 | 0 → 24 | 0 → 0 | 0 → 0 | 59 → 26 | 0 → 0 | 4 → 5 | 0 → 0 | 3 → 3 | 0 → 0 |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | 24 → 4 | 24 → 4 | 0 → 0 | 0 → 0 | 26 → 20 | 0 → 0 | 5 → 5 | 0 → 0 | 3 → 3 | 0 → 0 |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | 4 → 2 | 4 → 0 | 0 → 2 | 0 → 0 | 20 → 16 | 0 → 0 | 5 → 3 | 0 → 0 | 3 → 2 | 0 → 0 |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | 2 → 2 | 0 → 0 | 2 → 2 | 0 → 0 | 16 → 15 | 0 → 0 | 3 → 4 | 0 → 0 | 2 → 3 | 0 → 0 |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | 2 → 2 | 0 → 0 | 2 → 2 | 0 → 0 | 15 → 15 | 0 → 0 | 4 → 5 | 0 → 0 | 3 → 4 | 0 → 0 |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | 2 → 0 | 0 → 0 | 2 → 0 | 0 → 0 | 15 → 12 | 0 → 0 | 5 → 8 | 0 → 0 | 4 → 5 | 0 → 0 |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 59 → 12 | 0 → 0 | 4 → 8 | 0 → 0 | 3 → 5 | 0 → 0 |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | 6 → 0 | 5 → 0 | 0 → 0 | 1 → 0 | 22 → 12 | 0 → 0 | 9 → 8 | 0 → 0 | 5 → 5 | 0 → 0 |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 54 → 59 | 0 → 0 | 6 → 4 | 0 → 0 | 4 → 3 | 0 → 0 |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 14 → 12 | 0 → 0 | 10 → 8 | 0 → 0 | 5 → 5 | 0 → 0 |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 49 → 59 | 0 → 0 | 5 → 4 | 0 → 0 | 3 → 3 | 0 → 0 |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 15 → 12 | 0 → 0 | 8 → 8 | 0 → 0 | 4 → 5 | 0 → 0 |
| o3g_b0_2b_fup | o3g_r1_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 9 → 3 | 4 → 3 | 1 → 1 | 0 → 0 | 0 → 1 | 0 → 0 |
| o3g_r1_2b_fup | o3g_r2_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 3 → 3 | 3 → 3 | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |
| o3g_r2_2b_fup | o3g_r3_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 3 → 3 | 3 → 3 | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |
| o3g_r3_2b_fup | o3g_r4_2b_fup | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 3 → 1 | 3 → 1 | 1 → 2 | 0 → 0 | 1 → 2 | 0 → 0 |
| o3g_r4_2b_fup | o3g_r5_2b_fup | 1 → 2 | 0 → 0 | 1 → 2 | 0 → 0 | 1 → 1 | 1 → 1 | 2 → 1 | 0 → 0 | 2 → 1 | 0 → 0 |
| o3g_r5_2b_fup | o3g_r6_2b_fup | 2 → 0 | 0 → 0 | 2 → 0 | 0 → 0 | 1 → 0 | 1 → 0 | 1 → 2 | 0 → 0 | 1 → 2 | 0 → 0 |
| o3g_b0_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 9 → 0 | 4 → 0 | 1 → 2 | 0 → 0 | 0 → 2 | 0 → 0 |
| o3g_nr_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 3 → 2 | 0 → 0 | 3 → 2 | 0 → 0 |
| o3t_b0_2b_fup | o3g_b0_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 6 → 9 | 3 → 4 | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 2 | 0 → 0 | 3 → 2 | 0 → 0 |
| o3l_b0_2b_fup | o3g_b0_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 8 → 9 | 4 → 4 | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_r6_2b_fup | o3g_r6_2b_fup | 2 → 0 | 0 → 0 | 2 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 3 → 2 | 0 → 0 | 1 → 2 | 0 → 0 |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 0 → 12 | 0 → 5 | 0 → 4 | 0 → 3 | 118 → 51 | 72 → 30 | 9 → 35 | 0 → 0 | 2 → 29 | 0 → 0 |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 14 → 15 | 0 → 0 | 1 → 8 | 0 → 0 | 0 → 4 | 0 → 0 |
| o3g_b0_4b_rag | o3g_r1_4b_rag | 0 → 3 | 0 → 3 | 0 → 0 | 0 → 0 | 18 → 21 | 7 → 8 | 63 → 61 | 0 → 0 | 26 → 33 | 0 → 0 |
| o3g_r1_4b_rag | o3g_r2_4b_rag | 3 → 2 | 3 → 2 | 0 → 0 | 0 → 0 | 21 → 19 | 8 → 8 | 61 → 59 | 0 → 0 | 33 → 32 | 0 → 0 |
| o3g_r2_4b_rag | o3g_r3_4b_rag | 2 → 1 | 2 → 0 | 0 → 1 | 0 → 0 | 19 → 20 | 8 → 7 | 59 → 51 | 0 → 0 | 32 → 32 | 0 → 0 |
| o3g_r3_4b_rag | o3g_r4_4b_rag | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 | 20 → 8 | 7 → 3 | 51 → 68 | 0 → 0 | 32 → 49 | 0 → 0 |
| o3g_r4_4b_rag | o3g_r5_4b_rag | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 | 8 → 8 | 3 → 3 | 68 → 69 | 0 → 0 | 49 → 50 | 0 → 0 |
| o3g_r5_4b_rag | o3g_r6_4b_rag | 1 → 2 | 0 → 0 | 1 → 2 | 0 → 0 | 8 → 9 | 3 → 3 | 69 → 68 | 0 → 0 | 50 → 56 | 0 → 0 |
| o3g_b0_4b_rag | o3g_r6_4b_rag | 0 → 2 | 0 → 0 | 0 → 2 | 0 → 0 | 18 → 9 | 7 → 3 | 63 → 68 | 0 → 0 | 26 → 56 | 0 → 0 |
| o3g_nr_4b_rag | o3g_r6_4b_rag | 1 → 2 | 0 → 0 | 1 → 2 | 0 → 0 | 17 → 9 | 8 → 3 | 57 → 68 | 0 → 0 | 36 → 56 | 0 → 0 |
| o3t_b0_4b_rag | o3g_b0_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 20 → 18 | 9 → 7 | 61 → 63 | 0 → 0 | 33 → 26 | 0 → 0 |
| o3t_final_4b_rag | o3g_r6_4b_rag | 5 → 2 | 3 → 0 | 2 → 2 | 0 → 0 | 13 → 9 | 3 → 3 | 76 → 68 | 0 → 0 | 59 → 56 | 0 → 0 |
| o3l_b0_4b_rag | o3g_b0_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 23 → 18 | 8 → 7 | 62 → 63 | 0 → 0 | 35 → 26 | 0 → 0 |
| o3l_r6_4b_rag | o3g_r6_4b_rag | 1 → 2 | 0 → 0 | 1 → 2 | 0 → 0 | 5 → 9 | 1 → 3 | 75 → 68 | 0 → 0 | 52 → 56 | 0 → 0 |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | 0 → 5 | 0 → 5 | 0 → 0 | 0 → 0 | 19 → 20 | 0 → 0 | 22 → 13 | 0 → 0 | 12 → 6 | 0 → 0 |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | 5 → 9 | 5 → 9 | 0 → 0 | 0 → 0 | 20 → 18 | 0 → 0 | 13 → 23 | 0 → 0 | 6 → 13 | 0 → 0 |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | 9 → 10 | 9 → 5 | 0 → 0 | 0 → 5 | 18 → 0 | 0 → 0 | 23 → 18 | 0 → 0 | 13 → 13 | 0 → 0 |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | 10 → 10 | 5 → 5 | 0 → 0 | 5 → 5 | 0 → 0 | 0 → 0 | 18 → 19 | 0 → 0 | 13 → 14 | 0 → 0 |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | 10 → 10 | 5 → 5 | 0 → 0 | 5 → 5 | 0 → 0 | 0 → 0 | 19 → 20 | 0 → 0 | 14 → 15 | 0 → 0 |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | 10 → 11 | 5 → 6 | 0 → 0 | 5 → 5 | 0 → 0 | 0 → 0 | 20 → 17 | 0 → 0 | 15 → 14 | 0 → 0 |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | 0 → 11 | 0 → 6 | 0 → 0 | 0 → 5 | 19 → 0 | 0 → 0 | 22 → 17 | 0 → 0 | 12 → 14 | 0 → 0 |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | 2 → 11 | 1 → 6 | 1 → 0 | 0 → 5 | 18 → 0 | 0 → 0 | 18 → 17 | 0 → 0 | 9 → 14 | 0 → 0 |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 21 → 19 | 0 → 0 | 22 → 22 | 0 → 0 | 12 → 12 | 0 → 0 |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | 12 → 11 | 7 → 6 | 1 → 0 | 4 → 5 | 0 → 0 | 0 → 0 | 18 → 17 | 0 → 0 | 14 → 14 | 0 → 0 |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 20 → 19 | 0 → 0 | 21 → 22 | 0 → 0 | 15 → 12 | 0 → 0 |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | 11 → 11 | 7 → 6 | 0 → 0 | 4 → 5 | 1 → 0 | 0 → 0 | 19 → 17 | 0 → 0 | 16 → 14 | 0 → 0 |
| o3g_b0_4b_fup | o3g_r1_4b_fup | 0 → 2 | 0 → 2 | 0 → 0 | 0 → 0 | 2 → 2 | 1 → 2 | 2 → 2 | 0 → 0 | 2 → 2 | 0 → 0 |
| o3g_r1_4b_fup | o3g_r2_4b_fup | 2 → 2 | 2 → 2 | 0 → 0 | 0 → 0 | 2 → 2 | 2 → 2 | 2 → 2 | 0 → 0 | 2 → 2 | 0 → 0 |
| o3g_r2_4b_fup | o3g_r3_4b_fup | 2 → 1 | 2 → 0 | 0 → 0 | 0 → 1 | 2 → 2 | 2 → 2 | 2 → 2 | 0 → 0 | 2 → 2 | 0 → 0 |
| o3g_r3_4b_fup | o3g_r4_4b_fup | 1 → 1 | 0 → 0 | 0 → 0 | 1 → 1 | 2 → 2 | 2 → 2 | 2 → 2 | 0 → 0 | 2 → 2 | 0 → 0 |
| o3g_r4_4b_fup | o3g_r5_4b_fup | 1 → 0 | 0 → 0 | 0 → 0 | 1 → 0 | 2 → 0 | 2 → 0 | 2 → 0 | 0 → 0 | 2 → 0 | 0 → 0 |
| o3g_r5_4b_fup | o3g_r6_4b_fup | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 4 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_b0_4b_fup | o3g_r6_4b_fup | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 1 | 2 → 0 | 1 → 0 | 2 → 4 | 0 → 0 | 2 → 0 | 0 → 0 |
| o3g_nr_4b_fup | o3g_r6_4b_fup | 2 → 1 | 0 → 0 | 0 → 0 | 2 → 1 | 2 → 0 | 2 → 0 | 6 → 4 | 0 → 0 | 2 → 0 | 0 → 0 |
| o3t_b0_4b_fup | o3g_b0_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 1 → 1 | 3 → 2 | 0 → 0 | 3 → 2 | 0 → 0 |
| o3t_final_4b_fup | o3g_r6_4b_fup | 1 → 1 | 0 → 0 | 1 → 0 | 0 → 1 | 3 → 0 | 2 → 0 | 3 → 4 | 0 → 0 | 2 → 0 | 0 → 0 |
| o3l_b0_4b_fup | o3g_b0_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 1 → 1 | 4 → 2 | 0 → 0 | 4 → 2 | 0 → 0 |
| o3l_r6_4b_fup | o3g_r6_4b_fup | 0 → 1 | 0 → 0 | 0 → 0 | 0 → 1 | 1 → 0 | 1 → 0 | 4 → 4 | 0 → 0 | 3 → 0 | 0 → 0 |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 21 → 5 | 5 → 1 | 70 → 75 | 0 → 0 | 40 → 52 | 0 → 0 |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 0 → 11 | 0 → 7 | 0 → 0 | 0 → 4 | 19 → 1 | 0 → 0 | 20 → 19 | 0 → 0 | 17 → 16 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3g_b0_2b_rag | o3g_r1_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r1_2b_rag | o3g_r2_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r2_2b_rag | o3g_r3_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r3_2b_rag | o3g_r4_2b_rag | 0 → 25 | 0 → 20 | 0 → 54 | 0 → 15 |
| o3g_r4_2b_rag | o3g_r5_2b_rag | 25 → 25 | 20 → 20 | 54 → 54 | 15 → 15 |
| o3g_r5_2b_rag | o3g_r6_2b_rag | 25 → 25 | 20 → 20 | 54 → 27 | 15 → 5 |
| o3g_b0_2b_rag | o3g_r6_2b_rag | 0 → 25 | 0 → 20 | 0 → 27 | 0 → 5 |
| o3g_nr_2b_rag | o3g_r6_2b_rag | 0 → 25 | 0 → 20 | 32 → 27 | 6 → 5 |
| o3t_b0_2b_rag | o3g_b0_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_rag | o3g_r6_2b_rag | 25 → 25 | 20 → 20 | 45 → 27 | 8 → 5 |
| o3l_b0_2b_rag | o3g_b0_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_r6_2b_rag | o3g_r6_2b_rag | 25 → 25 | 20 → 20 | 38 → 27 | 6 → 5 |
| o3g_b0_2b_v12 | o3g_r1_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r1_2b_v12 | o3g_r2_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r2_2b_v12 | o3g_r3_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r3_2b_v12 | o3g_r4_2b_v12 | 0 → 0 | 0 → 1 | 0 → 8 | 0 → 2 |
| o3g_r4_2b_v12 | o3g_r5_2b_v12 | 0 → 0 | 1 → 1 | 8 → 8 | 2 → 2 |
| o3g_r5_2b_v12 | o3g_r6_2b_v12 | 0 → 0 | 1 → 1 | 8 → 7 | 2 → 2 |
| o3g_b0_2b_v12 | o3g_r6_2b_v12 | 0 → 0 | 0 → 1 | 0 → 7 | 0 → 2 |
| o3g_nr_2b_v12 | o3g_r6_2b_v12 | 0 → 0 | 0 → 1 | 8 → 7 | 3 → 2 |
| o3t_b0_2b_v12 | o3g_b0_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_v12 | o3g_r6_2b_v12 | 0 → 0 | 1 → 1 | 7 → 7 | 1 → 2 |
| o3l_b0_2b_v12 | o3g_b0_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_r6_2b_v12 | o3g_r6_2b_v12 | 0 → 0 | 1 → 1 | 7 → 7 | 1 → 2 |
| o3g_b0_2b_fup | o3g_r1_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r1_2b_fup | o3g_r2_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r2_2b_fup | o3g_r3_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r3_2b_fup | o3g_r4_2b_fup | 0 → 0 | 0 → 1 | 0 → 3 | 0 → 2 |
| o3g_r4_2b_fup | o3g_r5_2b_fup | 0 → 0 | 1 → 0 | 3 → 3 | 2 → 2 |
| o3g_r5_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 3 → 0 | 2 → 0 |
| o3g_b0_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_nr_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_b0_2b_fup | o3g_b0_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_b0_2b_fup | o3g_b0_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_r6_2b_fup | o3g_r6_2b_fup | 0 → 0 | 0 → 0 | 2 → 0 | 2 → 0 |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 0 → 25 | 0 → 20 | 0 → 38 | 0 → 6 |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 0 → 0 | 0 → 1 | 0 → 7 | 0 → 1 |
| o3g_b0_4b_rag | o3g_r1_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r1_4b_rag | o3g_r2_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r2_4b_rag | o3g_r3_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r3_4b_rag | o3g_r4_4b_rag | 0 → 25 | 0 → 20 | 0 → 7 | 0 → 4 |
| o3g_r4_4b_rag | o3g_r5_4b_rag | 25 → 25 | 20 → 20 | 7 → 7 | 4 → 4 |
| o3g_r5_4b_rag | o3g_r6_4b_rag | 25 → 25 | 20 → 20 | 7 → 7 | 4 → 3 |
| o3g_b0_4b_rag | o3g_r6_4b_rag | 0 → 25 | 0 → 20 | 0 → 7 | 0 → 3 |
| o3g_nr_4b_rag | o3g_r6_4b_rag | 0 → 25 | 0 → 20 | 6 → 7 | 2 → 3 |
| o3t_b0_4b_rag | o3g_b0_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_4b_rag | o3g_r6_4b_rag | 25 → 25 | 20 → 20 | 10 → 7 | 3 → 3 |
| o3l_b0_4b_rag | o3g_b0_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_r6_4b_rag | o3g_r6_4b_rag | 25 → 25 | 20 → 20 | 6 → 7 | 2 → 3 |
| o3g_b0_4b_v12 | o3g_r1_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r1_4b_v12 | o3g_r2_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r2_4b_v12 | o3g_r3_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r3_4b_v12 | o3g_r4_4b_v12 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 |
| o3g_r4_4b_v12 | o3g_r5_4b_v12 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 |
| o3g_r5_4b_v12 | o3g_r6_4b_v12 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 |
| o3g_b0_4b_v12 | o3g_r6_4b_v12 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 |
| o3g_nr_4b_v12 | o3g_r6_4b_v12 | 0 → 0 | 0 → 1 | 1 → 0 | 1 → 0 |
| o3t_b0_4b_v12 | o3g_b0_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_4b_v12 | o3g_r6_4b_v12 | 0 → 0 | 1 → 1 | 1 → 0 | 1 → 0 |
| o3l_b0_4b_v12 | o3g_b0_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_r6_4b_v12 | o3g_r6_4b_v12 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 |
| o3g_b0_4b_fup | o3g_r1_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r1_4b_fup | o3g_r2_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r2_4b_fup | o3g_r3_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_r3_4b_fup | o3g_r4_4b_fup | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 |
| o3g_r4_4b_fup | o3g_r5_4b_fup | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 |
| o3g_r5_4b_fup | o3g_r6_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_b0_4b_fup | o3g_r6_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3g_nr_4b_fup | o3g_r6_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_b0_4b_fup | o3g_b0_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_4b_fup | o3g_r6_4b_fup | 0 → 0 | 0 → 0 | 2 → 0 | 0 → 0 |
| o3l_b0_4b_fup | o3g_b0_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3l_r6_4b_fup | o3g_r6_4b_fup | 0 → 0 | 0 → 0 | 1 → 0 | 0 → 0 |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 0 → 25 | 0 → 20 | 0 → 6 | 0 → 2 |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3g_b0_2b_rag | o3g_r1_2b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3g_r1_2b_rag | o3g_r2_2b_rag | 0/0 (0.0%) → 31/356 (8.7%) | 0 → 0 | 0 → 0 |
| o3g_r2_2b_rag | o3g_r3_2b_rag | 31/356 (8.7%) → 33/382 (8.6%) | 0 → 0 | 0 → 0 |
| o3g_r3_2b_rag | o3g_r4_2b_rag | 33/382 (8.6%) → 35/382 (9.2%) | 0 → 0 | 0 → 0 |
| o3g_r4_2b_rag | o3g_r5_2b_rag | 35/382 (9.2%) → 26/382 (6.8%) | 0 → 10 | 0 → 2 |
| o3g_r5_2b_rag | o3g_r6_2b_rag | 26/382 (6.8%) → 14/382 (3.7%) | 10 → 6 | 2 → 0 |
| o3g_b0_2b_rag | o3g_r6_2b_rag | 0/0 (0.0%) → 14/382 (3.7%) | 0 → 6 | 0 → 0 |
| o3g_nr_2b_rag | o3g_r6_2b_rag | 0/0 (0.0%) → 14/382 (3.7%) | 0 → 6 | 0 → 0 |
| o3t_b0_2b_rag | o3g_b0_2b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_2b_rag | o3g_r6_2b_rag | 11/378 (2.9%) → 14/382 (3.7%) | 6 → 6 | 1 → 0 |
| o3l_b0_2b_rag | o3g_b0_2b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_r6_2b_rag | o3g_r6_2b_rag | 17/380 (4.5%) → 14/382 (3.7%) | 7 → 6 | 1 → 0 |
| o3g_b0_2b_fup | o3g_r1_2b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3g_r1_2b_fup | o3g_r2_2b_fup | 0/0 (0.0%) → 9/60 (15.0%) | 0 → 0 | 0 → 0 |
| o3g_r2_2b_fup | o3g_r3_2b_fup | 9/60 (15.0%) → 9/60 (15.0%) | 0 → 0 | 0 → 0 |
| o3g_r3_2b_fup | o3g_r4_2b_fup | 9/60 (15.0%) → 9/60 (15.0%) | 0 → 0 | 0 → 0 |
| o3g_r4_2b_fup | o3g_r5_2b_fup | 9/60 (15.0%) → 1/40 (2.5%) | 0 → 0 | 0 → 1 |
| o3g_r5_2b_fup | o3g_r6_2b_fup | 1/40 (2.5%) → 0/40 (0.0%) | 0 → 0 | 1 → 0 |
| o3g_b0_2b_fup | o3g_r6_2b_fup | 0/0 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3g_nr_2b_fup | o3g_r6_2b_fup | 0/0 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_b0_2b_fup | o3g_b0_2b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_2b_fup | o3g_r6_2b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_b0_2b_fup | o3g_b0_2b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_r6_2b_fup | o3g_r6_2b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 0/0 (0.0%) → 17/380 (4.5%) | 0 → 7 | 0 → 1 |
| o3g_b0_4b_rag | o3g_r1_4b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3g_r1_4b_rag | o3g_r2_4b_rag | 0/0 (0.0%) → 25/385 (6.5%) | 0 → 0 | 0 → 0 |
| o3g_r2_4b_rag | o3g_r3_4b_rag | 25/385 (6.5%) → 25/386 (6.5%) | 0 → 0 | 0 → 0 |
| o3g_r3_4b_rag | o3g_r4_4b_rag | 25/386 (6.5%) → 23/386 (6.0%) | 0 → 0 | 0 → 0 |
| o3g_r4_4b_rag | o3g_r5_4b_rag | 23/386 (6.0%) → 22/386 (5.7%) | 0 → 1 | 0 → 0 |
| o3g_r5_4b_rag | o3g_r6_4b_rag | 22/386 (5.7%) → 19/386 (4.9%) | 1 → 2 | 0 → 0 |
| o3g_b0_4b_rag | o3g_r6_4b_rag | 0/0 (0.0%) → 19/386 (4.9%) | 0 → 2 | 0 → 0 |
| o3g_nr_4b_rag | o3g_r6_4b_rag | 0/0 (0.0%) → 19/386 (4.9%) | 0 → 2 | 0 → 0 |
| o3t_b0_4b_rag | o3g_b0_4b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_4b_rag | o3g_r6_4b_rag | 19/384 (4.9%) → 19/386 (4.9%) | 2 → 2 | 0 → 0 |
| o3l_b0_4b_rag | o3g_b0_4b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_r6_4b_rag | o3g_r6_4b_rag | 25/386 (6.5%) → 19/386 (4.9%) | 5 → 2 | 0 → 0 |
| o3g_b0_4b_fup | o3g_r1_4b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3g_r1_4b_fup | o3g_r2_4b_fup | 0/0 (0.0%) → 14/58 (24.1%) | 0 → 0 | 0 → 0 |
| o3g_r2_4b_fup | o3g_r3_4b_fup | 14/58 (24.1%) → 14/60 (23.3%) | 0 → 0 | 0 → 0 |
| o3g_r3_4b_fup | o3g_r4_4b_fup | 14/60 (23.3%) → 14/60 (23.3%) | 0 → 0 | 0 → 0 |
| o3g_r4_4b_fup | o3g_r5_4b_fup | 14/60 (23.3%) → 1/40 (2.5%) | 0 → 0 | 0 → 0 |
| o3g_r5_4b_fup | o3g_r6_4b_fup | 1/40 (2.5%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3g_b0_4b_fup | o3g_r6_4b_fup | 0/0 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3g_nr_4b_fup | o3g_r6_4b_fup | 0/0 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_b0_4b_fup | o3g_b0_4b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_4b_fup | o3g_r6_4b_fup | 1/40 (2.5%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_b0_4b_fup | o3g_b0_4b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_r6_4b_fup | o3g_r6_4b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 0/0 (0.0%) → 25/386 (6.5%) | 0 → 5 | 0 → 0 |
