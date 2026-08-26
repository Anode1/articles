"""hidden.py: grade one endpoint work dir at the HTTP boundary.
Builds the side, starts it on a free port, runs the task's checks with
urllib, compares parsed JSON and statuses exactly. selfcheck verifies the
harness: baselines must fail each task's new checks and hold regressions,
defects must apply and flip a check.
"""
import json, os, shutil, socket, subprocess, sys, tempfile, time
import urllib.request, urllib.error

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from tasks import CHECKS, DEFECTS, TASKS

def free_port():
    s = socket.socket(); s.bind(("", 0)); p = s.getsockname()[1]; s.close()
    return p

def req(port, path, token):
    r = urllib.request.Request(f"http://127.0.0.1:{port}{path}")
    if token: r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            return resp.status, json.loads(resp.read()), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read()), dict(e.headers)

def build_and_start(d, side, port):
    if side == "plain":
        b = subprocess.run(["javac", "-cp", os.path.join(here, "h2.jar"), "App.java"],
                           cwd=d, capture_output=True, text=True)
        if b.returncode != 0: return None, b.stderr[-500:]
        proc = subprocess.Popen(["java", "-cp", ".:" + os.path.join(here, "h2.jar"),
                                 "App", str(port)], cwd=d,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        b = subprocess.run(["./gradlew", "-q", "bootJar"], cwd=d,
                           capture_output=True, text=True, timeout=300)
        if b.returncode != 0: return None, (b.stderr or b.stdout)[-500:]
        proc = subprocess.Popen(["java", "-jar", "build/libs/endpoint.jar",
                                 "--server.port=" + str(port)], cwd=d,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        try:
            req(port, "/items", "t-alice"); return proc, None
        except Exception:
            if proc.poll() is not None: return None, "server died"
            time.sleep(0.5)
    proc.kill(); return None, "server never answered"

def grade(workdir, side, task):
    tmp = tempfile.mkdtemp(prefix="egrade-")
    try:
        shutil.copytree(workdir, os.path.join(tmp, "w"), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("build", ".git", ".gradle"))
        d = os.path.join(tmp, "w")
        port = free_port()
        proc, err = build_and_start(d, side, port)
        checks = CHECKS(task)
        if proc is None:
            return False, 0, len(checks), ["build/start: " + str(err)]
        passed, fails = 0, []
        try:
            for i, (path, token, st, body, hdrs) in enumerate(checks):
                s, b, h = req(port, path, token)
                hl = {k.lower(): v for k, v in h.items()}
                ok = s == st and b == body
                for k, v in hdrs.items():
                    ok = ok and hl.get(k.lower(), "").startswith(v)
                if ok: passed += 1
                else: fails.append(f"check {i}: {path} -> {s} {json.dumps(b)[:120]}")
        finally:
            proc.kill()
        return True, passed, len(checks), fails
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def apply_defects(d, side, task):
    for fname, old, new in DEFECTS.get((side, task), []):
        p = os.path.join(d, fname)
        s = open(p).read()
        if old not in s: raise SystemExit(f"defect does not apply: {side}/{task}")
        open(p, "w").write(s.replace(old, new, 1))

def selfcheck():
    bad = 0
    for side in ("plain", "spring"):
        for task in TASKS:
            d = tempfile.mkdtemp(prefix="eself-")
            shutil.copytree(os.path.join(here, side), d, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns("build", ".gradle"))
            apply_defects(d, side, task)
            built, passed, total, fails = grade(d, side, task)
            full = built and passed == total
            none = passed == 0
            if not built or full or (task != "t4" and none):
                bad += 1
                print(f"SELFCHECK {side}/{task}: built={built} {passed}/{total} {fails[:2]}")
            shutil.rmtree(d, ignore_errors=True)
    print("selfcheck problems:", bad)
    return bad

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selfcheck":
        raise SystemExit(1 if selfcheck() else 0)
    print(grade(sys.argv[1], sys.argv[2], sys.argv[3]))
