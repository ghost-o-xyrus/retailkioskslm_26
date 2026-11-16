# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s2_2b_rag_s2 | 151 | 2.56 | 86% | 447 | 314 | 80 | 46 | 476 | 304 |
| o3s2_2b_v12_s2 | 78 | 2.14 | 64% | 357 | 529 | 60 | 66 | 459 | 543 |
| o3s2_4b_rag_s2 | 151 | 1.25 | 17% | 447 | 47 | 17 | 73 | 476 | 43 |
| o3s2_4b_v12_s2 | 78 | 1.42 | 37% | 356 | 179 | 25 | 89 | 459 | 177 |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| o3s2_2b_rag_s2 | 4% (0.6 s) | 17% (2.3 s) | 15% (2.1 s) | 40% (5.5 s) | 23% (3.2 s) | 1% (0.2 s) |
| o3s2_2b_v12_s2 | 3% (0.4 s) | 15% (2.0 s) | 19% (2.7 s) | 29% (4.0 s) | 32% (4.5 s) | 2% (0.3 s) |
| o3s2_4b_rag_s2 | 4% (0.8 s) | 32% (5.5 s) | 4% (0.7 s) | 11% (2.0 s) | 48% (8.3 s) | 1% (0.1 s) |
| o3s2_4b_v12_s2 | 3% (0.6 s) | 23% (4.8 s) | 11% (2.3 s) | 13% (2.8 s) | 49% (10.3 s) | 2% (0.4 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| o3s2_2b_rag_s2 | 7.7 s [7.0 s–10.6 s] | 18.7 s | 13.2 s [9.7 s–15.0 s] | 24.7 s | 5,344 MB |
| o3s2_2b_v12_s2 | 7.0 s [4.7 s–8.8 s] | 21.0 s | 10.2 s [7.1 s–16.1 s] | 26.0 s | 5,733 MB |
| o3s2_4b_rag_s2 | 7.5 s [7.3 s–7.8 s] | 20.5 s | 13.5 s [12.5 s–14.6 s] | 36.6 s | 4,058 MB |
| o3s2_4b_v12_s2 | 7.7 s [6.4 s–9.5 s] | 23.2 s | 13.8 s [12.2 s–16.6 s] | 46.7 s | 5,302 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s2_2b_rag_s2 | 170.0 | 14.4 | 562 ms | 250.9 | -118 ms | 13.9 | 6% / 28% |
| o3s2_2b_v12_s2 | 189.0 | 14.8 | 609 ms | 261.8 | -88 ms | 14.5 | 11% / 54% |
| o3s2_4b_rag_s2 | 78.8 | 8.8 | 1,220 ms | 104.0 | -240 ms | 8.5 | 7% / 29% |
| o3s2_4b_v12_s2 | 75.4 | 8.7 | 1,333 ms | 102.9 | -429 ms | 8.3 | 11% / 59% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request, tool-mode cases) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s2_2b_rag_s2 | 0% | 1.36 | 45 | 35 | 108 | 1 | 33 |
| o3s2_2b_v12_s2 | 3% | 1.37 | 0 | 0 | 13 | 1 | 11 |
| o3s2_4b_rag_s2 | 0% | 1.36 | 0 | 0 | 9 | 0 | 0 |
| o3s2_4b_v12_s2 | 3% | 1.37 | 0 | 0 | 2 | 1 | 1 |

## By category

**o3s2_2b_rag_s2**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 2.62 | 1948 | 17.3 s |
| rag/faq | 16 | 2.12 | 257 | 5.9 s |
| rag/glossary | 8 | 2.75 | 389 | 6.9 s |
| rag/hinglish_spec | 8 | 2.75 | 800 | 9.2 s |
| rag/hinglish_text | 6 | 1.67 | 594 | 2.9 s |
| rag/missing_attribute | 8 | 3.00 | 886 | 10.1 s |
| rag/missing_policy | 4 | 1.75 | 193 | 1.2 s |
| rag/negative | 9 | 2.89 | 1117 | 11.0 s |
| rag/nonexistent_product | 4 | 3.75 | 1666 | 18.0 s |
| rag/not_sold | 6 | 1.33 | 58 | 1.4 s |
| rag/off_topic | 4 | 1.00 | 19 | 1.2 s |
| rag/offer | 2 | 4.00 | 425 | 15.1 s |
| rag/policy | 7 | 2.57 | 665 | 7.0 s |
| rag/product_description | 10 | 3.60 | 1191 | 21.8 s |
| rag/product_name | 12 | 3.08 | 899 | 10.8 s |
| rag/product_sku | 9 | 2.67 | 776 | 10.7 s |
| rag/product_spec | 16 | 2.31 | 749 | 7.2 s |
| rag/spec_not_listed | 4 | 2.00 | 642 | 6.8 s |
| rag/store | 2 | 3.00 | 310 | 9.9 s |
| rag/typo_spec | 8 | 2.50 | 839 | 7.1 s |

**o3s2_2b_v12_s2**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.60 | 759 | 3.8 s |
| discovery | 16 | 2.62 | 1353 | 13.7 s |
| grounded_qa | 10 | 1.00 | 336 | 2.3 s |
| handoff | 6 | 2.33 | 464 | 7.2 s |
| hinglish | 10 | 3.30 | 1715 | 20.1 s |
| refusal | 12 | 1.50 | 333 | 2.5 s |
| tool_selection | 19 | 2.21 | 862 | 7.3 s |

**o3s2_4b_rag_s2**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 8 | 1.00 | 578 | 7.4 s |
| rag/faq | 16 | 1.12 | 165 | 3.3 s |
| rag/glossary | 8 | 1.00 | 278 | 4.5 s |
| rag/hinglish_spec | 8 | 1.00 | 606 | 7.9 s |
| rag/hinglish_text | 6 | 1.00 | 433 | 6.7 s |
| rag/missing_attribute | 8 | 1.12 | 588 | 8.3 s |
| rag/missing_policy | 4 | 1.00 | 146 | 2.2 s |
| rag/negative | 9 | 1.33 | 623 | 8.4 s |
| rag/nonexistent_product | 4 | 1.00 | 568 | 7.7 s |
| rag/not_sold | 6 | 1.50 | 68 | 3.3 s |
| rag/off_topic | 4 | 1.00 | 19 | 2.4 s |
| rag/offer | 2 | 1.00 | 236 | 4.3 s |
| rag/policy | 7 | 1.00 | 371 | 5.4 s |
| rag/product_description | 10 | 2.40 | 953 | 28.1 s |
| rag/product_name | 12 | 1.25 | 625 | 7.8 s |
| rag/product_sku | 9 | 2.22 | 734 | 14.1 s |
| rag/product_spec | 16 | 1.00 | 594 | 8.0 s |
| rag/spec_not_listed | 4 | 1.00 | 569 | 7.1 s |
| rag/store | 2 | 1.00 | 184 | 3.6 s |
| rag/typo_spec | 8 | 1.00 | 638 | 8.0 s |

**o3s2_4b_v12_s2**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 5 | 1.20 | 717 | 8.4 s |
| discovery | 16 | 1.44 | 514 | 5.6 s |
| grounded_qa | 10 | 1.00 | 336 | 5.4 s |
| handoff | 6 | 1.67 | 377 | 15.2 s |
| hinglish | 10 | 1.50 | 814 | 11.3 s |
| refusal | 12 | 1.33 | 309 | 5.4 s |
| tool_selection | 19 | 1.63 | 658 | 9.8 s |

