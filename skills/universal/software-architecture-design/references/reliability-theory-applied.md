# Reliability Theory Applied to Software Architecture Design

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

This file is a link adapter. It keeps only what is specific to architecture work: which design decisions each reliability primitive drives, architecture pitfalls, and re-derived worked examples. Definitions, formulas, and derivations live in the foundation — follow the pointers:

- Primitives: `../../foundations-reliability-theory/assets/templates/reliability-theory/` (01–11, indexed in [Sources](#sources))
- Decision gates and validation: [`decision-and-validation.md`](../../foundations-reliability-theory/references/decision-and-validation.md)
- Agentic / LLM components: [`ai-agent-reliability.md`](../../foundations-reliability-theory/references/ai-agent-reliability.md)
- SLO design and burn-rate alert implementation: [`qa-observability/references/slo-design-guide.md`](../../qa-observability/references/slo-design-guide.md)
- Safety-II / STPA hazard analysis: [`foundations-safety-engineering`](../../foundations-safety-engineering/SKILL.md)

**Budget window convention.** Error-budget minutes below use an *average calendar month* (43,800 min = 8,760 h / 12). A 30-day window is 43,200 min and a 28-day window 40,320 min; pass the window as a parameter rather than hard-coding it.

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

"How many replicas?", "do we need active-active?", "can we afford a single database?" each have a quantitative answer. Without it, teams over-provision non-bottleneck components or ship a SPOF that was visible before launch. The four architecture decisions it drives:

1. **Topology** — series vs parallel arrangement determines the ceiling and the bottleneck before anything is built.
2. **SLA decomposition** — a system SLO must be allocated to owning teams before they design to it.
3. **SPOF identification** — size-1 minimal cut sets are architectural SPOFs.
4. **Redundancy sizing** — minimum n and required switchover coverage c before hardware spend is justified.

---

## Patterns

### P1 — Serial vs Parallel System Decomposition

**Theory**: series/parallel/k-of-n formulas and the beta-factor common-cause model are in [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md) and [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md).

**Architecture decision it drives.** Map each user-facing request path to a reliability block diagram (RBD) *before* the C4 container diagram. The RBD topology drives container placement; the C4 diagram documents the result.

**Worked example — checkout flow (series).**

```
API Gateway → Auth → Inventory → Payment → Order DB
A = 0.9999 × 0.9997 × 0.9995 × 0.9993 × 0.9995 ≈ 0.9979   (≈ 18.4 h downtime/yr)

To reach 99.95% (≈ 4.4 h/yr): every component ≥ 99.99% (0.9999^5 ≈ 0.9995),
or active redundancy on the weakest members (payment, inventory).
```

**Worked example — redundancy capped by the bottleneck.** App tier at 0.999 in series with a DB at 0.9995: single app node gives 0.999 × 0.9995 ≈ 0.9985; an active pair (1 − 0.001² = 0.999999) gives ≈ 0.99950 — a gain of ≈ 8.75 h/yr, but no further app-tier redundancy can pass the DB's 99.95% ceiling. **Once the non-bottleneck tier approaches the ceiling, spend on the bottleneck.** The foundation's 3-tier example (CDN .9999, app .999 ×2 active-active, DB .9995) reaches the same ≈ 8.75 h/yr saving (14.0 → 5.26 h/yr).

**Common-cause check.** Two same-AZ nodes with β = 0.05: 0.999999 × 0.95 + 0.05 × 0.999 ≈ 0.99995. Spreading across AZs (β ≈ 0.01, illustrative) gives ≈ 0.99999. The β values are assumptions to be justified per failure domain, not measured constants.

---

### P2 — Target SLA Back-Allocation Across Services

**Theory**: equal, ARINC, and AGREE allocation formulas and their inputs are in [11-reliability-allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md); budget arithmetic in [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md).

**Architecture decision it drives.** Which method to use, and whether the architecture can meet the result:

| Situation | Method |
|-----------|--------|
| New system, similar services, no data | Equal allocation |
| Existing services with measured failure rates, topology mostly fixed | ARINC (preserves current proportions) |
| Services differ in complexity and criticality | AGREE |

**Worked example.** Product SLA 99.95%, five services in series: equal allocation gives Rᵢ = 0.9995^(1/5) ≈ 0.9999 per service → (1 − 0.9999) × 43,800 ≈ **4.38 min per average month** (4.32 min on a 30-day window). A single 5-minute deploy incident exhausts it — this number should drive the deployment-strategy conversation (canary, blue-green, feature flags) before the architecture is finalised.

**Ownership rule.** The allocated target is not real until it appears in the owning service's SLO dashboard, deploy policy, and escalation path. Re-run allocation at every major architecture review, whenever a new synchronous series dependency is added, and when a component is parallelised.

---

### P3 — Failure-Mode Budgeting in C4-Style Designs

**Theory**: FMEA scoring and ranking rules in [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md); minimal cut sets in [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md); budget in [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md).

**Architecture use.** Overlay a lightweight FMEA on each C4 container and inter-container interface, estimate each failure mode's expected downtime contribution (duration × probability), and sum against the SLO's error budget. The result is a per-box ceiling on how many minutes each container may spend.

**Procedure.**

1. Draw the C4 container diagram for the scope under review.
2. Per container/interface: enumerate failure modes, score S, O, D.
3. Estimate expected downtime contribution for each mode that affects the top-level SLO.
4. Sum and compare to the error budget.
5. If over budget: **review every S ≥ 9 item independently of RPN** (foundation 06-fmea), then prioritise by budget impact; RPN is a tiebreaker, never the sole ranking.

**Example worksheet.**

| Container | Failure Mode | Effect on SLO | S | O | D | RPN | Budget Impact (min/month) |
|-----------|-------------|---------------|---|---|---|-----|--------------------------|
| API Gateway | Misconfigured rate limit blocks valid traffic | All users see 429s | 9 | 3 | 5 | 135 | 6 |
| Auth Service | JWT signing key unavailable | All API requests rejected | 10 | 2 | 4 | 80 | 3 |
| Core Service | Deploy failure on hot path | 50% error rate | 8 | 5 | 3 | 120 | 10 |
| Message Queue | Consumer lag exceeds SLA | Event processing delayed > 5 min | 6 | 4 | 6 | 144 | 8 |
| Database | Replication lag spike | Stale reads on replica | 7 | 3 | 4 | 84 | 5 |

Total projected: 32 min/month vs a 99.95% budget of 21.9 min (average month) — **over by ≈ 10 min**. Note that RPN ranking alone would put the Message Queue (144) first and the Auth key loss (S = 10, RPN 80) near the bottom. Instead:

- Auth key loss (S = 10) and gateway misconfiguration (S = 9) get a mandatory design review regardless of RPN — both are total outages.
- By budget impact, the Core Service deploy failure (10 min) is the largest lever: canary/blue-green lowering O from 5 to 2 is estimated to cut its impact to ≈ 4 min, bringing the total to ≈ 26 min. Then the gateway (6 min) to reach budget.

**FTA hand-off.** When a single failure mode dominates, decompose it with FTA; size-1 minimal cut sets are SPOFs (P5), and the top-event probability converts directly into a monthly downtime contribution.

---

### P4 — Redundancy-vs-Cost ADR Template

**Theory**: minimum-n, imperfect-coverage, and coverage-validation math in [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md).

**Architecture decision it drives.** Given the allocated Rᵢ (P2) and single-unit availability A, how many units n, and what coverage c must the failover mechanism reach?

**Worked example.** Rᵢ = 0.9999, A = 0.999: n ≥ log(10⁻⁴) / log(10⁻³) ≈ 1.33 → **2 nodes**. With imperfect coverage, c_min = (Rᵢ − A_single) / (A_redundant − A_single). The coverage column below is re-derived from that formula; note that c must be *validated empirically* — the foundation shows ten successful failover drills cannot demonstrate c = .995.

**ADR structure.**

```
## ADR-NNN: [Component] Redundancy Architecture

### Status: Proposed

### Context
- Allocated reliability target: Rᵢ = [from P2]
- Current single-unit availability: A = [from MTBF/MTTR data]
- Minimum n required: [07-redundancy-math]
- Error budget at stake: [minutes per window]

### Options Considered
| Option | n | Architecture | A (before coverage) | Cost delta | c_min for Rᵢ = 0.9999 |
|--------|---|--------------|---------------------|------------|------------------------|
| A | 1 | None (current) | 0.9990 | baseline | N/A (cannot meet Rᵢ) |
| B | 2 | Active-active, same AZ (β = 0.05) | ≈ 0.99995 | [estimate] | ≈ 0.95 |
| C | 2 | Active-active, multi-AZ (β = 0.01) | ≈ 0.99999 | [estimate] | ≈ 0.91 |
| D | 2 | Active-standby, multi-AZ | [compute: 07, standby + switchover] | [estimate] | [compute] |

### Decision
[Option selected and rationale]

### Consequences
- MTTR changes: [failover + detection time, 01-mtbf-mttr]
- Coverage dependency: [what the LB/health-check must achieve, and how it is validated]
- Common-cause risk: [β value and the diversity mechanism that justifies it]
- Re-allocation required if topology changes
```

---

### P5 — SPOF Audit During Architecture Review

**Theory**: minimal cut sets and importance measures (Birnbaum, criticality, Fussell-Vesely) in [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md).

**Architecture definition.** A SPOF is a size-1 minimal cut set for the top event "system unavailable."

**Audit procedure.**

1. Use the RBD from P1 for each critical request path.
2. Any component appearing once with no parallel path is a candidate SPOF.
3. Verify independence of "redundant" paths: a shared network switch, power rail, managed-service control plane, software version, or deploy pipeline is the real SPOF.
4. Rank confirmed SPOFs by Fussell-Vesely importance; create owned, dated remediation items for those covering the top ~80% of importance.

**SPOF categories architecture reviews miss.**

| SPOF Category | Canonical Examples | Typical Oversight |
|---------------|-------------------|------------------|
| Network | Single ISP, single transit router, VPN endpoint | Treated as infrastructure, not modelled in RBD |
| Data | Single writable primary, single object-storage bucket | Assumed "always available" |
| Auth | Single KMS key, single identity provider | External dependency, not owned |
| Control plane | Single Kubernetes API server, single DNS zone | Background infrastructure |
| Deployment | Single deploy pipeline for all services | DevOps tooling, not in reliability model |
| External SaaS | Single payment gateway, single email provider | Third-party SLA accepted uncritically |

**Per-container review checklist.**

```
For [Container X]:
  □ Is there a parallel path if this container fails?
  □ If yes: do the paths share a failure domain (AZ, power, network, software, pipeline)?
  □ What is the failover mechanism, and what is its measured coverage c?
  □ Does the allocated Rᵢ require active redundancy, standby, or neither?
  □ Is the FMEA worksheet (P3) current for this container?
```

---

### P6 — Dependency-Graph Reliability Rollup

**Theory**: series composition in [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md).

**Architecture rule.** A_effective(S) = A_intrinsic(S) × ∏ A_effective(D) over *synchronous* downstream dependencies, propagated leaf-first. Async (queue-backed, fire-and-forget) dependencies are excluded from the request path and get their own model: message loss or processing delay beyond SLO, with MTBF/MTTR applied to the consumer ([01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md)).

**Worked example.**

```
User → API (0.9999)
        ├── Auth (0.9997)            [sync]
        ├── Core (0.9995)            [sync]
        │     └── DB (0.9993)        [sync]
        └── Notifications (0.9990)   [async — excluded]

A_eff(Core) = 0.9995 × 0.9993 ≈ 0.9988
A_eff(API)  = 0.9999 × 0.9997 × 0.9988 ≈ 0.9984   (≈ 14.0 h downtime/yr)
```

Every intrinsic value is above 99.9%, yet the effective figure is 99.84%; the DB (lowest A) is the series bottleneck.

**Operational use.** Automate the rollup in the service catalog: when a new synchronous dependency is added, re-run and flag any service whose A_effective falls below its allocated target — a continuous architecture fitness function.

---

### P7 — RTO and RPO Derivation from Primitives

**Theory**: MTTR decomposition in [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md); coverage in [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md); infant-mortality/wear-out in [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md).

**RTO is an MTTR bound — on the tail, not the mean.** Design so that the high-percentile MTTR (e.g. p95), not just the mean, stays within the agreed RTO. MTTR = T_detect + T_diagnose + T_remediate + T_verify; for automated failover T_detect = check interval × consecutive-failure threshold (plus probe timeout), T_diagnose ≈ 0, T_remediate = promotion + DNS TTL + LB drain.

- If T_detect alone exceeds RTO, no remediation speed can meet it.
- A 1-minute RTO implies T_detect ≲ 20 s, e.g. 10 s checks × 2 consecutive failures — a constraint on monitoring design, not just an ops concern.
- MTTR is often the cheaper lever than redundancy: the foundation's example (DB at .9991, MTTR 45 min, target .999875 at constant MTBF) requires MTTR ≈ 6.2 min.

**RPO is a data-loss bound.** With asynchronous replication, exposed RPO at primary failure ≈ replication lag at that moment + detection time. Design to the lag *spike*, not the median: if lag is normally 2 s but spikes to 30 s, design for 30 s + T_detect.

**DR paths follow the bathtub curve.** A new DR path has infant-mortality failures (untested runbooks, misconfigured replication, cold-path bugs); an unexercised one drifts from the primary and behaves like wear-out. RTO commitments therefore require regular DR drills.

---

## Anti-Patterns

### A1 — Treating Redundant Components as Independent When They Share a Failure Domain

**See**: beta-factor model in [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md); [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md).

The parallel formula assumes independent failures. In architectures the common causes are: the same container image (one bug takes down both), the same AZ, a shared managed-service control plane, and the same deploy pipeline (a bad rollout reaches both before detection). With β = 0.05, a 0.999 pair drops from 0.999999 to ≈ 0.99995 — unavailability rises from 10⁻⁶ to ≈ 5 × 10⁻⁵.

Break-even: since A_adj = A_par − β(A_par − A_single), the pair meets target A_target only if **β ≤ (A_par − A_target) / (A_par − A_single)**. For A = 0.999 and A_target = 0.9999: β ≤ ≈ 0.099.

**Instead**: enumerate common-cause modes before computing A_parallel; reduce β through diversity (software version, rack, power, AZ, pipeline) before adding units.

---

### A2 — Allocating Equal Availability Targets Without Checking Achievability

**See**: [11-reliability-allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md).

Equal allocation is misapplied when a component is a third-party SaaS whose published SLA is below its allocation (e.g. 99.999% allocated to a gateway with a 99.9% SLA), a shared database whose MTTR cannot drop without architectural change, or a component on a parallel path (which needs a looser individual target). Teams commit to targets that are arithmetically correct for a homogeneous series chain but physically unreachable, and the SLO is breached by the allocation, not the design.

**Instead**: after equal allocation, validate each Rᵢ against vendor SLA or observed availability, achievable MTTR at current MTBF (R2 Step 4), and the actual topology; switch to ARINC or AGREE where subsystems differ.

---

### A3 — Adding Replicas Without Verifying Switchover Reliability

**See**: imperfect coverage and coverage validation in [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md).

A hot-standby DB replica promoted by a script with c = 0.80: 0.80 × 0.999999 + 0.20 × 0.999 ≈ 0.99980. Better than 0.999, but short of a 0.9999 target — and adding more replicas does not help because the bottleneck is c, not n.

**Instead**: measure c for each failover mechanism (failover drills, chaos experiments) before counting it toward the target, and fix coverage before increasing n. Coverage differs sharply between automated restart of stateless services, DNS-TTL failover, and manual runbook promotion; do not assume a value — validate it with the foundation's trial-count guidance.

---

### A4 — Confusing Mission-Time Reliability with Steady-State Availability

**See**: [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md), [09-weibull-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md), [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md).

Two architecture traps:

1. **Batch SLAs** ("the nightly job must finish in 4 h") are mission-time questions: use R(4 h) from the failure distribution, not the component's steady-state 99.9%.
2. **New components** are in infant mortality; applying steady-state A right after launch overstates reliability.

**Instead**: steady-state A for continuous-service SLOs; R(t) (exponential or Weibull) for bounded tasks; account for burn-in on newly deployed components.

---

## Recipes

### R1 — System Reliability Rollup and Bottleneck Identification

**Objective**: compute end-to-end availability for a topology, find the bottleneck, and decide where reliability investment has the most leverage.

**Primitive stack**: #10 + #02 + #07 + #11.

1. **Collect** per-component A_intrinsic (SLO dashboard, incident history, vendor SLA, or MTBF/MTTR), redundancy (n, active/standby), coverage c, and a justified β.
2. **Draw the RBD** — e.g. `[CDN 0.9999] → [LB 0.99999] → [App ×2, 0.999, active] → [DB 0.9993]`.
3. **Roll up** bottom-up:

```python
def rollup(graph, node):
    """A_effective for node: own redundancy (beta, coverage) × sync downstream."""
    downstream = 1.0
    for dep in graph.get_sync_dependencies(node):
        downstream *= rollup(graph, dep)
    a = node.A_intrinsic
    if node.replica_count > 1:
        a_par = 1 - (1 - a) ** node.replica_count
        a_par = a_par * (1 - node.common_cause_beta) + node.common_cause_beta * a
        a = node.coverage * a_par + (1 - node.coverage) * a
    return a * downstream
```

4. **Identify the bottleneck**: in a series chain, first-order ΔA_system ≈ ΔAᵢ × (A_system / Aᵢ), so the least-available component gives the largest return.
5. **Evaluate redundancy vs MTTR reduction** for the bottleneck (P4, P7). β values per deployment option are assumptions to be justified in the ADR.
6. **Re-run** with the proposed change; verify A_system ≥ target and each A_effective(i) ≥ Rᵢ; record in a P4 ADR.

---

### R2 — SLA Back-Allocation to Microservices

**Objective**: give each owning team a concrete Rᵢ, error budget, and deploy-risk implication.

**Primitive stack**: #11 + #02 + #08 + #10.

1. **Scope**: user-facing SLO (e.g. checkout 99.95%), RBD from R1, series/parallel labels, owning team per block.
2. **Method**: pick per the P2 table.
3. **Baseline**: equal allocation, 5 series services → Rᵢ ≈ 0.9999.
4. **Achievability check** per service:
   - MTTR_required = MTBF × (1 − Rᵢ) / Rᵢ; flag if current MTTR is higher.
   - Third-party SLA ≥ Rᵢ? If not: renegotiate budget elsewhere, dual-vendor, or change method.
   - Parallel-path services get looser targets; recompute with the real topology.
5. **Budget and deploy risk** (window as a parameter):

```python
def error_budget_minutes(r_i, window_minutes=43_800):  # average month; 43_200 for 30 days
    return (1 - r_i) * window_minutes

budget = error_budget_minutes(0.9999)        # ≈ 4.38 min
# If each risky deploy costs ~1 effective minute (2 min at 50% errors):
max_risky_deploys = int(budget / 1.0)        # 4 per month
```

6. **Hand-off table**:

| Service | Allocated Rᵢ | Budget (min/avg month) | Max risky deploys | Current A | Gap |
|---------|-------------|------------------------|-------------------|-----------|-----|
| API Gateway | 0.9999 | 4.38 | 4 | 0.9999 | — |
| Auth Service | 0.9999 | 4.38 | 4 | 0.9997 | 0.0002 ← fix |
| Core Service | 0.9999 | 4.38 | 4 | 0.9995 | 0.0004 ← fix |
| Payment Proxy | 0.9999 | 4.38 | 4 | 0.9993 | 0.0006 ← fix |
| Database | 0.9999 | 4.38 | 4 | 0.9991 | 0.0008 ← fix |

Services with a gap improve MTTR or add redundancy; re-run R1 before finalising.

---

### R3 — SPOF Audit and Redundancy Decision for an Architecture Review

**Objective**: find all SPOFs, quantify their impact, and produce a prioritised remediation list with ADR stubs.

**Primitive stack**: #05 + #06 + #07 + #10 + #11.

1. **Enumerate** from the R1 RBD: single-instance components plus "parallel" paths sharing a failure domain.
2. **Lightweight FTA** per candidate: top event "SLO breach caused by [candidate]", OR-gate over software defect / infrastructure / operator error (probabilities from incident history, vendor SLA, change-failure rate). MCS = {candidate} confirms a SPOF. Expected downtime = (1 − Aᵢ) × window.
3. **Rank** by Fussell-Vesely importance. For a series chain of rare-failure components, FVᵢ ≈ (1 − Aᵢ) / (1 − A_system) ≈ (1 − Aᵢ) / Σⱼ(1 − Aⱼ).
4. **Remediate** the top-ranked SPOFs with the cheapest option that closes the gap to Rᵢ: redundancy (n and c_min per P4, β per A1), MTTR reduction (P7 decomposition), or accept-and-degrade (graceful degradation; reallocate budget) when a third-party SLA caps Rᵢ.
5. **Output table** (three series SPOFs only, so Σ(1 − Aⱼ) = 0.0014; downtime per average month):

| Component | Type | Current A | FV Importance | Downtime/mo | Rᵢ Target | Remediation | Owner |
|-----------|------|-----------|---------------|-------------|-----------|-------------|-------|
| Primary DB | Data SPOF | 0.9991 | ≈ 0.64 | ≈ 39.4 min | 0.9999 | Active-standby + validated c | DB team |
| ISP link | Network SPOF | 0.9997 | ≈ 0.21 | ≈ 13.1 min | 0.9999 | Dual-ISP | Infra |
| Auth KMS key | Auth SPOF | 0.9998 | ≈ 0.14 | ≈ 8.8 min | 0.9999 | Local key cache with TTL | Platform |

6. **ADR stubs** (P4) for the top three; gate the next architecture review on them being accepted or superseded.

**Success criterion**: after remediation, re-run R1; A_system ≥ target, else return to Step 3 with updated values.

---

## Composition

```
1. Draw RBD (P1)                → series vs parallel topology
2. Roll up A_effective (R1, P6) → system ceiling and bottleneck
3. Back-allocate (P2, R2)       → each team's Rᵢ and error budget
4. SPOF audit (P5, R3)          → size-1 MCS ranked by FV importance
5. Failure-mode budget (P3)     → FMEA (S ≥ 9 first) against the error budget
6. Redundancy ADR (P4)          → n and validated c before hardware spend
7. RTO/RPO (P7)                 → DR architecture grounded in MTTR decomposition
```

The critical chain is P1 → P2 → P4: allocation needs the topology, and redundancy sizing needs the allocated target. Do not write the ADR before the RBD exists.

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

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering*. O'Reilly. Chapters 3–4 (error budgets, SLOs).
- Beyer, B., Murphy, N. R., Rensin, D. K., Kawahara, K., & Thorne, S. (2018). *The Site Reliability Workbook*. O'Reilly. Chapter 2 "Implementing SLOs" (rolling windows); Chapter 5 "Alerting on SLOs" (multi-window, multi-burn-rate alerting, Table 5-8) — https://sre.google/workbook/alerting-on-slos/
- Lewis, E. E. (1995). *Introduction to Reliability Engineering* (2nd ed.). Wiley.
- Birolini, A. (2017). *Reliability Engineering: Theory and Practice* (8th ed.). Springer.
- O'Connor, P. D. T., & Kleyner, A. (2012). *Practical Reliability Engineering* (5th ed.). Wiley.
- IEEE Std 1413 (2010). *IEEE Standard Methodology for Reliability Prediction and Assessment for Electronic Systems and Equipment*.
- IEC 60812 (2018). *Failure modes and effects analysis (FMEA and FMECA)*.
- IEC 61025 (2006). *Fault tree analysis (FTA)*.
- IEC 61508-6 (2010). *Functional safety of E/E/PE safety-related systems — Part 6*. (Beta-factor guidance.)
- Nygard, M. (2018). *Release It!* (2nd ed.). Pragmatic Bookshelf. (Failure modes in distributed systems.)

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
