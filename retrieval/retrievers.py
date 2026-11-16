"""
Retrievers for the kiosk corpus (Objective 2). Used by the Step 5 benchmark and, later, by the assistant.

    BM25Retriever      keyword search, no dependencies
    DenseRetriever     sentence-transformers embedding model, exact cosine search in numpy
    HybridRetriever    reciprocal-rank fusion of BM25 and a dense retriever
    Reranker           cross-encoder that re-scores the top candidates of any retriever

Every retriever returns [(chunk_id, score), ...] best first. At 812 chunks an exact search over a numpy
matrix takes well under a millisecond, so no vector database (FAISS, Chroma) is needed at this size.
"""

import math
import re
from collections import Counter

STOPWORDS = set("""a an the is are was were be been am do does did of to in on at for from with by and or but if
then so as it its this that these those there here i me my you your we our he she his her they them their what
which who whom how when where why can could would should will shall may might must have has had any some please
tell show give get want need like about into than also just""".split())

# The Hinglish function words customers mix in; content words (watch, strap, kitni...) are kept.
HINGLISH_STOP = set("ka ki ke ko hai hain kya mein me se pe par aur ya toh bhi wala wali ho".split())


def tokenize(text):
    """Lowercase; drop possessive 's; keep letters+digits runs (so SKU codes like 1003sl01 stay whole);
    remove stopwords; fold simple English plurals (watches -> watch, batteries -> battery)."""
    text = text.lower().replace("'s", " ").replace("’s", " ")
    out = []
    for w in re.findall(r"[a-z0-9]+", text):
        if w in STOPWORDS or w in HINGLISH_STOP or len(w) == 1:
            continue
        if len(w) > 4 and not w[-2].isdigit():
            if w.endswith(("ches", "shes", "xes", "sses")):
                w = w[:-2]                      # watches -> watch, boxes -> box, glasses -> glass
            elif w.endswith("ies") and len(w) > 5:
                w = w[:-3] + "y"                # batteries -> battery
            elif w.endswith("s") and not w.endswith(("ss", "us", "is")):
                w = w[:-1]                      # straps -> strap (but glass, bonus, analysis stay)
        out.append(w)
    return out


class BM25Retriever:
    name = "bm25"

    def __init__(self, chunks, k1=1.2, b=0.75):
        self.ids = [c["id"] for c in chunks]
        self.k1, self.b = k1, b
        self.tfs = [Counter(tokenize(c["text"])) for c in chunks]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.avg = sum(self.lens) / len(self.lens)
        df = Counter(w for tf in self.tfs for w in tf)
        n = len(chunks)
        self.idf = {w: math.log(1 + (n - d + 0.5) / (d + 0.5)) for w, d in df.items()}
        self.postings = {}
        for i, tf in enumerate(self.tfs):
            for w in tf:
                self.postings.setdefault(w, []).append(i)

    def search(self, query, k=10):
        scores = {}
        for w in set(tokenize(query)):
            idf = self.idf.get(w)
            if idf is None:
                continue
            for i in self.postings[w]:
                tf = self.tfs[i][w]
                denom = tf + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg)
                scores[i] = scores.get(i, 0.0) + idf * tf * (self.k1 + 1) / denom
        top = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
        return [(self.ids[i], s) for i, s in top]


# Query/passage prefixes each model was trained with.
PREFIXES = {
    "BAAI/bge-small-en-v1.5": ("Represent this sentence for searching relevant passages: ", ""),
    "BAAI/bge-base-en-v1.5": ("Represent this sentence for searching relevant passages: ", ""),
    "intfloat/multilingual-e5-small": ("query: ", "passage: "),
}


class DenseRetriever:
    def __init__(self, chunks, model_name, encoder=None, batch_size=16):
        """`encoder` lets tests pass a stand-in with an .encode(texts, ...) method."""
        import numpy as np
        self.np = np
        self.model_name = model_name
        self.name = model_name.split("/")[-1]
        if encoder is None:
            from sentence_transformers import SentenceTransformer
            encoder = SentenceTransformer(model_name, device="cpu")
        self.encoder = encoder
        self.q_prefix, self.p_prefix = PREFIXES.get(model_name, ("", ""))
        self.ids = [c["id"] for c in chunks]
        self.matrix = self._encode([self.p_prefix + c["text"] for c in chunks], batch_size)

    def _encode(self, texts, batch_size=16):
        v = self.encoder.encode(texts, batch_size=batch_size, normalize_embeddings=True,
                                convert_to_numpy=True, show_progress_bar=False)
        return self.np.asarray(v, dtype="float32")

    def encode_query(self, query):
        return self._encode([self.q_prefix + query], 1)[0]

    def search_vector(self, qv, k=10):
        sims = self.matrix @ qv
        top = self.np.argsort(-sims)[:k]
        return [(self.ids[i], float(sims[i])) for i in top]

    def search(self, query, k=10):
        return self.search_vector(self.encode_query(query), k)


class HybridRetriever:
    """Reciprocal-rank fusion: score = sum over retrievers of 1 / (rrf_k + rank). rrf_k = 60 is the usual default."""

    def __init__(self, bm25, dense, depth=50, rrf_k=60):
        self.bm25, self.dense, self.depth, self.rrf_k = bm25, dense, depth, rrf_k
        self.name = f"hybrid-{dense.name}"

    @staticmethod
    def fuse(rankings, k, rrf_k=60):
        scores = {}
        for ranking in rankings:
            for rank, (cid, _) in enumerate(ranking, 1):
                scores[cid] = scores.get(cid, 0.0) + 1.0 / (rrf_k + rank)
        return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:k]

    def search(self, query, k=10, dense_hits=None):
        d = dense_hits if dense_hits is not None else self.dense.search(query, self.depth)
        return self.fuse([self.bm25.search(query, self.depth), d], k, self.rrf_k)


class Reranker:
    """Cross-encoder re-scoring of the top `depth` candidates. Scores are cached per (query, chunk)."""

    def __init__(self, chunks, model_name="BAAI/bge-reranker-base", model=None, max_length=512, batch_size=16):
        if model is None:
            from sentence_transformers import CrossEncoder
            model = CrossEncoder(model_name, max_length=max_length, device="cpu")
        self.model, self.batch_size = model, batch_size
        self.name = model_name.split("/")[-1]
        self.text = {c["id"]: c["text"] for c in chunks}
        self.cache = {}

    def score(self, query, ids):
        todo = [cid for cid in ids if (query, cid) not in self.cache]
        if todo:
            vals = self.model.predict([(query, self.text[cid]) for cid in todo], batch_size=self.batch_size,
                                      show_progress_bar=False)
            for cid, v in zip(todo, vals):
                self.cache[(query, cid)] = float(v)
        return [(cid, self.cache[(query, cid)]) for cid in ids]

    def rerank(self, query, hits, k=10):
        scored = self.score(query, [cid for cid, _ in hits])
        return sorted(scored, key=lambda kv: (-kv[1], kv[0]))[:k]
