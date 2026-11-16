# Scores (test split)

Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).

| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen35-4b_q4_k_m_vulkan_v11_greedy | 292 | **81% [76-85]** | 75% [68-81] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 92% [87-96] (n=133) | 100% [89-100] (n=32) | 100% [88-100] (n=27) | 64% [52-73] (n=77) | 0 |
| qwen35-4b_q4_k_m_vulkan_v11_t03 | 292 | **79% [74-83]** | 74% [67-80] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 90% [84-94] (n=133) | 100% [89-100] (n=32) | 96% [82-99] (n=27) | 60% [49-70] (n=77) | 0 |
| qwen35-2b_q8_0_vulkan_v11_greedy | 292 | **74% [68-78]** | 74% [67-80] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 83% [75-88] (n=133) | 94% [80-98] (n=32) | 78% [59-89] (n=27) | 90% [81-95] (n=77) | 0 |
| gemma4-e2b_q8_0_vulkan_v11_greedy | 292 | **70% [64-75]** | 69% [62-76] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 82% [75-88] (n=133) | 100% [89-100] (n=32) | 96% [82-99] (n=27) | 56% [45-66] (n=77) | 0 |
| qwen35-2b_q4_k_m_vulkan_v11_t03 | 292 | **69% [64-74]** | 60% [53-67] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 85% [78-90] (n=133) | 100% [89-100] (n=32) | 93% [77-98] (n=27) | 64% [52-73] (n=77) | 0 |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | 292 | **67% [62-73]** | 60% [53-67] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 83% [76-89] (n=133) | 97% [84-99] (n=32) | 89% [72-96] (n=27) | 69% [58-78] (n=77) | 0 |

| Run | Repeats | Mean pass over repeats | pass^k (all repeats pass) |
|---|---|---|---|
| qwen35-4b_q4_k_m_vulkan_v11_t03 | 3 | 79% | 78% [73-82] |
| qwen35-2b_q4_k_m_vulkan_v11_t03 | 3 | 69% | 69% [63-74] |

## Pass rate by category

| run | comparison (n) | discovery (n) | grounded_qa (n) | handoff (n) | hinglish (n) | refusal (n) | tool_selection (n) |
|---|---|---|---|---|---|---|---|
| gemma4-e2b_q8_0_vulkan_v11_greedy | 81% (21) | 79% (47) | 89% (35) | 21% (29) | 67% (30) | 74% (38) | 70% (92) |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | 90% (21) | 74% (47) | 91% (35) | 3% (29) | 47% (30) | 71% (38) | 75% (92) |
| qwen35-2b_q4_k_m_vulkan_v11_t03 | 95% (21) | 83% (47) | 97% (35) | 3% (29) | 47% (30) | 79% (38) | 70% (92) |
| qwen35-2b_q8_0_vulkan_v11_greedy | 95% (21) | 74% (47) | 91% (35) | 17% (29) | 73% (30) | 87% (38) | 74% (92) |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | 95% (21) | 85% (47) | 97% (35) | 59% (29) | 80% (30) | 92% (38) | 73% (92) |
| qwen35-4b_q4_k_m_vulkan_v11_t03 | 90% (21) | 81% (47) | 97% (35) | 62% (29) | 77% (30) | 92% (38) | 68% (92) |

## Pairwise differences (same cases)

Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. If the CI includes 0, treat the two as tied.

| A | B | Cases | A − B | 95% CI | McNemar p | Different? |
|---|---|---|---|---|---|---|
| qwen35-2b_q4_k_m_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_greedy | 292 | -13.7 | [-18.8, -8.9] | 0.0 | yes |
| qwen35-2b_q4_k_m_vulkan_v11_t03 | qwen35-4b_q4_k_m_vulkan_v11_greedy | 292 | -12.0 | [-17.1, -6.8] | 0.0 | yes |
| gemma4-e2b_q8_0_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_greedy | 292 | -11.6 | [-16.1, -7.2] | 0.0 | yes |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_t03 | 292 | -11.3 | [-16.1, -6.2] | 0.0 | yes |
| qwen35-2b_q4_k_m_vulkan_v11_t03 | qwen35-4b_q4_k_m_vulkan_v11_t03 | 292 | -9.6 | [-15.1, -4.5] | 0.0006 | yes |
| gemma4-e2b_q8_0_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_t03 | 292 | -9.2 | [-14.0, -4.8] | 0.0002 | yes |
| qwen35-2b_q8_0_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_greedy | 292 | -7.5 | [-12.7, -2.4] | 0.0071 | yes |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | qwen35-2b_q8_0_vulkan_v11_greedy | 292 | -6.2 | [-11.0, -1.4] | 0.0153 | yes |
| qwen35-2b_q8_0_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_t03 | 292 | -5.1 | [-10.3, +0.0] | 0.0769 | no (tie) |
| qwen35-2b_q4_k_m_vulkan_v11_t03 | qwen35-2b_q8_0_vulkan_v11_greedy | 292 | -4.5 | [-9.6, +0.3] | 0.1048 | no (tie) |
| gemma4-e2b_q8_0_vulkan_v11_greedy | qwen35-2b_q8_0_vulkan_v11_greedy | 292 | -4.1 | [-9.9, +1.4] | 0.1882 | no (tie) |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_t03 | 292 | +2.4 | [+0.0, +5.1] | 0.1185 | no (tie) |
| gemma4-e2b_q8_0_vulkan_v11_greedy | qwen35-2b_q4_k_m_vulkan_v11_greedy | 292 | +2.1 | [-3.1, +7.2] | 0.519 | no (tie) |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | qwen35-2b_q4_k_m_vulkan_v11_t03 | 292 | -1.7 | [-5.5, +2.1] | 0.4731 | no (tie) |
| gemma4-e2b_q8_0_vulkan_v11_greedy | qwen35-2b_q4_k_m_vulkan_v11_t03 | 292 | +0.3 | [-4.8, +5.5] | 1.0 | no (tie) |
