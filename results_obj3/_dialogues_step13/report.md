# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3s12d_2b | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.6 s | 10.7 s |
| o3s12d_4b | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 3.4 s | 17.7 s |
| o3s13ad_2b | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.6 s | 9.6 s |
| o3s13ad_4b | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.05 | 3.6 s | 16.4 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o3s12d_4b | o3s13ad_4b | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o3s12d_2b | o3s13ad_2b | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
