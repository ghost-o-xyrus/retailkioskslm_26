# Judged rates on O3-T (Objective 3, Step 15)

Labels: 942 of 942 items. Empty replies count as declined.

| Model | Configuration | Hallucination, unanswerable | Hallucination, near-miss | Hinglish unanswerable + near-miss | Unsupported details (judged sample) | False refusals |
|---|---|---|---|---|---|---|
| Qwen3.5-2B | O3-final | 36.8% (21/57) [25.5, 49.8] | 43.9% (36/82) [33.7, 54.7] | 62.5% (15/24) [42.7, 78.8] | 18.3% (11/60) [10.6, 29.9] | 8.3% (27/324) [5.8, 11.9] |
| Qwen3.5-2B | O3-B0 | 24.6% (14/57) [15.2, 37.1] | 45.1% (37/82) [34.8, 55.9] | 25.0% (6/24) [12.0, 44.9] | 11.7% (7/60) [5.8, 22.2] | 25.9% (84/324) [21.5, 31.0] |
| Qwen3.5-4B | O3-final | 22.8% (13/57) [13.8, 35.2] | 17.1% (14/82) [10.5, 26.6] | 29.2% (7/24) [14.9, 49.2] | 6.7% (4/60) [2.6, 15.9] | 5.6% (18/324) [3.5, 8.6] |
| Qwen3.5-4B | O3-B0 | 21.1% (12/57) [12.5, 33.3] | 18.3% (15/82) [11.4, 28.0] | 25.0% (6/24) [12.0, 44.9] | 8.3% (5/60) [3.6, 18.1] | 3.4% (11/324) [1.9, 6.0] |

## O3-final against O3-B0 (same questions, unsupported or not)

| Model | Set | Questions | O3-B0 | O3-final | Change [95% CI] | McNemar p |
|---|---|---:|---:|---:|---|---:|
| Qwen3.5-2B | unanswerable | 57 | 24.6% | 36.8% | +12.3 [-1.8, +28.1] | 0.167 |
| Qwen3.5-2B | near-miss | 82 | 45.1% | 43.9% | -1.2 [-12.2, +9.8] | 1 |
| Qwen3.5-4B | unanswerable | 57 | 21.1% | 22.8% | +1.8 [-10.5, +12.3] | 1 |
| Qwen3.5-4B | near-miss | 82 | 18.3% | 17.1% | -1.2 [-9.8, +6.1] | 1 |

## Unsupported replies of O3-final by question type

| Model | Type | Unsupported | Items |
|---|---|---:|---:|
| Qwen3.5-2B | negative | 16 | 29 |
| Qwen3.5-2B | missing_attribute | 16 | 25 |
| Qwen3.5-2B | missing_policy | 10 | 19 |
| Qwen3.5-2B | not_sold | 6 | 22 |
| Qwen3.5-2B | off_topic | 5 | 16 |
| Qwen3.5-2B | spec_not_listed | 4 | 13 |
| Qwen3.5-2B | nonexistent_product | 0 | 15 |
| Qwen3.5-4B | negative | 9 | 29 |
| Qwen3.5-4B | not_sold | 6 | 22 |
| Qwen3.5-4B | missing_policy | 6 | 19 |
| Qwen3.5-4B | spec_not_listed | 3 | 13 |
| Qwen3.5-4B | missing_attribute | 2 | 25 |
| Qwen3.5-4B | off_topic | 1 | 16 |
| Qwen3.5-4B | nonexistent_product | 0 | 15 |
