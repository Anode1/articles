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

## The block arm (2026-08-19, exploratory, not pre-registered)

Run after everything above was known, so the p-values are descriptive. Raw data in
`data/block_results.csv`, code in `data/sweep_block.c`, `data/run_sweep_block.sh` and
`data/block_analysis.py`; the paper carries it as Section 4.6.

Every method above perturbs all 2k variables per proposal. cjitter 0.10.0 adds
`cjitter_tuning.block`, the number of variables one proposal moves, defaulting to the whole
vector. Block 2 moves one table.

**The reproduction that licenses the comparison.** Re-running the whole pre-registered sweep
on the block-carrying harness with the block at its default reproduces all 640 per-seed
values of `results.csv` exactly. The two arms differ in the parameter and in nothing else.

**Power first.** Three of the eight pairs add one table, where 2k = 2 and block 2 *is* the
whole vector: identical by construction, so only five pairs can differ. At n = 5 the exact
two-sided Wilcoxon floor is 0.0625, so nothing here can reach 0.05 two-sided.

- climb improves on 5 of 5 affected pairs, exact two-sided p = 0.0625 (the floor), HL -436.
- anneal 4 of 5 (p = 0.31), ga 4 of 5 (p = 0.125).
- B* does not clearly improve: climb's median stays 2000, three pairs falling, one rising.
- **ga versus random moves from p = 0.109 to p = 0.0156**, by flipping exactly pair 14, the
  instance the appendix's leave-one-out already named as the hinge (45277 -> 34208 against
  the control's 44749). The pre-registered verdict stands as recorded; what the block shows
  is that it was a verdict about a method family at one proposal shape.

**Where it is not marginal**, quoted as illustration and not as evidence, both outside the
pre-registered eight: the 90-rectangle packing example goes from climb 12.8 / anneal 128 /
ga 1.38 to *exactly 0 on all seven seeds for all three*, a clean layout no method reaches at
any budget tried with whole-vector proposals; and on the shipped k = 10 instance climb's
median falls 46134 -> 32293 with its five-seed range falling 18662 -> 178.

**The hypothesis, declared not concluded.** Incremental placement is a sum over weakly
coupled objects (in the shipped instance no edge joins two added tables at all), so a
whole-vector proposal that seats one object well and another badly is rejected for the
second: acceptance on that instance is 47 of 8000 at whole vector against 124 at block 2. If
so the block's value grows with the number of such objects, which puts this benchmark's
k <= 5 instances at the bottom of the range. Testing it needs larger k than this schema
supplies. Margins here run 0.01 to 8.5 percent and do not order by k within that range.
