# v3: the frontend, and the context nobody counts

Pre-registered design. Nothing here has been built or run. Predictions and
refutation criteria are signed before the first subject is written.

## The question

v1 and v2 measured backend paths: C, C++, plain Java with JDBC, Spring. The
objection to extending the result to the UI, stated fairly, is that JSX is
more compact to write than `createElement` and `appendChild`, so a framework
should cost an agent less, not more.

That objection is about text written. Tokens-to-trace counts text read. v3
measures both, and adds the measurement neither side counts: the context that
decides behavior and lives outside every repository.

## The rule does not change

The floor is the platform, and anything the application configures, or that
varies by library version, is included. That rule already decides the
contested case: the browser engine sits below the line for the same reason
MySQL does, and React and Angular sit above it for the same reason Hibernate
does. `document.createElement` costs zero closure tokens exactly as
`PreparedStatement` does.

The entry point is one user interaction and the closure ends at the DOM the
browser paints, symmetric with wire to storage and back.

## A. Closure, third-party code on both sides

The subjects are community implementations of one specification, written by
different authors, so neither side is the author's own style. This applies
the Monocypher move to the whole comparison rather than to one row.

| Side | Subject |
| --- | --- |
| plain JS | the vanilla implementation of the shared specification |
| React | the React implementation of the same specification |
| Angular | the Angular implementation of the same specification |

Entry point: typing in the filter and the list re-rendering.

Reported per side: categories 1, 2 and 3, at region and whole-file
granularity, with floor sensitivity at both ends, once with the framework
runtime counted as floor (generous to the framework) and once with the rule
applied. If the framework's category 1 is smaller than plain JS, which is
what the objection predicts, that number is reported first and in the
abstract.

## B. Agent runs on behavior-matched twins

Twins built for the purpose, same rendered DOM, same store, same styling. Two
sides, four tasks, five repetitions, 40 runs. The tasks mirror the endpoint
four so that the two experiments compare directly.

| Task | Endpoint analogue |
| --- | --- |
| render one more field per row | add a field to the response |
| add a filter control that combines with the existing one | add a query filter |
| change the empty and error state contract | change the 401 contract |
| find an injected defect (prefix match where exact was meant) | find an injected defect |

Grading is hidden, through the CDP harness on headless Chrome: set inputs,
dispatch events, wait for quiescence, read the DOM. Equivalence is verified
before any run, over a fixed probe list, on a canonical projection of the DOM
rather than on bytes, because the frameworks add attributes of their own; the
projection is part of the artifact and its limits are stated with it.

Recorded per run: turns, cumulative context, wall time, pass, and the
distinction that matters here, whether a failure is loud (visible error) or
silent (renders, looks right, wrong content).

## C. Dispersion and stale recall

This is the new instrument and the reason for v3. External context is not
free, it is unbilled: the agent recalls it instead of reading it, so it costs
nothing in tokens and comes out in errors.

**C1, dispersion.** For each construct, the number of mutually incompatible
canonical forms in the framework's own published documentation, and the years
since the last change. A count anyone can recompute from published docs.

| Construct | plain JS | React | Angular |
| --- | --- | --- | --- |
| bind an event | | | |
| render a list | | | |
| hold form state | | | |
| run a side effect on mount | | | |
| fetch data | | | |

**C2, stale recall.** The decisive one. The repository is pinned to one
version and carries no documentation. The task's correct answer changed
between versions of that framework. Measured: which version's idiom the agent
produces, and whether the result is silently wrong for the pinned version.
The control is the same shape of task on the plain side, where the platform
did not move, and where the predicted rate is near zero.

The unit here is not tokens. It is the silent-wrong rate.

## Model conditions

Primary condition is the model of v1 and v2, so the numbers compare.

A second, stronger model runs the same tasks, and it tests the claim that
matters: whether this cost is a knowledge deficit or a version
indeterminacy. The v2 failure says it is the second. That agent knew Spring
well, wrote correct JPQL and idiomatic Spring, and still bound the parameter
by the Java name, because the repository named the version in its build file
and never named the version's rules. Holding more versions of a framework
widens the choice the model has to make and narrows nothing.

So the second condition is not a threat control. It is the experiment on the
claim, and the predicted result is that the silent-wrong rate does not fall
materially with model strength.

## Predictions, signed before building

The author's top-line prediction is that this replicates the Java result.
The mechanism should: category 2 volume, and a silent failure from a rule no
file states. Two numbers should not, and are named here so that reporting
them is not a concession extracted later. Category 1 went to plain Java
(7,566 against 8,175) and should go to JSX. Turns separated by 1.25 in the
endpoint runs with the framework taking one task of four, and React
localizes a rendering change more thoroughly than a filter class localizes
authentication, so the turn metric may come out flat or reversed.


1. React category 1 is smaller than plain JS category 1, by 20 to 40 per cent.
   The objection is right about authoring.
2. React category 1 plus 2 is several times plain JS at the same floor;
   Angular larger than React.
3. Turn counts separate less than in the endpoint experiment, and may not
   resolve at 40 runs. The framework wins at least one task outright, as
   Spring won the 401 task.
4. Silent-wrong rate separates: plain JS lower.
5. Dispersion: plain JS near one form per construct, React and Angular
   several, with the last change within three years.
6. Stale recall: the framework sides produce version-mixed code in a
   measurable fraction of runs; the plain side does not.

## Refutation

The design fails if the framework sides do not cost more once category 2 is
counted, or if the silent-wrong and stale-recall rates do not favour plain
JS. Prediction 1 coming true is not a refutation, and prediction 1 coming out
false is not a vindication; both are reported as they land.

## Threats, recorded now

The floor rule is the contested premise, so both ends are always printed. The
frameworks are better represented in training corpora than any particular
plain-JS application, which cuts both ways and is why C2 exists. Small
applications never force category 2 to be read, the same caution as the
endpoint experiment. One model unless the second condition runs. The DOM
projection used for equivalence is a choice, and a different projection could
change a pass into a failure.

## Executed, 2026-08-27

A and B ran as designed; C2 ran with two version boundaries; C1 is still
open. Predictions scored against what landed:

1. Failed, and in our favour: React category 1 is not smaller, it is 1.05
   times plain (1,092 against 1,145 tokens; 1.01 in the single-file
   control). Written in the map-and-innerHTML idiom System A uses, plain
   JS concedes nothing to JSX.
2. Held: category 2 is 282,717 tokens over 29 modules of the React 19.1
   runtime against zero for plain, 2.3 times the Spring closure. Angular
   was not measured.
3. Held exactly: 40 runs, turns flat (6.95 against 6.85, p = 0.91), React
   won one task outright (add a field, 5.6 against 7.6).
4. Failed: no silent-wrong separation, because nothing failed at all,
   40 of 40 and then 30 of 30 in C2.
5. Not yet measured (C1 open).
6. Failed: 30 C2 runs across React 18.3.1 and 19.2.8, zero version-wrong
   choices. The agent never read package.json in any of the ten
   version-critical runs; it did not need version awareness, because its
   habitual idioms are the version-portable ones: every default-value run
   on every side wrote the inline default, never defaultProps, and the
   focus runs wrote forwardRef 7 of 10 times, valid on both versions.
   ref-as-prop appeared only on the side where it works, 3 of 5, which at
   n = 5 may be chance.

What survived everywhere is the turn cost of indirection: threading a ref
across the component boundary cost 12.0 and 13.0 mean turns against
plain's uniform 6.0, twice the turns for identical behavior, with every
run passing. The frontend replicates the pairs result, not the endpoint
result: the framework's conventions did not bite where Spring's binding
did, and what the agent pays for is the walk across the boundary.

## Build order

1. Subjects checked out, closure manifests written, A measured.
2. Twins built, equivalence probe green.
3. Tasks and hidden grader, self-check green.
4. B run, 40 runs.
5. C1 counted from published documentation.
6. C2 built and run, plain control included.
