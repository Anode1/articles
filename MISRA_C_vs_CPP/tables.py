#!/usr/bin/env python3
"""tables.py: the paper's LaTeX table bodies from measurements.json (measure.py)
and pilot/runs/results.json (pilot/run.py). Printed to stdout; pasted into
article.tex unchanged.   venv/bin/python tables.py measurements.json [results.json]"""
import json, sys, statistics as st
from collections import defaultdict

M = json.load(open(sys.argv[1]))
S = {m["set"]: m for m in M["sets"]}
C = {m["set"]: m for m in M["corpus"]}

def n(v):
    if v is None: return "n/a"
    if isinstance(v, float): return f"{v:.0f}" if v == int(v) else f"{v:.1f}"
    return f"{v:,}"

print("% ---- equivalent sets: size")
for k in ["bench/C", "bench/Ada", "bench/Rust", "bench/Java", "bench/Python", "mincdp/C", "mincdp/Java", "linearr/C", "linearr/Java"]:
    m = S[k]
    print(f"{k} & {m['files']} & {n(m['physical'])} & {n(m['code'])} & {n(m['comment'])} & {n(m['lex_tokens'])} & "
          f"{n(m['id_tokens'])} & {n(m['distinct_ids'])} & {n(m['llm_o200k'])} & {n(m['llm_o200k_stripped'])} \\\\")
print("% ---- equivalent sets: structure")
for k in ["bench/C", "bench/Ada", "bench/Rust", "bench/Java", "bench/Python", "mincdp/C", "mincdp/Java", "linearr/C", "linearr/Java"]:
    m = S[k]
    print(f"{k} & {n(m.get('functions'))} & {n(m.get('fn_nloc_median'))} & {n(m.get('fn_nloc_max'))} & "
          f"{n(m.get('ccn_median'))} & {n(m.get('ccn_max'))} & {m['nesting']} \\\\")
print("% ---- ratios C / other, lexical and o200k")
for a, b in [("bench/C", "bench/Ada"), ("bench/C", "bench/Rust"), ("bench/C", "bench/Java"), ("bench/C", "bench/Python"),
             ("mincdp/C", "mincdp/Java"), ("linearr/C", "linearr/Java")]:
    print(f"% {a}/{b}: lex {S[a]['lex_tokens']/S[b]['lex_tokens']:.2f}  o200k {S[a]['llm_o200k']/S[b]['llm_o200k']:.2f}  code {S[a]['code']/S[b]['code']:.2f}")
print("% ---- key+post")
m = S["ais/key+post"]
print(f"% key+post: physical {m['physical']} code {m['code']} comment {m['comment']} lex {m['lex_tokens']} ids {m['id_tokens']} o200k {m['llm_o200k']} functions {m['functions']}")
print("% ---- corpus")
for k in ["ais/c", "cjitter/c", "bpnn/c", "linearr/c", "iac", "graphcrawl/c", "mincdp/c",
          "ljms/src", "aisgedcom/src", "aisconvert/src", "linearr/java", "mincdp/java", "systemA/java"]:
    m = C[k]
    print(f"{k} & {m['files']} & {n(m['code'])} & {n(m['lex_tokens'])} & {n(m['functions'])} & {n(m['fn_nloc_median'])} & {n(m['fn_nloc_p90'])} & "
          f"{n(m['fn_nloc_max'])} & {n(m['ccn_median'])} & {n(m['ccn_p90'])} & {n(m['ccn_max'])} & {n(m['ccn_gt10'])} & {m['nesting']} & "
          f"{n(m.get('fn_macros'))} & {n(m.get('cg_edges'))} & {n(m.get('cg_fanout_median'))} & {n(m.get('cg_fanout_max'))} & {n(m.get('cg_longest_chain'))} \\\\")

if len(sys.argv) > 2:
    rs = [r for r in json.load(open(sys.argv[2])) if r]
    LANGS = ["c", "ada", "rust", "java", "python"]; TASKS = ["t1_diff", "t2_icase", "t3_bug", "t4_firstlast"]
    NAME = {"t1_diff": "T1 add diff", "t2_icase": "T2 case-insensitive scan", "t3_bug": "T3 repair merge", "t4_firstlast": "T4 first/last id"}
    LN = {"c": "C", "ada": "Ada", "rust": "Rust", "java": "Java", "python": "Python"}
    by = defaultdict(list)
    for r in rs: by[(r["task"], r["lang"])].append(r)
    def med(g, k): return st.median([r[k] for r in g if r.get(k) is not None])
    def rng(g, k):
        xs = [r[k] for r in g if r.get(k) is not None]; return f"{min(xs):,}--{max(xs):,}"
    print("% ---- pilot per task x language: pass, context median (range), output median, turns median, tool calls median, wall median")
    for t in TASKS:
        for l in LANGS:
            g = by.get((t, l), [])
            if not g: continue
            print(f"{NAME[t] if l == 'c' else ''} & {LN[l]} & {sum(r['hidden_pass'] for r in g)}/{len(g)} & {med(g,'context_tokens'):,.0f} & "
                  f"{rng(g,'context_tokens')} & {med(g,'output_tokens'):,.0f} & {med(g,'num_turns'):.0f} & {med(g,'tool_calls'):.0f} & {med(g,'wall_s'):.0f} \\\\")
        print("\\addlinespace")
    print("% ---- pilot per language")
    for l in LANGS:
        g = [r for r in rs if r["lang"] == l]
        print(f"{LN[l]} & {sum(r['hidden_pass'] for r in g)}/{len(g)} & {med(g,'context_tokens'):,.0f} & {med(g,'output_tokens'):,.0f} & "
              f"{med(g,'num_turns'):.0f} & {med(g,'tool_calls'):.0f} & {med(g,'wall_s'):.0f} & {sum(r.get('cost_usd') or 0 for r in g):.2f} \\\\")
    print("% ---- per-task rank of languages by median context (1 = least)")
    for t in TASKS:
        order = sorted(LANGS, key=lambda l: med(by[(t, l)], 'context_tokens'))
        print(f"% {t}: " + " < ".join(f"{LN[l]} {med(by[(t,l)],'context_tokens'):,.0f}" for l in order))
    print("% ---- failures")
    for r in rs:
        if not r["hidden_pass"]:
            print(f"% {r['task']} {r['lang']} r{r['rep']} build_ok={r['build_ok']} stop={r.get('stop')} failed={[k for k,v in r['hidden_checks'].items() if not v][:5]}")
