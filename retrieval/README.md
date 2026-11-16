# Retrieval (Objective 2, Step 5)

Benchmarks 21 ways of searching the kiosk corpus, on your CPU, without the language model.

| First stage (7) | Re-ranking (3 options each) |
|---|---|
| `bm25` (keyword) | none |
| `dense-bge-small-en-v1.5`, `dense-bge-base-en-v1.5`, `dense-multilingual-e5-small` (meaning) | `+bge`: BAAI/bge-reranker-base (278M parameters, multilingual) |
| `hybrid-<each of the three>` (keyword and meaning, fused) | `+minilm`: cross-encoder/ms-marco-MiniLM-L-6-v2 (22M parameters, English) |

Files: `retrievers.py` (the retrievers, reused later by the assistant), `bench_retrieval.py` (the benchmark),
`download_models.py`, `language.py` (Hinglish detector), `test_retrieval.py` (8 tests, no downloads).

## Decision rule (fixed before the run)

For each tier, choose the configuration with the highest **dev** Recall@5. If the paired 95% interval against it
includes 0, it is a tie, and the cheaper configuration wins: lower RAM first, then lower latency. The chosen
configurations' **test** numbers are the ones reported against the Objective 2 targets (Recall@5 ≥ 90%,
MRR ≥ 0.75, p50 ≤ 300 ms on CPU, ≤ 0.8 GB added RAM). Test numbers of the other configurations are shown for
completeness, not used to choose.

## Commands (PowerShell, from `slm-kiosk-catalogue`, with `slm-env` active)

See the step-by-step list in the chat message, or in short:

```powershell
pip install sentence-transformers
python -m unittest retrieval.test_retrieval
python retrieval\download_models.py
python retrieval\bench_retrieval.py --configs bm25
python retrieval\bench_retrieval.py --configs all
```

Outputs go to `results_retrieval\`: `report.md`, `summary.csv`, `run_meta.json`, and `ranks\<config>.jsonl`
(top-10 chunks and scores for every question, which Step 6 uses to set the fallback threshold).

## Step 5b: latency variants of the chosen retriever

`bench_latency.py` keeps the Step 5 choice (hybrid bge-small-en-v1.5 + MiniLM) and varies only how the re-ranker
runs: backend (torch, onnx, onnx-int8, openvino), passage length (512, 256) and re-rank depth (20, 10, 5).
**Rule, fixed before the run:** a variant qualifies if its dev Recall@5 is statistically tied with the baseline
(torch, 512, depth 20) and at most 2 points below it. The fastest qualifying variant is chosen, and its test
numbers are reported. Outputs go to `results_retrieval\latency\`.

## Step 6: refusal fallback

`calibrate_fallback.py` reads the chosen retriever's saved scores (no models needed). Below a threshold on the
top-1 re-ranker score, the kiosk skips the language model and replies "I don't have that", offering staff.
**Rule, fixed before the run:** the highest threshold whose dev false-refusal rate on answerable questions is at
most 5% (half of the 10% system budget). Test is scored once. Outputs go to `results_retrieval\fallback\`,
including `fallback.json` (threshold and messages), which Step 7 loads.

### Step 6b: Hinglish bypass (post-hoc)

The first Step 6 run refused 6/31 = 19% of answerable Hinglish test questions against 1/227 = 0.4% of English ones:
the MiniLM re-ranker is English-only and scores Hinglish low even when the right chunk is retrieved.
`--hinglish-bypass` never refuses questions that `language.py` detects as Hinglish; they go to the model instead.
The threshold is re-chosen with the same 5% dev rule. Because this was added after seeing test results, its
test numbers are labelled post-hoc. The detector's word list was written while looking at the eval questions, so
its 45/45 detection rate is not an independent measure either. Outputs go to `results_retrieval\fallback_bypass\`.

```powershell
python retrieval\calibrate_fallback.py --hinglish-bypass
```

## Step 7: the knowledge base inside the assistant

- `knowledge_base.py`: the chosen pipeline behind one call, `KnowledgeBase().retrieve(question)`. It returns the
  chunks, scores, the fallback decision (with the Hinglish bypass) and per-stage timings. It has no score cache,
  so logged latency is real.
- `check_integration.py` (Step 7a) does three things:
  1. Checks the knowledge base reproduces the Step 5b scores, so the Step 6 threshold applies.
  2. Picks k by a rule fixed before the run: on dev, the smallest k from 1 to 5 whose Recall@k is at most
     2 points below Recall@5, with at most 1,500 context tokens.
  3. Measures latency and RAM in-process.

  It writes `results_retrieval\integration\{report.md, integration.json}`; the harness reads k from the json.

```powershell
python retrieval\check_integration.py
```

## Step 7d: Tier A latency

The pilot showed the 2B on 4 CPU threads reads prompts at about 60 tokens a second. Three full chunks (about
680 real tokens) therefore cost about 11 s before it can answer. `check_context_view.py` tests two cuts on the
saved ranks, with no model:
- **compact:** product cards without the marketing description. No eval fact lives only in a description.
- **chunk gate:** only chunks at or above the fallback threshold are shown.

**Rule, fixed before the run:** among variants whose dev gold-shown rate is within 2 points of the current
setup's, the one with the fewest dev tokens is chosen. The plan `harness\plans\obj2_step7d_latency.json` then
runs the 2B on the dev pilot cases with each variant, to check that replies hold up.
