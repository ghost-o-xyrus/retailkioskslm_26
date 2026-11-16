"""
Eval set v1.2 = v1.1 with the label fixes logged in Objective 1's audit (Objective 3, Step 2).

    python eval\\build_eval_v12.py      # -> eval/eval_set_v1.2.jsonl

v1.1 stays unchanged so Objective 1 and 2 scores can be reproduced. Objective 3 runs use v1.2.

Fixes:
  TSL-097 "Show me watches like <id>."            and
  TSL-098 "Anything in the same style as <id>?"
      Both were too lenient: they also accepted a check_inventory call as the whole answer. The customer asks for
      similar watches and says nothing about stock, so only get_alternatives (reason out_of_stock or
      similar_style) passes now. The other alternatives_oos cases keep the stock-check option, because there the
      customer says the watch is missing or sold out.
Both cases are in the test split, so dev scores are identical under v1.1 and v1.2.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STRICT_ALTERNATIVES = ("TSL-097", "TSL-098")


def fix(case):
    if case["id"] in STRICT_ALTERNATIVES:
        opts = case["expected"]["required_calls"]
        kept = [o for o in opts if [s["name"] for s in o] == ["get_alternatives"]]
        assert len(kept) == 1 and len(opts) == 2, case["id"]
        case["expected"]["required_calls"] = kept
        case["notes"] = (case.get("notes") + " " if case.get("notes") else "") + \
            "v1.2: stock check alone no longer accepted (Objective 1 audit)."
    case["version"] = "1.2"
    return case


def main():
    src = os.path.join(HERE, "eval_set_v1.1.jsonl")
    dst = os.path.join(HERE, "eval_set_v1.2.jsonl")
    with open(src, encoding="utf-8") as f:
        cases = [fix(json.loads(line)) for line in f if line.strip()]
    with open(dst, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"{dst}: {len(cases)} cases, fixed {', '.join(STRICT_ALTERNATIVES)}")


if __name__ == "__main__":
    main()
