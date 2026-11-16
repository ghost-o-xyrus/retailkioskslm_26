"""Figures for the Objective 2 write-up. Writes PDF (for LaTeX) and PNG (for slides) into figs/."""
import csv
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figs")
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, ORANGE, AQUA, YELLOW, GRAY, RED, PURPLE = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#b5b4ae", "#e34948", "#6250d6"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left",
    "legend.frameon": False, "figure.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.05,
})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf"))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=220)
    plt.close(fig)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * p, 100 * max(0, c - h), 100 * min(1, c + h)


# 1. Step 5: retriever benchmark, dev Recall@5 vs latency
def fig_bench():
    rows = list(csv.DictReader(open(os.path.join(HERE, "step5_summary.csv"), encoding="utf-8-sig")))
    dev = [r for r in rows if r["split"] == "dev"]
    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    style = {"": (GRAY, "o", "No re-ranker"), "minilm": (BLUE, "s", "+ MiniLM re-ranker (83 MB)"),
             "bge": (ORANGE, "^", "+ bge-reranker-base (1.4 GB)")}
    for key, (c, m, lab) in style.items():
        pts = [r for r in dev if (r["config"].split("+")[1] if "+" in r["config"] else "") == key]
        ax.scatter([float(r["latency_ms_p50"]) for r in pts], [100 * float(r["recall@5"]) for r in pts],
                   color=c, marker=m, s=38, label=lab, edgecolor="white", linewidth=0.8, zorder=3)
    ch = next(r for r in dev if r["config"] == "hybrid-bge-small-en-v1.5+minilm")
    ax.scatter([float(ch["latency_ms_p50"])], [100 * float(ch["recall@5"])], s=170, facecolor="none",
               edgecolor=INK, linewidth=1.5, zorder=4)
    ax.annotate("chosen: hybrid bge-small + MiniLM", (float(ch["latency_ms_p50"]), 100 * float(ch["recall@5"])),
                xytext=(18, -28), textcoords="offset points", fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    best = max(dev, key=lambda r: float(r["recall@5"]))
    ax.annotate("best dev: hybrid e5-small + bge\n(over the RAM budget)", (float(best["latency_ms_p50"]), 100 * float(best["recall@5"])),
                xytext=(-150, 6), textcoords="offset points", fontsize=8, color=INK2,
                arrowprops=dict(arrowstyle="-", color=INK2, lw=0.8))
    ax.set_xscale("log")
    ax.set_xlabel("Median latency per question, CPU 4 threads (ms, log scale)")
    ax.set_ylabel("Dev Recall@5 (%)")
    ax.set_ylim(70, 95)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("21 retrieval configurations on the 125 answerable dev questions")
    save(fig, "fig_bench")


# 2. Step 5b: latency variants
def fig_latency():
    V = [("torch 512 d20", 1065, 88.0, True), ("onnx 512 d20", 1001, 88.0, True), ("torch 256 d20", 749, 88.0, True),
         ("openvino 512 d20", 707, 88.0, True), ("onnx 256 d20", 623, 88.0, True), ("openvino 256 d20", 491, 88.0, True),
         ("openvino 256 d10", 284, 82.4, False), ("openvino 256 d5", 150, 75.2, False)]
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    y = np.arange(len(V))[::-1]
    for yy, (n, ms, r5, ok) in zip(y, V):
        c = BLUE if n == "openvino 256 d20" else (GRAY if ok else ORANGE)
        ax.barh(yy, ms, color=c, height=0.62)
        ax.text(ms + 15, yy, f"{ms} ms  ·  dev R@5 {r5:.1f}%{'' if ok else '  (rejected)'}", va="center", fontsize=8, color=INK)
    ax.axvline(300, color=RED, ls="--", lw=1)
    ax.text(305, y[-1] - 0.55, "300 ms target", color=RED, fontsize=8)
    ax.set_ylim(y[-1] - 0.8, y[0] + 0.5)
    ax.set_yticks(y, [v[0] for v in V])
    ax.set_xlim(0, 1500)
    ax.set_xlabel("Median latency, search + re-rank (ms)")
    ax.set_title("Re-ranker backend × passage length × depth (d = candidates re-ranked)")
    ax.grid(axis="y", visible=False)
    save(fig, "fig_latency")


# 3. Step 6: fallback calibration curves (dev)
def fig_fallback():
    rows = list(csv.DictReader(open(os.path.join(HERE, "curve_original.csv"), encoding="utf-8-sig")))
    x = [100 * float(r["dev_false_refusal"]) for r in rows]
    y = [100 * float(r["dev_refusal_recall"]) for r in rows]
    bx = [0, 0, 0, 0.9, 3.6, 5.4, 8.9, 12.5, 14.3, 17.0, 19.6, 23.2, 26.8, 28.6, 33.9, 38.4, 42.9, 47.3, 51.8, 55.4,
          60.7, 66.1, 71.4, 76.8, 81.2, 85.7]
    by = [0, 14.3, 35.7, 64.3, 78.6, 92.9] + [92.9] * 19 + [100]
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    ax.plot(x, y, color=GRAY, lw=2, label="Fallback on every question (Step 6)")
    ax.plot(bx, by, color=BLUE, lw=2, label="Hinglish exempt (Step 6b)")
    ax.scatter([4.5], [35.7], color=GRAY, s=45, zorder=3, edgecolor=INK, linewidth=0.8)
    ax.scatter([4.5], [85.7], color=BLUE, s=45, zorder=3, edgecolor=INK, linewidth=0.8)
    ax.annotate("chosen −7.97", (4.5, 35.7), xytext=(10, -14), textcoords="offset points", fontsize=8)
    ax.annotate("chosen −3.48", (4.5, 85.7), xytext=(10, -14), textcoords="offset points", fontsize=8)
    ax.axvline(5, color=RED, ls="--", lw=1)
    ax.text(5.6, 4, "5% budget", color=RED, fontsize=8)
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 102)
    ax.set_xlabel("Answerable dev questions refused (%)")
    ax.set_ylabel("Unanswerable dev questions refused (%)")
    ax.set_title("Threshold trade-off on dev (each point is a threshold)")
    ax.legend(loc="lower right", fontsize=8)
    save(fig, "fig_fallback")


# 4. Step 7: Tier A latency fixes (2B on CPU, dev pilot, knowledge questions)
def fig_tierA():
    S = [("No retrieval", 9.7, GRAY), ("Retrieve, full cards (pilot)", 24.0, ORANGE), ("+ soft fallback", 21.4, ORANGE),
         ("+ compact cards (7d)", 19.0, YELLOW), ("+ message unchanged when gated (7e)", 18.9, YELLOW),
         ("+ short reply to re-fetches (7f)", 13.8, BLUE)]
    fig, ax = plt.subplots(figsize=(7.0, 2.7))
    y = np.arange(len(S))[::-1]
    for yy, (n, v, c) in zip(y, S):
        ax.barh(yy, v, color=c, height=0.62)
        ax.text(v + 0.3, yy, f"{v:.1f} s", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(y, [s[0] for s in S])
    ax.set_xlim(0, 28)
    ax.set_xlabel("Median wait before the answer's first word (s)")
    ax.set_title("Tier A (2B, CPU, 4 threads): 24 dev knowledge questions")
    ax.grid(axis="y", visible=False)
    save(fig, "fig_tierA")


# 5. Step 8: answerable accuracy by condition
def fig_accuracy():
    conds = ["none", "tool", "deployed", "nofallback", "oracle"]
    labels = {"none": "No retrieval", "tool": "search_knowledge tool", "deployed": "Deployed setup",
              "nofallback": "Retrieval, no fallback", "oracle": "Gold chunks (ceiling)"}
    data = {"4B": {"none": 111, "tool": 141, "deployed": 173, "nofallback": 178, "oracle": 182},
            "2B": {"none": 89, "tool": 111, "deployed": 123, "nofallback": 128, "oracle": 153}}
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    y = np.arange(len(conds))[::-1]
    for off, (m, c) in zip((0.14, -0.14), (("4B", BLUE), ("2B", ORANGE))):
        for yy, k in zip(y, conds):
            v, lo, hi = wilson(data[m][k], 222)
            ax.plot([lo, hi], [yy + off] * 2, color=c, lw=2, solid_capstyle="round")
            ax.scatter([v], [yy + off], color=c, s=40, edgecolor="white", linewidth=1.2, zorder=3,
                       label=(f"Qwen3.5-{m}" if k == "none" else None))
            ax.text(hi + 1, yy + off, f"{v:.1f}%", va="center", fontsize=7.5, color=INK)
    ax.set_yticks(y, [labels[k] for k in conds])
    ax.set_xlim(30, 100)
    ax.set_xlabel("Answerable test questions answered correctly (%, 95% CI; n = 222 with an automatic check)")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_ylim(-0.6, len(conds) - 0.2)
    ax.set_title("Step 8: retrieval conditions, both models", pad=14)
    save(fig, "fig_accuracy")


# 6. Step 8: hallucination on unanswerable and near-miss questions
def fig_halluc():
    conds = [("none", "No retrieval"), ("nofallback", "Retrieval, no fallback"), ("deployed", "Deployed (soft fallback)"),
             ("hard", "Deployed + hard fallback")]
    U = {"4B": {"none": 17, "nofallback": 14, "deployed": 11, "hard": 9}, "2B": {"none": 23, "nofallback": 12, "deployed": 13, "hard": 7}}
    N = {"4B": {"none": 14, "nofallback": 12, "deployed": 13, "hard": 10}, "2B": {"none": 41, "nofallback": 20, "deployed": 28, "hard": 20}}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    y = np.arange(len(conds))[::-1]
    for ax, D, n, title in ((axes[0], U, 57, "Unanswerable (n = 57)"), (axes[1], N, 58, "Near miss (n = 58)")):
        for off, (m, c) in zip((0.14, -0.14), (("4B", BLUE), ("2B", ORANGE))):
            for yy, (k, _) in zip(y, conds):
                v, lo, hi = wilson(D[m][k], n)
                ax.plot([lo, hi], [yy + off] * 2, color=c, lw=2, solid_capstyle="round")
                ax.scatter([v], [yy + off], color=c, s=36, edgecolor="white", linewidth=1.2, zorder=3,
                           label=(f"Qwen3.5-{m}" if k == "none" else None))
                ax.text(hi + 1.2, yy + off, f"{v:.0f}%", va="center", fontsize=7.5, color=INK)
        ax.axvline(5, color=RED, ls="--", lw=1)
        ax.set_xlim(0, 90)
        ax.set_title(title)
        ax.set_xlabel("Judged hallucinating (%, 95% CI)")
    axes[0].set_yticks(y, [c[1] for c in conds])
    axes[0].text(5.8, y[-1] - 0.45, "5% target", color=RED, fontsize=7.5)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, fontsize=8, bbox_to_anchor=(0.62, 1.08))
    save(fig, "fig_halluc")


# 7. Step 8: v1.1 regression by category
def fig_regression():
    cats = ["comparison", "discovery", "handoff", "hinglish", "refusal", "tool_selection"]
    n = [11, 47, 29, 28, 27, 92]
    d = {"4B none": [100, 91, 59, 75, 85, 73], "4B deployed": [82, 74, 66, 79, 81, 66],
         "2B none": [100, 72, 17, 75, 81, 74], "2B deployed": [100, 45, 28, 36, 81, 65]}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True)
    x = np.arange(len(cats))
    for ax, m in zip(axes, ("4B", "2B")):
        ax.bar(x - 0.19, d[f"{m} none"], 0.38, color=GRAY, label="No retrieval")
        ax.bar(x + 0.19, d[f"{m} deployed"], 0.38, color=BLUE if m == "4B" else ORANGE, label="Deployed setup")
        ax.set_xticks(x, [f"{c.replace('_', ' ')} ({k})" for c, k in zip(cats, n)], fontsize=7, rotation=30, ha="right")
        ax.set_title({"4B": "Qwen3.5-4B: 78% → 72% overall", "2B": "Qwen3.5-2B: 69% → 56% overall"}[m])
        ax.set_ylim(0, 105)
        ax.grid(axis="x", visible=False)
        ax.legend(loc="upper right", fontsize=7.5)
    axes[0].set_ylabel("v1.1 test tool cases passed (%)")
    save(fig, "fig_regression")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig_bench, fig_latency, fig_fallback, fig_tierA, fig_accuracy, fig_halluc, fig_regression):
        f()
    print("figures written to", OUT)
