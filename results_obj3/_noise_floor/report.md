# Noise floor: identical greedy repeats (Objective 3, Step 2)

Pass/fail from the automatic checks. Flip rate = cases whose outcome is not the same in every repeat. Noise bound = 1.96 × √(d / n): the pass-rate difference that repeat noise alone stays under 95% of the time, for n cases with discordance d.

| Run | Model | Set | Cases × repeats | Pass rate per repeat | Reply text changed | Flip rate | Discordance d | Noise bound, this subset | Noise bound, full dev |
|---|---|---|---:|---|---:|---:|---:|---:|---:|
| o3s1sp_a_2b_rag_b0 | Qwen3.5-2B | rag | 36 × 3 | 44.4% / 47.2% / 47.2% | 19% | 2.8% | 1.9% | ±4.4 pts | ±2.2 pts (n=151) |
| o3s1sp_a_2b_v11_b0 | Qwen3.5-2B | tools | 30 × 3 | 56.7% / 56.7% / 56.7% | 10% | 0.0% | 0.0% | ±0.0 pts | ±0.0 pts (n=60) |
| o3s1sp_b_4b_rag_b0 | Qwen3.5-4B | rag | 36 × 3 | 86.1% / 83.3% / 83.3% | 28% | 2.8% | 1.9% | ±4.4 pts | ±2.2 pts (n=151) |
| o3s1sp_b_4b_v11_b0 | Qwen3.5-4B | tools | 30 × 3 | 76.7% / 76.7% / 76.7% | 7% | 0.0% | 0.0% | ±0.0 pts | ±0.0 pts (n=60) |

Rule for later steps: a dev difference counts only if it is larger than the full-dev noise bound for that model and set, and its paired bootstrap interval excludes 0.

