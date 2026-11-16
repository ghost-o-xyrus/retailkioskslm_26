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
