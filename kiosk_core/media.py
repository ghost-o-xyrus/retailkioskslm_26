"""
Objective 5, Step 7: product images.

A media table keyed by SKU, as retail systems keep it: images are held apart from the product record and linked to
it by SKU, with one main image and further views, and files named in the GS1 style from the product's GTIN
(GTIN-14, then a view code: front 1, left side 2, back 7; e.g. 02407816184951_1.svg). The company's photos are not
available yet, so each SKU's images are drawn from its own attributes: case shape, case finish, dial colour, strap
material and colour, water resistance. They are illustrations, labelled as such; they carry no brand name.

    python kiosk_core\\media.py build        # writes data/kiosk/media.csv and data/kiosk/media/*.svg, then validates
    python kiosk_core\\media.py check        # validation only; lookup timing

Files are SVG, so one file serves every size (thumbnail on a card, large in the viewer). The design asked for
derived sizes of raster photos; with vector illustrations they are not needed, and real photos will bring them back.

The engine uses it through show_product_images (run by the harness, never chosen by the model) and the app serves
the files at /media/<file>.
"""
import csv
import html
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

VIEWS = {"front": "1", "side": "2", "back": "7"}
VIEW_NAMES = {"front": "front", "side": "side", "back": "back (caseback)"}
_INDEX = {}

# ---------------------------------------------------------------- colours
FINISH = {"silver": ("#d7dbde", "#9aa2a8"), "gold-tone": ("#e2c27a", "#a8853a"), "black": ("#3a3d41", "#1d1f22"),
          "multicolour": ("#7fb6e0", "#e07f9a"), "rose gold": ("#e6b7a3", "#b07a66"), "gunmetal": ("#6b7176", "#43484c"),
          "grey": ("#a9aeb2", "#72787d"), "two-tone": ("#d7dbde", "#d2b066")}
DIAL = {"black": "#1f2226", "white": "#f7f7f4", "blue": "#2f5fa8", "green": "#2f7a4d", "grey": "#8a9096",
        "red": "#b8312f", "pink": "#e79ab8", "orange": "#e7792f", "silver": "#c9ced2", "gold": "#cfa94e",
        "navy": "#1f3557", "champagne": "#e8d7b0", "olive": "#6b7038", "cream": "#f1e8d2", "yellow": "#efcb3a",
        "brown": "#6e4a2f", "maroon": "#6d1f2c", "ivory": "#f4efe1", "tan": "#c79f73", "mint": "#a9dcc4",
        "mother-of-pearl": "#ece8f0", "rose": "#e2a7a0", "salmon": "#ef9c84", "sky blue": "#8cc4ec",
        "peacock green": "#1d7f7a", "teal": "#2a8a8e", "emerald green": "#1f8a5a", "lime": "#b3d63c",
        "lilac": "#c3a8dc", "aqua": "#62d0d0", "bronze": "#9c6a3a", "lavender": "#b9a8e0", "opal white": "#f2f3f6",
        "purple": "#6f3fa0", "slate grey": "#5d6670", "racing green": "#1f4d34", "royal blue": "#2747a8",
        "sand": "#d9c39c", "midnight blue": "#1a2747", "steel grey": "#78828c", "petrol blue": "#235566",
        "ruby red": "#a5182f"}
STRAP = {"gold-tone": "#d4b062", "black": "#24262a", "silver": "#c3c9cd", "rose gold": "#dba792", "red": "#b8312f",
         "white": "#f1f1ee", "green": "#2f7a4d", "grey": "#8a9096", "tan": "#b98a59", "navy": "#21385c",
         "brown": "#6a452b", "yellow": "#e9c43a", "gunmetal": "#5c6267", "blue": "#2f5fa8", "two-tone": "#cfd4d8",
         "orange": "#e2742d", "pink": "#e59ab6"}


def _lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- GTIN
def gtin_ok(code):
    s = re.sub(r"\D", "", str(code or ""))
    if len(s) not in (8, 12, 13, 14):
        return False
    digits = [int(c) for c in s]
    body, check = digits[:-1], digits[-1]
    tot = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(body)))
    return (10 - tot % 10) % 10 == check


def gtin14(code):
    return re.sub(r"\D", "", str(code)).zfill(14)


# ---------------------------------------------------------------- drawing
def _strap(x, w, y0, y1, mat, col):
    dark = "#000000" if _lum(col) > 0.5 else "#ffffff"
    out = [f'<rect x="{x}" y="{y0}" width="{w}" height="{y1 - y0}" rx="{6 if mat in ("silicone", "rubber", "resin") else 3}" fill="{col}"/>']
    if mat in ("metal", "mesh"):
        step = 6 if mat == "mesh" else 14
        yy = y0 + step
        while yy < y1:
            out.append(f'<line x1="{x}" y1="{yy}" x2="{x + w}" y2="{yy}" stroke="{dark}" stroke-opacity=".18" stroke-width="{1 if mat == "mesh" else 2}"/>')
            yy += step
    elif mat == "leather":
        out.append(f'<rect x="{x + 4}" y="{y0}" width="{w - 8}" height="{y1 - y0}" fill="none" stroke="{dark}" stroke-opacity=".25" stroke-dasharray="3 4"/>')
    elif mat == "fabric":
        for i in range(3):
            xx = x + w * (i + 1) / 4
            out.append(f'<line x1="{xx:.1f}" y1="{y0}" x2="{xx:.1f}" y2="{y1}" stroke="{dark}" stroke-opacity=".22" stroke-width="3"/>')
    return "".join(out)


def _case_path(shape, cx, cy, r):
    if shape == "Square":
        return f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" rx="{r * .22:.1f}"'
    if shape == "Oval":
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{r * .82:.1f}" ry="{r * 1.05:.1f}"'
    if shape == "Tonneau":
        return (f'<path d="M{cx - r * .8:.1f},{cy - r} Q{cx},{cy - r * 1.12:.1f} {cx + r * .8:.1f},{cy - r} '
                f'Q{cx + r * 1.05:.1f},{cy} {cx + r * .8:.1f},{cy + r} Q{cx},{cy + r * 1.12:.1f} {cx - r * .8:.1f},{cy + r} '
                f'Q{cx - r * 1.05:.1f},{cy} {cx - r * .8:.1f},{cy - r} Z"')
    return f'<circle cx="{cx}" cy="{cy}" r="{r}"'


def draw(sku, style, view):
    """One SVG illustration of a SKU from one view, from its own attributes."""
    shape = style.get("case_shape") or "Round"
    fin_hi, fin_lo = FINISH.get(sku.get("case_finish"), FINISH["silver"])
    dial = DIAL.get(sku.get("dial_colour"), "#c9ced2")
    strap = STRAP.get(sku.get("strap_colour"), "#555a5f")
    mat = sku.get("strap_material") or "leather"
    digital = (style.get("display") or "") == "digital"
    ink = "#111417" if _lum(dial) > 0.55 else "#f4f5f6"
    wr = style.get("water_resistance_m") or ""
    W, H, cx, cy, r = 240, 300, 120, 150, 70
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
             f'aria-label="{_esc(style.get("style_name", ""))}, {VIEW_NAMES[view]}">',
             '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{fin_hi}"/><stop offset="1" stop-color="{fin_lo}"/></linearGradient></defs>',
             f'<rect width="{W}" height="{H}" fill="#eef1f2"/>']
    if view == "front":
        parts.append(_strap(cx - 30, 60, 0, cy - r + 10, mat, strap))
        parts.append(_strap(cx - 30, 60, cy + r - 10, H, mat, strap))
        parts.append(_case_path(shape, cx, cy, r) + ' fill="url(#g)"/>')
        parts.append(f'<rect x="{cx + r - 2}" y="{cy - 8}" width="10" height="16" rx="3" fill="{fin_lo}"/>')
        parts.append(_case_path(shape, cx, cy, r - 10) + f' fill="{dial}"/>')
        if digital:
            parts.append(f'<rect x="{cx - 42}" y="{cy - 18}" width="84" height="36" rx="4" fill="#0f1a14" opacity=".85"/>')
            parts.append(f'<text x="{cx}" y="{cy + 10}" font-family="monospace" font-size="26" fill="#9ef0b8" text-anchor="middle">10:08</text>')
        else:
            import math
            for i in range(12):
                a = math.radians(i * 30)
                r1, r2 = r - 18, r - (26 if i % 3 == 0 else 22)
                parts.append(f'<line x1="{cx + r1 * math.sin(a):.1f}" y1="{cy - r1 * math.cos(a):.1f}" '
                             f'x2="{cx + r2 * math.sin(a):.1f}" y2="{cy - r2 * math.cos(a):.1f}" stroke="{ink}" '
                             f'stroke-width="{3 if i % 3 == 0 else 1.5}" stroke-linecap="round"/>')
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx - 22}" y2="{cy - 26}" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>')
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + 34}" y2="{cy - 30}" stroke="{ink}" stroke-width="3" stroke-linecap="round"/>')
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{ink}"/>')
    elif view == "side":
        try:
            th = max(18, min(40, float(style.get("case_thickness_mm") or 11) * 2.6))
        except ValueError:
            th = 28
        parts.append(f'<rect x="{cx - 95}" y="{cy - th / 2 + 4:.1f}" width="60" height="{th - 8:.1f}" fill="{strap}"/>')
        parts.append(f'<rect x="{cx + 35}" y="{cy - th / 2 + 4:.1f}" width="60" height="{th - 8:.1f}" fill="{strap}"/>')
        parts.append(f'<rect x="{cx - 40}" y="{cy - th / 2:.1f}" width="80" height="{th:.1f}" rx="8" fill="url(#g)"/>')
        parts.append(f'<rect x="{cx - 34}" y="{cy - th / 2 - 4:.1f}" width="68" height="5" rx="2" fill="#dfe8ee" opacity=".9"/>')
        parts.append(f'<rect x="{cx + 40}" y="{cy - 6}" width="9" height="12" rx="2" fill="{fin_lo}"/>')
        parts.append(f'<text x="{cx}" y="{cy + th / 2 + 26:.1f}" font-family="sans-serif" font-size="12" fill="#536070" '
                     f'text-anchor="middle">{_esc(style.get("case_thickness_mm") or "")} mm thick</text>')
    else:   # back
        parts.append(_strap(cx - 30, 60, 0, cy - r + 10, mat, strap))
        parts.append(_strap(cx - 30, 60, cy + r - 10, H, mat, strap))
        parts.append(_case_path(shape, cx, cy, r) + ' fill="url(#g)"/>')
        parts.append(_case_path(shape, cx, cy, r - 14) + f' fill="{fin_lo}" opacity=".55"/>')
        txt = [style.get("case_material") or "", f"WATER RESISTANT {wr} M" if wr else "", sku["sku"]]
        tcol = "#20262b" if _lum(fin_lo) > 0.35 else "#eef1f2"
        for i, t in enumerate([t for t in txt if t]):
            parts.append(f'<text x="{cx}" y="{cy - 10 + i * 16}" font-family="sans-serif" font-size="9.5" fill="{tcol}" '
                         f'text-anchor="middle" opacity=".8">{_esc(t)}</text>')
    parts.append(f'<text x="{W - 8}" y="{H - 8}" font-family="sans-serif" font-size="10" fill="#536070" '
                 f'text-anchor="end">illustration</text></svg>')
    return "".join(parts)


# ---------------------------------------------------------------- table
def media_dir(data_dir=None):
    from tools import mock_tools
    return os.path.join(data_dir or mock_tools.DATA_DIR, "media")


def table_path(data_dir=None):
    from tools import mock_tools
    return os.path.join(data_dir or mock_tools.DATA_DIR, "media.csv")


def build(data_dir=None):
    from tools import mock_tools
    db = mock_tools._load()
    out_dir = media_dir(data_dir)
    os.makedirs(out_dir, exist_ok=True)
    rows, seen_gtin = [], {}
    for code, sku in sorted(db["skus"].items()):
        style = db["styles"].get(sku["style_id"], {})
        ean = sku.get("ean") or ""
        ok = gtin_ok(ean) and ean not in seen_gtin
        seen_gtin.setdefault(ean, code)
        stem = gtin14(ean) if ok else f"sku_{code}"           # a bad or shared GTIN falls back to the SKU, flagged
        for rank, (view, vcode) in enumerate(VIEWS.items()):
            fn = f"{stem}_{vcode}.svg"
            with open(os.path.join(out_dir, fn), "w", encoding="utf-8") as f:
                f.write(draw(dict(sku, sku=code), style, view))
            rows.append({"sku": code, "gtin": ean, "gtin_valid": int(ok), "view": view, "rank": rank,
                         "is_main": int(view == "front"), "file": fn, "width": 240, "height": 300,
                         "alt": f"{style.get('style_name', '')}, {sku.get('dial_colour', '')} dial, "
                                f"{sku.get('strap_colour', '')} {sku.get('strap_material', '')}, {VIEW_NAMES[view]}",
                         "source": "illustration"})
    with open(table_path(data_dir), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    _INDEX.clear()
    return rows


def _index():
    if not _INDEX:
        p = table_path()
        if not os.path.exists(p):
            return {}
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                _INDEX.setdefault(r["sku"], {})[r["view"]] = r
    return _INDEX


def lookup(sku, view="front"):
    """The image row for a SKU and view, or None."""
    return (_index().get(sku) or {}).get(view)


def url(row):
    return "/media/" + row["file"] if row else None


def validate(data_dir=None):
    from tools import mock_tools
    db = mock_tools._load()
    idx = _index()
    out_dir = media_dir(data_dir)
    problems, gt_bad = [], []
    for code in db["skus"]:
        v = idx.get(code) or {}
        if "front" not in v:
            problems.append(f"{code}: no main image")
        for view, r in v.items():
            if not os.path.exists(os.path.join(out_dir, r["file"])):
                problems.append(f"{code}: missing file {r['file']}")
            if r["gtin_valid"] == "1" and not r["file"].startswith(gtin14(r["gtin"])):
                problems.append(f"{code}: file name does not match its GTIN")
        if v and next(iter(v.values()))["gtin_valid"] != "1":
            gt_bad.append(code)
    orphans = [k for k in idx if k not in db["skus"]]
    files = set(os.listdir(out_dir)) if os.path.isdir(out_dir) else set()
    listed = {r["file"] for v in idx.values() for r in v.values()}
    stray = sorted(files - listed)
    return {"skus": len(db["skus"]), "with_main": sum(1 for c in db["skus"] if "front" in (idx.get(c) or {})),
            "rows": sum(len(v) for v in idx.values()), "problems": problems, "orphan_rows": orphans,
            "stray_files": stray[:20], "gtin_fallback": gt_bad}


def lookup_timing(n_rounds=5):
    from tools import mock_tools
    codes = list(mock_tools._load()["skus"])
    _INDEX.clear()
    t = time.perf_counter()
    _index()
    load_ms = (time.perf_counter() - t) * 1000
    ts = []
    for _ in range(n_rounds):
        for c in codes:
            for v in VIEWS:
                t = time.perf_counter()
                show_product_images(c, v)
                ts.append((time.perf_counter() - t) * 1000)
    ts.sort()
    return {"load_ms": round(load_ms, 1), "n": len(ts), "p50_ms": round(ts[len(ts) // 2], 4),
            "p95_ms": round(ts[int(len(ts) * .95)], 4), "max_ms": round(ts[-1], 3)}


# ---------------------------------------------------------------- the tool
SCHEMA = {"type": "function", "function": {
    "name": "show_product_images", "description": "Show pictures of one watch by its product code.",
    "parameters": {"type": "object", "properties": {
        "product_id": {"type": "string"}, "view": {"type": "string", "enum": list(VIEWS)}},
        "required": ["product_id"]}}}


def show_product_images(product_id, view=None):
    """Images of one SKU: the requested view first, then the others. A design code (V1546) gives its first
    variant's images. Images come only from this lookup, never from model text."""
    from tools import mock_tools
    db = mock_tools._load()
    pid = (product_id or "").strip().upper()
    if pid.startswith("V") and pid in db["styles"]:
        variants = sorted(k for k, s in db["skus"].items() if s["style_id"] == pid)
        pid = variants[0] if variants else pid
    if pid not in db["skus"]:
        return {"error": {"type": "not_found", "message": f"No product with code {product_id}."}}
    rows = _index().get(pid) or {}
    if not rows:
        return {"error": {"type": "no_images", "message": f"No images for {pid} yet."}}
    want = view if view in VIEWS else "front"
    order = [want] + [v for v in VIEWS if v != want]
    sku = db["skus"][pid]
    style = db["styles"].get(sku["style_id"], {})
    return {"product_id": pid, "name": sku["product_name"], "design": style.get("style_name"),
            "images": [{"view": v, "url": url(rows[v]), "alt": rows[v]["alt"]} for v in order if v in rows]}


# ---------------------------------------------------------------- requests in a message
IMAGE_RE = re.compile(
    r"\b(photo|photos|picture|pictures|pic|pics|image|images|tasveer|tasvir|foto|"
    r"look(?:s)? like|kais[ai] dikh(?:ti|ta)|dikhne mein|"
    r"(?:see|show|dikhao|dikha(?:o|iye|na)?)\b[^.?!]{0,30}\b(?:back|side|front|caseback|peeche|piche|saamne|bagal)|"
    r"(?:back|side|front)\s*view)\b", re.I)
# "see-through caseback" is a question about the watch, not a request to see it
NOT_IMAGE_RE = re.compile(r"see[- ]through|transparent|exhibition", re.I)
BACK_RE = re.compile(r"\b(back|caseback|case back|peeche|piche|pichhe|reverse)\b", re.I)
SIDE_RE = re.compile(r"\b(side|profile|bagal|kinare|thickness|how thick)\b", re.I)


def wants_images(text):
    return bool(IMAGE_RE.search(text or "")) and not NOT_IMAGE_RE.search(text or "")


def view_of(text):
    t = text or ""
    if BACK_RE.search(t):
        return "back"
    if SIDE_RE.search(t):
        return "side"
    return "front"


def reply_text(res, view, hinglish):
    if "error" in res:
        if res["error"]["type"] == "not_found":
            code = res["error"]["message"].split("code ", 1)[-1].rstrip(".")
            return (f"Maaf kijiye, {code} hamare catalogue mein nahi mila. Kya aap code dobara check kar sakte hain?"
                    if hinglish else f"Sorry, I couldn't find {code} in our catalogue. Could you check the code?")
        return ("Iski tasveer abhi available nahi hai. Kya main staff member ko bula doon?" if hinglish
                else "There's no picture of this watch yet. Would you like me to call a staff member?")
    name = res.get("design") or res["product_id"]
    vw = {"front": "", "side": " side", "back": " back"}[view]
    if hinglish:
        return f"Yeh rahi {name} ({res['product_id']}) ki{vw} tasveer. Baaki views bhi neeche hain."
    return f"Here is the{vw} view of the {name} ({res['product_id']}). The other views are below it."


def main(argv=None):
    import json
    cmd = (argv or sys.argv[1:] or ["check"])[0]
    if cmd == "build":
        rows = build()
        print(f"Wrote {len(rows)} images ({len(rows) // len(VIEWS)} SKUs x {len(VIEWS)} views) to {media_dir()} "
              f"and {table_path()}")
    v = validate()
    tm = lookup_timing()
    print(json.dumps({"validation": {k: (len(x) if isinstance(x, list) else x) for k, x in v.items()},
                      "problems (first 10)": v["problems"][:10], "gtin_fallback (first 10)": v["gtin_fallback"][:10],
                      "lookup": tm}, indent=1))
    return 0 if not v["problems"] and not v["orphan_rows"] and tm["p95_ms"] <= 50 else 1


if __name__ == "__main__":
    sys.exit(main())
