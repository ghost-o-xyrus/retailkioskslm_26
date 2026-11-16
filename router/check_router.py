"""
Objective 3, Step 4: router accuracy on labelled cases (no language model needed).

    python router\\check_router.py                       # dev, rules + bge-small prototypes
    python router\\check_router.py --rules-only          # rules alone
    python router\\check_router.py --split test          # once, after tuning, as an overfitting check

Labels: eval/route_labels.json (python eval\\route_labels.py). Reports:
  accuracy            route == label ("unclear" counts as wrong)
  retrieval decision  retrieve (store or unclear) vs no retrieval, the decision Step 4 acts on
  store misrouted     store questions sent down a no-retrieval path (target <= 3%)
  unclear share       messages that fall back to the Objective 2 path
  latency             p50 / p95 per message
Pre-registered rule (Objective 3 plan): accuracy >= 95%, store misrouted <= 3%, p50 < 20 ms.
Writes <out>/report.md, <out>/routes.json and <out>/misroutes.csv.
"""

import argparse
import csv
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "retrieval"))

from router.router import Router, ROUTES  # noqa: E402

RETRIEVE = {"store", "unclear"}


class QueryEncoder:
    """bge-small with its query prefix, as the retriever uses it. backend: sentence-transformers (PyTorch)."""
    def __init__(self, fake=False):
        if fake:
            from bench_retrieval import FakeEncoder
            self.m, self.prefix = FakeEncoder(), ""
        else:
            from sentence_transformers import SentenceTransformer
            from retrievers import PREFIXES
            from knowledge_base import EMBEDDER
            self.m = SentenceTransformer(EMBEDDER, device="cpu")
            self.prefix = PREFIXES.get(EMBEDDER, ("", ""))[0]

    def encode_query(self, text):
        import numpy as np
        v = self.m.encode([self.prefix + text], normalize_embeddings=True, convert_to_numpy=True,
                          show_progress_bar=False)
        return np.asarray(v, dtype="float32")[0]


def load_cases():
    out = {}
    for f in ("rag_cases.jsonl", "eval_set_v1.2.jsonl"):
        with open(os.path.join(ROOT, "eval", f), encoding="utf-8") as fh:
            for line in fh:
                c = json.loads(line)
                out[c["id"]] = c
    return out


def pct(x):
    return f"{100 * x:.1f}%"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--rules-only", action="store_true")
    ap.add_argument("--fake-encoder", action="store_true", help="tests only")
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj3", "_router"))
    a = ap.parse_args(argv)
    with open(os.path.join(ROOT, "eval", "route_labels.json"), encoding="utf-8") as f:
        labels = json.load(f)
    cases = load_cases()
    enc = None if a.rules_only else QueryEncoder(fake=a.fake_encoder)
    router = Router(encoder=enc)
    rows = []
    for cid, lab in sorted(labels.items()):
        if a.split != "all" and lab["split"] != a.split:
            continue
        c = cases[cid]
        r = router.route(c["messages"])
        rows.append({"id": cid, "set": "retrieval" if lab["file"].startswith("rag") else "v1.2",
                     "category": f"{lab['category']}/{lab['subcategory']}", "label": lab["route"], "route": r["route"],
                     "source": r["source"], "ms": r["ms"], "message": c["messages"][-1]["content"],
                     "scores": {k: v for k, v in r.get("scores", {}).items() if v}})
    n = len(rows)
    ok = sum(x["route"] == x["label"] for x in rows)
    ret_ok = sum((x["route"] in RETRIEVE) == (x["label"] in RETRIEVE) for x in rows)
    store = [x for x in rows if x["label"] == "store"]
    store_mis = sum(x["route"] not in RETRIEVE for x in store)
    nonstore = [x for x in rows if x["label"] != "store"]
    extra_retrieval = sum(x["route"] in RETRIEVE for x in nonstore)
    unclear = sum(x["route"] == "unclear" for x in rows)
    ms = sorted(x["ms"] for x in rows)
    p50, p95 = statistics.median(ms), ms[int(0.95 * (n - 1))]
    passed = ok / n >= 0.95 and (store_mis / len(store) if store else 0) <= 0.03 and p50 < 20

    os.makedirs(a.out, exist_ok=True)
    mode = "rules only" if a.rules_only else ("rules + fake prototypes" if a.fake_encoder else "rules + bge-small prototypes")
    L = [f"# Router check ({a.split} split, {mode})", "",
         f"| Measure | Value | Target |", "|---|---:|---|",
         f"| Messages | {n} | |",
         f"| Accuracy (route = label; unclear counts as wrong) | {ok}/{n} = {pct(ok / n)} | ≥ 95% |",
         f"| Retrieval decision right | {ret_ok}/{n} = {pct(ret_ok / n)} | |",
         f"| Store questions sent down a no-retrieval path | {store_mis}/{len(store)} = {pct(store_mis / max(1, len(store)))} | ≤ 3% |",
         f"| Other messages given retrieval anyway | {extra_retrieval}/{len(nonstore)} = {pct(extra_retrieval / max(1, len(nonstore)))} | |",
         f"| Unclear (Objective 2 path) | {unclear}/{n} = {pct(unclear / n)} | |",
         f"| Latency p50 / p95 | {p50:.2f} / {p95:.2f} ms | p50 < 20 ms |",
         f"| Decided by | {dict(Counter(x['source'] for x in rows))} | |",
         "", f"**Verdict: {'PASS' if passed else 'FAIL'}** against the pre-registered rule.", "",
         "## Confusion (rows = label, columns = route)", "",
         "| Label | " + " | ".join(ROUTES + ("unclear",)) + " | Accuracy |", "|---|" + "---:|" * (len(ROUTES) + 2)]
    conf = defaultdict(Counter)
    for x in rows:
        conf[x["label"]][x["route"]] += 1
    for lab in ROUTES:
        if conf[lab]:
            tot = sum(conf[lab].values())
            L.append(f"| {lab} | " + " | ".join(str(conf[lab][r] or "") for r in ROUTES + ("unclear",))
                     + f" | {pct(conf[lab][lab] / tot)} ({tot}) |")
    L += ["", "## By set", "", "| Set | Messages | Accuracy | Retrieval decision |", "|---|---:|---:|---:|"]
    for st in ("retrieval", "v1.2"):
        xs = [x for x in rows if x["set"] == st]
        if xs:
            L.append(f"| {st} | {len(xs)} | {pct(sum(x['route'] == x['label'] for x in xs) / len(xs))} "
                     f"| {pct(sum((x['route'] in RETRIEVE) == (x['label'] in RETRIEVE) for x in xs) / len(xs))} |")
    mis = [x for x in rows if x["route"] != x["label"]]
    L += ["", f"## Misroutes ({len(mis)})", "", "| Case | Category | Label | Route | Source | Message |", "|---|---|---|---|---|---|"]
    for x in mis:
        L.append(f"| {x['id']} | {x['category']} | {x['label']} | {x['route']} | {x['source']} | {x['message'][:90]} |")
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "routes.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=0, ensure_ascii=False)
    with open(os.path.join(a.out, "misroutes.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["id", "category", "label", "route", "source", "message"], extrasaction="ignore")
        w.writeheader()
        w.writerows(mis)
    print(f"{a.split}: accuracy {pct(ok / n)}, store misrouted {pct(store_mis / max(1, len(store)))}, "
          f"unclear {pct(unclear / n)}, p50 {p50:.2f} ms -> {'PASS' if passed else 'FAIL'}")
    print(f"Wrote {os.path.join(a.out, 'report.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
