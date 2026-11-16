"""
Objective 5, Step 7: image-request cases.

40 dev and 40 test cases, generated with fixed seeds on different products, half Hinglish and a quarter
follow-ups (the watch named in an earlier turn). Kinds:
  code      "Can I see a photo of 1546SL01?"              -> that SKU, the view asked (front unless side or back)
  design    "Show me a picture of the Sovereign Saffron"  -> any variant of that design
  followup  (earlier turn names a code) "Can I see the back?" -> that SKU
  negative  an unknown code or another brand              -> no picture at all
The test split is used once, after the dev run passes.

    python eval\\build_image_cases.py      # writes eval/image_cases.jsonl
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

EN = {"front": ["Can I see a photo of {x}?", "Show me a picture of {x}.", "What does {x} look like?",
                "Do you have an image of {x}?"],
      "side": ["Can I see {x} from the side?", "Show me the side view of {x}."],
      "back": ["Can I see the back of {x}?", "Show me the caseback of {x}."]}
HI = {"front": ["{x} ki photo dikhao.", "{x} kaisi dikhti hai? Photo dikhaiye.", "{x} ki tasveer dikha sakte ho?"],
      "side": ["{x} ko side se dikhao, photo mein.", "{x} ki side view ki photo dikhao."],
      "back": ["{x} ka peeche se photo dikhao.", "{x} ki caseback ki photo dikhaiye."]}
FUP_EN = {"front": "Can I see a photo of it?", "side": "Can I see it from the side?", "back": "Can I see the back?"}
FUP_HI = {"front": "Iski photo dikhao.", "side": "Isko side se dikhao, photo mein.", "back": "Iska peeche se photo dikhao."}
NEG = [("en", "Can I see a photo of 9999SL01?"), ("hinglish", "8888AB01 ki photo dikhao."),
       ("en", "Show me a picture of a Rolex Submariner."), ("hinglish", "Casio G-Shock ki photo dikhao.")]


def build(split, seed, pool, n=40):
    from tools import mock_tools
    db = mock_tools._load()
    rng = random.Random(seed)
    skus = sorted(pool)
    rng.shuffle(skus)
    kinds = ["code"] * 14 + ["design"] * 12 + ["followup"] * 10 + ["negative"] * 4
    out = []
    for i, kind in enumerate(kinds):
        lang = "hinglish" if i % 2 else "en"
        view = rng.choice(["front", "front", "side", "back"])
        if kind == "negative":
            lang, text = NEG[len([c for c in out if c["subcategory"] == "negative"]) % len(NEG)]
            msgs, exp = [{"role": "user", "content": text}], {"images": None}
        else:
            sku = skus.pop()
            s = db["skus"][sku]
            st = db["styles"][s["style_id"]]
            if kind == "code":
                x = sku
            elif kind == "design":
                x = "the " + st["style_name"] if lang == "en" else st["style_name"]
            if kind == "followup":
                first = (f"Tell me about {sku}." if lang == "en" else f"{sku} ke baare mein batao.")
                said = (f"The {st['style_name']} ({sku}) has a {s['dial_colour']} dial and a {s['strap_colour']} "
                        f"{s['strap_material']} strap, at Rs {s['mrp']}.")
                msgs = [{"role": "user", "content": first}, {"role": "assistant", "content": said},
                        {"role": "user", "content": (FUP_EN if lang == "en" else FUP_HI)[view]}]
            else:
                tpl = rng.choice((EN if lang == "en" else HI)[view])
                msgs = [{"role": "user", "content": tpl.format(x=x)}]
            allowed = [sku] if kind != "design" else sorted(k for k, v in db["skus"].items()
                                                            if v["style_id"] == s["style_id"])
            exp = {"images": {"skus": allowed, "view": view, "style_id": s["style_id"]}}
        out.append({"id": f"IMG-{split[0].upper()}{i + 1:03d}", "category": "images", "subcategory": kind,
                    "mode": "tools", "language": lang, "difficulty": "", "messages": msgs, "context": None,
                    "expected": dict(exp, behaviour="images"), "rubric": [], "source": "eval/build_image_cases.py",
                    "notes": "", "split": split, "version": "o5-step7", "set": "images", "paired_with": None})
    return out


def main():
    from tools import mock_tools
    db = mock_tools._load()
    styles = sorted({v["style_id"] for v in db["skus"].values()})
    rng = random.Random(7707)
    rng.shuffle(styles)
    half = set(styles[: len(styles) // 2])          # dev and test use different designs
    dev_pool = [k for k, v in db["skus"].items() if v["style_id"] in half]
    test_pool = [k for k, v in db["skus"].items() if v["style_id"] not in half]
    cases = build("dev", 7711, dev_pool) + build("test", 7712, test_pool)
    p = os.path.join(ROOT, "eval", "image_cases.jsonl")
    with open(p, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    from collections import Counter
    print(f"Wrote {len(cases)} cases to {p}:",
          dict(Counter((c["split"], c["subcategory"]) for c in cases)),
          "Hinglish:", dict(Counter((c["split"], c["language"]) for c in cases)))


if __name__ == "__main__":
    main()
