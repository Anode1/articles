# Backpropagation Feed-Forward Neural Networks

**The 1997 undergraduate thesis, revised: the generalized delta rule derived as gradient
descent in weight space, including a consistent tensor form of the update.**

The report reviews the main architectural ideas behind feed-forward networks, introduces the
standard neuron model, and derives backpropagation from first principles. Two applications
are worked: classifying cells for cancer diagnosis, and handwritten digit recognition. It
closes on the argument that problem-specific heuristics in the topology and the
preprocessing are usually necessary before a network is trainable, convergent, and able to
generalize without severe underfitting or overfitting.

Corrections and later additions are marked and dated in place, so the 1997 text and the 2026
editing stay separable. The math is implemented in
[bpnn](https://github.com/Anode1/bpnn).

[coursework_1997_backprop_ffnn.pdf](coursework_1997_backprop_ffnn.pdf),
[doi:10.5281/zenodo.20450525](https://doi.org/10.5281/zenodo.20450525).
