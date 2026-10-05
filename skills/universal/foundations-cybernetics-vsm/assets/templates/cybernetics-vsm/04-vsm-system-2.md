# Primitive 4: VSM System 2 — Coordination

## Definition

**System 2 (S2)** is the anti-oscillation coordination layer between S1 operational units. It does not command S1; it provides the scheduling, information-sharing, and synchronisation signals that prevent S1 units from interfering with each other.

S2 is not a management layer — it has no authority over S1 units. It is an information channel and a shared protocol. Typical S2 mechanisms: scheduling systems, shared resource queues, event buses, coordination meetings, standard operating procedures for handoffs.

Without S2, S1 units optimising independently will produce oscillation, resource contention, and contradictory outputs. Beer called this the "stability sub-system."

## When to Use

- When S1 units share resources (compute, budget, users, data).
- When S1 unit actions have timing dependencies or ordering constraints.
- When two S1 units can produce contradictory outputs visible to the same environment.
- When diagnosing thrashing, deadlock, or race conditions between teams or services.

## Inputs

| Input | Description |
|-------|-------------|
| S1 unit schedules and resource claims | What each unit intends to do and when |
| Shared resource inventory | What is available and at what capacity |
| Conflict signals | Reports of interference or contention from S1 units |
| Coordination rules | Protocols agreed between units (not imposed by S3) |

## Outputs

| Output | Description |
|--------|-------------|
| Synchronised schedules | Non-conflicting activity timelines for S1 units |
| Resource allocation signals | Visibility of shared resource state to all S1 units |
| Conflict resolution records | Documentation of resolved interference events |
| Coordination protocol updates | Revised rules when new interference patterns emerge |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| S2 absent — units thrash | No coordination layer; each S1 unit unaware of others' actions | Introduce shared calendar, resource queue, or event bus |
| S2 becomes S3 | Coordination layer starts directing S1 rather than informing it | Audit S2 authority; remove any command-and-control elements |
| Over-coordination | S2 overhead exceeds coordination benefit | Reduce coordination frequency; use exception-based triggers instead of continuous sync |
| Coordination lag | S2 cycle time too slow for S1 action frequency | Reduce S2 latency; move to event-driven rather than periodic coordination |

## Worked Example

**Context**: Three agent executors (research-agent, drafting-agent, fact-check-agent) run in parallel on overlapping document sets.

**S2 design**:
- Shared document lock registry: each agent registers a document claim before reading/writing.
- Event bus: agents publish state-change events (e.g., `draft_ready`, `fact_check_complete`).
- Sequencing rule (coordination protocol): fact-check-agent only activates after `draft_ready` event; research-agent may run in parallel.
- Conflict detection: if two agents claim the same document, S2 signals the second agent to queue.

**What S2 does not do**: S2 does not decide which documents are processed or in what priority order — that is S3's policy domain. S2 only ensures the agents do not collide on the same resource at the same time.

## Sources

- Beer, S. (1972). _Brain of the Firm_. Allen Lane. Section "Autonomics — Systems One, Two, Three" — System Two as the anti-oscillation damper. *(2026-07 correction: no standalone "System Two" chapter exists; Systems One–Three are treated in one section per the verified table of contents.)*
- Beer, S. (1985). _Diagnosing the System for Organizations_. Wiley. S2 identification and design exercises.
- Hoverstadt, P. (2009). _The Fractal Organization_. Wiley. S2 in practice: what coordination protocols actually look like (ch. 3).
- Schwaninger, M. (2006). _Intelligent Organizations_. Springer. S2 and stability maintenance in complex organisations.
