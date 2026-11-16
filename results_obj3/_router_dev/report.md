# Router check (dev split, rules + bge-small prototypes)

| Measure | Value | Target |
|---|---:|---|
| Messages | 211 | |
| Accuracy (route = label; unclear counts as wrong) | 205/211 = 97.2% | ≥ 95% |
| Retrieval decision right | 207/211 = 98.1% | |
| Store questions sent down a no-retrieval path | 3/142 = 2.1% | ≤ 3% |
| Other messages given retrieval anyway | 1/69 = 1.4% | |
| Unclear (Objective 2 path) | 1/211 = 0.5% | |
| Latency p50 / p95 | 0.20 / 0.33 ms | p50 < 20 ms |
| Decided by | {'rule': 209, 'prototype': 2} | |

**Verdict: PASS** against the pre-registered rule.

## Confusion (rows = label, columns = route)

| Label | lookup | stock | compare | shopping | staff | chat | store | unclear | Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| lookup | 14 | 1 |  |  |  |  |  |  | 93.3% (15) |
| stock |  | 7 |  |  |  |  |  |  | 100.0% (7) |
| compare |  |  | 2 |  |  |  |  |  | 100.0% (2) |
| shopping |  |  |  | 36 |  |  | 1 |  | 97.3% (37) |
| staff |  |  |  |  | 5 |  |  |  | 100.0% (5) |
| chat |  |  |  |  |  | 3 |  |  | 100.0% (3) |
| store | 1 |  |  | 2 |  |  | 138 | 1 | 97.2% (142) |

## By set

| Set | Messages | Accuracy | Retrieval decision |
|---|---:|---:|---:|
| retrieval | 151 | 98.7% | 99.3% |
| v1.2 | 60 | 93.3% | 95.0% |

## Misroutes (6)

| Case | Category | Label | Route | Source | Message |
|---|---|---|---|---|---|
| R-OFF-006 | rag/off_topic | store | unclear | prototype | Tell me a joke. |
| R-POL-019 | rag/policy | store | shopping | rule | I want a watch thin enough to fit under my shirt cuff. |
| REF-007 | refusal/out_of_database | store | shopping | rule | Do you have a smartwatch that counts steps and shows notifications? |
| REF-019 | refusal/not_found | lookup | stock | rule | Is 9999SL01 in stock? |
| REF-038 | refusal/internal_info | store | lookup | prototype | What did the store pay for 1479PP03? |
| TSL-077 | tool_selection/search_filter | shopping | store | rule | Show me everything in the Karigari collection. |
