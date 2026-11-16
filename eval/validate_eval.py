"""
Check that every eval case is well-formed and answerable.

    python eval/validate_eval.py

Checks:
  1. ids unique, fields present, known categories and behaviours
  2. every expected tool call uses a real tool, real parameters and valid enum values
  3. every expected tool call actually runs against the mock tools without error
     (searches must return at least one watch)
  4. grounded cases: every expected fact is present in the context given to the model,
     and missing-field cases really lack the true value
  5. tool cases: expected facts appear in the tool results
  6. stock cases agree with the tools (in stock / out of stock / stale)
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from checks import text_has, REFUSAL_PHRASES  # noqa: E402
from tools import mock_tools as mt  # noqa: E402

CATEGORIES = {"grounded_qa", "discovery", "comparison", "tool_selection", "refusal", "handoff", "hinglish"}
BEHAVIOURS = {"answer", "answer_unknown", "clarify", "tool_use", "no_tool_answer", "refuse", "handoff"}
PHRASE_WORDS = {"yes", "no", "not", "sorry", "doesn't", "does not", "outdated", "not listed", "in stock",
                "couldn't find", "nahi"}


def is_phrase_group(group):
    return any(a in PHRASE_WORDS for a in group) or group == REFUSAL_PHRASES


def concrete(matcher):
    """Pick a representative value for a matcher (used to execute expected calls)."""
    if "absent_or" in matcher:
        return concrete(matcher["absent_or"])
    if "equals_any" in matcher:
        return matcher["equals_any"][0]
    if "range" in matcher:
        return matcher["range"][1]
    if "contains_any" in matcher:
        return matcher["contains_any"][0]
    if "set_equals" in matcher:
        return list(matcher["set_equals"])
    raise ValueError(matcher)


def main():
    mt.reload(os.path.join(ROOT, "data", "kiosk"))
    mt.STAFF_LOG = os.devnull
    schemas = {s["function"]["name"]: s["function"]["parameters"]["properties"] for s in mt.load_schemas(True)}
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "eval_set.jsonl")
    with open(path, encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    problems, ids = [], set()
    by_id = {c["id"]: c for c in cases}
    for c in cases:
        pw = c.get("paired_with")
        if pw:
            if pw not in by_id:
                problems.append(f"{c['id']}: paired_with {pw} not found")
            elif by_id[pw]["expected"] != c["expected"]:
                problems.append(f"{c['id']}: expectations differ from its English pair {pw}")
    for c in cases:
        cid = c["id"]
        if cid in ids:
            problems.append(f"{cid}: duplicate id")
        ids.add(cid)
        e = c["expected"]
        if c["category"] not in CATEGORIES:
            problems.append(f"{cid}: unknown category")
        if e["behaviour"] not in BEHAVIOURS:
            problems.append(f"{cid}: unknown behaviour {e['behaviour']}")
        if c["mode"] == "grounded" and not c.get("context"):
            problems.append(f"{cid}: grounded case without context")
        if c["mode"] == "grounded" and e.get("required_calls"):
            problems.append(f"{cid}: grounded case expects tool calls")
        if e["behaviour"] == "clarify" and not e.get("clarify_slots"):
            problems.append(f"{cid}: clarify case without slots")

        # 2 + 3 + 5: tool calls
        results_text = ""
        for oi, option in enumerate(e.get("required_calls", [])):
            for spec in option:
                name = spec["name"]
                if name not in schemas:
                    problems.append(f"{cid}: unknown tool {name}")
                    continue
                args = {}
                for p, m in spec.get("args", {}).items():
                    if p not in schemas[name]:
                        problems.append(f"{cid}: {name} has no parameter {p}")
                        continue
                    enum = schemas[name][p].get("enum")
                    vals = m.get("equals_any") or (m.get("absent_or") or {}).get("equals_any") or []
                    if enum:
                        bad = [v for v in vals if v not in enum]
                        if bad:
                            problems.append(f"{cid}: {name}.{p} values {bad} not in enum")
                    args[p] = concrete(m)
                res = mt.call_tool(name, args)
                if "error" in res:
                    problems.append(f"{cid}: option {oi} {name}({args}) -> {res}")
                elif name == "search_catalogue" and res["total_matches"] == 0:
                    problems.append(f"{cid}: option {oi} search returns nothing: {args}")
                if oi == 0:
                    results_text += json.dumps(res, ensure_ascii=False) + "\n"

        groups = e.get("must_include", [])
        # 4: grounded facts are in the context
        if c["mode"] == "grounded":
            computed = set(e.get("computed_fact_groups", []))
            for gi, g in enumerate(groups):
                if gi in computed:
                    continue
                if not is_phrase_group(g) and not text_has(c["context"], g):
                    problems.append(f"{cid}: fact {g[:3]} not found in context")
            if e["behaviour"] == "answer_unknown":
                for t in e.get("must_not_include", []):
                    if text_has(c["context"], [t]):
                        problems.append(f"{cid}: 'missing' value '{t}' is actually in the context")
        # 5: tool facts are in the tool results
        elif e.get("required_calls") and c["subcategory"] in ("details", "tool_compare"):
            for g in groups:
                if not is_phrase_group(g) and not text_has(results_text, g):
                    problems.append(f"{cid}: fact {g[:3]} not in tool results")
        # 6: stock cases agree with the tools
        if c["subcategory"] in ("stock_in", "stock_out", "stock_stale"):
            r = json.loads(results_text.splitlines()[0])["results"][0]
            if c["subcategory"] == "stock_in" and not r["in_stock"]:
                problems.append(f"{cid}: expected in stock")
            if c["subcategory"] == "stock_out":
                if r["in_stock"] or not r["other_stores_with_stock"]:
                    problems.append(f"{cid}: expected out of stock here, in stock elsewhere")
                if not any(text_has(results_text, [a]) for a in groups[1]):
                    problems.append(f"{cid}: nearest store name not in tool result")
            if c["subcategory"] == "stock_stale" and not r["stock_data_may_be_outdated"]:
                problems.append(f"{cid}: expected stale stock flag")

    # balance report
    from collections import Counter
    cat = Counter(c["category"] for c in cases)
    split = Counter((c["category"], c["split"]) for c in cases)
    print(f"{len(cases)} cases")
    for k in sorted(cat):
        print(f"  {k:15s} {cat[k]:3d}  (dev {split[(k, 'dev')]}, test {split[(k, 'test')]})")
    print("  behaviours:", dict(Counter(c["expected"]["behaviour"] for c in cases)))
    print("  languages: ", dict(Counter(c["language"] for c in cases)))
    print("  modes:     ", dict(Counter(c["mode"] for c in cases)))
    if any("set" in c for c in cases):
        print("  sets:      ", dict(Counter(c.get("set") for c in cases)))
        print("  splits:    ", dict(Counter(c["split"] for c in cases)))
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    print("\nAll eval cases valid.")


if __name__ == "__main__":
    main()
