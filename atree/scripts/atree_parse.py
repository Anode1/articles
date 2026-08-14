#!/usr/bin/env python3
"""Reference parser for the atree line grammar.

Implements exactly the BNF given in the paper's Grammar section, and is used to
check that every example in the paper (Section 5 and Appendix A) derives from
it. Run with no arguments to execute the built-in test suite:

    python3 atree_parse.py            # test the paper's own examples
    python3 atree_parse.py FILE ...   # parse files, report the first bad line
"""
import re, sys

MONTHS = "JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC"

# --- terminals -------------------------------------------------------------
PATH  = r"[MF]+"
HAPNM = r"[0-9A-Za-z][0-9A-Za-z.\-]*"
HAP   = rf"\[(?:(?:Y|mt):)?{HAPNM}\]"
NCH   = r"[0-9A-Za-z'\-.?]"                  # <name_char>
WORD  = rf"{NCH}+"
NTEXT = rf"{WORD}(?:[ \t]+{WORD})*"          # <name_text>, non-empty
MAID  = rf"\((?:{NTEXT})?\)"                 # <maiden>
SNAME = rf"/(?:{NTEXT})?(?:{MAID})?/"        # <surname>

YEAR  = r"[0-9]{1,4}"
DAY   = r"[0-9]{1,2}"
FULL  = rf"{DAY}[ \t]+(?:{MONTHS})[ \t]+{YEAR}"
SHORT = rf"(?:{MONTHS})[ \t]+{YEAR}"
APPRX = r"(?:(?:ABT|BEF|AFT|EST)[ \t]+|~)"
GDATE = rf"(?:{APPRX}?(?:{FULL}|{SHORT}|{YEAR})|\?)"
RANGE = rf"{GDATE}(?:[ \t]*-[ \t]*{GDATE})?"
DATES = rf"\([ \t]*{RANGE}[ \t]*\)"          # <dates>

# --- line-level ------------------------------------------------------------
NAMES = rf"(?:{NTEXT})?(?:[ \t]*{SNAME}(?:[ \t]*{NTEXT})?)?"
LOC   = r"[^#\n]*[^ \t#\n]"                  # <location>: no '#', no trailing blank;
                                             # must be separated by whitespace or a comma

PERSON = re.compile(
    rf"^(?P<path>{PATH})"
    rf"(?:[ \t]+(?P<haps>(?:{HAP}[ \t]*)+))?"
    rf"(?:[ \t]+,?[ \t]*(?P<names>{NAMES}))?"
    rf"(?:[ \t]*(?P<dates>{DATES}))?"
    rf"(?:(?:[ \t]+,?|,)[ \t]*(?P<loc>{LOC}))?"
    rf"(?:[ \t]*(?P<comment>\#[^\n]*))?"
    rf"[ \t]*$"
)
COMMENT_LINE = re.compile(r"^[ \t]*#[^\n]*$")
BLANK        = re.compile(r"^[ \t]*$")


def parse_line(line):
    """Return a dict of fields, or None if the line does not derive."""
    if BLANK.match(line):
        return {"kind": "blank"}
    if COMMENT_LINE.match(line):
        return {"kind": "comment"}
    m = PERSON.match(line)
    if not m:
        return None
    d = {k: (v or "").strip() for k, v in m.groupdict().items()}
    d["kind"] = "person"
    return d


# --- the paper's own examples ---------------------------------------------
SECTION5 = [
    "M   [Y:N1c1] ...",
    "MM  [Y:N1c1] ... /Gavrilov/",
    "MF  [mt:H10a1] Zoya Vasilyevna /Gavrilova (Guseva)/ (20 SEP 1941 - 20 OCT 1984)",
    "MFM Vasiliy Nikolayevich /Gusev/ (~1914 - 1963)",
    "MFF [mt:H10a1] Anastasiya Ivanovna /Guseva (Marinova)/ (20 DEC 1913 - 03 JUN 2006)",
    "MFMF Evdokiya Nikolayevna /Guseva (?)/ (?), Milna, daughter of merchant",
    "MMM [Y:R-M269] Ivan /Gavrilov/ (BEF 1880-?)",
]

# Appendix A lists field forms; each real line is prefixed by a path.
APPENDIX_FIELDS = [
    "FirstName",
    "FirstName (1600)",
    "FirstName (ABT 1600)",
    "FirstName (14 AUG 1855-5 APR 1877)",
    "FirstName /Surname/",
    "FirstName /Surname/ (?-ABT 1800)",
    "FirstName /Surname/ (AFT 1800-?)",
    "/Surname/ (28 OCT 1852-BEF 1880)",
    "FirstName /Surname (MaidenSurname)/ (1764-6 OCT 1813)",
    "FirstName Another Name /Surname (MaidenSurname)/ (14 AUG 1855-5 APR 1877), Place of origin",
    "FirstName // (1600)        # nothing but a date is known",
    "//                         # nothing is known",
    "/?/                        # surname refinement is the priority",
    "FirstName /Surname (?)/    # maiden surname unknown",
    "/Surname/, AnotherName (1800), Place of origin",
    "Names (?) Place of origin",
]

REJECT = [
    "MX Bad path letter",          # X is not a path letter, and no space follows the path
    "[Y:R-M269] no path at all",   # a person line must open with a path
    "123 numeric path",            # paths are [MF]+
    "M/Surname/ no space",         # <path> must be followed by whitespace
]


def main():
    if len(sys.argv) > 1:
        bad = 0
        for path in sys.argv[1:]:
            for n, line in enumerate(open(path), 1):
                if parse_line(line.rstrip("\n")) is None:
                    print(f"{path}:{n}: does not parse: {line.rstrip()}")
                    bad += 1
        sys.exit(1 if bad else 0)

    fails = 0
    print("Section 5 worked example")
    for line in SECTION5:
        ok = parse_line(line) is not None
        print(f"  {'ok  ' if ok else 'FAIL'} {line}")
        fails += not ok
    print("\nAppendix A field forms (each prefixed with a path)")
    for f in APPENDIX_FIELDS:
        line = "MFM " + f
        ok = parse_line(line) is not None
        print(f"  {'ok  ' if ok else 'FAIL'} {f}")
        fails += not ok
    print("\nMust be rejected")
    for line in REJECT:
        ok = parse_line(line) is None
        print(f"  {'ok  ' if ok else 'FAIL'} {line}")
        fails += not ok
    print(f"\n{'all examples derive' if not fails else str(fails) + ' FAILURES'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
