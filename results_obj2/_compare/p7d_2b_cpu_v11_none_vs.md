# Case comparison (reference: p7d_2b_cpu_v11_none)

Per run: pass (v1.1 checks; rough check for retrieval questions) / tool rounds / seconds before the answer's first word / G if the gate applied. Calls are listed for the reference and the last run.

| Case | p7d_2b_cpu_v11_none | p7e_2b_cpu_v11_omit | p7f_2b_cpu_v11_dedupe | Calls (p7d_2b_cpu_v11_none) | Calls (p7f_2b_cpu_v11_dedupe) |
|---|---|---|---|---|---|
| DSC-003 | pass / 1 / 0.4 | pass / 1 / 1.0 G | pass / 1 / 0.9 G | - | - |
| DSC-021 | pass / 2 / 12.4 | pass / 2 / 31.2 | pass / 2 / 30.6 | search_catalogue | search_catalogue |
| DSC-023 | FAIL / 4 / 41.5 | FAIL / 2 / 28.1 G | FAIL / 2 / 26.8 G | search_catalogue, get_alternatives, get_alternatives, get_alternatives | search_catalogue |
| CMP-012 | pass / 2 / 18.4 | pass / 2 / 35.0 | pass / 3 / 23.3 | get_product_details, get_product_details | get_product_details, get_product_details, compare_products |
| TSL-009 | pass / 2 / 5.9 | pass / 2 / 8.2 G | pass / 2 / 6.6 G | check_inventory | check_inventory |
| TSL-012 | FAIL / 2 / 6.5 | FAIL / 2 / 18.6 | FAIL / 2 / 19.7 | check_inventory | check_inventory |
| TSL-032 | pass / 1 / 0.4 | pass / 1 / 1.0 G | pass / 1 / 0.9 G | - | - |
| REF-013 | FAIL / 2 / 10.0 | pass / 1 / 1.2 G | pass / 1 / 1.2 G | get_product_details | - |
| REF-014 | pass / 1 / 0.5 | pass / 1 / 3.5 | pass / 1 / 3.6 | - | - |
| HND-002 | FAIL / 2 / 5.6 | pass / 3 / 18.3 | pass / 3 / 18.1 | check_inventory | check_inventory, call_staff |
| HND-014 | pass / 2 / 5.6 | pass / 2 / 8.6 | pass / 2 / 8.3 | call_staff | call_staff |
| HIN-005 | pass / 2 / 15.5 | FAIL / 2 / 29.8 | FAIL / 2 / 29.1 | search_catalogue | search_catalogue |
| HIN-006 | pass / 2 / 14.6 | FAIL / 3 / 44.4 | FAIL / 3 / 44.8 | search_catalogue | search_catalogue, get_alternatives |
| DSC-029 | FAIL / 1 / 0.4 | FAIL / 4 / 41.5 | FAIL / 4 / 41.6 | - | search_catalogue, get_product_details, check_inventory, call_staff |
| DSC-053 | FAIL / 4 / 23.0 | FAIL / 4 / 24.1 G | FAIL / 4 / 23.7 G | search_catalogue, search_catalogue, search_catalogue, search_catalogue | search_catalogue, search_catalogue, search_catalogue, search_catalogue |
| CMP-025 | pass / 2 / 8.7 | pass / 2 / 19.1 | pass / 2 / 20.1 | compare_products | compare_products |
| TSL-077 | pass / 2 / 13.8 | FAIL / 4 / 63.1 | FAIL / 4 / 46.1 | search_catalogue | search_catalogue, get_product_details, check_inventory, get_product_details |
| REF-035 | pass / 1 / 0.5 | pass / 1 / 1.2 G | pass / 1 / 1.1 G | - | - |
| HND-020 | FAIL / 3 / 14.6 | pass / 4 / 31.1 | pass / 4 / 23.6 | get_product_details, check_inventory | get_product_details, check_inventory, call_staff |
| HIN-037 | FAIL / 2 / 9.1 | pass / 2 / 20.5 | pass / 2 / 15.8 | get_product_details | get_product_details |

| Run | Pass | First word p50 / p90 s | Mean rounds | Hit round limit | Empty replies | Peak server RAM GB | Peak harness RAM GB | Peak total GB |
|---|---|---|---|---|---|---|---|---|
| p7d_2b_cpu_v11_none | 12/20 | 8.9 / 18.4 | 2.0 | 2 | 2 | 2.63 | 0.05 | 2.68 |
| p7e_2b_cpu_v11_omit | 13/20 | 19.8 / 41.5 | 2.2 | 3 | 3 | 3.05 | 0.91 | 3.95 |
| p7f_2b_cpu_v11_dedupe | 13/20 | 19.9 / 41.6 | 2.3 | 3 | 3 | 3.26 | 0.92 | 4.17 |
