# Step 7a: knowledge base check

## 1. Is it the same retriever as Step 5b?

Questions: 500. Same top-1 chunk: 500/500 = 100.0%. Top-1 score difference: median 0.0000, max 0.0000. Top-5 overlap: 100.0%. Same fallback decision: 500/500 = 100.0%.

Expected: about 100% and differences near 0.01 or less (small numeric noise between runs is normal). Large differences mean the assistant is not using the benchmarked retriever, and Step 6's threshold would not apply.

## 2. How many chunks the model sees (k)

Rule, fixed before the run: on dev, the smallest k from 1 to 5 with Recall@k at most 2 points below Recall@5, and at most 1500 context tokens. Computed from the saved Step 5b ranks.

| k | Dev Recall@k | Dev context tokens, mean / p90 | Test Recall@k |
|---|---|---|---|
| 1 | 76.0% | 170 / 298 | 78.1% |
| 2 | 84.0% | 337 / 514 | 86.8% |
| 3 **chosen** | 87.2% | 527 / 785 | 89.6% |
| 4 | 88.0% | 720 / 1026 | 89.9% |
| 5 | 88.0% | 923 / 1293 | 92.0% |

**k = 3.** Test Recall@k is shown for the record; it did not choose k.

## 3. Latency and RAM inside the assistant

Load time 77.1 s. Added RAM after loading: 804 MB; after 500 questions: 1025 MB.

| Stage | p50 ms | p90 ms |
|---|---|---|
| bm25 | 0.8 | 1.3 |
| dense | 15.0 | 18.3 |
| fuse | 0.1 | 0.1 |
| rerank | 519.2 | 576.3 |
| total | 534.8 | 592.9 |

Knowledge base settings: `{"embedder": "BAAI/bge-small-en-v1.5", "reranker": "cross-encoder/ms-marco-MiniLM-L-6-v2", "backend": "openvino", "max_length": 256, "depth": 20, "k": 3, "max_context_tokens": 1500, "threshold": -3.481874465942383, "hinglish_bypass": true, "fallback_file": "results_retrieval\\fallback_bypass\\fallback.json"}`
