"""
Objective 3, Step 4: the intended route of every single-message case, for checking the router.

    python eval\\route_labels.py          # -> eval/route_labels.json

Routes (what the kiosk should do with the customer's latest message):
  lookup     a product code is named and the customer wants its details or alternatives    -> product tools
  stock      availability of a named watch (code or name)                                   -> check_inventory
  compare    two or more named watches compared                                             -> compare_products
  shopping   the customer describes what they want (budget, recipient, style, features)     -> slots + search
  staff      asks for a person, to buy, to try on                                           -> call_staff
  chat       greetings, thanks, small talk about the kiosk itself                           -> no tool
  store      everything answered from store knowledge: policies, services, store info, facts about a named
             design (no code), not-sold brands, off-topic questions                         -> retrieval
Labels come from each case's category and subcategory (fixed in advance, not from the router's output):
  retrieval questions: product_sku -> lookup, product_description -> shopping, everything else -> store
  v1.2 tool cases: by category/subcategory (see MAP below); Hinglish cases follow their subcategory.
Grounded-mode cases are not routed (their context is given), so they get no label.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

MAP = {
    ("comparison", "tool_compare"): "compare",
    ("discovery", "*"): "shopping",
    ("handoff", "other"): "staff", ("handoff", "purchase"): "staff", ("handoff", "try_on"): "staff",
    ("handoff", "service"): "store", ("handoff", "question_unanswered"): "store",
    ("hinglish", "alternatives"): "lookup", ("hinglish", "clarify"): "shopping", ("hinglish", "details"): "lookup",
    ("hinglish", "handoff"): "staff", ("hinglish", "paired_clarify"): "shopping", ("hinglish", "paired_details"): "lookup",
    ("hinglish", "paired_purchase"): "staff", ("hinglish", "paired_search"): "shopping",
    ("hinglish", "paired_try_on"): "staff", ("hinglish", "search"): "shopping", ("hinglish", "stock"): "stock",
    ("refusal", "discount"): "store", ("refusal", "internal_info"): "store", ("refusal", "not_found"): "lookup",
    ("refusal", "out_of_database"): "store", ("refusal", "promise"): "store",
    ("tool_selection", "alternatives_cheaper"): "lookup", ("tool_selection", "alternatives_oos"): "lookup",
    ("tool_selection", "details"): "lookup", ("tool_selection", "no_tool"): "chat",
    ("tool_selection", "no_tool_context"): "store", ("tool_selection", "search_filter"): "shopping",
    ("tool_selection", "stock_colour"): "stock", ("tool_selection", "stock_colour_absent"): "stock",
    ("tool_selection", "stock_in"): "stock", ("tool_selection", "stock_out"): "stock",
    ("tool_selection", "stock_stale"): "stock",
}
RAG = {"product_sku": "lookup", "product_description": "shopping"}


def label(case):
    if case["mode"] != "tools":
        return None
    if case.get("set") == "rag" or case["category"] == "rag":
        return RAG.get(case["subcategory"], "store")
    return MAP.get((case["category"], case["subcategory"])) or MAP.get((case["category"], "*"))


def main():
    out = {}
    for f in ("rag_cases.jsonl", "eval_set_v1.2.jsonl"):
        with open(os.path.join(HERE, f), encoding="utf-8") as fh:
            for line in fh:
                c = json.loads(line)
                lab = label(c)
                if lab:
                    out[c["id"]] = {"route": lab, "split": c["split"], "file": f,
                                    "category": c["category"], "subcategory": c["subcategory"]}
    missing = [k for k, v in out.items() if not v["route"]]
    assert not missing, missing
    with open(os.path.join(HERE, "route_labels.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=0)
    from collections import Counter
    print(f"{len(out)} labels:", dict(Counter(v["route"] for v in out.values())))


if __name__ == "__main__":
    main()
