# Step 8: end-to-end results on the test retrieval questions

Split: dev. Automatic checks unless marked judged. Hard-fallback rows replace the reply with the fixed message wherever the fallback would refuse.

## Answerable questions

| Run | Model | Condition | Correct (auto-checked) | Refusal candidates (auto) | Judged: unsupported details (random sample) | Judged: false refusals (all answerable) |
|---|---|---|---|---|---|---|
| o3s1_2b_rag_b0 | Qwen3.5-2B | deployed | 57/96 = 59.4% [49.4%-68.7%] | 30/112 = 26.8% [19.5%-35.7%] | - | - |
| o3s1_2b_rag_b0 | Qwen3.5-2B | deployed+hard | 57/96 = 59.4% [49.4%-68.7%] | 32/112 = 28.6% [21.0%-37.5%] | - | - |
| o3s1_2b_rag_oracle | Qwen3.5-2B | oracle | 71/96 = 74.0% [64.4%-81.7%] | 28/112 = 25.0% [17.9%-33.8%] | - | - |
| o3s1_4b_rag_b0 | Qwen3.5-4B | deployed | 81/96 = 84.4% [75.8%-90.3%] | 6/112 = 5.4% [2.5%-11.2%] | - | - |
| o3s1_4b_rag_b0 | Qwen3.5-4B | deployed+hard | 81/96 = 84.4% [75.8%-90.3%] | 8/112 = 7.1% [3.7%-13.5%] | - | - |
| o3s1_4b_rag_oracle | Qwen3.5-4B | oracle | 85/96 = 88.5% [80.6%-93.5%] | 1/112 = 0.9% [0.2%-4.9%] | - | - |

## Unanswerable and near-miss questions

| Run | Condition | Unanswerable: decline phrase (auto) | Unanswerable: hallucinated (judged) | Near miss: expected no/not-listed (auto) | Near miss: hallucinated (judged) | Hinglish unanswerable: hallucinated (judged) |
|---|---|---|---|---|---|---|
| o3s1_2b_rag_b0 | deployed | 9/14 = 64.3% [38.8%-83.7%] | - | 8/25 = 32.0% [17.2%-51.6%] | - | - |
| o3s1_2b_rag_b0 | deployed+hard | 12/14 = 85.7% [60.1%-96.0%] | - | 10/25 = 40.0% [23.4%-59.3%] | - | - |
| o3s1_2b_rag_oracle | oracle | 10/14 = 71.4% [45.4%-88.3%] | - | 5/25 = 20.0% [8.9%-39.1%] | - | - |
| o3s1_4b_rag_b0 | deployed | 12/14 = 85.7% [60.1%-96.0%] | - | 16/25 = 64.0% [44.5%-79.8%] | - | - |
| o3s1_4b_rag_b0 | deployed+hard | 13/14 = 92.9% [68.5%-98.7%] | - | 17/25 = 68.0% [48.4%-82.8%] | - | - |
| o3s1_4b_rag_oracle | oracle | 13/14 = 92.9% [68.5%-98.7%] | - | 21/25 = 84.0% [65.3%-93.6%] | - | - |

## Speed, size and tool use

| Run | First word p50 / p90 s | End to end p50 / p90 s | Retrieval p50 / p90 ms | Context tokens mean | Peak RAM GB server / harness / total | search_knowledge used | Errors |
|---|---|---|---|---|---|---|---|
| o3s1_2b_rag_b0 | 6.8 / 18.5 | 9.5 / 23.9 | 491 / 542 | 305 | 6.17 / 0.35 / 6.52 | - | 0 |
| o3s1_2b_rag_oracle | 4.7 / 14.2 | 6.6 / 19.8 | 0 / 0 | 112 | 3.65 / 0.35 / 4.01 | - | 0 |
| o3s1_4b_rag_b0 | 7.3 / 14.4 | 12.9 / 31.3 | 744 / 854 | 305 | 3.73 / 0.90 / 4.63 | - | 0 |
| o3s1_4b_rag_oracle | 3.1 / 15.2 | 8.8 / 26.4 | 0 / 0 | 112 | 4.80 / 0.41 / 5.18 | - | 0 |

## Paired comparisons (answerable questions with an automatic check)

| Model | A | B | Cases | A - B (points) | 95% CI | McNemar p |
|---|---|---|---|---|---|---|
| Qwen3.5-2B | oracle | deployed | 96 | +14.6 | [+4.2, +25.0] | 0.0125 |
| Qwen3.5-4B | oracle | deployed | 96 | +4.2 | [-3.1, +11.5] | 0.4240 |

Retrieval loss target: oracle - deployed at most 5 points. Judged rates appear once eval\rag_judge labels are passed with --labels.

## Correct by question type (answerable, auto-checked)

| Type | o3s1_2b_rag_b0 | o3s1_2b_rag_oracle | o3s1_4b_rag_b0 | o3s1_4b_rag_oracle |
|---|---|---|---|---|
| collection | 5/8 | 8/8 | 8/8 | 8/8 |
| faq | 6/16 | 6/16 | 11/16 | 15/16 |
| glossary | - | - | - | - |
| hinglish_spec | 5/8 | 8/8 | 7/8 | 6/8 |
| hinglish_text | 2/6 | 4/6 | 1/6 | 4/6 |
| offer | 0/2 | 0/2 | 2/2 | 2/2 |
| policy | 4/7 | 2/7 | 6/7 | 6/7 |
| product_description | 6/10 | 8/10 | 10/10 | 9/10 |
| product_name | 10/12 | 12/12 | 12/12 | 12/12 |
| product_sku | 1/1 | 1/1 | 1/1 | 1/1 |
| product_spec | 12/16 | 15/16 | 16/16 | 14/16 |
| store | 1/2 | 1/2 | 2/2 | 2/2 |
| typo_spec | 5/8 | 6/8 | 5/8 | 6/8 |
