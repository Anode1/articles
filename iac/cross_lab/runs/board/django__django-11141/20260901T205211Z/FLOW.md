# Flow analysis of the board pilot (room-log.txt)

Three sonnet seats, django__django-11141, patch scored RESOLVED. Times are
seconds after the first message.

- t+0..11: three diagnoses posted before any seat read another, and they
  are near-identical (same file, line, root cause). Same-model diagnostic
  diversity on this instance was ~zero; the one divergence is seat3's
  multi-path guard, which reached the final patch. Whether cross-lab seats
  diverge here is phase 2's question.
- t+50..73: seat2 and seat3 race for loader.py; seat2 yields citing claim
  order. The append-only log's total order arbitrated, with no lock
  mechanism, because "who claimed first" is a shared verifiable fact.
- t+53: division of labour emerges unprompted: fix / tests / docs, the
  shape of a human patch review. The brief specifies no roles.
- t+80..185: seat1, beaten to the claim, becomes a verifier: finds an
  unused fixture corroborating the intended fix, builds a venv around a
  broken py3.12 parallel runner, runs 26 tests green. No verifier role
  exists in the brief.
- t+165: contamination in the open: seat1 checks the fix against its
  memory of the real upstream patch. On a board this is a quotable,
  auditable line; in a solo transcript it stays buried.
- t+715: seat1 exits after its four allowed recv timeouts, reporting the
  release-notes item still pending (seat2 died at the 40-turn cap).

14 messages, 11.9 min, $2.11 across seats.
