#!/usr/bin/env python3
"""Hidden tests. evaluate(task, lang, dir) builds the program in dir with the
README's command and runs it on fixtures/hidden/, which the agent never sees.
Every row's count must be right (Python prints two rows per operation, both
must agree). Returns {"build_ok", "checks": {name: bool}, "pass", "log"}."""
import json, os, re, subprocess, sys
from langs import LANGS

here = os.path.dirname(os.path.abspath(__file__))
HID = os.path.join(here, "fixtures", "hidden")
EXP = json.load(open(os.path.join(here, "fixtures", "expected.json")))["hidden"]

def sh(cmd, cwd, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"

def nums(out, key):
    return [int(x) for x in re.findall(re.escape(key) + r"=\s*(\d+)", out)]

def all_equal(out, key, expected, prefix=None):
    rows = [l for l in out.splitlines() if key + "=" in l and (prefix is None or l.startswith(prefix))]
    vals = [int(x) for l in rows for x in re.findall(re.escape(key) + r"=\s*(\d+)", l)]
    return len(vals) >= 1 and all(v == expected for v in vals)

def evaluate(task, lang, d):
    L = LANGS[lang]; log = []; checks = {}
    if L["clean"]: sh(L["clean"], d)
    if L["build"]:
        rc, out = sh(L["build"], d); log.append(out)
        if rc != 0:
            return {"build_ok": False, "checks": {}, "pass": False, "log": "\n".join(log)}
    run = L["run"]
    icase = task == "t2_icase"
    # scan: exact semantics unless the task changed them
    rc, out = sh(f"{run} find {HID}/store.txt Outputs", d); log.append(out)
    checks["find_Outputs"] = rc == 0 and all_equal(out, "hits", EXP["find_icase"] if icase else EXP["find_exact"])
    if icase:
        rc, out = sh(f"{run} find {HID}/store.txt ouTPuts", d); log.append(out)
        checks["find_mixed_case"] = rc == 0 and all_equal(out, "hits", EXP["find_icase"])
    # intersection on every pair, and the task-specific outputs
    for name, e in EXP["pairs"].items():
        A = f"{HID}/{name}_a.txt"; B = f"{HID}/{name}_b.txt"
        rc, out = sh(f"{run} and {A} {B}", d); log.append(out)
        checks[f"and_{name}"] = rc == 0 and all_equal(out, "common", e["common"])
        if task == "t4_firstlast":
            last = out.strip().splitlines()[-1] if out.strip() else ""
            m = re.search(r"first=(\S+)\s+last=(\S+)", last)
            checks[f"firstlast_{name}"] = bool(m) and m.group(1) == str(e["first"]) and m.group(2) == str(e["last"])
        if task == "t1_diff":
            rc, out = sh(f"{run} diff {A} {B}", d); log.append(out)
            checks[f"diff_{name}"] = rc == 0 and all_equal(out, "only", e["only"], prefix="diff")
    return {"build_ok": True, "checks": checks, "pass": all(checks.values()), "log": "\n".join(log)}

if __name__ == "__main__":
    r = evaluate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps({k: v for k, v in r.items() if k != "log"}, indent=1))
