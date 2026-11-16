# Objective 5, Step 4: streamed against non-streamed replies

Each model request was sent both ways; the turn went on with the non-streamed reply.

| Run | Cases | Identical cases | Requests with tools on: identical | Last rounds (tools off): identical | Different cases |
|---|---:|---:|---:|---:|---|
| o5s4_2b_v12_stream | 30 | 30 | 6/6 | 19/19 | – |
| o5s4_4b_v12_stream | 30 | 30 | 10/10 | 38/38 | – |

**Rule:** identical on every tool case for both models → every round streams; otherwise only rounds that cannot call tools stream.

**Decision:** every model round streams.
