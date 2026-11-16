# Step 12: retrieval speed and RAM (dev)

Machine: local (Intel64 Family 6 Model 154 Stepping 3, GenuineIntel, 16 logical cores). Each configuration ran in a fresh process; wait = the whole retrieval call over 60 dev questions after a warm-up. Re-rank depth 20.

Rule: Recall@3 at most 1 point below base (4 threads); lowest p50; within 5% of the best p50, lower RAM. Targets (reported): p50 <= 300 ms, added RAM <= 800 MB.

| Config | R@1 | R@3 | R@3 − base [95% CI] | R@5 | R@3 Hinglish | p50 ms | p95 ms | Added RAM MB | Load s | PyTorch | Qualifies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| rt-fp32-l256-full-t4 | 76.0% | 87.2% | +0.0 [+0.0, +0.0] | 88.0% | 71.4% | 538.3 | 565.9 | 675 | 58.9 | no | yes |
| rt-fp32-l256-full-t8 | 76.0% | 87.2% | +0.0 [+0.0, +0.0] | 88.0% | 71.4% | 490.7 | 526.2 | 679 | 53.5 | no | yes |
| rt-fp32-l128-compact-t4 | 74.4% | 80.0% | -7.2 [-12.8, -2.4] | 84.8% | 71.4% | 247.1 | 259.4 | 673 | 56.0 | no | no |
| rt-fp32-l128-compact-t8 | 74.4% | 80.0% | -7.2 [-12.8, -2.4] | 84.8% | 71.4% | 243.6 | 254.3 | 677 | 52.8 | no | no |
| base-t4 | 76.0% | 87.2% | +0.0 [+0.0, +0.0] | 88.0% | 71.4% | 462.5 | 972.7 | 840 | 111.9 | yes | yes |
| base-t8 | 76.0% | 87.2% | +0.0 [+0.0, +0.0] | 88.0% | 71.4% | 597.0 | 656.4 | 806 | 78.3 | yes | yes |
| rt-int8s-l256-full-t4 | 76.8% | 88.0% | +0.8 [+0.0, +2.4] | 88.8% | 78.6% | 230.0 | 309.6 | 638 | 57.2 | no | yes |
| rt-int8s-l256-full-t8 | 76.8% | 88.0% | +0.8 [+0.0, +2.4] | 88.8% | 78.6% | 311.8 | 342.3 | 647 | 63.2 | no | yes |
| rt-int8w-l256-full-t4 | 76.0% | 87.2% | +0.0 [+0.0, +0.0] | 88.0% | 71.4% | 315.6 | 356.3 | 563 | 57.0 | no | yes |
| rt-int8w-l256-full-t8 | 76.0% | 87.2% | +0.0 [+0.0, +0.0] | 88.0% | 71.4% | 439.4 | 467.9 | 565 | 63.0 | no | yes |

**Chosen: rt-int8s-l256-full-t4** (p50 230.0 ms: target met; added RAM 638 MB: target met).
