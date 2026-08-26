# Articles

Papers by Vasili Gavrilov (ORCID [0009-0007-9371-5994](https://orcid.org/0009-0007-9371-5994)),
with their sources, figures, data and working notes. Each directory holds the LaTeX source, the
built PDF, the figures, and whatever was needed to produce the numbers.

Most of these are deposited on Zenodo. The DOI below is the concept DOI in each case, which always
resolves to the latest version.

| directory | paper | DOI |
| --- | --- | --- |
| [`intelligence_compressors`](intelligence_compressors/) | Intelligence Is the Discovery of Compressors | [10.5281/zenodo.20440110](https://doi.org/10.5281/zenodo.20440110) |
| [`ConditionalProbability`](ConditionalProbability/) | Conditional Probability in Diagnostic Testing: An Isomorphism Between Tree Diagrams, Bayes' Theorem, Contingency Tables and ARR/RRR | [10.5281/zenodo.20449608](https://doi.org/10.5281/zenodo.20449608) |
| [`BPFNN_Coursework`](BPFNN_Coursework/) | Backpropagation Feed-Forward Neural Networks (1997 undergraduate thesis, revised) | [10.5281/zenodo.20450525](https://doi.org/10.5281/zenodo.20450525) |
| | The math in the thesis is implemented in [`bpnn`](https://github.com/Anode1/bpnn) (2001-...) | |
| [`ControlModel`](ControlModel/) | Artifact Promotion as a Control Model for Stable Cloud Deployment, and its implementation case study | [10.5281/zenodo.20451078](https://doi.org/10.5281/zenodo.20451078), [10.5281/zenodo.20528904](https://doi.org/10.5281/zenodo.20528904) |
| [`atree`](atree/) | The Atree Format: A Scalable Binary-Path Notation for Ancestral Genealogies | [10.5281/zenodo.20587715](https://doi.org/10.5281/zenodo.20587715) |
| [`innovation_compression`](innovation_compression/) | Chaos Makes Many, Compression Keeps Few: Where Innovation Comes From | [10.5281/zenodo.20603482](https://doi.org/10.5281/zenodo.20603482) |
| [`ais`](ais/) | Compress the Access, Not the Store, and the AIS priority and provenance record | [10.5281/zenodo.20764255](https://doi.org/10.5281/zenodo.20764255), [10.5281/zenodo.20647048](https://doi.org/10.5281/zenodo.20647048) |
| [`iac`](iac/) | A Wakeup, Not a Broker: The Minimal Transport for Coordinating Stateless LLM Agents | [10.5281/zenodo.21206970](https://doi.org/10.5281/zenodo.21206970) |
| [`smbpann`](smbpann/) | The Imposed and Emergent Pieces of Convolution Under an Energy Budget | [10.5281/zenodo.21423177](https://doi.org/10.5281/zenodo.21423177) |
| [`MISRA_C_vs_CPP`](MISRA_C_vs_CPP/) | When Abstraction Becomes Indirection: Tokens-to-trace, measured on four stacks | [10.5281/zenodo.22113993](https://doi.org/10.5281/zenodo.22113993) |

Directories without a DOI:

- [`energy`](energy/) is a Substack piece with its charts and the script that draws them.
- [`bpnn`](bpnn/) holds `resolution.tex`, a draft on what a neural architecture benchmark can and
  cannot resolve. It is unpublished and unsubmitted; read it as a draft.
- [`cjitter`](cjitter/) holds two drafts whose measurements live in the
  [cjitter](https://github.com/Anode1/cjitter) repository. `stationary.tex`, What Do People
  Optimize in Diagram Layout?, reads the tables under `example/diagrams`. `audit.tex`, The
  Test the Metaphor Benchmark Never Ran, runs `example/metaphors` against the GECCO 2024
  benchmark's own release
  ([10.5281/zenodo.10561215](https://doi.org/10.5281/zenodo.10561215)). Each paper's
  pre-registration was signed before its confirmatory numbers were computed,
  `PREREGISTRATION-STATIONARITY.md` and `PREREGISTRATION-AUDIT.md`; `review/` holds the
  referee panels.

## smbpann2: a retired line of work

[`smbpann2`](smbpann2/) is the follow-up to the emergence paper, and it is kept because it failed
in a way worth reading. `tiling.tex` is **retracted** and says so on its own first page: its energy
term was exactly indifferent to the property it was supposed to select, so a fully occupied genome
satisfied the convolution test for free and every operator that added units looked like a
discovery. `estimator.tex` is retired, its central mechanism falsified three ways on the afternoon
it was written. Neither should be cited or extended. `RETIRED.md` explains what is void and what
survived, and `PROTOCOL.md` lists the checks that would have caught both on day one.

## Related work by others

[`related`](related/) holds papers by other authors that bear on the work here, redistributed
under their own licences and unmodified. At present that is Hall, Galaev, Gavrilov and Mondoux
(2023) on machine-learned triage acuity scores, CC BY 4.0.

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
