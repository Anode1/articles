# Pre-registration: are human-authored diagram layouts stationary points of the
# aesthetic energies used to draw them?

DRAFT, unsigned. Nothing below is scored until Vasili signs and dates it. Written 2026-08-22
after a pilot, and the pilot is declared in full in section 9 rather than hidden.

## 1. The question

Layout tools minimise a weighted sum of aesthetic criteria. If people drew that way, a
human-authored layout would sit at or near a local minimum of such an energy. We test that
directly on diagrams whose coordinates a person chose, and if it fails we ask whether any
reweighting of the criteria, or one further criterion, repairs it.

## 2. Corpora

Three, unrelated in domain, authoring tool and community. All redistributable.

- WikiPathways GPML, CC0, `data.wikipathways.org/current/gpml/`, Homo sapiens archive.
- Reactome SBGN-ML.
- BPMN Academic Initiative model collection.

Inclusion, applied before any scoring: the largest connected component has 15 to 40 nodes;
at least one edge; a positive bounding-box extent. Every layout is rescaled so its bounding
box fits the unit square, node sizes scaled with it. Container glyphs (SBGN compartments,
BPMN pools and lanes) are not nodes. Deduplicate by model identity so ortholog copies of the
same pathway do not inflate the count. The realised count per corpus is reported, not fixed
in advance.

## 3. The energy

E_w(x) = sum_k w_k T_k(x), weights on the simplex (non-negative, summing to 3).

Base terms, each normalised as stated:
- T_C crossings: straight-line segment crossings between edges that share no endpoint,
  divided by the edge count.
- T_L edge-length uniformity: mean of ((len - L)/L)^2, with L the human layout's median edge
  length on that instance.
- T_O node overlap: total overlap area of node boxes divided by total node area.

Candidate fourth terms, each tested by adding it to the base three:
- T_R orthogonality: mean over edges of min(|dx|,|dy|)/(|dx|+|dy|); zero when axis-aligned.
- T_A alignment, PRIMARY DEFINITION A3: for each node, 1/(1 + sum over other nodes of
  exp(-(dx/s)^2) + exp(-(dy/s)^2)) with s = 0.02, averaged over nodes. No nearest-neighbour
  argmin anywhere in it. A1 (distance to the nearest node sharing a row or a column) and A2
  (rows and columns priced separately) are reported as a declared sensitivity table, never as
  the primary. A3 is primary because it is the strictest of the three and the one least able
  to reward mere proximity in one axis.
- T_N node-edge separation: penalty for a node lying within (w+h)/4 of an edge it does not
  join.

## 4. Estimands

Let x be the human layout, d the displacement cap, and y*(d) the best feasible point a
capped descent reaches.

- PRIMARY, relative trust-region decrease:
  rho_d = [E(x) - E(y*(d))] / E(x), as a percentage.
  This is the standard stationarity measure for a non-smooth constrained objective; for
  smooth E it is proportional to d.||grad E||/E as d -> 0, and it is defined where the
  gradient is not, which the piecewise-constant crossings term requires.
- SECONDARY, step displacement:
  delta_d = mean over nodes of ||y*_i - x_i|| divided by d.
  Reported alongside rho_d always, and used as the objective for weight fitting (section 6),
  because rho_d is not invariant to reweighting: moving weight onto a locally irreducible
  term shrinks rho_d without changing how far from stationary the layout is. delta_d is.

Cap grid: d in {0.005, 0.01, 0.02, 0.05} of the drawing width. Primary cell d = 0.02.

## 5. The null, and the control

Both are mandatory and both are reported beside every headline number.

- STATIONARITY NULL. The same descent, same budget, same cap, started from a layout descended
  to convergence from the human. A genuinely stationary layout must return rho ~ 0 and
  delta ~ 0. A power check accompanies it: the same descent started from that converged
  optimum perturbed by d must recover most of the perturbation, or the null's zero is
  blindness rather than power.
- MATCHED-BUDGET RANDOM CONTROL. Uniform sampling at the same evaluation budget. The human
  layout must beat it, or "the human is not stationary" is uninteresting.

## 6. Weight fitting

Random search over log-uniform weights in [10^-2, 10^2], renormalised to the simplex
(Bergstra and Bengio). 200 draws. Fitted on a random half of each corpus and reported on the
held-out half; the held-out number is the one quoted. Seeds and the split are fixed before
the run. Fitting minimises delta_d for the reason in section 4.

## 7. Hypotheses and refutation

- H1. Human layouts are not stationary: rho_0.02 exceeds the stationarity null on a majority
  of instances in all three corpora. REFUTED if rho_0.02 fails to exceed the null in any one
  corpus, or if the null itself returns a non-trivial rho, which would mean the procedure and
  not the layout is producing the effect.
- H2. No reweighting of the base three repairs it: held-out delta_0.02 under fitted weights
  is not materially below the asserted (1,1,1) value. REFUTED if fitting drops held-out
  delta_0.02 by more than 20 points.
- H3, the primary claim. No additive model over the six terms is stationary at human
  layouts: held-out delta_0.02 under the best six-term fit stays above 25% in all three
  corpora. REFUTED if any corpus falls at or below 25%.
- H4, directional and secondary. Among the three candidate terms, alignment gives the largest
  single reduction, under all three of its definitions. This is the weakest claim here and is
  declared as directional only.

Author's recorded prediction, before scoring: H1 and H3 hold; H2 holds; H4 holds for A1 and
A3 but may fail on at least one corpus for A2.

## 8. Analysis

Per corpus, per cap. Across instances the paired comparison is the exact Wilcoxon signed-rank
test, with the exact sign test reported beside it, and Holm correction over the declared
family within each corpus. Effects are Hodges-Lehmann shifts with distribution-free intervals
and their realised coverage stated. Every null result carries an interval, never a bare "no
difference". Panel: descent seeds per instance fixed at 15, justified by the pilot's
within-instance spread and stated in the freeze; five is known to be too few to reach 0.05
within an instance except on a clean sweep.

## 9. The pilot, declared

A pilot ran 2026-08-21 on WikiPathways, Reactome and BPMN, at one seed, with alignment
definition A1 as primary and an energy-fraction estimand. It found rho rising from 7% to 55%
with the cap, a stationarity null of 0.00% with a power check of 81 to 98%, edge-length
uniformity taking weight zero in every fit, and alignment the strongest single addition in
all three corpora with the effect ranging from 34 points under A1 to under one point under A3
on Reactome. Those numbers are exploratory, are superseded by anything this pre-registration
produces, and are the reason A3 rather than A1 is primary here.

## 10. Deviations

Any departure from this file is recorded in it, dated, with the reason, before the affected
analysis is run. Numbers produced under a deviation are labelled as such in the paper.
