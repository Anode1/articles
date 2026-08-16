"""Extract every consecutive ERD.mwb pair from kul's history for the pre-registered sweep.

Per pair: the frozen context is the PREVIOUS revision's live diagram (tables present in both
revisions, at previous coordinates); the added tables are those on the current diagram only,
with the human's answer being their current coordinates; edges are the current diagram's FK
edges restricted to surviving+added tables. Real table names stay in this scratchpad only;
nothing here is committed. Emits pairNN.h in erd_data.h's format plus ERD_DISPLACEMENT (the
median move of surviving tables) and an inventory line per pair.
"""
import json, os, re, subprocess, sys, zipfile, io, statistics

KUL = os.path.expanduser('~/kul')
OUT = os.path.dirname(os.path.abspath(__file__))

def revisions():
    out = subprocess.run(['git', '-C', KUL, 'log', '--reverse', '--format=%H %s',
                          '--', 'doc/DataModel/ERD.mwb'],
                         capture_output=True, text=True, check=True).stdout
    return [line.split(' ', 1) for line in out.strip().split('\n')]

def load_xml(rev):
    blob = subprocess.run(['git', '-C', KUL, 'show', f'{rev}:doc/DataModel/ERD.mwb'],
                          capture_output=True, check=True).stdout
    z = zipfile.ZipFile(io.BytesIO(blob))
    return z.read('document.mwb.xml').decode('utf-8', 'replace')

def parse(xml):
    """Figures of the live diagram (the one whose FK links resolve best) + FK edges."""
    fks = []
    starts = [m.start() for m in re.finditer(
        r'<value type="object" struct-name="db\.mysql\.ForeignKey" id="[0-9a-f-]+"', xml)]
    for i, s in enumerate(starts):
        b = xml[s:starts[i+1] if i+1 < len(starts) else s+6000]
        own = re.search(r'struct-name="db\.Table" key="owner">([0-9a-f-]+)</link>', b)
        ref = re.search(r'key="referencedTable">([0-9a-f-]+)</link>', b)
        if own and ref:
            fks.append((own.group(1), ref.group(1)))
    diagrams = {}
    for m in re.finditer(r'<value type="object" struct-name="workbench\.physical\.TableFigure"'
                         r'.*?key="name">([^<]*)</value>', xml, re.S):
        b = m.group(0)
        diag = re.search(r'struct-name="model\.Diagram" key="owner">([0-9a-f-]+)</link>', b)
        tid = re.search(r'key="table">([0-9a-f-]+)</link>', b)
        if not diag or not tid:
            continue
        geo = [float(re.search(rf'type="real" key="{k}">([-\d.]+)</value>', b).group(1))
               for k in ('left', 'top', 'width', 'height')]
        diagrams.setdefault(diag.group(1), {})[tid.group(1)] = (m.group(1), geo)
    best, bestedges = None, -1
    for figs in diagrams.values():
        names = {t: n for t, (n, g) in figs.items()}
        edges = {(names[o], names[r]) for o, r in fks
                 if o in names and r in names and o != r}
        if len(edges) > bestedges:
            best, bestedges = figs, len(edges)
    names = {t: n for t, (n, g) in best.items()}
    figs = {n: g for t, (n, g) in best.items()}
    edges = sorted({(names[o], names[r]) for o, r in fks
                    if o in names and r in names and o != r})
    return figs, edges

def emit(idx, prev_figs, cur_figs, cur_edges, path):
    surviving = sorted(set(prev_figs) & set(cur_figs))
    added = sorted(set(cur_figs) - set(prev_figs))
    if not added:
        return None
    keep = set(surviving) | set(added)
    edges = [(a, b) for a, b in cur_edges if a in keep and b in keep]
    order = surviving + added
    io_of = {n: i for i, n in enumerate(order)}
    # frozen at PREVIOUS coordinates; added at current (the human's answer)
    geo = {n: (prev_figs[n] if n in set(surviving) else cur_figs[n]) for n in order}
    disp = statistics.median(
        abs(prev_figs[n][0] - cur_figs[n][0]) + abs(prev_figs[n][1] - cur_figs[n][1])
        for n in surviving) if surviving else 0.0
    W = max(g[0] + g[2] for g in geo.values()) + 40
    H = max(g[1] + g[3] for g in geo.values()) + 40
    with open(path, 'w') as f:
        f.write(f'#define ERD_NFIXED {len(surviving)}\n')
        f.write(f'#define ERD_NNEW   {len(added)}\n')
        f.write(f'#define ERD_NEDGE  {len(edges)}\n')
        f.write(f'#define ERD_CW     {W:g}\n')
        f.write(f'#define ERD_CH     {H:g}\n')
        f.write(f'#define ERD_DISPLACEMENT {disp:g}\n')
        f.write(f'static const char *const erd_name[{len(order)}] = {{\n')
        for n in order:
            f.write(f'    "{n}",\n')
        f.write('};\n')
        for arr, j in (('cx', 0), ('cy', 1)):
            v = ['%g' % (geo[n][j] + geo[n][j+2] / 2) for n in order]
            f.write(f'static const double erd_{arr}[{len(order)}] = {{ '
                    + ', '.join(v) + ' };\n')
        for arr, j in (('w', 2), ('h', 3)):
            v = ['%g' % geo[n][j] for n in order]
            f.write(f'static const double erd_{arr}[{len(order)}] = {{ '
                    + ', '.join(v) + ' };\n')
        f.write(f'static const long erd_edge[{len(edges)}][2] = {{ '
                + ', '.join('{%d,%d}' % (io_of[a], io_of[b]) for a, b in edges)
                + ' };\n')
    return dict(pair=idx, nfixed=len(surviving), nnew=len(added),
                nedge=len(edges), disp=round(disp, 1))

revs = revisions()
print(f'{len(revs)} revisions')
inventory = []
xml_cache = {}
for i in range(1, len(revs)):
    (ra, sa), (rb, sb) = revs[i-1], revs[i]
    for r in (ra, rb):
        if r not in xml_cache:
            xml_cache[r] = parse(load_xml(r))
    prev_figs, _ = xml_cache[ra]
    cur_figs, cur_edges = xml_cache[rb]
    info = emit(i, prev_figs, cur_figs, cur_edges, f'{OUT}/pair{i:02d}.h')
    label = sb[:44]
    if info:
        inventory.append(info)
        print(f'pair{i:02d}: frozen {info["nfixed"]:3d} added {info["nnew"]:2d} '
              f'edges {info["nedge"]:3d} disp {info["disp"]:7.1f}  "{label}"')
    else:
        print(f'pair{i:02d}: EXCLUDED, no tables added                        "{label}"')
json.dump(inventory, open(f'{OUT}/inventory.json', 'w'), indent=1)
print(f'{len(inventory)} usable pairs')
