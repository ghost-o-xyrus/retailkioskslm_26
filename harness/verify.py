"""
Objective 3, Step 10: check that a knowledge-path answer's details are in what the model was shown.

A "detail" is something checkable in the reply:
  - a number with a unit or a price (mm, m, months, years, days, hours, minutes, %, Rs, km, ...), or any number of
    11 or more (prices, sizes, years); small counts such as "3 options" or list numbers are not details
  - a product code (1027SM02) or design id (V1027)
  - a spec word: glass, movement, material, function, shape, country of origin or dial colour (lists below)
A detail is supported if it appears in the evidence or in the customer's own message. Unit conversions the model
commonly makes are accepted: months <-> years (x12) and 12-hour clock times (10 pm = 22:00).

Modes:
  shown   evidence = every card shown this turn + every tool result this turn
  cited   the model ends its answer with the numbers of the cards it used, e.g. [1, 3]; evidence = those cards
          + tool results. A reply with details but no citation fails.
A failed check replaces the reply with the fixed "I don't have that information" reply. Citations are removed
from what the customer sees.

The same functions also give an independent measure for the report (eval/compare_dev.py): details not found in
the GOLD card(s) of the eval case, whatever was shown.
"""

import json
import re

UNITS = {"mm", "cm", "m", "metre", "metres", "meter", "meters", "atm", "bar", "month", "months", "mahine", "mahina",
         "year", "years", "saal", "day", "days", "din", "hour", "hours", "hrs", "ghante", "minute", "minutes", "min",
         "mins", "%", "percent", "km", "g", "grams", "pm", "am", "x", "rs", "inr", "lakh", "k"}
SPEC_WORDS = ["sapphire", "mineral", "acrylic", "hardlex", "automatic", "quartz", "solar", "mechanical", "kinetic",
              "hand-wound", "stainless steel", "titanium", "ceramic", "brass", "aluminium", "aluminum", "resin",
              "leather", "silicone", "rubber", "nylon", "fabric", "mesh", "chronograph", "luminous", "alarm",
              "stopwatch", "backlight", "open heart", "moon phase", "gmt", "tachymeter", "round", "square",
              "rectangular", "tonneau", "cushion", "oval", "switzerland", "swiss", "japan", "japanese", "india",
              "china", "germany"]
COLOURS = ["black", "white", "blue", "green", "red", "grey", "gray", "silver", "gold", "brown", "pink", "purple",
           "yellow", "orange", "navy", "olive", "tan", "cream", "beige", "lilac", "lavender", "maroon", "teal",
           "champagne", "bronze", "copper", "salmon", "rose gold", "mother-of-pearl"]
CODE_RE = re.compile(r"\b(\d{4}[a-z]{2}\d{2}|v\d{4})\b")
NUM_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*([a-z%]+)?")
CITE_RE = re.compile(r"\s*[\[\(](?:sources?:?\s*|cards?:?\s*)?(\d+(?:\s*[,;&]\s*\d+|\s*and\s*\d+)*)[\]\)]\s*")
WORD_RE = {w: re.compile(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])") for w in SPEC_WORDS + COLOURS}


def _norm(text):
    t = (text or "").lower().replace("₹", " rs ")
    t = re.sub(r"(?<=\d),(?=\d{2,3}\b)", "", t)          # 38,895 -> 38895 (Indian and Western grouping)
    t = re.sub(r"(?<=\d),(?=\d{2,3}\b)", "", t)
    return re.sub(r"\brs\.", "rs", t)


def _numbers(t):
    return {m.group(1).rstrip("0").rstrip(".") if "." in m.group(1) else m.group(1).lstrip("0") or "0"
            for m in NUM_RE.finditer(CODE_RE.sub(" ", t))}


def details(text):
    """The checkable details in a text: (numbers, codes, spec words)."""
    t = _norm(text)
    codes = set(CODE_RE.findall(t))
    body = CODE_RE.sub(" ", t)
    nums = set()
    for m in NUM_RE.finditer(body):
        raw, unit = m.group(1), (m.group(2) or "")
        before = body[max(0, m.start() - 4):m.start()]
        try:
            val = float(raw)
        except ValueError:
            continue
        if re.match(r"^\s*\d+\.\s", body[m.start():m.start() + 6]) and val <= 20 and not unit:
            continue                                     # a numbered list item
        if unit in UNITS or "rs" in before or val >= 11:
            nums.add((raw.rstrip("0").rstrip(".") if "." in raw else raw.lstrip("0") or "0", unit))
    words = {w for w, rx in WORD_RE.items() if rx.search(t)}
    return nums, codes, words


def _supported_number(n, unit, ev_nums):
    if n in ev_nums:
        return True
    try:
        v = float(n)
    except ValueError:
        return False
    cands = []
    if unit in ("year", "years", "saal"):
        cands.append(v * 12)
    if unit in ("month", "months", "mahine", "mahina"):
        cands.append(v / 12)
    if unit in ("pm",) or v <= 12:
        cands.append(v + 12)
    if unit in ("lakh",):
        cands.append(v * 100000)
    if unit == "k":
        cands.append(v * 1000)
    return any((str(int(c)) if c == int(c) else str(c)) in ev_nums for c in cands)


def unsupported(reply, question, evidence):
    """Details in the reply found neither in the evidence nor in the customer's message."""
    ev = _norm(evidence) + "\n" + _norm(question)
    ev_nums = _numbers(ev)
    ev_codes = set(CODE_RE.findall(ev))
    nums, codes, words = details(strip_citations(reply)[0])
    out = [f"{n} {u}".strip() for n, u in sorted(nums) if not _supported_number(n, u, ev_nums)]
    out += [c for c in sorted(codes) if c not in ev_codes and not (c.startswith("v") and any(x.startswith(c[1:]) for x in ev_codes))]
    out += [w for w in sorted(words) if not WORD_RE[w].search(ev)]
    return out


def strip_citations(reply):
    """(reply without citation brackets, [card numbers] or None)."""
    cited, out = [], reply or ""
    for m in list(CITE_RE.finditer(out)):
        cited += [int(x) for x in re.findall(r"\d+", m.group(1))]
    if cited:
        out = CITE_RE.sub(" ", out)
        out = re.sub(r"[ \t]+([.,!?])", r"\1", re.sub(r"[ \t]{2,}", " ", out)).strip()
    return out, (sorted(set(cited)) or None)


def tool_text(calls):
    return "\n".join(json.dumps(c.get("result"), ensure_ascii=False) for c in calls or [] if c.get("result") is not None)


def check(reply, question, shown_texts, tools_text, mode):
    """{"ok", "reply" (citations removed), "cited", "unsupported", "uncited"} for one knowledge-path reply.
    shown_texts: the card texts in the order the model saw them (card [1] first)."""
    clean, cited = strip_citations(reply)
    if mode == "cited":
        use = [shown_texts[i - 1] for i in (cited or []) if 1 <= i <= len(shown_texts)]
    else:
        use = list(shown_texts)
    bad = unsupported(clean, question, "\n".join(use) + "\n" + tools_text)
    nums, codes, words = details(clean)
    uncited = mode == "cited" and not cited and bool(nums or codes or words)
    return {"ok": not bad and not uncited, "reply": clean, "cited": cited, "unsupported": bad, "uncited": uncited}
