# Retrieval corpus (Objective 2, Step 3)

The text the kiosk searches when it needs facts: product cards, collection overviews, policies, FAQ, glossary,
offers and stores. It is built from `data/kiosk` and `data/docs`, so it carries the same noise the kiosk sees.

```powershell
python knowledge\build_corpus.py                 # writes knowledge\corpus.jsonl and corpus_overview.csv
python -m unittest knowledge.test_corpus -v      # 8 checks
python knowledge\build_corpus.py --data data_v1 --out knowledge\v1   # the Objective 1 catalogue, if needed
```

## What's in it (seed 42, large catalogue)

| Type | Chunks | Tokens (median, range) | One chunk is |
|---|---|---|---|
| `product` | 651 | 261 (181–401) | One design: specs, every variant with its price and status, descriptions |
| `collection` | 59 | 116 (96–137) | One collection: sub-brand, style, price range, sizes, materials, dials, design names |
| `faq` | 55 | 44 (27–72) | One FAQ question and its answer |
| `policy` | 11 | 140 (36–237) | One section of warranty, returns, service, care, size guide or brand overview |
| `glossary` | 25 | 19 (11–29) | One watch term |
| `offer` | 6 | 71 (59–74) | One promotion, with whether it is running, expired or upcoming on the reference date |
| `store` | 5 | 33 (28–37) | One store: type, distance, hours |
| **Total** | **812** | about 186,000 | |

At about 186,000 tokens the corpus is more than 20 times the 8,192-token context, so the model cannot be given all of
it. That is why it needs retrieval. Five product cards cost about 1,300 prompt tokens, which matters on the CPU tier.

## Chunk format

Each line of `corpus.jsonl` holds:
- `id`: stable across rebuilds, so eval gold labels can point at it. The forms are `product:V1003`,
  `collection:meridian`, `faq:<question-slug>`, `policy:care#everyday-care`, `glossary:chronograph`,
  `offer:PR-FEST10` and `store:ST02`.
- `type`, `title` and `text`: the text is what gets embedded and shown to the model, with the title as its first line.
- `source`: the file or files it came from.
- `meta`: filters and labels. For products: `style_id`, `skus`, `sub_brand`, `collection`, `gender`, `style_tag`,
  `status`, `price_min`, `price_max`, and `in_v1` (whether the design exists in the Objective 1 catalogue).
- `tokens`: an approximate count (1.3 per word plus punctuation), used only for sizing.

## Design decisions

- **One card per design, not per SKU.** Variants of a design share every spec except dial, strap, finish and price,
  so one card answers "tell me about the Meridian Orion" and "does it come in blue?" together. A SKU code such as
  `1003SL01` still appears in its card, so keyword search can find it.
- **Normalised like the tools.** Cards are read through `tools/mock_tools.py`, so "SS 316L", "P3H+D" and "10 ATM"
  become "Stainless Steel 316L", "3 hands + date" and "100 m", exactly as the tools return them.
- **Content defects kept.** All 20 planted contradictions (for example, a description claiming sapphire crystal on a
  mineral-glass watch) stay in the description, and missing fields read "not listed". This tests whether the
  model trusts the spec lines over the marketing text, which the grounded prompt tells it to do.
- **Internal and live data left out.** Cost price, staff notes, EAN and HSN never enter the corpus. Stock levels are
  left out too, because they change by the hour and belong to `check_inventory`.
- **FAQ and glossary split finely.** One question or term per chunk gives precise matches for short questions such as
  "what is lug width?". Policy documents split at their `##` sections.
- **The brand overview's collection list is dropped**, because the 59 collection chunks cover it with more detail.

## Checks (`test_corpus.py`)

1. IDs are unique, and two builds are identical.
2. Every design, SKU, collection, FAQ question, offer, store and glossary term has its chunk.
3. Prices match the clean data.
4. No staff note, EAN or cost price appears anywhere in the corpus.
5. No abbreviation survives in product spec lines.
6. Every planted contradiction is in its product card, and every missing spec reads "not listed".
7. Product cards are at most 450 tokens, and other chunks at most 300.
8. The Objective 1 catalogue (`data_v1`) also builds, with one card per design.

# Retrieval eval set (Objective 2, Step 4)

500 customer questions, each labelled with the corpus chunks that answer it. The set was split into dev
(30%, 151 questions) and test (70%, 349 questions) before any retrieval run.

```powershell
python knowledge\build_retrieval_eval.py           # writes retrieval_eval.jsonl and retrieval_eval_overview.csv
python -m unittest knowledge.test_retrieval_eval   # 10 checks
```

## What it contains

| Answer type | Test | Dev | Subtypes |
|---|---|---|---|
| `fact`: a gold chunk holds the answer | 258 | 112 | Product by name, SKU code or description; spec questions in English, Hinglish and with typos; collections; FAQ; policy; glossary; offers; stores; Hinglish FAQ |
| `negative`: a gold chunk proves the answer is "no" | 21 | 9 | "Is there a resin Regalia?", where the collection chunk lists only its real materials |
| `not_listed`: the right card, but the field reads "not listed" | 9 | 4 | Questions about specs missing from the kiosk data |
| `none`: nothing in the corpus answers it | 61 | 26 | Off-topic, not sold here, unknown policy, unknown product attributes (weight, lug width…), nonexistent Veyra designs |

- **Answerable test questions (with gold chunks):** 288, enough for about ±3.5 points on a 90% Recall@5.
- **Unanswerable test questions:** 61, for the fallback threshold. The dev split's 26 are used to set the
  threshold; the 61 in test are used once to measure it.
- **Near-miss questions:** 83 (58 in test). Similar products exist, but the asked thing does not. These are the
  misleading-context cases from the literature, reported separately.
- **Hinglish:** 45 questions. **Typos:** 25 spec questions with a misspelt collection name.
- **Several acceptable answers:** 50 questions have more than one gold chunk. Descriptions can match up to 3
  designs, and FAQ answers are sometimes also stated in a policy section.

## Fields

`id`, `query`, `language`, `subtype`, `answer_type`, `gold_ids` (any one counts as a hit), `related_ids`
(the near-miss context a retriever will likely surface), `facts` (strings the final answer should contain,
for the end-to-end run in Step 8), `near_miss`, `split`.

## How labels are kept honest

- Product, collection and near-miss questions are **generated from the kiosk data**, so the gold chunk and the
  facts come from the same record the corpus card was built from. Description questions are kept only when
  1–3 designs match, and all matches are gold.
- FAQ, policy, glossary, offer, store, Hinglish and unanswerable questions are **hand-written as a customer
  would ask them**, not copied from the FAQ wording ("When do you close tonight?", not "What are the store hours?").
- **Every expected fact is checked against its gold chunk** when the set is built. A wrong label stops the
  build: it caught "10 mm" against a card that says "10.0 mm".
- **The unanswerable questions are checked for absence.** None of their key terms (Rolex, smartwatch, Singapore,
  loyalty, lug width, weight…) appears anywhere in the corpus. Three words do appear but never as an answer:
  "perfume" (care advice), "clasp" (the mesh-strap glossary entry, so clasp questions skip mesh-strap watches)
  and "caseback" (the engraving FAQ). These are kept as deliberate lexical traps.
- Negatives are re-checked: the asked dial colour or strap is absent from the collection chunk's own lists.

## Smoke check (dev only, not a result)

A quick keyword (BM25) search, run only to confirm the labels are findable, put a gold chunk in the top 5 for
72% of dev questions. Names and specs were near 100%. Reworded FAQ questions were about 55%, Hinglish FAQ 2 of 6,
and negatives 0 of 9, because product cards outrank the collection chunk. Those are the gaps Step 5's
embedding and hybrid retrievers have to close. The smoke check also showed that keyword search needs proper
tokenisation: a naive split turned the "'s" in "men's" into a rare word and pushed SKU cards down.
