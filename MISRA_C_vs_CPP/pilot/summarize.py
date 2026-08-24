#!/usr/bin/env python3
"""Summarise runs/results.json: per task x language, pass rate and medians of
context tokens, output tokens, turns, tool calls, wall time. Also per-language
totals and a LaTeX table body.  python3 summarize.py runs/results.json"""
import json, sys, os, glob, statistics as st
from collections import defaultdict

src = sys.argv[1]
rs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(src, "*", "*", "r*", "result.json")))] if os.path.isdir(src) else [r for r in json.load(open(src)) if r]
LANGS = ["c", "ada", "rust", "java", "python"]
TASKS = ["t1_diff", "t2_icase", "t3_bug", "t4_firstlast"]

def med(xs): return st.median(xs) if xs else float("nan")
def cell(g, k): return med([r[k] for r in g if r.get(k) is not None])

by = defaultdict(list)
for r in rs: by[(r["task"], r["lang"])].append(r)

print("task          lang     n pass  ctx_med   out_med turns tools  wall  reads bash")
for t in TASKS:
    for l in LANGS:
        g = by.get((t, l), [])
        if not g: continue
        print(f"{t:13s} {l:7s} {len(g):2d} {sum(r['hidden_pass'] for r in g):2d}/{len(g)}  "
              f"{cell(g,'context_tokens'):8.0f} {cell(g,'output_tokens'):8.0f} {cell(g,'num_turns'):5.0f} "
              f"{cell(g,'tool_calls'):5.0f} {cell(g,'wall_s'):5.0f}  {med([len(r['reads']) for r in g]):4.0f} {med([len(r['bash']) for r in g]):4.0f}")
print()
print("lang     n pass   ctx_med  out_med turns tools  wall   cost_sum")
for l in LANGS:
    g = [r for r in rs if r["lang"] == l]
    if not g: continue
    print(f"{l:7s} {len(g):2d} {sum(r['hidden_pass'] for r in g):2d}/{len(g)} {cell(g,'context_tokens'):9.0f} "
          f"{cell(g,'output_tokens'):8.0f} {cell(g,'num_turns'):5.0f} {cell(g,'tool_calls'):5.0f} {cell(g,'wall_s'):5.0f}   "
          f"{sum(r.get('cost_usd') or 0 for r in g):6.2f}")
print()
print("failures:")
for r in rs:
    if not r["hidden_pass"]:
        bad = [k for k, v in r["hidden_checks"].items() if not v]
        print(f"  {r['task']} {r['lang']} r{r['rep']}: build_ok={r['build_ok']} stop={r.get('stop')} failed={bad[:6]}")
print()
print("% LaTeX rows: task & language & pass & context (median) & output (median) & turns & tool calls")
for t in TASKS:
    for l in LANGS:
        g = by.get((t, l), [])
        if not g: continue
        print(f"{t.replace('_',' ')} & {l} & {sum(r['hidden_pass'] for r in g)}/{len(g)} & "
              f"{cell(g,'context_tokens'):,.0f} & {cell(g,'output_tokens'):,.0f} & {cell(g,'num_turns'):.0f} & {cell(g,'tool_calls'):.0f} \\\\")
