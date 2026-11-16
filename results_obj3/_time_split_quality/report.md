# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s1_2b_rag_b0 | 151 | 2.40 | 81% | 447 | 295 | 69 | 50 | 476 | 286 |
| o3s1_2b_rag_oracle | 151 | 2.11 | 77% | 192 | 249 | 56 | 46 | 165 | 244 |
| o3s1_2b_v11_b0 | 78 | 2.13 | 63% | 351 | 517 | 65 | 61 | 459 | 530 |
| o3s1_2b_v11_none | 78 | 1.64 | 54% | 130 | 333 | 35 | 81 | – | 327 |
| o3s1_4b_rag_b0 | 151 | 1.20 | 15% | 447 | 38 | 15 | 71 | 476 | 34 |
| o3s1_4b_rag_oracle | 151 | 1.25 | 17% | 192 | 84 | 16 | 69 | 165 | 82 |
| o3s1_4b_v11_b0 | 78 | 1.40 | 36% | 350 | 164 | 24 | 92 | 459 | 159 |
| o3s1_4b_v11_none | 78 | 1.49 | 44% | 133 | 212 | 26 | 80 | – | 209 |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| o3s1_2b_rag_b0 | 4% (0.5 s) | 18% (2.3 s) | 15% (2.0 s) | 36% (4.6 s) | 26% (3.3 s) | 1% (0.1 s) |
| o3s1_2b_rag_oracle | 0% (0.0 s) | 13% (1.3 s) | 16% (1.6 s) | 38% (3.7 s) | 31% (3.0 s) | 1% (0.1 s) |
| o3s1_2b_v11_b0 | 3% (0.4 s) | 15% (2.0 s) | 19% (2.6 s) | 32% (4.4 s) | 30% (4.1 s) | 2% (0.3 s) |
| o3s1_2b_v11_none | 0% (0.0 s) | 10% (1.1 s) | 14% (1.6 s) | 22% (2.5 s) | 52% (5.8 s) | 1% (0.2 s) |
| o3s1_4b_rag_b0 | 5% (0.7 s) | 33% (5.4 s) | 4% (0.6 s) | 10% (1.7 s) | 48% (7.8 s) | 0% (0.1 s) |
| o3s1_4b_rag_oracle | 0% (0.0 s) | 22% (2.8 s) | 8% (1.0 s) | 13% (1.6 s) | 56% (7.1 s) | 1% (0.1 s) |
| o3s1_4b_v11_b0 | 3% (0.5 s) | 23% (4.5 s) | 10% (1.9 s) | 13% (2.5 s) | 49% (9.4 s) | 2% (0.3 s) |
| o3s1_4b_v11_none | 0% (0.0 s) | 16% (2.5 s) | 15% (2.4 s) | 16% (2.6 s) | 51% (8.1 s) | 2% (0.3 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| o3s1_2b_rag_b0 | 6.8 s [6.5 s–7.4 s] | 18.5 s | 9.5 s [8.4 s–13.3 s] | 23.9 s | 6,170 MB |
| o3s1_2b_rag_oracle | 4.7 s [4.6 s–4.9 s] | 14.2 s | 6.6 s [6.1 s–7.2 s] | 19.8 s | 3,652 MB |
| o3s1_2b_v11_b0 | 6.3 s [4.6 s–8.0 s] | 21.6 s | 9.4 s [7.0 s–15.9 s] | 27.2 s | 5,648 MB |
| o3s1_2b_v11_none | 4.2 s [2.6 s–5.4 s] | 10.6 s | 7.5 s [5.8 s–9.8 s] | 23.0 s | 4,368 MB |
| o3s1_4b_rag_b0 | 7.3 s [7.1 s–7.5 s] | 14.4 s | 12.9 s [12.3 s–13.6 s] | 31.3 s | 3,732 MB |
| o3s1_4b_rag_oracle | 3.1 s [3.1 s–3.2 s] | 15.2 s | 8.8 s [8.2 s–9.6 s] | 26.4 s | 4,804 MB |
| o3s1_4b_v11_b0 | 7.4 s [6.0 s–8.3 s] | 20.2 s | 12.7 s [11.2 s–14.8 s] | 38.9 s | 5,390 MB |
| o3s1_4b_v11_none | 6.1 s [5.0 s–7.9 s] | 16.2 s | 11.3 s [10.1 s–13.1 s] | 34.7 s | 6,015 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s1_2b_rag_b0 | 174.7 | 15.0 | 591 ms | 262.0 | -84 ms | 14.6 | 5% / 25% |
| o3s1_2b_rag_oracle | 154.4 | 15.0 | 579 ms | 268.9 | -77 ms | 14.7 | 11% / 45% |
| o3s1_2b_v11_b0 | 187.5 | 14.9 | 623 ms | 262.8 | -56 ms | 14.7 | 12% / 53% |
| o3s1_2b_v11_none | 170.2 | 13.9 | 554 ms | 255.7 | -130 ms | 13.6 | 11% / 83% |
| o3s1_4b_rag_b0 | 81.0 | 9.1 | 1,251 ms | 108.1 | -390 ms | 8.7 | 8% / 28% |
| o3s1_4b_rag_oracle | 71.8 | 9.8 | 1,136 ms | 113.9 | -234 ms | 9.4 | 8% / 44% |
| o3s1_4b_v11_b0 | 80.4 | 9.7 | 1,296 ms | 112.2 | -189 ms | 9.5 | 11% / 61% |
| o3s1_4b_v11_none | 70.8 | 9.8 | 1,292 ms | 117.0 | -194 ms | 9.6 | 15% / 83% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s1_2b_rag_b0 | 0% | 1.36 | 32 | 24 | 97 | 0 | 23 |
| o3s1_2b_rag_oracle | 0% | 1.34 | 20 | 15 | 69 | 0 | 12 |
| o3s1_2b_v11_b0 | 24% | 1.37 | 4 | 1 | 13 | 1 | 12 |
| o3s1_2b_v11_none | 27% | – | 3 | 0 | 0 | 1 | 2 |
| o3s1_4b_rag_b0 | 0% | 1.36 | 0 | 0 | 6 | 0 | 0 |
| o3s1_4b_rag_oracle | 0% | 1.34 | 3 | 3 | 7 | 0 | 2 |
| o3s1_4b_v11_b0 | 24% | 1.37 | 0 | 0 | 2 | 1 | 1 |
| o3s1_4b_v11_none | 28% | – | 0 | 0 | 0 | 1 | 1 |

## By category

**o3s1_2b_rag_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 2.75 | 1866 | 18.8 s |
| rag/faq | 16 | 1.56 | 193 | 1.9 s |
| rag/glossary | 8 | 2.62 | 381 | 6.7 s |
| rag/hinglish_spec | 8 | 2.50 | 735 | 6.7 s |
| rag/hinglish_text | 6 | 1.83 | 604 | 2.9 s |
| rag/missing_attribute | 8 | 2.62 | 793 | 6.9 s |
| rag/missing_policy | 4 | 1.75 | 193 | 1.1 s |
| rag/negative | 9 | 3.11 | 1269 | 14.6 s |
| rag/nonexistent_product | 4 | 3.75 | 1848 | 17.8 s |
| rag/not_sold | 6 | 1.33 | 58 | 1.3 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.2 s |
| rag/offer | 2 | 4.00 | 425 | 15.1 s |
| rag/policy | 7 | 2.43 | 656 | 7.4 s |
| rag/product_description | 10 | 3.20 | 1158 | 19.7 s |
| rag/product_name | 12 | 2.83 | 820 | 8.2 s |
| rag/product_sku | 9 | 2.67 | 776 | 10.2 s |
| rag/product_spec | 16 | 2.12 | 728 | 6.7 s |
| rag/spec_not_listed | 4 | 2.00 | 643 | 6.3 s |
| rag/store | 2 | 1.50 | 215 | 3.6 s |
| rag/typo_spec | 8 | 2.50 | 839 | 6.7 s |

**o3s1_2b_rag_oracle**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.38 | 714 | 1.7 s |
| rag/faq | 16 | 1.88 | 173 | 5.0 s |
| rag/glossary | 8 | 2.12 | 138 | 4.8 s |
| rag/hinglish_spec | 8 | 2.00 | 334 | 4.5 s |
| rag/hinglish_text | 6 | 1.17 | 141 | 1.0 s |
| rag/missing_attribute | 8 | 2.00 | 337 | 4.6 s |
| rag/missing_policy | 4 | 1.00 | 20 | 0.7 s |
| rag/negative | 9 | 3.33 | 1361 | 14.4 s |
| rag/nonexistent_product | 4 | 3.75 | 1491 | 17.4 s |
| rag/not_sold | 6 | 1.17 | 25 | 0.8 s |
| rag/off_topic | 4 | 1.00 | 19 | 0.8 s |
| rag/offer | 2 | 3.00 | 268 | 10.4 s |
| rag/policy | 7 | 2.29 | 494 | 6.0 s |
| rag/product_description | 10 | 2.50 | 776 | 12.7 s |
| rag/product_name | 12 | 2.42 | 538 | 4.9 s |
| rag/product_sku | 9 | 2.89 | 471 | 8.3 s |
| rag/product_spec | 16 | 2.00 | 321 | 4.5 s |
| rag/spec_not_listed | 4 | 2.00 | 304 | 4.5 s |
| rag/store | 2 | 1.50 | 294 | 3.6 s |
| rag/typo_spec | 8 | 2.00 | 372 | 4.7 s |

**o3s1_2b_v11_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.60 | 756 | 3.8 s |
| discovery | 16 | 2.69 | 1222 | 13.6 s |
| grounded_qa | 10 | 1.00 | 336 | 2.3 s |
| handoff | 6 | 2.33 | 464 | 7.2 s |
| hinglish | 10 | 3.20 | 1740 | 19.0 s |
| refusal | 12 | 1.42 | 328 | 2.6 s |
| tool_selection | 19 | 2.21 | 889 | 7.2 s |

**o3s1_2b_v11_none**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.40 | 630 | 4.0 s |
| discovery | 16 | 2.06 | 756 | 8.0 s |
| grounded_qa | 10 | 1.00 | 336 | 2.2 s |
| handoff | 6 | 1.83 | 210 | 4.2 s |
| hinglish | 10 | 1.60 | 445 | 6.1 s |
| refusal | 12 | 1.50 | 354 | 3.1 s |
| tool_selection | 19 | 1.74 | 397 | 4.6 s |

**o3s1_4b_rag_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 7.2 s |
| rag/faq | 16 | 1.06 | 161 | 3.4 s |
| rag/glossary | 8 | 1.00 | 278 | 4.3 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 7.5 s |
| rag/hinglish_text | 6 | 1.00 | 433 | 6.2 s |
| rag/missing_attribute | 8 | 1.00 | 578 | 7.3 s |
| rag/missing_policy | 4 | 1.25 | 161 | 4.2 s |
| rag/negative | 9 | 1.22 | 544 | 7.4 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 6.9 s |
| rag/not_sold | 6 | 1.50 | 180 | 2.9 s |
| rag/off_topic | 4 | 1.00 | 19 | 2.3 s |
| rag/offer | 2 | 1.00 | 236 | 4.3 s |
| rag/policy | 7 | 1.00 | 371 | 5.5 s |
| rag/product_description | 10 | 2.20 | 867 | 27.3 s |
| rag/product_name | 12 | 1.25 | 625 | 8.1 s |
| rag/product_sku | 9 | 1.89 | 690 | 13.2 s |
| rag/product_spec | 16 | 1.00 | 594 | 7.6 s |
| rag/spec_not_listed | 4 | 1.00 | 569 | 7.7 s |
| rag/store | 2 | 1.00 | 184 | 3.3 s |
| rag/typo_spec | 8 | 1.00 | 638 | 7.8 s |

**o3s1_4b_rag_oracle**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 202 | 3.0 s |
| rag/faq | 16 | 1.00 | 118 | 2.0 s |
| rag/glossary | 8 | 1.00 | 68 | 1.6 s |
| rag/hinglish_spec | 8 | 1.38 | 266 | 3.2 s |
| rag/hinglish_text | 6 | 1.00 | 130 | 2.0 s |
| rag/missing_attribute | 8 | 1.12 | 272 | 3.5 s |
| rag/missing_policy | 4 | 1.50 | 51 | 6.4 s |
| rag/negative | 9 | 1.78 | 819 | 15.8 s |
| rag/nonexistent_product | 4 | 1.75 | 714 | 17.5 s |
| rag/not_sold | 6 | 1.50 | 154 | 1.6 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.6 s |
| rag/offer | 2 | 1.00 | 142 | 2.5 s |
| rag/policy | 7 | 1.00 | 219 | 3.1 s |
| rag/product_description | 10 | 1.60 | 485 | 4.5 s |
| rag/product_name | 12 | 1.25 | 298 | 3.6 s |
| rag/product_sku | 9 | 2.11 | 403 | 9.3 s |
| rag/product_spec | 16 | 1.00 | 242 | 3.2 s |
| rag/spec_not_listed | 4 | 1.00 | 230 | 3.1 s |
| rag/store | 2 | 1.00 | 262 | 3.6 s |
| rag/typo_spec | 8 | 1.00 | 242 | 3.2 s |

**o3s1_4b_v11_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.20 | 717 | 8.3 s |
| discovery | 16 | 1.38 | 487 | 4.0 s |
| grounded_qa | 10 | 1.00 | 336 | 5.0 s |
| handoff | 6 | 1.83 | 387 | 14.5 s |
| hinglish | 10 | 1.30 | 680 | 7.2 s |
| refusal | 12 | 1.33 | 352 | 5.6 s |
| tool_selection | 19 | 1.63 | 635 | 8.9 s |

**o3s1_4b_v11_none**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.40 | 630 | 8.0 s |
| discovery | 16 | 1.38 | 256 | 1.8 s |
| grounded_qa | 10 | 1.00 | 336 | 5.0 s |
| handoff | 6 | 1.83 | 77 | 7.8 s |
| hinglish | 10 | 1.60 | 445 | 11.9 s |
| refusal | 12 | 1.33 | 355 | 5.0 s |
| tool_selection | 19 | 1.79 | 373 | 8.1 s |

