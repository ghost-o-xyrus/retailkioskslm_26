"""Figures for the Objective 1 write-up. Writes PDF (for LaTeX) and PNG (for slides) into figs/."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "results.json")))
OUT = os.path.join(HERE, "figs")

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
BLUE, ORANGE, AQUA, YELLOW, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#b5b4ae"
FAMILY = {"Qwen3.5-4B": BLUE, "Qwen3.5-2B": ORANGE, "Gemma 4 E2B": AQUA}


def colour(name):
    for k, v in FAMILY.items():
        if name.startswith(k):
            return v
    return GRAY


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


def dot_ci(ax, y, val, lo, hi, c, size=55):
    ax.plot([lo, hi], [y, y], color=c, lw=2, solid_capstyle="round", zorder=2)
    ax.scatter([val], [y], s=size, color=c, edgecolor="white", linewidth=1.5, zorder=3)


# 1. Stage 1 screen: pass rate and tool-call accuracy, 6 models
def fig_screen():
    ms = D["stage1"]["models"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True)
    ys = np.arange(len(ms))[::-1]
    for ax, key, title in [(axes[0], "pass", "Cases passed"), (axes[1], "tool", "Tool calls right")]:
        for y, m in zip(ys, ms):
            v, lo, hi = m[key]
            dot_ci(ax, y, v, lo, hi, colour(m["name"]))
            ax.text(hi + 1.5, y, f"{v}%", va="center", fontsize=8, color=INK,
                    bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"), zorder=5)
        ax.set_xlim(0, 105)
        ax.set_title(title)
        ax.set_xlabel("% of test cases (95% CI)" if key == "pass" else "% of tool cases (95% CI)")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(ys, [m["name"] for m in ms])
    axes[1].axvline(80, color=INK2, lw=1, ls=(0, (3, 3)))
    axes[1].text(80, len(ms) - 0.35, "80% cut-off", fontsize=7.5, color=INK2, ha="center")
    save(fig, "fig_screen")


# 2. Quantization: Q4 -> Q8 (-> BF16) per model
def fig_quant():
    fig, ax = plt.subplots(figsize=(5.2, 2.3))
    rows = D["stage2"]["rows"]
    ys = np.arange(len(rows))[::-1]
    for y, r in zip(ys, rows):
        c = colour(r["model"])
        ax.plot([r["q4"], r["q8"]], [y, y], color=GRID, lw=5, solid_capstyle="round", zorder=1)
        ax.scatter([r["q4"]], [y], s=60, facecolor="white", edgecolor=c, linewidth=2, zorder=3)
        ax.scatter([r["q8"]], [y], s=60, color=c, edgecolor="white", linewidth=1.5, zorder=4)
        d, lo, hi = r["diff"]
        ax.text(max(r["q4"], r["q8"]) + 2.5, y, ("Q4 and Q8 identical: " if d == 0 else "Q8 − Q4: ") + f"{d:+.1f} pts [{lo:+.1f}, {hi:+.1f}]", va="center",
                fontsize=8, color=INK)
    ax.set_yticks(ys, [r["model"] for r in rows])
    ax.set_xlim(50, 112)
    ax.set_xticks([50, 60, 70, 80, 90, 100])
    ax.set_xlabel("% of 106 test cases passed")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="white", mec=INK2, mew=2, label="Q4_K_M"),
                       Line2D([], [], marker="o", ls="", color=INK2, label="Q8_0")],
              loc="upper center", bbox_to_anchor=(0.45, -0.28), ncol=2, fontsize=8)
    ax.set_title("Stage 2: does 8-bit help? All three gaps are ties at n = 106")
    save(fig, "fig_quant")


# 3. Stage 3 head-to-head: pass and tool-call, 292 cases
def fig_h2h():
    runs = D["stage3"]["runs"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.5), sharey=True)
    ys = np.arange(len(runs))[::-1]
    for ax, key, title, xl in [(axes[0], "pass", "Cases passed", "% of 292 test cases (95% CI)"),
                               (axes[1], "tool", "Tool calls right", "% of 168 tool cases (95% CI)")]:
        for y, r in zip(ys, runs):
            v, lo, hi = r[key]
            dot_ci(ax, y, v, lo, hi, colour(r["name"]))
            ax.text(hi + 0.8, y, f"{v}%", va="center", fontsize=8, color=INK,
                    bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"), zorder=5)
        ax.set_xlim(50, 100)
        ax.set_title(title)
        ax.set_xlabel(xl)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(ys, [r["name"] for r in runs])
    axes[1].axvline(80, color=INK2, lw=1, ls=(0, (3, 3)))
    axes[1].text(80.6, len(runs) - 0.45, "80% cut-off", fontsize=7.5, color=INK2)
    save(fig, "fig_h2h")


# 4. Quality vs latency, with RAM
LABELS = {("Qwen3.5-4B Q4_K_M", "Vulkan"): (2, 84.3), ("Qwen3.5-4B Q4_K_M", "CPU"): (19, 84.3),
          ("Qwen3.5-2B Q8_0", "Vulkan"): (0.5, 77.6), ("Qwen3.5-2B Q8_0", "CPU"): (13, 77.6),
          ("Qwen3.5-2B BF16", "Vulkan"): (31, 76.6), ("Gemma 4 E2B Q8_0", "Vulkan"): (0.5, 66.4),
          ("Gemma 4 E2B Q8_0", "CPU"): (13, 66.4)}


def fig_tradeoff():
    passes = {r["name"]: r["pass"][0] for r in D["stage3"]["runs"]}
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    for s in D["stage4"]:
        c = colour(s["model"])
        y = passes[s["model"]] - (0.9 if s["model"] == "Qwen3.5-2B BF16" else 0)
        filled = s["backend"] == "Vulkan"
        ax.plot([s["median"], s["p90"]], [y, y], color=c, lw=1.2, alpha=0.45, zorder=1)
        ax.scatter([s["median"]], [y], s=40 + s["ram"] * 22, color=c if filled else "white", edgecolor=c,
                   linewidth=2, zorder=3)
        lab = f"{s['model'].replace(' Q4_K_M', ' Q4').replace(' Q8_0', ' Q8')}\n{s['backend']}, {s['ram']:.1f} GB"
        tx, ty = LABELS[(s["model"], s["backend"])]
        ax.annotate(lab, (s["median"], y), xytext=(tx, ty), fontsize=7, color=INK, va="center",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkA=0, shrinkB=6))
    ax.set_xlabel("Seconds per reply: dot = median, line runs to p90 (30-case subset)")
    ax.set_ylabel("% of 292 test cases passed")
    ax.set_xlim(0, 55)
    ax.set_ylim(64, 86)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=INK2, ms=7, label="Vulkan (iGPU)"),
                       Line2D([], [], marker="o", ls="", mfc="white", mec=INK2, mew=2, ms=7, label="CPU, 4 threads")],
              loc="lower right", fontsize=8, title="Dot size = peak RAM", title_fontsize=7.5)
    ax.set_title("Quality against waiting time: the 4B is best but slowest")
    save(fig, "fig_tradeoff")


# 5. Tool-call failure types
def fig_failures():
    f = D["failures"]
    names = ["Qwen3.5-4B Q4_K_M", "Qwen3.5-2B Q8_0", "Gemma 4 E2B Q8_0"]
    cols = [BLUE, ORANGE, AQUA, YELLOW]
    fig, ax = plt.subplots(figsize=(6.6, 2.0))
    ys = np.arange(len(names))[::-1]
    for y, n in zip(ys, names):
        left = 0
        for i, v in enumerate(f[n]):
            if v:
                ax.barh(y, v, left=left, color=cols[i], edgecolor="white", linewidth=2, height=0.6)
                if v >= 3:
                    ax.text(left + v / 2, y, str(v), ha="center", va="center", fontsize=8, color="white",
                            fontweight="bold")
            left += v
        ax.text(left + 1, y, f"{left} of 168", va="center", fontsize=8, color=INK)
    ax.set_yticks(ys, names)
    ax.set_xlim(0, 62)
    ax.set_xlabel("Missed tool cases, by type of miss")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=c) for c in cols], labels=f["types"], loc="upper center",
              bbox_to_anchor=(0.45, -0.32), ncol=2, fontsize=7.5)
    ax.set_title("Why tool calls miss: over-asking (4B) and missed staff calls (2B, Gemma)")
    save(fig, "fig_failures")


# 6. Category heatmap, Stage 3
def fig_heat():
    cats = ["Comparison", "Discovery", "Grounded\nQ&A", "Handoff", "Hinglish", "Refusal", "Tool\nselection"]
    runs = [r for r in D["stage3"]["runs"] if r["name"] != "Qwen3.5-2B BF16"]
    M = np.array([r["cats"] for r in runs])
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("b", ["#f3f7fd", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
    ax.imshow(M, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]}", ha="center", va="center", fontsize=8,
                    color="white" if M[i, j] >= 60 else INK)
    ax.set_xticks(range(len(cats)), cats, fontsize=8)
    ax.set_yticks(range(len(runs)), [r["name"] for r in runs], fontsize=8)
    ax.tick_params(length=0)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Pass rate (%) by category, Stage 3 test split: handoff is the weak spot for every model")
    save(fig, "fig_heat")


# 7. Rubric: per category and per rubric line
def fig_rubric():
    R = D["rubric"]
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 2.6), gridspec_kw={"width_ratios": [1, 1.5]})
    for ax, items, title in [(axes[0], R["cats"], "By category"), (axes[1], R["lines"], "Discovery rubric lines")]:
        keys = list(items)
        ys = np.arange(len(keys))[::-1]
        for y, k in zip(ys, keys):
            a, b = items[k]
            ax.plot([min(a, b), max(a, b)], [y, y], color=GRID, lw=5, solid_capstyle="round", zorder=1)
            ax.scatter([b], [y], s=50, color=ORANGE, edgecolor="white", linewidth=1.5, zorder=3)
            ax.scatter([a], [y], s=50, color=BLUE, edgecolor="white", linewidth=1.5, zorder=4)
        ax.set_yticks(ys, keys, fontsize=8)
        ax.set_xlim(3.0, 5.0)
        ax.set_xlabel("Mean judge score, 1–5")
        ax.set_title(title)
        ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.legend(handles=[Line2D([], [], marker="o", ls="", color=BLUE, label="Qwen3.5-4B Q4"),
                        Line2D([], [], marker="o", ls="", color=ORANGE, label="Qwen3.5-2B Q8")],
               loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=8)
    save(fig, "fig_rubric")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig_screen, fig_quant, fig_h2h, fig_tradeoff, fig_failures, fig_heat, fig_rubric):
        f()
    print("figures written to", OUT)
