# Pre-registration: phase 1, board versus every solo model, one lab

    status      DRAFT, unsigned. No arm runs before the owner signs.
    population  the 18 instances in runs/screen.tsv marked "unresolved"
    frozen      population, budgets, criterion; fixed at signing

## Question

On tasks no single Claude model solves at a given budget, does a team of
Claude seats coordinating over an iac board solve any, at the same budget?
This is the within-lab half of the design in README.md; the cross-lab arm
(phase 2) runs only if this phase finds an effect.

## Arms, per instance

The meter is the dollar figure the CLI reports per session (subscription
quota priced at API rates). Budget B = $3.00 per arm per instance.

    SOLO-m   for each model m in {haiku, sonnet, opus, fable*}: fresh
             attempts (run/run_solo.sh), one after another, until one
             resolves or spend reaches B. Each attempt a fresh clone,
             no memory of prior attempts.
    BOARD    three seats, models opus,sonnet,haiku, one shared checkout,
             one iac room (run/run_board.sh), runs until resolved or
             spend reaches B. max-turns 100 per seat.

    * fable confirmed headless (claude -p --model fable) 2026-09-01.

The BOARD lineup mixes Claude models so a seat's blind spot is not three
times the same blind spot; separating board-effect from within-lab-mix
is phase 2's job, not this phase's.

## Scoring

Official SWE-bench harness (run/eval_batched.sh pattern), dataset
SWE-bench/SWE-bench_Verified. An instance is SOLVED by an arm if any of
its attempts' patches scores resolved=True.

## Criterion, before any numbers

Primary: the number of instances BOARD solves that no SOLO-m solves,
minus the number any SOLO-m solves that BOARD does not. Pre-registered
test: two-sided sign test over discordant instances, alpha 0.05.
Pre-registered success: p < 0.05 with the difference favoring BOARD.
Anything else, including BOARD solving 1-2 with p above alpha, is
reported as what it is. A null is archived like any probe.

## Stated limitations

- Contamination: models partially remember upstream fixes for these
  historical issues (observed in the board pilot). It biases all arms
  equally; absolute solve rates are not capability claims.
- The meter prices subscription quota at API rates; it matches arms
  against each other, not against a real invoice.
- Seats run unsandboxed on the host; identical for every arm.

## Excluded

The seaborn and django-11141 pilots (runs/solo/mwaskom__seaborn-3187,
runs/board/django__django-11141) predate this document and are excluded.
django-11141 stays in the population; its arms rerun under this protocol.

## Signature

Signed: ____________  date: ____________
