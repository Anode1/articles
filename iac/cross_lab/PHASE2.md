# Phase 2: the posting threshold, swept for solves per dollar

    status      registered by the owner, 2026-09-03, before any threshold run
    parameter   tau, 0 to 100; a seat's claim rated under tau is held
    population  the five instances the phase-1 board lost (RESULTS.md)
    meter       solves per quota dollar at fixed lineup and turns

## Question

Phase 1 found the seats never abstain: 0 abstentions in 105 solo attempts
and 32 board runs, every board run closing on VERIFIED or FINAL, and a
prompted subtraction norm changed the patches without changing the
outcomes. The owner's hypothesis (PREDICTIONS.md, 2026-09-02) is that a
human collaborator withholds a claim below a confidence threshold because
a wrong claim costs reputation, and that LLM seats lack that threshold.
This phase gives the seats one mechanically, and searches its value.

## The instrument

The threshold brief (run/run_board.sh, variant threshold). Every board
message goes through $ROOM/post with an integer confidence, defined to the
seat as the probability that the claim survives a peer running a command
against it: 100 means executed and seen, an unexecuted claim is at most
60. The gate holds any message rated under tau, except CLAIM (file
coordination), and posts "[seat] PASS: <kind> withheld, conf=NN under tau"
in its place. A held DONE means the edit is reverted. Every attempt,
posted or held, lands in claims.tsv with its text, so a held claim can be
checked afterwards against the run's outcome. Posts that bypass the gate
(raw iac send, no conf=) are counted per run.

tau = 0 is the control: the standard protocol with confidence tags and
nothing held.

## Design

Lineup opus, sonnet, haiku; max-turns 100; no budget cap; one run costs
$2 to $7. Each run scored by the official harness as it lands
(run/threshold_sweep.py; rows in runs/threshold.tsv). Per tau the meter is
solves over dollars across the five instances and all draws.

Search order, chosen before data: tau 0 and 90 at two draws each (20 runs,
about $90); then the midpoint of whichever side is higher, at two draws;
then halve again. Stop when the bracket is 10 wide or spend passes $250.
Phase 1 measured the dispersion of this population at 3 of 5 resolving
under a rerun of the same brief, so two draws per point is the floor,
and a difference of one solve between points is noise.

## Predictions, before any run

8. Solves per dollar is not monotone in tau: some tau in 60 to 90 beats
   both tau 0 and tau 95. (Owner's hypothesis; the searched optimum.)
9. Stated confidence is not calibrated: of posted claims rated 90 or
   above, more than 10% are later vetoed with a receipt or are DONE
   claims in a run the harness scores unresolved.
10. At tau 80 or above, most runs contain a PASS, and the seat that
    passed either posts a receipted claim next or nothing; it does not
    post an unreceipted one. Under tau 0 no seat ever passes.
11. The gate is bypassed: at least one run per tau above 0 carries a raw
    iac send without conf=.

## What this phase does not test

The population is one that solo models solve (fable 16 of 18), so a
threshold cannot make the board beat a solo seat here; the meter is the
board against itself. Reputation proper, a track record carried across
runs, is not implemented: names are fresh every run. Both are the phase
that follows if 8 holds.
