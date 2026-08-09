---
description: Decision-theory patterns applied to software architecture decisions — ADRs with expected-utility framing, real options for irreversibility, MCDA with sensitivity, minimax regret, value of information for spike sizing, risk aversion in SLO budgets, and stochastic dominance as a shortcut.
last_verified: 2026-05-02
status: stable
---

# Decision Theory Applied to Architecture Decisions

> **Gate before invoking:** Check [`foundations-decision-theory` § When to Apply](../../foundations-decision-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Companion to [foundations-decision-theory](../../foundations-decision-theory/SKILL.md). Applies its 11 primitives to the concrete decision structures that arise in software architecture work: ADR writing, technology shortlists, irreversible splits, SLO budgets, and spike investment._

## Table of Contents

- [Why Decision Theory in Architecture](#why-decision-theory-in-architecture)
- [Patterns](#patterns)
  - [P1 — ADR Structured as an Expected-Utility Specification](#p1--adr-structured-as-an-expected-utility-specification)
  - [P3 — Minimax Regret for Ambiguous Long-Horizon Tech Bets](#p3--minimax-regret-for-ambiguous-long-horizon-tech-bets)
  - [P4 — Value of Information to Size Spike Investigations](#p4--value-of-information-to-size-spike-investigations)
  - [P5 — MCDA with Sensitivity Analysis for Technology Shortlists](#p5--mcda-with-sensitivity-analysis-for-technology-shortlists)
  - [P6 — Risk Aversion in Load and SLO Decisions](#p6--risk-aversion-in-load-and-slo-decisions)
  - [P7 — Real Options Framing for Irreversible Architectural Commits](#p7--real-options-framing-for-irreversible-architectural-commits)
  - [P11 — Stochastic Dominance to Short-Circuit MCDA](#p11--stochastic-dominance-to-short-circuit-mcda)
- [Anti-Patterns](#anti-patterns)
  - [A1 — ADR That States "We Picked X" Without Utility or Sensitivity Rationale](#a1--adr-that-states-we-picked-x-without-utility-or-sensitivity-rationale)
  - [A2 — Treating Reversibility-Asymmetric Decisions as Symmetric](#a2--treating-reversibility-asymmetric-decisions-as-symmetric)
  - [A3 — MCDA Scoring Without Acknowledging Weight Uncertainty](#a3--mcda-scoring-without-acknowledging-weight-uncertainty)
  - [A4 — Spike Investment Without VoI Sizing](#a4--spike-investment-without-voi-sizing)
  - [A5 — Risk-Neutral Architecture for Systems With Severe Downside](#a5--risk-neutral-architecture-for-systems-with-severe-downside)
- [Recipes](#recipes)
  - [R1 — ADR With EU and Sensitivity Sweep](#r1--adr-with-eu-and-sensitivity-sweep)
  - [R2 — Real-Options ADR for Irreversible Architectural Choices](#r2--real-options-adr-for-irreversible-architectural-choices)
  - [R3 — Spike Sizing via Value of Information](#r3--spike-sizing-via-value-of-information)
- [Composition: Stacking Primitives](#composition-stacking-primitives)
- [Sources](#sources)

---

## Why Decision Theory in Architecture

Architecture decisions fail in the same ways that decisions under uncertainty always fail — and for the same reasons. The formal structure of decision theory maps directly to the recurring traps:

| Architecture failure | Decision theory diagnosis |
|---|---|
| Chose PostgreSQL because "everyone uses it" | No utility function; outcome probabilities never stated |
| Committed to microservices before team owned two services | Irreversibility not priced; option to defer destroyed |
| MCDA spreadsheet produced a winner; no one checked whether swapping two weights reversed the ranking | Weight uncertainty suppressed; false objectivity |
| Two-week spike approved because it "might answer the question" | VoI not computed; spike cost may exceed the value of the information it produces |
| P99 latency target set at mean × 1.5 because that is "good enough" | Risk-neutral framing for a risk-averse stakeholder; CE < EV |
| Node.js chosen for a 10-year platform because a survey said it was popular | Minimax regret not applied; worst-case payoffs never compared |

Architecture decisions are not unique. They are instances of the same formal structures treated in [foundations-decision-theory](../../foundations-decision-theory/SKILL.md). Primitives 1, 3, 4, 5, 6, 7, and 11 cover the full decision space that appears in architectural work.

---

## Patterns

### P1 — ADR Structured as an Expected-Utility Specification

**Primitive**: EU (#1), Risk Aversion (#6)

An ADR whose rationale section says "we chose X because it fits our stack" has buried the decision theory. A decision-theoretically complete ADR makes utilities and probabilities visible so that reviewers can contest them and successors can reopen the decision when the evidence changes.

**Structure of a decision-theoretically complete ADR rationale**:

```
Options:        A (PostgreSQL + read replicas), B (CockroachDB), C (DynamoDB)
Decision driver: Write throughput at 5× current load, with p95 < 50ms
Outcomes per option (estimated):
  A: P(meets target) = 0.75; migration cost if it fails = 3 eng-months
  B: P(meets target) = 0.90; migration cost if it fails = 1 eng-month (reversible)
  C: P(meets target) = 0.95; lock-in cost if we want to leave = 6 eng-months

EU(A) = 0.75 × U(success) − 0.25 × U(3-month rework)
EU(B) = 0.90 × U(success) − 0.10 × U(1-month rework)
EU(C) = 0.95 × U(success) − 0.05 × U(6-month lock-in)

Sensitivity: if team is risk-averse (concave utility), the 6-month lock-in tail
on C reduces its CE below B despite higher expected success probability.
Robust pick: B.
```

**Example — database choice for a fintech payment rail**:

A team shortlisting PostgreSQL, CockroachDB, and Cassandra for a payment ledger first states the quality attributes that generate utility (durability, write latency, operational cost) and assigns probability estimates to each option meeting each attribute. They then run a sensitivity sweep: "If our write-load estimate is 2× too low, which option's EU ranking is stable?" PostgreSQL drops out; CockroachDB and Cassandra remain ordered. The ADR records this sweep and names the load threshold at which the ranking reverses, making the decision inspectable rather than merely recorded.

**When to use**: Any ADR for a technology choice that cannot be trivially reversed in under a sprint.

**Failure mode avoided**: Frozen rationale that cannot be re-evaluated when conditions change, because the original probability estimates and utility weights were never stated.

---

### P3 — Minimax Regret for Ambiguous Long-Horizon Tech Bets

**Primitive**: Minimax Regret (#3)

When probabilities are unknown or contested — typical of 5-year language, runtime, or framework bets — expected utility requires assigning a probability distribution that teams do not actually have. Minimax regret sidesteps this: identify the worst-case regret (the gap between what you got and what you would have gotten under the best option for each scenario) and choose the option whose worst-case regret is smallest.

**Minimax regret table for a language/runtime migration decision**:

| | Scenario: JS/TS remains dominant | Scenario: Rust wins for services | Scenario: WASM absorbs both |
|---|---|---|---|
| Stay on Node.js | 0 (best in scenario) | −8 | −6 |
| Migrate to Rust | −3 | 0 (best) | −2 |
| Hedge: Node for product, Rust for perf-critical | −1 | −2 | 0 (best) |
| **Max regret** | **−3** | **−8** | **−6** |

Minimax-regret pick: the hedge option (Node for product services, Rust for performance-critical paths), which has maximum regret of −3 across all scenarios — lower than committing fully to either language.

**When to use**:
- Language or runtime migrations with 3+ year horizons where ecosystem evolution is uncertain.
- Database engine choices where vendor stability, open-source licensing trajectories, or cloud-provider support are contested.
- Platform bets (Kubernetes vs. serverless-first) where the right answer depends on org trajectory that is not yet fixed.

**Failure mode avoided**: EU maximization with fabricated probability estimates for scenarios that are genuinely ambiguous, producing false precision in the ADR rationale.

---

### P4 — Value of Information to Size Spike Investigations

**Primitive**: VoI (#4)

A spike (proof of concept, technical investigation, load test) is an information purchase. Before approving it, compute EVPI — the maximum value the information could provide — and compare it to the spike's cost.

**EVPI formula applied to architecture decisions**:

```
EVPI = EU(best action with perfect info) − EU(best action with current info)
```

If the spike cannot move the EU-optimal action — because you would choose the same option regardless of what the spike reveals — EVPI = 0 and the spike should be cancelled.

**Example — gRPC vs REST spike for an inter-service protocol decision**:

- Current best action (no spike): adopt gRPC; EU advantage over REST ≈ 0.8 eng-weeks of future rework saved.
- Spike cost: 1 eng-week.
- If spike reveals gRPC latency is unacceptable: switch to REST, saving 2 eng-weeks of rework.
- Probability that spike reveals a disqualifying finding: 20%.

```
EVPI = P(disqualifying finding) × value_of_switching
     = 0.20 × 2 weeks = 0.4 weeks

Spike cost = 1 week > EVPI = 0.4 weeks → spike is not worth running.
```

The decision-theoretically correct action is to adopt gRPC without a spike and accept the 20% chance of a 2-week rework. The spike costs more than it is worth.

**When EVPI justifies a spike**: When the probability of a disqualifying finding is high (>40%), the cost of reversing the wrong choice is large, and the spike cost is small relative to that reversal cost.

**When to use**: Before any investigation, POC, or feasibility study that consumes more than half a sprint of engineering time.

**Failure mode avoided**: Approving open-ended spikes because they "might surface something useful," with no bound on cost or a clear link between findings and decision outcomes.

---

### P5 — MCDA with Sensitivity Analysis for Technology Shortlists

**Primitive**: MCDA (#5)

Multi-criteria decision analysis is the correct tool when a technology shortlist involves incommensurable objectives — performance, operational cost, team familiarity, vendor risk, ecosystem maturity. The failure mode is treating the MCDA output as objective truth when the weights are subjective preferences.

**MCDA process for architecture shortlists**:

1. Define criteria. For a service framework choice: latency headroom, cold-start behaviour, operational complexity, ecosystem maturity, team ramp-up time.
2. Elicit weights. Use AHP or direct assignment. Record who assigned the weights and why.
3. Score each option on each criterion (1–5 scale, anchored with objective evidence where available).
4. Compute weighted scores (TOPSIS or simple weighted sum).
5. Run the sensitivity sweep: perturb each weight ±20%. Record which rankings are stable and which reverse.
6. Disclose the sensitivity table in the ADR. A ranking that is stable across all ±20% perturbations is robust; a ranking that reverses at ±5% weight shift is fragile and should trigger explicit agreement on weight values before the decision is accepted.

**Example — monolith-to-service decomposition shortlist**:

A platform team shortlisting three decomposition strategies (extract read services first, extract write-path first, big-bang re-platform) runs MCDA with five criteria: delivery risk, time to first user value, operational runbooks required, rollback complexity, and team cognitive load. Under the initial weights, "extract read services first" scores highest. Sensitivity analysis reveals the ranking reverses if "rollback complexity" weight rises from 0.15 to 0.22 — a plausible weight for a team that recently failed a difficult rollback. The ADR names this reversal threshold explicitly, rather than claiming the MCDA produced a clear winner.

**When to use**: Any shortlist with 3+ options and 3+ incommensurable criteria. Do not apply to binary yes/no decisions, which are better framed as EU comparisons.

---

### P6 — Risk Aversion in Load and SLO Decisions

**Primitive**: Risk Aversion (#6)

Availability targets, error budgets, and capacity headroom are not expected-value decisions — they are certainty-equivalent decisions. A service that is available 99.9% of the time on average but fails catastrophically during the 0.1% tail is not equivalent to a service with stable 99.9% availability. The team (and its users) are risk-averse: they penalise variance in outcomes, not just the mean.

**Certainty-equivalent framing for SLO budgeting**:

```
CE = EV − (λ/2) × Var
```

Where λ is a risk-aversion coefficient and Var is the variance of outcome utility (e.g., penalty from SLO breaches). A risk-neutral team would set headroom at the mean predicted load plus a small margin. A risk-averse team shifts this upward by a factor proportional to λ × Var — which is why 3σ capacity headroom is standard practice even when the mean prediction is accurate.

**Example — read replica count for a content platform**:

Expected peak read QPS: 12,000. P99 spike estimate: 18,000 (σ ≈ 2,000). Each read replica handles 4,000 QPS.

- Risk-neutral sizing: 3 replicas (12,000 / 4,000).
- Risk-averse sizing: account for tail. At 3σ above mean = 18,000 QPS, need 5 replicas. With moderate risk aversion (λ = 1), the CE-optimal replica count is 5, not 3.

The right question is not "what is the average load?" but "what is the cost of under-provisioning, weighted by probability and risk aversion?" A read replica failure during a viral traffic event has disproportionate brand and revenue cost — concave utility, not linear.

**When to use**: Capacity headroom, error budget negotiation, SLO target setting, cache hit-rate floor decisions. Any architecture decision where the downside tail is more costly than the upside is beneficial.

**Failure mode avoided**: Setting SLOs at the median outcome (risk-neutral assumption) for a stakeholder who is actually risk-averse over service degradation events.

---

### P7 — Real Options Framing for Irreversible Architectural Commits

**Primitive**: Real Options (#7)

Jeff Bezos's "one-way door vs. two-way door" distinction is an informal statement of real options theory. A two-way-door decision has low reversal cost — the option to abandon is cheap to exercise. A one-way-door decision destroys the option to abandon or reverse. Real options analysis makes this precise: the value of deferring an irreversible commitment is positive as long as uncertainty exists and will reduce over time.

**Option types in architecture**:

| Option | Architecture analogue | When it has value |
|---|---|---|
| Option to defer | Delay microservices split until team owns 3+ services | Uncertainty about bounded contexts has not resolved |
| Option to expand | Build modular monolith; add service boundary later | Feature set not yet stable enough to split |
| Option to abandon | Use managed service before building in-house | Usage may not justify the operational cost |
| Compound option | Stage-gate the DB migration: dual-write first, then cut over | Each stage reveals information that gates the next |

**Example — monolith vs. microservices decision**:

A team of 6 is building a marketplace. Current revenue is pre-launch. The team is evaluating:

- Option A: Microservices from day one (commit now; cost to reverse = 4+ months of re-stitching).
- Option B: Modular monolith with clean domain boundaries (defer split; cost to reverse = extract one service per domain when ready).

The uncertainty that will resolve: whether the domain model is stable (resolves in 3–6 months after launch). The reversal cost of Option A if the domain model turns out to be wrong: 4 months. The cost of Option B if it turns out microservices were needed from day one: 1 month of extraction work.

Under real-options logic, the option-adjusted NPV of committing to microservices now is:
```
NPV_microservices_now = NPV_project − Option_value_of_waiting
```

If the domain model uncertainty resolves within 6 months with only a 1-month extraction cost, the option to defer is worth preserving. The modular monolith is the decision-theoretically correct choice — not because microservices are wrong, but because committing now destroys option value.

**When to use**: Monolith-to-service split timing, database engine migrations, programming language/runtime migrations, any architectural choice with asymmetric reversal cost.

---

### P11 — Stochastic Dominance to Short-Circuit MCDA

**Primitive**: Stochastic Dominance (#11)

When one architectural option dominates another across every plausible weight assignment — not just the nominal weights — a full MCDA run is unnecessary. First-order stochastic dominance (FSD) holds when option A scores at least as well as option B on every criterion, and strictly better on at least one. If FSD holds, no utility function or weight assignment can reverse the ranking; the inferior option can be eliminated without running the full MCDA.

**Checking for stochastic dominance before MCDA**:

1. Score all options on all criteria.
2. For each pair, check whether one option is dominated on all criteria.
3. If FSD holds for any pair, eliminate the dominated option before running weighted scoring.
4. If no FSD holds, proceed to full MCDA with sensitivity analysis (P5).

**Example — cloud provider shortlist for a UK fintech**:

Three options: AWS eu-west-2, Azure UK South, GCP europe-west2. Criteria: regulatory compliance (UK residency), SLA, operational maturity of Managed Postgres, egress cost.

If AWS eu-west-2 scores ≥ Azure on all criteria and strictly better on operational maturity, AWS FSD-dominates Azure for this specific decision. Azure is eliminated before running weighted MCDA. The remaining comparison is AWS vs. GCP — which requires full MCDA because GCP wins on egress cost while AWS wins on managed Postgres maturity, and no FSD holds.

**When to use**: Before running weighted MCDA on any shortlist. A 5-minute FSD check eliminates dominated options and reduces the MCDA to the genuinely contested subset.

**Failure mode avoided**: Running a full weighted MCDA on a shortlist that contains an obviously dominated option, which wastes time and can produce misleading sensitivity artefacts if the dominated option affects the weight calibration.

---

## Anti-Patterns

### A1 — ADR That States "We Picked X" Without Utility or Sensitivity Rationale

**Symptom**: The ADR decision section says "We chose Kafka over RabbitMQ because Kafka is more scalable." No probability estimates, no utility weights, no sensitivity sweep.

**Why it fails**: The decision is frozen in an unverifiable state. A successor who revisits the ADR has no way to know whether the utility weights have changed (team grew, RabbitMQ's managed offering improved, throughput requirements dropped), because the original weights were never stated. The ADR records an outcome, not a decision.

**Fix**: Follow [R1](#r1--adr-with-eu-and-sensitivity-sweep). State the utility-relevant quality attributes, assign probability estimates, run a sensitivity sweep, and name the conditions under which the ranking would reverse.

---

### A2 — Treating Reversibility-Asymmetric Decisions as Symmetric

**Symptom**: A team weighs "split to microservices now" against "stay monolith" using a symmetric cost-benefit comparison, ignoring that the split is a one-way door while staying monolith preserves the option to split later.

**Decision theory diagnosis**: Option value of deferral is positive but unpriced. Real options logic (P7) shows that committing to an irreversible action before uncertainty resolves destroys value even when the expected NPV of committing is positive.

**Fix**: Before any one-way-door decision, compute the reversal cost and the expected time for uncertainty to resolve. If (reversal cost × P(wrong choice)) > (deferral cost), defer. See [R2](#r2--real-options-adr-for-irreversible-architectural-choices).

**Architecture examples**:
- Choosing a primary database engine with no migration path documented.
- Decomposing a monolith before the team has ownership and on-call coverage for independent services.
- Committing to a cloud provider's proprietary orchestration layer (e.g., Step Functions, Durable Functions) before evaluating portability needs.

---

### A3 — MCDA Scoring Without Acknowledging Weight Uncertainty

**Symptom**: An architecture review produces a MCDA table with a clear winner. The weights were set by the tech lead based on intuition. No sensitivity sweep was run. The ranking is presented as objective.

**Decision theory diagnosis**: MCDA weights are subjective preferences embedded in numbers. Different reasonable stakeholders assign different weights. A ranking that is sensitive to small weight perturbations is fragile — but this fragility is hidden when no sensitivity analysis is reported.

**Fix**: Run the ±20% sensitivity sweep (P5). Any ranking that reverses within ±20% weight perturbation on any criterion must be disclosed. If the team cannot agree on weights, the MCDA cannot resolve the tie — escalate to explicit value negotiation rather than presenting a false winner.

---

### A4 — Spike Investment Without VoI Sizing

**Symptom**: "Let's run a two-week spike to evaluate whether we should use WebAssembly for our hot path." No calculation of what the spike needs to discover to change the decision, what the probability of that discovery is, or what the cost of the wrong choice would be without the spike.

**Decision theory diagnosis**: EVPI was never computed. The spike is implicitly assumed to have value proportional to its duration. In reality, EVPI = 0 whenever the decision is robust to the spike's possible outcomes — i.e., you would make the same architectural choice regardless of what the spike finds.

**Fix**: Before approving any spike, answer: "What would the spike need to find in order for our architectural decision to change?" If no finding changes the decision, EVPI = 0 — cancel the spike. See [R3](#r3--spike-sizing-via-value-of-information).

---

### A5 — Risk-Neutral Architecture for Systems With Severe Downside

**Symptom**: A payment processing system's retry policy is configured for mean-case recovery time. The database read-replica count is set at mean-load / capacity. SLO targets are set at median expected availability.

**Decision theory diagnosis**: Risk-neutral framing (EU maximisation without a concave utility function) is appropriate when outcomes are symmetric and downside tails have the same utility weight as upside tails. For systems where a failure during peak load triggers regulatory penalty, SLA breach penalties, or irreversible customer churn, the utility function is concave — the downside is worth more than a symmetric upside.

**Fix**: Apply certainty-equivalent sizing (P6). For any system where the downside tail loss exceeds the upside gain by more than 3×, treat the capacity, retry, and SLO design as a risk-averse problem. Size for the CE-optimal point, not the expected-value-optimal point. This is why circuit breakers, bulkheads, and warm standbys exist — they are risk-aversion instruments, not pure expected-value plays.

---

## Recipes

### R1 — ADR With EU and Sensitivity Sweep

**Goal**: Produce an ADR whose decision rationale is reproducible, contestable, and reopenable when conditions change.

**Inputs**: Two or more architectural options, a set of quality attributes that generate utility, probability estimates for each option meeting each attribute, cost estimates for the failure modes.

**Steps**:

1. **List options and quality attributes**. Example: PostgreSQL vs. CockroachDB vs. DynamoDB; quality attributes: write throughput (p95 < 50ms at 5× load), operational cost, lock-in reversibility.

2. **Assign utility values**. Quantify utility in a common unit (eng-weeks saved, revenue-risk avoided). State the reference event and scale. Example: "1 unit = 1 eng-week of future rework saved."

3. **Assign probability estimates per option per attribute**. Be explicit about confidence. Example: "P(PostgreSQL meets write throughput target) = 0.70, based on load test results from comparable workload at Acme Co."

4. **Compute EU per option**:
   ```
   EU(option) = Σ P(attribute_i met) × U(attribute_i met)
              + Σ P(attribute_i missed) × U(attribute_i missed)
   ```

5. **Apply risk-aversion check**. If the team is risk-averse (downside failures are penalised beyond their expected cost), compute certainty equivalents. Options with large downside tails (high lock-in reversal cost, catastrophic failure mode) may rank lower on CE than on raw EU.

6. **Run sensitivity sweep on probability estimates**. Perturb each probability ±15% and record rank stability. Name the threshold at which the ranking reverses. Include this table in the ADR rationale.

7. **State the robust pick**. The ADR decision records the option that is EU-optimal and CE-stable across the sensitivity sweep, plus the exact conditions that would reverse it.

**Template ADR rationale block**:

```markdown
### Decision Rationale

Options: A (PostgreSQL + read replicas), B (CockroachDB), C (DynamoDB)

Quality attributes and utility weights (1 unit = 1 eng-week avoided rework):
  - Write throughput at 5× load, p95 < 50ms: weight 3
  - Operational runbook simplicity: weight 1
  - Reversibility (migration cost if we change): weight 2

Estimated probabilities:
  A: throughput = 0.70, ops = 0.90, reversibility = 0.85
  B: throughput = 0.90, ops = 0.70, reversibility = 0.95
  C: throughput = 0.95, ops = 0.60, reversibility = 0.30

EU: A = 5.8, B = 7.1, C = 5.3 (units as defined above)

Risk-aversion adjustment: C's reversibility tail (migration cost = 6 months
if we exit) lowers its CE below A when team risk-aversion λ > 0.4.

Sensitivity: B's EU lead over A is stable unless A's throughput probability
rises above 0.87 (requires a load test confirming headroom).

Robust pick: B (CockroachDB). Reopen this decision if A's load test at 5×
throughput returns p95 < 45ms.
```

---

### R2 — Real-Options ADR for Irreversible Architectural Choices

**Goal**: Make the option value of deferral explicit before committing to a one-way-door architectural change.

**Inputs**: Candidate architectural commitment, estimated reversal cost, the uncertainty that will resolve and its resolution timeline, the cost of deferral.

**Steps**:

1. **Classify the decision as one-way or two-way door**. One-way: the reversal cost exceeds two months of engineering effort, or the decision commits a significant shared resource (schema, protocol contract, deployment topology). Two-way: the decision can be reversed in under two weeks.

2. **Identify the uncertainty that is live**. What do you not know that, if known, would change the decision? Example: "We do not know whether our domain model is stable. The Order and Inventory domains may merge if the product strategy shifts toward a marketplace model."

3. **Estimate the resolution timeline**. How long before this uncertainty resolves? Example: "We will have 3 months of production data on order patterns within 6 months of launch."

4. **Price the option to defer**:
   ```
   Option_value_of_deferral = P(current decision is wrong) × cost_of_reversal
   Cost_of_deferral = work required to keep the option open (e.g., maintain modular boundaries)
   ```
   If Option_value_of_deferral > Cost_of_deferral, defer.

5. **Structure the ADR as a compound option** where applicable. Each stage of a migration is an option purchase: completing Stage 1 buys the right to execute Stage 2. Do not approve all stages at the ADR stage; approve Stage 1 only, with the Stage 2 gate conditions stated explicitly.

**Example — monolith-to-microservices ADR**:

```markdown
### Decision Framing: One-Way or Two-Way?

Splitting the Order service from the Inventory monolith requires:
- Separate deployment pipelines (2 weeks to build)
- Database decomposition with dual-write phase (4 weeks)
- On-call ownership transfer (requires SRE resourcing)

Reversal cost if domain model turns out to be wrong: ~3 months.
Classification: ONE-WAY DOOR.

### Uncertainty in Play

Domain model stability: Product has not shipped. Order and Inventory
may merge under a marketplace strategy shift. Expected resolution: 6 months
post-launch (domain model stabilises after first 3 growth cycles).

### Option Pricing

P(current domain model is wrong) = 0.35 (based on product roadmap reviews)
Reversal cost = 3 months
Option_value_of_deferral = 0.35 × 3 months = 1.05 months

Cost of deferral (maintaining modular monolith boundaries for 6 months) = 0.5 months

Decision: Option_value (1.05 months) > Deferral_cost (0.5 months).
DEFER the service split. Proceed with modular monolith.
Stage 2 gate: execute service split when P(domain model wrong) < 0.15,
signalled by 3 consecutive quarters with no cross-domain schema merges.
```

---

### R3 — Spike Sizing via Value of Information

**Goal**: Bound the maximum justifiable cost of a spike (POC, investigation, load test, feasibility study) before approving it.

**Inputs**: The architectural decision the spike will inform, the current best action without the spike, the possible findings from the spike and their probabilities, the cost of the wrong architectural choice.

**Steps**:

1. **Name the decision the spike informs**. The spike is not a general exploration — it must be tied to a specific go/no-go gate. Example: "Should we adopt gRPC or REST for inter-service calls on the critical payment path?"

2. **Identify the decision-changing finding**. What specific result from the spike would change the architectural decision? Example: "If the gRPC benchmark shows p99 > 20ms under our expected message size distribution, we switch to REST."

3. **Estimate P(decision-changing finding)**. Be explicit. Example: "Based on benchmarks from similar payload sizes, P(gRPC p99 > 20ms) ≈ 0.15."

4. **Estimate the cost of the wrong decision without the spike**. This is the rework or migration cost incurred if you choose wrong and discover it in production. Example: "Migrating all inter-service calls from gRPC to REST post-deployment = 3 eng-weeks."

5. **Compute EVPI**:
   ```
   EVPI = P(decision-changing finding) × cost_of_wrong_decision
        = 0.15 × 3 weeks = 0.45 weeks
   ```

6. **Compare EVPI to spike cost**. If spike cost > EVPI, the spike is not worth running. If spike cost ≤ EVPI, approve the spike but cap its duration at EVPI.

7. **Set the spike cap and go/no-go criteria in the ticket**. A spike ticket without a go/no-go criterion is an open-ended investigation. State: "This spike is capped at 0.45 weeks. Decision criterion: if gRPC p99 > 20ms at 5KB payload, adopt REST; otherwise adopt gRPC."

**EVPI quick-reference table**:

| P(decision-changing finding) | Cost of wrong choice | EVPI | Spike justifiable at cost ≤ |
|---|---|---|---|
| 0.10 | 2 weeks | 0.2 weeks | 1 day |
| 0.20 | 4 weeks | 0.8 weeks | 4 days |
| 0.40 | 4 weeks | 1.6 weeks | ~8 days |
| 0.50 | 2 weeks | 1.0 weeks | 5 days |
| 0.60 | 6 weeks | 3.6 weeks | 18 days |

**Common spike scenarios and their EVPI signals**:

- *Low EVPI*: "Benchmark gRPC vs REST" when the team has high confidence in gRPC from prior work and the migration cost is low. Cancel the spike; commit to gRPC.
- *High EVPI*: "Load test the proposed Postgres schema at 10× traffic" when the migration to an alternative DB engine would cost 2 months and P(schema fails at 10×) ≈ 0.4. The spike is justified at up to 3.2 weeks.
- *Zero EVPI*: "Evaluate whether we need a message queue" when the team would adopt the queue regardless of the spike outcome (the traffic pattern already mandates async). EVPI = 0; cancel the spike.

---

## Composition: Stacking Primitives

Most real architectural decisions require more than one primitive. The table below maps common decision structures to the correct stack.

| Decision structure | Primary primitive | Supporting primitives | When to stack |
|---|---|---|---|
| Technology shortlist with 3+ incommensurable criteria | MCDA (#5) | Stochastic dominance (#11) first to eliminate dominated options; Risk aversion (#6) for options with large downside tails | Always check FSD before running full MCDA |
| Irreversible architectural commit under live uncertainty | Real options (#7) | EU (#1) to confirm the expected-value case; Minimax regret (#3) if the uncertainty is ambiguous (no reliable probability estimates) | When reversal cost > 1 month or the decision closes a deployment or schema boundary |
| Spike or POC investment decision | VoI (#4) | EU (#1) for the post-spike decision; Risk aversion (#6) if the post-spike action has a severe downside tail | Before any investigation longer than 3 days |
| ADR for a one-way-door decision | EU (#1) + Sensitivity sweep | Real options (#7) to price deferral; Minimax regret (#3) if probabilities are contested | All one-way-door ADRs |
| SLO, capacity, or error budget setting | Risk aversion (#6) | EU (#1) for the expected-value baseline; VoI (#4) if a load test is proposed to inform the SLO | Any system where downside tail cost exceeds upside benefit |

**Canonical composition for a full architectural decision**:

```
1. Check FSD (P11) — eliminate dominated options.
2. Check reversibility (P7) — if one-way door, price option to defer.
3. If probabilities are known: compute EU (P1) with risk-aversion adjustment (P6).
4. If probabilities are ambiguous: use minimax regret (P3).
5. If criteria are incommensurable: run MCDA (P5) with sensitivity sweep.
6. If a spike is proposed: compute EVPI (P4) first; cap the spike at EVPI.
7. Record the full rationale, probability estimates, weight assumptions,
   and reversal conditions in the ADR.
```

---

## Sources

Decision theory foundations (canonical sources — do not substitute practitioner summaries for these):

- von Neumann, J. and Morgenstern, O. (1944/1947). *Theory of Games and Economic Behavior*. Princeton University Press. — Expected utility axioms and vNM theorem.
- Savage, L. J. (1954). *The Foundations of Statistics*. Wiley. — Minimax regret; subjective probability.
- Raiffa, H. and Schlaifer, R. (1961). *Applied Statistical Decision Theory*. Harvard University Press. — EVPI, EVSI, Bayesian decision.
- Howard, R. A. (1966). "Information Value Theory." *IEEE Transactions on Systems Science and Cybernetics* 2(1). — VoI formalisation.
- Pratt, J. W. (1964). "Risk Aversion in the Small and in the Large." *Econometrica* 32(1–2). — CARA/CRRA utility functions, certainty equivalent.
- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill. — AHP weight elicitation for MCDA.
- Dixit, A. K. and Pindyck, R. S. (1994). *Investment under Uncertainty*. Princeton University Press. — Real options; option to defer, expand, abandon.
- Trigeorgis, L. (1996). *Real Options: Managerial Flexibility and Strategy in Resource Allocation*. MIT Press. — Compound options; stage-gate applications.
- Hadar, J. and Russell, W. R. (1969). "Rules for Ordering Uncertain Prospects." *American Economic Review* 59(1). — First-order stochastic dominance.
- Levy, H. (1992). "Stochastic Dominance and Expected Utility: Survey and Analysis." *Management Science* 38(4). — FSD/SSD dominance conditions.

Architecture decision records:

- Nygard, M. (2011). "Documenting Architecture Decisions." https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions — ADR format origin.
- Bezos, J. (2015). Amazon Shareholder Letter — one-way vs. two-way door decision classification.

Cross-links within this skill:

- [adr-template.md](../assets/planning/adr-template.md) — The ADR template this reference extends with EU framing.
- [migration-modernization-guide.md](migration-modernization-guide.md) — Reversibility analysis for monolith-to-service migrations.
- [scalability-reliability-guide.md](scalability-reliability-guide.md) — SLO budgets and capacity decisions that benefit from risk-aversion framing (P6).
- [modern-patterns.md](modern-patterns.md) — Architecture pattern selection decisions that benefit from MCDA and stochastic dominance (P5, P11).

Foundation skill:

- [foundations-decision-theory](../../foundations-decision-theory/SKILL.md) — Per-primitive playbooks with full definitions, inputs, outputs, failure modes, and worked examples.
