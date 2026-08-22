# SUPERSEDED. This reads results.csv, which was produced under the repair defect that
# Section "the repair" documents: the callback did not discharge the non-overlap
# constraint, and correcting it changed 1118 of 1200 per-seed values. Kept because
# it is what the published numbers were computed with. For anything current use
# corrected_analysis.py, which reproduces these numbers first and then reports the
# corrected sweep.
"""The pre-registered analysis over results.csv. Pairwise families go through bpnn's
pairstat (exact Wilcoxon, sign test, Hodges-Lehmann, Holm, MDE); this script adds the
Friedman omnibus (permutation null), rank-biserial effects, exact McNemar on the
zero-penetration binary, separation budgets B*, bootstrap intervals, and the variance
components. Everything prints; nothing is hidden in a variable."""
import csv, math, os, random, subprocess, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRSTAT = os.path.expanduser('~/bpnn/pairstat')
METHODS = ['random', 'climb', 'anneal', 'ga']
BUDGETS = [500, 2000, 8000, 32000]

runs = defaultdict(dict)      # (pair, method, budget) -> [5 seed bests]
meta = {}                     # pair -> dict
feas = defaultdict(dict)      # pair -> who -> (cross, pen)
for row in csv.reader(open(f'{HERE}/results.csv')):
    if row[0] == 'run':
        _, pair, m, budget, seed, best = row
        runs[(int(pair), m, int(budget))][int(seed)] = float(best)
    elif row[0] == 'meta':
        _, pair, nf, nn, ne, disp, cen, hum, cc, cp = row
        meta[int(pair)] = dict(nfixed=int(nf), nnew=int(nn), nedge=int(ne),
                               disp=float(disp), centroid=float(cen), human=float(hum),
                               cal_cross=int(cc), cal_pen=float(cp))
    elif row[0] == 'feas':
        _, pair, who, cc, pen = row
        feas[int(pair)][who] = (int(cc), float(pen))

pairs = sorted(meta)
print(f'pairs: {pairs}')

def med(vals):
    v = sorted(vals)
    return v[len(v)//2] if len(v) % 2 else 0.5*(v[len(v)//2-1]+v[len(v)//2])

# per-pair medians at each budget
M = {(p, m, b): med(list(runs[(p, m, b)].values())) for p in pairs
     for m in METHODS for b in BUDGETS}

print('\n== per-pair table at 8000 (medians), centroid, human, calibration ==')
print(f'{"pair":>4} {"nfix":>4} {"new":>3} {"disp":>7} | ' +
      ' '.join(f'{m:>9}' for m in METHODS) +
      f' | {"centroid":>9} {"human":>9} {"cal":>10}')
for p in pairs:
    i = meta[p]
    print(f'{p:>4} {i["nfixed"]:>4} {i["nnew"]:>3} {i["disp"]:>7.0f} | ' +
          ' '.join(f'{M[(p,m,8000)]:>9.0f}' for m in METHODS) +
          f' | {i["centroid"]:>9.0f} {i["human"]:>9.0f} '
          f'{i["cal_cross"]:>3d}/{i["cal_pen"]:>5.0f}')

# ---- pairstat: the declared families ----
def run_pairstat(lines, metrics, label):
    print(f'\n== pairstat: {label} ==')
    env = dict(os.environ, PREFIX='RAW', GROUP='0', METRICS=metrics)
    r = subprocess.run([PAIRSTAT], input='\n'.join(lines) + '\n',
                       capture_output=True, text=True, env=env)
    print(r.stdout.strip())
    if r.returncode:
        print(r.stderr.strip())

lines = ['RAW %d %.10g %.10g %.10g %.10g %.10g %.10g' %
         (p, M[(p,'ga',8000)], meta[p]['centroid'], M[(p,'random',8000)],
          M[(p,'climb',8000)], M[(p,'anneal',8000)], meta[p]['human'])
         for p in pairs]
run_pairstat(lines, 'ga_vs_centroid:3:4,ga_vs_random:5:3,climb_vs_centroid:6:4',
             'pre-registered family (Holm across these three)')
run_pairstat(lines, 'ga_vs_climb:6:3,ga_vs_anneal:7:3',
             'addendum family: the GA prediction (Holm across these two)')

# note pairstat METRICS columns are 1-based on the whole line (token 1 = RAW? check: PREFIX
# consumes the first token; columns count after it per bpnn convention: verified below by
# printing the first line for eyeball)
print('\nfirst pairstat input line for column verification:')
print(lines[0])

# ---- Friedman omnibus over the four methods (primary outcome, 8000) ----
def friedman(pairs, getv, k):
    ranks = []
    for p in pairs:
        vals = [(getv(p, j), j) for j in range(k)]
        order = sorted(vals)
        rk = [0.0]*k
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and order[j+1][0] == order[i][0]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for t in range(i, j+1):
                rk[order[t][1]] = avg
            i = j + 1
        ranks.append(rk)
    n = len(pairs)
    Rj = [sum(r[j] for r in ranks) for j in range(k)]
    stat = 12.0/(n*k*(k+1)) * sum(R*R for R in Rj) - 3*n*(k+1)
    rng = random.Random(20260815)
    ge = 0
    REPS = 20000
    for _ in range(REPS):
        Rp = [0.0]*k
        for r in ranks:
            sh = r[:]
            rng.shuffle(sh)
            for j in range(k):
                Rp[j] += sh[j]
        s2 = 12.0/(n*k*(k+1)) * sum(R*R for R in Rp) - 3*n*(k+1)
        if s2 >= stat - 1e-12:
            ge += 1
    return stat, (ge + 1) / (REPS + 1), [R/n for R in Rj]

stat, pval, meanranks = friedman(pairs, lambda p, j: M[(p, METHODS[j], 8000)], 4)
print(f'\n== Friedman over methods at 8000: stat {stat:.3f}, permutation p {pval:.5f}')
print('   mean ranks: ' + ', '.join(f'{m} {r:.2f}' for m, r in zip(METHODS, meanranks)))

# ---- rank-biserial effects for the declared comparisons ----
def rank_biserial(diffs):
    d = [x for x in diffs if x != 0]
    order = sorted(range(len(d)), key=lambda i: abs(d[i]))
    wp = wm = 0.0
    for rank0, i in enumerate(order):
        r = rank0 + 1.0
        if d[i] > 0: wp += r
        else: wm += r
    return (wp - wm) / (wp + wm) if wp + wm else 0.0

comps = [('ga', 'centroid', lambda p: meta[p]['centroid'] - M[(p,'ga',8000)]),
         ('ga', 'random',   lambda p: M[(p,'random',8000)] - M[(p,'ga',8000)]),
         ('climb', 'centroid', lambda p: meta[p]['centroid'] - M[(p,'climb',8000)]),
         ('ga', 'climb',    lambda p: M[(p,'climb',8000)] - M[(p,'ga',8000)]),
         ('ga', 'anneal',   lambda p: M[(p,'anneal',8000)] - M[(p,'ga',8000)])]
print('\n== rank-biserial (positive favors the first name) ==')
for a, b, f in comps:
    d = [f(p) for p in pairs]
    wins = sum(1 for x in d if x > 0)
    print(f'  {a} vs {b}: r_rb {rank_biserial(d):+.3f}, wins {wins}/{len(d)}')

# ---- exact McNemar: ga vs centroid on reaching zero penetration ----
b01 = b10 = 0
for p in pairs:
    ga0 = feas[p].get('ga', (0, 1))[1] <= 1e-9
    ce0 = feas[p].get('centroid', (0, 1))[1] <= 1e-9
    if ga0 and not ce0: b10 += 1
    if ce0 and not ga0: b01 += 1
disc = b01 + b10
if disc:
    from math import comb
    ptail = sum(comb(disc, i) for i in range(0, min(b01, b10)+1)) / 2**disc
    pmc = min(1.0, 2*ptail)
else:
    pmc = 1.0
print(f'\n== McNemar ga vs centroid on pen==0: ga-only {b10}, centroid-only {b01}, '
      f'exact two-sided p {pmc:.4f}')

# ---- separation budgets B* (per pair, per method, vs random at same budget) ----
def sign_p_onesided(w, n):
    from math import comb
    return sum(comb(n, k) for k in range(w, n+1)) / 2**n

print('\n== separation budget B* (smallest budget with 5-seed sign test p<=0.05 vs random) ==')
print(f'{"pair":>4} | ' + ' '.join(f'{m:>7}' for m in METHODS[1:]))
bstar = defaultdict(list)
for p in pairs:
    row = []
    for m in METHODS[1:]:
        got = None
        for b in BUDGETS:
            wins = sum(1 for s in range(5)
                       if runs[(p,m,b)][s] < runs[(p,'random',b)][s])
            if sign_p_onesided(wins, 5) <= 0.05:
                got = b
                break
        bstar[m].append(got)
        row.append(str(got) if got else 'inf')
    print(f'{p:>4} | ' + ' '.join(f'{v:>7}' for v in row))
for m in METHODS[1:]:
    vals = bstar[m]
    fin = [v for v in vals if v]
    print(f'  {m}: separated on {len(fin)}/{len(vals)} pairs, median B* '
          f'{med(fin) if fin else float("inf")}')

# ---- bootstrap 95% intervals on the across-pair median of the 8000 medians ----
rng = random.Random(1)
print('\n== across-pair median of per-pair medians at 8000, bootstrap 95% ==')
for m in METHODS:
    vals = [M[(p, m, 8000)] for p in pairs]
    boots = sorted(med([vals[rng.randrange(len(vals))] for _ in vals])
                   for _ in range(10000))
    print(f'  {m}: {med(vals):.0f}  [{boots[249]:.0f}, {boots[9749]:.0f}]')

# ---- variance components ----
print('\n== spread: within-pair across seeds (median sd) vs across pairs (sd of medians) ==')
for m in METHODS:
    sds = []
    for p in pairs:
        v = list(runs[(p, m, 8000)].values())
        mean = sum(v)/len(v)
        sds.append(math.sqrt(sum((x-mean)**2 for x in v)/(len(v)-1)))
    mm = [M[(p, m, 8000)] for p in pairs]
    mean = sum(mm)/len(mm)
    across = math.sqrt(sum((x-mean)**2 for x in mm)/(len(mm)-1))
    print(f'  {m}: within {med(sds):.0f}, across {across:.0f}')
