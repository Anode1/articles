# DRAFT AWAITING APPROVAL. Nothing here runs until Vasili signs and dates it.

# Pre-registration 2B: the noise ceiling on cheap stochastic search

The alternative successor, drafted from the methods advisor's memo of 2026-08-16. It unifies
two of Vasili's lines: resolution.tex measured the noise floors of NAS benchmarks (the ratio
r = sigma_W / sigma_B); this experiment measures at what r a search fed noisy evaluations
stops beating matched-budget sampling, and draws the measured NAS r-values as vertical lines
through the resulting curves. The refuted GA prediction feeds a second directional
prediction: recombination's known theoretical advantage is noise robustness (a population
implicitly averages), so the sigma = 0 ordering climb over ga may invert as r grows.

## Freeze

One cjitter commit adding a noise wrapper on the objective: noise enters only the feedback
the search sees; every reported final score is noiseless. Methods run exactly as shipped,
because the question is whether the methods as people run them survive noise. Freeze the
commit, the sigma_B table, the calibration thresholds, and this file before the first
non-pilot run. The 64-bit generator is mandatory at this draw volume.

## Instances (7)

Sphere d = 20 (known optimum); one deceptive trap; number partitioning through random keys;
and the four k >= 3 real migrations from experiment one's frozen set, declared by k, the
k <= 2 pairs excluded now for the reason already on record. The pilot pair stays out.

## Noise model

Additive Gaussian, iid per evaluation, sigma expressed only as r = sigma / sigma_B, where
sigma_B is the SD of the noiseless objective over 10^6 uniform box draws, seeded, frozen
pre-sweep. Grid r in {0, 0.03, 0.1, 0.3, 0.6, 1.0, 1.6, 2.6}. Declared secondary noise
model: the NB101 mixture (99 percent N(0, sigma_0^2), 1 percent N(0, (10 sigma_0)^2))
rescaled to the Gaussian cell's total variance at r = 1.0.

## Anchor cells (confirmatory)

Four r-values computed from resolution.tex's own sigma_W and sigma_B estimates and frozen
in a table before the sweep: NB201-C10 full set; NB201-C10 top-1000; NB101-C10 top-1000;
NB101 4-epoch full set (the coin-flip regime). Hypothesis tests live only at these four
columns; the rest of the grid is estimation.

## Arms, budgets, panel

climb, anneal, ga, the grouped per-block climber, random as control. Budgets
{500, 2000, 8000, 32000}, primary at 8000. Replicates within instance: N = 200 seeds per
method at the primary cell, 50 at other anchors, 25 on the descriptive grid; re-seeding per
(instance, replicate, method) from an indexed hash; calibration seeds a disjoint block.

## Declared comparisons

- Primary: climb (experiment one's named winner, pre-named) versus random, sphere d = 20,
  highest anchored r, budget 8000, noiseless final score, exact Wilcoxon signed-rank,
  two-sided alpha 0.05. Holm family of four: the same comparison at the four anchors.
- Secondary families, Holm within each: (i) ga versus climb at the four anchors, the
  inversion prediction; (ii) solve counts by exact McNemar, solved defined as reaching the
  5th percentile of a 1000-seed noiseless random-search panel at the same budget, threshold
  frozen pre-sweep, climb versus random per anchor; (iii) the real-migration replications;
  (iv) mixture versus Gaussian at equal variance, per method.
- Descriptive, no p-values: the sigma*(method, budget) curves; B* per r; the r-invariance
  collapse check across instances, which is what any NAS extrapolation stands on.

## Predictions, in tension by design

P1: at r >= 1.0 no method separates from random at budget 8000. P2: the sigma = 0 ordering
climb over ga inverts by r = 1.0. They cannot both survive intact, and this file says so.
The words of the recorded predictions must be Vasili's, added at approval time.

## Refutation and the estimand guard

If any search separates from random in its favor at the NAS coin-flip anchor, the headline
is refuted and the surviving margin is the finding. Sigma* is defined on the win-probability
scale (the r where per-replicate win probability against random crosses 0.75), estimated by
isotonic regression with a seeded bootstrap interval, never as the first non-significant
grid cell; every negative verdict carries TOST equivalence (margin 0.10 on the
win-probability scale) or the MDE. MDE arithmetic at N = 200: the sign test detects win
probability 0.60 at about 79 percent power; N = 50 cells detect about 0.70. Total compute
about 3 x 10^8 evaluations, CPU only.
