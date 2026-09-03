# Articles

Papers by Vasili Gavrilov (ORCID [0009-0007-9371-5994](https://orcid.org/0009-0007-9371-5994)),
with their sources, figures and data. Each directory holds the LaTeX source, the
built PDF, the figures, whatever was needed to produce the numbers, and a README saying in short
what the work is and what it shows.

## Catalog

The catalog of these papers, with DOI, venue and status for each, is kept in one place,
the profile page <https://github.com/Anode1>, so that it is never out of step with itself.
A `PRIVATE/` directory beside a paper, when present, is ignored by git and holds drafts,
letters and keys.

## Related work by others

[`related`](related/README.md) holds papers by other authors that bear on the work here,
redistributed under their own licences and unmodified. At present that is Hall, Galaev, Gavrilov
and Mondoux (2023) on machine-learned triage acuity scores, CC BY 4.0.

The code for the measurements is in the project repositories, which are linked from each paper:
[SMBPANN](https://github.com/Anode1/SMBPANN), [ais](https://github.com/Anode1/ais),
[iac](https://github.com/Anode1/iac), [bpnn](https://github.com/Anode1/bpnn),
[cjitter](https://github.com/Anode1/cjitter).

Shorter pieces and working notes are in [notes](https://github.com/Anode1/notes).
The context-renormalization paper has its own repository,
[context-renormalization](https://github.com/Anode1/context-renormalization); it is superseded by
*Compress the Access, Not the Store* in [`ais`](ais/README.md).

## Building

Each paper builds with `pdflatex`, and those with a bibliography also need `biber` or `bibtex`:

    cd smbpann && pdflatex emergence.tex

Build artifacts are not committed.

## Licence

Text and figures are the author's. Where a paper carries a licence on its Zenodo record, that
licence governs; otherwise ask.
