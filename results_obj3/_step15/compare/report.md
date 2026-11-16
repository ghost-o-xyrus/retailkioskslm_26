# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3l_r5_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | all checked | 423 | 69.5% | 68.8% | -0.7 [-4.0, +2.6] | 26 / 23 | 0.775 | ±1.3 | **tie** |
| o3l_r5_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 78.9% | 76.8% | -2.1 [-5.3, +1.1] | 14 / 8 | 0.286 | ±1.6 | **tie** |
| o3l_r5_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 138 | 50.0% | 52.2% | +2.2 [-5.1, +9.4] | 12 / 15 | 0.701 | ±2.3 | **tie** |
| o3l_r5_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 53.2% | 50.0% | -3.2 [-11.3, +4.8] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o3l_r5_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | origin: fresh | 289 | 75.4% | 75.4% | +0.0 [-3.8, +3.8] | 17 / 17 | 1.000 | ±1.6 | **tie** |
| o3l_r5_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 56.7% | 54.5% | -2.2 [-8.2, +3.0] | 9 / 6 | 0.607 | ±2.3 | **tie** |
| o3l_b0_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | all checked | 423 | 53.0% | 68.8% | +15.8 [+10.9, +20.8] | 29 / 96 | 0.000 | ±1.3 | **better** |
| o3l_b0_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 60.4% | 76.8% | +16.5 [+10.5, +22.1] | 16 / 63 | 0.000 | ±1.6 | **better** |
| o3l_b0_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 138 | 37.7% | 52.2% | +14.5 [+5.8, +23.9] | 13 / 33 | 0.005 | ±2.3 | **better** |
| o3l_b0_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 56.5% | 50.0% | -6.5 [-16.1, +3.2] | 7 / 3 | 0.344 | ±3.4 | **tie** |
| o3l_b0_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | origin: fresh | 289 | 56.7% | 75.4% | +18.7 [+12.8, +24.6] | 16 / 70 | 0.000 | ±1.6 | **better** |
| o3l_b0_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 44.8% | 54.5% | +9.7 [+0.7, +18.7] | 13 / 26 | 0.053 | ±2.3 | **better** |
| o3t_b0_2b_rag | o3l_b0_2b_rag | Qwen3.5-2B | all checked | 424 | 51.9% | 53.1% | +1.2 [-1.2, +3.5] | 11 / 16 | 0.442 | ±1.3 | **tie** |
| o3t_b0_2b_rag | o3l_b0_2b_rag | Qwen3.5-2B | answerable | 285 | 61.1% | 60.4% | -0.7 [-3.2, +1.8] | 7 / 5 | 0.774 | ±1.6 | **tie** |
| o3t_b0_2b_rag | o3l_b0_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 139 | 33.1% | 38.1% | +5.0 [-0.7, +10.8] | 4 / 11 | 0.118 | ±2.3 | **tie** |
| o3t_b0_2b_rag | o3l_b0_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 56.5% | +6.5 [+0.0, +14.5] | 1 / 5 | 0.219 | ±3.4 | **tie** |
| o3t_b0_2b_rag | o3l_b0_2b_rag | Qwen3.5-2B | origin: fresh | 290 | 56.2% | 56.9% | +0.7 [-1.7, +3.1] | 6 / 8 | 0.791 | ±1.6 | **tie** |
| o3t_b0_2b_rag | o3l_b0_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 42.5% | 44.8% | +2.2 [-3.0, +7.5] | 5 / 8 | 0.581 | ±2.3 | **tie** |
| o3t_final_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | all checked | 423 | 69.5% | 68.8% | -0.7 [-2.8, +1.4] | 12 / 9 | 0.664 | ±1.3 | **tie** |
| o3t_final_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | answerable | 285 | 77.2% | 76.8% | -0.4 [-2.8, +2.1] | 7 / 6 | 1.000 | ±1.6 | **tie** |
| o3t_final_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 138 | 53.6% | 52.2% | -1.4 [-5.8, +2.2] | 5 / 3 | 0.727 | ±2.3 | **tie** |
| o3t_final_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | language: hinglish | 62 | 50.0% | 50.0% | +0.0 [-4.8, +4.8] | 1 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_final_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | origin: fresh | 289 | 75.8% | 75.4% | -0.3 [-3.1, +2.4] | 9 / 8 | 1.000 | ±1.6 | **tie** |
| o3t_final_2b_rag | o3l_r6_2b_rag | Qwen3.5-2B | origin: held-out | 134 | 56.0% | 54.5% | -1.5 [-4.5, +1.5] | 3 / 1 | 0.625 | ±2.3 | **tie** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases | 192 | 64.1% | 76.6% | +12.5 [+4.7, +20.3] | 19 / 43 | 0.003 | ±0.0 | **better** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 45.9% | 81.1% | +35.1 [+16.2, +54.1] | 2 / 15 | 0.002 | ±0.0 | **better** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 76.9% | 73.5% | -3.4 [-11.1, +4.3] | 13 / 9 | 0.523 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 44.0% | 81.3% | +37.3 [+22.7, +50.7] | 6 / 34 | 0.000 | ±0.0 | **better** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 48.9% | 83.0% | +34.0 [+14.9, +53.2] | 5 / 21 | 0.002 | ±0.0 | **better** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 57.1% | 64.3% | +7.1 [-21.4, +35.7] | 2 / 3 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 47.2% | 80.6% | +33.3 [+13.9, +52.8] | 2 / 14 | 0.004 | ±0.0 | **better** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 55.6% | 66.7% | +11.1 [-22.2, +44.4] | 1 / 2 | 1.000 | ±0.0 | **(small)** |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 78.1% | 69.9% | -8.2 [-17.8, +0.0] | 9 / 3 | 0.146 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | tool cases | 192 | 62.5% | 64.1% | +1.6 [-1.6, +5.2] | 4 / 7 | 0.549 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 45.9% | 45.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 75.2% | 76.9% | +1.7 [-3.4, +6.8] | 3 / 5 | 0.727 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 42.7% | 44.0% | +1.3 [-2.7, +5.3] | 1 / 2 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 92.3% | 100.0% | +7.7 [+0.0, +23.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 46.8% | 48.9% | +2.1 [-4.3, +8.5] | 1 / 2 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 50.0% | 57.1% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 47.2% | 47.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 55.6% | -11.1 [-33.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 76.7% | 78.1% | +1.4 [-4.1, +8.2] | 2 / 3 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases | 192 | 77.6% | 76.6% | -1.0 [-2.6, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | language: hinglish | 37 | 83.8% | 81.1% | -2.7 [-8.1, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | origin: fresh | 117 | 74.4% | 73.5% | -0.9 [-2.6, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | origin: held-out | 75 | 82.7% | 81.3% | -1.3 [-4.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: discovery | 47 | 83.0% | 83.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 36 | 83.3% | 80.6% | -2.8 [-8.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: refusal | 9 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 73 | 71.2% | 69.9% | -1.4 [-4.1, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3l_b0_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | all checked | 60 | 75.0% | 86.7% | +11.7 [+1.7, +21.7] | 2 / 9 | 0.065 | ±3.4 | **better** |
| o3l_b0_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | answerable | 60 | 75.0% | 86.7% | +11.7 [+1.7, +21.7] | 2 / 9 | 0.065 | ±3.4 | **better** |
| o3l_b0_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 61.5% | 80.8% | +19.2 [+3.8, +34.6] | 0 / 5 | 0.062 | ±5.2 | **better** |
| o3l_b0_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 80.0% | 90.0% | +10.0 [-20.0, +40.0] | 1 / 2 | 1.000 | ±8.4 | **tie** |
| o3l_b0_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 80.0% | 96.7% | +16.7 [+3.3, +30.0] | 0 / 5 | 0.062 | ±4.9 | **better** |
| o3l_b0_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_b0_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 30.0% | 40.0% | +10.0 [-20.0, +40.0] | 1 / 2 | 1.000 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3l_b0_2b_fup | Qwen3.5-2B | all checked | 60 | 80.0% | 75.0% | -5.0 [-11.7, +1.7] | 4 / 1 | 0.375 | ±3.4 | **tie** |
| o3t_b0_2b_fup | o3l_b0_2b_fup | Qwen3.5-2B | answerable | 60 | 80.0% | 75.0% | -5.0 [-11.7, +1.7] | 4 / 1 | 0.375 | ±3.4 | **tie** |
| o3t_b0_2b_fup | o3l_b0_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 65.4% | 61.5% | -3.8 [-11.5, +0.0] | 1 / 0 | 1.000 | ±5.2 | **tie** |
| o3t_b0_2b_fup | o3l_b0_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 100.0% | 80.0% | -20.0 [-50.0, +0.0] | 2 / 0 | 0.500 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3l_b0_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3t_b0_2b_fup | o3l_b0_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_2b_fup | o3l_b0_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 40.0% | 30.0% | -10.0 [-40.0, +20.0] | 2 / 1 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | all checked | 60 | 90.0% | 86.7% | -3.3 [-8.3, +0.0] | 2 / 0 | 0.500 | ±3.4 | **tie** |
| o3t_final_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | answerable | 60 | 90.0% | 86.7% | -3.3 [-8.3, +0.0] | 2 / 0 | 0.500 | ±3.4 | **tie** |
| o3t_final_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | language: hinglish | 26 | 80.8% | 80.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3t_final_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 100.0% | 90.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 96.7% | 96.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3t_final_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_2b_fup | o3l_r6_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 50.0% | 40.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
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
| o3l_r5_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 82.1% | 82.3% | +0.2 [-1.9, +2.1] | 9 / 10 | 1.000 | ±1.3 | **tie** |
| o3l_r5_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 83.9% | 83.9% | +0.0 [-1.8, +1.8] | 3 / 3 | 1.000 | ±1.6 | **tie** |
| o3l_r5_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 78.4% | 79.1% | +0.7 [-4.3, +5.8] | 6 / 7 | 1.000 | ±2.3 | **tie** |
| o3l_r5_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 53.2% | 50.0% | -3.2 [-11.3, +4.8] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o3l_r5_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 87.9% | 88.6% | +0.7 [-1.7, +3.1] | 6 / 8 | 0.791 | ±1.6 | **tie** |
| o3l_r5_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 69.4% | 68.7% | -0.7 [-3.7, +2.2] | 3 / 2 | 1.000 | ±2.3 | **tie** |
| o3l_b0_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 79.7% | 82.3% | +2.6 [+0.0, +5.2] | 10 / 21 | 0.071 | ±1.3 | **tie** |
| o3l_b0_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 83.5% | 83.9% | +0.4 [-1.8, +2.5] | 5 / 6 | 1.000 | ±1.6 | **tie** |
| o3l_b0_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 71.9% | 79.1% | +7.2 [+0.7, +13.7] | 5 / 15 | 0.041 | ±2.3 | **better** |
| o3l_b0_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 50.0% | 50.0% | +0.0 [-9.7, +8.1] | 4 / 4 | 1.000 | ±3.4 | **tie** |
| o3l_b0_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 84.5% | 88.6% | +4.1 [+1.4, +7.2] | 4 / 16 | 0.012 | ±1.6 | **better** |
| o3l_b0_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 69.4% | 68.7% | -0.7 [-6.0, +4.5] | 6 / 5 | 1.000 | ±2.3 | **tie** |
| o3t_b0_4b_rag | o3l_b0_4b_rag | Qwen3.5-4B | all checked | 424 | 78.3% | 79.7% | +1.4 [-1.4, +4.2] | 16 / 22 | 0.418 | ±1.3 | **tie** |
| o3t_b0_4b_rag | o3l_b0_4b_rag | Qwen3.5-4B | answerable | 285 | 80.0% | 83.5% | +3.5 [+0.4, +6.7] | 6 / 16 | 0.052 | ±1.6 | **better** |
| o3t_b0_4b_rag | o3l_b0_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 74.8% | 71.9% | -2.9 [-8.6, +2.9] | 10 / 6 | 0.454 | ±2.3 | **tie** |
| o3t_b0_4b_rag | o3l_b0_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 58.1% | 50.0% | -8.1 [-16.1, +0.0] | 6 / 1 | 0.125 | ±3.4 | **tie** |
| o3t_b0_4b_rag | o3l_b0_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 80.3% | 84.5% | +4.1 [+0.7, +7.6] | 8 / 20 | 0.036 | ±1.6 | **better** |
| o3t_b0_4b_rag | o3l_b0_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 73.9% | 69.4% | -4.5 [-9.7, +0.0] | 8 / 2 | 0.109 | ±2.3 | **tie** |
| o3t_final_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | all checked | 424 | 81.4% | 82.3% | +0.9 [-1.2, +3.1] | 8 / 12 | 0.503 | ±1.3 | **tie** |
| o3t_final_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | answerable | 285 | 83.2% | 83.9% | +0.7 [-1.4, +2.8] | 4 / 6 | 0.754 | ±1.6 | **tie** |
| o3t_final_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 139 | 77.7% | 79.1% | +1.4 [-2.9, +5.8] | 4 / 6 | 0.754 | ±2.3 | **tie** |
| o3t_final_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | language: hinglish | 62 | 54.8% | 50.0% | -4.8 [-11.3, +0.0] | 3 / 0 | 0.250 | ±3.4 | **tie** |
| o3t_final_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | origin: fresh | 290 | 86.2% | 88.6% | +2.4 [-0.3, +5.2] | 5 / 12 | 0.143 | ±1.6 | **tie** |
| o3t_final_4b_rag | o3l_r6_4b_rag | Qwen3.5-4B | origin: held-out | 134 | 70.9% | 68.7% | -2.2 [-5.2, +0.0] | 3 / 0 | 0.250 | ±2.3 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 79.2% | 83.9% | +4.7 [-2.6, +12.0] | 21 / 30 | 0.262 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 78.4% | 81.1% | +2.7 [-16.2, +21.6] | 5 / 6 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 81.2% | 86.3% | +5.1 [-3.4, +12.8] | 10 / 16 | 0.327 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 76.0% | 80.0% | +4.0 [-9.3, +17.3] | 11 / 14 | 0.690 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 76.9% | 100.0% | +23.1 [+0.0, +46.2] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 76.6% | 80.9% | +4.3 [-12.8, +21.3] | 7 / 9 | 0.804 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 85.7% | 64.3% | -21.4 [-42.9, +0.0] | 3 / 0 | 0.250 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 77.8% | 80.6% | +2.8 [-13.9, +22.2] | 5 / 6 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 88.9% | 77.8% | -11.1 [-33.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 79.5% | 89.0% | +9.6 [-1.4, +20.5] | 5 / 12 | 0.143 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | tool cases | 192 | 78.1% | 79.2% | +1.0 [-2.1, +4.2] | 4 / 6 | 0.754 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 83.8% | 78.4% | -5.4 [-13.5, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 81.2% | 81.2% | +0.0 [-4.3, +4.3] | 3 / 3 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 73.3% | 76.0% | +2.7 [-2.7, +8.0] | 1 / 3 | 0.625 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 76.9% | 76.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 70.2% | 76.6% | +6.4 [+0.0, +14.9] | 0 / 3 | 0.250 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 92.9% | 85.7% | -7.1 [-21.4, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 83.3% | 77.8% | -5.6 [-13.9, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 77.8% | 88.9% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 78.1% | 79.5% | +1.4 [-2.7, +5.5] | 1 / 2 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases | 192 | 83.3% | 83.9% | +0.5 [-1.0, +2.6] | 1 / 2 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | language: hinglish | 37 | 81.1% | 81.1% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | origin: fresh | 117 | 85.5% | 86.3% | +0.9 [-1.7, +3.4] | 1 / 2 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | origin: held-out | 75 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: discovery | 47 | 80.9% | 80.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 36 | 80.6% | 80.6% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: refusal | 9 | 66.7% | 77.8% | +11.1 [+0.0, +33.3] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 73 | 89.0% | 89.0% | +0.0 [-4.1, +4.1] | 1 / 1 | 1.000 | ±0.0 | **tie** |
| o3l_b0_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | all checked | 60 | 66.7% | 90.0% | +23.3 [+8.3, +38.3] | 5 / 19 | 0.007 | ±3.4 | **better** |
| o3l_b0_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | answerable | 60 | 66.7% | 90.0% | +23.3 [+8.3, +38.3] | 5 / 19 | 0.007 | ±3.4 | **better** |
| o3l_b0_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 65.4% | 76.9% | +11.5 [-15.4, +38.5] | 5 / 8 | 0.581 | ±5.2 | **tie** |
| o3l_b0_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 50.0% | 100.0% | +50.0 [+20.0, +80.0] | 0 / 5 | 0.062 | ±8.4 | **better** |
| o3l_b0_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 53.3% | 100.0% | +46.7 [+30.0, +63.3] | 0 / 14 | 0.000 | ±4.9 | **better** |
| o3l_b0_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3l_b0_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 60.0% | -40.0 [-70.0, -10.0] | 4 / 0 | 0.125 | ±8.4 | **worse** |
| o3t_b0_4b_fup | o3l_b0_4b_fup | Qwen3.5-4B | all checked | 60 | 66.7% | 66.7% | +0.0 [-5.0, +5.0] | 1 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_b0_4b_fup | o3l_b0_4b_fup | Qwen3.5-4B | answerable | 60 | 66.7% | 66.7% | +0.0 [-5.0, +5.0] | 1 / 1 | 1.000 | ±3.4 | **tie** |
| o3t_b0_4b_fup | o3l_b0_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 61.5% | 65.4% | +3.8 [+0.0, +11.5] | 0 / 1 | 1.000 | ±5.2 | **tie** |
| o3t_b0_4b_fup | o3l_b0_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 40.0% | 50.0% | +10.0 [+0.0, +30.0] | 0 / 1 | 1.000 | ±8.4 | **tie** |
| o3t_b0_4b_fup | o3l_b0_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 56.7% | 53.3% | -3.3 [-10.0, +0.0] | 1 / 0 | 1.000 | ±4.9 | **tie** |
| o3t_b0_4b_fup | o3l_b0_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_b0_4b_fup | o3l_b0_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | all checked | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3t_final_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | answerable | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o3t_final_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | language: hinglish | 26 | 76.9% | 76.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.2 | **tie** |
| o3t_final_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3t_final_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 80.0% | 80.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3t_final_4b_fup | o3l_r6_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 60.0% | 60.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
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
| o3l_r5_2b_rag | o3l_r6_2b_rag | 2.06 → 1.85 | 541 → 437 | 94 → 96 | 4 → 5 | 0 → 0 | 95/643 → 96/535 | 30.2 s → 12.8 s |
| o3l_b0_2b_rag | o3l_r6_2b_rag | 2.45 → 1.85 | 837 → 437 | 220 → 96 | 90 → 5 | 90 → 0 | 0/778 → 96/535 | 33.2 s → 12.8 s |
| o3t_b0_2b_rag | o3l_b0_2b_rag | 2.51 → 2.45 | 846 → 837 | 214 → 220 | 98 → 90 | 98 → 90 | 0/815 → 0/778 | 7.9 s → 33.2 s (different machines: local vs kaggle-cpu; not comparable) |
| o3t_final_2b_rag | o3l_r6_2b_rag | 1.91 → 1.85 | 442 → 437 | 94 → 96 | 8 → 5 | 0 → 0 | 97/565 → 96/535 | 5.8 s → 12.8 s (different machines: local vs kaggle-cpu; not comparable) |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | 2.77 → 1.06 | 1067 → 260 | 305 → 121 | 37 → 0 | 37 → 0 | 0/392 → 144/184 | 39.4 s → 8.5 s |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | 2.78 → 2.77 | 1056 → 1067 | 296 → 305 | 42 → 37 | 42 → 37 | 0/399 → 0/392 | 10.3 s → 39.4 s (different machines: local vs kaggle-cpu; not comparable) |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | 1.06 → 1.06 | 260 → 260 | 121 → 121 | 0 → 0 | 0 → 0 | 144/183 → 144/184 | 1.6 s → 8.5 s (different machines: local vs kaggle-cpu; not comparable) |
| o3l_b0_2b_fup | o3l_r6_2b_fup | 1.88 → 1.28 | 733 → 402 | 296 → 79 | 2 → 0 | 2 → 0 | 0/55 → 20/37 | 28.4 s → 16.2 s |
| o3t_b0_2b_fup | o3l_b0_2b_fup | 1.88 → 1.88 | 743 → 733 | 312 → 296 | 1 → 2 | 1 → 2 | 0/54 → 0/55 | 6.5 s → 28.4 s (different machines: local vs kaggle-cpu; not comparable) |
| o3t_final_2b_fup | o3l_r6_2b_fup | 1.15 → 1.28 | 388 → 402 | 78 → 79 | 0 → 0 | 0 → 0 | 20/29 → 20/37 | 2.3 s → 16.2 s (different machines: local vs kaggle-cpu; not comparable) |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 2.20 → 1.85 | 495 → 437 | 216 → 96 | 52 → 5 | 52 → 0 | 0/609 → 96/535 | 17.9 s → 12.8 s |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 2.07 → 1.06 | 592 → 260 | 446 → 121 | 7 → 0 | 7 → 0 | 0/223 → 144/184 | 25.2 s → 8.5 s |
| o3l_r5_4b_rag | o3l_r6_4b_rag | 0.94 → 0.98 | 420 → 346 | 138 → 135 | 0 → 0 | 0 → 0 | 90/125 → 90/140 | 41.3 s → 28.8 s |
| o3l_b0_4b_rag | o3l_r6_4b_rag | 1.24 → 0.98 | 541 → 346 | 231 → 135 | 6 → 0 | 6 → 0 | 0/125 → 90/140 | 38.8 s → 28.8 s |
| o3t_b0_4b_rag | o3l_b0_4b_rag | 1.27 → 1.24 | 554 → 541 | 258 → 231 | 4 → 6 | 4 → 6 | 0/135 → 0/125 | 7.3 s → 38.8 s (different machines: local vs kaggle-cpu; not comparable) |
| o3t_final_4b_rag | o3l_r6_4b_rag | 1.05 → 0.98 | 375 → 346 | 130 → 135 | 3 → 0 | 0 → 0 | 93/188 → 90/140 | 5.3 s → 28.8 s (different machines: local vs kaggle-cpu; not comparable) |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | 1.78 → 0.96 | 747 → 259 | 354 → 135 | 1 → 7 | 1 → 0 | 0/153 → 155/165 | 65.0 s → 11.2 s |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | 1.88 → 1.78 | 746 → 747 | 312 → 354 | 3 → 1 | 3 → 1 | 0/174 → 0/153 | 13.3 s → 65.0 s (different machines: local vs kaggle-cpu; not comparable) |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | 0.96 → 0.96 | 257 → 259 | 133 → 135 | 7 → 7 | 0 → 0 | 154/164 → 155/165 | 3.5 s → 11.2 s (different machines: local vs kaggle-cpu; not comparable) |
| o3l_b0_4b_fup | o3l_r6_4b_fup | 1.25 → 1.03 | 507 → 375 | 210 → 69 | 1 → 0 | 1 → 0 | 0/16 → 20/22 | 45.8 s → 19.5 s |
| o3t_b0_4b_fup | o3l_b0_4b_fup | 1.30 → 1.25 | 527 → 507 | 238 → 210 | 1 → 1 | 1 → 1 | 0/19 → 0/16 | 7.6 s → 45.8 s (different machines: local vs kaggle-cpu; not comparable) |
| o3t_final_4b_fup | o3l_r6_4b_fup | 1.13 → 1.03 | 381 → 375 | 62 → 69 | 0 → 0 | 0 → 0 | 20/28 → 20/22 | 4.8 s → 19.5 s (different machines: local vs kaggle-cpu; not comparable) |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 1.29 → 0.98 | 283 → 346 | 240 → 135 | 4 → 0 | 4 → 0 | 0/140 → 90/140 | 15.9 s → 28.8 s |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 1.96 → 0.96 | 404 → 259 | 328 → 135 | 5 → 7 | 5 → 0 | 0/194 → 155/165 | 34.1 s → 11.2 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o3l_r5_2b_rag | o3l_r6_2b_rag | 462 | -15.03 s [-16.16, -14.05] | -17.67 s [-18.88, -16.23] |
| o3l_b0_2b_rag | o3l_r6_2b_rag | 462 | -20.47 s [-22.83, -19.37] | -24.56 s [-27.77, -22.79] |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | 192 | -31.63 s [-34.74, -28.52] | -36.58 s [-39.25, -33.18] |
| o3l_b0_2b_fup | o3l_r6_2b_fup | 60 | -9.57 s [-15.88, -5.82] | -9.03 s [-17.73, -6.32] |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 462 | -4.74 s [-6.49, -3.43] | -6.85 s [-8.84, -5.85] |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 192 | -15.38 s [-17.47, -14.48] | -23.43 s [-27.42, -17.87] |
| o3l_r5_4b_rag | o3l_r6_4b_rag | 463 | -0.75 s [-0.99, -0.61] | -2.15 s [-2.84, -1.68] |
| o3l_b0_4b_rag | o3l_r6_4b_rag | 463 | -5.23 s [-6.22, -4.33] | -6.06 s [-7.25, -4.51] |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | 192 | -52.49 s [-58.34, -44.31] | -66.96 s [-72.37, -55.48] |
| o3l_b0_4b_fup | o3l_r6_4b_fup | 60 | -21.39 s [-30.52, -18.23] | -28.57 s [-34.62, -22.47] |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 463 | +12.16 s [+10.30, +14.02] | +13.10 s [+11.63, +14.58] |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 192 | -17.35 s [-24.07, -15.18] | -24.68 s [-29.36, -22.18] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3l_r5_2b_rag | o3l_r6_2b_rag | 8 → 12 | 4 → 5 | 2 → 4 | 2 → 3 | 85 → 51 | 39 → 30 | 36 → 35 | 0 → 0 | 26 → 29 | 0 → 0 |
| o3l_b0_2b_rag | o3l_r6_2b_rag | 0 → 12 | 0 → 5 | 0 → 4 | 0 → 3 | 125 → 51 | 57 → 30 | 9 → 35 | 0 → 0 | 0 → 29 | 0 → 0 |
| o3t_b0_2b_rag | o3l_b0_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 135 → 125 | 60 → 57 | 7 → 9 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_rag | o3l_r6_2b_rag | 15 → 12 | 8 → 5 | 5 → 4 | 2 → 3 | 58 → 51 | 33 → 30 | 36 → 35 | 0 → 0 | 29 → 29 | 0 → 0 |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 49 → 15 | 0 → 0 | 5 → 8 | 0 → 0 | 3 → 4 | 0 → 0 |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 54 → 49 | 0 → 0 | 6 → 5 | 0 → 0 | 4 → 3 | 0 → 0 |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | 1 → 1 | 0 → 0 | 1 → 1 | 0 → 0 | 14 → 15 | 0 → 0 | 10 → 8 | 0 → 0 | 5 → 4 | 0 → 0 |
| o3l_b0_2b_fup | o3l_r6_2b_fup | 0 → 2 | 0 → 0 | 0 → 2 | 0 → 0 | 8 → 0 | 4 → 0 | 0 → 3 | 0 → 0 | 0 → 1 | 0 → 0 |
| o3t_b0_2b_fup | o3l_b0_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 6 → 8 | 3 → 4 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_fup | o3l_r6_2b_fup | 0 → 2 | 0 → 0 | 0 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 3 | 0 → 0 | 3 → 1 | 0 → 0 |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 0 → 12 | 0 → 5 | 0 → 4 | 0 → 3 | 118 → 51 | 72 → 30 | 9 → 35 | 0 → 0 | 2 → 29 | 0 → 0 |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 14 → 15 | 0 → 0 | 1 → 8 | 0 → 0 | 0 → 4 | 0 → 0 |
| o3l_r5_4b_rag | o3l_r6_4b_rag | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 2 → 5 | 0 → 1 | 73 → 75 | 0 → 0 | 49 → 52 | 0 → 0 |
| o3l_b0_4b_rag | o3l_r6_4b_rag | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 23 → 5 | 8 → 1 | 62 → 75 | 0 → 0 | 35 → 52 | 0 → 0 |
| o3t_b0_4b_rag | o3l_b0_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 20 → 23 | 9 → 8 | 61 → 62 | 0 → 0 | 33 → 35 | 0 → 0 |
| o3t_final_4b_rag | o3l_r6_4b_rag | 5 → 1 | 3 → 0 | 2 → 1 | 0 → 0 | 13 → 5 | 3 → 1 | 76 → 75 | 0 → 0 | 59 → 52 | 0 → 0 |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | 0 → 11 | 0 → 7 | 0 → 0 | 0 → 4 | 20 → 1 | 0 → 0 | 21 → 19 | 0 → 0 | 15 → 16 | 0 → 0 |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 21 → 20 | 0 → 0 | 22 → 21 | 0 → 0 | 12 → 15 | 0 → 0 |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | 12 → 11 | 7 → 7 | 1 → 0 | 4 → 4 | 0 → 1 | 0 → 0 | 18 → 19 | 0 → 0 | 14 → 16 | 0 → 0 |
| o3l_b0_4b_fup | o3l_r6_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 1 | 1 → 1 | 4 → 4 | 0 → 0 | 4 → 3 | 0 → 0 |
| o3t_b0_4b_fup | o3l_b0_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 2 → 2 | 1 → 1 | 3 → 4 | 0 → 0 | 3 → 4 | 0 → 0 |
| o3t_final_4b_fup | o3l_r6_4b_fup | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 3 → 1 | 2 → 1 | 3 → 4 | 0 → 0 | 2 → 3 | 0 → 0 |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 0 → 1 | 0 → 0 | 0 → 1 | 0 → 0 | 21 → 5 | 5 → 1 | 70 → 75 | 0 → 0 | 40 → 52 | 0 → 0 |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 0 → 11 | 0 → 7 | 0 → 0 | 0 → 4 | 19 → 1 | 0 → 0 | 20 → 19 | 0 → 0 | 17 → 16 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3l_r5_2b_rag | o3l_r6_2b_rag | 25 → 25 | 20 → 20 | 61 → 38 | 14 → 6 |
| o3l_b0_2b_rag | o3l_r6_2b_rag | 0 → 25 | 0 → 20 | 0 → 38 | 0 → 6 |
| o3t_b0_2b_rag | o3l_b0_2b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_rag | o3l_r6_2b_rag | 25 → 25 | 20 → 20 | 45 → 38 | 8 → 6 |
| o3l_b0_2b_v12 | o3l_r6_2b_v12 | 0 → 0 | 0 → 1 | 0 → 7 | 0 → 1 |
| o3t_b0_2b_v12 | o3l_b0_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_v12 | o3l_r6_2b_v12 | 0 → 0 | 1 → 1 | 7 → 7 | 1 → 1 |
| o3l_b0_2b_fup | o3l_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 2 | 0 → 2 |
| o3t_b0_2b_fup | o3l_b0_2b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_2b_fup | o3l_r6_2b_fup | 0 → 0 | 0 → 0 | 0 → 2 | 0 → 2 |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 0 → 25 | 0 → 20 | 0 → 38 | 0 → 6 |
| o3l_ref_2b_none | o3l_r6_2b_v12 | 0 → 0 | 0 → 1 | 0 → 7 | 0 → 1 |
| o3l_r5_4b_rag | o3l_r6_4b_rag | 25 → 25 | 20 → 20 | 1 → 6 | 0 → 2 |
| o3l_b0_4b_rag | o3l_r6_4b_rag | 0 → 25 | 0 → 20 | 0 → 6 | 0 → 2 |
| o3t_b0_4b_rag | o3l_b0_4b_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_4b_rag | o3l_r6_4b_rag | 25 → 25 | 20 → 20 | 10 → 6 | 3 → 2 |
| o3l_b0_4b_v12 | o3l_r6_4b_v12 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 |
| o3t_b0_4b_v12 | o3l_b0_4b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_4b_v12 | o3l_r6_4b_v12 | 0 → 0 | 1 → 1 | 1 → 0 | 1 → 0 |
| o3l_b0_4b_fup | o3l_r6_4b_fup | 0 → 0 | 0 → 0 | 0 → 1 | 0 → 0 |
| o3t_b0_4b_fup | o3l_b0_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3t_final_4b_fup | o3l_r6_4b_fup | 0 → 0 | 0 → 0 | 2 → 1 | 0 → 0 |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 0 → 25 | 0 → 20 | 0 → 6 | 0 → 2 |
| o3l_ref_4b_none | o3l_r6_4b_v12 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3l_r5_2b_rag | o3l_r6_2b_rag | 26/382 (6.8%) → 17/380 (4.5%) | 7 → 7 | 1 → 1 |
| o3l_b0_2b_rag | o3l_r6_2b_rag | 0/0 (0.0%) → 17/380 (4.5%) | 0 → 7 | 0 → 1 |
| o3t_b0_2b_rag | o3l_b0_2b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_2b_rag | o3l_r6_2b_rag | 11/378 (2.9%) → 17/380 (4.5%) | 6 → 7 | 1 → 1 |
| o3l_b0_2b_fup | o3l_r6_2b_fup | 0/0 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_b0_2b_fup | o3l_b0_2b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_2b_fup | o3l_r6_2b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_ref_2b_oracle | o3l_r6_2b_rag | 0/0 (0.0%) → 17/380 (4.5%) | 0 → 7 | 0 → 1 |
| o3l_r5_4b_rag | o3l_r6_4b_rag | 25/386 (6.5%) → 25/386 (6.5%) | 4 → 5 | 0 → 0 |
| o3l_b0_4b_rag | o3l_r6_4b_rag | 0/0 (0.0%) → 25/386 (6.5%) | 0 → 5 | 0 → 0 |
| o3t_b0_4b_rag | o3l_b0_4b_rag | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_4b_rag | o3l_r6_4b_rag | 19/384 (4.9%) → 25/386 (6.5%) | 2 → 5 | 0 → 0 |
| o3l_b0_4b_fup | o3l_r6_4b_fup | 0/0 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_b0_4b_fup | o3l_b0_4b_fup | 0/0 (0.0%) → 0/0 (0.0%) | 0 → 0 | 0 → 0 |
| o3t_final_4b_fup | o3l_r6_4b_fup | 1/40 (2.5%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3l_ref_4b_oracle | o3l_r6_4b_rag | 0/0 (0.0%) → 25/386 (6.5%) | 0 → 5 | 0 → 0 |
