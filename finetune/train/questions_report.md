# Objective 4 training questions (training catalogue)

## tools: 680 cases

- kinds: {'tools': 509, 'refuse': 70, 'handoff': 101}
- gaps: {'tool_choice': 509, 'decline': 70, 'staff_discipline': 101}
- Hinglish: 219 (32%)
- subcategories: {'details': 73, 'paired_details': 65, 'tool_compare': 57, 'stock_in': 52, 'stock_out': 50, 'paired_stock_in': 47, 'paired_stock_out': 47, 'internal_info': 37, 'stock_colour': 34, 'alternatives_oos': 34, 'discount': 33, 'purchase': 29}

## store: 2134 cases

- kinds: {'answer': 1268, 'not_listed': 429, 'decline': 437}
- gaps: {'staff_discipline': 952, 'not_listed': 429, 'decline': 437, 'ordinary': 316}
- Hinglish: 676 (32%)
- subcategories: {'hinglish_spec': 417, 'missing_attribute': 410, 'product_spec': 318, 'faq': 187, 'nonexistent_product': 177, 'negative': 165, 'product_name': 90, 'missing_policy': 76, 'glossary': 63, 'typo_spec': 58, 'product_sku': 39, 'policy': 33}

## followups: 443 cases

- kinds: {'answer': 443}
- gaps: {'staff_discipline': 380, 'ordinary': 63}
- Hinglish: 129 (29%)
- subcategories: {'followup_fact': 220, 'followup_colour': 80, 'followup_stock': 80, 'followup_switch': 63}

## Dropped as too close to an eval question

- follow-up: same text: 1
- follow-up: word overlap >= 0.6: 6
- store: copy of an eval question: 5
- store: hand-written, close to an eval question: 226
- store: same wording, other product: 31
- tool: copy of an eval question: 540
- tool: same wording, other product: 49
- tool: word overlap >= 0.6: 39
