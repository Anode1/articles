# Placing a migration's tables into a diagram somebody already arranged

`placement.tex`, the engineering paper for `~/cjitter/example/erd`. Five pages.

The claim is narrow on purpose. Freezing a subset and optimising the rest is Brandes and
Wagner 1997, Frishman and Tal's pinning weight, and it ships in Graphviz, ELK, NetworkX,
d3-force, draw.io, Visio, MSAGL and yFiles; the paper says so and claims none of it. What is
new is the edge model: every one of those libraries scores straight centre-to-centre
segments, an entity-relationship diagram draws orthogonal connectors, and the choice decides
the answer. Under straight edges the maintainer's arrangement and a uniform random placement
score within one per cent of each other.

Two results in it are against the authors and stay in: the searches beat the maintainer
under the routed objective, which means the objective is incomplete; and freezing buys
stability rather than quality, since a hill climber reaches the same overlap with the
diagram frozen or free.

Figures are generated from the committed geometry in `~/cjitter/example/erd/data`.
