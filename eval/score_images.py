"""
Objective 5, Step 7: score the image-request runs against the targets.

Targets (Success criteria): the right SKU and view on at least 95% of image requests; no image of a different SKU,
ever; cards match the products a reply names on every dev reply; image lookup p95 at most 50 ms.

    python eval\\score_images.py --runs o5s7_2b_img_dev o5s7_4b_img_dev [--cards-runs o5s2_2b_rag_core ...]

  --runs        image-request runs (eval/image_cases.jsonl)
  --cards-runs  other runs whose every reply is checked for cards (default: the Step 2 core runs, if present)
Writes results_obj5/_images_step7/report_<split>.md and .json.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


def records(rd, run):
    p = os.path.join(rd, run, "cases.jsonl")
    if not os.path.exists(p):
        return None
    out = {}
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("repeat", 0) == 0:
                out[r["id"]] = r
    return out


def url_to_sku():
    from kiosk_core import media
    return {media.url(r): sku for sku, v in media._index().items() for r in v.values()}


def shown_images(rec, cards):
    urls = list((rec.get("images") or {}).get("urls") or [])
    for c in cards:
        urls += [c.get("image")] if c.get("image") else []
        urls += [i["url"] for i in c.get("images") or []]
    return [u for u in urls if u]


def main(argv=None):
    from app.service import cards_for
    from kiosk_core import media
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--cards-runs", nargs="*", default=None)
    ap.add_argument("--results", default=os.path.join(ROOT, "results_obj5"))
    ap.add_argument("--cases", default=os.path.join(ROOT, "eval", "image_cases.jsonl"))
    a = ap.parse_args(argv)
    cases = {}
    with open(a.cases, encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            cases[c["id"]] = c
    u2s = url_to_sku()
    rows, split = [], None
    for run in a.runs:
        recs = records(a.results, run)
        if recs is None:
            print(f"{run}: no results")
            continue
        for cid, rec in recs.items():
            c = cases.get(cid)
            if not c:
                continue
            split = c["split"]
            exp = c["expected"]["images"]
            cards = cards_for(rec)
            shown = [u2s.get(u, "?") for u in shown_images(rec, cards)]
            call = next((t for t in rec.get("tool_calls") or [] if t.get("name") == "show_product_images"), None)
            res = (call or {}).get("result") or {}
            first = (res.get("images") or [{}])[0]
            # a wrong image: a picture of one SKU on another SKU's card, or a gallery of a product not asked for
            mism = [cd["product_id"] for cd in cards if cd.get("image") and u2s.get(cd["image"]) != cd["product_id"]]
            gallery = (rec.get("images") or {}).get("product_id") if (rec.get("images") or {}).get("urls") else None
            if exp is None:            # nothing to show: no gallery (cards of suggested watches carry their own)
                right = not gallery
                wrong = bool(gallery) or bool(mism)
            else:
                allowed = set(exp["skus"])
                right = bool(call) and res.get("product_id") in allowed and first.get("view") == exp["view"]
                wrong = bool(mism) or (gallery is not None and gallery not in allowed)
            rows.append({"run": run, "id": cid, "kind": c["subcategory"], "language": c["language"],
                         "expected": exp, "got": {"product_id": res.get("product_id"), "view": first.get("view")},
                         "shown": sorted(set(shown)), "right": right, "wrong_sku": wrong,
                         "reply": rec.get("final_reply"), "route": rec.get("route"), "error": rec.get("error")})
    # cards on every reply of other runs
    cards_runs = a.cards_runs
    if cards_runs is None:
        cards_runs = [r for r in ("o5s2_2b_rag_core", "o5s2_2b_v12_core", "o5s2_4b_rag_core", "o5s2_4b_v12_core")
                      if os.path.exists(os.path.join(a.results, r, "cases.jsonl"))]
    card_checks, card_bad, img_ok = 0, [], 0
    for run in list(cards_runs) + list(a.runs):
        for rec in (records(a.results, run) or {}).values():
            low = (rec.get("final_reply") or "").lower()
            for cd in cards_for(rec):
                card_checks += 1
                named = cd["product_id"].lower() in low or (cd.get("design") or "~").lower() in low
                has_img = bool(cd.get("image")) and u2s.get(cd["image"]) == cd["product_id"]
                img_ok += has_img
                if not named or not has_img:
                    card_bad.append({"run": run, "id": rec["id"], "card": cd["product_id"], "named": named,
                                     "image_of_this_sku": has_img})
    tm = media.lookup_timing(n_rounds=3)
    n = len([r for r in rows])
    right = sum(r["right"] for r in rows)
    wrong = sum(r["wrong_sku"] for r in rows)
    share = right / n if n else 0
    met = {"right": n > 0 and share >= 0.95, "wrong": wrong == 0, "cards": not card_bad, "lookup": tm["p95_ms"] <= 50}
    L = [f"# Objective 5, Step 7: product images ({split} cases)", "",
         "| Target | Result | Met |", "|---|---|---|",
         f"| Right SKU and view on at least 95% of image requests | {right}/{n} ({100 * share:.1f}%) | "
         f"{'yes' if met['right'] else 'NO'} |",
         f"| No image of a different SKU (on a card, or as the watch asked for) | {wrong} replies showed one | {'yes' if met['wrong'] else 'NO'} |",
         f"| Cards match the products the reply names (and show that SKU's picture) | {card_checks - len(card_bad)}/"
         f"{card_checks} cards, runs: {', '.join(list(cards_runs) + list(a.runs))} | {'yes' if met['cards'] else 'NO'} |",
         f"| Image lookup p95 at most 50 ms | {tm['p95_ms']} ms (p50 {tm['p50_ms']}, {tm['n']} lookups; "
         f"table load {tm['load_ms']} ms) | {'yes' if met['lookup'] else 'NO'} |", "",
         f"**All targets: {'met' if all(met.values()) else 'NOT met'}**", "", "## By kind and language", "",
         "| Run | Kind | Language | Right |", "|---|---|---|---:|"]
    from collections import defaultdict
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        k = (r["run"], r["kind"], r["language"])
        agg[k][0] += r["right"]
        agg[k][1] += 1
    for k in sorted(agg):
        L.append(f"| {k[0]} | {k[1]} | {k[2]} | {agg[k][0]}/{agg[k][1]} |")
    bad = [r for r in rows if not r["right"] or r["wrong_sku"]]
    if bad:
        L += ["", "## Misses", ""]
        for r in bad:
            L.append(f"- {r['run']} {r['id']} ({r['kind']}, {r['language']}): expected "
                     f"{(r['expected'] or {}).get('skus', ['none'])[:3]} {(r['expected'] or {}).get('view', '')}; got "
                     f"{r['got']}; shown {r['shown']}; route {r['route']}; reply: {str(r['reply'])[:140]!r}"
                     + (f"; error {r['error']}" if r.get("error") else ""))
    if card_bad:
        L += ["", "## Cards that do not match", ""] + [f"- {json.dumps(x)}" for x in card_bad[:30]]
    od = os.path.join(a.results, "_images_step7")
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, f"report_{split}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(od, f"report_{split}.json"), "w", encoding="utf-8") as f:
        json.dump({"met": met, "right": right, "n": n, "wrong_sku": wrong, "cards_checked": card_checks,
                   "cards_bad": card_bad, "lookup": tm, "rows": rows}, f, indent=1, ensure_ascii=False)
    print("\n".join(L))
    return 0 if all(met.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
