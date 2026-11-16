# Step 3: per-stage logs and the stage clock's cost

(1) coverage: 160/160 turns complete -> **met**
(2) stage times add up: 160/160 turns (100.0%) within max(5%, 5 ms); rule 99% -> **met**

## Cost of the stage clock (on against off)

| Set | Cases | Total time change, median of per-case differences [95% CI] | Rule |
|---|---:|---|---|
| o5s3_2b_rag | 40 | -746 ms [-993, -402] | met |
| o5s3_2b_v12 | 30 | -12 ms [-75, -1] | met |

(3) cost -> **met**

The clock's own measured cost per turn (median / max, ms): o5s3_2b_rag_on 0.21 / 0.47, o5s3_2b_v12_on 0.14 / 0.22, o5s3_2b_rag_seq 0.20 / 0.35, o5s3_2b_v12_seq 0.12 / 0.15

## Where the time goes (median ms per turn, by stage; a stage absent from a turn counts as 0)

| Run | input | route | retrieval | harness_tools | model_round | model_tools | checks | output |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| o5s3_2b_rag_on | 24 | 1 | 278 | 0 | 11370 | 0 | 2 | 0 |
| o5s3_2b_v12_on | 26 | 1 | 0 | 1 | 5111 | 0 | 0 | 0 |
| o5s3_2b_rag_seq | 25 | 1896 | 125 | 1 | 10717 | 0 | 1 | 0 |
| o5s3_2b_v12_seq | 23 | 1816 | 0 | 1 | 5161 | 0 | 0 | 0 |

Sequential policy (o5s3_2b_rag_seq): 11 worker starts, median start 1898.5 ms (reported; Step 8 chooses the policy).

Sequential policy (o5s3_2b_v12_seq): 11 worker starts, median start 1818.3 ms (reported; Step 8 chooses the policy).
