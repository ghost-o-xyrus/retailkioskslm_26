# Step 6: refusal fallback calibration (with Hinglish bypass)

Signal: top-1 re-ranker score from `openvino-len256-depth20.jsonl`. Rule: the highest threshold with dev false refusal at most 5%. Chosen on dev only; test scored once.

**Post-hoc variant.** Added after the first test run showed Hinglish questions being refused. Questions detected as Hinglish are never refused here and go to the model. Same rule, re-applied on dev. The eval set has no unanswerable Hinglish questions, so the cost of the bypass (Hinglish off-topic questions reaching the model) is not measured here; Step 8 must add some.

**Threshold: -3.4819**

| Split | False refusals (must answer) | Correct refusals (must refuse) | AUROC |
|---|---|---|---|
| dev | 5/112 = 4.5% | 12/14 = 85.7% | 0.876 |
| test | 13/258 = 5.0% [3.0%-8.4%] | 25/33 = 75.8% [59.0%-87.2%] | 0.922 |

False refusal = a question the corpus answers, refused by the fallback (target for the whole system: at most 10%; this step may use half). Correct refusal = an off-topic, not-sold or unknown-policy question stopped before the model. The rest reach the model, which must decline them itself (measured end to end in Step 8).

## Test: share refused, by question type

| Subtype | Role | Refused |
|---|---|---|
| collection | answer | 0/17 = 0.0% |
| faq | answer | 10/39 = 25.6% |
| glossary | answer | 0/17 = 0.0% |
| hinglish_spec | answer | 0/17 = 0.0% |
| hinglish_text | answer | 0/14 = 0.0% |
| offer | answer | 0/6 = 0.0% |
| policy | answer | 0/15 = 0.0% |
| product_description | answer | 0/25 = 0.0% |
| product_name | answer | 0/28 = 0.0% |
| product_sku | answer | 0/21 = 0.0% |
| product_spec | answer | 0/38 = 0.0% |
| store | answer | 0/4 = 0.0% |
| typo_spec | answer | 3/17 = 17.6% |
| missing_attribute | either | 0/17 = 0.0% |
| negative | either | 8/21 = 38.1% |
| nonexistent_product | either | 4/11 = 36.4% |
| spec_not_listed | either | 0/9 = 0.0% |
| missing_policy | refuse | 7/11 = 63.6% |
| not_sold | refuse | 10/14 = 71.4% |
| off_topic | refuse | 8/8 = 100.0% |

## Test: false refusals by language (must-answer questions only)

| Language | Refused |
|---|---|
| en | 13/227 = 5.7% |
| hinglish | 0/31 = 0.0% |

## Hinglish detector (retrieval/language.py), all 500 questions

Hinglish questions detected: 45/45. English questions wrongly detected: 0/455.
Test must-refuse questions let through by the bypass: 0.

## Dev curve (selected points)

| Threshold | Dev false refusal | Dev correct refusal |
|---|---|---|
| -inf | 0.0% | 0.0% |
| -10.096 | 0.0% | 14.3% |
| -7.817 | 0.0% | 35.7% |
| -5.748 | 0.9% | 64.3% |
| -4.012 | 3.6% | 78.6% |
| -2.424 | 5.4% | 92.9% |
| -1.968 | 8.9% | 92.9% |
| -1.532 | 12.5% | 92.9% |
| -0.591 | 14.3% | 92.9% |
| 0.098 | 17.0% | 92.9% |
| 0.733 | 19.6% | 92.9% |
| 1.499 | 23.2% | 92.9% |
| 2.452 | 26.8% | 92.9% |
| 2.949 | 28.6% | 92.9% |
| 3.362 | 33.9% | 92.9% |
| 3.666 | 38.4% | 92.9% |
| 3.855 | 42.9% | 92.9% |
| 4.117 | 47.3% | 92.9% |
| 4.308 | 51.8% | 92.9% |
| 4.556 | 55.4% | 92.9% |
| 5.098 | 60.7% | 92.9% |
| 5.346 | 66.1% | 92.9% |
| 5.786 | 71.4% | 92.9% |
| 5.932 | 76.8% | 92.9% |
| 6.691 | 81.2% | 92.9% |
| 8.782 | 85.7% | 100.0% |
| -3.482 **chosen** | 4.5% | 85.7% |

## Test questions the fallback got wrong

Refused although answerable:

- R-FAQ-035 (faq, en, score -9.17)
- R-FAQ-001 (faq, en, score -7.50)
- R-FAQ-010 (faq, en, score -7.33)
- R-FAQ-017 (faq, en, score -6.60)
- R-FAQ-018 (faq, en, score -6.25)
- R-FAQ-022 (faq, en, score -6.03)
- R-FAQ-052 (faq, en, score -5.61)
- R-TYP-007 (typo_spec, en, score -5.31)
- R-FAQ-011 (faq, en, score -5.09)
- R-TYP-005 (typo_spec, en, score -4.70)
- R-FAQ-006 (faq, en, score -4.66)
- R-TYP-022 (typo_spec, en, score -4.64)
- R-FAQ-013 (faq, en, score -4.54)

Passed to the model although nothing answers them:

- R-NSD-020 (not_sold, score 4.26, top chunk faq:does-every-watch-come-with-a-box)
- R-MPO-015 (missing_policy, score 3.07, top chunk faq:can-i-use-the-kiosk-to-find-a-watch-and-then-see-it)
- R-MPO-011 (missing_policy, score -0.12, top chunk policy:brand)
- R-NSD-012 (not_sold, score -0.21, top chunk faq:is-the-plating-on-gold-tone-watches-permanent)
- R-MPO-001 (missing_policy, score -2.60, top chunk faq:can-you-transfer-a-watch-from-another-store)
- R-NSD-007 (not_sold, score -2.92, top chunk faq:do-automatic-watches-need-a-battery)
- R-MPO-003 (missing_policy, score -3.22, top chunk faq:can-i-pay-partly-in-cash-and-partly-by-card)
- R-NSD-015 (not_sold, score -3.37, top chunk faq:do-you-buy-or-exchange-old-watches)

Plot: `curve.png`.
