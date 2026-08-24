# bench

A two-operation benchmark over an index of plain-text files.

    python3 bench.py find <store> <substr>    count the lines of <store> that contain <substr>
    python3 bench.py and  <listA> <listB>     count the ids common to two posting lists
                                   (one integer id per line, ascending, no duplicates)

Each operation prints one row per timed iteration.

Build: `(none: it is a script)`

`sh check.sh` builds the program and runs both operations on the files in `fixtures/`.
