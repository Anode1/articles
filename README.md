# Articles

Papers by Vasili Gavrilov (ORCID [0009-0007-9371-5994](https://orcid.org/0009-0007-9371-5994)),
with their sources, figures and data. Each directory holds the LaTeX source, the
built PDF, the figures, whatever was needed to produce the numbers, and a README saying in short
what the work is and what it shows.

Most of these are deposited on Zenodo. The DOI below is the concept DOI in each case, which always
resolves to the latest version.

| directory | paper | DOI |
| --- | --- | --- |
| [`intelligence_compressors`](intelligence_compressors/README.md) | Intelligence Is the Discovery of Compressors | [10.5281/zenodo.20440110](https://doi.org/10.5281/zenodo.20440110) |
| [`ConditionalProbability`](ConditionalProbability/README.md) | Conditional Probability in Diagnostic Testing: An Isomorphism Between Tree Diagrams, Bayes' Theorem, Contingency Tables and ARR/RRR | [10.5281/zenodo.20449608](https://doi.org/10.5281/zenodo.20449608) |
| [`BPFNN_Coursework`](BPFNN_Coursework/README.md) | Backpropagation Feed-Forward Neural Networks (1997 undergraduate thesis, revised) | [10.5281/zenodo.20450525](https://doi.org/10.5281/zenodo.20450525) |
| | The math in the thesis is implemented in [`bpnn`](https://github.com/Anode1/bpnn) (2001-...) | |
| [`ControlModel`](ControlModel/README.md) | Artifact Promotion as a Control Model for Stable Cloud Deployment, and its implementation case study | [10.5281/zenodo.20451078](https://doi.org/10.5281/zenodo.20451078), [10.5281/zenodo.20528904](https://doi.org/10.5281/zenodo.20528904) |
| [`atree`](atree/README.md) | The Atree Format: A Scalable Binary-Path Notation for Ancestral Genealogies | [10.5281/zenodo.20587715](https://doi.org/10.5281/zenodo.20587715) |
| [`innovation_compression`](innovation_compression/README.md) | Chaos Makes Many, Compression Keeps Few: Where Innovation Comes From | [10.5281/zenodo.20603482](https://doi.org/10.5281/zenodo.20603482) |
| [`ais`](ais/README.md) | Compress the Access, Not the Store, and the AIS priority and provenance record | [10.5281/zenodo.20764255](https://doi.org/10.5281/zenodo.20764255), [10.5281/zenodo.20647048](https://doi.org/10.5281/zenodo.20647048) |
| [`iac`](iac/README.md) | A Wakeup, Not a Broker: The Minimal Transport for Coordinating Stateless LLM Agents | [10.5281/zenodo.21206970](https://doi.org/10.5281/zenodo.21206970) |
| [`smbpann`](smbpann/README.md) | The Imposed and Emergent Pieces of Convolution Under an Energy Budget | [10.5281/zenodo.21423177](https://doi.org/10.5281/zenodo.21423177) |
| [`MISRA_C_vs_CPP`](MISRA_C_vs_CPP/README.md) | When Abstraction Becomes Indirection: Tokens-to-trace, measured on four stacks | [10.5281/zenodo.22113993](https://doi.org/10.5281/zenodo.22113993) |

Not deposited, and each says on its own first page or in its README what state it is in:

| directory | what it is |
| --- | --- |
| [`cjitter`](cjitter/README.md) | Two papers, both negative. What Do People Optimize in Diagram Layout?, and The Test the Metaphor Benchmark Never Ran |
| [`bpnn`](bpnn/README.md) | What a Benchmark Can Resolve: training noise as a ceiling on architecture comparison. Unpublished and unsubmitted |
| [`energy`](energy/README.md) | A Substack piece on pricing grid power for data centres, with its charts and the script that draws them |

## Related work by others

[`related`](related/README.md) holds papers by other authors that bear on the work here,
redistributed under their own licences and unmodified. At present that is Hall, Galaev, Gavrilov
and Mondoux (2023) on machine-learned triage acuity scores, CC BY 4.0.

The code for the measurements is in the project repositories, which are linked from each paper:
[SMBPANN](https://github.com/Anode1/SMBPANN), [ais](https://github.com/Anode1/ais),
[iac](https://github.com/Anode1/iac), [bpnn](https://github.com/Anode1/bpnn),
[linearr](https://github.com/Anode1/linearr).

Shorter pieces and working notes are in [notes](https://github.com/Anode1/notes).
The context-renormalization paper has its own repository:
[context-renormalization](https://github.com/Anode1/context-renormalization).

## Building

Each paper builds with `pdflatex`, and those with a bibliography also need `biber` or `bibtex`:

    cd smbpann && pdflatex emergence.tex

Build artifacts are not committed.

## Licence

Text and figures are the author's. Where a paper carries a licence on its Zenodo record, that
licence governs; otherwise ask.
