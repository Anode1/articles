#!/usr/bin/env python3
"""Paired analysis of emerge_gen2 arms, at the level a hostile reviewer would ask for.

Arms share task seeds, so every comparison is paired and is analysed as such. For each comparison
we report:

  - the paired difference with a bootstrap 95% CI (interpretable, unlike a p-value);
  - Wilcoxon signed-rank (non-parametric, since these distributions are skewed) and a paired t as
    a secondary check;
  - the effect normalised to the floor-to-ceiling gap measured on the SAME tasks, so "closes 40% of
    the gap" means something;
  - for every claim of NO effect, a TOST equivalence test against a pre-specified margin. A large
    p-value does not establish absence; TOST does, or fails to, and says which;
  - the minimum effect the comparison could have detected at 80% power, so a null is bounded.

Multiplicity: one primary comparison is declared in advance (visibility); the rest are secondary and
carry a Holm correction across the secondary family.

Usage: /home/vas/.venv-figs/bin/python analyse.py
"""
import re, glob, math, os
from statistics import mean, median, stdev

RAW = "/home/vas/smbpann"
PREFIX = "scratch_st2_"     # set to scratch_st_ for the n=60 pilot
EQUIV_MARGIN = 0.05      # pre-specified: differences below 5 accuracy points are declared negligible
BOOT = 20000
PRIMARY = "visibility: selection sees 4 extra positions"


def load(path):
    """Return (per-seed evolved accuracies, per-seed reference (conv, lc)) keyed by seed."""
    ev, ref = {}, {}
    for line in open(path):
        m = re.match(r"SEED (\d+) acc ([\d.]+) places (\d+) groups (\d+)", line)
        if m:
            # the probe prints the GA seed, which is task_index*7+1; invert it so evolved rows and
            # reference rows key on the same task and the comparison is genuinely paired
            ev[(int(m.group(1)) - 1) // 7] = float(m.group(2))
        m = re.match(r"REF (\d+) conv ([\d.]+) lc ([\d.]+)", line)
        if m:
            ref[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    return ev, ref


def wilcoxon(d):
    """Two-sided Wilcoxon signed-rank, normal approximation with tie and continuity correction."""
    nz = [x for x in d if x != 0.0]
    n = len(nz)
    if n < 6:
        return float("nan")
    order = sorted(range(n), key=lambda i: abs(nz[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(nz[order[j + 1]]) == abs(nz[order[i]]):
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    wp = sum(ranks[i] for i in range(n) if nz[i] > 0)
    mu = n * (n + 1) / 4.0
    sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    if sd == 0:
        return float("nan")
    z = (abs(wp - mu) - 0.5) / sd
    return math.erfc(z / math.sqrt(2))


def ttest_paired(d):
    n = len(d)
    if n < 3:
        return float("nan"), float("nan")
    m, s = mean(d), stdev(d)
    if s == 0:
        return float("inf"), 0.0
    t = m / (s / math.sqrt(n))
    return t, math.erfc(abs(t) / math.sqrt(2))      # normal approx, fine at n=60


def boot_ci(d, reps=BOOT, seed=12345):
    """Percentile bootstrap CI of the mean paired difference. Deterministic LCG, no numpy needed."""
    n = len(d)
    st = seed
    out = []
    for _ in range(reps):
        tot = 0.0
        for _ in range(n):
            st = (1103515245 * st + 12345) & 0x7FFFFFFF
            tot += d[(st >> 16) % n]      # high bits: an LCG's low bits cycle with period n
        out.append(tot / n)
    out.sort()
    return out[int(0.025 * reps)], out[int(0.975 * reps)]


def tost(d, margin=EQUIV_MARGIN):
    """Two one-sided tests. Equivalence is established when BOTH one-sided tests reject, i.e. the
    90% CI of the difference lies entirely inside (-margin, +margin)."""
    n = len(d)
    m, s = mean(d), stdev(d)
    se = s / math.sqrt(n)
    if se == 0:
        return 0.0, abs(m) < margin
    t_lo = (m + margin) / se        # H0: diff <= -margin
    t_hi = (margin - m) / se        # H0: diff >= +margin
    p_lo = math.erfc(t_lo / math.sqrt(2)) / 2 if t_lo > 0 else 1.0
    p_hi = math.erfc(t_hi / math.sqrt(2)) / 2 if t_hi > 0 else 1.0
    p = max(p_lo, p_hi)
    return p, p < 0.05


def mde(d, power=0.80, alpha=0.05):
    """Minimum detectable effect at the given power, in accuracy points."""
    s = stdev(d) if len(d) > 2 else float("nan")
    return (1.96 + 0.84) * s / math.sqrt(len(d))


def holm(pvals):
    idx = sorted(range(len(pvals)), key=lambda i: pvals[i])
    out = [0.0] * len(pvals)
    prev = 0.0
    for rank, i in enumerate(idx):
        adj = min(1.0, (len(pvals) - rank) * pvals[i])
        prev = max(prev, adj)
        out[i] = prev
    return out


def describe(name, xs, halfway=None):
    """These distributions are bimodal: many tasks land near chance and many near solved. A mean of a
    two-lump distribution describes neither lump, so the median, the inter-quartile range and the
    fraction of tasks actually solved are reported alongside it."""
    xs = sorted(xs)
    n = len(xs)
    q1, q3 = xs[n // 4], xs[(3 * n) // 4]
    lo = sum(1 for x in xs if x < 0.60)
    solved = f"{100*sum(1 for x in xs if x >= halfway)/n:3.0f}%" if halfway else "  . "
    print(f"  {name:<32} n={n:<4} mean {mean(xs):.3f}  median {median(xs):.3f}  "
          f"IQR [{q1:.3f},{q3:.3f}]  near-chance {100*lo/n:3.0f}%  solved {solved}")


def boot_median(d, reps=4000, seed=999):
    n, st, out = len(d), seed, []
    for _ in range(reps):
        samp = []
        for _ in range(n):
            st = (1103515245 * st + 12345) & 0x7FFFFFFF
            samp.append(d[(st >> 16) % n])
        out.append(median(samp))
    out.sort()
    return out[int(0.025 * reps)], out[int(0.975 * reps)]


def compare(label, a_ev, b_ev, ref, primary=False):
    seeds = sorted(set(a_ev) & set(b_ev) & set(ref))
    d = [b_ev[s] - a_ev[s] for s in seeds]
    gap = [ref[s][0] - ref[s][1] for s in seeds]
    m = mean(d)
    hl = median(d)                      # Hodges-Lehmann: the location estimate Wilcoxon actually tests
    hl_lo, hl_hi = boot_median(d)
    lo, hi = boot_ci(d)
    pw = wilcoxon(d)
    _, pt = ttest_paired(d)
    p_eq, equiv = tost(d)
    frac = m / mean(gap)
    return dict(label=label, n=len(seeds), diff=m, lo=lo, hi=hi, pw=pw, pt=pt, hl=hl,
                hl_lo=hl_lo, hl_hi=hl_hi,
                p_eq=p_eq, equiv=equiv, frac=frac, mde=mde(d), primary=primary)


def main():
    arms = {}
    for f in glob.glob(os.path.join(RAW, PREFIX + "*.out")):
        key = os.path.basename(f)[len(PREFIX):-len(".out")]
        ev, ref = load(f)
        if ev:
            arms[key] = (ev, ref)
    if not arms:
        raise SystemExit("no scratch_st_*.out with per-seed dumps found")

    print("DISTRIBUTIONS  (bimodal: mean, median, IQR, and fraction solved all reported)\n")
    any_ref = next(iter(arms.values()))[1]
    halfway = None
    if any_ref:
        cs = [v[0] for v in any_ref.values()]
        ls = [v[1] for v in any_ref.values()]
        halfway = (median(cs) + median(ls)) / 2.0     # "solved" = past the midpoint of floor and ceiling
        describe("reference: convolution", cs, halfway)
        describe("reference: locally connected", ls, halfway)
        print()
    for k in sorted(arms):
        describe(f"evolved: {k}", list(arms[k][0].values()), halfway)

    comps = []
    if "vis0" in arms and "vis4" in arms:
        comps.append(compare(PRIMARY, arms["vis0"][0], arms["vis4"][0], arms["vis0"][1], primary=True))
    for a, b, lab in [("base", "op2", "add units, copying NOTHING"),
                      ("op2",  "op3", "same, but copy the FILTER"),
                      ("op3",  "op1", "same, but also copy the SPACING"),
                      ("op3",  "op4", "same, but go GLOBAL"),
                      ("base", "vis0", "raise the addition rate instead of adding an operator"),
                      ("vis0", "op3", "dedicated copying operator vs matched addition rate")]:
        if a in arms and b in arms:
            comps.append(compare(lab, arms[a][0], arms[b][0], arms[a][1]))

    sec = [c for c in comps if not c["primary"]]
    if sec:
        adj = holm([c["pw"] for c in sec])
        for c, p in zip(sec, adj):
            c["pw_adj"] = p

    print("\n\nPAIRED COMPARISONS  (difference = second arm minus first, in accuracy points)\n")
    for c in comps:
        tag = "PRIMARY  " if c["primary"] else "secondary"
        print(f"  [{tag}] {c['label']}")
        print(f"      median diff {c['hl']:+.4f}  95% CI [{c['hl_lo']:+.4f}, {c['hl_hi']:+.4f}]   (Hodges-Lehmann)")
        print(f"      mean   diff {c['diff']:+.4f}  95% CI [{c['lo']:+.4f}, {c['hi']:+.4f}]   "
              f"n={c['n']}   closes {100*c['frac']:+.0f}% of the gap")
        padj = f"   Holm-adj {c['pw_adj']:.3g}" if "pw_adj" in c else ""
        print(f"      Wilcoxon p {c['pw']:.3g}   paired-t p {c['pt']:.3g}{padj}")
        pw = c["pw"] if c["pw"] == c["pw"] else 1.0        # nan -> treat as not significant
        verdict = ("EQUIVALENT within +-%.2f" % EQUIV_MARGIN) if c["equiv"] else \
                  ("not equivalent, and not shown different (underpowered)" if pw > 0.05 else "DIFFERENT")
        print(f"      TOST p {c['p_eq']:.3g}  ->  {verdict}")
        print(f"      minimum detectable effect at 80% power: {c['mde']:.3f}\n")

    print("Reading these: a null claim is only supported when TOST says EQUIVALENT. A large Wilcoxon")
    print("p with a failed TOST means the comparison is underpowered and the arm should not be")
    print(f"described as having no effect. Equivalence margin was fixed at {EQUIV_MARGIN} before running.")


if __name__ == "__main__":
    main()
