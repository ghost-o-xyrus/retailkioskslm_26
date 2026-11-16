"""
Build a blind rubric-scoring packet from two runs' cases.jsonl.

    python eval/rubric/build_blind_packet.py RUN_A/cases.jsonl RUN_B/cases.jsonl --out eval/rubric/stage3

Writes packet.json (no model names; replies shown as X/Y in a random order per case) and key.json (the un-blinding map,
never shown to the judge). Only test-split cases that carry a rubric are included.
"""
import argparse, json, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def trim(obj, limit=6000):
    s = json.dumps(obj, ensure_ascii=False)
    return s if len(s) <= limit else s[:limit] + " …[truncated]"


def load(path):
    recs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("repeat", 0) == 0:
                recs[r["id"]] = r
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs=2)
    ap.add_argument("--eval", default=os.path.join(ROOT, "eval", "eval_set_v1.1.jsonl"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    cases = [json.loads(l) for l in open(a.eval, encoding="utf-8")]
    cases = [c for c in cases if c["split"] == "test" and c.get("rubric")]
    runs = [load(p) for p in a.runs]
    names = [next(iter(r.values()))["run"] for r in runs]
    rng = random.Random(a.seed)
    rng.shuffle(cases)
    packet, key = [], {"runs": names, "items": {}}
    for i, c in enumerate(cases, 1):
        bid = f"C{i:03d}"
        order = [0, 1]
        rng.shuffle(order)
        replies = {}
        for label, idx in zip("XY", order):
            r = runs[idx].get(c["id"]) or {}
            replies[label] = {
                "tool_calls": [{"name": t.get("name"), "arguments": t.get("arguments"), "result": trim(t.get("result"))}
                               for t in r.get("tool_calls", [])],
                "final_reply": r.get("final_reply") or "(no reply)",
            }
        packet.append({"item": bid, "language": c["language"],
                       "conversation": [{"role": m["role"], "content": m["content"]} for m in c["messages"]],
                       "provided_information": c.get("context") or None,
                       "rubric": c["rubric"], "replies": replies})
        key["items"][bid] = {"case_id": c["id"], "category": c["category"], "X": names[order[0]], "Y": names[order[1]]}
    os.makedirs(a.out, exist_ok=True)
    json.dump(packet, open(os.path.join(a.out, "packet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(key, open(os.path.join(a.out, "key.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(packet)} items -> {a.out}")


if __name__ == "__main__":
    main()
