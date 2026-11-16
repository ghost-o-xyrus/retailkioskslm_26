"""Figures for the Objective 3 write-up. Writes PDF (for LaTeX) and PNG (for slides) into figs/.
All numbers are copied from the Step 14 and Step 15 result files (verdicts.md, report.md, ladder.md,
summary.md, scorecard.md)."""
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


RUNGS = ["B0", "R1\noutputs", "R2\nrouter", "R3\ntools,\ndiscovery", "R4\nfallback", "R5\nchecks,\nfollow-ups",
         "R6\nfinal"]
# Step 15 GPU ladder (results_obj3/_step15_gpu/ladder.md)
L = {
    "2b": {"Store questions": [50.7, 63.2, 64.4, 67.2, 70.8, 71.0, 69.5],
           "Tool cases": [61.5, 64.6, 71.4, 78.6, 78.6, 79.2, 76.0],
           "Follow-ups": [76.7, 76.7, 76.7, 75.0, 75.0, 90.0, 91.7],
           "Dialogue fit": [79, 84, 73, 97, 97, 97, 97],
           "Unanswerable / near-miss": [35.3, 35.3, 34.5, 38.8, 49.6, 51.8, 52.9]},
    "4b": {"Store questions": [80.4, 82.1, 82.3, 81.1, 82.3, 82.5, 82.3],
           "Tool cases": [79.7, 78.1, 86.5, 83.9, 83.9, 83.3, 83.3],
           "Follow-ups": [68.3, 65.0, 65.0, 66.7, 66.7, 96.7, 90.0],
           "Dialogue fit": [57, 56, 56, 97, 97, 97, 97],
           "Unanswerable / near-miss": [70.5, 77.0, 77.7, 74.1, 79.9, 80.6, 78.4]},
}
NR = {"2b": {"Store questions": 65.4, "Tool cases": 61.4, "Follow-ups": 63.3, "Dialogue fit": 76},
      "4b": {"Store questions": 82.1, "Tool cases": 81.8, "Follow-ups": 61.7, "Dialogue fit": 63}}
SETCOL = {"Store questions": BLUE, "Tool cases": ORANGE, "Follow-ups": AQUA, "Dialogue fit": PURPLE,
          "Unanswerable / near-miss": YELLOW}


def fig_ladder():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6), sharey=True)
    x = np.arange(len(RUNGS))
    for ax, (m, title) in zip(axes, (("2b", "Tier A: Qwen3.5-2B"), ("4b", "Tier B: Qwen3.5-4B"))):
        for k in ("Store questions", "Tool cases", "Follow-ups", "Dialogue fit"):
            ax.plot(x, L[m][k], marker="o", ms=3.5, lw=1.6, color=SETCOL[k], label=k)
            ax.scatter([len(RUNGS) - 0.55], [NR[m][k]], marker="x", color=SETCOL[k], s=22, zorder=4)
        ax.set_xticks(x)
        ax.set_xticklabels(RUNGS, fontsize=6.3)
        ax.set_title(title)
        ax.set_ylim(50, 100)
        ax.set_xlim(-0.3, len(RUNGS) - 0.3)
        ax.text(len(RUNGS) - 0.55, 51.5, "× no\nrouter", ha="center", fontsize=6.3, color=INK2)
    axes[0].set_ylabel("Pass rate / fit (%)")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=7.5, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, "fig_ladder")


def fig_reading():
    tok = {"2b": {"rag": [852, 638, 545, 553, 528, 528, 427], "v12": [1066, 716, 286, 268, 270, 270, 259]},
           "4b": {"rag": [563, 516, 447, 452, 429, 429, 363], "v12": [754, 592, 273, 261, 261, 261, 258]}}
    rnd = {"2b": {"rag": [2.54, 2.33, 2.20, 2.03, 1.97, 1.97, 1.73], "v12": [2.82, 2.67, 2.09, 1.04, 1.07, 1.07, 1.04]},
           "4b": {"rag": [1.30, 1.29, 1.37, 1.14, 1.02, 1.02, 1.07], "v12": [1.85, 1.90, 2.08, 0.94, 0.94, 0.94, 0.95]}}
    short = ["B0", "R1", "R2", "R3", "R4", "R5", "R6"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7))
    x = np.arange(7)
    for m, ls, lab in (("2b", "-", "2B"), ("4b", "--", "4B")):
        axes[0].plot(x, tok[m]["rag"], ls=ls, color=BLUE, marker="o", ms=3, label=f"{lab} store questions")
        axes[0].plot(x, tok[m]["v12"], ls=ls, color=ORANGE, marker="o", ms=3, label=f"{lab} tool cases")
        axes[1].plot(x, rnd[m]["rag"], ls=ls, color=BLUE, marker="o", ms=3)
        axes[1].plot(x, rnd[m]["v12"], ls=ls, color=ORANGE, marker="o", ms=3)
    axes[0].set_title("Prompt tokens read per turn")
    axes[1].set_title("Model requests per turn")
    axes[1].axhline(1.3, color=RED, lw=0.9, ls=":")
    axes[1].text(6.1, 1.34, "target 1.3", fontsize=7, color=RED, ha="right")
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(short)
    axes[0].legend(fontsize=6.8, ncol=2, loc="upper right")
    fig.tight_layout()
    save(fig, "fig_reading")


def fig_step14():
    rows = [("A", "Store questions", 17.7, 12.7, 22.6, "better"), ("A", "Tool cases", 15.1, 7.3, 22.9, "better"),
            ("A", "Follow-ups", 10.0, 0.0, 20.0, "tie"), ("B", "Store questions", 3.1, -0.2, 6.4, "tie"),
            ("B", "Tool cases", 5.2, -2.1, 12.5, "tie"), ("B", "Follow-ups", 23.3, 8.3, 38.3, "better")]
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    y = np.arange(len(rows))[::-1]
    for yi, (t, s, d, lo, hi, v) in zip(y, rows):
        c = AQUA if v == "better" else GRAY
        ax.plot([lo, hi], [yi, yi], color=c, lw=2.4, solid_capstyle="round")
        ax.scatter([d], [yi], color=c, s=34, zorder=3, edgecolor="white")
        ax.text(41, yi, f"{d:+.1f}  {v}", va="center", fontsize=8, color=INK if v == "better" else INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([f"Tier {t}: {s}" for t, s, *_ in rows])
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(-5, 52)
    ax.set_xlabel("O3-final − O3-B0, points (paired bootstrap 95% interval); verdict after Holm adjustment")
    fig.tight_layout()
    save(fig, "fig_step14")


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * p, 100 * max(0, c - h), 100 * min(1, c + h)


def fig_judged():
    # eval/rag_judge/step15/summary.md
    data = {"2B": {"Unanswerable": ((14, 57), (21, 57)), "Near-miss": ((37, 82), (36, 82)),
                   "Unsupported\n(answer sample)": ((7, 60), (11, 60)), "False refusals": ((84, 324), (27, 324))},
            "4B": {"Unanswerable": ((12, 57), (13, 57)), "Near-miss": ((15, 82), (14, 82)),
                   "Unsupported\n(answer sample)": ((5, 60), (4, 60)), "False refusals": ((11, 324), (18, 324))}}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    for ax, m in zip(axes, ("2B", "4B")):
        cats = list(data[m])
        x = np.arange(len(cats))
        for off, idx, col, lab in ((-0.18, 0, GRAY, "O3-B0"), (0.18, 1, BLUE, "O3-final")):
            vals = [wilson(*data[m][c][idx]) for c in cats]
            ax.bar(x + off, [v[0] for v in vals], width=0.34, color=col, label=lab)
            ax.errorbar(x + off, [v[0] for v in vals], yerr=[[v[0] - v[1] for v in vals], [v[2] - v[0] for v in vals]],
                        fmt="none", ecolor=INK2, elinewidth=0.8, capsize=2)
        ax.plot([-0.45, 2.45], [5, 5], color=RED, lw=0.9, ls=":")
        ax.plot([2.55, 3.45], [10, 10], color=RED, lw=0.9, ls=":")
        ax.set_xticks(x)
        ax.set_xticklabels(cats, fontsize=7)
        ax.set_title(f"Qwen3.5-{m} (judged)")
    axes[0].set_ylabel("% of questions (Wilson 95%)")
    axes[0].text(-0.4, 6.3, "target 5%", fontsize=6.8, color=RED)
    axes[0].text(3.45, 11.3, "target 10%", fontsize=6.8, color=RED, ha="right")
    axes[1].legend(fontsize=7.5, loc="upper right")
    fig.tight_layout()
    save(fig, "fig_judged")


def fig_wait():
    rows = [("Tier A store questions, first word", -3.86, -12.69, -1.31), ("Tier A store questions, total", -4.42, -10.73, -2.92),
            ("Tier A tool cases, first word", -19.14, -24.67, -13.56), ("Tier A tool cases, total", -22.27, -29.71, -17.52)]
    fig, ax = plt.subplots(figsize=(7.0, 1.9))
    y = np.arange(len(rows))[::-1]
    for yi, (s, d, lo, hi) in zip(y, rows):
        ax.plot([lo, hi], [yi, yi], color=BLUE, lw=2.4, solid_capstyle="round")
        ax.scatter([d], [yi], color=BLUE, s=30, zorder=3, edgecolor="white")
        ax.text(2.0, yi, f"{d:+.1f} s", va="center", fontsize=8)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(-32, 6)
    ax.set_xlabel("O3-final − O3-B0, median per-case change in seconds (laptop CPU, in place, 70 cases × 2 repeats)")
    fig.tight_layout()
    save(fig, "fig_wait")


def fig_dialogues():
    cats = ["Reached a\nrecommendation", "≥ 2 slots known\nbefore it", "Shown watches\nfit (mean)"]
    vals = {"2B": ([97, 34, 87], [100, 100, 97]), "4B": ([85, 84, 63], [100, 100, 97])}
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.4), sharey=True)
    for ax, m in zip(axes, ("2B", "4B")):
        x = np.arange(3)
        ax.bar(x - 0.18, vals[m][0], 0.34, color=GRAY, label="O3-B0")
        ax.bar(x + 0.18, vals[m][1], 0.34, color=AQUA, label="O3-final")
        for xi, v in zip(x, vals[m][1]):
            ax.text(xi + 0.18, v + 1.5, f"{v}%", ha="center", fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels(cats, fontsize=7)
        ax.set_ylim(0, 112)
        ax.set_title(f"Qwen3.5-{m}: 60 fresh dialogues")
    axes[1].legend(fontsize=7.5, loc="lower right")
    fig.tight_layout()
    save(fig, "fig_dialogues")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig_ladder, fig_reading, fig_step14, fig_judged, fig_wait, fig_dialogues):
        f()
    print("figures written to", OUT)
