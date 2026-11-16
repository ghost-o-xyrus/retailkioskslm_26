# Scores (test split, tools cases)

Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).

| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| s8_4b_v11_none | 234 | **78% [72-83]** | 76% [69-81] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 87% [77-93] (n=75) | 100% [81-100] (n=16) | 96% [82-99] (n=27) | 68% [56-77] (n=77) | 0 |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | 234 | **77% [72-82]** | 75% [68-81] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 89% [80-94] (n=75) | 100% [81-100] (n=16) | 100% [88-100] (n=27) | 64% [52-73] (n=77) | 0 |
| s8_4b_v11_deployed | 234 | **72% [66-77]** | 70% [62-76] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 85% [76-92] (n=75) | 100% [81-100] (n=16) | 96% [82-99] (n=27) | 61% [50-71] (n=77) | 0 |
| qwen35-2b_q8_0_vulkan_v11_greedy | 234 | **69% [63-74]** | 74% [67-80] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 75% [64-83] (n=75) | 94% [72-99] (n=16) | 78% [59-89] (n=27) | 90% [81-95] (n=77) | 0 |
| s8_2b_v11_none | 234 | **69% [63-74]** | 74% [67-80] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 75% [64-83] (n=75) | 94% [72-99] (n=16) | 78% [59-89] (n=27) | 88% [79-94] (n=77) | 0 |
| s8_2b_v11_deployed | 234 | **56% [50-63]** | 78% [71-84] (n=168) | 100% [98-100] (n=234) | 58% [32-81] (n=12) | 76% [65-84] (n=75) | 100% [81-100] (n=16) | 33% [19-52] (n=27) | 55% [43-65] (n=77) | 0 |

## Pass rate by category

| run | comparison (n) | discovery (n) | handoff (n) | hinglish (n) | refusal (n) | tool_selection (n) |
|---|---|---|---|---|---|---|
| qwen35-2b_q8_0_vulkan_v11_greedy | 100% (11) | 74% (47) | 17% (29) | 71% (28) | 81% (27) | 74% (92) |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | 100% (11) | 85% (47) | 59% (29) | 79% (28) | 89% (27) | 73% (92) |
| s8_2b_v11_deployed | 100% (11) | 45% (47) | 28% (29) | 36% (28) | 81% (27) | 65% (92) |
| s8_2b_v11_none | 100% (11) | 72% (47) | 17% (29) | 75% (28) | 81% (27) | 74% (92) |
| s8_4b_v11_deployed | 82% (11) | 74% (47) | 66% (29) | 79% (28) | 81% (27) | 66% (92) |
| s8_4b_v11_none | 100% (11) | 91% (47) | 59% (29) | 75% (28) | 85% (27) | 73% (92) |

## Pairwise differences (same cases)

Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. If the CI includes 0, treat the two as tied.

| A | B | Cases | A − B | 95% CI | McNemar p | Different? |
|---|---|---|---|---|---|---|
| s8_2b_v11_deployed | s8_4b_v11_none | 234 | -21.4 | [-28.2, -14.5] | 0.0 | yes |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | s8_2b_v11_deployed | 234 | +20.9 | [+14.1, +27.4] | 0.0 | yes |
| s8_2b_v11_deployed | s8_4b_v11_deployed | 234 | -15.4 | [-23.1, -8.1] | 0.0002 | yes |
| qwen35-2b_q8_0_vulkan_v11_greedy | s8_2b_v11_deployed | 234 | +12.4 | [+5.6, +19.2] | 0.0008 | yes |
| s8_2b_v11_deployed | s8_2b_v11_none | 234 | -12.4 | [-19.2, -5.6] | 0.0008 | yes |
| qwen35-2b_q8_0_vulkan_v11_greedy | s8_4b_v11_none | 234 | -9.0 | [-15.0, -2.6] | 0.0075 | yes |
| s8_2b_v11_none | s8_4b_v11_none | 234 | -9.0 | [-15.4, -2.6] | 0.0086 | yes |
| qwen35-2b_q8_0_vulkan_v11_greedy | qwen35-4b_q4_k_m_vulkan_v11_greedy | 234 | -8.5 | [-15.0, -2.1] | 0.0135 | yes |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | s8_2b_v11_none | 234 | +8.5 | [+2.1, +15.0] | 0.0135 | yes |
| s8_4b_v11_deployed | s8_4b_v11_none | 234 | -6.0 | [-11.5, -0.9] | 0.0385 | yes |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | s8_4b_v11_deployed | 234 | +5.6 | [+0.4, +11.1] | 0.066 | yes |
| qwen35-2b_q8_0_vulkan_v11_greedy | s8_4b_v11_deployed | 234 | -3.0 | [-9.8, +3.8] | 0.4767 | no (tie) |
| s8_2b_v11_none | s8_4b_v11_deployed | 234 | -3.0 | [-9.8, +3.8] | 0.4767 | no (tie) |
| qwen35-4b_q4_k_m_vulkan_v11_greedy | s8_4b_v11_none | 234 | -0.4 | [-2.6, +1.7] | 1.0 | no (tie) |
| qwen35-2b_q8_0_vulkan_v11_greedy | s8_2b_v11_none | 234 | +0.0 | [-2.1, +2.1] | 1.0 | no (tie) |
