EXPERIMENT PLAN
===============

Paper:
"What Do People Optimize in Graph Layout?"

Goal:
Complete the empirical part of the manuscript without changing the
scientific question or fabricating missing results.

The manuscript's primary estimand is:

    q_d(x) = fraction of nodes i for which
             E(x + d v^(i)) >= E(x)
             for all 16 directions v.

Primary radius:

    d = 0.02

Sensitivity:

    d = 0.005, 0.01, 0.02, 0.05

The primary analysis is deterministic and is preferred over the old
capped-descent pilot.


============================================================
1. FINAL DATASET
============================================================

Use:

WikiPathways:
    Homo sapiens
    final filtered set
    15--40 nodes
    expected n = 305

Reactome:
    SBGN-ML
    final filtered set
    15--40 nodes
    expected n = 248

BPMN:
    BPMN Academic Initiative
    retain models whose edges are BPMN flow/association under the
    manuscript's parser rules
    15--40 nodes
    use the final 300 models

For every input:

    - take largest connected component
    - exclude container glyphs
    - preserve node box sizes
    - rescale bounding box to unit square
    - scale box sizes consistently
    - preserve stored edge geometry where applicable

Record hashes and final counts.


============================================================
2. PRIMARY DIRECTIONAL TEST
============================================================

For every diagram:

    for each energy term:
        crossings
        overlap
        length
        stress
        orthogonality
        alignment A1
        alignment A3
        gridiness
        node-edge separation
        flow

    for each requested sum:
        C+O
        C+O+L
        C+O+S
        C+O+R
        C+O+A1
        C+O+A3
        C+O+grid
        C+O+N
        C+O+F

Evaluate:

    q_0.02

using:

    16 equally spaced directions
    exact double-precision direction vectors
    tie threshold = 1e-12 relative to energy

Also compute:

    median term value
    bootstrap 95% interval over diagrams

Use the SAME graphs and node sizes for:

    hand
    neato
    prism / neato with overlap removal
    dot
    ELK layered


============================================================
3. STORED-ROUTE EXPERIMENT
============================================================

The existing manuscript uses centre-to-centre chords as the main
sensitivity.

Now repeat the affected terms using the actual route representation:

    crossings
    orthogonality
    node-edge separation

For a stored polyline:

    source attachment
    interior waypoints
    target attachment

When the format has no stored route:

    use the chord.

When a format computes bends at rendering time but stores endpoints only,
document exactly what representation is used.

Compare:

    chord result
    stored-route result

Question:

    Does the main human-versus-tool result survive?

Output:

    table with q_0.02 for hand/neato/prism/dot/ELK
    bootstrap intervals for hand
    paired differences where appropriate


============================================================
4. FLOW EXPERIMENT
============================================================

Implement/verify T_F exactly as described:

    choose one of the four axis directions
    choose the direction minimizing T_F for the loaded layout
    fix it before any node move

Exclude undirected edge types.

Run:

    hand
    neato
    prism
    dot
    ELK

Report:

    q_0.02
    median T_F

Question:

    Is the human layout locally held because of reading direction?


============================================================
5. CONTAINMENT / BPMN LANES
============================================================

Investigate BPMN containment and lane structure.

Important:

    y-alignment is very high in BPMN.
    This may be imposed by lanes rather than an independently selected
    alignment aesthetic.

Do NOT count lane-induced alignment as evidence of free-space alignment.

If possible, separate:

    alignment within same lane
    alignment across lanes
    lane boundaries / containment constraints

Report clearly what can and cannot be attributed to the person.

Question:

    How much of the BPMN alignment signal survives after accounting for
    lanes and containment?


============================================================
6. ELK CONTROL
============================================================

Use final:

    ELK layered
    elkjs version explicitly recorded
    direction RIGHT
    all other options default

Confirm:

    same graph
    same node dimensions
    same edge directions

Generate final control layouts.

Recompute all primary metrics.

Question:

    Is the "layered profile" still present in a tool used by the relevant
    modeling ecosystem?


============================================================
7. MATCHED-BUDGET CONTROL
============================================================

Run:

    cjitter_compare

on final 15--40 node data.

Compare:

    hill climbing
    uniform random placement

Use:

    same graph
    same cap
    same evaluation budget
    same seeds

Do NOT compare different computational budgets.

Report:

    number of instances where climber beats random
    exact paired sign test
    Holm correction if multiple comparisons are made
    effect estimate

The claim should be:

    the search does better than uniform sampling at equal cost

not:

    the search proves the human layout is optimal.


============================================================
8. FINAL INVERSE OPTIMISATION
============================================================

For each corpus:

    build directional differences D_iv T_k

Solve:

    minimize total violation
    subject to w_k >= 0
    sum_k w_k = 1

Use HiGHS.

Report:

    fitted weights
    residual
    residual per node
    q under fitted weights

Then run:

    five seeded 2-fold splits

For each split:

    fit on half
    score q on other half

Important:

Overlap is exactly satisfied in human layouts.
Therefore an overlap-only weight vector can have zero residual.

This makes the raw fitted weight vector degenerate.

Therefore the informative analysis is:

    weight sweep

For each candidate term:

    start with crossings + overlap
    increase candidate weight
    decrease remaining weights proportionally
    measure q

Question:

    Can any positive weight on a candidate criterion coexist with
    stationarity of the human layouts?


============================================================
9. SPARSITY ANALYSIS
============================================================

Compute diagram-level relationship between:

    q_d
    m/n

for:

    crossings
    overlap
    possibly length/stress

Use diagram as unit of inference.

Question:

    Are the high held fractions simply caused by sparse near-tree graphs?

Compare with:

    same-graph tool controls

The tool controls are essential because they preserve graph sparsity.


============================================================
10. RADIUS ANALYSIS
============================================================

Repeat/verify:

    d = .005
    d = .01
    d = .02
    d = .05

Also, if feasible:

    d / median box width
    d / median box height
    d / median edge length

Do not overcomplicate this if the existing sweep is sufficient.

The key result to preserve is:

    hand length/stress q remains approximately zero across radius,
    whereas neato stress q approaches 1.


============================================================
11. REFERENCE LENGTH
============================================================

Verify:

A. fitted reference

    L_length = sum ell^2 / sum ell

    L_stress = sum (distance / graph-distance)^? 

Use the exact implementation in the manuscript/code.

B. median edge length

C. 1/sqrt(N)

The purpose is sensitivity, not choosing the reference after seeing
the hand result.

Question:

    Is the zero hand q an artifact of the reference scale?

Expected from current draft:

    hand result remains zero/near-zero;
    neato control is sensitive.


============================================================
12. STATISTICS
============================================================

Primary unit:

    diagram

For hand vs control:

    Wilcoxon signed-rank
    zeros dropped
    midranks for ties
    exact where appropriate
    normal approximation above specified threshold
    exact sign test as secondary
    Hodges-Lehmann shift + distribution-free 95% interval

Holm-correct within the specified family.

Do not use "failure to reject" to make equivalence claims.

For "no reweighting repairs it":

    use the weight sweep and/or residual geometry,
    not a non-significant p-value.


============================================================
13. OUTPUT FILES
============================================================

Generate machine-readable output, ideally:

    results/
        criteria.csv
        sums.csv
        routes.csv
        radius.csv
        reference_length.csv
        flow.csv
        containment.csv
        sparsity.csv
        matched_budget.csv
        inverse_fit.csv
        weight_sweep.csv
        statistics.csv

Also generate:

    run_manifest.txt

containing:

    git commit
    date/time
    OS
    compiler
    library versions
    Graphviz version
    ELK version
    HiGHS version
    corpus hashes
    command lines
    seeds
    sample counts


============================================================
14. MANUSCRIPT INSERTION POINTS
============================================================

Insert final results at these locations:

A. "Each criterion alone"
   Replace current provisional table if final run differs.

B. "The sums"
   Replace current table if final run differs.

C. "Radius"
   Replace with final radius output.

D. "Reference length"
   Replace with final sensitivity output.

E. "Chance"
   Replace old 373-diagram pilot result with final matched-budget result.

F. "Reweighting"
   Replace pilot descent-fit table with final LP residual/weight results.

G. After "Routes"
   Add stored-route sensitivity.

H. Alternatives #4
   Add flow/containment results.

I. Alternatives #6
   Add sparsity result.

J. Alternatives #7
   Add final ELK control.

K. Reproducibility
   Add commit hash and run manifest.


============================================================
15. WHAT MUST NOT CHANGE WITHOUT EVIDENCE
============================================================

Do not change the central interpretation merely because one secondary
experiment gives a complicated result.

The paper's hierarchy is:

    PRIMARY:
        local stationarity by criterion

    SECONDARY:
        capped descent / optimization behavior

    CONTROLS:
        neato
        prism
        dot
        ELK
        matched-budget random search

    SENSITIVITIES:
        radius
        reference length
        route representation

    ALTERNATIVE EXPLANATIONS:
        grid snapping
        sparsity
        reading direction
        containment/lanes
        wrong tool controls


============================================================
16. FINAL SCIENTIFIC QUESTION
============================================================

At the end, answer this precisely:

    Which terms of a conventional graph-layout energy actually hold
    human-accepted coordinates locally, and which additional criteria
    are necessary to explain those coordinates?

The current evidence suggests:

    overlap:
        yes

    uniform edge length:
        no

    stress:
        no

    alignment:
        yes, substantially

    orthogonality:
        corpus-dependent, especially BPMN

    node-edge separation:
        mostly flat / already satisfied

    flow:
        unresolved until final experiment

    containment/lanes:
        unresolved for BPMN

The final conclusion must reflect the final experiments rather than
assuming these provisional interpretations survive unchanged.
