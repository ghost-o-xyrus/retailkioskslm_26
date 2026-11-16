# Scores (dev split, tools cases)

Pass = every applicable check passed. Brackets are 95% confidence intervals (Wilson).

| Run | Cases | Pass | Tool call right | Format valid | No-tool right | Facts present | No forbidden claims | Clarifies | Names a real result | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| o3s1_4b_v11_none | 60 | **85% [74-92]** | 84% [69-92] (n=37) | 100% [94-100] (n=60) | 100% [57-100] (n=5) | 84% [62-94] (n=19) | 100% [61-100] (n=6) | 100% [72-100] (n=10) | 80% [58-92] (n=20) | 0 |
| o3s1_4b_v11_b0 | 60 | **75% [63-84]** | 68% [51-80] (n=37) | 100% [94-100] (n=60) | 100% [57-100] (n=5) | 84% [62-94] (n=19) | 100% [61-100] (n=6) | 100% [72-100] (n=10) | 60% [39-78] (n=20) | 0 |
| o3s1_2b_v11_none | 60 | **70% [57-80]** | 81% [66-91] (n=37) | 100% [94-100] (n=60) | 100% [57-100] (n=5) | 74% [51-88] (n=19) | 100% [61-100] (n=6) | 60% [31-83] (n=10) | 85% [64-95] (n=20) | 0 |
| o3s1_2b_v11_b0 | 60 | **57% [44-68]** | 84% [69-92] (n=37) | 100% [94-100] (n=60) | 60% [23-88] (n=5) | 74% [51-88] (n=19) | 100% [61-100] (n=6) | 40% [17-69] (n=10) | 45% [26-66] (n=20) | 0 |

## Pass rate by category

| run | comparison (n) | discovery (n) | handoff (n) | hinglish (n) | refusal (n) | tool_selection (n) |
|---|---|---|---|---|---|---|
| o3s1_2b_v11_b0 | 100% (2) | 44% (16) | 83% (6) | 11% (9) | 75% (8) | 68% (19) |
| o3s1_2b_v11_none | 100% (2) | 62% (16) | 17% (6) | 78% (9) | 75% (8) | 84% (19) |
| o3s1_4b_v11_b0 | 50% (2) | 81% (16) | 83% (6) | 56% (9) | 88% (8) | 74% (19) |
| o3s1_4b_v11_none | 100% (2) | 81% (16) | 83% (6) | 89% (9) | 88% (8) | 84% (19) |

## Pairwise differences (same cases)

Difference = pass rate of A minus B, in percentage points, with a paired bootstrap 95% CI. If the CI includes 0, treat the two as tied.

| A | B | Cases | A − B | 95% CI | McNemar p | Different? |
|---|---|---|---|---|---|---|
| o3s1_2b_v11_b0 | o3s1_4b_v11_none | 60 | -28.3 | [-41.7, -15.0] | 0.0002 | yes |
| o3s1_2b_v11_b0 | o3s1_4b_v11_b0 | 60 | -18.3 | [-31.7, -5.0] | 0.0192 | yes |
| o3s1_2b_v11_none | o3s1_4b_v11_none | 60 | -15.0 | [-30.0, +0.0] | 0.0784 | no (tie) |
| o3s1_2b_v11_b0 | o3s1_2b_v11_none | 60 | -13.3 | [-30.0, +1.7] | 0.1516 | no (tie) |
| o3s1_4b_v11_b0 | o3s1_4b_v11_none | 60 | -10.0 | [-20.0, -1.7] | 0.0703 | yes |
| o3s1_2b_v11_none | o3s1_4b_v11_b0 | 60 | -5.0 | [-21.7, +13.3] | 0.7011 | no (tie) |
