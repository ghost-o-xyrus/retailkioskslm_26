# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3s6d_2b_s6 | Qwen3.5-2B | 40 | 100% | 0.90 / 2 | 88% | 81% | 78% | 29% | 1.50 | 1.4 s | 11.8 s |
| o3s6d_2b_s6m | Qwen3.5-2B | 40 | 100% | 0.93 / 2 | 75% | 79% | 78% | 24% | 2.27 | 1.4 s | 14.5 s |
