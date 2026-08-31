# Tokens-to-trace

**A measure of what an AI coding agent must read before it can change one
endpoint safely, applied to plain C, idiomatic C++, plain Java with JDBC,
and Spring Boot 4, with 430 controlled agent runs behind it.**

The paper: [tokens_to_trace.pdf](tokens_to_trace.pdf), published as
[doi:10.5281/zenodo.22113993](https://doi.org/10.5281/zenodo.22113993).

The results in four lines. Counted the same way, whole files, the plain C
path is 90k tokens against 257k for idiomatic C++ (taskwarrior); matched
for identical behavior in seven small C/C++ pairs, C++ text is only 1.17x
C. Plain Java with JDBC keeps its whole path (7.6k tokens) inside the
project; Spring Boot 4 keeps 51-124k in framework jars and part of the
behavior in no file at all. In 280 paired agent runs every construct cost
more turns, and a control pair shows the largest cost is one-class-per-file
scatter (+3.5 turns over eight files, +0.5 in one file), not the dispatch.
Correctness never separated: 278 of 280 runs passed identical hidden tests.
Then one endpoint built on both Java stacks, run twice: 80 runs graded by
hidden HTTP checks. The turn cost did not survive its replication (batch
one +1.25 turns, p=0.02; batch two -0.45, p=0.62; combined +0.40, p=0.31),
and what replicated is the failure: five Spring runs of 40 returned silent
wrong answers against zero of 40 plain (one-sided hypergeometric p=0.027),
every one a wire name derived from a Java identifier by a convention no
application file states: @RequestParam bound minLen while the URL said
min_len, and Jackson emitted nameLength where the task said name_length.
The fifteen conventions on that path are stated in 31,535 tokens of
version-pinned documentation sources (cat3.py), four times the plain
side's whole deciding text.

Why, in short. Objects are for people: a class is a bundle sized to a
human working set, an interface is a promise a human can hold whole, and
an agent reads in neither unit. Structs are enough for the data and
functions over them are enough for the algorithm, the way ciphers and
codecs are written in every codebase. The frameworks and the layers were
the correct engineering for human working memory; the reader changed. So
the measure counts what the new reader must hold: the deciding text of
one path, and where that text lives, in your repository, in framework
jars, or in no file at all. The implicit context differs the same way:
K&R is 272 pages, Stroustrup is 1,368, and a framework's documentation
has no fixed size, it moves with the version.

What is here:

| File | What it is |
| --- | --- |
| tokens_to_trace.tex, .pdf | the paper |
| closures.py | the closure manifests; emits closures.json with per-region lines, chars, o200k tokens |
| pairs/ | the 280-run experiment: gen.py (all pair programs), tasks.py, hidden.py (grader with selfcheck), run.py |
| pairs/gen-v1-as-run.py, NOTE-v1.md | the first execution's generator, archived as run |
| endpoint/ | the two-stack endpoint experiment: both service builds (plain/, spring/), tasks.py, hidden.py (HTTP grader with selfcheck), run.py; run twice (runs/, runs2/) |
| cat3.py | category-3 token count for the endpoint stack: the documentation sources stating each convention, fetched at the exact BOM tags; emits cat3.json |
| ieee_software.tex, .pdf, figs.py | the IEEE Software version and its charts, drawn from the raw run records |
| measure.py, external.py, jpa.py, dup.py | corpus measurements the paper cites |
| ROADMAP.md | what is done and what the next experiments are |

Reproduce: `python3 closures.py` re-derives every closure (roots are
overridable env vars; the public subjects re-fetch from the repositories
cited in the paper; one subject is private and its rows ship redacted, so
the public systems reproduce without it). `python3 pairs/hidden.py
selfcheck` verifies the experiment harness; `python3 pairs/run.py` reruns
the experiment against a local `claude` CLI. The measured JSON outputs and
raw run records are not in this repository; they are available from the
author on request.
