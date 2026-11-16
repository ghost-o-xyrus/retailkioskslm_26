# Step 7d, part 1: what the model is shown

k = 3, threshold -3.482, Hinglish exempt from the gate: True. Tokens are the corpus estimate; Qwen's real count is about 1.25 times higher (fitted on the Step 7 pilot).

| Variant | Dev gold shown | Dev tokens mean / p90 (all questions) | Test gold shown | Test tokens mean |
|---|---|---|---|---|
| full | 91.1% | 508 / 777 | 92.2% | 508 |
| compact **chosen** | 91.1% | 333 / 443 | 92.2% | 336 |
| full + chunk gate | 86.6% | 421 / 736 | 88.0% | 395 |
| compact + chunk gate | 86.6% | 270 / 439 | 88.0% | 259 |

Rule: fewest dev tokens among variants within 2 points of the current setup's dev gold-shown rate (91.1%). Chosen: **compact**.
Test numbers did not choose. The model runs (obj2_step7d_latency.json) check that replies hold up.
