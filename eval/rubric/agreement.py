"""
Compare the human check sheet with the judge's scores.

    python eval/rubric/agreement.py eval/rubric/stage3
Reads human_check.xlsx (filled), human_check_key.json and scores*.json. Prints exact agreement, agreement within 1 point,
mean difference (judge − human) and quadratic-weighted kappa, over every rubric line both of you scored.
"""
import glob, json, os, sys
from openpyxl import load_workbook


def qwk(a, b, k=5):
    import itertools
    n = len(a)
    O = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        O[x - 1][y - 1] += 1
    ha = [sum(1 for x in a if x == i + 1) for i in range(k)]
    hb = [sum(1 for y in b if y == i + 1) for i in range(k)]
    num = den = 0.0
    for i, j in itertools.product(range(k), range(k)):
        w = (i - j) ** 2 / (k - 1) ** 2
        num += w * O[i][j]
        den += w * ha[i] * hb[j] / n
    return 1 - num / den if den else 1.0


def main(folder, exclude=()):
    key = json.load(open(os.path.join(folder, "human_check_key.json")))
    judge = {}
    for f in sorted(glob.glob(os.path.join(folder, "scores*.json"))):  # later files (re-judged items) win
        for s in json.load(open(f, encoding="utf-8")):
            judge[s["item"]] = s
    ws = load_workbook(os.path.join(folder, next((n for n in ("human_check_filled.xlsx", "human_check.xlsx") if os.path.exists(os.path.join(folder, n))))))["Check"]
    h, j = [], []
    for row in ws.iter_rows(min_row=2, values_only=True):
        cid = row[0]
        if cid not in key or cid in exclude:
            continue
        k = key[cid]
        js = judge[k["item"]][k["label"]]
        for i, col in enumerate((5, 7, 9, 11)):
            hv = row[col]
            if hv in (None, "") or js[i] is None:
                continue
            h.append(int(hv)); j.append(int(js[i]))
    n = len(h)
    if not n:
        print("No scored lines found. Fill the yellow Score cells first.")
        return
    exact = sum(a == b for a, b in zip(h, j)) / n
    within1 = sum(abs(a - b) <= 1 for a, b in zip(h, j)) / n
    bias = sum(b - a for a, b in zip(h, j)) / n
    print(f"Lines compared: {n}")
    print(f"Exact agreement: {100 * exact:.0f}%   Within 1 point: {100 * within1:.0f}%")
    print(f"Mean difference (judge - human): {bias:+.2f}   Quadratic-weighted kappa: {qwk(h, j):.2f}")


if __name__ == "__main__":
    main(sys.argv[1], exclude=set(a for x in sys.argv[2:] if x.startswith("--exclude=") for a in x[10:].split(",")))
