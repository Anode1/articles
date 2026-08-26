# Compress the Access, Not the Store

**How many tokens an AI agent spends to find an answer by searching the files, against
recalling it from a curated key index, measured on a real project of about 100k lines.**

Agents pay for context in tokens, and the bill grows with the store: file search and vector
retrieval scan the whole thing, sometimes badly. The same agent loop runs the same questions
twice, once with `grep` and read, once with the index.

The result depends on how the index is used, which is a design choice. When it returns the
answer or a reference a person consumes, retrieval is about 69x cheaper on the content
pulled into context, correct in 40 of 40 across repeats against 31 of 40 (on a substring
grading that by construction favours the curated index), and flat in repository size, while
search grows and occasionally explodes: one query reached 170,000 total tokens. Run directly
on the command line it costs zero model tokens. Making the model read the recalled document
instead shrinks the gain to about 3x, an avoidable misuse.

The idea is old: a user-owned plain-text index, exact and self-verifying, where a wrong key
returns the empty set and a checksum settles the rest, in a format that predates RAG. What
is new is the measurement. The tool measured is [ais](https://github.com/Anode1/ais).

`appendix_results.tex` holds the per-question runs; `priority_record.md` is the priority and
provenance record.

[compress_the_access.pdf](compress_the_access.pdf),
[doi:10.5281/zenodo.20764255](https://doi.org/10.5281/zenodo.20764255). The provenance
record is [doi:10.5281/zenodo.20647048](https://doi.org/10.5281/zenodo.20647048).
