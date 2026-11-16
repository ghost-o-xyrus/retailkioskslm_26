# Objective 5, Step 9: walkthrough of the design scenarios

Kiosk mode (the tier's Deployed setup, loaded at start-up) for K, 1-4 and 6; Lab mode for 5. Full traces: `<tier>/S<n>.json`. Rules: see `app/walkthrough.py`.

| Scenario | Tier A | Tier B |
|---|---|---|
| K Kiosk lock | pass | pass |
| 1 Shopping | pass | pass |
| 2 Store question | pass | pass |
| 3 Hinglish | pass | **FAIL** |
| 4 Images | pass | pass |
| 5 Compare (Lab) | pass | pass |
| 6 Hand-off | pass | pass |

## Tier A: 7/7 passed

Deployed · Tier A · Qwen3.5-2B Q8_0; Kiosk ready in 78.0 s, Lab in 166.7 s.

| # | Customer | Kiosk (first 160 characters) | First word | Total | Cards |
|---|---|---|---:|---:|---:|
| 1 | I need a gift for my father, around 15k | Here are 3 men's watches under Rs 15,000:  1. **1546SL01 Sovereign Saffron** - Midnight blue dial, white leather, 41mm. 2. **1996SM02 Heritage Aurel** - Brown d | 4.0 s | 11.9 s | 3 |
| 1 | Is the second one in stock here? | Yes, the 1996SM02 Heritage Aurel is in stock here. It's available in the back room. Would you like to check stock at other nearby stores or compare it with the  | 4.8 s | 7.8 s | 1 |
| 2 | What does the warranty cover? | Based on the store information, the warranty covers: - Manufacturing defects in the movement and battery - Automatic watches have no battery warranty - Quartz w | 19.4 s | 27.5 s | 0 |
| 3 | Tell me about 1024SL01 | This is the ◇ ◇ ◇ Meridian Atlas watch (design V1024). It's a men's formal watch with a white dial, brown leather strap, and automatic movement. It features a 3 | 4.3 s | 8.9 s | 1 |
| 3 | Kya ye black strap mein milta hai? | Haan, 1024SL03 Meridian Atlas black strap mein available hai. Iska price ₹1,29,990 hai. | 3.8 s | 5.8 s | 1 |
| 4 | Show me the back of it | Here is the back view of the Meridian Atlas (1024SL03). The other views are below it. | 0.0 s | 0.0 s | 1 |
| 6 | Can someone help me try it on? | Staff has been notified and will come to the kiosk in about 3 minutes to help you try it on. | 3.3 s | 4.8 s | 0 |
| 5A | What colour is the strap on 1003SM02? | The strap on watch 1003SM02 is rose gold metal. | – | – | – |
| 5B | What colour is the strap on 1003SM02? | The strap on watch 1003SM02 is made of metal and is rose gold in colour. | – | – | – |

- 1: 0 slot question(s), 3 cards; stock: {'second': '1996SM02', 'checked': ['1996SM02'], 'in_stock': True}
- 2: answer check passed; retrieved ['policy:warranty', 'faq:does-a-battery-replacement-affect-the-warranty', 'faq:is-the-plating-on-gold-tone-watches-permanent']
- 4: 1024SL03 back
- 5: the bare model's strap colour: right (rose gold)
- 6: ticket REQ-0001 (in the reply: False; in the staff log: True)
- 3 Hinglish, earlier run: FAIL (the reply is not Hinglish; does not say the black-strap variant (1024SL03) exists); rerun above
- 4 Images, earlier run: pass; rerun above
- 6 Hand-off, earlier run: pass; rerun above

## Tier B: 6/7 passed

Deployed · Tier B · Qwen3.5-4B Q4_K_M + lora; Kiosk ready in 81.2 s, Lab in 157.8 s.

| # | Customer | Kiosk (first 160 characters) | First word | Total | Cards |
|---|---|---|---:|---:|---:|
| 1 | I need a gift for my father, around 15k | Here are three options for your father under 15k: 1. 1546SL01 Sovereign Saffron / Rs 14,795 / 41 mm / midnight blue dial, white leather 2. 1996SM02 Heritage Aur | 4.4 s | 19.2 s | 3 |
| 1 | Is the second one in stock here? | Yes, the 1996SM02 Heritage Aurel is in stock here. We have one on display and two in the back room. It is also available at ◇ ◇ ◇ Store, City Centre Mall, 6.8 k | 5.8 s | 12.3 s | 1 |
| 2 | What does the warranty cover? | The warranty covers manufacturing defects in the movement and battery. It does not cover straps, glass breakage, scratches, water damage beyond rated resistance | 6.5 s | 10.9 s | 0 |
| 3 | Tell me about 1024SL01 | Here's the 1024SL01 ◇ ◇ ◇ Meridian Atlas White Dial Brown Leather Strap Watch for Men (design V1024). It has a 38 mm stainless steel case, sapphire glass, and a | 4.1 s | 11.8 s | 1 |
| 3 | Kya ye black strap mein milta hai? | Nahi, 1024SL01 mein black strap nahi milta. Ye sirf brown leather strap wala hai. Kya aap koi aur model dekhna chahenge? | 4.7 s | 9.4 s | 1 |
| 4 | Show me the back of it | Here is the back view of the Meridian Atlas (1024SL01). The other views are below it. | 0.0 s | 0.0 s | 1 |
| 6 | Can someone help me try it on? | I have asked a staff member to come and help you. They will be with you in a few minutes. | 4.4 s | 6.7 s | 0 |
| 5A | What colour is the strap on 1003SM02? | The strap on the 1003SM02 ◇ ◇ ◇ Meridian Orion watch is a rose gold metal bracelet. | – | – | – |
| 5B | What colour is the strap on 1003SM02? | The strap on product 1003SM02 is rose gold metal. It's a formal watch from the Meridian collection with a champagne dial. Would you like to check its availabili | – | – | – |

- 1: 0 slot question(s), 3 cards; stock: {'second': '1996SM02', 'checked': ['1996SM02'], 'in_stock': True}
- 2: answer check passed; retrieved ['policy:warranty', 'faq:does-a-battery-replacement-affect-the-warranty', 'faq:is-the-plating-on-gold-tone-watches-permanent']
- 4: 1024SL01 back
- 5: the bare model's strap colour: right (rose gold)
- 6: ticket REQ-0001 (in the reply: False; in the staff log: True)
- 3 Hinglish, earlier run: FAIL (does not say the black-strap variant (1024SL03) exists); rerun above
- 4 Images, earlier run: pass; rerun above
- 6 Hand-off, earlier run: pass; rerun above
- **3 Hinglish**: does not say the black-strap variant (1024SL03) exists
