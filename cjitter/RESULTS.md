# The pre-registered sweep: results

Run 2026-08-15 against cjitter frozen at 942e713, per PREREGISTRATION.md and its addenda.
Raw per-seed data in `data/results.csv`, extraction and analysis code beside it; the per-pair
geometry headers carry real table names and stay out of every repository, as the provenance
rules require. Of 16 consecutive ERD.mwb pairs, 7 added no tables (doc edits, re-layouts)
and pair 16 was the pilot, leaving n = 8. One validity note recorded before analysis:
matching is by table name, so pair 14 ("refactoring and renaming") may count renames as
additions. The pre-registered low-displacement subset (median context move at most 20) is
empty; the smallest realized displacement is 36.

## The declared verdicts

**Primary, ga versus centroid: success.** The GA beats the centroid heuristic on 8 of 8
migrations; exact Wilcoxon p = 0.0078, Holm-corrected 0.023, Hodges-Lehmann shift -72287
[-150515, -20728], rank-biserial +1.0. climb versus centroid reads the same (Holm 0.023,
HL -75495). The Friedman omnibus over the four methods rejects at p = 0.00045, so the
pairwise family carries its weight.

**The refutation clause fired for the GA.** ga versus random: 6 wins of 8, exact Wilcoxon
p = 0.109, HL +337 [-257, +1826], MDE 1479. At budget 8000 on these migrations the GA did
not demonstrate separation from uniform sampling. The per-pair table says why: half the
migrations add one or two tables, and at k <= 2 every method including random reaches the
same optimum to five digits; trivial instances cannot discriminate. The separation-budget
table repeats it: on pair 3 nothing separates at any budget tried.

**The author's prediction: refuted by its own experiment.** Declared in Addendum 1 before
the sweep: the GA would be the most efficient search. Measured: climb beats the GA on every
non-tied migration (7 of 7, exact p = 0.0156, Holm 0.031, rank-biserial -1.0), and the
Friedman mean ranks order climb 1.44, anneal 2.19, ga 2.69, random 3.69. Hill climbing is
the efficient method on this benchmark. The pilot pair (k = 10, excluded) had pointed the
other way, GA first, which yields the successor hypothesis rather than a rescue:
recombination's advantage, if real, appears at larger k, where there are more modules to
recombine. That is a new pre-registration, not a footnote to this one.

## The declared secondaries

- Separation budgets B* (five-seed sign test against random at the same budget; the test
  reaches 5% only on a 5-for-0 sweep, so B* detects sweeps and nothing weaker): climb
  separates on 7 of 8 pairs, anneal 6, ga 5. Medians with the never-separating pairs ranked
  above every finite budget: climb 2000, anneal 5000, ga 20000; over finite entries only:
  2000, 1250, 2000. The first convention is the table's, disclosed after a reviewer found
  the second silently flattering the method that most often never separates.
- McNemar, ga versus centroid on reaching zero routed penetration: discordant 2 versus 0 in
  the GA's favor, exact p = 0.50; the binary is underpowered at n = 8.
- Bootstrap 95% intervals on the across-pair median at 8000: random 18424 [15256, 44749],
  climb 16139 [14778, 33653], anneal 16466 [15246, 30985], ga 16598 [15242, 45277].
- Variance components at 8000: within-pair seed spread is tiny against across-pair spread
  (climb 27 versus 14666), so the instances, not the seeds, carry the uncertainty, and the
  five-seed panel is adequate for the per-pair medians.
- Router calibration per pair ranged from 2 to 13 crossings and 0 to 552 penetration against
  the human layouts' certified zeros; on three pairs the routed penetration is exactly zero.

## What this changes

The paper's claim order inverts from the pilot's suggestion: the story is not "the GA wins"
but "the control and the pre-registration did their job": the search family beats the
deployed-style heuristic decisively on real migrations, hill climbing is the budget-
efficient method at realistic migration sizes, the GA's pilot advantage did not survive
contact with the benchmark it was predicted on, and half of real migrations are too small to
need anything beyond sampling, which is itself a deployable observation: check k before
reaching for a search.

## Exploratory, post-hoc, author-prompted

climb versus anneal, asked after the results were seen and labeled accordingly: exact
Wilcoxon p = 0.578, Hodges-Lehmann +11 [-1334, +726], MDE 1326. No difference is
demonstrated, and none larger than about 1300 score units (a tenth of the primary effect)
could have hidden at this n. Corrected after the statistician's review: the supportable
ordering is climb and anneal indistinguishable from each other, climb directionally ahead
of the GA (with the dust-pair sensitivity the paper states), and anneal versus GA not
shown (declared test p = 0.297). The GA did not separate from random at these migration
sizes; the paper's Section 7 carries the full 6/1/1 decomposition, with the loss on the
rename-flagged pair carrying the verdict. The locality half of the pre-registered
prediction survived; the recombination half did not.
