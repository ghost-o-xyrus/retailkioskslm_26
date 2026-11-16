# Step 7 pilot (dev cases only; rough checks, not the Step 8 score)

| Run | Cases | Errors | E2E p50 / p90 s | First word p50 / p90 s | TTFT p50 s | Retrieval p50 ms | Prompt tokens | Cache reuse | Context tokens | search_knowledge used | Fallback would refuse | Rough: facts | Rough: declines | Peak RAM GB (server + harness) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| p7_2b_cpu_rag_always | 24 | 0 | 25.3 / 48.9 | 24.0 / 43.2 | 12.53 | 591 | 6030 | 82% | 452 | - | 4 | 7/12 | 2/3 | 4.00 |
| p7_2b_cpu_rag_none | 24 | 0 | 13.0 / 24.9 | 9.7 / 23.0 | 0.47 | - | 3682 | 86% | - | - | 0 | 2/12 | 2/3 | 3.17 |
| p7d_2b_cpu_rag_compact_chunkgate | 24 | 0 | 20.5 / 31.5 | 18.7 / 28.7 | 7.41 | 548 | 5428 | 86% | 227 | - | 4 | 7/12 | 2/3 | 4.88 |
| p7d_2b_cpu_rag_compact_gate | 24 | 0 | 20.7 / 38.0 | 19.0 / 32.7 | 8.42 | 561 | 5478 | 86% | 267 | - | 4 | 7/12 | 2/3 | 4.28 |
| p7d_2b_cpu_rag_full_gate | 24 | 0 | 24.1 / 39.8 | 21.4 / 38.0 | 10.93 | 537 | 5919 | 84% | 398 | - | 4 | 7/12 | 2/3 | 3.72 |
| p7d_2b_cpu_v11_compact_chunkgate | 20 | 0 | 31.7 / 53.4 | 22.3 / 42.0 | 3.75 | 552 | 7113 | 85% | 136 | - | 7 | - | - | 4.21 |
| p7d_2b_cpu_v11_compact_gate | 20 | 0 | 32.5 / 54.4 | 23.8 / 49.7 | 3.87 | 551 | 7484 | 84% | 205 | - | 7 | - | - | 5.20 |
| p7d_2b_cpu_v11_full_gate | 20 | 0 | 35.3 / 53.5 | 25.6 / 41.6 | 3.82 | 539 | 7266 | 84% | 332 | - | 7 | - | - | 4.78 |
| p7d_2b_cpu_v11_none | 20 | 0 | 17.2 / 29.7 | 9.1 / 18.4 | 0.51 | - | 4098 | 89% | - | - | 0 | - | - | 2.68 |

Flags per run (format problems): p7_2b_cpu_rag_always: {'max_rounds_reached': 4}; p7_2b_cpu_rag_none: {'max_rounds_reached': 1}; p7d_2b_cpu_rag_compact_chunkgate: {'max_rounds_reached': 3}; p7d_2b_cpu_rag_compact_gate: {'max_rounds_reached': 3}; p7d_2b_cpu_rag_full_gate: {'max_rounds_reached': 4}; p7d_2b_cpu_v11_compact_chunkgate: {'max_rounds_reached': 5}; p7d_2b_cpu_v11_compact_gate: {'max_rounds_reached': 6}; p7d_2b_cpu_v11_full_gate: {'max_rounds_reached': 4}; p7d_2b_cpu_v11_none: {'max_rounds_reached': 2}
