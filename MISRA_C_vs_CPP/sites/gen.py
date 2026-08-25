#!/usr/bin/env python3
"""gen.py: build the site-coverage conditions.

The reuse argument for abstraction says that one rule living in N places is N
chances to miss one. That is testable directly: give an agent a change that must
land at every one of N sites and count how many it lands.

Conditions are the same behaviour at four repetition counts plus one factored
control:
  rep1, rep3, rep10, rep30  N command handlers, each printing its own result line
  fac30                     30 commands, one shared print, so the same change is 1 site

Every condition passes the same hidden suite before the task and must pass it
after. The task text never names a command, so finding the sites is part of it.

  python3 gen.py <condition> <outdir>
"""
import os, sys

CMDS = ["add", "del", "find", "list", "stat", "dump", "keys", "tags", "init", "sync",
        "purge", "count", "first", "last", "next", "prev", "head", "tail", "grep", "sort",
        "merge", "split", "copy", "move", "link", "trim", "fill", "swap", "diff", "join"]

HANDLER = """
/* {name}: {doc} */
static int cmd_{name}(int argc, char **argv)
{{
    long n;

    if (argc < 1) {{
        fprintf(stderr, "{name}: needs an argument\\n");
        return 2;
    }}
    n = store_{name}(argv[0]);
    if (n < 0) {{
        fprintf(stderr, "{name}: failed\\n");
        return 1;
    }}
    printf("{name} ok=1 n=%ld\\n", n);
    return 0;
}}
"""

FAC_HANDLER = """
/* {name}: {doc} */
static int cmd_{name}(int argc, char **argv)
{{
    return run_one("{name}", store_{name}, argc, argv);
}}
"""

FAC_SHARED = """
/* One path for every command: parse, call, report. */
static int run_one(const char *name, long (*op)(const char *), int argc, char **argv)
{
    long n;

    if (argc < 1) {
        fprintf(stderr, "%s: needs an argument\\n", name);
        return 2;
    }
    n = op(argv[0]);
    if (n < 0) {
        fprintf(stderr, "%s: failed\\n", name);
        return 1;
    }
    printf("%s ok=1 n=%ld\\n", name, n);
    return 0;
}
"""

def build(cond):
    n = {"rep1": 1, "rep3": 3, "rep10": 10, "rep30": 30, "fac30": 30}[cond]
    factored = cond.startswith("fac")
    cmds = CMDS[:n]
    out = ['/* store.c -- a small record-store front end. C99, no dependencies. */',
           '#include <stdio.h>', '#include <stdlib.h>', '#include <string.h>', '']
    out.append("/* Each operation returns the number of records it touched, or -1. */")
    for i, c in enumerate(cmds):
        out.append(f'static long store_{c}(const char *arg)'
                   f' {{ return (long)(strlen(arg) + {i}); }}')
    out.append("")
    if factored:
        out.append(FAC_SHARED)
    for c in cmds:
        tpl = FAC_HANDLER if factored else HANDLER
        out.append(tpl.format(name=c, doc=f"{c} records matching the argument"))
    out.append("""
struct entry { const char *name; int (*fn)(int, char **); };

static const struct entry table[] = {
""" + "".join(f'    {{ "{c}", cmd_{c} }},\n' for c in cmds) + """    { NULL, NULL }
};

int main(int argc, char **argv)
{
    int i;

    if (argc < 2) {
        fprintf(stderr, "usage: store COMMAND ARG\\n");
        return 2;
    }
    for (i = 0; table[i].name; i++)
        if (strcmp(table[i].name, argv[1]) == 0)
            return table[i].fn(argc - 2, argv + 2);
    fprintf(stderr, "unknown command: %s\\n", argv[1]);
    return 2;
}
""")
    return "\n".join(out), cmds

README = """# store

A small record-store front end in C99.

Build:

    cc -O2 -std=c99 -o store store.c

Run:

    ./store COMMAND ARG

Each command prints one result line on success and returns 0.

Check:

    ./check.sh
"""

CHECK = """#!/bin/sh
# Builds and exercises a few commands. Not exhaustive.
set -e
cc -O2 -std=c99 -Wall -o store store.c
{lines}
echo "check.sh ok"
"""

if __name__ == "__main__":
    cond, outdir = sys.argv[1], sys.argv[2]
    src, cmds = build(cond)
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "store.c"), "w").write(src)
    open(os.path.join(outdir, "README.md"), "w").write(README)
    visible = cmds[:2]
    lines = "\n".join(f'./store {c} abc' for c in visible)
    p = os.path.join(outdir, "check.sh")
    open(p, "w").write(CHECK.format(lines=lines))
    os.chmod(p, 0o755)
    print(f"{cond}: {len(cmds)} commands -> {outdir}")
