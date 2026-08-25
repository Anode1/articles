#!/usr/bin/env python3
"""jpa.py: artifacts per persisted entity, over public Spring/JPA applications.

System A serves 37 tables through 39 DAO classes and one data carrier. The
conventional stack states the same behaviour across an entity, a repository, a
service, a controller and a mapper. This counts what real applications actually
carry, so the comparison is a distribution rather than one system scaled.

An application qualifies only if it persists with JPA: at least 5 @Entity classes.
Tutorial repositories that hold dozens of unrelated demos are excluded by hand,
since their per-entity ratios describe a book, not a system.

  venv/bin/python jpa.py [--json out.json]
"""
import json, os, re, subprocess, sys

ROOT = os.path.expanduser("~/corpora/ext-java")
SKIP_DIR = re.compile(r"/(test|tests|target|build|generated)/", re.I)
PAT = {
    "entity":     re.compile(r"@Entity\b"),
    "repository": re.compile(r"extends\s+(?:Jpa|Crud|Paging(?:AndSorting)?|Mongo|Reactive\w*)Repository|@Repository\b"),
    "service":    re.compile(r"@Service\b"),
    "controller": re.compile(r"@(?:Rest)?Controller\b"),
    "mapper":     re.compile(r"@Mapper\b|\bMapper\b"),
    "dto":        re.compile(r"\bDto\b|\bDTO\b"),
    "transact":   re.compile(r"@Transactional\b"),
}

def scan(app):
    d = os.path.join(ROOT, app)
    counts = {k: 0 for k in PAT}
    files = lines = 0
    for dp, _, fs in os.walk(d):
        if SKIP_DIR.search(dp.replace("\\", "/") + "/"):
            continue
        for f in fs:
            if not f.endswith(".java"):
                continue
            p = os.path.join(dp, f)
            try:
                src = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            files += 1
            lines += sum(1 for l in src.split("\n") if l.strip())
            for k, rx in PAT.items():
                if rx.search(src):
                    counts[k] += 1
    return {"app": app, "files": files, "nonblank_lines": lines, **counts}

if __name__ == "__main__":
    apps = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    out = []
    for a in apps:
        r = scan(a)
        if r["entity"] >= 5:
            r["files_per_entity"] = round(r["files"] / r["entity"], 2)
            r["lines_per_entity"] = round(r["nonblank_lines"] / r["entity"], 1)
            r["layers_per_entity"] = round(
                (r["entity"] + r["repository"] + r["service"] + r["controller"] + r["mapper"]) / r["entity"], 2)
            out.append(r)
        print(f"  {a:46} files {r['files']:5}  @Entity {r['entity']:4}"
              f"  {'INCLUDED' if r['entity'] >= 5 else 'skipped (<5 entities)'}", file=sys.stderr)
    if "--json" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    if not out:
        sys.exit("no qualifying applications")
    import statistics as st
    print("\n| application | files | entities | files/entity | lines/entity | layer classes/entity |")
    print("|---|---|---|---|---|---|")
    for r in sorted(out, key=lambda x: -x["entity"]):
        print(f"| {r['app']} | {r['files']:,} | {r['entity']} | {r['files_per_entity']} "
              f"| {r['lines_per_entity']:,.0f} | {r['layers_per_entity']} |")
    for k in ("files_per_entity", "lines_per_entity", "layers_per_entity"):
        v = [r[k] for r in out]
        print(f"\n{k}: n={len(v)} median {st.median(v):,.2f}  min {min(v):,.2f}  max {max(v):,.2f}")
