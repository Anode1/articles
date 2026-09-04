# Phase-1 results

**Negative, and not novel.** On 18 SWE-bench Verified instances that the
2025 field's best submissions all failed, one 2026 frontier model at $3 per
instance solves 16; the union of four solo models solves 17. The
pre-registered board criterion (instances the board solves that no solo
model solves) has one eligible instance, so the sign test cannot reach
alpha; the primary outcome is a null before the board arm reports. Both
facts that make it so were already published: SWE-bench Verified is
saturated and 59.4% of its unsolved instances are flawed
(OpenAI, "Why SWE-bench Verified no longer measures frontier coding
capabilities", 2026), and cost-matched repeated sampling of cheap models
was measured by Brown et al., "Large Language Monkeys" (2024). This file
records what was measured; nothing here is for publication.

## Population

37 instances failed by the best Claude-, GPT- and Gemini-based leaderboard
submissions (harvest/README.md). A single sonnet attempt each ($18.60
total) resolved 19; the 18 survivors are the population. Per the OpenAI
audit, a majority of such residual instances are expected to be flawed;
sympy__sympy-18199, the one instance no arm solved, was not checked
against that audit.

## SOLO arms (PREREGISTRATION.md, signed 2026-09-01)

443 attempts, $147.53 quota-priced, 2026-09-01 21:00 to 2026-09-02 16:30 UTC.
Solved instances of 18, by cumulative spend on that instance:

    budget   haiku  sonnet  opus  fable
    $0.5       0      5      4     0
    $1.0       2      8      8     8
    $1.5       2      8     13    12
    $2.0       2      8     13    12
    $2.5       3      8     13    14
    $3.0       3      9     13    14
    any        3     10     15    16

"any" exceeds "$3.0" because the budget check precedes an attempt: an
attempt started under $3 may finish above it (largest overrun: one fable
attempt at $5.02, unsolved). First-attempt solves: 0 / 7 / 12 / 13. Mean
attempts per instance: 14.2 / 6.6 / 2.1 / 1.7. Unsolved by every model:
sympy__sympy-18199 only.

Two readings, both narrow:

- At equal dollars the ladder is monotone in model strength; ~14 cheap
  haiku samples at $3 do not reach one fable sample. Brown et al. reach
  parity at k in the hundreds, so this is a low-k footnote, not a
  contradiction.
- Below $1 the three strong models are indistinguishable (8, 8, 8 at $1);
  fable separates only from $1.5. If organization can matter anywhere on
  this population it is in that sub-$1 regime, which this phase did not
  test (B was $3).

## BOARD arm

22 runs, $55.28 quota-priced, 2026-09-02. Lineup opus, sonnet, haiku on one
iac room, max-turns 100, budget $3 per instance; a board run costs $2.5 to
$4.6, so most instances got one run and the budget check let single runs
overrun to $4.60. BOARD solved 12 of 18.

The pre-registered test. Instances BOARD solves that no solo model solves:
none (sympy-18199 resisted the board too). Instances some solo model
solves that BOARD does not: five (astropy-14369, matplotlib-23299,
matplotlib-26208, sphinx-10614, sympy-20916). Two-sided sign test on the
five discordant instances: p = 0.0625, direction against the board. The
pre-registered success criterion is not met; the primary outcome is a
null, with every discordant instance falling the same way.

Secondary, exploratory: against its own best member, the board (12 of 18
at up to $4.60 per instance) did worse than opus alone (15 at $3) and
than fable alone (16), better than sonnet (10) and haiku (3). On this
population, three coordinated seats bought less than one strong seat at
lower cost.

## Why the board lost, from the five room logs

Read against a resolving solo patch for the same instance:

    instance           board did                              solo did
    sympy-20916 (x2)   the same one-line source fix, plus     the source fix only
                       edits to the test file the hidden
                       test patch also edits; that test fails
    matplotlib-23299   three diagnoses, all three fixes        one file
                       stacked ("both good"), plus a test edit
    sphinx-10614       "two bugs", two files patched; one     one file
                       seat wiped another's edit (git checkout)
    astropy-14369      grammar restructured wholesale; an      a narrower grammar fix
                       invalid unit now parses, two tests break
    matplotlib-26208   three identical diagnoses, one           a different approach
                       implementation, verified, wrong          in the same file

No seat stayed silent and no seat deferred wrongly. The board added:
more files, more fixes, test edits, broader rewrites. The protocol has
no subtraction step, so the shared tree is the union of three confident
contributions, and every run ends with all three posting VERIFIED or
FINAL over a patch larger than the fix. Four of five losses are consensus
by union (PREDICTIONS.md item 6, agreeableness in additive form); the
fifth is a convergent wrong branch (item 5). Item 1 holds at the
verification stage rather than the diagnosis stage. The norm this
implies is stated in PREDICTIONS.md as item 7.

## Counts over the 22 phase-1 board logs

Automated proxies, rough by construction (run/analyze_room.py plus regular
expressions; branches = diagnoses naming disjoint file sets; dissent =
disagree/veto/conflict/wrong; verified = VERIFIED or FINAL posts). Twelve
solved runs against ten lost:

    proxy                         solved   lost
    messages per run               15.3    12.5
    diagnoses posted                3.0     2.9
    branches (disjoint file sets)   2.0     2.6
    agreement posts                 2.2     2.1
    agreement without a receipt     1.2     1.2
    dissent posts                   1.2     0.6
    VERIFIED or FINAL posts         0.8     1.6

Against PREDICTIONS.md: item 5 expected the losses to be narrow, one
branch committed early; the losses were wider, and merged. Item 6
(agreement over evidence) reads in the dissent row: lost runs carried
half the dissent of solved runs, and twice the confident closings. Item
1 holds at closing: the confident wrong claim is the chorus of VERIFIED,
not an early diagnosis. n is 12 against 10 and the proxies are lexical;
a judged reading of the logs is the version a paper would carry.

## Prediction 7: the subtractive brief

10 runs, $43.88 quota-priced, 2026-09-03 05:32 to 08:04 UTC. The five
instances the phase-1 board lost, each run once under the standard brief
and once under the subtractive brief (run/run_board.sh, fourth argument),
same lineup opus, sonnet, haiku, max-turns 100, no budget cap. Each run
scored by the official harness as it finished (run/norm_test.py; verdicts
in runs/norm_test.tsv, runs in runs/board/ and runs/board-subtractive/).

    instance           standard          subtractive
    sympy-20916        RESOLVED   $1.93  RESOLVED    $2.03
    matplotlib-23299   lost       $4.77  lost        $4.53
    sphinx-10614       RESOLVED   $4.01  lost        $6.59
    astropy-14369      lost       $4.75  RESOLVED    $3.39
    matplotlib-26208   RESOLVED   $7.02  RESOLVED    $4.86
    solved             3 of 5    $22.48  3 of 5     $21.40

Item 7 asked for at least 3 of 5. The subtractive brief reached 3; so did
the standard brief rerun, the dispersion control, with one instance
flipping each way. The prediction is not supported: the control absorbs
the whole effect. The phase-1 losses were one draw each, and a second
draw under the same brief resolves three of the five, so the BOARD arm's
12 of 18 carries a run-to-run dispersion its single-run design could not
see.

The brief did what it was written to do. Diff lines 68/70/70/187/95 under
the standard brief against 13/18/45/99/24 subtractive, smaller on every
instance, by 2 to 5x; test-file hunks 7 across four standard runs, 0
across the five subtractive. The additive pathology read from the five
room logs was real and was removed. It was not what lost the instances.

## Phase 2, first two points: tau 0 against tau 90

20 runs, $87.62 quota-priced, 2026-09-03 19:30 to 2026-09-04 00:19 UTC
(PHASE2.md; rows in runs/threshold.tsv). Five instances, two draws each,
threshold brief, lineup opus, sonnet, haiku.

    tau   solved   dollars   solves/$   claims held   gate bypassed
     0    7 of 10   43.09     0.162          0             0
    90    6 of 10   44.53     0.135         30             0

One solve apart, which the registration calls noise. Per instance, tau 90
lost astropy-14369 and sphinx-10614 on both draws where tau 0 took each
once; the rest matched.

What the 30 holds bought. No seat ever stopped after a hold: the next
post came every time, 21 of 30 rated 90 or above, and 7 of those with no
command run in between (a NOTE at 85 reposted at 100, a DIAGNOSIS at 85
followed by a CLAIM at 100). The other 22 ran something first, and a few
were the intended path (a DIAGNOSIS at 60 followed by a REPRO at 100
after four commands). The haiku seat took 21 of the 30 holds. Mean stated
confidence was 92 under tau 0 and 93 under tau 90, against a brief that
caps an unexecuted claim at 60: the seats rate above the gate by default
and re-rate to pass it. Of posted claims rated 90 or above, DONE posts in
runs the harness scored unresolved: 14 of 103 under tau 0, 17 of 108
under tau 90.

Against PHASE2.md: 8 undetermined at two points, direction against the
threshold; 9 holds (over 10% at both points); 10 fails, no seat passed
and stayed silent; 11 fails, zero bypasses. The registered next point is
tau 45. Stated confidence is the parameter, and the seats set it; a
threshold on a self-report is met by the report moving.

## Limitations

- Contamination: OpenAI reports verbatim reproduction of gold patches on
  this benchmark; a pilot seat said as much on the board.
- Meter: subscription quota priced at API rates; matches arms against
  each other, not against an invoice.
- One attempt (sphinx-10614, haiku, 2026-09-02T15:03Z) was killed by the
  operator during a disk outage; marked excluded, never counted.
- Seats ran unsandboxed on the host with Bash allowed, identically for
  every arm.

## What the phase bought

The decision it was designed to inform: phase 2 (cross-lab seats, metered
API spend) is not justified on this population. The live version of the
question needs a population that current solo models fail at the budget
of interest (SWE-bench Pro, or a sub-$1 budget), and that decision was
reached for $147 of quota instead of the $500 phase 2 would have cost.
