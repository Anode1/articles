# Source: LiveJournal (English), "Compact text format for genealogies storing and exchange"

- URL: https://siberean.livejournal.com/14874.html
- Author: Vasili Gavrilov (LJ `siberean`)
- Tags: atree, genealogy, modified-ahnentafel
- Approx date: ~2011-2012 (post id 14874 precedes the conditional-probability post 16220). [TODO: confirm exact date from the post timestamp]
- Russian discussion: http://forum.molgen.org/index.php/topic,3066.0.html and .../topic,3065.0.html
- Tool: `aisgedcom` (GEDCOM 5.5 → atree), https://sourceforge.net/projects/aisgedcom/

This file preserves the primary source verbatim for the article. The author notes the
published BNF is "not without errors/bugs"; it is reproduced here as-is, to be cleaned
in the article (Appendix A).

---

## BNF grammar (as published: contains known minor errors)

```
============================
atree format grammar
============================
<atree>      ::= (<line>)*
<line>       ::= <comment> | <entry>
<comment>    ::= "#" (...)*
<ws>         ::= [:blank:]
<entry>      ::= (<haplogroup>){0,1} (<id>){0,1} (<person>){0,1} "," (<location>){0,1}
<haplogroup> ::= "[" ([:alpha:] | [:digit:]) "]"
<id>         ::= [FM]+
<person>     ::= (...)* (<names>){0,1} (<surname>){0,1} (<dates>){0,1}
<names>      ::= [:alpha:] | [:punct:] | [:blank:]
<surname>    ::= "/" ... {0,1} "/"
<dates>      ::= "(" ... + ")"
<date_range> ::= (<date>){0,1} "-" (<date>){0,1}
<date>       ::= ("ABT " | "BEF " | "AFT ")* [:digit:]{4}
<month>      ::= "JAN"|"FEB"|"MAR"|"APR"|"MAY"|"JUN"|"JUL"|"AUG"|"SEP"|"OCT"|"NOV"|"DEC"
<day>        ::= [:digit:]{1,2}
```

## Core rules

- Each line is one person; the first field is the **id = path of ancestral sexes** (M = father, F = mother) from the subject.
- First character encodes the **subject's own sex** (M if male, F if female).
- Lines are **self-sufficient**: no external context; a single line or subset can be sent to a relative.
- Surname delimited by `/.../` (GEDCOM-style); maiden surname in parentheses inside; `//` or `?` mark unknowns.
- Dates: `ABT`/`BEF`/`AFT` + 4-digit year; ranges `start-end`; `?` for unknown endpoints.
- Optional leading `[haplogroup]` (ties to molecular genealogy); trailing `, location`.

## id ↔ ahnentafel correspondence

| Person | Ahnentafel | Binary | atree (subject F) | atree (subject M) |
|---|---|---|---|---|
| Self | 1 | 1 | F | M |
| Father | 2 | 10 | FM | MM |
| Mother | 3 | 11 | FF | MF |
| Paternal GF | 4 | 100 | FMM | MMM |
| Paternal GM | 5 | 101 | FMF | MMF |
| Maternal GF | 6 | 110 | FFM | MFM |
| Maternal GM | 7 | 111 | FFF | MFF |

First 31 ids (template): `M, MM, MF, MMM, MMF, MFM, MFF, MMMM, MMMF, MMFM, MMFF, MFMM, MFMF, MFFM, MFFF, MMMMM, MMMMF, MMMFM, MMMFF, MMFMM, MMFMF, MMFFM, MMFFF, MFMMM, MFMMF, MFMFM, MFMFF, MFFMM, MFFMF, MFFFM, MFFFF`

## Worked example (author's own ascending tree, excerpt)

```
M   [N1c1] ...                                                              <== subject
MM  [N1c1] ... /Gavrilov/                                                   <== father
MF  [H10a1] Zoya Vasilyevna /Gavrilov (Gusev)/ (20 SEP 1941 - 20 OCT 1984) <== mother
MFM Vasiliy Nikolayevich /Gusev/ (~1914 - 1963)
MFF [H10a1] Anastasiya Ivanovna /Gusev (Marinov)/ (20 DEC 1913 - 03 JUN 2006)
MFMF Evdokiya Nikolayevna /Gusev (?)/ (?), Milna, daughter of merchant
MFMFM Nikolay /?/                                                          <== merchant, owned mill(s)?
MFMFF ?
MFMM Nikolay Gerasimovich /Gusev/, Vladimirskaya obl.
```

## Conversion: ahnentafel number -> atree id (atree2s.sh)

```sh
#!/bin/sh
my_gender=F
female=F
male=M
[ ! -n "$1" ] && { echo "Parameter not passed"; exit -1; }
if ! [[ "$1" =~ ^[0-9]+$ ]] ; then echo "Not a number"; exit -1; fi
input=$1
number=$(echo "obase=2;$input" | bc)
letters=$(printf "%0o\n" 0$number | tr '0' $male | tr '1' $female)
if [ "$my_gender" == "$male" ]; then
  letters=$(echo "$letters" | sed "s/^.\(.*\)/${my_gender}\1/")
fi
echo $letters
# $ sh atree2s.sh 23567   ->  FMFFFMMMMMMFFFF
```

## Conversion: atree id -> ahnentafel number (s2atree.sh)

```sh
#!/bin/sh
female=F
male=M
[ ! -n "$1" ] && { echo "Parameter not passed"; exit -1; }
input=$1
length=$(expr length "$input" - 1)
first_char=$(expr substr "$input" 1 1)
the_rest=$(expr substr "$input" 2 "$length")
if [ "$first_char" == "$male" ]; then
  input=$(echo "$female$the_rest")
fi
binary=$(echo $input | tr $male '0' | tr $female '1')
decimal=$(echo "ibase=2;obase=A;$binary" | bc)
echo $decimal
# $ sh s2atree.sh MFFMMMMFFFMMF   ->  7225
```

## Author's rationale / claims

- **Scalability:** path length grows as the *logarithm* of the tree size; decimal ahnentafel numbers "may overflow computer registers."
- **Exchange:** standardizes spaces, delimiters, and unknown-markers for human exchange and automated internet processing.
- **Interop:** `aisgedcom` converts plain-text GEDCOM 5.5/5.5.1 → atree.

## Stated limitations

- Ascending (ancestor) tree only: "not supposed to work for more general graphs for descending genealogies."
- The tree always shows one level of unknown terminal nodes (`?`) for not-yet-researched parents.
