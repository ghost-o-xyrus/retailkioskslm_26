# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3s6d_2b_s5h | Qwen3.5-2B | 40 | 78% | 0.90 / 2 | 71% | 62% | 45% | 21% | 4.45 | 5.9 s | 29.2 s |
| o3s6d_2b_s6 | Qwen3.5-2B | 40 | 100% | 0.90 / 2 | 88% | 81% | 78% | 29% | 1.50 | 1.4 s | 11.8 s |
| o3s6d_2b_s6m | Qwen3.5-2B | 40 | 100% | 0.93 / 2 | 75% | 79% | 78% | 24% | 2.27 | 1.4 s | 14.5 s |
| o3s6d_4b_s5h | Qwen3.5-4B | 40 | 92% | 1.11 / 2 | 97% | 49% | 43% | 26% | 3.98 | 8.6 s | 53.0 s |
| o3s6d_4b_s6 | Qwen3.5-4B | 40 | 100% | 0.97 / 2 | 98% | 78% | 72% | 34% | 1.18 | 2.9 s | 20.2 s |
| o3s6d_4b_s6m | Qwen3.5-4B | 40 | 100% | 1.18 / 2 | 98% | 78% | 75% | 40% | 2.25 | 2.9 s | 28.8 s |
| o3s6dsp_a_2b_s5h | Qwen3.5-2B | 40 | 78% | 1.19 / 3 | 65% | 65% | 48% | 10% | 4.67 | 7.2 s | 33.7 s |
| o3s6dsp_a_2b_s6 | Qwen3.5-2B | 40 | 100% | 0.90 / 2 | 88% | 81% | 78% | 29% | 1.50 | 4.0 s | 15.3 s |
| o3s6dsp_a_2b_s6m | Qwen3.5-2B | 40 | 100% | 1.05 / 2 | 78% | 82% | 80% | 32% | 2.40 | 4.0 s | 20.0 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o3s6d_4b_s5h | o3s6d_4b_s6 | 40 | +7.5 [+0.0, +17.5] | +32.8 [+15.3, +51.0] (n=37) |
| o3s6d_2b_s5h | o3s6d_2b_s6 | 40 | +22.5 [+10.0, +37.5] | +24.9 [+10.9, +39.3] (n=31) |
| o3s6d_4b_s5h | o3s6d_4b_s6m | 40 | +7.5 [+0.0, +17.5] | +29.2 [+11.9, +47.7] (n=37) |
| o3s6d_2b_s5h | o3s6d_2b_s6m | 40 | +22.5 [+10.0, +37.5] | +19.5 [+4.6, +35.2] (n=31) |
| o3s6dsp_a_2b_s5h | o3s6dsp_a_2b_s6 | 40 | +22.5 [+10.0, +35.0] | +11.9 [-4.4, +28.5] (n=31) |
