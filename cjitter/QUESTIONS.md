# What the instrument can test

layout.tex is one candidate paper, already converged and pre-registered. This file is the
opposite instrument: the map of questions the machinery can answer, kept so the template does
not become the boundary of the thinking. The machinery, abstracted away from layout: a
budget-exact, byte-reproducible harness for stochastic search over boxes of reals, with a
matched-budget random control, paired seed panels, exact tests, every method constant exposed
for ablation, and objectives cheap enough to run millions of times. That is a measurement
instrument for search itself. Layout is its first subject, not its definition.

## Questions, roughly ordered by expected yield

1. **At what objective noise does any search stop beating sampling?** Synthetic objective,
   known optimum, injected noise sigma, sweep: sigma*(method, budget) where the sign test
   stops separating from random. This closes a loop with the author's own unpublished draft
   (~/articles/bpnn/resolution.tex), which measured the noise floors of NAS benchmarks: put
   those measured sigmas into this sweep and the result says whether ANY cheap stochastic
   search could have separated architectures at the noise the benchmarks actually carry.
   Two of the author's own lines meeting in one figure, no GPU.

2. **Which stochastic method is efficient where: a field guide by separation budget.** B*
   (evaluations to separate from the control) measured across problem families: incremental
   placement, number partitioning (expected: nothing separates), N-queens and TSP through
   random keys, sphere with and without noise, deceptive traps. The literature compares
   methods by final quality on one family at one budget; a B* map across families is the
   question an engineer actually has, and the control makes "none of them, at any budget you
   can afford" a reportable answer.

3. **Do grouped mutations carry across domains?** The SMBPANN paper's main finding was
   grouped mutations, with its GA a little better than random. The operator question
   generalizes: mutate a coordinated group (in layout, one node's x and y, which is "move a
   table"; in a network, one unit's weights) against mutating every gene independently, at
   matched budget, same panel, exact verdict. If the grouping advantage reappears on
   placement, partitioning and the synthetic families, it is a statement about the operator
   rather than about networks, and it is the direct continuation of that paper's result
   inside the new line of work. The tuning API makes it one field per variant. The 2001
   label placer, the author now recalls precisely, WAS the grouped operator: hill climbing
   per label under the one summed cost. Resurrecting it as a named fifth method (pick a
   group, jitter it, keep if the total improves) puts the original solver into the harness
   against its modern descendants. The same
   experiment has a sibling: SMBPANN fused the two methods, a GA whose mutation carried an
   annealing schedule, where cjitter keeps them sealed so a verdict names a family. Adding
   the fusion as a fifth named method and running it against pure GA and pure annealing at
   matched budget asks whether the hybrid beats the best of its parts, a question the
   memetic-algorithm literature argues and does not test against a control.

   And the mechanism behind the author's GA prediction is itself testable. The prediction's
   reasoning: localized Markovian processes beat memoryless global sampling when the run is
   long and the variables many, because a move inherits every coordinate it does not touch.
   That separates local methods from random, but not the GA from climb and anneal; what the
   GA adds is recombination, whose known edge is modularity, and whose known failure is a
   rotated landscape where no coordinate subset means anything alone. So: the same placement
   problem through a fixed orthogonal rotation of the variables, all four methods, matched
   budget. If the GA's lead survives rotation, the prediction is about the GA; if it
   vanishes, the prediction was about modularity, placement is modular, and grouped
   mutations, recombination and the author's feeling are one finding wearing three coats.

4. **How much of the published method-vs-method literature survives a tuning ablation?**
   The GA here flipped from losing against random to best-of-four by one field
   (ga_mutate_decay 0 -> 0.9). The tuning API makes that systematic: take a claimed ordering,
   sweep the loser's constants at matched budget, report how often the ordering inverts.
   A methodological result about comparisons, not about methods.

5. **The proxy-medium gap, generalized.** The transfer gap (optimize straight, score routed)
   is one instance of scoring a proxy instead of the medium. The same measurement applies to
   any proxy pair the harness can hold: aesthetic-criteria layout scores vs a certified human
   layout; coarse-grid objectives vs fine; any cheap surrogate vs the objective it stands for.
   How large is the gap, and does the method ranking survive crossing it?

6. **The anchor continuum.** One weight from "nothing moves" to full redraw. Where on that
   continuum does the human's accepted layout sit? Is there a lambda at which the search's
   redraw beats neato at neato's own game, or does thirty years of graph drawing win the
   unfrozen end (expected, and worth printing)?

7. **Placement problems adjacent to diagrams**, where frozen context is the real constraint:
   labels around a moving map viewport; seating and floor plans grown by increments; FPGA/PCB
   coarse placement is the heavyweight neighbor (its literature is deep, entering it needs
   care); dashboards and node editors adding panels. Cheap to encode, each is one fitness
   and one repair.

## What is published next door, and the open slot

Stochastic layout: Davidson and Harel (simulated annealing, ACM TOG 1996, straight edges,
aesthetic criteria, ~30 nodes); genetic lines (TimGA and successors); recent metaheuristic
comparisons (Jaya vs hill climbing vs annealing) that still report quality and time only.
The named neighbor is the Constrained Incremental Graph Drawing Problem (Marti and others:
GRASP, Tabu, path relinking; an August 2025 arXiv adds graph representation learning), which
is LAYERED drawing, position-shift constraints, synthetic instance sets. Across all of it:
no matched-budget random control, no routed medium in the objective, no calibration against
a certified human layout, no pre-registration, statistics mostly mean tables. Geometric
frozen-context placement evaluated with those four properties is unoccupied, and questions
1-4 above are not layout questions at all, so the template cannot bind them.
