# Pre-registration: the 16-pair incremental layout experiment

Written 2026-08-15, before any pair beyond the shipped example has been extracted or scored.
The shipped example (the latest migration pair, in cjitter's README) served as the pilot and
its numbers will not enter the primary analysis. This file follows bpnn's lesson 7: the
primary comparison, the margin and what would refute it, timestamped before the pilot's
successor runs. Anything not named here is exploratory and will be labeled so.

## Two decisions taken here, flagged for the record

1. **The context freezes at the PREVIOUS revision's coordinates.** The task per pair: the
   previous diagram stands as drawn; the tables the migration added are placed. The human's
   reference placement is those tables' coordinates in the NEXT revision. The known
   imperfection: between revisions the human sometimes also moved context tables, so their
   reference answer was made in a slightly different context than the frozen one the methods
   see. This is accepted and reported per pair as the context displacement (median move of
   surviving tables); a secondary analysis restricted to low-displacement pairs is
   pre-registered below.

2. **The primary outcome is the routed objective score**, the quantity the methods optimize:
   penetration and crossings of orthogonally routed connectors at weight 100, connector
   length at 1, computed by the shipped router at the commit named in the results. The
   feasibility pair (crossings, penetration) and the router's per-pair calibration against
   the human layout are reported beside it, never as the test statistic.

## Design

- Units: the consecutive before/after pairs of `doc/DataModel/ERD.mwb` in the kul repository
  git history, excluding the shipped pilot pair. Expected n = 15; the exact n will be
  whatever the extraction yields and will be stated with reasons for any exclusion
  (unparseable revision, no tables added).
- Per pair, per method: cjitter at the shipped defaults, evaluations 8000, seeds 5, jitter
  0.25, pop 30, default tuning; the per-pair method value is the median over the 5 seeds.
- Arms: ga, climb, anneal, uniform random (matched budget), the centroid heuristic
  (0 evaluations), and the human reference.
- The router is frozen at the commit named in the results before the first non-pilot pair is
  scored. Its calibration (crossings, penetration on the human's full layout) is recorded per
  pair. No pair is excluded for poor calibration; the calibration column is the caveat.

## Primary comparison

**ga versus the centroid heuristic**, paired across pairs, on the primary outcome. Test:
exact Wilcoxon signed-rank via bpnn's pairstat, two-sided, alpha 0.05. Family for Holm
correction, declared now: (1) ga vs centroid, (2) ga vs random, (3) climb vs centroid.
Everything else is exploratory.

- Success: ga beats centroid, Holm-corrected p <= 0.05.
- Refutation: ga fails to separate from RANDOM (comparison 2 not significant in ga's favor,
  or significant against it). Then the conclusion is that at this budget the search
  adds nothing over sampling, and the paper says so.
- Equivalence: if comparison 1 is not significant, the result is reported as "not shown"
  with pairstat's minimum detectable effect, never as equivalence.

## Secondary, pre-registered

- The same three comparisons on the feasibility pair, crossings first, penetration breaking
  ties (a strict lexicographic order; ties after both are ties).
- The low-displacement subset: pairs whose median context displacement is at most 20 units.
- The human reference column, reported with the calibration caveat and never tested against:
  the human's on-screen achievement (0 crossings, 0 penetration) is not reproducible by the
  current router, so score comparisons against the human measure the router as much as the
  layout.

## What is fixed before running

cjitter commit hash, router included; the extraction pipeline (gen_data.py per pair); this
file. The seeds are the shipped panel (base 1, stride 7919). Nothing here changes after the
first non-pilot pair is scored; if something must change, the change and its reason are
appended below with a date, and the analysis reports both versions.

## Addendum, 2026-08-15: a directional prediction, recorded before the sweep

The author predicts the GA is the most efficient of the three searches on incremental
placement. This is a feeling, and it is being written down so it can be scored either way.
Added to the pre-registered secondary family: ga vs climb and ga vs anneal, paired across
pairs on the primary outcome, exact Wilcoxon signed-rank, Holm within this pair of
comparisons; and the separation budget B* per method (smallest budget whose sign test
against the control reaches 5% on the shared panel) as the efficiency curve, at budgets
500, 2000, 8000 and 32000. For the record, the pilot's shipped tables have the GA at the
best median in all three (labels, and both edge models of the ERD pair), which is
consistent with the prediction and proves nothing at one budget on one instance.
