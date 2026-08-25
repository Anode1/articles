#!/usr/bin/env python3
"""dup.py: how much of a corpus is duplicated code.

The reuse argument for abstraction says explicit style repeats itself, and that
every repetition is a site an edit can miss. That is measurable before any agent
runs: tokenize, slide a window of K tokens, and count the tokens that sit inside
a window occurring more than once.

Two passes. Exact: tokens compared verbatim (type-1 clones). Normalised: every
identifier and literal replaced by a placeholder, so code differing only in names
still matches (type-2 clones), which is the form the reuse argument is about.

Usage:  venv/bin/python dup.py [--json out.json]
"""
import json, os, sys, hashlib
import measure as M
import external as E

K = 50            # window length in tokens; the usual clone-detector default range

def tokens_of(path):
    ext = M.lang_of(path)
    try:
        src = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return [], []
    if ext == "py":
        toks = M.lex_python(src)
    else:
        toks = M.lex_generic(src, ext)
    exact, norm = [], []
    for kind, text in toks:
        exact.append(text)
        norm.append("@" if kind in ("id", "num", "str") else text)
    return exact, norm

def duplicated_fraction(streams):
    """Fraction of tokens inside a K-window that occurs more than once anywhere."""
    seen, dup_windows = {}, set()
    for si, toks in enumerate(streams):
        for i in range(len(toks) - K + 1):
            h = hashlib.blake2b(" ".join(toks[i:i + K]).encode(), digest_size=16).digest()
            if h in seen:
                dup_windows.add((si, i)); dup_windows.add(seen[h])
            else:
                seen[h] = (si, i)
    covered = {}
    for si, i in dup_windows:
        covered.setdefault(si, set()).update(range(i, i + K))
    tot = sum(len(t) for t in streams)
    return (sum(len(v) for v in covered.values()) / tot) if tot else 0.0, tot

def run(name, paths):
    ex, no = [], []
    for p in paths:
        a, b = tokens_of(p)
        if a: ex.append(a); no.append(b)
    fe, tot = duplicated_fraction(ex)
    fn, _ = duplicated_fraction(no)
    return {"set": name, "tokens": tot, "dup_exact": round(100 * fe, 2), "dup_normalised": round(100 * fn, 2)}

if __name__ == "__main__":
    HOME = os.path.expanduser("~")
    out = []
    groups = [("C", E.C_REPOS, E.C_EXT), ("C++", E.CPP_REPOS, E.CPP_EXT), ("Rust", E.RUST_REPOS, E.RUST_EXT)]
    for lang, repos, exts in groups:
        for nm, repo, sd in repos:
            paths = [os.path.join(HOME, p) for p in E.files_of(repo, sd, exts)]
            r = run(nm, paths); r["lang"] = lang
            print(f"  {lang:5} {nm:10} {r['tokens']:9,} tokens  exact {r['dup_exact']:5.2f}%  normalised {r['dup_normalised']:5.2f}%", file=sys.stderr)
            out.append(r)
    if "--json" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    print("\n| language | tokens | exact dup % | normalised dup % |")
    print("|---|---|---|---|")
    for lang in ("C", "C++", "Rust"):
        g = [r for r in out if r["lang"] == lang]
        t = sum(r["tokens"] for r in g)
        e = sum(r["dup_exact"] * r["tokens"] for r in g) / t
        nn = sum(r["dup_normalised"] * r["tokens"] for r in g) / t
        print(f"| {lang} | {t:,} | {e:.2f} | {nn:.2f} |")
