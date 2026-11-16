"""
Objective 3: the paired dev comparison every step's keep rule uses.

    python eval\\compare_dev.py --pair results_obj3\\o3s1_4b_rag_b0 results_obj3\\o3s2_4b_rag_s2 ^
                               --pair results_obj3\\o3s1_4b_v11_b0 results_obj3\\o3s2_4b_v12_s2 ^
                               --noise results_obj3\\_noise_floor\\noise.json --out results_obj3\\_compare_step2

Each --pair is BASE then NEW: two runs of the same model on the same cases. Scored with the automatic checks:
  retrieval questions (rag_cases.jsonl)   score_rag's check, reported for all checked questions, answerable only,
                                          and unanswerable/near-miss only
  tool cases (eval_set v1.1 / v1.2)       score.py pass/fail on tool-mode cases (--credit-shown-cards optional)
Per pair: rates, NEW - BASE in points with a paired bootstrap 95% CI, exact McNemar p, the noise bound for that
model and set (from eval/noise_floor.py, scaled to the number of cases), and the verdict:
  better / worse   |difference| > noise bound AND the bootstrap interval excludes 0
  tie              otherwise
Also: mean model rounds, mean prompt tokens read, and median wait to the first word, from the same records.
Repeat 0 only. Writes <out>/report.md and <out>/compare.json.
"""

import argparse
import json
import math
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import score as S          # noqa: E402
sys.path.insert(0, ROOT)
from harness import verify as VF  # noqa: E402
import score_rag as SR     # noqa: E402


def load_jsonl(p):
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:   # a line cut off when a run was stopped; the case was rerun
                    print(f"note: skipped an unreadable line in {p}", file=sys.stderr)
    return out


def load_run(d):
    with open(os.path.join(d, "run_meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    recs = {}
    for r in load_jsonl(os.path.join(d, "cases.jsonl")):
        if r.get("repeat", 0) == 0:
            recs[r["id"]] = r   # last record wins (resumed runs)
    return meta, recs


def eval_cases(meta, cache):
    ef = os.path.join(ROOT, meta.get("eval_file", "").replace("\\", "/"))
    if ef not in cache:
        cache[ef] = {c["id"]: c for c in load_jsonl(ef)}
    return ef, cache[ef]


def outcomes(meta, recs, cases, kind, chunks, credit):
    """Dict of subset -> {case id: 0/1}."""
    out = {}
    for cid, r in recs.items():
        if r.get("error") or cid not in cases:
            continue
        c = cases[cid]
        if kind == "rag":
            a = SR.auto(c, SR.scored_reply(r), chunks)
            if not a["checked"]:
                continue
            v = int(bool(a["correct"]))
            out.setdefault("all checked", {})[cid] = v
            sub = "answerable" if c["expected"]["behaviour"] == "answer" else "unanswerable / near-miss"
            out.setdefault(sub, {})[cid] = v
            if c.get("set") == "followup":            # Step 11: by follow-up type
                out.setdefault(f"type: {c['subcategory']}", {})[cid] = v
            _extra(out, c, cid, v)
        else:
            if c["mode"] != "tools":
                continue
            out.setdefault("tool cases", {})[cid] = int(bool(S.score_case(c, r, credit)["passed"]))
            out.setdefault(f"tool cases: {c['category']}", {})[cid] = out["tool cases"][cid]
            _extra(out, c, cid, out["tool cases"][cid])
    return out


ALL_HINGLISH = False          # Objective 4, Step 6 (--all-hinglish): the Hinglish subset on every set, dev included


def _extra(out, c, cid, v):
    """Step 14: results by origin (fresh / held-out) and for Hinglish, where the cases say so."""
    if c.get("o3t_origin"):
        out.setdefault(f"origin: {c['o3t_origin']}", {})[cid] = v
    if c.get("language") in ("hinglish", "hindi") and (ALL_HINGLISH or c.get("set") in ("o3t", "followup")):
        out.setdefault("language: hinglish", {})[cid] = v


def _calls(r):
    return "; ".join(f"{'H:' if c.get('by') == 'harness' else ''}{c['name']}({json.dumps(c.get('arguments'), ensure_ascii=False)[:120]})"
                     for c in r.get("tool_calls") or [])


def speed(recs):
    rs = [r for r in recs.values() if not r.get("error")]
    rounds = [len(r.get("turns") or []) for r in rs]
    read = [sum(t.get("prompt_n") or 0 for t in r.get("turns") or []) for r in rs]
    first = [(r.get("metrics") or {}).get("first_visible_ms") for r in rs]
    first = [x for x in first if x is not None]
    calls = [c for r in rs for c in r.get("tool_calls") or []]
    out_tok = [c.get("result_tokens") for c in calls if c.get("result_tokens") is not None]
    empty = sum(1 for r in rs if not (r.get("final_reply") or "").strip() or "empty_reply_fallback" in (r.get("flags") or []))
    return {"rounds": statistics.mean(rounds) if rounds else None, "tok_read": statistics.mean(read) if read else None,
            "first_p50_s": statistics.median(first) / 1000 if first else None,
            "tok_per_tool_output": statistics.mean(out_tok) if out_tok else None, "empty_replies": empty,
            "round_limit": sum(1 for r in rs if "max_rounds_reached" in (r.get("flags") or [])),
            "harness_calls": sum(1 for c in calls if c.get("by") == "harness"), "calls": len(calls)}


STAFF_WORDS = re.compile(r"(staff|store team|colleague|someone from the store|sales ?person|team member)", re.I)
# Step 8 split: a promise that someone is coming (a violation without a call) vs an offer asked as a question
STAFF_PROMISE = re.compile(r"(i've asked|i have asked|i've called|i have called|i've notified|i have notified|"
                           r"i've informed|will be with you|is coming|are coming|will come over|on (their|his|her) way|"
                           r"will be at the kiosk|bula (diya|raha|rahi)|bulaya)", re.I)
STAFF_QUESTION = re.compile(r"[^.!?\n]*(staff|store team|colleague|team member|sales ?person)[^.!?\n]*\?", re.I)


def unsupported_gold(recs, cases, chunks):
    """Step 10's independent measure: knowledge-path replies with a detail found neither in the eval case's gold or
    reference cards nor in the turn's tool results (whatever the model was shown)."""
    n = bad = 0
    for r in recs.values():
        c = cases.get(r["id"]) or {}
        e = c.get("expected") or {}
        if r.get("error") or r.get("route") not in ("store", "unclear") or "gold_ids" not in e:
            continue
        reply = SR.scored_reply(r) or ""
        if not reply.strip():
            continue
        ref = "\n".join(chunks[g]["text"] for g in set(e.get("gold_ids") or []) | set(e.get("oracle_ids") or [])
                        if g in chunks)
        n += 1
        bad += bool(VF.unsupported(reply, c["messages"][-1]["content"], ref + "\n" + VF.tool_text(r.get("tool_calls"))))
    return bad, n


def discipline(recs, cases):
    """Step 7: printed tool calls and staff discipline, counted over the run."""
    rs = [r for r in recs.values() if not r.get("error")]
    fl = lambda r: set(r.get("flags") or [])   # noqa: E731
    out = {"printed": sum(1 for r in rs if fl(r) & {"tool_call_as_text", "tool_text_seen"}),
           "printed_shown_fallback": sum(1 for r in rs if "tool_text_replaced" in fl(r)),
           "printed_stripped": sum(1 for r in rs if "tool_text_stripped" in fl(r)),
           "printed_recovered": sum(1 for r in rs if "tool_text_recovered" in fl(r)),
           "model_staff_calls": 0, "staff_on_answerable": 0, "offer_no_call": 0, "harness_staff_after": 0,
           "promised_no_call": 0, "offer_question": 0,
           "entity_replies": sum(1 for r in rs if any(f.startswith("entity_") for f in fl(r))),
           "fallback_replies": sum(1 for r in rs if "fallback_refused" in fl(r)),
           "staff_check_notes": sum(1 for r in rs for c in r.get("tool_calls") or [] if c.get("guard") == "staff_check"),
           "staff_checked_then_answered": 0,
           "verify_failed": sum(1 for r in rs if "verify_failed" in fl(r)),
           "cited": sum(1 for r in rs if "cited" in fl(r))}
    for r in rs:
        staff = [c for c in r.get("tool_calls") or [] if c.get("name") == "call_staff"]
        model_staff = [c for c in staff if c.get("by") != "harness" and c.get("guard") != "staff_check"]
        out["model_staff_calls"] += len(model_staff)
        exp = (cases.get(r["id"]) or {}).get("expected") or {}
        if model_staff and exp.get("behaviour") == "answer":
            out["staff_on_answerable"] += 1
        reply = r.get("final_reply") or ""
        real_staff = [c for c in staff if c.get("guard") != "staff_check"]
        if not real_staff and STAFF_WORDS.search(reply) and "empty_reply_fallback" not in fl(r):
            out["offer_no_call"] += 1
            if STAFF_PROMISE.search(reply):
                out["promised_no_call"] += 1
            elif STAFF_QUESTION.search(reply):
                out["offer_question"] += 1
        if any(c.get("guard") == "staff_check" for c in staff) and not real_staff:
            out["staff_checked_then_answered"] += 1
        if "harness_staff_after_answer" in fl(r):
            out["harness_staff_after"] += 1
    return out


def per_case_times(run_dir):
    """{case id: (median first-word ms, median total ms)} over every repeat (Step 13 in-place timing)."""
    by = {}
    for r in load_jsonl(os.path.join(run_dir, "cases.jsonl")):
        m = r.get("metrics") or {}
        if r.get("error") or m.get("first_visible_ms") is None:
            continue
        by.setdefault(r["id"], []).append((m["first_visible_ms"], m.get("end_to_end_ms") or m["first_visible_ms"]))
    return {k: (statistics.median(a for a, _ in v), statistics.median(b for _, b in v)) for k, v in by.items()}


def paired_median_diff(a, b, n=4000, seed=7):
    """Median of per-case differences (b - a) in seconds, with a bootstrap 95% interval over cases."""
    import random
    ids = sorted(set(a) & set(b))
    if not ids:
        return None
    d = [(b[i] - a[i]) / 1000 for i in ids]
    rng = random.Random(seed)
    meds = sorted(statistics.median(rng.choice(d) for _ in d) for _ in range(n))
    return statistics.median(d), meds[int(0.025 * n)], meds[int(0.975 * n)], len(ids)


def noise_bound(noise, model, kind, n):
    ds = [v["discordance"] for v in noise.values() if v.get("model") == model and v.get("kind") == kind]
    if not ds or not n:
        return None
    return 196 * math.sqrt(max(ds) / n)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", nargs=2, action="append", required=True, metavar=("BASE", "NEW"))
    ap.add_argument("--noise", default=None, help="noise.json from eval/noise_floor.py")
    ap.add_argument("--credit-shown-cards", action="store_true")
    ap.add_argument("--all-hinglish", action="store_true", help="Hinglish subset on every set (Objective 4, Step 6)")
    ap.add_argument("--out", default=os.path.join(ROOT, "results_obj3", "_compare"))
    a = ap.parse_args(argv)
    global ALL_HINGLISH
    ALL_HINGLISH = a.all_hinglish
    os.makedirs(a.out, exist_ok=True)
    noise = {}
    if a.noise:
        with open(a.noise, encoding="utf-8") as f:
            noise = json.load(f)
    chunks = {c["id"]: c for c in load_jsonl(os.path.join(ROOT, "knowledge", "corpus.jsonl"))}
    cache, rows, speeds, changed = {}, [], [], []
    missing = []
    for base_dir, new_dir in a.pair:
        gone = [d for d in (base_dir, new_dir) if not os.path.exists(os.path.join(d, "run_meta.json"))]
        if gone:              # a run not made yet (or stopped before it wrote anything): skip the pair, say so
            missing += [d for d in gone if d not in missing]
            print(f"skipped pair {base_dir} -> {new_dir}: no finished run in {', '.join(gone)}", file=sys.stderr)
            continue
        bm, br = load_run(base_dir)
        nm, nr = load_run(new_dir)
        ef, cases = eval_cases(bm, cache)
        _, cases_new = eval_cases(nm, cache)
        kind = "rag" if os.path.basename(ef).startswith("rag_") else "tools"   # rag_cases, rag_followups
        ob = outcomes(bm, br, cases, kind, chunks, a.credit_shown_cards)
        on = outcomes(nm, nr, cases_new, kind, chunks, a.credit_shown_cards)
        bname, nname = os.path.basename(os.path.normpath(base_dir)), os.path.basename(os.path.normpath(new_dir))
        bml, nml = (bm.get("machine") or {}).get("label", "local"), (nm.get("machine") or {}).get("label", "local")
        speeds.append({"base": bname, "new": nname, "base_speed": speed(br), "new_speed": speed(nr),
                       "machines": [bml, nml],
                       "base_disc": discipline(br, cases), "new_disc": discipline(nr, cases_new),
                       "base_unsup": unsupported_gold(br, cases, chunks) if kind == "rag" else None,
                       "new_unsup": unsupported_gold(nr, cases_new, chunks) if kind == "rag" else None})
        for sub in sorted(ob, key=lambda s: (":" in s, s)):
            ids = sorted(set(ob[sub]) & set(on.get(sub, {})))
            if not ids:
                continue
            x = [ob[sub][i] for i in ids]
            y = [on[sub][i] for i in ids]
            d, lo, hi = S.paired_bootstrap(y, x)
            b = sum(1 for i, j in zip(x, y) if i == 1 and j == 0)
            c = sum(1 for i, j in zip(x, y) if i == 0 and j == 1)
            p = S.mcnemar_exact(b, c)
            nb = noise_bound(noise, bm.get("model"), kind, len(ids))
            sig = lo > 0 or hi < 0
            beyond = nb is None or abs(100 * d) > nb
            verdict = ("better" if d > 0 else "worse") if (sig and beyond) else "tie"
            if ":" in sub and len(ids) < 10:
                verdict = "(small)" if verdict == "tie" else verdict
            if ":" not in sub and sub != "answerable" and sub != "unanswerable / near-miss":
                for i, xb, yn in zip(ids, x, y):
                    if xb != yn:
                        changed.append({"base": bname, "new": nname, "case": i, "change": "gained" if yn else "lost",
                                        "question": cases[i]["messages"][-1]["content"],
                                        "base_route": br[i].get("route"), "new_route": nr[i].get("route"),
                                        "base_calls": _calls(br[i]), "new_calls": _calls(nr[i]),
                                        "base_reply": (SR.scored_reply(br[i]) or "")[:500],
                                        "new_reply": (SR.scored_reply(nr[i]) or "")[:500],
                                        "new_flags": ",".join(nr[i].get("flags") or [])})
            rows.append({"base": bname, "new": nname, "model": bm.get("model"), "subset": sub, "n": len(ids),
                         "base_rate": sum(x) / len(ids), "new_rate": sum(y) / len(ids), "diff_pts": 100 * d,
                         "ci": [100 * lo, 100 * hi], "mcnemar_p": p, "lost": b, "gained": c,
                         "noise_bound_pts": nb, "verdict": verdict})

    L = ["# Paired dev comparison (Objective 3)", "",
         "NEW − BASE in points, repeat 0, automatic checks"
         + (", shown-card credit on" if a.credit_shown_cards else "") + ". Verdict: better/worse only if the "
         "difference is larger than the noise bound and the bootstrap interval excludes 0.", "",
         "| Base | New | Model | Subset | Cases | Base | New | New − Base [95% CI] | Lost / gained | McNemar p "
         "| Noise bound | Verdict |",
         "|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---|"]
    for r in rows:
        nb = "–" if r["noise_bound_pts"] is None else f"±{r['noise_bound_pts']:.1f}"
        L.append(f"| {r['base']} | {r['new']} | {r['model']} | {r['subset']} | {r['n']} | {r['base_rate']:.1%} "
                 f"| {r['new_rate']:.1%} | {r['diff_pts']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}] "
                 f"| {r['lost']} / {r['gained']} | {r['mcnemar_p']:.3f} | {nb} | **{r['verdict']}** |")
    L += ["", "## Rounds, reading and wait (same runs; quality runs, not in-place timing)", "",
          "| Base | New | Rounds base → new | Tokens read base → new | Tokens per tool output base → new "
          "| Empty replies base → new | Round limit hit base → new | Calls made by the harness base → new "
          "| First word p50 base → new |",
          "|---|---|---|---|---|---|---|---|---|"]
    f2 = lambda v, nd=2: "–" if v is None else f"{v:.{nd}f}"   # noqa: E731
    for s in speeds:
        b, n = s["base_speed"], s["new_speed"]
        L.append(f"| {s['base']} | {s['new']} | {f2(b['rounds'])} → {f2(n['rounds'])} "
                 f"| {f2(b['tok_read'], 0)} → {f2(n['tok_read'], 0)} "
                 f"| {f2(b['tok_per_tool_output'], 0)} → {f2(n['tok_per_tool_output'], 0)} "
                 f"| {b['empty_replies']} → {n['empty_replies']} | {b['round_limit']} → {n['round_limit']} "
                 f"| {b['harness_calls']}/{b['calls']} → {n['harness_calls']}/{n['calls']} "
                 f"| {f2(b['first_p50_s'], 1)} s → {f2(n['first_p50_s'], 1)} s"
                 + ("" if s["machines"][0] == s["machines"][1] else
                    f" (different machines: {s['machines'][0]} vs {s['machines'][1]}; not comparable)") + " |")
    L += ["", "## Paired waits per case (Step 13; every repeat, medians per case; only runs on the same machine)", "",
          "| Base | New | Cases | First word: median change [95% CI] | Total reply time: median change [95% CI] |",
          "|---|---|---|---|---|"]
    waits = []
    for base_dir, new_dir in a.pair:
        if base_dir in missing or new_dir in missing:
            continue
        bm, nm = load_run(base_dir)[0], load_run(new_dir)[0]
        if (bm.get("machine") or {}).get("label", "local") != (nm.get("machine") or {}).get("label", "local"):
            continue
        tb, tn = per_case_times(base_dir), per_case_times(new_dir)
        fw = paired_median_diff({k: v[0] for k, v in tb.items()}, {k: v[0] for k, v in tn.items()})
        tt = paired_median_diff({k: v[1] for k, v in tb.items()}, {k: v[1] for k, v in tn.items()})
        if fw and tt:
            waits.append({"base": os.path.basename(os.path.normpath(base_dir)),
                          "new": os.path.basename(os.path.normpath(new_dir)), "n": fw[3],
                          "first_word_s": list(fw[:3]), "total_s": list(tt[:3])})
            L.append(f"| {os.path.basename(os.path.normpath(base_dir))} | {os.path.basename(os.path.normpath(new_dir))} "
                     f"| {fw[3]} | {fw[0]:+.2f} s [{fw[1]:+.2f}, {fw[2]:+.2f}] | {tt[0]:+.2f} s [{tt[1]:+.2f}, {tt[2]:+.2f}] |")
    L += ["", "## Printed tool calls and staff discipline (Step 7)", "",
          "Printed: replies where the model wrote a tool call as text. Staff on answerable: questions with a known "
          "answer where the model itself called staff. Offered, not called: the reply mentions staff and no "
          "call_staff was made.", "",
          "| Base | New | Printed calls | Shown as staff line | Prose kept | Recovered | Model staff calls "
          "| Staff on answerable | Offered, not called | Promised, not called | Offer asked as a question "
          "| Harness call after offer |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s_ in speeds:
        b, n = s_["base_disc"], s_["new_disc"]
        L.append(f"| {s_['base']} | {s_['new']} | " + " | ".join(
            f"{b[k]} → {n[k]}" for k in ("printed", "printed_shown_fallback", "printed_stripped", "printed_recovered",
                                          "model_staff_calls", "staff_on_answerable", "offer_no_call",
                                          "promised_no_call", "offer_question", "harness_staff_after")) + " |")
    L += ["", "## Fixed replies and the staff check (Step 8)", "",
          "Entity: other brand, smartwatch, non-watch item or a design that does not exist. Fallback: store question "
          "below the threshold with no code or catalogue name. Staff check: the first 'can't answer' call_staff "
          "returned a note; 'then answered' = no staff call followed.", "",
          "| Base | New | Entity replies | Fallback replies | Staff-check notes | Checked, then answered |",
          "|---|---|---|---|---|---|"]
    for s_ in speeds:
        b, n = s_["base_disc"], s_["new_disc"]
        L.append(f"| {s_['base']} | {s_['new']} | " + " | ".join(
            f"{b[k]} → {n[k]}" for k in ("entity_replies", "fallback_replies", "staff_check_notes",
                                          "staff_checked_then_answered")) + " |")
    L += ["", "## Unsupported details and the answer check (Step 10)", "",
          "Unsupported: knowledge-path replies with a number, code or spec word found neither in the case's gold "
          "card(s) nor in the turn's tool results (independent of what was shown). Replaced: replies the answer "
          "check swapped for the fixed reply. Cited: replies that ended with card numbers.", "",
          "| Base | New | Unsupported base → new | Replaced by the check base → new | Cited base → new |",
          "|---|---|---|---|---|"]
    for s_ in speeds:
        if s_["base_unsup"] is None:
            continue
        (bb, bn), (nb_, nn) = s_["base_unsup"], s_["new_unsup"]
        L.append(f"| {s_['base']} | {s_['new']} | {bb}/{bn} ({bb / max(1, bn):.1%}) → {nb_}/{nn} ({nb_ / max(1, nn):.1%}) "
                 f"| {s_['base_disc']['verify_failed']} → {s_['new_disc']['verify_failed']} "
                 f"| {s_['base_disc']['cited']} → {s_['new_disc']['cited']} |")
    if missing:
        L += ["", "## Not compared", "", "These runs have no finished results yet (run the plan first; it resumes):", ""] \
            + [f"- {d}" for d in missing]
    with open(os.path.join(a.out, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    import csv
    with open(os.path.join(a.out, "changed_cases.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["base", "new", "case", "change", "question", "base_route", "new_route",
                                          "base_calls", "new_calls", "base_reply", "new_reply", "new_flags"])
        w.writeheader()
        w.writerows(changed)
    with open(os.path.join(a.out, "compare.json"), "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "speed": speeds, "waits": waits}, f, indent=1, default=str)
    print(f"Wrote {os.path.join(a.out, 'report.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
