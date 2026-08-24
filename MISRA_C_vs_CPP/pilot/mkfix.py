#!/usr/bin/env python3
"""Fixtures for the pilot: visible (in every run directory) and hidden (never
shown to the agent). Seeded, so `python3 mkfix.py` reproduces them byte for byte.
Writes fixtures/visible/, fixtures/hidden/ and fixtures/expected.json."""
import json, os, random

here = os.path.dirname(os.path.abspath(__file__))
vis = os.path.join(here, "fixtures", "visible")
hid = os.path.join(here, "fixtures", "hidden")
os.makedirs(vis, exist_ok=True); os.makedirs(hid, exist_ok=True)

def write_ids(path, ids):
    with open(path, "w") as f:
        for i in ids: f.write(f"{i}\n")

WORDS = ["Inputs", "Outputs", "outputs", "OUTPUTS", "oUtPuTs", "Output", "puts", "record", "alpha", "beta", "gamma"]
# text words never contain the substring, so a line holds it at most once (the
# five originals agree only on that domain: Python's idiomatic path counts occurrences)
TEXT = ["record", "alpha", "beta", "gamma", "delta", "epsilon", "put", "input"]

def store(path, n, rng, last_no_newline):
    """lines of the form id|key|text; returns (exact count, case-insensitive count) for 'Outputs'."""
    exact = icase = 0
    lines = []
    for i in range(n):
        k = rng.choice(WORDS); t = rng.choice(TEXT)
        line = f"{i}|{k}|{t} {rng.randint(0, 99)}"
        lines.append(line)
        if "Outputs" in line: exact += 1
        if "outputs" in line.lower(): icase += 1
    text = "\n".join(lines) + ("" if last_no_newline else "\n")
    open(path, "w").write(text)
    return exact, icase

# visible: small, human-readable
a = [1, 3, 5, 7, 9, 11, 12, 13, 20]
b = [2, 3, 5, 6, 11, 13, 21]
write_ids(os.path.join(vis, "a.txt"), a); write_ids(os.path.join(vis, "b.txt"), b)
rng = random.Random(7)
vx, vi = store(os.path.join(vis, "store.txt"), 24, rng, last_no_newline=False)

# hidden
rng = random.Random(20260823)
hx, hi = store(os.path.join(hid, "store.txt"), 400, rng, last_no_newline=True)
pairs = {}
A = sorted(rng.sample(range(1, 5000), 400)); B = sorted(rng.sample(range(1, 5000), 350))
pairs["p1_random"] = (A, B)
C = sorted(rng.sample(range(1, 3000), 120)); pairs["p2_identical"] = (C, list(C))
pairs["p3_disjoint"] = ([2 * i for i in range(1, 200)], [2 * i + 1 for i in range(1, 150)])
pairs["p4_empty_second"] = (list(range(10, 20)), [])
pairs["p5_last_only"] = ([1, 4, 9, 16, 25, 36, 49], [2, 3, 5, 49])
exp = {"visible": {"find_exact": vx, "find_icase": vi,
                   "and": len(set(a) & set(b)), "only": len(set(a) - set(b))},
       "hidden": {"find_exact": hx, "find_icase": hi, "pairs": {}}}
for name, (X, Y) in pairs.items():
    write_ids(os.path.join(hid, name + "_a.txt"), X); write_ids(os.path.join(hid, name + "_b.txt"), Y)
    common = sorted(set(X) & set(Y))
    exp["hidden"]["pairs"][name] = {"common": len(common), "only": len(set(X) - set(Y)),
                                    "first": common[0] if common else "none", "last": common[-1] if common else "none"}
json.dump(exp, open(os.path.join(here, "fixtures", "expected.json"), "w"), indent=1)
print(json.dumps(exp, indent=1))
