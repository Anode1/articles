#!/usr/bin/env python3
"""hidden.py: grade a finished run site by site.

The point of the experiment is not pass or fail, it is coverage: of the N sites
the change had to land at, how many did. Every command is exercised, including
the ones no visible check mentions.
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import CMDS

ARG = "abcdefg"          # 7 characters, so arg=7 is the expected field
LINE = re.compile(r"^(\w+) ok=1 n=(\d+)(?: arg=(\d+))?\s*$")

def grade(workdir, n_cmds):
    """Returns (built, per-command dict, covered, total)."""
    b = subprocess.run("cc -O2 -std=c99 -o store_hidden store.c", shell=True, cwd=workdir,
                       capture_output=True, text=True)
    if b.returncode != 0:
        return False, {}, 0, n_cmds
    per = {}
    for c in CMDS[:n_cmds]:
        r = subprocess.run([os.path.join(workdir, "store_hidden"), c, ARG],
                           capture_output=True, text=True, cwd=workdir)
        m = LINE.match(r.stdout.strip())
        if not m or m.group(1) != c:
            per[c] = "malformed"
        elif m.group(3) is None:
            per[c] = "missed"                 # the site was not edited
        elif int(m.group(3)) != len(ARG):
            per[c] = "wrong"                  # edited, but the value is wrong
        else:
            per[c] = "ok"
    covered = sum(1 for v in per.values() if v == "ok")
    return True, per, covered, n_cmds

if __name__ == "__main__":
    ok, per, cov, tot = grade(sys.argv[1], int(sys.argv[2]))
    print(f"built={ok} covered={cov}/{tot}")
    for k, v in per.items():
        if v != "ok":
            print(f"  {k}: {v}")
