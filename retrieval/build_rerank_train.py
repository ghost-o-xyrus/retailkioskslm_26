"""
Objective 3, Step 9a: training pairs for fine-tuning the re-ranker, generated from the corpus alone.

    python retrieval\\build_rerank_train.py            # uses the deployed first stage to mine hard negatives
    python retrieval\\build_rerank_train.py --fake     # code-path test, no models

Questions are written from templates over each chunk's own fields (design names, specs, collection facts, FAQ,
policy, offer, store and glossary titles), in English and Hinglish, with some typos in design names. No eval
question, label or gold id is read to write them. Every eval text (retrieval_eval, rag_cases, eval sets v1-v1.2,
dialogue openings, dev and test) is read only to DROP generated questions that are too close to one of them:
the same normalised text, or a word overlap (Jaccard) of 0.6 or more.

Each question gets its source chunk as the positive and 4 negatives: 3 drawn from the first stage's top 20 (hard
negatives) and 1 at random. A negative that could also answer the question is skipped: for non-product
questions, a chunk containing every content word of the question. 10% of source chunks are held out (gen-val)
as a sanity check for the training run; they are not an eval set.

Writes knowledge/rerank_train.jsonl, knowledge/rerank_genval.jsonl and results_obj3/_rerank_step9/train_data.md.
"""

import argparse
import json
import os
import random
import re
import sys
import zlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from retrievers import BM25Retriever, DenseRetriever, HybridRetriever, tokenize  # noqa: E402
import bench_retrieval as B  # noqa: E402

EMBEDDER = "BAAI/bge-small-en-v1.5"
EVAL_FILES = ["knowledge/retrieval_eval.jsonl", "eval/rag_cases.jsonl", "eval/eval_set.jsonl",
              "eval/eval_set_v1.1.jsonl", "eval/eval_set_v1.2.jsonl", "eval/o3_dialogues.jsonl"]
JACCARD_MAX = 0.6
SEED = 13

P_EN = ["What glass does the {n} have?", "Is the {n} water resistant?", "How big is the {n}?",
        "What is the case of the {n} made of?", "Where is the {n} made?", "What warranty does the {n} come with?",
        "Tell me about the {n}.", "How much does the {n} cost?", "Does the {n} have luminous hands?",
        "What movement does the {n} use?", "Which dial colours can I get the {n} in?", "Is the {n} for men or women?",
        "What straps are available for the {n}?", "Can I swim with the {n}?", "Price of {n}?", "{n} details please",
        "Does the {n} show the date?", "How thick is the {n}?"]
P_HI = ["{n} mein kaun sa glass hai?", "{n} waterproof hai kya?", "{n} ki warranty kitni hai?",
        "{n} kahan bani hai?", "{n} ka size kitna hai?", "{n} kitne ki hai?", "{n} ke baare mein batao",
        "{n} ka strap kaisa hai?", "{n} ladies ke liye hai ya gents?", "{n} mein date dikhta hai kya?"]
C_EN = ["What is in the {c} collection?", "Which dial colours does the {c} range come in?",
        "What is the price range of {c} watches?", "Are {c} watches automatic or quartz?",
        "How many designs are in the {c} line?", "What sizes do {c} watches come in?"]
C_HI = ["{c} collection mein kya kya hai?", "{c} range ki price kitni hai?", "{c} watches kitne size mein aati hain?"]
D_EN = ["I'm after a {g} {s} watch, {m}, about {z} mm, {d} dial, {st}.",
        "Looking for a {d}-dial {s} watch for {g}, {st}, {m}, {z} mm.",
        "Show me a {z} mm {m} {s} watch for {g} with a {d} dial on {st}."]
D_HI = ["{g} ke liye {s} watch chahiye, {m}, {z} mm, {d} dial aur {st}."]
GLOSS_EN = ["What does {t} mean?", "What is {t} on a watch?", "Explain {t}."]
GLOSS_HI = ["{t} kya hota hai?", "{t} ka matlab kya hai?"]
GEN_EN = ["Tell me about the {t}.", "{t}?", "What should I know about the {t}?"]
GEN_HI = ["{t} ke baare mein batao", "{t} kya hai?"]
FAQ_PREFIX = ["", "Can you tell me: ", "Quick question, ", "Hi, "]


def norm(t):
    return " ".join(re.findall(r"[a-z0-9]+", t.lower()))


def typo(word, rng):
    if len(word) < 5:
        return word
    i = rng.randrange(1, len(word) - 1)
    op = rng.choice(["drop", "swap", "double"])
    if op == "drop":
        return word[:i] + word[i + 1:]
    if op == "swap":
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    return word[:i] + word[i] + word[i:]


def field(text, name):
    m = re.search(name + r":\s*([^.\n]+)", text)
    return m.group(1).strip() if m else None


def product_queries(c, rng, unique_combo):
    name = c["title"].replace("Veyra ", "", 1)
    out = []
    for tpl in rng.sample(P_EN, 4):
        out.append(("en", "product", tpl.format(n=name)))
    out.append(("hinglish", "product", rng.choice(P_HI).format(n=name)))
    if rng.random() < 0.3:                      # a typo in one word of the design name
        words = name.split()
        j = rng.randrange(len(words))
        words[j] = typo(words[j], rng)
        out.append(("en", "product_typo", rng.choice(P_EN).format(n=" ".join(words))))
    if unique_combo and rng.random() < 0.5:
        g, s, m_, z, d, st = unique_combo
        lang = "hinglish" if rng.random() < 0.25 else "en"
        tpl = rng.choice(D_HI if lang == "hinglish" else D_EN)
        out.append((lang, "product_description", tpl.format(g=g, s=s, m=m_, z=z, d=d, st=st)))
    return out


def combos(products):
    """(design id) -> one variant's attribute combination that no other design shares."""
    seen, per = Counter(), {}
    for c in products:
        t = c["text"]
        g = {"men": "men", "women": "women", "unisex": "everyone", "kids": "kids"}.get((field(t, "For") or "").split(",")[0])
        s, m_ = field(t, "Style"), field(t, "Movement")
        z = re.search(r"(\d+) mm wide", t)
        lst = []
        for vm in re.finditer(r"- \w+: ([\w -]+?) dial, [^,]+, ([\w -]+?)\. MRP", t):
            key = (g, s, m_, z.group(1) if z else None, vm.group(1), vm.group(2))
            if None not in key:
                lst.append(key)
                seen[key] += 1
        per[c["id"]] = lst
    return {cid: next((k for k in ks if seen[k] == 1), None) for cid, ks in per.items()}


def other_queries(c, rng):
    t, title = c["type"], re.sub(r"\s*\([^)]*\)", "", c["title"]).strip()
    out = []
    if t == "collection":
        col = title.replace(" collection", "")
        out += [("en", t, q.format(c=col)) for q in rng.sample(C_EN, 3)] + [("hinglish", t, rng.choice(C_HI).format(c=col))]
    elif t == "faq":
        q = title.rstrip("?")
        out += [("en", t, rng.choice(FAQ_PREFIX) + title), ("en", t, q.lower() + "?")]
        kw = " ".join(w for w in re.findall(r"[A-Za-z]+", q) if w.lower() not in B_STOP)
        if kw:
            out += [("en", t, kw.lower()), ("hinglish", t, rng.choice(GEN_HI).format(t=kw.lower()))]
    elif t == "glossary":
        out += [("en", t, q.format(t=title.lower())) for q in rng.sample(GLOSS_EN, 2)] + \
               [("hinglish", t, rng.choice(GLOSS_HI).format(t=title.lower()))]
    else:                                      # policy, offer, store
        out += [("en", t, q.format(t=title)) for q in rng.sample(GEN_EN, 2)] + \
               [("hinglish", t, rng.choice(GEN_HI).format(t=title))]
    return out


B_STOP = {"what", "are", "is", "the", "do", "you", "can", "i", "a", "an", "my", "of", "to", "for", "on", "in", "does",
          "how", "it", "if", "with", "be", "your", "there", "any", "and", "or", "get", "have", "will", "which", "when"}


def eval_texts():
    out = []
    for rel in EVAL_FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        for it in B.load_jsonl(p):
            if it.get("query"):
                out.append(it["query"])
            for m in it.get("messages") or []:
                if m.get("role") == "user":
                    out.append(m["content"])
    return out


def too_close(q, eval_norm, eval_tok):
    n = norm(q)
    if n in eval_norm:
        return True
    a = set(tokenize(q))
    if not a:
        return False
    for b in eval_tok:
        if b and len(a & b) / len(a | b) >= JACCARD_MAX:
            return True
    return False


def answers_too(q, chunk_text):
    words = [w for w in tokenize(q) if len(w) > 2]
    return len(words) >= 2 and all(w in tokenize(chunk_text) for w in words)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=os.path.join(ROOT, "knowledge", "corpus.jsonl"))
    ap.add_argument("--out-train", default=os.path.join(ROOT, "knowledge", "rerank_train.jsonl"))
    ap.add_argument("--out-val", default=os.path.join(ROOT, "knowledge", "rerank_genval.jsonl"))
    ap.add_argument("--report", default=os.path.join(ROOT, "results_obj3", "_rerank_step9", "train_data.md"))
    ap.add_argument("--fake", action="store_true")
    a = ap.parse_args(argv)
    rng = random.Random(SEED)
    chunks = B.load_jsonl(a.corpus)
    by_id = {c["id"]: c for c in chunks}
    products = [c for c in chunks if c["type"] == "product"]
    uniq = combos(products)

    raw = []
    for c in chunks:
        qs = product_queries(c, rng, uniq.get(c["id"])) if c["type"] == "product" else other_queries(c, rng)
        raw += [dict(query=q, lang=lang, template=kind, pos=c["id"]) for lang, kind, q in qs]

    ev = eval_texts()
    ev_norm = {norm(t) for t in ev}
    ev_tok = [set(tokenize(t)) for t in ev]
    seen, kept, dropped = set(), [], Counter()
    for r in raw:
        n = norm(r["query"])
        if n in seen:
            dropped["duplicate"] += 1
            continue
        seen.add(n)
        if too_close(r["query"], ev_norm, ev_tok):
            dropped["close to an eval question"] += 1
            continue
        kept.append(r)

    print(f"{len(raw)} generated, {len(kept)} kept; first stage for hard negatives ...", flush=True)
    bm25 = BM25Retriever(chunks)
    dense = DenseRetriever(chunks, EMBEDDER, encoder=B.FakeEncoder() if a.fake else None)
    hybrid = HybridRetriever(bm25, dense)
    ids = [c["id"] for c in chunks]
    pos_in_top20 = 0
    for i, r in enumerate(kept, 1):
        top = [cid for cid, _ in hybrid.search(r["query"], 20)]
        pos_in_top20 += r["pos"] in top
        cand = [cid for cid in top if cid != r["pos"] and not (by_id[r["pos"]]["type"] != "product" and
                                                               answers_too(r["query"], by_id[cid]["text"]))]
        negs = rng.sample(cand, min(3, len(cand)))
        while True:
            x = rng.choice(ids)
            if x != r["pos"] and x not in negs:
                negs.append(x)
                break
        r["negs"] = negs
        if i % 500 == 0:
            print(f"  {i}/{len(kept)}", flush=True)

    held = lambda r: zlib.crc32(r["pos"].encode()) % 10 == 0   # noqa: E731
    train = [r for r in kept if not held(r)]
    val = [r for r in kept if held(r)]
    for path, rows in ((a.out_train, train), (a.out_val, val)):
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.makedirs(os.path.dirname(a.report), exist_ok=True)
    lang = Counter(r["lang"] for r in kept)
    kinds = Counter(r["template"] for r in kept)
    L = ["# Step 9a: re-ranker training data (generated from the corpus)", "",
         f"Generated {len(raw)} questions; kept {len(kept)} ({len(train)} train, {len(val)} gen-val held out by "
         f"source chunk). Dropped: " + ", ".join(f"{k} {v}" for k, v in dropped.items()) + ".", "",
         f"Languages: " + ", ".join(f"{k} {v}" for k, v in lang.items()) + ".",
         "Templates: " + ", ".join(f"{k} {v}" for k, v in sorted(kinds.items())) + ".",
         f"Positive in the first stage's top 20: {pos_in_top20}/{len(kept)} = {pos_in_top20 / max(1, len(kept)):.1%} "
         "(the re-ranker can only help when it is there).", "",
         "Leakage control: eval files read only to drop generated questions with the same normalised text or word "
         f"overlap >= {JACCARD_MAX} with any eval question (dev and test): " + ", ".join(EVAL_FILES) + "."]
    with open(a.report, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
