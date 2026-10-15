# A Wakeup, Not a Broker

**On one machine, what an LLM agent lacks is a wakeup; the transport that serves it is a
text log, a file lock and a blocking `recv`.**

An LLM agent is a slow serial consumer. It processes a single message per turn, each turn
costs seconds, and it cannot parallelize its own reasoning. Between turns it has no thread,
socket or event loop on which a message can be delivered. The only wakeup available to a stateless,
harness-invoked agent is the return of a blocking receive executed in a cheap child process,
which the harness re-invokes on exit: one model activation per message.

The transport is an append-only per-room log, advisory file locking for ordering and
presence, and a blocking `recv`: the Unix local-mail delivery model, repurposed. The reference implementation is
[iac](https://github.com/Anode1/iac), about 1,100 lines of C99, one binary, no runtime. Every
part is decades old; the argument is that for this class of consumer the correct engineering
answer is the smallest one.

`experiment/` holds the token-cost measurement (`tokenbill.py` and its results). A fleet of
agents used iac to develop iac, and that experience is reported in the paper.

[iac.pdf](iac.pdf),
[doi:10.5281/zenodo.21206970](https://doi.org/10.5281/zenodo.21206970).
