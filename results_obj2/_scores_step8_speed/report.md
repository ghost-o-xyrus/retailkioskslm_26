# Step 8: end-to-end results on the test retrieval questions

Split: test. Automatic checks unless marked judged. Hard-fallback rows replace the reply with the fixed message wherever the fallback would refuse.

## Answerable questions

| Run | Model | Condition | Correct (auto-checked) | Refusal candidates (auto) | Judged: unsupported details (random sample) | Judged: false refusals (all answerable) |
|---|---|---|---|---|---|---|
| s8sp_2b_cpu_rag_deployed | Qwen3.5-2B | deployed | 14/22 = 63.6% [43.0%-80.3%] | 5/26 = 19.2% [8.5%-37.9%] | - | - |
| s8sp_2b_cpu_rag_deployed | Qwen3.5-2B | deployed+hard | 14/22 = 63.6% [43.0%-80.3%] | 6/26 = 23.1% [11.0%-42.1%] | - | - |
| s8sp_2b_cpu_rag_none | Qwen3.5-2B | none | 9/22 = 40.9% [23.3%-61.3%] | 2/26 = 7.7% [2.1%-24.1%] | - | - |

## Unanswerable and near-miss questions

| Run | Condition | Unanswerable: decline phrase (auto) | Unanswerable: hallucinated (judged) | Near miss: expected no/not-listed (auto) | Near miss: hallucinated (judged) | Hinglish unanswerable: hallucinated (judged) |
|---|---|---|---|---|---|---|
| s8sp_2b_cpu_rag_deployed | deployed | 6/7 = 85.7% [48.7%-97.4%] | - | 2/7 = 28.6% [8.2%-64.1%] | - | - |
| s8sp_2b_cpu_rag_deployed | deployed+hard | 6/7 = 85.7% [48.7%-97.4%] | - | 3/7 = 42.9% [15.8%-75.0%] | - | - |
| s8sp_2b_cpu_rag_none | none | 5/7 = 71.4% [35.9%-91.8%] | - | 1/7 = 14.3% [2.6%-51.3%] | - | - |

## Speed, size and tool use

| Run | First word p50 / p90 s | End to end p50 / p90 s | Retrieval p50 / p90 ms | Context tokens mean | Peak RAM GB server / harness / total | search_knowledge used | Errors |
|---|---|---|---|---|---|---|---|
| s8sp_2b_cpu_rag_deployed | 12.5 / 24.6 | 14.1 / 26.7 | 641 / 745 | 264 | 2.89 / 0.93 / 3.80 | - | 0 |
| s8sp_2b_cpu_rag_none | 0.6 / 21.2 | 3.0 / 24.5 | - / - | - | 2.34 / 0.05 / 2.39 | - | 0 |

## Paired comparisons (answerable questions with an automatic check)

| Model | A | B | Cases | A - B (points) | 95% CI | McNemar p |
|---|---|---|---|---|---|---|
| Qwen3.5-2B | deployed | none | 22 | +22.7 | [+0.0, +45.5] | 0.1250 |

Retrieval loss target: oracle - deployed at most 5 points. Judged rates appear once eval\rag_judge labels are passed with --labels.

## Correct by question type (answerable, auto-checked)

| Type | s8sp_2b_cpu_rag_deployed | s8sp_2b_cpu_rag_none |
|---|---|---|
| collection | - | - |
| faq | 2/5 | 1/5 |
| glossary | - | - |
| hinglish_spec | 3/3 | 1/3 |
| hinglish_text | 1/3 | 0/3 |
| offer | - | - |
| policy | - | - |
| product_description | - | - |
| product_name | 0/1 | 1/1 |
| product_sku | 1/1 | 1/1 |
| product_spec | 6/7 | 5/7 |
| store | - | - |
| typo_spec | 1/2 | 0/2 |
