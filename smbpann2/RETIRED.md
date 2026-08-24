# RETIRED, 2026-08-12. Read this before opening anything else in this directory.

This directory is the record of a closed line of work. Nothing here should be extended. The measurement
work that came out of it continued in `~/bpnn`; its findings are in `~/bpnn/doc/FINDINGS.md` and its
operating manual, including the checks distilled from the failures recorded here, is `~/bpnn/AGENTS.md`.

Kept rather than deleted for four reasons, given below.

## What is void

**`tiling.tex`** is retracted and says so on its own first page. Every quantitative claim in it is an
artifact: its energy term was exactly indifferent to placement, so a fully occupied single-group genome
satisfied its own convolution predicate for free, and controls added afterwards showed an operator that
copied nothing scoring 26% while one that destroyed the target spacing scored 59%.

**`estimator.tex`** is retired as of 2026-08-12 and must not be picked up and extended. Its central
mechanism, that search compute converts into architecture quality only if the selection signal is
refreshed, was falsified three separate ways on the afternoon it was written. The same fixed single
replicate with the mutation rate raised fourfold beats the rotation arm outright; both deterministic
yardsticks plateau while both time-varying ones keep improving including one carrying no information at
all; and the fixed arm's own believed score is flat too, so it never learned its sample, it simply
stopped searching. The genetic algorithm underneath it also loses to matched-budget random search on the
benchmark. The draft's prose is good and its abstract is the best writing in the directory, which is
exactly why it is dangerous to leave unmarked.

**Section 6 of `FINDINGS.md`** rests on that same falsified mechanism. Its inflation measurement survives
and was carried into `~/bpnn`; its yardstick conclusions did not.

## What is still valid and worth reading

**`PROTOCOL.md`** and **`FINDINGS_PREV.md`** are the derivation of the pre-flight checks now carried in
`~/bpnn/AGENTS.md`. The manual states the checks; these files record what each one cost to learn. If a
check ever looks like pedantry, the answer is here.

**The paper-1 correction is documented in `FINDINGS.md`** and was applied to `../smbpann/emergence.tex`:
future work originally attributed the spoken-digit null to the optimal filter not being compact and
local, which nothing in that pipeline licensed, and the sentence now says the attempt is inconclusive.
Paper 1 is under review, so this record must survive until that is resolved.

**The pre-registration files** are the record of predictions scored as pre-registered, including the wrong ones.

## Why this is not deleted

1. **Paper 1 is still under review** and this directory documents a correction applied to it.
2. **It is the derivation** of the checks the successor project relies on. Delete the derivation and the
   checks become folklore.
3. **It records two retractions.** That record has value precisely because retractions are what most
   people quietly discard.
4. **It is not under version control.** Everything else in this line is recoverable through git; this
   directory is not, so deletion is irreversible and it costs a few hundred kilobytes to keep.

## What was actually learned here, in one paragraph

An evolutionary search was used as an instrument to ask which pieces of a convolution emerge unaided.
The instrument was the problem. On affordable problem sizes the search is a weak hill-climber that
stalls, and measurement after measurement turned out to be reporting that stall rather than anything
about architecture. Three separate threads died of the same class of fault: an objective blind to the
property being scored, a selection signal that was a biased estimate of the reported quantity, and a
comparison whose outcome shared its noise with the thing being selected on. What survived is not a
result about convolution but a method for catching that class of fault, and a set of measurements about
benchmarks that needed no search at all.
