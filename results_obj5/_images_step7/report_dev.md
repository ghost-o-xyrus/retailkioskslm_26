# Objective 5, Step 7: product images (dev cases)

| Target | Result | Met |
|---|---|---|
| Right SKU and view on at least 95% of image requests | 80/80 (100.0%) | yes |
| No image of a different SKU (on a card, or as the watch asked for) | 0 replies showed one | yes |
| Cards match the products the reply names (and show that SKU's picture) | 186/186 cards, runs: o5s2_2b_rag_core, o5s2_2b_v12_core, o5s2_4b_rag_core, o5s2_4b_v12_core, o5s7_2b_img_dev, o5s7_4b_img_dev | yes |
| Image lookup p95 at most 50 ms | 0.0023 ms (p50 0.0017, 13662 lookups; table load 10.2 ms) | yes |

**All targets: met**

## By kind and language

| Run | Kind | Language | Right |
|---|---|---|---:|
| o5s7_2b_img_dev | code | en | 7/7 |
| o5s7_2b_img_dev | code | hinglish | 7/7 |
| o5s7_2b_img_dev | design | en | 6/6 |
| o5s7_2b_img_dev | design | hinglish | 6/6 |
| o5s7_2b_img_dev | followup | en | 5/5 |
| o5s7_2b_img_dev | followup | hinglish | 5/5 |
| o5s7_2b_img_dev | negative | en | 2/2 |
| o5s7_2b_img_dev | negative | hinglish | 2/2 |
| o5s7_4b_img_dev | code | en | 7/7 |
| o5s7_4b_img_dev | code | hinglish | 7/7 |
| o5s7_4b_img_dev | design | en | 6/6 |
| o5s7_4b_img_dev | design | hinglish | 6/6 |
| o5s7_4b_img_dev | followup | en | 5/5 |
| o5s7_4b_img_dev | followup | hinglish | 5/5 |
| o5s7_4b_img_dev | negative | en | 2/2 |
| o5s7_4b_img_dev | negative | hinglish | 2/2 |
