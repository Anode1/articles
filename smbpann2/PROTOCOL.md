# Pre-flight protocol for evolutionary structure-discovery experiments

Every item below is one specific failure from 2026-07-30/08-01, in which two complete probes
(`emerge_tile.c`, `emerge_gen2.c`) each produced a confident, well-instrumented, statistically clean
result that turned out to be an artifact of the apparatus. Four independent reviews found the same
root cause both times.

**The root cause, once:** the fitness function could not see the property being measured, so the
measured outcome was set by a free variable that no arm controlled, and every operator that moved
that free variable looked like a discovery.

Items 1 and 5 alone would have killed both probes on day one, in roughly ten minutes of compute.

---

## Before any arm runs

### 1. Objective sensitivity check

Construct genomes by hand spanning the full range of the outcome variable. Evaluate fitness on each.
**Confirm fitness actually varies.** If it does not, stop: nothing the search does can be credited
for the outcome.

> Both probes failed here. With `energy = groups/N` and `beta = 0`, every single-group genome scores
> exactly `2 - 1/12 = 1.91667`, whether it has one unit or twelve, while held-out accuracy sweeps
> 0.53 to 0.95 across that same range. The objective was flat over the entire measurable outcome.

This check is now built into the probe template as `sensitivity_check()` and runs by default.

### 2. Name the free variable, then condition on it

Identify what the objective does **not** constrain. Report every outcome conditional on that
quantity, and report the arm effect as the increment over the pooled `outcome(free_variable)` curve.

> Occupancy was free in both versions. Pooled over 1050 runs, `acc = 0.527 + 0.037 x places`,
> R^2 = 0.478; arm identity given occupancy added R^2 = 0.045. Six of seven arms had zero residual.
> Raw differences of +0.107 / +0.160 / +0.147 became +0.001 / -0.004 / +0.015.

### 3. Enumerate every constant; sweep the load-bearing ones

List every `#define` and every hardcoded rate. For each, state whether a plausible change could move
the headline. Sweep those.

> `g_padd = 0.006` was solely responsible for the headline in **both** probes. In the first, raising
> it to 0.200 took the control from 0% to 44%. In the second, the baseline's unit count is just the
> mutational equilibrium: `(N-n)*padd = n*prem` gives `n* = 2.00`; observed 2.16.

### 4. The seed must not contain the answer

If the initial population already exhibits the structure under test, the experiment measures whether
that structure **survives**, not whether it **forms**.

> A fully-occupied placement is already a perfect stride-1 tiling. Under that seed and a gentle
> mutation rate, the control reached 28% "convolutions" with coverage and regularity both at 0.95,
> which is the seed left undisturbed.

**This item was already written when the second direction began, and the second direction violated it
throughout.** Every probe in the repo seeds dense (`w=N`, coverage 1.000 at generation zero), so the
search could only ever *spend* coverage, and the whole thread measured decay while asking about
formation. The cost was not subtle: rewiring's contribution to coverage is **-0.0111 (t = -0.38)**
from a dense seed and **+0.3250 (t = 5.93)** from a minimal one. Sign flip, thirtyfold magnitude, same
code. It also made coverage uninterpretable as an outcome, because anything that slows the search
leaves the population nearer the seed and so inflates the number.

Practical form: the seed direction is a variable to sweep, not a setting to inherit. Run dense and
minimal. If they disagree, the one that has to *build* the structure is the one answering the
question.

---

## In the design

### 5. The rate-matched null is the PRIMARY comparison

Every operator needs a twin that is identical except for the single property being claimed, matched
on **effective events per generation**, not on firing rate. If the null matches the treatment, there
is no result.

> `op2` differed from `op3` in two ways: whether the filter was copied, and whether the addition
> incurred an energy cost. `op1` silently declined to add a unit whenever both lattice sites were
> occupied, so its addition rate collapsed exactly as coverage grew. Neither contrast could support
> the conclusion drawn from it. A no-operator arm with the rates turned up beat every operator arm.

### 6. `GENS = 0` as a standard row

Best-of-population from the initial random draw, no selection. If the evolved arms do not beat it,
the search is not doing the work.

> Measured: `GENS=0` gave held-out 0.582 at 3.8 units; `GENS=80` gave 0.594 at 2.2 units. Eighty
> generations bought 0.012 accuracy and destroyed 1.6 units of occupancy.

Now built into the probe template and printed by default.

### 7. Re-derive every reference, threshold and budget per configuration

Thresholds, epoch budgets, ceilings and floors all go stale when the model class or the problem size
changes. Re-derive them from measurement at each configuration, and report what the derivation gave.

> `TARGET = 0.90` was inherited across a model-class change. The hand-built convolution itself
> reached only 0.869 at N=8 and 0.664 at N=24, so the target was unreachable at every size and the
> energy branch fired only on validation noise. This manufactured an apparent scaling collapse that
> was mistaken for a limitation of the mechanism.

Corollary: a fixed epoch budget is not portable either. Stop on a measured convergence criterion
(training accuracy plateau, never the validation signal fitness reads), report the epochs consumed,
and report how often the cap binds.

---

## Before the confirmatory run

### 8. Write the primary comparison and any equivalence margin to a file, with a timestamp

Do it **before the pilot**, not after. Derive the margin from something external to the runs, for
example one minimum-detectable-effect or a fixed fraction of the measured floor-to-ceiling gap.

> The primary comparison and the +-0.05 margin were both fixed 25 minutes after the pilot result for
> that exact comparison was in hand, and the analysis script described them as pre-specified. The
> margin also gave opposite verdicts to two effects of identical magnitude (+0.0318 "equivalent",
> +0.0322 "different"), decided by 0.003 of standard error.

---

## Analysis notes (these were done right and should be reused)

`analyse.py` is sound and worth keeping: paired per-task differences, Wilcoxon signed-rank with the
paired t as secondary, Hodges-Lehmann location with an exact rank-based CI, percentile bootstrap,
Holm across the declared family, TOST equivalence against a pre-specified margin, and a stated
minimum detectable effect so that null claims are bounded rather than assumed.

Three cautions learned the hard way:

- **Never quote an approximation far into a tail.** A Fisher implementation with an absolute
  tolerance floored every p-value below 1e-15 to cancellation noise; a normal approximation used in
  place of a t reported 4.74e-34 where the correct value was 4.41e-24, and flipped one equivalence
  verdict.
- **Hodges-Lehmann is the median of Walsh averages**, not the median of the differences.
- **Check the distribution before choosing a summary.** These outcomes are bimodal (the reference
  solves 89% of tasks outright and fails at chance on 11%); report medians and fraction-solved, and
  never a mean of a two-lump mixture.

---

## Prior art to check before claiming novelty

Nowlan & Hinton, *Simplifying Neural Networks by Soft Weight-Sharing*, Neural Computation 4(4), 1992.
A parameter-counting cost that rewards filter reuse is soft weight sharing with a hard-assignment
prior, with the MDL derivation in Hinton & van Camp, COLT 1993. The energy term used throughout this
line of work is a special case, and it is 34 years old.

---

## Added after the second direction closed (2026-08-10)

Numbered from 9 to avoid renumbering references in existing write-ups. Items 1 to 8 all still hold;
item 4 in particular was already correct and was ignored.

### 9. Score the target

Item 1 asks whether the objective can **see** the outcome axis. This asks whether it **wants** the
target you named.

Hand-build the target genome; score it under the exact objective, on the same tasks, with the same
trainer, **at the full seed count**: at n=12 the target's own standard error (0.023) dominated the
comparison it exists to make, and the estimate moved 0.026 between n=12 and n=40. Hand-build a deliberately worse neighbour and confirm the objective orders the two correctly.
Compare both against what the search reaches. Sweep the training budget before concluding, so a
slow-training target is not mistaken for a dispreferred one.

**If the search beats the hand-built target, stop tuning operators.** No operator, seed, budget,
population or recombination scheme will produce a structure the fitness function ranks second.

> The convolution this line was built to find scores **0.8176 +- 0.0127** (n=40); the search reaches
> **0.8693 +- 0.0045** (n=30). The gap is 0.052, about 3.8 standard errors, and it does not close with
> training (the target is flat to declining over a 16x epoch range), so it is preference rather than
> undertraining. Under correct parameter counting a shared kernel read at several
> prefix lengths costs no more than its widest filter and is strictly more expressive, so mixed widths
> dominate uniform ones. Cost of this check: minutes. Cost of skipping it: the whole direction.

### 10. Check that the inner learner converged inside its budget

Converged, and the endpoint summarises the learner: use it, and do not pay for the trajectory.
Not converged, and the endpoint reports how far **training** got rather than how good the
**architecture** is, so every result read off it moves when the budget moves.

> Both were measured on probes from the same repo. On the locality probe the learner converges and
> area-under-the-curve fitness is strictly worse than the endpoint (placement signal-to-noise 1.29
> against 1.42, by a 16-placement x 24-seed variance decomposition; re-verified and archived as
> `scratch_rewire_vardecomp.out` after an audit flagged it as unarchived). On the depth probe it does not
> converge, and accuracy at depth rose +0.217 when epochs and data were raised. Same code, opposite
> answers, so this has to be measured per probe rather than assumed once.

A related trap, found the hard way: do not compare two candidate metrics by conditioning on one of
them. Selecting on final accuracy compresses final accuracy's spread by construction and leaves the
rival's untouched, which manufactured an apparent 2.72x advantage that a proper two-way variance
decomposition erased.

### 11. Get a positive control before trusting any null

Every result in the second direction was measured on a substrate where nobody independently knows the
right answer, so any null could be blamed on the operator, the seed, the budget or the objective, and
each explanation cost days to test and reject. A task whose answer is known independently is the only
instrument that can report **the machinery is broken** rather than **the search was unlucky**.

> Run on real audio, the pipeline turned out not to learn the task at all: on spoken digit 0 vs 1, no
> filter support separates from chance (0.48 to 0.61; full support at 125 taps scores 0.495), and a
> thirtyfold epoch increase changes nothing, so it is the front end and not the optimizer. Everything
> measured on that substrate was uninterpretable, and one sentence in the submitted paper had to be
> corrected as a result.

Run it first, not last.
