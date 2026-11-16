# Scores (test split)

Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).

| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen35-4b_q4_k_m_vulkan | 106 | **82% [74-88]** | 74% [62-84] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 94% [84-98] (n=52) | 100% [82-100] (n=17) | 100% [65-100] (n=7) | 65% [46-81] (n=26) | 0 |
| qwen35-4b_q8_0_vulkan | 106 | **82% [74-88]** | 74% [62-84] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 94% [84-98] (n=52) | 94% [73-99] (n=17) | 100% [65-100] (n=7) | 65% [46-81] (n=26) | 0 |
| qwen35-2b_q8_0_vulkan | 106 | **75% [65-82]** | 69% [56-79] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 85% [72-92] (n=52) | 94% [73-99] (n=17) | 86% [49-97] (n=7) | 92% [76-98] (n=26) | 0 |
| qwen35-2b_q4_k_m_vulkan | 106 | **70% [61-78]** | 60% [47-72] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 83% [70-91] (n=52) | 94% [73-99] (n=17) | 100% [65-100] (n=7) | 73% [54-86] (n=26) | 0 |
| gemma4-e2b_q8_0_vulkan | 106 | **67% [58-75]** | 66% [53-76] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 79% [66-88] (n=52) | 100% [82-100] (n=17) | 100% [65-100] (n=7) | 62% [43-78] (n=26) | 0 |
| gemma4-e2b_q4_k_m_vulkan | 106 | **60% [51-69]** | 48% [36-61] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 83% [70-91] (n=52) | 100% [82-100] (n=17) | 100% [65-100] (n=7) | 23% [11-42] (n=26) | 0 |

## Pass rate by category

| run | comparison (n) | discovery (n) | grounded_qa (n) | handoff (n) | hinglish (n) | refusal (n) | tool_selection (n) |
|---|---|---|---|---|---|---|---|
| gemma4-e2b_q4_k_m_vulkan | 64% (11) | 47% (17) | 82% (17) | 9% (11) | 36% (11) | 79% (14) | 76% (25) |
| gemma4-e2b_q8_0_vulkan | 73% (11) | 76% (17) | 82% (17) | 9% (11) | 55% (11) | 71% (14) | 76% (25) |
| qwen35-2b_q4_k_m_vulkan | 82% (11) | 82% (17) | 82% (17) | 0% (11) | 45% (11) | 79% (14) | 84% (25) |
| qwen35-2b_q8_0_vulkan | 91% (11) | 82% (17) | 82% (17) | 9% (11) | 73% (11) | 86% (14) | 80% (25) |
| qwen35-4b_q4_k_m_vulkan | 91% (11) | 76% (17) | 94% (17) | 55% (11) | 73% (11) | 100% (14) | 80% (25) |
| qwen35-4b_q8_0_vulkan | 100% (11) | 76% (17) | 94% (17) | 55% (11) | 73% (11) | 86% (14) | 84% (25) |

## Pairwise differences (same cases)

Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. If the CI includes 0, treat the two as tied.

| A | B | Cases | A − B | 95% CI | McNemar p | Different? |
|---|---|---|---|---|---|---|
| gemma4-e2b_q4_k_m_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -21.7 | [-30.2, -13.2] | 0.0 | yes |
| gemma4-e2b_q4_k_m_vulkan | qwen35-4b_q8_0_vulkan | 106 | -21.7 | [-30.2, -13.2] | 0.0 | yes |
| gemma4-e2b_q8_0_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -15.1 | [-22.6, -7.5] | 0.0004 | yes |
| gemma4-e2b_q8_0_vulkan | qwen35-4b_q8_0_vulkan | 106 | -15.1 | [-23.6, -6.6] | 0.0009 | yes |
| gemma4-e2b_q4_k_m_vulkan | qwen35-2b_q8_0_vulkan | 106 | -14.2 | [-23.6, -4.7] | 0.0041 | yes |
| qwen35-2b_q4_k_m_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -12.3 | [-19.8, -5.7] | 0.0023 | yes |
| qwen35-2b_q4_k_m_vulkan | qwen35-4b_q8_0_vulkan | 106 | -12.3 | [-19.8, -4.7] | 0.0044 | yes |
| gemma4-e2b_q4_k_m_vulkan | qwen35-2b_q4_k_m_vulkan | 106 | -9.4 | [-17.9, -0.9] | 0.0525 | yes |
| gemma4-e2b_q8_0_vulkan | qwen35-2b_q8_0_vulkan | 106 | -7.5 | [-17.0, +0.9] | 0.1516 | no (tie) |
| qwen35-2b_q8_0_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -7.5 | [-15.1, +0.0] | 0.0963 | no (tie) |
| qwen35-2b_q8_0_vulkan | qwen35-4b_q8_0_vulkan | 106 | -7.5 | [-15.1, +0.0] | 0.0963 | no (tie) |
| gemma4-e2b_q4_k_m_vulkan | gemma4-e2b_q8_0_vulkan | 106 | -6.6 | [-13.2, +0.0] | 0.0923 | no (tie) |
| qwen35-2b_q4_k_m_vulkan | qwen35-2b_q8_0_vulkan | 106 | -4.7 | [-11.3, +0.9] | 0.2266 | no (tie) |
| gemma4-e2b_q8_0_vulkan | qwen35-2b_q4_k_m_vulkan | 106 | -2.8 | [-11.3, +5.7] | 0.6636 | no (tie) |
| qwen35-4b_q4_k_m_vulkan | qwen35-4b_q8_0_vulkan | 106 | +0.0 | [-3.8, +3.8] | 1.0 | no (tie) |
