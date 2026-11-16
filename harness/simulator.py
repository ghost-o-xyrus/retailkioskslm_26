"""
Objective 3, Step 6: a rule-based customer for multi-turn discovery dialogues (no second model).

Each dialogue has a hidden profile (eval/o3_dialogues.jsonl): who the watch is for, budget, occasion, strap
preference, language. The customer opens with a vague, partial or detailed message. After each kiosk reply it
answers whatever slots the reply asks about (detected with the scorer's slot keywords, eval/checks.py), in English or
Hinglish, and nothing else. If the reply asks about nothing it recognises and recommends nothing, it says "just show
me a few options". It never volunteers slots it was not asked for, so the slots known at the recommendation are the
ones the kiosk asked for or the opening gave.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "eval"))
from checks import SLOT_KEYWORDS, text_has  # noqa: E402

REL_EN = {"wife": "my wife", "husband": "my husband", "father": "my father", "mother": "my mother", "son": "my son",
          "daughter": "my daughter", "friend_m": "a male friend", "friend_f": "a female friend", "self_m": "myself",
          "self_f": "myself"}
REL_HI = {"wife": "Wife", "husband": "Husband", "father": "Papa", "mother": "Mummy", "son": "Bete", "daughter": "Beti",
          "friend_m": "Dost", "friend_f": "Saheli", "self_m": "Apne", "self_f": "Apne"}
OCC_EN = {"office": "office wear", "daily": "daily wear", "wedding": "a wedding", "sport": "the gym and running",
          "party": "parties"}
OCC_HI = {"office": "office", "daily": "roz pehenne", "wedding": "shaadi", "sport": "gym", "party": "party"}
STRAP_EN = {"leather": "A leather strap, please.", "metal": "A metal bracelet, please.",
            "silicone": "Something sporty, a silicone strap.", "none": "No preference on the strap."}
STRAP_HI = {"leather": "Leather strap.", "metal": "Metal chain wali.", "silicone": "Silicone strap.",
            "none": "Strap koi bhi chalega."}


def _money(v):
    return f"{v:,}"


def answer(profile, kiosk_reply, revealed):
    """The customer's next message, and the slots it reveals. revealed: set, updated in place."""
    hi = profile["language"] == "hinglish"
    asked = [s for s in ("recipient", "age", "budget", "occasion", "strap", "size")
             if text_has(kiosk_reply or "", SLOT_KEYWORDS[s])] if "?" in (kiosk_reply or "") else []
    parts = []
    for s in asked:
        if s == "recipient":
            parts.append(f"{REL_HI[profile['recipient']]} ke liye." if hi else
                         ("It's for myself." if profile["recipient"].startswith("self")
                          else f"It's for {REL_EN[profile['recipient']]}."))
            revealed.add("recipient")
            if profile.get("age") and profile["recipient"] in ("son", "daughter"):
                parts.append(f"{profile['age']} saal." if hi else
                             f"{'He' if profile['recipient'] == 'son' else 'She'}'s {profile['age']}.")
                revealed.add("age")
        elif s == "age" and profile.get("age"):
            parts.append(f"{profile['age']} saal." if hi else f"{'He' if profile['recipient'] == 'son' else 'She'}'s "
                                                               f"{profile['age']}.")
            revealed.add("age")
        elif s == "budget":
            parts.append(f"{profile['budget']} tak." if hi else f"Around {_money(profile['budget'])}.")
            revealed.add("budget")
        elif s == "occasion":
            parts.append(f"{OCC_HI[profile['occasion']]} ke liye." if hi else f"Mostly for {OCC_EN[profile['occasion']]}.")
            revealed.add("occasion")
        elif s == "strap":
            parts.append((STRAP_HI if hi else STRAP_EN)[profile["strap"]])
            revealed.add("strap")
        elif s == "size":
            parts.append("Normal size theek hai." if hi else "A normal size is fine.")
    if not parts:
        return ("Bas kuch options dikha do." if hi else "Just show me a few options."), []
    return " ".join(parts), asked
