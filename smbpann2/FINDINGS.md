# smbpann2: findings

Work of 2026-08-08 to 08-10. Paper 1 (`../smbpann/emergence.tex`, under review at GPEM) is unaffected;
one correction was applied to it and is described below.

- Full measurement log, dead ends and refuted hypotheses: **`FINDINGS_PREV.md`**
- Transferable lessons, as pre-flight checks: **`PROTOCOL.md`** items 4 and 9-11
- Every number here regenerates from a probe in `../../smbpann/validation/paper2/`, with per-seed data
  archived in that repo as `scratch_*.out`

---

## The arc, in three sentences

The structure-discovery direction failed for a reason that had nothing to do with operators: **the
objective ranked the hand-built convolution below what the search found unaided**, replicated on three
models with three energy definitions. A task was then built in which the convolution genuinely *is* the
optimum, verified by enumeration across a 48-fold LAMBDA range. On that task the search converges on a
structure worth +0.10 over a size-matched random support and still **misses the target by 0.078**, and
neither the operator set built across this direction nor a twelvefold budget increase recovers it.

---

## 1. The objective did not want the convolution

Hand-build the target, score it under the same objective on the same tasks, and the search beats it:

    ideal convolution (w=K=3, tiled, shared)   0.8176 +- 0.0127  (n=40)
    same at width K+1 (worse neighbour)        0.8036 +- 0.0126  (n=40)
    what the search finds unaided              0.8693 +- 0.0045  (n=30)

0.052, about 3.8 standard errors, and it does not close over a 16x epoch range, so the deficit is
preference and not undertraining. Caveats, all conservative: unpaired task-seed streams, and the target
scored on validation against the search's held-out test.

**Replicated three times** — window genome with prefix-tied weights, offset kernel with an L0 tap
count, and the same kernel under an L1 relaxation. Every time the search's own answer is smaller than
K, usually not contiguous, and scores higher.

**Why**, mechanically: no task in this line asked weight sharing to do the thing it is for. Every
position appeared in training and the label summed over all of them, so sharing cost nothing extra and
bought nothing either, and a smaller scattered support won on energy.

## 2. Descending the energy is worse than selecting on it

`emerge_relax.c` puts descent and selection on one model with one scorer. A structure is a binary
support over 21 offsets; four producers propose supports (L1 relaxation with a proximal step, a GA, the
hand-built ideal, a tap-matched random support); one function retrains each from scratch and scores it,
so optimizers are compared by the structures they hand over, never by their own objective values.

    producer                 taps   contig   test acc   objective
    ideal (hand-built K)     3.00     1.00      0.832      0.7601
    GA (select on energy)    2.35     0.25      0.879      0.8225
    relax lambda=0.028       2.80     0.40      0.661      0.5941   | tap-matched rnd 0.5755
    relax lambda=0.020      12.60     0.20      0.850      0.5502   | tap-matched rnd 0.5540

Relaxation does not find the target, does not come near the GA, and **a tap-matched random support
matches it at every lambda** — L1's structure does no work, only its size does. The non-organic
emergence analogy (crystals and convection cells relaxing an energy functional with no search) does not
transfer to this landscape.

## 3. A task where the convolution *is* the optimum

`emerge_transfer.c`. Two properties, neither predecessor had both: **sharing is a gene the search can
switch off** (`emerge_local` had this, but its task never charged for it) and **transfer to
never-trained positions is what pays for it** (`emerge_gen2` had this, but imposed sharing, which is
why its fitness was flat). Three disjoint position sets: train, select, report.

**The gate passes.** Enumerating all 231 contiguous shared supports, the planted width is rank 1, and
stays rank 1 across LAMBDA from 0.25 to 12 — a 48-fold range, so the *task* decides, not the tariff.

    producer                taps  shared contig  heldout   objective    paired vs ideal
    ideal conv (shared)      3.0    1.00   1.00    0.692      0.6774    --
    ideal support UNSHARED   3.0    0.00   1.00    0.437      0.2941    +0.383 (t=13.6) 20/20
    full support (shared)   21.0    1.00   1.00    0.582      0.4818    +0.196 (t= 8.4) 19/20
    tap-matched random       3.0    1.00   0.00    0.520      0.5058    +0.172 (t= 6.9) 19/20
    full support UNSHARED   21.0    0.00   1.00    0.426     -0.1454    +0.823 (t=26.2) 20/20
    GA (searches both)       6.0    1.00   0.15    0.628      0.5998    +0.078 (t= 2.8) 12/20

**Sharing is earned, not priced in.** At identical support the shared/unshared gap is 0.255 on held-out
positions, about twice the energy difference, and unshared sits near chance because it cannot transfer.
The GA chooses sharing in 20/20 seeds while selecting on transfer.

**What made it work, with its own control.** Negatives are a fresh random non-identity permutation of
the motif, so the magnitude multiset is identical between classes and no single tap can discriminate
(the first version's fixed rearrangement let one tap reach 0.746). A random-shape distractor sits
adjacent to the motif in both classes, so extra width bleeds into it and loses *accuracy* rather than
merely costing energy. **Turn the distractor off and width K+1 returns to rank 1 at 0.7530** — the
distractor is demonstrably what makes K optimal.

## 4. With a valid target, the search falls short of it

Operator arms pointed at it. This is the first interpretable operator result in the line, because it is
the first time the target was verified to be the optimum before the arms ran.

    objective            GENS=50   GENS=200   GENS=600
    ideal conv (target)   0.6774     0.6774     0.6774
    GA flip-only          0.5998     0.6047     0.6004
    GA flip+slide         0.5794     0.5716     0.6055
    GA flip+rewire        0.6200     0.5591     0.6051
    GA flip+xover         0.5882     0.5831     0.5809

Flat in both directions. No operator beats flip-only significantly (rewire +0.020, t=0.85, 10/20 wins;
slide and crossover slightly negative), and twelve times the generation budget moves nothing. Every arm
converges on six to eight scattered taps with contiguity near 0.05 against the planted three.

**The search is doing real work regardless:** a random support matched to the GA's own tap count scores
0.4952 against the GA's 0.60, so its structure is worth about 0.10 over its size alone. It converges
reliably, on something that is not the target.

**This reverses section 2's reading, and only now can it be read.** A search cannot be shown to fall
short of a target the objective ranks third; with a verified target it visibly does. Section 5 narrows
*why*, and the answer is neither the operators nor the algorithm.

## 5. Resolved: the selection signal, not the search and not the operators

The fork was "local optimum or noisy selection". The diagnostic returns a third answer that neither
branch anticipated, and it is the one that matters.

    what the SEARCH's own fitness (selection split) sees, 15 weight draws x 20 seeds
      target        selection-fitness 0.6351  sd 0.1180
      what GA finds selection-fitness 0.6280  sd 0.1365
      target wins a single draw 43.7% of the time      (50% = cannot tell them apart)
      separation = mean gap / pooled sd = 0.06
    seeding the whole population AT the target, 50 generations:
      taps 6.40   contig 0.05   objective 0.6325       (target is 3.00 / 1.00 / 0.6774)

**The target is not a fitness optimum under the search's own fitness.** Seeded directly at it, the
population walks away and lands where it lands from random init. On the selection split the two
structures are separated by 0.06 of a pooled sd, and the target wins a single draw *less* than half the
time. The search is behaving correctly given what it can see.

**The mechanism is selection overfitting, and the two gaps show it.** The target leads by 0.078 on the
reporting split and by 0.007 on the selection split. Both are held-out transfer, but the GA chose its
structure by maximising the selection split over roughly 1200 noisy evaluations (sd ~0.12) of a *fixed*
600-example set. It has fitted those examples, so its advantage there is inflated and disappears on a
split it never saw.

**So section 4's reading needs narrowing.** It is not the search algorithm, and not the operator set:
it is that the quantity being selected on is both too noisy to resolve the difference and reused often
enough to be memorised. That also explains cleanly why no operator and no budget helped — they were all
optimising a signal that does not rank the target first.

**Two fixes tested, and only one works — partially.**

*Resampling the selection examples every generation* (`RESAMPLE=1`, now the default) removes any fixed
set to memorise. It changes nothing: flip-only 0.5998 -> 0.6058, slide 0.5794 -> 0.6043, rewire
0.6200 -> 0.5788, crossover 0.5882 -> 0.5836, all within noise, all still at six to eight scattered
taps. So overfitting to particular examples was not the operative cause.

*Averaging the fitness over FEVAL weight draws* (`FEVAL`) attacks the variance itself, and it is the
first thing in this direction that moves the search toward the target (12 seeds, so noisier than the
20-seed tables above):

    FEVAL              1              4             12       (taps in brackets)
    ideal conv    0.6677         0.6677         0.6677        (3.0, contig 1.00)
    GA flip-only  0.6057 (6.5)   0.5751 (6.2)   0.6396 (5.2)
    GA flip+slide 0.5734 (6.7)   0.5853 (6.5)   0.5987 (5.2)
    GA flip+xover 0.6134 (6.2)   0.5568 (5.7)   0.5809 (4.9)

Tap count falls monotonically with averaging and the gap to the target roughly halves, 0.062 to 0.028.
It does not reach three contiguous taps, and contiguity stays near zero. Twelve draws puts the fitness
standard error near 0.034 against a 0.078 gap: enough to move the search, not enough to resolve the
target.

**So the binding constraint is the variance of the fitness estimate.** Not the operator set, not the
generation budget, not which examples are used. The variance lives in the weight draw and the training
run, which is why resampling data does nothing and averaging draws does something. It is reducible by
paying compute (roughly 35 draws for a standard error near 0.02) or by reducing training variance
directly, and neither has been pushed to the point where the target becomes reachable.

**What this reframes.** Every negative in this direction was measured with a fitness estimator whose
noise exceeded the effect being selected on. That does not retroactively validate the operators -- they
were also tested against a target the objective did not want, which is a separate defect -- but it does
mean no operator claim from this line rests on a signal capable of supporting it.

---

## 6. The deficit was a biased selection estimator. Repaired, the search matches the target
   functionally; what never emerges is alignment

Work of 2026-08-11. Pre-registered before any pilot in `PREREG_selection_signal.md`, with two
amendments (both gate failures) and the prediction verdicts scored before the LAMBDA sweep was read.
Every number below is 20 paired seeds through `./pairstat` (self-test PASSED), primary test Wilcoxon
signed-rank, archived as `scratch_rot_*.out` and `scratch_subscan_*.out`.

### The error in section 5

Section 5 prescribed ~35 weight draws to resolve a 0.078 gap. That conflated two quantities: 0.078
is the target's lead on the REPORTING split, which the search never sees; on the SELECTION split its
lead was 0.007. The two position sets are exchangeable random draws, so for a structure not chosen
using them the expected gap is identical on both. It was not. **The excess is therefore
selection-induced: the GA had overfitted WHICH positions it must transfer to** -- 3 fixed positions
at N=12 -- which is why `RESAMPLE` (fresh examples, same positions) changed nothing.

Measured directly, DIAG's new exchangeability lines: excess (report gap minus selection gap)
**0.0312 at ROTPOS=0, -0.0140 at ROTPOS=1.** Eliminated, not merely reduced.

### The fix

`ROTPOS=1` redraws the selection POSITIONS every generation from the whole non-train pool -- the
position analogue of RESAMPLE. No fixed subset to fit, so the selection mean estimates the same
transfer the report measures. Cheap, and it changes no task constant.

Two structural alternatives were tried first and both FAILED their gate, which is why rotation was
chosen: enlarging to N=16 put the planted width at rank 5 of 435, a DAMP sweep (0.9/1.1/1.4) made it
worse, and a two-sided distractor degraded even the passing N=12 gate to rank 3. The one-sided
distractor's left flank exists at only 3 of H positions, so it dilutes as N grows and no strength
restores it. Archived: `scratch_t16_dampscan_*.out`, `scratch_t{12,16}_dboth_scan.out`.

### The result: functional equivalence without structural convergence

Flip-only arm, ideal convolution = taps 3.0, contig 1.00, heldout 0.692:

    cell                taps  contig  heldout  objective gap to ideal   p(Wilcoxon)
    baseline, no fix     6.7    0.00    0.635          0.0745            0.0049  **
    rotation only        7.1    0.10    0.663          0.0479            0.202
    averaging only       5.7    0.05    0.683          0.0218            0.571
    both fixes           6.5    0.15    0.693          0.0151            0.275

**A significant deficit becomes an undetectable one.** Held-out transfer goes from a significant
0.057 deficit (16 wins/4 losses, p=0.021) to indistinguishable (-0.0013, HL -0.0025, CI
[-0.037,+0.033], 10/1/9, p=0.92). The search now transfers exactly as well as the hand-built
convolution while using twice the taps, scattered.

**The residual is entirely parsimony, and that is arithmetic.** Since objective = accuracy -
LAMBDA*energy, the gap decomposes, and across the four cells the functional deficit collapses
(0.057 -> 0.029 -> 0.009 -> -0.001) while the tap surcharge never moves (0.013-0.020). One tap is
worth LAMBDA/(NOFF*H) = 0.0048 against a per-evaluation sd of ~0.13, a factor of 27, so selection
cannot resolve individual taps at any faithfulness of the split.

**The search does heavy lifting throughout.** Against a null matched to its own tap count:
objective +0.1665 (HL +0.169, p=1.9e-05), held-out +0.150 (p=1.3e-04).

### The gate is stronger than it was, and one of my own hypotheses died on it

`SCAN` enumerates only CONTIGUOUS supports, so it never certified the target against the scattered
region the GA actually occupies. Hypothesis: the target was never really the optimum. **Refuted.**
New `SUBSCAN` enumerates all 127 subsets of the aligned 7-wide window, non-contiguous included:
planted target **rank 1 of 127**, and rank 1 again at LAMBDA 3, 6 and 12.

### Raising the tariff moves the structure monotonically, but never to the target

LAMBDA sweep at the repaired setting (ROTPOS=1, FEVAL=12), and `exact` = taps==3 AND contiguous:

    LAMBDA    taps  contig  exact      GA-vs-ideal objective (flip-only)
    1          6.5    0.15   1/20      +0.0151  p=0.275
    3          3.5    0.35   2/20      HL -0.0004  p=1.00   (dead tie)
    6          2.5    0.45   5/20      HL +0.0024  p=0.669  (dead tie)
    12         1.7    0.50   4/20      GA BEATS ideal (0.5537 vs 0.5202)

Taps fall monotonically as predicted and exact structural matches rise 0/20 -> 5/20. **The
contiguity column is confounded** -- a 1-tap support is trivially contiguous -- which is the defect
NOTES.md flagged for `reg`; the `exact` column is the honest metric and it survives the confound
(at LAMBDA=6 a 3-tap support is ABOVE the mean size of 2.5, so it is not a degenerate collapse).

Two limits, both real:
- **0/20 -> 5/20 is exact McNemar p=0.0625.** Marginal, not significant at n=20. This is the single
  claim worth more seeds, and a 60-seed factorial (fixes x tariff, 4 cells) is running.
- **At LAMBDA=12 the GA beats the hand-built target** (0.5537 vs 0.5202), so the target is not
  GLOBALLY optimal there even though it is rank 1 within its own window. The valid tariff window is
  bounded above somewhere below 12, and the earlier "argmax to LAMBDA=12" claim rested on a
  contiguous-only scan -- the same flaw `SUBSCAN` was written to close.

### What this direction now is

Three separable barriers to the emergence of a convolution, each identified by measurement and each
a property of the SEARCH's instrumentation rather than of the architecture space:

1. **The objective must rank the target first.** Sections 1-2; took a purpose-built transfer task.
2. **The selection estimator must be unbiased.** New here: position overfitting, removed by rotation.
   Closes the functional gap completely.
3. **The per-unit signal must exceed the noise floor.** Parsimony; responds monotonically to the
   tariff but has no setting that both keeps the target optimal and delivers it.

Written before the 60-seed factorial, the reading here was that alignment never emerges. **The
factorial overturns that**: with both barriers removed alignment does emerge, in 22% of runs against
2% at baseline (p=0.0018), and a tap-matched null never produces it. What survives as the honest
limit is narrower and more interesting -- the planted convolution is a reachable, selectable local
optimum rather than the global one, and the majority of runs still prefer a slightly better
non-aligned support. See the factorial and its two corrections below.

This is directly analogous to validation-set overfitting and noisy ranking in real NAS, which gives
it an audience the retracted `tiling.tex` framing lacked.

### Reproduction

Committed on branch `validation/selection-signal` as `b697298`, with all 22 archived outputs. Build
`make emerge_transfer`; for the abandoned N=16 arm,
`cc -std=c99 -W -Wall -O2 -DN=16 -o emerge_transfer16 validation/paper2/emerge_transfer.c -lm`.

    the gates          SCAN=1 SPLIT=2 SEEDS=20 ./emerge_transfer      -> scratch_scan_split2.out
                       SCAN=1 SPLIT=1 SEEDS=20 ./emerge_transfer      -> scratch_scan_split1.out
                       SUBSCAN=1 SUBW=7 SEEDS=20 LAMBDA=L ./emerge_transfer
    the mechanism      DIAG=1 ROTPOS={0,1} ./emerge_transfer          -> scratch_rot_diag_r*.out
    the four cells     RAW=1 ROTPOS={0,1} FEVAL={1,12} ./emerge_transfer
    the tariff sweep   RAW=1 ROTPOS=1 FEVAL=12 LAMBDA={3,6,12} ./emerge_transfer
    paired statistics  awk -f reshape.awk FILE | GROUP=2 \
                         METRICS=taps:4:8,contig:5:9,heldout:6:10,objective:7:11 ./pairstat
      where reshape.awk turns the per-arm RAW rows into pairstat's paired layout:
      /^RAW/ { if($2==0){ it[$3]=$4; ic[$3]=$6; ite[$3]=$8; io[$3]=$9; next }
               printf "RAW %d %d %s %s %s %s %s %s %s %s\n",
                      $2,$3, it[$3],ic[$3],ite[$3],io[$3], $4,$6,$8,$9 }
      pairstat groups are the arms: 1 flip-only, 2 slide, 3 rewire, 4 xover, 5 tap-matched null.
      Differences are ideal-minus-GA, so a POSITIVE objective difference is a deficit for the search.

**Measured cost, for planning long runs.** 20 seeds x 4 arms: 27 s/seed at FEVAL=1 (9 min total),
**5.65 min/seed at FEVAL=12** (113 min total), single-threaded, one process per cell. FEVAL multiplies
the GA's fitness evaluations directly (1224 per arm per seed x FEVAL), so a 60-seed FEVAL=12 cell is
about 5 h 40 m. The enumeration modes are cheap: SCAN 231 supports ~25 s, SUBSCAN 127 subsets ~2 min,
both at 20 seeds.

### The 60-seed factorial: the planted convolution DOES emerge, and both factors are needed

Ran 2026-08-11 14:33-20:2x, four cells, `RAW=1 SEEDS=60`, ROTPOS/FEVAL in {(0,1),(1,12)} x LAMBDA in
{1,6}, archived as `scratch_fact_r*_f*_lam*.out`. `exact` = the returned support has 3 taps AND is
contiguous, i.e. it IS the planted structure. Flip-only arm:

    exact matches / 60      LAMBDA=1     LAMBDA=6
    no fixes (r0,f1)          1/60         6/60
    both fixes (r1,f12)       2/60        13/60
    tap-matched null          0/60         0/60

Exact McNemar on the same 60 seeds, all four surviving Holm correction over the declared family:

    baseline (no fix, lam1) 1/60  ->  both fixes at lam6 13/60    p=0.00183   Holm 0.0055
    at lam6, no fix 6/60    ->  both fixes 13/60  (b=8, c=1)      p=0.03906   Holm 0.0391
    with fixes, lam1 2/60   ->  lam6 13/60        (b=12, c=1)     p=0.00342   Holm 0.0068
    at lam6 fixed, null 0/60 -> flip-only 13/60   (b=13, c=0)     p=0.000244  Holm 0.0010

**Both barriers are independently significant and neither alone suffices.** The tariff raises exact
matches 2 -> 13 with the fixes in place; the search fixes raise them 6 -> 13 at fixed tariff. The
outcome I flagged in advance as most worth guarding against -- the tariff alone doing all the work --
did not happen. Consistent across arms at LAMBDA=6 with fixes: flip 13, slide 11, rewire 14, xover 14
of 60. **The tap-matched random null is 0/60 in every one of the four cells (0/240 overall)**, so an
exact match is never a coincidence of tap count.

The rewire arm is the exception worth naming: 9/60 without the fixes against 14/60 with them,
p=0.227. Rewire already moves taps at constant count, so it recovers part of what the repaired signal
buys, and the fixes add nothing significant on top of it.

### Two corrections the larger seed count forced, both against the earlier reading

**The 20-seed gate was optimistic, and the gate has to be re-run at the seed count used.** At 60
seeds and LAMBDA=1 the planted target loses its rank-1 position, where at 20 seeds it held it. The
first 20 task draws were simply easier: the ideal's own held-out accuracy is 0.692 over those seeds
and 0.636 over all 60. Every 20-seed number in this section stands as measured but should be read as
the easy-seed subset.

**And the gate itself was under-resolved -- an ordering inside its own noise.** One draw per seed
gives each mask a standard error of 0.13/sqrt(60) = 0.0168, against a margin between the planted
support and its nearest rival of 0.0108. The rank was therefore not supported by the measurement,
however clean the number looked. `SUBSCAN` now takes `DRAWS`, averaging weight draws per (mask, seed),
and prints the standard error and the margin in SE beside the ranking so this cannot recur. At
DRAWS=12 x 60 seeds the error falls to 0.0048 and the picture resolves
(`scratch_subscan_hi_lam{1,6}.out`):

    LAMBDA   planted objective   rank of 127   margin over best rival
    1             0.6082              4            -0.0085  (-1.7 SE)
    6             0.5367              1            +0.0111  (+2.3 SE)

**This answers "why only 22%".** At LAMBDA=1 the planted convolution is *not* the optimum -- it is
rank 4, beaten by a width-4 and two wider supports -- so a search that does not return it is behaving
correctly, and 2/60 is the right answer rather than a failure. At LAMBDA=6 it *is* the optimum,
resolved at 2.3 SE, and there the search returns it 13/60 with the fixes against 6/60 without.
**The tariff is what makes the convolution optimal; the signal repair is what makes it findable.**
The two panels of the factorial were measuring two different things and now say so.

Of the 47 non-matching runs at LAMBDA=6 with fixes, **25 score ABOVE the ideal on their own seed and
22 below** (mean +0.0104), so roughly half of the shortfall is the search finding something better on
that draw rather than failing. 35 of 60 seeds (58%) end at least as good as the hand-built
convolution.

**A ceiling measurement that does NOT work, recorded so it is not retried.** `PERSEED` was written to
ask how often the planted support is the argmax of a single task draw, as a ceiling on any exact-match
rate. It reports 8% at both tariffs with a mean margin of -0.085, and **the number is an artifact**:
it takes the argmax of one noisy evaluation per mask, and the maximum of 127 noisy estimates is
whichever mask got lucky. The bias is about the size of the reported margin. Measuring the true
per-seed ceiling needs the argmax of 127 masks resolved to well under their ~0.01 spacing, i.e. of
order 1000 draws per mask per seed -- roughly 12 hours at 60 seeds -- so it is not affordable here and
the honest statement is that the per-seed ceiling is unmeasured. `scratch_perseed_lam{1,6}.out` are
kept as the record of the flawed attempt, not as evidence.

### The overnight runs (2026-08-11 21:09 to 08-12 12:14): stronger AND narrower

Three jobs, `scripts/overnight_ceiling.sh` then `scripts/overnight_lamwindow.sh`, seed-split across 8
cores. My ETA of 07:10 was wrong by four hours (actual 12:14): the 5.77 ms/evaluation figure was
calibrated on a 4-process run, and at 8 processes memory contention makes every phase ~40% slower.

**Job 2, 240 seeds at LAMBDA=6 -- the weakest link became the strongest.**

    exact recovery / 240      no repairs   both repairs   null
    flip-only                  16 (6.7%)    42 (17.5%)     1
    slide                      15           39
    rewire                     22           39
    xover                      16           48

Exact McNemar, same seeds: no repairs -> both is `b=34, c=8, p=0.00007` (was p=0.039 at 60 seeds);
null -> flip-only is `b=41, c=0, p<1e-7`. **The null is 1/240 here, not 0**, so the "0 of 240" above is
true of the 60-seed factorial's four cells only and must not be carried into this run.

**Job 3a, the tariff window -- reading ranks alone would have overstated it badly.**

    lambda        1      2      3      4      6      8     10
    rank of 127   4      2      1      1      1      1      1
    margin (SE) -1.7   -0.8    0.2    1.2    2.3    2.3    0.4

By rank the target is argmax across all of LAMBDA in [3,10]; by margin it is **resolved only at 6 and
8**, and at 3, 4, 10 it ranks first on an ordering its own noise cannot support. The objective's
preference for the planted width peaks in a band and decays both ways -- below it wider supports win on
accuracy, above it narrower ones win on the tariff. Report [6,8]. This also settles the cherry-picking
question: LAMBDA=8 is equally good, so 6 is not a lone tuned cell.

**Job 3b, a real coherence.** Recovery rate tracks the gate margin -- two independently measured
quantities rising and plateauing together:

    lambda             3        4        6        8
    exact / 60      8 (13%) 11 (18%) 13 (22%) 13 (22%)
    mean taps         3.63     3.12     2.38     1.83
    gate margin(SE)   0.2      1.2      2.3      2.3

**Job 1, the "ceiling" -- and my framing was wrong.** The planted support is the per-seed argmax of its
127-support neighbourhood on **8/60 seeds (13%) at LAMBDA=6**, 5/60 (8%) at LAMBDA=1, at 1000 draws per
candidate. It is *not* a ceiling: the search recovers the structure on 17.5% of runs, i.e. more often
than it is the best answer for an individual draw. The search never sees one draw -- it selects under
noise over 50 generations with rotating positions and 12-draw averaging, which estimates the objective
*averaged* over draws, and the planted support is rank 1 in that aggregate. The 13% is also **biased
downward** (in an argmax over 127 noisy candidates the true optimum loses to lucky rivals): the measured
rate rose 8% -> 13% as draws went 1 -> 1000, confirming the direction. So 13% is a lower bound, and the
honest statement is that recovery (17.5%) and per-draw optimality (>=13%) are the same order of
magnitude.

### THE CORRECTION THAT MATTERS: this is not an optimization result

At LAMBDA=6 with the repairs, 240 paired seeds, **the search BEATS the hand-built convolution**:

    objective   HL -0.0287, 95% CI [-0.0384,-0.0179], 149 wins / 70   p = 7.0e-08
    taps        2.30 vs 3.00                                          p = 1.7e-10
    heldout     indistinguishable                                     p = 0.276

and of the 198 runs that do not recover the planted support, **136 score above it on their own seed**, 62
below. Without the repairs the search sits slightly *below* the ideal (0.5224 vs 0.5301).

This does not contradict the gate. Enumeration finds the best **fixed** support averaged over task
draws; the search picks a support **per draw**, and a per-task adaptive choice should beat the best fixed
one. It also explains job 1 directly: per draw the planted support usually is not the best answer, and
the search finds what is.

So the defensible claim is **not** "the convolution emerges" in the sense of a search succeeding at
optimisation. It is:

> The planted convolution is the right answer for at least 13% of task draws, and the search returns it
> exactly on 6.7% of runs with a biased selection estimator and 17.5% with an unbiased one
> (p = 7e-05, null 0.4%). The repairs move recovery from about half the rate the task warrants to
> slightly above it.

Smaller than the earlier phrasing and the one the measurements support.

**Superseded, therefore:** "0 of 240" for the null (true only of the 60-seed cells); the 60-seed p=0.039
as the primary contrast (240 seeds give 7e-05); and the reading that "alignment emerges once two barriers
fall" (it is *recovered at a rate*, and the search outperforms it).

### The paper

`estimator.tex` -> `estimator.pdf`, 9 pages, builds clean. Title: *The Estimator, Not the Search:
Recovering a Planted Convolution at the Rate the Task Warrants*. Written to the corrected claim above,
with a dedicated section (\ref{sec:notopt}) stating why it is not an optimization claim, the tariff window
reported by margin rather than rank, and named paired statistics throughout (Wilcoxon primary, exact
McNemar for the structural counts, Hodges-Lehmann intervals, Holm across a declared family, MDE for
bounded nulls). Three `\pending{}` markers remain, all citation-verification under the
cite-only-what-you-have-read rule: the NAS validation-overfitting literature, and
Nowlan & Hinton 1992 / Elsayed et al. 2020 / d'Ascoli et al. 2019, plus Hubel & Wiesel and Fukushima.
Dead ends are cut from the paper per the author's instruction (N=16, DAMP sweep, two-sided distractor,
the flawed PERSEED mode, the retracted tiling history); they remain recorded here.

### The figure

`fig_barriers.py` -> `fig_barriers.pdf` / `.png`, four panels, every number from the archived probes:
(a) the exchangeability excess, 0.0312 -> -0.0140; (b) the functional deficit collapsing across the
four cells; (c) exact recovery, 240-seed cells at LAMBDA=6 beside the 60-seed LAMBDA=1 cells, plotted as
RATES because the denominators differ; (d) the whole tariff window, margin with +-2 SE, filled markers
where the margin clears the band. Palette is the two-colour categorical pair, checked for
normal-vision separation (dE 33.6), dichromacy (worst dE 26.5) and greyscale print (luminance gap
0.090), so it survives a black-and-white printer. Needs `/home/vas/.venv-figs/bin/python`.

**The planted convolution is not the global optimum, and the search proves it by construction.** At
LAMBDA=6 the GA's mean objective is 0.5593 against the ideal's 0.5502. Since 13 of 60 runs return the
ideal exactly, the remaining 47 must average about 0.5618, i.e. **the search finds non-aligned
supports that score slightly better than the planted one.** Enumeration cannot contradict this: SCAN
covers 231 contiguous supports and SUBSCAN 127 subsets of the aligned window, against a space of
2^21. So the honest claim is that the target is the optimum *of its neighbourhood and of the
contiguous family*, not of the space, and its emergence is therefore not reducible to "optimisation
succeeded". What the 1/60 -> 13/60 result says is that the planted structure becomes **reachable and
selected** once the estimator is unbiased and the per-tap signal clears the noise floor -- while a
slightly better non-aligned solution remains available and is what the other 78% of runs find.

---

## Paper 1

**Asset.** The composition negative is budget-independent: across 20x in epochs (300 to 6000) and 16x
in data (192 to 3072) the 0.85 target is reached at no budget. Past 768 examples the peak sits at
0.785-0.810 and does not move with 4x more data or 4x more epochs; below that the probe is genuinely
budget-limited, so the published claim needs that qualifier. The overshoot converges at +2..+3 for s=6
and +1 for s=8. **Strengthens a published result.**

**Correction, applied and verified.** Future-work originally attributed the spoken-digit null to the
optimal filter not being compact and local. Nothing in that pipeline reaches usable accuracy, so it
licenses no such claim. The sentence now says the attempt is inconclusive, that every support tested
lands between 0.54 and 0.59 held out, and that a thirtyfold epoch increase does not move it. `.tex`,
PDF and submission zip rebuilt and verified. Ready if the paper returns for revision.

**FSDD positive control: failed, and still outstanding.** Six of seven filter supports separate from
chance (t up to 8.7) but all land at 0.54-0.59 on a task a competent classifier solves above 90%, and
the optimum is a 5-9 tap support rather than the 3-tap one. A thirtyfold epoch increase does not move
it, which rules out training budget but does not isolate the front end. Nothing measured on that
substrate means anything until a known-good architecture works on it.

---

## Method: what actually caught the errors

Two adversarial reviews, by agents with no stake in the result, changed the conclusions twice.

The first audited `FINDINGS.md` against its own archived data and found four wrong claims: a standard
error inflated more than threefold, a headline statistic mixing best-individual accuracy with
population-mean energy, an accuracy range excluding 7 of 12 measured cells, and an FSDD claim that was
simply false. One of those had already reached the paper and had to be corrected twice.

The second red-teamed `emerge_transfer.c` before anything was built on it. The gate had passed cleanly
at 20 seeds and would have been written up; enumeration showed the target was **rank 3 of 231**, the GA
was selecting on training accuracy while every reported number was held-out, and the sharing verdict
was fixed by arithmetic before any data was seen.

Both are now standing checks in the probe: `SCAN=1` enumerates the whole contiguous family and prints
the ranking, and `LAMSCAN=1` reports the LAMBDA window in which the target is the argmax. "Beats the
five arms I chose" is not what protocol item 9 asks for; "is the argmax of a family" is.

## Tooling

- `emerge_rewire2.c` — TASK / GENOME / INNER LEARNER / FITNESS / OUTER SEARCH / PROTOCOL, six arms,
  protocol checks run by default and cannot be declined.
- `emerge_relax.c` — descend versus select on one model with one scorer, carries the tap-matched null.
- `emerge_transfer.c` — the transfer task, four operator arms, `SCAN` / `SUBSCAN` / `LAMSCAN` / `DIAG`
  modes. Knobs added 2026-08-11, every one env-gated with the default preserving archived behaviour:
  `ROTPOS` rotates the selection POSITIONS per generation (the fix of section 6); `SPLIT` chooses
  which split an enumeration scores, so a gate can be checked on the split the search actually sees;
  `SUBSCAN`/`SUBW` enumerate every subset of a window, non-contiguous included, which `SCAN` cannot;
  `NVP` sets the selection-position count; `DBOTH` flanks the motif on both sides (built for the N=16
  arm, failed its gate, left in place and off); and `N` is now a compile-time override.
  **The oracle applies to all of it**: a binary built from the unmodified HEAD source produces a
  byte-identical result table, verified twice (once mid-change, once after the last edit).
- `fsdd_target.c` — the positive control. Runs no search.
- `common.h`, `ga.h` — shared under *share what cannot change a number, duplicate what can*; `ga.h` is
  a compile-time template, not an interface, so there is no indirection.
- **An oracle.** `emerge_rewire2` reproduces `emerge_rewire.c` and the archived per-seed data
  byte-for-byte through every refactor, including extraction of the GA and the switch to inline
  headers. Independently re-verified during the audit. Any change to the shared headers must rerun it.
- The Makefile globs `validation/paperN/`, so a new probe needs no build edit.
