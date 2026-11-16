# Step 15: ablation ladder on the test set O3-T (Kaggle T4 GPU)

Each rung adds the changes kept on dev, in the order they were kept. Cells: pass rate (automatic checks), then in brackets the step from the rung above in points; ▲/▼ = better/worse by compare_dev's rule (beyond the noise bound, bootstrap interval excludes 0), unadjusted and descriptive. Dialogues: fit of shown watches (mean) and share that reached a recommendation.

## Tier A (2B)

| Rung | Store questions | answerable | unanswerable / near-miss | Tool cases | Follow-ups | Dialogues: fit / recommended |
|---|---:|---:|---:|---:|---:|---:|
| O3-B0 | 50.7% | 58.2% | 35.3% | 61.5% | 76.7% | 79% / 93% |
| R1 + tool output v2, loop guard | 63.2% (+12.5 ▲) | 76.8% (+18.6 ▲) | 35.3% (+0.0) | 64.6% (+3.1) | 76.7% (+0.0) | 84% / 100% (+4.8 ▲) |
| R2 + router | 64.4% (+1.2) | 78.9% (+2.1) | 34.5% (-0.7) | 71.4% (+6.8 ▲) | 76.7% (+0.0) | 73% / 92% (-8.9) |
| R3 + harness tools, discovery, forced answers | 67.2% (+2.8 ▲) | 81.1% (+2.1 ▲) | 38.8% (+4.3) | 78.6% (+7.3) | 75.0% (-1.7) | 97% / 100% (+23.7 ▲) |
| R4 + fallback, entity and staff checks | 70.8% (+3.5 ▲) | 81.1% (+0.0) | 49.6% (+10.8 ▲) | 78.6% (+0.0) | 75.0% (+0.0) | 97% / 100% (+0.0) |
| R5 + answer check, follow-up retrieval | 71.0% (+0.2) | 80.4% (-0.7) | 51.8% (+2.2) | 79.2% (+0.5) | 90.0% (+15.0 ▲) | 97% / 100% (+0.0) |
| R6 = O3-final (speed work) | 69.5% (-1.4) | 77.5% (-2.8) | 52.9% (+1.4) | 76.0% (-3.1) | 91.7% (+1.7) | 97% / 100% (+0.0) |
| O3-final without router | 65.4% | 77.0% | 42.4% | 61.4% | 63.3% | 76% / 100% |

| Comparison | Set | Cases | Base | New | New − base [95% CI] | McNemar p | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| Whole ladder: O3-final − O3-B0 | Store questions | 424 | 50.7% | 69.6% | +18.9 [+13.9, +23.6] | 1.66e-13 | better |
| Whole ladder: O3-final − O3-B0 | answerable | 285 | 58.2% | 77.5% | +19.3 [+13.7, +24.9] | 3.81e-10 | better |
| Whole ladder: O3-final − O3-B0 | unanswerable / near-miss | 139 | 35.3% | 53.2% | +18.0 [+9.4, +26.6] | 0.00017 | better |
| Whole ladder: O3-final − O3-B0 | Tool cases | 192 | 61.5% | 76.0% | +14.6 [+6.8, +22.9] | 0.000914 | better |
| Whole ladder: O3-final − O3-B0 | Follow-ups | 60 | 76.7% | 91.7% | +15.0 [+6.7, +25.0] | 0.00391 | better |
| Whole ladder: O3-final − O3-B0 | dialogue fit | 60 | – | – | +17.6 [+7.3, +27.9] | – | – |
| Router's effect: O3-final − without router | Store questions | 413 | 65.4% | 68.8% | +3.4 [+1.0, +6.1] | 0.0161 | better |
| Router's effect: O3-final − without router | answerable | 274 | 77.0% | 76.6% | -0.4 [-2.6, +1.8] | 1 | tie |
| Router's effect: O3-final − without router | unanswerable / near-miss | 139 | 42.4% | 53.2% | +10.8 [+5.0, +16.5] | 0.000729 | better |
| Router's effect: O3-final − without router | Tool cases | 189 | 61.4% | 75.7% | +14.3 [+5.8, +22.2] | 0.00131 | better |
| Router's effect: O3-final − without router | Follow-ups | 60 | 63.3% | 91.7% | +28.3 [+16.7, +40.0] | 1.53e-05 | better |
| Router's effect: O3-final − without router | dialogue fit | 60 | – | – | +21.4 [+12.3, +30.9] | – | – |

Reading per rung (same runs; machine-independent counts):

| Rung | Set | Model rounds | Tokens read | Tokens per tool output | Empty replies | Printed tool calls | Calls run by the harness |
|---|---|---:|---:|---:|---:|---:|---|
| O3-B0 | rag | 2.54 | 852 | 207 | 108 | 0 | 0/842 |
| O3-B0 | v12 | 2.82 | 1066 | 295 | 42 | 0 | 0/408 |
| O3-B0 | fup | 1.90 | 745 | 299 | 3 | 0 | 0/57 |
| R1 + tool output v2, loop guard | rag | 2.33 | 638 | 98 | 39 | 39 | 0/632 |
| R1 + tool output v2, loop guard | v12 | 2.67 | 716 | 124 | 24 | 24 | 0/363 |
| R1 + tool output v2, loop guard | fup | 1.83 | 585 | 147 | 0 | 0 | 0/50 |
| R2 + router | rag | 2.20 | 545 | 108 | 30 | 30 | 0/564 |
| R2 + router | v12 | 2.09 | 286 | 153 | 4 | 4 | 0/220 |
| R2 + router | fup | 1.83 | 585 | 147 | 0 | 0 | 0/50 |
| R3 + harness tools, discovery, forced answers | rag | 2.03 | 553 | 102 | 4 | 8 | 72/564 |
| R3 + harness tools, discovery, forced answers | v12 | 1.04 | 268 | 123 | 0 | 2 | 144/179 |
| R3 + harness tools, discovery, forced answers | fup | 1.83 | 585 | 147 | 0 | 0 | 0/50 |
| R4 + fallback, entity and staff checks | rag | 1.97 | 528 | 94 | 4 | 6 | 94/599 |
| R4 + fallback, entity and staff checks | v12 | 1.07 | 270 | 120 | 0 | 2 | 144/186 |
| R4 + fallback, entity and staff checks | fup | 1.85 | 587 | 144 | 0 | 1 | 0/52 |
| R5 + answer check, follow-up retrieval | rag | 1.97 | 528 | 94 | 4 | 6 | 94/599 |
| R5 + answer check, follow-up retrieval | v12 | 1.07 | 270 | 120 | 0 | 2 | 144/186 |
| R5 + answer check, follow-up retrieval | fup | 1.40 | 510 | 83 | 0 | 2 | 20/44 |
| R6 = O3-final (speed work) | rag | 1.73 | 427 | 101 | 4 | 9 | 92/479 |
| R6 = O3-final (speed work) | v12 | 1.04 | 259 | 123 | 0 | 0 | 144/180 |
| R6 = O3-final (speed work) | fup | 1.20 | 394 | 82 | 0 | 0 | 20/32 |
| O3-final without router | rag | 2.21 | 527 | 98 | 4 | 7 | 3/545 |
| O3-final without router | v12 | 2.60 | 610 | 123 | 5 | 6 | 3/314 |
| O3-final without router | fup | 1.53 | 423 | 133 | 0 | 0 | 0/32 |

Criteria that need a reference (Kaggle CPU, paired):

| Criterion | Cases | Reference | O3-final | O3-final − reference [95% CI] | Met |
|---|---:|---:|---:|---|---|
| Answerable store questions within 5 points of oracle cards | 285 | 71.2% | 76.8% | +5.6 [-0.4, +11.2] | yes |
| Tool cases not significantly below no retrieval (Stage 3) | 192 | 76.6% | 76.6% | +0.0 [-7.8, +7.8] | yes |

Cross-check against Step 14 (laptop, Vulkan → Kaggle CPU, same configuration):

| Configuration | Set | Cases | Laptop | Kaggle | Kaggle − laptop [95% CI] | Cases that flipped | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| O3-B0 | Store questions | 424 | 51.9% | 50.7% | -1.2 [-3.5, +1.2] | 27 | tie |
| O3-B0 | answerable | 285 | 61.1% | 58.2% | -2.8 [-5.6, +0.0] | 16 | tie |
| O3-B0 | unanswerable / near-miss | 139 | 33.1% | 35.3% | +2.2 [-2.2, +6.5] | 11 | tie |
| O3-B0 | Tool cases | 192 | 62.5% | 61.5% | -1.0 [-4.7, +2.1] | 12 | tie |
| O3-B0 | Follow-ups | 60 | 80.0% | 76.7% | -3.3 [-11.7, +5.0] | 6 | tie |
| O3-B0 | dialogue fit | 60 | 87% | 79% | – | – | – |
| O3-final | Store questions | 424 | 69.6% | 69.6% | +0.0 [-2.4, +2.4] | 26 | tie |
| O3-final | answerable | 285 | 77.2% | 77.5% | +0.4 [-2.5, +3.2] | 17 | tie |
| O3-final | unanswerable / near-miss | 139 | 54.0% | 53.2% | -0.7 [-5.0, +3.6] | 9 | tie |
| O3-final | Tool cases | 192 | 77.6% | 76.0% | -1.6 [-4.2, +0.5] | 5 | tie |
| O3-final | Follow-ups | 60 | 90.0% | 91.7% | +1.7 [+0.0, +5.0] | 1 | tie |
| O3-final | dialogue fit | 60 | 97% | 97% | – | – | – |
| O3-B0, Kaggle CPU → GPU | Store questions | 424 | 53.1% | 50.7% | -2.4 [-5.0, +0.0] | 28 | tie |
| O3-B0, Kaggle CPU → GPU | answerable | 285 | 60.4% | 58.2% | -2.1 [-5.3, +0.7] | 18 | tie |
| O3-B0, Kaggle CPU → GPU | unanswerable / near-miss | 139 | 38.1% | 35.3% | -2.9 [-7.2, +1.4] | 10 | tie |
| O3-B0, Kaggle CPU → GPU | Tool cases | 192 | 64.1% | 61.5% | -2.6 [-6.2, +1.0] | 13 | tie |
| O3-B0, Kaggle CPU → GPU | Follow-ups | 60 | 75.0% | 76.7% | +1.7 [-5.0, +8.3] | 5 | tie |
| O3-final, Kaggle CPU → GPU | Store questions | 423 | 68.8% | 69.5% | +0.7 [-1.2, +2.6] | 17 | tie |
| O3-final, Kaggle CPU → GPU | answerable | 285 | 76.8% | 77.5% | +0.7 [-1.4, +2.8] | 10 | tie |
| O3-final, Kaggle CPU → GPU | unanswerable / near-miss | 138 | 52.2% | 52.9% | +0.7 [-2.9, +4.3] | 7 | tie |
| O3-final, Kaggle CPU → GPU | Tool cases | 192 | 76.6% | 76.0% | -0.5 [-2.6, +1.6] | 5 | tie |
| O3-final, Kaggle CPU → GPU | Follow-ups | 60 | 86.7% | 91.7% | +5.0 [+0.0, +11.7] | 3 | tie |

## Tier B (4B)

| Rung | Store questions | answerable | unanswerable / near-miss | Tool cases | Follow-ups | Dialogues: fit / recommended |
|---|---:|---:|---:|---:|---:|---:|
| O3-B0 | 80.4% | 85.3% | 70.5% | 79.7% | 68.3% | 57% / 83% |
| R1 + tool output v2, loop guard | 82.1% (+1.7) | 84.6% (-0.7) | 77.0% (+6.5) | 78.1% (-1.6) | 65.0% (-3.3) | 56% / 73% (-1.7) |
| R2 + router | 82.3% (+0.2) | 84.6% (+0.0) | 77.7% (+0.7) | 86.5% (+8.3 ▲) | 65.0% (+0.0) | 56% / 98% (-1.2) |
| R3 + harness tools, discovery, forced answers | 81.1% (-1.2) | 84.6% (+0.0) | 74.1% (-3.6 ▼) | 83.9% (-2.6) | 66.7% (+1.7) | 97% / 100% (+41.7 ▲) |
| R4 + fallback, entity and staff checks | 82.3% (+1.2) | 83.5% (-1.1) | 79.9% (+5.8 ▲) | 83.9% (+0.0) | 66.7% (+0.0) | 97% / 100% (+0.0) |
| R5 + answer check, follow-up retrieval | 82.5% (+0.2) | 83.5% (+0.0) | 80.6% (+0.7) | 83.3% (-0.5) | 96.7% (+30.0 ▲) | 97% / 100% (+0.0) |
| R6 = O3-final (speed work) | 82.3% (-0.2) | 84.2% (+0.7) | 78.4% (-2.2) | 83.3% (+0.0) | 90.0% (-6.7 ▼) | 97% / 100% (+0.0) |
| O3-final without router | 82.1% | 84.9% | 76.3% | 81.8% | 61.7% | 63% / 82% |

| Comparison | Set | Cases | Base | New | New − base [95% CI] | McNemar p | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| Whole ladder: O3-final − O3-B0 | Store questions | 424 | 80.4% | 82.3% | +1.9 [-0.9, +4.5] | 0.256 | tie |
| Whole ladder: O3-final − O3-B0 | answerable | 285 | 85.3% | 84.2% | -1.1 [-3.5, +1.4] | 0.581 | tie |
| Whole ladder: O3-final − O3-B0 | unanswerable / near-miss | 139 | 70.5% | 78.4% | +7.9 [+0.7, +15.1] | 0.0433 | better |
| Whole ladder: O3-final − O3-B0 | Tool cases | 192 | 79.7% | 83.3% | +3.6 [-3.6, +10.9] | 0.401 | tie |
| Whole ladder: O3-final − O3-B0 | Follow-ups | 60 | 68.3% | 90.0% | +21.7 [+6.7, +36.7] | 0.0106 | better |
| Whole ladder: O3-final − O3-B0 | dialogue fit | 60 | – | – | +41.3 [+27.5, +54.8] | – | – |
| Router's effect: O3-final − without router | Store questions | 424 | 82.1% | 82.3% | +0.2 [-1.7, +2.1] | 1 | tie |
| Router's effect: O3-final − without router | answerable | 285 | 84.9% | 84.2% | -0.7 [-2.1, +0.7] | 0.625 | tie |
| Router's effect: O3-final − without router | unanswerable / near-miss | 139 | 76.3% | 78.4% | +2.2 [-2.2, +7.2] | 0.549 | tie |
| Router's effect: O3-final − without router | Tool cases | 192 | 81.8% | 83.3% | +1.6 [-5.2, +8.3] | 0.766 | tie |
| Router's effect: O3-final − without router | Follow-ups | 60 | 61.7% | 90.0% | +28.3 [+16.7, +40.0] | 7.63e-05 | better |
| Router's effect: O3-final − without router | dialogue fit | 60 | – | – | +34.6 [+21.2, +48.5] | – | – |

Reading per rung (same runs; machine-independent counts):

| Rung | Set | Model rounds | Tokens read | Tokens per tool output | Empty replies | Printed tool calls | Calls run by the harness |
|---|---|---:|---:|---:|---:|---:|---|
| O3-B0 | rag | 1.30 | 563 | 238 | 6 | 0 | 0/164 |
| O3-B0 | v12 | 1.85 | 754 | 327 | 3 | 0 | 0/170 |
| O3-B0 | fup | 1.37 | 549 | 248 | 2 | 0 | 0/24 |
| R1 + tool output v2, loop guard | rag | 1.29 | 516 | 95 | 3 | 3 | 0/153 |
| R1 + tool output v2, loop guard | v12 | 1.90 | 592 | 129 | 5 | 5 | 0/185 |
| R1 + tool output v2, loop guard | fup | 1.35 | 493 | 111 | 2 | 2 | 0/21 |
| R2 + router | rag | 1.37 | 447 | 120 | 2 | 2 | 0/189 |
| R2 + router | v12 | 2.08 | 273 | 138 | 9 | 9 | 0/227 |
| R2 + router | fup | 1.35 | 493 | 111 | 2 | 2 | 0/21 |
| R3 + harness tools, discovery, forced answers | rag | 1.14 | 452 | 119 | 0 | 1 | 68/160 |
| R3 + harness tools, discovery, forced answers | v12 | 0.94 | 261 | 132 | 5 | 10 | 154/160 |
| R3 + harness tools, discovery, forced answers | fup | 1.35 | 493 | 111 | 0 | 1 | 0/21 |
| R4 + fallback, entity and staff checks | rag | 1.02 | 429 | 118 | 0 | 1 | 90/168 |
| R4 + fallback, entity and staff checks | v12 | 0.94 | 261 | 132 | 5 | 10 | 154/160 |
| R4 + fallback, entity and staff checks | fup | 1.33 | 492 | 111 | 0 | 1 | 0/21 |
| R5 + answer check, follow-up retrieval | rag | 1.02 | 429 | 118 | 0 | 1 | 90/168 |
| R5 + answer check, follow-up retrieval | v12 | 0.94 | 261 | 132 | 5 | 10 | 154/160 |
| R5 + answer check, follow-up retrieval | fup | 1.02 | 467 | 71 | 0 | 0 | 20/21 |
| R6 = O3-final (speed work) | rag | 1.07 | 363 | 125 | 0 | 2 | 90/203 |
| R6 = O3-final (speed work) | v12 | 0.95 | 258 | 136 | 6 | 11 | 154/163 |
| R6 = O3-final (speed work) | fup | 1.07 | 377 | 72 | 0 | 1 | 21/24 |
| O3-final without router | rag | 1.35 | 439 | 108 | 0 | 1 | 0/193 |
| O3-final without router | v12 | 1.91 | 522 | 135 | 1 | 2 | 1/185 |
| O3-final without router | fup | 1.40 | 398 | 120 | 0 | 2 | 0/24 |

Criteria that need a reference (Kaggle CPU, paired):

| Criterion | Cases | Reference | O3-final | O3-final − reference [95% CI] | Met |
|---|---:|---:|---:|---|---|
| Answerable store questions within 5 points of oracle cards | 285 | 87.7% | 83.9% | -3.9 [-7.0, -0.7] | yes |
| Tool cases not significantly below no retrieval (Stage 3) | 192 | 88.5% | 83.9% | -4.7 [-10.9, +1.6] | yes |

Cross-check against Step 14 (laptop, Vulkan → Kaggle CPU, same configuration):

| Configuration | Set | Cases | Laptop | Kaggle | Kaggle − laptop [95% CI] | Cases that flipped | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| O3-B0 | Store questions | 424 | 78.3% | 80.4% | +2.1 [-0.7, +5.2] | 41 | tie |
| O3-B0 | answerable | 285 | 80.0% | 85.3% | +5.3 [+2.5, +8.1] | 19 | better |
| O3-B0 | unanswerable / near-miss | 139 | 74.8% | 70.5% | -4.3 [-10.8, +2.2] | 22 | tie |
| O3-B0 | Tool cases | 192 | 78.1% | 79.7% | +1.6 [-2.6, +5.7] | 15 | tie |
| O3-B0 | Follow-ups | 60 | 66.7% | 68.3% | +1.7 [-5.0, +10.0] | 5 | tie |
| O3-B0 | dialogue fit | 60 | 63% | 57% | – | – | – |
| O3-final | Store questions | 424 | 81.4% | 82.3% | +0.9 [-1.4, +3.1] | 24 | tie |
| O3-final | answerable | 285 | 83.2% | 84.2% | +1.1 [-1.1, +3.2] | 9 | tie |
| O3-final | unanswerable / near-miss | 139 | 77.7% | 78.4% | +0.7 [-4.3, +6.5] | 15 | tie |
| O3-final | Tool cases | 192 | 83.3% | 83.3% | +0.0 [-1.6, +1.6] | 2 | tie |
| O3-final | Follow-ups | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 | tie |
| O3-final | dialogue fit | 60 | 97% | 97% | – | – | – |
| O3-B0, Kaggle CPU → GPU | Store questions | 424 | 79.7% | 80.4% | +0.7 [-2.1, +3.8] | 39 | tie |
| O3-B0, Kaggle CPU → GPU | answerable | 285 | 83.5% | 85.3% | +1.8 [-0.7, +4.2] | 13 | tie |
| O3-B0, Kaggle CPU → GPU | unanswerable / near-miss | 139 | 71.9% | 70.5% | -1.4 [-8.6, +5.8] | 26 | tie |
| O3-B0, Kaggle CPU → GPU | Tool cases | 192 | 79.2% | 79.7% | +0.5 [-3.1, +4.2] | 13 | tie |
| O3-B0, Kaggle CPU → GPU | Follow-ups | 60 | 66.7% | 68.3% | +1.7 [-6.7, +10.0] | 7 | tie |
| O3-final, Kaggle CPU → GPU | Store questions | 424 | 82.3% | 82.3% | +0.0 [-2.1, +2.1] | 22 | tie |
| O3-final, Kaggle CPU → GPU | answerable | 285 | 83.9% | 84.2% | +0.4 [-1.1, +1.8] | 5 | tie |
| O3-final, Kaggle CPU → GPU | unanswerable / near-miss | 139 | 79.1% | 78.4% | -0.7 [-6.5, +5.0] | 17 | tie |
| O3-final, Kaggle CPU → GPU | Tool cases | 192 | 83.9% | 83.3% | -0.5 [-2.1, +1.0] | 3 | tie |
| O3-final, Kaggle CPU → GPU | Follow-ups | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 | tie |

