# Paper outline

Working title: *Silence Is Free: Blackboard Norms for Agent Teams*.
Thesis in one sentence: agent collaboration on a shared board pays only
when silence costs nothing (a parked recv, not a poll), claims are gated
by evidence (Chow's reject option as a posting rule), and priors differ
(else the first post is false confirmation); each condition is testable
and tested.

1. The classic blackboard worked by abstention. Hearsay-II knowledge
   sources fired only when their condition matched; credibility weights;
   the board held justified claims. LLM seats invert the default.
2. Why: no reputation without an iterated game. Spawn-and-die subagents
   have nothing at stake; durable names on a board do (folk theorem).
   Sycophancy/conformity literature; benchmarks reward guessing (OpenAI
   2025); the abstention training wave (Abstain-R1, TIAR, AA-Omniscience
   scoring = Chow).
3. Silence must also be cheap. A polling agent pays inference to say
   nothing; a parked recv pays zero (the wakeup paper's receipt). The
   reject option has no standing cost on this substrate.
4. Mechanism design, not exhortation: receipts turn cheap talk into
   costly signals; the append-only total order is the commitment device
   (claim race in the pilot arbitrated by ordering alone).
5. Predictions 1-6 (../cross_lab/PREDICTIONS.md, dated before board data), the
   metrics table, and the pre-registered sign test.
6. Results: [socket: phase-1 table; norm-variant table; branch-width and
   conformity counts from room logs].
7. Limitations: contamination (seats recall upstream fixes, observed and
   quotable), quota-priced meter, one lab in phase 1.

Register: ~/articles/STYLE.md; claims carry numbers; the flow analysis
(../cross_lab/runs/board/.../FLOW.md) supplies the qualitative specimens.
