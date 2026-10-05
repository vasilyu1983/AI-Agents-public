---
description: Decision-theory patterns applied to software architecture decisions — ADRs with expected-utility framing, real options for irreversibility, MCDA with sensitivity, minimax regret, value of information for spike sizing, risk aversion in SLO budgets, and dominance screening before MCDA.
last_verified: 2026-09-23
status: stable
---

# Decision Theory Applied to Architecture Decisions

> **Gate before invoking:** Check [`foundations-decision-theory` § When to Apply](../../foundations-decision-theory/SKILL.md#when-to-apply) first. The foundation owns every definition, formula, and generic failure mode; this file only maps them onto architecture decisions (ADRs, shortlists, irreversible splits, SLO budgets, spikes).

Theory pointers (from this directory):

- Root and primitive index: [`../../foundations-decision-theory/SKILL.md`](../../foundations-decision-theory/SKILL.md)
- Templates: [EU](../../foundations-decision-theory/assets/templates/decision-theory/01-expected-utility.md), [minimax regret](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md), [value of information](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md), [MCDA](../../foundations-decision-theory/assets/templates/decision-theory/05-multi-criteria.md), [risk aversion](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md), [real options](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md), [stochastic dominance](../../foundations-decision-theory/assets/templates/decision-theory/11-stochastic-dominance.md)
- Utility-compatible costs and sensitivity: [`practical-contract.md`](../../foundations-decision-theory/references/practical-contract.md); exact EVPI/EVSI: [`finite-state-calculator.md`](../../foundations-decision-theory/references/finite-state-calculator.md); stopping and thresholds: [`thresholds-stopping-and-ope.md`](../../foundations-decision-theory/references/thresholds-stopping-and-ope.md)

## Contents

- [Failure-to-Primitive Map](#failure-to-primitive-map)
- [Patterns](#patterns) — P1 ADR as EU spec · P3 minimax regret · P4 VoI for spikes · P5 MCDA · P6 risk aversion in SLOs · P7 real options · P11 dominance screening
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes) — R1 ADR with sensitivity sweep · R2 real-options ADR · R3 spike sizing via EVSI
- [Composition](#composition)
- [Sources](#sources)

---

## Failure-to-Primitive Map

| Architecture failure | Diagnosis | Pattern |
|---|---|---|
| Chose PostgreSQL because "everyone uses it" | No utility function; outcome probabilities never stated | P1 |
| Committed to microservices before the team owned two services | Irreversibility not priced; option to defer destroyed | P7 |
| MCDA spreadsheet produced a winner; nobody checked weight swaps | Weight uncertainty suppressed | P5 |
| Two-week spike approved because it "might answer the question" | Value of the *specific* spike never compared with its cost | P4, R3 |
| P99 latency or capacity set at the mean plus a vague margin | Risk-neutral framing for a severe downside tail | P6 |
| 10-year runtime chosen from a popularity survey | Contested probabilities; worst-case regret never compared | P3 |

---

## Patterns

### P1 — ADR Structured as an Expected-Utility Specification

**Applies to**: any technology choice that cannot be reversed within a sprint. Mechanics: [01-expected-utility](../../foundations-decision-theory/assets/templates/decision-theory/01-expected-utility.md).

State options, the decision driver, per-option outcome probabilities and failure costs so reviewers can contest them and successors can reopen the decision:

```
Options:  A (PostgreSQL + read replicas), B (CockroachDB), C (DynamoDB)
Driver:   write throughput at 5x current load, p95 < 50ms
  A: P(meets target) = 0.75; rework if it fails = 3 eng-months
  B: P(meets target) = 0.90; rework if it fails = 1 eng-month
  C: P(meets target) = 0.95; exit/lock-in cost   = 6 eng-months
Expected rework (risk-neutral, eng-months): A = 0.75, B = 0.10, C = 0.30
Risk check: concave utility penalises C's 6-month tail further; B stays first.
```

Record the sensitivity sweep and the threshold at which the ranking reverses (e.g., "if our write-load estimate is 2x too low, which option keeps its rank?"). The ADR then records a decision, not just an outcome.

### P3 — Minimax Regret for Ambiguous Long-Horizon Tech Bets

**Applies to**: 3+ year language/runtime migrations, database engines with contested vendor or licensing trajectories, platform bets (Kubernetes vs serverless-first) where probabilities cannot be defended. Mechanics: [03-minimax-regret](../../foundations-decision-theory/assets/templates/decision-theory/03-minimax-regret.md).

Regret table (illustrative utility units; regret = best payoff in scenario − this option's payoff, so ≥ 0):

| Option | JS/TS stays dominant | Rust wins for services | WASM absorbs both | **Max regret (row)** |
|---|---|---|---|---|
| Stay on Node.js | 0 | 8 | 6 | **8** |
| Migrate to Rust | 3 | 0 | 2 | **3** |
| Hedge: Node for product, Rust for perf-critical | 1 | 2 | 0 | **2** |

Minimax-regret pick: the hedge (max regret 2). Max regret is taken across each **row**, not down each scenario column. Adding or removing an option can change the pick — re-run the table if the shortlist changes.

### P4 — Value of Information to Size Spike Investigations

**Applies to**: any POC, benchmark, load test, or feasibility study costing more than half a sprint. Mechanics: [04-value-of-information](../../foundations-decision-theory/assets/templates/decision-theory/04-value-of-information.md).

A spike is an information purchase. Two-step rule:

1. **Screen with EVPI (ceiling only).** EVPI assumes the spike reveals the true state perfectly. If spike cost (including the delay it imposes) > EVPI, **skip** it. If no finding could change the decision, EVPI = 0 — cancel.
2. **Approve with EVSI.** EVPI > cost does **not** justify the spike. Estimate how likely the spike is to detect the decisive fact (sensitivity) and to raise a false alarm, compute the posterior-optimal action for each spike result, and approve only if EVSI > spike cost on the same scale (eng-weeks under risk neutrality; otherwise fold the cost into terminal outcomes — see [practical-contract](../../foundations-decision-theory/references/practical-contract.md)). Worked example: [R3](#r3--spike-sizing-via-value-of-information).

**Skip example — gRPC vs REST, inter-service protocol**: current best action is gRPC; P(disqualifying latency finding) = 0.20; switching to REST after such a finding saves 2 eng-weeks of rework. EVPI = 0.20 × 2 = 0.4 weeks < spike cost 1 week ⇒ skip; adopt gRPC and accept the 20% chance of a 2-week rework.

Spikes become worth pricing with EVSI when the prior is genuinely uncertain, the reversal cost is large relative to the spike cost, **and** the spike's test conditions (payload mix, concurrency, data volume) are close enough to production that it can actually detect the failure.

### P5 — MCDA with Sensitivity Analysis for Technology Shortlists

**Applies to**: shortlists with 3+ options and 3+ incommensurable criteria (latency headroom, cold start, operational complexity, ecosystem maturity, team ramp-up, vendor risk). Binary go/no-go calls are better framed as EU (P1). Mechanics (AHP, TOPSIS, weighted sum): [05-multi-criteria](../../foundations-decision-theory/assets/templates/decision-theory/05-multi-criteria.md).

Architecture-specific requirements:

- Record who set the weights and why; anchor 1–5 scores to benchmark or incident evidence where it exists.
- Perturb each weight ±20% and disclose rank stability in the ADR. A ranking that flips at ±5% is fragile and needs explicit weight agreement before acceptance.

**Example — monolith decomposition strategy**: criteria are delivery risk, time to first user value, runbooks required, rollback complexity, team cognitive load. "Extract read services first" wins at nominal weights, but the ranking reverses if the rollback-complexity weight rises from 0.15 to 0.22 — plausible for a team that recently failed a rollback. The ADR names that reversal threshold instead of claiming a clear winner.

### P6 — Risk Aversion in Load and SLO Decisions

**Applies to**: capacity headroom, error-budget negotiation, SLO targets, cache hit-rate floors — any decision where under-provisioning costs far more than over-provisioning. Mechanics (concave utility, certainty equivalents, CARA/CRRA): [06-risk-aversion](../../foundations-decision-theory/assets/templates/decision-theory/06-risk-aversion.md).

**Example — read replicas for a content platform**: expected peak 12,000 read QPS, σ ≈ 2,000 (normal approximation), 4,000 QPS per replica.

- Mean sizing: 12,000 / 4,000 = 3 replicas.
- P99 sizing: 12,000 + 2.33σ ≈ 16,650 QPS ⇒ 4.16 ⇒ 5 replicas. Mean + 3σ = 18,000 QPS (≈ P99.87) ⇒ 4.5 ⇒ 5 replicas.

Which quantile to size for is not a statistics question: it follows from the cost of an under-provisioned peak (brand, revenue, SLA credits, regulatory exposure) versus the cost of idle replicas. State both costs; if the downside is severe and hard to undo, a risk-neutral mean-based answer is the wrong model.

### P7 — Real Options Framing for Irreversible Architectural Commits

**Applies to**: monolith-to-service split timing, database engine migrations, runtime migrations, proprietary orchestration layers — any choice with asymmetric reversal cost. "One-way vs two-way door" (Bezos 2015 letter) is the informal version. Mechanics: [07-real-options](../../foundations-decision-theory/assets/templates/decision-theory/07-real-options.md).

| Option | Architecture analogue | Has value when |
|---|---|---|
| Defer | Delay the microservices split until bounded contexts are stable | Domain-model uncertainty is still resolving |
| Expand | Modular monolith with clean boundaries; extract a service later | Feature set not yet stable enough to split |
| Abandon | Managed service before building in-house | Usage may not justify the operational cost |
| Compound | Stage-gated DB migration: dual-write, then cut over | Each stage reveals information that gates the next |

**Example**: a 6-person pre-launch marketplace team compares microservices now (reversal ≈ 4 months if the domain model is wrong) with a modular monolith (≈ 1 month of extraction if services turn out to be needed). Domain-model uncertainty resolves 3–6 months after launch. Committing now destroys the deferral option; the modular monolith preserves it. Price it with [R2](#r2--real-options-adr-for-irreversible-architectural-choices).

### P11 — Dominance Screening Before MCDA

**Applies to**: every shortlist, before weighting. Distinguish two checks:

- **Criterion-wise (Pareto) dominance** — option A scores ≥ B on every criterion and > on at least one. Then no non-negative weighting can rank B above A; eliminate B before MCDA. This is **not** first-order stochastic dominance.
- **First-order stochastic dominance (FSD)** — compares outcome *distributions* of **one** scalar outcome (e.g., p99 latency across load-test runs, monthly cost across traffic scenarios). "FSD across quality and cost" is undefined until the criteria are scalarised. FSD on a handful of sample runs is not proof of dominance — check it on enough runs, or state the uncertainty. Mechanics: [11-stochastic-dominance](../../foundations-decision-theory/assets/templates/decision-theory/11-stochastic-dominance.md).

**Example — cloud region shortlist for a UK-regulated workload**: AWS eu-west-2, Azure UK South, GCP europe-west2; criteria: UK residency, SLA, managed-Postgres maturity, egress cost. If AWS scores ≥ Azure on all four and strictly better on managed-Postgres maturity, AWS Pareto-dominates Azure; drop Azure. AWS vs GCP still needs MCDA (GCP wins on egress, AWS on managed Postgres).

---

## Anti-Patterns

### A1 — ADR That States "We Picked X" Without Utility or Sensitivity Rationale

"We chose Kafka over RabbitMQ because Kafka is more scalable" records an outcome, not a decision. A successor cannot tell whether the weights have changed (team grew, managed offering improved, throughput requirement dropped). **Fix**: [R1](#r1--adr-with-eu-and-sensitivity-sweep).

### A2 — Treating Reversibility-Asymmetric Decisions as Symmetric

Weighing "split now" against "stay monolith" symmetrically ignores that the split is a one-way door while the monolith keeps the option to split. Typical cases: a primary database with no documented migration path; decomposition before independent on-call ownership exists; adopting a proprietary workflow orchestrator before portability needs are known. **Fix**: price deferral with [R2](#r2--real-options-adr-for-irreversible-architectural-choices).

### A3 — MCDA Scoring Without Acknowledging Weight Uncertainty

A tech lead's intuitive weights produce a "clear winner" with no sweep. **Fix**: disclose the ±20% sweep (P5); if stakeholders cannot agree on weights, escalate to explicit value negotiation instead of presenting a false winner.

### A4 — Spike Investment Without VoI Sizing (or Sized by EVPI)

Two failure forms:

- "Let's run a two-week spike on WebAssembly for the hot path" with no statement of which finding would change the decision. If no finding would, EVPI = 0 — cancel.
- **"EVPI exceeds the spike cost, so approve it" / "cap the spike at EVPI."** EVPI assumes a perfect reveal; a real benchmark can miss the problem or raise a false alarm. EVPI only rules spikes *out*. Approve on EVSI > cost, and set the timebox from what the spike must measure to reach its detection power, never at EVPI. **Fix**: [R3](#r3--spike-sizing-via-value-of-information).

### A5 — Risk-Neutral Architecture for Systems With Severe Downside

Retry policy tuned for mean recovery time, replica count at mean load, SLOs at median availability — on a payment path where a peak-time failure triggers SLA penalties, regulatory reporting, or irreversible churn. **Fix**: size from the stated cost of the downside (P6). Circuit breakers, bulkheads, and warm standbys are risk-aversion instruments, not expected-value plays.

---

## Recipes

### R1 — ADR With EU and Sensitivity Sweep

1. **Options and quality attributes** — e.g., PostgreSQL vs CockroachDB vs DynamoDB; write throughput (p95 < 50ms at 5x load), operational simplicity, reversibility.
2. **Utility unit** — e.g., "1 unit = 1 eng-week of rework avoided"; state the reference event.
3. **Probabilities per option per attribute**, with their evidence (load tests on a comparable workload, vendor benchmarks, incident history).
4. **Compute EU** (weighted sum of P(attribute met) × weight; mechanics in [01-expected-utility](../../foundations-decision-theory/assets/templates/decision-theory/01-expected-utility.md)).
5. **Risk check** — options with large downside tails (exit cost, catastrophic failure mode) can drop under concave utility.
6. **Sweep** — perturb each probability ±15%; name the threshold that reverses the ranking.
7. **Record** the robust pick and the reopen condition.

**Template rationale block** (numbers re-derived):

```markdown
### Decision Rationale
Options: A (PostgreSQL + read replicas), B (CockroachDB), C (DynamoDB)
Weights (1 unit = 1 eng-week avoided rework):
  throughput at 5x, p95 < 50ms: 3 | runbook simplicity: 1 | reversibility: 2
Probabilities:
  A: throughput 0.70, ops 0.90, reversibility 0.85
  B: throughput 0.90, ops 0.70, reversibility 0.95
  C: throughput 0.95, ops 0.60, reversibility 0.30
EU: A = 4.70, B = 5.30, C = 4.05
Risk check: C's low reversibility (6-month exit) already ranks it last; concave
utility widens the gap.
Sensitivity: B leads A unless A's throughput probability reaches 0.90
(requires a load test confirming headroom).
Robust pick: B. Reopen if A's 5x load test returns p95 < 45ms.
```

### R2 — Real-Options ADR for Irreversible Architectural Choices

1. **Classify the door** — one-way if reversal exceeds ~2 eng-months or it fixes a shared schema, protocol contract, or deployment topology; two-way if reversible in under two weeks (team heuristics; set your own).
2. **Name the live uncertainty** — e.g., "Order and Inventory may merge under a marketplace strategy."
3. **Estimate when and how completely it resolves** — e.g., "~6 months post-launch; P(resolved by the gate) ≈ 0.7 (illustrative)."
4. **Price deferral**: value of deferring ≈ P(current choice wrong) × P(uncertainty resolved by the gate) × reversal cost. `P(wrong) × reversal cost` alone assumes waiting reveals the answer perfectly — it is a ceiling, like EVPI. Compare with the cost of keeping the option open (maintaining modular boundaries, delayed benefits of the split).
5. **Stage it** — approve Stage 1 only; write the Stage 2 gate condition into the ADR.

```markdown
### Option Pricing (Order/Inventory split)
Reversal cost if the domain model is wrong: ~3 eng-months → ONE-WAY DOOR
P(current domain model wrong) = 0.35 (roadmap reviews)
P(uncertainty resolved within 6 months) = 0.7 (illustrative)
Ceiling (perfect resolution): 0.35 × 3 = 1.05 months
Expected value of deferring: 0.35 × 0.7 × 3 = 0.735 months
Cost of deferral (modular boundaries for 6 months): 0.5 months
Decision: 0.735 > 0.5 → DEFER; proceed with modular monolith.
Stage 2 gate: split when P(domain model wrong) < 0.15, signalled by
3 consecutive quarters with no cross-domain schema merges.
```

### R3 — Spike Sizing via Value of Information

**Goal**: decide whether a specific spike is worth its cost, and what it must measure.

1. **Tie the spike to one decision** — "gRPC or REST on the critical payment path?"
2. **Name the decision-changing finding** — "gRPC p99 > 20ms under our payload distribution ⇒ switch to REST."
3. **Prior** — P(issue) ≈ 0.15 (from comparable-payload benchmarks).
4. **Losses on one scale** (eng-weeks, risk-neutral): adopt gRPC and the issue exists ⇒ 3 weeks of post-deployment migration; adopt REST and there is no issue ⇒ 1 week of forgone gRPC benefit (illustrative).
5. **EVPI screen**: prior-optimal action is gRPC with expected loss 0.15 × 3 = 0.45 weeks (REST: 0.85 × 1 = 0.85). EVPI = 0.45 weeks. Any spike costing more — including decision delay — is ruled out. This is a ceiling, not a budget.
6. **EVSI** — state the spike's detection power: P(spike flags | issue exists) and P(spike flags | no issue). Illustrative: 0.7 and 0.1 (a synthetic benchmark can miss production payload mix or concurrency).

   | Spike result | P(result) | P(issue \| result) | Best action | Expected loss |
   |---|---|---|---|---|
   | Flags latency | 0.19 | 0.553 | REST | 0.447 wk |
   | No flag | 0.81 | 0.056 | gRPC | 0.167 wk |

   Pre-posterior loss = 0.19 × 0.447 + 0.81 × 0.167 = 0.22 weeks ⇒ **EVSI = 0.45 − 0.22 = 0.23 weeks** (≈ 1.1 days).
7. **Decide** — approve only if spike cost < 0.23 weeks. EVSI is sensitive to detection power: sensitivity 0.9 / false alarm 0.05 ⇒ EVSI ≈ 0.36 weeks; 0.5 / 0.2 ⇒ ≈ 0.055 weeks. If the cheapest credible spike costs more than its EVSI, commit to gRPC without it.
8. **Write the ticket** — decision criterion ("p99 > 20ms at 5KB payload ⇒ REST, else gRPC"), the test conditions that give it its detection power, and a timebox below its EVSI. For non-binary findings or more states use [finite-state-calculator](../../foundations-decision-theory/references/finite-state-calculator.md).

**Architecture spike signals**:

- *Zero EVPI*: "Do we need a message queue?" when the traffic pattern already mandates async — cancel.
- *Low EVPI*: "Benchmark gRPC vs REST" with strong prior experience and cheap migration — commit without the spike.
- *High EVPI, EVSI decides*: "Load test the proposed Postgres schema at 10x" with P(fails at 10x) ≈ 0.4 and ~8 eng-weeks to move engines ⇒ EVPI ≈ 3.2 weeks, so spikes above that are out; whether a 1-week load test is worth it depends on how faithfully it reproduces 10x production traffic (its EVSI).

---

## Composition

| Decision structure | Primary | Supporting |
|---|---|---|
| Shortlist, 3+ incommensurable criteria | MCDA (P5) | Dominance screen first (P11); risk aversion (P6) for large downside tails |
| Irreversible commit under live uncertainty | Real options (P7, R2) | EU (P1); minimax regret (P3) if probabilities are contested |
| Spike / POC investment | VoI (P4, R3) | EU for the post-spike decision; risk aversion if that decision has a severe tail |
| One-way-door ADR | EU + sensitivity (P1, R1) | Real options to price deferral; minimax regret if probabilities are contested |
| SLO, capacity, error budget | Risk aversion (P6) | EU baseline; VoI if a load test is proposed |

Canonical order: (1) dominance screen → (2) reversibility check and deferral pricing → (3) EU with risk check if probabilities are defensible, minimax regret if not → (4) MCDA with sweep for incommensurable criteria → (5) if a spike is proposed, EVPI to rule it out, EVSI to approve it → (6) record probabilities, weights, and reopen conditions in the ADR.

---

## Sources

Domain sources:

- Nygard, M. (2011). "Documenting Architecture Decisions." https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions — ADR format origin.
- Bezos, J. (2015). Amazon Shareholder Letter — one-way vs two-way door (Type 1 / Type 2) decisions.

Decision-theory canon: [`../../foundations-decision-theory/data/sources.json`](../../foundations-decision-theory/data/sources.json).

Related references in this skill:

- [adr-template.md](../assets/planning/adr-template.md) — the ADR template this reference extends.
- [migration-modernization-guide.md](migration-modernization-guide.md) — reversibility analysis for monolith-to-service migrations (P7, R2).
- [scalability-reliability-guide.md](scalability-reliability-guide.md) — SLO budgets and capacity decisions (P6).
- [modern-patterns.md](modern-patterns.md) — pattern selection that benefits from MCDA and dominance screening (P5, P11).
