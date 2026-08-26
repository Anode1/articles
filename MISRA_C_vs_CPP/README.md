# Tokens-to-trace

**A measure of what an AI coding agent must read before it can change one
endpoint safely, applied to plain C, idiomatic C++, plain Java with JDBC,
and Spring Boot 4, with a 280-run controlled agent experiment behind it.**

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
| measure.py, external.py, jpa.py, dup.py | corpus measurements the paper cites |
| ROADMAP.md | what is done and what the next experiments are |

Reproduce: `python3 closures.py` re-derives every closure (roots are
overridable env vars; the public subjects re-fetch from the repositories
cited in the paper; one subject is private and its rows ship redacted, so
the public systems reproduce without it). `python3 pairs/hidden.py
selfcheck` verifies the experiment harness; `python3 pairs/run.py` reruns
the experiment against a local `claude` CLI. The measured JSON outputs and
raw run records are not in this repository; they ship with the Zenodo
deposit.
