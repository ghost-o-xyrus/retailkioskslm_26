# Step 3: teacher replies, checks

2913 tasks; 2535 replies kept, 378 rejected (template kept), 0 not written yet.

| Check | Replies |
|---|---:|
| kept | 2535 |
| missing fact | 187 |
| staff on answer | 156 |
| self-talk | 33 |
| length | 32 |
| language | 12 |
| draft fact lost | 10 |
| staff promised | 2 |
| polarity | 1 |

| Draft type | Kept | Rejected | Reasons |
|---|---:|---:|---|
| answer | 1162 | 204 | missing fact 187, staff on answer 35, length 7, language 4, self-talk 4, staff promised 2, draft fact lost 1 |
| decline:missing_policy | 44 | 0 |  |
| decline:negative | 56 | 106 | staff on answer 93, self-talk 28 |
| decline:not_sold | 4 | 0 |  |
| decline:off_topic | 2 | 0 |  |
| handoff | 96 | 0 |  |
| in_stock | 63 | 1 | staff on answer 1 |
| missing | 112 | 0 |  |
| no | 51 | 1 | polarity 1 |
| not_listed | 417 | 0 |  |
| out_of_stock | 10 | 5 | staff on answer 5 |
| refuse:discount | 33 | 0 |  |
| refuse:internal_info | 33 | 3 | staff on answer 3 |
| tools | 435 | 58 | length 25, staff on answer 19, draft fact lost 9, language 8, self-talk 1 |
| yes | 17 | 0 |  |

Rejected replies to ask the teacher for again (job o4_teacher_retry): 378 -> finetune/teacher/retry_tasks.jsonl

Tier A: 2632 examples; replies from the teacher 2535, from templates 10, dropped (neither passes the checks) 368; tool-call answers 87.

Tier B: 2632 examples; replies from the teacher 2535, from templates 10, dropped (neither passes the checks) 368; tool-call answers 87.

Review sample: 200 kept replies -> finetune/teacher/review_sample.csv (verdict: ok / reject).
