# SLM kiosk: mock catalogue and tools

A fictional watch brand (**Veyra Watch Co.**) with a realistic catalogue, internal-style data tables, store policy documents, and the six kiosk tools. Built for Objective 1, Step 3 of the SLM kiosk project, and reused by the eval set (Step 4), RAG (Objective 2) and tools (Objective 3).

Only the Python standard library is needed, except `demo_tool_loop.py` (needs `pip install openai`).

## What's inside

| Path | What it is |
|---|---|
| `generate_catalogue.py` | Builds everything in `data/` from a seed. Rerunning gives identical files. `--size large` (default) gives the Objective 2 catalogue; `--size small` gives the original Objective 1 catalogue. |
| `data/clean/` | Ground truth: 59 collections, 651 styles, 1,518 SKUs, 6 offers, 5 stores, stock for every SKU in every store |
| `data/kiosk/` | Same data with realistic noise: abbreviations, mixed units, missing fields, contradictions, stale stock |
| `data/defects.csv` | Every injected defect (1,838 for seed 42), for building eval cases |
| `data/docs/` | Warranty, returns, care (water-resistance guide), service prices, store FAQ (about 60 questions), size guide, glossary, brand overview |
| `data_v1/` | The original Objective 1 catalogue (103 styles, 231 SKUs, 281 defects). Use it to reproduce Objective 1: set `SLM_DATA_DIR=data_v1\kiosk` |
| `data_dictionary.md` | Every column explained |
| `tools/schemas.json` | The six core tools in OpenAI tool format (what `llama-server --jinja` accepts) |
| `tools/schemas_optional.json` | `get_offers` (add only if tool-call scores hold up) |
| `tools/mock_tools.py` | Python implementations over `data/kiosk`, with `call_tool(name, args)` for the harness |
| `tools/test_tools.py` | 19 unit tests |
| `validate.py` | Data checks: keys, EAN checksums, price ranges, enums, description-vs-spec consistency, no real brand names |
| `demo_tool_loop.py` | One customer question through a local model + the tools |
| `harness/` | Step 5: runs eval cases against `llama-server`, staged run plans, run summaries. See `harness/README.md` |
| `knowledge/` | Objective 2, Step 3: the retrieval corpus (812 chunks) built from `data/`, its builder and 8 checks. See `knowledge/README.md` |
| `eval/` | Eval set v1.0 core (150 cases) and v1.1 (370 cases), system prompts, matching rules, speed subset, validator. See `eval/README.md` |

## Quick start (Windows PowerShell)

```powershell
cd slm-kiosk-catalogue
python generate_catalogue.py          # rebuilds data/ (already included)
python generate_catalogue.py --size small --out data_v1   # rebuilds the Objective 1 catalogue
python validate.py                    # should print "All checks passed."
python -m unittest tools.test_tools   # should print "OK"
python tools\mock_tools.py            # sample search result
```

Try a real model with the tools:

```powershell
# terminal 1
.\llama-cpu\llama-server.exe -m models\qwen3.5-4b\Qwen3.5-4B-Q4_K_M.gguf --jinja -c 8192 --port 8080
# terminal 2
pip install openai
python demo_tool_loop.py "I want a formal steel watch for my dad under 15000"
```

## The brand

| Sub-brand | Segment | MRP range | Collections |
|---|---|---|---|
| Veyra Atelier | Premium, automatics, sapphire | ₹14,000–58,000 | Meridian, Tidewater, Monsoon Chrono, Lumiere |
| Veyra | Flagship | ₹3,500–16,000 | Classique, Karigari, Workday, Skyline, Slim, Solar Line |
| Veyra Pulse | Youth | ₹1,200–6,500 | Street, Neon Digital, Loop, Track |
| Veyra Nitya | Value | ₹650–3,200 | Basics, Shagun, Daily Digital, Steel Smart |
| Veyra Junior | Kids | ₹500–1,800 | Little Explorer, Glow |

The structure mirrors a large Indian watch company's portfolio (premium, flagship, youth, value, kids), but every name, product and policy is invented. Fields follow the layout of public Indian watch product pages and typical retail SKU masters.

## How the tools treat the data

- They read `data/kiosk` and **normalise on load**: `SS 316L` → Stainless Steel 316L, `10 ATM` → 100 m, `LTHR` → leather, upper-case colours → lower-case. Missing values are reported as "not listed".
- They **never return** `cost_price`, `staff_notes`, EAN or HSN.
- Discontinued items are excluded from search and alternatives; pre-booking items appear with their status.
- Errors come back as data, e.g. `{"error": "not_found", ...}`, so the model can explain instead of crashing.
- Stock older than 48 hours is flagged `stock_data_may_be_outdated`.
- `call_staff` writes requests to `data/staff_requests.log`.

The noise survives in the product **descriptions** and the raw files, which is what retrieval (Objective 2) will index. The four planted contradictions (two "sapphire" claims on mineral-glass watches, one "steel bracelet" on a leather strap, one "swimming" claim on a 30–50 m watch) are faithfulness tests: the right answer follows the spec, not the description.

## Changing things

- Different catalogue: `python generate_catalogue.py --seed 7`
- More or fewer products: edit `n` per collection in `COLLECTIONS`
- New collection or sub-brand: add an entry to `COLLECTIONS` / `SUB_BRANDS`
- Noise levels: edit the probabilities in `add_noise()`
- "Today": `REFERENCE_DATE` (controls stock staleness and which offers are live)

## When real company data arrives

Map it onto the same files in `data/kiosk/` (same column names; extra columns are ignored). The tools, retrieval and eval harness then work unchanged. Keep `data/clean/` and `defects.csv` from the mock data for the controlled experiments.

## Scale-up (Objective 2, Step 2)

The large catalogue adds 39 collections to the original 20: two or three siblings of each original collection,
with their own names, dials and options, in every sub-brand. It uses a separate random stream, so:

- the first 103 styles, 231 SKUs, 1,155 stock rows and 281 defects are byte-identical to `data_v1/`, and every
  eval v1.0 and v1.1 case still validates;
- noise is planted at the same rates in the new rows, and contradictions are scaled with size (20 in total).

Kept out on purpose, because eval v1.1 relies on their absence: smartwatches, pocket watches, clocks, rings,
solid-gold cases, and answers to the questions v1.1 treats as unanswerable (shipping abroad, foreign cards,
custom dials, cash buy-back, special orders, bulk or employee discounts, price matching, same-day delivery).
