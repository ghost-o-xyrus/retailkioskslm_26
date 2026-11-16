# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | Qwen3.5-2B | all checked | 135 | 71.1% | 83.0% | +11.9 [+4.4, +19.3] | 5 / 21 | 0.002 | ±2.3 | **better** |
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | Qwen3.5-2B | answerable | 96 | 75.0% | 77.1% | +2.1 [-5.2, +9.4] | 5 / 7 | 0.774 | ±2.7 | **tie** |
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 61.5% | 97.4% | +35.9 [+20.5, +51.3] | 0 / 14 | 0.000 | ±4.3 | **better** |
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | Qwen3.5-2B | language: hinglish | 14 | 71.4% | 71.4% | +0.0 [-21.4, +21.4] | 1 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | tool cases | 59 | 84.7% | 93.2% | +8.5 [-1.7, +18.6] | 3 / 8 | 0.227 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | language: hinglish | 10 | 100.0% | 90.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 83.3% | -16.7 [-50.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 88.9% | -11.1 [-33.3, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 87.5% | +25.0 [-25.0, +62.5] | 1 / 3 | 0.625 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | Qwen3.5-2B | tool cases: tool_selection | 18 | 66.7% | 94.4% | +27.8 [+11.1, +50.0] | 0 / 5 | 0.062 | ±0.0 | **better** |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | Qwen3.5-2B | all checked | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 1 / 4 | 0.375 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | Qwen3.5-2B | answerable | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 1 / 4 | 0.375 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | Qwen3.5-2B | language: hinglish | 22 | 81.8% | 90.9% | +9.1 [+0.0, +22.7] | 0 / 2 | 0.500 | ±5.7 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | Qwen3.5-2B | type: followup_colour | 10 | 60.0% | 50.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | Qwen3.5-2B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 90.0% | +20.0 [+0.0, +50.0] | 0 / 2 | 0.500 | ±8.4 | **tie** |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | Qwen3.5-2B | all checked | 135 | 71.1% | 68.1% | -3.0 [-7.4, +0.7] | 6 / 2 | 0.289 | ±2.3 | **tie** |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | Qwen3.5-2B | answerable | 96 | 75.0% | 69.8% | -5.2 [-10.4, +0.0] | 6 / 1 | 0.125 | ±2.7 | **tie** |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 61.5% | 64.1% | +2.6 [+0.0, +7.7] | 0 / 1 | 1.000 | ±4.3 | **tie** |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | Qwen3.5-2B | language: hinglish | 14 | 71.4% | 71.4% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±7.1 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | tool cases | 59 | 84.7% | 86.4% | +1.7 [+0.0, +5.1] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 62.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | Qwen3.5-2B | tool cases: tool_selection | 18 | 66.7% | 72.2% | +5.6 [+0.0, +16.7] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | Qwen3.5-2B | all checked | 60 | 85.0% | 83.3% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | Qwen3.5-2B | answerable | 60 | 85.0% | 83.3% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | Qwen3.5-2B | language: hinglish | 22 | 81.8% | 81.8% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±5.7 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | Qwen3.5-2B | type: followup_colour | 10 | 60.0% | 50.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | Qwen3.5-2B | type: followup_fact | 30 | 93.3% | 93.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | Qwen3.5-2B | type: followup_switch | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | Qwen3.5-4B | all checked | 135 | 85.2% | 86.7% | +1.5 [-4.4, +7.4] | 7 / 9 | 0.804 | ±2.3 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | Qwen3.5-4B | answerable | 96 | 85.4% | 81.2% | -4.2 [-10.4, +2.1] | 7 / 3 | 0.344 | ±2.7 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 84.6% | 100.0% | +15.4 [+5.1, +28.2] | 0 / 6 | 0.031 | ±4.3 | **better** |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | Qwen3.5-4B | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 95.0% | +3.3 [+0.0, +8.3] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 89.5% | +5.3 [+0.0, +15.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | Qwen3.5-4B | all checked | 60 | 93.3% | 90.0% | -3.3 [-11.7, +5.0] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | Qwen3.5-4B | answerable | 60 | 93.3% | 90.0% | -3.3 [-11.7, +5.0] | 4 / 2 | 0.688 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | Qwen3.5-4B | language: hinglish | 22 | 86.4% | 90.9% | +4.5 [-9.1, +22.7] | 1 / 2 | 1.000 | ±5.7 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 50.0% | -40.0 [-70.0, -10.0] | 4 / 0 | 0.125 | ±8.4 | **worse** |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | Qwen3.5-4B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | all checked | 135 | 85.2% | 86.7% | +1.5 [-4.4, +7.4] | 7 / 9 | 0.804 | ±2.3 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | answerable | 96 | 85.4% | 81.2% | -4.2 [-10.4, +2.1] | 7 / 3 | 0.344 | ±2.7 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | unanswerable / near-miss | 39 | 84.6% | 100.0% | +15.4 [+5.1, +28.2] | 0 / 6 | 0.031 | ±4.3 | **better** |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | Qwen3.5-4B | language: hinglish | 14 | 71.4% | 78.6% | +7.1 [+0.0, +21.4] | 0 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 95.0% | +3.3 [+0.0, +8.3] | 0 / 2 | 0.500 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 100.0% | +12.5 [+0.0, +37.5] | 0 / 1 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 89.5% | +5.3 [+0.0, +15.8] | 0 / 1 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | all checked | 60 | 93.3% | 88.3% | -5.0 [-13.3, +3.3] | 5 / 2 | 0.453 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | answerable | 60 | 93.3% | 88.3% | -5.0 [-13.3, +3.3] | 5 / 2 | 0.453 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | language: hinglish | 22 | 86.4% | 86.4% | +0.0 [-18.2, +18.2] | 2 / 2 | 1.000 | ±5.7 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 40.0% | -50.0 [-80.0, -20.0] | 5 / 0 | 0.062 | ±8.4 | **worse** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | Qwen3.5-4B | all checked | 134 | 85.1% | 76.1% | -9.0 [-14.9, -3.0] | 15 / 3 | 0.008 | ±2.3 | **worse** |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | Qwen3.5-4B | answerable | 96 | 85.4% | 75.0% | -10.4 [-17.7, -4.2] | 11 / 1 | 0.006 | ±2.7 | **worse** |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | Qwen3.5-4B | unanswerable / near-miss | 38 | 84.2% | 78.9% | -5.3 [-18.4, +7.9] | 4 / 2 | 0.688 | ±4.3 | **tie** |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | Qwen3.5-4B | language: hinglish | 14 | 71.4% | 71.4% | +0.0 [-21.4, +21.4] | 1 / 1 | 1.000 | ±7.1 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 83.3% | -8.3 [-16.7, -1.7] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | language: hinglish | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 57.9% | -26.3 [-47.4, -5.3] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | Qwen3.5-4B | all checked | 60 | 93.3% | 95.0% | +1.7 [-3.3, +6.7] | 1 / 2 | 1.000 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | Qwen3.5-4B | answerable | 60 | 93.3% | 95.0% | +1.7 [-3.3, +6.7] | 1 / 2 | 1.000 | ±3.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | Qwen3.5-4B | language: hinglish | 22 | 86.4% | 95.5% | +9.1 [+0.0, +22.7] | 0 / 2 | 0.500 | ±5.7 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | Qwen3.5-4B | type: followup_fact | 30 | 93.3% | 100.0% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | 2.01 → 0.87 | 433 → 309 | 90 → 128 | 1 → 0 | 0 → 0 | 29/198 → 27/27 | 5.5 s → 1.8 s |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | 0.97 → 0.86 | 244 → 228 | 110 → 121 | 0 → 0 | 0 → 0 | 38/47 → 38/38 | 1.6 s → 1.4 s |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | 1.27 → 1.00 | 381 → 350 | 89 → 103 | 0 → 0 | 0 → 0 | 20/36 → 20/20 | 2.5 s → 2.4 s |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | 2.01 → 1.81 | 433 → 414 | 90 → 97 | 1 → 12 | 0 → 0 | 29/198 → 27/168 | 5.5 s → 4.9 s |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | 0.97 → 0.92 | 244 → 230 | 110 → 118 | 0 → 0 | 0 → 0 | 38/47 → 38/43 | 1.6 s → 1.3 s |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | 1.27 → 1.27 | 381 → 374 | 89 → 89 | 0 → 2 | 0 → 0 | 20/36 → 20/36 | 2.5 s → 2.1 s |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | 0.94 → 0.88 | 326 → 313 | 132 → 130 | 0 → 0 | 0 → 0 | 27/41 → 27/28 | 4.3 s → 4.3 s |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | 0.90 → 0.86 | 243 → 238 | 119 → 121 | 0 → 0 | 0 → 0 | 38/41 → 38/38 | 3.6 s → 3.8 s |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | 1.13 → 1.02 | 374 → 361 | 102 → 109 | 2 → 0 | 0 → 0 | 22/28 → 20/21 | 5.6 s → 6.4 s |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 0.94 → 0.88 | 326 → 311 | 132 → 130 | 0 → 0 | 0 → 0 | 27/41 → 27/28 | 4.3 s → 5.4 s |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 0.90 → 0.86 | 243 → 228 | 119 → 121 | 0 → 0 | 0 → 0 | 38/41 → 38/38 | 3.6 s → 3.8 s |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 1.13 → 1.02 | 374 → 354 | 102 → 109 | 2 → 0 | 0 → 0 | 22/28 → 20/21 | 5.6 s → 6.5 s |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | 0.94 → 1.15 | 326 → 351 | 132 → 112 | 0 → 9 | 0 → 0 | 27/41 → 39/69 | 4.3 s → 4.6 s |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | 0.90 → 0.95 | 243 → 254 | 119 → 122 | 0 → 5 | 0 → 0 | 38/41 → 43/46 | 3.6 s → 3.1 s |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | 1.13 → 1.13 | 374 → 379 | 102 → 111 | 2 → 2 | 0 → 0 | 22/28 → 25/28 | 5.6 s → 5.0 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | 151 | -3.08 s [-4.62, -2.92] | -2.96 s [-4.80, -2.46] |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | 77 | -0.19 s [-0.22, -0.10] | -0.05 s [-0.25, -0.00] |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | 60 | -0.19 s [-0.26, -0.15] | +0.48 s [-0.02, +0.72] |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | 151 | -0.52 s [-0.59, -0.44] | -0.63 s [-0.70, -0.55] |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | 77 | -0.29 s [-0.37, -0.25] | -0.48 s [-0.64, -0.39] |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | 60 | -0.39 s [-0.42, -0.35] | -0.44 s [-0.52, -0.38] |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | 151 | -0.21 s [-0.26, -0.12] | -2.08 s [-2.73, -1.54] |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | 78 | +0.30 s [+0.22, +0.36] | -0.29 s [-0.80, -0.01] |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | 60 | +0.74 s [+0.66, +0.82] | +1.24 s [+0.48, +1.62] |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 151 | +0.52 s [+0.38, +0.81] | -0.86 s [-1.56, -0.05] |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 78 | +0.23 s [+0.10, +0.33] | -0.19 s [-0.82, +0.00] |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 60 | +0.81 s [+0.69, +0.99] | +1.31 s [+0.63, +2.09] |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | 150 | -0.01 s [-0.05, +0.01] | -0.20 s [-0.75, -0.06] |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | 78 | -0.54 s [-0.64, -0.49] | -1.35 s [-1.73, -0.90] |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | 60 | -0.75 s [-0.78, -0.66] | -0.70 s [-0.78, -0.51] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | 3 → 0 | 1 → 0 | 1 → 0 | 1 → 0 | 34 → 0 | 20 → 0 | 11 → 39 | 0 → 0 | 9 → 39 | 0 → 0 |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 5 → 0 | 0 → 0 | 7 → 12 | 0 → 1 | 0 → 11 | 0 → 0 |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | 3 → 12 | 1 → 12 | 1 → 0 | 1 → 0 | 34 → 32 | 20 → 24 | 11 → 9 | 0 → 0 | 9 → 9 | 0 → 0 |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 5 → 3 | 0 → 0 | 7 → 7 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | 0 → 2 | 0 → 2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 4 | 0 → 0 | 1 → 1 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 27 → 32 | 0 → 0 | 22 → 32 | 0 → 0 |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 9 | 0 → 0 | 4 → 9 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | 3 → 0 | 2 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 2 → 3 | 0 → 0 | 1 → 3 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 27 → 32 | 0 → 0 | 22 → 32 | 0 → 0 |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 9 | 0 → 0 | 4 → 9 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 3 → 0 | 2 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 2 → 5 | 0 → 0 | 1 → 5 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | 0 → 14 | 0 → 9 | 0 → 1 | 0 → 4 | 0 → 7 | 0 → 4 | 27 → 22 | 0 → 0 | 22 → 19 | 0 → 0 |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | 0 → 6 | 0 → 5 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 | 7 → 6 | 0 → 0 | 4 → 4 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | 3 → 5 | 2 → 2 | 0 → 0 | 1 → 3 | 0 → 0 | 0 → 0 | 2 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | 10 → 10 | 8 → 8 | 26 → 0 | 6 → 0 |
| o4s6_2b_base_v12 | o4s7_2b_lora_off_v12 | 1 → 1 | 0 → 0 | 2 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | 10 → 10 | 8 → 8 | 26 → 0 | 6 → 0 |
| o4s6_2b_base_v12 | o4s7_2b_base_off_v12 | 1 → 1 | 0 → 0 | 2 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_v12 | o4s7_4b_lora_short_v12 | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_v12 | o4s7_4b_lora_shortoff_v12 | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | 10 → 10 | 8 → 8 | 0 → 4 | 0 → 1 |
| o4s6_4b_base_v12 | o4s7_4b_base_short_v12 | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o4s6_2b_base_rag | o4s7_2b_lora_off_rag | 8/130 (6.2%) → 2/131 (1.5%) | 0 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s7_2b_lora_off_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o4s6_2b_base_rag | o4s7_2b_base_off_rag | 8/130 (6.2%) → 6/122 (4.9%) | 0 → 0 | 0 → 0 |
| o4s6_2b_base_fup | o4s7_2b_base_off_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_short_rag | 3/131 (2.3%) → 0/131 (0.0%) | 3 → 0 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_short_fup | 0/38 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_lora_shortoff_rag | 3/131 (2.3%) → 0/131 (0.0%) | 3 → 0 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_lora_shortoff_fup | 0/38 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o4s6_4b_base_rag | o4s7_4b_base_short_rag | 3/131 (2.3%) → 5/129 (3.9%) | 3 → 3 | 0 → 0 |
| o4s6_4b_base_fup | o4s7_4b_base_short_fup | 0/38 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
