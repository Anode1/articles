# bench

A two-operation benchmark over an index of plain-text files.

    java -cp . Bench find <store> <substr>    count the lines of <store> that contain <substr>
    java -cp . Bench and  <listA> <listB>     count the ids common to two posting lists
                                   (one integer id per line, ascending, no duplicates)

Each operation prints one row per timed iteration.

Build: `javac -d . *.java`

`sh check.sh` builds the program and runs both operations on the files in `fixtures/`.
