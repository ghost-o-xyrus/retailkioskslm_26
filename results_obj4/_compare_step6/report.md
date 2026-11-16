# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o4s6_2b_base_rag | o4s6_2b_lora_rag | Qwen3.5-2B | all checked | 135 | 71.1% | 83.0% | +11.9 [+4.4, +19.3] | 5 / 21 | 0.002 | ±2.3 | **better** |
| o4s6_2b_base_rag | o4s6_2b_lora_rag | Qwen3.5-2B | answerable | 96 | 75.0% | 77.1% | +2.1 [-5.2, +9.4] | 5 / 7 | 0.774 | ±2.7 | **tie** |
| o4s6_2b_base_rag | o4s6_2b_lora_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 61.5% | 97.4% | +35.9 [+20.5, +51.3] | 0 / 14 | 0.000 | ±4.3 | **better** |
| o4s6_2b_base_rag | o4s6_2b_lora_rag | Qwen3.5-2B | language: hinglish | 14 | 71.4% | 71.4% | +0.0 [-21.4, +21.4] | 1 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | tool cases | 59 | 84.7% | 89.8% | +5.1 [-6.8, +15.3] | 4 / 7 | 0.549 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | language: hinglish | 10 | 100.0% | 80.0% | -20.0 [-50.0, +0.0] | 2 / 0 | 0.500 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 83.3% | -16.7 [-50.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 77.8% | -22.2 [-55.6, +0.0] | 2 / 0 | 0.500 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 87.5% | +25.0 [-25.0, +62.5] | 1 / 3 | 0.625 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | Qwen3.5-2B | tool cases: tool_selection | 18 | 66.7% | 88.9% | +22.2 [+5.6, +44.4] | 0 / 4 | 0.125 | ±0.0 | **better** |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | Qwen3.5-2B | all checked | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 1 / 4 | 0.375 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | Qwen3.5-2B | answerable | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 1 / 4 | 0.375 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | Qwen3.5-2B | language: hinglish | 22 | 81.8% | 90.9% | +9.1 [+0.0, +22.7] | 0 / 2 | 0.500 | ±5.7 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | Qwen3.5-2B | type: followup_colour | 10 | 60.0% | 50.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | Qwen3.5-2B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 90.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±8.4 | **tie** |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | all checked | 135 | 71.1% | 84.4% | +13.3 [+5.9, +20.7] | 4 / 22 | 0.001 | ±2.3 | **better** |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | answerable | 96 | 75.0% | 82.3% | +7.3 [+0.0, +14.6] | 4 / 11 | 0.118 | ±2.7 | **tie** |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 61.5% | 89.7% | +28.2 [+15.4, +43.6] | 0 / 11 | 0.001 | ±4.3 | **better** |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases | 59 | 84.7% | 96.6% | +11.9 [+1.7, +22.0] | 2 / 9 | 0.065 | ±0.0 | **better** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 83.3% | -16.7 [-50.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 87.5% | +25.0 [-25.0, +62.5] | 1 / 3 | 0.625 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: tool_selection | 18 | 66.7% | 100.0% | +33.3 [+11.1, +55.6] | 0 / 6 | 0.031 | ±0.0 | **better** |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | all checked | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 1 / 4 | 0.375 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | answerable | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 1 / 4 | 0.375 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | language: hinglish | 22 | 81.8% | 90.9% | +9.1 [+0.0, +22.7] | 0 / 2 | 0.500 | ±5.7 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_colour | 10 | 60.0% | 50.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 90.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±8.4 | **tie** |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | all checked | 135 | 83.0% | 84.4% | +1.5 [-3.7, +6.7] | 5 / 7 | 0.774 | ±2.3 | **tie** |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | answerable | 96 | 77.1% | 82.3% | +5.2 [+0.0, +11.5] | 2 / 7 | 0.180 | ±2.7 | **tie** |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 97.4% | 89.7% | -7.7 [-17.9, +0.0] | 3 / 0 | 0.250 | ±4.3 | **tie** |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | Qwen3.5-2B | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases | 60 | 88.3% | 95.0% | +6.7 [+1.7, +13.3] | 0 / 4 | 0.125 | ±0.0 | **better** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | language: hinglish | 10 | 80.0% | 100.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 77.8% | 100.0% | +22.2 [+0.0, +55.6] | 0 / 2 | 0.500 | ±0.0 | **(small)** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | Qwen3.5-2B | tool cases: tool_selection | 19 | 84.2% | 94.7% | +10.5 [+0.0, +26.3] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | all checked | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | answerable | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±3.4 | **tie** |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | language: hinglish | 22 | 90.9% | 90.9% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.7 | **tie** |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_colour | 10 | 50.0% | 50.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | Qwen3.5-2B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | Qwen3.5-4B | all checked | 135 | 85.2% | 85.9% | +0.7 [-5.2, +7.4] | 9 / 10 | 1.000 | ±2.3 | **tie** |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | Qwen3.5-4B | answerable | 96 | 85.4% | 80.2% | -5.2 [-12.5, +2.1] | 9 / 4 | 0.267 | ±2.7 | **tie** |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 84.6% | 100.0% | +15.4 [+5.1, +28.2] | 0 / 6 | 0.031 | ±4.3 | **better** |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | Qwen3.5-4B | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 95.0% | +3.3 [+0.0, +8.3] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 89.5% | +5.3 [+0.0, +15.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | Qwen3.5-4B | all checked | 60 | 93.3% | 90.0% | -3.3 [-11.7, +5.0] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | Qwen3.5-4B | answerable | 60 | 93.3% | 90.0% | -3.3 [-11.7, +5.0] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | Qwen3.5-4B | language: hinglish | 22 | 86.4% | 90.9% | +4.5 [-9.1, +22.7] | 1 / 2 | 1.000 | ±5.7 | **tie** |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 50.0% | -40.0 [-70.0, -10.0] | 4 / 0 | 0.125 | ±8.4 | **worse** |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | Qwen3.5-4B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o4s6_2b_base_rag | o4s6_2b_lora_rag | 2.01 → 0.87 | 433 → 312 | 90 → 128 | 1 → 0 | 0 → 0 | 29/198 → 27/27 | 5.5 s → 2.1 s |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | 0.97 → 0.86 | 244 → 238 | 110 → 121 | 0 → 0 | 0 → 0 | 38/47 → 38/38 | 1.6 s → 1.7 s |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | 1.27 → 1.00 | 381 → 357 | 89 → 103 | 0 → 0 | 0 → 0 | 20/36 → 20/20 | 2.5 s → 2.7 s |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | 2.01 → 0.87 | 433 → 312 | 90 → 128 | 1 → 0 | 0 → 0 | 29/198 → 27/27 | 5.5 s → 2.1 s |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | 0.97 → 0.86 | 244 → 238 | 110 → 121 | 0 → 0 | 0 → 0 | 38/47 → 38/38 | 1.6 s → 1.9 s |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | 1.27 → 1.00 | 381 → 357 | 89 → 103 | 0 → 0 | 0 → 0 | 20/36 → 20/20 | 2.5 s → 2.7 s |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | 0.87 → 0.87 | 312 → 312 | 128 → 128 | 0 → 0 | 0 → 0 | 27/27 → 27/27 | 2.1 s → 2.1 s |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | 0.86 → 0.86 | 238 → 238 | 121 → 121 | 0 → 0 | 0 → 0 | 38/38 → 38/38 | 1.7 s → 1.9 s |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | 1.00 → 1.00 | 357 → 357 | 103 → 103 | 0 → 0 | 0 → 0 | 20/20 → 20/20 | 2.7 s → 2.7 s |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | 0.94 → 0.88 | 326 → 313 | 132 → 130 | 0 → 0 | 0 → 0 | 27/41 → 27/28 | 4.3 s → 4.7 s |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | 0.90 → 0.86 | 243 → 238 | 119 → 121 | 0 → 0 | 0 → 0 | 38/41 → 38/38 | 3.6 s → 3.9 s |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | 1.13 → 1.02 | 374 → 361 | 102 → 109 | 2 → 0 | 0 → 0 | 22/28 → 20/21 | 5.6 s → 6.0 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o4s6_2b_base_rag | o4s6_2b_lora_rag | 151 | -2.83 s [-4.39, -2.74] | -2.76 s [-4.59, -2.18] |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | 77 | +0.12 s [+0.07, +0.23] | +0.31 s [+0.00, +0.65] |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | 60 | +0.12 s [+0.05, +0.15] | +0.82 s [+0.40, +1.08] |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | 151 | -2.84 s [-4.39, -2.73] | -2.62 s [-4.27, -1.87] |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | 77 | +0.19 s [+0.08, +0.24] | +0.61 s [+0.01, +0.80] |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | 60 | +0.11 s [+0.09, +0.19] | +1.00 s [+0.54, +1.29] |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | 151 | -0.00 s [-0.01, +0.01] | +0.00 s [-0.01, +0.03] |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | 78 | +0.03 s [+0.00, +0.07] | +0.03 s [-0.00, +0.23] |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | 60 | +0.01 s [-0.02, +0.03] | +0.10 s [-0.03, +0.20] |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | 151 | +0.40 s [+0.33, +0.47] | -1.38 s [-1.91, -0.91] |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | 78 | +0.33 s [+0.18, +0.38] | +0.00 s [-0.75, +0.01] |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | 60 | +0.46 s [+0.39, +0.52] | +0.60 s [+0.02, +1.28] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o4s6_2b_base_rag | o4s6_2b_lora_rag | 3 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 34 → 0 | 20 → 0 | 11 → 39 | 0 → 0 | 9 → 39 | 0 → 0 |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 5 → 0 | 0 → 0 | 7 → 13 | 0 → 2 | 0 → 11 | 0 → 0 |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 3 | 0 → 0 | 1 → 3 | 0 → 0 |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | 3 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 34 → 0 | 20 → 0 | 11 → 32 | 0 → 0 | 9 → 32 | 0 → 0 |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 5 → 0 | 0 → 0 | 7 → 11 | 0 → 0 | 0 → 10 | 0 → 0 |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 39 → 32 | 0 → 0 | 39 → 32 | 0 → 0 |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 13 → 11 | 2 → 0 | 11 → 10 | 0 → 0 |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 3 → 1 | 0 → 0 | 3 → 1 | 0 → 0 |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 27 → 35 | 0 → 0 | 22 → 35 | 0 → 0 |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 9 | 0 → 0 | 4 → 9 | 0 → 0 |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | 3 → 0 | 2 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 2 → 4 | 0 → 0 | 1 → 4 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o4s6_2b_base_rag | o4s6_2b_lora_rag | 10 → 10 | 8 → 8 | 26 → 0 | 6 → 0 |
| o4s6_2b_base_v12 | o4s6_2b_lora_v12 | 1 → 1 | 0 → 0 | 2 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | 10 → 10 | 8 → 8 | 26 → 0 | 6 → 0 |
| o4s6_2b_base_v12 | o4s6_2b_qlora_v12 | 1 → 1 | 0 → 0 | 2 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o4s6_2b_lora_v12 | o4s6_2b_qlora_v12 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_v12 | o4s6_4b_lora_v12 | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o4s6_2b_base_rag | o4s6_2b_lora_rag | 8/130 (6.2%) → 2/131 (1.5%) | 0 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s6_2b_lora_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o4s6_2b_base_rag | o4s6_2b_qlora_rag | 8/130 (6.2%) → 2/131 (1.5%) | 0 → 1 | 0 → 0 |
| o4s6_2b_base_fup | o4s6_2b_qlora_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o4s6_2b_lora_rag | o4s6_2b_qlora_rag | 2/131 (1.5%) → 2/131 (1.5%) | 0 → 1 | 0 → 0 |
| o4s6_2b_lora_fup | o4s6_2b_qlora_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s6_4b_lora_rag | 3/131 (2.3%) → 1/131 (0.8%) | 3 → 0 | 0 → 0 |
| o4s6_4b_base_fup | o4s6_4b_lora_fup | 0/38 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
