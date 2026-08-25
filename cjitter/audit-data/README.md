# The audit's verdict tables

Output of the confirmatory run of 2026-08-25 under `../PREREGISTRATION-AUDIT.md`,
computed by `example/metaphors/audit.c` in the cjitter repository from the GECCO 2024
benchmark's own release (Zenodo 10.5281/zenodo.10561215).

- `verdicts_uniform.tsv`: one row per (implementation, dimension, budget factor)
  against the uniform-on-the-box control: wins, losses, pairs, exact sign p both
  directions, Holm-corrected values, verdict. 8,624 rows.
- `verdicts_rs.tsv`: the same against the release's own RandomSearch.
- `summary_uniform.txt`, `summary_rs.txt`: the better / not shown / worse counts per
  (dimension, budget) over the 296 non-baseline implementations.
- `effect_top_budget.tsv`: median over pairs of the error ratio implementation over
  uniform control at the top budget, descriptive.
- `robust_set.txt`: the 102 implementations shown better than uniform sampling in
  every confirmatory (dimension, budget) cell.
- `robustness.txt`: the post-review annexes (2.5% rule, the 282 family, cluster-level,
  per-function, AOCC, Wilcoxon, effect facts, baseline win ranges), the output of
  `example/metaphors/robustness.py`.

Everything regenerates from the Zenodo release and the cjitter repository alone: the
pipeline is `example/metaphors/README.md` there, and the uniform control is
deterministic from the seed rule declared in `uniform.c`.
