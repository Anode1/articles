# Shakedown: three Claude seats on one board, 2026-08-31

Pipeline test only; it tests nothing about the hypothesis (see ../README.md).
Task: each seat holds one fragment of a passphrase, must collect the other two
over the board. 3 of 3 seats answered correctly ("wakeup-not-broker").

## Validated

- Headless `claude -p` seats reach the board with
  `--allowedTools "Read" "Bash(<iac>/iac:*)"`. 3 of 3 posted.
- `IAC_FROM` set in the launch environment inherits into the seat's tool
  shells, so log attribution is correct without any export inside the session.
- Wakeups: all three fragments crossed the board within 3 s of the first
  broadcast, across three separate CLI processes parked on `recv`.
- Per-seat dollar metering from the CLI's `--output-format json`
  (`total_cost_usd`, `modelUsage`); see `seats.json`. Total run: $0.42.
- The room log is the complete audit record (`room-log.txt`); the brief the
  seats received is `BRIEF.md`.

## Wrinkle

The sonnet seat held both peer fragments at t+3 s but ran its full 5-timeout
`recv` budget anyway, answering at t+327 s (14 turns vs 8-9). The brief's stop
condition ("while you have fewer than two") was followed by two seats and
overrun by one. Briefs for the real arms must state loop exits as checks the
seat performs, not conditions it interprets.

## Still open before HETERO

Benchmark and residual-set harvest rule; metered OpenAI and xAI keys; spend
cap; repeat count. `modelUsage` also shows ~$0.001 of harness-internal haiku
per seat: negligible, but the metering must state whether it counts.
