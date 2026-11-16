# Objective 5, Step 8: in-place measurement (app and harness, same cases, alternating)

Times in seconds, medians over cases (each case: median over repeats). Overhead: app minus harness, median of per-case differences [95% bootstrap interval].

| Run | Cases | App total p50 / p90 | App first word p50 / p90 | Harness total / first | Overhead total (rule ≤5%) | Overhead first word (rule ≤0.3 s) | Writing tok/s | Peak RAM (budget) | Same reply |
|---|---:|---|---|---|---|---|---:|---|---:|
| A resident dev ×2 | 70 | 7.58 / 19.78 | 2.63 / 17.88 | 7.05 / 2.53 | 0.03 s = 0.4% [0.01, 0.05] met | 0.02 [0.01, 0.06] met | 15.42 | 3.21 GB (5 GB) met | 140/140 |
| A resident test ×1 | 68 | 6.74 / 18.90 | 3.64 / 15.80 | 7.23 / 3.43 | 0.01 s = 0.2% [-2.11, 2.27] met | 0.01 [-2.11, 2.29] met | 15.14 | 3.16 GB (5 GB) met | 68/68 |
| A sequential dev ×2 | 70 | 7.94 / 17.41 | 3.62 / 15.76 | 7.90 / 3.66 | -0.01 s = -0.1% [-0.07, 0.03] met | -0.00 [-0.05, 0.03] met | 17.025 | 2.98 GB (5 GB) met | 140/140 |
| B resident dev ×2 | 70 | 6.36 / 13.94 | 2.38 / 3.95 | 6.34 / 2.36 | 0.01 s = 0.1% [-0.00, 0.02] met | 0.00 [-0.02, 0.01] met | 9.58 | 4.76 GB (10 GB) met | 140/140 |
| B resident test ×1 | 68 | 6.16 / 13.06 | 0.89 / 4.54 | 6.62 / 0.94 | 0.02 s = 0.4% [-1.36, 1.47] met | 0.02 [-1.36, 1.46] met | 9.7 | 4.74 GB (10 GB) met | 68/68 |

## Per stage (median ms per turn, through the app) and totals by kind

| Run | input | route | retrieval | harness tools | model rounds | model tools | checks | output | total: store / tools (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A resident dev | 13 | 1 | 585 | 1 | 7748 | 2 | 1 | 0 | 8.73 / 4.31 |
| A resident test | 17 | 2 | 693 | 2 | 8085 | 3 | 1 | 0 | 8.22 / 6.06 |
| A sequential dev | 13 | 1588 | 248 | 0 | 6668 | 2 | 1 | 0 | 9.50 / 5.04 |
| B resident dev | 17 | 2 | 238 | 0 | 7484 | 0 | 2 | 0 | 6.36 / 6.57 |
| B resident test | 13 | 1 | 197 | 1 | 7347 | 0 | 1 | 0 | 4.97 / 8.22 |

**Tier A stage policy: resident** (lower median total and within 5 GB).
