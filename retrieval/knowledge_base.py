"""
The kiosk's knowledge base (Objective 2, Step 7): the retriever chosen in Steps 5 and 5b plus the refusal
fallback calibrated in Step 6, behind one call.

    from retrieval.knowledge_base import KnowledgeBase
    kb = KnowledgeBase()                 # loads corpus, BM25, bge-small, MiniLM (OpenVINO), fallback.json
    r = kb.retrieve("Do you do gift wrapping?")
    r["chunks"]       [{"id", "score", "tokens"}, ...] best first, at most k, within the token cap
    r["refuse"]       True if the fallback says "skip the model, reply with r['message']"
    r["timings_ms"]   bm25, dense, fuse, rerank, total
    kb.context(r)     the chunk texts, numbered, ready to show the model

Pipeline (fixed by Steps 5/5b, not tuned here):
    BM25 top 50 + bge-small-en-v1.5 top 50 -> reciprocal-rank fusion -> top 20
    -> ms-marco-MiniLM-L-6-v2 cross-encoder (OpenVINO, 256 tokens) -> sorted by re-ranker score
Fallback (Step 6b): refuse when the top re-ranker score is below the threshold in fallback.json, unless the
message is detected as Hinglish (retrieval/language.py) and the config has hinglish_bypass = true.

No score cache: every call runs the models, so logged latency is real even when a question repeats.
"""

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from retrievers import BM25Retriever, DenseRetriever, HybridRetriever  # noqa: E402
from language import is_hinglish  # noqa: E402

EMBEDDER = "BAAI/bge-small-en-v1.5"
RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"
DEFAULT_CORPUS = os.environ.get("SLM_CORPUS", os.path.join(ROOT, "knowledge", "corpus.jsonl"))
DEFAULT_FALLBACK = os.path.join(ROOT, "results_retrieval", "fallback_bypass", "fallback.json")
DEFAULT_INTEGRATION = os.path.join(ROOT, "results_retrieval", "integration", "integration.json")
DEFAULT_OV_DIR = os.path.join(ROOT, "models", "ov")     # Objective 3, Step 12: retrieval/export_openvino.py

# The tool the model can call in the "tool" condition of Step 8.
SEARCH_KNOWLEDGE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_knowledge",
        "description": ("Search the store's knowledge base: store policies (returns, exchange, warranty, "
                        "repairs), services (delivery, engraving, gift wrapping, EMI, payment), store hours and "
                        "locations, offers, watch care and terms, and product descriptions. Returns the most "
                        "relevant passages. Use it for any question the other tools cannot answer."),
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string",
                                     "description": "The customer's question, in your own words if that helps."}},
            "required": ["query"],
        },
    },
}


def load_chunks(path=DEFAULT_CORPUS):
    with open(path, encoding="utf-8") as f:
        return {c["id"]: c for c in (json.loads(l) for l in f if l.strip())}


# Objective 3, Step 13: "focused" cards keep a product card's name and range lines plus only the lines the question
# is about. Topic words -> the card line that answers them (English and the Hinglish words customers use).
FOCUS_TOPICS = [
    ("Movement:", r"(movement|automatic|quartz|solar|mechanical|kinetic|function|chrono\w*|date|day|digital|analog|"
                  r"alarm|stopwatch|backlight|open heart|hands)"),
    ("Case:", r"(case|size|mm|big|small|large|thick|thin|slim|wide|glass|sapphire|mineral|acrylic|crystal|water|swim|"
              r"shower|dive|diving|waterproof|resistan\w*|lume|luminous|glow|dark|shape|round|square|material|steel|"
              r"titanium|ceramic|brass|alloy|resin|cheez|kaanch|paani)"),
    ("Warranty:", r"(warranty|guarantee|battery|made|origin|country|where|kahan|bani|banayi|swiss|japan|india)"),
    ("Variants:", r"(price|cost|how much|much|rs|rupees|mrp|kitne|kitna|kitni|daam|keemat|kimat|qeemat|keemath|colou?r|dial|strap|bracelet|band|leather|metal|"
                  r"mesh|silicone|rubber|variant|version|option|available|stock|rang|black|white|blue|green|grey|gray|"
                  r"silver|gold|brown|pink|red)"),
]


def focused_text(chunk, question):
    """A compact product card cut to the lines the question needs; unchanged when no topic is recognised or the
    card is not a product card."""
    import re
    text = model_text(chunk, "compact")
    if chunk.get("type") != "product" or not question:
        return text
    q = question.lower()
    # Step 13a2: the watch's own name and collection are not topics ("Tick Digital Grove ki keemat" is about the
    # price, not the display), so their words are removed from the question before matching
    head = text.split("\n")[:2]
    m = re.match(r"Veyra (.+?) \(design", head[0]) if head else None
    own = (m.group(1) if m else "") + " " + " ".join(re.findall(r"Collection: ([^.]+)\.", head[1] if len(head) > 1 else ""))
    for w in set(re.findall(r"[a-z]+", own.lower())):
        q = re.sub(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", " ", q)
    want = {h for h, rx in FOCUS_TOPICS if re.search(r"(?<![a-z])" + rx + r"(?![a-z])", q)}
    if not want:
        return text
    lines, keep, block, codes = text.split("\n"), [], None, []
    for i, line in enumerate(lines):
        if i < 2:
            keep.append(line)                       # name + sub-brand/collection/for/style
            continue
        if line.startswith("- ") and block == "Variants:":
            if "Variants:" in want:
                keep.append(line)
            else:
                codes.append(line[2:].split(":")[0].strip())
            continue
        block = next((h for h, _ in FOCUS_TOPICS if line.startswith(h)), None)
        if block in want:
            keep.append(line)
    if codes:                                        # Step 13a2: the variant codes stay, so a reply naming one is
        keep.append("Variant codes: " + ", ".join(codes) + ".")   # still supported by what was shown
    return "\n".join(keep)


def model_text(chunk, view="full", question=None):
    """The text the model sees. "compact" drops the marketing description from product cards: it repeats the
    spec lines, holds all the planted description/spec contradictions, and is about 43% of a card's tokens.
    No fact in the retrieval eval set lives only in a description (checked in Step 7d). "focused" (Step 13) also
    keeps only the product-card lines the question is about. Retrieval and re-ranking use their own text, so scores
    and the fallback threshold are unchanged."""
    if view == "focused":
        return focused_text(chunk, question)
    if view == "compact" and chunk.get("type") == "product":
        return chunk["text"].split("\nDescription:")[0]
    return chunk["text"]


def view_tokens(chunk, view="full"):
    if view == "focused":
        view = "compact"           # the token budget uses the compact size as an upper bound
    full = chunk.get("tokens", 0)
    if view == "full" or not chunk["text"]:
        return full
    return round(full * len(model_text(chunk, view)) / len(chunk["text"]))


def format_context(chunks, ids, view="full", question=None):
    """Numbered chunk texts, as the model sees them. `chunks` maps id -> chunk."""
    ids = [cid for cid in ids if cid in chunks]
    if not ids:
        return "(nothing found)"
    return "\n\n".join(f"[{i}] {model_text(chunks[cid], view, question)}" for i, cid in enumerate(ids, 1))


def load_integration_k(path=DEFAULT_INTEGRATION, default=5):
    """k chosen in Step 7a (check_integration.py); falls back to 5 if that step has not been run."""
    try:
        with open(path, encoding="utf-8") as f:
            return int(json.load(f)["k"])
    except (OSError, KeyError, ValueError, json.JSONDecodeError):
        return default


_SHARED = {}   # loaded models and indexes, shared by every KnowledgeBase in this process


class KnowledgeBase:
    def __init__(self, corpus_path=DEFAULT_CORPUS, fallback_path=DEFAULT_FALLBACK, k=None, depth=20,
                 max_context_tokens=1500, backend="openvino", max_length=256, threads=4, fake=False,
                 workdir=None, view="full", chunk_gate=False, reranker=RERANKER, int8=False, rerank_view="full",
                 ov_dir=DEFAULT_OV_DIR):
        """view: "full" or "compact" (see model_text). chunk_gate: show only chunks whose re-ranker score is at
        or above the fallback threshold (Hinglish questions exempt when the bypass is on), so weak matches cost
        no prompt tokens. With nothing left, the model is told nothing relevant was found."""
        self.view, self.chunk_gate = view, chunk_gate
        if not os.path.exists(fallback_path):
            raise FileNotFoundError(f"Fallback config not found: {fallback_path}\n"
                                    "Run: python retrieval\\calibrate_fallback.py --hinglish-bypass")
        with open(fallback_path, encoding="utf-8") as f:
            self.fallback = json.load(f)
        self.threshold = float(self.fallback["threshold"])
        self.bypass = bool(self.fallback.get("hinglish_bypass", False))
        self.messages = self.fallback["messages"]
        self.k = k if k is not None else load_integration_k()
        self.depth, self.max_context_tokens = depth, max_context_tokens

        os.environ.setdefault("OMP_NUM_THREADS", str(threads))
        # Objective 3, Step 9: another re-ranker (hub name or a folder inside the project) can replace MiniLM
        if reranker != RERANKER and not os.path.isabs(reranker) and os.path.isdir(os.path.join(ROOT, reranker)):
            reranker = os.path.join(ROOT, reranker)
        self.reranker = reranker
        self.rerank_view = rerank_view        # Step 12: "compact" re-ranks the card without its description
        key = (os.path.abspath(corpus_path), backend, max_length, threads, fake, reranker, int8)
        self.reused = key in _SHARED
        if not self.reused:
            # Load the models and index the corpus once per process. A plan runs several conditions one after
            # another in one process; reloading each time cost about 77 s and leaked about 0.3 GB per run.
            with open(corpus_path, encoding="utf-8") as f:
                chunks = [json.loads(l) for l in f if l.strip()]
            if fake:
                from bench_retrieval import FakeEncoder, FakeCrossEncoder
                encoder, cross = FakeEncoder(), FakeCrossEncoder()
            elif backend == "ovrt":
                # Step 12: OpenVINO runtime + tokenizers only; PyTorch is never imported
                from ov_runtime import OVEncoder, OVCrossEncoder
                encoder = OVEncoder(os.path.join(ov_dir, "bge-small"), threads)
                rname = "minilm" if reranker == RERANKER else os.path.basename(os.path.normpath(reranker))
                cross = OVCrossEncoder(os.path.join(ov_dir, rname), threads, max_length, int8=int8)
            else:
                try:
                    import torch
                    torch.set_num_threads(threads)
                except Exception:
                    pass
                from bench_latency import load_cross_encoder
                encoder = None
                cross = load_cross_encoder(backend, max_length, threads, workdir or os.path.join(ROOT, "results_retrieval"),
                                           model_name=reranker)
            bm25 = BM25Retriever(chunks)
            dense = DenseRetriever(chunks, EMBEDDER, encoder=encoder)
            _SHARED[key] = dict(chunks={c["id"]: c for c in chunks}, bm25=bm25, dense=dense, cross=cross,
                                hybrid=HybridRetriever(bm25, dense))
        sh = _SHARED[key]
        self.chunks, self.bm25, self.dense, self.hybrid, self.cross = (sh["chunks"], sh["bm25"], sh["dense"],
                                                                       sh["hybrid"], sh["cross"])
        self.config = dict(embedder=EMBEDDER, reranker=os.path.relpath(reranker, ROOT) if os.path.isabs(reranker) else reranker, backend="fake" if fake else backend,
                           max_length=max_length, depth=depth, k=self.k, max_context_tokens=max_context_tokens,
                           threshold=self.threshold, hinglish_bypass=self.bypass, view=view, chunk_gate=chunk_gate,
                           fallback_file=os.path.relpath(fallback_path, ROOT), int8=int8, rerank_view=rerank_view,
                           threads=threads)

    def retrieve(self, query, k=None):
        k = k or self.k
        t0 = time.perf_counter()
        bm = self.bm25.search(query, self.hybrid.depth)
        t1 = time.perf_counter()
        dn = self.dense.search(query, self.hybrid.depth)
        t2 = time.perf_counter()
        fused = HybridRetriever.fuse([bm, dn], self.depth, self.hybrid.rrf_k)
        t3 = time.perf_counter()
        ids = [cid for cid, _ in fused]
        scores = self.cross.predict([(query, model_text(self.chunks[c], self.rerank_view)) for c in ids],
                                    batch_size=32 if self.config.get("backend") == "ovrt" else 16,
                                    show_progress_bar=False) if ids else []
        ranked = sorted(zip(ids, (float(s) for s in scores)), key=lambda kv: (-kv[1], kv[0]))
        t4 = time.perf_counter()

        top1 = ranked[0][1] if ranked else float("-inf")
        hing = is_hinglish(query)
        refuse = top1 < self.threshold and not (self.bypass and hing)
        chosen, used = [], 0
        for cid, s in ranked[:k]:
            tok = view_tokens(self.chunks[cid], self.view)
            if chosen and used + tok > self.max_context_tokens:
                break
            chosen.append({"id": cid, "score": round(s, 4), "tokens": tok})
            used += tok
        shown = chosen
        if self.chunk_gate and not (self.bypass and hing):
            shown = [c for c in chosen if c["score"] >= self.threshold]
        used = sum(c["tokens"] for c in shown)
        ms = lambda a, b: round((b - a) * 1000, 1)
        return {"query": query, "chunks": shown, "retrieved": [c["id"] for c in chosen],
                "top1": round(top1, 4) if ranked else None,
                "top10": [[cid, round(s, 4)] for cid, s in ranked[:10]],
                "hinglish": hing, "refuse": refuse, "message": self.messages["hinglish" if hing else "en"],
                "context_tokens": used,
                "timings_ms": {"bm25": ms(t0, t1), "dense": ms(t1, t2), "fuse": ms(t2, t3),
                               "rerank": ms(t3, t4), "total": ms(t0, t4)}}

    def context(self, ids_or_result):
        """Numbered chunk texts. Accepts a retrieve() result or a list of chunk ids."""
        ids = [c["id"] for c in ids_or_result["chunks"]] if isinstance(ids_or_result, dict) else list(ids_or_result)
        q = ids_or_result.get("query") if isinstance(ids_or_result, dict) else None
        return format_context(self.chunks, ids, self.view, q)

    def tokens(self, ids):
        return sum(view_tokens(self.chunks[c], self.view) for c in ids if c in self.chunks)

    def tool_result(self, query):
        """What search_knowledge returns to the model, plus the retrieval record for the log."""
        r = self.retrieve(query)
        res = {"results": [{"text": model_text(self.chunks[c["id"]], self.view)} for c in r["chunks"]]}
        return res, r
