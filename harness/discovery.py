"""
Objective 3, Step 6: guided discovery for the shopping route.

Every customer message of the conversation so far is read for shopping slots. The kiosk then either asks one slot
question (at most two in a conversation) or runs exactly one search with every known slot and lets the model write
the recommendation in one request.

    slots = extract_slots(["I need a gift for my wife.", "Office, around 10,000."])
    decide(slots, questions_asked=1, last_text="Office, around 10,000.")   -> "search"
    search_args(slots) -> {"gender": "women", "style": "formal", "price_max": 10000}

Slots: budget (price_min/price_max), recipient (gender; a child of 12 or under -> kids), occasion (style), strap,
size (case_size_min/max_mm), and "hard" product features that are worth a search on their own: movement, display,
water resistance, dial colour, strap, an explicit size in mm, and feature words (sapphire, titanium, chronograph...).
Search when: any hard feature is known, or at least two slots are known, or two questions have been asked already,
or the customer says "just show me" and at least one slot is known. Otherwise ask.
"""

import re

NUM = r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(k\b|thousand|hazaar|hazar|lakh)?"
COLOURS = ("midnight blue", "rose gold", "mother-of-pearl", "black", "white", "blue", "green", "red", "grey", "gray",
           "silver", "gold", "brown", "pink", "purple", "yellow", "orange", "navy", "olive", "cream", "lilac",
           "lavender", "maroon", "teal", "champagne", "bronze", "salmon")
FEATURES = ("sapphire", "titanium", "chronograph", "open heart", "open-heart", "luminous", "glow", "skeleton",
            "moonphase", "gold-tone", "gold tone", "rose gold", "mother-of-pearl", "ceramic", "day-date", "date")
STYLE_WORDS = [  # first match wins
    ("formal", r"office|formal|work wear|workwear|business|boardroom|meeting"),
    ("ethnic", r"weddings?|shaadi|shadi|festive|ethnic|traditional|puja|diwali|sangeet"),
    ("sport", r"sports?|sporty|gym|running|run|trek|hiking|outdoor|fitness|cricket"),
    ("fashion", r"party|parties|fashion|trendy|stylish|funky"),
    ("casual", r"casual|daily|everyday|roz|regular use"),
]
STRAP_WORDS = [("metal", r"metal|bracelet|chain|steel strap|steel band"), ("leather", r"leather"), ("mesh", r"mesh"),
               ("silicone", r"silicone"), ("rubber", r"rubber"), ("fabric", r"fabric|nylon|canvas|nato"),
               ("resin", r"resin|plastic strap")]
MEN = r"men's|mens|for men|for a man|man's|gents|male|for him|husband|father|dad|papa|pitaji|brother|bhai|boyfriend|" \
      r"grandfather|dada|nana|uncle|boss\b(?! lady)"
WOMEN = r"women's|womens|for women|for a woman|ladies|lady|female|for her|wife|mother|mom|mum|mummy|maa\b|sister|" \
        r"behen|didi|girlfriend|grandmother|dadi|nani|aunt"
CHILD = r"son\b|daughter|beta\b|bete|beti|kid|kids|child|children|bachch|boy\b|girl\b"
JUST_SHOW = r"just show|show me (some|any|a few)|anything is fine|any is fine|kuch bhi|koi bhi|whatever|no preference|" \
            r"not sure,? just|dikha do"


def _num(s, unit):
    v = float(s.replace(",", ""))
    if unit in ("k", "thousand", "hazaar", "hazar"):
        v *= 1000
    elif unit == "lakh":
        v *= 100000
    return int(v)


def _budget(t):
    """price_min / price_max from the text, ignoring sizes, depths, ages and product codes."""
    t = re.sub(r"\b\d{4}[a-z]{2}\d{2}\b", " ", t)
    m = re.search(r"between\s+(?:rs\.?\s*|₹\s*)?" + NUM + r"\s*(?:and|to|-)\s*(?:rs\.?\s*|₹\s*)?" + NUM, t)
    if m:
        return {"price_min": _num(m.group(1), m.group(2)), "price_max": _num(m.group(3), m.group(4))}
    m = re.search(NUM + r"\s*(?:-|to)\s*" + NUM + r"\s*(rs|rupees|inr|k\b)?", t)
    if m and (m.group(5) or m.group(4) or m.group(2)):
        lo, hi = _num(m.group(1), m.group(2) or m.group(4)), _num(m.group(3), m.group(4))
        if hi >= 500:
            return {"price_min": lo, "price_max": hi}
    for m in re.finditer(r"(?:rs\.?\s*|₹\s*)?" + NUM + r"(?!\s*(?:mm|m\b|metre|meter|years?|yrs?|saal|%|atm))", t):
        v = _num(m.group(1), m.group(2))
        before = t[max(0, m.start() - 25):m.start()]
        after = t[m.end():m.end() + 20]
        money = bool(m.group(2)) or "rs" in t[max(0, m.start() - 4):m.start() + 4] or "₹" in before[-3:] or \
            re.search(r"budget|under|below|within|upto|up to|around|about|approx|lagbhag|max|less than|more than|"
                      r"above|over|price|spend|cost", before) or re.search(r"^\s*(ke )?(neeche|tak|se kam|se upar|"
                                                                           r"rupees|rs|inr|ka|ki|budget)", after)
        if not money or v < 300:
            continue
        if re.search(r"(above|over|more than|at least|minimum)\s*(rs\.?\s*|₹\s*)?$", before) or \
                re.search(r"^\s*(se upar|se zyada|plus|\+)", after):
            return {"price_min": v}
        return {"price_max": v}
    return {}


def extract_slots(texts):
    """texts: every customer message so far, oldest first. Later messages override earlier ones."""
    s = {}
    for raw in texts:
        t = " " + (raw or "").lower().replace("’", "'") + " "
        s.update(_budget(t))
        age = re.search(r"(?:she's|he's|she is|he is|age|aged|umar)\s*(\d{1,2})|(\d{1,2})\s*(?:years?|yrs?|saal)", t)
        if age:
            s["age"] = int(age.group(1) or age.group(2))
        if re.search(r"(?<![a-z])(" + CHILD + r")", t):
            s["recipient"] = "child"
        if re.search(r"(?<![a-z])(friend|dost|colleague|someone|somebody)(?![a-z])", t):
            s.setdefault("recipient", "friend")
        if re.search(r"(?<![a-z])(" + MEN + r")(?![a-z])", t):
            s["recipient"], s["gender"] = "men", "men"
        if re.search(r"(?<![a-z])(" + WOMEN + r"|saheli)(?![a-z])", t):
            s["recipient"], s["gender"] = "women", "women"
        if re.search(r"unisex|for (me|myself)|for my ?self|apne liye|khud", t):
            s.setdefault("recipient", "self")
        if s.get("recipient") == "child" or re.search(r"(?<![a-z])(" + CHILD + r")", t):
            if s.get("age") is not None and s["age"] <= 12:
                s["gender"] = "kids"
            elif s.get("age") is not None:
                s["gender"] = "women" if re.search(r"daughter|beti|girl", t) else "men"
        for style, rx in STYLE_WORDS:
            if re.search(r"(?<![a-z])(" + rx + r")(?![a-z])", t):
                s["style"] = style
                break
        for strap, rx in STRAP_WORDS:
            if re.search(r"(?<![a-z])(" + rx + r")(?![a-z])", t):
                s["strap"] = strap
                break
        if re.search(r"automatic|self[- ]winding", t):
            s["movement"] = "automatic"
        elif re.search(r"solar|light[- ]powered", t):
            s["movement"] = "solar"
        elif re.search(r"quartz|battery[- ]powered", t):
            s["movement"] = "quartz"
        if re.search(r"digital", t):
            s["display"] = "digital"
        elif re.search(r"analog", t):
            s["display"] = "analog"
        m = re.search(r"(\d{2})\s*mm\s*(or smaller|or less|ya usse kam|max|maximum|and below|or under)", t) or \
            re.search(r"(?:under|below|max|upto|up to)\s*(\d{2})\s*mm", t)
        if m:
            s["size_max"] = int(m.group(1))
            s["size_explicit"] = True
        else:
            m = re.search(r"(\d{2})\s*mm\s*(or bigger|or more|ya usse zyada|minimum|and above)", t) or \
                re.search(r"(?:at least|over|above)\s*(\d{2})\s*mm", t)
            if m:
                s["size_min"] = int(m.group(1))
                s["size_explicit"] = True
            else:
                m = re.search(r"(\d{2})\s*mm", t)
                if m:   # a bare size is the size asked for; relaxation drops it if nothing matches
                    s["size_min"], s["size_max"], s["size_explicit"] = int(m.group(1)), int(m.group(1)), True
                elif re.search(r"(?<![a-z])(small|smaller|chhot[aie]|petite|slim|thin|dainty)(?![a-z])", t):
                    s["size_max"] = 34
                elif re.search(r"(?<![a-z])(big|bigger|large|bad[aie]|chunky|oversized)(?![a-z])", t):
                    s["size_min"] = 42
        m = re.search(r"(\d{2,3})\s*(?:m|metres?|meters?)\b(?!m)", t)
        if m and re.search(r"water|resistan|swim|div", t):
            s["water_min"] = int(m.group(1))
        elif re.search(r"div(e|ing)|snorkel|scuba", t):
            s["water_min"] = 200
        elif re.search(r"swim|pool|tairak|tairne", t):
            s["water_min"] = 100
        elif re.search(r"shower|nahate|rain|barish", t):
            s["water_min"] = 50
        for c in colours():
            if re.search(r"(?<![a-z])" + re.escape(c) + r"(?![a-z])\s*(dial|face)|dial\s*(in\s*)?" + re.escape(c), t):
                s["dial"] = c
                break
        feats = [f for f in FEATURES if re.search(r"(?<![a-z])" + re.escape(f) + r"(?![a-z])", t)
                 and not (f in ("rose gold", "mother-of-pearl") and s.get("dial") == f)]
        if feats:
            s["features"] = sorted(set(s.get("features", []) + feats))
        if re.search(JUST_SHOW, t):
            s["just_show"] = True
    return s


_COLOURS = []


def colours():
    """Dial colours: the catalogue's own (lime, sky blue, opal white...) plus common words, longest first."""
    if not _COLOURS:
        names = set(COLOURS)
        try:
            import os
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from tools import mock_tools
            names |= {k["dial_colour"] for k in mock_tools._load()["skus"].values() if k.get("dial_colour")}
        except Exception:  # noqa: BLE001 - fall back to the fixed list
            pass
        _COLOURS.extend(sorted(names, key=len, reverse=True))
    return _COLOURS


HARD = ("movement", "display", "water_min", "dial", "strap", "features", "size_explicit")


def count_slots(s):
    keys = ["budget" if ("price_max" in s or "price_min" in s) else None,
            "recipient" if s.get("recipient") else None, "style" if s.get("style") else None,
            "strap" if s.get("strap") else None, "size" if ("size_min" in s or "size_max" in s) else None]
    keys += [k for k in ("movement", "display", "water_min", "dial", "features") if s.get(k)]
    return [k for k in keys if k]


def decide(s, questions_asked):
    """'search' or 'ask'."""
    if any(s.get(k) for k in HARD):
        return "search"
    n = len(count_slots(s))
    if n >= 2 or questions_asked >= 2 or (s.get("just_show") and n >= 1) or (s.get("just_show") and questions_asked):
        return "search"
    return "ask"


def search_args(s):
    a = {}
    for k in ("price_min", "price_max"):
        if s.get(k):
            a[k] = s[k]
    if s.get("gender"):
        a["gender"] = s["gender"]
    if s.get("style"):
        a["style"] = s["style"]
    if s.get("strap"):
        a["strap_material"] = s["strap"]
    if s.get("movement"):
        a["movement"] = s["movement"]
    if s.get("display"):
        a["display"] = s["display"]
    if s.get("size_min"):
        a["case_size_min_mm"] = s["size_min"]
    if s.get("size_max"):
        a["case_size_max_mm"] = s["size_max"]
    if s.get("water_min"):
        a["water_resistance_min_m"] = s["water_min"]
    if s.get("dial"):
        a["dial_colour"] = s["dial"]
    if s.get("features"):
        a["query"] = " ".join(f.replace("-", " ") for f in s["features"] if f != "date")
        if not a["query"]:
            del a["query"]
    return a


RELAX_ORDER = ("case_size_min_mm", "case_size_max_mm", "dial_colour", "query", "strap_material", "style", "display",
               "water_resistance_min_m", "price_min")
LABEL = {"case_size_min_mm": "minimum size", "case_size_max_mm": "maximum size", "dial_colour": "dial colour",
         "query": "the feature words", "strap_material": "strap", "style": "style", "display": "display",
         "water_resistance_min_m": "water resistance", "price_min": "minimum price"}


def relaxations(args):
    """Successively looser versions of a search that found nothing (budget and gender are kept). A wedding watch
    first tries formal instead of ethnic, before any other filter is dropped."""
    a = dict(args)
    out = []
    if a.get("style") == "ethnic":
        a["style"] = "formal"
        out.append((dict(a), "the ethnic style (formal shown instead)"))
    for k in RELAX_ORDER:
        if k in a:
            a = {kk: vv for kk, vv in a.items() if kk != k}
            out.append((dict(a), LABEL[k]))
    return out


# ---- slot questions -----------------------------------------------------------------------------------------------
Q_EN = {
    "start": "Happy to help you find one. Who is it for, and roughly what budget do you have in mind?",
    "budget_occasion": "Lovely. What budget do you have in mind, and is it for daily wear, office or a special occasion?",
    "age_budget": "Sure. How old are they, and what budget do you have in mind?",
    "recipient_occasion": "Got it. Who is it for, and is it for daily wear, office or a special occasion?",
    "recipient_budget": "Nice choice. Who is it for, and what budget do you have in mind?",
    "budget": "What budget do you have in mind?",
    "strap": "Do you prefer a leather strap, a metal bracelet or something sporty like silicone?",
}
Q_HI = {
    "start": "Zaroor! Watch kiske liye hai, aur aapka budget kitna hai?",
    "budget_occasion": "Accha! Budget kitna rakhna hai, aur daily wear, office ya kisi occasion ke liye chahiye?",
    "age_budget": "Theek hai. Unki umar kitni hai, aur budget kitna hai?",
    "recipient_occasion": "Theek hai. Watch kiske liye hai, aur daily wear, office ya kisi occasion ke liye?",
    "recipient_budget": "Badhiya. Watch kiske liye hai, aur budget kitna hai?",
    "budget": "Aapka budget kitna hai?",
    "strap": "Strap kaisa pasand hai: leather, metal bracelet ya silicone?",
}
WHAT = {"start": "who the watch is for and their budget", "budget_occasion": "their budget and the occasion",
        "age_budget": "the age of the person it is for and their budget",
        "recipient_occasion": "who it is for and the occasion", "recipient_budget": "who it is for and their budget",
        "budget": "their budget", "strap": "their strap preference (leather, metal or silicone)"}


def question_key(s, questions_asked):
    has_budget = "price_max" in s or "price_min" in s
    rec = s.get("recipient")
    if questions_asked >= 1 and has_budget and rec and not s.get("strap"):
        return "strap"
    if rec == "child" and s.get("age") is None:
        return "age_budget"
    if not rec and not has_budget:
        return "recipient_occasion" if False else "start"
    if rec and not has_budget:
        return "budget_occasion" if not s.get("style") else "budget"
    if has_budget and not rec:
        return "recipient_occasion" if not s.get("style") else "recipient_budget"
    return "strap"


def question(s, questions_asked, hinglish=False):
    k = question_key(s, questions_asked)
    return k, (Q_HI if hinglish else Q_EN)[k]


def model_note(s, questions_asked):
    k = question_key(s, questions_asked)
    return (f"(Kiosk note: before recommending, ask the customer one short, friendly question about {WHAT[k]}. "
            "Do not recommend a watch yet. Reply in the customer's language.)")
