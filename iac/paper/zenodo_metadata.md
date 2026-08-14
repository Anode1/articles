# Zenodo upload metadata - "A Wakeup, Not a Broker"

Paste these into the Zenodo "New upload" form, field by field. Upload the final
`iac.pdf` as the file. (Fields below match Zenodo's form as of 2026.)

---

**Resource type**
Publication  ->  Preprint

**Title**
A Wakeup, Not a Broker: The Minimal Transport for Coordinating Stateless LLM Agents

**Creators (authors)**
- Vasili Gavrilov  -  Affiliation: Independent researcher  -  ORCID: (add if you have one)

  (If you decide to credit the company, do NOT add it as a creator. Add it under
  "Contributors" with role "Sponsor" or "Hosting institution" - that credits the
  support without implying authorship, which reads correctly to reviewers.)

**Publication date**
(use the actual upload date, 2026)

**Description**
(The paper's abstract, de-LaTeX'd and inline for clean web rendering - paste this as-is; do not copy from the .tex, and do not let any line wrap hard.)

Multi-agent coordination on one machine is treated as a messaging problem and handed to a queue, a broker, or an inter-agent protocol. That answers the wrong question. Moving bytes between processes was solved decades ago; the hard part is that an LLM agent, between turns, is not a running process at all - slow, serial, dormant - so throughput, the thing a broker manages, never binds. The scarce primitive is a wakeup, and the only one a stateless agent can receive is the return of a blocking recv parked in a cheap child process the harness re-invokes on exit, one activation per message, not per poll. We present iac, a dependency-free C99 board (about 800 lines, one binary, no heap). None of the primitives are new; the assembly and the argument are. The economy is measured: a self-polling agent reprocesses its whole context on every check - millions of tokens an hour to watch an empty mailbox - while a C-blocked wakeup costs zero, on any model. The transport is almost nothing: an append-only text log under a file lock, the commit log a log-based broker is built on minus the service, auditable by cat and grep and, because every agent reads the whole shared log, open to peer review - neither of which a queue can give. The one genuinely new thing is the participant: an agent woken by nothing but a returning process. A fleet of agents used the board to build the board. Give it exactly that and no more: a wakeup, not a broker.

Reference implementation and reproducible benchmarks: https://github.com/Anode1/iac

**License**
Creative Commons Attribution 4.0 International (CC-BY-4.0)   [for the paper text]
(The reference implementation iac is separately licensed ISC.)

**Keywords**
LLM agents; multi-agent systems; agent coordination; inter-process communication; message passing; wakeup; polling; prompt caching; token cost; Unix; C; systems programming; blackboard systems; tuple spaces; commit log; auditability; open source

**Language**
English (eng)

**Version**
1.0 (preprint)

**Related / alternate identifiers**
- "is supplement to"  ->  https://github.com/Anode1/iac   (URL, resource type: Software)
- (optional, later) "is supplemented by"  ->  the software's own Zenodo DOI, if you
  enable the GitHub-Zenodo integration and cut a tagged release.

**Additional notes**
Preprint; not peer-reviewed. All measured figures are reproducible: latency via scripts/bench.sh in the repository, and the token-cost measurement via the experiment/ directory. Modeled and measured quantities are labelled separately in the paper.

---

## Tips

- To also give the *software* a citable DOI: on GitHub, enable the Zenodo
  integration (zenodo.org/account/settings/github), then cut a tagged release of
  Anode1/iac. Zenodo archives it and mints a DOI you can cross-link here.
- CC-BY-4.0 lets anyone reuse the text with attribution - the standard, permissive
  choice for a preprint you want read and cited. Pick CC-BY-NC only if you want to
  bar commercial reuse (usually not worth it for reach).
- Keep the title identical everywhere (paper, Zenodo, arXiv/TechRxiv cross-posts) so
  the versions are recognised as the same work.
