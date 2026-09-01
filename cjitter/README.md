# One paper on one library

**It reads [cjitter](https://github.com/Anode1/cjitter), it is a negative result, and it
is not deposited.**

`stationary.tex`, *What Holds a Hand-Drawn Diagram?*, the full version, every
sensitivity inline; `stationary_gd.tex` is the same paper in GD's `gd-lipics` class,
500 lines of main matter and the sensitivities in an appendix, for GD 2027, Track 2. Fitting a layout
energy to human drawings by inverse optimisation assumes the drawings sit at a minimum of
some weighted sum of the standard criteria. Tested one criterion at a time on 853 hand-drawn
diagrams of 15 to 40 boxes, that assumption fails. Overlap holds every box at zero. Uniform
edge length and stress hold 0.3 to 1.1% of hand-placed boxes per corpus, with a median
diagram of 0.00, and not for want of anything to gain. The criterion that does hold a hand
layout, and that the energy omits, is alignment into rows and columns: 0.52 and 0.21 on the
two biological corpora and 0.87 over the full BPMN population, against 0.06 for `neato`. A
hand layout is a layered layout with partial alignment. Measurements are in
`example/diagrams`.

The metaphor-benchmark audit that stood beside it is withdrawn: a correction inherits the
audience of what it corrects. Its verdict tables remain in the library's
`example/metaphors`.

| file | what it is |
| --- | --- |
| PREREGISTRATION-STATIONARITY.md | signed 2026-08-22, governs `stationary.tex` |
| figures/ | the TikZ figures the paper includes |
| verified.bib | every citation checked: DOI resolved, PDF read |
| gd-lipics-v3.cls, lipics-v2021.cls | the GD submission class and the LIPIcs class it wraps |
