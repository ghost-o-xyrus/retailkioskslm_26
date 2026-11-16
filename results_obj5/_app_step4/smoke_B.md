# Objective 5, Step 4: the app with the real models, Tier B

Stand-in mode: False

| # | Scenario | Result | Total | First word | First status | Model load | Stages | Cards | Peak MB | Problems |
|---|---|---|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Shopping question with cards | pass | 58.0 s | 17.7 s | 0.01 s | 6.6 s | input route harness_tools model_round checks output | 3 | 4725 | – |
| 2 | Store question | pass | 5.4 s | 2.5 s | 0.04 s | 0.0 s | input route retrieval harness_tools model_round checks output | 0 | 4704 | – |
| 3 | Another brand | pass | 0.0 s | 0.0 s | 0.03 s | 0.0 s | input route output | 3 | 4704 | – |
| 4 | Custom, retrieval off | pass | 22.5 s | 15.2 s | 0.01 s | 0.0 s | input route model_round checks output | 0 | 4801 | – |
| 5 | Compare O3-final and Model only | pass | 46.8 s | 0.0 s | 0.00 s | 0.0 s |  |  |  | – |

Scenario 6 (Kiosk mode) is checked by hand; see the instructions.
