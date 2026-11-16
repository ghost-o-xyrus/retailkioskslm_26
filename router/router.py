"""
Objective 3, Step 4: the intent router. Decides, before any model call, which path a customer message takes.

    from router.router import Router
    r = Router(encoder=kb.dense)                # reuse the retriever's bge-small; encoder=None = rules only
    r.route(messages)  -> {"route": "store", "source": "rule", "scores": {...}, "margin": 2.0, "ms": 0.4}

Routes: lookup, stock, compare, shopping, staff, chat, store, and "unclear" when neither stage is confident.
See eval/route_labels.py for what each route means.

Stage 1, rules: weighted cue words and patterns in English and Hinglish (product codes, stock words, budgets,
recipients, policy and service words, staff requests, greetings, catalogue design names, brands Veyra does not
sell). The route with the highest score wins if it leads the runner-up by at least RULE_MARGIN.
Stage 2, prototypes: otherwise the message is embedded with bge-small (already loaded for retrieval) and compared
with hand-written example sentences per route (router/prototypes.json, written for this purpose, not taken from
any eval set). Highest mean similarity of the top 3 examples wins if it leads by at least PROTO_MARGIN, else
"unclear". Rules that fired restrict the prototype vote to their candidate routes.
Stage 3, follow-ups: a message with no cue of its own inherits the route of the previous customer message when
that was shopping (a reply to a slot question such as "Office, around 10,000").
"""

import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ROUTES = ("lookup", "stock", "compare", "shopping", "staff", "chat", "store")
RULE_MARGIN = 1.0
PROTO_MARGIN = 0.02

CODE_RE = re.compile(r"\b(\d{4}[A-Za-z]{2}\d{2}|V\d{4})\b")


def _rx(words):
    return re.compile(r"(?<![a-z0-9])(" + "|".join(words) + r")(?![a-z0-9])")


# (route, weight, pattern) on the lower-cased message
CUES = [
    # staff: a person, buying, trying on
    ("staff", 4, _rx([r"(speak|talk) (to|with) (a |the |some )?(person|human|staff|manager|someone|salesperson|"
                      r"sales ?person|real person|employee)", r"(call|get|send) (a |the |some )?(staff|person|"
                      r"manager|salesperson|someone)", r"store manager", r"customer care", r"complaint",
                      r"i('ll| will) take (it|this|that|\d)", r"how (do|can|should) i pay", r"(i want|i'd like) to buy (it|this|that|\d)",
                      r"buy (it|this|that) now", r"bill (it|this)", r"pack (it|this)", r"try (it |this |that )?on",
                      r"try on", r"try [a-z0-9 ]{1,20} on", r"in person", r"complain", r"pehen ?(ke|kar) dekh", r"pehenna hai", r"try kar", r"lena hai",
                      r"le leta", r"le lunga", r"le lungi", r"kharidna", r"manager se", r"staff (ko|se)",
                      r"insaan se"])),
    # chat: greetings and small talk
    ("chat", 3, re.compile(r"^\W*(thanks?|thank you|ok(ay)?|great|cool|perfect|got it)\b[^?]{0,30}$|"
                           r"^\W*(hi+|hello|hey|hii+|namaste|namaskar|good (morning|afternoon|evening)|thanks?( a lot)?|"
                           r"thank you( so much)?|ok(ay)?( thanks?)?|bye|shukriya|dhanyavad|who are you|"
                           r"are you (a )?(real|human|robot|bot|person)( person)?|what can you do)\W*$")),
    # compare
    ("compare", 3, _rx([r"compare", r"vs\.?", r"versus", r"difference between", r"which (one )?is better",
                        r"better (one|option)", r"farak", r"fark", r"mein se kaun"])),
    # stock
    ("stock", 2, _rx([r"in stock", r"stock", r"available", r"availability", r"avail", r"sold out", r"out of stock",
                      r"on display", r"(get|buy|take) (it |this |one )?(here )?today", r"today from here", r"milega",
                      r"milegi", r"mil jayega", r"mil sakta", r"hai kya (yahan|is store)", r"is store mein",
                      r"comes? in (a |an )?(black|white|blue|green|red|grey|gray|silver|gold|rose gold|brown|pink|purple|yellow|"
                      r"orange|navy|other colou?rs?|another colou?r|a different colou?r)", r"do you have (the|a|an) [a-z]+ "
                      r"[a-z]+ (in|with)", r"have it in", r"right now", r"here today", r"(have|got) [a-z0-9]+ here"])),
    # lookup-flavoured words (alternatives, details) - only count with a product code (see below)
    ("lookup", 2, _rx([r"similar", r"like it", r"like this", r"like that", r"cheaper", r"instead", r"alternatives?",
                       r"other options?", r"same style", r"over my budget", r"less money", r"sasta", r"jaisa",
                       r"jaise", r"details?", r"specs?", r"specification", r"tell me (more )?about", r"baare mein",
                       r"price of", r"how much is", r"what is the price", r"kitne ka", r"keemat"])),
    # shopping: wants, budgets, recipients, occasions
    ("shopping", 2, _rx([r"looking for", r"i want (a|an|to buy a|some)", r"i need (a|an)", r"show me", r"suggest",
                         r"recommend", r"options? (for|under)", r"something (for|in|under|with|nice|classy)",
                         r"gift for", r"present for", r"for my (wife|husband|father|dad|mother|mom|mum|son|"
                         r"daughter|brother|sister|friend|boyfriend|girlfriend|boss|grandfather|grandmother|wife's|"
                         r"husband's)", r"chahiye", r"leni hai", r"lena chahta", r"lena chahti", r"dikhao", r"dikhaiye",
                         r"ke liye", r"help me (pick|choose|find|select)", r"(pick|choose|find|select) a watch", r"lene aaya", r"lene aayi", r"watch lena", r"budget", r"under \d", r"below \d", r"within \d", r"around \d", r"upto \d",
                         r"up to \d", r"\d+ ?(k|rs|inr|rupees|thousand|hazaar|hazar)", r"\d[\d,]* tak",
                         r"rs\.? ?\d", r"₹ ?\d", r"to buy a watch", r"buy a watch", r"watch for (him|her|me|my)",
                         r"watch(es)? (for|with|under)", r"do you have (a|an|any|some) [a-z\- ]*watch(es)?", r"cheapest",
                         r"most affordable", r"which watch", r"best watch", r"birthday", r"anniversary",
                         r"(dad|father|wife|husband|mom|mum|mother|son|daughter|brother|sister|friend)'s", r"pasand",
                         r"wali", r"wala", r"unisex", r"digital watch", r"analog watch", r"\d+ ?mm (ya|or) (usse|less|smaller|bigger)", r"i like (big|small|large)"])),
    ("shopping", 1, _rx([r"formal", r"casual", r"sporty?", r"office", r"wedding", r"party", r"daily wear",
                         r"everyday wear", r"for (men|women|kids|boys|girls|ladies|gents)", r"men's", r"women's",
                         r"kids'"])),
    # store: policies, services, store facts, how-it-works questions
    ("store", 3, _rx([r"warranty", r"guarantee", r"return", r"exchange", r"refund", r"repair", r"servic(e|ing)",
                      r"battery (replacement|change)", r"replace (the |my )?(battery|glass|strap)", r"new battery",
                      r"stopped working", r"not working", r"engrav(e|ing)", r"initials", r"naam likh",
                      r"deliver(y|ed)?", r"ship(ping)?", r"home delivery", r"gift ?wrap", r"wrap (it|this)",
                      r"payment", r"pay (with|by|using|in)", r"upi", r"google pay", r"gpay", r"paytm", r"emi",
                      r"credit card", r"debit card", r"cash", r"store hours", r"open(ing)? (time|hours)", r"close",
                      r"closing", r"timings?", r"kab (khulta|band)", r"parking", r"wheelchair", r"accessible",
                      r"address", r"located", r"location", r"nearest store", r"other stores?", r"branch",
                      r"offers?", r"discounts?", r"sale", r"coupon", r"loyalty", r"points", r"membership",
                      r"invoice", r"gst", r"care", r"clean(ing)?", r"waterproof", r"water ?resistan(t|ce)",
                      r"shower", r"swim(ming)?", r"sauna", r"cost price", r"margin", r"how much do you buy",
                      r"resiz(e|ing)", r"remove links?", r"size guide", r"measure my wrist", r"exchange my old",
                      r"old watch", r"do you sell", r"do you have a store", r"who (makes|designs|owns)",
                      r"\d+ ?% off", r"percent off", r"what (is|are|does) (a|an|the)? ?[a-z\- ]+(mean|for)\b",
                      r"what('s| is) (a|an) ", r"how does (a|an|the) ", r"why does", r"meaning of", r"range", r"collection",
                      r"how many designs", r"broke(n)?", r"crack(ed)?", r"box", r"dabba", r"receipt", r"bill that",
                      r"steam", r"fade", r"hold (this|it|a|the) (watch )?for me",
                      r"reserve", r"keep (it|this|a watch) for me", r"did (the store|you) pay", r"buying price",
                      r"match (their|the|that) price", r"price match", r"amazon", r"flipkart", r"scuba", r"diving", r"stopwatch", r"alarm", r"beep",
                      r"likhwa", r"chhot(a|i) karwa", r"battery kitne", r"how long does it run"])),
]

QUESTION_RE = re.compile(r"\?|^\s*(what|how|why|when|where|which|who|can|could|do|does|did|is|are|will|would|"
                         r"should|am|kya|kitn|kab|kaise|kahan|kaun)\b")

NOT_CARRIED = ("rolex", "omega", "casio", "seiko", "citizen", "fossil", "titan", "fastrack", "sonata", "timex",
               "tissot", "apple watch", "samsung", "garmin", "rado", "longines", "swatch", "armani", "guess",
               "maxima", "amazfit", "fitbit", "cartier", "breitling", "hublot", "patek", "tudor", "g-shock",
               "sunglasses", "wallet", "perfume", "jewellery", "jewelry", "phone", "smartwatch", "smart watch",
               "fitness band", "fitness tracker", "counts steps", "step count", "notifications", "heart rate",
               "heart-rate", "gps", "wall clock", "alarm clock", "table clock")


class Router:
    def __init__(self, encoder=None, prototypes_path=os.path.join(HERE, "prototypes.json"), names=None):
        """encoder: an object with encode_query(text) -> unit vector (the retriever's DenseRetriever), or None."""
        self.encoder = encoder
        with open(prototypes_path, encoding="utf-8") as f:
            self.prototypes = json.load(f)
        self.proto = None
        if encoder is not None:
            import numpy as np
            self.np = np
            self.proto = {r: np.stack([encoder.encode_query(t) for t in ex]) for r, ex in self.prototypes.items()}
        self.collections, self.designs, self.all_collections = names if names is not None else _catalogue_names()

    # ---------------------------------------------------------------
    def rule_scores(self, text):
        t = " " + text.lower().strip() + " "
        s = {r: 0.0 for r in ROUTES}
        hits = []
        for route, w, rx in CUES:
            n = len({m.group(0) for m in rx.finditer(t)})
            if n:
                s[route] += w * min(n, 3)
                hits.append(route)
        codes = CODE_RE.findall(text)
        named = self._named(t, text)
        brand = any(re.search(r"(?<![a-z])" + re.escape(b) + r"(?![a-z])", t) for b in NOT_CARRIED)
        if brand:
            s["store"] += 4                       # not sold: the knowledge path declines
        if len(set(codes)) >= 2:
            s["compare"] += 6                     # two product codes: a comparison
        if codes and re.search(r"(?<![a-z])(buy|purchase|take it|lena|le lunga|pack|bill|pay)(?![a-z])", t) \
                and not re.search(r"(\d+ ?% off|discount|cheaper|sasta|budget|did (the store|you) pay|match)", t):
            s["staff"] += 4
        if codes and len(set(codes)) < 2:
            s["lookup"] += 3                      # a product code is a lookup unless something stronger says otherwise
            s["shopping"] = max(0.0, s["shopping"] - 2)
            if s["stock"]:
                s["stock"] += 2
        elif named:
            s["store"] += 2                       # facts about a named design come from its card
            s["lookup"] = 0.0                     # "tell me about the X" without a code is a store question
            if s["stock"]:
                s["stock"] += 2
            s["shopping"] = max(0.0, s["shopping"] - 2)
        else:
            s["lookup"] = 0.0
            s["stock"] = 0.0                      # stock needs a watch to check: "do you have formal watches" is shopping
        if not any(s.values()) and QUESTION_RE.search(t):
            s["store"] = 1.0                      # an unmatched question goes to the knowledge path
        if s["staff"] and (s["store"] >= 3 and re.search(r"(\d+ ?% off|discount)", t)):
            s["staff"] = 0.0                      # "give me 30% off and I'll buy it" is a discount question
        return s, {"codes": codes, "named": named, "not_carried": brand}

    def _named(self, t, original=""):
        if any(d in t for d in self.designs):
            return True
        if any(re.search(r"(?<![a-z])" + re.escape(c) + r"(?![a-z])", t) for c in self.collections):
            return True
        # "the Everyday Zenith", "Veyra Utsavi Phantom": a collection word followed by a capitalised name, even
        # when that design does not exist (near-miss questions belong to the knowledge path)
        if re.search(r"\bVeyra [A-Z][a-z]+", original):
            return True
        if self.all_collections and re.search(r"\b(" + "|".join(self.all_collections) + r") [A-Z][a-z]+", original):
            return True
        return bool(self.all_collections and re.search(r"(?<=\w )(" + "|".join(self.all_collections) + r")\b", original))

    def proto_scores(self, text, allowed=None):
        if self.proto is None:
            return None
        v = self.encoder.encode_query(text)
        out = {}
        for r, m in self.proto.items():
            if allowed and r not in allowed:
                continue
            sims = sorted((m @ v).tolist(), reverse=True)[:3]
            out[r] = sum(sims) / len(sims)
        return out

    # ---------------------------------------------------------------
    def route_text(self, text):
        s, info = self.rule_scores(text)
        ranked = sorted(s.items(), key=lambda kv: -kv[1])
        (r1, v1), (_, v2) = ranked[0], ranked[1]
        if v1 > 0 and v1 - v2 >= RULE_MARGIN:
            return {"route": r1, "source": "rule", "scores": s, "margin": v1 - v2, **info}
        allowed = [r for r, v in s.items() if v > 0 and v >= v1 - RULE_MARGIN] if v1 > 0 else None
        p = self.proto_scores(text, allowed if allowed and len(allowed) > 1 else None)
        if p:
            pr = sorted(p.items(), key=lambda kv: -kv[1])
            margin = pr[0][1] - (pr[1][1] if len(pr) > 1 else 0.0)
            if margin >= PROTO_MARGIN:
                return {"route": pr[0][0], "source": "prototype", "scores": s, "proto": p, "margin": margin, **info}
            return {"route": "unclear", "source": "prototype", "scores": s, "proto": p, "margin": margin, **info}
        if v1 > 0:   # rules only (no encoder): best rule guess, marked as a tie
            return {"route": r1 if v1 > v2 else "unclear", "source": "rule-tie", "scores": s, "margin": v1 - v2, **info}
        return {"route": "unclear", "source": "none", "scores": s, "margin": 0.0, **info}

    def route(self, messages):
        """messages: chat messages (dicts with role/content). Routes the latest customer message."""
        t0 = time.perf_counter()
        users = [m["content"] for m in messages if m.get("role") == "user" and isinstance(m.get("content"), str)]
        if not users:
            return {"route": "chat", "source": "none", "ms": 0.0}
        out = self.route_text(users[-1])
        if len(users) > 1 and out["route"] in ("unclear", "store") and out["source"] != "rule":
            prev = self.route_text(users[-2])
            if prev["route"] == "shopping":
                out = dict(out, route="shopping", source="follow-up")
        out["ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return out


def _catalogue_names():
    """Lower-cased design names ('sovereign orion') and distinctive collection names from the catalogue."""
    import sys
    sys.path.insert(0, ROOT)
    from tools import mock_tools
    db = mock_tools._load()
    designs = sorted({s["style_name"].lower() for s in db["styles"].values()}, key=len, reverse=True)
    common = {"basics", "candy", "charm", "circuit", "commute", "daylight", "desk", "everyday", "feather", "glow",
              "heritage", "horizon", "jungle", "loop", "rally", "ribbon", "roots", "skyline", "slim", "sprint",
              "street", "track", "turbo", "weekender", "workday", "arcade", "altitude", "ambassador", "promenade"}
    cols = sorted({s["collection"].lower() for s in db["styles"].values()} - common, key=len, reverse=True)
    all_cols = sorted({re.escape(s["collection"]) for s in db["styles"].values()}, key=len, reverse=True)
    return cols, designs, all_cols
