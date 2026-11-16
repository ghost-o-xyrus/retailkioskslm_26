# Scores (dev split)

Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).

| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| p7d_2b_cpu_v11_none | 20 | **60% [39-78]** | 79% [52-92] (n=14) | 100% [84-100] (n=20) | 100% [21-100] (n=1) | 57% [25-84] (n=7) | 100% [34-100] (n=2) | 50% [9-91] (n=2) | 67% [30-90] (n=6) | 0 |
| p7d_2b_cpu_v11_compact_gate | 20 | **50% [30-70]** | 86% [60-96] (n=14) | 100% [84-100] (n=20) | 0% [0-79] (n=1) | 43% [16-75] (n=7) | 100% [34-100] (n=2) | 50% [9-91] (n=2) | 33% [10-70] (n=6) | 0 |
| p7d_2b_cpu_v11_full_gate | 20 | **50% [30-70]** | 79% [52-92] (n=14) | 100% [84-100] (n=20) | 0% [0-79] (n=1) | 43% [16-75] (n=7) | 100% [34-100] (n=2) | 50% [9-91] (n=2) | 50% [19-81] (n=6) | 0 |
| p7d_2b_cpu_v11_compact_chunkgate | 20 | **45% [26-66]** | 79% [52-92] (n=14) | 100% [84-100] (n=20) | 0% [0-79] (n=1) | 43% [16-75] (n=7) | 100% [34-100] (n=2) | 50% [9-91] (n=2) | 33% [10-70] (n=6) | 0 |

## Pass rate by category

| run | comparison (n) | discovery (n) | handoff (n) | hinglish (n) | refusal (n) | tool_selection (n) |
|---|---|---|---|---|---|---|
| p7d_2b_cpu_v11_compact_chunkgate | 100% (2) | 40% (5) | 67% (3) | 67% (3) | 33% (3) | 0% (4) |
| p7d_2b_cpu_v11_compact_gate | 100% (2) | 40% (5) | 100% (3) | 67% (3) | 33% (3) | 0% (4) |
| p7d_2b_cpu_v11_full_gate | 100% (2) | 40% (5) | 100% (3) | 67% (3) | 33% (3) | 0% (4) |
| p7d_2b_cpu_v11_none | 100% (2) | 40% (5) | 33% (3) | 67% (3) | 67% (3) | 75% (4) |

## Pairwise differences (same cases)

Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. If the CI includes 0, treat the two as tied.

| A | B | Cases | A − B | 95% CI | McNemar p | Different? |
|---|---|---|---|---|---|---|
| p7d_2b_cpu_v11_compact_chunkgate | p7d_2b_cpu_v11_none | 20 | -15.0 | [-40.0, +10.0] | 0.4531 | no (tie) |
| p7d_2b_cpu_v11_compact_gate | p7d_2b_cpu_v11_none | 20 | -10.0 | [-35.0, +20.0] | 0.7266 | no (tie) |
| p7d_2b_cpu_v11_full_gate | p7d_2b_cpu_v11_none | 20 | -10.0 | [-35.0, +20.0] | 0.7266 | no (tie) |
| p7d_2b_cpu_v11_compact_chunkgate | p7d_2b_cpu_v11_compact_gate | 20 | -5.0 | [-15.0, +0.0] | 1.0 | no (tie) |
| p7d_2b_cpu_v11_compact_chunkgate | p7d_2b_cpu_v11_full_gate | 20 | -5.0 | [-15.0, +0.0] | 1.0 | no (tie) |
| p7d_2b_cpu_v11_compact_gate | p7d_2b_cpu_v11_full_gate | 20 | +0.0 | [+0.0, +0.0] | 1.0 | no (tie) |
