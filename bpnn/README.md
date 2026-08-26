# What a Benchmark Can Resolve

**Training noise sets a ceiling on architecture comparison and on predictor evaluation, and
the benchmarks' own repeated runs, which their distributed tables average away, measure
where that ceiling sits.**

Unpublished and unsubmitted. Read `resolution.tex` as a draft.

NAS-Bench-101 trained each of its 423,624 architectures three times; NAS-Bench-201 trained
each of 15,625 three times on each of three datasets, at every epoch up to 200. Recovering
those runs gives a reference statistically independent of any single one of them, and four
things follow.

Comparing two architectures from one training run each disagrees with an independent
reference 33 to 42% of the time when the observed difference is 0.1 to 0.2 percentage
points, on both benchmarks and all three datasets. At low training budget the comparison is
a coin flip at every effect size: at 4 epochs on NAS-Bench-101 a one-to-two point difference
is called backwards 45% of the time, against 4% at 108 epochs, which bears directly on
multi-fidelity and early-stopping search. A benchmark's reported optimum is not a point:
3,558 of NAS-Bench-101's architectures cannot be separated from its winner using its own
data, so regret measured against that winner inherits the width. And there is a ceiling on
the rank correlation any performance predictor can achieve, because the label it is scored
against is itself one noisy run.

The engine is [bpnn](https://github.com/Anode1/bpnn).
