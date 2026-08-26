"""hidden.py: grade one work directory against the task's hidden scenarios.

Never shown to the agent. Sources are copied to a fresh temp dir (the React
side is built there with vite, node_modules symlinked from the template),
served statically, and driven through headless Chrome by cdp.py. A scenario
passes when the rendered projection equals the model's, field by field.

  grade(workdir, side, task) -> (built, passed, total, failures)
  python3 hidden.py selfcheck
"""
import os, shutil, subprocess, sys, tempfile, time

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import cdp
from tasks import DEFECTS, SCENARIOS, TASKS, model

NODE_BIN = os.path.expanduser("~/.local/bin")

HELPER = r"""
window.__h = {
  set(sel, v) {
    const el = document.querySelector(sel);
    const proto = el instanceof HTMLSelectElement
      ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, "value").set.call(el, v);
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  },
  click(sel) { document.querySelector(sel).click(); },
  read() {
    const t = (sel) => {
      const el = document.querySelector(sel);
      return el ? el.textContent : null;
    };
    return {
      count: t("#count"), selected: t("#selected"),
      empty: t("#rows .empty"),
      count_empty_class:
        !!document.querySelector("#count")?.classList.contains("is-empty"),
      caret_id: t('[data-sort="id"]'), caret_name: t('[data-sort="name"]'),
      rows: [...document.querySelectorAll(".item-row")].map((r) => ({
        id: r.dataset.id,
        author: r.querySelector(".item-author")?.textContent,
        name: r.querySelector(".item-name")?.textContent,
        badge: r.querySelector(".badge")?.className,
        checked: !!r.querySelector(".select")?.checked,
        len: r.querySelector(".item-len")?.textContent ?? null,
      })),
    };
  },
};
"""

OPS_JS = {
    "text": '__h.set("#filter", {arg!r})',
    "minlen": '__h.set("#minLen", {arg!r})',
    "state": '__h.set("#stateFilter", {arg!r})',
    "sort": '__h.click(\'[data-sort="{arg}"]\')',
    "toggle": '__h.click(\'.item-row[data-id="{arg}"] .select\')',
    "delete": '__h.click(\'.item-row[data-id="{arg}"] .delete\')',
}


def build(workdir, side):
    """Copy sources to a temp dir ready to serve; return (dir, err)."""
    tmp = tempfile.mkdtemp(prefix="grade-")
    if side == "plain":
        for f in os.listdir(workdir):
            if f.endswith((".js", ".css", ".html", ".json")):
                shutil.copy(os.path.join(workdir, f), tmp)
        return tmp, None
    for f in ("index.html", "package.json", "vite.config.js"):
        if os.path.exists(os.path.join(workdir, f)):
            shutil.copy(os.path.join(workdir, f), tmp)
    for d in ("src", "public"):
        if os.path.isdir(os.path.join(workdir, d)):
            shutil.copytree(os.path.join(workdir, d), os.path.join(tmp, d))
    os.symlink(os.path.join(here, "react", "node_modules"),
               os.path.join(tmp, "node_modules"))
    p = subprocess.run([os.path.join(NODE_BIN, "npx"), "vite", "build"],
                       cwd=tmp, capture_output=True, text=True, timeout=180,
                       env={**os.environ,
                            "PATH": NODE_BIN + os.pathsep + os.environ["PATH"]})
    if p.returncode != 0:
        return None, (p.stderr or p.stdout)[-500:]
    return os.path.join(tmp, "dist"), None


def compare(got, exp):
    for k, want in exp.items():
        if k == "rows":
            continue
        if k in ("empty", "count_empty_class") and want is None:
            continue
        if got.get(k) != want:
            return f"{k}: {got.get(k)!r} != {want!r}"
    grows = got.get("rows", [])
    if len(grows) != len(exp["rows"]):
        return f"rows: {len(grows)} != {len(exp['rows'])}"
    for g, w in zip(grows, exp["rows"]):
        for k, want in w.items():
            if g.get(k) != want:
                return f"row {w['id']} {k}: {g.get(k)!r} != {want!r}"
    return None


def grade(workdir, side, task):
    scenarios = SCENARIOS[task]
    served, err = build(workdir, side)
    if err:
        return False, 0, len(scenarios), ["build: " + err]
    page = None
    try:
        srv = cdp.Server(served)
        page = cdp.Page()
        passed, failures = 0, []
        for i, ops in enumerate(scenarios):
            # A missing element (the control a task asks for) fails the
            # scenario, not the grade.
            try:
                page.goto(srv.url())
                for _ in range(50):                  # data fetch is async
                    if page.eval('document.querySelectorAll(".item-row")'
                                 '.length > 0'):
                        break
                    time.sleep(0.1)
                page.eval(HELPER)
                for kind, arg in ops:
                    page.eval(OPS_JS[kind].format(arg=arg))
                    time.sleep(0.05)
                time.sleep(0.1)
                got = page.eval("__h.read()")
                diff = compare(got, model(ops, task))
            except Exception as e:
                diff = "script: " + str(e)[:200]
            if diff is None:
                passed += 1
            else:
                failures.append(f"scenario {i} {ops}: {diff}")
        return True, passed, len(scenarios), failures
    except Exception as e:
        return False, 0, len(scenarios), ["harness: " + str(e)[:300]]
    finally:
        if page:
            page.close()
        try:
            srv.close()
        except Exception:
            pass
        shutil.rmtree(os.path.dirname(served) if side == "react" else served,
                      ignore_errors=True)


def apply_defects(d, side, task):
    for fname, old, new in DEFECTS.get((side, task), []):
        p = os.path.join(d, fname)
        s = open(p).read()
        if old not in s:
            raise SystemExit(f"defect does not apply: {side}/{task} {fname}")
        open(p, "w").write(s.replace(old, new, 1))


def make_workdir(side, task, d):
    src = os.path.join(here, side)
    ignore = shutil.ignore_patterns("node_modules", "dist", "runs")
    shutil.copytree(src, d, ignore=ignore)
    if side == "react":
        os.symlink(os.path.join(here, "react", "node_modules"),
                   os.path.join(d, "node_modules"))
    apply_defects(d, side, task)


def selfcheck():
    bad = 0
    for side in ("plain", "react"):
        for task in ("t1", "t2", "t3", "t4"):
            d = tempfile.mkdtemp(prefix="self-")
            shutil.rmtree(d)
            make_workdir(side, task, d)
            built, passed, total, fails = grade(d, side, task)
            # Baseline (t4: defective) must build, must fail the checks that
            # demand new behavior, and must not fail everything.
            full = built and passed == total
            none = passed == 0
            if not built or full or none:
                bad += 1
                print(f"SELFCHECK {side}/{task}: built={built} "
                      f"passed={passed}/{total} {fails[:2]}")
            else:
                print(f"ok {side}/{task}: baseline {passed}/{total}")
            shutil.rmtree(d, ignore_errors=True)
    print("selfcheck problems:", bad)
    return bad


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selfcheck":
        raise SystemExit(1 if selfcheck() else 0)
    print(grade(sys.argv[1], sys.argv[2], sys.argv[3]))
