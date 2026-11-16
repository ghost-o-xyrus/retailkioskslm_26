# Step 9: fallback thresholds for the chosen re-ranker (dev)

Re-ranker: rt-int8s-l256-full-t4.

- Without the Hinglish bypass, the 5% rule gives -7.343, which refuses 5 of 14 answerable dev Hinglish questions: bypass **kept** (retired if at most 1).
- Soft threshold (cards shown): -3.457 (was -3.481874465942383).
- Hard threshold (Step 8, store questions): -5.534 (was -5.6122); refuses 2/40 must-answer and 6/8 must-refuse dev store questions it can act on.
