# Harvest: the residual set

    benchmark  SWE-bench Verified, 500 instances, executable ground truth
    record     github.com/swe-bench/experiments, evaluation/verified,
               134 submissions, frozen 2026-08-31
    rule       residual = failed by the best-scoring submission built on
               each lineup lab's model
    result     37 of 500

Best per lab at the freeze:

    anthropic  20251215_livesweagent_claude-opus-4-5       396/500
    openai     20251015_Prometheus_v1.2.1_gpt5             372/500
    google     20251120_livesweagent_gemini-3-pro-preview  387/500

Across all 134 submissions no instance is unresolved by everyone (9 are
resolved exactly once), so "resolved by nobody" harvests an empty set; the
per-lab rule is the operative one.

The leaderboard only nominates candidates. A submission's failure is scaffold
plus model, not the model's ceiling, so the SOLO arm re-establishes solo
failure under our own harness at matched dollars before any HETERO gain is
claimed. xAI has no submission in the record; a Grok seat enters with no
leaderboard prior.

`harvest.py` reproduces the computation. `residual.json` is its frozen output.
`tasks.json` carries the 37 task rows: problem statement, repo, base commit,
and the held-out test names. Seats must never see `FAIL_TO_PASS`,
`PASS_TO_PASS`, or the test patch.
