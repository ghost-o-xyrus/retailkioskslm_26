"""
Objective 3, Step 8: the entity check. Two kinds of message get a fixed reply from the harness, with no model call:

  not carried     another brand ("Do you sell Fossil watches?"), a smartwatch or fitness feature, or something
                  that is not a watch ("Do you sell perfume?"), asked with a shopping word (sell, have, available,
                  looking for, chahiye...). Watch brands and smart features also get up to 3 real Veyra watches
                  close to what was asked (digital for smartwatches and G-Shock, automatic for luxury brands).
  missing design  a real collection followed by a capitalised design name that is not in the catalogue
                  ("Veyra Everyday Zenith"): "we don't have a watch called ..." plus up to 3 real designs from
                  that collection.

Both lists come from the catalogue and router/router.py, not from eval cases.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from tools import mock_tools  # noqa: E402
from router.router import NOT_CARRIED  # noqa: E402

SMART = {"smartwatch", "smart watch", "fitness band", "fitness tracker", "counts steps", "step count",
         "notifications", "heart rate", "heart-rate", "gps", "apple watch", "fitbit", "amazfit", "garmin", "samsung"}
ITEMS = {"sunglasses", "wallet", "perfume", "jewellery", "jewelry", "phone", "wall clock", "alarm clock", "table clock"}
HINTS = {"casio": {"display": "digital"}, "g-shock": {"display": "digital", "style": "sport"},
         "rolex": {"movement": "automatic"}, "omega": {"movement": "automatic"}, "tissot": {"movement": "automatic"},
         "longines": {"movement": "automatic"}, "rado": {"movement": "automatic"}, "cartier": {"movement": "automatic"},
         "breitling": {"movement": "automatic"}, "hublot": {"movement": "automatic"}, "patek": {"movement": "automatic"},
         "tudor": {"movement": "automatic"}, "seiko": {"movement": "automatic"}, "citizen": {"movement": "solar"},
         "fossil": {"style": "casual"}, "timex": {"style": "casual"}, "swatch": {"style": "fashion"},
         "armani": {"style": "fashion"}, "guess": {"style": "fashion"}}
SHOP_WORD = re.compile(r"(?<![a-z])(sell|sells|selling|have|has|stock|carry|carries|looking for|look for|want|need|buy|"
                       r"available|show me|get|milega|milegi|milta|chahiye|hai kya|dikhao|rakhte)(?![a-z])")
STOP = {"Watch", "Watches", "Range", "Collection", "Series", "Line", "Model", "Models", "Men", "Women", "For", "In",
        "With", "Available", "Strap", "Dial"}
_CAT = {}


def _catalogue():
    if not _CAT:
        db = mock_tools._load()
        cols = sorted({s["collection"] for s in db["styles"].values()}, key=len, reverse=True)
        _CAT["designs"] = {s["style_name"].lower() for s in db["styles"].values()}
        _CAT["rx"] = re.compile(r"\b(" + "|".join(re.escape(c) for c in cols) + r") ([A-Z][a-z]+)\b")
    return _CAT


def not_carried(text):
    """(display name, kind, matched terms) or None. kind: brand | smart | item."""
    tl = " " + (text or "").lower() + " "
    if not SHOP_WORD.search(tl):
        return None
    spans = []
    for b in NOT_CARRIED:
        for m in re.finditer(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", tl):
            spans.append((m.start(), m.end(), b))
    if not spans:
        return None
    spans.sort()
    s0, e0, _ = spans[0]
    terms = [t for _, _, t in spans]
    for s, e, _ in spans[1:]:
        if s <= e0 + 1:
            e0 = max(e0, e)
    name = text[s0 - 1:e0 - 1].strip()       # the original spelling ("Casio G-Shock")
    kind = "smart" if any(t in SMART for t in terms) else ("item" if all(t in ITEMS for t in terms) else "brand")
    return name, kind, terms


def missing_design(text):
    """(collection, word) for 'Collection Word' where that design does not exist, else None."""
    c = _catalogue()
    for m in c["rx"].finditer(text or ""):
        col, w = m.group(1), m.group(2)
        if w in STOP:
            continue
        if f"{col} {w}".lower() not in c["designs"]:
            return col, w
    return None


def _short(row):
    """The design name ('Steel Smart Atlas') from the catalogue, else the first words of the product name."""
    st = mock_tools._load()["styles"].get("V" + str(row.get("product_id", ""))[:4])
    if st:
        return st["style_name"]
    words = (row.get("name") or "").split()
    words = words[1:] if words and words[0] == "Veyra" else words
    return " ".join(words[:2])


def _search(args, keep=lambda r: True):
    """Up to 3 results that pass keep(), from a wider search (the call is logged with the arguments given)."""
    res = mock_tools.search_catalogue(**dict(args, limit=10))
    rows = [r for r in res.get("results") or [] if keep(r)][:3]
    return dict(res, results=rows, shown=len(rows))


def _lines(results):
    out = []
    for i, r in enumerate(results[:3], 1):
        price = "price not listed" if r.get("mrp") is None else f"Rs {int(r['mrp']):,}"
        out.append(f"{i}. {r['product_id']} {_short(r)} - {price} ({r.get('dial_colour') or 'dial not listed'} dial, "
                   f"{r.get('strap') or 'strap not listed'})")
    return out


def reply(text, hinglish=False):
    """None, or {"kind", "reply", "search": (arguments, result) or None, "name"} for a fixed entity reply."""
    nc = not_carried(text)
    if nc:
        name, kind, terms = nc
        args = None
        if kind == "smart":
            args = {"display": "digital"}
        elif kind == "brand":
            args = next((dict(HINTS[t]) for t in terms if t in HINTS), None)
        res = _search(args, lambda r: r.get("gender") != "kids") if args else None
        rows = (res or {}).get("results") or []
        if kind == "item":
            msg = (f"Maaf kijiye, is store mein sirf Veyra watches milti hain, {name} nahi." if hinglish else
                   f"Sorry, this store sells only Veyra watches, so we don't have {name}.")
        elif kind == "smart":
            msg = ("Maaf kijiye, Veyra smartwatch ya fitness tracker nahi bechta." if hinglish else
                   "Sorry, Veyra doesn't sell smartwatches or fitness trackers.")
        else:
            msg = (f"Maaf kijiye, hum {name} nahi bechte; is store mein sirf Veyra watches milti hain." if hinglish else
                   f"Sorry, we don't sell {name} here; this store sells only Veyra watches.")
        if rows:
            head = ("Yeh Veyra watches dekh sakte hain:" if hinglish else
                    ("Here are some Veyra digital watches:" if kind == "smart" else
                     "Here are some Veyra watches you might like instead:"))
            tail = "Inmein se kisi ki details chahiye?" if hinglish else "Would you like details on any of these?"
            msg = "\n".join([msg, head] + _lines(rows) + [tail])
        return {"kind": "not_carried", "name": name, "reply": msg, "search": (args, res) if args else None}
    md = missing_design(text)
    if md:
        col, w = md
        args = {"query": col}
        names = sorted(st["style_name"] for st in mock_tools._load()["styles"].values()
                       if st["collection"].lower() == col.lower() and st.get("status", "active") == "active")
        rows = []
        for nm in names:          # one search per real design in the collection, cheapest variant of each
            got = [r for r in mock_tools.search_catalogue(query=nm, limit=3).get("results") or []
                   if _short(r).lower() == nm.lower()]
            rows += got[:1]
            if len(rows) == 3:
                break
        res = {"total_matches": len(names), "results": rows, "shown": len(rows), "collection_designs": names}
        rows = res.get("results") or []
        if hinglish:
            msg = f"Maaf kijiye, {col} {w} naam ki koi watch hamare paas nahi hai."
            if rows:
                msg = "\n".join([msg, f"{col} ke yeh designs hain:"] + _lines(rows) + ["Inmein se kisi ki details chahiye?"])
        else:
            msg = f"Sorry, we don't have a watch called {col} {w}."
            if rows:
                msg = "\n".join([msg, f"Here are {col} designs we do have:"] + _lines(rows) +
                                ["Would you like details on any of these?"])
        return {"kind": "missing_design", "name": f"{col} {w}", "reply": msg, "search": (args, res)}
    return None
