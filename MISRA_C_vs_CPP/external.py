#!/usr/bin/env python3
"""external.py: the same measurements as measure.py, over public repositories.

Two purposes, both stated in the paper's Section 7:
  1. C systems by other authors, to test whether the median and boundary
     findings hold outside one author's code.
  2. C++ by other authors, to fix the feature rates the synthetic pairs are
     built at, so the C++ conditions are not a straw man.

Feature counts are lexical, over comment-stripped source. A semantic count
would need each project's build configuration; that is stated, not hidden.

Usage:  venv/bin/python external.py [--json out.json]
"""
import json, os, re, subprocess, sys
import measure as M

ROOT = os.path.expanduser("~/corpora")
GENERATED = []

# main implementation directory of each project, named so the selection is checkable
C_REPOS = [
    ("sqlite",   "ext-c/sqlite",   ["src"]),
    ("redis",    "ext-c/redis",    ["src"]),
    ("nginx",    "ext-c/nginx",    ["src"]),
    ("curl",     "ext-c/curl",     ["lib"]),
    ("postgres", "ext-c/postgres", ["src/backend"]),
]
RUST_REPOS = [
    ("ripgrep",  "ext-rust/ripgrep",  ["crates"]),
    ("tokio",    "ext-rust/tokio",    ["tokio"]),
    ("serde",    "ext-rust/serde",    ["serde", "serde_derive"]),
    ("hyper",    "ext-rust/hyper",    ["src"]),
    ("fd",       "ext-rust/fd",       ["src"]),
]
CPP_REPOS = [
    ("leveldb",  "ext-cpp/leveldb",  ["db", "table", "util", "include"]),
    ("rocksdb",  "ext-cpp/rocksdb",  ["db", "table", "util", "include"]),
    ("protobuf", "ext-cpp/protobuf", ["src/google/protobuf"]),
    ("fmt",      "ext-cpp/fmt",      ["include", "src"]),
    ("spdlog",   "ext-cpp/spdlog",   ["include"]),
    ("json",     "ext-cpp/json",     ["include"]),
]

C_EXT   = (".c", ".h")
CPP_EXT = (".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh", ".ipp")
RUST_EXT = (".rs",)
SKIP    = ("/test", "/tests", "/third_party", "/benchmark", "/example", "/fuzz", "/_deps")

GEN_MARK = re.compile(rb"(DO NOT EDIT|do not edit|[Gg]enerated by|[Aa]utomatically generated|"
                      rb"machine-generated|@generated|This file was generated|GENERATED FILE)")
GEN_NAME = re.compile(r"\.(pb|pb2)\.(cc|h)$|^(gram|scan|preproc|stem_)")

def is_generated(path):
    """Generated files are neither written nor maintained by a person; exclude them.
    Detected by name (protobuf output, bison/flex output, Snowball stemmers) or by a
    marker in the first 4 kB."""
    base = os.path.basename(path)
    if GEN_NAME.search(base):
        return True
    try:
        with open(path, "rb") as fh:
            return bool(GEN_MARK.search(fh.read(4096)))
    except Exception:
        return False

def files_of(repo, subdirs, exts):
    out = []
    for sd in subdirs:
        base = os.path.join(ROOT, repo, sd)
        for dp, _, fs in os.walk(base):
            low = dp.replace("\\", "/").lower()
            if any(k in low for k in SKIP):
                continue
            for f in sorted(fs):
                if f.endswith(exts) and not f.endswith(("_test.cc", "_test.cpp", "_test.h")):
                    full = os.path.join(dp, f)
                    if is_generated(full):
                        GENERATED.append(os.path.relpath(full, ROOT)); continue
                    out.append(os.path.relpath(full, os.path.expanduser("~")))
    return sorted(out)

def commit(repo):
    return subprocess.run(["git", "-C", os.path.join(ROOT, repo), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()

def max_fn(paths):
    """The highest-complexity function, and what file it is in."""
    import lizard
    best = None
    for p in paths:
        try:
            for fn in lizard.analyze_file(p).function_list:
                if best is None or fn.cyclomatic_complexity > best[0]:
                    best = (fn.cyclomatic_complexity, fn.nloc, fn.name, os.path.basename(p))
        except Exception:
            pass
    return best

# lexical feature counters, over comment-stripped source
FEATS = {
    "virtual":     re.compile(r"\bvirtual\b"),
    "override":    re.compile(r"\boverride\b"),
    "template":    re.compile(r"\btemplate\s*<"),
    "operator":    re.compile(r"\boperator\s*(?:[-+*/%^&|~!=<>]+|\(\s*\)|\[\s*\]|\bnew\b|\bdelete\b)"),
    "inherit":     re.compile(r"\b(?:class|struct)\s+\w[\w:<>, ]*\s*:\s*(?:public|protected|private|virtual)\b"),
    "smartptr":    re.compile(r"\b(?:unique_ptr|shared_ptr|weak_ptr|make_unique|make_shared)\b"),
    "classes":     re.compile(r"\b(?:class|struct)\s+\w+\s*(?:final\s*)?[:{]"),
    "namespaces":  re.compile(r"\bnamespace\s+\w+"),
    "auto":        re.compile(r"\bauto\b"),
    "lambda":      re.compile(r"\[\s*(?:&|=|\w+)?[^\]]*\]\s*\([^)]*\)\s*(?:mutable\s*)?(?:->[^{]+)?\{"),
}

def measure_repo(name, repo, subdirs, exts, feats=False):
    paths = files_of(repo, subdirs, exts)
    abspaths = [os.path.join(os.path.expanduser("~"), p) for p in paths]
    m = M.measure(name, paths, callgraph=False)
    m["commit"] = [commit(repo)]
    mf = max_fn(abspaths)
    if mf:
        m["max_ccn_fn"] = {"ccn": mf[0], "nloc": mf[1], "name": mf[2], "file": mf[3]}
    if feats:
        src = []
        for p in abspaths:
            try:
                src.append(M.strip_c_comments(open(p, encoding="utf-8", errors="replace").read()))
            except Exception:
                pass
        blob = "\n".join(src)
        kloc = m["code"] / 1000.0
        m["features"] = {k: len(r.findall(blob)) for k, r in FEATS.items()}
        m["per_kloc"] = {k: round(v / kloc, 2) for k, v in m["features"].items()}
    return m

if __name__ == "__main__":
    out = {"c": [], "cpp": []}
    for name, repo, sd in C_REPOS:
        print(f"  measuring {name} ...", file=sys.stderr)
        out["c"].append(measure_repo(name, repo, sd, C_EXT))
    for name, repo, sd in CPP_REPOS:
        print(f"  measuring {name} ...", file=sys.stderr)
        out["cpp"].append(measure_repo(name, repo, sd, CPP_EXT, feats=True))
    out["rust"] = []
    for name, repo, sd in RUST_REPOS:
        print(f"  measuring {name} ...", file=sys.stderr)
        out["rust"].append(measure_repo(name, repo, sd, RUST_EXT))
    out["generated_excluded"] = GENERATED
    print(f"  excluded {len(GENERATED)} generated files", file=sys.stderr)
    if "--json" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)

    def row(m, cols):
        def f(v):
            if isinstance(v, float): return f"{v:.1f}"
            return f"{v:,}" if isinstance(v, int) else str(v)
        return "| " + " | ".join(f(m.get(c)) for c in cols) + " |"

    print("\n## Public C systems, other authors\n")
    cols = ["set", "commit", "files", "code", "functions", "fn_nloc_median", "fn_nloc_p90",
            "fn_nloc_max", "ccn_median", "ccn_p90", "ccn_max", "ccn_gt10", "nesting"]
    print("| " + " | ".join(cols) + " |"); print("|" + "---|" * len(cols))
    for m in out["c"]:
        print(row(m, cols))
    print("\nHighest-complexity function per project:\n")
    for m in out["c"] + out["cpp"]:
        k = m.get("max_ccn_fn")
        if k: print(f"  {m['set']:10} {k['name']} ({k['file']})  CCN {k['ccn']}, NLOC {k['nloc']}")

    print("\n## Public C++, other authors\n")
    print("| " + " | ".join(cols) + " |"); print("|" + "---|" * len(cols))
    for m in out["cpp"]:
        print(row(m, cols))

    print("\n## C++ feature rates, per 1,000 code lines (lexical)\n")
    keys = list(FEATS)
    print("| project | code | " + " | ".join(keys) + " |"); print("|" + "---|" * (len(keys) + 2))
    for m in out["cpp"]:
        print(f"| {m['set']} | {m['code']:,} | " + " | ".join(f"{m['per_kloc'][k]:.1f}" for k in keys) + " |")
    tot = {k: sum(m["features"][k] for m in out["cpp"]) for k in keys}
    tk = sum(m["code"] for m in out["cpp"]) / 1000.0
    print(f"| **all** | {int(tk*1000):,} | " + " | ".join(f"**{tot[k]/tk:.1f}**" for k in keys) + " |")
