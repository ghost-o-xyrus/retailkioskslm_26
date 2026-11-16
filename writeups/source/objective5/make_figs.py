"""Figures for the Objective 5 write-up. Writes PDF (for LaTeX) and PNG (for slides) into figs/.
All numbers are copied from the Step 8, 9 and 10 result files (report.md, policy.json)."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figs")
os.makedirs(OUT, exist_ok=True)
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, ORANGE, AQUA, YELLOW, GRAY, RED = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#b5b4ae", "#e34948"
GOOD, BAD = "#1f8f5f", "#c9302c"

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


# Step 8 (results_obj5/_measure_step8/report.md)
RUNS = ["A resident\ndev", "A resident\ntest", "A sequential\ndev", "B resident\ndev", "B resident\ntest"]
TOT = [(7.58, 19.78), (6.74, 18.90), (7.94, 17.41), (6.36, 13.94), (6.16, 13.06)]
FIRST = [(2.63, 17.88), (3.64, 15.80), (3.62, 15.76), (2.38, 3.95), (0.89, 4.54)]
H_TOT = [7.05, 7.23, 7.90, 6.34, 6.62]
OVH = [(0.03, 0.01, 0.05), (0.01, -2.11, 2.27), (-0.01, -0.07, 0.03), (0.01, -0.00, 0.02), (0.02, -1.36, 1.47)]
OVH_F = [(0.02, 0.01, 0.06), (0.01, -2.11, 2.29), (-0.00, -0.05, 0.03), (0.00, -0.02, 0.01), (0.02, -1.36, 1.46)]
COL = [ORANGE, ORANGE, GRAY, BLUE, BLUE]


def fig_latency():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.7), sharey=True)
    x = np.arange(len(RUNS))
    for ax, data, title in ((axes[0], TOT, "Total reply time"), (axes[1], FIRST, "First word on screen")):
        p50 = [d[0] for d in data]
        p90 = [d[1] for d in data]
        ax.bar(x, p50, width=0.55, color=COL, label="median")
        ax.scatter(x, p90, marker="_", s=260, color=INK, linewidths=1.6, zorder=3, label="90th percentile")
        for xi, a, b in zip(x, p50, p90):
            if a > 1.5:
                ax.text(xi, a - 0.35, f"{a:.1f}", ha="center", va="top", fontsize=7.2, color="white", fontweight="bold")
            else:
                ax.text(xi, a + 0.3, f"{a:.1f}", ha="center", fontsize=7.2, color=INK)
            ax.text(xi + 0.32, b, f"{b:.1f}", ha="left", va="center", fontsize=6.6, color=INK2)
        ax.set_xticks(x)
        ax.set_xticklabels(RUNS, fontsize=6.6)
        ax.set_title(title, fontsize=9)
        ax.set_ylim(0, 22)
    axes[0].set_ylabel("Seconds, through the app")
    axes[1].legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    save(fig, "fig_latency")


def fig_overhead():
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.5), sharey=True)
    y = np.arange(len(RUNS))[::-1]
    labels = [r.replace("\n", " ") for r in RUNS]
    for ax, data, title, lim in ((axes[0], OVH, "Total: app minus harness", None),
                                 (axes[1], OVH_F, "First word: app minus harness", 0.3)):
        for yi, (m, lo, hi), c in zip(y, data, COL):
            ax.plot([lo, hi], [yi, yi], color=c, lw=2, solid_capstyle="round")
            ax.scatter([m], [yi], color=c, s=28, zorder=3, edgecolor="white", linewidth=1)
            ax.text(3.45, yi, f"{m:+.2f} s", va="center", ha="right", fontsize=7, color=INK)
        ax.axvline(0, color=MUTED, lw=0.8)
        if lim:
            ax.axvline(lim, color=RED, lw=1, ls="--", label="rule: at most 0.3 s")
            ax.legend(fontsize=6.8, loc="lower left", bbox_to_anchor=(0, -0.52))
        ax.set_xlim(-2.4, 3.5)
        ax.set_title(title, fontsize=9)
        ax.set_xlabel("Seconds; median of paired differences, 95% interval", fontsize=7)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(labels, fontsize=7)
    # 5% of the harness total per run
    for k, (yi, h) in enumerate(zip(y, H_TOT)):
        axes[0].plot([0.05 * h], [yi], marker="|", color=RED, ms=9, mew=1.4, ls="none",
                     label="rule: at most 5% of the harness total" if k == 0 else None)
    axes[0].legend(fontsize=6.8, loc="lower left", bbox_to_anchor=(0, -0.52))
    fig.tight_layout()
    save(fig, "fig_overhead")


def fig_ram():
    fig, ax = plt.subplots(figsize=(4.6, 2.5))
    groups = ["Tier A (2B, CPU)", "Tier B (4B, GPU)"]
    o2 = [3.8, 6.7]
    dev = [3.21, 4.76]
    test = [3.16, 4.74]
    budget = [5, 10]
    x = np.arange(2)
    w = 0.24
    for off, vals, c, lab in ((-w, o2, GRAY, "Objective 2 (harness)"), (0, dev, BLUE, "App, dev"),
                              (w, test, AQUA, "App, test")):
        ax.bar(x + off, vals, width=w - 0.03, color=c, label=lab)
        for xi, v in zip(x, vals):
            ax.text(xi + off, v + 0.15, f"{v:.1f}" if c == GRAY else f"{v:.2f}", ha="center", fontsize=7, color=INK)
    for xi, b in zip(x, budget):
        ax.plot([xi - 0.42, xi + 0.42], [b, b], color=RED, lw=1.2, ls="--")
        ax.text(xi + 0.42, b + 0.2, f"budget {b} GB", ha="right", fontsize=7, color=RED)
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Peak RAM, model + app (GB)")
    ax.set_ylim(0, 11.2)
    ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    save(fig, "fig_ram")


def fig_policy():
    stages = ["input", "route", "retrieval", "harness tools", "model rounds", "model tools", "checks"]
    res = [13, 1, 585, 1, 7748, 2, 1]
    seq = [13, 1588, 248, 0.5, 6668, 2, 1]
    fig, ax = plt.subplots(figsize=(7.4, 2.4))
    y = np.arange(len(stages))[::-1]
    h = 0.36
    ax.barh(y + h / 2, res, height=h - 0.04, color=ORANGE, label="resident (chosen)")
    ax.barh(y - h / 2, seq, height=h - 0.04, color=GRAY, label="sequential")
    for yi, a, b in zip(y, res, seq):
        ax.text(a * 1.15, yi + h / 2, f"{a:,.0f} ms", va="center", fontsize=6.8, color=INK)
        ax.text(b * 1.15, yi - h / 2, f"{b:,.0f} ms", va="center", fontsize=6.8, color=INK2)
    ax.set_xscale("log")
    ax.set_xlim(0.3, 60000)
    ax.set_yticks(y)
    ax.set_yticklabels(stages)
    ax.set_xlabel("Median ms per turn (log scale), Tier A, dev, through the app")
    ax.legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    save(fig, "fig_policy")


def fig_walk():
    rows = ["K  Kiosk lock", "1  Shopping", "2  Store question", "3  Hinglish", "4  Images", "5  Compare (Lab)",
            "6  Hand-off", "R1 llama-server restart", "R2 App restart", "N  No network use", "P  Same replies"]
    cols = ["A\nStep 9", "A\nrerun", "A\nStep 10", "B\nStep 9", "B\nrerun", "B\nStep 10"]
    P, F, N = 1, 0, -1
    data = np.array([
        [P, N, P, P, N, P],
        [P, N, P, P, N, P],
        [P, N, P, P, N, P],
        [F, P, P, F, F, F],
        [P, P, P, P, P, P],
        [P, N, P, P, N, P],
        [P, P, P, P, P, P],
        [N, N, P, N, N, P],
        [N, N, P, N, N, P],
        [N, N, F, N, N, F],
        [N, N, P, N, N, P],
    ])
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    ax.grid(False)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = data[i, j]
            fc = {P: "#e3f3ea", F: "#f9e1df", N: "#f4f3f0"}[v]
            tc = {P: GOOD, F: BAD, N: MUTED}[v]
            txt = {P: "pass", F: "FAIL", N: "–"}[v]
            ax.add_patch(plt.Rectangle((j + 0.04, i + 0.06), 0.92, 0.88, color=fc, lw=0))
            ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=7.4, color=tc,
                    fontweight="bold" if v == F else "normal")
    ax.set_xlim(0, data.shape[1])
    ax.set_ylim(data.shape[0], 0)
    ax.set_xticks(np.arange(data.shape[1]) + 0.5)
    ax.set_xticklabels(cols, fontsize=7.2)
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(data.shape[0]) + 0.5)
    ax.set_yticklabels(rows, fontsize=7.4)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axvline(3, color=MUTED, lw=0.8)
    fig.tight_layout()
    save(fig, "fig_walk")


if __name__ == "__main__":
    fig_latency()
    fig_overhead()
    fig_ram()
    fig_policy()
    fig_walk()
    print("figures written")
