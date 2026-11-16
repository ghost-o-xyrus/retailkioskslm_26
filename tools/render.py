"""
Compact tool-output view (Objective 3, Step 3): what the model reads after a tool call.

The mock tools still return full dicts. Those are logged unchanged and the scorer reads them. With the harness's
`--tool-view compact`, the model is shown this text instead of the JSON:
  - one line per watch, with only the fields a shopper compares: id, design name, who and what it is for, price, size,
    dial and strap, stock here. Movement and water resistance appear when the search filtered on them.
  - no marketing description (the kiosk copy's descriptions sometimes contradict the spec row)
  - honest headers: "showing 3 of 260", whether every search word matched, brands Veyra does not sell
  - missing values print as "not listed", never blank
Typical sizes against the JSON view: search 3 results about 130 tokens instead of about 500 for 5; details about
130 instead of about 420.
"""


def _v(x, unit=""):
    if x is None or x == "" or x == "not listed":
        return "not listed"
    return f"{x}{unit}"


def _rs(x):
    return "price not listed" if x is None else f"Rs {int(x):,}"


def _short(row):
    """'Veyra Sovereign Atlas White Dial ... for Women' -> 'Sovereign Atlas'."""
    name = row.get("name") or ""
    words = name.split()
    if words and words[0] == "Veyra":
        words = words[1:]
    return " ".join(words[:2]) if words else row.get("product_id", "")


def _stock_word(row):
    v = row.get("in_stock_here")
    return "in stock here" if v else ("not in stock here" if v is not None else "stock not listed")


def _row(i, r, extra=()):
    parts = [f"{i}. {r['product_id']} {_short(r)}",
             f"{_v(r.get('gender'))}, {_v(r.get('style'))}",
             _rs(r.get("mrp")),
             _v(r.get("case_diameter_mm"), " mm"),
             f"{_v(r.get('dial_colour'))} dial, {_v(r.get('strap'))}"]
    if "movement" in extra:
        parts.append(_v(r.get("movement")))
    if "water" in extra:
        parts.append(f"water resistant {_v(r.get('water_resistance_m'), ' m')}")
    parts.append(_stock_word(r))
    if r.get("status") and r["status"] != "active":
        parts.append(r["status"].replace("_", " "))
    return " | ".join(parts)


def _extras(args):
    a = args or {}
    ex = set()
    if a.get("movement"):
        ex.add("movement")
    if a.get("water_resistance_min_m"):
        ex.add("water")
    return ex


def search(args, r):
    n, shown = r.get("total_matches", 0), len(r.get("results", []))
    if n == 0:
        head = ["No watches match this search."]
    else:
        head = [f"Showing {shown} of {n} matching watches ({r.get('styles_matched', n)} designs), one per design."]
    words = r.get("query_words") or []
    if words and r.get("all_words_matched") is False and n:
        head.append(f"No watch matches all of: {', '.join(words)}. These are the closest matches, not exact ones.")
    for b in r.get("not_carried_brands") or []:
        head.append(f"Veyra does not sell {b.title()} watches; this store sells only Veyra.")
    ex = _extras(args)
    return "\n".join(head + [_row(i, x, ex) for i, x in enumerate(r.get("results", []), 1)])


def details(r):
    lines = [f"{r['product_id']} {r.get('name', '')} (design {r.get('style_id')})",
             f"For: {_v(r.get('gender'))}, {_v(r.get('style'))} | {_rs(r.get('mrp'))} | {_v(r.get('status'))}",
             f"Case: {_v(r.get('case_diameter_mm'), ' mm')} {_v(r.get('case_shape')).lower()}, "
             f"{_v(r.get('case_material'))}, {_v(r.get('case_finish'))} finish, "
             f"thickness {_v(r.get('case_thickness_mm'), ' mm')} | Glass: {_v(r.get('glass'))}",
             f"Movement: {_v(r.get('movement'))}, {_v(r.get('display'))}, {_v(r.get('function'))} | "
             f"Water resistance: {_v(r.get('water_resistance_m'), ' m')} | Luminous: {_v(r.get('luminous'))}",
             f"Dial: {_v(r.get('dial_colour'))} | Strap: {_v(r.get('strap_colour'))} {_v(r.get('strap_material'))}",
             f"Warranty: {_v(r.get('warranty'))} | Made in: {_v(r.get('country_of_origin'))}"]
    others = [v for v in r.get("variants", []) if v.get("product_id") != r.get("product_id")]
    if others:
        lines.append("Other versions: " + "; ".join(
            f"{v['product_id']} {_v(v.get('dial_colour'))} dial, {_v(v.get('strap'))}, {_rs(v.get('mrp'))}"
            + ("" if v.get("status") == "active" else f" ({v.get('status')})") for v in others))
    lines.append("Stock is not part of this record: use check_inventory.")
    return "\n".join(lines)


def inventory(r):
    if r.get("available") is False:
        return f"{r.get('message')} Available versions: {'; '.join(r.get('available_colours') or [])}."
    out = []
    for e in r.get("results", []):
        here = (f"in stock here ({e.get('on_display', 0)} on display, {e.get('in_backroom', 0)} in the back room)"
                if e.get("in_stock") else "not in stock at this store")
        s = f"{e['product_id']} {_short(e)}: {here}, as of {_v(e.get('as_of'))}"
        if e.get("stock_data_may_be_outdated"):
            s += " (stock data may be outdated)"
        if e.get("note"):
            s += f". {e['note']}"
        others = e.get("other_stores_with_stock") or []
        s += ". Other stores: " + ("; ".join(f"{o['store']} {o['distance_km']} km ({o['quantity']})" for o in others)
                                   if others else "none") + "."
        out.append(s)
    return "\n".join(out) or "No stock record."


def alternatives(r):
    alts = r.get("alternatives") or []
    reason = (r.get("reason") or "").replace("_", " ")
    if not alts:
        return f"No in-stock alternatives to {r.get('based_on')} ({reason})."
    rows = [_row(i, dict(a, in_stock_here=a.get("in_stock_here", True)), set()) for i, a in enumerate(alts, 1)]
    return "\n".join([f"Alternatives to {r.get('based_on')} ({reason}):"] + rows)


def compare(r):
    out = []
    for i, c in enumerate(r.get("comparison", []), 1):
        out.append(f"{i}. {c['product_id']} {_short(c)} | {_rs(c.get('mrp'))} | {_v(c.get('movement'))}, "
                   f"{_v(c.get('function'))} | {_v(c.get('case_diameter_mm'), ' mm')} {_v(c.get('case_material'))}, "
                   f"{_v(c.get('case_thickness_mm'), ' mm')} thick | {_v(c.get('glass'))} glass | water resistant "
                   f"{_v(c.get('water_resistance_m'), ' m')} | {_v(c.get('strap_material'))} strap | "
                   f"{_v(c.get('dial_colour'))} dial | luminous {_v(c.get('luminous'))} | warranty "
                   f"{_v(c.get('warranty'))}")
    return "\n".join(out) or "Nothing to compare."


def staff(r):
    return (f"Staff notified (ticket {r.get('ticket')}). Someone will come to the kiosk in about "
            f"{r.get('expected_wait_minutes', 'a few')} minutes.")


def render(name, args, result):
    """Text the model reads for one tool call. Unknown tools and unexpected shapes fall back to the JSON."""
    import json
    if not isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    if result.get("error"):
        return f"Error ({result['error']}): {result.get('message', '')}"
    if "note" in result and len(result) <= 3:       # harness notes (shown card, loop guard)
        return result["note"]
    try:
        if name == "search_catalogue":
            return search(args, result)
        if name == "get_product_details":
            return details(result)
        if name == "check_inventory":
            return inventory(result)
        if name == "get_alternatives":
            return alternatives(result)
        if name == "compare_products":
            return compare(result)
        if name == "call_staff":
            return staff(result)
    except (KeyError, TypeError, ValueError):
        pass
    return json.dumps(result, ensure_ascii=False)
