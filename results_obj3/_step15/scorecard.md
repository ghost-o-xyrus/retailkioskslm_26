# Objective 3 success criteria: O3-final on the test set O3-T

## Tier A (Qwen3.5-2B)

| Criterion | Target | O3-final | Met | Note |
|---|---|---|---|---|
| Right tool run with valid arguments, whole system | ≥ 90% | 77.6% (149/192) | **no** |  |
| Right tool chosen by the model alone (unclear turns) | ≥ 80% | 100.0% (1/1) | – | not measurable on O3-final: the router left only 1 tool case(s) unclear; every other one went to the kiosk's own tools or a fixed reply |
| Valid arguments in model-written calls | ≥ 98% | 100.0% (464/464) | yes |  |
| Router accuracy | ≥ 95% | 94.7% (610/644) | **no** | unclear counts as right for a store question (it is retrieved) |
| Store questions sent down a tool path | ≤ 3% | 3.6% (15/414) | **no** |  |
| Slots known before the first recommendation (≥ 2 of 4) | ≥ 85% of dialogues | 100% | yes |  |
| Questions before the recommendation | ≤ 2 | max 2, mean 0.80 | yes |  |
| Shown watches fit what the customer said | ≥ 90% | 97% | yes |  |
| Staff called when asked or needed | ≥ 90% | 64% (9/14) | **no** | hand-off tool cases |
| Unneeded staff calls | ≤ 5% | 10.2% (33/324) | **no** | model staff calls on answerable store questions |
| Staff calls per turn | at most 1 | 0 turns with more than one ticket | yes | 27 repeated calls were stopped by the loop guard (no second ticket) |
| No regression on tool cases (vs no retrieval, Stage 3) | not significantly below | +0.0 [-7.8, +7.8] (tie) | yes | Step 15 reference run (Kaggle CPU) |
| Answerable store questions within 5 points of oracle cards | ≥ −5 points | +5.6 [-0.4, +11.2] | yes | Step 15 reference run (Kaggle CPU) |
| Hallucination on unanswerable questions | ≤ 5% | 36.8% (21/57) | **no** | blind judge |
| Hallucination on near-miss questions | ≤ 5% | 43.9% (36/82) | **no** | blind judge |
| False refusals | ≤ 10% | 8.3% (27/324) | yes | blind judge |
| Hallucination, Hinglish (unanswerable + near-miss) | reported | 62.5% (15/24) | – | blind judge |
| Unsupported details in answers (automatic) | ≤ 5% | 2.9% (11/378) | yes | knowledge-path replies with a detail in neither the gold card nor the tool results |
| Unsupported details in answers (judged sample) | ≤ 5% | 18.3% (11/60) | **no** | blind judge |
| Wait to first word, median / 90th percentile | ≤ 6 s / ≤ 12 s | 4.6 s / 15.5 s | **no** | in place, laptop CPU, every repeat |
| Full reply, median | ≤ 11 s | 10.1 s | yes | in place, laptop CPU, every repeat |
| Model rounds per turn, mean | ≤ 1.3 | 1.62 | **no** | store questions, tool cases and follow-ups |
| Tokens read before the answer, vs Objective 2 deployed | ≤ 50% | 43% (388 vs 894) | yes |  |
| Retrieval latency p50 (CPU) | ≤ 300 ms | 286 ms | yes | store-route turns, in place |
| Peak RAM, model server plus assistant | ≤ 5 GB | 4.04 GB | yes |  |
| RAM added over O3-B0 (assistant process) | ≤ 0.8 GB | +0.29 GB | yes | both include the retrieval stack; O3-final's re-ranker is the 8-bit one |

Met 14 of 24 decided criteria.

## Tier B (Qwen3.5-4B)

| Criterion | Target | O3-final | Met | Note |
|---|---|---|---|---|
| Right tool run with valid arguments, whole system | ≥ 90% | 83.3% (160/192) | **no** |  |
| Right tool chosen by the model alone (unclear turns) | ≥ 80% | 0.0% (0/1) | – | not measurable on O3-final: the router left only 1 tool case(s) unclear; every other one went to the kiosk's own tools or a fixed reply |
| Valid arguments in model-written calls | ≥ 98% | 100.0% (100/100) | yes |  |
| Router accuracy | ≥ 95% | 94.7% (610/644) | **no** | unclear counts as right for a store question (it is retrieved) |
| Store questions sent down a tool path | ≤ 3% | 3.6% (15/414) | **no** |  |
| Slots known before the first recommendation (≥ 2 of 4) | ≥ 85% of dialogues | 100% | yes |  |
| Questions before the recommendation | ≤ 2 | max 2, mean 0.80 | yes |  |
| Shown watches fit what the customer said | ≥ 90% | 97% | yes |  |
| Staff called when asked or needed | ≥ 90% | 64% (9/14) | **no** | hand-off tool cases |
| Unneeded staff calls | ≤ 5% | 0.9% (3/324) | yes | model staff calls on answerable store questions |
| Staff calls per turn | at most 1 | 0 turns with more than one ticket | yes | 4 repeated calls were stopped by the loop guard (no second ticket) |
| No regression on tool cases (vs no retrieval, Stage 3) | not significantly below | -4.7 [-10.9, +1.6] (tie) | yes | Step 15 reference run (Kaggle CPU) |
| Answerable store questions within 5 points of oracle cards | ≥ −5 points | -3.9 [-7.0, -0.7] | yes | Step 15 reference run (Kaggle CPU) |
| Hallucination on unanswerable questions | ≤ 5% | 22.8% (13/57) | **no** | blind judge |
| Hallucination on near-miss questions | ≤ 5% | 17.1% (14/82) | **no** | blind judge |
| False refusals | ≤ 10% | 5.6% (18/324) | yes | blind judge |
| Hallucination, Hinglish (unanswerable + near-miss) | reported | 29.2% (7/24) | – | blind judge |
| Unsupported details in answers (automatic) | ≤ 5% | 4.9% (19/384) | yes | knowledge-path replies with a detail in neither the gold card nor the tool results |
| Unsupported details in answers (judged sample) | ≤ 5% | 6.7% (4/60) | **no** | blind judge |
| Wait to first word, median / 90th percentile | ≤ 4 s / ≤ 9 s | 3.9 s / 14.5 s | **no** | laptop Vulkan quality runs, speed subset, one repeat |
| Full reply, median | ≤ 11 s | 11.9 s | **no** | laptop Vulkan quality runs, speed subset, one repeat |
| Model rounds per turn, mean | ≤ 1.3 | 1.03 | yes | store questions, tool cases and follow-ups |
| Tokens read before the answer, vs Objective 2 deployed | ≤ 50% | 57% (344 vs 604) | **no** |  |
| Peak RAM, model server plus assistant | ≤ 10 GB | 5.70 GB | yes |  |
| RAM added over O3-B0 (assistant process) | ≤ 0.8 GB | -0.34 GB | yes | both include the retrieval stack; O3-final's re-ranker is the 8-bit one |

Met 13 of 23 decided criteria.

