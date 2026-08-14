#!/usr/bin/env python3
"""Gallery: what each mutation regime does to the SAME disordered starting points.

One column per run. The top row is the seed that run began from; the rows below are what each
mutation regime evolved it into. Because the seeds are shared down each column, the columns are
paired comparisons and the differences between rows are attributable to the move set alone.

Every panel is a weight matrix: rows are hidden units, columns are input positions, a cell is filled
when that unit reads that input, and colour is the weight group. A convolution is one colour on a
regular band (a circulant matrix); panels that meet the definition are outlined.

Usage:  /home/vas/.venv-figs/bin/python fig_gallery.py scratch_gallery.out
Writes: fig_gallery.pdf and .png
"""
import sys, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

K = 3
NCOL = 8                    # runs shown

PALETTE = ["#3B6DB0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
           "#937860", "#DA8BC3", "#7F7F7F", "#CCB974", "#64B5CD",
           "#B07AA1", "#59A14F"]
EMPTY = "#F2F2F2"
CONV_EDGE = "#1A7F37"


def parse(path):
    """Return {arm: [(seed_genome, evolved_genome, is_conv), ...]}."""
    arms, cur, pending = {}, None, None
    for line in open(path):
        line = line.strip()
        if line.startswith("ARM "):
            cur = line[4:].strip(); arms.setdefault(cur, []); pending = None
        elif line.startswith("SEED0 "):
            pending = line.split()[1]
        elif line.startswith("GENOME ") and cur is not None:
            m = re.match(r"GENOME (\S+) conv=(\d+)", line)
            if m and pending is not None:
                arms[cur].append((pending, m.group(1), int(m.group(2))))
                pending = None
    return arms


def cell(ax, genome, outline=False):
    n = len(genome)
    letters = sorted({c for c in genome if c != "."})
    cidx = {ch: PALETTE[k % len(PALETTE)] for k, ch in enumerate(letters)}
    for r in range(n):
        for c in range(n):
            ax.add_patch(Rectangle((c, n - 1 - r), 1, 1, fc=EMPTY, ec="white", lw=0.35))
    for p, ch in enumerate(genome):
        if ch == ".":
            continue
        for k in range(K):
            ax.add_patch(Rectangle(((p + k) % n, n - 1 - p), 1, 1,
                                   fc=cidx[ch], ec="white", lw=0.35))
    ax.set_xlim(0, n); ax.set_ylim(0, n); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor(CONV_EDGE if outline else "#CCCCCC")
        sp.set_linewidth(2.4 if outline else 0.6)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "scratch_gallery.out"
    arms = parse(path)

    def find(needle):
        for label, rows in arms.items():
            if needle in label and rows:
                return rows
        raise SystemExit(f"arm not found: {needle!r}\navailable: {list(arms)}")

    ctrl, grow, tile = find("CONTROL"), find("CRYSTAL GROWTH"), find("fixed low rate")
    total = min(len(ctrl), len(grow), len(tile))
    n = min(NCOL, total)
    # Systematic sample at a regular stride across all runs, rather than the first few. The first
    # seven runs happen to contain no tandem-duplication success (its rate is 17%), so showing them
    # would understate that row; an evenly spaced sample gives every arm its natural chance and
    # involves no choice about which runs to display.
    idx = [round(i * (total - 1) / (n - 1)) for i in range(n)] if n > 1 else [0]

    rate = lambda rows: sum(r[2] for r in rows) / len(rows)
    rows_spec = [
        ("Started from\n(disordered seed)", [(ctrl[i][0], 0) for i in idx], None),
        (f"Per-site mutation\n{rate(ctrl):.0%} convolutions",
         [(ctrl[i][1], ctrl[i][2]) for i in idx], rate(ctrl)),
        (f"+ tandem duplication\n(local copying)  {rate(grow):.0%}",
         [(grow[i][1], grow[i][2]) for i in idx], rate(grow)),
        (f"+ segment repeat\n(global copying)  {rate(tile):.0%}",
         [(tile[i][1], tile[i][2]) for i in idx], rate(tile)),
    ]

    fig, axes = plt.subplots(len(rows_spec), n, figsize=(1.62 * n + 2.1, 1.62 * len(rows_spec) + 1.5))
    for ri, (label, items, _) in enumerate(rows_spec):
        for ci in range(n):
            ax = axes[ri][ci]
            genome, is_conv = items[ci]
            cell(ax, genome, outline=bool(is_conv))
            if ri == 0:
                ax.set_title(f"run {idx[ci] + 1}", fontsize=8.5, color="#555555", pad=4)
        axes[ri][0].set_ylabel(label, fontsize=9.2, fontweight="bold",
                               rotation=0, ha="right", va="center", labelpad=14)

    fig.suptitle("Same seeds, four move sets. Colour collapses everywhere; only copying closes the band.",
                 fontsize=12.5, fontweight="bold", y=0.985)
    fig.text(0.5, 0.022,
             "Each panel is a weight matrix (rows: hidden units, columns: input positions); colour is the "
             "weight group, so one colour means one shared filter.\nColumns share a seed, so differences "
             "down a column are due to the move set alone. Green outline: meets the definition of a "
             "convolution.",
             ha="center", fontsize=8.4, color="#444444")
    fig.tight_layout(rect=[0.02, 0.055, 1, 0.94])
    for ext in ("pdf", "png"):
        fig.savefig(f"fig_gallery.{ext}", dpi=185, bbox_inches="tight")
    print("wrote fig_gallery.pdf / .png")


if __name__ == "__main__":
    main()
