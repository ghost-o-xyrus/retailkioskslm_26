# Step 9: re-ranker trial (dev retrieval questions)

Dev: 125 answerable (14 Hinglish), 26 unanswerable. Backend openvino, 256 tokens, 4 threads; latency = first stage + re-rank on 60 dev questions.
Recall computed on: local. Latency measured on: local.

Rule: p50 <= 300 ms and (Recall@3 +2 points, or Hinglish Recall@3 +5 with Recall@3 not lower) against minilm at depth 20.

| Config | R@1 | R@3 | R@3 − base [95% CI] | R@5 | MRR | R@3 Hinglish | R@3 English | p50 ms | p95 ms | Added RAM MB | Qualifies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| minilm-d20 | 76.0% | 87.2% | +0.0 [+0.0, +0.0] | 88.0% | 0.818 | 71.4% | 89.2% | 490.2 | 562.7 | 192 | baseline |
| minilm-d10 | 72.0% | 81.6% | -5.6 [-9.6, -1.6] | 82.4% | 0.771 | 71.4% | 82.9% | 261.2 | 273.7 | 192 | no |
| minilm-veyra-d20 | 77.6% | 87.2% | +0.0 [-3.2, +3.2] | 89.6% | 0.828 | 78.6% | 88.3% | 493.9 | 567.0 | 184 | no |
| minilm-veyra-d10 | 74.4% | 80.0% | -7.2 [-12.0, -3.2] | 82.4% | 0.781 | 71.4% | 81.1% | 288.8 | 331.3 | 184 | no |
| mminilm-l12-d20 | 77.6% | 86.4% | -0.8 [-5.6, +4.0] | 88.8% | 0.820 | 71.4% | 88.3% | 985.5 | 1095.2 | 816 | no |
| mminilm-l12-d10 | 74.4% | 81.6% | -5.6 [-10.4, -0.8] | 82.4% | 0.782 | 71.4% | 82.9% | 524.6 | 571.8 | 816 | no |

**No configuration qualifies: the deployed re-ranker stays.**
