# Scores (test split)

Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).

| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| qwen35-2b_bf16_vulkan_v11_greedy | 292 | **74% [69-79]** | 74% [67-80] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 83% [76-89] (n=133) | 94% [80-98] (n=32) | 78% [59-89] (n=27) | 90% [81-95] (n=77) | 0 |
| qwen35-2b_q8_0_vulkan_v11_greedy | 292 | **74% [68-78]** | 74% [67-80] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 83% [75-88] (n=133) | 94% [80-98] (n=32) | 78% [59-89] (n=27) | 90% [81-95] (n=77) | 0 |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | 292 | **67% [62-73]** | 60% [53-67] (n=168) | 100% [98-100] (n=234) | 100% [76-100] (n=12) | 83% [76-89] (n=133) | 97% [84-99] (n=32) | 89% [72-96] (n=27) | 69% [58-78] (n=77) | 0 |

## Pass rate by category

| run | comparison (n) | discovery (n) | grounded_qa (n) | handoff (n) | hinglish (n) | refusal (n) | tool_selection (n) |
|---|---|---|---|---|---|---|---|
| qwen35-2b_bf16_vulkan_v11_greedy | 95% (21) | 74% (47) | 91% (35) | 21% (29) | 73% (30) | 87% (38) | 75% (92) |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | 90% (21) | 74% (47) | 91% (35) | 3% (29) | 47% (30) | 71% (38) | 75% (92) |
| qwen35-2b_q8_0_vulkan_v11_greedy | 95% (21) | 74% (47) | 91% (35) | 17% (29) | 73% (30) | 87% (38) | 74% (92) |

## Pairwise differences (same cases)

Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. If the CI includes 0, treat the two as tied.

| A | B | Cases | A − B | 95% CI | McNemar p | Different? |
|---|---|---|---|---|---|---|
| qwen35-2b_bf16_vulkan_v11_greedy | qwen35-2b_q4_k_m_vulkan_v11_greedy | 292 | +6.8 | [+2.4, +11.6] | 0.0055 | yes |
| qwen35-2b_q4_k_m_vulkan_v11_greedy | qwen35-2b_q8_0_vulkan_v11_greedy | 292 | -6.2 | [-11.0, -1.4] | 0.0153 | yes |
| qwen35-2b_bf16_vulkan_v11_greedy | qwen35-2b_q8_0_vulkan_v11_greedy | 292 | +0.7 | [-2.1, +3.4] | 0.8036 | no (tie) |
