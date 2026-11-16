"""
Objective 3, Step 13b: speculative decoding against plain decoding, per tier.

    python eval\\compare_spec.py --prefix o3s13b_a_2b --prefix o3s13b_b_4b --out results_obj3\\_spec_step13b

Runs are named <prefix>_<set>_<config> in results_obj3 (set: rag or v12; config: none, none2, ngram-mod, ...).
"none" is plain decoding; "none2" is plain decoding again, run last, to show how far plain decoding agrees with
itself and how far the machine drifted during the session. Every case from both sets is pooled.

Per candidate, against "none":
    identical      replies exactly the same as plain decoding (greedy, temperature 0)
    writing speed  per case: generated tokens / generation time over all model requests; median ratio new / plain
                   with a bootstrap 95% interval over cases
    first word, total reply time   median per-case change with a bootstrap interval
    acceptance     accepted draft tokens / drafted tokens
    peak RAM       median per-case peak (harness measure)

Rule (written before the runs): a candidate qualifies if
    (1) its replies are identical to plain decoding at least as often as "none2" is (100% if there is no "none2"),
    (2) the median writing-speed ratio is at least 1.2,
    (3) the first word is not significantly later (the interval of the change is not wholly above 0), and
    (4) the total reply time is not significantly longer.
Among qualifiers the lowest median total reply time is chosen. MTP candidates (mtp2, mtp6) run on the Unsloth
MTP file of the same model; they qualify only if plain decoding on that file ("mtpfile") passes (1) as well. Same machine only (timing on the laptop).
"""

import argparse
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SETS = ("rag", "v12")
MIN_RATIO = 1.2


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load(run_dir):
    """{(set, id, repeat): record} for one run directory, or None when the run is missing."""
    p = os.path.join(run_dir, "cases.jsonl")
    if not os.path.exists(os.path.join(run_dir, "run_meta.json")) or not os.path.exists(p):
        return None
    with open(os.path.join(run_dir, "run_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    return meta, {(r["id"], r.get("repeat", 0)): r for r in load_jsonl(p) if not r.get("error")}


def per_case(recs):
    out = {}
    for (cid, rep), r in recs.items():
        turns = r.get("turns") or []
        n = sum(t.get("predicted_n") or 0 for t in turns)
        ms = sum(t.get("predicted_ms") or 0 for t in turns)
        m = r.get("metrics") or {}
        out[(cid, rep)] = {"reply": r.get("final_reply") or "", "speed": n / ms * 1000 if n and ms else None,
                           "first": m.get("first_visible_ms"), "total": m.get("end_to_end_ms"),
                           "drafted": sum(t.get("draft_n") or 0 for t in turns),
                           "accepted": sum(t.get("draft_n_accepted") or 0 for t in turns),
                           "ram": m.get("peak_rss_mb")}
    return out


def boot_median(d, n=4000, seed=7):
    if not d:
        return None
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choice(d) for _ in d) for _ in range(n))
    return statistics.median(d), meds[int(0.025 * n)], meds[int(0.975 * n)]


def compare(base, new):
    ids = sorted(set(base) & set(new))
    same = sum(1 for i in ids if base[i]["reply"].strip() == new[i]["reply"].strip())
    ratio = [new[i]["speed"] / base[i]["speed"] for i in ids if base[i]["speed"] and new[i]["speed"]]
    first = [(new[i]["first"] - base[i]["first"]) / 1000 for i in ids
             if base[i]["first"] is not None and new[i]["first"] is not None]
    total = [(new[i]["total"] - base[i]["total"]) / 1000 for i in ids
             if base[i]["total"] is not None and new[i]["total"] is not None]
    drafted = sum(new[i]["drafted"] for i in ids)
    rams = [new[i]["ram"] for i in ids if new[i]["ram"] is not None]
    return {"n": len(ids), "identical": same, "identical_rate": same / max(1, len(ids)),
            "ratio": boot_median(ratio), "first": boot_median(first), "total": boot_median(total),
            "acceptance": sum(new[i]["accepted"] for i in ids) / drafted if drafted else None,
            "ram": statistics.median(rams) if rams else None,
            "differing": [i[0] for i in ids if base[i]["reply"].strip() != new[i]["reply"].strip()]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", action="append", required=True)
    ap.add_argument("--results", default=os.path.join(ROOT, "results_obj3"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj3", "_spec_step13b"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    L = ["# Step 13b: speculative decoding (dev speed subset, greedy)", "",
         f"Rule: identical replies at least as often as plain decoding agrees with itself (none2); median writing-speed "
         f"ratio ≥ {MIN_RATIO}; first word and total reply time not significantly later. Lowest median total time "
         "wins.", ""]
    summary, missing = {}, []
    for pre in a.prefix:
        configs = sorted({d[len(pre) + 1:].split("_", 1)[1] for d in os.listdir(a.results)
                          if d.startswith(pre + "_") and "_" in d[len(pre) + 1:]})
        runs = {}
        for c in configs:
            pooled, meta = {}, None
            for s in SETS:
                got = load(os.path.join(a.results, f"{pre}_{s}_{c}"))
                if got is None:
                    missing.append(f"{pre}_{s}_{c}")
                    continue
                meta, recs = got
                pooled.update({(s + ":" + k[0], k[1]): v for k, v in per_case(recs).items()})
            if pooled:
                runs[c] = (meta, pooled)
        L += [f"## {pre}", ""]
        if "none" not in runs:
            L += ["No plain-decoding run (none) yet.", ""]
            continue
        machines = {(m or {}).get("machine", {}).get("label", "local") for m, _ in runs.values()}
        if len(machines) > 1:
            L += [f"Runs come from different machines ({', '.join(sorted(machines))}): timing not compared.", ""]
        base = runs["none"][1]
        ref = compare(base, runs["none2"][1]) if "none2" in runs else None
        need = ref["identical_rate"] if ref else 1.0
        L += [f"Plain decoding agrees with itself on {ref['identical']}/{ref['n']} cases." if ref else
              "No second plain run (none2): identical output must be 100%.", "",
              "| Config | Cases | Identical | Writing speed ratio [95% CI] | First word change s [95% CI] | "
              "Total change s [95% CI] | Acceptance | Peak RAM MB | Qualifies |",
              "|---|---:|---:|---|---|---|---:|---:|---|"]
        rows = []
        # Step 13b: the MTP candidates use another file of the same model; plain decoding on that file (mtpfile)
        # must give the deployed file's replies as often as plain decoding agrees with itself, or MTP is out
        file_ok = None
        if "mtpfile" in runs:
            file_ok = compare(base, runs["mtpfile"][1])["identical_rate"] >= need
        for c, (meta, recs) in runs.items():
            if c == "none":
                continue
            r = compare(base, recs)
            f = lambda t: "–" if t is None else f"{t[0]:+.2f} [{t[1]:+.2f}, {t[2]:+.2f}]"   # noqa: E731
            ok = c not in ("none2", "mtpfile") and (not c.startswith("mtp") or bool(file_ok)) and len(machines) == 1 and r["identical_rate"] >= need and r["ratio"] is not None \
                and r["ratio"][0] >= MIN_RATIO and r["first"] is not None and r["first"][1] <= 0 \
                and r["total"] is not None and r["total"][1] <= 0
            r.update(config=c, qualifies=ok)
            rows.append(r)
            rt = "–" if r["ratio"] is None else f"{r['ratio'][0]:.2f}× [{r['ratio'][1]:.2f}, {r['ratio'][2]:.2f}]"
            acc = "–" if r["acceptance"] is None else f"{r['acceptance']:.0%}"
            ram = "–" if r["ram"] is None else str(round(r["ram"]))
            verdict = "(reference)" if c == "none2" else \
                (("(file check: same replies)" if file_ok else "(file check: different replies)") if c == "mtpfile"
                 else ("yes" if ok else "no"))
            L.append(f"| {c} | {r['n']} | {r['identical']} ({r['identical_rate']:.0%}) | {rt} | {f(r['first'])} | "
                     f"{f(r['total'])} | {acc} | {ram} | {verdict} |")
        q = [r for r in rows if r["qualifies"]]
        choice = min(q, key=lambda r: r["total"][0])["config"] if q else None
        L += ["", f"**Chosen: {choice}**" if choice else "**No candidate qualifies: plain decoding stays.**", ""]
        for r in rows:
            if r["differing"] and r["config"] != "none2":   # mtpfile listed too: where the other file differs
                L.append(f"- {r['config']}: replies differ on {', '.join(r['differing'][:12])}"
                         + (" ..." if len(r["differing"]) > 12 else ""))
        L.append("")
        summary[pre] = {"choice": choice, "rows": rows, "self_agreement": ref}
    if missing:
        L += ["## Not compared", "", "No finished results yet (run the plan first; it resumes, and a server that "
              "would not start shows as failed in the plan summary):", ""] + [f"- {m}" for m in missing]
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
