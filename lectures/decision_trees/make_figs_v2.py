"""Generate the figures used by decision_trees_v2.md.

Run from this directory:  python3 make_figs_v2.py
Everything lands in figs_v2/.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs_v2")
os.makedirs(OUT, exist_ok=True)

POS = "#1f6feb"   # blue,  class +
NEG = "#d1620a"   # orange, class -
INK = "#222222"
FAINT = "#cccccc"

plt.rcParams.update({
    "font.size": 15,
    "svg.fonttype": "path",
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
})

# The running classification example.  Deliberately unsorted in both columns
# so that the "sort by the attribute" step has something to do.
DATA = [(2, 4, "+"), (7, 9, "+"), (6, 3, "-"), (1, 1, "+"), (9, 5, "-"), (3, 7, "+")]


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, bbox_inches="tight", transparent=True)
    plt.close(fig)
    print("wrote", path)


def glyph(ax, x, y, label, size=26):
    color = POS if label == "+" else NEG
    ch = "+" if label == "+" else "−"
    ax.text(x, y, ch, color=color, fontsize=size, fontweight="bold",
            ha="center", va="center", zorder=5)


def scatter_axes(figsize=(4.4, 4.4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xticks(range(0, 11, 2))
    ax.set_yticks(range(0, 11, 2))
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$", rotation=0, labelpad=12)
    ax.set_aspect("equal")
    ax.grid(True, color=FAINT, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    return fig, ax


# --------------------------------------------------------------------------
# 1. The raw data, plotted.
# --------------------------------------------------------------------------
def fig_data():
    fig, ax = scatter_axes()
    for x1, x2, y in DATA:
        glyph(ax, x1, x2, y)
    save(fig, "example_data.svg")


# --------------------------------------------------------------------------
# 2. Sorted number lines showing every candidate split point.
# --------------------------------------------------------------------------
def fig_sorted():
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 3.1))
    for ax, attr, name in zip(axes, (0, 1), ("$x_1$", "$x_2$")):
        rows = sorted(DATA, key=lambda r: r[attr])
        vals = [r[attr] for r in rows]
        ax.set_xlim(0, 10)
        ax.set_ylim(-1.1, 1.3)
        ax.axhline(0, color=INK, linewidth=1.2)
        ax.set_yticks([])
        ax.set_xticks([])
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.text(-0.35, 0, name, fontsize=17, ha="right", va="center")
        for (x1, x2, y), v in zip(rows, vals):
            ax.plot([v, v], [-0.16, 0.16], color=INK, linewidth=1.2)
            ax.text(v, -0.62, str(v), fontsize=14, ha="center", va="center")
            glyph(ax, v, 0.66, y, size=24)
        for a, b in zip(vals, vals[1:]):
            mid = (a + b) / 2
            ax.plot([mid, mid], [-0.95, 0.95], color="#888888",
                    linewidth=1.4, linestyle=(0, (4, 3)))
            txt = f"{mid:g}"
            ax.text(mid, 1.12, txt, fontsize=12, color="#666666",
                    ha="center", va="center")
    fig.text(0.5, 1.02, "candidate split points", fontsize=13,
             color="#666666", ha="center")
    fig.tight_layout()
    save(fig, "example_sorted.svg")


# --------------------------------------------------------------------------
# 3/4. The winning split, then the finished partition.
# --------------------------------------------------------------------------
def fig_partition(name, cuts, regions):
    fig, ax = scatter_axes()
    for (x0, y0, w, h, label) in regions:
        color = POS if label == "+" else NEG
        ax.add_patch(Rectangle((x0, y0), w, h, facecolor=color, alpha=0.10,
                               edgecolor="none", zorder=0))
    for kind, value, lo, hi in cuts:
        if kind == "v":
            ax.plot([value, value], [lo, hi], color=INK, linewidth=2.5, zorder=3)
            ax.text(value + 0.2, lo + 0.35, f"$x_1\\leq{value:g}$", fontsize=14,
                    ha="left", va="bottom")
        else:
            ax.plot([lo, hi], [value, value], color=INK, linewidth=2.5, zorder=3)
            ax.text(hi - 0.15, value + 0.25, f"$x_2\\leq{value:g}$", fontsize=14,
                    ha="right", va="bottom")
    for x1, x2, y in DATA:
        glyph(ax, x1, x2, y)
    save(fig, name)


# --------------------------------------------------------------------------
# 5. Tree diagrams.
# --------------------------------------------------------------------------
def node(ax, x, y, text, kind="internal", w=2.5, h=0.9):
    if kind == "internal":
        fc, ec, tc = "#ffffff", INK, INK
    elif kind == "pos":
        fc, ec, tc = "#e3edfd", POS, POS
    elif kind == "neg":
        fc, ec, tc = "#fbe9da", NEG, NEG
    else:
        fc, ec, tc = "#f2f2f2", "#999999", "#555555"
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.08,rounding_size=0.18",
                                facecolor=fc, edgecolor=ec, linewidth=2, zorder=3))
    ax.text(x, y, text, ha="center", va="center", fontsize=15, color=tc,
            zorder=4, linespacing=1.35)


def edge(ax, x0, y0, x1, y1, label, side="left"):
    ax.plot([x0, x1], [y0, y1], color=INK, linewidth=1.6, zorder=1)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    ax.text(mx + (-0.28 if side == "left" else 0.28), my, label, fontsize=13,
            color="#555555", ha="right" if side == "left" else "left",
            va="center", zorder=4,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none"))


def tree_axes(figsize, xlim, ylim):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def fig_tree_step1():
    fig, ax = tree_axes((5.6, 3.3), (-4.2, 4.2), (-2.6, 1.0))
    node(ax, 0, 0.5, "$x_1 \\leq 4.5$")
    edge(ax, -0.6, 0.1, -2.1, -1.5, "True")
    edge(ax, 0.6, 0.1, 2.1, -1.5, "False", side="right")
    node(ax, -2.1, -1.9, "3 +,  0 $-$\npure: leaf  +", kind="pos", h=1.2)
    node(ax, 2.1, -1.9, "1 +,  2 $-$\nrecurse", kind="other", h=1.2)
    save(fig, "example_tree_step1.svg")


def fig_tree_final():
    fig, ax = tree_axes((6.8, 4.4), (-4.6, 6.0), (-5.0, 1.2))
    node(ax, 0, 0.5, "$x_1 \\leq 4.5$")
    edge(ax, -0.6, 0.1, -2.4, -1.4, "True")
    edge(ax, 0.6, 0.1, 2.4, -1.4, "False", side="right")
    node(ax, -2.4, -1.8, "+\n(3 +, 0 $-$)", kind="pos", h=1.15)
    node(ax, 2.4, -1.8, "$x_2 \\leq 7$")
    edge(ax, 1.8, -2.3, 0.6, -3.6, "True")
    edge(ax, 3.0, -2.3, 4.2, -3.6, "False", side="right")
    node(ax, 0.6, -4.0, "$-$\n(0 +, 2 $-$)", kind="neg", h=1.15, w=2.3)
    node(ax, 4.2, -4.0, "+\n(1 +, 0 $-$)", kind="pos", h=1.15, w=2.3)
    save(fig, "example_tree_final.svg")


# --------------------------------------------------------------------------
# 6. Entropy and Gini on one set of axes.
# --------------------------------------------------------------------------
def fig_impurity_curves():
    p = np.linspace(1e-9, 1 - 1e-9, 500)
    ent = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
    gin = 2 * p * (1 - p)
    fig, ax = plt.subplots(figsize=(5.6, 3.8))
    ax.plot(p, ent, color=POS, linewidth=2.6, label="Entropy (bits)")
    ax.plot(p, gin, color=NEG, linewidth=2.6, label="Gini impurity")
    ax.set_xlabel("$p_+$  (fraction of the node that is  $+$)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.grid(True, color=FAINT, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(fontsize=12, loc="lower center", frameon=True, framealpha=1.0,
              edgecolor="none", facecolor="white")
    ax.annotate("maximally mixed", xy=(0.5, 1.0), xytext=(0.5, 1.02),
                fontsize=12, color="#666666", ha="center", va="bottom")
    fig.tight_layout()
    save(fig, "impurity_curves.svg")


# --------------------------------------------------------------------------
# 7. A ladder of nodes from pure to maximally mixed.
# --------------------------------------------------------------------------
def fig_impurity_scale():
    nodes = [(8, 0), (6, 2), (5, 3), (4, 4)]
    fig, ax = plt.subplots(figsize=(9.6, 3.0))
    ax.set_xlim(-0.6, len(nodes) * 2.6 - 0.4)
    ax.set_ylim(-1.9, 1.5)
    ax.axis("off")
    for i, (npos, nneg) in enumerate(nodes):
        cx = i * 2.6 + 0.6
        ax.add_patch(FancyBboxPatch((cx - 0.95, -0.55), 1.9, 1.5,
                                    boxstyle="round,pad=0.06,rounding_size=0.12",
                                    facecolor="white", edgecolor=INK,
                                    linewidth=1.8))
        seq = ["+"] * npos + ["-"] * nneg
        for k, ch in enumerate(seq):
            gx = cx - 0.62 + (k % 4) * 0.42
            gy = 0.62 - (k // 4) * 0.55
            glyph(ax, gx, gy, ch, size=22)
        m = npos + nneg
        pp = npos / m
        gini = 1 - pp ** 2 - (1 - pp) ** 2
        ent = 0.0 if pp in (0.0, 1.0) else -(pp * math.log2(pp) +
                                             (1 - pp) * math.log2(1 - pp))
        ax.text(cx, -0.95, f"Gini  {gini:.3f}", fontsize=14, ha="center",
                va="center", color=NEG)
        ax.text(cx, -1.45, f"Entropy  {ent:.3f}", fontsize=14, ha="center",
                va="center", color=POS)
    ax.annotate("", xy=(len(nodes) * 2.6 - 1.0, 1.25), xytext=(-0.2, 1.25),
                arrowprops=dict(arrowstyle="->", color="#888888", linewidth=1.6))
    ax.text(-0.2, 1.4, "pure", fontsize=13, color="#666666", ha="left")
    ax.text(len(nodes) * 2.6 - 1.0, 1.4, "maximally mixed", fontsize=13,
            color="#666666", ha="right")
    fig.tight_layout()
    save(fig, "impurity_scale.svg")


# --------------------------------------------------------------------------
# 8. The regression example.
# --------------------------------------------------------------------------
def fig_mse():
    xs = np.array([1, 2, 3, 4, 5, 6])
    ys = np.array([3, 5, 4, 12, 10, 14])
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.4), sharey=True)
    for ax, t, title in zip(axes, (None, 3.5),
                            ("Root: one leaf", "Split at $x \\leq 3.5$")):
        ax.scatter(xs, ys, s=110, color=POS, zorder=4)
        ax.set_xlim(0, 7)
        ax.set_ylim(0, 17)
        ax.set_xlabel("$x$")
        ax.set_title(title, fontsize=15)
        ax.grid(True, color=FAINT, linewidth=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        if t is None:
            groups = [(xs, ys, 0, 7)]
        else:
            m = xs <= t
            groups = [(xs[m], ys[m], 0, t), (xs[~m], ys[~m], t, 7)]
            ax.axvline(t, color="#888888", linewidth=1.6,
                       linestyle=(0, (4, 3)), zorder=2)
        for gx, gy, lo, hi in groups:
            mean = gy.mean()
            ax.plot([lo, hi], [mean, mean], color=NEG, linewidth=2.8, zorder=3)
            for px, py in zip(gx, gy):
                ax.plot([px, px], [py, mean], color=NEG, linewidth=1.2,
                        alpha=0.6, zorder=2)
            ax.text((lo + hi) / 2, 15.4, f"$\\hat{{y}}={mean:g}$",
                    fontsize=15, color=NEG, ha="center", va="center")
    axes[0].set_ylabel("$y$", rotation=0, labelpad=12)
    fig.tight_layout()
    save(fig, "mse_example.svg")


# --------------------------------------------------------------------------
# 9. Overfitting: unrestricted tree vs. depth-limited tree.
# --------------------------------------------------------------------------
def fig_overfit():
    from sklearn.tree import DecisionTreeClassifier
    rng = np.random.default_rng(7)
    n = 60
    xa = rng.normal([3.2, 3.2], 1.5, size=(n, 2))
    xb = rng.normal([6.8, 6.8], 1.5, size=(n, 2))
    X = np.vstack([xa, xb])
    y = np.r_[np.zeros(n), np.ones(n)]
    flip = rng.choice(len(y), 12, replace=False)
    y[flip] = 1 - y[flip]

    gx, gy = np.meshgrid(np.linspace(-1, 11, 400), np.linspace(-1, 11, 400))
    grid = np.c_[gx.ravel(), gy.ravel()]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.4))
    for ax, depth, title in zip(axes, (None, 3),
                                ("Grown until every leaf is pure",
                                 "max_depth = 3")):
        clf = DecisionTreeClassifier(max_depth=depth, random_state=0).fit(X, y)
        zz = clf.predict(grid).reshape(gx.shape)
        ax.contourf(gx, gy, zz, levels=[-0.5, 0.5, 1.5],
                    colors=[POS, NEG], alpha=0.14)
        ax.contour(gx, gy, zz, levels=[0.5], colors=[INK], linewidths=1.4)
        ax.scatter(X[y == 0, 0], X[y == 0, 1], s=45, color=POS, zorder=3)
        ax.scatter(X[y == 1, 0], X[y == 1, 1], s=45, color=NEG, marker="s",
                   zorder=3)
        ax.set_xlim(-1, 11)
        ax.set_ylim(-1, 11)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"{title}\n({clf.get_n_leaves()} leaves)", fontsize=15)
        ax.set_aspect("equal")
    fig.tight_layout()
    save(fig, "overfit.svg")


# --------------------------------------------------------------------------
# 10. Sensitivity to the orientation of the data.
# --------------------------------------------------------------------------
def fig_rotation():
    from sklearn.tree import DecisionTreeClassifier
    rng = np.random.default_rng(3)
    n = 60
    X = rng.uniform(-3, 3, size=(2 * n, 2))
    y = (X[:, 0] > 0).astype(float)
    X[:, 0] += np.where(y > 0, 0.06, -0.06)

    theta = np.pi / 4
    R = np.array([[math.cos(theta), -math.sin(theta)],
                  [math.sin(theta), math.cos(theta)]])
    Xr = X @ R.T

    gx, gy = np.meshgrid(np.linspace(-6, 6, 400), np.linspace(-6, 6, 400))
    grid = np.c_[gx.ravel(), gy.ravel()]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.4))
    for ax, XX, title in zip(axes, (X, Xr),
                             ("Original data", "Same data, rotated 45°")):
        clf = DecisionTreeClassifier(random_state=0).fit(XX, y)
        zz = clf.predict(grid).reshape(gx.shape)
        ax.contourf(gx, gy, zz, levels=[-0.5, 0.5, 1.5],
                    colors=[POS, NEG], alpha=0.14)
        ax.contour(gx, gy, zz, levels=[0.5], colors=[INK], linewidths=1.4)
        ax.scatter(XX[y == 0, 0], XX[y == 0, 1], s=40, color=POS, zorder=3)
        ax.scatter(XX[y == 1, 0], XX[y == 1, 1], s=40, color=NEG, marker="s",
                   zorder=3)
        ax.set_xlim(-6, 6)
        ax.set_ylim(-6, 6)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")
        ax.set_title(f"{title}\n({clf.get_n_leaves()} leaves)", fontsize=15)
    fig.tight_layout()
    save(fig, "rotation.svg")


if __name__ == "__main__":
    fig_data()
    fig_sorted()
    fig_partition("example_split1.svg",
                  cuts=[("v", 4.5, 0, 10)],
                  regions=[])
    fig_partition("example_final.svg",
                  cuts=[("v", 4.5, 0, 10), ("h", 7, 4.5, 10)],
                  regions=[(0, 0, 4.5, 10, "+"),
                           (4.5, 0, 5.5, 7, "-"),
                           (4.5, 7, 5.5, 3, "+")])
    fig_tree_step1()
    fig_tree_final()
    fig_impurity_curves()
    fig_impurity_scale()
    fig_mse()
    fig_overfit()
    fig_rotation()
