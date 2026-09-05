# One paper on one library

**It reads [cjitter](https://github.com/Anode1/cjitter), and it is a negative result:
a diagram a person laid out is a local minimum of no weighting of the standard layout
energy with positive weight on a distance term, and the criterion that does hold its
boxes, alignment into rows and columns, is one neither base energy prices.**

`stationary.tex`, *Hand-Drawn Diagrams Are Not Minima of Edge-Length or Stress Energies*.
Fitting a layout energy to human drawings by inverse optimisation assumes the drawings
sit at a minimum of some weighted sum of the standard criteria. Tested one criterion at a
time on 853 working diagrams of 15 to 40 boxes, 136 laboratory drawings and 1,072
drawings from the graph-drawing proceedings, that assumption fails. Overlap holds every
box at zero. Uniform edge length and stress hold 0.00 of the median drawing in every
corpus while a stress minimiser's own layouts are held at 1.00, and a weight of 0.001 on
either term holds under 0.015 of the boxes. Alignment puts 58, 36 and 81 per cent of
hand-placed boxes in a row or column of three or more, none of the stress minimiser's,
and a pairwise alignment term holds 0.52, 0.21 and 0.85 of them against 0.06 to 0.07 by
chance; offered every term, the fit puts 0.81 of its weight on alignment in the one corpus
where no term is satisfied exactly.
Whether the hand or the editor's guide aligned them the coordinates cannot say, and for a
fit it does not matter. Measurements are in `example/diagrams` in the
[cjitter repository](https://github.com/Anode1/cjitter).

[stationary.pdf](stationary.pdf),
[doi:10.5281/zenodo.22313827](https://doi.org/10.5281/zenodo.22313827) (the first
edition; the version here is not yet deposited).

The metaphor-benchmark audit that stood beside it is withdrawn: a correction inherits the
audience of what it corrects. Its verdict tables remain in
`example/metaphors` in the [cjitter repository](https://github.com/Anode1/cjitter).

| file | what it is |
| --- | --- |
| PREREGISTRATION-STATIONARITY.md | signed 2026-08-22, the plan the study was run to; its hypotheses and outcomes are the paper's last appendix |
| stationary_gd.tex | the first edition in GD's `gd-lipics` class, not rebuilt from the current text |
| figures/ | the TikZ figures the paper includes |
| verified.bib | every citation checked: DOI resolved, PDF read, or the note says what was not |
| corpora/ | the three raw archives and a clone of the WikiPathways database repository, not in git |
| gd-lipics-v3.cls, lipics-v2021.cls | the GD submission class and the LIPIcs class it wraps |
