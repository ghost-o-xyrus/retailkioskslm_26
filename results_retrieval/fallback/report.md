# Step 6: refusal fallback calibration

Signal: top-1 re-ranker score from `openvino-len256-depth20.jsonl`. Rule: the highest threshold with dev false refusal at most 5%. Chosen on dev only; test scored once.

**Threshold: -7.9675**

| Split | False refusals (must answer) | Correct refusals (must refuse) | AUROC |
|---|---|---|---|
| dev | 5/112 = 4.5% | 5/14 = 35.7% | 0.876 |
| test | 7/258 = 2.7% [1.3%-5.5%] | 13/33 = 39.4% [24.7%-56.3%] | 0.922 |

False refusal = a question the corpus answers, refused by the fallback (target for the whole system: at most 10%; this step may use half). Correct refusal = an off-topic, not-sold or unknown-policy question stopped before the model. The rest reach the model, which must decline them itself (measured end to end in Step 8).

## Test: share refused, by question type

| Subtype | Role | Refused |
|---|---|---|
| collection | answer | 0/17 = 0.0% |
| faq | answer | 1/39 = 2.6% |
| glossary | answer | 0/17 = 0.0% |
| hinglish_spec | answer | 0/17 = 0.0% |
| hinglish_text | answer | 6/14 = 42.9% |
| offer | answer | 0/6 = 0.0% |
| policy | answer | 0/15 = 0.0% |
| product_description | answer | 0/25 = 0.0% |
| product_name | answer | 0/28 = 0.0% |
| product_sku | answer | 0/21 = 0.0% |
| product_spec | answer | 0/38 = 0.0% |
| store | answer | 0/4 = 0.0% |
| typo_spec | answer | 0/17 = 0.0% |
| missing_attribute | either | 0/17 = 0.0% |
| negative | either | 1/21 = 4.8% |
| nonexistent_product | either | 1/11 = 9.1% |
| spec_not_listed | either | 0/9 = 0.0% |
| missing_policy | refuse | 2/11 = 18.2% |
| not_sold | refuse | 3/14 = 21.4% |
| off_topic | refuse | 8/8 = 100.0% |

## Test: false refusals by language (must-answer questions only)

| Language | Refused |
|---|---|
| en | 1/227 = 0.4% |
| hinglish | 6/31 = 19.4% |

## Dev curve (selected points)

| Threshold | Dev false refusal | Dev correct refusal |
|---|---|---|
| -inf | 0.0% | 0.0% |
| -10.096 | 2.7% | 14.3% |
| -7.817 | 5.4% | 35.7% |
| -5.748 | 6.2% | 64.3% |
| -4.012 | 9.8% | 78.6% |
| -2.424 | 12.5% | 92.9% |
| -1.968 | 17.0% | 92.9% |
| -1.532 | 21.4% | 92.9% |
| -0.591 | 24.1% | 92.9% |
| 0.098 | 26.8% | 92.9% |
| 0.733 | 30.4% | 92.9% |
| 1.499 | 34.8% | 92.9% |
| 2.452 | 39.3% | 92.9% |
| 2.949 | 41.1% | 92.9% |
| 3.362 | 46.4% | 92.9% |
| 3.666 | 50.9% | 92.9% |
| 3.855 | 55.4% | 92.9% |
| 4.117 | 59.8% | 92.9% |
| 4.308 | 64.3% | 92.9% |
| 4.556 | 67.9% | 92.9% |
| 5.098 | 73.2% | 92.9% |
| 5.346 | 78.6% | 92.9% |
| 5.786 | 83.9% | 92.9% |
| 5.932 | 89.3% | 92.9% |
| 6.691 | 93.8% | 92.9% |
| 8.782 | 98.2% | 100.0% |
| -7.967 **chosen** | 4.5% | 35.7% |

## Test questions the fallback got wrong

Refused although answerable:

- R-HTX-014 (hinglish_text, hinglish, score -11.07)
- R-HTX-016 (hinglish_text, hinglish, score -10.76)
- R-HTX-004 (hinglish_text, hinglish, score -10.70)
- R-HTX-001 (hinglish_text, hinglish, score -10.66)
- R-FAQ-035 (faq, en, score -9.17)
- R-HTX-007 (hinglish_text, hinglish, score -8.85)
- R-HTX-003 (hinglish_text, hinglish, score -8.73)

Passed to the model although nothing answers them:

- R-NSD-020 (not_sold, score 4.26, top chunk faq:does-every-watch-come-with-a-box)
- R-MPO-015 (missing_policy, score 3.07, top chunk faq:can-i-use-the-kiosk-to-find-a-watch-and-then-see-it)
- R-MPO-011 (missing_policy, score -0.12, top chunk policy:brand)
- R-NSD-012 (not_sold, score -0.21, top chunk faq:is-the-plating-on-gold-tone-watches-permanent)
- R-MPO-001 (missing_policy, score -2.60, top chunk faq:can-you-transfer-a-watch-from-another-store)
- R-NSD-007 (not_sold, score -2.92, top chunk faq:do-automatic-watches-need-a-battery)
- R-MPO-003 (missing_policy, score -3.22, top chunk faq:can-i-pay-partly-in-cash-and-partly-by-card)
- R-NSD-015 (not_sold, score -3.37, top chunk faq:do-you-buy-or-exchange-old-watches)
- R-MPO-009 (missing_policy, score -4.18, top chunk faq:do-you-deliver)
- R-MPO-013 (missing_policy, score -4.24, top chunk faq:can-i-try-a-watch-on)
- R-MPO-014 (missing_policy, score -5.61, top chunk faq:which-other-veyra-stores-are-nearby)
- R-NSD-018 (not_sold, score -5.67, top chunk glossary:open-heart)
- R-NSD-001 (not_sold, score -5.92, top chunk faq:does-every-watch-come-with-a-box)
- R-NSD-019 (not_sold, score -5.99, top chunk faq:can-i-swap-a-leather-strap-for-a-metal-bracelet)
- R-NSD-016 (not_sold, score -6.02, top chunk faq:do-automatic-watches-need-a-battery)
- R-MPO-006 (missing_policy, score -6.35, top chunk faq:do-you-replace-batteries-in-other-brands-watches)
- R-MPO-007 (missing_policy, score -6.88, top chunk faq:do-i-get-a-printed-or-digital-invoice)
- R-NSD-013 (not_sold, score -7.26, top chunk faq:do-you-sell-gift-cards)
- R-NSD-006 (not_sold, score -7.32, top chunk faq:can-i-reserve-a-watch-online-and-pick-it-up-here)
- R-NSD-004 (not_sold, score -7.82, top chunk faq:can-i-track-my-repair)

Plot: `curve.png`.
