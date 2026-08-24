# bench

A two-operation benchmark over an index of plain-text files.

    ./bench find <store> <substr>    count the lines of <store> that contain <substr>
    ./bench and  <listA> <listB>     count the ids common to two posting lists
                                   (one integer id per line, ascending, no duplicates)

Each operation prints one row per timed iteration.

Build: `rustc -O bench.rs -o bench`

`sh check.sh` builds the program and runs both operations on the files in `fixtures/`.
