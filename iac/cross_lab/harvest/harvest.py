#!/usr/bin/env python3
"""Recompute the residual set from the public SWE-bench Verified record.

Sparse-clones github.com/swe-bench/experiments (results.json per submission),
takes the best-scoring submission built on each lab's model, and keeps the
instances all of them failed. Output matches residual.json when run against
the record as of 2026-08-31; a later record can only shrink the set.

Usage: python3 harvest.py [workdir]
"""
import json, glob, os, subprocess, sys

work = sys.argv[1] if len(sys.argv) > 1 else "/tmp/swexp"
if not os.path.isdir(work):
    subprocess.run(["git", "clone", "--filter=blob:none", "--sparse",
                    "--depth", "1",
                    "https://github.com/swe-bench/experiments.git", work],
                   check=True)
    subprocess.run(["git", "-C", work, "sparse-checkout", "set", "--no-cone",
                    "evaluation/verified/*/results/results.json"], check=True)

subs = {}
for p in glob.glob(os.path.join(work, "evaluation/verified/*/results/results.json")):
    name = p.split(os.sep)[-3]
    subs[name] = set(json.load(open(p)).get("resolved") or [])

ranked = sorted(subs.items(), key=lambda kv: -len(kv[1]))

def best(*pats):
    for n, r in ranked:
        if any(p in n.lower() for p in pats):
            return n, r

lab = {"anthropic": best("claude"),
       "openai":    best("gpt5", "gpt-5", "openai", "codex"),
       "google":    best("gemini")}

universe = set().union(*subs.values())
residual = sorted(universe - set.union(*(r for _, r in lab.values())))

print(f"submissions: {len(subs)}   universe: {len(universe)}   residual: {len(residual)}")
for k, (n, r) in lab.items():
    print(f"  {k:10s} {n}  {len(r)}/500")
json.dump({"per_lab_best": {k: n for k, (n, _) in lab.items()},
           "residual": residual},
          open(os.path.join(os.path.dirname(__file__) or ".", "residual.json"), "w"),
          indent=1)
