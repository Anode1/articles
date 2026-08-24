"""Per-language facts shared by setup.py, run.py and hidden.py: source file,
build and run commands, and the exact text substitution that injects the T3 bug."""
import os
PERF = os.path.expanduser("~/ais/tests/perf")

LANGS = {
  "c": dict(src="bench.c", clean="rm -f bench", build="cc -O2 -o bench bench.c", run="./bench",
            bug=("else if(x<y)i++;else j++;", "else if(x<y)j++;else i++;")),
  "ada": dict(src="bench.adb", clean="rm -rf obj bench", build="mkdir -p obj && gnatmake -q -O2 -D obj -o bench bench.adb", run="./bench",
            bug=("elsif A (I) < B (J) then I := I + 1;\n         else J := J + 1;",
                 "elsif A (I) < B (J) then J := J + 1;\n         else I := I + 1;")),
  "rust": dict(src="bench.rs", clean="rm -f bench", build="rustc -O bench.rs -o bench", run="./bench",
            bug=("else if x < y { i += 1; }\n        else { j += 1; }",
                 "else if x < y { j += 1; }\n        else { i += 1; }")),
  "java": dict(src="Bench.java", clean="rm -f *.class", build="javac -d . *.java", run="java -cp . Bench",
            bug=("if (x==y){c++;i++;j++;} else if (x<y) i++; else j++;",
                 "if (x==y){c++;i++;j++;} else if (x<y) j++; else i++;")),
  "python": dict(src="bench.py", clean="", build="", run="python3 bench.py",
            bug=("elif x<y: i+=1\n            else: j+=1", "elif x<y: j+=1\n            else: i+=1")),
}

README = """# bench

A two-operation benchmark over an index of plain-text files.

    {run} find <store> <substr>    count the lines of <store> that contain <substr>
    {run} and  <listA> <listB>     count the ids common to two posting lists
                                   (one integer id per line, ascending, no duplicates)

Each operation prints one row per timed iteration.

Build: `{build}`

`sh check.sh` builds the program and runs both operations on the files in `fixtures/`.
"""

CHECK = """#!/bin/sh
# builds, then runs both operations on the visible fixtures
set -e
cd "$(dirname "$0")"
{build}
{run} find fixtures/store.txt Outputs
{run} and fixtures/a.txt fixtures/b.txt
"""
