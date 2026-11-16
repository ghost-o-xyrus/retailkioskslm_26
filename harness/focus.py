"""
Objective 3, Step 11: the product in focus and follow-up questions.

    product_in_focus(messages)  the watch the conversation is about: the newest product code or design name in the
                                earlier turns (customer or kiosk), before the latest customer message
    is_followup(text, info)     the latest message names no product (no code, no catalogue name) and no store topic
                                (hours, payment, gift wrapping, returns...; unless it also refers back), and either
                                refers back ("it", "this one", "iska", "ye"...) or is short (6 words or fewer)

A single-turn case has no earlier turns, so nothing here can change it.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from tools import mock_tools  # noqa: E402

CODE_RE = re.compile(r"\b(\d{4}[A-Z]{2}\d{2})\b")
DESIGN_RE = re.compile(r"\bV(\d{4})\b")
ANAPHOR = re.compile(r"(?<![a-z])(it|its|it's|this one|that one|this watch|that watch|the same|them|they|"
                     r"iska|iski|iske|isme|ismein|isko|ye|yeh|woh|wo|vo|is watch|us watch)(?![a-z])")
STOCK_Q = re.compile(r"(?<![a-z])(in stock|stock mein|stock me|available here|on display|have it here|can i get it "
                     r"(today|here)|abhi milega|available hai)(?![a-z])")
# Step 9: "milta hai", "aata hai", "strap mein" added ("Kya ye black strap mein milta hai?" was missed)
COLOUR_Q = re.compile(r"(?<![a-z])(comes? (in|with)|available in|aati hai|milti hai|milta hai|milte hai|aata hai|aate hai|"
                      r"milega|colou?r|dial mein|strap mein)(?![a-z])")
# Store-level topics: a message naming one of these is a new question, not a follow-up about the watch, unless it
# also refers back ("is it covered by the return policy?"). Product attributes (warranty, glass...) are not here.
POLICY_RE = re.compile(r"(?<![a-z])(store|shop|open|opening|close|closing|khula|khulta|band hota|hours|timing|timings|"
                       r"gift ?wrap\w*|wrapping|payment|pay|upi|card|cash|emi|delivery|deliver|home delivery|return|"
                       r"returns|exchange|refund|repair|service|servicing|engrav\w*|parking|location|address|branch|"
                       r"offer|offers|discount|sale|policy|claim|membership|loyalty|gift card|invoice|bill)(?![a-z])")
_NAMES = {}


def _names():
    if not _NAMES:
        for st in mock_tools._load()["styles"].values():
            _NAMES[st["style_name"].lower()] = st["style_id"]
    return _NAMES


def product_in_focus(messages):
    """{"style_id", "code" (an SKU or None), "name"} or None."""
    users = [i for i, m in enumerate(messages) if m.get("role") == "user"]
    if len(users) < 2:
        return None
    db = mock_tools._load()
    for m in reversed(messages[:users[-1]]):
        text = m.get("content") if isinstance(m.get("content"), str) else ""
        if m.get("role") == "tool":
            text = m.get("content") or ""
        for code in reversed(CODE_RE.findall(text or "")):
            sku = db["skus"].get(code)
            if sku:
                st = db["styles"][sku["style_id"]]
                return {"style_id": st["style_id"], "code": code, "name": st["style_name"]}
        for d in reversed(DESIGN_RE.findall(text or "")):
            st = db["styles"].get("V" + d)
            if st:
                return {"style_id": st["style_id"], "code": None, "name": st["style_name"]}
        low = (text or "").lower()
        hits = [(low.rfind(n), n) for n in _names() if n in low]
        if hits:
            n = max(hits)[1]
            sid = _names()[n]
            return {"style_id": sid, "code": None, "name": mock_tools._load()["styles"][sid]["style_name"]}
    return None


# Objective 5, Step 9: "the second one", "doosra wala": a watch picked by its place in the kiosk's last list
ORDINAL_RE = re.compile(r"(?<![a-z])(?:the\s+)?(first|second|third|1st|2nd|3rd|last|pehla|pehli|pehle|pahla|pahli|"
                        r"doosra|doosri|doosre|dusra|dusri|dusre|teesra|teesri|teesre|tisra|tisri|aakhri|akhri)"
                        r"\s+(one|wala|wali|wale|option)(?![a-z])"
                        r"|(?<![a-z])(?:number|no\.?|#)\s*([123])(?![0-9a-z])")
_ORD = {"first": 0, "1st": 0, "pehla": 0, "pehli": 0, "pehle": 0, "pahla": 0, "pahli": 0, "1": 0,
        "second": 1, "2nd": 1, "doosra": 1, "doosri": 1, "doosre": 1, "dusra": 1, "dusri": 1, "dusre": 1, "2": 1,
        "third": 2, "3rd": 2, "teesra": 2, "teesri": 2, "teesre": 2, "tisra": 2, "tisri": 2, "3": 2,
        "last": -1, "aakhri": -1, "akhri": -1}


def listed_products(text):
    """The watches a kiosk reply names, in the order it names them: product codes, else design names."""
    db = mock_tools._load()
    out, seen = [], set()
    for m in CODE_RE.finditer(text or ""):
        sku = db["skus"].get(m.group(1))
        if sku and sku["style_id"] not in seen:
            seen.add(sku["style_id"])
            out.append((m.start(), {"style_id": sku["style_id"], "code": m.group(1),
                                    "name": db["styles"][sku["style_id"]]["style_name"]}))
    low = (text or "").lower()
    for n, sid in _names().items():
        i = low.find(n)
        if i >= 0 and sid not in seen:
            seen.add(sid)
            out.append((i, {"style_id": sid, "code": None, "name": db["styles"][sid]["style_name"]}))
    return [p for _, p in sorted(out, key=lambda x: x[0])]


def ordinal_focus(messages, text):
    """The watch an ordinal reference picks from the kiosk's latest reply that listed two or more watches, or
    None (no ordinal word, no such list, or the place is past the end of the list)."""
    m = ORDINAL_RE.search((text or "").lower())
    if not m or CODE_RE.search(text or "") or DESIGN_RE.search(text or ""):
        return None
    k = _ORD[m.group(1) or m.group(3)]
    users = [i for i, x in enumerate(messages) if x.get("role") == "user"]
    if len(users) < 2:
        return None
    for x in reversed(messages[:users[-1]]):
        if x.get("role") != "assistant" or not isinstance(x.get("content"), str):
            continue
        items = listed_products(x["content"])
        if len(items) >= 2:
            return items[k] if -len(items) <= k < len(items) else None
    return None


def is_followup(text, info=None):
    info = info or {}
    if info.get("codes") or info.get("named") or CODE_RE.search(text or "") or DESIGN_RE.search(text or ""):
        return False
    low = (text or "").lower()
    if any(n in low for n in _names()):
        return False
    if POLICY_RE.search(low) and not ANAPHOR.search(low):
        return False                     # a store question ("Gift wrapping milta hai kya?"), not a follow-up
    return bool(ANAPHOR.search(low)) or len(re.findall(r"\w+", low)) <= 6


def retrieval_query(messages, focus):
    """The current message, then the previous customer message, then the focused watch's name."""
    users = [m["content"] for m in messages if m.get("role") == "user" and isinstance(m.get("content"), str)]
    parts = [users[-1]] + ([users[-2]] if len(users) > 1 else []) + ([focus["name"]] if focus else [])
    return " ".join(parts)


def own_route(text):
    """For a follow-up about the focused watch: stock and colour questions go to the stock route (the harness runs
    check_inventory on the focused code), everything else to the knowledge path."""
    low = (text or "").lower()
    return "stock" if STOCK_Q.search(low) or COLOUR_Q.search(low) else None
