"""Figures for the Objective 4 write-up. Writes PDF (for LaTeX) and PNG (for slides) into figs/.
All numbers are copied from the Step 6, 7 and 8 result files (verdicts.md, report.md)."""
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




def fig_step6():
    # results_obj4/_step6/verdicts.md (dev, Vulkan)
    sets = ["Store", "Tools", "Follow-\nups", "Unans. /\nnear-miss"]
    rows = {"lora_2b (Tier A)": ([71.1, 84.7, 85.0, 61.5], [83.0, 89.8, 90.0, 97.4], ["better", "tie", "tie", "better"]),
            "qlora_2b (Tier A)": ([71.1, 84.7, 85.0, 61.5], [84.4, 96.6, 90.0, 89.7], ["better", "better", "tie", "better"]),
            "lora_4b (Tier B)": ([85.2, 91.7, 93.3, 84.6], [85.9, 95.0, 90.0, 100.0], ["tie", "tie", "tie", "better"])}
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.8), sharey=True)
    x = np.arange(len(sets))
    for ax, (name, (b, a, v)) in zip(axes, rows.items()):
        ax.bar(x - 0.19, b, width=0.36, color=GRAY, label="O3-final")
        ax.bar(x + 0.19, a, width=0.36, color=[AQUA if vv == "better" else BLUE for vv in v], label="+ adapter")
        for xi, aa, vv in zip(x, a, v):
            if vv == "better":
                ax.text(xi + 0.19, aa + 1.2, "▲", ha="center", fontsize=7, color=AQUA)
        ax.set_xticks(x)
        ax.set_xticklabels(sets, fontsize=6.8)
        ax.set_ylim(40, 105)
        ax.set_title(name, fontsize=9)
    axes[0].set_ylabel("Pass rate on dev (%)")
    from matplotlib.patches import Patch
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.legend(handles=[Patch(color=GRAY, label="O3-final"), Patch(color=BLUE, label="+ adapter (tie)"),
                        Patch(color=AQUA, label="+ adapter (better)")], fontsize=7, loc="lower center", ncol=3)
    save(fig, "fig_step6")


def fig_behaviour():
    # H1-H3 counts on dev (Step 6 and 7 reports)
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.5))
    ax = axes[0]
    lab = ["2B\nO3-final", "2B\n+ lora", "4B short\nreplies", "4B short\n+ lora"]
    vals = [3, 0, 27, 0]
    ax.bar(range(4), vals, color=[GRAY, AQUA, GRAY, AQUA], width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.6, str(v), ha="center", fontsize=8)
    ax.set_xticks(range(4)); ax.set_xticklabels(lab, fontsize=6.8)
    ax.set_title("Printed tool calls (H1)", fontsize=9)
    ax = axes[1]
    ax.bar([0, 1], [20, 0], color=[GRAY, AQUA], width=0.55)
    for i, v in enumerate([20, 0]):
        ax.text(i, v + 0.4, str(v), ha="center", fontsize=8)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["O3-final", "+ lora_2b"], fontsize=7.5)
    ax.set_title("2B staff calls on\nanswerable questions (H2)", fontsize=9)
    ax = axes[2]
    ax.bar([0, 1], [6.2, 1.5], color=[GRAY, AQUA], width=0.55)
    for i, (v, t) in enumerate([(6.2, "8/130"), (1.5, "2/131")]):
        ax.text(i, v + 0.15, t, ha="center", fontsize=8)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["O3-final", "+ lora_2b"], fontsize=7.5)
    ax.set_ylabel("% of answers", fontsize=8)
    ax.set_title("2B unsupported details\n(automatic check)", fontsize=9)
    fig.tight_layout()
    save(fig, "fig_behaviour")


def fig_step7():
    # results_obj4/_step7/verdicts.md: difference from O3-final, points, with 95% intervals
    rows = [("4B short replies, no adapter", "Store questions", -9.0, -14.9, -3.0, "worse"),
            ("4B short replies, no adapter", "Tool cases", -8.3, -16.7, -1.7, "worse"),
            ("4B + lora, short replies, patches off", "Store questions", 1.5, -4.4, 7.4, "tie"),
            ("4B + lora, short replies, patches off", "Tool cases", 3.3, 0.0, 8.3, "tie"),
            ("4B + lora, short replies, patches off", "Follow-ups", -5.0, -13.3, 3.3, "tie"),
            ("2B patches off, no adapter", "Store questions", -3.0, -7.4, 0.7, "tie"),
            ("2B + lora, patches off", "Store questions", 11.9, 4.4, 19.3, "better"),
            ("2B + lora, patches off", "Tool cases", 8.5, -1.7, 18.6, "tie"),
            ("2B + lora, patches off", "Follow-ups", 5.0, -1.7, 13.3, "tie")]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    y = np.arange(len(rows))[::-1]
    for yi, (r, s, d, lo, hi, v) in zip(y, rows):
        c = AQUA if v == "better" else RED if v == "worse" else GRAY
        ax.plot([lo, hi], [yi, yi], color=c, lw=2.4, solid_capstyle="round")
        ax.scatter([d], [yi], color=c, s=30, zorder=3, edgecolor="white")
        ax.text(22, yi, f"{d:+.1f}  {v}", va="center", fontsize=7.5, color=INK if v != "tie" else INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r}: {s}" for r, s, *_ in rows], fontsize=7.3)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(-18, 30)
    ax.set_xlabel("Difference from O3-final on dev, points (paired bootstrap 95% interval)")
    fig.tight_layout()
    save(fig, "fig_step7")


def fig_step8():
    # results_obj4/_compare_step8/report.md, paired waits per case (laptop CPU, 2 repeats)
    rows = [("+ lora_2b, patches on", "store, first word", -2.51, -6.52, -0.02),
            ("+ lora_2b, patches on", "store, total", -2.25, -6.45, -0.10),
            ("+ lora_2b, patches on", "tools, first word", -0.77, -1.58, -0.01),
            ("+ lora_2b, patches on", "tools, total", -0.87, -2.00, 0.00),
            ("candidate: patches off", "store, first word", -2.24, -5.96, -0.06),
            ("candidate: patches off", "store, total", -2.01, -5.80, -0.40),
            ("candidate: patches off", "tools, first word", 3.31, 0.01, 3.97),
            ("candidate: patches off", "tools, total", 2.65, 0.01, 4.17)]
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    y = np.arange(len(rows))[::-1]
    for yi, (r, s, d, lo, hi) in zip(y, rows):
        c = RED if lo > 0 else BLUE
        ax.plot([lo, hi], [yi, yi], color=c, lw=2.4, solid_capstyle="round")
        ax.scatter([d], [yi], color=c, s=30, zorder=3, edgecolor="white")
        ax.text(5.0, yi, f"{d:+.2f} s", va="center", fontsize=7.5)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r}: {s}" for r, s, *_ in rows], fontsize=7.3)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_xlim(-7.5, 6.5)
    ax.set_xlabel("Change from O3-final, median per case, seconds (laptop CPU, 4 threads, 70 cases × 2 repeats)")
    fig.tight_layout()
    save(fig, "fig_step8")


def fig_data():
    # Step 2-3: training mix and filtering
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.5))
    ax = axes[0]
    gaps = ["Staff\ndiscipline", "Format", "Not\nlisted", "Decline", "Tool\nchoice"]
    vals = [50, 25, 18, 9.4, 2.9]
    ax.bar(range(5), vals, color=BLUE, width=0.6)
    ax.axhline(10, color=RED, lw=0.9, ls=":")
    ax.text(4.45, 11, "10% target", fontsize=6.8, color=RED, ha="right")
    for i, v in enumerate(vals):
        ax.text(i, v + 1, f"{v:g}%", ha="center", fontsize=7.5)
    ax.set_xticks(range(5)); ax.set_xticklabels(gaps, fontsize=7)
    ax.set_ylabel("% of 3,000 examples", fontsize=8)
    ax.set_title("Target gaps in the training mix", fontsize=8.5)
    ax = axes[1]
    st = ["Replies\nneeded", "Pass after\nfirst pass", "Pass after\nretry", "Examples per\ntier (of 3,000)"]
    v = [2913, 2243, 2535, 2632]
    ax.bar(range(4), v, color=[GRAY, BLUE, BLUE, AQUA], width=0.6)
    for i, x in enumerate(v):
        ax.text(i, x + 40, f"{x:,}", ha="center", fontsize=7.5)
    ax.set_ylim(0, 3300)
    ax.set_xticks(range(4)); ax.set_xticklabels(st, fontsize=7)
    ax.set_title("Teacher replies through the checks", fontsize=8.5)
    fig.tight_layout()
    save(fig, "fig_data")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig_step6, fig_behaviour, fig_step7, fig_step8, fig_data):
        f()
    print("figures written")
