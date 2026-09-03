# A Wakeup, Not a Broker: The Minimal Transport for Coordinating Stateless LLM Agents

*Engineering argument / experience report. Reference implementation: iac (github.com/Anode1/iac).*
*Draft: outline + abstract. Intended for Zenodo (citable technical report; not peer-reviewed).*

---

## Abstract

Coordinating multiple LLM agents on a single machine is widely treated as a messaging problem, to be solved with a message queue, an inter-agent protocol, or a hosted bus. We argue this misidentifies the constraint. An LLM agent is not a fast, concurrent consumer but a slow, serial one: it processes a single message per turn, each turn costs seconds, and it cannot parallelize its own reasoning. Moreover, between turns it is not a running process at all, and so has no thread, socket, or event loop on which a message can be delivered. The scarce primitive is therefore not throughput or buffering but a *wakeup*: an interrupt inlet by which an inbound message can rouse an otherwise dormant agent. We show that the only wakeup available to a stateless, harness-invoked agent is the return of a blocking receive executed in a cheap child process, which the harness re-invokes on exit: one model activation per message rather than per poll. Given this, the transport collapses to its minimal form: an append-only per-room log, advisory file locking for ordering and presence, and a blocking `recv`: structurally the Unix local-mail (mbox) delivery model, repurposed. We present `iac`, a dependency-free C99 reference implementation (~1,100 lines, one binary, no runtime), characterize the token-cost model that motivates moving the poll out of the model and into C, situate the design against the current field of agent-coordination tools and protocols, and report an experience in which a fleet of agents used `iac` to develop `iac` itself. The contribution is not a new mechanism (every part is decades old) but an argument that, for this class of consumer, the correct engineering answer is the smallest one: a wakeup, not a broker.

---

## Outline

### 1. Introduction: the misidentified constraint
- The problem: several LLM agents on one machine that need to coordinate.
- The default reflex: reach for a queue / bus / inter-agent protocol (name the field briefly).
- Thesis: the hard part is not moving messages (bytes move fine); it is *waking a reader that, between turns, isn't running.*
- Contributions: (i) the consumer-mismatch argument; (ii) the wakeup primitive + its cost model; (iii) the minimal transport and a reference implementation; (iv) an experience report.

### 2. The consumer an agent actually is
- **Slow:** seconds per turn, not microseconds.
- **Serial:** one message at a time; one context, one attention, one output; cannot parallelize its own reasoning.
- **Dormant between turns:** not a running process (no thread, fd, socket, or event loop); advances only when its harness re-invokes it.
- **Locality bound:** one operator effectively steers only a handful of agents, roughly 3–10 and single-digit for interdependent work, so the fleet never reaches throughput scale in the first place. This is the familiar span-of-control / working-memory range: Miller's 7±2 and Cowan's ~4 for what a mind tracks at once; ~5–6 in the management literature and the military "rule of three-to-five" for interdependent subordinates; bounded further, on one host, by per-agent memory.

### 3. Why a message broker does not fit
- What brokers optimize: throughput, concurrency, fan-out, backpressure: the opposite of a slow serial reader.
- How brokers actually reach consumers: (a) the consumer runs a poll loop, or (b) the broker pushes to a held connection. Both presuppose a *running* consumer.
- A dormant agent has neither; and making the model itself poll costs one full inference per poll (paying an LLM to check an empty box).
- Conclusion: a broker can *hold* the message but cannot *deliver the interrupt* to a reader that isn't there. It does not solve the problem; it adds cost.

### 4. The wakeup primitive
- The one interrupt a stateless agent's environment already supplies: "a background child process finished" → the harness re-invokes the agent.
- So the right primitive is a **blocking `recv` in a cheap C process** (the consumer's poll loop relocated to where it is affordable), whose *return* is the wakeup.
- **One model activation per message, not per poll.** The polling still happens, but in C (nanoseconds), never in the model (a turn).
- **Scope:** stateless / harness-invoked agents (the common case). A hosted long-lived agent has a socket and can be pushed to; that is the heavy path this paper sets aside.

### 5. Cost model
- Formalize model-activation cost: model-held poll ≈ (idle_time / poll_interval) × (context_tokens) inferences; C-held poll ≈ 0.
- Idle cost: a bash `while`-driver re-blocks in C on timeout → **0 tokens while idle, minutes or days**; a model-held foreground loop pays one activation per timeout, plus a prompt-cache miss (full-context reprocessing) past the ~5-min cache TTL.
- Delivery latency: process spin-up + wake: inotify append event (sub-millisecond) on Linux; ~100 ms poll fallback elsewhere.
- Takeaway: the token economics, not aesthetics, force the poll into C.

### 6. The minimal transport (design)
- Room = a directory; **log** = one append-only, totally-ordered stream; per-reader **cursor**; **roster** = presence.
- **Frame** format (`from|to|epoch|len` + body); addressing (`*` broadcast, `name` p2p, `a,b,c` subset, `?` competing-consumers). Broadcast = one append (O(1)).
- **`flock`** does three jobs: serialize appends (total order under concurrent senders), back presence (shared lock = online), guard claims (exclusive).
- **`?` work queue:** crash-recoverable claim via `O_CREAT|O_EXCL` keyed on log offset; unacked-claim steal after a TTL.
- **Presence** = a held `flock`, self-clearing on death (even SIGKILL): no heartbeat, no stale-reap.
- Observation: this is structurally **Unix local mail** (an append-only mbox the delivery agent locks, read forward), pointed at agents instead of people.

### 7. Reference implementation: iac
- ~1,100 lines C99, zero dependencies, one binary; POSIX only (`flock`, `writev`, `pread`/`pwrite`, `dirent`, `inotify` on Linux with a poll fallback).
- Verbs (`send`/`recv`/`drain`/`ack`/`ask`/`join`/`hold`/`who`/`log`/`compact`); the three receive-loop shapes (drain-per-turn / background `recv` / bash `while`-driver) and when each applies.
- Engineering discipline: no heap on any path (footprint = f(struct sizes), not data), bounded strings, single-exit cleanup: the Power-of-Ten / MISRA-C:2012 register; CI builds + sanitizers (ASan/UBSan) on Linux and macOS.

### 8. Related work
- **In-process agent frameworks** (AutoGen/AG2, LangGraph, CrewAI, MetaGPT): orchestration inside one runtime; not cross-process delivery.
- **Same-host agent tools** (tap, hcom, swarm-protocol, ntm, amux, Claude Code Agent Teams): the closest cousins; contrast on dependency/runtime tax and harness lock-in.
- **Inter-agent protocols** (A2A, MCP, ACP, ANP): the networked/enterprise interoperability layer; different scale and target.
- **Classical lineage:** named pipes / Unix domain sockets / ZeroMQ / D-Bus; mbox and Maildir; the actor model and Erlang mailboxes; `poll`/`epoll`.
- **Positioning:** iac's axis is *minimal, dependency-free, same-host, harness-agnostic*, chosen for install-simplicity, auditability, and longevity, orthogonal to feature/scale competition.

### 9. Limitations and trade-offs
- Same-host / shared filesystem only (cross-host needs a shared mount or a socket; NFS `flock` is a known hazard).
- Cooperative trust: `IAC_FROM` is an unverified label; every participant can read every message; the natural extension is a per-frame HMAC verified at `recv`.
- Scale: a single append lock serializes all sends; each reader scans the whole log (shard into rooms); the log grows unbounded (manual `compact`).
- The wakeup argument is scoped to stateless/harness-invoked agents.
- The tool may be subsumed by native harness coordination; the *argument* is the durable contribution.

### 10. Experience: agents building the tool
- Report: a fleet of independent agents used the board to develop the board: a presence/pid fix in the C, a macOS portability pass, the documentation, all coordinated as messages on the plain-text log.
- What it shows: real cross-agent coordination with an auditable transcript (the log reads as a chat history you can `cat`/`grep`).
- Caveat: single-operator, author-controlled agents on one machine (n = 1); a demonstration of feasibility, not a controlled evaluation.

### 11. Conclusion
- For a slow, serial, dormant consumer, the correct transport is the minimal one: a *wakeup*, not a broker.
- None of the parts are new; the assembly and the participant are. The engineering thesis is that, here, minimality is the answer.

---

## References

### A. Primary sources: the reference implementation and its documentation (the evidence)
All at github.com/Anode1/iac unless noted. Every design, cost, and behavior claim in this paper is drawn from and checkable against these; they are the proof, not illustration.
- `README.md`: the model (room / log / cursor / roster), frame format, presence, trust model, and stated limits.
- `doc/dev/RECEIVE_MODEL.md`: the `poll`/`epoll` account of the wakeup, the receive-loop, and the token **cost contract** (§4–§7); the backbone of Sections 3–5.
- `SKILL.md`: the three receive-loop shapes (drain-per-turn / background `recv` / bash `while`-driver) and their cost trade-offs.
- `doc/ORCHESTRATION.md`: the verbs as a control plane, and the messenger-vs-board comparison.
- `doc/INTEGRATION.md`: the ~40-line external-messenger bridge (the hosted / remote-ingress path).
- `doc/ROADMAP.md`: bounded log growth and stale-name reaping (declared future work).
- `*.c`, `*.h`, `tests.c`: the ~1,100-line C99 implementation and the end-to-end test suite (drives the real binary; p2p, broadcast, order, claim, presence, recovery).
- AIS `doc/dev/STYLE.md`: the engineering discipline (no-heap, bounded strings, single-exit) iac conforms to.

### B. Author's related work
- V. Gavrilov, *Intelligence Is the Discovery of Compressors.* Zenodo, https://doi.org/10.5281/zenodo.20440110 (also gavr144.substack.com): the low-entropy / compression thesis that iac's minimality instantiates: coordination compressed to its irreducible primitive, and an artifact low-entropy enough to audit by inspection.
- V. Gavrilov, *The Atree Format.* Zenodo, https://doi.org/10.5281/zenodo.20587715: compact binary-path representation and lineage matching; a kindred low-entropy encoding.
- `ljms` (2001): the author's peer-to-peer message broker with broadcast and multicast; iac descends from it and deliberately removes the broker (see the `README.md` Lineage). Prior, unpublished work.

### C. Landscape (related tools and protocols)
- **tap**: file-based protocol for heterogeneous LLM-agent collaboration (arXiv:2606.14445).
- **hcom, swarm-protocol, ntm, amux, Claude Code Agent Teams**: same-host agent messaging / orchestration (see the *awesome-cli-coding-agents* and *awesome-agent-orchestrators* indexes).
- **A2A** (a2a-protocol.org, v1.0, 2026), **MCP** (Anthropic; Linux Foundation), **ACP** (IBM), **ANP**: networked inter-agent interoperability protocols.

### D. Discipline and lineage
- G. Holzmann, *The Power of Ten: Rules for Developing Safety-Critical Code* (2006); MISRA-C:2012, rule 21.3; A. Robbins, *Linux Programming by Example* (2004).
- E. Raymond, *The Art of Unix Programming* (2003); D. J. Bernstein, Maildir; O'Neil et al., the log-structured merge-tree (1996); C. Hewitt et al., the actor model.
- J. P. Bigus & J. Bigus, *Constructing Intelligent Agents with Java* (Wiley, 1998).
- **Locality bound / span of control (§2):** G. A. Miller, *The Magical Number Seven, Plus or Minus Two* (Psychological Review, 1956): 7±2; N. Cowan, *The Magical Number 4 in Short-Term Memory* (Behavioral and Brain Sciences, 2001): ~4; V. A. Graicunas, *Relationship in Organization* (1933) and L. F. Urwick, *The Manager's Span of Control* (Harvard Business Review, 1956): ~5–6 for interdependent work; U.S. Army organizational doctrine, the "rule of three-to-five" (a commander's span kept at ~3–7 subordinate elements). Cited as supporting intuition for the locality bound, not proof.
