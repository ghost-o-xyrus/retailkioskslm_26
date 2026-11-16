"""
Objective 3, Step 6: score simulated discovery dialogues (harness run_eval.py --dialogues).

    python eval\\score_dialogues.py results_obj3\\o3s6d_* --out results_obj3\\_dialogues_step6
    python eval\\score_dialogues.py ... --pair results_obj3\\o3s6d_2b_s5h results_obj3\\o3s6d_2b_s6
    python eval\\score_dialogues.py ... --packet results_obj3\\o3s6d_2b_s6 results_obj3\\o3s6d_2b_s6m

Per run (dialogue = one hidden profile, up to 4 kiosk turns, ends when search results are shown):
  recommended        dialogues that reached a recommendation
  questions          kiosk turns before the recommendation
  slots known        of recipient, budget, occasion, strap: how many the customer had revealed when the kiosk
                     recommended (target: at least 2 in at least 85% of dialogues)
  fit                share of shown watches that satisfy every constraint the customer had revealed (budget within
                     5%, gender, style for the occasion, strap); target >= 90%. "fit, full profile" checks the whole
                     hidden profile, including what the kiosk never asked.
  speed              model requests per dialogue, median first-word wait per kiosk turn, kiosk time to recommendation
--pair BASE NEW (repeatable): paired differences in recommended rate and fit, with bootstrap intervals.
--packet A B: a blind A/B packet of the kiosk's slot questions in the same dialogues (first question of each), for
              the 1-5 rubric (natural, asks for what is missing, short). Writes packet.csv and key.json.
"""

import argparse
import csv
import glob
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import score as S  # noqa: E402

GENDER_OK = {"men": {"men", "unisex"}, "women": {"women", "unisex"}, "kids": {"kids"}}
KEY_SLOTS = ("recipient", "budget", "occasion", "strap")


def load(run_dir):
    with open(os.path.join(run_dir, "run_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    recs = {}
    with open(os.path.join(run_dir, "cases.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if not r.get("error") and r.get("dialogue"):
                recs[r["id"]] = r
    return meta, recs


def profiles(path):
    with open(path, encoding="utf-8") as f:
        return {p["id"]: p for p in map(json.loads, f)}


GENDERLESS = {"en": {"self_m", "self_f"}, "hinglish": {"self_m", "self_f", "friend_m"}}


def gender_revealed(p, revealed):
    """The customer said something that fixes the gender: "my wife", "Papa"... but not "myself" or "Dost"; a son
    or daughter fixes it only once the age is known (kids' watches at 12 or under)."""
    if "recipient" not in revealed or p["recipient"] in GENDERLESS[p["language"]]:
        return False
    if p["recipient"] in ("son", "daughter"):
        return "age" in revealed
    return True


def misfits(row, p, revealed):
    """Constraints the customer had stated that this shown watch breaks."""
    bad = []
    if "budget" in revealed and row.get("mrp") is not None and row["mrp"] > 1.05 * p["budget"]:
        bad.append("budget")
    if gender_revealed(p, revealed) and row.get("gender") not in GENDER_OK.get(p["gender"], {row.get("gender")}):
        bad.append("gender")
    if "occasion" in revealed and p["gender"] != "kids" and row.get("style") not in p["styles"]:
        bad.append("style")
    if "strap" in revealed and p["strap"] != "none" and p["strap"] not in (row.get("strap") or ""):
        bad.append("strap")
    return bad


def fits(row, p, revealed):
    return not misfits(row, p, revealed)


def score_run(run_dir, prof):
    meta, recs = load(run_dir)
    out = {}
    for pid, r in recs.items():
        p = prof[pid]
        d = r["dialogue"]
        k = d.get("recommended_at")
        rows = []
        if k is not None:
            t = d["turns"][k]
            srch = [c for c in t["tool_calls"] if c["name"] == "search_catalogue" and (c.get("result") or {}).get("results")]
            rows = srch[-1]["result"]["results"] if srch else []
        revealed = set(d.get("revealed_at_recommendation") or [])
        firsts = [x for x in r["metrics"].get("first_visible_ms_per_turn") or [] if x is not None]
        disc = (d["turns"][k].get("discovery") or {}) if k is not None else {}
        reasons = {}
        for x in rows:
            for b in misfits(x, p, revealed):
                reasons[b] = reasons.get(b, 0) + 1
        out[pid] = {
            "misfit_reasons": reasons, "relaxed": disc.get("relaxed"), "search_args": disc.get("search_args"),
            "revealed": sorted(revealed), "recipient": p["recipient"], "shown": [x.get("product_id") for x in rows],
            "recommended": k is not None, "questions": k if k is not None else d["kiosk_turns"],
            "slots_known": len(revealed & set(KEY_SLOTS)) if k is not None else None,
            "fit": (sum(fits(x, p, revealed) for x in rows) / len(rows)) if rows else None,
            "fit_full": (sum(fits(x, p, set(KEY_SLOTS) | {"age"}) for x in rows) / len(rows)) if rows else None,
            "model_requests": r["metrics"].get("model_requests"), "first_word_ms": firsts,
            "kiosk_ms": r["metrics"].get("end_to_end_ms"), "language": p["language"], "opening": p["opening"],
            "first_question": next((t["kiosk"] for t in d["turns"] if not any(
                c["name"] == "search_catalogue" for c in t["tool_calls"])), None),
        }
    return meta, out


def summary(name, meta, res):
    n = len(res)
    rec = [v for v in res.values() if v["recommended"]]
    fits_ = [v["fit"] for v in rec if v["fit"] is not None]
    full = [v["fit_full"] for v in rec if v["fit_full"] is not None]
    firsts = [x for v in res.values() for x in v["first_word_ms"]]
    return {"run": name, "model": meta.get("model"), "config": meta.get("config_label"), "dialogues": n,
            "recommended": len(rec) / n if n else None,
            "questions_mean": statistics.mean(v["questions"] for v in rec) if rec else None,
            "questions_max": max((v["questions"] for v in rec), default=None),
            "slots2_share": sum(1 for v in rec if v["slots_known"] >= 2) / len(rec) if rec else None,
            "fit_mean": statistics.mean(fits_) if fits_ else None,
            "fit_all_share": sum(1 for x in fits_ if x == 1) / len(fits_) if fits_ else None,
            "fit_full_mean": statistics.mean(full) if full else None,
            "model_requests_mean": statistics.mean(v["model_requests"] for v in res.values()) if n else None,
            "first_word_p50_s": statistics.median(firsts) / 1000 if firsts else None,
            "kiosk_s_mean": statistics.mean(v["kiosk_ms"] for v in res.values()) / 1000 if n else None}


def pct(x):
    return "–" if x is None else f"{100 * x:.0f}%"


def boot(a, b, n=4000, seed=0):
    rng = random.Random(seed)
    idx = list(range(len(a)))
    ds = sorted(sum(b[i] - a[i] for i in (rng.choice(idx) for _ in idx)) / len(idx) for _ in range(n))
    return sum(y - x for x, y in zip(a, b)) / len(a), ds[int(0.025 * n)], ds[int(0.975 * n) - 1]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--profiles", default=os.path.join(HERE, "o3_dialogues.jsonl"))
    ap.add_argument("--pair", nargs=2, action="append", default=[], metavar=("BASE", "NEW"))
    ap.add_argument("--packet", nargs=2, default=None, metavar=("A", "B"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj3", "_dialogues"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    prof = profiles(a.profiles)
    dirs = sorted({d for p in a.runs for d in glob.glob(p) if os.path.exists(os.path.join(d, "cases.jsonl"))})
    scored = {}
    for d in dirs:
        meta, res = score_run(d, prof)
        if res:
            scored[os.path.basename(os.path.normpath(d))] = (meta, res)
    L = ["# Simulated discovery dialogues (Objective 3, Step 6)", "",
         "Targets: at least 2 of 4 slots known before the recommendation in at least 85% of dialogues; at most 2 "
         "questions; at least 90% of shown watches fit what the customer said.", "",
         "| Run | Model | Dialogues | Recommended | Questions (mean / max) | ≥2 slots known | Fit (mean) "
         "| All shown fit | Fit, full profile | Model requests | First word p50 | Kiosk time |",
         "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    sums = {}
    for name, (meta, res) in scored.items():
        s = summary(name, meta, res)
        sums[name] = s
        qm = "–" if s["questions_mean"] is None else f"{s['questions_mean']:.2f}"
        fw = "–" if s["first_word_p50_s"] is None else f"{s['first_word_p50_s']:.1f} s"
        L.append(f"| {name} | {s['model']} | {s['dialogues']} | {pct(s['recommended'])} | {qm} / {s['questions_max']} "
                 f"| {pct(s['slots2_share'])} | {pct(s['fit_mean'])} | {pct(s['fit_all_share'])} | {pct(s['fit_full_mean'])} "
                 f"| {s['model_requests_mean']:.2f} | {fw} | {s['kiosk_s_mean']:.1f} s |")
    if a.pair:
        L += ["", "## Paired comparisons (same dialogues)", "",
              "| Base | New | Dialogues | Recommended: new − base [95% CI] | Fit: new − base [95% CI] (both recommended) |",
              "|---|---|---:|---|---|"]
        for b, n in a.pair:
            bn, nn = os.path.basename(os.path.normpath(b)), os.path.basename(os.path.normpath(n))
            if bn not in scored or nn not in scored:
                continue
            B, N = scored[bn][1], scored[nn][1]
            ids = sorted(set(B) & set(N))
            d1 = boot([int(B[i]["recommended"]) for i in ids], [int(N[i]["recommended"]) for i in ids])
            both = [i for i in ids if B[i]["fit"] is not None and N[i]["fit"] is not None]
            d2 = boot([B[i]["fit"] for i in both], [N[i]["fit"] for i in both]) if both else None
            L.append(f"| {bn} | {nn} | {len(ids)} | {100 * d1[0]:+.1f} [{100 * d1[1]:+.1f}, {100 * d1[2]:+.1f}] | "
                     + (f"{100 * d2[0]:+.1f} [{100 * d2[1]:+.1f}, {100 * d2[2]:+.1f}] (n={len(both)})" if d2 else "–") + " |")
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "dialogues.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["run", "dialogue", "language", "opening", "recipient", "recommended", "questions", "revealed",
                    "search_args", "relaxed", "shown", "fit", "misfit_reasons", "first_question"])
        for name, (meta, res) in scored.items():
            for i, v in sorted(res.items()):
                w.writerow([name, i, v["language"], v["opening"], v["recipient"], v["recommended"], v["questions"],
                            "|".join(v["revealed"]), json.dumps(v["search_args"], ensure_ascii=False),
                            "|".join(v["relaxed"] or []), "|".join(v["shown"]),
                            "" if v["fit"] is None else round(v["fit"], 2), json.dumps(v["misfit_reasons"]),
                            (v["first_question"] or "")[:200]])
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(sums, f, indent=1)
    if a.packet:
        an, bn = (os.path.basename(os.path.normpath(x)) for x in a.packet)
        A, B = scored[an][1], scored[bn][1]
        rng = random.Random(7)
        rows, key = [], {}
        for i in sorted(set(A) & set(B)):
            qa, qb = A[i]["first_question"], B[i]["first_question"]
            if not qa or not qb:
                continue
            flip = rng.random() < 0.5
            item = f"Q{len(rows) + 1:03d}"
            key[item] = {"dialogue": i, "first": bn if flip else an, "second": an if flip else bn}
            rows.append({"item": item, "customer": prof[i]["messages"][0]["content"],
                         "reply_1": qb if flip else qa, "reply_2": qa if flip else qb,
                         "score_1 (1-5)": "", "score_2 (1-5)": ""})
        with open(os.path.join(a.out, "packet.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["item"])
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(a.out, "key.json"), "w", encoding="utf-8") as f:
            json.dump(key, f, indent=1)
        print(f"Packet: {len(rows)} pairs -> {os.path.join(a.out, 'packet.csv')}")
    print(f"Wrote {os.path.join(a.out, 'report.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
