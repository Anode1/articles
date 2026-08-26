#!/usr/bin/env python3
"""hidden.py: grade one work directory against the task's hidden checks.

The suite never enters the work directory the agent saw: sources are copied
to a fresh temp dir, built with make, and each check runs with its own
data.txt. A check passes when stdout, exit code, and (where the check pins
them) stderr and out.txt all match exactly.

  grade(workdir, pair, task) -> (built, passed, total, failures)

Self-check mode verifies the harness itself: every (pair, lang, task) at
baseline must FAIL the task checks that demand new behavior and PASS its
regressions, the reference solution is not built here (the agent's job), and
every defect must apply cleanly and flip at least one check.

  python3 hidden.py selfcheck
"""
import os, shutil, subprocess, sys, tempfile

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from tasks import CHECKS, DEFECTS

SRC_EXT = (".c", ".cpp", ".h", "Makefile")


def grade(workdir, pair, task):
    tmp = tempfile.mkdtemp(prefix="grade-")
    try:
        for f in os.listdir(workdir):
            if f.endswith((".c", ".cpp", ".h")) or f == "Makefile":
                shutil.copy(os.path.join(workdir, f), tmp)
        b = subprocess.run(["make", "-s"], cwd=tmp, capture_output=True, text=True)
        if b.returncode != 0 or not os.path.exists(os.path.join(tmp, "store")):
            return False, 0, len(CHECKS[(pair, task)]), ["build: " + b.stderr[-500:]]
        passed, failures = 0, []
        for i, c in enumerate(CHECKS[(pair, task)]):
            dp = os.path.join(tmp, "data.txt")
            op = os.path.join(tmp, "out.txt")
            if os.path.exists(dp):
                os.remove(dp)
            if os.path.exists(op):
                os.remove(op)
            if c["data"] is not None:
                open(dp, "w").write(c["data"])
            if c["precreate_outfile"] is not None:
                open(op, "w").write(c["precreate_outfile"])
            p = subprocess.run(["./store"] + c["argv"], cwd=tmp,
                               input=c["stdin"].encode() if c["stdin"] else None,
                               capture_output=True, timeout=10)
            ok = p.stdout == c["out"].encode() and p.returncode == c["rc"]
            if ok and c["err"] is not None:
                ok = p.stderr == c["err"].encode()
            if ok and c["outfile"] is not None:
                ok = os.path.exists(op) and open(op).read() == c["outfile"]
            if ok and c["outfile_absent"]:
                ok = not os.path.exists(op)
            if ok:
                passed += 1
            else:
                failures.append(f"check {i}: argv={c['argv']} "
                                f"out={p.stdout[:200]!r} rc={p.returncode}")
        return True, passed, len(CHECKS[(pair, task)]), failures
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def apply_defects(d, pair, lang):
    for fname, old, new in DEFECTS[(pair, lang)]:
        p = os.path.join(d, fname)
        s = open(p).read()
        if old not in s:
            raise SystemExit(f"defect does not apply: {pair}/{lang} {fname}")
        open(p, "w").write(s.replace(old, new, 1))


def selfcheck():
    from gen import build, PAIRS
    bad = 0
    for pair in PAIRS:
        for lang in ("c", "cpp"):
            base = tempfile.mkdtemp(prefix="self-")
            for name, content in build(pair, lang).items():
                open(os.path.join(base, name), "w").write(content)
            for task in ("t1", "t2", "t3", "t4"):
                d = tempfile.mkdtemp(prefix="self-")
                for f in os.listdir(base):
                    shutil.copy(os.path.join(base, f), d)
                if task == "t4":
                    apply_defects(d, pair, lang)
                built, passed, total, fails = grade(d, pair, task)
                # Baseline (t4: defective baseline) must build, must fail the
                # suite (the task is real work), and must not fail everything
                # (the regressions hold).
                full = built and passed == total
                none = passed == 0
                if not built or full or (task != "t4" and none):
                    bad += 1
                    print(f"SELFCHECK {pair}/{lang}/{task}: built={built} "
                          f"passed={passed}/{total} {fails[:2]}")
                shutil.rmtree(d, ignore_errors=True)
            shutil.rmtree(base, ignore_errors=True)
    print("selfcheck problems:", bad)
    return bad


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selfcheck":
        raise SystemExit(1 if selfcheck() else 0)
    built, passed, total, fails = grade(sys.argv[1], sys.argv[2], sys.argv[3])
    print(built, passed, total, fails)
