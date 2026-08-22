"""Draws figures/results.svg from results.csv: per-pair medians at budget 8000 for the four
methods, with the centroid heuristic and the human reference beside them, log scale. No
plotting library; the SVG is written directly, like every drawing in this project."""
import csv, math, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
runs = defaultdict(dict)
meta = {}
for row in csv.reader(open(f'{HERE}/results.csv')):
    if row[0] == 'run' and row[3] == '8000':
        runs[(int(row[1]), row[2])][int(row[4])] = float(row[5])
    elif row[0] == 'meta':
        meta[int(row[1])] = (float(row[6]), float(row[7]))   # centroid, human

def med(v):
    v = sorted(v)
    n = len(v)
    return v[n//2] if n % 2 else 0.5*(v[n//2-1]+v[n//2])

pairs = sorted(meta)
METHODS = [('random', '#999'), ('climb', '#06c'), ('anneal', '#909'), ('ga', '#c60')]

W, H, L, B, T, R = 640, 400, 64, 40, 16, 12
ymin, ymax = math.log10(9000), math.log10(300000)
def Y(v):
    return T + (H - T - B) * (1 - (math.log10(v) - ymin) / (ymax - ymin))
def X(i):
    return L + (W - L - R) * (i + 0.5) / len(pairs)

out = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' "
       "font-family='sans-serif' font-size='12'>",
       f"<rect width='{W}' height='{H}' fill='white'/>"]
for g in (10000, 20000, 50000, 100000, 200000):
    y = Y(g)
    out.append(f"<line x1='{L}' y1='{y:.1f}' x2='{W-R}' y2='{y:.1f}' stroke='#eee'/>")
    out.append(f"<text x='{L-6}' y='{y+4:.1f}' text-anchor='end' fill='#555'>"
               f"{g//1000}k</text>")
out.append(f"<line x1='{L}' y1='{T}' x2='{L}' y2='{H-B}' stroke='#999'/>")
out.append(f"<line x1='{L}' y1='{H-B}' x2='{W-R}' y2='{H-B}' stroke='#999'/>")
for i, p in enumerate(pairs):
    x = X(i)
    out.append(f"<text x='{x:.1f}' y='{H-B+16}' text-anchor='middle' fill='#333'>{p}</text>")
    cen, hum = meta[p]
    y = Y(cen)
    out.append(f"<path d='M{x-9:.1f},{y:.1f} L{x+9:.1f},{y:.1f}' stroke='#b00' "
               "stroke-width='2'/>")
    y = Y(hum)
    out.append(f"<path d='M{x:.1f},{y-6:.1f} L{x+6:.1f},{y:.1f} L{x:.1f},{y+6:.1f} "
               f"L{x-6:.1f},{y:.1f} Z' fill='none' stroke='#080' stroke-width='1.6'/>")
    for j, (m, c) in enumerate(METHODS):
        v = med(list(runs[(p, m)].values()))
        y = Y(v)
        dx = (j - 1.5) * 7
        out.append(f"<circle cx='{x+dx:.1f}' cy='{y:.1f}' r='3.4' fill='{c}'/>")
out.append(f"<text x='{L-46}' y='{T+8}' fill='#333'>S</text>")
out.append(f"<text x='{(L+W-R)/2:.0f}' y='{H-6}' text-anchor='middle' fill='#333'>"
           "migration pair</text>")
lx = L + 12
for m, c in METHODS:
    out.append(f"<circle cx='{lx}' cy='{T+10}' r='4' fill='{c}'/>")
    out.append(f"<text x='{lx+8}' y='{T+14}' fill='#333'>{m}</text>")
    lx += 16 + 8 * len(m)
out.append(f"<path d='M{lx-4},{T+10} L{lx+14},{T+10}' stroke='#b00' stroke-width='2'/>")
out.append(f"<text x='{lx+18}' y='{T+14}' fill='#333'>centroid</text>")
lx += 84
out.append(f"<path d='M{lx+5},{T+4} L{lx+11},{T+10} L{lx+5},{T+16} L{lx-1},{T+10} Z' "
           "fill='none' stroke='#080' stroke-width='1.6'/>")
out.append(f"<text x='{lx+16}' y='{T+14}' fill='#333'>human</text>")
out.append('</svg>')
os.makedirs(f'{HERE}/../figures', exist_ok=True)
open(f'{HERE}/../figures/results.svg', 'w').write('\n'.join(out))
print('figures/results.svg written')
