# Plan for the stationarity paper, 2026-08-22

Three independent reviews (review/methodologist.md, review/referee.md, review/code.md) and
two days of checks (review/checks-2026-08-22.md) read against the pilot. This file is what
they agree on and what to do, ranked. The pre-registration stays unsigned until the
amendments in section 4 are accepted or refused.

## 1. The finding, as it now stands

Under crossings and overlap the hand layout is a local minimum: fraction of boxes with no
improving direction among 16 at radius 0.02 is 1.00, 1.00, 0.94 on WikiPathways, Reactome,
BPMN. Under uniform edge length it is not: 0.00, 0.06, 0.10. The pilot's "hand layouts are
not stationary" was the length term and nothing else; with any positive weight on it the
sum holds no box, which is why every fit gave it weight zero. neato's layouts have the
opposite profile. Alignment A1 holds 0.53, 0.28, 0.79 of hand-placed boxes and under 0.06
of neato's. Exact alignment is the person's act in WikiPathways (2% integer coordinates, a
third of boxes share an x) and mostly the grid and the lanes in BPMN.

The paper's claim is therefore a profile, per criterion, of what people satisfy exactly and
what they do not, not "people are not at a minimum". The referee's surviving title was the
negative one; the sharper profile is more defensible because each cell is a deterministic
count with a tool control beside it.

## 2. What was wrong with the pilot

| defect | found by | consequence | fix |
| --- | --- | --- | --- |
| step 0.1 at cap 0.02: proposals land on the cap circle | methodologist A1, code D1 | delta_d = fraction of nodes that accepted any move; alignment residual 47 to 18 with the step | directional test primary; descent step set from the cap |
| only the length term has a gradient at the hand layout | methodologist A2, referee B3 | H1 under (1,1,1) is "edges are not uniform" | per-term test; report the profile |
| null is the same climber's fixed point | methodologist A6, referee B7 | tautological zero | tool control (neato, dot, ELK) and a second optimiser |
| H1 Wilcoxon against a constant | methodologist A7 | p = 2^-n by construction | test against the tool control |
| straight chords; parsers drop waypoints; anchors manufacture edges | referee B1, methodologist A8 | crossings, orthogonality, node-edge misstated; BPMN orthogonality suspect | evaluate on stored polylines; report waypoint fraction |
| no stress term | referee B2 | "not the energy tools minimise", refutable in one sentence | stress as second base energy |
| alignment definition is the author's | referee B5, methodologist A12 | fragile across A1/A3; A3's s equals the cap | HOLA gridiness R4 as primary, A1 to A3 as sensitivities |
| L from the hand layout's own median | methodologist A15, code D5 | T_L centred on the human by construction | declare; report L = 1/sqrt(N) and boundary-to-boundary lengths |
| held-out half reused for model choice | methodologist A10 | not held out after H4 | 5x2 cross-validation; selection inside training folds |
| exp() in A3, no -ffp-contract=off | code D6, D7 | byte reproducibility broken across platforms | exp_neg from the library; Makefile flags |
| RNG one stream per process | code D3 | a graph's result depends on its neighbours in the input | per-instance seed |
| WP5037, WP3391 are Reactome-derived | referee B8 | corpora not independent | drop, state the count |
| SBGN parser keeps process nodes | referee B6 | m/n 0.96 is a bipartite process graph | say so; report entity-only as sensitivity |

## 3. What to add, ranked by information per hour

1. Directional test as the primary instrument (done as a prototype, scratch dirtest.c;
   to be rebuilt in example/diagrams/ on the library). Per node, 16 directions at radii
   {grid step, 0.005, 0.01, 0.02, 0.05}; per term decrease recorded; q_d per energy; the
   LP residual over the simplex from the same differences. Seconds per corpus.
2. Tool controls on every instance: neato (done for 60 per corpus), dot, ELK layered for
   BPMN. Same test, same terms. Calibrates every threshold.
3. Stress as a second base energy (shortest-path distances scaled by the median edge
   length), both as a term in the profile and as the energy for the neato control.
4. Polyline geometry: parsers keep waypoints, anchors and dockers; crossings,
   orthogonality and node-edge on the drawn route; report the fraction of edges with
   waypoints per corpus.
5. Half-grid jitter test: jitter every box uniformly by half the detected pitch, rerun the
   alignment cell. What survives is the person's.
6. Flow term (penalty on edges against reading direction) and containment (compartment,
   lane) as hard constraint: the domain criteria the referee and the methodologist both
   expect to beat alignment.
7. HOLA formative data as a fourth corpus: 17 designers x 8 graphs, coordinates in SVG,
   a 65-judge rank per layout; test whether better-ranked layouts are held more.
8. Per-node figures: which boxes are free, under which term, in which direction, by node
   class. One small multiple per corpus.
9. Cache the instance-by-energy matrix so cross-validation, bootstrap intervals on fitted
   weights and leave-one-term-out cost nothing more.
10. GD Contest manual submissions as a positive control (humans minimising crossings
    alone), if the files are downloadable.

## 4. Pre-registration amendments proposed

1. Primary estimand: q_d, the fraction of nodes held under the directional test at
   d = 0.02 with 16 directions, reported per term and per declared energy. Climber-based
   rho_d and delta_d secondary, with the climber's step declared as a fraction of the cap.
2. Stationarity reference and controls: converged layout (must exceed 0.95), neato and dot
   layouts of the same graph (the null distribution for the tests), uniform in-cap sampling
   at matched budget through cjitter_compare.
3. Energies declared: each term alone; crossings + overlap; crossings + overlap + length;
   stress; each of the candidate terms added to crossings + overlap. Weights by the LP
   residual on training folds, 5x2 cross-validation.
4. Hypotheses. H1: q_0.02 under crossings + overlap exceeds 0.9 on the median hand layout
   in every corpus and exceeds the neato control (Wilcoxon, Holm over 3). H2: q_0.02 under
   length alone is below 0.2 in every corpus and below the neato control. H3: adding length
   at any positive weight to crossings + overlap drops q_0.02 below 0.2 (the LP gives it
   weight zero). H4, directional: alignment (gridiness R4 primary) holds more hand-placed
   boxes than orthogonality or node-edge separation in every corpus, and more than in the
   tool control; declared fragile under the half-grid jitter for BPMN.
5. Families: F1 = H1 over 3 corpora; F2 = H2, H3 over 3 corpora; H4 descriptive with
   bootstrap intervals. All at d = 0.02; other caps and A1 to A3 as sensitivities without
   tests. Unit of inference the diagram; seeds averaged within instance.
6. Corpus: drop WP5037 and WP3391; deduplicate by model identity; report size
   distributions and a 41 to 100 node sensitivity.
7. One binary, one commit, for reference, control, fit and test.

## 5. Reuse of the library (review/code.md in full)

example/diagrams/ on cjitter: energy.c with one function per term and alignment by enum,
corpus.c reader with the inclusion rule and rescale, station.c driving the directional
test, the descent, the references and the control, CSV out; fit.py and analyse.py over
the CSVs. Library additions: `start` in cjitter_problem (~15 lines), cjitter_compare_raw
(~50), public cjitter_sign_p and cjitter_holm (~5), a method mask on compare (~10). The
climber maps as block = 2, box = x0 +- d per coordinate, repair = disc projection, patience
and step declared. Incremental energy evaluation (one moved node, ~12x) as a two-state
cache inside the fitness; exp_neg instead of exp. Thirteen tests, all under a second,
pinned in make check; the full panel (about 13 minutes) and the fit run by hand and are
committed under data/results/.

## 6. Order of work

1. example/diagrams/ skeleton on the library, directional test first, tests 1, 2, 5, 9,
   11 from review/code.md. Pin the 60-graph numbers above as the fixture.
2. Polyline parsers and the waypoint fraction; rerun the profile.
3. Stress; neato and dot controls on every instance; ELK on BPMN.
4. Half-grid jitter; flow and containment terms; HOLA corpus.
5. Sign the amended pre-registration; freeze; run; write the measurements section.
