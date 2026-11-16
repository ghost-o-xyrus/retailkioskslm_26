"""
Objective 3, Step 12: run both retrieval models with the OpenVINO runtime and the `tokenizers` library only:
no PyTorch, no transformers, no sentence-transformers at run time (they cost RAM and start-up time).

    OVEncoder(folder, threads)        bge-small-en-v1.5: CLS pooling, normalised (as sentence-transformers does)
    OVCrossEncoder(folder, threads)   ms-marco-MiniLM-L-6-v2 re-ranker: the raw score (logit)

Both read a folder written by retrieval/export_openvino.py (openvino/*.xml + tokenizer.json). `int8=True` loads the
8-bit quantised re-ranker from the same folder. The interfaces match what DenseRetriever and KnowledgeBase call:
encode(texts, batch_size, normalize_embeddings, convert_to_numpy, show_progress_bar) and
predict(pairs, batch_size, show_progress_bar).
"""

import glob
import os

import numpy as np


def _find_xml(folder, int8=False):
    xs = sorted(glob.glob(os.path.join(folder, "**", "*.xml"), recursive=True))
    if int8 in ("static", "weights"):          # Step 12: retrieval/quantize_reranker.py
        xs = [x for x in xs if os.path.basename(x) == f"openvino_model_int8_{int8}.xml"]
    elif int8:
        xs = [x for x in xs if "int8" in os.path.basename(x) or "qint8" in os.path.basename(x)]
    else:
        xs = [x for x in xs if "int8" not in os.path.basename(x)]
    if not xs:
        have = sorted(os.path.relpath(p, folder) for p in glob.glob(os.path.join(folder, "**", "*"), recursive=True))[:20] \
            if os.path.isdir(folder) else "folder missing"
        raise FileNotFoundError(f"no {'8-bit ' if int8 else ''}OpenVINO model in {folder} "
                                f"(run retrieval\\export_openvino.py first). Found: {have}")
    return xs[0]


def _compile(xml, threads):
    import openvino as ov
    core = ov.Core()
    return core.compile_model(core.read_model(xml), "CPU",
                              {"INFERENCE_NUM_THREADS": int(threads), "PERFORMANCE_HINT": "LATENCY"})


def _tokenizer(folder, max_length):
    from tokenizers import Tokenizer
    path = os.path.join(folder, "tokenizer.json")
    if not os.path.exists(path):
        path = next(iter(sorted(glob.glob(os.path.join(folder, "**", "tokenizer.json"), recursive=True))), path)
    tok = Tokenizer.from_file(path)
    tok.enable_truncation(max_length=max_length, strategy="longest_first")
    pad = tok.token_to_id("[PAD]")
    tok.enable_padding(pad_id=0 if pad is None else pad, pad_token="[PAD]")
    return tok


class _Model:
    def __init__(self, folder, threads=4, max_length=256, int8=False):
        self.xml = _find_xml(folder, int8)
        self.model = _compile(self.xml, threads)
        self.inputs = {i.get_any_name() for i in self.model.inputs}
        self.tok = _tokenizer(folder, max_length)

    def _run(self, encs):
        feed = {"input_ids": np.array([e.ids for e in encs], dtype=np.int64),
                "attention_mask": np.array([e.attention_mask for e in encs], dtype=np.int64)}
        if "token_type_ids" in self.inputs:
            feed["token_type_ids"] = np.array([e.type_ids for e in encs], dtype=np.int64)
        out = self.model(feed)
        return out[self.model.output(0)], feed["attention_mask"]


class OVEncoder(_Model):
    def __init__(self, folder, threads=4, max_length=512):
        super().__init__(folder, threads, max_length)

    def encode(self, texts, batch_size=16, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False):
        out = []
        for i in range(0, len(texts), batch_size):
            hidden, _ = self._run(self.tok.encode_batch(list(texts[i:i + batch_size])))
            v = hidden[:, 0, :]                                    # CLS pooling (bge)
            if normalize_embeddings:
                v = v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-12)
            out.append(v.astype("float32"))
        return np.concatenate(out) if out else np.zeros((0, 384), dtype="float32")


class OVCrossEncoder(_Model):
    def predict(self, pairs, batch_size=32, show_progress_bar=False):
        scores = []
        for i in range(0, len(pairs), batch_size):
            logits, _ = self._run(self.tok.encode_batch([(q, p) for q, p in pairs[i:i + batch_size]]))
            scores.extend(np.asarray(logits).reshape(len(logits), -1)[:, 0].tolist())
        return np.array(scores, dtype="float32")
