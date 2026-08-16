# The night plan, 2026-08-16

Written before Vasili leaves for the night; he closes the session in the morning and then
goes camping for three days. The loop below works through this list top to bottom, commits
the articles repository after every completed item, and writes MORNING.md last. Ground
rules, absolute: no pushes to any remote (morning review gates publication), no new
measurements that would need pre-registration sign-off, no use of the word "honest",
PROSE.md rules everywhere, every cjitter change passes the full gate (check, pedantic, both
sanitizers) with pins and docs re-derived together before its commit, and every decision
that is Vasili's to make gets flagged in MORNING.md instead of taken.

1. **The paper's prose.** Write every \pending body section of layout.tex from the material
   that already exists: README and AGENTS of cjitter, PREREGISTRATION.md and its addenda,
   RESULTS.md, QUESTIONS.md, the AGENTS history of the 2001 method. The abstract already
   carries the results; the body must earn it. Build the PDF after each section.

2. **Figures.** The paper needs: the before/after migration pair (fixtures exist), the
   straight-versus-routed pair, a results figure (per-pair medians at 8000 with the
   centroid and human references, drawn from data/results.csv with a small committed
   script), and the separation-budget table as a LaTeX table. Static images only.

3. **Critics on the draft.** Three independent reviewers via the Agent tool, none given the
   author's conclusions: a statistician (the analysis chain, n=8 caveats, what a referee
   rejects), a graph-drawing reader (positioning against Davidson-Harel, CIGDP, the
   mental-map line; what is genuinely new and what is oversold), and the style reader
   calibrated on PROSE.md and the no-"honest" rule. Apply what survives verification;
   list the rest in MORNING.md.

4. **The advisor panel on directions.** Two or three agents argue where the line of work
   goes next, seeded with QUESTIONS.md: which question is the second paper, what the
   successor pre-registration must fix that this one exposed (n=8, trivial-k pairs, the
   rename confound), and whether the venue is graph drawing, metaheuristics, or methods.
   Their case goes into MORNING.md as recommendations, never as decisions.

5. **The successor pre-registration, as a draft.** PREREGISTRATION2-DRAFT.md: recombination
   pays at larger k, synthetic migrations at controlled k and modularity, the rotation
   mechanism test, the 2001 per-label climber as a fifth arm, budgets and tests declared.
   Marked DRAFT AWAITING APPROVAL on line one; it does not run.

6. **The presentable library.** C work in ~/cjitter, committed locally, gate-clean:
   a `libcjitter.a` target and `make install`/`uninstall` (PREFIX honored, header plus
   static library), a version macro in cjitter.h, a header-comment pass so the .h reads as
   the library's manual, and any const-correctness or naming nits a fresh reader would
   trip on. House style throughout; the Makefile stays as plain as bpnn's.

7. **The fifth method, only if 1 through 6 are done and green.** The 2001 per-label
   climber ("gclimb": pick one group of coordinates, unit-scaled jitter on that group
   alone, keep if the total improves), groups declared through the interface so labels and
   erd can name their pairs. Full pin re-derivation, README and AGENTS numbers re-measured,
   the whole gate including sanitizers. If anything resists, stop and flag rather than
   ship a half method.

8. **MORNING.md.** What was done, what the critics found and what was applied, the
   advisors' case, the flagged decisions, and the exact next actions for the first session
   after camping.
