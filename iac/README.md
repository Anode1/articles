# A Wakeup, Not a Broker

**Coordinating LLM agents on one machine is not a messaging problem: the scarce primitive is
a wakeup, not a queue.**

An LLM agent is not a fast concurrent consumer but a slow serial one. It processes a single
message per turn, each turn costs seconds, and it cannot parallelize its own reasoning.
Between turns it is not a running process at all, so it has no thread, socket or event loop
on which a message can be delivered. The only wakeup available to a stateless,
harness-invoked agent is the return of a blocking receive executed in a cheap child process,
which the harness re-invokes on exit: one model activation per message rather than per poll.

Given that, the transport collapses to its minimal form: an append-only per-room log,
advisory file locking for ordering and presence, and a blocking `recv`. Structurally that is
the Unix local-mail delivery model, repurposed. The reference implementation is
[iac](https://github.com/Anode1/iac), about 900 lines of C99, one binary, no runtime. Every
part is decades old; the argument is that for this class of consumer the correct engineering
answer is the smallest one.

`experiment/` holds the token-cost measurement (`tokenbill.py` and its results). A fleet of
agents used iac to develop iac, and that experience is reported in the paper.

[paper/iac.pdf](paper/iac.pdf),
[doi:10.5281/zenodo.21206970](https://doi.org/10.5281/zenodo.21206970).
