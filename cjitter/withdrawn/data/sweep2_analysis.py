"""The analysis for sweep2: a 101-seed panel, both clearance arms, with the reference
layouts scored.

Three things this can answer that the five-seed record could not.

  1. Per-instance effects with their own uncertainty. At five seeds the within-instance sign
     test reaches 0.05 only on a clean sweep, so every per-instance verdict was a 5-bit
     measurement. At 101 seeds the win probability against the control carries a binomial
     interval of about +/- 0.10, and the across-instance test can run on those instead of on
     a median of five draws.
  2. Whether the repair correction or the clearance change carried the difference. The
     commit that fixed the repair also moved the clearance the repair keeps from 0 to 12,
     so the corrected sweep optimizes a different feasible set. The gap 0 arm separates them.
  3. The pre-registered secondary on the feasibility pair (C, P), which could not be
     computed on block_results_fixed.csv because the centroid and human rows were never
     written there.

Exact tests are imported from corrected_analysis so both scripts share one implementation,
and that one is validated against the published record before it is used anywhere.
"""
import csv, os, sys
from collections import defaultdict
from math import comb

from corrected_analysis import wilcoxon, hodges_lehmann, median, sign_one_sided, holm

HERE = os.path.dirname(os.path.abspath(__file__))
METHODS = ['random', 'climb', 'anneal', 'ga']
PRIMARY = 8000
SHIPPED_GAP = 12.0


def load(path):
    runs, meta, feas = defaultdict(dict), {}, {}
    for row in csv.reader(open(path)):
        if not row or row[0].startswith('#'):
            continue
        if row[0] == 'run':
            _, p, gap, m, blk, b, s, v = row
            runs[(int(p), float(gap), m, int(blk), int(b))][int(s)] = float(v)
        elif row[0] == 'meta':
            _, p, gap, nf, nn, ne, disp, cen, hum, cc, cp = row
            meta[(int(p), float(gap))] = dict(
                k=int(nn), nfixed=int(nf), nedge=int(ne), disp=float(disp),
                centroid=float(cen), human=float(hum), cal=(int(cc), float(cp)))
        elif row[0] == 'feas':
            _, p, gap, who, blk, cc, pen, mc = row
            feas[(int(p), float(gap), who, int(blk))] = (int(cc), float(pen), float(mc))
    return runs, meta, feas


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval, by bisection on the tail sums. No scipy."""
    def tail_ge(p):
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    def tail_le(p):
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))

    def bisect(f, target):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    low = 0.0 if k == 0 else bisect(tail_ge, alpha / 2)
    high = 1.0 if k == n else bisect(lambda p: 1 - tail_le(p), 1 - alpha / 2)
    return low, high


def wv(meta, p, gap):
    return 2 * meta[(p, gap)]['k']


def report(runs, meta, feas, pairs, gap, panel):
    print(f'\n{"=" * 78}\nclearance {gap:g}, panel {panel}, budget {PRIMARY}\n{"=" * 78}')

    M = {m: [median(runs[(p, gap, m, wv(meta, p, gap), PRIMARY)].values()) for p in pairs]
         for m in METHODS}
    cen = [meta[(p, gap)]['centroid'] for p in pairs]

    print('\n-- across instances, on per-instance medians (the record\'s estimand) --')
    for a, b, lbl in [('ga', cen, 'ga vs centroid'), ('climb', cen, 'climb vs centroid'),
                      ('random', cen, 'random vs centroid'),
                      ('climb', 'random', 'climb vs random'),
                      ('anneal', 'random', 'anneal vs random'),
                      ('ga', 'random', 'ga vs random'),
                      ('climb', 'ga', 'climb vs ga'),
                      ('climb', 'anneal', 'climb vs anneal')]:
        A = M[a]
        B = b if isinstance(b, list) else M[b]
        d = [x - y for x, y in zip(A, B)]
        rel = [100.0 * (x - y) / y for x, y in zip(A, B)]
        p_, n = wilcoxon(d)
        hl, lo, hi, cov = hodges_lehmann(rel)
        iv = f'[{lo:+.2f}, {hi:+.2f}]' if lo is not None else 'n/a'
        print(f'   {lbl:<19} p={p_:.4f}  n={n}  wins={sum(1 for x in d if x < 0)}/{len(d)}'
              f'  HL={hl:+7.2f}% {iv}')

    print(f'\n-- per-instance win probability against the control, {panel} paired seeds --')
    print(f'{"pair":>5} {"k":>2} | ' + ' '.join(f'{m:>22}' for m in METHODS[1:]))
    A_by = {m: [] for m in METHODS[1:]}
    for p in pairs:
        cells = []
        for m in METHODS[1:]:
            mm = runs[(p, gap, m, wv(meta, p, gap), PRIMARY)]
            rr = runs[(p, gap, 'random', wv(meta, p, gap), PRIMARY)]
            n = len(mm)
            w = sum(1 for s in mm if mm[s] < rr[s])
            t = sum(1 for s in mm if mm[s] == rr[s])
            A = (w + 0.5 * t) / n
            A_by[m].append(A)
            live = n - t
            if live == 0:
                cells.append(f'{A:5.3f} all {n} tied')
            else:
                lo, hi = clopper_pearson(w, live)
                cells.append(f'{A:5.3f} [{lo:.2f},{hi:.2f}] t={t}')
        print(f'{p:>5} {meta[(p, gap)]["k"]:>2} | ' + ' '.join(f'{c:>22}' for c in cells))
    print('   across instances, exact sign test on A - 0.5 (ties at 0.5 dropped):')
    for m in METHODS[1:]:
        d = [a - 0.5 for a in A_by[m]]
        nz = [x for x in d if x != 0]
        w = sum(1 for x in nz if x > 0)
        pv = 2 * min(sign_one_sided(w, len(nz)), sign_one_sided(len(nz) - w, len(nz)))
        print(f'     {m:>7}: {w}/{len(nz)} instances favour it, two-sided p = {min(pv,1.0):.4f}')

    print('\n-- separation budget B* --')
    for m in METHODS[1:]:
        row = []
        for p in pairs:
            got = 'inf'
            for b in (500, 2000, PRIMARY, 32000):
                mm = runs[(p, gap, m, wv(meta, p, gap), b)]
                rr = runs[(p, gap, 'random', wv(meta, p, gap), b)]
                w = sum(1 for s in mm if mm[s] < rr[s])
                if sign_one_sided(w, len(mm)) <= 0.05:
                    got = b
                    break
            row.append(got)
        print(f'   {m:>7} ' + ' '.join(f'{str(x):>6}' for x in row) +
              f'  never={row.count("inf")}')

    print('\n-- the reference layouts, and the feasibility pair (C, P) --')
    print(f'{"pair":>5} | {"human (C,P)":>16} {"clear":>7} | {"centroid (C,P)":>16} {"clear":>7}')
    for p in pairs:
        h = feas.get((p, gap, 'human', -1))
        c = feas.get((p, gap, 'centroid', -1))
        if not h or not c:
            continue
        print(f'{p:>5} | {f"({h[0]}, {h[1]:.0f})":>16} {h[2]:>7.0f} | '
              f'{f"({c[0]}, {c[1]:.0f})":>16} {c[2]:>7.0f}')
    infeasible = [p for p in pairs if feas.get((p, gap, 'human', -1), (0, 0, 1))[2] < 0]
    if infeasible:
        vals = [feas[(p, gap, 'human', -1)][2] for p in infeasible]
        print(f'   the human reference is INFEASIBLE on {len(infeasible)}/{len(pairs)} '
              f'instances, clearance {min(vals):.0f} to {max(vals):.0f}')


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else f'{HERE}/sweep2_results.csv'
    runs, meta, feas = load(path)
    gaps = sorted({k[1] for k in meta})
    pairs = [p for p in sorted({k[0] for k in meta}) if p != 16]
    for gap in gaps:
        have = [p for p in pairs if (p, gap, 'climb', wv(meta, p, gap), PRIMARY) in runs]
        if not have:
            continue
        panel = len(runs[(have[0], gap, 'climb', wv(meta, have[0], gap), PRIMARY)])
        report(runs, meta, feas, have, gap, panel)

    if len(gaps) > 1:
        print(f'\n{"=" * 78}\nunbundling: does the verdict come from the repair fix or from '
              f'the clearance change?\n{"=" * 78}')
        g0, g1 = min(gaps), max(gaps)
        for m in METHODS[1:]:
            rows = []
            for p in pairs:
                key = lambda g, mm: (p, g, mm, wv(meta, p, g), PRIMARY)
                if key(g0, m) not in runs or key(g1, m) not in runs:
                    continue
                a = median(runs[key(g0, m)].values()) - median(runs[key(g0, 'random')].values())
                b = median(runs[key(g1, m)].values()) - median(runs[key(g1, 'random')].values())
                rows.append((p, a, b))
            if not rows:
                continue
            print(f'   {m:>7} vs control, margin at clearance {g0:g} then {g1:g}:')
            for p, a, b in rows:
                print(f'      pair {p:>2}: {a:>+10.0f}  {b:>+10.0f}')


if __name__ == '__main__':
    main()
