# Reliability Theory Applied to Software Architecture Design

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Reliability-engineering primitives mapped to software architecture decisions: serial vs parallel decomposition, SLA back-allocation, failure-mode budgeting in C4 designs, redundancy-vs-cost ADRs, SPOF audits, dependency-graph rollup, and RTO/RPO derivation. Each section names the anchoring primitive and cross-links its full reference.

---

## Table of Contents

- [Why Reliability Theory for Architecture](#why-reliability-theory-for-architecture)
- [Patterns](#patterns)
  - [P1 — Serial vs Parallel System Decomposition](#p1--serial-vs-parallel-system-decomposition)
  - [P2 — Target SLA Back-Allocation Across Services](#p2--target-sla-back-allocation-across-services)
  - [P3 — Failure-Mode Budgeting in C4-Style Designs](#p3--failure-mode-budgeting-in-c4-style-designs)
  - [P4 — Redundancy-vs-Cost ADR Template](#p4--redundancy-vs-cost-adr-template)
  - [P5 — SPOF Audit During Architecture Review](#p5--spof-audit-during-architecture-review)
  - [P6 — Dependency-Graph Reliability Rollup](#p6--dependency-graph-reliability-rollup)
  - [P7 — RTO and RPO Derivation from Primitives](#p7--rto-and-rpo-derivation-from-primitives)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Treating Redundant Components as Independent When They Share a Failure Domain](#a1--treating-redundant-components-as-independent-when-they-share-a-failure-domain)
  - [A2 — Allocating Equal Availability Targets Without Checking Achievability](#a2--allocating-equal-availability-targets-without-checking-achievability)
  - [A3 — Adding Replicas Without Verifying Switchover Reliability](#a3--adding-replicas-without-verifying-switchover-reliability)
  - [A4 — Confusing Mission-Time Reliability with Steady-State Availability](#a4--confusing-mission-time-reliability-with-steady-state-availability)
- [Recipes](#recipes)
  - [R1 — System Reliability Rollup and Bottleneck Identification](#r1--system-reliability-rollup-and-bottleneck-identification)
  - [R2 — SLA Back-Allocation to Microservices](#r2--sla-back-allocation-to-microservices)
  - [R3 — SPOF Audit and Redundancy Decision for an Architecture Review](#r3--spof-audit-and-redundancy-decision-for-an-architecture-review)
- [Composition](#composition)
- [Sources](#sources)

---

## Why Reliability Theory for Architecture

Architecture decisions that feel qualitative — "how many replicas?", "do we need active-active?", "can we afford a single database?" — each have a quantitative answer derivable from reliability primitives. Without the math, teams either over-provision (spending redundancy budget on components that are not the bottleneck) or under-provision (hitting SLO breaches from a SPOF that was visible before launch).

The four places where reliability theory pays off most directly in architecture work:

1. **Topology decisions**: series vs parallel arrangement of services multiplies or adds nines. The arithmetic proves which arrangement is the bottleneck before you build it.
2. **SLA decomposition**: a system-level SLO must be allocated to subsystems before teams can design to it. Without allocation, each team sets its own reliability target independently and the system misses the aggregate goal.
3. **SPOF identification**: fault tree minimal cut sets of size 1 are architectural SPOFs. Finding them analytically before production is cheaper than discovering them in an incident.
4. **Redundancy sizing**: the redundancy formulas tell you the minimum n and required coverage probability c before adding hardware is cost-justified.

Foundation primitives live in `../../foundations-reliability-theory/assets/templates/reliability-theory/`. Refer to them for derivations; this file applies them.

---

## Patterns

### P1 — Serial vs Parallel System Decomposition

**Primitive anchors**: [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md)

**The architecture framing.** Every request path through a distributed system is either a series chain (all components must succeed), a parallel cluster (any one component suffices), or a mix of both. The topology determines the reliability formula and identifies the bottleneck before any component is built.

**Series path — the weakest-link law.**

When components are in series, each component degrades the system multiplicatively:

```
A_system = A₁ × A₂ × A₃ × ... × Aₙ
```

A series system is always less available than its least-available member. A single 99.9% dependency in a chain of 99.99% components pulls the whole chain to 99.89%.

**Practical decomposition during design.** Map each user-facing request path to a reliability block diagram (RBD) before committing to the topology:

```
Example: checkout flow
  API Gateway  →  Auth  →  Inventory  →  Payment  →  Order DB

  Series:  A_checkout = A_gw × A_auth × A_inv × A_pay × A_db
                      = 0.9999 × 0.9997 × 0.9995 × 0.9993 × 0.9995
                      ≈ 0.9979   (99.79% — about 18.4 hours downtime/year)

  To reach 99.95% (< 4.4 hours downtime/year), every component needs ≥ 99.99%,
  OR the weakest members (payment, inventory) need active redundancy.
```

**Parallel group — the k-of-n gain.**

Active redundancy with n identical nodes all serving traffic:

```
A_parallel = 1 - (1 - A)^n
```

Two application servers at 99.9% each:

```
A_pair = 1 - (1 - 0.999)^2 = 1 - 0.000001 = 0.999999
```

If this app tier sits in series with a database at 99.95%, going from a single app node (99.9%) to the redundant pair (99.9999%) raises the combined app+DB availability from 0.999 × 0.9995 ≈ 0.9985 to 0.999999 × 0.9995 ≈ 0.99950 — a real gain of roughly 8.8 hours/year, but one that is capped by the database's own ceiling: no amount of further app-tier redundancy pushes the combined figure past ~99.95%, because the database remains the series bottleneck. This is the central insight: **redundancy on a non-bottleneck component has a hard ceiling set by the bottleneck component — once you approach that ceiling, further investment should go to the bottleneck itself, not to the already-redundant tier**.

**Common-cause failure adjustment.** When redundant nodes share a failure domain (same AZ, same underlying managed service, same software version), apply the beta-factor model from primitive 10:

```
A_adjusted = A_independent × (1 - β) + β × A_single
```

Two nodes in the same AZ with β = 0.05:

```
A_adjusted = 0.999999 × 0.95 + 0.05 × 0.999
           ≈ 0.94999905 + 0.049950 ≈ 0.99995
```

Spreading across two AZs reduces β from ~0.05 to ~0.01, recovering most of the parallel benefit.

**Design rule.** Draw the RBD before the C4 container diagram. The RBD topology drives container placement decisions; the C4 diagram documents the result.

---

### P2 — Target SLA Back-Allocation Across Services

**Primitive anchors**: [11-reliability-allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md)

**The problem.** A product SLA of 99.95% monthly availability means the error budget is 21.9 minutes per month. If five microservices sit in a series call path, every team setting its own reliability target independently will underdeliver the aggregate. Back-allocation is the mechanism for distributing the system target to individual owners before they build.

**Equal allocation (series topology, similar services).**

```
Rᵢ = R_system^(1/n)
```

For five series services and R_system = 0.9995:

```
Rᵢ = 0.9995^(1/5) ≈ 0.9999   (each needs four nines)
```

Each service's monthly error budget: `(1 - 0.9999) × 43,800 min = 4.38 min/month`. That is tight: a single 5-minute deploy incident exhausts it. This number drives the conversation about deployment strategy before architecture is finalized.

**ARINC allocation (existing services with measured data).**

When some services already have known failure rates, allocate proportionally to current failure rate:

```
λᵢ_target = λ_system_target × (λᵢ_current / Σλⱼ_current)
Rᵢ_target = exp(-λᵢ_target × t_mission)
```

ARINC preserves current proportions — it reduces the target failure rate of high-failure components without requiring less-reliable components to become disproportionately better. Use it when architecture is mostly fixed and targets must be realistic.

**AGREE allocation (services differ in complexity and criticality).**

When services differ significantly in function count and exposure:

```
Rᵢ = exp(-nᵢ × ln(1/R_system) / (wᵢ × N))
```

Where `nᵢ` is the module count in service i, `wᵢ` is the importance weight, `N` is total mission time. This directs tighter requirements at complex, critical paths and relaxes them on lightweight adapters.

**Error-budget translation.** Always translate the allocated Rᵢ to a concrete error budget:

```
Monthly budget for service i = (1 - Rᵢ) × 43,800 minutes
```

Teams must own this number in their runbooks, deploy policies, and on-call escalation paths. The allocated target is not real until it appears in a service's SLO dashboard.

**Allocation update trigger.** Re-run allocation at every major architecture review, when a new series dependency is added (it immediately degrades the system target), and when a component is parallelised (it contributes less to the series budget consumption).

---

### P3 — Failure-Mode Budgeting in C4-Style Designs

**Primitive anchors**: [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md), [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md)

**The link between FMEA/FTA and architecture diagrams.** A C4 container diagram shows what exists; an FMEA worksheet shows what can go wrong; and the error budget shows how much can go wrong before the SLO is breached. Combining all three at the container level produces a failure-mode budget — a per-component ceiling on how many minutes of downtime each box in the C4 diagram may contribute to the system error budget.

**Failure-mode budgeting procedure.**

1. Draw the C4 container diagram for the scope under review.
2. For each container (and each inter-container interface), run a lightweight FMEA: enumerate failure modes, score S × O × D = RPN.
3. For each failure mode that affects the top-level SLO, estimate expected downtime contribution (duration × probability).
4. Sum contributions; compare to the error budget from primitive 08.
5. If the sum exceeds the budget, rank by RPN and address the top items until the projected sum fits.

**FMEA at C4 container level (example worksheet).**

| Container | Failure Mode | Effect on SLO | S | O | D | RPN | Budget Impact (min/month) |
|-----------|-------------|---------------|---|---|---|-----|--------------------------|
| API Gateway | Misconfigured rate limit blocks valid traffic | All users see 429s | 9 | 3 | 5 | 135 | 6 min |
| Auth Service | JWT signing key unavailable | All API requests rejected | 10 | 2 | 4 | 80 | 3 min |
| Core Service | Deploy failure on hot path | 50% error rate | 8 | 5 | 3 | 120 | 10 min |
| Message Queue | Consumer lag exceeds SLA | Event processing delayed > 5 min | 6 | 4 | 6 | 144 | 8 min |
| Database | Replication lag spike | Stale reads on replica | 7 | 3 | 4 | 84 | 5 min |

Total projected: 32 min/month. Budget (99.95% SLO): 21.9 min/month. **Over budget by 10 min.** Address Core Service deploy failure (RPN 120, 10 min impact) first: blue-green or canary deployment reduces O from 5 to 2, projected residual impact drops to 4 min, bringing the total to ~26 min. Then attack API Gateway misconfiguration (RPN 135) to reach the target.

**FTA for top-event quantification.** When a single failure mode has disproportionate RPN, decompose it with FTA to find the minimal cut sets. Size-1 MCS are SPOFs (see Pattern P5). The top-event probability from FTA converts directly into a monthly downtime contribution for the budget.

---

### P4 — Redundancy-vs-Cost ADR Template

**Primitive anchors**: [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [11-reliability-allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md)

**The decision.** Adding replicas costs money and operational complexity. The redundancy formulas make the trade-off explicit: given the allocated reliability target Rᵢ and the current single-unit availability A, how many units n are required, and what coverage probability c does the switchover mechanism need?

**Redundancy requirement derivation.**

From the allocated target Rᵢ and single-unit availability A, minimum n for active redundancy:

```
n ≥ log(1 - Rᵢ) / log(1 - A)
```

Example: Rᵢ = 0.9999, A = 0.9990 (single node):

```
n ≥ log(1 - 0.9999) / log(1 - 0.9990)
  = log(0.0001) / log(0.001)
  = -4 / -3
  ≈ 1.33  →  2 nodes required
```

Two nodes at 0.9990 yields:

```
A_pair = 1 - (0.001)^2 = 0.999999  (six nines — over-spec by 2 nines)
```

Three nodes would be unnecessary unless the common-cause beta factor is large.

**Coverage sensitivity check.** Always compute the coverage threshold below which redundancy becomes harmful:

```
R_covered = c × R_parallel + (1-c) × R_single

Solve for c_min where R_covered = R_single:
c_min = 0   (redundancy always helps for R_parallel > R_single)

Solve for c_min where R_covered = Rᵢ:
c_min = (Rᵢ - R_single) / (R_parallel - R_single)
```

If the failover mechanism (load balancer health check, DNS failover, Kubernetes liveness probe) has coverage below `c_min`, adding the replica does not achieve the allocated target.

**ADR structure for redundancy decisions.**

```
## ADR-NNN: [Component] Redundancy Architecture

### Status: Proposed

### Context
- Allocated reliability target: Rᵢ = [from P2 allocation]
- Current single-unit availability: A = [from MTBF/MTTR data]
- Minimum n required: [formula result]
- Error budget at stake: [minutes/month]

### Options Considered
| Option | n | Architecture | A_system | Cost delta | Coverage c required |
|--------|---|-------------|----------|------------|---------------------|
| A | 1 | None (current) | 0.9990 | baseline | N/A |
| B | 2 | Active-active, same AZ | 0.999999 | +100% | 0.92 |
| C | 2 | Active-active, multi-AZ | 0.99999 (β=0.01) | +120% | 0.92 |
| D | 2 | Active-standby, multi-AZ | 0.99998 (switchover=3s) | +90% | 0.95 |

### Decision
[Option selected and rationale]

### Consequences
- MTTR changes: [failover time + detection time from primitive 01]
- Coverage dependency: [what must the LB/health-check achieve]
- Common-cause risk: [beta value and diversity mechanism]
- Re-allocation required if topology changes
```

---

### P5 — SPOF Audit During Architecture Review

**Primitive anchors**: [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md), [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md), [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md)

**What an SPOF is in reliability terms.** A single point of failure is a minimal cut set of size 1 in the fault tree for the top event "system unavailable." A size-1 MCS means there exists one component whose failure alone is sufficient to cause the top event, with no redundant path to bypass it.

**SPOF audit procedure for architecture review.**

1. Draw the reliability block diagram for each critical request path (same diagram as Pattern P1).
2. Any component that appears exactly once in the RBD, with no parallel path, is a candidate SPOF.
3. For each candidate, verify independence: if the "redundant" parallel paths share a network switch, power rail, managed service account, software version, or deployment pipeline, they are not truly independent — the shared dependency is the real SPOF.
4. Score each confirmed SPOF using FTA importance measures: Fussell-Vesely importance = fraction of total top-event probability attributable to that component. Rank by importance.
5. For each SPOF in the top 80% of Fussell-Vesely importance, create a remediation item with owner and target date.

**SPOF categories in distributed systems.**

| SPOF Category | Canonical Examples | Typical Oversight |
|---------------|-------------------|------------------|
| Network | Single ISP, single transit router, VPN endpoint | Treated as infrastructure, not modelled in RBD |
| Data | Single writable primary, single S3 bucket | Assumed "always available" |
| Auth | Single KMS key, single identity provider | External dependency, not owned |
| Control plane | Single Kubernetes API server, single DNS zone | Background infrastructure |
| Deployment | Single deploy pipeline for all services | DevOps tooling, not in reliability model |
| External SaaS | Single payment gateway, single email provider | Third-party SLA accepted uncritically |

**Checklist question for each C4 component box during architecture review:**

```
For [Container X]:
  □ Is there a parallel path if this container fails?
  □ If yes: do the paths share a common failure domain (AZ, power, network, software)?
  □ What is the failover mechanism and what is its coverage probability c?
  □ Does the allocated reliability target Rᵢ require active redundancy, standby, or neither?
  □ Is the FMEA worksheet current for this container?
```

---

### P6 — Dependency-Graph Reliability Rollup

**Primitive anchors**: [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [03-hazard-functions](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md)

**The problem.** Microservice estates have dozens of services with complex dependency graphs. Reliability is not just a property of each service in isolation but of the composed call graph. A service with 99.99% intrinsic availability that calls three downstream services each at 99.9% has an effective end-to-end availability much lower than its intrinsic number.

**Rollup algorithm.**

1. Represent the dependency graph as a directed acyclic graph where each node is a service with its intrinsic availability A_intrinsic.
2. For each node, compute A_effective by multiplying its intrinsic availability with the series availability of all synchronous downstream dependencies:

```
A_effective(S) = A_intrinsic(S) × ∏ A_effective(Dᵢ)   for all synchronous downstream D
```

3. Async dependencies (fire-and-forget, queue-backed) are NOT in the series product for synchronous request reliability; they enter a separate availability model for the async path.
4. Walk the graph leaf-first (topological sort, leaves first); propagate A_effective bottom-up.

**Worked rollup example.**

```
Dependency graph:
  User →  API (A=0.9999)
           ├── Auth (A=0.9997)    [sync]
           ├── Core (A=0.9995)    [sync]
           │     └── DB (A=0.9993)   [sync]
           └── Notifications (A=0.9990)  [async — excluded from sync path]

A_effective(DB)   = 0.9993
A_effective(Core) = 0.9995 × A_effective(DB) = 0.9995 × 0.9993 = 0.9988
A_effective(Auth) = 0.9997
A_effective(API)  = 0.9999 × A_effective(Auth) × A_effective(Core)
                  = 0.9999 × 0.9997 × 0.9988
                  ≈ 0.9984   (99.84%)
```

The system's effective availability is 99.84% — about 14.0 hours of downtime per year — despite all individual intrinsic values being above 99.9%. The DB is the series bottleneck.

**Operational use.** Automate this rollup in a service catalog or dependency graph tool. When a new synchronous dependency is added, the rollup re-runs and flags any service whose A_effective drops below its allocated target. This turns a static reliability model into a continuous architecture fitness function.

**Async path model.** For async-backed paths, the reliability model changes: failure is measured as message loss or processing delay exceeding SLO, not request unavailability. Apply primitive 01 (MTBF/MTTR) to the queue consumer separately.

---

### P7 — RTO and RPO Derivation from Primitives

**Primitive anchors**: [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md)

**RTO (Recovery Time Objective) is an MTTR bound.** RTO is the maximum tolerable time from failure to restored service. It maps directly to MTTR in primitive 01: the architecture must be designed so that the expected MTTR ≤ RTO, with the tail of the MTTR distribution also considered (the 95th-percentile MTTR should not exceed the agreed RTO).

**MTTR decomposition.**

```
MTTR = T_detect + T_diagnose + T_remediate + T_verify

Where:
  T_detect    = time from failure to alert (monitoring lag)
  T_diagnose  = time from alert to root cause (observability quality)
  T_remediate = time to apply fix (automation coverage, runbook completeness)
  T_verify    = time to confirm restoration (smoke test, SLO recovery)
```

For automated failover:

```
T_detect   = health-check interval + consecutive failures threshold × interval
T_diagnose = 0 (automated)
T_remediate = failover time (standby promotion, DNS TTL, LB drain)
T_verify   = health-check re-confirmation × interval
```

If T_detect alone exceeds RTO, the architecture cannot meet its objective regardless of how fast remediation is.

**RPO (Recovery Point Objective) is a data-loss bound.** RPO is the maximum tolerable age of the most recent committed data after a failure. It maps to backup/replication frequency:

```
RPO ≥ replication_lag + time_since_last_checkpoint
```

For a database with asynchronous replication, at the moment of primary failure:

```
RPO_exposed = current_replication_lag + failover_detection_time
```

If replication lag is normally 2 seconds but can spike to 30 seconds, design for RPO_exposed = 30 s + T_detect, not 2 s.

**Availability implication of RTO/RPO choices.**

An aggressive RTO (< 1 minute) requires automated failover, which requires reliable detection (coverage c) and a pre-warmed standby. From redundancy math (primitive 07), imperfect coverage erodes the availability gain:

```
A_achieved = c × A_with_failover + (1-c) × A_without_failover
```

A 1-minute RTO requires T_detect ≤ ~20 s, which requires health-check intervals of ≤ 10 s with 2 consecutive failures. This is an architectural constraint on the monitoring design, not just an ops concern.

**Bathtub-curve implication for DR testing.** Newly deployed disaster-recovery paths are in their infant-mortality phase (left tail of the bathtub curve, primitive 04): they have elevated failure rates due to untested runbooks, misconfigured replication, and cold-path bugs. DR paths not exercised regularly enter the wear-out phase on the right tail as their configuration drifts from the primary. RTO commitments require regular DR drills to keep the DR path in its useful-life phase (flat hazard rate).

---

## Anti-Patterns

### A1 — Treating Redundant Components as Independent When They Share a Failure Domain

**Primitive misapplied**: [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md)

Applying the active redundancy formula `A_parallel = 1 - (1-A)^n` while ignoring common-cause failures is the most frequent reliability mistake in distributed system design. The formula assumes statistical independence: the two nodes fail from different, uncorrelated causes. In practice:

- Both nodes run the same Docker image (software bug takes them both down simultaneously).
- Both nodes are in the same AZ (power event, cooling failure, network partition affects both).
- Both nodes are provisioned from the same managed service with a shared control plane (AWS RDS Multi-AZ shares the same RDS control plane).
- Both nodes are deployed in the same pipeline (a bad deploy rolls out to both in sequence before the problem is detected).

The beta-factor correction from primitive 10 reveals the impact:

```
A_pair = 1 - (1-A)^2                   ← independence assumption: 0.999999
A_adjusted = A_pair(1-β) + β × A_single ← β=0.05: ≈ 0.99995  (two nines lost)
```

The correction costs roughly two full nines. When β ≥ (A_parallel - A_single) / (A_parallel - A_single + A_single - A_target), adding the second node does not achieve the allocation target at all.

**What to do instead.** Enumerate common-cause failure modes explicitly before computing A_parallel. Diversity of software version, physical rack, power circuit, AZ, and deployment pipeline are the levers that reduce β. Add redundancy only after diversity has been addressed.

---

### A2 — Allocating Equal Availability Targets Without Checking Achievability

**Primitive misapplied**: [11-reliability-allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md)

Equal allocation — `Rᵢ = R_system^(1/n)` — is the correct starting formula for homogeneous series systems, but it is misapplied when:

- A component is a third-party SaaS with a published SLA below the allocated target (e.g., allocated 99.999% to a payment gateway with a 99.9% SLA).
- A component is a shared database cluster whose MTTR cannot be reduced further without architectural change.
- A component sits in a parallel path rather than a series chain, so its individual allocation should be looser, not equal to the series components.

The consequence: the allocation looks reasonable on paper, teams commit to it, and then miss their allocated targets because the physical constraint was not checked. The system SLO is breached not from a design flaw but from an allocation that was mathematically correct for a homogeneous series system but not for the actual topology.

**What to do instead.** After equal allocation, validate each Rᵢ against: (a) the vendor SLA or historically observed availability for third-party services, (b) achievable MTTR given current MTBF data, (c) the correct topology — parallel components need less aggressive individual targets. Apply AGREE or ARINC allocation when subsystems differ in complexity or achievability.

---

### A3 — Adding Replicas Without Verifying Switchover Reliability

**Primitive misapplied**: [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md)

The imperfect coverage formula:

```
R_covered = c × R_parallel + (1-c) × R_single
```

shows that when coverage c is low, redundancy can actively reduce availability. A concrete case: adding a hot standby database replica where the promotion mechanism (custom script, manual runbook) has 80% coverage c:

```
R_parallel (no coverage): 0.999999
R_covered (c = 0.80):     0.80 × 0.999999 + 0.20 × 0.999 = 0.99980
R_single:                 0.999
```

At c = 0.80, the standby still helps (0.99980 > 0.999), but the gain is mostly lost. If the allocation target is 0.99990, the standby at c = 0.80 does not achieve it. Engineers add more nodes, which does not help because the bottleneck is c, not n.

**What to do instead.** Measure or estimate c for each failover mechanism before counting it toward the reliability target. Kubernetes liveness-probe-based restart has high c (~0.999) for stateless services; DNS-TTL-based failover has lower c for short-TTL implementations (~0.95–0.98); manual runbook promotion has c depending on runbook quality and on-call response time. Fix coverage before increasing n.

---

### A4 — Confusing Mission-Time Reliability with Steady-State Availability

**Primitive misapplied**: [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md)

These are two different quantities:

```
Availability (steady-state):  A = MTBF / (MTBF + MTTR)  — fraction of time system is up
Reliability (mission-time):   R(t) = exp(-λt)            — probability system survives t hours
```

They coincide only for exponentially distributed failure times. Using steady-state availability as if it were mission-time reliability produces wrong answers in two common architecture scenarios:

1. **Batch processing SLAs**: "the nightly job must complete in 4 hours" is a mission-time reliability question. Using the component's steady-state availability (e.g. 99.9%) to answer it is wrong — the relevant number is R(4h) from the component's failure distribution, which requires Weibull parameters (primitive 09), not just MTBF/MTTR.

2. **Component age**: steady-state availability assumes the system has been running long enough for failure rate to reach its useful-life constant. A freshly deployed service is in the infant-mortality phase (bathtub curve left tail, primitive 04) and has a higher instantaneous failure rate. Applying steady-state A immediately after launch overstates actual reliability.

**What to do instead.** Use `A = MTBF / (MTBF + MTTR)` for continuous-service SLO analysis. Use `R(t) = exp(-λt)` (or the Weibull equivalent) for point-in-time mission-critical tasks. For newly deployed components, apply a burn-in period or explicitly account for the infant-mortality failure rate before relying on steady-state figures.

---

## Recipes

### R1 — System Reliability Rollup and Bottleneck Identification

**Objective**: Compute the effective end-to-end availability for a service topology, identify the bottleneck component, and determine where reliability investment has the greatest leverage.

**Primitive stack**: System Reliability (#10) + Availability Formulas (#02) + Redundancy Math (#07) + Reliability Allocation (#11)

**Step 1: Collect component availability data.**

```
For each service / infrastructure component on the critical path:
  - Source: SLO dashboard, incident history, vendor SLA, or MTBF/MTTR estimates
  - Record: intrinsic availability A_intrinsic, redundancy architecture (n, active/standby), coverage c
```

**Step 2: Draw the reliability block diagram.**

```
Represent each synchronous series dependency as a block in a chain.
Represent each parallel cluster as a parallel bank.
Annotate each block with A_intrinsic and architecture type.

Example:
  [CDN 0.9999] →→ [LB 0.99999] →→ [App × 2, A=0.9990, active] →→ [DB Primary 0.9993]
```

**Step 3: Compute effective availability bottom-up.**

```python
# Pseudocode: reliability rollup
def rollup(graph, node):
    """Compute A_effective for node given its downstream dependencies."""
    deps = graph.get_sync_dependencies(node)
    if not deps:
        return node.A_intrinsic

    # Series composition with all sync downstream nodes
    downstream_A = 1.0
    for dep in deps:
        downstream_A *= rollup(graph, dep)

    # Parallel composition within the node's own redundancy cluster
    n = node.replica_count
    c = node.coverage
    A_base = node.A_intrinsic

    if n > 1:
        A_parallel = 1 - (1 - A_base) ** n
        # Apply beta-factor for common-cause
        beta = node.common_cause_beta
        A_parallel = A_parallel * (1 - beta) + beta * A_base
        # Apply imperfect coverage
        A_node = c * A_parallel + (1 - c) * A_base
    else:
        A_node = A_base

    return A_node * downstream_A
```

**Step 4: Identify the bottleneck.**

```
Sort components by A_effective contribution:
  Bottleneck = component with lowest A_effective × (series multiplier impact)

Impact of improving component i by delta_A:
  delta_A_system ≈ delta_A × (A_system / A_i)  [first-order approximation]
```

The component where a 0.001 improvement in A_i yields the largest delta_A_system is the bottleneck. For a series chain, this is always the least-available component.

**Step 5: Evaluate redundancy options for the bottleneck.**

```
Given bottleneck A_i, compute n_required to achieve allocated target Rᵢ:
  n ≥ log(1 - Rᵢ) / log(1 - A_i)

Compute cost of each option:
  - Active n=2, same-AZ: β ≈ 0.05, cost = 2× node cost + LB config
  - Active n=2, multi-AZ: β ≈ 0.01, cost = 2× node cost + cross-AZ transfer
  - Managed HA service: β ≈ 0.02–0.10 (vendor dependent), cost = premium tier delta

Select based on allocated target, budget, and common-cause exposure.
```

**Step 6: Re-run rollup with proposed changes; confirm target is met.**

```
Verify: A_effective(system) ≥ R_system_target
Verify: each A_effective(i) ≥ Rᵢ (allocated target from P2)
Document in ADR using P4 template.
```

---

### R2 — SLA Back-Allocation to Microservices

**Objective**: Distribute a system-level SLO target to individual microservices so each team has a concrete reliability target, an error budget, and a deploy-frequency implication to design against.

**Primitive stack**: Reliability Allocation (#11) + Availability Formulas (#02) + Error Budgets (#08) + System Reliability (#10)

**Step 1: Define the allocation scope.**

```
1. Identify the user-facing SLO: e.g. "checkout flow 99.95% monthly availability"
2. Draw the reliability block diagram for the checkout flow (from R1, Step 2)
3. Label each block as series or parallel
4. Identify which blocks are owned by which teams
```

**Step 2: Choose the allocation method.**

```
New system (no data):         → Equal allocation
Existing services (with data): → ARINC (proportional to current failure rate)
Heterogeneous criticality:    → AGREE (weighted by module count and importance)
```

**Step 3: Run equal allocation as the baseline.**

```python
import math

def equal_allocation(R_system, n_series_components):
    """R_i for each of n series components to achieve R_system."""
    R_i = R_system ** (1 / n_series_components)
    return R_i

# Example: 5 services, 99.95% system target
R_system = 0.9995
n = 5
R_i = equal_allocation(R_system, n)
# R_i ≈ 0.9999
```

**Step 4: Validate each allocated target against reality.**

```
For each service:
  □ Is R_i achievable with current MTBF/MTTR?
     → MTTR_required = MTBF × (1 - R_i) / R_i
     → Compare to current MTTR. If MTTR_required < current MTTR, flag for improvement.
  □ For third-party services: is R_i ≤ vendor SLA?
     → If vendor SLA < R_i, either accept and negotiate budget elsewhere,
        add redundancy (dual-vendor), or change the allocation method.
  □ Is the service in a series path or a parallel path?
     → Parallel paths need looser targets. Recalculate with correct topology.
```

**Step 5: Convert to error budget and deploy implication.**

```python
def to_error_budget(R_i, window_minutes=43800):
    """Compute error budget and max deploy frequency."""
    budget_minutes = (1 - R_i) * window_minutes
    return budget_minutes

# Continuing example: R_i = 0.9999
budget = to_error_budget(0.9999)
# budget ≈ 4.38 minutes/month

# If each deploy historically risks 2-minute partial outage (50% error rate = 1 effective min):
deploy_risk_per_deploy = 1.0  # effective minutes
max_risky_deploys = int(budget / deploy_risk_per_deploy)
# max_risky_deploys = 4 per month (at given risk level)
```

**Step 6: Produce the allocation table and hand off to service owners.**

```
| Service        | Allocated Rᵢ | Monthly Budget (min) | Max risky deploys | Current R | Gap |
|----------------|-------------|---------------------|------------------|-----------|-----|
| API Gateway    | 0.9999      | 4.38                | 4                | 0.9999    | —   |
| Auth Service   | 0.9999      | 4.38                | 4                | 0.9997    | 0.0002 ← fix |
| Core Service   | 0.9999      | 4.38                | 4                | 0.9995    | 0.0004 ← fix |
| Payment Proxy  | 0.9999      | 4.38                | 4                | 0.9993    | 0.0006 ← fix |
| Database       | 0.9999      | 4.38                | 4                | 0.9991    | 0.0008 ← fix |
```

Services with a gap need to either improve MTTR or add redundancy; re-run R1 rollup to verify before the allocation is finalized. Re-run at every architecture review and at each new series dependency addition.

---

### R3 — SPOF Audit and Redundancy Decision for an Architecture Review

**Objective**: Identify all single points of failure in the architecture under review, quantify their reliability impact, and produce a prioritised remediation list with redundancy ADR stubs for the top items.

**Primitive stack**: FTA (#05) + FMEA (#06) + Redundancy Math (#07) + System Reliability (#10) + Reliability Allocation (#11)

**Step 1: Enumerate candidate SPOFs from the RBD.**

```
Walk the reliability block diagram from R1.
For each component:
  - Does it appear exactly once with no parallel path? → SPOF candidate
  - Does its "parallel path" share a common-cause failure domain? → Effective SPOF candidate
Record all candidates with their current A_intrinsic.
```

**Step 2: Run lightweight FTA for each SPOF candidate.**

```
Top event: "System SLO breach caused by [candidate] failure"

Fault tree:
  Top event
    └─ [Candidate] fails (OR)
         ├─ Software defect (P = from incident history)
         ├─ Infrastructure failure (P = from vendor SLO)
         └─ Operator error (P = from change-failure-rate data)

MCS = { [Candidate] } — size 1 confirms it is a SPOF

Compute top-event probability:
  P(breach | candidate) = 1 - A_candidate
  Expected downtime contribution: (1 - A_candidate) × window_minutes
```

**Step 3: Rank SPOFs by Fussell-Vesely importance.**

```
FV_importance(i) = P(at least one MCS containing i is in cut set)
                 ≈ (1 - A_i) / (1 - A_system)

For components in series, FV_importance ≈ 1 - A_i / (1 - A_system)
```

Sort descending by FV importance. Focus remediation on the top 20% that account for 80% of expected downtime.

**Step 4: For each top-ranked SPOF, evaluate remediation options.**

```
For each SPOF i with FV rank in top 80%:

  Option A: Redundancy
    n_required = log(1 - Rᵢ) / log(1 - A_i)     ← from primitive 07
    Check c_required for switchover mechanism
    Check beta for common-cause exposure
    Compute A_achieved after redundancy

  Option B: MTTR reduction (RTO improvement)
    Target MTTR_new = MTBF × (1 - Rᵢ) / Rᵢ
    Identify which T_detect, T_diagnose, T_remediate components to reduce
    (Use MTTR decomposition from Pattern P7)

  Option C: Accept and mitigate
    If Rᵢ is achievable by third-party SLA only:
      Accept and allocate remaining budget to other components
      Add graceful degradation so SPOF failure doesn't cause full outage

  Pick cheapest option that closes the gap between current A_i and allocated Rᵢ.
```

**Step 5: Produce the SPOF audit output table.**

```
| Component     | Type         | Current A  | FV Importance | Downtime/mo | Rᵢ Target | Remediation Option  | Owner |
|---------------|-------------|------------|---------------|-------------|-----------|---------------------|-------|
| Primary DB    | Data SPOF   | 0.9991     | 0.42          | 3.8 min     | 0.9999    | Active-standby + c  | DB team |
| ISP link      | Network SPOF| 0.9997     | 0.15          | 1.3 min     | 0.9999    | Dual-ISP            | Infra  |
| Auth KMS key  | Auth SPOF   | 0.9998     | 0.10          | 0.9 min     | 0.9999    | Local key cache TTL | Platform |
```

**Step 6: Write ADR stubs for the top 3 items.**

Using the ADR template from Pattern P4, create draft ADRs covering: architecture options with computed A_achieved, coverage requirements, common-cause risk, and cost delta. Gate the next architecture review on these ADRs being in "accepted" or "superseded" status.

**Success criterion.** After all remediations are applied, re-run the R1 rollup. A_system must equal or exceed R_system_target. If not, return to Step 3 and re-rank with updated values.

---

## Composition

The patterns and recipes in this file compose into a single reliability design workflow for a new architecture or a major architecture review:

```
1. Draw RBD (P1) → identifies series vs parallel topology
2. Rollup A_effective (R1) → finds the system ceiling and bottleneck
3. Back-allocate targets (P2, R2) → gives each team a concrete Rᵢ and error budget
4. SPOF audit (P5, R3) → enumerates size-1 MCS and ranks by FV importance
5. Failure-mode budget (P3) → overlays FMEA RPN onto the C4 diagram within the error budget
6. Redundancy ADR (P4) → quantifies n and c before any hardware decision
7. RTO/RPO derivation (P7) → ties the reliability model to DR architecture constraints
```

The central dependency is P1 → P2 → P4: you cannot allocate targets correctly without the topology, and you cannot size redundancy correctly without the allocated target. Do not skip to the ADR before the RBD is drawn.

| Mechanism | Failure Mode Addressed |
|-----------|----------------------|
| Series rollup (P1) | System availability ceiling underestimated |
| Back-allocation (P2) | Teams designing to inconsistent local targets |
| FMEA budgeting (P3) | Failure modes outside the error budget undetected at design time |
| Redundancy ADR (P4) | Replicas added without quantified benefit |
| SPOF audit (P5) | Size-1 cut sets surviving to production |
| Dependency rollup (P6) | Downstream reliability impact not visible to upstream owners |
| RTO/RPO derivation (P7) | DR architecture not grounded in actual MTTR decomposition |

---

## Sources

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapters 3–4 (error budget, SLO design).
- Beyer, B., Murphy, N. R., Rensin, D. K., Kawahara, K., & Thorne, S. (2018). *The Site Reliability Workbook*. O'Reilly. Chapter 2 (multi-window burn rate).
- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley. Chapters 4, 6–9.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer. Chapters 2–3.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley. Chapters 2–3, 6–8.
- IEEE Std 1413 (2010). *IEEE Standard Methodology for Reliability Prediction and Assessment for Electronic Systems and Equipment*.
- IEC 60812 (2018). *Failure modes and effects analysis (FMEA and FMECA)*. International Electrotechnical Commission.
- IEC 61025 (2006). *Fault tree analysis (FTA)*. International Electrotechnical Commission.
- IEC 61508-6 (2010). *Functional safety of E/E/PE safety-related systems — Part 6*. (Beta-factor guidance.)
- Nygard, M. (2018). *Release It! Design and Deploy Production-Ready Software* (2nd ed.). Pragmatic Bookshelf. (Failure modes in distributed systems.)

### Primitive Cross-References (foundations-reliability-theory)

| # | File |
|---|------|
| 01 | [01-mtbf-mttr.md](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) |
| 02 | [02-availability-formulas.md](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) |
| 03 | [03-hazard-functions.md](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md) |
| 04 | [04-bathtub-curve.md](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) |
| 05 | [05-fault-tree-analysis.md](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) |
| 06 | [06-fmea.md](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) |
| 07 | [07-redundancy-math.md](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) |
| 08 | [08-error-budgets.md](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) |
| 09 | [09-weibull-analysis.md](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md) |
| 10 | [10-system-reliability.md](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md) |
| 11 | [11-reliability-allocation.md](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) |
