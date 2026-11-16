# Step 7: patches removed and short replies with the adapter (pre-registered rules)

Tier A adapter: lora_2b; Tier B adapter: lora_4b (Step 6 status: kept). Baselines: the Step 6 O3-final runs.

## Sets against O3-final

| Run | Set | Cases | O3-final | Run | Difference [95% CI] | McNemar p | Verdict |
|---|---|---:|---:|---:|---|---:|---|
| lora_2b, patches off | store questions | 135 | 71.1% | 83.0% | +11.9 [+4.4, +19.3] | 0.00249 | better |
| lora_2b, patches off | tool cases | 59 | 84.7% | 93.2% | +8.5 [-1.7, +18.6] | 0.227 | tie |
| lora_2b, patches off | follow-ups | 60 | 85.0% | 90.0% | +5.0 [-1.7, +13.3] | 0.375 | tie |
| O3-final, patches off (control) | store questions | 135 | 71.1% | 68.1% | -3.0 [-7.4, +0.7] | 0.289 | tie |
| O3-final, patches off (control) | tool cases | 59 | 84.7% | 86.4% | +1.7 [+0.0, +5.1] | 1 | tie |
| O3-final, patches off (control) | follow-ups | 60 | 85.0% | 83.3% | -1.7 [-5.0, +0.0] | 1 | tie |
| lora_4b + short replies | store questions | 135 | 85.2% | 86.7% | +1.5 [-4.4, +7.4] | 0.804 | tie |
| lora_4b + short replies | tool cases | 60 | 91.7% | 95.0% | +3.3 [+0.0, +8.3] | 0.5 | tie |
| lora_4b + short replies | follow-ups | 60 | 93.3% | 90.0% | -3.3 [-11.7, +5.0] | 0.688 | tie |
| lora_4b + short replies, patches off | store questions | 135 | 85.2% | 86.7% | +1.5 [-4.4, +7.4] | 0.804 | tie |
| lora_4b + short replies, patches off | tool cases | 60 | 91.7% | 95.0% | +3.3 [+0.0, +8.3] | 0.5 | tie |
| lora_4b + short replies, patches off | follow-ups | 60 | 93.3% | 88.3% | -5.0 [-13.3, +3.3] | 0.453 | tie |
| O3-final + short replies (control) | store questions | 134 | 85.1% | 76.1% | -9.0 [-14.9, -3.0] | 0.00754 | worse |
| O3-final + short replies (control) | tool cases | 60 | 91.7% | 83.3% | -8.3 [-16.7, -1.7] | 0.0625 | worse |
| O3-final + short replies (control) | follow-ups | 60 | 93.3% | 95.0% | +1.7 [-3.3, +6.7] | 1 | tie |

## Printed tool calls (runs, repeat 0)

| Run | Store | Tool cases | Follow-ups | Dialogues | Rule |
|---|---:|---:|---:|---:|---|
| lora_2b, patches off | 0 | 0 | 0 | 0 | met |
| O3-final, patches off (control) | 12 | 0 | 2 | 0 | not met |
| lora_4b + short replies | 0 | 0 | 0 | 0 | met |
| lora_4b + short replies, patches off | 0 | 0 | 0 | 0 | met |
| O3-final + short replies (control) | 14 | 6 | 5 | 2 | not met |

## Checks

- lora_2b, patches off: no regression **holds** (store questions: better, tool cases: tie, follow-ups: tie, dialogues: met, hinglish: ok); printed met; Hinglish pooled +2.2 points; dialogue fit +0.0 points
- O3-final, patches off (control) (reported only): no regression **holds** (store questions: tie, tool cases: tie, follow-ups: tie, dialogues: met, hinglish: ok); printed not met; Hinglish pooled +0.0 points; dialogue fit +0.0 points
- lora_4b + short replies: no regression **holds** (store questions: tie, tool cases: tie, follow-ups: tie, dialogues: met, hinglish: ok); printed met; Hinglish pooled +4.3 points; dialogue fit +0.0 points
- lora_4b + short replies, patches off: no regression **holds** (store questions: tie, tool cases: tie, follow-ups: tie, dialogues: met, hinglish: ok); printed met; Hinglish pooled +2.2 points; dialogue fit +0.0 points
- O3-final + short replies (control) (reported only): no regression **does not hold** (store questions: worse, tool cases: worse, follow-ups: tie, dialogues: met, hinglish: ok); printed not met; Hinglish pooled +4.3 points; dialogue fit +0.0 points

## Decisions

- H5, Tier A: holds: the patches are switched off
- Tier B: kept, short replies back on, patches off; H5 holds
- Deployed candidate (timed in Step 8 for Tier A): Tier A: O3-final + lora_2b, patches off; Tier B: O3-final + lora_4b, patches off, short replies

## Staff discipline and waits on store questions (reported)

| Run | Model staff calls on answerable | Offered, not called | First word p50 |
|---|---|---|---|
| lora_2b, patches off | 20 → 0 | 11 → 39 | 5.5 s → 1.8 s |
| O3-final, patches off (control) | 20 → 24 | 11 → 9 | 5.5 s → 4.9 s |
| lora_4b + short replies | 0 → 0 | 27 → 32 | 4.3 s → 4.3 s |
| lora_4b + short replies, patches off | 0 → 0 | 27 → 32 | 4.3 s → 5.4 s |
| O3-final + short replies (control) | 0 → 4 | 27 → 22 | 4.3 s → 4.6 s |
