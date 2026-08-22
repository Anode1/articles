# Pre-registration: which aesthetic criteria hold a human-authored diagram layout?

Signed Vasili Gavrilov, 2026-08-22. Amended from the unsigned draft of the same morning
after three independent reviews (review/) and the checks of review/checks-2026-08-22.md.
Everything measured before this date is exploratory and is declared in section 9.

## 1. The question

Layout tools minimise a weighted sum of aesthetic criteria. If people drew that way, a
hand layout would be a local minimum of every criterion that carries weight. We test each
criterion separately on diagrams whose coordinates a person chose, against the same test
on layouts a tool produced for the same graphs, and ask which criteria people satisfy
exactly, which they do not, and whether any weighting or any candidate missing criterion
makes the sum hold the layout.

## 2. Corpora

- WikiPathways GPML, CC0, Homo sapiens archive of 2026-08-10, without WP5037 and WP3391
  (coordinates converted from Reactome).
- Reactome SBGN-ML.
- BPMN Academic Initiative model collection.
- HOLA formative layouts (data.graphlayout.net/HOLA/formative/), 17 designers x 8 graphs,
  as a fourth corpus with its own inclusion rule (all sizes; 4 to 13 nodes).

Inclusion for the first three: largest connected component of 15 to 40 nodes, at least one
edge, positive extent. Container glyphs are not nodes; SBGN process glyphs are. Rescale to
the unit square, box sizes with it. Deduplicate by model identity. Realised counts
reported, with the size distribution, and a 41 to 100 node sensitivity.

Geometry: crossings, orthogonality and node-edge separation are evaluated on the stored
polylines (GPML and SBGN waypoints and anchors, BPMN dockers); the fraction of edges with
waypoints is reported per corpus; the straight-chord values are a sensitivity.

## 3. Terms and energies

Terms, each normalised as in stationary.tex: T_C crossings, T_O overlap, T_L edge-length
uniformity (L the layout's median edge length; L = 1/sqrt(N) as sensitivity), T_S stress
(graph distances scaled by L), T_R orthogonality, T_A alignment, T_N node-edge separation.
Alignment primary definition: HOLA gridiness R4 (fraction of nodes in an alignment of
three or more, tolerance 0.005 of the drawing width); A1, A2, A3 as sensitivities.

Energies declared: each term alone; C+O; C+O+L at (1,1,1); S; C+O+S; C+O plus each
candidate (R, A, N) at fitted weight; all seven at fitted weights.

## 4. Estimand

PRIMARY. q_d: the fraction of nodes held, where node i is held if none of 16 equally
spaced moves of length d lowers the energy with every other node fixed. Deterministic.
d = 0.02 of the drawing width primary; d in {0.005, 0.01, 0.05} and d = one grid pitch as
sensitivities.

SECONDARY. The capped descent of the earlier draft (fraction of the cap used, fraction of
energy removed), hill climbing one node per proposal through cjitter with block = 2, step
0.25 of the cap, patience N, 4000 evaluations, 15 seeds averaged within instance.

Weights: the linear program over the simplex minimising total violation of
sum_k w_k D_iv T_k >= 0 over nodes and directions, fitted on training folds of 5x2
cross-validation, residual and q_d reported on held-out folds. The 200-draw random search
of the pilot beside it as a check.

## 5. References and controls

- Converged reference: the layout after an uncapped descent under the same energy; q_d
  must exceed 0.95, or the test lacks power for that energy.
- Tool controls: neato and dot layouts of the same graph with the same box sizes; ELK
  layered for BPMN. Same test, same terms. These are the null distribution for every
  comparison.
- Matched-budget control: uniform placement inside the cap at the same evaluation budget
  through cjitter_compare, for the secondary estimand.

## 6. Hypotheses

- H1. Under C+O the hand layout is held: median q_0.02 above 0.9 in every corpus, and above
  the neato control. REFUTED in a corpus where either fails.
- H2. Under T_L alone it is not: median q_0.02 below 0.2 in every corpus and below the
  neato control. REFUTED if any corpus is at or above 0.2.
- H3. No positive weight on T_L repairs C+O+L: the LP gives T_L weight zero and q_0.02
  under C+O+L at any weight above 0.01 on T_L is below 0.2. REFUTED if a weight on T_L
  above 0.01 keeps median q_0.02 above 0.5.
- H4, directional. Alignment holds more hand-placed boxes than orthogonality or node-edge
  separation in every corpus, and more than in the tool control. Declared fragile for BPMN
  under the half-grid jitter test of section 7.
- H5, exploratory. Under stress alone the hand layout is held less than the neato layout.

Prediction, recorded before the run: H1, H2, H3 hold in all corpora; H4 holds in
WikiPathways and HOLA, fails on BPMN after jitter; H5 holds.

## 7. Alternatives declared, each with its test

- Grid snapping: pitch detected per corpus; every box jittered by half a pitch; the
  alignment cell rerun. What survives is reported as the person's.
- Unmodelled constraints: a flow term (edges against reading direction) and containment
  (compartment, lane) as a hard constraint, added as candidates to C+O.
- Cap in other units: d as a fraction of median box width and of median edge length; rank
  correlation of instance q_d across units.
- Selection: q_d against m/n and n within each corpus.

## 8. Analysis

Unit of inference: the diagram. Per corpus: H1 and H2 by the one-sided exact Wilcoxon
signed-rank test of hand minus neato, exact sign test beside it, Hodges-Lehmann shift with
95% distribution-free interval. Family F1 = H1 over the corpora, F2 = H2 and H3 over the
corpora, Holm within each. H4 and H5 descriptive with bootstrap intervals (1000 resamples
of diagrams), no p-value. Thresholds tested by the lower 95% bootstrap bound on the median.
Every null result carries an interval. All tests at d = 0.02; other caps and alignment
definitions are sensitivity tables without tests.

One binary, one commit of cjitter, named in the freeze, for reference, controls, fit and
test; the directional test has no seed.

## 9. Exploratory work, declared

2026-08-21: the pilot of PILOT.md (capped climber, step five times the cap, one seed,
A1 primary, energy-fraction estimand). 2026-08-22: the step sensitivity, the grid
diagnostic, and the directional test on 60 diagrams per corpus against neato
(review/checks-2026-08-22.md): q_0.02 under C+O 1.00, 1.00, 0.94; under T_L 0.00, 0.06,
0.10; alignment A1 0.53, 0.28, 0.79. Those numbers fixed the hypotheses above and are
superseded by anything this file produces.

## 10. Deviations

Any departure from this file is recorded here, dated, with the reason, before the affected
analysis is run.
