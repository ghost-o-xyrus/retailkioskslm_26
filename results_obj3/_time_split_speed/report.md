# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s1sp_a_2b_rag_b0 | 120 | 2.65 | 85% | 413 | 345 | 89 | 28 | 446 | 346 |
| o3s1sp_a_2b_v11_b0 | 90 | 2.47 | 77% | 273 | 598 | 96 | 48 | 470 | 622 |
| o3s1sp_b_4b_rag_b0 | 120 | 1.17 | 12% | 440 | 36 | 16 | 73 | 446 | 33 |
| o3s1sp_b_4b_v11_b0 | 90 | 1.47 | 47% | 285 | 171 | 32 | 80 | 470 | 162 |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| o3s1sp_a_2b_rag_b0 | 3% (0.5 s) | 32% (6.4 s) | 28% (5.5 s) | 28% (5.6 s) | 9% (1.8 s) | 1% (0.1 s) |
| o3s1sp_a_2b_v11_b0 | 2% (0.5 s) | 18% (4.2 s) | 40% (9.4 s) | 26% (6.1 s) | 13% (3.0 s) | 0% (0.1 s) |
| o3s1sp_b_4b_rag_b0 | 4% (0.6 s) | 32% (4.8 s) | 3% (0.5 s) | 11% (1.6 s) | 49% (7.3 s) | 0% (0.1 s) |
| o3s1sp_b_4b_v11_b0 | 3% (0.6 s) | 21% (3.5 s) | 11% (1.9 s) | 18% (3.2 s) | 46% (8.0 s) | 0% (0.1 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| o3s1sp_a_2b_rag_b0 | 14.0 s [13.4 s–18.0 s] | 36.6 s | 19.2 s [15.4 s–20.9 s] | 39.5 s | 3,670 MB |
| o3s1sp_a_2b_v11_b0 | 12.8 s [8.6 s–19.6 s] | 46.3 s | 18.7 s [11.1 s–23.1 s] | 52.1 s | 4,479 MB |
| o3s1sp_b_4b_rag_b0 | 6.5 s [6.2 s–6.8 s] | 13.5 s | 10.9 s [10.4 s–11.8 s] | 27.8 s | 4,824 MB |
| o3s1sp_b_4b_v11_b0 | 7.2 s [6.5 s–8.0 s] | 20.0 s | 11.9 s [10.3 s–14.0 s] | 43.9 s | 4,105 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s1sp_a_2b_rag_b0 | 63.8 | 15.9 | 151 ms | 66.0 | -75 ms | 15.4 | 4% / 16% |
| o3s1sp_a_2b_v11_b0 | 64.0 | 15.8 | 76 ms | 64.9 | -82 ms | 15.4 | 3% / 14% |
| o3s1sp_b_4b_rag_b0 | 90.3 | 10.0 | 926 ms | 113.6 | -191 ms | 9.8 | 6% / 28% |
| o3s1sp_b_4b_v11_b0 | 83.7 | 10.0 | 954 ms | 112.6 | -166 ms | 9.8 | 11% / 55% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s1sp_a_2b_rag_b0 | 0% | 1.35 | 36 | 36 | 92 | 0 | 36 |
| o3s1sp_a_2b_v11_b0 | 0% | 1.36 | 9 | 3 | 9 | 0 | 24 |
| o3s1sp_b_4b_rag_b0 | 0% | 1.35 | 0 | 0 | 6 | 0 | 0 |
| o3s1sp_b_4b_v11_b0 | 0% | 1.36 | 0 | 0 | 0 | 0 | 0 |

## Repeat stability

| Run | Cases | First-word spread across repeats (CV), median / p90 | Identical replies | Identical tool calls |
|---|---:|---:|---:|---:|
| o3s1sp_a_2b_rag_b0 | 40 | 2% / 8% | 82% | 98% |
| o3s1sp_a_2b_v11_b0 | 30 | 1% / 3% | 90% | 100% |
| o3s1sp_b_4b_rag_b0 | 40 | 1% / 4% | 70% | 95% |
| o3s1sp_b_4b_v11_b0 | 30 | 1% / 2% | 93% | 100% |

Greedy decoding should repeat itself; if replies differ, paired comparisons in later steps carry that noise too.

## By category

**o3s1sp_a_2b_rag_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 6 | 4.00 | 2284 | 48.3 s |
| rag/faq | 12 | 2.25 | 273 | 8.6 s |
| rag/glossary | 6 | 3.00 | 404 | 13.3 s |
| rag/hinglish_spec | 6 | 3.00 | 750 | 16.3 s |
| rag/hinglish_text | 6 | 2.50 | 548 | 13.1 s |
| rag/missing_attribute | 6 | 2.50 | 798 | 16.1 s |
| rag/missing_policy | 3 | 1.00 | 19 | 0.7 s |
| rag/negative | 6 | 4.00 | 2096 | 44.1 s |
| rag/nonexistent_product | 3 | 4.00 | 1413 | 32.3 s |
| rag/not_sold | 6 | 1.00 | 18 | 0.9 s |
| rag/off_topic | 3 | 1.00 | 20 | 0.9 s |
| rag/offer | 3 | 4.00 | 464 | 17.7 s |
| rag/policy | 6 | 3.00 | 433 | 14.1 s |
| rag/product_description | 9 | 3.33 | 1137 | 29.1 s |
| rag/product_name | 9 | 2.67 | 736 | 13.1 s |
| rag/product_sku | 6 | 3.00 | 906 | 18.8 s |
| rag/product_spec | 12 | 2.25 | 715 | 13.9 s |
| rag/spec_not_listed | 3 | 2.00 | 682 | 13.3 s |
| rag/store | 3 | 2.00 | 276 | 8.1 s |
| rag/typo_spec | 6 | 2.00 | 686 | 13.1 s |

**o3s1sp_a_2b_v11_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 3 | 3.00 | 860 | 21.7 s |
| discovery | 24 | 2.75 | 1144 | 25.1 s |
| handoff | 9 | 2.67 | 592 | 14.0 s |
| hinglish | 12 | 4.00 | 1805 | 40.2 s |
| refusal | 12 | 1.50 | 196 | 3.9 s |
| tool_selection | 30 | 1.90 | 634 | 7.8 s |

**o3s1sp_b_4b_rag_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 6 | 1.00 | 592 | 6.8 s |
| rag/faq | 12 | 1.00 | 190 | 3.0 s |
| rag/glossary | 6 | 1.00 | 273 | 3.7 s |
| rag/hinglish_spec | 6 | 1.00 | 601 | 6.8 s |
| rag/hinglish_text | 6 | 1.00 | 365 | 4.7 s |
| rag/missing_attribute | 6 | 1.00 | 542 | 6.5 s |
| rag/missing_policy | 3 | 1.00 | 19 | 1.5 s |
| rag/negative | 6 | 1.00 | 568 | 6.7 s |
| rag/nonexistent_product | 3 | 1.00 | 523 | 6.2 s |
| rag/not_sold | 6 | 1.00 | 18 | 1.8 s |
| rag/off_topic | 3 | 1.00 | 20 | 1.9 s |
| rag/offer | 3 | 1.00 | 270 | 3.9 s |
| rag/policy | 6 | 1.00 | 302 | 4.1 s |
| rag/product_description | 9 | 2.22 | 1013 | 26.5 s |
| rag/product_name | 9 | 1.00 | 613 | 7.1 s |
| rag/product_sku | 6 | 2.50 | 828 | 15.6 s |
| rag/product_spec | 12 | 1.00 | 587 | 6.7 s |
| rag/spec_not_listed | 3 | 1.00 | 607 | 7.2 s |
| rag/store | 3 | 1.00 | 208 | 3.4 s |
| rag/typo_spec | 6 | 1.00 | 613 | 7.0 s |

**o3s1sp_b_4b_v11_b0**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| comparison | 3 | 1.00 | 654 | 7.6 s |
| discovery | 24 | 1.50 | 515 | 9.7 s |
| handoff | 9 | 2.00 | 502 | 17.1 s |
| hinglish | 12 | 1.25 | 719 | 6.5 s |
| refusal | 12 | 1.00 | 70 | 1.9 s |
| tool_selection | 30 | 1.60 | 423 | 7.8 s |

