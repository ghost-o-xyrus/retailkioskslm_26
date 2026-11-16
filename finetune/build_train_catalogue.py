"""
Objective 4, Step 1: the training catalogue. A second fictional catalogue for building LoRA training data, so the
adapters learn how to behave (answer from what is shown, decline, call staff, call tools) and not Veyra's facts.

    python finetune\\build_train_catalogue.py          # -> data_train/ and finetune/knowledge/corpus.jsonl

It runs the same generator as data/ (generate_catalogue.py) with:
  - a new seed (7177);
  - every collection renamed and new style-name words, none shared with the deployed catalogue;
  - design codes from V6000 up (the deployed catalogue uses V1001-V4258), so no product code is shared;
  - other store names and opening hours;
  - service prices scaled by 1.2 and service, delivery and return times moved by a few days, so a policy answer
    learnt in training never matches the deployed store's own policy (the eval sets ask about those).
What stays: the brand architecture (the five sub-brands and their price bands), the document structure, the
warranty rules that the product cards themselves carry, and the noise the kiosk copy has. Run-time prompts and
the harness name the brand, so the brand name stays.

Checks at the end (the script stops if one fails): no collection name, style name or design code in common with
data/; every product chunk's code is V6000+; the corpus builds.
"""

import csv
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import generate_catalogue as G  # noqa: E402

SEED = 7177
STYLE_ID_START = 6000
OUT = os.path.join(ROOT, "data_train")
CORPUS_OUT = os.path.join(HERE, "knowledge")

COLLECTION_NAMES = {
    # the original 20
    "Meridian": "Concord", "Tidewater": "Seaward", "Monsoon Chrono": "Cyclone Chrono", "Lumiere": "Solenne",
    "Classique": "Vantage", "Karigari": "Naksh", "Workday": "Officeline", "Skyline": "Highpoint", "Slim": "Wafer",
    "Solar Line": "Sunray", "Street": "Avenue", "Neon Digital": "Lumen Digital", "Loop": "Bangle",
    "Track": "Stadium", "Basics": "Essentials", "Shagun": "Vivaah", "Daily Digital": "Daybook Digital",
    "Steel Smart": "Ironside", "Little Explorer": "Junior Scout", "Glow": "Firefly",
    # the Objective 2 extension
    "Sovereign": "Imperial", "Regalia": "Majesty", "Fathom": "Abyss", "Corsair": "Buccaneer",
    "Velocita": "Accelero", "Aurelia": "Celestine", "Opaline": "Pearline", "Heritage": "Legacy",
    "Ambassador": "Envoy", "Promenade": "Boulevard", "Kalaa": "Rangreza", "Utsavi": "Tyohaar",
    "Commute": "Transit", "Weekender": "Holiday", "Horizon": "Vista", "Altitude": "Zenara", "Sprint": "Dash",
    "Feather": "Wisp", "Daylight": "Sunbeam", "Kaleido": "Spectrum", "Mixtape": "Playlist", "Candy": "Lollipop",
    "Arcade": "Joystick", "Circuit": "Kilobyte", "Charm": "Trinket", "Ribbon": "Sash", "Turbo": "Nitro",
    "Rally": "Grand Prix", "Everyday": "Routine", "Saathi": "Humsafar", "Roots": "Mitti", "Mangal": "Aashirwad",
    "Shringar": "Solah", "Tick Digital": "Beat Digital", "Desk": "Cubicle", "Space Cadet": "Astro Kid",
    "Jungle": "Safari", "Ocean Pals": "Sea Buddies", "Tiny Tots": "Wee Ones",
}
NAME_WORDS = {
    "formal": ["Brasco", "Cendre", "Damask", "Ermine", "Filigree", "Gravure", "Ingot", "Jessamy", "Lucent",
               "Mandarin", "Nacre", "Ondine", "Pavane", "Quartet"],
    "sport": ["Barracuda", "Cobalt", "Drover", "Flint", "Gannet", "Harrier", "Impulse", "Jetstream", "Kodiak",
              "Lancer", "Marlin", "Nomad", "Osprey", "Piston"],
    "casual": ["Acorn", "Bramble", "Clover", "Driftwood", "Easel", "Fern", "Gable", "Hazel", "Inkwell", "Juniper",
               "Kettle", "Linen", "Maple", "Nutmeg"],
    "ethnic": ["Abhushan", "Bindiya", "Champa", "Darpan", "Ekta", "Ghungroo", "Heena", "Jhumka", "Kajal",
               "Lehariya", "Mehndi", "Nazakat", "Payal", "Rajni"],
    "fashion": ["Blip", "Confetti", "Dazzle", "Emoji", "Fringe", "Gizmo", "Hula", "Jazzy", "Kitsch", "Limelight",
                "Mambo", "Nifty", "Oomph", "Popsicle"],
    "kids": ["Bumble", "Cubby", "Doodlebug", "Fluffy", "Gummy", "Hoppy", "Inky", "Jumbo", "Kiwi", "Lolly",
             "Muffin", "Nibbles", "Otter", "Pip"],
}
EXT_NAME_WORDS = {
    "formal": ["Rosaline", "Serene", "Tessera", "Umber", "Vellum", "Wren", "Argent", "Basque", "Cordova", "Duchess",
               "Esprit", "Ferrule", "Garnet", "Hallmark", "Inlay", "Jubilee"],
    "sport": ["Rover", "Thunder", "Uplift", "Viper", "Wolverine", "Anvil", "Bolt", "Cyclone", "Derby", "Excel",
              "Ferro", "Glider", "Hornet", "Ironclad", "Jaguar", "Mustang"],
    "casual": ["Oakley", "Parchment", "Quince", "Russet", "Sorrel", "Thistle", "Upland", "Vale", "Walnut", "Yarrow",
               "Almond", "Birch", "Cobble", "Dew", "Elm", "Flax"],
    "ethnic": ["Sanjh", "Tulsi", "Ujala", "Vasant", "Zevar", "Aangan", "Barkha", "Chunri", "Diya", "Gajra", "Hansa",
               "Indu", "Jyoti", "Kiran", "Laali", "Moti"],
    "fashion": ["Quirk", "Razzle", "Sizzle", "Twirl", "Unicorn", "Vibe", "Whizz", "Yoyo", "Zany", "Bling", "Chroma",
                "Disco", "Frisbee", "Glam", "Hipster", "Kazoo"],
    "kids": ["Quack", "Ruffles", "Sprinkle", "Tumble", "Wiggles", "Yeti", "Biscuit", "Cricket", "Dumpling",
             "Giggles", "Honey", "Jellybean", "Moppet", "Noodle", "Pudding", "Toffee"],
}
STORES = [
    ("ST01", "Veyra Store, Lakeview Mall (this store)", "brand store", 0.0, "10:30-21:30"),
    ("ST02", "Veyra Store, Church Road", "brand store", 2.7, "11:00-21:00"),
    ("ST03", "Veyra Store, Riverside Mall", "brand store", 7.4, "10:00-22:30"),
    ("ST04", "Clock Tower Multi-brand Outlet", "partner outlet", 11.2, "10:00-20:30"),
    ("ST05", "Veyra Warehouse (3-day transfer)", "warehouse", 22.0, "n/a"),
]
STAFF_NOTES_SWAP = {"Workday": "Officeline"}
PERTURB_DOCS = ("service.md", "faq.md", "returns.md", "care.md")
STORE_TEXT = [("Central Mall store: 10:00 to 22:00", "Lakeview Mall store: 10:30 to 21:30"),
              ("Central Mall", "Lakeview Mall"),
              ("Station Road (3.2 km, 10:30 to 21:30)", "Church Road (2.7 km, 11:00 to 21:00)"),
              ("City Centre Mall (6.8 km, 11:00 to 22:00)", "Riverside Mall (7.4 km, 10:00 to 22:30)"),
              ("the Time Square multi-brand outlet (9.5 km, 10:00 to 21:00)",
               "the Clock Tower multi-brand outlet (11.2 km, 10:00 to 20:30)"),
              ("2-day transfer", "3-day transfer")]
RENAME_DOCS = ("faq.md", "size_guide.md", "care.md", "returns.md", "service.md")


def _scale_rs(m):
    v = int(m.group(2).replace(",", ""))
    new = max(50, int(round(v * 1.2 / 50.0)) * 50)
    s = f"{new:,}"
    return f"{m.group(1)}{s}"


def _shift(m):
    a, unit = int(m.group(1)), m.group(3)
    b = m.group(2)
    step = {"day": 2, "days": 2, "working days": 2, "minutes": 5, "weeks": 1}.get(unit, 0)
    if b:
        return f"{a + step} to {int(b) + step} {unit}"
    return f"{a + step} {unit}"


def perturb(text):
    text = re.sub(r"(Rs\. ?)(\d[\d,]*)", _scale_rs, text)
    text = re.sub(r"\b(\d{1,2})(?: to (\d{1,2}))? (working days|days|day|minutes|weeks)\b", _shift, text)
    return text


def rename(text):
    for old in sorted(COLLECTION_NAMES, key=len, reverse=True):     # "Neon Digital" before "Digital"
        text = re.sub(r"(?<![A-Za-z])" + re.escape(old) + r"(?![A-Za-z])", COLLECTION_NAMES[old], text)
    return text


def patch_generator():
    old_words = {w for d in (G.NAME_WORDS, G.EXT_NAME_WORDS) for ws in d.values() for w in ws}
    new_words = {w for d in (NAME_WORDS, EXT_NAME_WORDS) for ws in d.values() for w in ws}
    old_colls = {c["name"] for c in G.COLLECTIONS} | {e[0] for e in G.EXT_SPEC}
    assert set(COLLECTION_NAMES) == old_colls, "every collection needs a new name"
    clash = (new_words | set(COLLECTION_NAMES.values())) & (old_words | old_colls)
    assert not clash, f"names shared with the deployed catalogue: {sorted(clash)}"
    for c in G.COLLECTIONS:
        c["name"] = COLLECTION_NAMES[c["name"]]
    G.EXT_SPEC[:] = [(COLLECTION_NAMES[n], COLLECTION_NAMES[b], k, o) for n, b, k, o in G.EXT_SPEC]
    G.NAME_WORDS.clear()
    G.NAME_WORDS.update(NAME_WORDS)
    G.EXT_NAME_WORDS.clear()
    G.EXT_NAME_WORDS.update(EXT_NAME_WORDS)
    G.STORES[:] = STORES
    G.STAFF_NOTES[:] = [rename(n) for n in G.STAFF_NOTES]
    G.STYLE_ID_START = STYLE_ID_START
    orig_promos = G.make_promos
    G.make_promos = lambda: [{k: rename(v) if isinstance(v, str) else v for k, v in p.items()} for p in orig_promos()]


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    patch_generator()
    sys.argv = ["generate_catalogue.py", "--seed", str(SEED), "--out", OUT]
    G.main()
    docs = os.path.join(OUT, "docs")
    for name in os.listdir(docs):
        p = os.path.join(docs, name)
        with open(p, encoding="utf-8") as f:
            text = f.read()
        if name in RENAME_DOCS:
            text = rename(text)
        if name in PERTURB_DOCS:
            text = perturb(text)
        for a, b in STORE_TEXT:                       # the docs' own mentions of the stores
            text = text.replace(a, b)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    meta_p = os.path.join(OUT, "meta.json")
    with open(meta_p, encoding="utf-8") as f:
        meta = json.load(f)
    meta.update(purpose="Objective 4 training catalogue (not for evaluation)", generated_by="finetune/build_train_catalogue.py",
                style_id_start=STYLE_ID_START)
    with open(meta_p, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # checks against the deployed catalogue
    dep = read_csv(os.path.join(ROOT, "data", "clean", "styles.csv"))
    new = read_csv(os.path.join(OUT, "clean", "styles.csv"))
    dep_skus = {r["sku"] for r in read_csv(os.path.join(ROOT, "data", "clean", "skus.csv"))}
    new_skus = {r["sku"] for r in read_csv(os.path.join(OUT, "clean", "skus.csv"))}
    problems = []
    if {r["collection"] for r in dep} & {r["collection"] for r in new}:
        problems.append("collection names shared")
    if {r["style_name"] for r in dep} & {r["style_name"] for r in new}:
        problems.append("style names shared")
    if {r["style_id"] for r in dep} & {r["style_id"] for r in new} or dep_skus & new_skus:
        problems.append("design or product codes shared")
    if min(int(r["style_id"][1:]) for r in new) <= STYLE_ID_START:
        problems.append("design codes below the start")
    for name in os.listdir(docs):
        with open(os.path.join(docs, name), encoding="utf-8") as f:
            text = f.read()
        left = [c for c in COLLECTION_NAMES if re.search(r"(?<![A-Za-z])" + re.escape(c) + r"(?![A-Za-z])", text)
                and c not in ("Everyday",)]          # "Everyday care" is a heading, not the collection
        if left:
            problems.append(f"{name} still names {left}")
        stale = [w for w in ("Central Mall", "Station Road", "City Centre", "Time Square") if w in text]
        if stale:
            problems.append(f"{name} still names the stores {stale}")
    if problems:
        sys.exit("Training catalogue checks failed: " + "; ".join(problems))

    subprocess.run([sys.executable, os.path.join(ROOT, "knowledge", "build_corpus.py"), "--data", OUT,
                    "--out", CORPUS_OUT], check=True, stdout=subprocess.DEVNULL)
    with open(os.path.join(CORPUS_OUT, "corpus.jsonl"), encoding="utf-8") as f:
        chunks = [json.loads(line) for line in f]
    prods = [c for c in chunks if c["type"] == "product"]
    assert all(int(c["id"].split(":V")[1]) > STYLE_ID_START for c in prods)
    print(f"{OUT}: {meta['n_collections']} collections, {meta['n_styles']} designs, {meta['n_skus']} products; "
          f"corpus {len(chunks)} chunks ({len(prods)} product cards) -> {CORPUS_OUT}")


if __name__ == "__main__":
    main()
