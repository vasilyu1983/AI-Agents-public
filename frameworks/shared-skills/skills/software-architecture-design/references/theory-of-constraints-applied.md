---
description: Theory of Constraints applied to software architecture decisions — bottleneck identification across services, throughput accounting for investment, policy-constraint detection, CRT for performance stalls, and evaporating cloud for stability-vs-velocity tensions.
foundation: foundations-theory-of-constraints
last_verified: 2026-05-02
status: stable
---

# Theory of Constraints Applied to Software Architecture

> **Gate before invoking:** Check [`foundations-theory-of-constraints` § When to Apply](../../foundations-theory-of-constraints/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Why TOC Applies to Architecture](#why-toc-applies-to-architecture)
- [Patterns](#patterns)
  - [P1 — System-Wide Bottleneck Identification via 5FS over the Service Map](#p1--system-wide-bottleneck-identification-via-5fs-over-the-service-map)
  - [P2 — Throughput Accounting for Architecture Investment Decisions](#p2--throughput-accounting-for-architecture-investment-decisions)
  - [P3 — Policy-Constraint Detection in API Contracts and Deployment Processes](#p3--policy-constraint-detection-in-api-contracts-and-deployment-processes)
  - [P4 — Current Reality Tree for Architecture-Level Performance Stalls](#p4--current-reality-tree-for-architecture-level-performance-stalls)
  - [P5 — Evaporating Cloud for Stability-vs-Velocity Tensions](#p5--evaporating-cloud-for-stability-vs-velocity-tensions)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Refactoring Non-Bottleneck Services](#a1--refactoring-non-bottleneck-services)
  - [A2 — Replacing the Entire Stack When One Component Is the Constraint](#a2--replacing-the-entire-stack-when-one-component-is-the-constraint)
  - [A3 — Optimizing Latency on Services with Idle Capacity](#a3--optimizing-latency-on-services-with-idle-capacity)
  - [A4 — Cost-Accounting Architecture Choices Instead of Throughput-Accounting Them](#a4--cost-accounting-architecture-choices-instead-of-throughput-accounting-them)
  - [A5 — Treating Policy Constraints as Immutable](#a5--treating-policy-constraints-as-immutable)
- [Recipes](#recipes)
  - [R1 — System-Wide Bottleneck Hunt](#r1--system-wide-bottleneck-hunt)
  - [R2 — Refactor Scope Decision via Throughput Accounting](#r2--refactor-scope-decision-via-throughput-accounting)
  - [R3 — Stability-vs-Velocity ADR via Evaporating Cloud](#r3--stability-vs-velocity-adr-via-evaporating-cloud)
- [Composition](#composition)
- [Sources](#sources)

---

## Why TOC Applies to Architecture

A distributed system is a chain. Total throughput — requests completed, features deployed, revenue recognized — is set by its weakest link, not by the average performance across all services. Architectural decisions that strengthen non-bottleneck links do not increase throughput; they increase local efficiency at the cost of real investment.

TOC gives architects three things the standard toolkit does not:

1. **A principled reason to say no** to improvement work on non-bottleneck services.
2. **A financial frame** (throughput accounting) that evaluates architectural investment by system-level impact, not by service-level cost reduction.
3. **A conflict-resolution method** (evaporating cloud) that dissolves deadlocks between architectural camps — stability vs. velocity, centralized vs. federated, monolith vs. services — without compromise.

The primitives here are domain-specific applications of the canonical TOC tools in
[`../../../foundations-theory-of-constraints/SKILL.md`](../../../foundations-theory-of-constraints/SKILL.md).
Full playbooks for each primitive live in
[`../../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/`](../../../foundations-theory-of-constraints/assets/templates/theory-of-constraints/).

---

## Patterns

### P1 — System-Wide Bottleneck Identification via 5FS over the Service Map

**Problem**: Engineering effort spreads across every service in a distributed system. Throughput does not improve because the real constraint — one overloaded service, one slow downstream dependency, one serialized deployment step — is never named.

**TOC Primitive**: Five Focusing Steps (5FS).

**Architecture Translation**:

Map services and their inter-service flows as a value stream. For each node, collect:

- Observed queue depth (requests waiting at each service boundary).
- P99 latency and saturation ratio (CPU/connection-pool/thread-pool utilization at peak).
- Deployment frequency and rollback rate (for delivery-pipeline bottlenecks).

The constraint is the node with the deepest sustained queue or the highest saturation at peak load — not the slowest average latency and not the highest nominal utilization in isolation.

**5FS applied to a service map**:

1. **Identify**: run the service map with queue depths and utilization. The constraint is the node whose queue grows while all upstream queues stay bounded.
2. **Exploit**: eliminate waste at the constraint without new capacity — remove N+1 queries, increase connection pool to the database ceiling, add a read replica in front of the constraint service, shed non-critical work.
3. **Subordinate**: rate-limit all upstream callers to what the constraint can process. Do not accept more traffic than the constraint can drain. Add backpressure or a queue with a depth cap.
4. **Elevate**: if exploit + subordinate do not clear the constraint at target throughput, invest — horizontal scale, hardware upgrade, rewrite of the hot path.
5. **Repeat**: after elevation, the constraint shifts. Re-run the measurement pass to find the new weakest link before the next sprint begins.

**Example**: A payment service at 92% CPU saturation with a 400-request queue is the constraint. The fraud-scoring service runs at 20% CPU. Investing in fraud-scoring performance does not increase payment throughput. Exploit payment first: batch fraud calls, cache low-risk verdicts, raise connection-pool limit. Subordinate: cap inbound payment API rate to match fraud throughput after the batch optimization. Elevate only if needed.

**Signal to apply**: multiple teams are "optimizing" different services and throughput is flat.

---

### P2 — Throughput Accounting for Architecture Investment Decisions

**Problem**: Architecture decisions — migrate to a new database, decompose a monolith, adopt a service mesh — are evaluated on cost reduction ("this will save N engineer-hours") rather than on their impact on system throughput. Low-T/CU investments get prioritized; the constraint stays untouched.

**TOC Primitive**: Throughput Accounting (T, I, OE).

**Architecture Translation**:

Map architectural investment decisions to TOC metrics:

| Decision | Throughput (T) Impact | Investment (I) | Operating Expense (OE) |
|----------|-----------------------|----------------|------------------------|
| Shard the constraint database | Removes the constraint → T increases significantly | Migration cost, new infra | Increased DB ops cost |
| Re-architect a non-constraint service | Does not move the constraint → T unchanged | High migration cost | Neutral |
| Add a read replica to the constraint service | Exploit step → T increases | Low (replica cost) | Marginal increase |
| Adopt service mesh across all services | No constraint impact → T unchanged | High rollout cost | Increased mesh ops overhead |

**Decision rule**: rank every architectural investment by its **Throughput per Investment Unit** (T/IU) — the expected throughput gain divided by the investment cost (engineer-time + infrastructure + risk exposure). Investments that do not move the constraint have T/IU ≈ 0.

**Example**: Three proposals are on the table — (a) migrate from PostgreSQL to CockroachDB at the constraint service, (b) refactor the notification service to async, (c) introduce Istio mesh. Proposal (a) removes the database constraint and unlocks T. Proposal (b) improves a non-bottleneck. Proposal (c) adds operational overhead without moving T. TA ranking: (a) first, (b) deferred, (c) rejected until the constraint shifts to network policy.

**Signal to apply**: architecture roadmap is full of "quality improvements" and throughput is flat; every proposal is justified by cost savings rather than throughput gain.

---

### P3 — Policy-Constraint Detection in API Contracts and Deployment Processes

**Problem**: Physical capacity appears available — services have headroom, infrastructure is not saturated — but throughput still does not increase. The real constraint is a rule, not a resource: a synchronous approval gate in the deployment pipeline, an API contract that forces sequential calls, a rate limit that cannot be raised without a vendor change-control process.

**TOC Primitive**: Policy Constraints.

**Architecture Translation**:

Policy constraints in software architecture appear in three forms:

| Policy Form | Example | Detection Signal |
|-------------|---------|-----------------|
| API contract enforcing sequential calls | A downstream API that does not support bulk or async requests forces the caller to serialize | High caller latency despite low service CPU; queue builds at the call site |
| Deployment process gate | Manual approval required before every production deploy; change-advisory board meets weekly | Deploy frequency capped at gate cadence regardless of team capacity |
| Infrastructure change-control rule | Database schema migrations require DBA sign-off; migrations batch weekly | Feature velocity constrained by schema review schedule, not engineering throughput |

**Detection procedure**:

1. Audit the service map for nodes where queue depth is high but service CPU/memory is low — the constraint is upstream of the service, in the call protocol or process.
2. Audit the deployment pipeline: count handoff points that require human approval or batch scheduling. Each is a potential policy constraint.
3. Read API contracts for the constraint service's dependencies: are there per-minute rate limits, synchronous-only endpoints, or schema-version locks that prevent parallelism?

**Exploit before elevating**: most policy constraints can be partially bypassed without removing them — batch API calls to stay under rate limits, parallelize deployment stages that do not share state, automate low-risk approval gates with fitness functions.

**Example**: An order-processing service hits 1,000 req/s but the downstream inventory API enforces a 500 req/s per-key rate limit. The physical constraint (order service CPU) is at 30%. The policy constraint is the inventory API rate limit. Exploit: batch inventory checks into 10-item bulk calls, cutting constraint-unit consumption by 10×. Elevate: negotiate a higher rate limit or add a second API key for peak windows.

**Signal to apply**: physical capacity appears available but throughput is capped; adding resources does not move the needle.

---

### P4 — Current Reality Tree for Architecture-Level Performance Stalls

**Problem**: A system has a well-known "performance problem." Teams have tried numerous fixes — database indexes, caching layers, CDN additions, service rewrites — but throughput or latency has not improved durably. The fixes target symptoms, not the root cause.

**TOC Primitive**: Current Reality Tree (CRT).

**Architecture Translation**:

Collect 5–10 Undesirable Effects (UDEs) from incident reports, SLO burn alerts, and post-mortems. State each as a concrete, negative, observable outcome — not a hypothesis.

**Example UDE set for a stalled e-commerce platform**:

1. P99 checkout latency exceeds 3 s at peak (SLO breach).
2. Cart service restarts 4× per week under load.
3. Payment service error rate spikes to 5% on flash sales.
4. Deploy frequency dropped from 10/day to 2/day after the last database migration.
5. On-call receives >20 alerts per peak event.
6. Engineers report that new feature work is blocked by "performance fires."
7. Database CPU hits 98% during peak windows.
8. Read replicas lag > 30 s during peak windows.
9. Background jobs compete with API traffic on shared database connections.
10. Caching layer hit rate is 40% because cache keys are scoped per user, not per product.

**CRT construction**: trace "If … Then" logic backward from each UDE. In this example, most UDEs trace to one core problem: background jobs and API traffic share a single database connection pool, which saturates at peak and cascades into latency, restarts, and error rates. The cache key design (per-user rather than per-product) is a second branch that compounds the DB load.

**Architectural injection**: separate background job connections onto a dedicated pool with a hard cap; rework cache keys to product-scope. This addresses the core problem — it does not just add indexes or increase instance size.

**Failure mode to avoid**: building the CRT around technology symptoms ("the database is slow") rather than system behaviors ("checkout requests queue behind background jobs at the constraint connection pool").

**Signal to apply**: multiple independent fixes have been tried, all produce temporary relief, and the same symptoms recur within one release cycle.

---

### P5 — Evaporating Cloud for Stability-vs-Velocity Tensions

**Problem**: Two valid architectural positions are deadlocked. The platform team requires full test coverage, change-control review, and staged rollouts (stability). The product team requires same-day deploys, feature flags for live experiments, and rapid rollback (velocity). Both positions are well-reasoned. The team compromises — neither position is fully implemented — and the result is slow deploys that are also not safe.

**TOC Primitive**: Evaporating Cloud (EC).

**Cloud structure**:

```
Shared Goal (A): Deliver working software reliably at high frequency

Requirement B (stability camp): Protect system integrity and user trust
  → Prerequisite D:  Enforce change-control review and full test gates before production

Requirement C (velocity camp): Ship features fast enough to remain competitive
  → Prerequisite D′: Allow same-day deploys with lightweight review and feature flags

Conflict: D and D′ appear mutually exclusive — you cannot have both mandatory review gates and same-day deploys.
```

**Arrow challenges** (each assumption on each arrow is a candidate for injection):

| Arrow | Assumption | Challenge |
|-------|-----------|-----------|
| B → D | Full test coverage requires manual gate review | Automated fitness functions can enforce coverage thresholds without human review |
| B → D | Change-control review prevents incidents | Most incidents come from infra changes and data migrations, not application logic; scope review to those only |
| C → D′ | Same-day deploys require bypassing review | Feature flags decouple deploy from release; deploy can go out same day while feature stays off |
| A → B | User trust requires zero-defect production deploys | User trust is maintained by fast rollback when issues appear, not by preventing all deploys |

**Injection**: Progressive delivery — automated gates (unit, integration, performance regression, security scan) run on every commit; deploys are gated on automated checks only; feature flags gate user exposure; a human review is triggered only for infrastructure-layer or data-migration changes. This satisfies B (integrity protected by automation) and C (velocity unlocked by separating deploy from release).

**ADR anchor**: the EC output becomes the context section of the Architecture Decision Record for the delivery policy. Record the cloud, the challenged assumptions, and the chosen injection.

**Signal to apply**: two technically valid positions are deadlocked; the team keeps revisiting the same debate; solutions are compromises that partially satisfy neither requirement.

---

## Anti-Patterns

### A1 — Refactoring Non-Bottleneck Services

**Description**: Engineers invest sprint cycles refactoring a service that is not the system constraint — improving its code quality, reducing its latency, reducing its memory footprint — while the true bottleneck service continues to cap system throughput.

**TOC Diagnosis**: Violates 5FS step 3 (subordinate). Improvement energy is directed at non-constraints, increasing local efficiency without increasing system T.

**Architecture Signal**: The refactored service's latency drops 40%; end-to-end user-facing latency is unchanged; throughput is flat.

**Fix**: Run 5FS on the service map before the next refactor quarter. Place a formal "non-constraint hold" on services identified as non-bottlenecks — no investment until the constraint is broken and a new 5FS pass is complete.

---

### A2 — Replacing the Entire Stack When One Component Is the Constraint

**Description**: Throughput is limited by a single component — a slow database query path, a single synchronous dependency, a saturated connection pool. The architectural response is to migrate the entire service (or estate) to a new technology stack: new language, new framework, new database engine.

**TOC Diagnosis**: Elevating the entire system when only one node is the constraint. The migration consumes enormous investment (I) and OE with a marginal T gain because the constraint was localized. Post-migration, the same component is often still the constraint, now in the new stack.

**Architecture Signal**: Six-month rewrite completes; P99 latency improves 10%; the new constraint is the same query path, now in Go instead of Python.

**Fix**: Apply the CRT to identify the true root cause before scope is set. Scope architectural investment to the constraint node only. Rewrite the hot path; keep the non-constraint services running on the existing stack.

---

### A3 — Optimizing Latency on Services with Idle Capacity

**Description**: Engineers spend time reducing P99 latency on a service that runs at 15% CPU utilization and has no queue. The assumption is that latency reduction anywhere improves user experience.

**TOC Diagnosis**: The service has slack capacity — it is not the constraint. Latency reduction here does not reduce end-to-end latency; the bottleneck service's queue still determines user-perceived response time.

**Architecture Signal**: Service A's P99 drops from 20 ms to 8 ms; end-to-end P99 is unchanged because the constraint (Service B, at 85% CPU with a 200-request queue) still gates every response.

**Fix**: For each latency optimization proposal, verify the service is on the critical path at peak load and that it is the constraint. If it is not the constraint, defer; redirect effort to the constraint service.

---

### A4 — Cost-Accounting Architecture Choices Instead of Throughput-Accounting Them

**Description**: Architecture decisions are evaluated by cost reduction: "migrating to Aurora saves $50k/year," "adopting a monorepo saves 2 engineer-hours per week in CI." The T impact of each decision — whether it removes a constraint and increases system throughput — is not modeled.

**TOC Diagnosis**: Cost-accounting bias drives local optimization. A decision that saves $50k/year but does not touch the constraint has T/IU ≈ 0. A decision that costs $120k/year but removes the constraint and doubles throughput has high T/IU.

**Architecture Signal**: Architecture roadmap is dense with efficiency and cost-saving initiatives; throughput growth is flat; the constraint is never named in roadmap discussions.

**Fix**: Before approving any architecture investment, require a throughput accounting statement: "This change moves the constraint in the following way, increasing T by an estimated X%." Investments with T/IU ≈ 0 are deferred or rejected regardless of cost savings.

---

### A5 — Treating Policy Constraints as Immutable

**Description**: A policy constraint — a mandatory approval gate, a rate limit on a vendor API, a hard schema-review requirement — is accepted as a permanent architectural boundary. Teams design around it (adding workarounds, buffers, compensating services) rather than challenging whether the underlying assumption that created the policy is still valid.

**TOC Diagnosis**: Policy constraints are invisible and feel external. But every policy was created to satisfy a requirement at a specific time. The requirement may no longer apply, or the policy may achieve its goal more cheaply under a different form.

**Architecture Signal**: The team has built three compensating microservices to work around a rate limit that was set in a vendor contract two years ago; no one has renegotiated the limit; the compensating services are now the new constraint.

**Fix**: Apply the Policy Constraint audit: state the policy, the requirement it was created to satisfy, and the assumption linking the policy to the requirement. Challenge the assumption: is it still true? If not, negotiate, automate, or replace the policy. Do not engineer permanently around a constraint that can be dissolved.

---

## Recipes

### R1 — System-Wide Bottleneck Hunt

**Goal**: Identify the single service or process step that limits system throughput, and sequence improvement work around it.

**Inputs**: Service map with current queue depths, P99 latencies, CPU/connection-pool saturation at peak, and deployment pipeline stage durations.

**Steps**:

1. **Build the service map** — list every service and its measured saturation at peak load. Include the deployment pipeline as a node if deploy frequency is a throughput concern.
   - Verify: queue depth and saturation data are from peak-load windows, not averages.

2. **Identify the constraint** (5FS step 1) — the constraint is the node with the deepest sustained queue at peak. If two nodes tie, pick the one on the critical path to the user-facing SLO.
   - Verify: the identified constraint's queue grows while adjacent services drain. A service with high CPU but no queue is saturated but not the constraint.

3. **Exploit the constraint** (5FS step 2) — before any new investment, extract maximum throughput from the constraint with existing resources: eliminate N+1 queries, increase connection pool to the database ceiling, batch outbound calls, shed or defer non-critical workloads at the constraint.
   - Verify: constraint throughput (requests/s or deploys/day) increases measurably within the sprint.

4. **Subordinate non-constraints** (5FS step 3) — rate-limit or backpressure every upstream service to match the constraint's capacity. Non-constraint services should have explicit WIP caps that prevent flooding the constraint.
   - Verify: queue depth at the constraint stops growing during normal load; upstream queues absorb burst before it reaches the constraint.

5. **Audit for policy constraints** (Policy Constraints check) — if the constraint has idle physical capacity but throughput is still capped, the constraint is a policy. Audit API rate limits, deployment approval gates, and schema-change processes.
   - Verify: is there a rule or process step that prevents the physical capacity from being used?

6. **Elevate if needed** (5FS step 4) — if exploit + subordinate do not reach target throughput, invest: horizontal scale, hardware upgrade, rewrite of the hot path, or negotiation of the rate limit.
   - Verify: after elevation, re-run queue-depth measurement. If the same node is still the deepest queue, the elevation was insufficient or the constraint moved within the node.

7. **Repeat** (5FS step 5) — schedule a 5FS review after every elevation. The constraint shifts; the previous subordination plan may now starve the new constraint.
   - Verify: the next 5FS pass identifies a different node as constraint. If the same node is always the constraint despite repeated elevation, the constraint is a policy or a market limit.

**Output**: A ranked architecture backlog where all investment in the next quarter flows to the constraint and non-constraint services have a documented "do not improve" hold.

---

### R2 — Refactor Scope Decision via Throughput Accounting

**Goal**: Determine whether a proposed refactor or architectural migration is worth executing, and if so, which scope delivers the highest throughput return per investment unit.

**Inputs**: List of candidate refactor proposals (each with an estimated investment cost in engineer-weeks and infrastructure spend), current system throughput baseline, identified constraint from R1.

**Steps**:

1. **State each proposal's constraint impact** — for each candidate, explicitly answer: does this change move the constraint?
   - Yes, it removes or elevates the current constraint → proceed to step 2.
   - No, it improves a non-constraint service → T/IU ≈ 0; reject or defer until constraint shifts.
   - Uncertain → run 5FS (R1) first; do not evaluate investment until the constraint is known.

2. **Estimate T gain** — for proposals that touch the constraint, estimate the throughput increase: expected requests/s or deploys/day after the change, minus the current baseline. Be conservative; use P50 scenario, not best case.

3. **Estimate investment cost** — sum engineer-weeks (at fully-loaded cost), infrastructure delta (new service cost minus retired service cost), and risk premium (P(outage) × expected revenue impact during migration). This is the I figure.

4. **Compute T/IU** — rank proposals by (estimated T gain) / (total investment cost). Higher T/IU wins.

5. **Scope to the constraint only** — if a full rewrite has T/IU = X, and refactoring only the hot path within the existing service has T/IU = 3X with one-fifth the investment, choose the scoped option. The full rewrite is only justified if the rest of the service is also a near-future constraint.

6. **Document in ADR** — record the T accounting statement as the context section of the Architecture Decision Record. State what throughput gain is expected, at what investment, and why non-constraint alternatives were rejected.

**Output**: A prioritized list of refactor candidates with T/IU rankings, an approved scope for the highest-ranked option, and a rejection rationale for non-constraint proposals.

---

### R3 — Stability-vs-Velocity ADR via Evaporating Cloud

**Goal**: Resolve a recurring architectural deadlock between a stability-focused requirement (change control, coverage gates, staged rollouts) and a velocity-focused requirement (same-day deploys, rapid experimentation, lightweight review) by surfacing and challenging the assumption that makes the conflict appear irresolvable.

**Inputs**: A named, recurring conflict between two architectural positions; the two requirements driving each position; the shared goal both positions are trying to serve.

**Steps**:

1. **Name the shared goal (A)** — state the common objective both camps are trying to achieve. Example: "Ship reliable software at a pace that sustains competitive product velocity."

2. **State both requirements (B and C)** — one sentence each. B: "Protect system integrity and user trust." C: "Maintain feature velocity sufficient to respond to the market."

3. **State the conflicting prerequisites (D and D′)** — what each requirement seems to demand. D: "All production changes pass mandatory human review and full test suites." D′: "Teams deploy to production on the same day code is ready, with minimal gates."

4. **Draw the cloud** and verify the conflict is real — can you actually deploy same-day AND run mandatory human review? If yes, the conflict was not real; restate. If no, proceed.

5. **List every assumption on every arrow**:
   - A → B: "User trust requires preventing defects from reaching production."
   - B → D: "Human review is necessary to catch the defects that threaten user trust."
   - A → C: "Competitive velocity requires frequent production deploys."
   - C → D′: "Frequent production deploys require removing review gates."

6. **Challenge each assumption**:
   - "Human review catches the defects that matter" — test: which production incidents were caused by logic defects vs. infrastructure/configuration changes? Scope human review to the incident-producing category only.
   - "Frequent deploys require removing review gates" — test: can automated fitness functions (coverage threshold, performance regression, security scan) replace human review for application logic changes?
   - "User trust requires zero production defects" — test: does rapid rollback (under 5 minutes) preserve user trust as effectively as preventing the deploy?

7. **Identify the injection** — the assumption that, when challenged, collapses the conflict. Most commonly: human review is not necessary for all change types; automated gates plus feature flags provide the same protection for application logic changes while preserving velocity.

8. **State the injection as an architectural decision** — "Progressive delivery: automated gates on every deploy; human review scoped to infrastructure and data-migration changes; feature flags decouple deploy from release." This resolves D and D′ simultaneously because they were never truly incompatible — the incompatibility was in the assumption that human review must cover all change types.

9. **Write the ADR** — context: the cloud and challenged assumptions. Decision: the injection. Consequences: what each camp gains, what constraints remain, how the decision will be evaluated.

**Output**: An Architecture Decision Record whose context section contains the evaporating cloud, whose decision section contains the injection, and whose consequences section documents how the resolved tension will be monitored.

---

## Composition

These patterns and recipes compose with the rest of the `software-architecture-design` skill:

| TOC Tool | Composes With | When |
|----------|---------------|------|
| R1 (Bottleneck Hunt) | [scalability-reliability-guide.md](scalability-reliability-guide.md) | After identifying the constraint, apply the guide's horizontal scaling, caching, and circuit-breaker patterns to the constraint node only |
| R2 (Refactor Scope) | [migration-modernization-guide.md](migration-modernization-guide.md) | Use TA to decide which strangler-fig slices to cut first; start with the constraint service |
| P3 (Policy Constraints) | [api-gateway-service-mesh.md](api-gateway-service-mesh.md) | Policy constraints in API rate limits are often solvable with gateway-level batching or request coalescing before contract renegotiation |
| R3 (Stability vs. Velocity ADR) | [adr-template.md](../assets/planning/adr-template.md) | The EC output populates the ADR context section; the injection is the decision |
| P4 (CRT on Performance Stalls) | [operational-playbook.md](operational-playbook.md) | CRT UDEs map directly to the playbook's architecture review questions |
| P5 (Evaporating Cloud) | [decision-theory-applied.md](decision-theory-applied.md) | When the cloud injection is uncertain, use decision theory to evaluate injection options under uncertainty |
| P2 (Throughput Accounting) | [queueing-theory-applied.md](queueing-theory-applied.md) | Queueing theory provides the model for how constraint utilization translates to queue depth and latency; use together to size the exploit step |

---

## Sources

These sources underpin the TOC primitives applied here. Full citation list is in
[`../../../foundations-theory-of-constraints/references/primitives-overview.md`](../../../foundations-theory-of-constraints/references/primitives-overview.md).

- Goldratt, E.M. & Cox, J. (1984). *The Goal*. North River Press. — Origin of 5FS and throughput accounting.
- Goldratt, E.M. (1990). *The Haystack Syndrome*. North River Press. — Throughput Accounting formalization: T, I, OE metrics.
- Goldratt, E.M. (1994). *It's Not Luck*. North River Press. — Evaporating Cloud and Thinking Processes in operational context.
- Cox, J.F. & Spencer, M.S. (1998). *The Constraints Management Handbook*. CRC Press. — Policy constraint detection and classification.
- Corbett, T. (1998). *Throughput Accounting*. North River Press. — T/CU ranking for product-mix and investment decisions.
- Dettmer, H.W. (2007). *The Logical Thinking Process*. ASQ Quality Press. — CRT construction and validation methodology.
- Kim, G., Behr, K. & Spafford, G. (2013). *The Phoenix Project*. IT Revolution Press. — TOC applied to IT operations and software delivery; the "three ways."
- Kim, G. et al. (2016). *The DevOps Handbook*. IT Revolution Press. — Policy constraint detection in deployment pipelines; progressive delivery patterns.
- Forsgren, N., Humble, J. & Kim, G. (2018). *Accelerate*. IT Revolution Press. — Empirical evidence that deployment frequency and change-fail rate are independent; supports the EC injection in R3.
