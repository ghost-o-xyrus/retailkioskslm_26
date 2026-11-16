"""
Objective 3, Step 10: apply the answer check to a finished run, without the model.

    python eval\\replay_verify.py results_obj3\\o3s8_4b_rag --mode shown --name o3s10v_4b_rag

The check (harness/verify.py) only reads the final reply, the cards shown and the tool results, which every run
logs, so "verify against what was shown" (O3-S10v) needs no new model run: this copies the run, applies the
check to each knowledge-path reply exactly as run_eval.py --verify-answers would, and writes a new run folder
that eval/compare_dev.py reads like any other. Waits and tokens are copied unchanged (the check takes well under
a millisecond).
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "retrieval"))
from harness import verify  # noqa: E402
from knowledge_base import load_chunks, model_text, DEFAULT_FALLBACK  # noqa: E402
from language import is_hinglish  # noqa: E402


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--mode", default="shown", choices=["shown", "cited"])
    ap.add_argument("--name", required=True, help="name of the new run folder (next to the input run)")
    a = ap.parse_args(argv)
    with open(os.path.join(a.run, "run_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    cases = {c["id"]: c for c in load_jsonl(os.path.join(ROOT, meta["eval_file"].replace("\\", "/")))}
    chunks = load_chunks()
    view = (meta.get("retrieval") or {}).get("context_view", "compact")
    fb_file = ((meta.get("retrieval") or {}).get("knowledge_base") or {}).get("fallback_file")
    fb_path = os.path.join(ROOT, fb_file) if fb_file else DEFAULT_FALLBACK
    messages = {"en": "Sorry, I don't have information about that. Would you like me to call a staff member to help?"}
    if os.path.exists(fb_path):
        with open(fb_path, encoding="utf-8") as f:
            messages = json.load(f)["messages"]
    out_dir = os.path.join(os.path.dirname(os.path.normpath(a.run)), a.name)
    os.makedirs(out_dir, exist_ok=True)
    n_checked = n_failed = n_cited = 0
    with open(os.path.join(out_dir, "cases.jsonl"), "w", encoding="utf-8") as out:
        for r in load_jsonl(os.path.join(a.run, "cases.jsonl")):
            flags = list(r.get("flags") or [])
            q = (cases.get(r["id"]) or {}).get("messages", [{}])[-1].get("content", "")
            if r.get("route") in ("store", "unclear") and r.get("final_reply") and r.get("turns") and \
                    "empty_reply_fallback" not in flags:
                ret = r.get("retrieval") or {}
                ids = [] if ret.get("fallback_applied") else list(ret.get("chunk_ids") or [])
                shown = [model_text(chunks[c], view, ret.get("query")) for c in ids if c in chunks]
                info = verify.check(r["final_reply"], q, shown, verify.tool_text(r.get("tool_calls")), a.mode)
                n_checked += 1
                r = dict(r, verify=info, final_reply=info["reply"], original_reply=r["final_reply"])
                if info["cited"]:
                    flags.append("cited")
                    n_cited += 1
                if not info["ok"]:
                    r["final_reply"] = ret.get("fallback_message") or messages["hinglish" if is_hinglish(q) else "en"]
                    flags.append("verify_failed")
                    n_failed += 1
                r["flags"] = sorted(set(flags))
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = dict(meta, name=a.name, config_label=(meta.get("config_label") or "") + f" + verify ({a.mode}, replayed)",
                verify_answers=a.mode, replayed_from=os.path.basename(os.path.normpath(a.run)))
    with open(os.path.join(out_dir, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1)
    print(f"{a.name}: {n_checked} knowledge-path replies checked, {n_failed} replaced, {n_cited} cited -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
