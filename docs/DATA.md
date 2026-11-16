# The fictional data

Everything the kiosk knows was generated for this project, so every answer can be checked against a known truth.
No real company's products, prices or policies are in it. The brand name in the files is invented.

## Three catalogues

| Folder | What | Size |
|---|---|---|
| `data/` | The store catalogue used from Objective 2 on | 59 collections, 651 designs, 1,518 product variants, 5 stores, 7,590 stock rows, 6 offers, 4,554 pictures, 8 store documents |
| `data_v1/` | The smaller Objective 1 catalogue; the first rows of `data/` are byte-identical to it | 103 designs, 231 variants, 281 logged defects |
| `data_train/` | A separate catalogue for Objective 4's training data; shares no product name or code with `data/` | 1,480 variants |

Each has the same layout:

| Path | What it is |
|---|---|
| `clean/` | The truth: every table without noise. Expected answers in the evaluation sets are computed from it |
| `kiosk/` | What the kiosk reads: the same tables with realistic noise (abbreviations, mixed units, missing fields, contradictions, stale stock) |
| `defects.csv` | Every planted defect with its clean value (1,838 in `data/`) |
| `docs/` | Store documents: warranty, returns, service, care, size guide, a 60-question help page, glossary, brand story |
| `meta.json` | Seed, sizes and reference date of the build |

[`data_dictionary.md`](../data_dictionary.md) explains every column.

## Tables in `data/kiosk/`

| File | Rows | One row is |
|---|---:|---|
| `styles.csv` | 651 | A design: sub-brand, collection, name, movement, case, glass, water resistance, warranty, tax code, staff-only notes |
| `skus.csv` | 1,518 | A variant of a design: product code (for example `1024SL03`), barcode, dial colour, strap, list price, cost price (never shown), status |
| `inventory.csv` | 7,590 | Stock of one variant in one store: on display, in the back room, last updated |
| `prices_promos.csv` | 6 | An offer: type, value, what it applies to, dates |
| `stores.csv` | 5 | This store, two other malls, a partner outlet, a warehouse |
| `media.csv` and `media/` | 4,554 | Front, side and back illustration of every variant |

## Rebuilding it

```powershell
python generate_catalogue.py                              # data/  (seed 42; identical files every time)
python generate_catalogue.py --size small --out data_v1   # the Objective 1 catalogue
python finetune\build_train_catalogue.py                  # data_train/
python validate.py                                        # keys, barcodes, price ranges, no real brand names
python knowledge\build_corpus.py                          # the 812 knowledge chunks from catalogue + documents
```

## What is derived from it

| Path | What |
|---|---|
| `knowledge/corpus.jsonl` | 812 chunks of store text for retrieval (documents plus catalogue descriptions) |
| `knowledge/retrieval_eval.jsonl` | 500 retrieval test questions with the chunks that answer them |
| `eval/eval_set*.jsonl` | Tool-task cases: 150 core, 370 in v1.1, 192 in the Objective 3 test set |
| `eval/rag_cases*.jsonl`, `rag_followups.jsonl` | Store questions (answerable and unanswerable) and follow-ups |
| `eval/o3_dialogues.jsonl` | Simulated shopper profiles for multi-turn dialogues |
| `eval/image_cases.jsonl` | Picture requests |
| `finetune/train/`, `finetune/examples/` | Objective 4's training questions and exported training examples |

## How the tools treat the data

- They read `data/kiosk` and normalise on load (`SS 316L` → Stainless Steel 316L, `10 ATM` → 100 m). Missing
  values are reported as "not listed".
- They never return cost price, staff notes, barcode or tax code.
- Discontinued items are left out of search; stock older than 48 hours is flagged as possibly outdated.
- Errors come back as data, so the model can explain instead of failing.

## Using real data instead

Map a real catalogue onto the same files in `data/kiosk/` (same column names; extra columns are ignored) and the
store's documents into `data/docs/`, then rebuild the knowledge chunks. The tools, retrieval, harness and app work
unchanged. Thresholds that were calibrated on this data (the retrieval fallback, the router's example sentences)
and the evaluation sets need rebuilding with the same scripts.
