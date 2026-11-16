# Case comparison (reference: p7_2b_cpu_rag_none)

Per run: pass (v1.1 checks; rough check for retrieval questions) / tool rounds / seconds before the answer's first word / G if the gate applied. Calls are listed for the reference and the last run.

| Case | p7_2b_cpu_rag_none | p7e_2b_cpu_rag_omit | p7f_2b_cpu_rag_dedupe | Calls (p7_2b_cpu_rag_none) | Calls (p7f_2b_cpu_rag_dedupe) |
|---|---|---|---|---|---|
| R-PNM-012 | pass / 2 / 40.5 | pass / 2 / 17.3 | pass / 2 / 12.2 | search_catalogue | get_product_details |
| R-SKU-014 | pass / 2 / 9.3 | pass / 3 / 23.2 | pass / 3 / 18.6 | get_product_details | get_product_details, check_inventory |
| R-DSC-022 | pass / 2 / 9.7 | FAIL / 4 / 38.5 | pass / 4 / 31.3 | search_catalogue | search_catalogue, get_product_details, check_inventory |
| R-SPC-034 | pass / 3 / 22.6 | pass / 2 / 19.0 | pass / 2 / 13.2 | search_catalogue, get_product_details | get_product_details |
| R-SPC-035 | pass / 2 / 11.1 | pass / 2 / 19.3 | pass / 2 / 13.7 | get_product_details | get_product_details |
| R-HSP-012 | FAIL / 2 / 14.2 | pass / 2 / 19.5 | pass / 3 / 20.1 | search_catalogue | get_product_details, check_inventory |
| R-TYP-018 | FAIL / 3 / 18.2 | pass / 2 / 18.7 | pass / 2 / 13.9 | search_catalogue, get_product_details | get_product_details |
| R-NLS-009 | FAIL / 3 / 21.7 | pass / 2 / 17.5 | FAIL / 2 / 12.9 | search_catalogue, get_product_details | get_product_details |
| R-COL-013 | FAIL / 2 / 14.2 | pass / 2 / 36.2 | pass / 2 / 35.7 | search_catalogue | search_catalogue |
| R-NEG-017 | FAIL / 4 / 30.7 | pass / 3 / 36.5 | FAIL / 4 / 39.2 | search_catalogue, get_product_details, get_product_details, get_product_details | search_catalogue, get_product_details, check_inventory |
| R-NEG-020 | pass / 3 / 23.0 | pass / 2 / 20.0 | pass / 3 / 16.8 | search_catalogue, get_product_details | get_product_details, get_product_details |
| R-FAQ-020 | FAIL / 1 / 0.5 | pass / 2 / 7.8 | pass / 2 / 8.0 | - | call_staff |
| R-FAQ-037 | FAIL / 1 / 0.5 | FAIL / 1 / 1.1 G | FAIL / 1 / 1.1 G | - | - |
| R-FAQ-053 | FAIL / 1 / 0.5 | pass / 1 / 2.9 | pass / 1 / 2.9 | - | - |
| R-POL-004 | FAIL / 1 / 0.5 | FAIL / 4 / 20.4 | FAIL / 4 / 20.3 | - | call_staff, call_staff, call_staff, call_staff |
| R-GLO-012 | pass / 1 / 0.4 | FAIL / 4 / 20.7 | FAIL / 4 / 21.1 | - | call_staff, call_staff, call_staff, call_staff |
| R-OFR-007 | FAIL / 1 / 0.5 | FAIL / 4 / 18.1 | FAIL / 4 / 18.4 | - | call_staff, call_staff, call_staff, call_staff |
| R-STR-006 | FAIL / 1 / 0.5 | FAIL / 2 / 8.5 | FAIL / 2 / 8.4 | - | call_staff |
| R-HTX-005 | FAIL / 1 / 0.6 | FAIL / 1 / 3.0 | FAIL / 1 / 2.9 | - | - |
| R-NSD-003 | FAIL / 1 / 0.4 | FAIL / 1 / 1.0 G | FAIL / 1 / 1.0 G | - | - |
| R-OFF-005 | pass / 1 / 0.5 | pass / 1 / 1.0 G | pass / 1 / 1.0 G | - | - |
| R-MPO-008 | pass / 1 / 0.4 | pass / 1 / 0.7 G | pass / 1 / 0.6 G | - | - |
| R-MAT-007 | FAIL / 2 / 13.4 | FAIL / 2 / 21.4 | FAIL / 4 / 21.9 | search_catalogue | get_product_details, get_product_details, get_product_details, get_product_details |
| R-NEX-010 | FAIL / 2 / 14.0 | FAIL / 4 / 34.2 | FAIL / 4 / 34.0 | search_catalogue | search_catalogue, get_alternatives, get_alternatives, get_alternatives |

| Run | Pass | First word p50 / p90 s | Mean rounds | Hit round limit | Empty replies | Peak server RAM GB | Peak harness RAM GB | Peak total GB |
|---|---|---|---|---|---|---|---|---|
| p7_2b_cpu_rag_none | 9/24 | 9.5 / 22.6 | 1.8 | 1 | 1 | 2.34 | 0.83 | 3.17 |
| p7e_2b_cpu_rag_omit | 14/24 | 18.9 / 34.2 | 2.2 | 5 | 5 | 2.77 | 0.92 | 3.69 |
| p7f_2b_cpu_rag_dedupe | 13/24 | 13.8 / 31.3 | 2.5 | 5 | 5 | 2.83 | 0.94 | 3.77 |
