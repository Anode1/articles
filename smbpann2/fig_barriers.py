#!/usr/bin/env python
"""fig_barriers.py -- the paper-2 result figure: two measurement repairs and what they buy.

Every number is measured, from probes archived in ~/smbpann as scratch_*.out:
  panel a  scratch_rot_diag_r{0,1}.out       DIAG exchangeability lines
  panel b  scratch_rot_r{0,1}_f{1,12}.out    20 seeds, LAMBDA=1, flip-only, paired vs ideal
  panel c  scratch_fact_r0_f1_lam1.out,      LAMBDA=1 cells at 60 seeds;
           scratch_fact_r1_f12_lam1.out,     LAMBDA=6 cells at 240 seeds from
           scratch_big_{nofix,fixed}_s*.out  (heights are RATES, denominators differ)
  panel d  scratch_subscan_hi_lam{1,6}.out   127-support enumeration, 12 draws x 60 seeds,
           scratch_gate_lam{2,3,4,8,10}.out  margins and their standard error

Run with /home/vas/.venv-figs/bin/python (system python3 has no matplotlib).
Palette: dataviz categorical slots 1 and 2, unchanged; validated for normal vision
(dE 33.6), dichromacy (worst dE 26.5) and greyscale print (luminance gap 0.090).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

NOFIX, FIXED, MID = "#eb6834", "#2a78d6", "#a8a7a1"
INK, INK2, INK3, RULE = "#0b0b0b", "#52514e", "#84837c", "#d9d8d2"

plt.rcParams.update({
    "text.usetex": False, "axes.formatter.use_mathtext": True,
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.edgecolor": INK3, "axes.linewidth": 0.6, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "figure.facecolor": "white", "axes.facecolor": "white",
})

def frame(ax, ygrid=True):
    """Recessive axes: no top/right spine, hairline y grid behind the marks."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if ygrid:
        ax.yaxis.grid(True, color=RULE, lw=0.5)
        ax.set_axisbelow(True)

def panel_label(ax, s, x=-0.13):
    ax.text(x, 1.10, s, transform=ax.transAxes, fontsize=9.5,
            fontweight="bold", va="top", ha="left", color=INK)

fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.4))
fig.subplots_adjust(left=0.085, right=0.985, top=0.9, bottom=0.085,
                    wspace=0.28, hspace=0.62)

# ---- (a) the mechanism: the selection split was biased ----------------------
ax = axes[0][0]; frame(ax)
vals = [0.0312, -0.0140]
bars = ax.bar([0, 1], vals, width=0.5, color=[NOFIX, FIXED], zorder=3)
ax.axhline(0, color=INK3, lw=0.8, zorder=4)
ax.set_xticks([0, 1])
ax.set_xticklabels(["selection positions\nheld fixed", "selection positions\nrotated"])
ax.set_ylabel("excess of report gap over\nselection gap")
ax.set_ylim(-0.03, 0.045)
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v + (0.003 if v > 0 else -0.003),
            f"{v:+.4f}", ha="center", va="bottom" if v > 0 else "top",
            fontsize=8, color=INK)
ax.text(0.5, 0.0055, "exchangeability implies zero", transform=ax.get_yaxis_transform(),
        ha="left", va="bottom", fontsize=7, color=INK3, style="italic")
ax.set_title("The search was overfitting which positions\nit had to transfer to",
             fontsize=8.5, color=INK, loc="left", pad=6)
panel_label(ax, "a")

# ---- (b) function converges -------------------------------------------------
ax = axes[0][1]; frame(ax)
lab = ["baseline", "rotation\nonly", "averaging\nonly", "both\nrepairs"]
val = [0.0571, 0.0290, 0.0090, -0.0013]
col = [NOFIX, MID, MID, FIXED]
bars = ax.bar(range(4), val, width=0.55, color=col, zorder=3)
ax.axhline(0, color=INK3, lw=0.8, zorder=4)
ax.set_xticks(range(4)); ax.set_xticklabels(lab)
ax.set_ylabel("held-out transfer deficit\nvs the built convolution")
ax.set_ylim(-0.015, 0.081)
for b, v in zip(bars, val):
    ax.text(b.get_x() + b.get_width()/2, v + (0.002 if v > 0 else -0.002),
            f"{v:+.3f}", ha="center", va="bottom" if v > 0 else "top",
            fontsize=7.5, color=INK)
ax.annotate("", xy=(2.85, 0.0690), xytext=(0.2, 0.0690),
            arrowprops=dict(arrowstyle="->", color=INK3, lw=0.7))
ax.text(1.5, 0.0715, "significant deficit  →  indistinguishable", ha="center",
        fontsize=7, color=INK2)
ax.set_title("Repairing the signal closes the functional gap\ncompletely",
             fontsize=8.5, color=INK, loc="left", pad=6)
panel_label(ax, "b")

# ---- (c) structure emerges: the headline ------------------------------------
ax = axes[1][0]; frame(ax)
# Rates, not counts: the lambda=1 cells ran 60 seeds and the lambda=6 cells 240, so raw heights
# would not be comparable between groups. Counts are given in the labels.
cnt   = {"nofix": [(1, 60), (16, 240)], "fixed": [(2, 60), (42, 240)]}
pct   = {k: [100.0*a/b for a, b in v] for k, v in cnt.items()}
x = [0, 1]; w = 0.34
b1 = ax.bar([i - w/2 - 0.012 for i in x], pct["nofix"], width=w, color=NOFIX,
            zorder=3, label="no repairs")
b2 = ax.bar([i + w/2 + 0.012 for i in x], pct["fixed"], width=w, color=FIXED,
            zorder=3, label="both repairs")
for key, bars in (("nofix", b1), ("fixed", b2)):
    for (n, d), b in zip(cnt[key], bars):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.55,
                f"{n}/{d}", ha="center", fontsize=7.5, color=INK)
ax.set_xticks(x)
ax.set_xticklabels(["$\\lambda = 1$\n(target rank 4)", "$\\lambda = 6$\n(target rank 1, 2.3 SE)"])
ax.set_ylabel("exact recovery of the planted\nconvolution  (% of runs)")
ax.set_ylim(0, 25)
ax.legend(frameon=False, fontsize=7.5, loc="upper left", handlelength=1.1,
          labelcolor=INK2, borderpad=0.2)
xl, xr, yb = 1 - w/2 - 0.012, 1 + w/2 + 0.012, 21.2          # bracket over the lam=6 pair
ax.plot([xl, xl, xr, xr], [yb - 0.5, yb, yb, yb - 0.5], color=INK3, lw=0.7, zorder=4)
ax.text(1.0, yb + 0.45, "McNemar $p = 7\\times10^{-5}$", ha="center", fontsize=7, color=INK2)
ax.text(0.02, 0.52, "tap-matched random null:\n1 of 240 at $\\lambda=6$",
        transform=ax.transAxes, fontsize=7, color=INK3, style="italic")
ax.set_title("Exact recovery of the planted structure",
             fontsize=8.5, color=INK, loc="left", pad=6)
panel_label(ax, "c")

# ---- (d) the tariff window: where the objective prefers the planted support ---
ax = axes[1][1]; frame(ax)
lam  = [1, 2, 3, 4, 6, 8, 10]
marg = [-0.0085, -0.0037, 0.0011, 0.0058, 0.0111, 0.0111, 0.0019]
se   = 0.0048
xs   = list(range(len(lam)))                 # categorical spacing; lambda is not linear here
resolved = [abs(m) >= 2*se and m > 0 for m in marg]
ax.axhline(0, color=INK3, lw=0.8, zorder=2)
ax.axhspan(-2*se, 2*se, color=RULE, alpha=0.55, zorder=1, lw=0)
ax.plot(xs, marg, "-", color=INK3, lw=1.0, zorder=3)
for xi, m, r in zip(xs, marg, resolved):
    ax.errorbar([xi], [m], yerr=[se], fmt="o", ms=7 if r else 5,
                color=INK if r else "white", ecolor=INK3, elinewidth=0.9,
                capsize=2.5, markeredgecolor=INK, markeredgewidth=1.0, zorder=4)
ax.set_xticks(xs); ax.set_xticklabels([str(l) for l in lam])
ax.set_xlabel("tariff $\\lambda$")
ax.set_ylabel("planted support's margin over\nits best rival of 127")
ax.set_xlim(-0.5, len(lam) - 0.5); ax.set_ylim(-0.021, 0.0205)
ax.text(4.5, 0.0172, "resolved", ha="center", fontsize=7, color=INK)
ax.text(0.35, -0.0182, "planted support is not the argmax", fontsize=7,
        color=INK3, style="italic")
ax.text(len(lam) - 0.55, 0.0188, "band $\\pm$2 SE; filled = margin clears it",
        ha="right", fontsize=6.5, color=INK3)
ax.set_title("The objective prefers the planted width only\nin a band, peaking at $\\lambda\\in[6,8]$",
             fontsize=8.5, color=INK, loc="left", pad=6)
panel_label(ax, "d")

for ext in ("pdf", "png"):
    fig.savefig(f"fig_barriers.{ext}", dpi=300,
                bbox_inches="tight", facecolor="white")
print("wrote fig_barriers.pdf and fig_barriers.png")
