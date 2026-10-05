---
name: foundations-distributed-systems
description: Designs consensus, quorums, leases, idempotency, and CRDTs. Use when facing split brain, fencing tokens, exactly-once claims, duplicate retries, stale reads, or leader flapping.
compatibility: Portable core only.
version: "1.5"
last_validated: 2026-09-17
---

# Distributed Systems Foundations

## When to Apply

**Apply when:**
- 2+ nodes participate in a write or shared state (replication, consensus).
- A retry, timeout or lost response can duplicate or drop an effect (idempotency, "exactly once").
- Two nodes may both act as primary (leases, fencing).
- A consistency level is being chosen per feature (linearizable / causal / eventual).
- Multi-AZ or multi-region failover and quorum sizing are being decided.

**Skip, or route elsewhere, when:**
- No coordination, retry/ambiguous-completion, durability or causal-order question exists. A single node or single writer alone is not a skip condition: a committed effect followed by a lost response can still be duplicated by a serial retry.
- The question is throughput or latency under load: use foundations-queueing-theory.
- The question is overload that persists after the trigger, retry storms or load shedding: use qa-resilience.
- The question is availability or SLO budget: use foundations-reliability-theory.
- The question is which verification tool to use (TLA+, model checking, proofs): use foundations-formal-methods.
- "Strong consistency" is a vague preference, not a stated business invariant: challenge it first; the cost is high.

## Quick Reference: Primitives

One table; each link opens the full playbook (definition, inputs, outputs, failure modes, worked example).

| # | Primitive | Failure it addresses | Reach for it when |
|---|-----------|----------------------|-------------------|
| 1 | [CAP / PACELC](assets/templates/distributed-systems/01-cap-pacelc.md) | Confusing consistency and availability during a partition; latency vs consistency otherwise | Choosing a replication topology or data store |
| 2 | [FLP impossibility](assets/templates/distributed-systems/02-flp-impossibility.md) | Expecting deterministic consensus to always terminate with one crash | Judging liveness claims and timeout assumptions |
| 3 | [Paxos](assets/templates/distributed-systems/03-paxos.md) | Dueling proposers; fragile quorum agreement | Auditing a quorum-based agreement protocol |
| 4 | [Raft](assets/templates/distributed-systems/04-raft.md) | Log divergence; leader ambiguity; production flapping | Leader-based replicated log (etcd, Consul-style stores) |
| 5 | [Vector clocks / Lamport](assets/templates/distributed-systems/05-vector-clocks-lamport.md) | Wall-clock ordering of possibly concurrent events | Deciding whether A happened before B across nodes |
| 6 | [CRDTs](assets/templates/distributed-systems/06-crdts.md) | Merge conflicts in eventually consistent state | Replicas must converge without coordination |
| 7 | [Idempotency](assets/templates/distributed-systems/07-idempotency.md) | Duplicate effects from at-least-once delivery | Retries, redelivery, webhooks, agent tool calls |
| 8 | [Leases and fencing](assets/templates/distributed-systems/08-leases-fencing.md) | Two nodes both believing they hold the lock (split brain) | Leader handover, locks, exclusive resources |
| 9 | [Quorums (NWR)](assets/templates/distributed-systems/09-quorums.md) | Stale reads or lost writes from uncoordinated replication | Choosing N, W, R and failure tolerance |
| 10 | [Causal consistency](assets/templates/distributed-systems/10-causal-consistency.md) | Reads seeing an effect before its cause | Feeds, replies, comments across replicas |
| 11 | [Broadcast protocols](assets/templates/distributed-systems/11-broadcast-protocols.md) | Unordered or lossy dissemination; failure detection | Gossip, total-order broadcast, membership |

Fault tolerance of a majority quorum: quorum = ⌊N/2⌋+1 tolerates ⌊(N−1)/2⌋ failures, so 4 nodes tolerate 1, the same as 3.

## Expert Diagnosis: Reading Symptoms

Go from a bug report to one falsifiable hypothesis before instrumenting anything.

| Symptom | What it smells like | First things to check | Primitive |
|---------|---------------------|------------------------|-----------|
| "We read the old value right after the write succeeded" | The read hit a replica that had not applied the write | Is W + R > N? Is read-your-writes enforced or the read sticky? Did a load balancer route the read elsewhere? | #9, #10 |
| "Two nodes both think they're primary" (split brain) | A lease expired without the storage layer enforcing a fencing token, or a pause exceeded the lease TTL | Is the fencing token checked at the resource (storage), not only in application logic? Any GC pause, VM stop or CPU throttle longer than the lease? | #8 |
| "A write vanished after failover" | Ack before a durable majority, or promotion of a replica not guaranteed to hold every committed entry | Does the ack require majority persistence? Does election enforce the up-to-date-log check? Did the client treat a timeout as a definite failure? | #3/#4, #7 |
| "Duplicate charge/email/row after a retry" | Retry without a stable idempotency key, or a key regenerated per attempt | Is the key client-generated and identical across retries? Is check-and-execute atomic? | #7 |
| "Replicas never converge" | A violated CRDT merge/delivery contract, missed updates, or unsafe metadata GC | State-based: inflationary updates and join merge? Operation-based: concurrent effectors commute and required delivery guarantees hold? Was metadata removed before every relevant replica observed it? | #6, #5 |
| "Retries made the outage worse" / "it stayed down after the dependency recovered" | Synchronized retries, or re-queued timed-out work sustaining overload (metastable) | Triad below for client retries; for a loop that outlives the trigger, see [production-failure-modes.md](references/production-failure-modes.md) and qa-resilience | #7 |
| "Leader keeps flapping" / "consensus looks stuck" | A real partition with no majority, or slow fsync, thread-pool or CPU saturation that looks like a partition to heartbeats | Check host resources and fsync latency before the network; check PreVote/CheckQuorum ([Raft pitfalls](assets/templates/distributed-systems/04-raft.md#production-pitfalls)) | #2, #4 |
| "Healthy per the cluster, failing for clients" | Gray failure: differential observability | Compare client-observed errors with heartbeats ([production-failure-modes.md](references/production-failure-modes.md#gray-failure)) | #11 |
| "Worked in staging, fell over in prod" | Pool exhaustion, a timeout below real tail latency, clock skew beyond the lease margin, or a changed quorum/TTL | See [Operational Triage](#operational-triage-before-protocol-changes) | triage first |

Treat this as triage: match the symptom, check the specific mechanism, confirm with logs or traces, then open the primitive's playbook.

## Consistency Level by Product Feature

Ask which level the specific feature needs; consistency is not one global dial.

| Product feature | Consistency needed | Why | Common mistake |
|-----------------|--------------------|-----|----------------|
| Bank balance / ledger entry | Atomic transactions with invariant enforcement and serializable isolation; strict serializability if real-time order is required | Linearizable individual reads/writes alone do not make a multi-record transfer atomic | Unconstrained LWW/PN-counter balances, or a check-then-write race |
| Inventory decrement | Atomic conditional decrement or serialized invariant check; fenced ownership where applicable | A majority acknowledgement alone does not prevent two writers from overselling | Separating the stock check from the decrement |
| Shopping cart | Causal or eventual (OR-Set) | Availability matters more than order | Routing cart writes through consensus |
| Like / view counters | Eventual (G-/PN-Counter) | A few seconds of undercount is invisible | Coordinating increments through a leader |
| Post + reply ordering | Causal | "Reply before post" is a visible anomaly | Wall-clock ordering; skew reorders causally related posts |
| Session / token revocation | Read-your-writes; linearizable on revocation | A stale "still valid" read is a security defect | Caching validity longer than the revocation SLA |
| Leaderboard | Eventual with periodic reconciliation | Exact real-time rank is rarely a requirement | Transactional re-rank on every update |
| Distributed lock / leader election | Linearizable, consensus-backed, fenced | Lock safety is an invariant | TTL lock with no fencing token |
| Collaborative editing | A convergent editing algorithm (for example RGA), with its required delivery contract | Causal broadcast alone does not specify how concurrent edits merge | Assuming ordered delivery supplies edit conflict semantics |
| Feature flags / kill switch | Declare maximum propagation lag; use linearizable checks when immediate revocation is required | The permitted stale-decision window determines the design | One propagation SLA for all flags |

When a stakeholder asks for "strong consistency" without tracing it to a business invariant (money, inventory, security), challenge it.

## Anti-Patterns

| Anti-pattern | Why it is wrong | Fix |
|--------------|-----------------|-----|
| CAP as "pick 2 of 3" | CAP applies only during a partition | State the partition-time choice; use PACELC for normal-operation latency vs consistency (#1) |
| Claiming "exactly once" delivery | No transport gives end-to-end exactly-once; a durable journal does not make an external effect atomic | At-least-once delivery + idempotent receiver + dedupe store (#7); state the atomicity boundary |
| Leader-only writes without fencing | A deposed leader after a pause keeps writing | Monotonic fencing token per lease; storage rejects stale tokens (#8) |
| One convergence rule applied to every CRDT | State-based and operation-based CRDTs have different contracts | State-based: inflationary updates and join-semilattice merge. Operation-based: concurrent effectors commute under reliable causal delivery; unordered delivery requires all effectors to commute ([Preguiça, Synchronization Model](https://arxiv.org/html/1805.06358)) |
| Quorum reads as "linearizable" | R + W > N gives intersection, not linearizability; partial writes and reconfiguration break "latest read" | Atomic-register or consensus protocol, durable acks, safe reconfiguration; test histories (#9) |
| Causal visibility inferred from timestamps alone | A clock labels events; it does not ensure dependencies are delivered or visible | Track dependencies and enforce causal delivery/visibility. Lamport/HLC timestamps respect happens-before but timestamp order alone does not prove causation ([Lamport, Clock Condition](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)) |
| Assuming consensus is always live | FLP: no deterministic protocol guarantees termination in asynchrony with one crash | State the partial-synchrony assumption; calibrate election timeouts to measured tails (#2, #4) |
| Lease reads with unbounded clock drift | The leader can hold the lease past its validity | ReadIndex by default; leases only with CheckQuorum and a drift bound ([04-raft](assets/templates/distributed-systems/04-raft.md#production-pitfalls)) |
| Single-leader bottleneck in read-heavy WAN workloads | All reads route through the leader | Follower reads with ReadIndex, or leaderless variants; see [research-frontier.md](references/research-frontier.md#wan-consensus-latency) before adopting one |

## The Retry/Timeout/Idempotency Triad

Design these three together; changing one changes the safety requirement of the other two.

- **Timeout shorter than real tail latency** → the caller retries requests that would have succeeded. Safe only if the receiver is idempotent (#7).
- **Retry without backoff and jitter** → synchronized retries hit a degraded downstream together. Use exponential backoff with full jitter, bounded attempts, a retry budget, and a circuit breaker.
- **Idempotency and retry policy solve different problems.** Dedupe also protects broker redelivery and delayed duplicate requests. Bind the key to the payload and commit the key/result atomically with the effect ([AWS idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)).
- **Timeouts:** choose a latency percentile from the tolerated false-timeout rate and include connection/network overhead; no universal p99.9 floor applies. Across hops, propagate an end-to-end deadline and cap each hop by its remaining budget ([deadlines](references/production-failure-modes.md#deadlines-across-hops)).
- **Dedupe retention** must cover the admitted duplicate horizon, including broker redelivery, replay and delayed requests. If delay is unbounded, a finite TTL alone cannot guarantee deduplication.
- **Limit of the triad:** client backoff and jitter alone cannot clear server queues that sustain overload through internal retries; add admission control and a recovery mechanism for that metastable loop (qa-resilience).

## Operational Triage Before Protocol Changes

**Worked example: AWS us-east-1, 20 October 2025** ([post-event summary](https://aws.amazon.com/message/101925/)). AWS describes a DNS automation race followed by recovery overload, rather than attributing the incident to a consensus invariant violation.

1. **Empty DNS record.** A latent race in DynamoDB's DNS automation: two DNS Enactor processes ran concurrently, one stalled, the other applied a newer plan and its cleanup deleted the plan the stalled one had just written. A specific interleaving, the kind deterministic simulation testing is built to find.
2. **Recovery caused the second outage.** Once DynamoDB returned, EC2's DropletWorkflow Manager had to re-establish leases (#8) with a very large host fleet. Lease work timed out and was re-queued, and the service entered "congestive collapse". These re-queued attempts are internal retries, so "retry storm" is a fair label, but the remedy is not client backoff. Engineers throttled incoming work and restarted hosts to clear the queues; AWS's stated fix is a rate limit on incoming work based on the waiting-queue size for EC2 data propagation. This is a metastable failure: see [production-failure-modes.md](references/production-failure-modes.md#overload-that-persists-after-the-trigger-metastable-failure) and qa-resilience.
3. **Backlogged propagation** → NLB health checks failed → many dependent services degraded.

Lessons: the failure was in automation that *manages* the primitives; recovery load exceeded steady-state load and needed queue-depth admission control and a tested recovery path; a regional dependency shared by many services made one control-plane fault systemic. No stronger consensus protocol fixes any of it.

Before changing a primitive to "fix" an incident, ask:
- Was a quorum size, election/lease timeout, TTL or pool limit changed without a capacity or timing review?
- Was the failover path tested under the incident's load and network conditions?
- Is "consensus stuck" really a partition, or fsync, thread-pool or CPU saturation?
- Did a dependency upgrade change a timeout, retry or pooling default?

Check these operational mechanisms before choosing a protocol-level remedy; an incident may have both operational and protocol causes.

## Testing: Deterministic Simulation and Fault Injection

- **Deterministic simulation testing (DST)** runs the system under controlled clock, scheduler, network and disk behavior so failures replay from their seed. Control all relevant nondeterminism; retrofitting these interfaces can require substantial redesign. It finds only faults the simulator can generate.
- **Black-box consistency checking** (Jepsen with the Elle checker) drives a real cluster under real faults and checks the history against the claimed model. Use it to falsify vendor claims, including your own.
- **Historical Jepsen examples:** [MariaDB Galera, March 2026](https://jepsen.io/analyses/mariadb-galera-cluster-12.1.2): recommended `innodb_flush_log_at_trx_commit=0` allowed acknowledged writes to be lost on coordinated crashes. [TigerBeetle, June 2025](https://jepsen.io/analyses/tigerbeetle-0.16.11): two safety issues were found; version 0.16.30 appeared to satisfy Strong Serializability in that exploration. These results are scoped to the tested releases, configurations and workloads. Before selecting a deployed release, check its current documentation, fixes and matching fault-test evidence.
- **Evidence boundary:** adversarial testing can falsify guarantees, not prove bug absence. Record which faults and model were tested, and whether the deployed configuration matches; distinguish proof under assumptions from testing of an implementation.
- Formal verification tool choice (TLA+, P, model checking, proofs) belongs to [`foundations-formal-methods`](../foundations-formal-methods/SKILL.md); the evidence hierarchy is in [formal-theory-map.md](references/formal-theory-map.md#empirical-falsification-complement-not-substitute).

## Workflow

1. Name the failure mode: split brain, stale read, duplicate effect, causal anomaly, lost write, stuck consensus, persistent overload.
2. Map it to a primitive with the [Primitives](#quick-reference-primitives) and [symptom](#expert-diagnosis-reading-symptoms) tables; do operational triage first.
3. Open the primitive's playbook; load the [template composition guide](assets/templates/distributed-systems/README.md) when choosing a stack, then use [composition-recipes.md](references/composition-recipes.md) for scenario contracts.
4. Check the [Anti-Patterns](#anti-patterns) and [patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) before asserting "exactly once", "leader safe" or "CRDT-friendly".
5. Verify protocol guarantees against primary papers, naming the failure/timing model and safety versus liveness. Decide how each implementation claim will be falsified (DST, Jepsen-style checking, model checking) before implementation.

For every advertised guarantee, keep a **guarantee ledger** with one row per property: `operation scope | safety/liveness property | fault model | timing model | durability boundary | evidence`. "Consensus-backed", "exactly once" and "available" are incomplete until the row names which failures are tolerated and which property survives them. Evidence for safety does not establish liveness.

## Navigation

- [references/composition-recipes.md](references/composition-recipes.md): read when stacking primitives (multi-region writes, exactly-once receiver, split-brain prevention with the 3- vs 5-node worked example, gossip, agent tool calls and the durable-execution correctness contract).
- [references/production-failure-modes.md](references/production-failure-modes.md): read for persistent overload, gray failure, multi-hop deadlines, hedged requests, and clock-based safety (leases, HLC, bounded-uncertainty clocks).
- [references/execution-histories.md](references/execution-histories.md): read when writing a receiver contract with allowed and forbidden histories.
- [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md): read before asserting a guarantee.
- [references/formal-theory-map.md](references/formal-theory-map.md): read when the design depends on model assumptions (asynchrony, happens-before, quorum intersection, linearizability vs serializability).
- [references/research-frontier.md](references/research-frontier.md): read only when choosing among research protocols (DAG-BFT, WAN fast paths, cross-cluster broadcast, encrypted CRDTs).
- [references/primitives-overview.md](references/primitives-overview.md): domain-by-domain anti-patterns.
- Sources and verification dates: [`data/sources.json`](data/sources.json).

## Related Skills

- [`qa-resilience`](../qa-resilience/SKILL.md): metastable failures, retry budgets, load shedding, chaos testing.
- [`foundations-formal-methods`](../foundations-formal-methods/SKILL.md): choosing and running TLA+, model checkers and proofs.
- [`ai-coding-agents-state`](../ai-coding-agents-state/SKILL.md): durable-execution runtime selection for agent tasks.
- [`foundations-queueing-theory`](../foundations-queueing-theory/SKILL.md) and [`ai-llm-inference`](../ai-llm-inference/SKILL.md): capacity, tail latency, disaggregated serving.
- [`software-architecture-design`](../software-architecture-design/SKILL.md), [`data-streaming`](../data-streaming/SKILL.md), [`ops-devops-platform`](../ops-devops-platform/SKILL.md), [`agents-subagents`](../agents-subagents/SKILL.md), [`software-realtime`](../software-realtime/SKILL.md): domain applications of these primitives.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
