"""
Agreement between the judge and a person on the Step 8 human check.

    python eval\\rag_judge\\agreement.py eval\\rag_judge\\step8\\human_check_filled.csv

Reads the filled human_check.csv (last column: answered / unsupported / declined) and the judge's labels*.json in
the same folder. Reports exact agreement, Cohen's kappa, agreement on the key question (unsupported or not) and a
confusion table.
"""

import csv
import glob
import json
import os
import sys

LABELS = ("answered", "unsupported", "declined")


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    pe = sum((sum(a == l for a, _ in pairs) / n) * (sum(b == l for _, b in pairs) / n) for l in LABELS)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python eval\\rag_judge\\agreement.py <filled human_check csv>")
    path = sys.argv[1]
    folder = os.path.dirname(os.path.abspath(path))
    judge = {}
    for fp in glob.glob(os.path.join(folder, "labels*.json")):
        with open(fp, encoding="utf-8") as f:
            for row in json.load(f):
                judge[row["item"]] = row["label"]
    pairs = []
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))[1:]
    for row in rows:
        h = row[-1].strip().lower()
        if h in LABELS and row[0] in judge:
            pairs.append((h, judge[row[0]]))
    if not pairs:
        sys.exit("No labelled rows matched judge labels.")
    n = len(pairs)
    exact = sum(a == b for a, b in pairs)
    bin_ = sum((a == "unsupported") == (b == "unsupported") for a, b in pairs)
    print(f"Items: {n}. Exact agreement: {exact}/{n} = {100 * exact / n:.0f}%. Cohen's kappa: {kappa(pairs):.2f}.")
    print(f"Unsupported vs not: {bin_}/{n} = {100 * bin_ / n:.0f}% agree.")
    print("\nRows = person, columns = judge")
    print("            " + "".join(f"{l:>13s}" for l in LABELS))
    for a in LABELS:
        print(f"{a:12s}" + "".join(f"{sum(1 for x, y in pairs if x == a and y == b):13d}" for b in LABELS))


if __name__ == "__main__":
    main()
