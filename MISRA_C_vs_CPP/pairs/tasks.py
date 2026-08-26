#!/usr/bin/env python3
"""tasks.py: four tasks per pair, the same text for both languages, naming
behavior and output only, never a file, a function, or a language construct.
Per pair: two local tasks (t1 feature at the print site, t2 add a command or
mode) and two whose effect lives behind the construct (t3 semantics change,
t4 an injected defect to find and fix). DEFECTS[(pair, lang)] is the list of
(file, old, new) substitutions applied before a t4 run only.

CHECKS[(pair, task)] is the hidden suite: each check is a dict with the
data.txt content (None = no file), argv, optional stdin, and the expected
stdout, exit code, stderr, out.txt content or absence. Baseline regressions
ride along so an untouched command must stay untouched.
"""

D1 = "3|tea\n11|espresso\n7|milk\n11|latte\n2|x\n"
DE = "3|tea\nE|11|espresso|maria k\n7|milk\nE|4|latte|jo\nE|5|mocha|maria k\n"
DE2 = "E|1|a|mariah\nE|2|b|maria k\n"
DM = "9|-250\n1|1000\n4|-500\n2|300\n"
DM2 = "1|-500\n2|300\n"
DOV = "1|1999999999\n2|2\n"
DT = "5|aaaa\n6|bbbb\n"
DCRLF = "3|tea\r\n11|espresso\r\n"

TASKS = {}
def _alias():
    pass
_VIRT1 = None
_T = {
("virt", "t1"): "The list command prints each record as id|value. Change list, and only list, to print id|value|N where N is the number of characters in the value.",
("virt", "t2"): "Add a command 'last' that prints the one record line with the numerically largest id; when several share it, the later line wins. On an empty store it prints 'empty' and exits 1.",
("virt", "t3"): "When find matches nothing it prints nothing and exits 0. Change it: with no matching record, print 'no match' to standard error and exit 1. Matching behavior stays as it is.",
("virt", "t4"): "The count command prints a number one higher than the true number of records. Fix it.",
("tmpl", "t1"): "Both commands print the winning record as id|value. Change the output of every command to best=id|value.",
("tmpl", "t2"): "Add a command 'shortest' that prints the record with the shortest value, first wins a tie, as id|value. On an empty store it prints 'empty' and exits 1.",
("tmpl", "t3"): "On a tie today the earlier record wins, for every command. Change the tie-breaking so the later record wins, for every command.",
("tmpl", "t4"): "Both commands pick the wrong record: maxid prints the record with the smallest id, and longest prints one of the shortest values. Fix the selection so each command picks the largest again, with the earlier record winning ties.",
("oper", "t1"): "Every printed amount must be prefixed with USD and a space: USD 12.34, and for negatives USD -5.00.",
("oper", "t2"): "Add a command 'min' that prints the smallest amount, in the same format max uses. On an empty store it prints 'empty' and exits 1.",
("oper", "t3"): "Any addition that would take the running sum above 2000000000 cents or below -2000000000 cents must stop the program immediately: print 'overflow' and exit 3, whatever the command.",
("oper", "t4"): "Negative amounts confuse the max command: with the amounts -500 and 300 it prints -5.00, but the largest is 3.00. Fix the comparison so max is right for any mix of signs.",
("raii", "t1"): "The trailer line is 'packed K'. Change it to 'packed K of T' where T is the total number of records read.",
("raii", "t2"): "Accept an optional final argument -v: when it is given, print the id of each kept record to standard error, one per line, in input order. Output files stay exactly as they are.",
("raii", "t3"): "After any failed run (nonzero exit), out.txt must not exist, even if an earlier run left one behind or this run created a partial one. Successful runs keep writing out.txt as today.",
("raii", "t4"): "When no record is long enough, out.txt is missing its trailer line. Every successful run must end out.txt with the trailer, 'packed 0' included.",
("inh", "t1"): "In the list output, prefix plain records with 'R ' and extended records with 'X ': R 3|tea, X 11|espresso|maria k.",
("inh", "t2"): "Add a command 'count' that prints two numbers separated by one space: the total number of records, then the number of extended records.",
("inh", "t3"): "Everywhere an id is printed, print it zero-padded to four digits: 0003 instead of 3. Nothing else about the output changes.",
("inh", "t4"): "The who command treats two different people as the same person when their names begin with the same three letters, and prints only the first. Print every distinct full name, in order of first appearance.",
("mix", "t1"): "Before the record lines, print one line total=K where K is the number of records about to be printed.",
("mix", "t2"): "Accept an optional final argument --desc: sort descending by id instead of ascending; records sharing an id keep input order either way.",
("mix", "t3"): "Input with Windows line endings leaves an invisible carriage return at the end of each value. Strip it wherever input is read, so file and standard input give identical values.",
("mix", "t4"): "Records that share an id print in reverse input order; they must print in input order. Everything else about the ordering is right.",
}
TASKS.update(_T)
for _k, _v in list(_T.items()):
    if _k[0] == "virt":
        TASKS[("virt1", _k[1])] = _v

DEFECTS = {
("virt", "c"): [("store.c", "long n = 0;", "long n = 1;")],
("virt", "cpp"): [("cmd_count.cpp", "read_lines().size()", "read_lines().size() + 1")],
("virt1", "c"): [("store.c", "long n = 0;", "long n = 1;")],
("virt1", "cpp"): [("store.cpp", "read_lines().size()", "read_lines().size() + 1")],
("tmpl", "c"): [("store.c", "if (ids[i] > ids[best])", "if (ids[i] < ids[best])"),
                ("store.c", "if (strlen(values[i]) > strlen(values[best]))",
                 "if (strlen(values[i]) < strlen(values[best]))")],
("tmpl", "cpp"): [("maxby.h", "if (key(i) > key(best))", "if (key(i) < key(best))")],
("oper", "c"): [("store.c", "return a.cents < b.cents;",
                 "return (unsigned long)a.cents < (unsigned long)b.cents;")],
("oper", "cpp"): [("money.h", "return a.cents < b.cents;",
                   "return (unsigned long)a.cents < (unsigned long)b.cents;")],
("raii", "c"): [("store.c", '    fprintf(out, "packed %ld\\n", k);',
                 '    if (k > 0)\n        fprintf(out, "packed %ld\\n", k);')],
("raii", "cpp"): [("main.cpp", '    std::fprintf(out.get(), "packed %ld\\n", k);',
                   '    if (k > 0)\n        std::fprintf(out.get(), "packed %ld\\n", k);')],
("inh", "c"): [("store.c", "if (strcmp(whos[i], w) == 0)",
                "if (strncmp(whos[i], w, 3) == 0)")],
("inh", "cpp"): [("main.cpp", "if (w == e->who())",
                  "if (w.compare(0, 3, e->who(), 0, 3) == 0)")],
("mix", "c"): [("store.c", "return ra->seq - rb->seq;", "return rb->seq - ra->seq;")],
("mix", "cpp"): [("reader.h", "return a.seq < b.seq;", "return b.seq < a.seq;")],
}

def C(data, argv, out, rc=0, err=None, stdin=None, outfile=None,
      outfile_absent=False, precreate_outfile=None):
    return {"data": data, "argv": argv, "stdin": stdin, "out": out, "rc": rc,
            "err": err, "outfile": outfile, "outfile_absent": outfile_absent,
            "precreate_outfile": precreate_outfile}

FIND_E = "3|tea\n11|espresso\n11|latte\n"
LIST1 = D1
PACK4 = "11|espresso\n7|milk\n11|latte\n"

CHECKS = {}
_C = {
("virt", "t1"): [C(D1, ["list"], "3|tea|3\n11|espresso|8\n7|milk|4\n11|latte|5\n2|x|1\n"),
                 C(D1, ["find", "e"], FIND_E),
                 C(D1, ["count"], "5\n")],
("virt", "t2"): [C(D1, ["last"], "11|latte\n"),
                 C("", ["last"], "empty\n", rc=1),
                 C(D1, ["list"], LIST1),
                 C(D1, ["count"], "5\n")],
("virt", "t3"): [C(D1, ["find", "zzz"], "", rc=1, err="no match\n"),
                 C(D1, ["find", "e"], FIND_E, rc=0),
                 C(D1, ["list"], LIST1)],
("virt", "t4"): [C(D1, ["count"], "5\n"),
                 C("", ["count"], "0\n"),
                 C(D1, ["list"], LIST1)],
("tmpl", "t1"): [C(D1, ["maxid"], "best=11|espresso\n"),
                 C(D1, ["longest"], "best=11|espresso\n"),
                 C(DT, ["maxid"], "best=6|bbbb\n"),
                 C("", ["maxid"], "empty\n", rc=1)],
("tmpl", "t2"): [C(D1, ["shortest"], "2|x\n"),
                 C("", ["shortest"], "empty\n", rc=1),
                 C(D1, ["maxid"], "11|espresso\n"),
                 C(D1, ["longest"], "11|espresso\n")],
("tmpl", "t3"): [C(D1, ["maxid"], "11|latte\n"),
                 C(DT, ["longest"], "6|bbbb\n"),
                 C(D1, ["longest"], "11|espresso\n")],
("tmpl", "t4"): [C(D1, ["maxid"], "11|espresso\n"),
                 C(D1, ["longest"], "11|espresso\n"),
                 C(DT, ["maxid"], "6|bbbb\n")],
("oper", "t1"): [C(DM, ["sum"], "USD 5.50\n"),
                 C(DM, ["max"], "USD 10.00\n"),
                 C(DM2, ["sum"], "USD -2.00\n"),
                 C("", ["sum"], "empty\n", rc=1)],
("oper", "t2"): [C(DM, ["min"], "-5.00\n"),
                 C("", ["min"], "empty\n", rc=1),
                 C(DM, ["sum"], "5.50\n"),
                 C(DM, ["max"], "10.00\n")],
("oper", "t3"): [C(DOV, ["sum"], "overflow\n", rc=3),
                 C(DOV, ["max"], "overflow\n", rc=3),
                 C(DM, ["sum"], "5.50\n"),
                 C(DM, ["max"], "10.00\n")],
("oper", "t4"): [C(DM2, ["max"], "3.00\n"),
                 C(DM, ["max"], "10.00\n"),
                 C(DM, ["sum"], "5.50\n")],
("raii", "t1"): [C(D1, ["pack", "4"], "", outfile=PACK4 + "packed 3 of 5\n"),
                 C(D1, ["pack", "99"], "", outfile="packed 0 of 5\n"),
                 C(None, ["pack", "3"], "", rc=1)],
("raii", "t2"): [C(D1, ["pack", "4", "-v"], "", err="11\n7\n11\n",
                   outfile=PACK4 + "packed 3\n"),
                 C(D1, ["pack", "4"], "", err="", outfile=PACK4 + "packed 3\n")],
("raii", "t3"): [C(None, ["pack", "3"], "", rc=1, outfile_absent=True,
                   precreate_outfile="stale\n"),
                 C(D1, ["pack", "4"], "", outfile=PACK4 + "packed 3\n")],
("raii", "t4"): [C(D1, ["pack", "99"], "", outfile="packed 0\n"),
                 C(D1, ["pack", "4"], "", outfile=PACK4 + "packed 3\n")],
("inh", "t1"): [C(DE, ["list"], "R 3|tea\nX 11|espresso|maria k\nR 7|milk\n"
                                "X 4|latte|jo\nX 5|mocha|maria k\n"),
                C(DE, ["who"], "maria k\njo\n")],
("inh", "t2"): [C(DE, ["count"], "5 3\n"),
                C(DE, ["list"], "3|tea\n11|espresso|maria k\n7|milk\n"
                                "4|latte|jo\n5|mocha|maria k\n")],
("inh", "t3"): [C(DE, ["list"], "0003|tea\n0011|espresso|maria k\n0007|milk\n"
                                "0004|latte|jo\n0005|mocha|maria k\n"),
                C(DE, ["who"], "maria k\njo\n")],
("inh", "t4"): [C(DE2, ["who"], "mariah\nmaria k\n"),
                C(DE, ["who"], "maria k\njo\n"),
                C(DE, ["list"], "3|tea\n11|espresso|maria k\n7|milk\n"
                                "4|latte|jo\n5|mocha|maria k\n")],
("mix", "t1"): [C(D1, ["report", "3"], "total=4\n3|tea\n7|milk\n11|espresso\n11|latte\n"),
                C(D1, ["report", "99"], "total=0\n"),
                C(None, ["report", "3", "nofile.txt"], "", rc=1)],
("mix", "t2"): [C(D1, ["report", "3", "data.txt", "--desc"],
                  "11|espresso\n11|latte\n7|milk\n3|tea\n"),
                C(D1, ["report", "3"], "3|tea\n7|milk\n11|espresso\n11|latte\n")],
("mix", "t3"): [C(DCRLF, ["report", "3"], "3|tea\n11|espresso\n"),
                C(None, ["report", "3", "-"], "3|tea\n11|espresso\n", stdin=DCRLF),
                C(D1, ["report", "3"], "3|tea\n7|milk\n11|espresso\n11|latte\n")],
("mix", "t4"): [C(D1, ["report", "3"], "3|tea\n7|milk\n11|espresso\n11|latte\n"),
                C(D1, ["report", "0"], "2|x\n3|tea\n7|milk\n11|espresso\n11|latte\n")],
}
CHECKS.update(_C)
for _k, _v in list(_C.items()):
    if _k[0] == "virt":
        CHECKS[("virt1", _k[1])] = _v
