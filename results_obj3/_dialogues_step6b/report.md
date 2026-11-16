# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3s6d2_2b_s5h | Qwen3.5-2B | 40 | 72% | 0.86 / 2 | 76% | 66% | 52% | 24% | 4.40 | 6.9 s | 33.6 s |
| o3s6d2_2b_s6 | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 88% | 88% | 40% | 1.00 | 1.5 s | 10.3 s |
| o3s6d2_4b_s5h | Qwen3.5-4B | 40 | 98% | 1.08 / 3 | 97% | 47% | 41% | 26% | 3.85 | 12.8 s | 58.4 s |
| o3s6d2_4b_s6 | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 88% | 88% | 40% | 1.00 | 3.6 s | 19.2 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o3s6d2_4b_s5h | o3s6d2_4b_s6 | 40 | +2.5 [+0.0, +7.5] | +41.4 [+23.4, +59.0] (n=39) |
| o3s6d2_2b_s5h | o3s6d2_2b_s6 | 40 | +27.5 [+15.0, +42.5] | +24.7 [+9.7, +40.7] (n=29) |
