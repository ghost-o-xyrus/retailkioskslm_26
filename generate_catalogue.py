"""
Generate a synthetic watch-retail catalogue for the SLM kiosk project.

Fictional brand: Veyra Watch Co. (5 sub-brands, 20 collections).
Everything is seeded, so re-running produces identical files.

Outputs (under data/):
  clean/   ground-truth tables (use these to score answers)
  kiosk/   the same tables with realistic noise (what the kiosk reads)
  docs/    policy and FAQ documents for retrieval
  defects.csv          every injected defect, for building eval cases
  meta.json            generation settings and reference date

Usage:
  python generate_catalogue.py            # default seed 42
  python generate_catalogue.py --seed 7   # a different catalogue
Only the Python standard library is used.
"""

import argparse
import csv
import json
import os
import random
from datetime import date, datetime, timedelta

REFERENCE_DATE = date(2026, 10, 17)   # "today" for stock timestamps and promos
STYLE_ID_START = 1000                 # design codes start above this (Objective 4's training catalogue moves it)
THIS_STORE = "ST01"

# --------------------------------------------------------------------------
# Brand design
# --------------------------------------------------------------------------

SUB_BRANDS = {
    "Veyra Atelier": {"segment": "premium", "price": (14000, 58000),
                      "blurb": "premium automatics and sapphire-crystal dress watches"},
    "Veyra":         {"segment": "flagship", "price": (3500, 16000),
                      "blurb": "the core range for office, occasion and sport"},
    "Veyra Pulse":   {"segment": "youth", "price": (1200, 6500),
                      "blurb": "bold, colourful watches for students and young professionals"},
    "Veyra Nitya":   {"segment": "value", "price": (650, 3200),
                      "blurb": "dependable everyday watches at accessible prices"},
    "Veyra Junior":  {"segment": "kids", "price": (500, 1800),
                      "blurb": "durable, easy-to-read watches for children"},
}

# Each collection: rules the generator samples within.
# genders: list of (gender, weight); movement: list of (movement, weight)
# size: {gender: (min_mm, max_mm)}; wr: water-resistance options in metres
COLLECTIONS = [
    # ---- Atelier ----
    dict(sub="Veyra Atelier", name="Meridian", style="formal", n=6,
         genders=[("men", 3), ("women", 2)], movement=[("automatic", 7), ("quartz", 3)],
         display="analog", functions=["3 hands + date", "3 hands", "open heart"],
         size={"men": (38, 41), "women": (32, 34)}, thick=(9, 12),
         case_mat=["Stainless Steel 316L"], finishes=["silver", "gold-tone", "rose gold"],
         straps=[("leather", 5), ("metal", 4)],
         dials=["white", "silver", "blue", "black", "champagne"], wr=[50],
         glass=["Sapphire"], shape=["Round"], lume=False),
    dict(sub="Veyra Atelier", name="Tidewater", style="sport", n=5,
         genders=[("men", 1)], movement=[("automatic", 8), ("quartz", 2)],
         display="analog", functions=["3 hands + date"],
         size={"men": (41, 43)}, thick=(12, 14),
         case_mat=["Stainless Steel 316L"], finishes=["silver", "black"],
         straps=[("metal", 5), ("rubber", 4)],
         dials=["black", "blue", "green"], wr=[200, 300],
         glass=["Sapphire"], shape=["Round"], lume=True),
    dict(sub="Veyra Atelier", name="Monsoon Chrono", style="sport", n=4,
         genders=[("men", 1)], movement=[("quartz", 6), ("automatic", 4)],
         display="analog", functions=["chronograph + date"],
         size={"men": (42, 44)}, thick=(12, 14),
         case_mat=["Stainless Steel 316L", "Titanium"], finishes=["silver", "grey"],
         straps=[("metal", 5), ("leather", 4)],
         dials=["black", "white", "blue", "grey"], wr=[100],
         glass=["Sapphire"], shape=["Round"], lume=True),
    dict(sub="Veyra Atelier", name="Lumiere", style="formal", n=4,
         genders=[("women", 1)], movement=[("quartz", 6), ("automatic", 4)],
         display="analog", functions=["3 hands", "2 hands"],
         size={"women": (28, 32)}, thick=(7, 9),
         case_mat=["Stainless Steel 316L"], finishes=["gold-tone", "rose gold", "silver"],
         straps=[("metal", 6), ("leather", 3)],
         dials=["mother-of-pearl", "white", "pink"], wr=[50],
         glass=["Sapphire"], shape=["Round", "Tonneau"], lume=False),
    # ---- Veyra flagship ----
    dict(sub="Veyra", name="Classique", style="formal", n=7,
         genders=[("men", 4), ("women", 3)], movement=[("quartz", 1)],
         display="analog", functions=["3 hands", "3 hands + date"],
         size={"men": (38, 42), "women": (28, 32)}, thick=(7, 10),
         case_mat=["Brass", "Stainless Steel"], finishes=["silver", "gold-tone", "rose gold"],
         straps=[("leather", 5), ("metal", 4)],
         dials=["white", "black", "blue", "silver", "champagne"], wr=[30, 50],
         glass=["Mineral"], shape=["Round", "Square"], lume=False),
    dict(sub="Veyra", name="Karigari", style="ethnic", n=5,
         genders=[("women", 1)], movement=[("quartz", 1)],
         display="analog", functions=["2 hands", "3 hands"],
         size={"women": (26, 32)}, thick=(6, 9),
         case_mat=["Brass"], finishes=["gold-tone", "rose gold"],
         straps=[("metal", 1)],
         dials=["gold", "ruby red", "emerald green", "white"], wr=[30],
         glass=["Mineral"], shape=["Round", "Oval", "Square"], lume=False),
    dict(sub="Veyra", name="Workday", style="casual", n=7,
         genders=[("men", 4), ("women", 3)], movement=[("quartz", 1)],
         display="analog", functions=["3 hands + date", "day-date"],
         size={"men": (39, 42), "women": (30, 34)}, thick=(8, 11),
         case_mat=["Stainless Steel"], finishes=["silver", "black", "gold-tone"],
         straps=[("metal", 5), ("leather", 4)],
         dials=["black", "blue", "white", "grey", "green"], wr=[50],
         glass=["Mineral"], shape=["Round"], lume=False),
    dict(sub="Veyra", name="Skyline", style="sport", n=6,
         genders=[("men", 1)], movement=[("quartz", 1)],
         display="analog", functions=["chronograph + date", "multifunction"],
         size={"men": (42, 46)}, thick=(11, 13),
         case_mat=["Stainless Steel"], finishes=["silver", "black", "gunmetal"],
         straps=[("metal", 5), ("silicone", 4)],
         dials=["black", "blue", "grey", "green"], wr=[100],
         glass=["Mineral"], shape=["Round"], lume=True),
    dict(sub="Veyra", name="Slim", style="formal", n=4,
         genders=[("men", 2), ("women", 2)], movement=[("quartz", 1)],
         display="analog", functions=["2 hands", "3 hands"],
         size={"men": (38, 40), "women": (30, 32)}, thick=(5, 7),
         case_mat=["Stainless Steel"], finishes=["silver", "gold-tone", "rose gold"],
         straps=[("leather", 5), ("mesh", 4)],
         dials=["white", "black", "blue"], wr=[30],
         glass=["Mineral"], shape=["Round"], lume=False),
    dict(sub="Veyra", name="Solar Line", style="casual", n=3,
         genders=[("unisex", 1)], movement=[("solar", 1)],
         display="analog", functions=["3 hands + date"],
         size={"unisex": (38, 41)}, thick=(9, 11),
         case_mat=["Stainless Steel"], finishes=["silver", "black"],
         straps=[("fabric", 4), ("metal", 4)],
         dials=["black", "olive", "blue"], wr=[100],
         glass=["Mineral"], shape=["Round"], lume=True),
    # ---- Pulse (youth) ----
    dict(sub="Veyra Pulse", name="Street", style="fashion", n=8,
         genders=[("unisex", 3), ("men", 2), ("women", 2)], movement=[("quartz", 1)],
         display="analog", functions=["3 hands", "3 hands + date"],
         size={"unisex": (40, 44), "men": (42, 45), "women": (34, 38)}, thick=(9, 12),
         case_mat=["Alloy", "Plastic"], finishes=["black", "silver", "multicolour"],
         straps=[("silicone", 4), ("fabric", 3), ("leather", 2)],
         dials=["black", "orange", "navy", "white", "lime", "red"], wr=[30, 50],
         glass=["Mineral"], shape=["Round", "Square"], lume=False),
    dict(sub="Veyra Pulse", name="Neon Digital", style="sport", n=6,
         genders=[("unisex", 1)], movement=[("quartz", 1)],
         display="digital", functions=["digital: alarm, stopwatch, backlight", "ana-digi: dual time, alarm"],
         size={"unisex": (42, 46)}, thick=(12, 15),
         case_mat=["Resin"], finishes=["black", "multicolour"],
         straps=[("resin", 1)],
         dials=["black", "blue", "red", "white"], wr=[50, 100],
         glass=["Acrylic"], shape=["Round", "Square"], lume=True),
    dict(sub="Veyra Pulse", name="Loop", style="fashion", n=5,
         genders=[("women", 3), ("unisex", 2)], movement=[("quartz", 1)],
         display="analog", functions=["2 hands", "3 hands"],
         size={"women": (32, 36), "unisex": (36, 38)}, thick=(6, 8),
         case_mat=["Alloy"], finishes=["silver", "rose gold", "gold-tone"],
         straps=[("mesh", 6), ("leather", 3)],
         dials=["white", "pink", "black", "sky blue"], wr=[30],
         glass=["Mineral"], shape=["Round"], lume=False),
    dict(sub="Veyra Pulse", name="Track", style="sport", n=5,
         genders=[("men", 1)], movement=[("quartz", 1)],
         display="analog", functions=["chronograph-look multifunction"],
         size={"men": (43, 46)}, thick=(11, 13),
         case_mat=["Alloy"], finishes=["black", "gunmetal"],
         straps=[("silicone", 5), ("metal", 3)],
         dials=["black", "red", "blue", "yellow"], wr=[50],
         glass=["Mineral"], shape=["Round"], lume=True),
    # ---- Nitya (value) ----
    dict(sub="Veyra Nitya", name="Basics", style="casual", n=7,
         genders=[("men", 4), ("women", 3)], movement=[("quartz", 1)],
         display="analog", functions=["3 hands", "3 hands + date"],
         size={"men": (38, 41), "women": (28, 32)}, thick=(7, 10),
         case_mat=["Brass"], finishes=["silver", "gold-tone"],
         straps=[("leather", 5), ("metal", 4)],
         dials=["white", "black", "blue", "brown"], wr=[30],
         glass=["Mineral"], shape=["Round", "Square"], lume=False),
    dict(sub="Veyra Nitya", name="Shagun", style="ethnic", n=5,
         genders=[("women", 1)], movement=[("quartz", 1)],
         display="analog", functions=["2 hands", "3 hands"],
         size={"women": (24, 30)}, thick=(6, 8),
         case_mat=["Brass"], finishes=["gold-tone"],
         straps=[("metal", 1)],
         dials=["gold", "white", "maroon"], wr=[30],
         glass=["Mineral"], shape=["Round", "Oval"], lume=False),
    dict(sub="Veyra Nitya", name="Daily Digital", style="casual", n=4,
         genders=[("unisex", 1)], movement=[("quartz", 1)],
         display="digital", functions=["digital: alarm, stopwatch, backlight"],
         size={"unisex": (38, 42)}, thick=(10, 13),
         case_mat=["Resin"], finishes=["black", "grey"],
         straps=[("resin", 1)],
         dials=["black", "grey"], wr=[30, 50],
         glass=["Acrylic"], shape=["Square", "Round"], lume=True),
    dict(sub="Veyra Nitya", name="Steel Smart", style="formal", n=4,
         genders=[("men", 1)], movement=[("quartz", 1)],
         display="analog", functions=["3 hands + date", "day-date"],
         size={"men": (39, 42)}, thick=(8, 10),
         case_mat=["Stainless Steel"], finishes=["silver", "two-tone"],
         straps=[("metal", 1)],
         dials=["white", "black", "blue"], wr=[30, 50],
         glass=["Mineral"], shape=["Round"], lume=False),
    # ---- Junior (kids) ----
    dict(sub="Veyra Junior", name="Little Explorer", style="kids", n=4,
         genders=[("kids", 1)], movement=[("quartz", 1)],
         display="analog", functions=["3 hands, learning dial"],
         size={"kids": (30, 34)}, thick=(8, 10),
         case_mat=["Plastic"], finishes=["multicolour"],
         straps=[("silicone", 6), ("fabric", 3)],
         dials=["white", "yellow", "sky blue", "pink"], wr=[30, 50],
         glass=["Acrylic"], shape=["Round"], lume=False),
    dict(sub="Veyra Junior", name="Glow", style="kids", n=4,
         genders=[("kids", 1)], movement=[("quartz", 1)],
         display="digital", functions=["digital: alarm, backlight"],
         size={"kids": (32, 36)}, thick=(10, 12),
         case_mat=["Resin"], finishes=["multicolour"],
         straps=[("resin", 1)],
         dials=["blue", "green", "purple", "red"], wr=[50],
         glass=["Acrylic"], shape=["Round", "Square"], lume=True),
]

# Words for style names, per collection mood (all invented)
NAME_WORDS = {
    "formal": ["Aurel", "Crest", "Prism", "Regent", "Vela", "Orion", "Sable", "Ivory", "Noble", "Atlas", "Halo", "Linnea"],
    "sport": ["Reef", "Vortex", "Apex", "Torrent", "Ridge", "Falcon", "Strike", "Delta", "Pace", "Summit", "Rapid", "Arc"],
    "casual": ["Daybreak", "Harbor", "Field", "Metro", "Pebble", "Cedar", "Plain", "Ember", "Grove", "Signal", "Dune"],
    "ethnic": ["Kalyani", "Meher", "Rangoli", "Zari", "Chandni", "Kesar", "Utsav", "Mohini", "Noor", "Tara"],
    "fashion": ["Riff", "Flick", "Glitch", "Swirl", "Pop", "Remix", "Volt", "Doodle", "Spark", "Drift", "Loop", "Fizz"],
    "kids": ["Comet", "Rocket", "Panda", "Starlet", "Dino", "Bubbles", "Zoom", "Kite"],
}

# --------------------------------------------------------------------------
# Scale-up (Objective 2): sibling collections built on the original 20.
# Each entry: (new collection name, base collection, number of styles, overrides).
# Rules for staying compatible with eval v1.1: no smartwatches, pocket watches, clocks or rings;
# no solid-gold cases; no collection named Galaxy or Nova; existing collections are untouched.
# --------------------------------------------------------------------------

EXT_NAME_WORDS = {
    "formal": ["Sterling", "Laurel", "Monarch", "Velour", "Solace", "Cameo", "Tribute", "Bastion", "Elan",
               "Quill", "Marquee", "Saffron", "Opus", "Tiara", "Fable", "Verity"],
    "sport": ["Breaker", "Kestrel", "Thrust", "Gale", "Shoal", "Dynamo", "Ranger", "Volt", "Sabre", "Blaze",
              "Tempest", "Orca", "Javelin", "Comet", "Quasar", "Talon"],
    "casual": ["Meadow", "Sundial", "Trail", "Lantern", "Willow", "Courier", "Mosaic", "Tide", "Basalt",
               "Pilot", "Hearth", "Canvas", "Orchard", "Quarry", "Ripple"],
    "ethnic": ["Jharokha", "Sitara", "Paisley", "Mehfil", "Kundan", "Roshni", "Basant", "Phulkari", "Gulmohar",
               "Chandan", "Bandhani", "Damini", "Malhar", "Suhana"],
    "fashion": ["Glimmer", "Neon", "Echo", "Pixel", "Bounce", "Prism", "Jive", "Tango", "Zest", "Funk",
                "Retro", "Sorbet", "Mirage", "Groove", "Ziggy", "Hype"],
    "kids": ["Teddy", "Robo", "Sunny", "Bunny", "Owl", "Turtle", "Rainbow", "Puffin", "Lion", "Koala", "Jelly",
             "Pogo", "Sprout", "Whale"],
}

EXT_SPEC = [
    # ---- Atelier ----
    ("Sovereign", "Meridian", 12, dict(dials=["white", "slate grey", "midnight blue", "ivory", "salmon"])),
    ("Regalia", "Meridian", 10, dict(functions=["3 hands + date", "small seconds", "moonphase"],
                                     dials=["silver", "black", "emerald green", "champagne"])),
    ("Fathom", "Tidewater", 11, dict(dials=["black", "petrol blue", "orange", "white"], wr=[200])),
    ("Corsair", "Tidewater", 9, dict(case_mat=["Stainless Steel 316L", "Titanium"], dials=["grey", "black", "bronze"])),
    ("Velocita", "Monsoon Chrono", 10, dict(dials=["white", "black", "racing green", "red"])),
    ("Aurelia", "Lumiere", 11, dict(dials=["mother-of-pearl", "champagne", "lavender", "white"])),
    ("Opaline", "Lumiere", 9, dict(shape=["Round", "Square"], dials=["opal white", "pink", "silver"])),
    # ---- Veyra flagship ----
    ("Heritage", "Classique", 14, dict(dials=["cream", "black", "navy", "silver", "brown"])),
    ("Ambassador", "Classique", 12, dict(functions=["3 hands + date", "day-date"], dials=["white", "blue", "grey"])),
    ("Promenade", "Classique", 11, dict(genders=[("women", 1)], dials=["white", "rose", "silver", "champagne"])),
    ("Kalaa", "Karigari", 12, dict(dials=["gold", "royal blue", "maroon", "ivory"])),
    ("Utsavi", "Karigari", 10, dict(dials=["gold", "peacock green", "pink"])),
    ("Commute", "Workday", 14, dict(dials=["black", "navy", "olive", "white", "steel grey"])),
    ("Weekender", "Workday", 12, dict(straps=[("leather", 4), ("fabric", 3), ("metal", 3)],
                                      dials=["green", "tan", "blue", "cream"])),
    ("Horizon", "Workday", 11, dict(dials=["sky blue", "white", "black"])),
    ("Altitude", "Skyline", 12, dict(dials=["black", "blue", "orange", "grey"])),
    ("Sprint", "Skyline", 11, dict(functions=["chronograph + date"], dials=["white", "black", "red"])),
    ("Feather", "Slim", 10, dict(dials=["white", "silver", "black", "blue"])),
    ("Daylight", "Solar Line", 9, dict(dials=["sand", "black", "green"])),
    # ---- Pulse (youth) ----
    ("Kaleido", "Street", 14, dict(dials=["purple", "teal", "orange", "black", "white"])),
    ("Mixtape", "Street", 12, dict(dials=["black", "red", "lime", "grey"])),
    ("Candy", "Street", 11, dict(genders=[("women", 3), ("unisex", 2)], dials=["pink", "mint", "lilac", "white"])),
    ("Arcade", "Neon Digital", 12, dict(dials=["black", "green", "orange", "blue"])),
    ("Circuit", "Neon Digital", 10, dict(dials=["grey", "black", "red"])),
    ("Charm", "Loop", 12, dict(dials=["white", "rose", "black", "mint"])),
    ("Ribbon", "Loop", 10, dict(straps=[("leather", 5), ("mesh", 4)], dials=["pink", "white", "blue"])),
    ("Turbo", "Track", 12, dict(dials=["black", "blue", "orange", "green"])),
    ("Rally", "Track", 10, dict(dials=["red", "black", "white"])),
    # ---- Nitya (value) ----
    ("Everyday", "Basics", 14, dict(dials=["white", "black", "blue", "grey", "green"])),
    ("Saathi", "Basics", 12, dict(dials=["white", "cream", "brown", "black"])),
    ("Roots", "Basics", 11, dict(straps=[("leather", 5), ("fabric", 3)], dials=["tan", "olive", "black"])),
    ("Mangal", "Shagun", 12, dict(dials=["gold", "white", "red", "green"])),
    ("Shringar", "Shagun", 10, dict(dials=["gold", "maroon", "pink"])),
    ("Tick Digital", "Daily Digital", 11, dict(dials=["black", "blue", "grey"])),
    ("Desk", "Steel Smart", 11, dict(dials=["white", "blue", "silver", "black"])),
    # ---- Junior (kids) ----
    ("Space Cadet", "Little Explorer", 10, dict(dials=["navy", "white", "orange"])),
    ("Jungle", "Little Explorer", 9, dict(dials=["green", "yellow", "white"])),
    ("Ocean Pals", "Glow", 10, dict(dials=["blue", "aqua", "orange"])),
    ("Tiny Tots", "Glow", 9, dict(dials=["pink", "yellow", "green"])),
]


EXT_SIZE_FACTOR = 1.27   # tuned so the large catalogue lands near 1,500 SKUs


def extension_collections(rng):
    base = {c["name"]: c for c in COLLECTIONS}
    out = []
    for name, base_name, n, over in EXT_SPEC:
        c = dict(base[base_name])
        c.update(over)
        c["name"], c["n"] = name, round(n * EXT_SIZE_FACTOR)
        out.append(c)
    return out


STAFF_NOTES = [
    "Popular as a gift; suggest the presentation box.",
    "Runs slightly large on thin wrists; offer the smaller variant.",
    "Leather strap needs a few days to soften.",
    "Strong seller during wedding season.",
    "Customers often ask whether it is waterproof for swimming; it is not.",
    "Bracelet can be resized in store in about 10 minutes.",
    "Lume is bright but fades after about 2 hours.",
    "Frequently compared with the Workday range.",
    "Stock moves fast after salary day.",
    "Second-most returned item in the collection due to size.",
]

STORES = [
    # store_id, name, type, distance_km from this store, hours
    ("ST01", "Veyra Store, Central Mall (this store)", "brand store", 0.0, "10:00-22:00"),
    ("ST02", "Veyra Store, Station Road", "brand store", 3.2, "10:30-21:30"),
    ("ST03", "Veyra Store, City Centre Mall", "brand store", 6.8, "11:00-22:00"),
    ("ST04", "Time Square Multi-brand Outlet", "partner outlet", 9.5, "10:00-21:00"),
    ("ST05", "Veyra Warehouse (2-day transfer)", "warehouse", 18.0, "n/a"),
]

CASE_CODE = {"Stainless Steel 316L": "S", "Stainless Steel": "S", "Titanium": "T", "Brass": "B",
             "Alloy": "A", "Plastic": "P", "Resin": "R"}
STRAP_CODE = {"leather": "L", "metal": "M", "mesh": "N", "silicone": "P", "rubber": "K",
              "fabric": "F", "resin": "R"}

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def weighted(rng, pairs):
    items, weights = zip(*pairs)
    return rng.choices(items, weights=weights, k=1)[0]


def indian_price(x):
    """Round to typical Indian retail endings: ...95 or ...99 (or ...499/...999 for small)."""
    x = int(x)
    if x < 1500:
        return int(round(x / 50.0)) * 50 - 1 if x > 100 else x
    return int(round(x / 100.0)) * 100 - 5


def ean13(rng, seen):
    """EAN-13 in the 200-299 restricted-circulation range, so codes never clash with real products."""
    while True:
        body = "2" + "".join(str(rng.randint(0, 9)) for _ in range(11))
        total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(body))
        check = (10 - total % 10) % 10
        code = body + str(check)
        if code not in seen:
            seen.add(code)
            return code


def write_csv(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def fmt_inr(x):
    s = str(int(x))
    if len(s) <= 3:
        return "₹" + s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return "₹" + ",".join(parts) + "," + tail


# --------------------------------------------------------------------------
# Description writer (template-based, so every fact matches the spec row)
# --------------------------------------------------------------------------

OPENERS = {
    "formal": ["A refined dress watch", "An understated formal piece", "A classic dress watch for the boardroom and beyond"],
    "sport": ["A rugged sports watch", "A sports watch built for active days", "A sporty, hard-wearing design"],
    "casual": ["An easy everyday watch", "A versatile daily companion", "A clean, practical design"],
    "ethnic": ["A festive, jewellery-inspired watch", "An elegant piece for occasions", "A dressy watch designed to pair with traditional wear"],
    "fashion": ["A bold, trend-led watch", "A fun statement piece", "A youthful design with attitude"],
    "kids": ["A cheerful first watch", "A tough, easy-to-read watch for kids", "A playful watch for young wrists"],
}


MATERIAL_PHRASE = {"Stainless Steel 316L": "316L stainless steel", "Stainless Steel": "stainless steel",
                   "Titanium": "titanium", "Brass": "brass", "Alloy": "alloy", "Plastic": "plastic", "Resin": "resin"}
FUNC_PHRASE = {
    "3 hands + date": "hour, minute and seconds hands with a date window",
    "3 hands": "hour, minute and seconds hands",
    "2 hands": "a minimal two-hand display",
    "open heart": "an open-heart window that shows the balance wheel at work",
    "chronograph + date": "a stopwatch chronograph with a date window",
    "multifunction": "day, date and 24-hour sub-dials",
    "day-date": "day and date displays",
    "chronograph-look multifunction": "chronograph-style sub-dials for day, date and 24-hour time",
    "digital: alarm, stopwatch, backlight": "an alarm, stopwatch and backlight",
    "ana-digi: dual time, alarm": "analog hands plus a digital screen for dual time and alarm",
    "3 hands, learning dial": "a learning dial that labels the minutes to help children tell the time",
    "digital: alarm, backlight": "an alarm and a colourful backlight",
    "small seconds": "hour and minute hands with a small seconds sub-dial",
    "moonphase": "a moonphase window that tracks the phase of the moon",
}


def strap_phrase(sku):
    m = sku["strap_material"]
    if m == "metal":
        return f"{sku['strap_colour']} metal bracelet"
    return f"{sku['strap_colour']} {m} strap"


def describe(rng, style, sku):
    mood = style["style_tag"]
    who = {"men": "made for men", "women": "made for women", "unisex": "designed for anyone",
           "kids": "made for children"}[style["gender"]]
    s1 = f"{rng.choice(OPENERS[mood])} from the {style['collection']} collection, {who}."
    case = f"a {style['case_diameter_mm']} mm {MATERIAL_PHRASE[style['case_material']]} case"
    if style["display"] == "digital":
        s2 = f"It has {case}, a {sku['dial_colour']} digital display and a {strap_phrase(sku)}."
    else:
        s2 = f"It pairs {case} and a {sku['dial_colour']} dial with a {strap_phrase(sku)}."
    mv = {"automatic": "a self-winding automatic movement", "quartz": "a quartz movement",
          "solar": "a light-powered solar quartz movement"}[style["movement"]]
    s3 = (f"Powered by {mv}, it has {FUNC_PHRASE[style['function']]}, "
          f"and is water resistant to {style['water_resistance_m']} m.")
    extras = []
    if style["glass"] == "Sapphire":
        extras.append("scratch-resistant sapphire crystal")
    if style["lume"] == "yes":
        extras.append("luminous hands" if style["display"] == "analog" else "a luminous display")
    s4 = f"Details include {' and '.join(extras)}." if extras else ""
    return " ".join(x for x in [s1, s2, s3, s4] if x)


# --------------------------------------------------------------------------
# Generation
# --------------------------------------------------------------------------

def _build_collection(rng, coll, words, state, styles, skus):
    """Sample the styles and SKUs of one collection. `state` carries style_counter and the EAN set."""
    sub = SUB_BRANDS[coll["sub"]]
    pmin, pmax = sub["price"]
    for i in range(coll["n"]):
        state["style_counter"] += rng.randint(1, 9)
        sid = f"V{state['style_counter']}"
        gender = weighted(rng, coll["genders"])
        movement = weighted(rng, coll["movement"])
        lo, hi = coll["size"][gender]
        diameter = rng.randint(lo, hi)
        thick = round(rng.uniform(*coll["thick"]), 1)
        case_mat = rng.choice(coll["case_mat"])
        wr = rng.choice(coll["wr"])
        func = rng.choice(coll["functions"])
        if movement == "automatic" and func == "3 hands":
            func = "3 hands + date"
        base_word = words[i]
        style_name = f"{coll['name']} {base_word}"
        # Base price: position within sub-brand range, with premiums
        frac = rng.uniform(0.05, 0.75)
        if movement == "automatic":
            frac += 0.2
        if case_mat == "Titanium":
            frac += 0.1
        if wr >= 200:
            frac += 0.08
        if coll["sub"] == "Veyra Atelier" and movement == "quartz":
            frac -= 0.15
        frac = min(max(frac, 0.0), 1.0)
        base_price = pmin + frac * (pmax - pmin)
        status = "active"
        r = rng.random()
        launch = REFERENCE_DATE - timedelta(days=rng.randint(30, 1400))
        if r < 0.06:
            status = "discontinued"
        elif r < 0.10:
            status = "pre_booking"
            launch = REFERENCE_DATE + timedelta(days=rng.randint(10, 45))
        warranty_mv = 24 if coll["sub"] in ("Veyra Atelier", "Veyra") else 12
        if movement == "automatic":
            warranty_mv = 24
        style = dict(
            style_id=sid, sub_brand=coll["sub"], collection=coll["name"], style_name=style_name,
            gender=gender, style_tag=coll["style"], movement=movement, display=coll["display"],
            function=func, case_shape=rng.choice(coll["shape"]), case_material=case_mat,
            case_diameter_mm=diameter, case_thickness_mm=thick, glass=rng.choice(coll["glass"]),
            water_resistance_m=wr, lume="yes" if coll["lume"] else "no",
            warranty_movement_months=warranty_mv,
            warranty_battery_months=0 if movement == "automatic" else 12,
            hsn="9102", gst_rate_pct=18, country_of_origin="India" if coll["sub"] != "Veyra Atelier" else rng.choice(["India", "Switzerland"]),
            launch_date=launch.isoformat(), status=status,
            staff_notes=rng.choice(STAFF_NOTES) if rng.random() < 0.35 else "",
        )
        if movement == "solar":
            style["warranty_battery_months"] = 24
        styles.append(style)

        # Variants
        n_var = rng.choices([1, 2, 3, 4], weights=[2, 4, 3, 1])[0]
        combos = set()
        for v in range(1, n_var + 1):
            for _ in range(20):
                dial = rng.choice(coll["dials"])
                strap = weighted(rng, coll["straps"])
                finish = rng.choice(coll["finishes"])
                if (dial, strap, finish) not in combos:
                    break
            combos.add((dial, strap, finish))
            strap_colour = {"metal": finish if finish not in ("multicolour",) else "silver",
                            "mesh": finish if finish not in ("multicolour",) else "silver"}.get(
                strap, rng.choice(["black", "brown", "tan", "navy", "grey", "green", "red", "white"]))
            if strap in ("silicone", "resin", "fabric", "rubber") and coll["style"] in ("kids", "fashion"):
                strap_colour = rng.choice(["black", "blue", "red", "orange", "pink", "green", "yellow", "white"])
            mult = 1.0
            if strap in ("metal", "mesh"):
                mult += rng.uniform(0.06, 0.14)
            if finish in ("gold-tone", "rose gold", "two-tone"):
                mult += rng.uniform(0.03, 0.08)
            mrp = indian_price(min(max(base_price * mult, pmin), pmax))
            while mrp < pmin:
                mrp += 100 if mrp >= 1500 else 50
            while mrp > pmax:
                mrp -= 100 if mrp >= 1500 else 50
            sku_code = f"{sid[1:]}{CASE_CODE[case_mat]}{STRAP_CODE[strap]}{v:02d}"
            sku_status = status
            if status == "active" and n_var > 1 and rng.random() < 0.05:
                sku_status = "discontinued"
            sku = dict(
                sku=sku_code, style_id=sid, ean=ean13(rng, state["eans"]), case_finish=finish,
                dial_colour=dial, strap_material=strap, strap_colour=strap_colour,
                mrp=mrp, cost_price=int(mrp * rng.uniform(0.32, 0.45)), status=sku_status,
            )
            band = (f"{strap_colour.title()} Bracelet" if strap == "metal"
                    else f"{strap_colour.title()} {strap.title()} Strap")
            for_whom = {"men": "for Men", "women": "for Women", "unisex": "(Unisex)", "kids": "for Kids"}[gender]
            face = "Display" if coll["display"] == "digital" else "Dial"
            sku["product_name"] = f"Veyra {style_name} {dial.title()} {face} {band} Watch {for_whom}"
            sku["description"] = describe(rng, style, sku)
            skus.append(sku)


def generate(seed):
    """The original 20-collection catalogue (v1: 103 styles, 231 SKUs). Its random stream is unchanged."""
    rng = random.Random(seed)
    styles, skus = [], []
    state = {"style_counter": STYLE_ID_START, "eans": set()}
    for coll in COLLECTIONS:
        words = list(NAME_WORDS[coll["style"]])  # names repeat across collections, never within one
        rng.shuffle(words)
        _build_collection(rng, coll, words, state, styles, skus)
    return rng, styles, skus, state


def generate_extension(seed, state):
    """The scale-up collections (Objective 2). A separate random stream, so v1 rows stay byte-identical."""
    rng = random.Random(f"{seed}-extension")
    styles, skus = [], []
    for coll in extension_collections(rng):
        pool = list(dict.fromkeys(NAME_WORDS[coll["style"]] + EXT_NAME_WORDS[coll["style"]]))
        rng.shuffle(pool)
        _build_collection(rng, coll, pool, state, styles, skus)
    return rng, styles, skus


def make_promos():
    return [
        dict(promo_id="PR-FEST10", name="Festive 10% off", type="percent_off", value=10,
             applies_to_type="sub_brand", applies_to="Veyra", min_mrp=4999, max_discount=1500,
             start_date="2026-10-01", end_date="2026-11-15", stackable="no",
             conditions="Valid on full-price Veyra watches with MRP of Rs. 4,999 or more; maximum discount Rs. 1,500."),
        dict(promo_id="PR-PULSE300", name="Flat Rs. 300 off Pulse", type="flat_off", value=300,
             applies_to_type="sub_brand", applies_to="Veyra Pulse", min_mrp=2499, max_discount=300,
             start_date="2026-10-10", end_date="2026-10-31", stackable="no",
             conditions="Flat Rs. 300 off Veyra Pulse watches with MRP of Rs. 2,499 or more."),
        dict(promo_id="PR-SHAGUN15", name="Shagun wedding season 15%", type="percent_off", value=15,
             applies_to_type="collection", applies_to="Shagun", min_mrp=0, max_discount=600,
             start_date="2026-10-15", end_date="2026-12-31", stackable="no",
             conditions="15% off the Shagun collection, maximum discount Rs. 600."),
        dict(promo_id="PR-EXCH500", name="Old watch exchange", type="flat_off", value=500,
             applies_to_type="sub_brand", applies_to="Veyra Atelier", min_mrp=14000, max_discount=500,
             start_date="2026-09-01", end_date="2027-03-31", stackable="yes",
             conditions="Rs. 500 off any Veyra Atelier watch when you exchange an old working or non-working watch of any brand."),
        dict(promo_id="PR-MONSOON20", name="Monsoon sale 20%", type="percent_off", value=20,
             applies_to_type="sub_brand", applies_to="Veyra Nitya", min_mrp=0, max_discount=500,
             start_date="2026-07-01", end_date="2026-08-31", stackable="no",
             conditions="Expired. 20% off Veyra Nitya, maximum Rs. 500."),
        dict(promo_id="PR-KIDSDAY", name="Children's Day 2 for 1,499", type="bundle", value=1499,
             applies_to_type="sub_brand", applies_to="Veyra Junior", min_mrp=0, max_discount=0,
             start_date="2026-11-10", end_date="2026-11-16", stackable="no",
             conditions="Upcoming. Any two Veyra Junior watches for Rs. 1,499 in total."),
    ]


def make_inventory(rng, styles, skus):
    style_by_id = {s["style_id"]: s for s in styles}
    rows = []
    for k in skus:
        st = style_by_id[k["style_id"]]
        for store_id, _, stype, _, _ in STORES:
            if k["status"] == "pre_booking":
                disp, back = 0, 0
            elif k["status"] == "discontinued":
                disp, back = (rng.choice([0, 0, 0, 1]), 0)
            else:
                if stype == "warehouse":
                    disp, back = 0, rng.choice([0, 2, 5, 8, 12, 20])
                else:
                    in_stock_p = 0.80 if store_id == THIS_STORE else 0.65
                    if st["sub_brand"] == "Veyra Atelier":
                        in_stock_p -= 0.15
                    if rng.random() < in_stock_p:
                        disp = rng.choice([1, 1, 1, 2])
                        back = rng.choice([0, 0, 1, 2, 3, 5])
                    else:
                        disp, back = 0, 0
            hours_ago = rng.randint(0, 30)
            updated = datetime.combine(REFERENCE_DATE, datetime.min.time()) + timedelta(hours=9) - timedelta(hours=hours_ago)
            rows.append(dict(store_id=store_id, sku=k["sku"], qty_display=disp, qty_backroom=back,
                             updated_at=updated.strftime("%Y-%m-%d %H:%M")))
    return rows


# --------------------------------------------------------------------------
# Noise for the kiosk copy
# --------------------------------------------------------------------------

ABBREV = {
    "case_material": {"Stainless Steel 316L": "SS 316L", "Stainless Steel": "SS", "Titanium": "TI"},
    "glass": {"Mineral": "MIN", "Sapphire": "SAPH", "Acrylic": "ACR"},
    "function": {"3 hands + date": "P3H+D", "3 hands": "P3H", "2 hands": "P2H",
                 "chronograph + date": "CHRONO+D", "day-date": "DD", "multifunction": "MF"},
    "strap_material": {"rubber": "FKM", "silicone": "SIL", "leather": "LTHR", "metal": "SS bracelet"},
}
OPTIONAL_STYLE_FIELDS = ["case_thickness_mm", "lume", "case_shape", "glass", "country_of_origin", "launch_date"]
OPTIONAL_SKU_FIELDS = ["strap_colour", "case_finish"]


def add_noise(rng, styles, skus, inventory, contradictions=(2, 1, 1)):
    """contradictions: how many (sapphire claims, bracelet claims, swim claims) to plant."""
    defects = []
    n_styles = [dict(s) for s in styles]
    n_skus = [dict(k) for k in skus]
    n_inv = [dict(r) for r in inventory]

    def log(file, key, field, clean, kiosk, kind):
        defects.append(dict(file=file, key=key, field=field, clean_value=clean, kiosk_value=kiosk, defect_type=kind))

    for s in n_styles:
        # abbreviations
        for field in ("case_material", "glass", "function"):
            if rng.random() < 0.3 and s[field] in ABBREV[field]:
                new = ABBREV[field][s[field]]
                log("styles.csv", s["style_id"], field, s[field], new, "abbreviation")
                s[field] = new
        # unit mixing for water resistance
        if rng.random() < 0.35:
            m = int(s["water_resistance_m"])
            new = rng.choice([f"{m // 10} ATM", f"{m}M", f"{m} m / {m // 10} bar"])
            log("styles.csv", s["style_id"], "water_resistance_m", m, new, "unit_format")
            s["water_resistance_m"] = new
        # missing optional fields
        for field in OPTIONAL_STYLE_FIELDS:
            if rng.random() < 0.05:
                log("styles.csv", s["style_id"], field, s[field], "", "missing")
                s[field] = ""

    for k in n_skus:
        if rng.random() < 0.25 and k["strap_material"] in ABBREV["strap_material"]:
            new = ABBREV["strap_material"][k["strap_material"]]
            log("skus.csv", k["sku"], "strap_material", k["strap_material"], new, "abbreviation")
            k["strap_material"] = new
        if rng.random() < 0.15:
            new = k["dial_colour"].upper()
            log("skus.csv", k["sku"], "dial_colour", k["dial_colour"], new, "inconsistent_case")
            k["dial_colour"] = new
        for field in OPTIONAL_SKU_FIELDS:
            if rng.random() < 0.05:
                log("skus.csv", k["sku"], field, k[field], "", "missing")
                k[field] = ""

    # contradictions: description claims something the spec row does not say
    style_by_id = {s["style_id"]: s for s in styles}
    candidates = [k for k in n_skus if style_by_id[k["style_id"]]["glass"] == "Mineral"]
    for k in rng.sample(candidates, contradictions[0]):
        old = k["description"]
        k["description"] = old + " The sapphire crystal resists everyday scratches."
        log("skus.csv", k["sku"], "description", "glass=Mineral", "description claims sapphire crystal", "contradiction")
    candidates = [k for k in n_skus if k["strap_material"] in ("leather", "LTHR")]
    for _ in range(contradictions[1]):
        if not candidates:
            break
        k = rng.choice(candidates)
        candidates.remove(k) if contradictions[1] > 1 else None
        k["description"] = k["description"] + " A solid-link steel bracelet completes the look."
        log("skus.csv", k["sku"], "description", "strap_material=leather", "description claims steel bracelet", "contradiction")
    candidates = [k for k in n_skus if int(style_by_id[k["style_id"]]["water_resistance_m"]) <= 50]
    for _ in range(contradictions[2]):
        k = rng.choice(candidates)
        candidates.remove(k) if contradictions[2] > 1 else None
        k["description"] = k["description"] + " Suitable for swimming and snorkelling."
        log("skus.csv", k["sku"], "description",
            f"water_resistance_m={style_by_id[k['style_id']]['water_resistance_m']}",
            "description claims swim/snorkel suitable", "contradiction")

    # stale inventory timestamps
    for r in n_inv:
        if r["store_id"] != "ST05" and rng.random() < 0.05:
            old = r["updated_at"]
            days = rng.randint(5, 20)
            new = (datetime.strptime(old, "%Y-%m-%d %H:%M") - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
            log("inventory.csv", f"{r['store_id']}|{r['sku']}", "updated_at", old, new, "stale_stock")
            r["updated_at"] = new

    return n_styles, n_skus, n_inv, defects


# --------------------------------------------------------------------------
# Policy documents (fictional)
# --------------------------------------------------------------------------

DOCS = {
"brand.md": """# About Veyra Watch Co.

Veyra Watch Co. is a fictional Indian watchmaker used for this prototype. It sells through brand stores, partner outlets and its website.

## Sub-brands
{sub_brand_lines}

## Collections
{collection_lines}
""",
"warranty.md": """# Warranty policy

- **Movement warranty:** 24 months for Veyra Atelier and Veyra watches, and for all automatic watches. 12 months for Veyra Pulse, Veyra Nitya and Veyra Junior.
- **Battery warranty:** 12 months on quartz watches; 24 months on solar watches (rechargeable cell). Automatic watches have no battery.
- **Starts from:** the date on the purchase invoice. Keep the invoice and the warranty card; either digital or paper is accepted.
- **Covered:** manufacturing defects in the movement and battery.
- **Not covered:** straps and bracelets, glass breakage, scratches, water damage beyond the rated water resistance, damage from accidents or misuse, repairs by unauthorised service centres, and normal wear of plating.
- **How to claim:** bring the watch and invoice to any Veyra brand store. Most claims are assessed within 7 working days. Repaired or replaced watches carry the remaining original warranty or 3 months, whichever is longer.
- **Gifts:** a gift recipient can claim with the giver's invoice or the order number.
""",
"returns.md": """# Returns and exchanges

- **In-store purchases:** exchange within 7 days with invoice, if the watch is unworn, all protective films are intact and the original box is included. Refunds are given only for manufacturing defects found within 7 days.
- **Online orders:** return within 15 days of delivery for a full refund, under the same condition rules.
- **Sale items:** items bought under a promotion can be exchanged but not refunded.
- **Engraved watches** cannot be returned or exchanged.
- **Discontinued models** can be exchanged for any watch of equal or higher MRP (pay the difference).
""",
"care.md": """# Watch care and water resistance

## What the water-resistance rating means
| Rating | Suitable for | Not suitable for |
|---|---|---|
| 30 m (3 ATM / 3 bar) | Rain, splashes, hand-washing | Showering, swimming |
| 50 m (5 ATM) | Showering, light swimming in a pool | Diving, water sports |
| 100 m (10 ATM) | Swimming, snorkelling | Scuba diving |
| 200 m and above (20 ATM+) | Recreational scuba diving | Saturation diving |

The rating is a laboratory pressure test, not a depth you can safely dive to. Never press the buttons or pull the crown under water. Leather straps should never get wet regardless of the watch's rating.

## Everyday care
- Wipe the case and bracelet with a soft dry cloth; rinse metal and rubber straps in fresh water after sea or pool use.
- Keep watches away from strong magnets (speakers, phone cases with magnetic clasps), which can stop quartz movements or affect automatics.
- Avoid perfume and sanitiser directly on leather straps.
- Automatic watches wind themselves when worn; if unworn for more than about 40 hours they stop and need to be reset.
- Solar watches recharge under any light; leave them face-up near a window if they have been stored in a drawer.
""",
"service.md": """# Service and repairs

| Service | Typical price | Time |
|---|---|---|
| Battery replacement (quartz) | Rs. 250 to Rs. 450 | 30 minutes in store |
| Bracelet resizing | Free for Veyra watches | 10 to 15 minutes |
| Strap replacement (leather) | Rs. 600 to Rs. 1,800 | Same day if in stock |
| Glass replacement (mineral) | Rs. 500 to Rs. 900 | 5 to 7 days |
| Automatic movement service | Rs. 3,500 to Rs. 6,000 | 3 to 4 weeks |
| Water-resistance test and reseal | Rs. 400 | 2 to 3 days |

- Automatic watches should be serviced every 4 to 5 years.
- Battery replacement within the battery warranty period is free.
- Book a service slot at any brand store or ask a staff member at the counter.
""",
"faq.md": """# Store FAQ

**What are the store hours?** Central Mall store: 10:00 to 22:00 every day.

**Which payment methods are accepted?** UPI, credit and debit cards, net banking, and cash. No-cost EMI is available on cards for purchases above Rs. 5,000.

**Do you offer gift wrapping?** Yes, free gift wrapping and a greeting card at the billing counter.

**Can I get a watch engraved?** Yes, on the caseback of steel watches. Rs. 500, ready in 2 days. Engraved watches cannot be returned.

**Can I try a watch on?** Yes. Ask the kiosk to call a staff member, or speak to anyone at the counter.

**Can you hold a watch for me?** Staff can hold an in-stock watch for up to 24 hours.

**Can you transfer a watch from another store?** Yes. Transfers from other city stores take 1 to 2 days; from the warehouse, 2 days.

**Do you deliver?** Home delivery within the city is free for orders above Rs. 2,000 and takes 1 to 3 days.

**Do you buy or exchange old watches?** Through the old-watch exchange offer on Veyra Atelier only.
""",
}


# Extra knowledge text for the large catalogue (Objective 2 retrieval corpus).
# Kept consistent with the v1 documents, and deliberately silent on the questions that eval v1.1 treats as
# unanswerable (shipping abroad, foreign cards, custom dials, cash buy-back, special orders, bulk or
# employee discounts, price matching, same-day delivery, sales figures, suppliers, scripts for engraving).
FAQ_EXTRA = """
## Buying and paying

**Are prices inclusive of GST?** Yes. The MRP on the tag and on the kiosk includes 18% GST. The invoice shows the GST amount separately.

**Which EMI tenures are available?** No-cost EMI for 3 or 6 months on major credit cards for purchases above Rs. 5,000. Longer tenures carry the bank's interest.

**Can I pay partly in cash and partly by card?** Yes, a bill can be split between two payment methods at the counter.

**Do I get a printed or digital invoice?** Both. The digital invoice is sent by SMS and email if you share a number or address at billing.

**I lost my invoice. Can I get a copy?** Yes. Staff can reprint an invoice from the billing system using the phone number used at purchase.

**What does pre-booking mean?** Some new models are listed for pre-booking before launch. You pay a Rs. 500 token amount, adjusted against the final bill, and the watch is held for you on launch day. The token is refundable until the launch date.

**Can I reserve a watch online and pick it up here?** Yes. Reserve-and-collect orders are held for 24 hours at the chosen store.

**Can I be told when an out-of-stock watch arrives?** Yes. Staff can register your number and you get an SMS when the watch reaches this store.

**Do you sell gift cards?** Yes. Veyra gift cards from Rs. 500 to Rs. 25,000, valid for 12 months, usable at any Veyra brand store.

**Can a gift card be used with a festive offer?** Yes, a gift card is a payment method, so it can be used with any current offer.

## Gifts and packaging

**Does every watch come with a box?** Yes. Veyra Atelier watches come in a wooden presentation box; other sub-brands come in a card gift box.

**Can I get a gift receipt without the price?** Yes. Ask for a gift receipt at billing; it lets the recipient exchange the watch without showing the price.

**Can the person I gift it to exchange it?** Yes, with the gift receipt or the invoice, within the normal 7-day exchange window.

## Sizing and fit

**How do I know which case size suits me?** See the size guide. As a rule of thumb, wrists under 15 cm suit cases of 28 to 36 mm, 15 to 17 cm suit 36 to 41 mm, and over 17 cm suit 41 mm and above.

**Can a metal bracelet be shortened?** Yes, free for Veyra watches in about 10 to 15 minutes. Removed links are returned to you in a small pouch.

**Can a bracelet be made longer?** Spare links can be ordered for most Veyra bracelets. They take 5 to 7 days and cost Rs. 150 to Rs. 400 per link.

**Can I swap a leather strap for a metal bracelet?** Only where the case is designed for both. Staff can check whether a bracelet is available for your model.

**What is lug width?** The distance between the two lugs where the strap attaches, in millimetres. A replacement strap must match it.

## Batteries and power

**How long does a battery last?** Usually 2 to 3 years on analog quartz watches and 1 to 2 years on digital watches with frequent backlight or alarm use.

**How do I know the battery is low?** On many analog quartz watches the seconds hand starts jumping in 2- or 4-second steps. Digital displays fade or blink.

**Do you replace batteries in other brands' watches?** Yes, for quartz watches, at Rs. 250 to Rs. 450. The store cannot guarantee water resistance after opening a non-Veyra watch.

**How long does a solar watch run in the dark?** A fully charged Veyra solar watch runs for about 6 months in darkness.

**How long does an automatic run when I take it off?** About 40 hours on a full wind. After that it stops and the time must be set again.

**Do automatic watches need a battery?** No. They are powered by the movement of your wrist.

## Using your watch

**How do I set the date safely?** Avoid changing the date between 9 pm and 3 am on analog watches, when the date wheel is already moving.

**What is a screw-down crown?** A crown that screws into the case to keep water out. Always screw it back in fully after setting the time.

**How do I use a chronograph?** Press the top pusher to start and stop the stopwatch, and the bottom pusher to reset it. Do not press the pushers under water.

**How do I set the alarm on a digital watch?** Press the mode button until the alarm screen appears, hold the adjust button to edit the hours and minutes, then press mode to save.

**Does the backlight drain the battery?** Heavy backlight use shortens battery life. Use it for a few seconds at a time.

**What does dual time mean?** The watch shows a second time zone, set separately from the main time.

**Why does my watch gain or lose a few seconds?** Quartz watches are accurate to about plus or minus 15 seconds a month; automatics to about plus or minus 20 seconds a day.

## Care and safety

**Can I wear my watch in the gym?** Yes, but rinse metal, rubber and silicone straps after heavy sweating and keep leather straps dry.

**Can I wear my watch in a sauna or hot shower?** No. Heat and steam can damage the seals of any water-resistant watch.

**How should I store a watch I don't wear often?** In its box, away from direct sunlight, magnets and damp. Solar watches should be stored face-up in light.

**Why has my leather strap changed colour?** Leather darkens with skin oils, sweat and sunlight. This is normal wear and is not covered by the warranty.

**Is the plating on gold-tone watches permanent?** Gold-tone and rose gold finishes are plated and can wear at edges over years of use. Plating wear is not covered by the warranty.

## Warranty and service

**Do I need to register my watch for the warranty?** No. The warranty starts from the invoice date automatically.

**I lost the warranty card. Is my warranty still valid?** Yes, the invoice alone is enough.

**Can I claim warranty at another Veyra store?** Yes, at any Veyra brand store in India, with the invoice.

**Does a battery replacement affect the warranty?** Not if it is done at a Veyra store. Battery changes elsewhere void the water-resistance cover.

**How long does a repair take?** Most warranty claims are assessed within 7 working days. Service times are listed in the service price table.

**Can I track my repair?** Yes. You get a job card number and an SMS when the watch is ready to collect.

## Store visit

**Is there parking at Central Mall?** Yes, the mall has paid parking for cars and two-wheelers.

**Is the store wheelchair accessible?** Yes. The store is on the ground floor with step-free entry.

**Can I use the kiosk to find a watch and then see it?** Yes. The kiosk can search the catalogue, check stock and call a staff member to bring the watch to you.

**Which other Veyra stores are nearby?** Station Road (3.2 km, 10:30 to 21:30), City Centre Mall (6.8 km, 11:00 to 22:00) and the Time Square multi-brand outlet (9.5 km, 10:00 to 21:00).
"""

SIZE_GUIDE = """# Size guide

## Case size by wrist
| Wrist circumference | Suggested case diameter | Typical collections |
|---|---|---|
| Under 15 cm | 26 to 34 mm | Shagun, Karigari, Lumiere, Little Explorer |
| 15 to 17 cm | 34 to 41 mm | Classique, Workday, Meridian, Loop |
| Over 17 cm | 41 to 46 mm | Skyline, Track, Tidewater, Neon Digital |

## Children
| Age | Suggested watch |
|---|---|
| 4 to 7 years | Analog learning dial, 30 to 34 mm, with a soft silicone or fabric strap (Little Explorer, Jungle, Space Cadet) |
| 7 to 12 years | Digital with alarm and backlight, 32 to 36 mm (Glow, Ocean Pals, Tiny Tots) |

## Case thickness
- Under 8 mm: dress watches that slide under a shirt cuff (Slim, Feather, Lumiere).
- 8 to 12 mm: everyday watches.
- Over 12 mm: sports and dive watches, which feel heavier on the wrist.

## Measuring your wrist
Wrap a strip of paper around the wrist just above the wrist bone, mark where it overlaps and measure the length with a ruler.
"""

GLOSSARY = """# Watch glossary

- **Analog:** shows the time with hands on a dial.
- **Digital:** shows the time as numbers on a display.
- **Ana-digi:** has both hands and a digital display.
- **Quartz:** a battery-powered movement controlled by a quartz crystal; very accurate and low-maintenance.
- **Automatic:** a mechanical movement wound by the motion of the wrist; needs no battery.
- **Solar:** a quartz movement charged by light through the dial.
- **Chronograph:** a watch with a built-in stopwatch, operated by pushers beside the crown.
- **Multifunction:** extra small dials for day, date and 24-hour time.
- **Day-date:** shows both the day of the week and the date.
- **Moonphase:** a small window showing the current phase of the moon.
- **Small seconds:** the seconds are shown on a small separate dial.
- **Open heart:** a cut-out in the dial that shows part of the moving balance wheel.
- **Sapphire crystal:** very scratch-resistant glass used on Veyra Atelier watches.
- **Mineral glass:** hardened glass, more scratch-prone than sapphire; used on most Veyra and Veyra Nitya watches.
- **Acrylic glass:** light plastic glass used on kids' and digital watches; scratches can be polished out.
- **ATM / bar:** units of water resistance. 1 ATM is about 10 metres, so 5 ATM equals 50 m.
- **Lume:** luminous paint on hands and markers that glows in the dark after exposure to light.
- **316L stainless steel:** a corrosion-resistant steel used on Veyra Atelier cases.
- **Titanium:** a light, strong, hypoallergenic metal about 40% lighter than steel.
- **Tonneau:** a barrel-shaped case.
- **Bezel:** the ring around the glass; on dive watches it rotates to time a dive.
- **Crown:** the knob used to set the time and date.
- **Lugs:** the arms of the case that hold the strap.
- **Mesh strap:** a fine woven metal strap with an adjustable clasp.
- **FKM rubber:** a durable rubber used on dive straps.
"""


def write_docs(base, large=False):
    os.makedirs(base, exist_ok=True)
    sub_lines = "\n".join(f"- **{k}** ({v['segment']}): {v['blurb']}. Price range roughly {fmt_inr(v['price'][0])} to {fmt_inr(v['price'][1])}."
                          for k, v in SUB_BRANDS.items())
    colls = list(COLLECTIONS) + (extension_collections(None) if large else [])
    coll_lines = "\n".join(f"- **{c['name']}** ({c['sub']}): {c['style']} watches." for c in colls)
    docs = dict(DOCS)
    if large:
        docs["faq.md"] = DOCS["faq.md"] + FAQ_EXTRA
        docs["size_guide.md"] = SIZE_GUIDE
        docs["glossary.md"] = GLOSSARY
    for old in ("size_guide.md", "glossary.md"):
        if old not in docs and os.path.exists(os.path.join(base, old)):
            os.remove(os.path.join(base, old))
    for name, text in docs.items():
        if name == "brand.md":
            text = text.format(sub_brand_lines=sub_lines, collection_lines=coll_lines)
        with open(os.path.join(base, name), "w", encoding="utf-8") as f:
            f.write(text)


# --------------------------------------------------------------------------

STYLE_FIELDS = ["style_id", "sub_brand", "collection", "style_name", "gender", "style_tag", "movement",
                "display", "function", "case_shape", "case_material", "case_diameter_mm", "case_thickness_mm",
                "glass", "water_resistance_m", "lume", "warranty_movement_months", "warranty_battery_months",
                "hsn", "gst_rate_pct", "country_of_origin", "launch_date", "status", "staff_notes"]
SKU_FIELDS = ["sku", "style_id", "ean", "product_name", "case_finish", "dial_colour", "strap_material",
              "strap_colour", "mrp", "cost_price", "status", "description"]
PROMO_FIELDS = ["promo_id", "name", "type", "value", "applies_to_type", "applies_to", "min_mrp",
                "max_discount", "start_date", "end_date", "stackable", "conditions"]
INV_FIELDS = ["store_id", "sku", "qty_display", "qty_backroom", "updated_at"]
STORE_FIELDS = ["store_id", "name", "type", "distance_km", "hours"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--size", choices=["large", "small"], default="large",
                    help="large: about 1,500 SKUs (Objective 2 onward). small: the original 231 SKUs (Objective 1).")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
    args = ap.parse_args()

    # v1 catalogue: same random stream as before, so its rows are byte-identical
    rng, styles, skus, state = generate(args.seed)
    promos = make_promos()
    inventory = make_inventory(rng, styles, skus)
    stores = [dict(store_id=a, name=b, type=c, distance_km=d, hours=e) for a, b, c, d, e in STORES]
    k_styles, k_skus, k_inv, defects = add_noise(rng, styles, skus, inventory)
    n_v1 = len(skus)

    if args.size == "large":
        e_rng, e_styles, e_skus = generate_extension(args.seed, state)
        e_inv = make_inventory(e_rng, e_styles, e_skus)
        scale = max(1, round(len(e_skus) / n_v1))
        ek_styles, ek_skus, ek_inv, e_defects = add_noise(e_rng, e_styles, e_skus, e_inv,
                                                          contradictions=(2 * scale, scale, scale))
        styles, skus, inventory = styles + e_styles, skus + e_skus, inventory + e_inv
        k_styles, k_skus, k_inv, defects = k_styles + ek_styles, k_skus + ek_skus, k_inv + ek_inv, defects + e_defects

    for sub, st, sk, inv in (("clean", styles, skus, inventory), ("kiosk", k_styles, k_skus, k_inv)):
        base = os.path.join(args.out, sub)
        write_csv(os.path.join(base, "styles.csv"), st, STYLE_FIELDS)
        write_csv(os.path.join(base, "skus.csv"), sk, SKU_FIELDS)
        write_csv(os.path.join(base, "prices_promos.csv"), promos, PROMO_FIELDS)
        write_csv(os.path.join(base, "inventory.csv"), inv, INV_FIELDS)
        write_csv(os.path.join(base, "stores.csv"), stores, STORE_FIELDS)
    write_csv(os.path.join(args.out, "defects.csv"), defects,
              ["file", "key", "field", "clean_value", "kiosk_value", "defect_type"])
    write_docs(os.path.join(args.out, "docs"), large=args.size == "large")
    n_coll = len({s["collection"] for s in styles})
    meta = dict(seed=args.seed, size=args.size, reference_date=REFERENCE_DATE.isoformat(), this_store=THIS_STORE,
                n_collections=n_coll, n_styles=len(styles), n_skus=len(skus), n_v1_skus=n_v1,
                n_defects=len(defects), generated_by="generate_catalogue.py")
    with open(os.path.join(args.out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
