# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| s8sp_2b_cpu_rag_deployed | 40 | 1.93 | 65% | 402 | 198 | 38 | 35 | – | – |
| s8sp_2b_cpu_rag_none | 40 | 1.73 | 48% | 22 | 424 | 24 | 46 | – | – |
| s8sp_2b_cpu_v11_deployed | 30 | 2.17 | 67% | 407 | 457 | 61 | 80 | – | – |
| s8sp_2b_cpu_v11_none | 30 | 1.60 | 47% | 201 | 314 | 29 | 76 | – | – |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| s8sp_2b_cpu_rag_deployed | 4% (0.6 s) | 42% (6.3 s) | 22% (3.2 s) | 16% (2.4 s) | 15% (2.3 s) | 1% (0.1 s) |
| s8sp_2b_cpu_rag_none | 0% (0.0 s) | 4% (0.4 s) | 57% (6.4 s) | 13% (1.4 s) | 25% (2.8 s) | 1% (0.1 s) |
| s8sp_2b_cpu_v11_deployed | 2% (0.5 s) | 27% (6.7 s) | 32% (7.8 s) | 17% (4.2 s) | 22% (5.5 s) | 0% (0.1 s) |
| s8sp_2b_cpu_v11_none | 0% (0.0 s) | 21% (3.2 s) | 33% (4.9 s) | 12% (1.8 s) | 33% (4.9 s) | 1% (0.1 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| s8sp_2b_cpu_rag_deployed | 12.5 s [8.1 s–13.6 s] | 24.7 s | 14.0 s [9.2 s–15.0 s] | 27.6 s | 2,888 MB |
| s8sp_2b_cpu_rag_none | 0.6 s [0.5 s–13.1 s] | 21.3 s | 2.9 s [2.5 s–16.0 s] | 24.6 s | 2,339 MB |
| s8sp_2b_cpu_v11_deployed | 15.1 s [8.9 s–18.6 s] | 42.1 s | 18.7 s [12.0 s–26.1 s] | 51.5 s | 3,675 MB |
| s8sp_2b_cpu_v11_none | 6.4 s [5.7 s–11.5 s] | 23.9 s | 9.4 s [8.0 s–16.4 s] | 33.7 s | 2,910 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| s8sp_2b_cpu_rag_deployed | 63.3 | 15.6 | 156 ms | 65.4 | -62 ms | 15.2 | 2% / 13% |
| s8sp_2b_cpu_rag_none | 65.8 | 16.5 | 76 ms | 67.1 | -69 ms | 16.1 | 21% / 29% |
| s8sp_2b_cpu_v11_deployed | 59.3 | 14.5 | 272 ms | 61.8 | -110 ms | 14.2 | 6% / 18% |
| s8sp_2b_cpu_v11_none | 63.4 | 15.7 | 67 ms | 64.2 | -154 ms | 15.2 | 2% / 24% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit |
|---|---:|---:|---:|---:|---:|---:|---:|
| s8sp_2b_cpu_rag_deployed | 0% | – | 0 | 0 | 20 | 0 | 2 |
| s8sp_2b_cpu_rag_none | 0% | – | 0 | 0 | 0 | 0 | 0 |
| s8sp_2b_cpu_v11_deployed | 33% | – | 7 | 6 | 2 | 1 | 4 |
| s8sp_2b_cpu_v11_none | 40% | – | 3 | 0 | 0 | 1 | 1 |

## By category

**s8sp_2b_cpu_rag_deployed**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/faq | 5 | 1.40 | 185 | 6.9 s |
| rag/glossary | 3 | 2.00 | 391 | 11.5 s |
| rag/hinglish_spec | 3 | 1.67 | 658 | 12.0 s |
| rag/hinglish_text | 3 | 1.00 | 423 | 7.7 s |
| rag/missing_policy | 1 | 1.00 | 22 | 1.2 s |
| rag/negative | 4 | 3.25 | 1457 | 29.4 s |
| rag/nonexistent_product | 2 | 3.50 | 1350 | 29.1 s |
| rag/not_sold | 1 | 1.00 | 22 | 1.1 s |
| rag/off_topic | 5 | 1.00 | 110 | 1.1 s |
| rag/product_name | 1 | 4.00 | 964 | 24.6 s |
| rag/product_sku | 2 | 2.50 | 813 | 17.0 s |
| rag/product_spec | 7 | 2.00 | 676 | 13.1 s |
| rag/spec_not_listed | 1 | 2.00 | 697 | 13.4 s |
| rag/typo_spec | 2 | 2.00 | 760 | 14.3 s |

**s8sp_2b_cpu_rag_none**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/faq | 5 | 1.00 | 24 | 0.5 s |
| rag/glossary | 3 | 1.00 | 23 | 0.4 s |
| rag/hinglish_spec | 3 | 1.67 | 415 | 0.5 s |
| rag/hinglish_text | 3 | 1.00 | 23 | 0.5 s |
| rag/missing_policy | 1 | 1.00 | 22 | 0.4 s |
| rag/negative | 4 | 2.25 | 1005 | 18.1 s |
| rag/nonexistent_product | 2 | 2.50 | 926 | 17.4 s |
| rag/not_sold | 1 | 1.00 | 22 | 0.5 s |
| rag/off_topic | 5 | 1.00 | 20 | 0.4 s |
| rag/product_name | 1 | 2.00 | 547 | 9.4 s |
| rag/product_sku | 2 | 2.00 | 455 | 8.6 s |
| rag/product_spec | 7 | 2.43 | 834 | 19.4 s |
| rag/spec_not_listed | 1 | 3.00 | 1145 | 21.7 s |
| rag/typo_spec | 2 | 3.00 | 937 | 18.5 s |

**s8sp_2b_cpu_v11_deployed**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 3 | 1.33 | 829 | 11.6 s |
| discovery | 5 | 2.40 | 1297 | 26.9 s |
| grounded_qa | 5 | 1.00 | 392 | 5.5 s |
| handoff | 3 | 3.33 | 552 | 17.6 s |
| hinglish | 2 | 1.50 | 762 | 14.9 s |
| refusal | 4 | 2.25 | 436 | 13.6 s |
| tool_selection | 8 | 2.75 | 1258 | 25.1 s |

**s8sp_2b_cpu_v11_none**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 3 | 1.33 | 734 | 11.0 s |
| discovery | 5 | 1.40 | 547 | 0.5 s |
| grounded_qa | 5 | 1.00 | 392 | 6.1 s |
| handoff | 3 | 2.00 | 316 | 6.1 s |
| hinglish | 2 | 2.00 | 652 | 12.5 s |
| refusal | 4 | 2.00 | 328 | 6.8 s |
| tool_selection | 8 | 1.75 | 623 | 11.1 s |

