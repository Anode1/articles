# Priority and Provenance Record (AIS)

**Author:** Vasili Gavrilov, ORCID 0009-0007-9371-5994. Handles: GitHub `Anode1`, LiveJournal `siberean`, SourceForge `vgavrilov`.
**This record:** 2026-06 (concise edition). Deposited to Zenodo (DOI 10.5281/zenodo.20647047), SHA-256 anchored via OpenTimestamps, committed under signed git tags.

## Purpose
A dated, citable record that the author conceived and implemented these ideas by the dates below. It establishes **credit and provenance, not patent rights** (disclosed long ago; independent commercial implementations now exist). Where an idea has prior art, the claim is **independence and non-derivation, not novelty**.

## Evidence tiers
**A** independently / third-party dated (strongest). **B** self-authored dated artifact. **C** attested (testimony). When testimony and an artifact conflict, the artifact wins.

## The claim, in one paragraph
**AIS** is an associative, key-to-content personal-memory store: keywords index content (a URI or free text), a record may hold several links (a small graph), and retrieval is by **union and intersection of keys** over a plain-text, immutable-content store with a rebuildable index and a pluggable backend. Conceived around 2001 and run **by hand** on the filesystem (directory names as keys, manually balanced into sub-buckets, immutable content copied across redundant disks); automated as **software in 2005**; re-implemented from scratch in **ANSI C in 2026**. The companion thesis, **compression as intelligence** (intelligence is the discovery of compressors), grew from the same root: a compact key-set that *addresses* content instead of scanning it.

## Dated trail
| Date | Milestone | Evidence | Tier |
|---|---|---|---|
| 1995-96 | CS coursework: keyed records DB (Pascal), binary-search trees (Ada); the keys-as-structure training | OUI archive; Pascal mtimes 1995-12, Ada `.ali` 1996-01-08 | B |
| 1997 | Backprop feed-forward NN thesis (architecture as prior) | re-rendered copy; advisor attestation pending | B/C |
| 2001-04 | `org.is`/`is` namespace, in the LJMS messaging library; origin of the `is` name, not indexing code | archive: earliest source 2001-04-13; `CVS/Root` = SourceForge `ljms` | B |
| 2001 | ANSI C key-value proof-of-concept (`aisconfig`), source (c) 2001 | github.com/Anode1/aisconfig | B |
| ~2001-2004 | Filesystem-as-index run by hand (the manual practice) | `INDEX/` restore-stamped 2004-12-31, an upper bound only | C |
| 2003 | Backend research (DB2/Oracle/MySQL/Postgres/Berkeley DB) before settling on plain text | archive; `db2java.jar` 2003 | B/C |
| 2003-10 | Immutable content archive (`records/`) in active use | archive mtimes from 2003-10 | B |
| 2004-04 | First program form: a JavaScript client named `is` | archive mtimes 2004-04-14 | B |
| **2004-11-22** | **AIS registered on SourceForge** (earliest independent anchor) | sourceforge.net/projects/ais | **A** |
| 2005-01-28 | Shell `ais-scripts`: sharded plain-text INDEX, auto re-sharding (`pump.sh`), unit tests | CVS `$Id` 2005-01-28 | A |
| 2005-11 | C implementation `is` v0.0.1 (the 2026 engine re-implements this line) | archive mtimes 2005-11 | B |
| 2005-11-06 | First Java copy (CVS `$Id`); the Java line began 2005, not 2009 | CVS `$Id` | A |
| 2007 | Lucene adopted (a full Lucene/Tomcat version in use); AIS pitched to VC; took a government post Nov 2007 | archive 2007-11/12 | B/C |
| 2009-08 | Java/Lucene/Jetty release (a later milestone of the 2005 Java line) | sourceforge.net/projects/ais/files | A |
| 2011-08-10 | Shell INDEX manager published (auto re-sharding) | siberean.livejournal.com/13367.html | A |
| ~2005-07 | Wearable heads-up *interface* for AIS imagined once automatic-index development began (and after encountering the CS preservation problem): a light pilot's-helmet / HUD glasses, modelled on the visor HUDs military pilots wore in the late 1990s | attested | C |
| 2013 | Google Glass recognized as the realization of that imagined helmet ("this is it"); the specific "glasses + gloves" device framing dates here, postdating the 2007 pitch | attested | C |
| 2022-05-13 | Wayback snapshot of the SourceForge AIS page | web.archive.org | A |
| 2025 | Context Renormalization protocol | github.com/Anode1/context-renormalization | A/B |
| 2026 | Papers (*Emergence Does Not Care About Substrate*; *Intelligence Is the Discovery of Compressors*) and AIS re-implemented in ANSI C | github.com/Anode1/ais; Substack (to be DOI-deposited) | A/B |

Two distinct VC pitches: **~2001 was the 1997 backprop NN** (not AIS); **~2007 was AIS**. The wearable framing is later still (2013).

## Method and exclusions
- Tier every claim; **defer to artifacts over testimony**, recording both on conflict.
- **No third-party client or employer names** (projects are described, not named).
- **Exclude reused-asset and restore dates**: the `INDEX/` 2004-12-31 mtime is a restore upper bound, not a creation date; a 1988 Ada-manual mtime and 2026 LaTeX re-renders are not year-evidence.
- **No novelty over prior art** (JMS, JXTA, Gnutella/P2P, content-addressing, TDD): independence only. The 2001 `org.is` code predates JXTA's 2001-04-25 public launch, which is evidence of non-derivation.
- Keep **idea vs manual practice (~2001-2004) vs AIS software (2005)** distinct; the 2001 `is` name is not the 2005 AIS indexing project.
- The JavaScript `is` dictionary client (~2004) is verifiable via archive mtimes (not "unverifiable"); the archive is simply not mounted at the moment.

## Context (prior art)
The underlying problem, decades-long preservation and format compatibility of personal archives, is a recognized grand challenge: **Gray (2003)**, the UKCRC **"Memories for Life" (2003)**, **Rothenberg (1995)**. AIS descends from **Bush's Memex (1945)**: retrieval by association. The associative-index idea is Bush's and widely prior; AIS's claim is the **implementation and approach**, plain-text, durable, user-owned (the index never leaves the machine), which is the line between it and cloud lifelogging.

## Durability
Zenodo DOI (fixed timestamp), OpenTimestamps (SHA-256 anchored into Bitcoin), GPG-signed git tags, and a confirmed 2022 Wayback capture. Record this file's SHA-256 on finalizing.

## Limitations
Establishes priority of authorship and provenance, not patent. Pre-2004 conception rests on testimony (Tier C); the 2004-11-22 SourceForge registration is the earliest independent anchor. Some artifacts survive only as re-rendered or re-hosted copies.

## References
1. Gray, J. (2003). "What Next? A Dozen Information-Technology Research Goals." *Journal of the ACM* 50(1): 41-57. DOI 10.1145/602382.602401.
2. O'Hara, K. et al. (2006). "Memories for life: a review of the science and technology." *J. R. Soc. Interface* 3(8): 351-365. DOI 10.1098/rsif.2006.0125.
3. Rothenberg, J. (1995). "Ensuring the Longevity of Digital Documents." *Scientific American* 272(1): 42-47. DOI 10.1038/scientificamerican0195-42.
4. Bush, V. (1945). "As We May Think." *The Atlantic Monthly* 176(1): 101-108.

*Prepared with AI assistance, 2026-06. Items still pending corroboration are tracked separately.*
