# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3s6d2_2b_s5h | Qwen3.5-2B | 40 | 72% | 0.86 / 2 | 76% | 66% | 52% | 24% | 4.40 | 6.9 s | 33.6 s |
| o3s6d2_4b_s5h | Qwen3.5-4B | 40 | 98% | 1.08 / 3 | 97% | 47% | 41% | 26% | 3.85 | 12.8 s | 58.4 s |
| o3s6d3_2b_s6 | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.3 s | 9.9 s |
| o3s6d3_4b_s6 | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 3.3 s | 18.1 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o3s6d2_4b_s5h | o3s6d3_4b_s6 | 40 | +2.5 [+0.0, +7.5] | +53.3 [+37.9, +68.2] (n=39) |
| o3s6d2_2b_s5h | o3s6d3_2b_s6 | 40 | +27.5 [+15.0, +42.5] | +33.9 [+19.3, +49.5] (n=29) |
