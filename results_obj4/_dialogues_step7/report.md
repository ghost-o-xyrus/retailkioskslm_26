# Simulated discovery dialogues (Objective 3, Step 6)

Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 questions; at least 90% of shown watches fit what the customer said.

| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) | All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| o4s6_2b_base_dlg | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.6 s | 9.9 s |
| o4s6_4b_base_dlg | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 3.7 s | 16.8 s |
| o4s7_2b_base_off_dlg | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.3 s | 9.5 s |
| o4s7_2b_lora_off_dlg | Qwen3.5-2B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 1.4 s | 8.4 s |
| o4s7_4b_base_short_dlg | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.05 | 3.2 s | 15.5 s |
| o4s7_4b_lora_short_dlg | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 4.2 s | 17.4 s |
| o4s7_4b_lora_shortoff_dlg | Qwen3.5-4B | 40 | 100% | 0.88 / 2 | 100% | 100% | 100% | 48% | 1.00 | 3.9 s | 16.5 s |

## Paired comparisons (same dialogues)

| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |
|---|---|---:|---|---|
| o4s6_2b_base_dlg | o4s7_2b_lora_off_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o4s6_2b_base_dlg | o4s7_2b_base_off_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o4s6_4b_base_dlg | o4s7_4b_lora_short_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o4s6_4b_base_dlg | o4s7_4b_lora_shortoff_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
| o4s6_4b_base_dlg | o4s7_4b_base_short_dlg | 40 | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] (n=40) |
