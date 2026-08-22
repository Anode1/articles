# SUPERSEDED. This reads results.csv, which was produced under the repair defect that
# Section "the repair" documents: the callback did not discharge the non-overlap
# constraint, and correcting it changed 1118 of 1200 per-seed values. Kept because
# it is what the published numbers were computed with. For anything current use
# corrected_analysis.py, which reproduces these numbers first and then reports the
# corrected sweep.
"""Leave-one-out robustness of the headline verdicts. For each declared comparison,
the exact two-sided Wilcoxon signed-rank p on the per-pair medians at budget 8000,
computed on all eight pairs and then with each pair dropped in turn. Zero differences
are dropped before ranking (the convention the main analysis used). Prints a plain
table and the LaTeX rows for the appendix."""
import csv, itertools, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
runs = defaultdict(dict)
meta = {}
for row in csv.reader(open(f'{HERE}/results.csv')):
    if row[0] == 'run':
        _, pair, m, budget, seed, best = row
        runs[(int(pair), m, int(budget))][int(seed)] = float(best)
    elif row[0] == 'meta':
        meta[int(row[1])] = float(row[6])          # centroid score

pairs = sorted(meta)

def med(vals):
    v = sorted(vals)
    return v[len(v)//2] if len(v) % 2 else 0.5*(v[len(v)//2-1]+v[len(v)//2])

def val(p, m):
    if m == 'centroid':
        return meta[p]
    return med(list(runs[(p, m, 8000)].values()))

def wilcoxon_exact(diffs):
    d = [x for x in diffs if x != 0]
    n = len(d)
    if n == 0:
        return float('nan')
    srt = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0]*n
    i = 0
    while i < n:
        j = i
        while j+1 < n and abs(d[srt[j+1]]) == abs(d[srt[i]]):
            j += 1
        r = (i + j)/2 + 1
        for k in range(i, j+1):
            ranks[srt[k]] = r
        i = j+1
    w = sum(ranks[i] for i in range(n) if d[i] > 0)
    lo = hi = 0
    for signs in itertools.product((0, 1), repeat=n):
        ws = sum(ranks[i] for i in range(n) if signs[i])
        lo += ws <= w
        hi += ws >= w
    total = 2**n
    return min(1.0, 2*min(lo, hi)/total)

COMPS = [('ga', 'centroid'), ('climb', 'centroid'), ('random', 'centroid'),
         ('ga', 'random'), ('climb', 'ga'), ('climb', 'random')]

print(f'{"comparison":<18} {"full":>7} ' + ' '.join(f'-{p:<5}' for p in pairs))
latex = []
for a, b in COMPS:
    full = wilcoxon_exact([val(p, a) - val(p, b) for p in pairs])
    loo = [wilcoxon_exact([val(p, a) - val(p, b) for p in pairs if p != drop])
           for drop in pairs]
    print(f'{a+" vs "+b:<18} {full:>7.4f} ' + ' '.join(f'{x:<6.4f}' for x in loo))
    cells = ' & '.join(f'{x:.3f}' for x in loo)
    latex.append(f'{a} vs.\\ {b} & {full:.4f} & {cells} \\\\')
print()
for line in latex:
    print(line)
