# Step 6: adapters against O3-final on dev (pre-registered rules)

## Sets

| Adapter | Set | Cases | O3-final | + adapter | Difference [95% CI] | McNemar p | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| lora_2b | store questions | 135 | 71.1% | 83.0% | +11.9 [+4.4, +19.3] | 0.00249 | better |
| lora_2b | tool cases | 59 | 84.7% | 89.8% | +5.1 [-6.8, +15.3] | 0.549 | tie |
| lora_2b | follow-ups | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 0.375 | tie |
| qlora_2b | store questions | 135 | 71.1% | 84.4% | +13.3 [+5.9, +20.7] | 0.000534 | better |
| qlora_2b | tool cases | 59 | 84.7% | 96.6% | +11.9 [+1.7, +22.0] | 0.0654 | better |
| qlora_2b | follow-ups | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 0.375 | tie |
| lora_4b | store questions | 135 | 85.2% | 85.9% | +0.7 [-5.2, +7.4] | 1 | tie |
| lora_4b | tool cases | 60 | 91.7% | 95.0% | +3.3 [+0.0, +8.3] | 0.5 | tie |
| lora_4b | follow-ups | 60 | 93.3% | 90.0% | -3.3 [-11.7, +5.0] | 0.688 | tie |

## Dialogues (40 dev profiles)

| Run | Recommended | ≥2 slots known | Questions max | Fit (mean) | Fit vs O3-final [95% CI] |
|---|---:|---:|---:|---:|---|
| o4s6_2b_base_dlg | 100% | 100% | 2 | 100% |  |
| o4s6_2b_lora_dlg | 100% | 100% | 2 | 100% | +0.0 [+0.0, +0.0] |
| o4s6_2b_qlora_dlg | 100% | 100% | 2 | 100% | +0.0 [+0.0, +0.0] |
| o4s6_4b_base_dlg | 100% | 100% | 2 | 100% |  |
| o4s6_4b_lora_dlg | 100% | 100% | 2 | 100% | +0.0 [+0.0, +0.0] |

## Printed tool calls (runs, repeat 0)

| Adapter | | Store | Tool cases | Follow-ups | Dialogues |
|---|---|---:|---:|---:|---:|
| lora_2b | O3-final | 3 | 0 | 0 | 0 |
| lora_2b | adapter | 0 | 0 | 0 | 0 |
| qlora_2b | O3-final | 3 | 0 | 0 | 0 |
| qlora_2b | adapter | 0 | 0 | 0 | 0 |
| lora_4b | O3-final | 0 | 0 | 3 | 0 |
| lora_4b | adapter | 0 | 0 | 0 | 0 |

## Hypotheses and verdicts

- **lora_2b** (Tier A): **kept**. store questions: better, tool cases: tie, follow-ups: tie, dialogues: met, hinglish: ok, H1: gain, H2: met, H3: met, H4: met. Hinglish pooled 82.6% → 82.6% (+0.0 points, 46 cases); staff on answerable 20 → 0; unsupported 8/130 → 2/131
- **qlora_2b** (Tier A): **kept**. store questions: better, tool cases: better, follow-ups: tie, dialogues: met, hinglish: ok, H1: gain, H2: met, H3: met, H4: met. Hinglish pooled 82.6% → 89.1% (+6.5 points, 46 cases); staff on answerable 20 → 0; unsupported 8/130 → 2/131
- **lora_4b** (Tier B): **kept**. store questions: tie, tool cases: tie, follow-ups: tie, dialogues: met, hinglish: ok, H1: gain, H4: met. Hinglish pooled 84.8% → 89.1% (+4.3 points, 46 cases)
- **H6, QLoRA vs LoRA (2B):** store questions: tie, tool cases: better, follow-ups: tie. QLoRA is not worse than LoRA on any set; it is better on at least one, against the expectation.
- Carried to Step 7: Tier A lora_2b; Tier B lora_4b.

## Reported, not used to decide

| Base | New | Subset | Cases | Base | New | Difference [95% CI] | Verdict |
|---|---|---|---:|---:|---:|---|---|
| o4s6_2b_base_rag | o4s6_2b_lora_rag | answerable | 96 | 75.0% | 77.1% | +2.1 [-5.2, +9.4] | tie |
| o4s6_2b_base_rag | o4s6_2b_lora_rag | unanswerable / near-miss | 39 | 61.5% | 97.4% | +35.9 [+20.5, +51.3] | better |
| o4s6_2b_base_rag | o4s6_2b_lora_rag | language: hinglish | 14 | 71.4% | 71.4% | +0.0 [-21.4, +21.4] | tie |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | language: hinglish | 10 | 100.0% | 80.0% | -20.0 [-50.0, +0.0] | tie |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | tool cases: tool_selection | 18 | 66.7% | 88.9% | +22.2 [+5.6, +44.4] | better |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | answerable | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | tie |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | language: hinglish | 22 | 81.8% | 90.9% | +9.1 [+0.0, +22.7] | tie |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | type: followup_colour | 10 | 60.0% | 50.0% | -10.0 [-30.0, +0.0] | tie |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | tie |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | type: followup_switch | 10 | 70.0% | 90.0% | +20.0 [+0.0, +50.0] | tie |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | answerable | 96 | 75.0% | 82.3% | +7.3 [+0.0, +14.6] | tie |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | unanswerable / near-miss | 39 | 61.5% | 89.7% | +28.2 [+15.4, +43.6] | better |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | tie |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | tool cases: tool_selection | 18 | 66.7% | 100.0% | +33.3 [+11.1, +55.6] | better |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | answerable | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | tie |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | language: hinglish | 22 | 81.8% | 90.9% | +9.1 [+0.0, +22.7] | tie |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | type: followup_colour | 10 | 60.0% | 50.0% | -10.0 [-30.0, +0.0] | tie |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | tie |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | type: followup_switch | 10 | 70.0% | 90.0% | +20.0 [+0.0, +50.0] | tie |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | answerable | 96 | 77.1% | 82.3% | +5.2 [+0.0, +11.5] | tie |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | unanswerable / near-miss | 39 | 97.4% | 89.7% | -7.7 [-17.9, +0.0] | tie |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | tie |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | language: hinglish | 10 | 80.0% | 100.0% | +20.0 [+0.0, +50.0] | tie |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | tool cases: tool_selection | 19 | 84.2% | 94.7% | +10.5 [+0.0, +26.3] | tie |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | answerable | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | language: hinglish | 22 | 90.9% | 90.9% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | type: followup_colour | 10 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | answerable | 96 | 85.4% | 80.2% | -5.2 [-12.5, +2.1] | tie |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | unanswerable / near-miss | 39 | 84.6% | 100.0% | +15.4 [+5.1, +28.2] | better |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | tie |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | tool cases: tool_selection | 19 | 84.2% | 89.5% | +5.3 [+0.0, +15.8] | tie |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | answerable | 60 | 93.3% | 90.0% | -3.3 [-11.7, +5.0] | tie |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | language: hinglish | 22 | 86.4% | 90.9% | +4.5 [-9.1, +22.7] | tie |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | type: followup_colour | 10 | 90.0% | 50.0% | -40.0 [-70.0, -10.0] | worse |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | tie |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | tie |

First-word wait p50 on the quality runs (Vulkan; Step 8 measures Tier A in place):

- o4s6_2b_base_rag → o4s6_2b_lora_rag: 5.5 s → 2.1 s
- o4s6_2b_base_v12 → o4s6_2b_lora_v12: 1.6 s → 1.7 s
- o4s6_2b_base_fup → o4s6_2b_lora_fup: 2.5 s → 2.7 s
- o4s6_2b_base_rag → o4s6_2b_qlora_rag: 5.5 s → 2.1 s
- o4s6_2b_base_v12 → o4s6_2b_qlora_v12: 1.6 s → 1.9 s
- o4s6_2b_base_fup → o4s6_2b_qlora_fup: 2.5 s → 2.7 s
- o4s6_2b_lora_rag → o4s6_2b_qlora_rag: 2.1 s → 2.1 s
- o4s6_2b_lora_v12 → o4s6_2b_qlora_v12: 1.7 s → 1.9 s
- o4s6_2b_lora_fup → o4s6_2b_qlora_fup: 2.7 s → 2.7 s
- o4s6_4b_base_rag → o4s6_4b_lora_rag: 4.3 s → 4.7 s
- o4s6_4b_base_v12 → o4s6_4b_lora_v12: 3.6 s → 3.9 s
- o4s6_4b_base_fup → o4s6_4b_lora_fup: 5.6 s → 6.0 s
