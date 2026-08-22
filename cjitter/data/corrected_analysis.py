"""Every declared comparison, recomputed on the corrected-repair sweep.

Validated first by reproducing the paper's published numbers from the frozen results.csv
(the defective run), exactly as block_analysis.py does: statistics checked against the
record before they are trusted on anything new.

Reads:
  results.csv             the frozen pre-registered sweep (defective repair)   -> VALIDATION
  block_results.csv       both block arms, defective repair                    -> history
  block_results_fixed.csv both block arms, corrected repair                    -> PRIMARY

The whole-vector arm of a block file is block = 2k, which is what the pre-registered
comparison ran; block = 2 is one table per proposal.

Exact tests in pure Python, no pairstat dependency: two-sided Wilcoxon signed-rank by
enumeration, one-sided sign test, Hodges-Lehmann with its distribution-free interval, Holm.
"""
import csv, os, sys
from itertools import product
from math import comb
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
METHODS = ['random', 'climb', 'anneal', 'ga']
BUDGETS = [500, 2000, 8000, 32000]
PRIMARY = 8000


# ---------------------------------------------------------------- exact statistics

def _ranks(vals):
    """Mid-ranks of |vals|, 1-based."""
    n = len(vals)
    order = sorted(range(n), key=lambda i: abs(vals[i]))
    r = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(vals[order[j + 1]]) == abs(vals[order[i]]):
            j += 1
        avg = (i + j + 2) / 2.0
        for t in range(i, j + 1):
            r[order[t]] = avg
        i = j + 1
    return r


def wilcoxon(d):
    """Exact two-sided signed-rank p, zeros dropped. Returns (p, n_nonzero)."""
    d = [x for x in d if x != 0]
    n = len(d)
    if n == 0:
        return None, 0
    if n > 20:
        raise ValueError('enumeration only up to n = 20')
    r = _ranks(d)
    tot = sum(r)
    W = sum(r[i] for i in range(n) if d[i] > 0)
    obs = min(W, tot - W)
    hit = 0
    for signs in product((0, 1), repeat=n):
        w = sum(r[i] for i in range(n) if signs[i])
        if min(w, tot - w) <= obs + 1e-9:
            hit += 1
    return hit / 2 ** n, n


def sign_one_sided(wins, n):
    """Exact P(X >= wins) under a fair coin."""
    return sum(comb(n, i) for i in range(wins, n + 1)) / 2 ** n


def hodges_lehmann(d):
    """Median of Walsh averages, and the distribution-free interval with its realized
    coverage (the attainable one, which is not 95% at small n)."""
    n = len(d)
    if n == 0:
        return None, None, None, None
    w = sorted((d[i] + d[j]) / 2.0 for i in range(n) for j in range(i, n))
    m = len(w)
    hl = w[m // 2] if m % 2 else 0.5 * (w[m // 2 - 1] + w[m // 2])
    # largest k with P(W+ <= k-1) <= 0.025, by enumeration of the null signed-rank sum
    null = defaultdict(int)
    null[0.0] = 1
    for i in range(1, n + 1):
        nxt = defaultdict(int)
        for s, c in null.items():
            nxt[s] += c
            nxt[s + i] += c
        null = nxt
    cum, k, tail = 0, 0, 2 ** n
    for s in sorted(null):
        if (cum + null[s]) / tail > 0.025:
            break
        cum += null[s]
        k = int(s) + 1
    if k >= m:
        return hl, None, None, None
    cover = 1 - 2 * cum / tail
    return hl, w[k], w[m - 1 - k], cover


def holm(named):
    """[(name, p)] -> {name: adjusted p}, step-down."""
    out, prev = {}, 0.0
    for i, (nm, p) in enumerate(sorted(named, key=lambda t: t[1])):
        adj = max(prev, min(1.0, (len(named) - i) * p))
        out[nm] = adj
        prev = adj
    return out


def median(vals):
    v = sorted(vals)
    n = len(v)
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


# ---------------------------------------------------------------- loading

def load(path, blocked):
    """-> runs[(pair, method, block, budget)][seed], meta[pair], feas[pair][who]
    A flat file is stored under block = 0.

    Note on a defect in the block files. sweep_block.c loops two arms, block = 2k and
    block = 2, so on the three k = 1 pairs where 2k IS 2 it emits every row twice: 160 run
    rows for pair 3 where 80 are distinct. Storing by (pair, method, block, budget, seed)
    deduplicates them, which is why the numbers here are right; anything that loads those
    files into a list instead double-counts three of the eight instances. sweep_block.c is
    left as it is because it produced the frozen record."""
    runs, meta, feas = defaultdict(dict), {}, defaultdict(dict)
    for row in csv.reader(open(path)):
        if row[0] == 'run':
            if blocked:
                _, p, m, blk, b, s, v = row
            else:
                _, p, m, b, s, v = row
                blk = 0
            key, seed = (int(p), m, int(blk), int(b)), int(s)
            prev = runs[key].get(seed)
            if prev is not None and prev != float(v):
                raise ValueError(f'duplicate row disagrees at {key} seed {seed}')
            runs[key][seed] = float(v)
        elif row[0] == 'meta':
            _, p, nf, nn, ne, disp, cen, hum, cc, cp = row
            meta[int(p)] = dict(nfixed=int(nf), k=int(nn), nedge=int(ne), disp=float(disp),
                                centroid=float(cen), human=float(hum),
                                cal=(int(cc), float(cp)))
        elif row[0] == 'feas':
            if blocked:
                _, p, who, blk, cc, pen = row
                feas[int(p)][(who, int(blk))] = (int(cc), float(pen))
            else:
                _, p, who, cc, pen = row
                feas[int(p)][who] = (int(cc), float(pen))
    return runs, meta, feas


def arm(runs, meta, method, block, budget, pairs):
    """Per-pair medians over seeds. block='wv' selects the whole vector (2k)."""
    out = []
    for p in pairs:
        blk = 2 * meta[p]['k'] if block == 'wv' else block
        out.append(median(runs[(p, method, blk, budget)].values()))
    return out


# ---------------------------------------------------------------- validation

def validate(runs, meta, pairs):
    """Reproduce the paper's published numbers from the frozen defective sweep. Any
    mismatch here means the statistics below are not to be trusted."""
    print('== VALIDATION: this script against the published record (results.csv) ==')
    M = {m: [median(runs[(p, m, 0, PRIMARY)].values()) for p in pairs] for m in METHODS}
    cen = [meta[p]['centroid'] for p in pairs]
    expect = [
        ('ga vs centroid',    M['ga'],    cen,          0.0078),
        ('climb vs centroid', M['climb'], cen,          0.0078),
        ('ga vs random',      M['ga'],    M['random'],  0.1094),
        ('climb vs ga',       M['climb'], M['ga'],      0.0156),
        ('climb vs random',   M['climb'], M['random'],  0.0156),
        ('ga vs anneal',      M['ga'],    M['anneal'],  0.2969),
    ]
    ok = True
    for name, a, b, want in expect:
        p, n = wilcoxon([x - y for x, y in zip(a, b)])
        good = abs(p - want) < 5e-4
        ok &= good
        print(f'  {name:<18} p = {p:.4f}  paper {want:.4f}  {"ok" if good else "MISMATCH"}')
    hl, _, _, _ = hodges_lehmann([x - y for x, y in zip(M['ga'], cen)])
    good = abs(hl - (-72287)) < 1
    ok &= good
    print(f'  {"ga vs centroid HL":<18} {hl:.0f}      paper -72287  '
          f'{"ok" if good else "MISMATCH"}')
    print(f'  -> {"VALIDATED" if ok else "FAILED; stop here"}\n')
    return ok


# ---------------------------------------------------------------- reports

def per_pair_table(runs, meta, pairs, label, block):
    print(f'== per-pair medians at {PRIMARY}, {label} ==')
    print(f'{"pair":>4} {"k":>2} {"disp":>6} | ' + ' '.join(f'{m:>8}' for m in METHODS) +
          f' | {"centroid":>9} {"human":>8} {"calib":>10}')
    for p in pairs:
        i = meta[p]
        cells = ' '.join(
            f'{median(runs[(p, m, 2 * i["k"] if block == "wv" else block, PRIMARY)].values()):>8.0f}'
            for m in METHODS)
        print(f'{p:>4} {i["k"]:>2} {i["disp"]:>6.0f} | {cells} | '
              f'{i["centroid"]:>9.0f} {i["human"]:>8.0f} '
              f'{i["cal"][0]:>3d}/{i["cal"][1]:>5.0f}')
    print()


def comparisons(runs, meta, pairs, label, block):
    print(f'== declared comparisons, {label} (exact two-sided Wilcoxon at {PRIMARY}) ==')
    M = {m: arm(runs, meta, m, block, PRIMARY, pairs) for m in METHODS}
    cen = [meta[p]['centroid'] for p in pairs]
    tests = [
        ('ga vs centroid',     M['ga'],     cen),
        ('climb vs centroid',  M['climb'],  cen),
        ('anneal vs centroid', M['anneal'], cen),
        ('random vs centroid', M['random'], cen),
        ('climb vs random',    M['climb'],  M['random']),
        ('anneal vs random',   M['anneal'], M['random']),
        ('ga vs random',       M['ga'],     M['random']),
        ('climb vs ga',        M['climb'],  M['ga']),
        ('ga vs anneal',       M['ga'],     M['anneal']),
        ('climb vs anneal',    M['climb'],  M['anneal']),
    ]
    print(f'{"comparison":<19} {"p":>7} {"n":>3} {"wins":>6} {"HL (raw)":>12} '
          f'{"HL % of control":>26}')
    rows = {}
    for name, a, b in tests:
        d = [x - y for x, y in zip(a, b)]
        rel = [100.0 * (x - y) / y for x, y in zip(a, b)]
        p, n = wilcoxon(d)
        wins = sum(1 for x in d if x < 0)
        hl, lo, hi, cov = hodges_lehmann(d)
        rhl, rlo, rhi, _ = hodges_lehmann(rel)
        iv = f'[{rlo:+.2f}, {rhi:+.2f}] @{100 * cov:.1f}%' if rlo is not None else 'n/a'
        print(f'{name:<19} {p:>7.4f} {n:>3} {wins:>3}/{len(d)} {hl:>12.0f} '
              f'{rhl:>+7.2f}% {iv:>18}')
        rows[name] = p
    # Holm over the families the pre-registration actually declared
    f1 = [(k, rows[k]) for k in ('ga vs centroid', 'ga vs random', 'climb vs centroid')]
    f2 = [(k, rows[k]) for k in ('climb vs ga', 'ga vs anneal')]
    print('  Holm, declared family 1 (prereg):    ' +
          ', '.join(f'{k} {v:.4f}' for k, v in holm(f1).items()))
    print('  Holm, declared family 2 (addendum 1):' +
          ', '.join(f'{k} {v:.4f}' for k, v in holm(f2).items()))
    print('  NOT DECLARED anywhere: climb vs random, anneal vs random, random vs centroid,'
          ' climb vs anneal\n')
    return rows


def bstar(runs, meta, pairs, label, block):
    print(f'== separation budget B*, {label} (5-seed one-sided sign test vs random) ==')
    print(f'{"method":>7} ' + ' '.join(f'{p:>6}' for p in pairs) +
          f' | {"median":>7} {"never":>5} {"<=2000":>6}')
    for m in ('climb', 'anneal', 'ga'):
        row, INF = [], float('inf')
        for p in pairs:
            blk = 2 * meta[p]['k'] if block == 'wv' else block
            got = INF
            for b in BUDGETS:
                mm, rr = runs[(p, m, blk, b)], runs[(p, 'random', blk, b)]
                w = sum(1 for s in mm if mm[s] < rr[s])
                if sign_one_sided(w, len(mm)) <= 0.05:
                    got = b
                    break
            row.append(got)
        med = median(row)
        cells = ' '.join(f'{"inf" if x == INF else int(x):>6}' for x in row)
        print(f'{m:>7} {cells} | {"inf" if med == INF else int(med):>7} '
              f'{row.count(INF):>5} {sum(1 for x in row if x <= 2000):>6}')
    print()


def block_arm(runs, meta, pairs, label):
    live = [p for p in pairs if meta[p]['k'] >= 2]
    print(f'== block 2 vs whole vector, {label} (only k >= 2 can differ: {live}) ==')
    for m in ('climb', 'anneal', 'ga'):
        wv = arm(runs, meta, m, 'wv', PRIMARY, live)
        b2 = arm(runs, meta, m, 2, PRIMARY, live)
        d = [x - y for x, y in zip(b2, wv)]
        p, n = wilcoxon(d)
        hl, _, _, _ = hodges_lehmann(d)
        print(f'  {m:>7}: {sum(1 for x in d if x < 0)}/{len(d)} improved  '
              f'p = {p:.4f}  HL = {hl:>8.0f}  deltas = ' +
              ' '.join(f'{x:+.0f}' for x in d))
    print()


def leave_one_out(runs, meta, pairs, label, block):
    print(f'== leave-one-out exact two-sided Wilcoxon, {label} ==')
    M = {m: arm(runs, meta, m, block, PRIMARY, pairs) for m in METHODS}
    cen = [meta[p]['centroid'] for p in pairs]
    tests = [('ga vs centroid', M['ga'], cen), ('climb vs centroid', M['climb'], cen),
             ('random vs centroid', M['random'], cen),
             ('ga vs random', M['ga'], M['random']),
             ('climb vs ga', M['climb'], M['ga']),
             ('climb vs random', M['climb'], M['random'])]
    print(f'{"comparison":<19} {"all":>6} ' + ' '.join(f'{-p:>6}' for p in pairs))
    for name, a, b in tests:
        full, _ = wilcoxon([x - y for x, y in zip(a, b)])
        cells = []
        for i in range(len(pairs)):
            d = [a[j] - b[j] for j in range(len(pairs)) if j != i]
            p, _ = wilcoxon(d)
            cells.append(f'{p:>6.3f}')
        print(f'{name:<19} {full:>6.4f} ' + ' '.join(cells))
    print()


def human_and_feasibility(runs, meta, feas, pairs, label, block):
    print(f'== against the human reference, {label} ==')
    for m in METHODS:
        a = arm(runs, meta, m, block, PRIMARY, pairs)
        beats = sum(1 for x, p in zip(a, pairs) if x < meta[p]['human'])
        print(f'  {m:>7} outscores the human on {beats}/{len(pairs)} pairs')
    print('  (the control does it too: an objective under which uniform sampling beats a')
    print('   maintainer has not demonstrated construct validity)')
    have = sorted({w for p in feas for w in
                   ([k[0] for k in feas[p]] if isinstance(next(iter(feas[p]), ('', 0)), tuple)
                    else list(feas[p]))})
    print(f'  feasibility rows present for: {have}')
    if 'centroid' not in have:
        print('  MISSING: centroid and human feasibility rows. The pre-registered secondary')
        print('  on the (C, P) pair cannot be computed on this sweep.')
    print()


# ---------------------------------------------------------------- main

def main():
    frozen, fmeta, ffeas = load(f'{HERE}/results.csv', False)
    pairs = [p for p in sorted(fmeta) if p != 16]

    if not validate(frozen, fmeta, pairs):
        sys.exit(1)

    for path, label in ((f'{HERE}/block_results.csv', 'DEFECTIVE repair (disclosed history)'),
                        (f'{HERE}/block_results_fixed.csv', 'CORRECTED repair (primary)')):
        runs, meta, feas = load(path, True)
        pp = [p for p in sorted(meta) if p != 16]
        print('#' * 78)
        print(f'# {label}')
        print('#' * 78)
        per_pair_table(runs, meta, pp, label, 'wv')
        comparisons(runs, meta, pp, label, 'wv')
        bstar(runs, meta, pp, label, 'wv')
        block_arm(runs, meta, pp, label)
        leave_one_out(runs, meta, pp, label, 'wv')
        human_and_feasibility(runs, meta, feas, pp, label, 'wv')


if __name__ == '__main__':
    main()
