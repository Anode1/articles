# Articles

Papers by Vasili Gavrilov (ORCID [0009-0007-9371-5994](https://orcid.org/0009-0007-9371-5994)),
with their sources, figures and data. Each directory holds the LaTeX source, the
built PDF, the figures, whatever was needed to produce the numbers, and a README saying in short
what the work is and what it shows.

## Papers

Measured or derived results, the kind that go to arXiv and then to a journal. The DOI is the
concept DOI, which always resolves to the latest version; a paper not yet deposited says so.

| directory | paper | DOI or status |
| --- | --- | --- |
| [`iac`](iac/README.md) | A Wakeup, Not a Broker: The Minimal Transport for Coordinating Stateless LLM Agents | [10.5281/zenodo.21206970](https://doi.org/10.5281/zenodo.21206970); arXiv cs.MA submission pending endorsement |
| [`smbpann`](smbpann/README.md) | The Imposed and Emergent Pieces of Convolution Under an Energy Budget | [10.5281/zenodo.21423177](https://doi.org/10.5281/zenodo.21423177); under review at Genetic Programming and Evolvable Machines (with the editor, September 2026) |
| [`MISRA_C_vs_CPP`](MISRA_C_vs_CPP/README.md) | When Abstraction Becomes Indirection: Tokens-to-trace, measured on six stacks | [10.5281/zenodo.22113993](https://doi.org/10.5281/zenodo.22113993); a shorter version under review at IEEE Software since 31 August 2026 |
| [`ais`](ais/README.md) | Compress the Access, Not the Store, and the AIS priority and provenance record | [10.5281/zenodo.20764255](https://doi.org/10.5281/zenodo.20764255), [10.5281/zenodo.20647048](https://doi.org/10.5281/zenodo.20647048) |
| [`ControlModel`](ControlModel/README.md) | Artifact Promotion as a Control Model for Stable Cloud Deployment, and its implementation case study | [10.5281/zenodo.20451078](https://doi.org/10.5281/zenodo.20451078), [10.5281/zenodo.20528904](https://doi.org/10.5281/zenodo.20528904) |
| [`BPFNN_Coursework`](BPFNN_Coursework/README.md) | Backpropagation Feed-Forward Neural Networks (1997 undergraduate thesis, revised); implemented in [`bpnn`](https://github.com/Anode1/bpnn) | [10.5281/zenodo.20450525](https://doi.org/10.5281/zenodo.20450525) |
| [`cjitter`](cjitter/README.md) | What Holds a Hand-Drawn Diagram? A negative result | not deposited; targeting GD 2027. The metaphor-benchmark audit is withdrawn; its tables live in the library |
| [`bpnn`](bpnn/README.md) | What a Benchmark Can Resolve: training noise as a ceiling on architecture comparison | unpublished and unsubmitted |

## Other articles and essays

Expository, speculative, or narrow pieces. Deposited where a DOI is shown; none is headed to
arXiv in its present form.

| directory | article | DOI or status |
| --- | --- | --- |
| [`intelligence_compressors`](intelligence_compressors/README.md) | Intelligence Is the Discovery of Compressors | [10.5281/zenodo.20440110](https://doi.org/10.5281/zenodo.20440110) |
| [`innovation_compression`](innovation_compression/README.md) | Chaos Makes Many, Compression Keeps Few: Where Innovation Comes From | [10.5281/zenodo.20603482](https://doi.org/10.5281/zenodo.20603482) |
| [`ConditionalProbability`](ConditionalProbability/README.md) | Conditional Probability in Diagnostic Testing: An Isomorphism Between Tree Diagrams, Bayes' Theorem, Contingency Tables and ARR/RRR | [10.5281/zenodo.20449608](https://doi.org/10.5281/zenodo.20449608); declined by medRxiv on 26 May 2026 under its institutional-affiliation policy, rejected by Advances in Health Sciences Education |
| [`atree`](atree/README.md) | The Atree Format: A Scalable Binary-Path Notation for Ancestral Genealogies | [10.5281/zenodo.20587715](https://doi.org/10.5281/zenodo.20587715) |
| [`energy`](energy/README.md) | A Substack piece on pricing grid power for data centres, with its charts and the script that draws them | Substack |

## Related work by others

[`related`](related/README.md) holds papers by other authors that bear on the work here,
redistributed under their own licences and unmodified. At present that is Hall, Galaev, Gavrilov
and Mondoux (2023) on machine-learned triage acuity scores, CC BY 4.0.

The code for the measurements is in the project repositories, which are linked from each paper:
[SMBPANN](https://github.com/Anode1/SMBPANN), [ais](https://github.com/Anode1/ais),
[iac](https://github.com/Anode1/iac), [bpnn](https://github.com/Anode1/bpnn),
[linearr](https://github.com/Anode1/linearr), [cjitter](https://github.com/Anode1/cjitter).

Shorter pieces and working notes are in [notes](https://github.com/Anode1/notes).
The context-renormalization paper has its own repository,
[context-renormalization](https://github.com/Anode1/context-renormalization); it is superseded by
*Compress the Access, Not the Store* above.

## Building

Each paper builds with `pdflatex`, and those with a bibliography also need `biber` or `bibtex`:

    cd smbpann && pdflatex emergence.tex

Build artifacts are not committed.

## Licence

Text and figures are the author's. Where a paper carries a licence on its Zenodo record, that
licence governs; otherwise ask.
