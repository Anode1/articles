# SUPERSEDED. This reads block_results.csv, which was produced under the repair defect that
# Section "the repair" documents: the callback did not discharge the non-overlap
# constraint, and correcting it changed 1118 of 1200 per-seed values. Kept because
# it is what the published numbers were computed with. For anything current use
# corrected_analysis.py, which reproduces these numbers first and then reports the
# corrected sweep.
"""Exact statistics for the block arm, matching the paper's declared tests.
Validated first by reproducing the published numbers from the frozen results.csv."""
import csv, itertools, math, os
from collections import defaultdict

METHODS = ['random','climb','anneal','ga']
BUDGETS = [500,2000,8000,32000]
HERE = os.path.dirname(os.path.abspath(__file__))

def med(v):
    v = sorted(v)
    return v[len(v)//2] if len(v)%2 else 0.5*(v[len(v)//2-1]+v[len(v)//2])

def ranks(a):
    idx = sorted(range(len(a)), key=lambda i: a[i])
    r = [0.0]*len(a); i = 0
    while i < len(idx):
        j = i
        while j+1 < len(idx) and a[idx[j+1]] == a[idx[i]]: j += 1
        avg = (i+j)/2.0 + 1
        for k in range(i, j+1): r[idx[k]] = avg
        i = j+1
    return r

def wilcoxon_exact(x, y):
    """two-sided exact Wilcoxon signed-rank; zeros dropped (Pratt not used, as in the paper)"""
    d = [a-b for a,b in zip(x,y) if a != b]
    n = len(d)
    if n == 0: return 1.0, 0
    rk = ranks([abs(v) for v in d])
    wp = sum(r for v,r in zip(d,rk) if v > 0)
    mu = sum(rk)/2.0
    obs = abs(wp-mu)
    cnt = 0
    for signs in itertools.product([0,1], repeat=n):
        w = sum(r for s,r in zip(signs,rk) if s)
        if abs(w-mu) >= obs - 1e-9: cnt += 1
    return cnt/2**n, n

def hodges_lehmann(x, y):
    d = sorted(a-b for a,b in zip(x,y))
    w = sorted((d[i]+d[j])/2.0 for i in range(len(d)) for j in range(i,len(d)))
    return med(w)

def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    out = [0.0]*len(ps); run = 0.0
    for k,i in enumerate(order):
        v = (len(ps)-k)*ps[i]
        run = max(run, v)
        out[i] = min(1.0, run)
    return out

def sign_p_onesided(w, n):
    return sum(math.comb(n,k) for k in range(w,n+1))/2**n

def load(path, blocked):
    runs = defaultdict(dict); meta = {}
    for row in csv.reader(open(path)):
        if row[0]=='meta':
            meta[int(row[1])] = dict(nnew=int(row[3]), centroid=float(row[6]), human=float(row[7]))
        elif row[0]=='run':
            if blocked:
                _,p,m,blk,b,s,best = row
                runs[(int(p),m,int(blk),int(b))][int(s)] = float(best)
            else:
                _,p,m,b,s,best = row
                runs[(int(p),m,0,int(b))][int(s)] = float(best)
    return runs, meta

frozen,_ = load('/home/vas/articles/cjitter/data/results.csv', False)
blk, meta = load(f'{HERE}/block_results.csv', True)
PRIMARY = [3,4,6,7,12,13,14,15]     # the pre-registered eight; 16 is the pilot
NV = {p: 2*meta[p]['nnew'] for p in meta}

def series(src, m, block, budget, pairs):
    return [med(list(src[(p,m,block,budget)].values())) for p in pairs]

print('== VALIDATION: my statistics against the paper, on the frozen results.csv ==')
cen = [ [r for r in csv.reader(open('/home/vas/articles/cjitter/data/results.csv'))] ]
centroid = {}
for row in csv.reader(open('/home/vas/articles/cjitter/data/results.csv')):
    if row[0]=='meta': centroid[int(row[1])] = float(row[6])
ga = series(frozen,'ga',0,8000,PRIMARY); ce = [centroid[p] for p in PRIMARY]
p1,_ = wilcoxon_exact(ga, ce)
print(f'  GA vs centroid      p = {p1:.4f}   (paper 0.0078)   HL = {hodges_lehmann(ga,ce):.0f}  (paper -72287)')
rnd = series(frozen,'random',0,8000,PRIMARY)
p2,_ = wilcoxon_exact(ga, rnd)
print(f'  GA vs random        p = {p2:.4f}   (paper 0.109)')
cl = series(frozen,'climb',0,8000,PRIMARY)
p3,n3 = wilcoxon_exact(cl, ga)
print(f'  climb vs GA         p = {p3:.4f}   (paper 0.016, n={n3} non-tied, paper 7)')
an = series(frozen,'anneal',0,8000,PRIMARY)
p4,_ = wilcoxon_exact(ga, an)
print(f'  GA vs anneal        p = {p4:.4f}   (paper 0.297)')
print(f'  Holm over [GA-centroid, climb-GA]: {[round(v,4) for v in holm([p1,p3])]}  (paper 0.023, 0.031)')

print('\n== the block arm: which pairs can differ at all ==')
for p in sorted(meta):
    tag = 'pilot' if p == 16 else ''
    print(f'  pair {p:>2}: k={meta[p]["nnew"]:>2}, {NV[p]:>2} variables -> block 2 is '
          f'{"the whole vector, identical by construction" if NV[p]<=2 else "one table of %d"%meta[p]["nnew"]} {tag}')

AFFECT = [p for p in PRIMARY if NV[p] > 2]
print(f'\n  affected pairs among the pre-registered eight: {AFFECT}  (n = {len(AFFECT)})')
print(f'  best attainable two-sided exact p at n={len(AFFECT)}: {2/2**len(AFFECT):.4f}')

print('\n== per-pair medians at budget 8000: block n -> block 2 ==')
print(f'{"pair":>5} {"k":>2} | ' + ' '.join(f'{m:>21}' for m in METHODS))
for p in PRIMARY + [16]:
    row = f'{p:>5} {meta[p]["nnew"]:>2} | '
    for m in METHODS:
        a = med(list(blk[(p,m,NV[p],8000)].values()))
        b = med(list(blk[(p,m,2,8000)].values()))
        row += f'{a:>9.0f}->{b:<9.0f}  ' if NV[p]>2 else f'{a:>9.0f} {"=":<10}  '
    print(row)

print('\n== block 2 vs block n, per method, on the affected pairs (exploratory) ==')
for m in METHODS:
    a = [med(list(blk[(p,m,NV[p],8000)].values())) for p in AFFECT]
    b = [med(list(blk[(p,m,2,8000)].values())) for p in AFFECT]
    wins = sum(1 for x,y in zip(a,b) if y < x)
    pv,n = wilcoxon_exact(b,a)
    hl = hodges_lehmann(b,a)
    print(f'  {m:>7}: block 2 better on {wins}/{len(AFFECT)}   exact two-sided p={pv:.4f}   '
          f'one-sided {pv/2:.4f}   HL shift {hl:+.0f}')

print('\n== does each method separate from the matched-budget control? (5-seed sign test) ==')
for arm_name, getblk in (('block n', lambda p: NV[p]), ('block 2', lambda p: 2)):
    print(f'  -- {arm_name} --')
    for m in METHODS[1:]:
        sep = []
        for p in PRIMARY:
            got = None
            for bud in BUDGETS:
                wins = sum(1 for s in range(5)
                           if blk[(p,m,getblk(p),bud)][s] < blk[(p,'random',getblk(p),bud)][s])
                if sign_p_onesided(wins,5) <= 0.05: got = bud; break
            sep.append(got)
        fin = [v for v in sep if v]
        print(f'    {m:>7}: separates on {len(fin)}/8 pairs   B* per pair: '
              + ' '.join(str(v) if v else 'inf' for v in sep))

print('\n== the refutation clause re-run: method vs control at 8000, over the eight ==')
for arm_name, getblk in (('block n', lambda p: NV[p]), ('block 2', lambda p: 2)):
    for m in METHODS[1:]:
        a = [med(list(blk[(p,m,getblk(p),8000)].values())) for p in PRIMARY]
        r = [med(list(blk[(p,'random',getblk(p),8000)].values())) for p in PRIMARY]
        pv,n = wilcoxon_exact(a,r)
        print(f'  {arm_name}  {m:>7} vs random: exact two-sided p={pv:.4f} (n={n} non-tied)')
