# Paired dev comparison (Objective 3)

NEW − BASE in points, repeat 0, automatic checks. Verdict: better/worse only if the difference is larger than the noise bound and the bootstrap interval excludes 0.

| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p | Noise bound | Verdict |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|
| o3s12_4b_rag | o3s13a_4b_rag | Qwen3.5-4B | all checked | 134 | 83.6% | 77.6% | -6.0 [-11.9, +0.0] | 13 / 5 | 0.096 | ±2.3 | **tie** |
| o3s12_4b_rag | o3s13a_4b_rag | Qwen3.5-4B | answerable | 96 | 84.4% | 75.0% | -9.4 [-16.7, -3.1] | 10 / 1 | 0.012 | ±2.7 | **worse** |
| o3s12_4b_rag | o3s13a_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 38 | 81.6% | 84.2% | +2.6 [-10.5, +15.8] | 3 / 4 | 1.000 | ±4.3 | **tie** |
| o3s12_4b_rag | o3s13a2_4b_rag | Qwen3.5-4B | all checked | 134 | 83.6% | 76.1% | -7.5 [-13.4, -1.5] | 14 / 4 | 0.031 | ±2.3 | **worse** |
| o3s12_4b_rag | o3s13a2_4b_rag | Qwen3.5-4B | answerable | 96 | 84.4% | 75.0% | -9.4 [-16.7, -3.1] | 10 / 1 | 0.012 | ±2.7 | **worse** |
| o3s12_4b_rag | o3s13a2_4b_rag | Qwen3.5-4B | unanswerable / near-miss | 38 | 81.6% | 78.9% | -2.6 [-15.8, +10.5] | 4 / 3 | 1.000 | ±4.3 | **tie** |
| o3s12_2b_rag | o3s13a2_2b_rag | Qwen3.5-2B | all checked | 135 | 74.8% | 71.1% | -3.7 [-8.1, +0.7] | 7 / 2 | 0.180 | ±2.3 | **tie** |
| o3s12_2b_rag | o3s13a2_2b_rag | Qwen3.5-2B | answerable | 96 | 79.2% | 75.0% | -4.2 [-9.4, +0.0] | 5 / 1 | 0.219 | ±2.7 | **tie** |
| o3s12_2b_rag | o3s13a2_2b_rag | Qwen3.5-2B | unanswerable / near-miss | 39 | 64.1% | 61.5% | -2.6 [-10.3, +5.1] | 2 / 1 | 1.000 | ±4.3 | **tie** |
| o3s12_4b_v12 | o3s13a2_4b_v12 | Qwen3.5-4B | tool cases | 60 | 91.7% | 83.3% | -8.3 [-16.7, -1.7] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o3s12_4b_v12 | o3s13a2_4b_v12 | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a2_4b_v12 | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_v12 | o3s13a2_4b_v12 | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a2_4b_v12 | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a2_4b_v12 | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13a2_4b_v12 | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 57.9% | -26.3 [-47.4, -5.3] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o3s12_2b_v12 | o3s13a2_2b_v12 | Qwen3.5-2B | tool cases | 59 | 84.7% | 84.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_2b_v12 | o3s13a2_2b_v12 | Qwen3.5-2B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a2_2b_v12 | Qwen3.5-2B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_2b_v12 | o3s13a2_2b_v12 | Qwen3.5-2B | tool cases: handoff | 6 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a2_2b_v12 | Qwen3.5-2B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a2_2b_v12 | Qwen3.5-2B | tool cases: refusal | 8 | 62.5% | 62.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_2b_v12 | o3s13a2_2b_v12 | Qwen3.5-2B | tool cases: tool_selection | 18 | 66.7% | 66.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_fup | o3s13a2_4b_fup | Qwen3.5-4B | all checked | 60 | 96.7% | 95.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13a2_4b_fup | Qwen3.5-4B | answerable | 60 | 96.7% | 95.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13a2_4b_fup | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13a2_4b_fup | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3s12_4b_fup | o3s13a2_4b_fup | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13a2_4b_fup | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_2b_fup | o3s13a2_2b_fup | Qwen3.5-2B | all checked | 60 | 86.7% | 85.0% | -1.7 [-10.0, +6.7] | 4 / 3 | 1.000 | ±3.4 | **tie** |
| o3s12_2b_fup | o3s13a2_2b_fup | Qwen3.5-2B | answerable | 60 | 86.7% | 85.0% | -1.7 [-10.0, +6.7] | 4 / 3 | 1.000 | ±3.4 | **tie** |
| o3s12_2b_fup | o3s13a2_2b_fup | Qwen3.5-2B | type: followup_colour | 10 | 80.0% | 60.0% | -20.0 [-50.0, +0.0] | 2 / 0 | 0.500 | ±8.4 | **tie** |
| o3s12_2b_fup | o3s13a2_2b_fup | Qwen3.5-2B | type: followup_fact | 30 | 86.7% | 93.3% | +6.7 [+0.0, +16.7] | 0 / 2 | 0.500 | ±4.9 | **tie** |
| o3s12_2b_fup | o3s13a2_2b_fup | Qwen3.5-2B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_2b_fup | o3s13a2_2b_fup | Qwen3.5-2B | type: followup_switch | 10 | 80.0% | 70.0% | -10.0 [-40.0, +20.0] | 2 / 1 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | Qwen3.5-4B | all checked | 135 | 83.7% | 85.2% | +1.5 [-3.0, +5.9] | 3 / 5 | 0.727 | ±2.3 | **tie** |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | Qwen3.5-4B | answerable | 96 | 84.4% | 85.4% | +1.0 [+0.0, +3.1] | 0 / 1 | 1.000 | ±2.7 | **tie** |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | Qwen3.5-4B | unanswerable / near-miss | 39 | 82.1% | 84.6% | +2.6 [-10.3, +15.4] | 3 / 4 | 1.000 | ±4.3 | **tie** |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | Qwen3.5-4B | all checked | 134 | 83.6% | 76.1% | -7.5 [-13.4, -1.5] | 14 / 4 | 0.031 | ±2.3 | **worse** |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | Qwen3.5-4B | answerable | 96 | 84.4% | 75.0% | -9.4 [-16.7, -3.1] | 10 / 1 | 0.012 | ±2.7 | **worse** |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | Qwen3.5-4B | unanswerable / near-miss | 38 | 81.6% | 78.9% | -2.6 [-15.8, +10.5] | 4 / 3 | 1.000 | ±4.3 | **tie** |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | Qwen3.5-4B | tool cases | 60 | 91.7% | 91.7% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 84.2% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | Qwen3.5-4B | tool cases | 60 | 91.7% | 83.3% | -8.3 [-16.7, -1.7] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | Qwen3.5-4B | tool cases: comparison | 2 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | Qwen3.5-4B | tool cases: discovery | 16 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | Qwen3.5-4B | tool cases: handoff | 6 | 83.3% | 83.3% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | Qwen3.5-4B | tool cases: hinglish | 9 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | Qwen3.5-4B | tool cases: refusal | 8 | 87.5% | 87.5% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | Qwen3.5-4B | tool cases: tool_selection | 19 | 84.2% | 57.9% | -26.3 [-47.4, -5.3] | 5 / 0 | 0.062 | ±0.0 | **worse** |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | Qwen3.5-4B | all checked | 60 | 96.7% | 93.3% | -3.3 [-8.3, +0.0] | 2 / 0 | 0.500 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | Qwen3.5-4B | answerable | 60 | 96.7% | 93.3% | -3.3 [-8.3, +0.0] | 2 / 0 | 0.500 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 93.3% | -6.7 [-16.7, +0.0] | 2 / 0 | 0.500 | ±4.9 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | Qwen3.5-4B | all checked | 60 | 96.7% | 95.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | Qwen3.5-4B | answerable | 60 | 96.7% | 95.0% | -1.7 [-5.0, +0.0] | 1 / 0 | 1.000 | ±3.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | Qwen3.5-4B | type: followup_colour | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | 1 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | Qwen3.5-4B | type: followup_fact | 30 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±4.9 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | Qwen3.5-4B | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | Qwen3.5-4B | type: followup_switch | 10 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±8.4 | **tie** |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | Qwen3.5-2B | all checked | 36 | 83.3% | 72.2% | -11.1 [-25.0, +2.8] | 6 / 2 | 0.289 | ±4.4 | **tie** |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | Qwen3.5-2B | answerable | 26 | 84.6% | 69.2% | -15.4 [-30.8, -3.8] | 4 / 0 | 0.125 | ±5.2 | **worse** |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | Qwen3.5-2B | unanswerable / near-miss | 10 | 80.0% | 80.0% | +0.0 [-40.0, +40.0] | 2 / 2 | 1.000 | ±8.4 | **tie** |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | Qwen3.5-2B | tool cases | 30 | 86.7% | 83.3% | -3.3 [-10.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **tie** |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | Qwen3.5-2B | tool cases: comparison | 1 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | Qwen3.5-2B | tool cases: discovery | 8 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | Qwen3.5-2B | tool cases: handoff | 3 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | Qwen3.5-2B | tool cases: hinglish | 4 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | Qwen3.5-2B | tool cases: refusal | 4 | 75.0% | 50.0% | -25.0 [-75.0, +0.0] | 1 / 0 | 1.000 | ±0.0 | **(small)** |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | Qwen3.5-2B | tool cases: tool_selection | 10 | 70.0% | 70.0% | +0.0 [+0.0, +0.0] | 0 / 0 | 1.000 | ±0.0 | **tie** |

## Rounds, reading and wait (same runs; quality runs, not in-place timing)

| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new | Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new | First word p50 base → new |
|---|---|---|---|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 0.93 → 1.14 | 397 → 340 | 130 → 114 | 0 → 9 | 0 → 0 | 27/40 → 39/68 | 5.9 s → 4.1 s |
| o3s12_4b_rag | o3s13a2_4b_rag | 0.93 → 1.15 | 397 → 352 | 130 → 112 | 0 → 9 | 0 → 0 | 27/40 → 39/69 | 5.9 s → 4.7 s |
| o3s12_2b_rag | o3s13a2_2b_rag | 2.20 → 2.01 | 517 → 433 | 83 → 90 | 0 → 1 | 0 → 0 | 28/227 → 29/198 | 6.6 s → 5.8 s |
| o3s12_4b_v12 | o3s13a2_4b_v12 | 0.90 → 0.95 | 243 → 254 | 119 → 122 | 0 → 5 | 0 → 0 | 38/41 → 43/46 | 3.5 s → 4.3 s |
| o3s12_2b_v12 | o3s13a2_2b_v12 | 1.00 → 0.97 | 261 → 244 | 112 → 110 | 0 → 0 | 0 → 0 | 38/55 → 38/47 | 1.4 s → 1.6 s |
| o3s12_4b_fup | o3s13a2_4b_fup | 1.02 → 1.13 | 469 → 379 | 106 → 111 | 0 → 2 | 0 → 0 | 21/21 → 25/28 | 7.4 s → 6.0 s |
| o3s12_2b_fup | o3s13a2_2b_fup | 1.53 → 1.27 | 510 → 381 | 79 → 89 | 0 → 0 | 0 → 0 | 20/52 → 20/36 | 3.3 s → 2.5 s |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | 0.93 → 0.94 | 397 → 326 | 130 → 132 | 0 → 0 | 0 → 0 | 27/40 → 27/41 | 5.9 s → 4.5 s |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | 0.93 → 1.15 | 397 → 351 | 130 → 112 | 0 → 9 | 0 → 0 | 27/40 → 39/69 | 5.9 s → 4.9 s |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | 0.90 → 0.90 | 243 → 243 | 119 → 119 | 0 → 0 | 0 → 0 | 38/41 → 38/41 | 3.5 s → 3.7 s |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | 0.90 → 0.95 | 243 → 254 | 119 → 122 | 0 → 5 | 0 → 0 | 38/41 → 43/46 | 3.5 s → 3.8 s |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | 1.02 → 1.13 | 469 → 374 | 106 → 102 | 0 → 2 | 0 → 0 | 21/21 → 22/28 | 7.4 s → 5.7 s |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | 1.02 → 1.13 | 469 → 379 | 106 → 111 | 0 → 2 | 0 → 0 | 21/21 → 25/28 | 7.4 s → 5.7 s |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | 2.30 → 2.02 | 524 → 427 | 86 → 82 | 0 → 1 | 0 → 0 | 7/64 → 8/53 | 14.3 s → 9.6 s |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | 0.80 → 0.83 | 152 → 159 | 115 → 119 | 0 → 0 | 0 → 0 | 20/20 → 20/21 | 2.8 s → 2.9 s |

## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)

| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |
|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 150 | +0.01 s [-0.04, +0.26] | -0.78 s [-1.47, -0.07] |
| o3s12_4b_rag | o3s13a2_4b_rag | 150 | -0.00 s [-0.14, +0.05] | -0.67 s [-1.52, -0.07] |
| o3s12_2b_rag | o3s13a2_2b_rag | 151 | +0.00 s [-0.07, +0.04] | -0.35 s [-0.71, -0.01] |
| o3s12_4b_v12 | o3s13a2_4b_v12 | 78 | +0.74 s [+0.62, +0.82] | +0.64 s [-0.01, +1.04] |
| o3s12_2b_v12 | o3s13a2_2b_v12 | 77 | +0.15 s [+0.11, +0.19] | +0.01 s [-0.00, +0.13] |
| o3s12_4b_fup | o3s13a2_4b_fup | 60 | +0.06 s [-1.06, +0.27] | -0.18 s [-0.83, +0.24] |
| o3s12_2b_fup | o3s13a2_2b_fup | 60 | -0.29 s [-0.59, +0.19] | -0.73 s [-1.04, -0.19] |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | 151 | +0.03 s [-0.05, +0.31] | -0.06 s [-0.24, +0.02] |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | 150 | +0.01 s [-0.02, +0.49] | -0.66 s [-1.62, -0.12] |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | 78 | +0.21 s [+0.14, +0.25] | -0.16 s [-0.39, -0.02] |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | 78 | +0.15 s [+0.08, +0.22] | -0.35 s [-1.24, -0.06] |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | 60 | -0.01 s [-1.49, +0.29] | -0.36 s [-1.21, +0.03] |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | 60 | -0.22 s [-1.69, +0.08] | -0.77 s [-1.60, -0.40] |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | 40 | -0.91 s [-2.56, -0.01] | -2.12 s [-4.24, -0.70] |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | 30 | +0.00 s [-0.01, +0.02] | -0.70 s [-1.07, -0.03] |

## Printed tool calls and staff discipline (Step 7)

Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known answer where the model itself called staff. Offered, not called: the reply mentions staff and no call_staff was made.

| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls | Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question | Harness call after offer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 0 → 14 | 0 → 9 | 0 → 1 | 0 → 4 | 1 → 7 | 0 → 4 | 27 → 24 | 0 → 0 | 22 → 19 | 0 → 0 |
| o3s12_4b_rag | o3s13a2_4b_rag | 0 → 14 | 0 → 9 | 0 → 1 | 0 → 4 | 1 → 7 | 0 → 4 | 27 → 22 | 0 → 0 | 22 → 19 | 0 → 0 |
| o3s12_2b_rag | o3s13a2_2b_rag | 2 → 3 | 0 → 1 | 1 → 1 | 1 → 1 | 47 → 34 | 24 → 20 | 13 → 11 | 0 → 0 | 10 → 9 | 0 → 0 |
| o3s12_4b_v12 | o3s13a2_4b_v12 | 0 → 6 | 0 → 5 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 | 7 → 6 | 0 → 0 | 4 → 4 | 0 → 0 |
| o3s12_2b_v12 | o3s13a2_2b_v12 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 → 5 | 0 → 0 | 6 → 7 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s12_4b_fup | o3s13a2_4b_fup | 1 → 5 | 0 → 2 | 0 → 0 | 1 → 3 | 0 → 0 | 0 → 0 | 2 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |
| o3s12_2b_fup | o3s13a2_2b_fup | 1 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 1 → 0 | 1 → 0 | 4 → 4 | 0 → 0 | 2 → 1 | 0 → 0 |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 0 | 0 → 0 | 27 → 27 | 0 → 0 | 22 → 22 | 0 → 0 |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | 0 → 14 | 0 → 9 | 0 → 1 | 0 → 4 | 1 → 7 | 0 → 4 | 27 → 22 | 0 → 0 | 22 → 19 | 0 → 0 |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 7 → 7 | 0 → 0 | 4 → 4 | 0 → 0 |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | 0 → 6 | 0 → 5 | 0 → 0 | 0 → 1 | 0 → 0 | 0 → 0 | 7 → 6 | 0 → 0 | 4 → 4 | 0 → 0 |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | 1 → 3 | 0 → 2 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 | 2 → 2 | 0 → 0 | 1 → 1 | 0 → 0 |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | 1 → 5 | 0 → 2 | 0 → 0 | 1 → 3 | 0 → 0 | 0 → 0 | 2 → 1 | 0 → 0 | 1 → 1 | 0 → 0 |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | 0 → 1 | 0 → 1 | 0 → 0 | 0 → 0 | 15 → 11 | 8 → 7 | 4 → 3 | 0 → 0 | 3 → 3 | 0 → 0 |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |

## Fixed replies and the staff check (Step 8)

Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff returned a note; 'then answered' = no staff call followed.

| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |
|---|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 10 → 10 | 8 → 8 | 0 → 5 | 0 → 2 |
| o3s12_4b_rag | o3s13a2_4b_rag | 10 → 10 | 8 → 8 | 0 → 4 | 0 → 1 |
| o3s12_2b_rag | o3s13a2_2b_rag | 10 → 10 | 8 → 8 | 30 → 26 | 4 → 6 |
| o3s12_4b_v12 | o3s13a2_4b_v12 | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o3s12_2b_v12 | o3s13a2_2b_v12 | 1 → 1 | 0 → 0 | 2 → 2 | 1 → 0 |
| o3s12_4b_fup | o3s13a2_4b_fup | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s12_2b_fup | o3s13a2_2b_fup | 0 → 0 | 0 → 0 | 4 → 0 | 3 → 0 |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | 10 → 10 | 8 → 8 | 0 → 0 | 0 → 0 |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | 10 → 10 | 8 → 8 | 0 → 4 | 0 → 1 |
| o3s12_4b_v12 | o3s13x_4b_v12_nolen | 1 → 1 | 0 → 0 | 1 → 1 | 1 → 1 |
| o3s12_4b_v12 | o3s13x_4b_v12_nopar | 1 → 1 | 0 → 0 | 1 → 0 | 1 → 0 |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | 3 → 3 | 2 → 2 | 10 → 8 | 2 → 1 |
| o3s13sp2_a_2b_v12_s12 | o3s13sp2_a_2b_v12_s13a2 | 1 → 1 | 0 → 0 | 0 → 0 | 0 → 0 |

## Unsupported details and the answer check (Step 10)

Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer check swapped for the fixed reply. Cited: replies that ended with card numbers.

| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |
|---|---|---|---|---|
| o3s12_4b_rag | o3s13a_4b_rag | 4/131 (3.1%) → 5/129 (3.9%) | 5 → 3 | 0 → 0 |
| o3s12_4b_rag | o3s13a2_4b_rag | 4/131 (3.1%) → 5/129 (3.9%) | 5 → 3 | 0 → 0 |
| o3s12_2b_rag | o3s13a2_2b_rag | 10/131 (7.6%) → 8/130 (6.2%) | 2 → 0 | 0 → 0 |
| o3s12_4b_fup | o3s13a2_4b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3s12_2b_fup | o3s13a2_2b_fup | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3s12_4b_rag | o3s13x_4b_rag_nolen | 4/131 (3.1%) → 3/131 (2.3%) | 5 → 3 | 0 → 0 |
| o3s12_4b_rag | o3s13x_4b_rag_nopar | 4/131 (3.1%) → 5/129 (3.9%) | 5 → 3 | 0 → 0 |
| o3s12_4b_fup | o3s13x_4b_fup_nolen | 0/40 (0.0%) → 0/38 (0.0%) | 0 → 0 | 0 → 0 |
| o3s12_4b_fup | o3s13x_4b_fup_nopar | 0/40 (0.0%) → 0/40 (0.0%) | 0 → 0 | 0 → 0 |
| o3s13sp2_a_2b_rag_s12 | o3s13sp2_a_2b_rag_s13a2 | 3/35 (8.6%) → 0/34 (0.0%) | 1 → 1 | 0 → 0 |
