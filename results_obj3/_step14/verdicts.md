# Step 14: confirming run on O3-T (pre-registered rules)

## Primary sets (Holm-adjusted across 6 tests)

| Tier | Set | Cases | O3-B0 | O3-final | Difference [95% CI] | McNemar p | Holm p | Verdict |
|---|---|---:|---:|---:|---|---:|---:|---|
| A | store questions | 424 | 51.9% | 69.6% | +17.7 [+12.7, +22.6] | 1.99e-12 | 1.2e-11 | **better** |
| A | tool cases | 192 | 62.5% | 77.6% | +15.1 [+7.3, +22.9] | 0.000337 | 0.00168 | **better** |
| A | follow-ups | 60 | 80.0% | 90.0% | +10.0 [+0.0, +20.0] | 0.109 | 0.276 | **tie** |
| B | store questions | 424 | 78.3% | 81.4% | +3.1 [-0.2, +6.4] | 0.0919 | 0.276 | **tie** |
| B | tool cases | 192 | 78.1% | 83.3% | +5.2 [-2.1, +12.5] | 0.22 | 0.276 | **tie** |
| B | follow-ups | 60 | 66.7% | 90.0% | +23.3 [+8.3, +38.3] | 0.00661 | 0.0264 | **better** |

## Dialogues (60 fresh profiles)

| Tier | Run | Recommended | ≥2 slots known | Questions max | Fit (mean) | Fit vs O3-B0 [95% CI] | Targets |
|---|---|---:|---:|---:|---:|---|---|
| A | O3-B0 | 97% | 34% | 1 | 87% |  |  |
| A | O3-final | 100% | 100% | 2 | 97% | +10.6 [+1.9, +20.4] | met |
| B | O3-B0 | 85% | 84% | 3 | 63% |  |  |
| B | O3-final | 100% | 100% | 2 | 97% | +34.0 [+21.0, +47.5] | met |

## Tier A in place (2B on CPU, test speed subset, 2 repeats)

| Set | Cases | First word change s [95% CI] | Total reply time change s [95% CI] | Rule |
|---|---:|---|---|---|
| store questions | 40 | -3.86 [-12.69, -1.31] | -4.42 [-10.73, -2.92] | met |
| tool cases | 30 | -19.14 [-24.67, -13.56] | -22.27 [-29.71, -17.52] | met |

## Verdicts

- Tier A: **not confirmed** (store questions: better, tool cases: better, follow-ups: tie, dialogues: met, timing: met)
- Tier B: **confirmed** (store questions: tie, tool cases: tie, follow-ups: better, dialogues: met)

## Reported, not used to decide

| Base | New | Subset | Cases | Base | New | Difference [95% CI] | Verdict (unadjusted) |
|---|---|---|---:|---:|---:|---|---|
| o3t_b0_4b_rag | o3t_final_4b_rag | answerable | 285 | 80.0% | 83.2% | +3.2 [+0.0, +6.7] | tie |
| o3t_b0_4b_rag | o3t_final_4b_rag | unanswerable / near-miss | 139 | 74.8% | 77.7% | +2.9 [-4.3, +10.1] | tie |
| o3t_b0_4b_rag | o3t_final_4b_rag | language: hinglish | 62 | 58.1% | 54.8% | -3.2 [-12.9, +6.5] | tie |
| o3t_b0_4b_rag | o3t_final_4b_rag | origin: fresh | 290 | 80.3% | 86.2% | +5.9 [+1.7, +10.0] | better |
| o3t_b0_4b_rag | o3t_final_4b_rag | origin: held-out | 134 | 73.9% | 70.9% | -3.0 [-8.2, +2.2] | tie |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | language: hinglish | 37 | 83.8% | 81.1% | -2.7 [-18.9, +13.5] | tie |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | origin: fresh | 117 | 81.2% | 85.5% | +4.3 [-4.3, +12.8] | tie |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | origin: held-out | 75 | 73.3% | 80.0% | +6.7 [-8.0, +20.0] | tie |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | tool cases: comparison | 13 | 76.9% | 100.0% | +23.1 [+0.0, +46.2] | tie |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | tool cases: discovery | 47 | 70.2% | 80.9% | +10.6 [-6.4, +27.7] | tie |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | tool cases: handoff | 14 | 92.9% | 64.3% | -28.6 [-57.1, -7.1] | worse |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | tool cases: hinglish | 36 | 83.3% | 80.6% | -2.8 [-19.4, +13.9] | tie |
| o3t_b0_4b_v12 | o3t_final_4b_v12 | tool cases: tool_selection | 73 | 78.1% | 89.0% | +11.0 [+1.4, +21.9] | better |
| o3t_b0_4b_fup | o3t_final_4b_fup | answerable | 60 | 66.7% | 90.0% | +23.3 [+8.3, +38.3] | better |
| o3t_b0_4b_fup | o3t_final_4b_fup | language: hinglish | 26 | 61.5% | 76.9% | +15.4 [-11.5, +42.3] | tie |
| o3t_b0_4b_fup | o3t_final_4b_fup | type: followup_colour | 10 | 40.0% | 100.0% | +60.0 [+30.0, +90.0] | better |
| o3t_b0_4b_fup | o3t_final_4b_fup | type: followup_fact | 30 | 56.7% | 100.0% | +43.3 [+26.7, +60.0] | better |
| o3t_b0_4b_fup | o3t_final_4b_fup | type: followup_stock | 10 | 90.0% | 80.0% | -10.0 [-30.0, +0.0] | tie |
| o3t_b0_4b_fup | o3t_final_4b_fup | type: followup_switch | 10 | 100.0% | 60.0% | -40.0 [-70.0, -10.0] | worse |
| o3t_b0_2b_rag | o3t_final_2b_rag | answerable | 285 | 61.1% | 77.2% | +16.1 [+10.5, +21.8] | better |
| o3t_b0_2b_rag | o3t_final_2b_rag | unanswerable / near-miss | 139 | 33.1% | 54.0% | +20.9 [+12.9, +28.8] | better |
| o3t_b0_2b_rag | o3t_final_2b_rag | language: hinglish | 62 | 50.0% | 50.0% | +0.0 [-8.1, +8.1] | tie |
| o3t_b0_2b_rag | o3t_final_2b_rag | origin: fresh | 290 | 56.2% | 75.9% | +19.7 [+13.8, +25.2] | better |
| o3t_b0_2b_rag | o3t_final_2b_rag | origin: held-out | 134 | 42.5% | 56.0% | +13.4 [+5.2, +21.6] | better |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | language: hinglish | 37 | 45.9% | 83.8% | +37.8 [+18.9, +56.8] | better |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | origin: fresh | 117 | 75.2% | 74.4% | -0.9 [-8.5, +6.8] | tie |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | origin: held-out | 75 | 42.7% | 82.7% | +40.0 [+25.3, +53.3] | better |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | tool cases: comparison | 13 | 92.3% | 100.0% | +7.7 [+0.0, +23.1] | tie |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | tool cases: discovery | 47 | 46.8% | 83.0% | +36.2 [+17.0, +55.3] | better |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | tool cases: handoff | 14 | 50.0% | 64.3% | +14.3 [-14.3, +42.9] | tie |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | tool cases: hinglish | 36 | 47.2% | 83.3% | +36.1 [+16.7, +55.6] | better |
| o3t_b0_2b_v12 | o3t_final_2b_v12 | tool cases: tool_selection | 73 | 76.7% | 71.2% | -5.5 [-15.1, +2.7] | tie |
| o3t_b0_2b_fup | o3t_final_2b_fup | answerable | 60 | 80.0% | 90.0% | +10.0 [+0.0, +20.0] | tie |
| o3t_b0_2b_fup | o3t_final_2b_fup | language: hinglish | 26 | 65.4% | 80.8% | +15.4 [+0.0, +34.6] | tie |
| o3t_b0_2b_fup | o3t_final_2b_fup | type: followup_colour | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o3t_b0_2b_fup | o3t_final_2b_fup | type: followup_fact | 30 | 80.0% | 96.7% | +16.7 [+3.3, +30.0] | better |
| o3t_b0_2b_fup | o3t_final_2b_fup | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o3t_b0_2b_fup | o3t_final_2b_fup | type: followup_switch | 10 | 40.0% | 50.0% | +10.0 [-30.0, +50.0] | tie |
| o3t_final_2b_rag | o3t_final12_2b_rag | all checked | 424 | 69.6% | 73.8% | +4.2 [+1.2, +7.5] | better |
| o3t_final_2b_rag | o3t_final12_2b_rag | answerable | 285 | 77.2% | 80.7% | +3.5 [+0.4, +6.7] | better |
| o3t_final_2b_rag | o3t_final12_2b_rag | unanswerable / near-miss | 139 | 54.0% | 59.7% | +5.8 [-1.4, +13.7] | tie |
| o3t_final_2b_rag | o3t_final12_2b_rag | language: hinglish | 62 | 50.0% | 53.2% | +3.2 [-4.8, +11.3] | tie |
| o3t_final_2b_rag | o3t_final12_2b_rag | origin: fresh | 290 | 75.9% | 81.7% | +5.9 [+2.1, +10.0] | better |
| o3t_final_2b_rag | o3t_final12_2b_rag | origin: held-out | 134 | 56.0% | 56.7% | +0.7 [-4.5, +6.0] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | tool cases | 192 | 77.6% | 76.0% | -1.6 [-4.7, +1.6] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | language: hinglish | 37 | 83.8% | 81.1% | -2.7 [-8.1, +0.0] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | origin: fresh | 117 | 74.4% | 74.4% | +0.0 [-4.3, +4.3] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | origin: held-out | 75 | 82.7% | 78.7% | -4.0 [-9.3, +0.0] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | tool cases: comparison | 13 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | tool cases: discovery | 47 | 83.0% | 78.7% | -4.3 [-10.6, +0.0] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | tool cases: handoff | 14 | 64.3% | 64.3% | +0.0 [+0.0, +0.0] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | tool cases: hinglish | 36 | 83.3% | 80.6% | -2.8 [-8.3, +0.0] | tie |
| o3t_final_2b_v12 | o3t_final12_2b_v12 | tool cases: tool_selection | 73 | 71.2% | 71.2% | +0.0 [-5.5, +5.5] | tie |
| o3t_final_2b_fup | o3t_final12_2b_fup | all checked | 60 | 90.0% | 90.0% | +0.0 [-5.0, +5.0] | tie |
| o3t_final_2b_fup | o3t_final12_2b_fup | answerable | 60 | 90.0% | 90.0% | +0.0 [-5.0, +5.0] | tie |
| o3t_final_2b_fup | o3t_final12_2b_fup | language: hinglish | 26 | 80.8% | 80.8% | +0.0 [+0.0, +0.0] | tie |
| o3t_final_2b_fup | o3t_final12_2b_fup | type: followup_colour | 10 | 100.0% | 90.0% | -10.0 [-30.0, +0.0] | tie |
| o3t_final_2b_fup | o3t_final12_2b_fup | type: followup_fact | 30 | 96.7% | 96.7% | +0.0 [+0.0, +0.0] | tie |
| o3t_final_2b_fup | o3t_final12_2b_fup | type: followup_stock | 10 | 100.0% | 100.0% | +0.0 [+0.0, +0.0] | tie |
| o3t_final_2b_fup | o3t_final12_2b_fup | type: followup_switch | 10 | 50.0% | 60.0% | +10.0 [+0.0, +30.0] | tie |
