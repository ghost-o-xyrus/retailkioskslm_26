"""
Is a customer message Hinglish (Hindi written in Latin letters, often mixed with English)?

Used by the refusal fallback: the re-ranker (ms-marco-MiniLM-L-6-v2) is English-only and scores Hinglish questions
low even when the right chunk is found, so the fallback must not refuse on its score for Hinglish questions.

The rule is a short list of common Hindi function words and verbs. Words that are also ordinary English
("do", "me", "band", "to") are left out on purpose, so English questions are not caught.
A message counts as Hinglish with two or more listed words, or one listed word in a message of four words or fewer.
"""

import re

HINGLISH_WORDS = frozenset("""
kya hai hain ka ki ke ko mein se pe par aur toh bhi wala wali wale kitna kitni kitne kaun kaunsa kaunsi
kab kaise kahan kyun kyon nahi nahin hoga hogi hota hoti ho jayega jayegi chahiye chahte chahta chahti
milta milti milega milegi sakte sakta sakti karte karta karti karo karna karne karoge karenge kar dena lena
liye mere mera meri mujhe aap tum hum yeh ye woh wo baje khulta khulti kal aaj abhi thoda bahut accha acchi
achha ghar dabba keemat batao bataiye dikhao dikhaiye pasand aaya lagega lagta saal pehen pehna pehenne ek
leni lena dijiye chalega rakh rakhna rakhoge namaste shukriya dhanyavaad ghadi shaadi bachche bachcha matlab
badalne badalna bolo boliye haan ji ya usse chhota chhote chhoti bada bade badi
""".split())

_WORD = re.compile(r"[a-z]+")


def is_hinglish(text: str) -> bool:
    toks = _WORD.findall(text.lower())
    hits = sum(t in HINGLISH_WORDS for t in toks)
    return hits >= 2 or (hits >= 1 and len(toks) <= 4)
