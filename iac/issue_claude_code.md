# A wakeup primitive for background subagents: cheap idle wait + auditable local coordination

Opening this as a discussion, not a bug. I maintain a small tool that targets a gap I keep hitting with Claude Code, and I think the underlying pattern is worth surfacing even if the tool itself never lands.

**The gap.** Claude Code can run background bash jobs and spawn subagents on one machine, but a subagent has no interrupt inlet. Nothing outside can rouse it between turns; it advances only when the harness re-invokes it. So when one subagent needs to wait on another (fan out and gather, hand a job to whoever is free, wait for a human's redirect), the options today are to poll, which pays a full model inference per check, or to keep a context alive spinning.

**The pattern.** The wait an agent needs is not a socket, it is a blocking `recv` whose return is the wakeup, the same signal a parent already gets when a background child finishes. Push the wait into a cheap child process that just blocks, and let its return re-invoke the agent holding the message. This is the `epoll_wait` instinct: don't poll from the expensive thing.

**What I built.** `iac` is a dependency-free C99 binary implementing exactly that. A backgrounded `iac recv <room> <me> &` parks off the CPU (inotify wake on Linux, sub-millisecond, zero tokens idle) and returns once, on the first message addressed to that agent, which becomes the wakeup. Coordination lives in a single append-only plain-text log the operator can `cat`, `grep`, and version, one total order, no daemon, no sockets, no accounts. Broadcast is one append. `?` addressing hands a task to exactly one free worker (crash-recoverable). A human is just another name on the board, which fits human-in-the-loop steering. It ships a `SKILL.md` self-onboarding protocol for a worker, and the receive pattern is explicitly "background shell job, not a spawned model," so the wait stays I/O, not cognition.

**Limits.** Same host or shared mount, cooperative same-host trust model (no in-band auth; `from` is an unverified label). Right for coordination latency, wrong for a chatty inner loop. Enforcement, if ever needed, goes in the frame as a per-message signature without changing the transport.

**Why I'm posting.** Two things I'd value: (1) whether a cheap-wakeup / background-coordination primitive is in scope for Claude Code's subagent and background-task model, or deliberately out of it; (2) if in scope, whether a plain-text auditable-log approach is the right shape or whether you'd want something else.

Design argument and a measured token-cost comparison: https://doi.org/10.5281/zenodo.21206970
Reference implementation (single C99 binary, ISC): https://github.com/Anode1/iac

Happy to prototype a tighter Claude Code integration if there's interest.
