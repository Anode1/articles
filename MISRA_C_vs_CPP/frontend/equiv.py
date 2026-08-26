"""equiv.py: verify the two twins are equivalent at the rendered-DOM
boundary before any run. Both templates are built and served, every base
scenario is replayed on each, and the projections (count, selection, rows,
carets, empty state) must be equal field for field. Run before the
experiment; any mismatch fails loudly.

  python3 equiv.py
"""
import shutil, sys, tempfile, time

import cdp
import hidden
from tasks import BASE


def project(side):
    d = tempfile.mkdtemp(prefix="equiv-")
    shutil.rmtree(d)
    hidden.make_workdir(side, "t1", d)          # t1 injects no defect
    served, err = hidden.build(d, side)
    if err:
        raise SystemExit(f"{side} build: {err}")
    srv = cdp.Server(served)
    page = cdp.Page()
    out = []
    try:
        for ops in BASE:
            page.goto(srv.url())
            for _ in range(50):
                if page.eval('document.querySelectorAll(".item-row").length > 0'):
                    break
                time.sleep(0.1)
            page.eval(hidden.HELPER)
            for kind, arg in ops:
                page.eval(hidden.OPS_JS[kind].format(arg=arg))
                time.sleep(0.05)
            time.sleep(0.1)
            out.append(page.eval("__h.read()"))
    finally:
        page.close()
        srv.close()
        shutil.rmtree(d, ignore_errors=True)
    return out


if __name__ == "__main__":
    a, b = project("plain"), project("react")
    bad = 0
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            bad += 1
            keys = [k for k in x if x.get(k) != y.get(k)]
            print(f"MISMATCH scenario {i} {BASE[i]}: {keys}")
            for k in keys[:2]:
                print(f"  plain {x.get(k)!r}\n  react {y.get(k)!r}")
    print(f"{len(BASE)} scenarios, {bad} mismatches")
    sys.exit(1 if bad else 0)
