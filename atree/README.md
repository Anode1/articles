# The Atree Format

**A compact plain-text notation for ascending genealogies: each ancestor is named by the
path of ancestral sexes from the subject, `M` for father, `F` for mother, so `MF` is the
father's mother.**

That path is exactly the classical Ahnentafel (Sosa-Stradonitz) number written in binary,
reading each 0 as father and each 1 as mother. A decimal Ahnentafel number doubles every
generation and soon grows unwieldy; an atree path has one letter per generation, so its
length is simply how far back one is looking, and each line stands on its own, needing no
surrounding file, so any subset can be shared freely.

The paper gives the grammar, exact and reversible conversions to and from Ahnentafel, tool
support (GEDCOM import, an HIR/centimorgan calculator), and the limits: ascending trees
only, and pedigree collapse turns the tree into a graph when the same ancestor recurs
through cousin marriage.

The application is cross-person lineage matching. When two people's paths share a tail, the
names along it sound alike, and any Y or mtDNA haplogroups agree, that is a measurable,
spelling-robust signal that the two trees meet at the same ancestor. About 37 yes/no choices
suffice to single out any human who has ever lived, so identifying a person is itself a form
of compression.

[atree.pdf](atree.pdf), [doi:10.5281/zenodo.20587715](https://doi.org/10.5281/zenodo.20587715).
