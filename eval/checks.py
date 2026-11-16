"""
Matching rules for the eval set. The harness (Step 5) and scorer (Step 6)
should use these functions so every case is judged the same way.

Text matching
-------------
- Case-insensitive; runs of whitespace count as one space.
- An alternative matches only as a whole token: "50 m" matches "50 m" or "50m"
  but not "150 m"; "no" does not match inside "not".
- Spaces inside an alternative are optional ("12,795" also matches "12795"
  because commas are optional too).

Argument matchers (expected tool-call arguments)
------------------------------------------------
{"equals_any": [...]}     value equals one of these (strings compared case-insensitively)
{"range": [lo, hi]}       number within lo..hi inclusive
{"contains_any": [...]}   string contains one of these (case-insensitive)
{"set_equals": [...]}     list with exactly these items, any order
{"absent_or": <matcher>}  argument may be omitted; if present it must satisfy <matcher>
"""

import re


def _alt_regex(alt):
    parts = []
    for ch in alt.lower():
        if ch.isspace():
            parts.append(r"\s*")
        elif ch == ",":
            parts.append(r",?")
        elif ch == "." and parts and parts[-1] == "s" and "".join(parts[-2:]) == "rs":
            parts.append(r"\.?")          # "Rs." also matches "Rs" (Step 13 scorer fix)
        else:
            parts.append(re.escape(ch))
    body = "".join(parts)
    return re.compile(r"(?<![0-9a-zऀ-ॿ])" + body + r"(?![0-9a-zऀ-ॿ])")


# Step 13 scorer fix (applied to every run when a comparison is re-scored, base and new alike): spelling and
# phrasing variants the alternative lists missed. "50 meters" now matches "50 metres"; "Rs. 500 and Rs. 900"
# matches "Rs. 500 to Rs. 900"; a decline written as "isn't specified" / "doesn't specify" / "isn't listed"
# counts wherever "not listed" or "don't have" does.
DECLINE_ALIASES = ("isn't listed", "is not listed", "not specified", "isn't specified", "is not specified",
                   "don't specify", "doesn't specify", "does not specify", "do not specify", "do not have",
                   "no information")
_ALIAS_KEYS = ("not listed", "not mentioned", "don't have")


def normalise(text):
    t = re.sub(r"\s+", " ", (text or "").lower())
    t = re.sub(r"(?<![a-z])meters(?![a-z])", "metres", t)
    t = re.sub(r"(?<![a-z])meter(?![a-z])", "metre", t)
    t = re.sub(r"(rs\.? ?[0-9][0-9,]*) and (rs\.? ?[0-9])", r"\1 to \2", t)
    return t


def _expand(alternatives):
    alts = list(alternatives)
    if any(a.lower() in _ALIAS_KEYS for a in alts):
        alts += [a for a in DECLINE_ALIASES if a not in alts]
    return alts


def text_has(text, alternatives):
    """True if any alternative appears in text as a whole token."""
    t = normalise(text)
    return any(_alt_regex(normalise(a)).search(t) for a in _expand(alternatives))


def check_must_include(text, groups):
    """groups: list of alternative-lists. Returns (passed_count, total, missing_groups)."""
    missing = [g for g in groups if not text_has(text, g)]
    return len(groups) - len(missing), len(groups), missing


def check_must_not_include(text, phrases):
    """Returns the forbidden phrases found (empty list = pass)."""
    return [p for p in phrases if text_has(text, [p])]


def arg_matches(value, matcher):
    if "absent_or" in matcher:
        return value is None or arg_matches(value, matcher["absent_or"])
    if value is None:
        return False
    if "equals_any" in matcher:
        opts = matcher["equals_any"]
        if isinstance(value, str):
            return value.strip().lower() in [str(o).lower() for o in opts]
        return value in opts
    if "range" in matcher:
        try:
            v = float(value)
        except (TypeError, ValueError):
            return False
        lo, hi = matcher["range"]
        return lo <= v <= hi
    if "contains_any" in matcher:
        return isinstance(value, str) and any(o.lower() in value.lower() for o in matcher["contains_any"])
    if "set_equals" in matcher:
        return isinstance(value, list) and sorted(str(v).upper() for v in value) == sorted(
            str(v).upper() for v in matcher["set_equals"])
    raise ValueError(f"unknown matcher {matcher}")


def call_matches(call, spec):
    """call: {"name": str, "arguments": dict}; spec: {"name": str, "args": {param: matcher}}."""
    if call.get("name") != spec["name"]:
        return False
    args = call.get("arguments") or {}
    return all(arg_matches(args.get(p), m) for p, m in spec.get("args", {}).items())


def calls_satisfy(calls, options):
    """options: list of options; each option is a list of call specs that must ALL appear (any order).
    Returns the index of the first satisfied option, or None."""
    for i, option in enumerate(options):
        if all(any(call_matches(c, spec) for c in calls) for spec in option):
            return i
    return None


REFUSAL_PHRASES = [
    "sorry", "unfortunately", "i'm afraid", "i am afraid", "can't", "cannot", "can not", "unable",
    "not able", "don't have", "do not have", "don't carry", "do not carry", "don't sell", "do not sell",
    "not available", "couldn't find", "could not find", "no record", "not listed", "not mentioned",
    "not in our", "isn't in", "is not in", "doesn't", "does not", "not possible", "not something",
    "maaf", "nahi", "nahin",
]


# Keywords that count as asking about a discovery slot (clarify cases)
SLOT_KEYWORDS = {
    "budget": ["budget", "price range", "spend", "how much", "price", "rupees", "range", "kitna", "kitne"],
    "recipient": ["for whom", "who is it for", "for yourself", "yourself", "gift", "for him", "for her",
                  "men or women", "man or woman", "gents or ladies", "kiske liye", "for you", "aapke liye",
                  "khud ke liye", "gents", "ladies"],
    "occasion": ["occasion", "office", "daily", "everyday", "formal", "casual", "party", "wedding", "sport",
                 "wear it", "use it", "mauka", "mauke", "pehenne"],
    "strap": ["strap", "bracelet", "leather", "metal"],
    "size": ["size", "dial size", "small", "large", "mm", "wrist"],
    "age": ["age", "how old", "years old", "umar"],
}


def asks_about_slots(text, slots):
    """Clarify check: the reply asks a question (contains '?') and mentions at least one missing slot."""
    if "?" not in (text or ""):
        return False, []
    hit = [s for s in slots if text_has(text, SLOT_KEYWORDS[s])]
    return bool(hit), hit
