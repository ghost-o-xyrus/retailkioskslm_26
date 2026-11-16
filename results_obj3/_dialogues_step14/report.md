# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3t_b0_2b_dlg | Qwen3.5-2B | 60 | 97% | 0.41 / 1 | 34% | 87% | 83% | 26% | 4.00 | 8.9 s | 25.6 s |
| o3t_b0_4b_dlg | Qwen3.5-4B | 60 | 85% | 0.96 / 3 | 84% | 63% | 53% | 36% | 3.58 | 7.8 s | 59.5 s |
| o3t_final_2b_dlg | Qwen3.5-2B | 60 | 100% | 0.80 / 2 | 100% | 97% | 97% | 56% | 1.00 | 1.4 s | 9.7 s |
| o3t_final_4b_dlg | Qwen3.5-4B | 60 | 100% | 0.80 / 2 | 100% | 97% | 97% | 56% | 1.00 | 3.2 s | 17.6 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o3t_b0_4b_dlg | o3t_final_4b_dlg | 60 | +15.0 [+6.7, +25.0] | +34.1 [+20.8, +47.3] (n=51) |
| o3t_b0_2b_dlg | o3t_final_2b_dlg | 60 | +3.3 [+0.0, +8.3] | +10.6 [+1.6, +20.0] (n=58) |
