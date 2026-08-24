#!/usr/bin/env python3
"""Per-call context from the traces: what the model was shown on its first call
(the harness constant: system prompt, tool schemas, the task) and how the
per-call context grows. Also the share of the run's context that the source
file itself could account for.   python3 overhead.py runs"""
import glob, json, os, statistics as st, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from langs import LANGS

runs = sys.argv[1]
try:
    import tiktoken; enc = tiktoken.get_encoding("o200k_base")
except ImportError:
    enc = None
first, last, growth, share = [], [], [], []
per_lang = {}
for f in sorted(glob.glob(os.path.join(runs, "*", "*", "r*", "trace.jsonl"))):
    lang = f.split(os.sep)[-3]
    calls = []
    for line in open(f):
        try: ev = json.loads(line)
        except ValueError: continue
        if ev.get("type") == "assistant":
            u = ev["message"].get("usage") or {}
            ctx = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
            if ctx: calls.append(ctx)
    if not calls: continue
    # consecutive assistant events within one API call repeat the same usage; keep distinct values in order
    dedup = [c for i, c in enumerate(calls) if i == 0 or c != calls[i - 1]]
    first.append(dedup[0]); last.append(dedup[-1]); growth.append((dedup[-1] - dedup[0]) / max(1, len(dedup) - 1))
    src = os.path.join(os.path.dirname(f), "work", LANGS[lang]["src"])
    if enc and os.path.exists(src):
        stoks = len(enc.encode(open(src, errors="replace").read()))
        total = sum(dedup)
        share.append(stoks * len(dedup) / total)     # upper bound: the file shown on every call
        per_lang.setdefault(lang, []).append(stoks * len(dedup) / total)
print(f"runs {len(first)}")
print(f"first call context: median {st.median(first):,.0f}  min {min(first):,}  max {max(first):,}")
print(f"last call context:  median {st.median(last):,.0f}  min {min(last):,}  max {max(last):,}")
print(f"growth per call:    median {st.median(growth):,.0f} tokens")
if share:
    print(f"source file share of run context (upper bound): median {100*st.median(share):.1f}%  max {100*max(share):.1f}%")
    for l, xs in per_lang.items(): print(f"  {l:7s} median {100*st.median(xs):.1f}%")
