# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| s8_2b_rag_deployed | 373 | 2.35 | 79% | 449 | 354 | 69 | 46 | – | – |
| s8_2b_v11_deployed | 292 | 2.27 | 68% | 378 | 483 | 70 | 65 | – | – |
| s8_4b_rag_deployed | 373 | 1.24 | 18% | 449 | 77 | 21 | 74 | – | – |
| s8_4b_v11_deployed | 292 | 1.57 | 46% | 380 | 183 | 31 | 90 | – | – |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| s8_2b_rag_deployed | 4% (0.6 s) | 18% (2.4 s) | 16% (2.2 s) | 36% (4.8 s) | 24% (3.2 s) | 1% (0.2 s) |
| s8_2b_v11_deployed | 3% (0.4 s) | 14% (2.0 s) | 17% (2.5 s) | 33% (4.7 s) | 31% (4.5 s) | 1% (0.2 s) |
| s8_4b_rag_deployed | 3% (0.5 s) | 32% (5.3 s) | 6% (1.0 s) | 13% (2.1 s) | 46% (7.5 s) | 0% (0.1 s) |
| s8_4b_v11_deployed | 2% (0.4 s) | 24% (4.7 s) | 12% (2.3 s) | 16% (3.1 s) | 46% (8.9 s) | 1% (0.2 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| s8_2b_rag_deployed | 7.3 s [7.1 s–7.8 s] | 18.7 s | 10.6 s [9.1 s–12.4 s] | 25.5 s | 4,247 MB |
| s8_2b_v11_deployed | 7.2 s [6.3 s–8.0 s] | 21.1 s | 11.6 s [9.7 s–14.2 s] | 27.5 s | 7,680 MB |
| s8_4b_rag_deployed | 7.1 s [7.0 s–7.3 s] | 18.2 s | 13.0 s [12.4 s–13.4 s] | 31.5 s | 5,746 MB |
| s8_4b_v11_deployed | 7.7 s [7.1 s–8.1 s] | 21.1 s | 14.6 s [12.4 s–16.2 s] | 41.5 s | 8,499 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| s8_2b_rag_deployed | 175.3 | 14.4 | 471 ms | 231.1 | -182 ms | 13.7 | 8% / 31% |
| s8_2b_v11_deployed | 193.6 | 14.7 | 498 ms | 259.7 | -87 ms | 14.4 | 8% / 45% |
| s8_4b_rag_deployed | 84.5 | 9.9 | 853 ms | 101.9 | -159 ms | 9.7 | 5% / 21% |
| s8_4b_v11_deployed | 80.8 | 10.1 | 866 ms | 100.3 | -190 ms | 9.8 | 5% / 51% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit |
|---|---:|---:|---:|---:|---:|---:|---:|
| s8_2b_rag_deployed | 0% | – | 67 | 50 | 208 | 8 | 64 |
| s8_2b_v11_deployed | 21% | – | 28 | 9 | 72 | 13 | 49 |
| s8_4b_rag_deployed | 0% | – | 6 | 0 | 16 | 0 | 5 |
| s8_4b_v11_deployed | 21% | – | 3 | 0 | 18 | 11 | 3 |

## By category

**s8_2b_rag_deployed**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 17 | 2.65 | 2080 | 16.5 s |
| rag/faq | 39 | 1.87 | 290 | 6.0 s |
| rag/glossary | 17 | 2.18 | 372 | 5.9 s |
| rag/hinglish_spec | 17 | 1.94 | 762 | 6.8 s |
| rag/hinglish_text | 14 | 1.36 | 485 | 2.5 s |
| rag/missing_attribute | 17 | 3.00 | 861 | 10.0 s |
| rag/missing_policy | 19 | 1.74 | 518 | 2.1 s |
| rag/negative | 21 | 2.90 | 1320 | 15.1 s |
| rag/nonexistent_product | 11 | 3.36 | 1378 | 17.0 s |
| rag/not_sold | 22 | 2.18 | 673 | 4.5 s |
| rag/off_topic | 16 | 1.62 | 326 | 1.8 s |
| rag/offer | 6 | 3.50 | 1194 | 16.0 s |
| rag/policy | 15 | 2.07 | 593 | 6.4 s |
| rag/product_description | 25 | 3.16 | 1340 | 22.3 s |
| rag/product_name | 28 | 2.89 | 902 | 10.9 s |
| rag/product_sku | 21 | 2.76 | 800 | 10.3 s |
| rag/product_spec | 38 | 2.29 | 732 | 7.0 s |
| rag/spec_not_listed | 9 | 2.00 | 736 | 6.9 s |
| rag/store | 4 | 1.00 | 212 | 1.5 s |
| rag/typo_spec | 17 | 2.00 | 734 | 7.0 s |

**s8_2b_v11_deployed**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 21 | 1.90 | 872 | 8.1 s |
| discovery | 47 | 2.94 | 1346 | 15.9 s |
| grounded_qa | 35 | 1.00 | 346 | 2.0 s |
| handoff | 29 | 1.97 | 379 | 5.4 s |
| hinglish | 30 | 3.23 | 1405 | 18.7 s |
| refusal | 38 | 1.76 | 368 | 3.1 s |
| tool_selection | 92 | 2.50 | 985 | 7.5 s |

**s8_4b_rag_deployed**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 17 | 1.00 | 549 | 6.7 s |
| rag/faq | 39 | 1.13 | 215 | 3.1 s |
| rag/glossary | 17 | 1.00 | 298 | 4.1 s |
| rag/hinglish_spec | 17 | 1.00 | 609 | 7.3 s |
| rag/hinglish_text | 14 | 1.07 | 394 | 5.4 s |
| rag/missing_attribute | 17 | 1.12 | 623 | 7.6 s |
| rag/missing_policy | 19 | 1.42 | 372 | 6.0 s |
| rag/negative | 21 | 1.52 | 682 | 6.9 s |
| rag/nonexistent_product | 11 | 1.36 | 631 | 7.5 s |
| rag/not_sold | 22 | 1.14 | 310 | 3.0 s |
| rag/off_topic | 16 | 1.00 | 286 | 3.4 s |
| rag/offer | 6 | 1.00 | 411 | 6.0 s |
| rag/policy | 15 | 1.07 | 397 | 4.8 s |
| rag/product_description | 25 | 2.24 | 908 | 25.3 s |
| rag/product_name | 28 | 1.14 | 624 | 7.6 s |
| rag/product_sku | 21 | 1.57 | 658 | 7.8 s |
| rag/product_spec | 38 | 1.03 | 613 | 7.4 s |
| rag/spec_not_listed | 9 | 1.00 | 603 | 7.4 s |
| rag/store | 4 | 1.00 | 212 | 3.4 s |
| rag/typo_spec | 17 | 1.47 | 888 | 8.2 s |

**s8_4b_v11_deployed**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 21 | 1.52 | 760 | 8.8 s |
| discovery | 47 | 1.55 | 689 | 7.7 s |
| grounded_qa | 35 | 1.00 | 346 | 4.8 s |
| handoff | 29 | 1.66 | 272 | 7.7 s |
| hinglish | 30 | 1.43 | 750 | 8.2 s |
| refusal | 38 | 1.42 | 269 | 5.1 s |
| tool_selection | 92 | 1.87 | 689 | 12.4 s |

