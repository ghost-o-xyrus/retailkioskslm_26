# Objective 5, Step 7: product images (test cases)

| Target | Result | Met |
|---|---|---|
| Right SKU and view on at least 95% of image requests | 80/80 (100.0%) | yes |
| No image of a different SKU (on a card, or as the watch asked for) | 0 replies showed one | yes |
| Cards match the products the reply names (and show that SKU's picture) | 186/186 cards, runs: o5s2_2b_rag_core, o5s2_2b_v12_core, o5s2_4b_rag_core, o5s2_4b_v12_core, o5s7_2b_img_test, o5s7_4b_img_test | yes |
| Image lookup p95 at most 50 ms | 0.005 ms (p50 0.0033, 13662 lookups; table load 21.5 ms) | yes |

**All targets: met**

## By kind and language

| Run | Kind | Language | Right |
|---|---|---|---:|
| o5s7_2b_img_test | code | en | 7/7 |
| o5s7_2b_img_test | code | hinglish | 7/7 |
| o5s7_2b_img_test | design | en | 6/6 |
| o5s7_2b_img_test | design | hinglish | 6/6 |
| o5s7_2b_img_test | followup | en | 5/5 |
| o5s7_2b_img_test | followup | hinglish | 5/5 |
| o5s7_2b_img_test | negative | en | 2/2 |
| o5s7_2b_img_test | negative | hinglish | 2/2 |
| o5s7_4b_img_test | code | en | 7/7 |
| o5s7_4b_img_test | code | hinglish | 7/7 |
| o5s7_4b_img_test | design | en | 6/6 |
| o5s7_4b_img_test | design | hinglish | 6/6 |
| o5s7_4b_img_test | followup | en | 5/5 |
| o5s7_4b_img_test | followup | hinglish | 5/5 |
| o5s7_4b_img_test | negative | en | 2/2 |
| o5s7_4b_img_test | negative | hinglish | 2/2 |
