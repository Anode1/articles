# What a search shows, and what a benchmark never asked

**Two drafts, both negative results, both read from the same library:
[cjitter](https://github.com/Anode1/cjitter). Neither is deposited.**

`stationary.tex`, *What Do People Optimize in Diagram Layout?*, 19 pages. Fitting a layout
energy to human drawings by inverse optimisation assumes the drawings sit at a minimum of
some weighted sum of the standard criteria. Tested one criterion at a time on 853 hand-drawn
diagrams of 15 to 40 boxes, that assumption fails. Overlap holds every box at zero. Uniform
edge length and stress hold 0.3 to 1.1% of hand-placed boxes per corpus, with a median
diagram of 0.00, and not for want of anything to gain. The criterion that does hold a hand
layout, and that the energy omits, is alignment into rows and columns: 0.52 and 0.21 on the
two biological corpora and 0.87 over the full BPMN population, against 0.06 for `neato`. A
hand layout is a layered layout with partial alignment. Measurements are in
`example/diagrams`.

`audit.tex`, *The Test the Metaphor Benchmark Never Ran*, 5 pages. The largest benchmark of
metaphor-based optimization heuristics ran 294 implementations for 1,411,200 runs on the 24
BBOB functions and contains no statistical test: the word does not occur in it, and none of
the 21 papers citing it adds one. Its raw data is public, so the missing test is computable
from it. At the top budget of 10^4 d evaluations, 66 to 98 implementations per dimension,
one in three in 2D, are not shown better than uniform random sampling at equal cost, and 53
to 79 of those are shown strictly worse. Measurements are in `example/metaphors`, run
against the benchmark's own release, Zenodo 10.5281/zenodo.10561215.

| file | what it is |
| --- | --- |
| PREREGISTRATION-STATIONARITY.md | signed 2026-08-22, governs `stationary.tex` |
| PREREGISTRATION-AUDIT.md | signed before the audit's confirmatory numbers were computed |
| audit-data/ | the audit's verdict tables, summaries and robust set |
| figures/ | the TikZ figures both papers include |
| review/ | the referee panels, by paper |
