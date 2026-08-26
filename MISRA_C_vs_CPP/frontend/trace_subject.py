"""trace_subject.py: the real-subject closure of the paper's web section.

Mechanical import trace of one screen of a third-party React application
(yurisldk/realworld-react-fsd at 969709a), from the router entry of the
profile screen, the article-list-by-author page. Alias resolution follows
the project's tsconfig paths; a bare package specifier is not repository
text and is recorded, the generated ~shared/api/generated/* among them.
Sibling page modules pulled in only by the router table are excluded from
the screen-path count and included in the full-trace count.

  SUBJECT=~/corpora/rw-react-fsd python3 trace_subject.py
"""
import os, re, sys

import tiktoken

ROOT = os.path.expanduser(os.environ.get("SUBJECT", "~/corpora/rw-react-fsd"))
ENTRIES = ["src/app/index.tsx", "src/app/browser-router.tsx",
           "src/pages/profile/profile.route.ts",
           "src/pages/profile/profile.ui.tsx",
           "src/pages/profile/profile.loader.ts",
           "src/pages/profile/profile.state.ts",
           "src/pages/profile/actions/article-favorite-toggle.action.ts"]
SIBLINGS = ("src/pages/article/", "src/pages/editor/", "src/pages/home/",
            "src/pages/login/", "src/pages/page-404/", "src/pages/register/",
            "src/pages/settings/")
ALIAS = {"~app": "src/app", "~pages": "src/pages", "~widgets": "src/widgets",
         "~features": "src/features", "~entities": "src/entities",
         "~shared": "src/shared"}
EXT = [".ts", ".tsx", ".js", ".jsx"]
IMP = re.compile(r"""(?:^|\n)\s*(?:import|export)[^'"\n]*?from\s*['"]([^'"]+)['"]""")
SIDE = re.compile(r"""(?:^|\n)\s*import\s*['"]([^'"]+)['"]""")


def resolve(spec, frm):
    if spec.startswith("."):
        base = os.path.normpath(os.path.join(os.path.dirname(frm), spec))
    else:
        for a, p in ALIAS.items():
            if spec == a or spec.startswith(a + "/"):
                base = os.path.join(ROOT, p, spec[len(a) + 1:])
                break
        else:
            return None
    for e in EXT:
        if os.path.isfile(base + e):
            return base + e
    if os.path.isfile(base):
        return base
    for e in EXT:
        p = os.path.join(base, "index" + e)
        if os.path.isfile(p):
            return p
    return None


def trace():
    seen, bare = set(), {}
    stack = [os.path.join(ROOT, e) for e in ENTRIES]
    while stack:
        f = stack.pop()
        if not f or f in seen or not os.path.isfile(f):
            continue
        seen.add(f)
        src = open(f, encoding="utf-8", errors="ignore").read()
        for m in IMP.findall(src) + SIDE.findall(src):
            r = resolve(m, f)
            if r:
                stack.append(r)
            elif not m.startswith("."):
                bare[m] = bare.get(m, 0) + 1
    return sorted(os.path.relpath(x, ROOT) for x in seen), bare


if __name__ == "__main__":
    enc = tiktoken.get_encoding("o200k_base")

    def count(files):
        L = T = 0
        for f in files:
            s = open(os.path.join(ROOT, f), encoding="utf-8",
                     errors="ignore").read()
            L += len(s.splitlines())
            T += len(enc.encode(s))
        return len(files), L, T

    files, bare = trace()
    print("full trace       %d files, %d lines, %d tokens" % count(files))
    path = [f for f in files if not f.startswith(SIBLINGS)]
    print("screen path only %d files, %d lines, %d tokens" % count(path))
    gen = sorted(k for k in bare if k.startswith("~shared/api/generated"))
    print(f"unresolved generated imports: {len(gen)}")
    for g in gen:
        print("  ", g)
