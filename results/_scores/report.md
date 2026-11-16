# Scores (test split)

Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).

| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen35-4b_q4_k_m_vulkan | 106 | **82% [74-88]** | 74% [62-84] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 94% [84-98] (n=52) | 100% [82-100] (n=17) | 100% [65-100] (n=7) | 65% [46-81] (n=26) | 0 |
| qwen35-2b_q4_k_m_vulkan | 106 | **70% [61-78]** | 60% [47-72] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 83% [70-91] (n=52) | 94% [73-99] (n=17) | 100% [65-100] (n=7) | 73% [54-86] (n=26) | 0 |
| gemma4-e2b_q4_k_m_vulkan | 106 | **60% [51-69]** | 48% [36-61] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 83% [70-91] (n=52) | 100% [82-100] (n=17) | 100% [65-100] (n=7) | 23% [11-42] (n=26) | 0 |
| qwen35-0.8b_q4_k_m_vulkan | 106 | **45% [36-55]** | 22% [14-35] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 77% [64-86] (n=52) | 94% [73-99] (n=17) | 71% [36-92] (n=7) | 12% [4-29] (n=26) | 0 |
| llama32-3b_q4_k_m_vulkan | 106 | **36% [27-45]** | 64% [51-75] (n=58) | 100% [95-100] (n=77) | 0% [0-56] (n=3) | 44% [32-58] (n=52) | 100% [82-100] (n=17) | 29% [8-64] (n=7) | 4% [1-19] (n=26) | 0 |
| phi4-mini_q4_k_m_vulkan | 106 | **36% [27-45]** | 0% [0-6] (n=58) | 100% [95-100] (n=77) | 100% [44-100] (n=3) | 65% [52-77] (n=52) | 94% [73-99] (n=17) | 71% [36-92] (n=7) | 0% [0-13] (n=26) | 0 |

## Pass rate by category

| run | comparison (n) | discovery (n) | grounded_qa (n) | handoff (n) | hinglish (n) | refusal (n) | tool_selection (n) |
|---|---|---|---|---|---|---|---|
| gemma4-e2b_q4_k_m_vulkan | 64% (11) | 47% (17) | 82% (17) | 9% (11) | 36% (11) | 79% (14) | 76% (25) |
| llama32-3b_q4_k_m_vulkan | 27% (11) | 18% (17) | 76% (17) | 73% (11) | 27% (11) | 43% (14) | 8% (25) |
| phi4-mini_q4_k_m_vulkan | 27% (11) | 29% (17) | 76% (17) | 0% (11) | 18% (11) | 86% (14) | 12% (25) |
| qwen35-0.8b_q4_k_m_vulkan | 55% (11) | 35% (17) | 71% (17) | 9% (11) | 27% (11) | 86% (14) | 32% (25) |
| qwen35-2b_q4_k_m_vulkan | 82% (11) | 82% (17) | 82% (17) | 0% (11) | 45% (11) | 79% (14) | 84% (25) |
| qwen35-4b_q4_k_m_vulkan | 91% (11) | 76% (17) | 94% (17) | 55% (11) | 73% (11) | 100% (14) | 80% (25) |

## Pairwise differences (same cases)

Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. If the CI includes 0, treat the two as tied.

| A | B | Cases | A − B | 95% CI | McNemar p | Different? |
|---|---|---|---|---|---|---|
| llama32-3b_q4_k_m_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -46.2 | [-57.5, -34.9] | 0.0 | yes |
| phi4-mini_q4_k_m_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -46.2 | [-55.7, -36.8] | 0.0 | yes |
| qwen35-0.8b_q4_k_m_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -36.8 | [-46.2, -27.4] | 0.0 | yes |
| llama32-3b_q4_k_m_vulkan | qwen35-2b_q4_k_m_vulkan | 106 | -34.0 | [-46.2, -21.7] | 0.0 | yes |
| phi4-mini_q4_k_m_vulkan | qwen35-2b_q4_k_m_vulkan | 106 | -34.0 | [-45.3, -23.6] | 0.0 | yes |
| gemma4-e2b_q4_k_m_vulkan | llama32-3b_q4_k_m_vulkan | 106 | +24.5 | [+12.3, +36.8] | 0.0002 | yes |
| gemma4-e2b_q4_k_m_vulkan | phi4-mini_q4_k_m_vulkan | 106 | +24.5 | [+15.1, +34.0] | 0.0 | yes |
| qwen35-0.8b_q4_k_m_vulkan | qwen35-2b_q4_k_m_vulkan | 106 | -24.5 | [-34.9, -15.1] | 0.0 | yes |
| gemma4-e2b_q4_k_m_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -21.7 | [-30.2, -13.2] | 0.0 | yes |
| gemma4-e2b_q4_k_m_vulkan | qwen35-0.8b_q4_k_m_vulkan | 106 | +15.1 | [+5.7, +24.5] | 0.0052 | yes |
| qwen35-2b_q4_k_m_vulkan | qwen35-4b_q4_k_m_vulkan | 106 | -12.3 | [-19.8, -5.7] | 0.0023 | yes |
| gemma4-e2b_q4_k_m_vulkan | qwen35-2b_q4_k_m_vulkan | 106 | -9.4 | [-17.9, -0.9] | 0.0525 | yes |
| llama32-3b_q4_k_m_vulkan | qwen35-0.8b_q4_k_m_vulkan | 106 | -9.4 | [-20.8, +2.8] | 0.1641 | no (tie) |
| phi4-mini_q4_k_m_vulkan | qwen35-0.8b_q4_k_m_vulkan | 106 | -9.4 | [-17.0, -1.9] | 0.0309 | yes |
| llama32-3b_q4_k_m_vulkan | phi4-mini_q4_k_m_vulkan | 106 | +0.0 | [-10.4, +10.4] | 1.0 | no (tie) |
