# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) | Tool calls | Tokens per tool output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s4_2b_rag_s4 | 151 | 2.33 | 86% | 376 | 149 | 59 | 55 | 460 | 125 | 1.36 | 92 |
| o3s4_2b_v12_s4 | 78 | 1.63 | 59% | 144 | 131 | 33 | 93 | 206 | 120 | 0.72 | 167 |
| o3s4_4b_rag_s4 | 151 | 1.31 | 19% | 376 | 46 | 19 | 69 | 460 | 40 | 0.34 | 119 |
| o3s4_4b_v12_s4 | 78 | 1.51 | 44% | 145 | 92 | 28 | 85 | 206 | 83 | 0.55 | 151 |
| o3s4sp_a_2b_rag_s4 | 40 | 2.40 | 85% | 366 | 152 | 64 | 54 | 421 | 127 | 1.40 | 90 |
| o3s4sp_a_2b_v12_s4 | 30 | 1.67 | 63% | 31 | 140 | 33 | 89 | 152 | 128 | 0.70 | 182 |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| o3s4_2b_rag_s4 | 4% (0.4 s) | 18% (2.0 s) | 11% (1.3 s) | 35% (4.0 s) | 32% (3.7 s) | 1% (0.1 s) |
| o3s4_2b_v12_s4 | 0% (0.1 s) | 11% (1.2 s) | 8% (0.8 s) | 20% (2.2 s) | 59% (6.3 s) | 1% (0.1 s) |
| o3s4_4b_rag_s4 | 4% (0.5 s) | 29% (4.4 s) | 4% (0.7 s) | 14% (2.0 s) | 49% (7.3 s) | 0% (0.1 s) |
| o3s4_4b_v12_s4 | 1% (0.1 s) | 16% (2.8 s) | 8% (1.4 s) | 18% (3.0 s) | 55% (9.4 s) | 2% (0.3 s) |
| o3s4sp_a_2b_rag_s4 | 3% (0.6 s) | 34% (5.9 s) | 16% (2.7 s) | 25% (4.3 s) | 21% (3.7 s) | 1% (0.1 s) |
| o3s4sp_a_2b_v12_s4 | 0% (0.0 s) | 5% (0.5 s) | 21% (2.2 s) | 20% (2.1 s) | 53% (5.7 s) | 1% (0.1 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| o3s4_2b_rag_s4 | 7.0 s [6.6 s–8.9 s] | 14.4 s | 10.8 s [8.8 s–12.0 s] | 19.1 s | 3,051 MB |
| o3s4_2b_v12_s4 | 4.1 s [3.5 s–4.9 s] | 7.3 s | 7.7 s [6.2 s–9.1 s] | 20.9 s | 4,136 MB |
| o3s4_4b_rag_s4 | 6.8 s [6.6 s–7.0 s] | 12.8 s | 12.4 s [11.7 s–13.2 s] | 27.3 s | 4,244 MB |
| o3s4_4b_v12_s4 | 7.2 s [5.8 s–7.8 s] | 14.3 s | 12.3 s [11.7 s–13.2 s] | 34.4 s | 4,574 MB |
| o3s4sp_a_2b_rag_s4 | 13.9 s [9.7 s–17.2 s] | 22.6 s | 15.8 s [12.4 s–20.9 s] | 31.4 s | 2,396 MB |
| o3s4sp_a_2b_v12_s4 | 4.4 s [2.4 s–6.6 s] | 10.5 s | 7.7 s [5.2 s–13.7 s] | 22.1 s | 2,298 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s4_2b_rag_s4 | 157.9 | 14.8 | 541 ms | 254.4 | -35 ms | 14.6 | 7% / 23% |
| o3s4_2b_v12_s4 | 136.3 | 14.8 | 601 ms | 264.2 | -83 ms | 14.6 | 15% / 79% |
| o3s4_4b_rag_s4 | 84.0 | 9.5 | 898 ms | 109.7 | -163 ms | 9.2 | 11% / 23% |
| o3s4_4b_v12_s4 | 56.2 | 9.0 | 1,335 ms | 107.7 | -200 ms | 8.8 | 18% / 82% |
| o3s4sp_a_2b_rag_s4 | 60.4 | 14.7 | 262 ms | 65.2 | 164 ms | 15.4 | 4% / 18% |
| o3s4sp_a_2b_v12_s4 | 62.7 | 15.9 | 72 ms | 65.6 | -96 ms | 15.5 | 3% / 29% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request, tool-mode cases) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit | Empty replies (incl. fallback) | Loop-guard notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s4_2b_rag_s4 | 0% | 1.36 | 13 | 13 | 63 | 0 | 0 | 0 | 13 |
| o3s4_2b_v12_s4 | 2% | 1.15 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| o3s4_4b_rag_s4 | 0% | 1.36 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| o3s4_4b_v12_s4 | 2% | 1.15 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| o3s4sp_a_2b_rag_s4 | 0% | 1.34 | 5 | 5 | 17 | 0 | 0 | 0 | 5 |
| o3s4sp_a_2b_v12_s4 | 0% | 1.01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Loop guard, forced final requests** (tool_choice none). If these read far more tokens than other tool rounds, the server dropped the tool list from the prompt and lost the prompt cache.

| Run | Forced final requests | Mean tokens read: forced final | Mean tokens read: other tool rounds |
|---|---:|---:|---:|
| o3s4_2b_rag_s4 | 17 | 86 | 114 |
| o3s4_2b_v12_s4 | 1 | 424 | 205 |
| o3s4_4b_rag_s4 | 8 | 212 | 134 |
| o3s4_4b_v12_s4 | 2 | 182 | 180 |
| o3s4sp_a_2b_rag_s4 | 7 | 81 | 112 |

## By route (Step 4 router)

**o3s4_2b_rag_s4**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 9 | 2.00 | 220 | 4.3 s |
| shopping | 11 | 2.36 | 243 | 9.0 s |
| store | 130 | 2.36 | 574 | 6.9 s |
| unclear | 1 | 1.00 | 17 | 1.2 s |

**o3s4_2b_v12_s4**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 0.7 s |
| compare | 2 | 2.00 | 316 | 6.2 s |
| lookup | 6 | 2.00 | 215 | 4.7 s |
| shopping | 27 | 1.74 | 232 | 5.6 s |
| staff | 5 | 1.80 | 127 | 3.9 s |
| stock | 8 | 2.00 | 125 | 4.0 s |
| store | 9 | 2.00 | 498 | 5.6 s |

**o3s4_4b_rag_s4**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 9 | 2.11 | 232 | 7.3 s |
| shopping | 11 | 3.00 | 298 | 27.0 s |
| store | 130 | 1.12 | 449 | 6.6 s |
| unclear | 1 | 1.00 | 17 | 1.8 s |

**o3s4_4b_v12_s4**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 1.7 s |
| compare | 2 | 2.00 | 316 | 11.5 s |
| lookup | 6 | 2.33 | 296 | 8.8 s |
| shopping | 27 | 1.48 | 156 | 2.4 s |
| staff | 5 | 2.00 | 89 | 7.6 s |
| stock | 8 | 2.12 | 130 | 7.4 s |
| store | 9 | 1.33 | 358 | 4.3 s |

**o3s4sp_a_2b_rag_s4**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 2 | 2.00 | 240 | 5.9 s |
| shopping | 3 | 2.00 | 157 | 9.1 s |
| store | 35 | 2.46 | 565 | 14.5 s |

**o3s4sp_a_2b_v12_s4**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 0.3 s |
| compare | 1 | 2.00 | 405 | 10.7 s |
| lookup | 2 | 2.00 | 215 | 6.1 s |
| shopping | 14 | 1.64 | 202 | 7.3 s |
| staff | 3 | 2.00 | 162 | 4.3 s |
| stock | 5 | 2.00 | 138 | 4.4 s |
| store | 2 | 1.00 | 115 | 2.4 s |

## By category

**o3s4_2b_rag_s4**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 2.38 | 1041 | 10.4 s |
| rag/faq | 16 | 1.88 | 206 | 5.6 s |
| rag/glossary | 8 | 2.75 | 360 | 6.8 s |
| rag/hinglish_spec | 8 | 2.50 | 735 | 9.3 s |
| rag/hinglish_text | 6 | 2.00 | 558 | 6.1 s |
| rag/missing_attribute | 8 | 2.88 | 782 | 10.0 s |
| rag/missing_policy | 4 | 1.25 | 156 | 1.1 s |
| rag/negative | 9 | 2.89 | 723 | 12.2 s |
| rag/nonexistent_product | 4 | 4.00 | 944 | 15.4 s |
| rag/not_sold | 6 | 1.33 | 81 | 1.2 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.3 s |
| rag/offer | 2 | 3.00 | 328 | 10.6 s |
| rag/policy | 7 | 2.43 | 459 | 7.0 s |
| rag/product_description | 10 | 2.20 | 207 | 8.9 s |
| rag/product_name | 12 | 3.00 | 776 | 9.5 s |
| rag/product_sku | 9 | 2.00 | 220 | 4.3 s |
| rag/product_spec | 16 | 2.25 | 710 | 6.6 s |
| rag/spec_not_listed | 4 | 2.25 | 652 | 6.3 s |
| rag/store | 2 | 2.00 | 234 | 5.7 s |
| rag/typo_spec | 8 | 2.38 | 769 | 7.0 s |

**o3s4_2b_v12_s4**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.40 | 505 | 3.6 s |
| discovery | 16 | 1.75 | 265 | 5.5 s |
| grounded_qa | 10 | 1.00 | 336 | 2.3 s |
| handoff | 6 | 1.83 | 140 | 4.0 s |
| hinglish | 10 | 1.60 | 211 | 5.1 s |
| refusal | 12 | 1.50 | 301 | 3.2 s |
| tool_selection | 19 | 1.95 | 252 | 4.1 s |

**o3s4_4b_rag_s4**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 6.5 s |
| rag/faq | 16 | 1.12 | 163 | 3.0 s |
| rag/glossary | 8 | 1.00 | 287 | 3.8 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 7.0 s |
| rag/hinglish_text | 6 | 1.00 | 442 | 6.0 s |
| rag/missing_attribute | 8 | 1.00 | 578 | 8.0 s |
| rag/missing_policy | 4 | 1.25 | 156 | 4.0 s |
| rag/negative | 9 | 1.56 | 645 | 7.2 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 7.5 s |
| rag/not_sold | 6 | 1.50 | 66 | 2.7 s |
| rag/off_topic | 4 | 1.00 | 19 | 2.3 s |
| rag/offer | 2 | 1.00 | 245 | 3.7 s |
| rag/policy | 7 | 1.00 | 334 | 4.6 s |
| rag/product_description | 10 | 3.20 | 326 | 27.2 s |
| rag/product_name | 12 | 1.25 | 606 | 6.7 s |
| rag/product_sku | 9 | 2.11 | 232 | 7.3 s |
| rag/product_spec | 16 | 1.00 | 604 | 7.2 s |
| rag/spec_not_listed | 4 | 1.25 | 580 | 6.7 s |
| rag/store | 2 | 1.00 | 192 | 3.0 s |
| rag/typo_spec | 8 | 1.00 | 638 | 7.0 s |

**o3s4_4b_v12_s4**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.40 | 505 | 8.9 s |
| discovery | 16 | 1.44 | 132 | 2.4 s |
| grounded_qa | 10 | 1.00 | 336 | 5.7 s |
| handoff | 6 | 1.83 | 102 | 7.4 s |
| hinglish | 10 | 1.60 | 211 | 9.3 s |
| refusal | 12 | 1.33 | 279 | 5.0 s |
| tool_selection | 19 | 1.84 | 234 | 7.5 s |

**o3s4sp_a_2b_rag_s4**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 2 | 2.00 | 924 | 19.7 s |
| rag/faq | 4 | 1.75 | 226 | 7.5 s |
| rag/glossary | 2 | 3.00 | 360 | 18.1 s |
| rag/hinglish_spec | 2 | 3.50 | 836 | 19.7 s |
| rag/hinglish_text | 2 | 2.00 | 454 | 10.1 s |
| rag/missing_attribute | 2 | 3.00 | 708 | 18.5 s |
| rag/missing_policy | 1 | 1.00 | 19 | 0.8 s |
| rag/negative | 2 | 4.00 | 1257 | 30.4 s |
| rag/nonexistent_product | 1 | 4.00 | 864 | 23.9 s |
| rag/not_sold | 2 | 1.00 | 18 | 1.2 s |
| rag/off_topic | 1 | 1.00 | 20 | 1.6 s |
| rag/offer | 1 | 4.00 | 399 | 21.7 s |
| rag/policy | 2 | 2.50 | 370 | 12.8 s |
| rag/product_description | 3 | 2.00 | 157 | 9.1 s |
| rag/product_name | 3 | 3.00 | 844 | 18.3 s |
| rag/product_sku | 2 | 2.00 | 240 | 5.9 s |
| rag/product_spec | 4 | 2.25 | 677 | 14.1 s |
| rag/spec_not_listed | 1 | 2.00 | 669 | 13.2 s |
| rag/store | 1 | 2.00 | 255 | 7.8 s |
| rag/typo_spec | 2 | 2.50 | 767 | 16.1 s |

**o3s4sp_a_2b_v12_s4**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 1 | 2.00 | 405 | 10.7 s |
| discovery | 8 | 1.62 | 237 | 8.0 s |
| handoff | 3 | 2.00 | 162 | 4.3 s |
| hinglish | 4 | 1.50 | 153 | 4.2 s |
| refusal | 4 | 1.50 | 130 | 3.9 s |
| tool_selection | 10 | 1.70 | 119 | 4.4 s |

