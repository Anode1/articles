#!/usr/bin/env python3
"""The task text. Identical for every condition, and it names no command:
finding the sites is part of what is measured."""

TASK = (
    "Every command of this program prints one result line on success. "
    "Add a field to that line so it also reports the length of the argument it was given: "
    "the line must end with a space and then arg=N, where N is the number of characters "
    "in the command's argument. For example a line that read `add ok=1 n=3` must now read "
    "`add ok=1 n=3 arg=3`. This must hold for every command the program accepts, with no "
    "exceptions. Change nothing else about the output. Verify with ./check.sh, "
    "and do not ask questions."
)
