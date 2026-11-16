# Step 9a: re-ranker training data (generated from the corpus)

Generated 4302 questions; kept 3938 (3550 train, 388 gen-val held out by source chunk). Dropped: close to an eval question 342, duplicate 22.

Languages: en 3107, hinglish 831.
Templates: collection 197, faq 181, glossary 67, offer 18, policy 33, product 3091, product_description 145, product_typo 192, store 14.
Positive in the first stage's top 20: 3924/3938 = 99.6% (the re-ranker can only help when it is there).

Leakage control: eval files read only to drop generated questions with the same normalised text or word overlap >= 0.6 with any eval question (dev and test): knowledge/retrieval_eval.jsonl, eval/rag_cases.jsonl, eval/eval_set.jsonl, eval/eval_set_v1.1.jsonl, eval/eval_set_v1.2.jsonl, eval/o3_dialogues.jsonl.
