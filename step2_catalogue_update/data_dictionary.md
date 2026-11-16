# Data dictionary

All data is fictional (Veyra Watch Co.). `data/clean/` is the ground truth; `data/kiosk/` has the same rows with realistic noise; `data/defects.csv` lists every difference.

## styles.csv — one row per watch design

| Column | Meaning | Values |
|---|---|---|
| style_id | Design ID | `V` + 4 digits, e.g. `V1001` |
| sub_brand | Sub-brand | Veyra Atelier, Veyra, Veyra Pulse, Veyra Nitya, Veyra Junior |
| collection | Collection name | 59 collections (20 in `data_v1`), e.g. Meridian, Workday, Shagun, Heritage, Kaleido |
| style_name | Collection + model name | e.g. Meridian Ivory |
| gender | Intended wearer | men, women, unisex, kids |
| style_tag | Occasion style | formal, casual, sport, fashion, ethnic, kids |
| movement | Movement | quartz, automatic, solar |
| display | Display type | analog, digital |
| function | Complications | e.g. `3 hands + date`, `chronograph + date` (kiosk copy may use codes like `P3H+D`) |
| case_shape | Case shape | Round, Square, Oval, Tonneau |
| case_material | Case material | Stainless Steel 316L, Stainless Steel, Titanium, Brass, Alloy, Plastic, Resin (kiosk: `SS 316L`, `SS`, `TI`) |
| case_diameter_mm | Case size | integer mm |
| case_thickness_mm | Thickness | mm, one decimal |
| glass | Crystal | Sapphire, Mineral, Acrylic (kiosk: `SAPH`, `MIN`, `ACR`) |
| water_resistance_m | Water resistance | metres (kiosk may say `10 ATM`, `100M`, `100 m / 10 bar`) |
| lume | Luminous hands/display | yes, no |
| warranty_movement_months | Movement warranty | 12 or 24 |
| warranty_battery_months | Battery warranty | 0 (automatic), 12 (quartz), 24 (solar) |
| hsn, gst_rate_pct | Tax codes | 9102 (wrist watches), 18 |
| country_of_origin | Origin | India, Switzerland |
| launch_date | Launch date | ISO date; future for pre-booking |
| status | Lifecycle | active, discontinued, pre_booking |
| staff_notes | **Internal** staff tips | never shown to customers verbatim |

## skus.csv — one row per sellable variant

| Column | Meaning |
|---|---|
| sku | Product ID: style number + case code + strap code + variant, e.g. `1001SL01` (S = steel case, L = leather strap) |
| style_id | Parent design |
| ean | 13-digit barcode in the 200–299 in-store range (never clashes with real products) |
| product_name | Display name |
| case_finish | silver, gold-tone, rose gold, black, grey, gunmetal, two-tone, multicolour |
| dial_colour | Dial or display colour (kiosk copy sometimes upper-case) |
| strap_material | leather, metal, mesh, silicone, rubber, fabric, resin (kiosk: `LTHR`, `SS bracelet`, `SIL`, `FKM`) |
| strap_colour | Strap or bracelet colour |
| mrp | Maximum retail price, rupees |
| cost_price | **Internal** cost; the kiosk must never reveal it |
| status | active, discontinued, pre_booking (a variant can be discontinued while the design is active) |
| description | 3–4 sentence marketing text written from the spec row (kiosk copy has 4 planted contradictions) |

Strap and case codes: case S steel, T titanium, B brass, A alloy, P plastic, R resin; strap L leather, M metal, N mesh, P silicone, K rubber, F fabric, R resin.

## prices_promos.csv — offers

| Column | Meaning |
|---|---|
| promo_id, name | ID and display name |
| type | percent_off, flat_off, bundle |
| value | Percent, rupees off, or bundle price |
| applies_to_type, applies_to | sub_brand or collection, and its name |
| min_mrp, max_discount | Eligibility threshold and cap (rupees) |
| start_date, end_date | Validity window (one expired, one upcoming, four live on 17 Oct 2026) |
| stackable | Whether it combines with other offers |
| conditions | Customer-facing terms |

## inventory.csv — stock per store per SKU

| Column | Meaning |
|---|---|
| store_id | ST01 (this store) to ST05 (warehouse) |
| sku | Variant |
| qty_display, qty_backroom | Units on the shop floor and in the back room |
| updated_at | Last stock sync; kiosk copy has stale timestamps (5–20 days old) on ~5% of rows |

## stores.csv

store_id, name, type (brand store, partner outlet, warehouse), distance_km from this store, hours.

## defects.csv — every injected defect

| Column | Meaning |
|---|---|
| file, key | Which file and row (style_id, sku, or `store|sku`) |
| field | Affected column |
| clean_value, kiosk_value | Before and after |
| defect_type | abbreviation, unit_format, inconsistent_case, missing, contradiction, stale_stock |

Use `missing` and `contradiction` rows to build refusal and faithfulness eval cases; `stale_stock` rows to test whether the model warns that stock data may be outdated.

## docs/ — retrieval documents

brand.md, warranty.md, returns.md, care.md (water-resistance table), service.md (prices and times), faq.md (hours, payment, engraving, holds, transfers, delivery; plus, in the large catalogue, about 50 more questions on buying, gifts, sizing, batteries, using and caring for a watch, warranty and the store visit), size_guide.md and glossary.md (large catalogue only).
