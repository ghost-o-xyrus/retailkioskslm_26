# Step 8: hard-fallback threshold on dev store questions

Run read: `o3s7a_4b_rag`. Store or unclear questions with a logged score: 131; the fallback can act on 48 (no code or catalogue name, not caught by the entity check, not Hinglish): 40 must answer, 8 must refuse, 0 either.

Rule: highest threshold with false refusals on must-answer at most 5%.

| Threshold | False refusals (must answer) [95% CI] | Refused (must refuse) | Refused (either) |
|---|---|---|---|
| Objective 2 -3.482 | 5/40 = 12.5% [5.5%, 26.1%] | 7/8 | 0/0 |
| chosen -5.612 | 2/40 = 5.0% [1.4%, 16.5%] | 6/8 | 0/0 |

Questions refused at the chosen threshold:

- R-OFF-005 (refuse, off_topic) score -10.470
- R-OFF-006 (refuse, off_topic) score -10.302
- R-MPO-008 (refuse, missing_policy) score -9.031
- R-FAQ-037 (answer, faq) score -7.817
- R-OFF-007 (refuse, off_topic) score -6.346
- R-OFF-010 (refuse, off_topic) score -6.345
- R-FAQ-004 (answer, faq) score -5.748
- R-MPO-012 (refuse, missing_policy) score -5.699
