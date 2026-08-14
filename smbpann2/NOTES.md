# smbpann2 — lab notebook

**Paper (working title):** Does the Tiling Emerge? Which Energy Term Selects Which Half of a Convolution

**Author:** Vasili Gavrilov (ORCID 0009-0007-9371-5994)
**Started:** 2026-07-30
**Probe:** `~/smbpann/validation/emerge_tile.c`, target `make emerge_tile`
**Archived output:** `~/smbpann/scratch_emerge_tile.out`
**Rule for this project:** new probe only. No existing experiment in the repo is modified.

---

## 1. The question, and why paper 1 could not answer it

Paper 1 (*The Imposed and Emergent Pieces of Convolution Under an Energy Budget*, Zenodo
10.5281/zenodo.21423177, submitted to GPEM 2026-07-28) showed the compact **filter** emerges once
mutation acts on the shared offset rather than on one edge. But it bought that with an offset-mask
genome, and `emerge_offset.c` says so in its own header:

> "making the genome an offset mask also makes the connectivity translation-invariant by construction"

So the **tiling** — one filter reused across positions — was imposed, not emergent. That is the last
unfilled cell in paper 1's imposed-versus-emergent map, and it is what this paper attacks.

## 2. Design

**Genome.** Over `P = N-K+1` candidate window positions:
- `on[p]` — is there a hidden unit reading the K-window at position p?
- `g[p]` — which weight group that unit draws its taps from (0..P-1, so every unit *can* be its own)

**Exhaustive seed** = the locally-connected net: every position occupied, every position its own filter.
Nothing in the genome encodes translation. A convolution is one point in this space among many that
are not: ragged placements, full coverage with unshared filters, shared filters on a ragged subset.

**Two energy terms**, which is the whole idea. Paper 1's mechanism was that sharing *decouples*
connection count from parameter count. Pushed forward, the two halves of a convolution are charged by
two different costs:

| term | formula | sharing | placement |
|---|---|---|---|
| `E_param` | groups·K / (P·K) | dear | free |
| `E_conn`  | places·K / (P·K) | free | dear |

**Pre-registered prediction (written before running):** neither term alone selects a convolution.
`E_param` collapses groups to 1 and leaves coverage to the task; `E_conn` thins placements and leaves
filters unshared.

## 3. Two task versions, and why the first was wrong

**v1, summed response.** Label = sign of the motif response summed over all positions. **Failed as a
task:** accuracy 0.89 at 41% coverage, because the sum is predictable from a subset. Coverage drifted
freely once the accuracy threshold was met. That is a property of the task, not of the search.

**v2, detection (current).** A K-tap motif is planted at a uniformly random position, or absent. Now
missing a position means missing detections. Also dropped `NTR` from 64 to 24, following paper 1
§3.3 (the weight-sharing advantage grows as data thins). That opened the ceiling/floor gap from
0.008 to ~0.11, which is what makes the experiment able to discriminate at all.

## 4. Results (16 seeds, 80 gens, target 0.90)

```
                          cover  groups  reg   test   equiv-err  %conv
CONVOLUTION (ceiling)     1.00   1.0     1.00  0.835    0.278
locally connected (seed)  1.00   10.0    1.00  0.724    0.355

E_param (per group)       0.58   1.3     0.65  0.813    0.237     0%
E_conn  (per placement)   0.42   1.2     0.71  0.789    0.267     0%
both                      0.44   1.2     0.65  0.777    0.246     0%
random (matched budget)   0.53   3.1     0.65  0.721    0.276     0%
```

### What holds

1. **Directed search does real work.** `E_param` reaches 0.813 against the convolution ceiling of
   0.835, while matched-budget random sits at 0.721, i.e. at the locally-connected floor. Random also
   fails to share (3.1 groups vs 1.2). This is the paper-1 §2.4 result reproduced on a new axis.
2. **Sharing emerges, but not from the budget.** Groups collapse to ~1.2 under *every* cost term,
   including `E_conn`, which charges nothing for groups. So sharing here is driven by **data scarcity**
   (accuracy), not by the energy term. This *contradicts the second half of the prediction* and is more
   interesting than the prediction was: the sharing half of a convolution is selected by the task.
3. **The tiling does not emerge.** `%conv` is 0% everywhere and coverage tops out at 0.58. The search
   finds convolution's *accuracy* without convolution's *structure*: one good filter on a ragged subset
   of positions. This is the paper's central negative and it is a clean one.

### Open discrepancy, found by the equivariance measure

**The hand-built convolution scores equiv-err 0.278, worse than evolved `E_param` at 0.237.** That
should be impossible if the measure is right, and it is not noise. Cause: on a finite **non-circular**
strip, a convolution is genuinely *not* translation-equivariant. Interior positions are covered by more
overlapping windows than edge positions, so detection rate falls off at the boundary. The theorem
(below) is stated for the cyclic group.

**This is a real finding about the measurement, not a bug to hide.** Next run switches to circular
placement and circular motif planting, where equivariance is exact and the ceiling should go to
~0. Until then the equiv-err column is not interpretable across rows.

## 5. The theoretical anchor

A linear map is translation-equivariant **iff** it is a convolution. Classically this is harmonic
analysis; in ML the precise statement is **Kondor & Trivedi, ICML 2018** (a layer equivariant to a
compact group action is a generalized convolution), with **Cohen & Welling, ICML 2016** (Group
Equivariant CNNs) as predecessor and Bronstein et al., *Geometric Deep Learning*, as survey.

Why it matters here, and this was the author's move: we cannot tell from a placement diagram whether
what the search found "is a convolution." The theorem lets us **test the property instead of guessing
at the wiring** — plant the motif at each position in turn and take the spread of the detection rate.
Zero spread is equivariance. This is architecture-agnostic, so it transfers to any network structure
tested later.

Two honest caveats for the paper:
- The theorem covers *linear* maps and *exact* equivariance. This setup has a tanh per unit and a
  learned readout, so the theorem supplies the target point, not a proof that the whole search space
  reduces to it.
- The energy budget never asks for equivariance. So there is no a priori reason it should select it,
  which is exactly what the 0% `%conv` column shows.

**Citations to verify before they stand** (the cite-only-what-you-have-read rule): Kondor & Trivedi,
Cohen & Welling. Hubel & Wiesel (1962) and Fukushima (1980) are also owed here and are missing from
paper 1 as well (see `~/articles/smbpann/revision_notes_gpem.md`).

---

## 5b. Run 2 (2026-07-31): circular domain + the tiling macro-mutation

Author's proposal, implemented: per-position edits may be unable to build a tiling at all, because the
intermediate states are not fitter (half a tiling costs energy and buys nothing). Biology does not build
repeated structure one limb at a time either. So add a rare GLOBAL operator: pick a period T, repeat the
genome's first T slots across the whole range. **Serial homology** — the mechanism behind a millipede.
It confers periodicity, not a convolution; the search still picks the period and the filter.

Also this run: circular domain (P = N, wrap-around), and energy left as a per-neuron fraction so the
budget scales with network size rather than punishing it.

```
                        cover  groups  reg   test   eq-err  %conv  tilings
CONVOLUTION (ceiling)   1.00   1.0     1.00  0.851  0.207
locally connected       1.00   12.0    1.00  0.743  0.343

(1) local mutation only  (paper 1's mutation model)
  E_param               0.61   1.4     0.58  0.824  0.248    0%     0
  E_conn                0.49   1.4     0.59  0.819  0.274    0%     0
  both                  0.49   1.3     0.59  0.808  0.278    0%     0
(2) tiling at p=0.05 per offspring
  E_param               0.80   1.1     0.78  0.852  0.201   44%    79
  E_conn                0.54   1.1     0.63  0.834  0.254   12%    79
  both                  0.53   1.1     0.62  0.817  0.268   12%    79
(3) tiling on stagnation (flat 8 gens)
  E_param               0.74   1.3     0.73  0.823  0.241   25%   145
  E_conn                0.57   1.3     0.72  0.813  0.275   12%   139
  both                  0.56   1.3     0.71  0.800  0.281   12%   134
random (matched budget) 0.48   3.7     0.46  0.739  0.319    0%
```

### The result

**0% -> 44%.** Per-position mutation never produces a convolution in any arm. The rare global operator
does. Under `E_param` the evolved net ties the hand-built ceiling on every axis (test 0.852 vs 0.851,
eq-err 0.201 vs 0.207). This is **paper 1's granularity mechanism one level up**: there, the compact
filter was unreachable by per-connection mutation and reachable by per-offset mutation; here, the tiling
is unreachable by per-position mutation and reachable by a global one. Same shape, two levels. That
parallel is the paper's thesis.

Two secondary findings worth keeping:
- **The fixed low rate beats the stagnation trigger** (44% vs 25%) while firing *fewer* tilings (79 vs
  145). Bursts on stagnation appear to wreck converged solutions; a steady drizzle lets selection sift.
  Report rather than tune away.
- **The operator makes the tiling reachable; the cost function decides whether it is kept.** The
  macro-mutation only pays under `E_param` (44%); under `E_conn` and `both` it stays at 12%.

### The check FAILED, and it caught a mislabelled reference

Predicted: on the circle, the hand-built convolution's eq-err goes to ~0. Measured: **0.207.**

Cause, and it is in the model not the measure: the readout weights `v[p]` and hidden biases `bh[p]` are
**per-position and independently learned**. So a shared filter sits underneath an *unshared*
locally-connected layer, and the composed map is not equivariant. The row labelled "CONVOLUTION" is
therefore not one: it is a shared filter with an unshared readout. A real ConvNet shares the bias per
channel and pools before the readout.

The equivariance measure has now caught two things the structural metrics missed: the boundary artifact
(run 1) and this mislabelled reference (run 2). That is the theorem earning its keep, and both belong in
the paper as method, not as errata.

**Decision needed:** tying `bh` and `v` within a group changes the model class for every row and
requires re-running everything. Pending author's call.

---

## 5c. Run 3 (2026-07-31): shared readout, 40 seeds. THE RESULT.

Fix applied: filter, bias **and readout weight** are now all shared within a group, i.e. a channel with
sum-pooling. Previously a shared filter sat under an unshared per-position readout, so the row labelled
"CONVOLUTION" was not one. **The check now passes: the hand-built convolution's eq-err went 0.207 ->
0.017.** The equivariance column is finally interpretable.

```
                        cover  groups  reg   test   eq-err  %conv  tilings
CONVOLUTION (reference) 1.00   1.0     1.00  0.825  0.017
locally connected       1.00   12.0    1.00  0.724  0.323

(1) local mutation only  (paper 1's mutation model)
  E_param               0.60   1.7     0.58  0.847  0.210    0%     0
  E_conn                0.43   1.6     0.55  0.836  0.239    0%     0
  both                  0.44   1.6     0.57  0.835  0.226    0%     0
(2) tiling at p=0.05 per offspring
  E_param               0.80   1.4     0.86  0.880  0.131   50%    81
  E_conn                0.44   1.4     0.74  0.852  0.203    5%    81
  both                  0.45   1.4     0.70  0.850  0.209    0%    81
(3) tiling on stagnation (flat 8 gens)
  E_param               0.65   1.3     0.70  0.860  0.152   25%   146
  E_conn                0.42   1.4     0.62  0.843  0.216    8%   140
  both                  0.42   1.3     0.66  0.848  0.201    8%   140
random (matched budget) 0.49   3.5     0.53  0.809  0.289    0%
```

### The headline

**0/40 -> 20/40 convolutions.** Fisher exact, two-sided, **p = 7.8e-08**. Per-position mutation produces
a convolution in zero runs out of forty; the rare global operator produces one in half of them. The
equivariance error drops in step (0.210 -> 0.131) and accuracy rises (0.847 -> 0.880), so it is not a
metric artifact: the nets really do become more translation-equivariant and better at the task.

This is **paper 1's granularity mechanism one level up.** There: the compact filter is unreachable by
per-connection mutation, reachable by per-offset mutation. Here: the tiling is unreachable by
per-position mutation, reachable by a global one. Same mechanism, two levels of structure. That
parallel is the paper's thesis and it is now supported at n=40 with a named test.

Secondary, both robust across runs 2 and 3:
- **Fixed low rate beats the stagnation trigger** (50% vs 25%) while firing *fewer* tilings (81 vs 146).
  Bursts on stagnation appear to disrupt converged solutions; a steady drizzle lets selection sift.
- **The operator makes the tiling reachable; the energy term decides whether it is kept.** Under
  `E_param` the macro-mutation yields 50%; under `E_conn` 5% and under `both` 0%. Two separate claims.

### Third mislabelled reference, caught again by measurement

**The evolved nets BEAT the hand-built convolution** (0.880 vs 0.825). So the full convolution is not
the optimum of this task and "ceiling" is the wrong word for it. Cause: with sum-pooling over all 12
positions, a full tiling sums noise from every position, while the motif occupies one. A sparser or
partial tiling has better signal-to-noise. This is exactly why real ConvNets use **max**-pooling for
detection, and this setup uses sum-pooling.

Call it a *reference*, not a ceiling, and consider a max-pool arm. Three times now the measurement has
corrected a label (boundary artifact, unshared readout, and now sum-pool SNR). Worth stating in the
paper as method: the reference has to be re-derived every time the model class changes.

### Figure

`fig_structures.py` -> `fig_structures.pdf` / `.png`. Four panels on the circular input, drawn from the
`DUMP=1` genome dump (seed 1 in each arm, no cherry-picking): started from (12 colours, one filter per
position), aiming at (one colour, every position), evolved with local mutation only (one colour but
holes: `a.aaaaa.aaaa`), evolved with the tiling operator (`aaaaaaaaaaaa`, a full convolution). Colour =
weight group; same colour means the same filter.

Requires matplotlib: use `/home/vas/.venv-figs/bin/python` (system python3 has none).

---

## 5d. Run 4 (2026-07-31, overnight): 200 seeds, rate sweep, N sweep, reachability control

Launched via `~/smbpann/scripts/tile_overnight.sh`, finished 03:34. Four jobs, all `E_param` rows quoted
(the arm where the operator pays).

### Job 1 — headline at 200 seeds

```
                        cover  groups  reg   test   eq-err  %conv
CONVOLUTION (reference) 1.00   1.0     1.00  0.791  0.020
locally connected       1.00   12.0    1.00  0.662  0.309
(1) local mutation      0.67   1.9     0.64  0.821  0.218    0%
(2) tiling p=0.05       0.84   1.6     0.87  0.847  0.153   38%
(3) tiling on stagnation 0.72  1.6     0.76  0.833  0.168   22%
random                  0.53   3.9     0.56  0.766  0.296    0%
```
**0/200 vs 76/200. Fisher exact, two-sided, p = 1.8e-16.** Equivariance error falls in step
(0.218 -> 0.153) and accuracy rises (0.821 -> 0.847), so it is not a metric artifact. All three
secondary claims from the 40-seed run survive: fixed rate beats stagnation (38% vs 22%) while firing
fewer tilings; the operator only pays under `E_param` (38% vs 8% and 5%).

### Job 4 — the reachability control, and it PASSED

At **400 generations**, five times the budget, local mutation still yields **0%** (`E_param` and `both`;
2% for `E_conn`). The macro arm sits at 40%, essentially unchanged from 38% at 80 generations, so both
arms have converged. Fisher on the 400-gen run: **p = 6.6e-09**.

This is the control that matters. The central negative is about **reachability**, not about not having
run long enough. Local mutation does not get there with five times the compute. Had it started producing
convolutions at 400 generations, the headline would have collapsed to a claim about search efficiency.

### Job 2 — rate sweep: a plateau, not a peak

```
rate   0.01  0.02  0.05  0.10  0.20
%conv   31%   38%   40%   39%   43%
test  0.842 0.844 0.860 0.863 0.856
```
Rises fast to ~40% by 0.05 then flat. **The result is not a tuning artifact**; 0.05 was not a knife
edge. Still creeping up at 0.20, so the upper end is untested and the rate at which the operator starts
destroying population diversity is unknown. Worth one more sweep at 0.3/0.5/0.8.

### Job 3 — N sweep: THE LIMITATION, and it is real

```
N        8     12     16     20     24
control  2%     0%     0%     0%     0%
tiling  63%    40%    17%     8%     4%
test  0.902  0.860  0.811  0.772  0.750
Fisher    -   <1e-9 7.3e-06 6.8e-03  0.12  (control vs tiling)
```

**The effect decays with scale and is no longer significant at N=24** (p = 0.12). The qualitative
ordering holds everywhere (control is 0% at every N above 8), but the magnitude collapses.

**Confound that must be named, not hidden:** the sweep held `POP=24` and `GENS=80` fixed while N grew,
so compute per unit of search space fell sharply as the space grew like 2^N x N^N. This does **not**
currently separate "the budget did not scale" from "the mechanism does not scale". Paper 1 faced the
same question in its Sec 2.4 and answered it by growing the budget quadratically in N; the same control
is owed here and is the single most important missing experiment.

Until that is run, the honest claim is: **demonstrated at N<=16, decaying beyond, cause unresolved.**

---

## 5e. Run 5 (2026-07-31): the scaling limitation was an artifact. It is gone.

Three experiments, in the order they were run. The second refuted the first; the third explained both.

### (a) Budget scaling: NOT the cause

The N-sweep of run 4 held `POP` and `GENS` fixed, so it could not separate "budget did not scale" from
"mechanism does not scale". Re-ran with `GENS` proportional to N and to N^2 (10 jobs, parallel, 100
seeds each). `E_param`, arm (2):

```
N            8     12     16     20     24
GENS=80     63%    40%    17%     8%     4%
GENS ~ N    62%    40%    17%     8%     4%
GENS ~ N^2  62%    40%    17%     8%     5%
```
Identical. The GA converges long before the budget is spent; extra generations buy nothing. **The
confound is resolved: the decay was not compute.**

### (b) The period-prior hypothesis: REFUTED

Hypothesis (mine): `tile_mutation` draws the period T uniformly from 1..N/2, but only T <= K can leave
no gap wider than the kernel, so the useful fraction is 2K/N and decays as ~6/N. Implemented `TPRIOR=1`
drawing P(T) proportional to 1/T, which raises P(T<=3) at N=24 from 0.25 to 0.59.

```
N            8     12     16     20     24
uniform T   63%    40%    17%     8%     4%
P(T) ~ 1/T  62%    40%    20%    11%     4%
```
Within noise. **The operator's period prior is not the bottleneck.** Prediction failed; recorded because
the reasoning was plausible and the refutation is what pointed at the real cause.

### (c) The real cause: an unreachable accuracy target (a bug in this probe's design)

The hand-built convolution's own test accuracy falls with N, because a longer circle means more noise
summed into the readout and the same 24 training examples spread over more positions:

```
N                     8      12      16      20      24
conv reference     0.869   0.795   0.736   0.686   0.664
TARGET (fixed)     0.90    0.90    0.90    0.90    0.90
```

**The target was unreachable at every N, including N=8.** In `objective = (acc>=target) ? (2-energy) :
acc`, the energy branch therefore fired only when a genome got lucky on the 300-sample validation set.
As N grew and accuracy sank further below target, luck struck less often, the energy term engaged less,
and %conv decayed. The scaling curve was measuring the miscalibrated threshold, not the mechanism.

### The corrected sweep: the effect is FLAT in N

Re-ran with `TARGET` set per N to 95% of what a convolution actually achieves at that N:

```
N              8      12      16      20      24
TARGET       0.83    0.76    0.70    0.65    0.63
control       2%      0%      0%      0%      0%
tiling       68%     63%     55%     48%     51%
Fisher p   2.2e-16 1.2e-15 4.0e-16 3.5e-16 7.5e-16
```

**The decay is gone.** 4% -> 51% at N=24. The macro-mutation effect is essentially flat from N=8 to
N=24, the control is 0% at every N above 8, and every comparison sits at p < 1e-15.

So the paper's headline limitation does not exist. What existed was a threshold that no architecture in
the space could clear, which silently switched off the energy term that the whole result depends on.

**Method lesson, worth a line in the paper:** a threshold objective needs its threshold re-derived
whenever the model class or the problem size changes, or it stops being a constraint and becomes a
noise filter. This is the fourth time here that a reference or a threshold went stale under a change
(boundary artifact, unshared readout, sum-pool SNR, and now the target). Consider replacing the
threshold with a continuous objective (acc - lambda*energy) so the energy term always has a gradient.

### What must be re-run before anything is written up

Runs 1-4 all used `TARGET=0.90`, so **every number in 5a-5d was produced under the same broken
threshold**, including the 200-seed headline. The 0% vs 38% comparison is still internally valid (both
arms faced the same objective), but the magnitudes are not trustworthy and the energy-term comparison
between `E_param` / `E_conn` / `both` needs redoing at a reachable target.

---

## 5f. Run 6 (2026-07-31): final numbers, and the paper

**Paper drafted: `tiling.tex` -> `tiling.pdf`, 7 pages, builds clean.**
Title: *The Tiling Does Not Emerge: Mutation Granularity as the Reachability Constraint on Convolution*

### Main table, N=12, 200 seeds, reachable target (0.76)

```
mutation        energy      cover groups reg   test   eq-err %conv
convolution (reference)     1.00  1.0    1.00  0.791  0.020
locally connected (seed)    1.00  12.0   1.00  0.662  0.309
per-position    E_param     0.56  1.5    0.57  0.782  0.266   0%
per-position    E_conn      0.32  1.4    0.28  0.732  0.345   0%
per-position    both        0.32  1.4    0.30  0.738  0.345   2%
+ tiling        E_param     0.82  1.3    0.87  0.836  0.137  61%
+ tiling        E_conn      0.31  1.2    0.33  0.737  0.351   2%
+ tiling        both        0.32  1.2    0.35  0.738  0.343   2%
+ stagnation    E_param     0.63  1.3    0.70  0.802  0.205  27%
random                      0.38  2.8    0.39  0.714  0.350   0%
```

Fisher exact, two-sided:
- control vs tiling (E_param): 0/200 vs 122/200, **p = 4.3e-16**
- tiling: E_param vs E_conn: 122/200 vs 4/200, **p = 8.8e-16**
- tiling vs stagnation (E_param): 122/200 vs 54/200, p = 9.2e-12

**With the target fixed, the energy-term separation is far sharper than before** (61% vs 2%, where the
broken threshold gave 38% vs 8%). The "operator makes it reachable, cost term decides whether it is
kept" claim is now the strongest thing in the paper after the headline. E_conn actively prevents a
tiling: it thins coverage to 0.31 and no regular stride survives.

### N sweep, 200 seeds, reachable targets

```
N          8    12    16    20    24
control    1%    0%    0%    0%    0%
tiling    66%   60%   55%   52%   48%
Fisher  5e-16 2e-15 2e-15 4e-16 4e-16
```
Essentially flat. The scaling limitation of run 4 is gone and was entirely the unreachable target.

### Continuous objective (acc - lambda*E), 200 seeds, N=12

```
lambda        0.02  0.05  0.10  0.20  0.40  | threshold
per-position    0%    0%    0%    0%    1%  |   0%
+ tiling        5%    6%   10%   14%   18%  |  61%
groups         1.8   1.7   1.5   1.4   1.2  |  1.3
```
Fisher, control vs tiling: p = 1.7e-03 at lambda=0.02 rising to 1.1e-09 at 0.40.

**Direction robust, magnitude not.** The gap is structural, not tuning: a threshold objective is a
*constrained* optimisation (among individuals clearing the bar, fitness is 2-E, so energy is minimised
with unlimited weight and accuracy above the bar buys nothing), while a linear penalty is *scalarised*
(energy can never move fitness by more than lambda, against an accuracy range of ~0.4). Classical
constrained vs penalty formulations; not interchangeable. The threshold applies much more selection
pressure to structure, at the cost of the staleness failure mode.

This is worth flagging to paper 1 as well, which uses the threshold form throughout: it is relying on
lexicographic behaviour whether or not it says so, and owes a check that its bar is clearable.

Continuous N sweep at lambda=0.10 does decay (42% / 2% / 4% at N=8/16/24), but that is expected with a
weak penalty: energy barely competes with accuracy, so structure is under-selected at every N.

---

## 5g. Run 7 (2026-07-31): max-pooling, and the honest range

### Max-pooling makes the reference a real ceiling

Implemented `POOL=1`: units within a group are max-pooled before the readout, which is what a ConvNet
does for detection. Only the argmax unit receives gradient. Effect on the reference:

```
                     sum-pool          max-pool
convolution test      0.791             0.918
convolution eq-err    0.020             0.000   <- exact
evolved beats it?     YES (0.836)       NO (0.894 < 0.918)
```

**The paper's most awkward caveat is gone.** Under sum-pooling a full convolution sums noise from every
position while the motif occupies one, so a sparser net had better SNR and the "ceiling" was beatable.
Max-pooling removes that: the hand-built convolution is a perfect, exactly translation-invariant
detector, and no evolved arm reaches it.

### Main table, max-pool, N=12, 200 seeds, TARGET=0.90

```
mutation      energy    cover groups reg   test   eq-err %conv
convolution (ceiling)   1.00  1.0    1.00  0.918  0.000
locally connected       1.00  12.0   1.00  0.662  0.309
per-position  E_param   0.55  1.1    0.54  0.817  0.177   1%
per-position  E_conn    0.35  1.1    0.48  0.738  0.233   2%
per-position  both      0.35  1.1    0.47  0.748  0.234   0%
+ tiling      E_param   0.79  1.0    0.81  0.894  0.078  32%
+ tiling      E_conn    0.34  1.0    0.59  0.764  0.217   8%
+ tiling      both      0.34  1.0    0.62  0.758  0.225   8%
+ stagnation  E_param   0.72  1.0    0.79  0.846  0.101  26%
random                  0.51  3.3    0.55  0.696  0.278   0%
```
Fisher: control vs tiling 2/200 vs 64/200, **p = 1.4e-16**; E_param vs E_conn 64/200 vs 16/200,
p = 1.7e-09. Groups collapse to exactly 1.0 under every tiling arm.

Max-pool N sweep: tiling 36/32/18/13/8% for N=8/12/16/20/24, control 4/1/0/0/0%, all significant
(1.1e-15 down to 2.2e-05). It **decays** where the sum-pool sweep was flat, and the reason is
interpretable: max-pooling makes a partial tiling good enough, because uncovered positions cost
detections but add no noise, so the pressure to complete the tiling is weaker exactly where a longer
circle needs more of it.

### The lambda plateau closes the constrained-vs-penalty question

```
lambda   0.02 0.05 0.10 0.20 0.40 0.80 1.60 | threshold
tiling    5%   6%  10%  14%  18%  18%  20%  |   61%
```
**Plateaus near 20%.** Raising lambda to 1.60, forty times the smallest setting, does not approach the
threshold form. So the gap is structural (constrained vs scalarised optimisation), not a weighting
that was set too low. That is the evidence the paper needed for the claim.

### The honest headline

The %conv magnitude ranges 8%-61% across pooling rules, objective forms and problem sizes. **The
control is between 0% and 4% in every single configuration**, and the operator arm is always
dramatically higher and always significant. So: direction robust everywhere, magnitude
configuration-dependent, and the paper reports the range rather than the best cell.

Primary configuration chosen as **max-pool + threshold**, despite giving 32% rather than 61%, because
it is the only setting in which the hand-built convolution is a genuine ceiling. Choosing the
methodologically sound cell over the flattering one.

---

## 5h. Run 8 (2026-07-31): the author's crystal-growth proposal, and a confound it exposed

Author's proposal: do not tile globally. Grow from a nucleation centre, one unit at a time, staying near
the stable configuration, with a cap. Implemented as `grow_mutation`: pick an occupied position, measure
the spacing to the nearest unit sharing its filter (its lattice constant), and place one more unit of
the same filter at that spacing. Tandem duplication, local and incremental.

### (a) Growth works, and the rate matters

```
PGROW  ctrl  global  growth  cov   reg
0.05    1%    32%     2%    0.61  0.62
0.15    1%    32%     2%    0.68  0.67
0.30    1%    32%     6%    0.73  0.73
0.60    1%    32%     8%    0.82  0.82
1.00    1%    32%    18%    0.86  0.86
```
Monotonic, with coverage and regularity climbing together. **The move does not have to be global.** What
matters is that the ordering current outruns the disordering one: pruning fires ~0.36 times per
offspring (prem 0.03 x ~12 positions), so growth only competes once it fires comparably often.

### (b) The ratio, not the growth rate: confirmed, and it exposed a confound

Held growth at 0.05 and lowered the prune rate instead:

```
PREM   ratio  ctrl_conv  growth_conv  ctrl_cover  ctrl_reg
0.030  0.14      1%          2%         0.55       0.54
0.015  0.28      2%          3%         0.69       0.66
0.008  0.52      6%          8%         0.83       0.81
0.004  1.04     18%         21%         0.91       0.90
0.002  2.08     28%         30%         0.95       0.95
```
The ratio hypothesis held: order appears as growth/dissolution crosses ~1. **But the control rose too,
to 28%, and that is the tell.** Control coverage 0.95 and regularity 0.95 at prem=0.002 is simply the
seed, undisturbed.

**THE CONFOUND: the locally-connected seed occupies every position, which is already a perfect stride-1
tiling.** Positional order is present at generation zero; the search only ever had to merge filters. So
every result up to here answered *does order survive?*, not *does order emerge?* At high prune rates the
seed's order is destroyed and cannot be rebuilt; at low prune rates it is never destroyed. Both look
like "convolutions appear" and neither is emergence.

### (c) The decisive run: a DISORDERED seed

Added `SEEDMODE=1`: random subset of positions, random filters. No positional order at generation zero,
so any that appears has to be built.

```
PREM    control  global tiling  crystal growth
0.030     1%          21%            5%
0.008     0%          40%           11%
0.002     0%          62%           17%
```
Fisher, control vs global tiling: p = 1.3e-11, 1.1e-15, 6.2e-16.
Fisher, control vs crystal growth: p = 3.6e-02, 2.6e-07, 2.5e-11.

**Undirected local mutation never builds order: 0-1% at every dissolution rate.** The 28% of (b) was
entirely inheritance. Both structure-propagating moves do build it, the global rewrite more effectively
than local growth, and both improve as dissolution falls.

### The corrected physical picture

Three statements, and they are cleanly separable:

1. **Nucleation.** Undirected local mutation cannot nucleate positional order at all, at any dissolution
   rate. Random single-site flips have no gradient on a global order parameter.
2. **Propagation.** A move that *copies existing structure* nucleates it, and it does not have to be
   global: local tandem duplication works (5-17%), the global period-rewrite works better (21-62%). The
   distinguishing property is copying versus perturbing, not local versus global. **This corrects the
   paper's framing, which attributed the effect to globality.**
3. **Survival.** Once nucleated, order persists only if the ordering current exceeds the disordering
   one; %conv rises monotonically as the prune rate falls, in both propagating arms.

Nucleation, growth, dissolution: the three ingredients of a crystallisation problem, now separated by
experiment rather than asserted.

**The paper needs revising for this.** Its current claim, "the tiling is unreachable by local mutation
and reachable by a rare global one", is wrong in its second half and imprecise in its first. The correct
claim is that it is unreachable by *undirected* mutation and reachable by a *structure-propagating* one,
of which the global rewrite is merely the most aggressive instance. All headline numbers should be
re-derived from the disordered seed, since the locally-connected seed cannot support an emergence claim.

---

## 5i. Run 9 (2026-07-31): the paper reframed around crystallisation

**Paper rewritten: `tiling.tex` -> `tiling.pdf`, 7 pages. v1 kept as `tiling_v1_backup.tex`.**
New title: *Convolution as Crystallisation: Nucleation, Growth and Dissolution in Evolutionary
Architecture Search*

The old framing ("the tiling needs a global mutation") was wrong in its second half and imprecise in its
first. The reframe: a convolution decomposes into **composition** (sharing) and **order** (tiling), and
these have different status under search because composition is a per-site property and order is not.

### Primary table, disordered seed, N=12, 200 seeds, max-pool, prem=0.002

```
                            cover groups reg   test   eq-err  %conv
convolution (ceiling)       1.00  1.0    1.00  0.918  0.000
per-site only (control)     0.66  1.1    0.64  0.843  0.180    0%
+ tandem duplication (local)0.86  1.2    0.85  0.890  0.112   17%
+ segment repeat (global)   0.83  1.0    0.89  0.885  0.046   62%
+ segment on stagnation     0.78  1.0    0.87  0.872  0.057   62%
random (matched budget)     0.52  3.2    0.54  0.700  0.273    0%
```
By cost term (%conv): control 0/0/1, tandem 17/0/0, segment 62/11/10 for E_param/E_conn/both.
**Groups collapse to 1.0-1.3 under every arm and every cost term, including E_conn which pays nothing
for sharing.** Composition is selected by data scarcity, not by the budget.

### The three claims, now separable by experiment

1. **Nucleation.** Undirected per-site mutation never builds order: 0-1% at every dissolution rate
   (0.030 / 0.008 / 0.002). Not slow, blind: no single-site move raises the regularity of an irregular
   placement, so there is no gradient on a global order parameter.
2. **Growth.** Any move that *copies existing structure* nucleates it, and **locality is irrelevant**:
   local tandem duplication 17% (p = 2.5e-11), global segment repeat 62% (p = 6.2e-16). Copying versus
   perturbing is the operative distinction, not local versus global. This is the correction the author's
   crystal-growth proposal produced, and it also revises how paper 1's per-offset result should be read:
   that move copies one decision across every instance of a shared feature.
3. **Dissolution.** Once nucleated, survival tracks the ordering/disordering ratio: 21/40/62% for the
   global operator as the per-site rate falls 0.030 -> 0.008 -> 0.002. The control stays on the floor
   throughout, so dissolution governs survival and has no bearing on whether order can start.

### The corollary that makes it matter beyond this experiment

**No parameter-counting or connection-counting penalty can produce translational order, because neither
has order in its objective.** E_param is indifferent to placement once filters are shared; E_conn
actively prevents order by thinning to a third coverage. This is why ConvNets hardwire the tiling rather
than learn it, and it is not a compute limitation. Under search the prior does not disappear, it
**relocates** into the move set: in our case into the operators' distributions over periods and lattice
spacings, which someone still had to choose. That is the compression thesis with a mechanism and a
measurement attached.

### Figures (two, both weight-matrix representations)

`fig_structures.py` -> Figure 1. Five panels: disordered seed, target convolution, per-site (0%), tandem
duplication (17%), segment repeat (62%). The two copying operators find **different** convolutions, a
dense stride-1 tiling and a stride-3 tiling, and both satisfy the definition.

`fig_gallery.py` -> Figure 2. **The illustrative one.** Four rows (seed, per-site, tandem, segment) by
eight columns (runs), with columns sharing a seed so every difference down a column is due to the move
set alone. Convolutions outlined green. Requires the `SEED0` dump line added to `run_ga` on 2026-07-31.

Runs are sampled at a regular stride across all 200, not taken from the front: the first seven runs
happen to contain no tandem success (rate 17%), so showing them would understate that row. The stride
sample gives 0/8, 2/8, 4/8 for per-site, tandem and segment, matching 0%, 17%, 62% reasonably.

What the gallery shows at a glance and the tables do not: **colour collapses to one filter in nearly
every panel of every row including the control**, so composition is never the hard part. What separates
the rows is only whether the band closes.

Both figures need `/home/vas/.venv-figs/bin/python` (system python3 has no matplotlib).

---

## 5j. Run 10 (2026-07-31): the two fixes, and the experiment that reframed it again

**Paper retitled: *Stable but Unreachable: Convolution as a Reachability Problem in Evolutionary
Architecture Search*. 9 pages.** The crystallisation title was dropped because the crystallisation
physics turned out not to hold (below).

### The two referee-proofing fixes, done

- **Dispersion.** Probe now accumulates squares; every continuous column reports mean +- SD across
  seeds. Fixes the gap that was paper 1's known weakness ("no named statistical test anywhere").
- **Threshold sensitivity.** %conv is now reported at three regularity thresholds (>=0.999 / 0.90 /
  0.80), so the headline no longer rests on one bespoke cutoff. Ordering is stable across all three.
- Added `longest_run()`, the longest run of consecutive units sharing one filter: the order parameter.

### Two predictions of mine, both refuted, both productive

**(a) No nucleation barrier.** Planted domains of m=1..10, per-site mutation only, prem=0.008:
drift is `+2.8, +2.3, +1.5, +1.2, +0.4, +0.5, -0.3, -1.1` for m = 1,2,3,4,5,6,8,10. Small domains
*grow* and large ones *shrink* -- the opposite sign from classical nucleation, so there is no critical
nucleus. Not barrier-limited.

**(b) No stationary domain size either.** From the drift crossings I fitted
`m* = -4.06 + 2.19 ln(1/mu)` (m* = 3.3, 7.3, 9.2 at mu = 0.030, 0.008, 0.002) and predicted per-site
mutation alone should reach full order below mu ~ 7e-4. **Tested at mu down to 2e-4: still 0% convolutions,
and the domain saturates at 4.8.** The law does not extrapolate because there is no stationary state:
the final domain retains memory of the seed, so the dynamics is frozen, not equilibrating.

### The experiment those refutations produced: STABLE BUT UNREACHABLE

Same dynamics, same mutation rate, two starting points (per-site mutation only):

```
mu       planted 12/12   planted 11/12   domain    from disorder   domain
0.030        29%              2%          8.3           1%          4.6
0.008        52%              3%         10.6           0%          4.7
0.002        81%              6%         11.7           0%          4.8
```

- **Planted convolution survives 122/150 at mu=0.002; built from disorder 0/200. p = 1.2e-15.**
- **Planting 11 of 12 gives 6% against 81% for a complete plant (p = 6.8e-16): the search cannot add
  the twelfth unit.** The barrier is at every step including the last, not concentrated at the start.
- From disorder the domain saturates at 4.8 and does not move when mu is cut tenfold.

This rules out both alternative explanations at once. Not instability: per-site mutation preserves a
convolution perfectly well. Not a slow approach: gentling the mutation does not move the saturation
point. It is a **reachability** problem, and that is precisely what the copying operators solve, by
placing order by construction rather than by search.

This is the sharpest form of the paper's claim and it needed three refuted predictions to reach.

## 6. Next steps

- [x] **Circular domain.** Done in run 2. Did NOT drive the ceiling's eq-err to 0; diagnosed as the
      unshared readout, not the domain. See 5b.
- [x] **Tiling macro-mutation.** Done in run 2. 0% -> 44%. The central result.
- [ ] **Shared readout** (`bh` and `v` tied within a group), so the hand-built convolution is actually
      a convolution and eq-err becomes interpretable. Changes the model class; re-runs everything.
      **Blocking the equivariance claims.**
- [x] Re-run at scale. Done: 200 seeds, p = 1.8e-16.
- [x] Sweep the tiling rate. Done: plateau, not a peak (31% at 0.01 rising to ~40% by 0.05, flat after).
- [x] N-sweep. Done, and it is the paper's main limitation: 63% at N=8 down to 4% at N=24 (n.s.).
- [ ] **THE BLOCKING EXPERIMENT: scale the budget with N.** The N-sweep held POP=24 and GENS=80 fixed
      while the search space grew like 2^N x N^N, so it cannot separate "budget did not scale" from
      "mechanism does not scale". Paper 1 answered the same question in Sec 2.4 by growing the budget
      quadratically in N. Re-run the N-sweep with GENS proportional to N and to N^2. Until this exists
      the scaling claim cannot be stated either way.
- [ ] Extend the rate sweep to 0.3 / 0.5 / 0.8 to find where the operator destroys diversity; it was
      still creeping up at 0.20, so the top of the plateau is untested.
- [ ] Max-pool arm. Sum-pooling makes the full convolution sum noise from every position, which is why
      the evolved nets beat the "ceiling"; max-pool is what a real ConvNet uses for detection.
- [ ] Sweep the accuracy target. The threshold objective means anything above target is equal-fitness,
      so coverage drifts freely above it. Sweep to find where coverage stops drifting.
- [ ] `reg` is confounded at low placement counts (2 placements = 1 gap = trivially regular). Either
      condition on places>=3 (partly done) or drop `reg` in favour of equiv-err once it is trustworthy.
- [ ] Subsampling / pooling, the Neocognitron C-cell layer, is absent from paper 1 and from this probe.
- [ ] Named statistical test on paired seeds. Paper 1's most likely revision request was the absence of
      one; do not repeat it here.

## 7. Framing note

This paper is the natural home for the **act/artifact and amortization** thesis from
`~/articles/intelligence_compressors`: convolution is an artifact whose search cost was paid once by
evolution, read off the cortex by Hubel and Wiesel, and amortized by every ConvNet since. That essay
has no empirical grounding and never will standing alone. Here it would have a price tag: exactly which
pieces a search rediscovers, under which cost, and which it does not. Harvest it into the discussion
rather than rewriting it as a standalone.
