# DRAFT AWAITING APPROVAL. Nothing here runs until Vasili signs and dates it.

# Pre-registration 2A: recombination, modularity, and the rotation test

The successor to PREREGISTRATION.md, drafted from the applied advisor's memo of 2026-08-16.
The refuted prediction of experiment one, that the GA is the most efficient search, survives
as a mechanism hypothesis: recombination pays when there are enough modules to recombine.
The pilot pair (k = 10, GA first) suggested it; the sweep (k <= 5, climb first) could not
test it. This experiment puts k and modularity under control and adds the rotation test that
separates "recombination works" from "the problem is modular."

## Instrument fixes carried from experiment one

- n is derived, not inherited: 12 instances per factorial cell, so confirmatory strata carry
  n = 24 to 36 non-trivial instances; the McNemar binary becomes live.
- k is a factor: k in {2, 4, 8, 16, 32}; k = 2 is descriptive-only, a replication of the
  count-the-nodes rule, never in a Holm family.
- Triviality screen from control-only runs, decided before any method comparison is seen:
  an instance is confirmatory only if random at the top budget misses the reference optimum
  on at least 20 percent of seeds. Every pre-registered subset must be shown non-empty on a
  screening pass that sees no method comparisons.
- Matching by object id, not name: .mwb objects carry persistent ids across revisions;
  renames stop counting as additions. Pair 14 of experiment one is re-run under id-matching
  as a robustness note.
- Seeds: 15 per (instance, arm, budget); the exact binomial threshold becomes 12 of 15
  (p = 0.0176), so B* tolerates three lucky control seeds instead of zero. Budget grid
  500 x 2^i up to 32000 (128000 for k = 32 only). B* reported with censoring stated, never
  coerced. Per-run reseeding from a hash of (instance, seed index, method).

## Instances

- Synthetic migrations (confirmatory): real frozen contexts (the remaining kul revisions,
  plus the anonymized shipped pair) with synthesized additions: k tables whose FK edges are
  wired CLUSTERED (each new table's FKs within one neighborhood of the frozen diagram) or
  UNIFORM (FKs uniform over frozen tables). Third factor ROTATION: identity versus one
  fixed orthogonal rotation of the 2k variables inside the fitness. Factorial
  k x {clustered, uniform} x {rotated, not}, 12 instances per cell, generator seed declared.
- Mined real pairs (secondary, external validity): public GitHub .mwb files under declared
  inclusion rules (parses; diagram whose FK links resolve; additions by object id; k >= 3;
  base layout plausibly human; license permits geometry-only extraction). Target 20 to 40
  pairs; the k distribution is reported, never selected on.
- Second domain: labels (rectangles, minimum overlap), same arms, matched budget, so the
  operator claim crosses domains. Exploratory annex, gating nothing: the network-weights
  domain, one unit's weight block versus independent weights, the SMBPANN grouped-mutation
  claim finally run against a control.

## Arms, six, sealed

random (control), climb, anneal, ga, label2001 (the resurrected per-label climber: pick a
block, jitter it, keep if the total falls), fused (the SMBPANN hybrid: GA whose mutation
carries an annealing schedule).

## Declared families, Holm within each

- F1, primary: ga versus climb at k >= 16, clustered, unrotated, exact Wilcoxon signed-rank
  on per-instance seed medians; and the mechanism statistic, exact Wilcoxon on the
  per-instance interaction (ga - climb) rotated minus unrotated. Holm across these two.
  Refutation: ga fails to beat climb at k = 32 clustered at the top budget; then the
  recombination hypothesis is dead and the paper says so at the same prominence.
- F2, hybrid: fused versus climb AND fused versus anneal; the hybrid claim requires beating
  both parents. Holm within the pair.
- F3, heritage: label2001 versus climb with a declared equivalence margin of one tenth of
  experiment one's primary shift; equivalence is a bounded claim, never an accepted null.
- Solve counts by exact McNemar wherever the screen shows the binary is live (reaching the
  reference optimum on synthetics; zero routed penetration on migrations).
- Friedman omnibus gates each six-arm family; Hodges-Lehmann with distribution-free
  intervals; MDE beside every null; per-seed data and code frozen at a commit.

## The author's prediction, to be recorded at approval time

Vasili records a directional prediction before the first non-pilot run, with all four cells
of the (GA-lead returns at k >= 16) x (lead vanishes under rotation) outcome table
interpreted in advance. Suggested wording exists in the advisor memo; the words must be his.

## Venue intent

Paper one to arXiv (cs.CG, cross-list cs.NE) and JGAA; this experiment aimed at the
evolutionary-computation audience (GECCO 2027 or IEEE TEVC), the operator question stated
as domain-general with placement and labels as the two instrumented domains.
