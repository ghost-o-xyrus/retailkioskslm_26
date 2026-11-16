# Step 15: ablation ladder on the test set O3-T (Kaggle CPU)

Each rung adds the changes kept on dev, in the order they were kept. Cells: pass rate (automatic checks), then in brackets the step from the rung above in points; ▲/▼ = better/worse by compare_dev's rule (beyond the noise bound, bootstrap interval excludes 0), unadjusted and descriptive. Dialogues: fit of shown watches (mean) and share that reached a recommendation.

## Tier A (2B)

| Rung | Store questions | answerable | unanswerable / near-miss | Tool cases | Follow-ups | Dialogues: fit / recommended |
|---|---:|---:|---:|---:|---:|---:|
| O3-B0 | 53.1% | 60.4% | 38.1% | 64.1% | 75.0% | 80% / 95% |
| R1 + tool output v2, loop guard | – | – | – | – | – | – |
| R2 + router | – | – | – | – | – | – |
| R3 + harness tools, discovery, forced answers | – | – | – | – | – | – |
| R4 + fallback, entity and staff checks | – | – | – | – | – | – |
| R5 + answer check, follow-up retrieval | 69.5% | 78.9% | 50.0% | – | – | – |
| R6 = O3-final (speed work) | 68.8% (-0.7) | 76.8% (-2.1) | 52.2% (+2.2) | 76.6% | 86.7% | 97% / 100% |
| O3-final without router | – | – | – | – | – | – |

| Comparison | Set | Cases | Base | New | New − base [95% CI] | McNemar p | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| Whole ladder: O3-final − O3-B0 | Store questions | 423 | 53.0% | 68.8% | +15.8 [+10.9, +20.8] | 1.43e-09 | better |
| Whole ladder: O3-final − O3-B0 | answerable | 285 | 60.4% | 76.8% | +16.5 [+10.5, +22.1] | 9.44e-08 | better |
| Whole ladder: O3-final − O3-B0 | unanswerable / near-miss | 138 | 37.7% | 52.2% | +14.5 [+5.8, +23.9] | 0.00453 | better |
| Whole ladder: O3-final − O3-B0 | Tool cases | 192 | 64.1% | 76.6% | +12.5 [+4.7, +20.3] | 0.00316 | better |
| Whole ladder: O3-final − O3-B0 | Follow-ups | 60 | 75.0% | 86.7% | +11.7 [+1.7, +21.7] | 0.0654 | better |
| Whole ladder: O3-final − O3-B0 | dialogue fit | 60 | – | – | +16.9 [+6.4, +26.9] | – | – |

Reading per rung (same runs; machine-independent counts):

| Rung | Set | Model rounds | Tokens read | Tokens per tool output | Empty replies | Printed tool calls | Calls run by the harness |
|---|---|---:|---:|---:|---:|---:|---|
| O3-B0 | rag | 2.45 | 837 | 220 | 90 | 0 | 0/778 |
| O3-B0 | v12 | 2.77 | 1067 | 305 | 37 | 0 | 0/392 |
| O3-B0 | fup | 1.88 | 733 | 296 | 2 | 0 | 0/55 |
| R5 + answer check, follow-up retrieval | rag | 2.06 | 541 | 94 | 4 | 8 | 95/643 |
| R6 = O3-final (speed work) | rag | 1.85 | 437 | 96 | 5 | 12 | 96/535 |
| R6 = O3-final (speed work) | v12 | 1.06 | 260 | 121 | 0 | 1 | 144/184 |
| R6 = O3-final (speed work) | fup | 1.28 | 402 | 79 | 0 | 2 | 20/37 |

Criteria that need a reference (Kaggle CPU, paired):

| Criterion | Cases | Reference | O3-final | O3-final − reference [95% CI] | Met |
|---|---:|---:|---:|---|---|
| Answerable store questions within 5 points of oracle cards | 285 | 71.2% | 76.8% | +5.6 [-0.4, +11.2] | yes |
| Tool cases not significantly below no retrieval (Stage 3) | 192 | 76.6% | 76.6% | +0.0 [-7.8, +7.8] | yes |

Cross-check against Step 14 (laptop, Vulkan → Kaggle CPU, same configuration):

| Configuration | Set | Cases | Laptop | Kaggle | Kaggle − laptop [95% CI] | Cases that flipped | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| O3-B0 | Store questions | 424 | 51.9% | 53.1% | +1.2 [-1.2, +3.5] | 27 | tie |
| O3-B0 | answerable | 285 | 61.1% | 60.4% | -0.7 [-3.2, +1.8] | 12 | tie |
| O3-B0 | unanswerable / near-miss | 139 | 33.1% | 38.1% | +5.0 [-0.7, +10.8] | 15 | tie |
| O3-B0 | Tool cases | 192 | 62.5% | 64.1% | +1.6 [-1.6, +5.2] | 11 | tie |
| O3-B0 | Follow-ups | 60 | 80.0% | 75.0% | -5.0 [-11.7, +1.7] | 5 | tie |
| O3-B0 | dialogue fit | 60 | 87% | 80% | – | – | – |
| O3-final | Store questions | 423 | 69.5% | 68.8% | -0.7 [-2.8, +1.4] | 21 | tie |
| O3-final | answerable | 285 | 77.2% | 76.8% | -0.4 [-2.8, +2.1] | 13 | tie |
| O3-final | unanswerable / near-miss | 138 | 53.6% | 52.2% | -1.4 [-5.8, +2.2] | 8 | tie |
| O3-final | Tool cases | 192 | 77.6% | 76.6% | -1.0 [-2.6, +0.0] | 2 | tie |
| O3-final | Follow-ups | 60 | 90.0% | 86.7% | -3.3 [-8.3, +0.0] | 2 | tie |
| O3-final | dialogue fit | 60 | 97% | 97% | – | – | – |

## Tier B (4B)

| Rung | Store questions | answerable | unanswerable / near-miss | Tool cases | Follow-ups | Dialogues: fit / recommended |
|---|---:|---:|---:|---:|---:|---:|
| O3-B0 | 79.7% | 83.5% | 71.9% | 79.2% | 66.7% | 60% / 82% |
| R1 + tool output v2, loop guard | – | – | – | – | – | – |
| R2 + router | – | – | – | – | – | – |
| R3 + harness tools, discovery, forced answers | – | – | – | – | – | – |
| R4 + fallback, entity and staff checks | – | – | – | – | – | – |
| R5 + answer check, follow-up retrieval | 82.1% | 83.9% | 78.4% | – | – | – |
| R6 = O3-final (speed work) | 82.3% (+0.2) | 83.9% (+0.0) | 79.1% (+0.7) | 83.9% | 90.0% | 97% / 100% |
| O3-final without router | – | – | – | – | – | – |

| Comparison | Set | Cases | Base | New | New − base [95% CI] | McNemar p | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| Whole ladder: O3-final − O3-B0 | Store questions | 424 | 79.7% | 82.3% | +2.6 [+0.0, +5.2] | 0.0708 | tie |
| Whole ladder: O3-final − O3-B0 | answerable | 285 | 83.5% | 83.9% | +0.4 [-1.8, +2.5] | 1 | tie |
| Whole ladder: O3-final − O3-B0 | unanswerable / near-miss | 139 | 71.9% | 79.1% | +7.2 [+0.7, +13.7] | 0.0414 | better |
| Whole ladder: O3-final − O3-B0 | Tool cases | 192 | 79.2% | 83.9% | +4.7 [-2.6, +12.0] | 0.262 | tie |
| Whole ladder: O3-final − O3-B0 | Follow-ups | 60 | 66.7% | 90.0% | +23.3 [+8.3, +38.3] | 0.00661 | better |
| Whole ladder: O3-final − O3-B0 | dialogue fit | 60 | – | – | +38.2 [+24.3, +52.0] | – | – |

Reading per rung (same runs; machine-independent counts):

| Rung | Set | Model rounds | Tokens read | Tokens per tool output | Empty replies | Printed tool calls | Calls run by the harness |
|---|---|---:|---:|---:|---:|---:|---|
| O3-B0 | rag | 1.24 | 541 | 231 | 6 | 0 | 0/125 |
| O3-B0 | v12 | 1.78 | 747 | 354 | 1 | 0 | 0/153 |
| O3-B0 | fup | 1.25 | 507 | 210 | 1 | 0 | 0/16 |
| R5 + answer check, follow-up retrieval | rag | 0.94 | 420 | 138 | 0 | 0 | 90/125 |
| R6 = O3-final (speed work) | rag | 0.98 | 346 | 135 | 0 | 1 | 90/140 |
| R6 = O3-final (speed work) | v12 | 0.96 | 259 | 135 | 7 | 11 | 155/165 |
| R6 = O3-final (speed work) | fup | 1.03 | 375 | 69 | 0 | 0 | 20/22 |

Criteria that need a reference (Kaggle CPU, paired):

| Criterion | Cases | Reference | O3-final | O3-final − reference [95% CI] | Met |
|---|---:|---:|---:|---|---|
| Answerable store questions within 5 points of oracle cards | 285 | 87.7% | 83.9% | -3.9 [-7.0, -0.7] | yes |
| Tool cases not significantly below no retrieval (Stage 3) | 192 | 88.5% | 83.9% | -4.7 [-10.9, +1.6] | yes |

Cross-check against Step 14 (laptop, Vulkan → Kaggle CPU, same configuration):

| Configuration | Set | Cases | Laptop | Kaggle | Kaggle − laptop [95% CI] | Cases that flipped | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| O3-B0 | Store questions | 424 | 78.3% | 79.7% | +1.4 [-1.4, +4.2] | 38 | tie |
| O3-B0 | answerable | 285 | 80.0% | 83.5% | +3.5 [+0.4, +6.7] | 22 | better |
| O3-B0 | unanswerable / near-miss | 139 | 74.8% | 71.9% | -2.9 [-8.6, +2.9] | 16 | tie |
| O3-B0 | Tool cases | 192 | 78.1% | 79.2% | +1.0 [-2.1, +4.2] | 10 | tie |
| O3-B0 | Follow-ups | 60 | 66.7% | 66.7% | +0.0 [-5.0, +5.0] | 2 | tie |
| O3-B0 | dialogue fit | 60 | 63% | 60% | – | – | – |
| O3-final | Store questions | 424 | 81.4% | 82.3% | +0.9 [-1.2, +3.1] | 20 | tie |
| O3-final | answerable | 285 | 83.2% | 83.9% | +0.7 [-1.4, +2.8] | 10 | tie |
| O3-final | unanswerable / near-miss | 139 | 77.7% | 79.1% | +1.4 [-2.9, +5.8] | 10 | tie |
| O3-final | Tool cases | 192 | 83.3% | 83.9% | +0.5 [-1.0, +2.6] | 3 | tie |
| O3-final | Follow-ups | 60 | 90.0% | 90.0% | +0.0 [+0.0, +0.0] | 0 | tie |
| O3-final | dialogue fit | 60 | 97% | 97% | – | – | – |

## Not yet available

Runs with no results yet (the ladder table fills in as they arrive):

- o3l_nr_2b_fup
- o3l_nr_2b_rag
- o3l_nr_2b_v12
- o3l_nr_4b_fup
- o3l_nr_4b_rag
- o3l_nr_4b_v12
- o3l_r1_2b_fup
- o3l_r1_2b_rag
- o3l_r1_2b_v12
- o3l_r1_4b_fup
- o3l_r1_4b_rag
- o3l_r1_4b_v12
- o3l_r2_2b_fup
- o3l_r2_2b_rag
- o3l_r2_2b_v12
- o3l_r2_4b_fup
- o3l_r2_4b_rag
- o3l_r2_4b_v12
- o3l_r3_2b_fup
- o3l_r3_2b_rag
- o3l_r3_2b_v12
- o3l_r3_4b_fup
- o3l_r3_4b_rag
- o3l_r3_4b_v12
- o3l_r4_2b_fup
- o3l_r4_2b_rag
- o3l_r4_2b_v12
- o3l_r4_4b_fup
- o3l_r4_4b_rag
- o3l_r4_4b_v12
- o3l_r5_2b_fup
- o3l_r5_2b_v12
- o3l_r5_4b_fup
- o3l_r5_4b_v12
