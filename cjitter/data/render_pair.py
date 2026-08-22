"""Render one benchmark instance for the paper's figures.

The routing is render.py's, which is erd.c's rule: two L shapes and Z shapes sliding across
the channel, least penetration wins, length breaks ties. Table names are replaced by letters
here as they are in the shipped example, because the geometry is publishable and the names are
not.

    python3 render_pair.py pair12_seen.h layouts.txt out-prefix
"""
import re, sys, string

added = set()



T = [-0.25, 0.15, 0.3, 0.5, 0.7, 0.85, 1.25]


def pen_of(pts, figs, skip):
    """Penetration of an axis-aligned polyline into every table except the endpoints' own,
    open intervals at the borders, exactly as erd.c's apen computes it."""
    p = 0.0
    for n, f in figs.items():
        if n in skip:
            continue
        x0, y0, w, h = f
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if y1 == y2:
                if y0 < y1 < y0 + h:
                    lo, hi = max(min(x1, x2), x0), min(max(x1, x2), x0 + w)
                    if hi > lo:
                        p += hi - lo
            else:
                if x0 < x1 < x0 + w:
                    lo, hi = max(min(y1, y2), y0), min(max(y1, y2), y0 + h)
                    if hi > lo:
                        p += hi - lo
    return p


def seg_cross(a1, a2, b1, b2):
    def orient(p, q, r):
        return (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
    d1, d2 = orient(a1, a2, b1), orient(a1, a2, b2)
    d3, d4 = orient(b1, b2, a1), orient(b1, b2, a2)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def cross_count(pts, others):
    k = 0
    for opts in others:
        for s1 in zip(pts, pts[1:]):
            for s2 in zip(opts, opts[1:]):
                if seg_cross(s1[0], s1[1], s2[0], s2[1]):
                    k += 1
    return k


TIN = [0.15, 0.3, 0.5, 0.7, 0.85]
TOUT = [-0.75, -0.5, -0.25, 1.25, 1.5, 1.75]


def route(a, b, figs, cx, offs, already):
    """Same rule as erd.c: the candidate pays penetration and crossings against every edge
    already routed, in-channel shapes first, a clean one ends the search."""
    (ax, ay), (bx, by) = cx[a], cx[b]
    fa, fb = figs[a], figs[b]
    oa, ob = offs
    ya, xa = ay + oa * fa[3], ax + oa * fa[2]
    yb, xb = by + ob * fb[3], bx + ob * fb[2]
    cands = [[(ax, ya), (xb, ya), (xb, by)], [(xa, ay), (xa, yb), (bx, yb)]]
    for t in TIN:
        mx = ax + t * (bx - ax)
        cands.append([(ax, ya), (mx, ya), (mx, yb), (bx, yb)])
    for t in TIN:
        my = ay + t * (by - ay)
        cands.append([(xa, ay), (xa, my), (xb, my), (xb, by)])
    for t in TOUT:
        mx = ax + t * (bx - ax)
        cands.append([(ax, ya), (mx, ya), (mx, yb), (bx, yb)])
    for t in TOUT:
        my = ay + t * (by - ay)
        cands.append([(xa, ay), (xa, my), (xb, my), (xb, by)])
    best, bestcost = None, None
    for i, pts in enumerate(cands):
        pen = pen_of(pts, figs, {a, b})
        length = sum(abs(x2 - x1) + abs(y2 - y1)
                     for (x1, y1), (x2, y2) in zip(pts, pts[1:]))
        crs = cross_count(pts, already)
        cost = 100.0 * (pen + crs) + length
        if bestcost is None or cost < bestcost:
            best, bestcost = pts, cost
            if pen == 0 and crs == 0 and i < 12:
                break
    return best


def trim(p0, p1, f):
    """Border position as a fraction of the segment leaving a table's centre."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    t = 2.0
    if dx:
        t = min(t, (f[2] / 2) / abs(dx))
    if dy:
        t = min(t, (f[3] / 2) / abs(dy))
    return t


def anchor(pts, fa, fb):
    """Connectors leave a table's border, never its centre; same rule as erd.c's anchor."""
    pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
    if len(pts) < 2:
        return pts
    if len(pts) == 2:
        ta, tb = trim(pts[0], pts[1], fa), trim(pts[1], pts[0], fb)
        if ta + tb < 1:
            (x0, y0), (x1, y1) = pts
            dx, dy = x1 - x0, y1 - y0
            pts = [(x0 + ta * dx, y0 + ta * dy), (x1 - tb * dx, y1 - tb * dy)]
        return pts
    t = trim(pts[0], pts[1], fa)
    if t <= 1:
        (x0, y0), (x1, y1) = pts[0], pts[1]
        pts[0] = (x0 + t * (x1 - x0), y0 + t * (y1 - y0))
    t = trim(pts[-1], pts[-2], fb)
    if t <= 1:
        (x0, y0), (x1, y1) = pts[-1], pts[-2]
        pts[-1] = (x0 + t * (x1 - x0), y0 + t * (y1 - y0))
    return pts


FORCE_WH = None


def render(rev, path, mark_added, straight=False):
    figs, edges = rev['figs'], rev['edges']
    if FORCE_WH:
        W, H = FORCE_WH
    else:
        W = max(f[0] + f[2] for f in figs.values()) + 40
        H = max(f[1] + f[3] for f in figs.values()) + 40
    cx = {n: (f[0] + f[2] / 2, f[1] + f[3] / 2) for n, f in figs.items()}
    # each edge leaves its table at its own attachment slot, same rule as erd.c: the j-th of
    # a table's d edges at fraction ((j+1)/(d+1) - 1/2) * 0.8 of the side
    deg, seen = {}, {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    slots = []
    for a, b in edges:
        sa, sb = seen.get(a, 0), seen.get(b, 0)
        seen[a], seen[b] = sa + 1, sb + 1
        slots.append((((sa + 1) / (deg[a] + 1) - 0.5) * 0.8,
                      ((sb + 1) / (deg[b] + 1) - 0.5) * 0.8))
    out = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 %g %g' "
           "font-family='sans-serif'>" % (W, H),
           "<rect width='%g' height='%g' fill='#fafafa'/>" % (W, H)]
    already = []
    for (a, b), off in zip(edges, slots):
        nu = mark_added and (a in added or b in added)
        pts = [cx[a], cx[b]] if straight else route(a, b, figs, cx, off, already)
        pts = anchor(pts, figs[a], figs[b])
        already.append(pts)
        out.append("<polyline points='%s' fill='none' stroke='%s' stroke-width='2'/>"
                   % (' '.join('%g,%g' % p for p in pts), '#c60' if nu else '#999'))
    for n, f in figs.items():
        nu = mark_added and n in added
        out.append("<rect x='%g' y='%g' width='%g' height='%g' rx='6' fill='%s' "
                   "stroke='%s' stroke-width='2'/>"
                   % (f[0], f[1], f[2], f[3], '#fc3' if nu else '#e8e8e8',
                      '#963' if nu else '#555'))
        out.append("<text x='%g' y='%g' text-anchor='middle' font-size='22' fill='%s'>%s</text>"
                   % (f[0] + f[2] / 2, f[1] + f[3] / 2 + 7,
                      '#630' if nu else '#333', n))
    out.append('</svg>')
    open(path, 'w').write('\n'.join(out))
    print(path, len(figs), 'tables,', len(edges), 'edges, canvas %gx%g' % (W, H))




def letters(n):
    out = []
    for i in range(n):
        s, j = "", i
        while True:
            s = string.ascii_uppercase[j % 26] + s
            j = j // 26 - 1
            if j < 0:
                break
        out.append(s)
    return out


def load_header(path):
    t = open(path).read()
    g = lambda k: int(re.search(rf"#define {k}\s+(\d+)", t).group(1))
    nf, nn, ne = g("ERD_NFIXED"), g("ERD_NNEW"), g("ERD_NEDGE")
    arr = {}
    for a in ("cx", "cy", "w", "h"):
        m = re.search(rf"erd_{a}\[\d+\]\s*=\s*\{{(.*?)\}};", t, re.S)
        arr[a] = [float(x) for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
    m = re.search(r"erd_edge\[\d+\]\[2\]\s*=\s*\{(.*?)\};", t, re.S)
    edges = [tuple(int(v) for v in e.split(",")) for e in re.findall(r"\{(\d+,\d+)\}", m.group(1))]
    return nf, nn, arr, edges


def build(nf, nn, arr, edges, override=None):
    """figs keyed by letter, [left, top, w, h]; override replaces the added tables' centres."""
    lab = letters(nf + nn)
    cx = list(arr["cx"]); cy = list(arr["cy"])
    if override:
        for k in range(nn):
            cx[nf + k] = override[2 * k]
            cy[nf + k] = override[2 * k + 1]
    figs = {lab[i]: [cx[i] - arr["w"][i] / 2, cy[i] - arr["h"][i] / 2, arr["w"][i], arr["h"][i]]
            for i in range(nf + nn)}
    return figs, [(lab[a], lab[b]) for a, b in edges], set(lab[nf:])


if __name__ == "__main__":
    hdr, lays, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
    nf, nn, arr, edges = load_header(hdr)
    want = sys.argv[4].split(",") if len(sys.argv) > 4 else ["human", "centroid", "climb"]
    rows = [l.split() for l in open(lays) if not l.startswith("#")]
    rows = [f for f in rows if f[0] in want]
    W = H = 0
    for f in rows:
        vec = [float(x) for x in f[4:4 + 2 * nn]]
        figs, _, _ = build(nf, nn, arr, edges, vec)
        W = max(W, max(v[0] + v[2] for v in figs.values()) + 40)
        H = max(H, max(v[1] + v[3] for v in figs.values()) + 40)
    FORCE_WH = (W, H)
    globals()["FORCE_WH"] = FORCE_WH
    for f in rows:
        vec = [float(x) for x in f[4:4 + 2 * nn]]
        figs, es, add = build(nf, nn, arr, edges, vec)
        added.clear(); added.update(add)
        render({"figs": figs, "edges": es}, f"{prefix}-{f[0]}.svg", True)
