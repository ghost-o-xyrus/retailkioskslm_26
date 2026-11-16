# Step 5b: retriever latency variants

First stage: hybrid BM25 + BAAI/bge-small-en-v1.5 (17 ms median). Re-ranker: cross-encoder/ms-marco-MiniLM-L-6-v2. CPU threads: 4. Latency = search + re-rank, one question at a time, 60 questions.

Rule: qualifies if dev Recall@5 is tied with the baseline (torch, 512, depth 20) and at most 2 points below; the fastest qualifying variant is chosen.

| Backend | Length | Depth | Dev R@5 | Dev diff [95% CI] | Qualifies | Test R@5 [95% CI] | Test MRR | Test AUROC | Hinglish (test) | "No" answers (test) | p50 / p95 ms | RAM MB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| openvino | 256 | 5 | 75.2% | -12.8 [-19.2, -6.4] | no | 81.2% [76.3%-85.3%] | 0.741 | 0.803 | 29/31 | 1/21 | 150 / 158 | 126 |
| openvino | 512 | 5 | 75.2% | -12.8 [-19.2, -6.4] | no | 81.2% [76.3%-85.3%] | 0.753 | 0.809 | 29/31 | 1/21 | 186 / 236 | -20 |
| onnx | 256 | 5 | 75.2% | -12.8 [-19.2, -6.4] | no | 81.2% [76.3%-85.3%] | 0.741 | 0.803 | 29/31 | 1/21 | 187 / 210 | 86 |
| torch | 256 | 5 | 75.2% | -12.8 [-19.2, -6.4] | no | 81.2% [76.3%-85.3%] | 0.741 | 0.803 | 29/31 | 1/21 | 219 / 269 | -12 |
| onnx | 512 | 5 | 75.2% | -12.8 [-19.2, -6.4] | no | 81.2% [76.3%-85.3%] | 0.753 | 0.809 | 29/31 | 1/21 | 244 / 340 | 141 |
| openvino | 256 | 10 | 82.4% | -5.6 [-10.4, -1.6] | no | 88.5% [84.3%-91.7%] | 0.810 | 0.805 | 28/31 | 7/21 | 284 / 295 | 126 |
| torch | 512 | 5 | 75.2% | -12.8 [-19.2, -6.4] | no | 81.2% [76.3%-85.3%] | 0.753 | 0.809 | 29/31 | 1/21 | 286 / 424 | 7 |
| onnx | 256 | 10 | 82.4% | -5.6 [-10.4, -1.6] | no | 88.5% [84.3%-91.7%] | 0.810 | 0.805 | 28/31 | 7/21 | 352 / 390 | 86 |
| openvino | 512 | 10 | 81.6% | -6.4 [-11.2, -2.4] | no | 88.5% [84.3%-91.7%] | 0.823 | 0.810 | 28/31 | 7/21 | 382 / 495 | -20 |
| torch | 256 | 10 | 82.4% | -5.6 [-10.4, -1.6] | no | 88.5% [84.3%-91.7%] | 0.810 | 0.805 | 28/31 | 7/21 | 423 / 476 | -12 |
| openvino **chosen** | 256 | 20 | 88.0% | +0.0 [+0.0, +0.0] | yes | 92.0% [88.3%-94.6%] | 0.844 | 0.807 | 27/31 | 12/21 | 491 / 557 | 126 |
| onnx | 512 | 10 | 81.6% | -6.4 [-11.2, -2.4] | no | 88.5% [84.3%-91.7%] | 0.823 | 0.810 | 28/31 | 7/21 | 515 / 696 | 141 |
| torch | 512 | 10 | 81.6% | -6.4 [-11.2, -2.4] | no | 88.5% [84.3%-91.7%] | 0.823 | 0.810 | 28/31 | 7/21 | 613 / 768 | 7 |
| onnx | 256 | 20 | 88.0% | +0.0 [+0.0, +0.0] | yes | 92.0% [88.3%-94.6%] | 0.844 | 0.807 | 27/31 | 12/21 | 623 / 718 | 86 |
| openvino | 512 | 20 | 88.0% | +0.0 [+0.0, +0.0] | yes | 92.4% [88.7%-94.9%] | 0.860 | 0.812 | 27/31 | 11/21 | 707 / 858 | -20 |
| torch | 256 | 20 | 88.0% | +0.0 [+0.0, +0.0] | yes | 92.0% [88.3%-94.6%] | 0.844 | 0.807 | 27/31 | 12/21 | 749 / 891 | -12 |
| onnx | 512 | 20 | 88.0% | +0.0 [+0.0, +0.0] | yes | 92.4% [88.7%-94.9%] | 0.860 | 0.812 | 27/31 | 11/21 | 1001 / 1266 | 141 |
| torch | 512 | 20 | 88.0% | +0.0 [+0.0, +0.0] | yes | 92.4% [88.7%-94.9%] | 0.860 | 0.812 | 27/31 | 11/21 | 1065 / 1402 | 7 |

**Chosen:** openvino, max length 256, depth 20: test Recall@5 92.0%, MRR 0.844, p50 491 ms (misses the 300 ms target).

Skipped backends:
- onnx-int8-len512: ValueError: Unrecognized model in C:\Users\user\Downloads\SLM_work\slm-kiosk-catalogue\results_retrieval\latency\minilm-onnx. Should have a `model_type` key in its config.json, or contain one of the following st
- onnx-int8-len256: ValueError: Unrecognized model in C:\Users\user\Downloads\SLM_work\slm-kiosk-catalogue\results_retrieval\latency\minilm-onnx. Should have a `model_type` key in its config.json, or contain one of the following st
