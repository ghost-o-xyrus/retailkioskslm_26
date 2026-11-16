"""
Validate the generated catalogue. Run after generate_catalogue.py:
    python validate.py
Exits with code 1 and lists problems if any check fails.
"""

import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(ROOT, "data", "clean")
KIOSK = os.path.join(ROOT, "data", "kiosk")

ENUMS = {
    "gender": {"men", "women", "unisex", "kids"},
    "style_tag": {"formal", "casual", "sport", "fashion", "ethnic", "kids"},
    "movement": {"quartz", "automatic", "solar"},
    "display": {"analog", "digital"},
    "strap_material": {"leather", "metal", "mesh", "silicone", "rubber", "fabric", "resin"},
    "status": {"active", "discontinued", "pre_booking"},
}
PRICE_RANGES = {"Veyra Atelier": (14000, 58000), "Veyra": (3500, 16000), "Veyra Pulse": (1200, 6500),
                "Veyra Nitya": (650, 3200), "Veyra Junior": (500, 1800)}
# Real brand and collection names that must not appear in the mock data
FORBIDDEN = ["titan", "fastrack", "sonata", "xylys", "raga", "octane", "zoop", "nebula", "helios",
             "rolex", "omega", "casio", "fossil", "seiko", "timex", "tissot"]


def read(base, name):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ean_ok(code):
    if not re.fullmatch(r"\d{13}", code):
        return False
    total = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(code[:12]))
    return (10 - total % 10) % 10 == int(code[12])


def main():
    problems = []
    styles = read(CLEAN, "styles.csv")
    skus = read(CLEAN, "skus.csv")
    inv = read(CLEAN, "inventory.csv")
    stores = read(CLEAN, "stores.csv")
    style_by_id = {s["style_id"]: s for s in styles}

    # uniqueness and keys
    if len(style_by_id) != len(styles):
        problems.append("duplicate style_id")
    if len({k["sku"] for k in skus}) != len(skus):
        problems.append("duplicate sku")
    if len({k["ean"] for k in skus}) != len(skus):
        problems.append("duplicate ean")
    for k in skus:
        if k["style_id"] not in style_by_id:
            problems.append(f"{k['sku']}: unknown style {k['style_id']}")
        if not ean_ok(k["ean"]):
            problems.append(f"{k['sku']}: bad EAN checksum")
        if int(k["cost_price"]) >= int(k["mrp"]):
            problems.append(f"{k['sku']}: cost >= MRP")
        lo, hi = PRICE_RANGES[style_by_id[k["style_id"]]["sub_brand"]]
        if not lo <= int(k["mrp"]) <= hi:
            problems.append(f"{k['sku']}: MRP {k['mrp']} outside {lo}-{hi}")
        for f, allowed in ENUMS.items():
            if f in k and k[f] not in allowed:
                problems.append(f"{k['sku']}: {f}={k[f]}")
    for s in styles:
        for f, allowed in ENUMS.items():
            if f in s and s[f] not in allowed:
                problems.append(f"{s['style_id']}: {f}={s[f]}")
        if s["movement"] == "automatic" and int(s["warranty_battery_months"]) != 0:
            problems.append(f"{s['style_id']}: automatic with battery warranty")

    # every SKU stocked row for every store
    store_ids = {s["store_id"] for s in stores}
    pairs = {(r["store_id"], r["sku"]) for r in inv}
    for k in skus:
        for sid in store_ids:
            if (sid, k["sku"]) not in pairs:
                problems.append(f"missing inventory row {sid}/{k['sku']}")
    for r in inv:
        if int(r["qty_display"]) < 0 or int(r["qty_backroom"]) < 0:
            problems.append(f"negative stock {r['store_id']}/{r['sku']}")

    # clean descriptions must agree with their spec rows
    for k in skus:
        s = style_by_id[k["style_id"]]
        d = k["description"].lower()
        if f"{s['case_diameter_mm']} mm" not in d:
            problems.append(f"{k['sku']}: description case size mismatch")
        if f"{s['water_resistance_m']} m" not in d:
            problems.append(f"{k['sku']}: description water resistance mismatch")
        if ("sapphire" in d) != (s["glass"] == "Sapphire"):
            problems.append(f"{k['sku']}: description glass mismatch")
        if k["strap_material"] not in d and not (k["strap_material"] == "metal" and "bracelet" in d):
            problems.append(f"{k['sku']}: description strap mismatch")

    # no real brand names anywhere in the generated data
    for base in (CLEAN, KIOSK, os.path.join(ROOT, "data", "docs")):
        for name in os.listdir(base):
            with open(os.path.join(base, name), encoding="utf-8") as f:
                text = f.read().lower()
            for word in FORBIDDEN:
                if re.search(rf"\b{word}\b", text):
                    problems.append(f"{name}: contains real brand name '{word}'")

    # kiosk copy has the same keys as clean
    if {k["sku"] for k in read(KIOSK, "skus.csv")} != {k["sku"] for k in skus}:
        problems.append("kiosk skus differ from clean skus")

    with open(os.path.join(ROOT, "data", "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    print(f"Styles: {len(styles)}  SKUs: {len(skus)}  Stores: {len(stores)}  "
          f"Inventory rows: {len(inv)}  Defects logged: {meta['n_defects']}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems[:50]:
            print(" -", p)
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
