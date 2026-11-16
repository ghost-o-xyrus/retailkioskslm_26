# Eval set v1.1 (Objective 1, Step 4)

Test cases for comparing small models on the kiosk's real job. Every expected answer is computed from `data/clean`, so nothing is hand-labelled except the wording of the questions.

- **v1.0 core:** 150 cases. Used for Stage 1 screening and Stage 2 quantization runs.
- **v1.1 total:** 370 cases (the 150 core plus a 220-case expansion), with 292 in the test split. Used for the Stage 3 head-to-head between the two finalists.

```powershell
python eval\build_eval_set.py                          # v1.0 core -> eval_set.jsonl
python eval\build_eval_v11.py                          # v1.1 -> eval_set_v1.1.jsonl (+ speed subset)
python eval\validate_eval.py                           # validate v1.0
python eval\validate_eval.py eval\eval_set_v1.1.jsonl  # validate v1.1
```

## Files

| File | What it is |
|---|---|
| `eval_set.jsonl` / `eval_set_overview.csv` | v1.0 core: 150 cases, as JSON lines and as a readable table |
| `eval_set_v1.1.jsonl` / `eval_set_v1.1_overview.csv` | v1.1: 370 cases; each case has `"set": "core"` or `"expansion"` |
| `speed_subset_ids.json` | 30 fixed core test cases for the Stage 4 speed and RAM runs on every backend |
| `system_prompts.json` | The fixed system prompts for tool mode and grounded mode |
| `checks.py` | Matching functions the harness (Step 5) and scorer (Step 6) must use |
| `build_eval_set.py` / `build_eval_v11.py` | Generators (deterministic) |
| `validate_eval.py` | Runs every expected tool call against the mock tools and checks every expected fact is reachable |

## What v1.1 adds, and why

A review against published small-model studies found three gaps in v1.0:
- **Too small to separate close models.** 106 test cases can only separate models that differ by roughly 12+ points; close rivals need about 300.
- **Too few no-tool cases.** There were only 5, but calling a tool when none is needed is a standard failure to measure.
- **Hinglish couldn't be compared directly.** Its 15 cases weren't paired with English versions of the same questions.

| Category | v1.0 | v1.1 | What was added |
|---|---|---|---|
| grounded_qa | 25 | 45 | New products and phrasings, half with noisy specs; 8 new store-policy questions (EMI, engraving, transfers, magnets, service intervals) |
| discovery | 25 | 63 | 12 vague requests, 18 fully specified searches, 8 multi-turn |
| comparison | 15 | 26 | 5 grounded pairs, 6 tool comparisons |
| tool_selection | 35 | 111 | Details, stock in/out/stale, colours, 16 new search filters, alternatives, and 12 more no-tool cases (17 in total) |
| refusal | 20 | 50 | 8 false presuppositions, 6 not-sold-here, 3 promises, 4 internal info, 3 haggling, 6 unknown IDs |
| handoff | 15 | 35 | 20 new requests across all five `call_staff` reasons |
| hinglish | 15 | 40 | 25 Hinglish translations of English core cases, each linked by `paired_with` |

**Expansion cases use products not used in the core set**, so the same watch rarely appears twice.

**Paired cases share the exact `expected` block of their English source.** This lets the language gap be measured question by question. For example: "the model passed 20/25 in English but 14/25 of the same questions in Hinglish."

**Expansion cases are 85% test, 15% dev.** Core cases keep their v1.0 split. Overall: 292 test, 78 dev.

**Fix in this version:** the v1.0 builder reused a few product pairs across comparison cases, so two grounded comparisons were exact duplicates. Every pair is now used once, and `eval_set.jsonl` was regenerated with that fix.

## Scoring runs (Step 6)

```powershell
python eval\score.py results\*_q4_k_m_vulkan                  # Stage 1, test split (default)
python eval\score.py results\*_q4_k_m_vulkan --split all      # all 150 core cases
```

This writes `results\_scores\`:
- `report.md`: pass rates with 95% CIs, per-check failure modes, per-category table, pairwise model differences
- `summary.csv`, `by_category.csv`, `pairwise.csv`
- `cases_<run>.csv`: every case with its checks and reply
- `audit_<run>.csv`: 15 random failures per run to read by hand. Mark whether the scorer was right, before trusting the numbers.

The scorer was checked on the Qwen3.5-4B pilot: it failed exactly the 4 cases a manual read had judged wrong. `python -m unittest eval.test_score` tests the statistics and every check type.

## Principles used

| Principle | Where it comes from | How it shows up here |
|---|---|---|
| Stratify by intent; enough cases per cell | Golden-set design guidance | 7 categories (15–35 cases each in v1.0, 26–111 in v1.1), with subcategories |
| Several acceptable tool calls and argument values | BFCL "possible answers" matching | `required_calls` lists options; matchers accept ranges and alternatives |
| Test when *not* to call a tool | BFCL irrelevance detection | 5 no-tool cases (greetings, off-topic, answerable from store info) |
| Unanswerable requests are a category, not an afterthought | UAEval4RAG (underspecified, false-presupposition, out-of-database) | 12 clarify cases, 5 false-presupposition, 4 out-of-database, 3 unknown IDs, 4 missing-field |
| Check the outcome *and* the required information in the reply | τ-bench (state + required outputs) | Tool cases check the call; `must_include` checks the facts in the final answer |
| Reliability, not one lucky run | τ-bench pass^k | Main scores use greedy decoding; the two finalists run the v1.1 test split 3 times at the deployment temperature and report pass^3 |
| Faithfulness to context | RAG faithfulness metrics | Noisy contexts, planted contradictions, missing fields |
| Deterministic scoring first, judge only where needed | General eval practice | 103 cases fully automatic; 47 also carry a 1–5 rubric |
| Hold out a test split; version the set | Golden-set design guidance | `split`: 44 dev / 106 test; `version: 1.0` |

**Use the dev split** to tune the system prompt and harness. **Report results on the test split only**, so prompt tuning doesn't inflate the numbers.

## Categories (v1.0 core)

| Category | n | What it tests | Mode |
|---|---|---|---|
| grounded_qa | 25 | 12 spec questions (half from abbreviated/noisy specs: `SS 316L`, `10 ATM`, `MIN`); 4 missing fields; 4 description-vs-spec contradictions; 5 store policies | Product/store info pasted, no tools |
| discovery | 25 | 12 vague requests that need clarifying questions; 9 fully specified requests → right `search_catalogue` filters; 4 multi-turn with constraints spread over turns | Tools |
| comparison | 15 | 8 two-product questions with specs pasted (which is more water resistant, cheaper and by how much, thinner…); 7 that need `compare_products` | Mixed |
| tool_selection | 35 | Details (5), stock in/out/stale (8), colour variants (3), filtered search (8), alternatives (6), no tool needed (5) | Tools |
| refusal | 20 | False presuppositions (5), not sold here (4), promises the store can't make (3), internal info (3), discount haggling (2), unknown product IDs (3) | Mixed |
| handoff | 15 | `call_staff` with the right reason: try-on, purchase, service, unanswerable question, manager/complaint | Tools |
| hinglish | 15 | Romanised Hindi + English across search, stock, details, alternatives, handoff, clarify and grounded Q&A, plus one Devanagari question | Mixed |

## Case format

```jsonc
{
  "id": "DSC-013", "version": "1.0", "split": "test",
  "category": "discovery", "subcategory": "search",
  "mode": "tools",                 // "tools": pass schemas.json; "grounded": no tools
  "language": "en",                // en | hinglish | hindi
  "difficulty": "medium",
  "messages": [{"role": "user", "content": "Formal watch for my father with a metal bracelet, budget around 15,000."}],
  "context": null,                 // text to append to the system prompt (product specs / store docs)
  "expected": {
    "behaviour": "tool_use",       // answer | answer_unknown | clarify | tool_use | no_tool_answer | refuse | handoff
    "required_calls": [            // list of OPTIONS; any one option passes; every call in it must appear
      [{"name": "search_catalogue", "args": {
          "gender": {"equals_any": ["men"]}, "style": {"equals_any": ["formal"]},
          "strap_material": {"equals_any": ["metal"]}, "price_max": {"range": [14000, 16500]}}}]
    ],
    "must_mention_tool_result": true
  },
  "rubric": ["Recommends only watches returned by the tools", "..."],
  "source": "hand-written", "notes": ""
}
```

Other `expected` keys:

| Key | Meaning |
|---|---|
| `must_include` | List of groups; each group is a list of alternatives. Every group must match the final reply. |
| `must_not_include` | Affirmative claims that must not appear (e.g. "yes, it has"), or a value the model can't know (a missing field's true value, a cost price). |
| `no_tool_calls` | The model must answer without calling any tool. |
| `clarify_slots` | For clarify cases: the reply must contain a question mentioning at least one of these slots (keywords in `checks.SLOT_KEYWORDS`). |
| `must_mention_tool_result` | The reply must name at least one product ID or name returned by the tools. |
| `computed_fact_groups` | Indices of `must_include` groups the model must calculate (e.g. a price difference), not copy. |

Argument matchers: `equals_any`, `range`, `contains_any`, `set_equals`, and `absent_or` (argument optional, but if given it must match). Arguments not listed are free: a search that also adds a sensible extra filter still passes. Check that results aren't empty in the scorer, not here.

## How Steps 5 and 6 should use it

**Harness (Step 5).** For each case:
1. Build the system prompt from `system_prompts.json`, using `tools` or `grounded`, and append `context_template` if `context` is set.
2. Send `messages`. Pass `tools/schemas.json` only in tools mode.
3. Run the tool loop with `tools.mock_tools.call_tool`, up to 4 rounds.
4. Log every tool call with its name and parsed arguments, the final reply, timings and tokens.

**Automatic scoring (Step 6).** Score each case on these checks:

| Check | Applies when | Function |
|---|---|---|
| Tool call correct | `required_calls` | `checks.calls_satisfy(calls, required_calls)` |
| Arguments valid JSON / schema | any tool call | parse + compare with `schemas.json` |
| No tool called | `no_tool_calls` | `len(calls) == 0` |
| Facts present | `must_include` | `checks.check_must_include` |
| Forbidden claims absent | `must_not_include` | `checks.check_must_not_include` |
| Asked a clarifying question | `clarify_slots` | `checks.asks_about_slots` |
| Grounded in results | `must_mention_tool_result` | reply contains an ID/name from the logged tool results |

A case passes when all applicable checks pass. Report pass rate per category and per behaviour, not just overall. The 47 rubric cases additionally get a blind 1–5 score per rubric line.

## Limits to keep in mind

- Text matching is strict. Before trusting a failure, read a sample of failed replies: a correct answer phrased unusually ("five ATM") can fail. If you widen an alternative list, bump the version.
- `must_not_include` can't understand negation. Phrases are written as affirmative claims to avoid false failures, and the rubric covers the rest.
- Uncertainty: on the 106-case v1.0 test split, only differences of roughly 12+ points between two models are reliable. On the 292-case v1.1 test split, roughly 7–8 points. Per-category numbers are much wider. Compare models question by question (paired bootstrap or McNemar), and treat differences inside the confidence interval as ties.
- The questions are written by the developer, not taken from real customers. When real kiosk logs exist, add them as `source: "production"` cases.
