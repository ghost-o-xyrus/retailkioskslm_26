# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o3s6d_4b_s6 | Qwen3.5-4B | 40 | 100% | 0.97 / 2 | 98% | 78% | 72% | 34% | 1.18 | 2.9 s | 20.2 s |
| o3s6d_4b_s6m | Qwen3.5-4B | 40 | 100% | 1.18 / 2 | 98% | 78% | 75% | 40% | 2.25 | 2.9 s | 28.8 s |
