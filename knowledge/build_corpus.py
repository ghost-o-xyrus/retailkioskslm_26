"""
Build the retrieval corpus (Objective 2, Step 3) from the kiosk data and the store documents.

    python knowledge/build_corpus.py                 # reads data/kiosk and data/docs
    python knowledge/build_corpus.py --data data_v1  # the Objective 1 catalogue

Writes knowledge/corpus.jsonl (one chunk per line) and knowledge/corpus_overview.csv.

Chunk types and IDs (stable across rebuilds, so eval gold labels can point at them):
    product:V1003          one card per design: specs, every variant, descriptions
    collection:meridian    one overview per collection
    faq:<slug>             one per FAQ question
    policy:<doc>#<slug>    one per policy section (warranty, returns, service, care, brand, size guide)
    glossary:<slug>        one per glossary term
    offer:PR-FEST10        one per promotion, with its status on the reference date
    store:ST01             one per store

Rules:
- Products are read through tools/mock_tools.py, so abbreviations and units are normalised exactly as the
  tools normalise them. Content defects stay: contradictions in descriptions are kept, and missing fields
  read "not listed".
- Internal fields never enter the corpus: cost price, staff notes, EAN and HSN. Live stock is not in the
  corpus either; it changes by the hour and belongs to check_inventory.
Only the standard library is used.
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import mock_tools  # noqa: E402

GENDER_TEXT = {"men": "men", "women": "women", "unisex": "anyone (unisex)", "kids": "kids"}
STATUS_TEXT = {"active": "available", "discontinued": "discontinued", "pre_booking": "pre-booking"}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def approx_tokens(text):
    """Rough subword count: about 1.3 tokens per word, plus punctuation. Good enough for sizing chunks."""
    words = re.findall(r"[A-Za-z0-9]+", text)
    punct = re.findall(r"[^\w\s]", text)
    return int(round(len(words) * 1.3 + len(punct) * 0.5))


def inr(x):
    s = str(int(x))
    if len(s) <= 3:
        return "Rs. " + s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return "Rs. " + ",".join(parts + [tail])


def show(v, unit=""):
    return f"{v}{unit}" if v not in (None, "") else "not listed"


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]


# --------------------------------------------------------------------------
# Products and collections
# --------------------------------------------------------------------------

def product_chunks(db, v1_style_ids):
    by_style = {}
    for k in db["skus"].values():
        by_style.setdefault(k["style_id"], []).append(k)
    chunks = []
    for sid, s in db["styles"].items():
        variants = sorted(by_style.get(sid, []), key=lambda k: k["sku"])
        title = f"Veyra {s['style_name']}"
        status = STATUS_TEXT.get(s.get("status"), s.get("status"))
        if s.get("status") == "pre_booking" and s.get("launch_date"):
            status += f", launches on {s['launch_date']}"
        if s.get("movement") == "automatic":
            battery = "no battery (automatic)"
        else:
            battery = f"{show(s.get('warranty_battery_months'))} months on the battery"
        lines = [
            f"{title} (design {sid})",
            f"Sub-brand: {s['sub_brand']}. Collection: {s['collection']}. For: {GENDER_TEXT.get(s['gender'], s['gender'])}. "
            f"Style: {s['style_tag']}. Status: {status}.",
            f"Movement: {show(s.get('movement'))}. Display: {show(s.get('display'))}. Functions: {show(s.get('function'))}.",
            f"Case: {show(s.get('case_material'))}, {show((s.get('case_shape') or '').lower() or None)} shape, {show(s.get('case_diameter_mm'), ' mm')} "
            f"wide, {show(s.get('case_thickness_mm'), ' mm')} thick. Glass: {show(s.get('glass'))}. "
            f"Water resistance: {show(s.get('water_resistance_m'), ' m')}. Luminous hands: {show(s.get('lume'))}.",
            f"Warranty: {show(s.get('warranty_movement_months'))} months on the movement; {battery}. "
            f"Made in: {show(s.get('country_of_origin'))}.",
            "Variants:",
        ]
        for k in variants:
            note = "" if k.get("status") == "active" else f" ({STATUS_TEXT.get(k['status'], k['status'])})"
            strap = (" ".join(x for x in (k.get("strap_colour"), k.get("strap_material")) if x) + " strap"
                     if k.get("strap_material") else "strap not listed")
            if k.get("strap_material") == "metal":
                strap = f"{k.get('strap_colour') or ''} metal bracelet".strip()
            lines.append(f"- {k['sku']}: {show(k.get('dial_colour'))} dial, {show(k.get('case_finish'))} case finish, "
                         f"{strap}. MRP {inr(k['mrp'])}{note}.")
        # Descriptions: the first variant's in full, then any sentence another variant adds.
        seen, desc = set(), []
        for k in variants:
            for sent in sentences(k.get("description")):
                if sent not in seen:
                    seen.add(sent)
                    desc.append(sent)
        if desc:
            lines.append("Description: " + " ".join(desc))
        text = "\n".join(lines)
        prices = [k["mrp"] for k in variants]
        chunks.append(dict(
            id=f"product:{sid}", type="product", title=title, text=text,
            source="data/kiosk/styles.csv + skus.csv",
            meta=dict(style_id=sid, skus=[k["sku"] for k in variants], sub_brand=s["sub_brand"],
                      collection=s["collection"], gender=s["gender"], style_tag=s["style_tag"],
                      status=s.get("status"), price_min=min(prices) if prices else None,
                      price_max=max(prices) if prices else None, in_v1=sid in v1_style_ids)))
    return chunks


def collection_chunks(db):
    by_coll = {}
    for s in db["styles"].values():
        by_coll.setdefault(s["collection"], []).append(s)
    sku_by_style = {}
    for k in db["skus"].values():
        sku_by_style.setdefault(k["style_id"], []).append(k)
    chunks = []
    for coll, styles in by_coll.items():
        skus = [k for s in styles for k in sku_by_style.get(s["style_id"], [])]
        prices = [k["mrp"] for k in skus]
        def vals(field, unit=""):
            vs = sorted({s.get(field) for s in styles if s.get(field) not in (None, "")}, key=str)
            return ", ".join(f"{v}{unit}" for v in vs) or "not listed"
        sizes = [s["case_diameter_mm"] for s in styles if s.get("case_diameter_mm")]
        dials = sorted({k["dial_colour"] for k in skus if k.get("dial_colour")})
        straps = sorted({k["strap_material"] for k in skus if k.get("strap_material")})
        names = ", ".join(s["style_name"].replace(coll + " ", "", 1) for s in styles)
        first = styles[0]
        text = "\n".join([
            f"The {coll} collection by Veyra Watch Co.",
            f"Sub-brand: {first['sub_brand']}. Style: {first['style_tag']}. For: {vals('gender')}.",
            f"{len(styles)} designs and {len(skus)} variants, priced from {inr(min(prices))} to {inr(max(prices))}.",
            f"Movements: {vals('movement')}. Display: {vals('display')}. Case sizes: {min(sizes)} to {max(sizes)} mm. "
            f"Case materials: {vals('case_material')}. Glass: {vals('glass')}. Water resistance: {vals('water_resistance_m', ' m')}.",
            f"Dial colours: {', '.join(dials)}. Straps: {', '.join(straps)}.",
            f"Designs: {names}.",
        ])
        chunks.append(dict(id=f"collection:{slug(coll)}", type="collection", title=f"{coll} collection", text=text,
                           source="data/kiosk/styles.csv + skus.csv",
                           meta=dict(collection=coll, sub_brand=first["sub_brand"], style_tag=first["style_tag"],
                                     n_designs=len(styles), price_min=min(prices), price_max=max(prices))))
    return chunks


# --------------------------------------------------------------------------
# Documents
# --------------------------------------------------------------------------

def split_sections(md):
    """Return (doc_title, [(section_title, body)]) for a markdown file with '#' and '##' headings."""
    title, sections, cur, buf = None, [], None, []
    for line in md.splitlines():
        if line.startswith("# ") and title is None:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if buf and any(x.strip() for x in buf):
                sections.append((cur, "\n".join(buf).strip()))
            cur, buf = line[3:].strip(), []
            continue
        buf.append(line)
    if buf and any(x.strip() for x in buf):
        sections.append((cur, "\n".join(buf).strip()))
    return title, sections


def faq_chunks(md):
    chunks, section = [], "General"
    title, sections = split_sections(md)
    for sec_title, body in sections:
        section = sec_title or "General"
        for m in re.finditer(r"\*\*(.+?\?)\*\*\s*(.+?)(?=\n\s*\n\*\*|\Z)", body, re.S):
            q, a = m.group(1).strip(), " ".join(m.group(2).split())
            chunks.append(dict(id=f"faq:{slug(q)}", type="faq", title=q, text=f"Store FAQ ({section}). {q} {a}",
                               source="data/docs/faq.md", meta=dict(section=section)))
    return chunks


def glossary_chunks(md):
    chunks = []
    for m in re.finditer(r"^- \*\*(.+?):\*\*\s*(.+)$", md, re.M):
        term, definition = m.group(1).strip(), m.group(2).strip()
        chunks.append(dict(id=f"glossary:{slug(term)}", type="glossary", title=term,
                           text=f"Watch glossary. {term}: {definition}", source="data/docs/glossary.md", meta={}))
    return chunks


def policy_chunks(name, md, skip_sections=()):
    doc = name[:-3]
    title, sections = split_sections(md)
    chunks = []
    for sec_title, body in sections:
        if sec_title in skip_sections:
            continue
        head = f"{title}" + (f": {sec_title}" if sec_title else "")
        cid = f"policy:{doc}" + (f"#{slug(sec_title)}" if sec_title else "")
        chunks.append(dict(id=cid, type="policy", title=head, text=f"{head}\n{body}",
                           source=f"data/docs/{name}", meta=dict(doc=doc, section=sec_title)))
    return chunks


def offer_chunks(db):
    today = db["now"].date()
    chunks = []
    for p in db["promos"]:
        start, end = date.fromisoformat(p["start_date"]), date.fromisoformat(p["end_date"])
        status = "running now" if start <= today <= end else ("expired" if end < today else "upcoming")
        text = (f"Offer {p['promo_id']}: {p['name']}. Status: {status} (from {p['start_date']} to {p['end_date']}). "
                f"Applies to {p['applies_to_type'].replace('_', '-')} {p['applies_to']}. "
                f"Can be combined with other offers: {p['stackable']}. {p['conditions']}")
        chunks.append(dict(id=f"offer:{p['promo_id']}", type="offer", title=p["name"], text=text,
                           source="data/kiosk/prices_promos.csv",
                           meta=dict(status=status, applies_to=p["applies_to"])))
    return chunks


def store_chunks(db):
    chunks = []
    for sid, s in db["stores"].items():
        hours = "no walk-in customers" if s["hours"] == "n/a" else f"open {s['hours']}"
        where = ("This is the store the kiosk is in" if sid == db["this_store"]
                 else f"{s['distance_km']:g} km from this store")
        text = f"Store {sid}: {s['name']}. Type: {s['type']}. {where}; {hours}."
        chunks.append(dict(id=f"store:{sid}", type="store", title=s["name"], text=text,
                           source="data/kiosk/stores.csv", meta={}))
    return chunks


# --------------------------------------------------------------------------

def build(data_root):
    mock_tools.reload(os.path.join(data_root, "kiosk"))
    db = mock_tools._load()
    with open(os.path.join(data_root, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    v1_ids = set()
    v1_styles = os.path.join(ROOT, "data_v1", "clean", "styles.csv")
    if os.path.exists(v1_styles):
        with open(v1_styles, encoding="utf-8") as f:
            v1_ids = {r["style_id"] for r in csv.DictReader(f)}
    docs = os.path.join(data_root, "docs")
    def read(name):
        with open(os.path.join(docs, name), encoding="utf-8") as fh:
            return fh.read()
    chunks = product_chunks(db, v1_ids) + collection_chunks(db)
    chunks += faq_chunks(read("faq.md"))
    for name in ("warranty.md", "returns.md", "service.md", "care.md", "size_guide.md"):
        if os.path.exists(os.path.join(docs, name)):
            chunks += policy_chunks(name, read(name))
    # brand.md: the overview and sub-brand list; the collection list is covered by collection chunks
    chunks += policy_chunks("brand.md", read("brand.md"), skip_sections=("Collections",))
    if os.path.exists(os.path.join(docs, "glossary.md")):
        chunks += glossary_chunks(read("glossary.md"))
    chunks += offer_chunks(db) + store_chunks(db)
    for c in chunks:
        c["tokens"] = approx_tokens(c["text"])
    return chunks, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(ROOT, "data"), help="Folder with kiosk/, docs/ and meta.json")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    chunks, meta = build(a.data)
    ids = [c["id"] for c in chunks]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        sys.exit(f"Duplicate chunk IDs: {dupes[:10]}")
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "corpus.jsonl"), "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "corpus_overview.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "type", "title", "tokens"])
        for c in chunks:
            w.writerow([c["id"], c["type"], c["title"], c["tokens"]])
    by_type = {}
    for c in chunks:
        by_type.setdefault(c["type"], []).append(c["tokens"])
    print(f"Catalogue: {meta.get('n_skus')} SKUs ({meta.get('size', 'small')}). Chunks: {len(chunks)}")
    for t, toks in by_type.items():
        toks.sort()
        print(f"  {t:11s} {len(toks):4d}  tokens median {toks[len(toks) // 2]:4d}  min {toks[0]:4d}  max {toks[-1]:4d}")
    print(f"  total tokens about {sum(c['tokens'] for c in chunks):,}")


if __name__ == "__main__":
    main()
