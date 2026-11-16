# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o4s6_2b_base_dlg | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.6 s | 9.9 s |
| o4s6_2b_lora_dlg | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.7 s | 8.5 s |
| o4s6_2b_qlora_dlg | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.8 s | 10.0 s |
| o4s6_4b_base_dlg | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 3.7 s | 16.8 s |
| o4s6_4b_lora_dlg | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 4.1 s | 16.9 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o4s6_2b_base_dlg | o4s6_2b_lora_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o4s6_2b_base_dlg | o4s6_2b_qlora_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o4s6_4b_base_dlg | o4s6_4b_lora_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
