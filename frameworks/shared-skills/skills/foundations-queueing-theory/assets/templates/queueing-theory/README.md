# Queueing Theory Primitives — Composition Guide

11 domain-agnostic queueing-theory primitives for capacity planning, saturation prediction, and backpressure design. Each file is a standalone playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist, composition recipes — lives in [`../../../SKILL.md`](../../../SKILL.md) and [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | Core Question It Answers |
|---|------|--------------------------|
| 1 | [01-littles-law.md](01-littles-law.md) | How do queue depth, arrival rate, and latency relate at steady state? |
| 2 | [02-mm1.md](02-mm1.md) | How does a single-server system behave as utilization increases? |
| 3 | [03-mmc.md](03-mmc.md) | How many parallel servers meet a wait-time SLO at given load? |
| 4 | [04-mg1-pollaczek-khinchine.md](04-mg1-pollaczek-khinchine.md) | How much does service-time variability inflate queue wait? |
| 5 | [05-priority-queues.md](05-priority-queues.md) | How do I protect high-priority workloads from low-priority queue congestion? |
| 6 | [06-jackson-networks.md](06-jackson-networks.md) | Where is the bottleneck in a multi-stage microservice pipeline? |
| 7 | [07-kingman-formula.md](07-kingman-formula.md) | What is the queue wait when arrivals and service are both non-Poisson/non-exponential? |
| 8 | [08-bufferbloat.md](08-bufferbloat.md) | Why is latency high even though throughput looks fine and packet loss is zero? |
| 9 | [09-usl-universal-scalability.md](09-usl-universal-scalability.md) | Will adding more servers improve throughput or trigger retrograde? |
| 10 | [10-loss-systems-erlang-b.md](10-loss-systems-erlang-b.md) | How many channels/servers keep blocking probability below a target GoS? |
| 11 | [11-fork-join-parallel.md](11-fork-join-parallel.md) | How much does fan-out parallelism help latency when the join waits for the slowest worker? |

---

## Composition Stacks by Scenario

### Capacity Plan for a New Service

**Goal**: Size the server pool before launch.

1. **Little's Law** (01): derive steady-state L, λ, W from initial estimates.
2. **M/M/c** (03): compute minimum server count for target Wq SLO.
3. **P-K / Kingman** (04, 07): adjust for measured service-time variability (CV²_s) and bursty arrivals (CV²_a).
4. **USL** (09): confirm that adding servers scales throughput in the expected regime.

---

### Saturation SLO — Predicting Latency Cliff

**Goal**: Determine the utilization threshold at which latency breaches SLO.

1. **M/M/1** (02): establish baseline latency vs. ρ curve; find ρ where W > SLO.
2. **Kingman** (07): apply real CV²_a and CV²_s; true cliff is earlier than M/M/1 alone.
3. **Bufferbloat** (08): check whether large application queues mask the cliff with latency spikes rather than errors.
4. **Little's Law** (01): verify Lq = λ × Wq; alert on queue depth as leading indicator.

---

### Multi-Stage Pipeline Bottleneck Identification

**Goal**: Find and fix the throughput bottleneck in a microservice chain.

1. **Jackson networks** (06): solve flow-balance equations; identify station with highest ρᵢ.
2. **M/M/c** (03): compute servers needed at bottleneck station to achieve target ρ.
3. **USL** (09): verify that scaling the bottleneck does not trigger retrograde at downstream stages.
4. **Priority queues** (05): if SLO classes mix at bottleneck, separate with priority scheduling.

---

### Fan-Out / Scatter-Gather Latency Sizing

**Goal**: Predict p50 and p99 completion time for a fan-out of K parallel workers.

1. **Fork-join** (11): compute E[max] = E[S] × H_K; assess p50 SLO feasibility.
2. **M/M/1** (02): each worker operates at ρ; compute individual Wq for each worker.
3. **P-K** (04): if workers have high CV²_s (e.g., LLM inference), inflate E[max] appropriately.
4. **Priority queues** (05): add hedge request / speculative execution for tail risk.

---

### Loss System Sizing (Calls/Connections Dropped at Capacity)

**Goal**: Size channels to keep blocking below GoS target.

1. **Erlang-B** (10): compute B(c, a) for candidate c values; find minimum c for target GoS.
2. **Little's Law** (01): carried load = a × (1 − B); verify occupancy.
3. **Erlang-C / M/M/c** (03): cross-check: if the system actually queues some load, use Erlang-C.

---

## When to Escalate to Simulation

These primitives cover analytical closed-form cases. Use discrete-event simulation (DES) when:

- Service or inter-arrival distributions are not well-characterized by mean + variance alone (empirical histogram required).
- System has complex routing, finite buffers, and priority simultaneously.
- Fork-join with load-dependent workers or correlated sub-task times.
- Transient (non-steady-state) behavior during startup or incident recovery is the target.

Recommended tools: SimPy (Python), JMT (Java Modeling Tools, GUI + MVA), CloudSim, or custom Monte Carlo.
