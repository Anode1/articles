# Approved to run 2026-08-25: Vasili instructed "go ahead" in session. Nothing below changed after approval.

# Pre-registration: the paired audit of the metaphor benchmark

The question: of the 296 metaphor-library implementations in Vermetten, Doerr, Wang,
Kononova and Bäck (GECCO 2024, DOI 10.1145/3638529.3654122), how many are shown better
than random search by an exact paired test at the benchmark's own budgets, how many are
not shown better, and how many are shown worse. The benchmark's own paper ranks by
anytime AOCC and contains no paired test; the word "test" occurs once, in a reference
title, and none of its 21 citing papers adds one. The audit is of the benchmark's own
data against its own baseline, not of the algorithms in general.

## Disclosure of what has been seen

A pilot on 2026-08-25 computed exploratory counts against the release's RandomSearch
only: 65 to 100 of 296 not shown better at the top budget by dimension, 227 of 296 in
2D at the smallest, with Holm at 5% per (dimension, budget) family. Those numbers were
seen before this document was written. What the confirmatory run adds and the pilot did
not touch: the uniform control, the recomputation through the C instrument, the
secondary estimands, and every decision rule below, which the pilot forced but did not
freeze. No verdict of the confirmatory run is known.

## Data

Zenodo 10.5281/zenodo.10561215, CC-BY 4.0, fetched 2026-08-25; provenance and local
layout in metaphors/PROVENANCE.md. The unit of audit is the implementation, a
(library, algname) pair: 308 in the release, 12 baselines and 296 others across
EVOLOPY, NIAPY, OPYTIMIZER and mealpy. Base*/Original* variants of one metaphor are
distinct implementations and both count; the same name in two libraries is two
implementations. Reconciling our 296 against the paper's 282 is a reporting item, not a
selection step.

Per implementation and dimension d in {2, 5, 10, 20}: 24 BBOB functions, instances 1 to
10, 5 runs, best-so-far error at budgets b x d for b in {10, 50, 100, 500, 1000, 5000,
10000}. A complete (dimension, budget) cell is 1200 runs. 18 implementations have
incomplete panels (19 to 1186 pairs), consistent with the release Readme's warning
about split raw folders.

## The two controls

1. Their own: the release's Baselines:RandomSearch, nevergrad over
   `Array.set_bounds(-5, 5)`. This samples a Gaussian through nevergrad's bound
   transform, not uniformly on the box; `benchmark_baselines.py` in the release shows
   the construction.
2. Uniform on the box: cjitter's `random` method on the BBOB functions through
   coco-experiment's C evaluator, same functions, instances, dimensions and budget
   grid, 5 runs per instance, seeds declared in the driver. This is the control the
   library's own verdict column uses.

Every implementation is judged against both. Disagreement between the two verdicts is a
secondary estimand, not a nuisance: it measures how much the benchmark's baseline
choice moves its own conclusion, and it bounds the Kudela centre-bias effect
(arXiv:2301.01984) from the control's side.

## Pairing and test

Pairs are (function, instance, run): the collection scripts seed `np.random.seed(run)`
per repetition, so run indices are fixed labels; pairing by them is arbitrary but
declared here, and exchangeable under the null of equal distributions per instance.
Wins are strict (error strictly below the control's); ties count for neither side and
leave n, the cjitter convention. Per (implementation, dimension, budget): the exact
one-sided sign test in the better direction and in the worse direction,
`cjitter_sign_p` both. Holm across the 296 implementations within each (dimension,
budget), separately per direction and per control, `cjitter_holm`. Verdict at 5% after
correction: better, worse, or not shown. "Not shown" is a failure to demonstrate and is
never read as equality.

## Estimands

Primary, per control, per (dimension, budget): the count of the 296 shown better, not
shown, and shown worse. The headline is the top-budget row, 10000 x d evaluations.

Secondary, all descriptive or tested as stated:
1. Verdict disagreement between the two controls: the count of implementations whose
   verdict changes, and the direction of each change.
2. Same-name cross-library disagreement at the top budget: names present in two or more
   libraries whose verdicts differ. The pilot saw SCA worse than random in OPYTIMIZER
   and better in mealpy; the estimand is the count of such names.
3. Effect size beside every verdict: the median over pairs of the error ratio
   implementation over control, no test attached.
4. Budget trend: the worse-than-random count by budget within each dimension. The pilot
   saw it rise with budget in 2D, 25 to 79.

## Decision rules, frozen before the run

- Budget factor 10 is descriptive only, excluded from every Holm family: below most
  initial population sizes the compared value is the shared-seed initial sample (many
  identical win counts in the pilot), and nevergrad's DE has zero pairs there.
- Incomplete panels stay in, tested on their available pairs, coverage printed beside
  the verdict. Sensitivity annex: the same tables on complete cells only. A cell with
  no pairs is printed as such, never as a verdict.
- RandomSearch is not tested against itself; the baselines are reported in the same
  tables but form their own Holm family of 11, so the metaphor count is never diluted
  by them.
- No deduplication, no exclusion for centre bias, no exclusion of any implementation
  for any property of its results.

## Outcome-neutral checks

The instrument fails, and the run stops for repair rather than reinterpretation, if any
of these does not hold at the top budget against their RandomSearch: DE, DiagonalCMA,
modcma, bipop and lshade shown better in every dimension; every sign p in [0, 1] and
none NaN; win counts symmetric (wins of A vs B plus losses plus ties = pairs).
The pilot's one anomaly is pre-declared for verification, not suppression: nevergrad's
PSO shown worse than random at 10D and 20D at every budget, 35 of 1200 wins at the 10D
top budget. Before the paper states it, the raw IOHprofiler logs in Raw.zip must
confirm the processed values for one (function, instance) cell of it.

## Instrument

Verdicts come from `cjitter_sign_p` and `cjitter_holm` through a C driver reading a
flat text export of the condensed table, compiled with the shipped Makefile flags. The
2026-08-25 fix making `cjitter_sign_p` safe past 1028 pairs (scaled sum, pure
arithmetic, pinned against exact rational references) must be merged first. The Python
pilot stays in the repository as the cross-check; both must agree to every printed
digit on every confirmatory number.

## Threats stated in advance

- BBOB shifts and rotates its instances; algorithms with centre bias lose there for a
  published reason (Kudela). The audit therefore claims "not shown better than random
  sampling on this benchmark at these budgets", never "worthless".
- The five runs per instance share numpy seeds across implementations within a library
  script, so panels of different implementations are correlated; Holm controls the
  family-wise rate under arbitrary dependence, and no estimand pools across
  implementations.
- The processed release, not Raw.zip, is the source; the split-folder warning means
  some incompleteness is a release artifact. Coverage is reported per cell.
- fx semantics (best-so-far error at budget, lower better) are taken from the release's
  processing scripts; one cell is re-derived from Raw.zip as a check before the run.

## Addendum, 2026-08-25, after independent review

Four independent referees (review/audit/) reviewed the confirmatory draft. Analysis
changes made in response, all additive and all disclosed as post-hoc:

1. The two-directional rule: 5% per direction holds each directional family at 5% and
   the pair at no worse than 10%. The 2.5%-per-direction tables are computed and
   reported beside the primary; 27 of 7,104 verdicts differ.
2. Robustness annexes added, none pre-registered: cluster-level sign test on
   per-(function, instance) medians; the same audit on the release's per-run AOCC;
   paired Wilcoxon; the 282-implementation family named by the release's own
   aggregate; per-function verdict counts. All in example/metaphors/robustness.py.
3. Corrections of prose against the shipped tables (trend shape, baseline win-rate
   range, effect-size tail, the audited paper's own fixed-budget section and counts).
   No pre-registered estimand, rule, or table changed.
