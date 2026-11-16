# Objective 5, Step 4: the app with the real models, Tier A

Stand-in mode: False

| # | Scenario | Result | Total | First word | First text on screen | First status | Model load | Stages | Cards | Peak MB | Problems |
|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Shopping question with cards | pass | 34.9 s | 27.5 s | 27.6 s | 0.04 s | 0.0 s | input route harness_tools model_round checks output | 3 | 3063 | – |
| 2 | Store question | pass | 3.4 s | 2.4 s | 2.5 s | 0.03 s | 0.0 s | input route retrieval harness_tools model_round checks output | 0 | 3076 | – |
| 3 | Another brand | pass | 0.0 s | 0.0 s | 0.0 s | 0.03 s | 0.0 s | input route output | 3 | 3076 | – |
| 4 | Custom, retrieval off | pass | 28.9 s | 23.7 s | 26.5 s | 0.00 s | 0.0 s | input route model_round checks output | 0 | 3076 | – |
| 5 | Compare O3-final and Model only | pass | 79.2 s | 0.0 s | 0.0 s | 0.00 s | 0.0 s |  |  |  | – |

Scenario 6 (Kiosk mode) is checked by hand; see the instructions.
