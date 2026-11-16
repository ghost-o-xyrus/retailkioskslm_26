# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) | Tool calls | Tokens per tool output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s5_2b_rag_s5 | 151 | 1.10 | 7% | 391 | 15 | 8 | 48 | 460 | 29 | 0.37 | 78 |
| o3s5_2b_v12_s5 | 78 | 1.26 | 26% | 188 | 71 | 15 | 89 | 206 | 96 | 0.59 | 163 |
| o3s5_4b_rag_s5 | 151 | 1.15 | 7% | 391 | 19 | 11 | 68 | 460 | 30 | 0.34 | 88 |
| o3s5_4b_v12_s5 | 78 | 1.17 | 17% | 188 | 45 | 12 | 83 | 206 | 70 | 0.46 | 152 |
| o3s5h_2b_rag_ht | 151 | 2.28 | 80% | 390 | 138 | 58 | 55 | 460 | 125 | 1.37 | 91 |
| o3s5h_2b_v12_ht | 78 | 1.37 | 35% | 186 | 93 | 22 | 92 | 206 | 114 | 0.72 | 158 |
| o3s5h_4b_rag_ht | 151 | 1.25 | 13% | 390 | 34 | 17 | 68 | 460 | 39 | 0.33 | 119 |
| o3s5h_4b_v12_ht | 78 | 1.21 | 18% | 187 | 50 | 14 | 84 | 206 | 74 | 0.47 | 155 |
| o3s5sp_a_2b_rag_s5 | 40 | 1.07 | 8% | 380 | 9 | 8 | 48 | 421 | 23 | 0.38 | 63 |
| o3s5sp_a_2b_v12_s5 | 30 | 1.30 | 30% | 86 | 83 | 19 | 88 | 152 | 113 | 0.70 | 161 |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| o3s5_2b_rag_s5 | 7% (0.5 s) | 32% (2.1 s) | 2% (0.1 s) | 9% (0.6 s) | 49% (3.3 s) | 1% (0.1 s) |
| o3s5_2b_v12_s5 | 1% (0.1 s) | 15% (1.3 s) | 4% (0.4 s) | 11% (1.0 s) | 68% (6.2 s) | 2% (0.2 s) |
| o3s5_4b_rag_s5 | 5% (0.7 s) | 34% (4.9 s) | 2% (0.3 s) | 8% (1.2 s) | 51% (7.4 s) | 1% (0.1 s) |
| o3s5_4b_v12_s5 | 1% (0.1 s) | 21% (3.0 s) | 4% (0.6 s) | 9% (1.3 s) | 63% (9.0 s) | 2% (0.3 s) |
| o3s5h_2b_rag_ht | 4% (0.4 s) | 17% (1.8 s) | 9% (1.0 s) | 36% (3.9 s) | 34% (3.7 s) | 1% (0.1 s) |
| o3s5h_2b_v12_ht | 0% (0.0 s) | 12% (1.1 s) | 5% (0.5 s) | 16% (1.5 s) | 65% (6.1 s) | 1% (0.1 s) |
| o3s5h_4b_rag_ht | 3% (0.5 s) | 31% (4.5 s) | 4% (0.6 s) | 13% (1.9 s) | 49% (7.0 s) | 0% (0.1 s) |
| o3s5h_4b_v12_ht | 0% (0.1 s) | 20% (2.6 s) | 4% (0.6 s) | 10% (1.4 s) | 64% (8.5 s) | 1% (0.2 s) |
| o3s5sp_a_2b_rag_s5 | 5% (0.5 s) | 58% (6.3 s) | 1% (0.2 s) | 5% (0.5 s) | 30% (3.3 s) | 1% (0.1 s) |
| o3s5sp_a_2b_v12_s5 | 0% (0.0 s) | 14% (1.5 s) | 15% (1.7 s) | 12% (1.3 s) | 58% (6.5 s) | 1% (0.1 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| o3s5_2b_rag_s5 | 3.3 s [3.2 s–3.4 s] | 3.9 s | 5.7 s [5.6 s–5.8 s] | 9.8 s | 3,034 MB |
| o3s5_2b_v12_s5 | 2.0 s [1.6 s–2.5 s] | 6.6 s | 5.7 s [4.9 s–6.9 s] | 20.5 s | 3,802 MB |
| o3s5_4b_rag_s5 | 7.0 s [6.7 s–7.3 s] | 8.7 s | 12.9 s [12.0 s–13.5 s] | 24.0 s | 3,104 MB |
| o3s5_4b_v12_s5 | 3.6 s [2.8 s–4.9 s] | 12.3 s | 10.3 s [9.2 s–12.0 s] | 32.7 s | 5,126 MB |
| o3s5h_2b_rag_ht | 6.3 s [6.0 s–8.5 s] | 13.2 s | 10.2 s [8.2 s–11.4 s] | 18.3 s | 3,052 MB |
| o3s5h_2b_v12_ht | 2.0 s [1.5 s–2.8 s] | 6.5 s | 5.8 s [4.8 s–7.4 s] | 20.3 s | 4,162 MB |
| o3s5h_4b_rag_ht | 6.4 s [6.2 s–6.8 s] | 12.2 s | 11.8 s [11.0 s–12.4 s] | 28.5 s | 4,303 MB |
| o3s5h_4b_v12_ht | 3.0 s [2.4 s–4.4 s] | 11.0 s | 9.5 s [8.5 s–10.6 s] | 29.7 s | 6,485 MB |
| o3s5sp_a_2b_rag_s5 | 9.7 s [5.2 s–10.1 s] | 11.5 s | 12.2 s [9.4 s–13.0 s] | 14.8 s | 2,297 MB |
| o3s5sp_a_2b_v12_s5 | 3.0 s [1.8 s–4.6 s] | 11.1 s | 6.6 s [4.5 s–9.4 s] | 26.0 s | 2,284 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s5_2b_rag_s5 | 183.2 | 14.6 | 627 ms | 265.8 | -49 ms | 14.4 | 11% / 49% |
| o3s5_2b_v12_s5 | 148.6 | 14.5 | 591 ms | 258.7 | -142 ms | 14.2 | 12% / 81% |
| o3s5_4b_rag_s5 | 78.7 | 9.3 | 1,364 ms | 112.3 | 6 ms | 9.3 | 12% / 59% |
| o3s5_4b_v12_s5 | 65.5 | 9.2 | 1,282 ms | 113.2 | -360 ms | 8.9 | 15% / 82% |
| o3s5h_2b_rag_ht | 187.7 | 15.0 | 368 ms | 267.6 | -68 ms | 14.7 | 5% / 21% |
| o3s5h_2b_v12_ht | 174.6 | 14.9 | 406 ms | 267.6 | -93 ms | 14.7 | 8% / 78% |
| o3s5h_4b_rag_ht | 84.0 | 9.5 | 1,013 ms | 112.0 | -577 ms | 8.8 | 12% / 23% |
| o3s5h_4b_v12_ht | 74.5 | 10.0 | 971 ms | 118.0 | -340 ms | 9.6 | 13% / 80% |
| o3s5sp_a_2b_rag_s5 | 60.0 | 14.6 | 22 ms | 60.2 | -313 ms | 13.4 | 3% / 13% |
| o3s5sp_a_2b_v12_s5 | 51.7 | 13.7 | 90 ms | 53.6 | -292 ms | 13.1 | 12% / 26% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request, tool-mode cases) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit | Empty replies (incl. fallback) | Loop-guard notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s5_2b_rag_s5 | 0% | 1.36 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| o3s5_2b_v12_s5 | 2% | 1.15 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| o3s5_4b_rag_s5 | 0% | 1.36 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| o3s5_4b_v12_s5 | 2% | 1.15 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| o3s5h_2b_rag_ht | 0% | 1.36 | 15 | 15 | 63 | 0 | 0 | 0 | 15 |
| o3s5h_2b_v12_ht | 2% | 1.15 | 0 | 0 | 4 | 1 | 0 | 0 | 0 |
| o3s5h_4b_rag_ht | 0% | 1.36 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| o3s5h_4b_v12_ht | 2% | 1.15 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| o3s5sp_a_2b_rag_s5 | 0% | 1.34 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| o3s5sp_a_2b_v12_s5 | 0% | 1.01 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Loop guard, forced final requests** (tool_choice none). If these read far more tokens than other tool rounds, the server dropped the tool list from the prompt and lost the prompt cache.

| Run | Forced final requests | Mean tokens read: forced final | Mean tokens read: other tool rounds |
|---|---:|---:|---:|
| o3s5_2b_rag_s5 | 141 | 418 | 160 |
| o3s5_2b_v12_s5 | 30 | 227 | 278 |
| o3s5_4b_rag_s5 | 145 | 409 | 138 |
| o3s5_4b_v12_s5 | 30 | 227 | 270 |
| o3s5h_2b_rag_ht | 27 | 140 | 110 |
| o3s5h_2b_v12_ht | 22 | 196 | 244 |
| o3s5h_4b_rag_ht | 17 | 234 | 116 |
| o3s5h_4b_v12_ht | 22 | 180 | 254 |
| o3s5sp_a_2b_rag_s5 | 37 | 408 | 121 |
| o3s5sp_a_2b_v12_s5 | 13 | 167 | 275 |

## By route (Step 4 router)

**o3s5_2b_rag_s5**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 9 | 1.00 | 253 | 1.5 s |
| shopping | 11 | 2.36 | 243 | 9.0 s |
| store | 130 | 1.00 | 434 | 3.3 s |
| unclear | 1 | 1.00 | 17 | 1.2 s |

**o3s5_2b_v12_s5**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 0.7 s |
| compare | 2 | 1.00 | 268 | 1.8 s |
| lookup | 6 | 1.00 | 254 | 1.5 s |
| shopping | 27 | 1.74 | 232 | 5.6 s |
| staff | 5 | 1.00 | 105 | 1.0 s |
| stock | 8 | 1.00 | 162 | 1.2 s |
| store | 9 | 1.00 | 324 | 2.0 s |

**o3s5_4b_rag_s5**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 9 | 1.00 | 253 | 2.9 s |
| shopping | 11 | 3.00 | 298 | 28.1 s |
| store | 130 | 1.00 | 434 | 7.0 s |
| unclear | 1 | 1.00 | 17 | 2.3 s |

**o3s5_4b_v12_s5**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 1.6 s |
| compare | 2 | 1.00 | 268 | 4.2 s |
| lookup | 6 | 1.00 | 254 | 3.3 s |
| shopping | 27 | 1.48 | 156 | 2.8 s |
| staff | 5 | 1.00 | 105 | 2.1 s |
| stock | 8 | 1.00 | 162 | 2.7 s |
| store | 9 | 1.00 | 324 | 4.1 s |

**o3s5h_2b_rag_ht**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 9 | 1.00 | 253 | 1.3 s |
| shopping | 11 | 2.36 | 243 | 8.6 s |
| store | 130 | 2.38 | 574 | 6.3 s |
| unclear | 1 | 1.00 | 17 | 1.0 s |

**o3s5h_2b_v12_ht**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 0.6 s |
| compare | 2 | 1.00 | 268 | 1.5 s |
| lookup | 6 | 1.00 | 254 | 1.3 s |
| shopping | 27 | 1.74 | 232 | 5.3 s |
| staff | 5 | 1.00 | 105 | 0.8 s |
| stock | 8 | 1.00 | 162 | 1.0 s |
| store | 9 | 2.00 | 498 | 5.2 s |

**o3s5h_4b_rag_ht**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 9 | 1.00 | 253 | 3.7 s |
| shopping | 11 | 3.00 | 298 | 29.6 s |
| store | 130 | 1.12 | 449 | 6.4 s |
| unclear | 1 | 1.00 | 17 | 1.7 s |

**o3s5h_4b_v12_ht**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 1.3 s |
| compare | 2 | 1.00 | 268 | 3.6 s |
| lookup | 6 | 1.00 | 254 | 2.9 s |
| shopping | 27 | 1.48 | 156 | 1.7 s |
| staff | 5 | 1.00 | 105 | 1.8 s |
| stock | 8 | 1.00 | 162 | 2.3 s |
| store | 9 | 1.33 | 358 | 3.0 s |

**o3s5sp_a_2b_rag_s5**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| lookup | 2 | 1.00 | 274 | 4.7 s |
| shopping | 3 | 2.00 | 157 | 10.0 s |
| store | 35 | 1.00 | 415 | 9.8 s |

**o3s5sp_a_2b_v12_s5**

| Route | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| chat | 3 | 1.00 | 16 | 0.4 s |
| compare | 1 | 1.00 | 266 | 4.9 s |
| lookup | 2 | 1.00 | 255 | 4.2 s |
| shopping | 14 | 1.64 | 202 | 8.9 s |
| staff | 3 | 1.00 | 105 | 1.9 s |
| stock | 5 | 1.00 | 171 | 3.0 s |
| store | 2 | 1.00 | 115 | 2.8 s |

## By category

**o3s5_2b_rag_s5**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 3.3 s |
| rag/faq | 16 | 1.00 | 162 | 1.8 s |
| rag/glossary | 8 | 1.00 | 287 | 2.6 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 3.5 s |
| rag/hinglish_text | 6 | 1.00 | 442 | 3.2 s |
| rag/missing_attribute | 8 | 1.00 | 578 | 3.5 s |
| rag/missing_policy | 4 | 1.00 | 162 | 1.2 s |
| rag/negative | 9 | 1.00 | 466 | 3.4 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 3.4 s |
| rag/not_sold | 6 | 1.00 | 45 | 1.3 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.2 s |
| rag/offer | 2 | 1.00 | 245 | 2.1 s |
| rag/policy | 7 | 1.43 | 427 | 3.3 s |
| rag/product_description | 10 | 2.20 | 207 | 8.9 s |
| rag/product_name | 12 | 1.00 | 584 | 3.5 s |
| rag/product_sku | 9 | 1.00 | 253 | 1.5 s |
| rag/product_spec | 16 | 1.00 | 604 | 3.6 s |
| rag/spec_not_listed | 4 | 1.00 | 569 | 3.3 s |
| rag/store | 2 | 1.00 | 192 | 2.2 s |
| rag/typo_spec | 8 | 1.00 | 638 | 3.5 s |

**o3s5_2b_v12_s5**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.00 | 486 | 3.4 s |
| discovery | 16 | 1.75 | 265 | 5.5 s |
| grounded_qa | 10 | 1.00 | 336 | 2.3 s |
| handoff | 6 | 1.00 | 126 | 1.0 s |
| hinglish | 10 | 1.50 | 214 | 4.4 s |
| refusal | 12 | 1.08 | 272 | 2.2 s |
| tool_selection | 19 | 1.11 | 213 | 1.3 s |

**o3s5_4b_rag_s5**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 7.7 s |
| rag/faq | 16 | 1.00 | 162 | 4.0 s |
| rag/glossary | 8 | 1.00 | 287 | 4.3 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 7.3 s |
| rag/hinglish_text | 6 | 1.00 | 442 | 6.5 s |
| rag/missing_attribute | 8 | 1.00 | 578 | 7.6 s |
| rag/missing_policy | 4 | 1.00 | 162 | 2.4 s |
| rag/negative | 9 | 1.00 | 466 | 7.4 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 7.4 s |
| rag/not_sold | 6 | 1.00 | 45 | 2.4 s |
| rag/off_topic | 4 | 1.00 | 19 | 2.3 s |
| rag/offer | 2 | 1.00 | 245 | 4.2 s |
| rag/policy | 7 | 1.00 | 344 | 5.2 s |
| rag/product_description | 10 | 3.20 | 326 | 28.7 s |
| rag/product_name | 12 | 1.00 | 584 | 6.9 s |
| rag/product_sku | 9 | 1.00 | 253 | 2.9 s |
| rag/product_spec | 16 | 1.00 | 604 | 7.8 s |
| rag/spec_not_listed | 4 | 1.00 | 569 | 7.3 s |
| rag/store | 2 | 1.00 | 192 | 3.5 s |
| rag/typo_spec | 8 | 1.00 | 638 | 7.6 s |

**o3s5_4b_v12_s5**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.00 | 486 | 7.7 s |
| discovery | 16 | 1.44 | 132 | 2.2 s |
| grounded_qa | 10 | 1.00 | 336 | 5.1 s |
| handoff | 6 | 1.00 | 126 | 2.1 s |
| hinglish | 10 | 1.50 | 214 | 8.3 s |
| refusal | 12 | 1.00 | 270 | 4.0 s |
| tool_selection | 19 | 1.05 | 217 | 2.8 s |

**o3s5h_2b_rag_ht**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 2.38 | 1041 | 9.8 s |
| rag/faq | 16 | 1.88 | 206 | 5.3 s |
| rag/glossary | 8 | 2.75 | 360 | 6.4 s |
| rag/hinglish_spec | 8 | 2.50 | 735 | 8.7 s |
| rag/hinglish_text | 6 | 2.00 | 558 | 5.7 s |
| rag/missing_attribute | 8 | 2.88 | 782 | 9.0 s |
| rag/missing_policy | 4 | 1.25 | 156 | 0.9 s |
| rag/negative | 9 | 2.89 | 723 | 11.3 s |
| rag/nonexistent_product | 4 | 4.00 | 944 | 14.5 s |
| rag/not_sold | 6 | 1.33 | 81 | 1.0 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.0 s |
| rag/offer | 2 | 3.00 | 328 | 10.1 s |
| rag/policy | 7 | 2.43 | 459 | 6.5 s |
| rag/product_description | 10 | 2.20 | 207 | 8.5 s |
| rag/product_name | 12 | 3.00 | 776 | 8.9 s |
| rag/product_sku | 9 | 1.00 | 253 | 1.3 s |
| rag/product_spec | 16 | 2.25 | 710 | 6.0 s |
| rag/spec_not_listed | 4 | 2.25 | 652 | 5.8 s |
| rag/store | 2 | 3.00 | 276 | 9.6 s |
| rag/typo_spec | 8 | 2.38 | 769 | 6.1 s |

**o3s5h_2b_v12_ht**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.00 | 486 | 3.1 s |
| discovery | 16 | 1.75 | 265 | 5.0 s |
| grounded_qa | 10 | 1.00 | 336 | 2.1 s |
| handoff | 6 | 1.17 | 122 | 0.8 s |
| hinglish | 10 | 1.50 | 214 | 3.8 s |
| refusal | 12 | 1.33 | 307 | 2.0 s |
| tool_selection | 19 | 1.37 | 275 | 1.1 s |

**o3s5h_4b_rag_ht**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 6.3 s |
| rag/faq | 16 | 1.12 | 163 | 2.9 s |
| rag/glossary | 8 | 1.00 | 287 | 3.7 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 6.8 s |
| rag/hinglish_text | 6 | 1.00 | 442 | 5.8 s |
| rag/missing_attribute | 8 | 1.00 | 578 | 6.8 s |
| rag/missing_policy | 4 | 1.25 | 156 | 3.8 s |
| rag/negative | 9 | 1.56 | 645 | 6.7 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 6.5 s |
| rag/not_sold | 6 | 1.50 | 66 | 2.4 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.7 s |
| rag/offer | 2 | 1.00 | 245 | 3.6 s |
| rag/policy | 7 | 1.00 | 334 | 4.4 s |
| rag/product_description | 10 | 3.20 | 326 | 29.9 s |
| rag/product_name | 12 | 1.25 | 606 | 8.1 s |
| rag/product_sku | 9 | 1.00 | 253 | 3.7 s |
| rag/product_spec | 16 | 1.00 | 604 | 7.1 s |
| rag/spec_not_listed | 4 | 1.25 | 580 | 6.5 s |
| rag/store | 2 | 1.00 | 192 | 2.9 s |
| rag/typo_spec | 8 | 1.00 | 638 | 7.0 s |

**o3s5h_4b_v12_ht**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.00 | 486 | 6.9 s |
| discovery | 16 | 1.44 | 132 | 1.5 s |
| grounded_qa | 10 | 1.00 | 336 | 4.5 s |
| handoff | 6 | 1.00 | 114 | 1.8 s |
| hinglish | 10 | 1.50 | 214 | 7.3 s |
| refusal | 12 | 1.25 | 302 | 3.9 s |
| tool_selection | 19 | 1.05 | 217 | 2.4 s |

**o3s5sp_a_2b_rag_s5**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 2 | 1.00 | 596 | 10.1 s |
| rag/faq | 4 | 1.00 | 211 | 4.1 s |
| rag/glossary | 2 | 1.00 | 278 | 5.1 s |
| rag/hinglish_spec | 2 | 1.00 | 606 | 10.8 s |
| rag/hinglish_text | 2 | 1.00 | 370 | 6.7 s |
| rag/missing_attribute | 2 | 1.00 | 542 | 11.1 s |
| rag/missing_policy | 1 | 1.00 | 19 | 0.7 s |
| rag/negative | 2 | 1.00 | 573 | 9.8 s |
| rag/nonexistent_product | 1 | 1.00 | 523 | 11.1 s |
| rag/not_sold | 2 | 1.00 | 18 | 1.1 s |
| rag/off_topic | 1 | 1.00 | 20 | 1.1 s |
| rag/offer | 1 | 1.00 | 275 | 5.3 s |
| rag/policy | 2 | 1.00 | 307 | 5.5 s |
| rag/product_description | 3 | 2.00 | 157 | 10.0 s |
| rag/product_name | 3 | 1.00 | 617 | 10.0 s |
| rag/product_sku | 2 | 1.00 | 274 | 4.7 s |
| rag/product_spec | 4 | 1.00 | 592 | 10.8 s |
| rag/spec_not_listed | 1 | 1.00 | 612 | 10.4 s |
| rag/store | 1 | 1.00 | 213 | 4.3 s |
| rag/typo_spec | 2 | 1.00 | 618 | 10.7 s |

**o3s5sp_a_2b_v12_s5**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 1 | 1.00 | 266 | 4.9 s |
| discovery | 8 | 1.62 | 237 | 9.5 s |
| handoff | 3 | 1.00 | 105 | 1.9 s |
| hinglish | 4 | 1.50 | 153 | 6.7 s |
| refusal | 4 | 1.25 | 138 | 4.4 s |
| tool_selection | 10 | 1.10 | 140 | 2.9 s |

