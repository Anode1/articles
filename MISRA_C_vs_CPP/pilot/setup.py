#!/usr/bin/env python3
"""Build templates/<lang>/ from ~/ais/tests/perf: the one source file, a neutral
README, check.sh and the visible fixtures. Also verifies that every original
passes the hidden tests that do not depend on a task (baseline), and that the
T3 bug injects cleanly and makes the intersection wrong."""
import os, shutil, subprocess, sys, json
from langs import LANGS, README, CHECK, PERF

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import hidden

for lang, L in LANGS.items():
    d = os.path.join(here, "templates", lang)
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    shutil.copy(os.path.join(PERF, L["src"]), d)
    open(os.path.join(d, "README.md"), "w").write(README.format(run=L["run"], build=L["build"] or "(none: it is a script)"))
    open(os.path.join(d, "check.sh"), "w").write(CHECK.format(build=L["build"], run=L["run"]))
    shutil.copytree(os.path.join(here, "fixtures", "visible"), os.path.join(d, "fixtures"))
    src = open(os.path.join(d, L["src"])).read()
    assert src.count(L["bug"][0]) == 1, (lang, "bug anchor not found exactly once")

# baseline: originals must pass every non-task check; the bugged copy must fail the intersection
for lang, L in LANGS.items():
    d = os.path.join(here, "scratch_base", lang)
    shutil.rmtree(d, ignore_errors=True); shutil.copytree(os.path.join(here, "templates", lang), d)
    r = hidden.evaluate("baseline", lang, d)
    print(lang, "baseline", "PASS" if r["pass"] else "FAIL", {k: v for k, v in r["checks"].items() if not v})
    bd = os.path.join(here, "scratch_bug", lang)
    shutil.rmtree(bd, ignore_errors=True); shutil.copytree(d, bd)
    p = os.path.join(bd, L["src"]); s = open(p).read().replace(*L["bug"]); open(p, "w").write(s)
    r = hidden.evaluate("t3_bug", lang, bd)
    print(lang, "bugged", "fails intersection as intended" if not r["pass"] else "STILL PASSES: bug ineffective")
