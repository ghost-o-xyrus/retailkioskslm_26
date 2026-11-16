# Step 13b: speculative decoding (dev speed subset, greedy)

Rule: identical replies at least as often as plain decoding agrees with itself (none2); median writing-speed ratio ≥ 1.2; first word and total reply time not significantly later. Lowest median total time wins.

## o3s13b_a_2b

Plain decoding agrees with itself on 67/70 cases.

| Config | Cases | Identical | Writing speed ratio [95% CI] | First word change s [95% CI] | Total change s [95% CI] | Acceptance | Peak RAM MB | Qualifies |
|---|---:|---:|---|---|---|---:|---:|---|
| mtp2 | 70 | 49 (70%) | 1.02× [0.99, 1.04] | -0.00 [-0.07, +0.03] | -0.00 [-0.05, +0.12] | 82% | 2511 | no |
| mtp6 | 70 | 49 (70%) | 0.84× [0.75, 0.89] | +0.11 [+0.01, +0.33] | +1.57 [+1.09, +1.90] | 54% | 2592 | no |
| mtpfile | 70 | 67 (96%) | 1.03× [1.01, 1.04] | -0.11 [-0.19, -0.01] | -0.13 [-0.36, -0.03] | – | 2261 | (file check: same replies) |
| ngram-mod | 70 | 56 (80%) | 0.97× [0.91, 1.01] | -0.01 [-0.11, +0.00] | -0.00 [-0.01, +0.34] | 23% | 2383 | no |
| ngram-simple | 70 | 62 (89%) | 0.97× [0.94, 1.03] | +0.00 [-0.01, +0.29] | +0.00 [-0.01, +0.79] | 28% | 2336 | no |
| none2 | 70 | 67 (96%) | 1.01× [0.99, 1.03] | -0.01 [-0.11, +0.05] | -0.01 [-0.27, -0.00] | – | 2260 | (reference) |

**No candidate qualifies: plain decoding stays.**

- mtp2: replies differ on rag:R-DSC-001, rag:R-DSC-021, rag:R-FAQ-020, rag:R-HSP-018, rag:R-HTX-012, rag:R-MAT-023, rag:R-NEG-003, rag:R-NEG-004, rag:R-NLS-008, rag:R-PNM-002, rag:R-PNM-018, rag:R-PNM-026 ...
- mtp6: replies differ on rag:R-DSC-001, rag:R-DSC-021, rag:R-FAQ-020, rag:R-HSP-018, rag:R-HTX-012, rag:R-MAT-023, rag:R-NEG-003, rag:R-NEG-004, rag:R-NLS-008, rag:R-PNM-002, rag:R-PNM-018, rag:R-PNM-026 ...
- mtpfile: replies differ on rag:R-POL-004, rag:R-POL-017, v12:HND-020
- ngram-mod: replies differ on rag:R-DSC-021, rag:R-FAQ-036, rag:R-HSP-016, rag:R-HSP-018, rag:R-MAT-023, rag:R-NEG-003, rag:R-NEG-004, rag:R-PNM-002, rag:R-PNM-018, rag:R-POL-004, rag:R-POL-017, rag:R-STR-006 ...
- ngram-simple: replies differ on rag:R-MAT-023, rag:R-NEG-004, rag:R-PNM-002, rag:R-PNM-026, rag:R-POL-004, rag:R-POL-017, v12:DSC-042, v12:HND-020

## o3s13b_b_4b

Plain decoding agrees with itself on 70/70 cases.

| Config | Cases | Identical | Writing speed ratio [95% CI] | First word change s [95% CI] | Total change s [95% CI] | Acceptance | Peak RAM MB | Qualifies |
|---|---:|---:|---|---|---|---:|---:|---|
| draft08 | 70 | 54 (77%) | 0.47× [0.45, 0.48] | +0.56 [+0.50, +0.66] | +6.44 [+5.37, +8.80] | 63% | 4741 | no |
| mtp2 | 70 | 25 (36%) | 1.29× [1.28, 1.33] | +0.01 [-0.01, +0.04] | -1.12 [-1.64, -0.77] | 76% | 4332 | no |
| mtp6 | 70 | 25 (36%) | 0.96× [0.87, 1.05] | +0.02 [+0.00, +0.04] | +0.00 [-0.04, +0.28] | 45% | 4521 | no |
| mtpfile | 70 | 25 (36%) | 1.04× [1.04, 1.05] | -0.11 [-0.16, -0.08] | -0.27 [-0.46, -0.14] | – | 3918 | (file check: different replies) |
| ngram-mod | 70 | 69 (99%) | 1.02× [1.01, 1.03] | -0.02 [-0.04, -0.01] | -0.09 [-0.20, -0.03] | 1% | 4032 | no |
| ngram-simple | 70 | 68 (97%) | 1.01× [1.00, 1.01] | -0.00 [-0.04, +0.01] | -0.02 [-0.07, +0.01] | 2% | 4022 | no |
| none2 | 70 | 70 (100%) | 1.08× [1.07, 1.08] | -0.03 [-0.05, -0.00] | -0.46 [-0.59, -0.35] | – | 3907 | (reference) |

**No candidate qualifies: plain decoding stays.**

- draft08: replies differ on rag:R-HTX-005, rag:R-HTX-012, rag:R-MAT-024, rag:R-NEG-003, rag:R-NEG-004, rag:R-NLS-008, rag:R-OFR-007, rag:R-PNM-002, rag:R-PNM-018, rag:R-SPC-015, v12:DSC-047, v12:HIN-035 ...
- mtp2: replies differ on rag:R-COL-008, rag:R-COL-016, rag:R-DSC-001, rag:R-DSC-021, rag:R-DSC-028, rag:R-FAQ-042, rag:R-FAQ-051, rag:R-GLO-022, rag:R-HSP-018, rag:R-HTX-005, rag:R-HTX-012, rag:R-MAT-023 ...
- mtp6: replies differ on rag:R-COL-008, rag:R-COL-016, rag:R-DSC-001, rag:R-DSC-021, rag:R-DSC-028, rag:R-FAQ-042, rag:R-FAQ-051, rag:R-GLO-022, rag:R-HSP-018, rag:R-HTX-005, rag:R-HTX-012, rag:R-MAT-023 ...
- mtpfile: replies differ on rag:R-COL-008, rag:R-COL-016, rag:R-DSC-001, rag:R-DSC-021, rag:R-DSC-028, rag:R-FAQ-042, rag:R-FAQ-051, rag:R-GLO-022, rag:R-HSP-018, rag:R-HTX-005, rag:R-HTX-012, rag:R-MAT-024 ...
- ngram-mod: replies differ on rag:R-NLS-008
- ngram-simple: replies differ on rag:R-SPC-015, v12:HND-014

