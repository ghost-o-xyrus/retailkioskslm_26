# Rubric scores (blind LLM judge, test split)

Items: 88 of 88

Mean score 1–5 per case (mean of its rubric lines). Brackets: paired bootstrap 95% CI.

| Run | Mean case score | Cases scoring ≤ 2.5 | Lines scored 1–2 |
|---|---|---|---|
| qwen35-4b_q4_k_m_vulkan_v11_greedy | 4.35 | 3 of 88 | 8% |
| qwen35-2b_q8_0_vulkan_v11_greedy | 4.03 | 11 of 88 | 16% |

**qwen35-4b_q4_k_m_vulkan_v11_greedy − qwen35-2b_q8_0_vulkan_v11_greedy: +0.32 points [+0.05, +0.59]**, Wilcoxon p = 0.0448

Cases where qwen35-4b_q4_k_m_vulkan_v11_greedy scored higher: 44; lower: 22; tied: 22.

## By category

| Category | n | qwen35-4b_q4_k_m_vulkan_v11_greedy | qwen35-2b_q8_0_vulkan_v11_greedy |
|---|---|---|---|
| comparison | 21 | 4.67 | 4.71 |
| discovery | 47 | 4.35 | 3.76 |
| hinglish | 20 | 4.00 | 3.95 |

## By rubric line (most common lines)

| Rubric line | n | qwen35-4b_q4_k_m_vulkan_v11_greedy | qwen35-2b_q8_0_vulkan_v11_greedy |
|---|---|---|---|
| Respects every stated constraint | 40 | 4.05 | 4.05 |
| Gives price and one or two relevant features per watch | 40 | 3.92 | 3.55 |
| Under about 80 words, friendly tone | 40 | 4.17 | 3.90 |
| Recommends only watches returned by the tools | 36 | 4.56 | 4.50 |
| Asks one or two short questions instead of recommending | 27 | 4.00 | 3.22 |
| Questions target missing information that matters (budget, recipient, occasion, strap, size) | 27 | 4.78 | 3.26 |
| Does not name or price specific products yet | 27 | 4.85 | 4.11 |
| Friendly and concise | 27 | 4.04 | 3.56 |
| States correct values for each product | 21 | 4.81 | 4.81 |
| Answers the comparison question directly | 21 | 4.62 | 4.57 |
| Mentions no specs that are not in the provided information | 21 | 4.76 | 4.90 |
| Concise and easy to follow | 21 | 4.48 | 4.57 |

Lines marked not applicable: 4 of 704.
