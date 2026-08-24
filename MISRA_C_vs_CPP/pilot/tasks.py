"""The four maintenance tasks. One text each, identical for every language: it
names behaviour and output, never a file, function or language feature."""

INTRO = ("This directory holds a small command-line benchmark program. README.md says how to "
         "build and run it, and `sh check.sh` builds it and runs it on the files in fixtures/. "
         "It has two operations: a full scan of a store file counting the lines that contain a "
         "substring, and the intersection of two sorted posting lists (one integer id per line, "
         "ascending, no duplicates).\n\n")

OUTRO = ("\n\nKeep everything else unchanged, verify with check.sh before finishing, and do not "
         "ask questions: complete the task and stop.")

TASKS = {
  "t1_diff": INTRO +
    "Add a third operation, `diff`, taking the same two posting-list arguments as the intersection. "
    "It must count the ids present in the first list and absent from the second, in a single forward "
    "pass over both lists, without building a set, map or hash table. Like the other operations it "
    "prints one row per timed iteration; each of its rows must begin with `diff` and contain "
    "`only=<count>`, where <count> is that number." + OUTRO,
  "t2_icase": INTRO +
    "The scan currently counts a line when it contains the substring with an exact byte match. "
    "Change the scan so that ASCII letters match regardless of case (`a` matches `A`); every byte "
    "that is not an ASCII letter must still match exactly. A line is still counted at most once. "
    "The output format is unchanged." + OUTRO,
  "t3_bug": INTRO +
    "The intersection reports a wrong count on the fixture lists: check.sh shows the value it "
    "prints, and the correct number of ids common to fixtures/a.txt and fixtures/b.txt is 4. "
    "Find and fix the defect without changing the output format." + OUTRO,
  "t4_firstlast": INTRO +
    "After the timed rows of the intersection, print one extra final line of the form "
    "`first=<id> last=<id>` giving the smallest and the largest id common to both lists, or "
    "`first=none last=none` when they have no id in common. The timed rows themselves are "
    "unchanged." + OUTRO,
}
