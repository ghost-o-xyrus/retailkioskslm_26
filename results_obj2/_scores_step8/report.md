# Step 8: end-to-end results on the test retrieval questions

Split: test. Automatic checks unless marked judged. Hard-fallback rows replace the reply with the fixed message wherever the fallback would refuse.

## Answerable questions

| Run | Model | Condition | Correct (auto-checked) | Refusal candidates (auto) | Judged: unsupported details (random sample) | Judged: false refusals (all answerable) |
|---|---|---|---|---|---|---|
| s8_2b_rag_deployed | Qwen3.5-2B | deployed | 123/222 = 55.4% [48.8%-61.8%] | 68/258 = 26.4% [21.4%-32.1%] | 5/60 = 8.3% [3.6%-18.1%] | 69/258 = 26.7% [21.7%-32.5%] |
| s8_2b_rag_deployed | Qwen3.5-2B | deployed+hard | 120/222 = 54.1% [47.5%-60.5%] | 76/258 = 29.5% [24.2%-35.3%] | 5/60 = 8.3% [3.6%-18.1%] | 74/258 = 28.7% [23.5%-34.5%] |
| s8_2b_rag_nofallback | Qwen3.5-2B | nofallback | 128/222 = 57.7% [51.1%-64.0%] | 68/258 = 26.4% [21.4%-32.1%] | - | - |
| s8_2b_rag_nofallback | Qwen3.5-2B | nofallback+hard | 122/222 = 55.0% [48.4%-61.4%] | 74/258 = 28.7% [23.5%-34.5%] | - | - |
| s8_2b_rag_none | Qwen3.5-2B | none | 89/222 = 40.1% [33.9%-46.7%] | 35/258 = 13.6% [9.9%-18.3%] | - | - |
| s8_2b_rag_oracle | Qwen3.5-2B | oracle | 153/222 = 68.9% [62.6%-74.6%] | 52/258 = 20.2% [15.7%-25.5%] | - | - |
| s8_2b_rag_tool | Qwen3.5-2B | tool | 111/222 = 50.0% [43.5%-56.5%] | 18/258 = 7.0% [4.5%-10.8%] | - | - |
| s8_4b_rag_deployed | Qwen3.5-4B | deployed | 173/222 = 77.9% [72.0%-82.9%] | 27/258 = 10.5% [7.3%-14.8%] | 4/60 = 6.7% [2.6%-15.9%] | 14/258 = 5.4% [3.3%-8.9%] |
| s8_4b_rag_deployed | Qwen3.5-4B | deployed+hard | 171/222 = 77.0% [71.1%-82.1%] | 31/258 = 12.0% [8.6%-16.6%] | 4/60 = 6.7% [2.6%-15.9%] | 20/258 = 7.8% [5.1%-11.7%] |
| s8_4b_rag_nofallback | Qwen3.5-4B | nofallback | 178/222 = 80.2% [74.4%-84.9%] | 22/258 = 8.5% [5.7%-12.6%] | - | - |
| s8_4b_rag_nofallback | Qwen3.5-4B | nofallback+hard | 171/222 = 77.0% [71.1%-82.1%] | 31/258 = 12.0% [8.6%-16.6%] | - | - |
| s8_4b_rag_none | Qwen3.5-4B | none | 111/222 = 50.0% [43.5%-56.5%] | 52/258 = 20.2% [15.7%-25.5%] | - | - |
| s8_4b_rag_oracle | Qwen3.5-4B | oracle | 182/222 = 82.0% [76.4%-86.5%] | 12/258 = 4.7% [2.7%-8.0%] | - | - |
| s8_4b_rag_tool | Qwen3.5-4B | tool | 141/222 = 63.5% [57.0%-69.6%] | 26/258 = 10.1% [7.0%-14.4%] | - | - |

## Unanswerable and near-miss questions

| Run | Condition | Unanswerable: decline phrase (auto) | Unanswerable: hallucinated (judged) | Near miss: expected no/not-listed (auto) | Near miss: hallucinated (judged) | Hinglish unanswerable: hallucinated (judged) |
|---|---|---|---|---|---|---|
| s8_2b_rag_deployed | deployed | 32/57 = 56.1% [43.3%-68.2%] | 13/57 = 22.8% [13.8%-35.2%] | 15/58 = 25.9% [16.3%-38.4%] | 28/58 = 48.3% [35.9%-60.8%] | 6/24 = 25.0% [12.0%-44.9%] |
| s8_2b_rag_deployed | deployed+hard | 38/57 = 66.7% [53.7%-77.5%] | 7/57 = 12.3% [6.1%-23.2%] | 24/58 = 41.4% [29.6%-54.2%] | 20/58 = 34.5% [23.6%-47.3%] | 6/24 = 25.0% [12.0%-44.9%] |
| s8_2b_rag_nofallback | nofallback | 30/57 = 52.6% [39.9%-65.0%] | 12/57 = 21.1% [12.5%-33.3%] | 12/58 = 20.7% [12.3%-32.8%] | 20/58 = 34.5% [23.6%-47.3%] | 7/24 = 29.2% [14.9%-49.2%] |
| s8_2b_rag_nofallback | nofallback+hard | 36/57 = 63.2% [50.2%-74.5%] | 9/57 = 15.8% [8.5%-27.4%] | 23/58 = 39.7% [28.1%-52.5%] | 18/58 = 31.0% [20.6%-43.8%] | 7/24 = 29.2% [14.9%-49.2%] |
| s8_2b_rag_none | none | 24/57 = 42.1% [30.2%-55.0%] | 23/57 = 40.4% [28.6%-53.3%] | 8/58 = 13.8% [7.2%-24.9%] | 41/58 = 70.7% [58.0%-80.8%] | 17/24 = 70.8% [50.8%-85.1%] |
| s8_2b_rag_oracle | oracle | 27/57 = 47.4% [35.0%-60.1%] | - | 15/58 = 25.9% [16.3%-38.4%] | - | - |
| s8_2b_rag_tool | tool | 18/57 = 31.6% [21.0%-44.5%] | - | 9/58 = 15.5% [8.4%-26.9%] | - | - |
| s8_4b_rag_deployed | deployed | 45/57 = 78.9% [66.7%-87.5%] | 11/57 = 19.3% [11.1%-31.3%] | 35/58 = 60.3% [47.5%-71.9%] | 13/58 = 22.4% [13.6%-34.7%] | 6/24 = 25.0% [12.0%-44.9%] |
| s8_4b_rag_deployed | deployed+hard | 46/57 = 80.7% [68.7%-88.9%] | 9/57 = 15.8% [8.5%-27.4%] | 45/58 = 77.6% [65.3%-86.4%] | 10/58 = 17.2% [9.6%-28.9%] | 6/24 = 25.0% [12.0%-44.9%] |
| s8_4b_rag_nofallback | nofallback | 47/57 = 82.5% [70.6%-90.2%] | 14/57 = 24.6% [15.2%-37.1%] | 42/58 = 72.4% [59.8%-82.2%] | 12/58 = 20.7% [12.3%-32.8%] | 7/24 = 29.2% [14.9%-49.2%] |
| s8_4b_rag_nofallback | nofallback+hard | 47/57 = 82.5% [70.6%-90.2%] | 10/57 = 17.5% [9.8%-29.4%] | 43/58 = 74.1% [61.6%-83.7%] | 10/58 = 17.2% [9.6%-28.9%] | 7/24 = 29.2% [14.9%-49.2%] |
| s8_4b_rag_none | none | 44/57 = 77.2% [64.8%-86.2%] | 17/57 = 29.8% [19.5%-42.7%] | 23/58 = 39.7% [28.1%-52.5%] | 14/58 = 24.1% [15.0%-36.5%] | 8/24 = 33.3% [18.0%-53.3%] |
| s8_4b_rag_oracle | oracle | 47/57 = 82.5% [70.6%-90.2%] | - | 43/58 = 74.1% [61.6%-83.7%] | - | - |
| s8_4b_rag_tool | tool | 38/57 = 66.7% [53.7%-77.5%] | - | 19/58 = 32.8% [22.1%-45.6%] | - | - |

## Speed, size and tool use

| Run | First word p50 / p90 s | End to end p50 / p90 s | Retrieval p50 / p90 ms | Context tokens mean | Peak RAM GB server / harness / total | search_knowledge used | Errors |
|---|---|---|---|---|---|---|---|
| s8_2b_rag_deployed | 7.3 / 18.8 | 10.6 / 25.5 | 585 / 710 | 303 | 4.25 / 0.65 / 4.57 | - | 0 |
| s8_2b_rag_nofallback | 7.7 / 19.2 | 11.7 / 24.2 | 524 / 637 | 338 | 5.78 / 0.36 / 6.15 | - | 0 |
| s8_2b_rag_none | 5.3 / 10.2 | 8.2 / 17.4 | - / - | - | 3.24 / 0.39 / 3.62 | - | 0 |
| s8_2b_rag_oracle | 4.3 / 14.3 | 6.4 / 20.6 | 0 / 0 | 116 | 5.11 / 0.64 / 5.76 | - | 0 |
| s8_2b_rag_tool | 5.8 / 10.6 | 9.5 / 18.5 | 0 / 404 | - | 3.00 / 0.36 / 3.35 | 43/373 | 0 |
| s8_4b_rag_deployed | 7.1 / 18.2 | 13.0 / 31.5 | 533 / 587 | 303 | 5.75 / 1.03 / 6.67 | - | 0 |
| s8_4b_rag_nofallback | 6.5 / 15.8 | 12.1 / 28.7 | 527 / 607 | 338 | 6.37 / 0.98 / 7.34 | - | 0 |
| s8_4b_rag_none | 12.1 / 24.4 | 18.6 / 37.6 | - / - | - | 4.77 / 0.05 / 4.82 | - | 0 |
| s8_4b_rag_oracle | 3.1 / 15.5 | 9.0 / 28.3 | 0 / 0 | 116 | 4.10 / 0.03 / 4.13 | - | 0 |
| s8_4b_rag_tool | 11.7 / 24.0 | 19.2 / 35.7 | 0 / 627 | - | 4.20 / 0.37 / 4.55 | 102/373 | 0 |

## Paired comparisons (answerable questions with an automatic check)

| Model | A | B | Cases | A - B (points) | 95% CI | McNemar p |
|---|---|---|---|---|---|---|
| Qwen3.5-2B | oracle | deployed | 222 | +13.5 | [+7.2, +19.8] | 0.0001 |
| Qwen3.5-2B | deployed | none | 222 | +15.3 | [+8.1, +22.5] | 0.0000 |
| Qwen3.5-2B | deployed | nofallback | 222 | -2.3 | [-5.9, +1.4] | 0.3018 |
| Qwen3.5-2B | tool | deployed | 222 | -5.4 | [-13.5, +2.3] | 0.2127 |
| Qwen3.5-4B | oracle | deployed | 222 | +4.1 | [-0.5, +9.0] | 0.1360 |
| Qwen3.5-4B | deployed | none | 222 | +27.9 | [+21.6, +34.7] | 0.0000 |
| Qwen3.5-4B | deployed | nofallback | 222 | -2.3 | [-4.5, +0.0] | 0.1250 |
| Qwen3.5-4B | tool | deployed | 222 | -14.4 | [-20.7, -8.6] | 0.0000 |

Retrieval loss target: oracle - deployed at most 5 points. Judged rates appear once eval\rag_judge labels are passed with --labels.

## Correct by question type (answerable, auto-checked)

| Type | s8_2b_rag_deployed | s8_2b_rag_nofallback | s8_2b_rag_none | s8_2b_rag_oracle | s8_2b_rag_tool | s8_4b_rag_deployed | s8_4b_rag_nofallback | s8_4b_rag_none | s8_4b_rag_oracle | s8_4b_rag_tool |
|---|---|---|---|---|---|---|---|---|---|---|
| collection | 11/17 | 13/17 | 5/17 | 16/17 | 6/17 | 17/17 | 17/17 | 7/17 | 17/17 | 9/17 |
| faq | 13/39 | 16/39 | 5/39 | 17/39 | 12/39 | 26/39 | 31/39 | 7/39 | 32/39 | 17/39 |
| glossary | - | - | - | - | - | - | - | - | - | - |
| hinglish_spec | 13/17 | 13/17 | 4/17 | 13/17 | 3/17 | 10/17 | 10/17 | 4/17 | 9/17 | 5/17 |
| hinglish_text | 5/13 | 5/13 | 1/13 | 5/13 | 1/13 | 5/13 | 5/13 | 1/13 | 6/13 | 3/13 |
| offer | 2/6 | 0/6 | 0/6 | 4/6 | 4/6 | 6/6 | 6/6 | 0/6 | 5/6 | 6/6 |
| policy | 8/15 | 9/15 | 1/15 | 9/15 | 7/15 | 14/15 | 14/15 | 3/15 | 15/15 | 10/15 |
| product_description | 11/25 | 11/25 | 18/25 | 17/25 | 17/25 | 22/25 | 22/25 | 23/25 | 25/25 | 22/25 |
| product_name | 24/28 | 24/28 | 27/28 | 28/28 | 28/28 | 28/28 | 28/28 | 28/28 | 28/28 | 28/28 |
| product_sku | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| product_spec | 23/38 | 23/38 | 21/38 | 28/38 | 23/38 | 28/38 | 28/38 | 24/38 | 26/38 | 25/38 |
| store | 2/4 | 2/4 | 0/4 | 2/4 | 3/4 | 3/4 | 3/4 | 0/4 | 3/4 | 3/4 |
| typo_spec | 8/17 | 9/17 | 4/17 | 11/17 | 4/17 | 11/17 | 11/17 | 11/17 | 13/17 | 10/17 |
