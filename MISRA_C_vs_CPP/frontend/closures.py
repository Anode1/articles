"""closures.py: the frontend pair, counted the way the paper counts.

Category 1 is the twin application on each side; category 2 is the framework
text that decides its behavior before it runs. The browser engine is floor on
both sides, by the rule that puts MySQL below the line and Hibernate above
it: React varies by version and the application configures it, so it is
counted.

  REACT_SRC=~/corpora/react-v19 python3 closures.py

React source: facebook/react tag v19.1.0, commit 4a9df08157f001c01b078d259748512211233dcf.
The category-2 list is one rater's derivation and has not been blind-checked.
"""
import os, sys, json
import tiktoken

here = os.path.dirname(os.path.abspath(__file__))
REACT = os.path.expanduser(os.environ.get("REACT_SRC", "~/corpora/react-v19"))
enc = tiktoken.get_encoding("o200k_base")

CAT1 = {
    "plain": ["plain/index.html", "plain/app.js"],
    "react": ["react/index.html", "react/src/main.jsx", "react/src/App.jsx",
              "react/src/ItemsTable.jsx", "react/src/ItemRow.jsx"],
    "react1": ["react1/index.html", "react1/src/main.jsx"],
}

# Build configuration decides the JSX transform and the pinned version, not
# the screen's behavior, so it is counted apart rather than folded in.
CONFIG = {"react": ["react/package.json", "react/vite.config.js"]}

# The modules that decide the screen: root creation, the render loop,
# reconciliation identity (keys), the hooks the components use, the commit
# that writes the DOM, prop and attribute application, controlled inputs, and
# the delegated event system that turns a click into a handler.
CAT2_REACT = [
    "packages/react/src/ReactHooks.js",
    "packages/react/src/jsx/ReactJSXElement.js",
    "packages/react-dom/src/client/ReactDOMRoot.js",
    "packages/react-reconciler/src/ReactFiberReconciler.js",
    "packages/react-reconciler/src/ReactFiberWorkLoop.js",
    "packages/react-reconciler/src/ReactFiberBeginWork.js",
    "packages/react-reconciler/src/ReactFiberCompleteWork.js",
    "packages/react-reconciler/src/ReactFiberCommitWork.js",
    "packages/react-reconciler/src/ReactFiberCommitHostEffects.js",
    "packages/react-reconciler/src/ReactFiberCommitEffects.js",
    "packages/react-reconciler/src/ReactChildFiber.js",
    "packages/react-reconciler/src/ReactFiberHooks.js",
    "packages/react-reconciler/src/ReactFiberLane.js",
    "packages/react-reconciler/src/ReactFiberConcurrentUpdates.js",
    "packages/react-reconciler/src/ReactEventPriorities.js",
    "packages/react-reconciler/src/ReactFiber.js",
    "packages/react-dom-bindings/src/client/ReactDOMComponent.js",
    "packages/react-dom-bindings/src/client/ReactDOMComponentTree.js",
    "packages/react-dom-bindings/src/client/DOMPropertyOperations.js",
    "packages/react-dom-bindings/src/client/ReactDOMInput.js",
    "packages/react-dom-bindings/src/client/inputValueTracking.js",
    "packages/react-dom-bindings/src/events/DOMPluginEventSystem.js",
    "packages/react-dom-bindings/src/events/ReactDOMEventListener.js",
    "packages/react-dom-bindings/src/events/getListener.js",
    "packages/react-dom-bindings/src/events/EventRegistry.js",
    "packages/react-dom-bindings/src/events/plugins/SimpleEventPlugin.js",
    "packages/react-dom-bindings/src/events/plugins/ChangeEventPlugin.js",
    "packages/react-dom-bindings/src/events/SyntheticEvent.js",
    "packages/scheduler/src/forks/Scheduler.js",
]

# Whole-runtime upper bound, the bound taskwarrior is reported at.
RUNTIME_TREES = ["packages/react/src", "packages/react-dom/src",
                 "packages/react-dom-bindings/src", "packages/react-reconciler/src",
                 "packages/scheduler/src", "packages/shared"]
SKIP_DIRS = ("__tests__", "__mocks__", "npm", "node_modules")


def count(paths, root):
    rows, L, T = [], 0, 0
    for p in paths:
        full = os.path.join(root, p)
        if not os.path.exists(full):
            print("MISSING", p, file=sys.stderr)
            continue
        s = open(full, encoding="utf-8", errors="ignore").read()
        l, t = len(s.splitlines()), len(enc.encode(s))
        rows.append({"file": p, "lines": l, "tokens": t})
        L += l
        T += t
    return {"files": len(rows), "lines": L, "tokens": T, "rows": rows}


def walk(trees, root):
    L = T = F = 0
    for tree in trees:
        for d, dirs, files in os.walk(os.path.join(root, tree)):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in files:
                if not f.endswith((".js", ".jsx")):
                    continue
                s = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
                F += 1
                L += len(s.splitlines())
                T += len(enc.encode(s))
    return {"files": F, "lines": L, "tokens": T}


if __name__ == "__main__":
    out = {"cat1": {k: count(v, here) for k, v in CAT1.items()},
           "config": {k: count(v, here) for k, v in CONFIG.items()},
           "cat2": {"plain": {"files": 0, "lines": 0, "tokens": 0, "rows": []},
                    "react": count(CAT2_REACT, REACT)},
           "runtime_whole_files": walk(RUNTIME_TREES, REACT)}
    json.dump(out, open(os.path.join(here, "closures.json"), "w"), indent=1)
    p, r = out["cat1"]["plain"], out["cat1"]["react"]
    print(f"{'side':10} {'files':>5} {'lines':>6} {'cat1':>8} {'cat2':>10}")
    print(f"{'plain':10} {p['files']:>5} {p['lines']:>6} {p['tokens']:>8,} {0:>10,}")
    print(f"{'react':10} {r['files']:>5} {r['lines']:>6} {r['tokens']:>8,} "
          f"{out['cat2']['react']['tokens']:>10,}")
    print(f"cat1 ratio react/plain: {r['tokens'] / p['tokens']:.2f}")
    print(f"react runtime, whole files: {out['runtime_whole_files']['tokens']:,}")
