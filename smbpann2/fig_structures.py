#!/usr/bin/env python3
"""Draw the four connectivity structures as WEIGHT MATRICES.

Rows are hidden units (indexed by the position they read from), columns are input positions.
A cell is filled when that unit reads that input, and coloured by the weight group it uses, so
the same colour means literally the same weight.

This is the standard representation for the question at hand: a convolution is a circulant
Toeplitz matrix, one colour, constant along each diagonal, wrapping at the corner. Weight sharing
shows up as colour uniformity; the tiling shows up as an unbroken regular band. The two properties
the paper separates are therefore two visually independent features of the same picture.

Input: the GENOME lines emitted by `DUMP=1 ./emerge_tile`, e.g.
    ARM (1) CONTROL... | E_param (per group)
    GENOME a.bb.c..dd. conv=0 groups=4 places=7

Usage:  /home/vas/.venv-figs/bin/python fig_structures.py scratch_pool_main.out
Writes: fig_structures.pdf and .png
"""
import sys, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

K = 3                       # kernel width, must match the probe
SEED_SHOWN = 0

PALETTE = ["#3B6DB0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
           "#937860", "#DA8BC3", "#7F7F7F", "#CCB974", "#64B5CD",
           "#B07AA1", "#59A14F"]
EMPTY = "#F2F2F2"


def parse(path):
    arms, cur = {}, None
    for line in open(path):
        line = line.strip()
        if line.startswith("ARM "):
            cur = line[4:].strip()
            arms.setdefault(cur, [])
        elif line.startswith("GENOME ") and cur is not None:
            m = re.match(r"GENOME (\S+) conv=(\d+) groups=(\d+) places=(\d+)", line)
            if m:
                arms[cur].append((m.group(1), int(m.group(2)),
                                  int(m.group(3)), int(m.group(4))))
    return arms


def draw(ax, genome, title, subtitle):
    n = len(genome)
    letters = sorted({c for c in genome if c != "."})
    cidx = {ch: PALETTE[k % len(PALETTE)] for k, ch in enumerate(letters)}

    for r in range(n):                       # background grid
        for c in range(n):
            ax.add_patch(Rectangle((c, n - 1 - r), 1, 1, fc=EMPTY, ec="white", lw=0.7))

    for p, ch in enumerate(genome):          # a unit at p reads inputs p, p+1, p+2 (mod n)
        if ch == ".":
            continue
        for k in range(K):
            c = (p + k) % n
            ax.add_patch(Rectangle((c, n - 1 - p), 1, 1, fc=cidx[ch], ec="white", lw=0.7))

    ax.set_xlim(0, n); ax.set_ylim(0, n); ax.set_aspect("equal")
    ax.set_xticks([0.5, n - 0.5]); ax.set_xticklabels(["0", str(n - 1)], fontsize=8)
    ax.set_yticks([0.5, n - 0.5]); ax.set_yticklabels([str(n - 1), "0"], fontsize=8)
    ax.set_xlabel("input position", fontsize=8.5)
    ax.set_ylabel("hidden unit", fontsize=8.5)
    for sp in ax.spines.values():
        sp.set_edgecolor("#BBBBBB"); sp.set_linewidth(0.8)
    ax.set_title(title, fontsize=11.5, fontweight="bold", pad=8)
    ax.text(n / 2, -3.1, subtitle, ha="center", va="top", fontsize=8.6, color="#333333")


def pick(arms, needle, seed=SEED_SHOWN, want_conv=False):
    """Return (row, rate). With want_conv, return the first run that produced a convolution,
    plus the fraction of runs in that arm that did."""
    for label, rows in arms.items():
        if needle in label and rows:
            rate = sum(r[1] for r in rows) / len(rows)
            if want_conv:
                for r in rows:
                    if r[1]:
                        return r, rate
            return rows[min(seed, len(rows) - 1)], rate
    raise SystemExit(f"arm not found in dump: {needle!r}\navailable: {list(arms)}")


def disordered_seed(n=12, rng_seed=7):
    """One draw from the seed distribution actually used: each position occupied with probability 1/2,
    each occupied position given a random filter. Drawn here rather than read from the dump because the
    seed is random by construction, so no single run's seed is more representative than another."""
    rng = np.random.default_rng(rng_seed)
    out = []
    for _ in range(n):
        out.append(chr(ord('a') + int(rng.integers(0, n))) if rng.random() < 0.5 else ".")
    return "".join(out)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "scratch_final2_main.out"
    arms = parse(path)

    seed_g       = disordered_seed()
    conv, _      = pick(arms, "CONVOLUTION")
    ctrl, r_ctrl = pick(arms, "CONTROL")
    grow, r_grow = pick(arms, "CRYSTAL GROWTH", want_conv=True)
    tile, r_tile = pick(arms, "fixed low rate", want_conv=True)

    ngroups = len({c for c in seed_g if c != "."})
    seed_row = (seed_g, 0, ngroups, sum(1 for c in seed_g if c != "."))

    panels = [
        (seed_row, "Started from",
         "disordered seed: random subset\nof positions, random filters.\nNo order at generation zero"),
        (conv, "Aiming at",
         "convolution: one filter on a\nregular stride. A circulant matrix,\nconstant along each diagonal"),
        (ctrl, "Per-site mutation",
         f"undirected edits. Colour collapses,\nthe band never forms:\n{r_ctrl:.0%} of 200 runs"),
        (grow, "+ tandem duplication",
         f"LOCAL copying, one unit at a time,\nat the existing spacing:\n{r_grow:.0%} of 200 runs"),
        (tile, "+ segment repeat",
         f"GLOBAL copying, whole-genome\nperiod rewrite:\n{r_tile:.0%} of 200 runs"),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(18.0, 4.7))
    for ax, (row, title, sub) in zip(axes, panels):
        genome, conv_f, groups, places = row
        tag = f"{genome}\ngroups={groups}  units={places}"
        draw(ax, genome, title, sub + "\n\n" + tag)

    fig.suptitle("Filters merge under any mutation. A regular placement appears only when the move copies "
                 "\u2014 and it need not copy globally.",
                 fontsize=12.5, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0.06, 1, 0.93])
    for ext in ("pdf", "png"):
        fig.savefig(f"fig_structures.{ext}", dpi=190, bbox_inches="tight")
    print("wrote fig_structures.pdf / .png")


if __name__ == "__main__":
    main()
