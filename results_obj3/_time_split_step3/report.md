# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) | Tool calls | Tokens per tool output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s3_2b_rag_s3 | 151 | 2.47 | 86% | 447 | 154 | 65 | 58 | 476 | 127 | 1.50 | 85 |
| o3s3_2b_v12_s3 | 78 | 2.09 | 67% | 350 | 208 | 53 | 89 | 459 | 188 | 1.19 | 157 |
| o3s3_4b_rag_s3 | 151 | 1.23 | 16% | 447 | 28 | 19 | 69 | 476 | 24 | 0.26 | 91 |
| o3s3_4b_v12_s3 | 78 | 1.45 | 36% | 351 | 71 | 27 | 89 | 459 | 62 | 0.47 | 132 |
| o3s3g_2b_rag_guard | 151 | 2.56 | 86% | 447 | 310 | 70 | 55 | 476 | 282 | 1.59 | 177 |
| o3s3g_2b_v12_guard | 78 | 2.14 | 64% | 357 | 529 | 54 | 75 | 459 | 509 | 1.15 | 441 |
| o3s3g_4b_rag_guard | 151 | 1.25 | 17% | 447 | 47 | 17 | 73 | 476 | 43 | 0.25 | 169 |
| o3s3g_4b_v12_guard | 78 | 1.42 | 37% | 356 | 179 | 24 | 90 | 459 | 172 | 0.44 | 394 |
| o3s3sp_a_2b_rag_s3 | 40 | 2.60 | 85% | 443 | 164 | 73 | 60 | 446 | 136 | 1.60 | 85 |
| o3s3sp_a_2b_v12_s3 | 30 | 2.37 | 77% | 285 | 241 | 65 | 70 | 470 | 216 | 1.43 | 151 |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| o3s3_2b_rag_s3 | 5% (0.6 s) | 18% (2.4 s) | 11% (1.4 s) | 35% (4.6 s) | 31% (4.1 s) | 1% (0.1 s) |
| o3s3_2b_v12_s3 | 3% (0.5 s) | 14% (2.1 s) | 10% (1.5 s) | 27% (3.9 s) | 44% (6.4 s) | 1% (0.2 s) |
| o3s3_4b_rag_s3 | 5% (0.8 s) | 33% (5.5 s) | 3% (0.5 s) | 12% (2.0 s) | 46% (7.6 s) | 0% (0.1 s) |
| o3s3_4b_v12_s3 | 3% (0.6 s) | 24% (4.7 s) | 6% (1.2 s) | 15% (2.9 s) | 51% (10.0 s) | 2% (0.3 s) |
| o3s3g_2b_rag_guard | 4% (0.5 s) | 17% (2.3 s) | 16% (2.1 s) | 35% (4.7 s) | 28% (3.7 s) | 1% (0.2 s) |
| o3s3g_2b_v12_guard | 3% (0.4 s) | 14% (2.0 s) | 19% (2.7 s) | 26% (3.6 s) | 36% (5.1 s) | 2% (0.3 s) |
| o3s3g_4b_rag_guard | 4% (0.7 s) | 33% (5.2 s) | 5% (0.7 s) | 11% (1.8 s) | 47% (7.4 s) | 1% (0.1 s) |
| o3s3g_4b_v12_guard | 3% (0.5 s) | 24% (4.5 s) | 11% (2.1 s) | 13% (2.4 s) | 48% (9.1 s) | 2% (0.3 s) |
| o3s3sp_a_2b_rag_s3 | 3% (0.5 s) | 37% (7.1 s) | 15% (2.8 s) | 25% (4.7 s) | 21% (3.9 s) | 0% (0.1 s) |
| o3s3sp_a_2b_v12_s3 | 3% (0.5 s) | 26% (4.6 s) | 22% (4.0 s) | 23% (4.3 s) | 26% (4.6 s) | 0% (0.1 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| o3s3_2b_rag_s3 | 9.0 s [7.2 s–9.9 s] | 15.8 s | 12.3 s [9.6 s–13.2 s] | 24.0 s | 3,052 MB |
| o3s3_2b_v12_s3 | 6.1 s [5.2 s–7.9 s] | 17.9 s | 10.1 s [8.0 s–14.7 s] | 31.6 s | 4,144 MB |
| o3s3_4b_rag_s3 | 7.3 s [7.0 s–7.5 s] | 18.7 s | 13.4 s [12.5 s–14.2 s] | 30.5 s | 1,604 MB |
| o3s3_4b_v12_s3 | 7.7 s [6.0 s–8.6 s] | 19.8 s | 13.5 s [12.4 s–15.2 s] | 40.8 s | 5,680 MB |
| o3s3g_2b_rag_guard | 7.6 s [6.7 s–10.3 s] | 18.5 s | 12.2 s [9.5 s–14.2 s] | 23.7 s | 5,920 MB |
| o3s3g_2b_v12_guard | 6.9 s [4.6 s–8.6 s] | 21.1 s | 10.0 s [7.2 s–15.8 s] | 26.8 s | 6,024 MB |
| o3s3g_4b_rag_guard | 7.0 s [6.9 s–7.3 s] | 19.5 s | 12.5 s [11.5 s–13.4 s] | 33.5 s | 4,275 MB |
| o3s3g_4b_v12_guard | 7.3 s [5.8 s–8.6 s] | 21.0 s | 12.7 s [11.0 s–14.8 s] | 40.5 s | 5,014 MB |
| o3s3sp_a_2b_rag_s3 | 16.5 s [13.8 s–18.3 s] | 29.3 s | 20.1 s [15.3 s–22.7 s] | 35.0 s | 2,388 MB |
| o3s3sp_a_2b_v12_s3 | 9.4 s [5.8 s–16.4 s] | 30.7 s | 15.2 s [8.0 s–24.6 s] | 34.3 s | 2,416 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s3_2b_rag_s3 | 158.4 | 14.1 | 552 ms | 247.2 | -24 ms | 14.0 | 6% / 25% |
| o3s3_2b_v12_s3 | 157.6 | 13.7 | 592 ms | 242.3 | -50 ms | 13.6 | 7% / 36% |
| o3s3_4b_rag_s3 | 79.0 | 9.2 | 1,398 ms | 110.8 | -127 ms | 9.1 | 11% / 33% |
| o3s3_4b_v12_s3 | 71.2 | 8.9 | 1,336 ms | 105.7 | -527 ms | 8.4 | 14% / 57% |
| o3s3g_2b_rag_guard | 173.7 | 15.0 | 578 ms | 263.2 | -83 ms | 14.6 | 5% / 30% |
| o3s3g_2b_v12_guard | 190.0 | 14.9 | 602 ms | 262.5 | -92 ms | 14.6 | 7% / 50% |
| o3s3g_4b_rag_guard | 83.1 | 9.8 | 1,238 ms | 112.3 | -382 ms | 9.3 | 8% / 30% |
| o3s3g_4b_v12_guard | 81.2 | 9.9 | 1,287 ms | 112.4 | -233 ms | 9.6 | 10% / 61% |
| o3s3sp_a_2b_rag_s3 | 61.2 | 15.3 | 133 ms | 63.4 | -105 ms | 14.8 | 2% / 10% |
| o3s3sp_a_2b_v12_s3 | 60.9 | 15.3 | 108 ms | 62.7 | -92 ms | 14.9 | 2% / 11% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request, tool-mode cases) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit | Empty replies (incl. fallback) | Loop-guard notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s3_2b_rag_s3 | 0% | 1.36 | 14 | 13 | 76 | 0 | 0 | 0 | 14 |
| o3s3_2b_v12_s3 | 2% | 1.37 | 0 | 0 | 14 | 1 | 0 | 0 | 0 |
| o3s3_4b_rag_s3 | 0% | 1.36 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| o3s3_4b_v12_s3 | 2% | 1.37 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| o3s3g_2b_rag_guard | 0% | 1.36 | 28 | 24 | 91 | 1 | 0 | 0 | 28 |
| o3s3g_2b_v12_guard | 3% | 1.37 | 0 | 0 | 11 | 1 | 0 | 0 | 0 |
| o3s3g_4b_rag_guard | 0% | 1.36 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |
| o3s3g_4b_v12_guard | 3% | 1.37 | 0 | 0 | 2 | 1 | 0 | 0 | 0 |
| o3s3sp_a_2b_rag_s3 | 0% | 1.35 | 5 | 5 | 21 | 0 | 0 | 0 | 5 |
| o3s3sp_a_2b_v12_s3 | 0% | 1.36 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |

**Loop guard, forced final requests** (tool_choice none). If these read far more tokens than other tool rounds, the server dropped the tool list from the prompt and lost the prompt cache.

| Run | Forced final requests | Mean tokens read: forced final | Mean tokens read: other tool rounds |
|---|---:|---:|---:|
| o3s3_2b_rag_s3 | 24 | 91 | 106 |
| o3s3_2b_v12_s3 | 14 | 144 | 200 |
| o3s3_4b_rag_s3 | 3 | 389 | 95 |
| o3s3_4b_v12_s3 | 2 | 150 | 158 |
| o3s3g_2b_rag_guard | 38 | 144 | 209 |
| o3s3g_2b_v12_guard | 17 | 221 | 521 |
| o3s3g_4b_rag_guard | 2 | 140 | 195 |
| o3s3g_4b_v12_guard | 1 | 167 | 432 |
| o3s3sp_a_2b_rag_s3 | 10 | 92 | 105 |
| o3s3sp_a_2b_v12_s3 | 9 | 121 | 192 |

## By category

**o3s3_2b_rag_s3**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 2.38 | 1041 | 11.0 s |
| rag/faq | 16 | 1.88 | 206 | 6.1 s |
| rag/glossary | 8 | 2.75 | 351 | 7.4 s |
| rag/hinglish_spec | 8 | 2.50 | 735 | 9.9 s |
| rag/hinglish_text | 6 | 2.00 | 549 | 6.5 s |
| rag/missing_attribute | 8 | 2.88 | 782 | 10.3 s |
| rag/missing_policy | 4 | 1.25 | 156 | 1.3 s |
| rag/negative | 9 | 2.89 | 723 | 12.9 s |
| rag/nonexistent_product | 4 | 4.00 | 944 | 16.2 s |
| rag/not_sold | 6 | 1.33 | 81 | 1.5 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.5 s |
| rag/offer | 2 | 3.00 | 319 | 11.3 s |
| rag/policy | 7 | 2.43 | 498 | 7.5 s |
| rag/product_description | 10 | 3.40 | 907 | 20.5 s |
| rag/product_name | 12 | 3.00 | 776 | 9.4 s |
| rag/product_sku | 9 | 3.00 | 720 | 9.9 s |
| rag/product_spec | 16 | 2.25 | 699 | 7.0 s |
| rag/spec_not_listed | 4 | 2.25 | 652 | 6.7 s |
| rag/store | 2 | 2.00 | 226 | 6.2 s |
| rag/typo_spec | 8 | 2.38 | 769 | 7.2 s |

**o3s3_2b_v12_s3**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.80 | 779 | 4.0 s |
| discovery | 16 | 2.38 | 568 | 8.1 s |
| grounded_qa | 10 | 1.00 | 336 | 2.4 s |
| handoff | 6 | 2.33 | 412 | 8.7 s |
| hinglish | 10 | 3.30 | 985 | 16.0 s |
| refusal | 12 | 1.50 | 301 | 3.6 s |
| tool_selection | 19 | 2.16 | 592 | 7.1 s |

**o3s3_4b_rag_s3**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 6.9 s |
| rag/faq | 16 | 1.12 | 163 | 3.8 s |
| rag/glossary | 8 | 1.00 | 278 | 5.1 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 7.4 s |
| rag/hinglish_text | 6 | 1.00 | 433 | 6.8 s |
| rag/missing_attribute | 8 | 1.00 | 578 | 8.0 s |
| rag/missing_policy | 4 | 1.25 | 156 | 4.8 s |
| rag/negative | 9 | 1.56 | 645 | 8.1 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 7.8 s |
| rag/not_sold | 6 | 1.50 | 66 | 3.1 s |
| rag/off_topic | 4 | 1.00 | 19 | 2.6 s |
| rag/offer | 2 | 1.00 | 236 | 5.3 s |
| rag/policy | 7 | 1.00 | 371 | 5.4 s |
| rag/product_description | 10 | 2.30 | 775 | 25.4 s |
| rag/product_name | 12 | 1.25 | 606 | 7.8 s |
| rag/product_sku | 9 | 1.78 | 621 | 8.9 s |
| rag/product_spec | 16 | 1.00 | 594 | 7.3 s |
| rag/spec_not_listed | 4 | 1.25 | 580 | 7.1 s |
| rag/store | 2 | 1.00 | 184 | 3.7 s |
| rag/typo_spec | 8 | 1.00 | 638 | 7.5 s |

**o3s3_4b_v12_s3**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.20 | 687 | 9.1 s |
| discovery | 16 | 1.50 | 322 | 4.2 s |
| grounded_qa | 10 | 1.00 | 336 | 5.6 s |
| handoff | 6 | 1.83 | 370 | 15.4 s |
| hinglish | 10 | 1.30 | 583 | 7.6 s |
| refusal | 12 | 1.33 | 279 | 4.9 s |
| tool_selection | 19 | 1.74 | 503 | 8.8 s |

**o3s3g_2b_rag_guard**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 2.62 | 1948 | 16.3 s |
| rag/faq | 16 | 2.19 | 253 | 5.9 s |
| rag/glossary | 8 | 2.75 | 376 | 6.8 s |
| rag/hinglish_spec | 8 | 2.75 | 800 | 8.6 s |
| rag/hinglish_text | 6 | 1.67 | 594 | 2.8 s |
| rag/missing_attribute | 8 | 3.00 | 882 | 10.1 s |
| rag/missing_policy | 4 | 1.75 | 184 | 1.2 s |
| rag/negative | 9 | 2.89 | 1117 | 10.4 s |
| rag/nonexistent_product | 4 | 3.75 | 1666 | 18.2 s |
| rag/not_sold | 6 | 1.33 | 58 | 1.2 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.3 s |
| rag/offer | 2 | 4.00 | 391 | 15.1 s |
| rag/policy | 7 | 2.57 | 660 | 6.9 s |
| rag/product_description | 10 | 3.60 | 1191 | 20.4 s |
| rag/product_name | 12 | 3.08 | 899 | 10.3 s |
| rag/product_sku | 9 | 2.67 | 770 | 10.3 s |
| rag/product_spec | 16 | 2.31 | 749 | 6.8 s |
| rag/spec_not_listed | 4 | 2.00 | 642 | 6.4 s |
| rag/store | 2 | 3.00 | 292 | 9.8 s |
| rag/typo_spec | 8 | 2.38 | 827 | 6.6 s |

**o3s3g_2b_v12_guard**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.60 | 759 | 3.7 s |
| discovery | 16 | 2.62 | 1353 | 13.5 s |
| grounded_qa | 10 | 1.00 | 336 | 2.3 s |
| handoff | 6 | 2.33 | 464 | 7.3 s |
| hinglish | 10 | 3.30 | 1718 | 20.0 s |
| refusal | 12 | 1.50 | 333 | 2.5 s |
| tool_selection | 19 | 2.21 | 862 | 7.2 s |

**o3s3g_4b_rag_guard**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 6.9 s |
| rag/faq | 16 | 1.12 | 165 | 3.5 s |
| rag/glossary | 8 | 1.00 | 278 | 4.2 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 7.4 s |
| rag/hinglish_text | 6 | 1.00 | 433 | 6.2 s |
| rag/missing_attribute | 8 | 1.12 | 588 | 7.5 s |
| rag/missing_policy | 4 | 1.00 | 146 | 2.2 s |
| rag/negative | 9 | 1.33 | 623 | 7.4 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 7.1 s |
| rag/not_sold | 6 | 1.50 | 68 | 2.9 s |
| rag/off_topic | 4 | 1.00 | 19 | 2.3 s |
| rag/offer | 2 | 1.00 | 236 | 4.1 s |
| rag/policy | 7 | 1.00 | 371 | 5.0 s |
| rag/product_description | 10 | 2.40 | 953 | 25.6 s |
| rag/product_name | 12 | 1.25 | 625 | 7.5 s |
| rag/product_sku | 9 | 2.22 | 734 | 13.3 s |
| rag/product_spec | 16 | 1.00 | 594 | 7.4 s |
| rag/spec_not_listed | 4 | 1.00 | 569 | 7.0 s |
| rag/store | 2 | 1.00 | 184 | 3.3 s |
| rag/typo_spec | 8 | 1.00 | 638 | 7.4 s |

**o3s3g_4b_v12_guard**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.20 | 717 | 8.1 s |
| discovery | 16 | 1.44 | 514 | 4.9 s |
| grounded_qa | 10 | 1.00 | 336 | 5.1 s |
| handoff | 6 | 1.67 | 377 | 13.8 s |
| hinglish | 10 | 1.50 | 814 | 10.5 s |
| refusal | 12 | 1.33 | 309 | 5.0 s |
| tool_selection | 19 | 1.63 | 658 | 9.5 s |

**o3s3sp_a_2b_rag_s3**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 2 | 2.00 | 924 | 19.8 s |
| rag/faq | 4 | 1.75 | 226 | 7.8 s |
| rag/glossary | 2 | 3.00 | 360 | 13.4 s |
| rag/hinglish_spec | 2 | 3.50 | 836 | 19.5 s |
| rag/hinglish_text | 2 | 2.00 | 454 | 10.9 s |
| rag/missing_attribute | 2 | 3.00 | 708 | 16.6 s |
| rag/missing_policy | 1 | 1.00 | 19 | 0.7 s |
| rag/negative | 2 | 4.00 | 1257 | 30.0 s |
| rag/nonexistent_product | 1 | 4.00 | 864 | 24.5 s |
| rag/not_sold | 2 | 1.00 | 18 | 0.9 s |
| rag/off_topic | 1 | 1.00 | 20 | 0.9 s |
| rag/offer | 1 | 4.00 | 399 | 17.3 s |
| rag/policy | 2 | 2.50 | 370 | 11.9 s |
| rag/product_description | 3 | 4.00 | 986 | 29.7 s |
| rag/product_name | 3 | 3.00 | 844 | 18.1 s |
| rag/product_sku | 2 | 3.00 | 799 | 17.6 s |
| rag/product_spec | 4 | 2.25 | 677 | 14.1 s |
| rag/spec_not_listed | 1 | 2.00 | 669 | 13.7 s |
| rag/store | 1 | 2.00 | 255 | 8.3 s |
| rag/typo_spec | 2 | 2.50 | 767 | 16.6 s |

**o3s3sp_a_2b_v12_s3**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 1 | 4.00 | 1113 | 31.8 s |
| discovery | 8 | 2.25 | 503 | 10.4 s |
| handoff | 3 | 2.67 | 533 | 14.7 s |
| hinglish | 4 | 4.00 | 1120 | 28.2 s |
| refusal | 4 | 1.50 | 130 | 4.3 s |
| tool_selection | 10 | 1.90 | 406 | 6.0 s |

