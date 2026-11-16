"""
Mock kiosk tools over the generated catalogue.

The tools read the *kiosk* (noisy) copy of the data, the way a real kiosk
would read a company's internal exports, and normalise it on load:
abbreviations are expanded, water-resistance units are converted to metres,
colour casing is fixed and missing values become None.

Every tool returns a plain dict (JSON-serialisable). Errors are returned as
data, e.g. {"error": "not_found", "message": "..."}, never raised, so the
language model can read them and respond.

Internal fields (cost_price, staff_notes, EAN, HSN) are never returned.

Usage from the eval harness:
    from tools.mock_tools import call_tool
    result = call_tool("search_catalogue", {"price_max": 15000, "gender": "men"})
"""

import csv
import json
import os
import re
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("SLM_DATA_DIR", os.path.join(HERE, "..", "data", "kiosk"))
META_PATH = os.path.join(DATA_DIR, "..", "meta.json")
STAFF_LOG = os.environ.get("SLM_STAFF_LOG", os.path.join(DATA_DIR, "..", "staff_requests.log"))

UNABBREV = {
    "case_material": {"SS 316L": "Stainless Steel 316L", "SS": "Stainless Steel", "TI": "Titanium"},
    "glass": {"MIN": "Mineral", "SAPH": "Sapphire", "ACR": "Acrylic"},
    "function": {"P3H+D": "3 hands + date", "P3H": "3 hands", "P2H": "2 hands",
                 "CHRONO+D": "chronograph + date", "DD": "day-date", "MF": "multifunction"},
    "strap_material": {"FKM": "rubber", "SIL": "silicone", "LTHR": "leather", "SS bracelet": "metal"},
}
STALE_HOURS = 48
DEFAULT_LIMIT, MAX_LIMIT = 5, 10

_DB = None
_TICKET = [0]


# --------------------------------------------------------------------------
# Loading and normalisation
# --------------------------------------------------------------------------

def _read(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_water_resistance(value):
    """'100', '100M', '10 ATM', '100 m / 10 bar' -> 100 (metres). Empty -> None."""
    if value is None or str(value).strip() == "":
        return None
    v = str(value).strip().upper()
    m = re.match(r"^(\d+)\s*(ATM|BAR)$", v)
    if m:
        return int(m.group(1)) * 10
    m = re.match(r"^(\d+)", v)
    return int(m.group(1)) if m else None


def _clean(value):
    v = (value or "").strip()
    return v if v else None


def _load():
    global _DB
    if _DB is not None:
        return _DB
    meta = {}
    if os.path.exists(META_PATH):
        with open(META_PATH, encoding="utf-8") as f:
            meta = json.load(f)
    ref = meta.get("reference_date")
    now = datetime.combine(date.fromisoformat(ref), datetime.min.time()).replace(hour=12) if ref else datetime.now()
    this_store = meta.get("this_store", "ST01")

    styles = {}
    for r in _read("styles.csv"):
        s = {k: _clean(v) for k, v in r.items()}
        for field in ("case_material", "glass", "function"):
            if s.get(field) in UNABBREV[field]:
                s[field] = UNABBREV[field][s[field]]
        s["water_resistance_m"] = parse_water_resistance(s.get("water_resistance_m"))
        for field in ("case_diameter_mm", "warranty_movement_months", "warranty_battery_months"):
            s[field] = int(s[field]) if s.get(field) else None
        s["case_thickness_mm"] = float(s["case_thickness_mm"]) if s.get("case_thickness_mm") else None
        styles[s["style_id"]] = s

    skus = {}
    for r in _read("skus.csv"):
        k = {f: _clean(v) for f, v in r.items()}
        if k.get("strap_material") in UNABBREV["strap_material"]:
            k["strap_material"] = UNABBREV["strap_material"][k["strap_material"]]
        for field in ("dial_colour", "strap_colour", "case_finish", "strap_material"):
            if k.get(field):
                k[field] = k[field].lower()
        k["mrp"] = int(k["mrp"])
        skus[k["sku"]] = k

    stores = {r["store_id"]: dict(r, distance_km=float(r["distance_km"])) for r in _read("stores.csv")}
    inventory = {}
    for r in _read("inventory.csv"):
        inventory[(r["store_id"], r["sku"])] = dict(
            qty_display=int(r["qty_display"]), qty_backroom=int(r["qty_backroom"]),
            updated_at=r["updated_at"])
    promos = _read("prices_promos.csv")
    _DB = dict(styles=styles, skus=skus, stores=stores, inventory=inventory, promos=promos,
               now=now, this_store=this_store)
    return _DB


def reload(data_dir=None):
    """Force a reload, optionally from another data directory (e.g. data/clean)."""
    global _DB, DATA_DIR, META_PATH
    if data_dir:
        DATA_DIR = data_dir
        META_PATH = os.path.join(DATA_DIR, "..", "meta.json")
    _DB = None
    _WORDS.clear()
    return _load()


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _err(kind, message):
    return {"error": kind, "message": message}


def _resolve(product_id):
    """Return a list of SKUs for a SKU or style ID (style -> all its SKUs)."""
    db = _load()
    pid = (product_id or "").strip()
    if pid in db["skus"]:
        return [db["skus"][pid]]
    pid_up = pid.upper()
    if pid_up in db["styles"]:
        return [k for k in db["skus"].values() if k["style_id"] == pid_up]
    return []


def _stock(store_id, sku):
    db = _load()
    return db["inventory"].get((store_id, sku), dict(qty_display=0, qty_backroom=0, updated_at=None))


def _in_stock_here(sku):
    s = _stock(_load()["this_store"], sku)
    return s["qty_display"] + s["qty_backroom"] > 0


def _show(v):
    return v if v not in (None, "") else "not listed"


def _summary(k):
    db = _load()
    s = db["styles"][k["style_id"]]
    return {
        "product_id": k["sku"], "name": k["product_name"], "mrp": k["mrp"],
        "collection": s["collection"], "sub_brand": s["sub_brand"], "gender": s["gender"],
        "style": s["style_tag"], "movement": s["movement"],
        "case_diameter_mm": _show(s["case_diameter_mm"]), "dial_colour": _show(k["dial_colour"]),
        "strap": f"{_show(k['strap_colour'])} {k['strap_material']}",
        "water_resistance_m": _show(s["water_resistance_m"]),
        "in_stock_here": _in_stock_here(k["sku"]), "status": k["status"],
    }


def _warranty_text(s):
    parts = [f"{s['warranty_movement_months']} months on the movement"]
    if s["warranty_battery_months"]:
        parts.append(f"{s['warranty_battery_months']} months on the battery")
    return ", ".join(parts) + " from the date of purchase"


def _details(k):
    db = _load()
    s = db["styles"][k["style_id"]]
    variants = [{"product_id": v["sku"], "dial_colour": _show(v["dial_colour"]),
                 "strap": f"{_show(v['strap_colour'])} {v['strap_material']}", "mrp": v["mrp"],
                 "status": v["status"]}
                for v in db["skus"].values() if v["style_id"] == k["style_id"]]
    return {
        "product_id": k["sku"], "style_id": k["style_id"], "name": k["product_name"],
        "sub_brand": s["sub_brand"], "collection": s["collection"], "gender": s["gender"],
        "style": s["style_tag"], "movement": s["movement"], "display": s["display"],
        "function": _show(s["function"]), "case_shape": _show(s["case_shape"]),
        "case_material": _show(s["case_material"]), "case_finish": _show(k["case_finish"]),
        "case_diameter_mm": _show(s["case_diameter_mm"]), "case_thickness_mm": _show(s["case_thickness_mm"]),
        "glass": _show(s["glass"]), "water_resistance_m": _show(s["water_resistance_m"]),
        "luminous": _show(s["lume"]), "dial_colour": _show(k["dial_colour"]),
        "strap_material": k["strap_material"], "strap_colour": _show(k["strap_colour"]),
        "mrp": k["mrp"], "status": k["status"], "warranty": _warranty_text(s),
        "country_of_origin": _show(s["country_of_origin"]),
        "description": k["description"], "variants": variants,
    }


def _gender_ok(wanted, actual):
    if not wanted:
        return True
    if wanted in ("men", "women"):
        return actual in (wanted, "unisex")
    return actual == wanted


# --------------------------------------------------------------------------
# Free-text matching for search_catalogue (Objective 3, Step 2)
# --------------------------------------------------------------------------
# Before Step 2 the query was matched as raw substrings of the product text, so the generic word "watch" (and "men"
# inside "women") matched every product: "dress watch" returned all 1,391 active SKUs. Now the query is split into
# words, generic words are dropped, plurals are folded, and a word must match a whole word of the product text
# (or, from 4 letters, the start of one: "chrono" finds "chronograph"). Material, glass, function, movement and
# lume are part of the searchable text, because the query field is where those features go. When some products
# match every query word, only those are returned; otherwise products matching some words come back, best first.

SEARCH_STOPWORDS = frozenset("""
watch watches wristwatch wristwatches timepiece timepieces a an the for with and or of in on to at by from me my i
we you your our show find want need looking look some any good nice best new latest please something one ones
under below above over around about less more than within upto up rs inr rupee rupees price budget cost range
men mens man male gents gent women womens woman female ladies lady boy boys girl girls kid kids unisex
dial dials strap straps band colour color coloured colored
ghadi ghadiyan ghari wali wala wale ke ki ka liye koi kuch dikhao dikhaiye chahiye hai hain mein mujhe mere
""".split())


def _fold(w):
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith(("ches", "shes", "xes", "sses")):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def query_tokens(query):
    """Content words of a search query: lower-cased, plurals folded, generic words dropped."""
    out = []
    for w in re.findall(r"[a-z0-9]+", (query or "").lower()):
        if len(w) < 2 or w in SEARCH_STOPWORDS:
            continue
        f = _fold(w)
        if f not in SEARCH_STOPWORDS and f not in out:
            out.append(f)
    return out


_WORDS = {}

# Objective 3, Step 3 ("honest tools", on when HONEST is set by the harness's --tool-view compact):
#   - specification words (glass, materials, movement, strap, functions, water use, lume) are matched only against
#     the structured spec fields, never the marketing description. The kiosk copy has descriptions that contradict
#     the spec row on purpose (e.g. "sapphire crystal" on a mineral-glass watch): before this, 7 of the top 10
#     "sapphire" results had mineral glass.
#   - search results say whether every query word matched, and name brands Veyra does not sell.
HONEST = False
SPEC_WORDS = frozenset(_fold(w) for w in """
sapphire mineral acrylic crystal glass titanium steel stainless brass alloy resin plastic ceramic gold silver
automatic quartz solar mechanical kinetic leather metal mesh silicone rubber fabric bracelet chronograph chrono
date day moonphase gmt heart swim swimming snorkel snorkelling snorkeling dive diving water resistant luminous lume
glow
""".split())
OTHER_BRANDS = frozenset("""
rolex omega casio seiko citizen fossil titan fastrack sonata timex tissot apple samsung garmin rado longines
swatch armani guess maxima amazfit fitbit cartier breitling hublot patek tudor gshock
""".split())


def _search_words(k, s):
    key = (DATA_DIR, k["sku"], HONEST)
    if key not in _WORDS:
        fields = (k["product_name"], s["collection"], s["sub_brand"], s.get("style_name"), k["dial_colour"],
                  k["strap_colour"], k["strap_material"], k.get("case_finish"), s["style_tag"], s.get("movement"),
                  s.get("display"), s.get("function"), s.get("case_material"), s.get("glass"), s.get("case_shape"))
        text = " ".join(str(x) for x in fields if x).lower()
        if str(s.get("lume") or "").lower() == "yes":
            text += " luminous lume glow"
        words = {_fold(w) for w in re.findall(r"[a-z0-9]+", text)}
        desc = {_fold(w) for w in re.findall(r"[a-z0-9]+", (k["description"] or "").lower())}
        if HONEST:
            desc -= SPEC_WORDS
        _WORDS[key] = frozenset(words | desc)
    return _WORDS[key]


def _word_hit(token, words):
    if token in words:
        return True
    return len(token) >= 4 and any(w.startswith(token) for w in words)


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------

def search_catalogue(query=None, price_min=None, price_max=None, gender=None, style=None,
                     movement=None, display=None, strap_material=None, dial_colour=None,
                     case_size_min_mm=None, case_size_max_mm=None, water_resistance_min_m=None,
                     sub_brand=None, in_stock_only=False, limit=None):
    db = _load()
    try:
        limit = max(1, min(int(limit or DEFAULT_LIMIT), MAX_LIMIT))
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    tokens = query_tokens(query)
    if HONEST:   # a brand Veyra does not sell is reported, not searched for
        tokens = [t for t in tokens if t not in OTHER_BRANDS]
    results = []
    for k in db["skus"].values():
        if k["status"] == "discontinued":
            continue
        s = db["styles"][k["style_id"]]
        if price_min is not None and k["mrp"] < int(price_min):
            continue
        if price_max is not None and k["mrp"] > int(price_max):
            continue
        if not _gender_ok(gender, s["gender"]):
            continue
        if style and s["style_tag"] != style:
            continue
        if movement and s["movement"] != movement:
            continue
        if display and s["display"] != display:
            continue
        if strap_material and k["strap_material"] != strap_material.lower():
            continue
        if dial_colour and dial_colour.lower() not in (k["dial_colour"] or ""):
            continue
        size = s["case_diameter_mm"]
        if case_size_min_mm is not None and (size is None or size < int(case_size_min_mm)):
            continue
        if case_size_max_mm is not None and (size is None or size > int(case_size_max_mm)):
            continue
        wr = s["water_resistance_m"]
        if water_resistance_min_m is not None and (wr is None or wr < int(water_resistance_min_m)):
            continue
        if sub_brand and s["sub_brand"].lower() != sub_brand.lower():
            continue
        here = _in_stock_here(k["sku"])
        if in_stock_only and not here:
            continue
        score = 0
        if tokens:
            words = _search_words(k, s)
            score = sum(1 for t in tokens if _word_hit(t, words))
            if score == 0:
                continue
        results.append((score, here, k))
    all_matched = bool(tokens and results and max(r[0] for r in results) == len(tokens))
    if all_matched:
        results = [r for r in results if r[0] == len(tokens)]   # all words matched somewhere: keep only those
    # With a budget, show watches closest to the budget first; otherwise cheapest first.
    sign = -1 if price_max is not None else 1
    results.sort(key=lambda x: (-x[0], not x[1], sign * x[2]["mrp"]))
    # One result per style (other colours are listed by get_product_details)
    picked, seen = [], set()
    for _, _, k in results:
        if k["style_id"] in seen:
            continue
        seen.add(k["style_id"])
        picked.append(_summary(k))
        if len(picked) == limit:
            break
    out = {"total_matches": len(results), "styles_matched": len({k["style_id"] for _, _, k in results}),
           "results": picked}
    if HONEST:
        raw = re.findall(r"[a-z0-9]+", (query or "").lower())
        out.update(shown=len(picked), query_words=tokens, all_words_matched=all_matched if tokens else None,
                   not_carried_brands=sorted({w for w in raw if w in OTHER_BRANDS}))
    return out


def get_product_details(product_id):
    found = _resolve(product_id)
    if not found:
        return _err("not_found", f"No watch with ID '{product_id}'.")
    active = [k for k in found if k["status"] != "discontinued"] or found
    return _details(active[0])


def compare_products(product_ids, attributes=None):
    if not isinstance(product_ids, list) or not 2 <= len(product_ids) <= 3:
        return _err("invalid_arguments", "Give 2 or 3 product IDs to compare.")
    rows, missing = [], []
    for pid in product_ids:
        found = _resolve(pid)
        if not found:
            missing.append(pid)
            continue
        rows.append(_details(found[0]))
    if missing:
        return _err("not_found", f"Unknown product IDs: {', '.join(missing)}.")
    default = ["name", "mrp", "movement", "function", "case_diameter_mm", "case_thickness_mm",
               "case_material", "glass", "water_resistance_m", "strap_material", "dial_colour",
               "luminous", "warranty", "status"]
    attrs = attributes or default
    unknown = [a for a in attrs if a not in rows[0]]
    if unknown:
        return _err("invalid_arguments", f"Unknown attributes: {', '.join(unknown)}. Valid: {', '.join(default)}.")
    return {"comparison": [{"product_id": r["product_id"], **{a: r[a] for a in attrs}} for r in rows]}


def check_inventory(product_id, colour=None, store_id=None):
    db = _load()
    store_id = store_id or db["this_store"]
    if store_id not in db["stores"]:
        return _err("not_found", f"Unknown store '{store_id}'.")
    found = _resolve(product_id)
    if not found:
        return _err("not_found", f"No watch with ID '{product_id}'.")
    if colour:
        c = colour.lower()
        matched = [k for k in found if c in (k["dial_colour"] or "") or c in (k["strap_colour"] or "")
                   or c in (k["case_finish"] or "")]
        if not matched:
            return {"product_id": product_id, "colour": colour, "available": False,
                    "message": f"This watch does not come in {colour}.",
                    "available_colours": sorted({f"{_show(k['dial_colour'])} dial, {_show(k['strap_colour'])} {k['strap_material']}" for k in found})}
        found = matched

    out = []
    for k in found:
        st = _stock(store_id, k["sku"])
        stale = False
        if st["updated_at"]:
            age_h = (db["now"] - datetime.strptime(st["updated_at"], "%Y-%m-%d %H:%M")).total_seconds() / 3600
            stale = age_h > STALE_HOURS
        entry = {
            "product_id": k["sku"], "name": k["product_name"], "status": k["status"],
            "store": db["stores"][store_id]["name"],
            "in_stock": st["qty_display"] + st["qty_backroom"] > 0,
            "on_display": st["qty_display"], "in_backroom": st["qty_backroom"],
            "as_of": st["updated_at"], "stock_data_may_be_outdated": stale,
        }
        if k["status"] == "pre_booking":
            entry["note"] = f"Not yet launched (launch {db['styles'][k['style_id']]['launch_date'] or 'date not listed'}); pre-booking available through staff."
        elif k["status"] == "discontinued":
            entry["note"] = "This model is discontinued; only remaining display pieces may be available."
        others = []
        for sid, store in db["stores"].items():
            if sid == store_id:
                continue
            o = _stock(sid, k["sku"])
            qty = o["qty_display"] + o["qty_backroom"]
            if qty > 0:
                others.append({"store": store["name"], "distance_km": store["distance_km"], "quantity": qty})
        entry["other_stores_with_stock"] = sorted(others, key=lambda x: x["distance_km"])
        out.append(entry)
    return {"results": out}


def get_alternatives(product_id, reason):
    if reason not in ("out_of_stock", "cheaper", "similar_style"):
        return _err("invalid_arguments", "reason must be out_of_stock, cheaper or similar_style.")
    db = _load()
    found = _resolve(product_id)
    if not found:
        return _err("not_found", f"No watch with ID '{product_id}'.")
    base = found[0]
    bs = db["styles"][base["style_id"]]
    cands = []
    for k in db["skus"].values():
        if k["status"] != "active" or not _in_stock_here(k["sku"]):
            continue
        s = db["styles"][k["style_id"]]
        same_style = k["style_id"] == base["style_id"]
        if reason != "out_of_stock" and same_style:
            continue
        if s["style_tag"] != bs["style_tag"] or not _gender_ok(bs["gender"], s["gender"]):
            continue
        ratio = k["mrp"] / base["mrp"]
        if reason == "cheaper":
            if k["mrp"] >= base["mrp"]:
                continue
            score = ratio  # closest cheaper first
        elif reason == "similar_style":
            if not 0.75 <= ratio <= 1.25:
                continue
            score = 1 - abs(1 - ratio) + (0.3 if s["collection"] == bs["collection"] else 0)
        else:  # out_of_stock
            if not 0.7 <= ratio <= 1.3:
                continue
            score = (1 - abs(1 - ratio)) + (1.0 if same_style else 0) + (0.3 if s["collection"] == bs["collection"] else 0)
        cands.append((score, k))
    cands.sort(key=lambda x: -x[0])
    picked, seen_styles = [], set()
    for _, k in cands:
        if k["style_id"] in seen_styles:
            continue
        seen_styles.add(k["style_id"])
        picked.append(_summary(k))
        if len(picked) == 3:
            break
    if not picked:
        return {"alternatives": [], "message": "No suitable in-stock alternatives found; consider calling staff."}
    return {"based_on": base["sku"], "reason": reason, "alternatives": picked}


def call_staff(reason, product_id=None, note=None):
    valid = ("try_on", "purchase", "question_unanswered", "service", "other")
    if reason not in valid:
        return _err("invalid_arguments", f"reason must be one of: {', '.join(valid)}.")
    _TICKET[0] += 1
    ticket = f"REQ-{_TICKET[0]:04d}"
    record = {"ticket": ticket, "reason": reason, "product_id": product_id, "note": note,
              "time": datetime.now().isoformat(timespec="seconds")}
    try:
        with open(STAFF_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except OSError:
        pass
    return {"status": "notified", "ticket": ticket,
            "message": "A staff member has been notified and will come to the kiosk shortly.",
            "expected_wait_minutes": 3}


def get_offers(product_id):
    db = _load()
    found = _resolve(product_id)
    if not found:
        return _err("not_found", f"No watch with ID '{product_id}'.")
    k = found[0]
    s = db["styles"][k["style_id"]]
    today = db["now"].date()
    valid, upcoming = [], []
    for p in db["promos"]:
        target = s["sub_brand"] if p["applies_to_type"] == "sub_brand" else s["collection"]
        if p["applies_to"] != target or k["mrp"] < int(p["min_mrp"]):
            continue
        start, end = date.fromisoformat(p["start_date"]), date.fromisoformat(p["end_date"])
        info = {"offer": p["name"], "conditions": p["conditions"], "valid_until": p["end_date"]}
        if start <= today <= end:
            if p["type"] == "percent_off":
                disc = min(k["mrp"] * int(p["value"]) // 100, int(p["max_discount"]) or 10**9)
            elif p["type"] == "flat_off":
                disc = int(p["value"])
            else:
                disc = 0
            info["discount"] = disc
            info["stackable"] = p["stackable"] == "yes"
            valid.append(info)
        elif start > today:
            info["starts"] = p["start_date"]
            upcoming.append(info)
    best = 0
    if valid:
        non_stack = [o["discount"] for o in valid if not o["stackable"]]
        stack = sum(o["discount"] for o in valid if o["stackable"])
        best = (max(non_stack) if non_stack else 0) + stack
    return {"product_id": k["sku"], "mrp": k["mrp"], "offers": valid,
            "price_after_best_offer": k["mrp"] - best, "upcoming_offers": upcoming}


# --------------------------------------------------------------------------
# Dispatcher for the eval harness / llama-server tool calls
# --------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "search_catalogue": search_catalogue,
    "get_product_details": get_product_details,
    "compare_products": compare_products,
    "check_inventory": check_inventory,
    "get_alternatives": get_alternatives,
    "call_staff": call_staff,
    "get_offers": get_offers,
}


def call_tool(name, arguments):
    """Run a tool by name. `arguments` may be a dict or a JSON string (as returned by llama-server)."""
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return _err("unknown_tool", f"No tool named '{name}'.")
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments or "{}")
        except json.JSONDecodeError:
            return _err("invalid_arguments", "Arguments are not valid JSON.")
    if not isinstance(arguments, dict):
        return _err("invalid_arguments", "Arguments must be a JSON object.")
    try:
        return fn(**arguments)
    except TypeError as e:
        return _err("invalid_arguments", str(e))
    except (ValueError, KeyError) as e:
        return _err("invalid_arguments", f"Bad value: {e}")


def load_schemas(include_optional=False):
    with open(os.path.join(HERE, "schemas.json"), encoding="utf-8") as f:
        schemas = json.load(f)
    if include_optional:
        with open(os.path.join(HERE, "schemas_optional.json"), encoding="utf-8") as f:
            schemas += json.load(f)
    return schemas


if __name__ == "__main__":
    print(json.dumps(call_tool("search_catalogue", {"gender": "men", "style": "formal", "price_max": 15000,
                                                    "strap_material": "metal"}), indent=2, ensure_ascii=False))
