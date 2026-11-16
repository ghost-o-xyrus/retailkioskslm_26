# Where the time goes (Objective 3, Step 1)

Times are summed over every case of a run, so the shares say where the run's total waiting went. "First word" is the wait before the answer starts: retrieval, every tool round and the final prompt reading. Tokens "read" are prompt tokens the server actually computed (cached prefix excluded).

## Rounds and tokens per case

| Run | Cases | Rounds (mean) | Multi-round | Read: message | Read: tool outputs | Written: calls | Written: answer | Context (real) | Tool outputs (real) | Tool calls | Tokens per tool output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s3p_2b_rag_s3 | 35 | 3.29 | 100% | 502 | 224 | 116 | 69 | 456 | 183 | 2.29 | 80 |

## Time split (share of all case time)

| Run | Retrieval | Read message (+ cards) | Read tool outputs | Write tool calls | Write answer | Other (tools, HTTP, template) |
|---|---:|---:|---:|---:|---:|---:|
| o3s3p_2b_rag_s3 | 3% (0.6 s) | 14% (2.6 s) | 11% (2.0 s) | 45% (8.5 s) | 27% (5.1 s) | 1% (0.2 s) |

Each cell: share of the run's total, then the mean per case.

## Waits

| Run | First word p50 [95% CI] | First word p90 | Reply p50 [95% CI] | Reply p90 | Peak RAM, server |
|---|---:|---:|---:|---:|---:|
| o3s3p_2b_rag_s3 | 13.2 s [11.3 s–15.4 s] | 21.2 s | 17.3 s [14.1 s–23.3 s] | 30.8 s | 2,890 MB |

## Speeds and the first-word formula

| Run | Read tok/s | Write tok/s | Fit: read overhead per request | Fit: read tok/s | Fit: write overhead | Fit: write tok/s | Formula error, median / p90 |
|---|---:|---:|---:|---:|---:|---:|---:|
| o3s3p_2b_rag_s3 | 155.1 | 13.5 | 481 ms | 234.1 | -98 ms | 13.2 | 4% / 16% |

Formula: T = t_fetch + Σ tool rounds (w / v_write + n / v_read) + n_final / v_read, with the run's own v_read and v_write. Pre-registered check: the formula is good enough to plan with if its median absolute error is at most 15% on the speed runs.

## Checks

| Run | Cache misses (first request, tool-mode cases) | Context real / estimate | Repeated identical calls | call_staff beyond 1 | Shown cards re-fetched | Tool errors | Hit round limit | Empty replies (incl. fallback) | Loop-guard notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| o3s3p_2b_rag_s3 | 0% | 1.37 | 15 | 14 | 15 | 0 | 0 | 0 | 15 |

**Loop guard, forced final requests** (tool_choice none). If these read far more tokens than other tool rounds, the server dropped the tool list from the prompt and lost the prompt cache.

| Run | Forced final requests | Mean tokens read: forced final | Mean tokens read: other tool rounds |
|---|---:|---:|---:|
| o3s3p_2b_rag_s3 | 18 | 87 | 101 |

## By category

**o3s3p_2b_rag_s3**

| Category | Cases | Rounds | Tokens read | First word p50 |
|---|---:|---:|---:|---:|
| rag/collection | 2 | 2.00 | 924 | 12.2 s |
| rag/faq | 4 | 2.25 | 292 | 7.0 s |
| rag/glossary | 3 | 4.00 | 470 | 14.8 s |
| rag/hinglish_spec | 2 | 3.00 | 788 | 11.0 s |
| rag/hinglish_text | 1 | 3.00 | 772 | 9.6 s |
| rag/missing_attribute | 1 | 3.00 | 1049 | 10.3 s |
| rag/missing_policy | 1 | 4.00 | 646 | 15.2 s |
| rag/nonexistent_product | 2 | 4.00 | 945 | 14.4 s |
| rag/offer | 2 | 3.00 | 328 | 12.7 s |
| rag/policy | 2 | 3.50 | 664 | 13.6 s |
| rag/product_description | 8 | 3.75 | 960 | 21.1 s |
| rag/product_name | 3 | 3.33 | 858 | 11.3 s |
| rag/product_sku | 1 | 4.00 | 847 | 14.0 s |
| rag/product_spec | 1 | 3.00 | 855 | 11.0 s |
| rag/store | 1 | 4.00 | 296 | 18.5 s |
| rag/typo_spec | 1 | 2.00 | 807 | 8.0 s |

