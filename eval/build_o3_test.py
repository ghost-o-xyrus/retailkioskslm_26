"""
Objective 3, Step 14: the confirming test set O3-T. Built once, before any Step 14 run; nothing in Objective 3 was
tuned on any of it.

    python eval\\build_o3_test.py

Two kinds of material:
  fresh     generated now from the catalogue with new seeds (tool cases: 3141/3142; store questions: 4049). Any
            case whose wording (and context) matches an existing case in any split is dropped, so every fresh case
            is new to every earlier run.
  held-out  the Objective 3 test halves of the hand-written categories, which a new seed cannot regenerate:
            discovery and Hinglish tool cases (eval_set_v1.2 test split), and the hand-written store-question types
            (FAQ, policy, glossary, offers, store, Hinglish text, not sold, off-topic, missing policy) from the
            rag_cases test split. Objective 3 never ran a test case; these were last used in Objective 2's final run.
Follow-ups: the test half of eval/rag_followups.jsonl (Step 11 built it and kept it aside) is used as it is.
Dialogues: 60 fresh hidden profiles, seed 202, appended to eval/o3_dialogues.jsonl as split "test".

Only tool-mode cases are kept (Objective 3 scores tool-mode cases only). Every case has split "test", set "o3t" and
"o3t_origin" (fresh | held-out), so reports can split results by origin and by language.

Writes:
    eval/eval_set_o3t.jsonl     tool cases
    eval/rag_cases_o3t.jsonl    store questions
    eval/o3t_speed_ids.json     40 store questions + 30 tool cases (stratified, seed 94) for Tier A in-place timing
    eval/o3t_overview.csv       one line per case
"""

import collections
import copy
import csv
import json
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "knowledge"))

TOOL_SEEDS = (3141, 3142)
STORE_SEED = 4049
SPEED_SEED = 94
DIALOGUE_SEED, DIALOGUE_N = 202, 60
GENERATED_STORE = {"product_spec", "product_name", "product_description", "product_sku", "negative", "hinglish_spec",
                   "missing_attribute", "typo_spec", "collection", "nonexistent_product", "spec_not_listed"}
HELD_OUT_TOOL_CATEGORIES = ("discovery", "hinglish")
STRICT_ALTERNATIVES = re.compile(r"^(show me watches like|anything in the same style as)", re.I)   # v1.2 fix


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def key(c):
    return json.dumps([[m.get("content") for m in c["messages"]], c.get("context")], ensure_ascii=False)


def v12_fix(c):
    """The Objective 1 audit fix that made v1.2, applied by wording instead of by id."""
    opts = (c.get("expected") or {}).get("required_calls")
    if opts and STRICT_ALTERNATIVES.match(c["messages"][-1]["content"]):
        kept = [o for o in opts if [s["name"] for s in o] == ["get_alternatives"]]
        if kept:
            c["expected"]["required_calls"] = kept
    return c


def fresh_tool_cases(existing):
    import build_eval_set as core
    from checks import REFUSAL_PHRASES
    core.REFUSAL_LIKE = REFUSAL_PHRASES
    import build_eval_v11 as v11
    core.CASES.clear()
    core.build(random.Random(TOOL_SEEDS[0]))
    new_core = list(core.CASES)
    core.CASES.clear()
    for i, c in enumerate(new_core):
        c["id"], c["set"] = f"TMP-{i}", "core"
    cases = new_core + v11.build_expansion(random.Random(TOOL_SEEDS[1]), new_core) + v11.build_paired(new_core)
    seen, out = set(existing), []
    for c in cases:
        k = key(c)
        if c["mode"] != "tools" or k in seen:
            continue
        seen.add(k)
        out.append(v12_fix(c))
    counters, src = collections.Counter(), {}
    for c in out:                                   # core cases come first, so a TMP id first names the source
        p = v11.PREFIX[c["category"]]
        counters[p] += 1
        new = f"N-{p}-{counters[p]:03d}"
        if c.get("id") and str(c["id"]).startswith("TMP-") and not c.get("paired_with"):
            src.setdefault(c["id"], new)
        c["id"] = new
    for c in out:
        if c.get("paired_with"):
            c["paired_with"] = src.get(c["paired_with"])   # None when its English source was a duplicate
        c.update(split="test", set="o3t", o3t_origin="fresh", version="o3t")
        c.setdefault("paired_with", None)
    return out


def fresh_store_questions(existing_queries):
    import build_retrieval_eval as R
    from build_rag_cases import to_case
    b = R.Builder(STORE_SEED, os.path.join(ROOT, "knowledge", "corpus.jsonl"), os.path.join(ROOT, "data"))
    b.seen |= set(existing_queries)                    # never repeat an earlier question
    b.products_by_name()
    b.products_by_sku()
    b.products_by_description()
    b.product_specs(55)
    b.product_specs(25, language="hinglish", subtype="hinglish_spec")
    b.product_specs(25, subtype="typo_spec", typo_names=True)
    b.missing_fields()
    b.collections()
    b.negatives()
    b.missing_attributes()
    used = {w for s in b.styles.values() for w in s["style_name"].split()}
    b.nonexistent(15, words=[w for w in R.STYLE_WORDS if w not in used])
    problems = b.expand_and_validate()
    if problems:
        sys.exit("Label problems in the fresh store questions:\n  " + "\n  ".join(problems[:10]))
    prefix = {"product_name": "PNM", "product_sku": "SKU", "product_description": "DSC", "product_spec": "SPC",
              "hinglish_spec": "HSP", "typo_spec": "TYP", "spec_not_listed": "NLS", "collection": "COL",
              "negative": "NEG", "missing_attribute": "MAT", "nonexistent_product": "NEX"}
    counters, out = collections.Counter(), []
    for it in b.items:
        p = prefix[it["subtype"]]
        counters[p] += 1
        it.update(id=f"RT-{p}-{counters[p]:03d}", split="test")
        c = to_case(it, "eval/build_o3_test.py", "Step 14 fresh question")
        c.update(set="o3t", o3t_origin="fresh", version="o3t")
        out.append(c)
    return out


def main():
    v12 = load(os.path.join(HERE, "eval_set_v1.2.jsonl"))
    every_tool_case = v12 + load(os.path.join(HERE, "eval_set.jsonl")) + load(os.path.join(HERE, "eval_set_v1.1.jsonl"))
    tools = fresh_tool_cases({key(c) for c in every_tool_case})
    held = [dict(copy.deepcopy(c), set="o3t", o3t_origin="held-out") for c in v12
            if c["split"] == "test" and c["mode"] == "tools" and c["category"] in HELD_OUT_TOOL_CATEGORIES]
    have = {c["id"] for c in tools + held}
    for c in held:                     # its English partner is outside O3-T (dev or not held out): keep the link aside
        if c.get("paired_with") and c["paired_with"] not in have:
            c["paired_with_v12"], c["paired_with"] = c["paired_with"], None
    tools += held

    rag = load(os.path.join(HERE, "rag_cases.jsonl"))
    retr = load(os.path.join(ROOT, "knowledge", "retrieval_eval.jsonl"))
    store = fresh_store_questions({q["query"].lower() for q in retr} | {c["messages"][-1]["content"].lower() for c in rag})
    store += [dict(copy.deepcopy(c), set="o3t", o3t_origin="held-out") for c in rag
              if c["split"] == "test" and c["subcategory"] not in GENERATED_STORE]

    ids = [c["id"] for c in tools + store]
    dup = [i for i, n in collections.Counter(ids).items() if n > 1]
    assert not dup, f"duplicate ids: {dup[:10]}"
    for name, cases in (("eval_set_o3t.jsonl", tools), ("rag_cases_o3t.jsonl", store)):
        with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
            for c in cases:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")

    import build_o3_speed_ids as SP
    rng = random.Random(SPEED_SEED)
    s_ids, s_q = SP.stratified(store, lambda c: c["subcategory"], 40, rng)
    t_ids, t_q = SP.stratified(tools, lambda c: c["category"], 30, rng)
    with open(os.path.join(HERE, "o3t_speed_ids.json"), "w", encoding="utf-8") as f:
        json.dump({"version": "o3-step14", "seed": SPEED_SEED, "split": "test",
                   "purpose": "Step 14 Tier A in-place timing, O3-final against O3-B0", "rag_ids": s_ids,
                   "v11_ids": t_ids, "ids": s_ids + t_ids, "strata": {"rag_subcategory": s_q, "tool_category": t_q}},
                  f, indent=1)

    with open(os.path.join(HERE, "o3t_overview.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "file", "origin", "category", "subcategory", "language", "behaviour", "question"])
        for name, cases in (("tools", tools), ("store", store)):
            for c in cases:
                w.writerow([c["id"], name, c["o3t_origin"], c["category"], c["subcategory"], c["language"],
                            c["expected"].get("behaviour"), c["messages"][-1]["content"]])

    # dialogues: 60 fresh hidden profiles (only once)
    dpath = os.path.join(HERE, "o3_dialogues.jsonl")
    if not any(d.get("split") == "test" for d in load(dpath)):
        subprocess.run([sys.executable, os.path.join(HERE, "build_dialogues.py"), "--split", "test", "--n",
                        str(DIALOGUE_N), "--seed", str(DIALOGUE_SEED), "--append"], check=True)
    dlg = [d for d in load(dpath) if d.get("split") == "test"]

    fup = [c for c in load(os.path.join(HERE, "rag_followups.jsonl")) if c["split"] == "test"]
    C = collections.Counter
    print(f"tool cases: {len(tools)}  {dict(C((c['o3t_origin'], c['category']) for c in tools))}")
    print(f"  Hinglish: {sum(c['language'] != 'en' for c in tools)}")
    print(f"store questions: {len(store)}  {dict(C(c['o3t_origin'] for c in store))}  "
          f"answerable {sum(c['expected']['behaviour'] == 'answer' for c in store)}, "
          f"Hinglish {sum(c['language'] == 'hinglish' for c in store)}")
    print(f"follow-ups (test half): {len(fup)}  Hinglish {sum(c['language'] == 'hinglish' for c in fup)}")
    print(f"dialogues (test): {len(dlg)}  Hinglish {sum(d.get('language') == 'hinglish' for d in dlg)}")
    print(f"speed subset: {len(s_ids)} store + {len(t_ids)} tool cases")


if __name__ == "__main__":
    main()
