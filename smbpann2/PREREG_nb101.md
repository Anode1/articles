# Pre-registration: selection bias on real NAS-Bench-101 data

**Written 2026-08-12, before any pilot of `nb101_signal.c`** (PROTOCOL item 8). Predictions fixed
here; the probe had not been run when this was written.

## Why

The toy result (`estimator.tex`) shows a search overfitting *which held-out positions* it must
generalize to, and repairs it by rotating them. Its weakest sentence is that the mechanism "should
transfer to any search selecting on a held-out statistic, but that is an argument rather than a
measurement." This experiment turns that into a measurement on data referees already trust.

## Why NAS-Bench-101 can carry the argument

NAS-Bench-101 trains every architecture **3 independent times**. Those 3 validation accuracies are
exchangeable replicates (same architecture, different init and training seed), which is precisely
what the exchangeability argument needs: for an architecture not chosen using replicate *i*, the
expected accuracy on replicate *i* equals that on replicate *j*. Any excess is selection-induced.

The shipped table in this repo averages the trials away, so a new extractor (`nb101_trials.c`) keeps
them. **Oracle:** the mean of the 3 extracted trials reproduces the archived averaged table to
1e-4 pp across all 423,624 architectures.

**Replicate noise, measured before designing the experiment:** within-architecture SD of validation
accuracy is p50 0.328, p90 0.786, **p99 42.68**, max 48.0 percentage points. About 1% of
architectures are effectively bimodal: they sometimes train and sometimes collapse to chance. This
is a strong and entirely real mechanism for a single-measurement search to be misled.

## Design (E1: selection intensity)

Per repetition: randomly permute the 3 trials, then draw `K` architectures uniformly at random.

- **FIXED** arm: score each candidate by trial `perm[0]`; take the argmax.
- **AVG2** arm: score each candidate by `mean(perm[0], perm[1])`; take the argmax.
- **Report** for both arms is trial `perm[2]`, never used for selection by either.

Recorded per repetition: the arm's *believed* score, the *reported* accuracy on the held-out
replicate, the chosen architecture's *true quality* (mean of all 3 trials), and the *regret*
against the best true quality present in that sample of `K`.

`K` sweeps powers of 2 from 2 to ~65536. Repetitions large enough that standard errors are far below
the effects (the table is a lookup, so evaluations are effectively free).

**Primary quantity: inflation = believed - reported.** Exchangeability sets its expectation to zero
for an architecture chosen without using the selection replicate; any positive value is
selection-induced.

## Predictions, fixed before running

- **P1.** Inflation is positive and grows monotonically with `K`, approximately linearly in
  `sqrt(log K)` (the classical winner's-curse form for a maximum of noisy draws).
- **P2.** AVG2 has strictly lower inflation than FIXED at every `K`, by roughly a factor of
  `sqrt(2)` if the noise were Gaussian and homoscedastic. Because the noise is heavy-tailed
  (p99 = 42.7 pp), I expect the reduction to be **larger** than `sqrt(2)`, since averaging
  suppresses the bimodal-collapse cases that dominate the tail.
- **P3.** AVG2 also finds genuinely better architectures: higher true quality and lower regret than
  FIXED at equal `K`. This is the practically important claim: the repair is not merely honest
  bookkeeping, it changes what the search returns.
- **P4.** At large `K` the FIXED arm's *true quality* eventually stops improving, or degrades, while
  its *believed* score keeps rising: the search buys more illusion, not more architecture.
- **P5 (cost).** The inflation at practical budgets (`K` of order 100-1000) exceeds the accuracy
  differences that NAS papers routinely treat as meaningful (a few tenths of a percentage point).

## What refutes what

- P1 false (inflation flat or zero): the exchangeability framing does not apply to this benchmark and
  the toy result stays a toy result.
- P2 true, P3 false: averaging is honest bookkeeping only; the paper must say the repair improves
  reporting and not search quality.
- P4 false: selection intensity is harmless here, weakening the practical claim.

## E2: rotation vs averaging (`nb101_search.c`), registered 2026-08-12 after E1 and a 50-run pilot

A generational GA over the NAS-Bench-101 cell space, graph representation, canonicalisation and
mutation taken verbatim from `validation/nb101.c` so the space and oracle match the published
crossover experiment. Three arms differing only in the selection rule:

    FIXED    score = v[perm[0]]                    one replicate for the whole run
    ROTATE   score = v[perm[gen & 1]]              redrawn every generation
    AVG2     score = mean(v[perm[0]], v[perm[1]])  the same two replicates, averaged

ROTATE and AVG2 have identical replicate access and differ only in alternating versus averaging, so
any difference between them isolates that distinction. ROTATE's per-generation signal is exactly as
noisy as FIXED's, so it is not a variance reduction: it only removes the fixed sample that could be
memorised across generations. Report is always `v[perm[2]]`, which no arm selects on.

**A 50-run pilot (recorded, underpowered, SE 0.055 on inflation) suggested ROTATE is inert here while
AVG2 helps**: the opposite of the toy task, where rotation was the effective repair. Two readings,
and the experiment is designed to separate them:

- **P6 (accumulation).** If rotation matters by preventing accumulation of replicate-lucky
  architectures across generations, its advantage over FIXED must **grow with generation count**,
  because there is more to accumulate. Prediction: the ROTATE-minus-FIXED difference in true quality
  is near zero at 10-20 generations and positive and growing by 100-200.
- **P7 (nothing to memorise).** If instead the replicate structure here is pure per-architecture iid
  noise, with no systematic component to memorise, rotation should be inert at **every** generation
  count, and only averaging (which actually lowers the variance the winner's curse feeds on)
  should help. Prediction: ROTATE tracks FIXED at all generation counts, flat in the sweep.

P7 would be a real and reportable difference between the two settings rather than a failure: the toy's
bias is *systematic* (a fixed set of held-out positions the search can fit), while NAS-Bench-101's is
*variance* (iid replicate noise), and the two call for different repairs. That distinction, if it
holds, is more useful to a practitioner than a claim that one repair fixes everything.

**Design:** generation sweep {10, 20, 50, 100, 200} at POP=24, and a population sweep {8, 48, 96} at
GENS=50, 20,000 runs per arm per cell. Runs share the benchmark rather than a per-seed task, so the
across-arm comparison is two-sample, not paired, and 20,000 runs put the standard error on true
quality near 0.002, far below the ~0.06 differences the pilot showed.

**Primary outcome for E2 is true quality and regret, not inflation.** With FIXED and ROTATE both
taking a final argmax over the population on a single noisy replicate, their final-step winner's curse
is the same by construction, so inflation cannot separate them; what can is whether the population
they arrive at is actually better.
