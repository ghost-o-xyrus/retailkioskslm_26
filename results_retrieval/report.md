# Retrieval benchmark (Objective 2, Step 5)

Corpus: 812 chunks. Questions: 151 dev, 349 test. CPU threads: 4.

Recall@k: share of answerable questions with a gold chunk in the top k (95% CI for @5). AUROC: how well the top-1 score separates answerable from unanswerable questions (0.5 = no better than chance); this is what the Step 6 fallback threshold relies on. Latency: one question at a time, p50 / p95.

| Config | Split | R@1 | R@5 [95% CI] | R@10 | MRR@10 | AUROC | Latency p50 / p95 |
|---|---|---|---|---|---|---|---|
| hybrid-multilingual-e5-small+bge | dev | 78% | 91% [85%-95%] | 93% | 0.839 | 0.77 | 5367.8 / 7458.6 ms |
| hybrid-bge-small-en-v1.5+bge | dev | 77% | 90% [84%-94%] | 92% | 0.833 | 0.771 | 5363.0 / 7449.6 ms |
| hybrid-bge-base-en-v1.5+bge | dev | 78% | 90% [84%-94%] | 91% | 0.837 | 0.762 | 5401.4 / 7522.1 ms |
| dense-multilingual-e5-small+bge | dev | 77% | 90% [84%-94%] | 92% | 0.832 | 0.767 | 5366.5 / 7454.7 ms |
| hybrid-bge-small-en-v1.5+minilm | dev | 77% | 88% [81%-93%] | 90% | 0.823 | 0.747 | 761.8 / 1042.9 ms |
| hybrid-bge-base-en-v1.5+minilm | dev | 77% | 88% [81%-93%] | 89% | 0.822 | 0.746 | 800.6 / 1092.6 ms |
| hybrid-multilingual-e5-small+minilm | dev | 78% | 88% [81%-93%] | 90% | 0.828 | 0.749 | 761.8 / 1046.3 ms |
| dense-multilingual-e5-small+minilm | dev | 78% | 87% [80%-92%] | 89% | 0.825 | 0.751 | 763.7 / 1043.7 ms |
| bm25+bge | dev | 74% | 86% [79%-91%] | 86% | 0.800 | 0.764 | 5347.3 / 7433.0 ms |
| dense-multilingual-e5-small | dev | 68% | 84% [77%-89%] | 90% | 0.753 | 0.781 | 20.6 / 26.3 ms |
| bm25+minilm | dev | 75% | 84% [77%-89%] | 86% | 0.797 | 0.737 | 742.1 / 1020.1 ms |
| hybrid-multilingual-e5-small | dev | 63% | 83% [76%-89%] | 91% | 0.726 | 0.661 | 20.9 / 28.1 ms |
| dense-bge-base-en-v1.5+bge | dev | 69% | 80% [72%-86%] | 82% | 0.741 | 0.74 | 5416.8 / 7504.7 ms |
| dense-bge-small-en-v1.5+bge | dev | 67% | 78% [70%-84%] | 79% | 0.724 | 0.744 | 5364.3 / 7448.2 ms |
| dense-bge-base-en-v1.5+minilm | dev | 69% | 78% [70%-84%] | 79% | 0.732 | 0.74 | 825.9 / 1091.6 ms |
| hybrid-bge-base-en-v1.5 | dev | 66% | 77% [69%-83%] | 87% | 0.708 | 0.644 | 62.7 / 88.0 ms |
| bm25 | dev | 65% | 76% [68%-83%] | 82% | 0.702 | 0.662 | 0.6 / 2.1 ms |
| dense-bge-small-en-v1.5+minilm | dev | 66% | 76% [68%-83%] | 78% | 0.711 | 0.735 | 759.9 / 1036.5 ms |
| hybrid-bge-small-en-v1.5 | dev | 62% | 75% [67%-82%] | 86% | 0.674 | 0.596 | 20.4 / 28.1 ms |
| dense-bge-base-en-v1.5 | dev | 67% | 74% [66%-81%] | 80% | 0.708 | 0.655 | 67.4 / 95.5 ms |
| dense-bge-small-en-v1.5 | dev | 64% | 74% [65%-81%] | 78% | 0.683 | 0.605 | 17.8 / 22.2 ms |
| hybrid-multilingual-e5-small+bge | test | 77% | 95% [92%-97%] | 96% | 0.853 | 0.826 | 5367.8 / 7458.6 ms |
| hybrid-bge-base-en-v1.5+bge | test | 78% | 94% [91%-97%] | 97% | 0.858 | 0.827 | 5401.4 / 7522.1 ms |
| hybrid-bge-small-en-v1.5+bge | test | 79% | 94% [91%-96%] | 96% | 0.861 | 0.825 | 5363.0 / 7449.6 ms |
| hybrid-bge-base-en-v1.5+minilm | test | 81% | 93% [89%-95%] | 95% | 0.866 | 0.813 | 800.6 / 1092.6 ms |
| hybrid-multilingual-e5-small+minilm | test | 81% | 93% [89%-95%] | 96% | 0.867 | 0.812 | 761.8 / 1046.3 ms |
| dense-multilingual-e5-small+bge | test | 73% | 92% [89%-95%] | 92% | 0.821 | 0.811 | 5366.5 / 7454.7 ms |
| hybrid-bge-small-en-v1.5+minilm | test | 80% | 92% [89%-95%] | 95% | 0.860 | 0.812 | 761.8 / 1042.9 ms |
| bm25+bge | test | 75% | 91% [87%-93%] | 92% | 0.827 | 0.821 | 5347.3 / 7433.0 ms |
| dense-multilingual-e5-small+minilm | test | 79% | 91% [87%-93%] | 93% | 0.842 | 0.807 | 763.7 / 1043.7 ms |
| bm25+minilm | test | 77% | 89% [85%-92%] | 92% | 0.830 | 0.805 | 742.1 / 1020.1 ms |
| dense-bge-base-en-v1.5+bge | test | 70% | 87% [82%-90%] | 87% | 0.780 | 0.796 | 5416.8 / 7504.7 ms |
| hybrid-multilingual-e5-small | test | 66% | 86% [82%-90%] | 93% | 0.755 | 0.653 | 20.9 / 28.1 ms |
| dense-multilingual-e5-small | test | 64% | 85% [81%-89%] | 91% | 0.736 | 0.755 | 20.6 / 26.3 ms |
| dense-bge-base-en-v1.5+minilm | test | 74% | 85% [80%-89%] | 87% | 0.791 | 0.797 | 825.9 / 1091.6 ms |
| hybrid-bge-base-en-v1.5 | test | 65% | 84% [79%-88%] | 92% | 0.736 | 0.647 | 62.7 / 88.0 ms |
| dense-bge-small-en-v1.5+bge | test | 69% | 84% [79%-88%] | 84% | 0.761 | 0.789 | 5364.3 / 7448.2 ms |
| hybrid-bge-small-en-v1.5 | test | 61% | 81% [76%-85%] | 91% | 0.702 | 0.642 | 20.4 / 28.1 ms |
| dense-bge-small-en-v1.5+minilm | test | 70% | 81% [76%-85%] | 83% | 0.753 | 0.791 | 759.9 / 1036.5 ms |
| dense-bge-base-en-v1.5 | test | 64% | 77% [72%-82%] | 83% | 0.695 | 0.686 | 67.4 / 95.5 ms |
| bm25 | test | 57% | 77% [72%-81%] | 86% | 0.663 | 0.678 | 0.6 / 2.1 ms |
| dense-bge-small-en-v1.5 | test | 62% | 76% [71%-81%] | 80% | 0.682 | 0.673 | 17.8 / 22.2 ms |

## Paired differences in Recall@5 against the best dev config (hybrid-multilingual-e5-small+bge)

| Config | Dev diff [95% CI] | Test diff [95% CI] |
|---|---|---|
| bm25 | -15.2 [-22.4, -8.0] | -18.4 [-23.6, -13.5] |
| dense-bge-small-en-v1.5 | -17.6 [-25.6, -10.4] | -18.8 [-24.0, -13.9] |
| hybrid-bge-small-en-v1.5 | -16.0 [-23.2, -9.6] | -13.9 [-18.8, -9.4] |
| dense-bge-base-en-v1.5 | -16.8 [-24.0, -10.4] | -17.7 [-22.6, -12.8] |
| hybrid-bge-base-en-v1.5 | -14.4 [-21.6, -8.0] | -11.1 [-15.3, -6.9] |
| dense-multilingual-e5-small | -7.2 [-13.6, -0.8] | -9.7 [-13.9, -5.6] |
| hybrid-multilingual-e5-small | -8.0 [-14.4, -2.4] | -9.0 [-13.2, -5.2] |
| bm25+bge | -4.8 [-9.6, -0.8] | -4.5 [-7.6, -1.7] |
| dense-bge-small-en-v1.5+bge | -13.6 [-20.8, -7.2] | -11.5 [-15.6, -7.6] |
| hybrid-bge-small-en-v1.5+bge | -0.8 [-4.0, +1.6] | -1.0 [-2.8, +0.3] |
| dense-bge-base-en-v1.5+bge | -11.2 [-17.6, -4.8] | -8.3 [-12.2, -4.9] |
| hybrid-bge-base-en-v1.5+bge | -0.8 [-4.0, +1.6] | -0.7 [-1.7, +0.0] |
| dense-multilingual-e5-small+bge | -0.8 [-4.0, +2.4] | -2.8 [-5.2, -0.3] |
| bm25+minilm | -7.2 [-12.0, -3.2] | -6.2 [-9.7, -2.8] |
| dense-bge-small-en-v1.5+minilm | -15.2 [-22.4, -8.8] | -14.2 [-18.8, -10.1] |
| hybrid-bge-small-en-v1.5+minilm | -3.2 [-7.2, +0.8] | -2.8 [-5.6, +0.0] |
| dense-bge-base-en-v1.5+minilm | -13.6 [-20.0, -7.2] | -10.1 [-14.2, -6.2] |
| hybrid-bge-base-en-v1.5+minilm | -3.2 [-7.2, +0.8] | -2.4 [-4.9, +0.0] |
| dense-multilingual-e5-small+minilm | -4.0 [-8.8, +0.0] | -4.5 [-7.6, -1.4] |
| hybrid-multilingual-e5-small+minilm | -3.2 [-6.4, -0.8] | -2.4 [-5.2, +0.0] |

## Recall@5 by question type (test split; n under each heading)

| Config | collection (17) | faq (39) | glossary (17) | hinglish_spec (17) | hinglish_text (14) | lang:en (257) | lang:hinglish (31) | near_miss (30) | negative (21) | offer (6) | policy (15) | product_description (25) | product_name (28) | product_sku (21) | product_spec (38) | spec_not_listed (9) | store (4) | typo_spec (17) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hybrid-multilingual-e5-small+bge | 100% | 95% | 88% | 100% | 93% | 95% | 97% | 87% | 81% | 100% | 87% | 96% | 100% | 100% | 100% | 100% | 75% | 94% |
| hybrid-bge-small-en-v1.5+bge | 100% | 95% | 88% | 100% | 86% | 94% | 94% | 80% | 71% | 100% | 87% | 96% | 100% | 100% | 100% | 100% | 75% | 94% |
| hybrid-bge-base-en-v1.5+bge | 100% | 95% | 88% | 100% | 93% | 94% | 97% | 80% | 71% | 100% | 87% | 96% | 100% | 100% | 100% | 100% | 75% | 94% |
| dense-multilingual-e5-small+bge | 100% | 97% | 100% | 100% | 86% | 92% | 94% | 83% | 76% | 100% | 80% | 88% | 100% | 71% | 100% | 100% | 75% | 94% |
| hybrid-bge-small-en-v1.5+minilm | 100% | 97% | 94% | 100% | 71% | 93% | 87% | 67% | 52% | 100% | 93% | 96% | 100% | 100% | 100% | 100% | 75% | 82% |
| hybrid-bge-base-en-v1.5+minilm | 100% | 97% | 94% | 100% | 79% | 93% | 90% | 67% | 52% | 100% | 93% | 96% | 100% | 100% | 100% | 100% | 75% | 82% |
| hybrid-multilingual-e5-small+minilm | 100% | 97% | 94% | 100% | 71% | 93% | 87% | 70% | 57% | 100% | 93% | 96% | 100% | 100% | 100% | 100% | 75% | 82% |
| dense-multilingual-e5-small+minilm | 100% | 95% | 100% | 100% | 79% | 91% | 90% | 70% | 57% | 100% | 87% | 88% | 100% | 71% | 100% | 100% | 75% | 94% |
| bm25+bge | 94% | 72% | 88% | 100% | 93% | 90% | 97% | 77% | 67% | 100% | 80% | 100% | 100% | 100% | 100% | 100% | 75% | 94% |
| dense-multilingual-e5-small | 100% | 85% | 100% | 100% | 86% | 84% | 94% | 63% | 48% | 100% | 73% | 68% | 100% | 52% | 100% | 100% | 75% | 100% |
| bm25+minilm | 94% | 72% | 94% | 100% | 79% | 89% | 90% | 70% | 57% | 100% | 80% | 100% | 100% | 100% | 100% | 100% | 75% | 82% |
| hybrid-multilingual-e5-small | 71% | 77% | 94% | 100% | 93% | 85% | 97% | 43% | 19% | 100% | 80% | 92% | 100% | 90% | 100% | 100% | 100% | 100% |
| dense-bge-base-en-v1.5+bge | 100% | 97% | 100% | 100% | 64% | 87% | 84% | 80% | 71% | 100% | 87% | 68% | 100% | 33% | 100% | 100% | 75% | 94% |
| dense-bge-small-en-v1.5+bge | 100% | 97% | 94% | 100% | 71% | 83% | 87% | 87% | 81% | 100% | 87% | 40% | 100% | 14% | 100% | 100% | 75% | 94% |
| dense-bge-base-en-v1.5+minilm | 100% | 97% | 100% | 100% | 57% | 86% | 81% | 67% | 52% | 100% | 93% | 68% | 100% | 33% | 100% | 100% | 75% | 88% |
| hybrid-bge-base-en-v1.5 | 76% | 87% | 94% | 100% | 79% | 83% | 90% | 30% | 0% | 100% | 80% | 72% | 100% | 95% | 100% | 100% | 100% | 94% |
| bm25 | 53% | 62% | 88% | 100% | 86% | 75% | 94% | 30% | 0% | 100% | 73% | 100% | 100% | 90% | 100% | 100% | 100% | 24% |
| dense-bge-small-en-v1.5+minilm | 100% | 97% | 94% | 100% | 57% | 81% | 81% | 67% | 52% | 100% | 93% | 40% | 100% | 14% | 100% | 100% | 75% | 88% |
| hybrid-bge-small-en-v1.5 | 71% | 82% | 94% | 100% | 86% | 80% | 94% | 33% | 5% | 100% | 80% | 56% | 100% | 81% | 100% | 100% | 100% | 94% |
| dense-bge-base-en-v1.5 | 88% | 95% | 100% | 100% | 64% | 77% | 84% | 33% | 5% | 100% | 87% | 44% | 100% | 19% | 100% | 100% | 75% | 88% |
| dense-bge-small-en-v1.5 | 94% | 95% | 94% | 100% | 79% | 75% | 90% | 47% | 24% | 100% | 87% | 24% | 100% | 10% | 100% | 100% | 75% | 76% |

## Memory and build time

| Item | Value |
|---|---|
| RAM added by bge-small-en-v1.5 | 234 MB |
| RAM added by bge-base-en-v1.5 | 502 MB |
| RAM added by multilingual-e5-small | 893 MB |
| RAM added by bge-reranker-base | 1436 MB |
| RAM added by ms-marco-MiniLM-L-6-v2 | 83 MB |
| bm25_index_s | 0.09 |
| bge-small-en-v1.5_load_and_index_s | 77.8 |
| bge-base-en-v1.5_load_and_index_s | 232.1 |
| multilingual-e5-small_load_and_index_s | 101.2 |
| rerank_bge_all_s | 5990.1 |
| rerank_minilm_all_s | 764.7 |
| Re-rank only (bge), 20 candidates, median | 5347.1 ms |
| Re-rank only (minilm), 20 candidates, median | 741.5 ms |
| Process RAM at start | 437 MB |
