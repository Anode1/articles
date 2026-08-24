# smbpann2: what was tried, why it failed, what to keep

**Status: direction scrapped 2026-08-01.** Paper 1 (`../smbpann/emergence.tex`, Zenodo
10.5281/zenodo.21423177, under review at GPEM) is unaffected and was independently re-verified.

## The question

Paper 1 showed a compact filter emerges only when mutation acts on the shared feature rather than one
edge, but its offset-mask genome made the connectivity translation-invariant by construction, so the
**tiling** was imposed rather than emergent. smbpann2 asked whether the tiling emerges when nothing in
the genome encodes translation.

## Two probes, two failures, one cause

**`emerge_tile.c`** scored a structural predicate: one shared filter, regular stride, no gap wider than
the kernel. Reported 0/200 to 124/200 convolutions when a copying operator was added.
**Refuted.** `E_param = groups/P` is exactly indifferent to placement, so a fully-occupied single-group
genome satisfies the predicate for free (all gaps are 1). Controls: an operator copying *nothing* scored
26%, one that deliberately *destroyed* the target spacing scored 59%, the operator built to produce it
scored 17%. A hardcoded, never-swept `padd = 0.006` was solely responsible for the 0/200 baseline;
raising it to 0.200 took the control to 44%.

**`emerge_gen2.c`** replaced the structural predicate with a functional one, held-out translation
generalization: train on 2 of 12 positions, test on the other 10. Reported a large visibility effect and
a filter-copying mechanism.
**Also refuted, same cause.** Fitness is *constant* at `2 - 1/12 = 1.91667` for every single-group
genome from 1 unit to 12, while held-out accuracy sweeps 0.53 to 0.95 over that same range. So:

- held-out accuracy is a single function of unit count (`acc = 0.527 + 0.037 x places`, R^2 = 0.478),
  and arm identity given occupancy adds R^2 = 0.045;
- conditioned on occupancy, every effect collapses: +0.107 / +0.160 / +0.147 become
  +0.001 / -0.004 / +0.015, and the primary visibility effect goes +0.188 -> +0.025 (TOST equivalent);
- `GENS=0` (no evolution at all) scored 0.582/3.8 units against 0.594/2.2 for 80 generations. Selection
  contributed nothing and *reduced* occupancy;
- the baseline's unit count is the mutational equilibrium `(N-n)*padd = n*prem` -> n* = 2.00; observed 2.16.

**Root cause both times: the fitness function could not see the property being measured, so the outcome
was set by a free variable no arm controlled, and any operator that moved that variable looked like a
discovery.** Changing the measure did not fix it; the defect was in the objective.

## What is actually true

**No parameter-counting or connection-counting penalty selects for spatial coverage.** `E_param` is
provably indifferent to placement; `E_conn` actively destroys it (occupancy collapses to 1.35, held-out
0.586). Supported by both probes. Note this is a property of *these* costs, not of costs in general:
Immer et al. (NeurIPS 2022) select invariances from the training set alone.

## Prior art that covers the positive claims

- Nowlan & Hinton, *Simplifying Neural Networks by Soft Weight-Sharing*, Neural Computation 4(4), 1992:
  a parameter-counting cost rewarding filter reuse, with the MDL derivation in Hinton & van Camp 1993.
  The energy term used throughout this line is a special case, 34 years old.
- Elsayed et al., *Revisiting Spatial Invariance with Low-Rank Local Connectivity*, ICML 2020: the
  locally-connected-to-convolutional continuum, i.e. this genome, already published.
- d'Ascoli et al., NeurIPS 2019: the gradient-space version of the reachability story.

## Why no better substrate would have helped either

Run after the direction was scrapped, as protocol check 1 applied to the *objective* rather than to a
probe (`../../smbpann/validation/objcheck.c`, no search involved). Genomes are built by hand spanning
the full range of the outcome; each candidate cost is asked whether it varies over that range and in
which direction. 40 seeds, N=12.

```
genome                         outcome   A grp/N   B pls/N   C place   D total
 1 places, regular, 1 filter    0.528     0.083     0.083     0.167     0.094
 5 places, regular, 1 filter    0.824     0.083     0.417     0.250     0.105
11 places, regular, 1 filter    0.965     0.083     0.917     0.250     0.105
 3 places, regular, unshared    0.576     0.250     0.250     0.167     0.239
11 places, regular, unshared    0.561     0.917     0.917     0.250     0.830

A  groups/N        range 0.833   corr -0.51   sees SHARING only; flat along coverage
B  places/N        range 0.833   corr +0.57   WRONG WAY: better outcome costs more
C  placement MDL   range 0.417   corr +0.29   non-monotone; cheap when sparse AND when dense
D  total MDL       range 0.736   corr -0.48   A again, wearing the filter-bits term
```

**No candidate objective sees coverage in the right direction, and the reason is structural: a
complexity penalty rewards small structures while translation generalization requires large ones, so
the two are anti-correlated by construction.** `A` is flat at 0.083 along the coverage axis while the
outcome sweeps 0.528 to 0.965; its apparent correlation comes entirely from the sharing axis. `B` sees
coverage and opposes it.

Consequence: coverage pressure cannot come from a description-length or parameter-counting prior. It
has to come from the data term. That is why the `NVALPOS` manipulation was the only thing that ever
moved the outcome, and why it reduced to "the search installs one detector per position the fitness
function evaluates."

It also settles the question of whether a better substrate would rescue the direction. 2-D with
multiple channels and the 3000 FSDD recordings already sitting in `../../smbpann/data/fsdd` would have
inherited this defect unchanged. The problem was never the toy scale; it was that the objective is
anti-correlated with the outcome on the axis that matters.

Cost of finding this out with `objcheck`: one hour. Cost of finding it out empirically: two days and
two papers.

## Keep

- **`PROTOCOL.md`**: eight pre-flight checks, each annotated with the failure it prevents. Items 1
  (objective sensitivity) and 5 (rate-matched null as the primary comparison) would have killed both
  probes on day one in ten minutes of compute.
- **`analyse.py`**: paired per-task differences, Wilcoxon, Hodges-Lehmann with exact CI, bootstrap,
  Holm, TOST against a pre-specified margin, minimum detectable effect. A referee called it better than
  most real submissions. The inference was clean; it was run on confounded contrasts.
- **Two transferable findings.** A topology search seeded from a fully-occupied mask inherits the order
  it appears to discover. And: any metric monotone in a quantity the objective does not constrain will
  manufacture this failure, so report every outcome conditional on that quantity.

## Reusable code, now in the repo

- `validation/emerge_offset_check.c`: paper 1's experiment with `PREM`/`PADD` exposed. Used to verify
  paper 1 against the failure that killed smbpann2; the gap never closed or inverted across a tenfold
  rate sweep, because its mechanism is analytic rather than rate-dependent.
- `validation/objcheck.c`: **the most transferable artifact from this direction.** Protocol check 1 as
  a standalone tool: build genomes spanning the outcome, ask of each candidate objective whether it
  varies over that range and in which direction. Runs no search, costs an hour, and answers "is this
  objective worth searching under" for any future experiment, not only this one.
- `validation/emerge_gen2.c`: carries the two automated protocol checks (objective sensitivity in the
  feasible region, and a `GENS=0` row) that run by default on every invocation. Useful as a template
  even though its own direction is scrapped.

## If this is ever revisited

**Not with a better substrate.** That was the working assumption until `objcheck` was run, and it is
wrong: 2-D, multiple channels and real data would all have inherited an objective anti-correlated with
the outcome. The toy scale was never the binding problem.

What it would actually need is a different **source of coverage pressure**, since no complexity prior
can supply it. Three options, none of them small:

1. A data term that spans the positions, which is what `NVALPOS` did, but then the result is close to
   tautological ("the search installs a detector per position the objective evaluates") and needs a
   sharper question to be worth reporting.
2. Quality-diversity (MAP-Elites with position coverage as the behaviour descriptor). This is the
   field's standard answer to "the objective cannot see the property you want" and was never tried.
   A referee asked directly why not, and there is no answer.
3. Modularly varying goals, after Kashtan & Alon (PNAS 2005): change the structure of the objective
   over time rather than adding a term to it.

Before any of that: run `objcheck` on the proposed objective. If it cannot see the outcome, nothing
downstream will rescue it, and one hour will have saved the two days this cost.

---

# Thread 2 (2026-08-08): budget dependence of the depth result, and the placement neutral network

Separate from the scrapped tiling direction above. Nothing here touches paper 1, which is submitted;
these are follow-up results about two of its probes.

## The depth probe's never-swept constants (`emerge_compose.c`)

`LMAX 8`, `TEPOCHS 300`, `NTR 192` and `RESTARTS 4` are compile-time constants and no run varied them.
`LMAX` was already known to be load-bearing: paper 1's runs stopped at L=5 and had to print
`(at ceiling)`. Protocol item 3. A four-level budget ladder was run at 32 seeds, s=6 and s=8, L=1..8,
test accuracy, fair mean over restarts (no best-of):

    s=6, required L=3
      A   300ep/192tr  0.524 0.551 0.623 0.662 0.657 0.585 0.521 0.497   peak 4, tied {4,5}
      E  1500ep/192tr  0.524 0.556 0.643 0.703 0.728 0.731 0.609 0.518   peak 6, tied {4,5,6}
      B  1500ep/768tr  0.538 0.574 0.657 0.742 0.791 0.802 0.643 0.542   peak 6, tied {5,6}
      D  6000ep/768tr  0.538 0.573 0.658 0.737 0.768 0.751 0.640 0.546   peak 5, tied {5,6}

    s=8, required L=4
      A   300ep/192tr  0.519 0.544 0.590 0.626 0.642 0.562 0.520 0.507   peak 5, tied {4,5}
      E  1500ep/192tr  0.518 0.550 0.599 0.676 0.732 0.657 0.567 0.518   peak 5, tied {5}
      B  1500ep/768tr  0.533 0.566 0.634 0.733 0.785 0.722 0.616 0.522   peak 5, tied {5}
      D  6000ep/768tr  0.533 0.566 0.636 0.733 0.784 0.690 0.641 0.534   peak 5, tied {5}

"tied" = depths within 2 combined SE of the argmax; the argmax alone is not stable enough to report.

**The peak is interior, not a ceiling artifact.** At L=1..8 accuracy rises to a peak and then falls
hard (s=6: 0.802 at L=6 down to 0.542 at L=8). Paper 1 could not see this because the runs stopped at 5.

**The old curves were undertrained, and the deficit grew with depth.** A to B lifts by +0.014 at L=1
and +0.217 at L=6. Shallow stacks are architecture-limited (they cannot see the spike pair at any
budget); deep stacks were optimization-limited. E isolates the cause: at the s=6 peak, epochs alone
took 0.662 to 0.731, epochs plus data took it to 0.802, so the two contributed about equally.

**More epochs at fixed data then makes it worse.** D is 4x B's epochs with the same 768 examples and
loses accuracy exactly where capacity is highest: s=6 L=6 falls 0.802 to 0.751, L=5 falls 0.791 to
0.768, while L=1..4 do not move. Ordinary overfitting. The remaining ceiling is **data-limited, not
epoch-limited**, so `NTR` is the lever for any further attempt, not `TEPOCHS`.

**The 0.85 negative survives, and is now much better founded.** Peak accuracy converges near 0.80
(s=6) and 0.785 (s=8) across a 20x epoch range and a 4x data range. Paper 1's "never crosses the
target, so nothing is cleanly selected" is therefore not an artifact of a small training budget. This
was the outcome in doubt when the ladder was run, and it came out in paper 1's favour.

**But the selected depth is budget-conditional, and the overshoot is not a constant margin.** At s=6
the tied set moves {4,5} to {5,6} between A and B and then stops; at s=8 it sharpens {4,5} to {5} and
then stops. Converged overshoot is +2..+3 at s=6 and +1 at s=8. A fixed margin explanation (exact
receptive field leaves no slack, so one extra layer is easier to optimise) predicts the same offset on
both tasks and is refuted by that difference. Consequence for any follow-up: **a selected-depth number
is meaningless without the training budget beside it.**

Reproduction: the ladder used a patched copy of `emerge_compose.c` with `NTR`/`TEPOCHS`/`RESTARTS`
wrapped in `#ifndef` so `-D` works, plus `SEED0`/`DI0`/`DI1`/`RAW` env knobs for parallelism across
seed chunks. Exposing those in the probe itself is the obvious next commit.

## The placement neutral network (`emerge_local.c`)

`param_energy()` reads `maxwidth` when shared and the sum of widths when unshared. **Neither reads
`start`.** So moving a window at fixed width is exactly energy-neutral, and the equal-energy genomes
form a connected neutral network. This is the one axis a count-based complexity prior provably cannot
select on, which is the same analytic shape as paper 1's width-axis mechanism and as `E_param =
groups/P` above.

Measured over 288 hand-built genomes (widths pinned at K=3, sharing on, only `start` varying, 12 tasks):

- energy is identical for every genome: **0.025000**, as the code requires;
- test accuracy ranges **0.559 to 0.931**, so accuracy sees placement clearly;
- `acc = 0.612 + 0.190 x coverage`, **R^2 = 0.174**. Coverage explains only a sixth of the variance, so
  placement carries real structure beyond occupancy. Contrast the scrapped arm, where occupancy
  explained R^2 = 0.478 and swallowed the whole effect;
- of the 288, **15 clear the 0.90 target and all 15 score objective 1.975000**, identical to six
  decimals.

**The objective is a step, and above the step it is blind to placement.** `objective()` returns
`(acc >= target) ? (2 - energy) : acc`. Below target it is accuracy, which selects placement well.
At or above target it is `2 - energy`, provably constant in `start`. Since any genome clearing target
scores ~1.975 against at most 1.0 for anything below it, the first clearing individual dominates
selection and every placement among the cleared elites ties. **The endgame is neutral drift, and the
endgame is when the final population is measured.** `emerge_local.c` already contains a rewiring
operator (`start += +-1` at a hardcoded, never-swept 0.15, "window can slide"), and for the part of the
run that decides the reported structure, that operator is a random walk.

## New probe: `validation/emerge_rewire.c`

Written for this thread; does not modify `emerge_local.c`.

- **Continuous objective** `acc - lambda*energy` replaces the step, so accuracy keeps selecting on
  placement at every accuracy level. This is the substantive fix.
- **Three arms**, sharing identical width mutation so only placement differs: `0 no-rewire` (start
  never mutates; the add/remove-only control), `1 slide-1` (`start += +-1`, neighbour-only, diffusive,
  O(d^2) to move distance d), `2 rewire-rand` (`start :=` uniform valid, O(1) to move d). Arm 1 imposes
  a spatial neighbourhood, which is the prior under test, so **arm 2 is the primary result and arm 1
  measures what the prior buys**.
- `sensitivity_check()` runs by default and returns rc=2 rather than producing results if the objective
  is flat over placement or over width (item 1; same role as `objcheck.c`). It passes here: placement
  spans 0.280 of objective at constant energy.
- Every run emits a RAW row with coverage, so an arm effect is read as the increment over the pooled
  `acc(coverage)` curve, never raw (item 2).
- `PSLIDE`, `LAMBDA`, `PGROW`, `PSHARE`, `GENS`, `SEEDS` are all env knobs (item 3). `GENS=0` is the
  no-evolution control.

Rationale for the operator: rewiring is count-preserving, so it travels the neutral network at zero
energy cost. Biologically this is the synaptic-turnover-versus-neurogenesis asymmetry, but the rate
should not be taken from biology; it is a free constant and must be swept, or better, put in the genome
and self-adapted the way paper 1's mutation rate already is.

### Result (30 seeds, 150 generations, LAMBDA=1)

                    test acc          energy           max-w      objective
    no-rewire    0.8932 +- 0.0068  0.0936 +- 0.0012  11.23 +- 0.15   0.7996
    slide-1      0.9117 +- 0.0080  0.0742 +- 0.0038   8.90 +- 0.46   0.8376
    rewire-rand  0.9057 +- 0.0060  0.0422 +- 0.0045   5.07 +- 0.54   0.8635

    paired against no-rewire, same task seeds:
      slide-1      d_acc +0.0186 +- 0.0045 (t=4.13)   d_energy -0.0194 +- 0.0036 (t=-5.46)
      rewire-rand  d_acc +0.0125 +- 0.0053 (t=2.38)   d_energy -0.0514 +- 0.0044 (t=-11.74)

`GENS=0` control: all three arms identical (0.894 acc, energy 1.0, width 12), so no seed or pipeline
asymmetry. Coverage conditioning (item 2): pooled `acc = 0.817 + 0.092 x coverage`, **R^2 = 0.056**, so
coverage is not the confound here as it was in the scrapped arm (R^2 = 0.478); the arm ordering
survives conditioning, though the residuals alone are not individually significant.

**Rewiring is what makes low energy reachable, and the effect is on compactness, not accuracy.** After
150 generations add/remove-only still sits at a 11.2-tap shared kernel, essentially the full input
width of 12. Mechanism, which follows analytically from the code: with sharing on, energy is the
*maximum* width, and under add/remove-only every window is pinned at `start=0`, so the only way to
cover the input is to grow wide, and one wide unit sets the kernel width for everyone. Rewiring buys
coverage by *moving* instead of *growing*. That is the neutral-network argument confirmed: being able
to travel placement at zero energy cost is what makes the compact basin reachable at all.

### PSLIDE sweep: the spatial neighbourhood prior buys nothing but delay

Rates 0.02 / 0.05 / 0.15 / 0.40, everything else fixed. Arm 0 ignores the rate and came out identical
in all four runs (0.8932 acc, 0.0936 energy), which checks determinism.

    PSLIDE               0.02     0.05     0.15     0.40
    slide-1     energy  0.0842   0.0806   0.0742   0.0608     max-w  10.10  9.67  8.90  7.30
    rewire-rand energy  0.0608   0.0528   0.0422   0.0422     max-w   7.30  6.33  5.07  5.07

**`rewire-rand` at 0.02 exactly equals `slide-1` at 0.40** (energy 0.0608, max-w 7.30 in both). Random
targeting reaches at a twentieth of the rate what neighbour-only reaches at the top of the sweep, which
is the O(1)-versus-O(d^2) displacement argument measured rather than asserted. `rewire-rand` then
saturates: 0.15 and 0.40 are identical (0.0422 / 5.07). `slide-1` has not saturated even at 0.40.

Accuracy is flat in the rate for both rewiring arms (0.906..0.912 everywhere) against 0.8932 for
no-rewire, so the accuracy gain is robust and the apparent slide-1 accuracy advantage at 0.15 is noise:
at 0.05 and 0.40 `rewire-rand` is equal or better, and the gaps are inside the error bars throughout.

**So the neighbourhood prior contributes nothing except slower travel.** An operator with no spatial
bias at all finds more compact shared filters, faster, at every rate tested. Stated precisely, because
the limit matters: locality is still imposed in the *genome* (windows are contiguous by construction).
What emerges without any spatial bias in the *operator* is the arrangement of those windows and the
width of the shared kernel.

**Not reached:** the compact convolution target is width -> K=3, and `rewire-rand` floors at 5.07 taps.
Whatever stops it there is the next question, and it is not the rewiring rate, which has saturated.

Open constants: `LAMBDA` fixed at 1.0 and never swept; one task family at N=12; and the `GENS=0`
control can only detect seed and pipeline asymmetry, not drift, since with no mutation all arms are the
same genome. Putting the rewiring rate in the genome and self-adapting it, the way paper 1's mutation
rate already is, would remove the rate as a free constant entirely.

### LAMBDA sweep: the 5-tap floor was the energy weight, not the search

`LAMBDA` was the last unswept constant. Rates 1 / 2 / 4 / 8 / 16, PSLIDE=0.15, 30 seeds, 150 gens.

    LAMBDA    rewire-rand: max-w    acc      cov   |   no-rewire: max-w    acc      cov
       1                    5.07  0.9057   0.925   |             11.23  0.8932   0.936
       2                    3.53  0.8986   0.886   |             10.97  0.8900   0.914
       4                    2.13  0.8822   0.839   |             10.03  0.8661   0.836
       8                    1.17  0.8649   0.772   |              6.50  0.7549   0.542
      16                    1.00  0.8630   0.756   |              1.13  0.5916   0.094

**At LAMBDA=2 the shared kernel reaches 3.53 taps against a true filter of K=3**, at an accuracy cost
inside the error bars (0.9057 -> 0.8986). Raising LAMBDA further drives it past the target (2.13, 1.17,
1.00), so nothing structural held it at 5.07: the earlier floor was the energy weight being too weak to
ask for K, and `LAMBDA=1` was an unexamined choice inherited from the emerge_local objective's scale.

**The high-LAMBDA rows are the sharpest statement of the mechanism.** At LAMBDA=16 both arms are driven
to width-1 units, but `rewire-rand` holds coverage 0.756 and accuracy 0.863 while `no-rewire` collapses
to coverage 0.094 and accuracy 0.592, near chance. Same width, same pressure; the only difference is
whether units may move. Under add/remove-only every window stays pinned at `start=0`, so width-1 units
pile onto one input and the network sees a single pixel. Rewiring spreads them. When energy forbids
growing, function survives only if placement is free.

**Remaining gap:** at LAMBDA=2 coverage is 0.886, not ~1, so the tiling half of the convolution
criterion is close but not met. Width and sharing are there; a clean tiling is not. Whether the width
and coverage optima can be met at one LAMBDA, or whether they trade off, is the next question
and is a two-parameter question (LAMBDA against PSLIDE) rather than another one-dimensional sweep.

**Thread 2 summary.** Rewiring is necessary for compaction and add/remove provably cannot supply it;
the spatial neighbourhood prior is unnecessary and only slows the search by a factor of about twenty;
the compact kernel reaches K at LAMBDA=2; the tiling does not. Every constant in the probe has now been
swept: the arm, PSLIDE, LAMBDA, and GENS (the 0-generation control).

## Tried and rejected: efficiency (learning-curve) fitness

The two-level structure is: an inner objective trains the net, an outer fitness scores the topology by
the quality of that inner learner. The code collapses the whole inner process to one scalar, the
endpoint at a fixed `TEPOCHS`. Proposal: score the *trajectory* instead (accuracy at equal iterations,
or the area under the learning curve), so that fitness measures learning efficiency rather than a
single endpoint, and keeps a gradient where final accuracy saturates.

`run_net` was extended to evaluate every 5 epochs and return AULC, then compared against final accuracy
on the placement axis (widths pinned at K, sharing on, energy identical by construction).

**Rejected on this probe.** Two-way variance decomposition, 16 *fixed* placements x 24 task seeds, so
the placement main effect is signal and the residual after removing the task effect is noise:

    metric              sd_placement  sd_residual  signal/noise  F(placement)
    final accuracy           0.07705      0.05416          1.42          49.6
    AULC                     0.07187      0.05576          1.29          40.9
    (6 best placements, the compressed regime)
    final accuracy           0.02584      0.02649          0.98          23.8
    AULC                     0.02370      0.02465          0.96          23.2

AULC has a smaller placement effect and a larger residual: strictly worse, overall and in the
compressed regime. `epochs-to-0.85` is worse still and is censored at its maximum for every low-coverage
placement, since those never reach 0.85 at all: another thresholded metric that cannot rank the cases
that most need ranking.

**A false positive was produced on the way, and it is worth recording.** Conditioning on
`final acc >= cut` and comparing spreads showed AULC 2.72x more discriminating among the genomes that
cleared 0.90. That is selection on the dependent variable: conditioning on final accuracy compresses
final accuracy's spread by construction while leaving AULC's untouched. The apparent advantage was made
by the comparison, not by the metric. The fixed-placement decomposition is the valid test.

**Why it failed, and where it would not.** On this probe the inner learner converges well inside its 50
epochs, so the endpoint is a sufficient statistic for the trajectory and the curve contributes only
early-training noise. Efficiency fitness cannot beat accuracy once accuracy has converged. The
condition it needs is an *unconverged* inner learner, which is exactly what the budget ladder found in
`emerge_compose`, where accuracy at depth rose +0.217 with more epochs and data, so the endpoint there
was reporting optimization progress rather than architecture quality. If this idea is revisited, the
depth probe is the candidate, not the locality probe.

**New pre-check, in the spirit of `objcheck`:** before choosing an outer fitness, measure whether the
inner learner has converged within its budget. Converged -> use the endpoint and do not pay for the
curve. Not converged -> the endpoint is confounded with training speed, and either the trajectory or an
explicitly stated and swept budget is required.

If ever built for real: iterations, never wall-clock (wall-clock rewards cheap architectures, silently
re-charging the energy term, and makes fitness hardware-dependent), and area under the curve, never
epochs-to-threshold.

### Data sweep: the depth ceiling is structural, not budget of any kind

The epoch ladder left one hypothesis standing: D lost accuracy at depth with 4x epochs at fixed data,
which is overfitting, so the remaining ceiling looked data-limited. Two more levels at fixed
`TEPOCHS=1500`, varying only `NTR`, same 32 seeds, s=6 and s=8, L=1..8:

    peak accuracy      s=6 (need L=3)        s=8 (need L=4)
      B   768 train       0.802                 0.785
      F  1536 train       0.805                 0.808
      G  3072 train       0.795                 0.810

Data saturates exactly as epochs did. Across the whole ladder the budget now spans **20x in epochs
(300..6000) and 16x in training data (192..3072)**, and peak accuracy never leaves 0.79..0.81. The 0.85
target is not reached at any budget in any direction.

**This settles it in paper 1's favour.** The composition negative is not an artifact of a small
training budget, and the reading after level B alone (that it looked budget-dependent) was wrong.
The overshoot is budget-converged too: tied sets are {5,6} at s=6 (overshoot +2..+3) and {5} at s=8
(+1) at every level from B onward, unchanged by F and G. What remains conditional is only the
*approach* to convergence, not the converged value, so a selected-depth number is safe to report once
the budget is stated and shown to be past saturation.

### LAMBDA x PSLIDE: the compact kernel and the full tiling are not simultaneously selectable

The open item from the LAMBDA sweep was whether width -> K and coverage -> 1 can be met at one setting
or trade off. 3x3 grid, `rewire-rand`, 30 seeds (run on `emerge_rewire2`):

    LAMBDA  PSLIDE      max-w          coverage        test acc
         1    0.05   6.33 +- 0.60   0.933 +- 0.022      0.912
         1    0.15   5.07 +- 0.54   0.925 +- 0.024      0.906
         1    0.40   5.07 +- 0.51   0.917 +- 0.027      0.912
         2    0.05   3.90 +- 0.54   0.897 +- 0.024      0.887
         2    0.15   3.53 +- 0.46   0.886 +- 0.025      0.899
         2    0.40   2.83 +- 0.33   0.900 +- 0.025      0.895
         4    0.05   2.13 +- 0.18   0.839 +- 0.029      0.886
         4    0.15   2.13 +- 0.33   0.839 +- 0.029      0.882
         4    0.40   1.73 +- 0.14   0.828 +- 0.026      0.878

**They trade off.** Coverage falls monotonically as LAMBDA tightens the kernel, 0.933 down to 0.828,
and no cell reaches both targets; the closest is LAMBDA=2, PSLIDE=0.40 at a 2.83-tap kernel and 0.900
coverage. PSLIDE helps a little at fixed LAMBDA (3.53 -> 2.83 at LAMBDA=2) but cannot buy coverage back:
rewiring controls how *reachable* a configuration is, not what the objective *wants*.

This is the same conclusion `objcheck` reached from the other direction, now measured inside a running
search: a parameter-counting prior cannot supply coverage pressure, so tightening it necessarily spends
coverage. Getting both would require the tiling to come from the data term. Two independent routes to
one statement is worth more than either alone.

## Code layout for paper 2 (and later)

`validation/paper2/`, additive; every paper-1 probe is untouched and stays that way while the paper is
under review.

- **`emerge_rewire2.c`**: version 2 of the rewire probe. Self-contained, no indirection, reads top to
  bottom through TASK / GENOME / INNER LEARNER / FITNESS / OUTER SEARCH / PROTOCOL. Substantive changes
  over version 1: the inner learner records a learning curve; a **convergence check** runs by default
  and states whether the endpoint is a faithful summary of the learner; and the fitness is one named
  function rather than an expression buried mid-probe, which is how a step objective went unexamined.
- **`common.h`**: the shared leaves, under one rule: **share what cannot change a number, duplicate
  what can.** RNG streams, env parsing, protocol reporters. It never calls into a probe and never draws
  a random number itself. Task, genome, mutation, inner learner and fitness are barred from it: a
  shared version of those would hide the thing under test.
- **Makefile**: four auto-globbing lines, so a new probe needs no Makefile edit, and paper 3 is the
  same four lines with the directory changed.

**Acceptance test, and it passed:** `emerge_rewire2` reproduces `emerge_rewire.c` and the archived
per-seed data (commit 70e6ea0) **exactly**: all 90 RAW rows byte-identical. Any future refactor of
`common.h` must rerun it, because a bug there would move every paper-2 probe at once. That is the price
of not duplicating, and it is only worth paying because the oracle exists.

**Note for the port of `emerge_compose`:** it has no GA and no fitness function (it enumerates depths
and applies a selection rule), so it does not fit the inner-learner-plus-outer-search shape and should
not be forced into it. Its faithful version 2 is inner learner + enumeration + an explicit, selectable
selection rule (target-crossing vs argmax vs tied set), which is a different template.

## Topology crossover: implemented, tested, null, and the coverage confound found on the way

### The operators

`emerge_rewire2.c` arms 3-5, all inheriting arm 2's placement mutation so that recombination is the
ONLY difference from the mutation-only arm:

- **3 xover-canon**: units sorted by position, then each unit taken from either parent.
- **4 xover-raw**: same, WITHOUT the sort.
- **5 xover-block**: a contiguous run of whole units copied from the other parent (the structural
  clone, closest to the "vegetative reproduction" idea).

Recombination over STRUCTURES, not over a NAS-style encoding string: a genome here is a set of units,
each a whole little structure, so crossover exchanges units.

The 3-vs-4 pair exists because this genome has permutation symmetry: any unit may look anywhere, so
two parents holding the same solution in a different order are different genomes, and recombining by
index mixes incompatible conventions. That is the classic competing-conventions failure and was the
live candidate for paper 1's four-operator crossover null. Canonicalising costs nothing; arm 4 omits
it, so the pair measures operator design against the space, which is the question paper 1 says it most
wants answered.

The second parent costs one extra `r32()`, drawn only when an arm recombines, so arms 0-2 consume the
same stream as before. Verified: arms 0-2 stayed byte-identical to `scratch_rewire_main.out` through
every change in this section.

### Result: null, and not for either of the reasons expected

Paired against arm 2, 30 seeds, LAMBDA=1, PSLIDE=0.15:

    arm            d coverage         d max-w    d test acc
    xover-canon   +0.0056 (t= 0.42)     +0.80    +0.0099 (t=2.25)
    xover-raw     -0.0056 (t=-0.49)     -0.30    +0.0022 (t=0.67)
    xover-block   -0.0111 (t=-0.75)     +0.00    +0.0061 (t=1.94)

**No arm moves coverage**, which was the target. Small accuracy gains appear but canon pays for them
in width (+0.80 on max-w), and on the objective actually optimised (acc - energy) the arm WITHOUT the
conventions fix wins: raw 0.8636, canon 0.8593, mutation-only 0.8546. So competing conventions is not
the explanation for the null.

### The diversity hypothesis, tested and refuted

Proposed explanation: POP=24 with ELITE=4 and truncation selection collapses the population, so both
parents come from four near-identical elites and recombination copies a genome onto itself. `ELITE`
was a hardcoded, never-swept constant sitting directly upstream of a null: protocol item 3.

Made runtime, swept 4/8/12/18, with population diversity (mean pairwise genome distance) now MEASURED
rather than inferred:

    ELITE  diversity(arm2)  obj arm2  obj xover-raw   paired d(objective)
        4          0.0723     0.8635         0.8681   +0.0047 (t= 1.13)
        8          0.0922     0.8605         0.8629   +0.0024 (t= 0.72)
       12          0.1023     0.8630         0.8546   -0.0084 (t=-1.91)
       18          0.1151     0.8441         0.8400   -0.0041 (t=-0.93)

**Refuted.** Diversity at ELITE=4 is 0.072, not zero: the population had not collapsed. The knob works
(diversity rises steadily to 0.115). And crossover's edge does not improve with diversity: it decays
and turns negative. More raw material, no benefit.

So the crossover null survives both explanations offered for it. On this genome, at this scale,
recombination adds nothing that mutation plus rewiring does not already provide.

Incidental: ELITE=4, hardcoded and never swept, is the best value on the objective across the sweep.
An unswept constant that survives sweeping, for once.

### THE COVERAGE CONFOUND: applies retroactively to results above

**The seed genome is width 12 at coverage 1.000, the maximum of both.** Every search in this line
starts at full coverage and moves away from it. Therefore ANY manipulation that slows the search
inflates coverage, and coverage cannot be read as an outcome without conditioning on how far the
population has travelled from the seed.

The ELITE sweep shows it directly: arm 2 goes coverage 0.876 -> 0.961 as ELITE rises 4 -> 18, with
max-w rising 5.11 -> 8.28 alongside it, while the objective FALLS 0.8635 -> 0.8441. Weaker selection
is simply worse search wearing a better coverage number.

This is the free-variable failure of protocol item 2 in a new costume, and it applies to the
LAMBDA x PSLIDE grid recorded above: part of the coverage decline as LAMBDA tightens is the search
travelling further from the seed, not a genuine trade-off against width. The grid's *conclusion*,
that the compact kernel and the full tiling are not simultaneously selectable, survives, because
`objcheck` reached it independently and analytically. But the grid's coverage numbers should not be
quoted as a measured trade-off curve without conditioning on distance-from-seed.

**And it reframes the question.** "Does the tiling emerge?" is not quite the right question for this
genome. The tiling is present at generation zero; compaction spends it. What should be asked is
whether anything RETAINS the tiling while the kernel tightens: a different experiment, and one that
explains why every knob tried so far trades one against the other.

## THE HEADLINE: the objective does not have the convolution as its optimum

Everything in thread 2 above (operators, recombination, seed direction, LAMBDA, PSLIDE, ELITE, epoch
and data budgets) was tuned in pursuit of a target the fitness function ranks BELOW what the search
already reaches unaided. Score the target by hand and the whole thread collapses into one fact.

### The measurement

Build the thing the probe claims to hunt (shared weights, width exactly K=3, windows tiling the
input) and score it under the same objective, same tasks, same trainer (new `PROTOCOL target` check
in `emerge_rewire2.c`):

    ideal convolution (w=K=3, tiled)   fitness 0.7917
    w=K+1 variant                      fitness 0.7725
    what the search finds (arm 2, minimal seed, LAMBDA=1)   0.890 acc - 0.0279 energy = 0.8621

**The search beats the hand-built convolution by ~0.07, about ten times the standard errors involved.**
The comparison is conservative: the ideal's number is a validation fitness (what selection uses) and
the evolved genome's accuracy is held out, and it still wins by 0.073 on raw accuracy before energy.

The objective is not blind near the target: it ranks K above K+1 at every budget tested. It can see
the neighbourhood. It simply prefers somewhere else, by a lot.

### It is not an optimization artifact

The obvious objection is the `emerge_compose` failure mode: an endpoint at a fixed epoch budget
reporting how far training got rather than what the architecture can do. The ideal is a bigger, slower
net than the evolved mixed-width genomes, so it might merely be undertrained. Tested over a 16x range:

    EPOCHS      ideal (w=K, tiled)    w=K+1     convergence gain
        50                  0.7917    0.7725             -0.0047
       200                  0.7736    0.7581             -0.0065
       800                  0.7661    0.7517             -0.0067

It gets WORSE with more training (overfitting, not undertraining) and moves away from 0.862 rather
than toward it. The deficit is preference, not budget.

### What the search finds instead, and why it wins

Mixed-width units (mean 1.46, max 2.68) all sharing ONE kernel tied by within-window offset, so a
width-1 unit uses the kernel's first tap, a width-2 unit its first two, and so on. That is a shared
kernel read at several scales (a multi-scale filter bank), and ten identical width-3 windows cannot
express it. On this task that is worth about 0.07 of accuracy.

Note this holds even though the task is GENERATED by a 3-tap filter slid over all positions. Matching
the generative form is not the same as maximising this objective on finite data with this readout.

### Why this reframes the whole thread rather than adding to it

By the project's own premise (pass everything into the function, let search generate the solution,
treat parameters and methods as implementation), naming "the convolution" as the target was the
error, and the search outperforming it is the method working as specified. The interesting content is
WHAT it found, not that it failed to find what a human named.

It also explains, in one stroke, several results recorded above that were each given their own local
explanation: the kernel never stopping at K under any LAMBDA; the coverage plateau; and three separate
crossover nulls (against competing conventions, against population diversity, and in the assembly
regime that should have favoured recombination). None of them were operator failures.

### New standing protocol item: score the target

`objcheck.c` asks whether the objective can SEE the outcome axis. This asks whether the objective
WANTS the target you named:

  1. hand-build the target genome and score it under the exact objective, on the same tasks;
  2. hand-build a deliberately worse neighbour and confirm the objective orders them correctly;
  3. compare both against what the search reaches;
  4. sweep the training budget before concluding, so a slow-training target is not mistaken for a
     dispreferred one.

If the search beats the hand-built target, stop tuning operators. No operator, budget, seed or
recombination scheme will produce a structure the fitness function ranks second. Change the target or
change the objective.

Cost of this check: minutes. Cost of not running it: this thread.

### Boundary worth stating, since "ideally everything is searched" invites crossing it

Machinery can be searched (PSLIDE, PGROW, PSHARE, the operator choice itself, arguably selection
pressure), and paper 1 already shows self-adaptation works here (rate in the genome, log-normal
perturbation at birth, wins consistently). But LAMBDA is a coefficient of the FITNESS FUNCTION, not
machinery. Put it in the genome and the search drives it to zero, because the cheapest way to score
well on `acc - lambda*energy` is to stop charging for energy. An objective cannot self-adapt.
