# Step 8: speed and RAM (pre-registered rules)

Tier A: O3-final against O3-final + lora_2b and the deployed candidate (lora_2b, patches off); 2B Q8_0 on CPU, 4 threads, dev speed subset, 2 repeats.

## Tier A in place

| Set | Writing speed tokens/s: O3-final → + adapter (ratio) | Rule (1) | Total time change, candidate s [95% CI] | Rule (2) | First word change, candidate s [95% CI] |
|---|---|---|---|---|---|
| store questions | 16.1 → 15.4 (0.96) | met | -2.01 [-5.80, -0.40] | met | -2.24 [-5.96, -0.06] |
| tool cases | 15.1 → 14.6 (0.96) | met | +2.65 [+0.01, +4.17] | not met | +3.31 [+0.01, +3.97] |

Peak server RAM: O3-final 2432.9 MB, + adapter 2303.8 MB (-129 MB; expected under +200 MB).

**Tier A speed rules: not met** -> deployed: O3-final (the adapter's quality gain is reported with its speed cost)

## Tier B (Vulkan quality runs, reported)

O3-final against o4s7_4b_lora_shortoff (single runs, per-case medians).

| Set | Writing speed tokens/s | First word change s [95% CI] | Total time change s [95% CI] |
|---|---|---|---|
| store questions | 9.7 → 8.8 (0.91) | +0.52 [+0.38, +0.81] | -0.86 [-1.56, -0.05] |
| tool cases | 10.0 → 9.1 (0.91) | +0.23 [+0.10, +0.33] | -0.19 [-0.82, +0.00] |
| follow-ups | 10.6 → 9.0 (0.85) | +0.81 [+0.69, +0.99] | +1.31 [+0.63, +2.09] |
