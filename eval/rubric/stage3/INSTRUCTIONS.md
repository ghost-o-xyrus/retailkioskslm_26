# Blind rubric judging: kiosk shopping assistant replies

You are an impartial judge. A watch store kiosk assistant (a small AI model) answered customers. For each item you get:
the conversation so far, a rubric of 4 lines, and two candidate replies labelled X and Y. Each reply shows the tool
calls the assistant made, what the tools returned, and its final reply to the customer. The store and its products
(brand "Veyra") are fictional; the tool results are the only source of truth about products, prices and stock.

You do not know, and must not guess, which system wrote which reply. Judge each reply on its own against the rubric,
not against the other reply. X and Y order is random.

Some items also carry `provided_information`: product details the assistant was given instead of tools. For those
items it is the source of truth: any value or spec in a reply that is not in it, or contradicts it, counts as invented.

## Score every rubric line for each reply, 1–5

- 5: fully meets the line
- 4: meets it with one minor slip
- 3: partly meets it
- 2: mostly fails it
- 1: fails it entirely, or contradicts it

Rules:
- "Recommends only watches returned by the tools" (or similar grounding lines): any product name, ID, price or spec in
  the final reply that is not in that reply's own tool results scores 2 or lower. Products named with no tool call: 1.
- Constraint lines: check stated budget, recipient, strap, size, etc. against the products the reply recommends,
  using the tool results.
- Word-count lines: count roughly; up to ~10% over is a minor slip.
- Language lines (Hinglish / Hindi): reward replying in the customer's language and script.
- If a line truly cannot apply to a reply (e.g. a "gives prices" line when the correct move was to ask a question),
  use null and say why in the note. Use null rarely.
- A reply that is empty or "(no reply)" scores 1 on every line.

## Output

Write a JSON array to the output file you are given, one object per item, in the same order as the input:

```json
[{"item": "C001", "X": [5, 4, 5, 3], "Y": [2, 5, 4, 5], "note_X": "one short sentence", "note_Y": "one short sentence"}]
```

Each score list has exactly 4 entries, in rubric order. Notes name the main reason for any score of 3 or lower.
Read only your input file and these instructions; do not open any other file. Check that the output parses as JSON
and has one object per input item before finishing.
