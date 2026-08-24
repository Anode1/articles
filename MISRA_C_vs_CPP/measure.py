#!/usr/bin/env python3
"""measure.py: source measurements over the real Anode1 repositories.

Usage:  venv/bin/python measure.py [--json out.json]

Every number in the paper's source tables comes from here. The sets are named
below with their files; each repository's commit is recorded in the output.

Measures, per set:
  files, physical lines, blank, comment, code (cloc 1.98);
  lexical tokens and identifier tokens of the comment-stripped source (the
  lexer in this file; Python via the stdlib tokenize module);
  LLM tokens of the raw file (tiktoken o200k_base and cl100k_base);
  functions, NLOC per function, cyclomatic complexity per function (lizard),
  max brace nesting (brace languages) or indent depth (Python);
  for C sets: function-like macros, and the intra-project call graph from
  libclang (fan-out, longest call chain).
"""
import json, os, re, statistics, subprocess, sys, tokenize, io, keyword

HOME = os.path.expanduser("~")
LIZARD_EXT = {"c": "c", "h": "c", "java": "java", "rs": "rust", "py": "python",
              "cc": "cpp", "cpp": "cpp", "cxx": "cpp", "hpp": "cpp", "hh": "cpp", "ipp": "cpp"}

SETS = [
  # same algorithm, five languages, same author (ais/tests/perf, LANG_COMPARISON.md)
  ("bench/C",      ["ais/tests/perf/bench.c"]),
  ("bench/Ada",    ["ais/tests/perf/bench.adb"]),
  ("bench/Rust",   ["ais/tests/perf/bench.rs"]),
  ("bench/Java",   ["ais/tests/perf/Bench.java"]),
  ("bench/Python", ["ais/tests/perf/bench.py"]),
  # same command set and demo, two languages (mincdp)
  ("mincdp/C",    ["mincdp/c/cdp.h", "mincdp/c/demo.c"]),
  ("mincdp/Java", ["mincdp/java/Cdp.java", "mincdp/java/Demo.java"]),
  # linearr: Linearr.java is main.c+process.c, Regress.java is regress.c, Csv.java is csv.c
  ("linearr/C",    ["linearr/c/main.c", "linearr/c/process.c", "linearr/c/process.h",
                    "linearr/c/regress.c", "linearr/c/regress.h", "linearr/c/csv.c", "linearr/c/csv.h"]),
  ("linearr/Java", ["linearr/java/Linearr.java", "linearr/java/Regress.java", "linearr/java/Csv.java"]),
  # the ais key/posting subsystem the earlier draft counted
  ("ais/key+post", ["ais/c/key.c", "ais/c/key.h", "ais/c/post.c", "ais/c/post.h"]),
]

def globset(rel, exts, exclude=()):
    d = os.path.join(HOME, rel)
    out = []
    for f in sorted(os.listdir(d)):
        if f.split(".")[-1] in exts and f not in exclude:
            out.append(os.path.join(rel, f))
    return out

def javaset(rel, third_party=()):
    """Every .java under rel, excluding tests/ packages and named third-party files."""
    root = os.path.join(HOME, rel)
    return sorted(os.path.relpath(os.path.join(dp, f), HOME)
                  for dp, _, fs in os.walk(root)
                  for f in fs
                  if f.endswith(".java") and "/tests" not in dp and f not in third_party)

# whole projects: the C corpus (tests.c excluded, it is a unit-test file) and the
# author's Java for contrast
CORPUS = [
  ("ais/c",         globset("ais/c", ("c", "h"), exclude=("tests.c",))),
  ("cjitter/c",     globset("cjitter/c", ("c", "h"))),
  ("bpnn/c",        globset("bpnn/c", ("c", "h"))),
  ("linearr/c",     globset("linearr/c", ("c", "h"), exclude=("tests.c",))),
  ("iac",           globset("iac", ("c", "h"), exclude=("tests.c",))),
  ("graphcrawl/c",  globset("graphcrawl/c", ("c", "h"), exclude=("tests.c", "web.c"))),   # web.c: generated embed of web/
  ("mincdp/c",      globset("mincdp/c", ("c", "h"))),
  ("ljms/src",      [os.path.join("ljms/src/org/ljms", f) for f in sorted(os.listdir(os.path.join(HOME, "ljms/src/org/ljms")))]),
  # a commercial project, private repository, production Java only. Not named
  # here: set PRIVATE_JAVA to its source root to include it, and the row is skipped without it.
  ("systemA/java",  sorted(os.path.relpath(os.path.join(dp, f), HOME) for dp, _, fs in os.walk(os.path.join(HOME, os.environ.get("PRIVATE_JAVA", "")))
                           for f in fs if f.endswith(".java") and "/tests" not in dp) if os.environ.get("PRIVATE_JAVA") else []),
  # the 2009/2011 genomics Java, written before the C style guide; tests and the two
  # third-party files (Sun's SwingWorker, SourcePortal's UCProperties) excluded
  ("aisgedcom/src", javaset("aisgedcom/src", third_party=("SwingWorker.java", "UCProperties.java"))),
  ("aisconvert/src", javaset("aisconvert/src", third_party=("SwingWorker.java",))),
  ("linearr/java",  globset("linearr/java", ("java",))),
  ("mincdp/java",   globset("mincdp/java", ("java",))),
]

def lang_of(path):
    return path.rsplit(".", 1)[-1]

# ---------------------------------------------------------------- lexing
C_KW = set("""auto break case char const continue default do double else enum extern float for goto if
inline int long register restrict return short signed sizeof static struct switch typedef union unsigned
void volatile while _Bool _Complex _Imaginary""".split())
JAVA_KW = set("""abstract assert boolean break byte case catch char class const continue default do double
else enum extends final finally float for goto if implements import instanceof int interface long native
new package private protected public return short static strictfp super switch synchronized this throw
throws transient try void volatile while true false null var record""".split())
RUST_KW = set("""as break const continue crate else enum extern false fn for if impl in let loop match mod
move mut pub ref return self Self static struct super trait true type unsafe use where while dyn""".split())
ADA_KW = set("""abort abs abstract accept access aliased all and array at begin body case constant declare
delay delta digits do else elsif end entry exception exit for function generic goto if in interface is
limited loop mod new not null of or others out overriding package pragma private procedure protected raise
range record rem renames requeue return reverse select separate some subtype synchronized tagged task
terminate then type until use when while with xor""".split())
CPP_KW = C_KW | set("""alignas alignof and and_eq asm bitand bitor bool catch char8_t char16_t char32_t
class compl concept consteval constexpr constinit const_cast co_await co_return co_yield decltype delete
dynamic_cast explicit export false friend mutable namespace new noexcept not not_eq nullptr operator or
or_eq private protected public reinterpret_cast requires static_assert static_cast template this
thread_local throw true try typeid typename using virtual wchar_t xor xor_eq override final auto""".split())

KW = {"c": C_KW, "h": C_KW, "java": JAVA_KW, "rs": RUST_KW, "adb": ADA_KW, "ads": ADA_KW,
      "cc": CPP_KW, "cpp": CPP_KW, "cxx": CPP_KW, "hpp": CPP_KW, "hh": CPP_KW, "ipp": CPP_KW}

OPS = sorted("""<<= >>= ... -> :: ++ -- += -= *= /= %= &= |= ^= == != <= >= && || << >> => .. **
:= /= <> ..= ::< """.split(), key=len, reverse=True)

def strip_c_comments(src):
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c == '"' or c == "'":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append(src[i:j + 1]); i = j + 1
        elif src.startswith("//", i):
            j = src.find("\n", i); i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2); out.append(" "); i = n if j < 0 else j + 2
        else:
            out.append(c); i += 1
    return "".join(out)

def strip_ada_comments(src):
    out = []
    for line in src.split("\n"):
        i, ins = 0, False
        while i < len(line):
            if line[i] == '"': ins = not ins
            elif not ins and line.startswith("--", i):
                line = line[:i]; break
            i += 1
        out.append(line)
    return "\n".join(out)

TOK = re.compile(r"""
  (?P<str>"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])')        # string / char literal
| (?P<num>0[xX][0-9a-fA-F_]+|\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?[a-zA-Z_]*)
| (?P<id>[A-Za-z_][A-Za-z0-9_]*)
| (?P<op>%s)
| (?P<pu>[^\s])
""" % "|".join(re.escape(o) for o in OPS), re.X)

def lex_generic(src, lang):
    """token list of comment-stripped source: (kind, text)."""
    src = strip_ada_comments(src) if lang in ("adb", "ads") else strip_c_comments(src)
    toks = []
    for m in TOK.finditer(src):
        kind = m.lastgroup; text = m.group()
        if kind == "id" and text.lower() in KW[lang] if lang in ("adb", "ads") else (kind == "id" and text in KW[lang]):
            kind = "kw"
        toks.append((kind, text))
    return toks

def lex_python(src):
    toks = []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type in (tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER):
            continue
        if t.type == tokenize.NAME:
            toks.append(("kw" if keyword.iskeyword(t.string) else "id", t.string))
        elif t.type == tokenize.STRING: toks.append(("str", t.string))
        elif t.type == tokenize.NUMBER: toks.append(("num", t.string))
        elif t.type == tokenize.OP: toks.append(("op", t.string))
        else: toks.append(("layout", t.type))          # NEWLINE INDENT DEDENT
    return toks

def max_nesting(toks, lang):
    depth = mx = 0
    prev = None
    for kind, text in toks:
        after_end = prev == "end"; prev = text.lower() if kind == "kw" else None
        if after_end: continue                       # `end loop`, `end if`: the second word does not open
        if lang == "py":
            if kind == "layout" and text == tokenize.INDENT: depth += 1; mx = max(mx, depth)
            elif kind == "layout" and text == tokenize.DEDENT: depth -= 1
        elif lang in ("adb", "ads"):
            w = text.lower() if kind == "kw" else ""
            if w in ("begin", "loop", "if", "case", "record", "select"): depth += 1; mx = max(mx, depth)
            elif w == "end": depth -= 1
        else:
            if text == "{": depth += 1; mx = max(mx, depth)
            elif text == "}": depth -= 1
    return mx

# ---------------------------------------------------------------- tools
def cloc(files):
    r = subprocess.run(["cloc", "--json", "--quiet", "--by-file"] + files, capture_output=True, text=True)
    d = json.loads(r.stdout)
    tot = {"blank": 0, "comment": 0, "code": 0}
    for k, v in d.items():
        if k in ("header", "SUM"): continue
        for m in tot: tot[m] += v[m]
    return tot

def lizard_funcs(path):
    import lizard
    ext = lang_of(path)
    if ext not in LIZARD_EXT: return None
    fi = lizard.analyze_file(path)
    return [(f.name, f.nloc, f.cyclomatic_complexity, f.length) for f in fi.function_list]

def c_callgraph(files):
    """intra-project call graph of the C files via libclang. Returns
    (defined functions, edges, fan-out list, longest chain, parse diagnostics)."""
    import clang.cindex as ci
    if not ci.Config.loaded:
        for so in ("/usr/lib/llvm-18/lib/libclang-18.so.1", "/usr/lib/x86_64-linux-gnu/libclang-18.so.1"):
            if os.path.exists(so):
                ci.Config.set_library_file(so); break
    idx = ci.Index.create()
    incdirs = sorted({os.path.dirname(f) for f in files})
    args = ["-std=c99", "-D_POSIX_C_SOURCE=200809L", "-D_DEFAULT_SOURCE",
            "-isystem", "/usr/lib/gcc/x86_64-linux-gnu/13/include"] + ["-I" + d for d in incdirs]
    defined, calls, errs = set(), {}, 0
    fileset = set(files)
    for f in files:
        if not f.endswith(".c"): continue
        tu = idx.parse(f, args=args)
        errs += sum(1 for d in tu.diagnostics if d.severity >= ci.Diagnostic.Error)
        def walk(node, cur):
            if node.kind == ci.CursorKind.FUNCTION_DECL and node.is_definition() and node.location.file and node.location.file.name in fileset:
                cur = node.spelling; defined.add(cur); calls.setdefault(cur, set())
            elif node.kind == ci.CursorKind.CALL_EXPR and cur:
                ref = node.referenced
                if ref is not None and ref.spelling: calls[cur].add(ref.spelling)
            for ch in node.get_children(): walk(ch, cur)
        walk(tu.cursor, None)
    g = {u: {v for v in vs if v in defined and v != u} for u, vs in calls.items()}
    # longest chain, back edges cut by DFS colouring
    memo, onstack = {}, set()
    def depth(u):
        if u in memo: return memo[u]
        onstack.add(u); best = 0
        for v in g.get(u, ()):
            if v in onstack: continue
            best = max(best, 1 + depth(v))
        onstack.discard(u); memo[u] = best; return best
    longest = max((depth(u) for u in g), default=0)
    fanout = [len(vs) for vs in g.values()]
    nedges = sum(fanout)
    return len(defined), nedges, fanout, longest, errs

def macros(files):
    n = 0
    for f in files:
        if lang_of(f) in ("c", "h"):
            n += len(re.findall(r"^\s*#\s*define\s+\w+\(", open(f).read(), re.M))
    return n

def git_commit(rel):
    top = os.path.join(HOME, rel.split("/")[0])
    return subprocess.run(["git", "-C", top, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()

# ---------------------------------------------------------------- measure
def q(xs, p):
    if not xs: return None
    xs = sorted(xs); k = (len(xs) - 1) * p; lo = int(k); hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

def measure(name, rels, callgraph=False):
    import tiktoken
    enc_o = tiktoken.get_encoding("o200k_base"); enc_c = tiktoken.get_encoding("cl100k_base")
    files = [os.path.join(HOME, r) for r in rels]
    m = {"set": name, "files": len(files), "commit": sorted({git_commit(r) for r in rels}),
         "physical": 0, "lex_tokens": 0, "id_tokens": 0, "distinct_ids": 0, "llm_o200k": 0, "llm_cl100k": 0,
         "llm_o200k_stripped": 0, "nesting": 0, "bytes": 0}
    m.update(cloc(files))
    ids, funcs, nest = set(), [], 0
    for f in files:
        src = open(f, encoding="utf-8", errors="replace").read()
        lang = lang_of(f)
        m["physical"] += src.count("\n") + (0 if src.endswith("\n") or not src else 1)
        m["bytes"] += len(src.encode())
        toks = lex_python(src) if lang == "py" else lex_generic(src, lang)
        m["lex_tokens"] += len(toks)
        these = [t for k, t in toks if k == "id"]
        m["id_tokens"] += len(these); ids.update(these)
        m["nesting"] = max(m["nesting"], max_nesting(toks, lang))
        m["llm_o200k"] += len(enc_o.encode(src)); m["llm_cl100k"] += len(enc_c.encode(src))
        stripped = strip_ada_comments(src) if lang in ("adb", "ads") else (src if lang == "py" else strip_c_comments(src))
        if lang == "py":
            stripped = "\n".join(l for l in src.split("\n") if not l.strip().startswith("#"))
        m["llm_o200k_stripped"] += len(enc_o.encode(stripped))
        lf = lizard_funcs(f)
        if lf is not None: funcs += lf
    m["distinct_ids"] = len(ids)
    if funcs:
        nl = [x[1] for x in funcs]; cc = [x[2] for x in funcs]
        m.update({"functions": len(funcs), "fn_nloc_median": q(nl, .5), "fn_nloc_p90": q(nl, .9), "fn_nloc_max": max(nl),
                  "ccn_median": q(cc, .5), "ccn_p90": q(cc, .9), "ccn_max": max(cc), "ccn_gt10": sum(1 for c in cc if c > 10)})
    else:
        m["functions"] = None
    if callgraph and any(f.endswith(".c") for f in files):
        nd, ne, fo, longest, errs = c_callgraph(files)
        m.update({"cg_functions": nd, "cg_edges": ne, "cg_fanout_median": q(fo, .5), "cg_fanout_max": max(fo) if fo else 0,
                  "cg_longest_chain": longest, "cg_parse_errors": errs, "fn_macros": macros(files)})
    return m

def fmt(v):
    if v is None: return "n/a"
    if isinstance(v, float): return f"{v:.1f}"
    if isinstance(v, list): return ",".join(v)
    return str(v)

def table(rows, cols):
    print("| " + " | ".join(c for c, _ in cols) + " |")
    print("|" + "|".join("---:" if i else ":---" for i, _ in enumerate(cols)) + "|")
    for r in rows:
        print("| " + " | ".join(fmt(r.get(k)) for _, k in cols) + " |")
    print()

if __name__ == "__main__":
    out = {"sets": [], "corpus": []}
    for name, rels in SETS:
        out["sets"].append(measure(name, rels, callgraph=False))
    for name, rels in CORPUS:
        if not rels:                      # a private set whose path was not supplied
            print(f"skipping {name}: no files", file=sys.stderr); continue
        out["corpus"].append(measure(name, rels, callgraph=True))
    if "--json" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    print("## Equivalent implementations\n")
    table(out["sets"], [("set", "set"), ("commit", "commit"), ("files", "files"), ("physical", "physical"), ("code", "code"),
                        ("comment", "comment"), ("lex tokens", "lex_tokens"), ("ident tokens", "id_tokens"),
                        ("distinct idents", "distinct_ids"), ("o200k raw", "llm_o200k"), ("o200k stripped", "llm_o200k_stripped"),
                        ("cl100k raw", "llm_cl100k"), ("functions", "functions"), ("fn NLOC med", "fn_nloc_median"),
                        ("fn NLOC max", "fn_nloc_max"), ("CCN med", "ccn_median"), ("CCN max", "ccn_max"), ("nesting", "nesting")])
    print("## Whole projects\n")
    table(out["corpus"], [("project", "set"), ("commit", "commit"), ("files", "files"), ("code", "code"), ("comment", "comment"),
                          ("lex tokens", "lex_tokens"), ("o200k raw", "llm_o200k"), ("functions", "functions"),
                          ("fn NLOC med", "fn_nloc_median"), ("fn NLOC p90", "fn_nloc_p90"), ("fn NLOC max", "fn_nloc_max"),
                          ("CCN med", "ccn_median"), ("CCN p90", "ccn_p90"), ("CCN max", "ccn_max"), ("CCN>10", "ccn_gt10"),
                          ("nesting", "nesting"), ("fn macros", "fn_macros"), ("cg fns", "cg_functions"), ("cg edges", "cg_edges"),
                          ("fan-out med", "cg_fanout_median"), ("fan-out max", "cg_fanout_max"), ("longest chain", "cg_longest_chain"),
                          ("parse errs", "cg_parse_errors")])
