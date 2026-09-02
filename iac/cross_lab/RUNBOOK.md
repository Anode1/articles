# Runbook

State of the experiment and how a fresh agent instance continues it.
Design: [README.md](README.md). Population: [harvest/](harvest/README.md).

## Done

- Design committed; prior work and the pre-registered criterion are in
  README.md.
- Shakedown of three Claude seats on one iac board passed
  ([shakedown/](shakedown/NOTES.md)): 3 of 3 correct, wakeups under 3 s,
  per-seat dollar metering from `claude -p --output-format json`, $0.42 total.
- Residual set harvested and frozen: 37 instances of SWE-bench Verified that
  the best Claude-, GPT- and Gemini-based submissions all fail.
- The screen is done. One sonnet attempt per instance ($18.60 total,
  `run/screen.sh` to generate, `run/eval_batched.sh` to score on a
  space-limited disk) resolved 19 of the 37 instances the 2025 leaderboard's
  best all failed. `runs/screen.tsv` holds the verdicts; the 18 unresolved
  instances are the experiment's population. A survivor of one attempt may
  still fall to repeats or a stronger model; the SOLO arm exists to settle
  that at matched dollars.

## Conventions

- `~/iac` carries code only; all research for this experiment lives here,
  `~/articles/iac/cross_lab`, a subproject of the articles repo like cjitter.
- Commits in the articles repo name only cross_lab paths (other agents work in
  this tree); push only when Vas says.
- Prose follows `~/articles/STYLE.md`; match `cjitter/README.md`.

## Storage

- `~/articles/iac/cross_lab` (NVMe, git): everything reproduction of the
  article needs: harvest, briefs, patches, run metadata, room logs.
- `~/.local/share/cross_lab` (NVMe): everything a run needs while it
  runs: the swebench venv, harness logs (`evals/`), per-seat streams
  (`streams/`), orchestrator logs (`logs/`). Docker and containerd stay at
  their defaults on the root disk; images are retired per group to fit.
- `/media/vas/kuldata/iac` (USB2 enclosure, ~700G), symlinked as
  `~/articles/iac/external_data`: archive only, synced from the local
  tree when a phase ends. The link drops on its own; a run must never
  depend on it (it did once and stalled). The three kul directories
  beside it (`data`, `data2`, `staging`) belong to another project:
  never touch.
- `/tmp` scratch: seat workdirs (`CROSS_LAB_WORK` in `run/run_solo.sh`),
  disposable; seat crash reports go to `/tmp/cross_lab_apport`.

## Running a SOLO attempt

    run/run_solo.sh <instance_id> <model> [max_turns]

Scratch clone of the repo at `base_commit`; the seat sees the problem
statement and the tree, never `FAIL_TO_PASS`, `PASS_TO_PASS`, or the test
patch. The patch, cost and metadata land in `runs/solo/<id>/<stamp>/`.
Patches accumulate unscored until an evaluation path exists (below).

## Board arms (HOMO, HETERO)

Reuse the shakedown launch pattern: one iac room per run, `IAC_FROM` set in
each seat's launch environment, the brief in a file in the room, exact send
commands stated in the brief, loop exits written as commands to run, not
conditions to judge (a seat burned 5 idle minutes on an interpreted
condition). Runner script not yet written; model it on `run/run_solo.sh` plus
`shakedown/BRIEF.md`.

- Board pilot (`run/run_board.sh`, three sonnet seats, django__django-11141,
  $2.11): protocol held end to end: independent diagnoses posted before
  reading, a claim conflict negotiated, work split fix/tests/docs, and the
  collective patch scores RESOLVED on an instance the solo screen failed.
  Not a comparison: budgets were unmatched and pilots are excluded by design.
  Lessons: board seats need max-turns well above 40 (recv polling eats
  turns), and seats sometimes recall the upstream fix from training data;
  the contamination is symmetric across arms but must be stated as a
  limitation of any absolute claim.

## Evaluation

Docker is installed (defaults, root disk), and the dataset name that works
with swebench 5.0.2 is `SWE-bench/SWE-bench_Verified` (prebuilt
per-instance images; the old `princeton-nlp/` name lacks the `image` field
and fails). One patch, from the venv at `~/.local/share/cross_lab/venv`:

    sg docker -c "$VENV/bin/python -m swebench.harness.run_evaluation \
      --dataset_name SWE-bench/SWE-bench_Verified \
      --predictions_path preds.jsonl --run_id <id> --max_workers 2"

`preds.jsonl` rows: `{"instance_id", "model_name_or_path", "model_patch"}`.
Verdicts (`report.json`) are copied beside the run in `runs/solo/`.

## Blocked, and on what

- HETERO: metered OpenAI and xAI API keys (not subscriptions; dollar-matched
  arms need metered billing).
- Owner decisions still open: spend cap, repeat count.
- Seats currently run unsandboxed on the host with Bash allowed; acceptable
  for pilots, containers once docker exists.
