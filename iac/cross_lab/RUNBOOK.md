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

## Conventions

- `~/iac` carries code only; all research for this experiment lives here,
  `~/articles/iac/cross_lab`, a subproject of the articles repo like cjitter.
- Commits in the articles repo name only cross_lab paths (other agents work in
  this tree); push only when Vas says.
- Prose follows `~/articles/STYLE.md`; match `cjitter/README.md`.

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

## Blocked, and on what

- Patch evaluation: needs docker (sudo install, Vas) or an sb-cli token.
  The official harness runs each instance's held-out tests in a container.
- HETERO: metered OpenAI and xAI API keys (not subscriptions; dollar-matched
  arms need metered billing).
- Owner decisions still open: spend cap, repeat count.
- Seats currently run unsandboxed on the host with Bash allowed; acceptable
  for pilots, containers once docker exists.
