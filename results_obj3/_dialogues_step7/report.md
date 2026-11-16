# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3s6d3_2b_s6 | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.3 s | 9.9 s |
| o3s6d3_4b_s6 | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 3.3 s | 18.1 s |
| o3s7d_2b_s7 | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.5 s | 10.8 s |
| o3s7d_4b_s7 | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.02 | 3.4 s | 19.6 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o3s6d3_4b_s6 | o3s7d_4b_s7 | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o3s6d3_2b_s6 | o3s7d_2b_s7 | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
