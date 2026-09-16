# One paper on one library

**It is built on [cjitter](https://github.com/Anode1/cjitter), and it is a check to run before
fitting a layout energy to human coordinates: per criterion, whether a diagram a person
laid out in an editor is a local minimum, against a converged layout and a random one.
On 853 diagrams from three editors, 136 laboratory drawings and 1,072 published figures,
edge length and stress hold under 0.015 of the boxes at any weight; alignment and flow,
which neither base energy prices, hold the boxes.**

`stationary.tex`, *Layouts Made in Diagram Editors Are Held by Alignment and Flow, Not by
Edge Length or Stress: A Per-Term Stationarity Test Before Fitting a Layout Energy*.
Inverse optimisation and inverse optimal control fit an objective to demonstrations taken
as stationary points; graph drawing has not made that fit and now has a corpus to make it
on. The paper's abstract carries the numbers. Measurements are in `example/diagrams` in
the [cjitter repository](https://github.com/Anode1/cjitter).

[stationary.pdf](stationary.pdf), [stationary_supplement.pdf](stationary_supplement.pdf),
[doi:10.5281/zenodo.22313827](https://doi.org/10.5281/zenodo.22313827) (all versions).

The metaphor-benchmark audit that stood beside it is withdrawn: a correction inherits the
audience of what it corrects. Its verdict tables remain in
`example/metaphors` in the [cjitter repository](https://github.com/Anode1/cjitter).

| file | what it is |
| --- | --- |
| stationary_supplement.tex | the sensitivities, controls and secondary estimands, one section each, cited from the paper as Supplement S1 to S8 |
| PLAN-STATIONARITY.md | the analysis plan the study started from, signed 2026-08-22; outcomes and departures in Supplement S8 |
| figures/ | the TikZ figures the paper includes |
| verified.bib | every citation checked: DOI resolved, PDF read, or the note says what was not |
| corpora/ | the three raw archives and a clone of the WikiPathways database repository, not in git and not in any deposit |
| gd-lipics-v3.cls, lipics-v2021.cls | the GD submission class and the LIPIcs class it wraps, kept for a conference edition |
