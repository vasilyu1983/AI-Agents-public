---
description: Reliability-theory patterns for QA strategy — FMEA-driven risk-based test selection, FTA-guided fault injection coverage, hazard-function test prioritization across the release lifecycle, test-pyramid reliability allocation, Weibull-based regression cadence, and error-budget-aware test gating.
last_verified: 2026-05-02
status: stable
primitives:
  - foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md
  - foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md
  - foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md
  - foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md
  - foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md
  - foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md
  - foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md
  - foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md
  - foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md
  - foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md
  - foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md
---

# Reliability Theory Applied — QA Testing Strategy

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Why Reliability Theory for QA Strategy](#why-reliability-theory-for-qa-strategy)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — FMEA-Driven Risk-Based Test Selection](#p1--fmea-driven-risk-based-test-selection)
  - [P2 — FTA-Guided Fault Injection Coverage](#p2--fta-guided-fault-injection-coverage)
  - [P3 — Hazard-Function Test Prioritization Across the Release Lifecycle](#p3--hazard-function-test-prioritization-across-the-release-lifecycle)
  - [P4 — Test-Pyramid Reliability Allocation](#p4--test-pyramid-reliability-allocation)
  - [P5 — Weibull-Based Regression Test Cadence After a Fix](#p5--weibull-based-regression-test-cadence-after-a-fix)
  - [P6 — Error-Budget-Aware Test Gating](#p6--error-budget-aware-test-gating)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Uniform Coverage Ignoring Severity Distribution](#a1--uniform-coverage-ignoring-severity-distribution)
  - [A2 — Fault Injection Without MCS Prioritization](#a2--fault-injection-without-mcs-prioritization)
  - [A3 — Static Suite Composition Across the Bathtub Curve](#a3--static-suite-composition-across-the-bathtub-curve)
  - [A4 — RPN-Gated Release Without Residual-Risk Check](#a4--rpn-gated-release-without-residual-risk-check)
- [Recipe Catalog](#recipe-catalog)
  - [R1 — Pre-Release FMEA-to-Test-Plan Translation](#r1--pre-release-fmea-to-test-plan-translation)
  - [R2 — FTA Minimal-Cut-Set Fault Injection Sprint](#r2--fta-minimal-cut-set-fault-injection-sprint)
  - [R3 — Error-Budget Gate with Weibull Regression Cadence](#r3--error-budget-gate-with-weibull-regression-cadence)
- [Cross-References](#cross-references)

---

## Why Reliability Theory for QA Strategy

Test strategy decisions are made under resource constraints: finite CI budget, finite engineering hours, finite risk appetite per release. Without a formal model of failure, the decisions default to intuition — "test what changed," "add E2E for anything critical," "rerun until green." These heuristics accumulate waste and leave the highest-impact failure modes uncovered.

Reliability theory provides the quantitative foundation that converts intuition into defensible decisions:

1. **FMEA** (Primitive 06) turns a component inventory into a ranked failure-mode list with RPN scores. That ranking directly maps to a prioritized test selection — the highest-RPN failure modes own the largest test investment before any line of test code is written.

2. **FTA** (Primitive 05) reveals the minimal cut sets — the smallest combinations of component failures that produce a top-level system failure. A fault injection suite built from MCS targets the exact failure combinations that matter, rather than injecting arbitrary chaos.

3. **Hazard functions** (Primitive 03) and the **bathtub curve** (Primitive 04) show that failure rates are not constant across a component's life. Tests that are correctly weighted at release time (infant mortality zone) need different emphasis from tests in the steady-state zone or wear-out zone. A static suite ignores this structure.

4. **Reliability allocation** (Primitive 11) makes the test-pyramid layer budget explicit: when the system-level reliability target is known, the required reliability of each layer (unit, integration, E2E) can be derived, not guessed. This prevents over-investment in E2E while the unit layer leaks.

5. **Weibull analysis** (Primitive 09) models time-to-failure distributions after a fix is deployed. The shape parameter β identifies whether a fix produced a reliability improvement, degradation, or introduced early-life failures — information that drives the post-fix regression cadence rather than a fixed "run the suite once."

6. **Error budgets** (Primitive 08) convert SLO targets into a concrete release gate: how much of the budget has this release cycle consumed, and does the remaining budget permit a deploy? The gate is quantitative and audit-traceable, not a team vote.

The goal is not to make QA mathematical for its own sake. It is to prevent the most expensive failure modes in test strategy: spending test budget on low-severity, high-detectability paths while the single-point-of-failure MCS goes untested; deploying into an exhausted error budget; and running the same regression suite regardless of where the system sits on the bathtub curve.

---

## Pattern Catalog

### P1 — FMEA-Driven Risk-Based Test Selection

**Problem.** Before a release, the team has more potential test scenarios than CI budget can cover. The selection is made informally — the author of the PR nominates their own test cases, or tests are selected by coverage percentage with no weighting by impact.

**Reliability framing.** FMEA (Primitive 06: `RPN = Severity × Occurrence × Detection`) produces a ranked failure-mode table. Risk-based test selection maps test cases to FMEA rows and allocates test effort proportionally to RPN. Failure modes with S = 9–10 receive test coverage regardless of overall RPN — a low-occurrence, easily-detected catastrophic failure mode can have RPN = 90 yet still demands a test because the severity score alone warrants coverage.

**Operationalization.**

Before the release sprint, run a scoped FMEA over the components touched by the release. Produce a worksheet with one row per failure mode: component, failure mode, effect on the system SLO, S/O/D scores, and RPN.

Group rows into three tiers:

- Tier 1 (RPN ≥ 150 or S ≥ 9): mandatory test coverage. These are the scenarios that block merge or deploy.
- Tier 2 (RPN 60–149 and S ≤ 8): included in the targeted batch suite run before the deploy gate.
- Tier 3 (RPN < 60 and S ≤ 6): tracked but not actively tested in this release cycle. Reviewed if the component's failure rate changes.

For each Tier-1 row, write a corresponding test case title, assign it to the smallest effective layer (unit → component → integration → E2E in that preference order), and mark it as a gate-blocking scenario.

**Test selection output.** A test-selection manifest linking each gate-blocking scenario to its FMEA row, the chosen layer, and the RPN that justified it. This manifest survives as release evidence.

**Derives from Primitive 06: FMEA.** The RPN formula and Tier thresholds are direct applications of the FMEA scoring model. Severity-gated coverage regardless of RPN implements the FMEA canonical guidance: "always review S = 9–10 items regardless of RPN."

---

### P2 — FTA-Guided Fault Injection Coverage

**Problem.** The team runs chaos/fault injection tests but the injected faults are chosen by what is easy to inject (single-node kills, network drops) rather than by what combinations actually produce the top-level failure. The suite misses common-cause failures and multi-component MCS while over-investing in already-redundant single-node faults.

**Reliability framing.** FTA (Primitive 05) produces minimal cut sets — the smallest sets of basic events whose joint occurrence produces the top event. An MCS of size 1 is a single point of failure: injecting it alone brings down the system. An MCS of size 2 requires two simultaneous or sequential events. An MCS of size 3 or more is typically low-risk and can be deprioritized.

**Operationalization.**

Define the top event precisely: not "system failure" but "checkout service returns 5xx for > 30 s." Build the fault tree from the checkout service dependency diagram, decomposing to basic events (individual service failure, database failure, network path failure, third-party API timeout).

Enumerate MCS using the MOCUS algorithm or a BDD tool. Rank MCS by probability using basic event failure rates from incident history or MTBF data (Primitive 01).

Map each MCS to a fault injection scenario:

- MCS size 1: single-fault injection. The system must survive or degrade gracefully. If it does not, this is a P0 reliability gap.
- MCS size 2: paired fault injection (inject both faults simultaneously). The system may fail at the top event — this is acceptable provided recovery time meets the MTTR target (Primitive 01).
- MCS size 3+: covered only in scheduled resilience tests, not in pre-release gates.

Assign fault injection scenarios to CI stages:

- MCS size-1 scenarios in the pre-merge smoke gate (must pass before merge).
- MCS size-2 scenarios in the deploy gate resilience suite.
- MCS size 3+ in the quarterly resilience sprint.

**Derives from Primitive 05: Fault Tree Analysis.** MCS enumeration and size-based prioritization are core FTA outputs. Importance measures (Birnbaum, Fussell-Vesely) from Primitive 05 rank which basic events to inject first when budget is constrained.

---

### P3 — Hazard-Function Test Prioritization Across the Release Lifecycle

**Problem.** The regression suite runs at the same depth and cadence regardless of whether the component is newly deployed (infant mortality zone), has been stable for months (constant-hazard zone), or is approaching end of support (wear-out zone). This wastes CI budget on stable components and underinvests in newly deployed ones.

**Reliability framing.** The hazard function h(t) (Primitive 03) is the instantaneous failure rate at time t given survival to time t. The bathtub curve (Primitive 04) divides a component's lifecycle into three zones:

- Early-life (infant mortality): h(t) decreasing. Defects from manufacturing or integration are present and cause high early failure rates.
- Useful life (constant hazard): h(t) ≈ λ (constant). Failures are random and memoryless.
- Wear-out: h(t) increasing. Accumulated degradation, technical debt, or dependency decay drives rising failure rates.

Each zone has a different optimal test strategy.

**Operationalization.**

Tag each service and component with its lifecycle zone using a deployment age heuristic:

- Early-life: deployed < 30 days ago, or a major rewrite deployed < 14 days ago.
- Useful life: deployed 30–365 days ago with a stable incident rate.
- Wear-out: deprecated component still in path, end-of-support dependency, or component with an increasing defect density trend over the last 90 days.

Apply zone-specific test strategies:

- Early-life: run the full targeted regression batch on every merge, include integration smoke on all dependency paths, and add observability assertions (Primitive 01 MTTR-derived: alert threshold at 2× historical p99). This is the highest test density zone.
- Useful life: run smoke plus changed-path tests on merge (using TIA or `jest --findRelatedTests`). Run full regression weekly. This is the steady-state density zone.
- Wear-out: add explicit degradation tests: does the component exceed its memory budget, does its latency trend upward under steady load, does its error rate exceed the historical mean by > 1 σ? These tests are not pass/fail on functionality but on drift metrics.

**Derives from Primitive 03: Hazard Functions and Primitive 04: Bathtub Curve.** Zone classification maps to h(t) shape: decreasing (early-life), flat (useful life), increasing (wear-out). Test density follows h(t) — highest investment where failure rate is highest.

---

### P4 — Test-Pyramid Reliability Allocation

**Problem.** The team chooses test-pyramid proportions (unit vs. integration vs. E2E) by convention ("lots of unit, some integration, few E2E") without connecting the proportions to the system's reliability target. The resulting pyramid may satisfy code coverage metrics while failing to deliver the required system-level availability.

**Reliability framing.** Reliability allocation (Primitive 11) solves the inverse problem: given a system-level reliability target R_system, what reliability R_i must each subsystem i achieve? The allocation can use equal apportionment, AGREE allocation (weighted by complexity and usage), or ARINC allocation (weighted by failure rate history).

In the test-pyramid context, each layer contributes to the probability of detecting failures before they reach production. The combined detection probability across layers must meet the release quality gate: P(defect escapes all layers) ≤ escape_rate_budget.

**Operationalization.**

State the system reliability target explicitly: for example, "production error rate ≤ 0.1% of requests per week" (derived from the SLO and error budget — Primitive 08).

Compute the required defect escape rate. If the expected defect injection rate from the release is D defects per deployment, the test pyramid must achieve:

```text
P(escape) ≤ escape_budget / D
```

Allocate detection responsibility across layers. As a starting point, use AGREE-style allocation weighted by layer efficiency (unit tests catch logic defects cheaply; E2E tests catch integration failures expensively but exhaustively at the system level):

- Unit layer: targets logic and invariant defects. Allocate detection share proportional to the fraction of defects that are pure logic failures (typically 40–60% of the defect taxonomy from FMEA Tier-1 rows with low integration-surface scores).
- Integration layer: targets boundary and dependency defects. Allocate detection share proportional to defects with an integration-surface FMEA score.
- E2E layer: targets cross-service journey defects. Allocate only the residual escape budget. If unit + integration allocation already meets the budget, E2E scope can be reduced to critical-journey smoke only.

Track the allocation in the test-strategy manifest. When a production defect escapes the pyramid, audit which layer failed to detect it and adjust that layer's allocation, not the total coverage number.

**Derives from Primitive 11: Reliability Allocation and Primitive 10: System Reliability.** The series-system reliability model (Primitive 10: R_system = ∏ R_i) maps directly to the multi-layer detection model. Each layer is a component in the detection chain, and the product of detection probabilities must meet the system-level escape budget.

---

### P5 — Weibull-Based Regression Test Cadence After a Fix

**Problem.** After a production defect is fixed and deployed, the team runs the regression suite once, sees green, and returns to normal cadence. But some fixes introduce early-life failures (the fix changed adjacent code, a new code path is exercised for the first time under production load) or fail to actually improve the failure rate.

**Reliability framing.** Weibull analysis (Primitive 09) fits a two-parameter distribution to time-to-failure data: the shape parameter β determines whether the failure rate is decreasing (β < 1: early-life), constant (β ≈ 1: random), or increasing (β > 1: wear-out). After a fix is deployed, tracking the post-fix failure rate allows β estimation — and β < 1 in the post-fix window indicates the fix introduced an early-life failure pattern that warrants intensified short-term regression.

**Operationalization.**

Collect post-fix failure events. Use CI test failures, production error-rate spikes on the repaired component, and support signals. Track events in the window [deploy + 0, deploy + 72 h] at hourly resolution.

Fit a Weibull distribution to the inter-failure times or to the event count per hour using maximum likelihood estimation:

```bash
# Using scipy in Python
from scipy.stats import weibull_min
import numpy as np

# hours_to_failure: array of observed hours-to-failure events
params = weibull_min.fit(hours_to_failure, floc=0)
beta, loc, eta = params  # shape, location, scale
```

Interpret β:

- β < 0.9: early-life pattern. Run the full regression batch at 4 h, 24 h, and 72 h post-deploy. Do not reduce to smoke-only until β stabilizes above 1.0 in an updated fit at the 72 h mark.
- 0.9 ≤ β ≤ 1.1: constant-hazard. Return to normal weekly cadence.
- β > 1.1: wear-out signal on the fixed component. Escalate: the fix may have introduced technical debt that increases failure rate under accumulating load. Add a degradation test (latency trend assertion) to the nightly suite.

Document the β estimate in the post-fix retrospective alongside the MTBF change (Primitive 01): `MTBF_after / MTBF_before`. A ratio > 1.2 with β in the constant-hazard range confirms a successful, stable fix.

**Derives from Primitive 09: Weibull Analysis.** β estimation and the three-regime interpretation are direct applications of the Weibull shape-parameter model. The cadence thresholds (4 h, 24 h, 72 h) are derived from the infant mortality window implied by β < 1 distributions, where the hazard rate declines rapidly in the first few characteristic life fractions.

---

### P6 — Error-Budget-Aware Test Gating

**Problem.** Release gates are binary: all required tests pass → deploy. But a release that passes all tests may still consume the remaining error budget, leaving no headroom for the next deploy or for an unplanned incident. The gate does not account for the reliability state of the system at deploy time.

**Reliability framing.** Error budgets (Primitive 08) convert an SLO into a quantitative allowance: `error_budget = 1 − SLO_target`. Consumed budget is the observed error rate minus the SLO target, integrated over time. Budget remaining at deploy time constrains how much reliability risk the release is permitted to carry.

**Operationalization.**

At deploy decision time, compute the current error budget state:

```text
budget_remaining = (1 − SLO_target) × window_hours − cumulative_downtime_minutes / 60
```

For example, with a 99.9% SLO over a 30-day window (720 h) and 38 min of downtime consumed:

```text
budget_remaining = (0.001 × 720 h) − (38/60 h)
               = 0.72 h − 0.633 h
               = 0.087 h ≈ 5.2 minutes remaining
```

Apply a tiered gate based on budget remaining:

- Budget > 50%: standard gate. Required tests passing is sufficient to deploy.
- Budget 20–50%: elevated gate. All Tier-1 FMEA scenarios from P1 must pass, plus the MCS size-2 fault injection scenarios from P2. A FMEA re-score of changed components is required if the last FMEA is > 14 days old.
- Budget 10–20%: restricted deploy. Requires explicit sign-off from an on-call engineer, full E2E deploy-gate suite passing, and a documented risk statement citing current budget and projected consumption of the release.
- Budget < 10%: deploy freeze. Only reliability-improvement patches may deploy. Each exception requires a written justification that the patch is expected to restore budget, with a rollback plan and a post-deploy MTTR target (Primitive 01).

Publish budget state in the CI pipeline as a named check: "Error Budget Gate: 87 min / 432 min remaining (20%). Elevated gate active." This makes the gate visible in the PR timeline alongside functional test results.

**Derives from Primitive 08: Error Budgets.** The budget calculation formula and the concept of using budget depletion to trigger gate escalation are direct applications of the error budget model. The tiered gate thresholds (50%, 20%, 10%) mirror the SRE error budget policy patterns from the reliability literature.

---

## Anti-Pattern Catalog

### A1 — Uniform Coverage Ignoring Severity Distribution

**Description.** The team measures test coverage by percentage of lines, branches, or scenarios without weighting by failure mode severity. A 90% statement coverage metric is treated as evidence of adequate risk management.

**Reliability diagnosis.** Coverage metrics aggregate all code paths with equal weight. FMEA (Primitive 06) shows that failure modes with S = 1 (minor inconvenience) and S = 9 (data loss) are not equivalent. A test suite that achieves 90% coverage by exercising many low-severity paths while missing two high-severity paths (because they are harder to exercise) has the wrong shape of coverage entirely.

**Primitive misapplied.** Primitive 06 (FMEA) is either not run, or run but its severity dimension is discarded. The RPN rank is used to claim all failures are equal, violating FMEA's own canonical guidance: always cover S ≥ 9 rows regardless of RPN.

**How it manifests.** A critical authentication bypass (S = 10, O = 2, D = 7, RPN = 140) sits below the coverage threshold because the code path requires a specific JWT edge case to trigger. Meanwhile, 200 low-severity format-validation tests push the coverage percentage above target. The bypass ships to production.

**Fix.** Separate coverage tracking by severity tier. Report: "Tier-1 failure modes covered: 14/14 (100%). Tier-2 covered: 28/35 (80%). Overall line coverage: 88%." Gate on Tier-1 coverage = 100%, not on overall percentage. See P1 for the FMEA-to-test-selection mapping.

**Derives from Primitive 06: FMEA misapplied** — the severity dimension is ignored, reducing FMEA to a checkbox activity rather than a risk-ranking tool.

---

### A2 — Fault Injection Without MCS Prioritization

**Description.** The chaos engineering suite injects faults by rotating through a catalog of single-node kills and network partitions without reference to the fault tree. The injected faults are chosen by what the chaos tool makes easy, not by what the FTA shows is likely to produce the top event.

**Reliability diagnosis.** FTA (Primitive 05) identifies that many single-node failures are already handled by redundancy — their MCS has size 2 or more. Injecting them in isolation tests the redundancy mechanism but not the actual top-event risk. Meanwhile, the true SPOF (MCS of size 1) or the common-cause failure (two nodes sharing a single power domain) may never be tested because it requires a non-trivial simultaneous injection.

**Primitive misapplied.** Primitive 05 (FTA) is either skipped, or used only to draw a diagram and not to enumerate MCS and assign injection priorities.

**How it manifests.** The team demonstrates "we chaos test every week" but the quarterly failure involves a network partition on both read replicas simultaneously (MCS size 2 with a shared network path). This MCS was in the fault tree but never injected because the tool's default test list only kills one replica at a time.

**Fix.** Build the fault injection catalog directly from the MCS enumeration. For each MCS, write an explicit injection script that activates all events in the MCS simultaneously or in sequence within the failure propagation window. See P2 and R2 for the full procedure.

**Derives from Primitive 05: FTA misapplied** — MCS enumeration is skipped, leaving the top-down analytical output unused and reverting to ad hoc injection.

---

### A3 — Static Suite Composition Across the Bathtub Curve

**Description.** The regression suite depth and cadence are fixed at project inception and never adjusted for component lifecycle phase. A newly deployed service and a two-year-old stable service run the same suite at the same frequency.

**Reliability diagnosis.** The bathtub curve (Primitive 04) and hazard functions (Primitive 03) show that failure rates are not constant across a component's life. Early-life components have a decreasing hazard function — the first weeks of operation surface latent integration defects that a fixed-cadence suite may miss between runs.

**Primitive misapplied.** Primitives 03 and 04 are used to describe system behavior in documentation but not operationalized in the test schedule. The implication — that test intensity should track the hazard function — is never drawn.

**How it manifests.** A service rewrite is deployed on Monday. The regression suite runs on its normal weekly cadence. An early-life integration defect (a subtle JWT claim handling difference between old and new implementations) surfaces in production on Thursday — between cadence windows. The defect would have been caught by a 24 h post-deploy regression run.

**Fix.** Tag components by lifecycle zone and apply zone-specific cadence as described in P3. The early-life zone warrants daily regression; the useful-life zone warrants weekly; the wear-out zone warrants drift monitoring. Review zone tags at each sprint planning cycle.

**Derives from Primitives 03 and 04 misapplied** — the hazard rate model is acknowledged but not translated into a test scheduling rule, leaving cadence decisions at constant frequency regardless of h(t) shape.

---

### A4 — RPN-Gated Release Without Residual-Risk Check

**Description.** The team uses FMEA RPN thresholds as release gates: "no open Tier-1 items" means the release is cleared. But the gate is checked only against pre-mitigation RPN, and residual RPN (after mitigations are applied) is never recomputed. Alternatively, mitigations are marked "completed" when the action is taken rather than when the residual risk is measured.

**Reliability diagnosis.** FMEA (Primitive 06) produces both an initial RPN and a post-mitigation residual RPN. The checkout example in Primitive 06 shows a Payment API timeout moving from RPN 270 to projected residual RPN 90 after adding a circuit breaker and idempotency key. A gate that clears on initial RPN 270 being "resolved" without verifying the residual does not know whether the mitigation actually worked.

**Primitive misapplied.** Primitive 06 (FMEA) is used only for initial ranking and mitigation planning. The residual-RPN column of the FMEA worksheet remains unfilled, and the gate condition is "mitigation action assigned" rather than "residual RPN measured and below threshold."

**How it manifests.** A circuit breaker is added to the payment path (mitigation action: complete). The FMEA item is marked cleared. The circuit breaker is misconfigured with a timeout shorter than the payment provider's p95 response time, causing false-positive opens. Residual O is higher than projected, and residual D is lower because the misconfiguration is not monitored. The actual residual RPN is higher than the initial RPN.

**Fix.** Require a measured residual-RPN recompute before closing any Tier-1 FMEA row. The measurement must come from a test result, not from the engineer's judgment. For a circuit breaker mitigation, the test is: inject a payment timeout at the known p99 latency and verify the breaker opens only on the configured threshold, not earlier. See R1 step 5 for the residual-risk verification pattern.

**Derives from Primitive 06: FMEA misapplied** — the residual-risk column is the critical output of FMEA iteration but is treated as optional bookkeeping rather than a gate condition.

---

## Recipe Catalog

### R1 — Pre-Release FMEA-to-Test-Plan Translation

**When to use.** Planning the test scope for a release that touches a high-risk component or introduces a new integration boundary. Use when the team needs a defensible, traceable test plan rather than coverage-percentage targets.

**Steps.**

**Step 1: Scope the FMEA to the release changeset.**

List every component touched by the release (from the PR diff or ticket scope). For each component, list its functions and draft failure modes. Time-box this to 90 minutes for a typical sprint release.

```bash
# Pull changed files for the release branch
git diff main...HEAD --name-only | sort -u

# Cross-reference with service ownership map to identify component scope
```

**Step 2: Score each failure mode.**

Fill in the FMEA worksheet for each failure mode. Score S, O, D on 1–10. Anchor O scores to observed failure rates from incident history where available (Primitive 01 MTBF data). Do not score O by intuition alone.

| Component | Failure Mode | Effect | S | O | D | RPN |
|---|---|---|---|---|---|---|
| Auth service | KMS timeout | All API auth fails | 9 | 2 | 5 | 90 |
| Order DB | Replication lag > 500ms | Stale reads, duplicate orders | 8 | 3 | 4 | 96 |
| Payment API | Timeout under load | Silent order failure | 9 | 6 | 5 | 270 |

**Step 3: Tier and assign test cases.**

For each row, classify the tier (Tier 1: RPN ≥ 150 or S ≥ 9; Tier 2: RPN 60–149; Tier 3: < 60) and assign a test case to the smallest effective layer. Write the test case title in the worksheet.

```text
Payment API timeout (RPN 270, Tier 1):
  → Integration test: inject 5 s timeout on payment provider mock;
    assert circuit breaker opens; assert idempotency key prevents duplicate charge.
  → Gate: merge-blocking.

Order DB replication lag (RPN 96, Tier 2):
  → Integration test: simulate lag > 500 ms on read replica;
    assert application-layer idempotency check fires.
  → Gate: deploy-gate batch.
```

**Step 4: Map gate assignments to CI pipeline stages.**

- Tier-1 tests: added to the PR smoke gate. Failing any Tier-1 test blocks merge.
- Tier-2 tests: added to the deploy gate targeted batch. Failing blocks the deploy.
- Tier-3 tests: tracked in the weekly regression run. Failures raise a ticket but do not block.

**Step 5: Verify residual RPN after mitigations.**

After each Tier-1 mitigation action is implemented, recompute S, O, D and recalculate residual RPN. Close the FMEA row only when measured residual RPN < 100 and S ≤ 7, or when S ≥ 9 items have explicit sign-off from the release owner.

```bash
# In your CI pipeline, assert gate tiers pass before proceed
# Example: tag tests with tier in pytest markers
pytest -m "tier1" --junitxml=tier1-results.xml
# Gate: exit code 0 required for merge
pytest -m "tier2" --junitxml=tier2-results.xml
# Gate: exit code 0 required for deploy
```

**Output.** FMEA worksheet with test-case column populated, tier tags, gate assignments, and residual RPN after mitigations. This worksheet is the release evidence for risk-based test selection.

**Verify.** Every S ≥ 9 row has a corresponding test case. Every Tier-1 test is tagged as gate-blocking in CI. Residual RPN column is filled for all Tier-1 rows before deploy.

---

### R2 — FTA Minimal-Cut-Set Fault Injection Sprint

**When to use.** Before a major release, a new dependency integration, or after a production incident involving a multi-component failure. Run as a focused 1–2 day sprint with the platform and QA engineers.

**Steps.**

**Step 1: Define the top event precisely.**

Write the top event as a measurable system state with a threshold. Do not use "service failure."

```text
Top event: "Checkout service returns HTTP 5xx on > 1% of requests
            for a sustained window of > 60 seconds."
```

**Step 2: Build the fault tree.**

From the checkout service dependency diagram, decompose to basic events. Use AND gates for failure modes that require joint occurrence of independent components, and OR gates where any single failure produces the intermediate event.

```text
Top event: Checkout 5xx > 60 s
└─ OR
   ├─ Payment provider unavailable (MCS size 1 if no fallback)
   ├─ Order DB primary AND replica both unavailable (MCS size 2)
   │  ├─ Primary DB failure  [λ = 0.003/day]
   │  └─ Replica DB failure  [λ = 0.003/day]
   └─ Auth service AND JWT cache both unavailable (MCS size 2)
      ├─ Auth service failure [λ = 0.002/day]
      └─ JWT cache failure    [λ = 0.01/day]
```

**Step 3: Enumerate MCS and rank by probability.**

```python
# Compute MCS probabilities (rare-event approximation)
lambda_primary_db = 0.003   # failures/day
lambda_replica_db = 0.003
lambda_auth       = 0.002
lambda_jwt_cache  = 0.010
lambda_payment    = 0.0005  # single ISP/provider path

p_mcs_db      = lambda_primary_db * lambda_replica_db  # 9e-6/day
p_mcs_auth    = lambda_auth * lambda_jwt_cache          # 2e-5/day
p_mcs_payment = lambda_payment                          # 5e-4/day (SPOF)

# Payment provider SPOF dominates by 25×
```

**Step 4: Write a fault injection test per MCS.**

For each MCS, create a test that activates all basic events in the MCS and verifies the system response against the top event definition.

```python
# MCS size-1: payment provider unavailable
def test_payment_provider_spof(checkout_service, payment_mock):
    payment_mock.set_failure(mode="timeout", duration_seconds=90)
    response = checkout_service.post("/checkout", order_payload)
    # System should degrade gracefully — not hit top event
    assert response.status_code != 500
    # OR: if degradation is acceptable, assert it is logged and surfaced
    assert checkout_service.metrics.error_rate_pct < 1.0

# MCS size-2: both DB replicas unavailable simultaneously
def test_db_primary_and_replica_failure(checkout_service, db_primary, db_replica):
    with db_primary.pause(), db_replica.pause():
        time.sleep(5)  # allow health checks to detect
        response = checkout_service.post("/checkout", order_payload)
    # Top event allowed — verify MTTR recovery starts within SLA
    assert checkout_service.recovery_time_seconds <= 120
```

**Step 5: Assign injection tests to CI stages.**

- MCS size-1 injections → pre-merge smoke gate (must pass; any SPOF that causes the top event is a P0 finding).
- MCS size-2 injections → deploy gate resilience suite.
- Document findings as reliability gaps in the FMEA worksheet (feeds back to P1).

**Output.** Fault injection test suite with one test per MCS, CI stage assignments, and a findings report listing any MCS that produced the top event. For each finding: the MCS, the observed top-event duration, and the recommended mitigation (redundancy, circuit breaker, fallback path).

**Verify.** Every MCS size-1 has a passing test (or an open P0 ticket). Every MCS size-2 has a test that validates MTTR ≤ the target. FTA probability rank is reflected in CI stage assignments.

---

### R3 — Error-Budget Gate with Weibull Regression Cadence

**When to use.** At every release decision point. This recipe combines the P6 error-budget gate with the P5 Weibull-based post-deploy regression cadence into a single deploy-and-monitor workflow.

**Steps.**

**Step 1: Compute current error budget state before the deploy.**

```bash
# Fetch SLO window metrics from monitoring system
# Example using Prometheus / Grafana query pattern

SLO_TARGET=0.999          # 99.9%
WINDOW_HOURS=720          # 30-day rolling window
DOWNTIME_MINUTES=$(curl -s "$PROMETHEUS_URL/api/v1/query" \
  --data-urlencode 'query=sum_over_time(slo_downtime_minutes[30d])' \
  | jq '.data.result[0].value[1]' | tr -d '"')

BUDGET_REMAINING_HOURS=$(echo "scale=3; (1 - $SLO_TARGET) * $WINDOW_HOURS \
  - $DOWNTIME_MINUTES / 60" | bc)

echo "Error budget remaining: ${BUDGET_REMAINING_HOURS} hours"

# Determine gate tier
if (( $(echo "$BUDGET_REMAINING_HOURS > 0.5 * (1 - $SLO_TARGET) * $WINDOW_HOURS" | bc -l) )); then
  echo "Gate: STANDARD — functional tests required"
elif (( $(echo "$BUDGET_REMAINING_HOURS > 0.1 * (1 - $SLO_TARGET) * $WINDOW_HOURS" | bc -l) )); then
  echo "Gate: ELEVATED — Tier-1 FMEA + MCS-2 fault injection required"
elif (( $(echo "$BUDGET_REMAINING_HOURS > 0" | bc -l) )); then
  echo "Gate: RESTRICTED — explicit sign-off required"
else
  echo "Gate: FREEZE — reliability patches only"
  exit 1
fi
```

**Step 2: Run the gate-appropriate test suite.**

Under elevated gate, execute Tier-1 FMEA tests and MCS size-2 fault injections from R1 and R2 in addition to the standard suite. Emit a gate summary artifact:

```text
Error Budget Gate Summary
  SLO target:        99.9%
  Window:            30 days (720 h)
  Total budget:      43.2 min  ((1 - 0.999) x 720 h x 60 min/h)
  Budget consumed:   38 min    (88.0% of total budget)
  Budget remaining:  5.2 min   (12.0% of total budget)
  Gate tier:         RESTRICTED (12.0% falls in the 10-20% band)
  Required suites:   smoke, tier1-fmea, contract, full E2E deploy-gate suite
  Sign-off:          on-call engineer required, risk statement attached
  All suites:        PASS
  Deploy:            APPROVED WITH RESTRICTED GATE
```

Note the units: the 720-hour window is the *measurement period*, not the *budget size*. The budget size is `(1 - SLO_target) x window_hours`, converted to minutes here for readability. Confusing the window length with the budget total is a common gate-math mistake — always compute the budget from the SLO gap, never from the window size directly.

**Step 3: Deploy and start the Weibull monitoring window.**

Record the deploy timestamp. For the next 72 hours, collect hourly failure counts for the changed components from production telemetry and CI post-deploy runs.

**Step 4: Fit Weibull β at the 4 h, 24 h, and 72 h marks.**

```python
from scipy.stats import weibull_min
import numpy as np

# hours_to_failure: list of hours elapsed at each failure event
# (fill from PagerDuty/monitoring alert timestamps minus deploy time)
def estimate_weibull_beta(hours_to_failure):
    if len(hours_to_failure) < 3:
        return None, "insufficient data"
    params = weibull_min.fit(hours_to_failure, floc=0)
    beta, _, _ = params
    return beta, params

beta_4h,  _ = estimate_weibull_beta(failures_by_4h)
beta_24h, _ = estimate_weibull_beta(failures_by_24h)
beta_72h, _ = estimate_weibull_beta(failures_by_72h)

# Interpret and schedule cadence
if beta_4h is not None and beta_4h < 0.9:
    print("Early-life signal detected (β={:.2f}). Run full regression at 24h.".format(beta_4h))
elif beta_72h is not None and 0.9 <= beta_72h <= 1.1:
    print("Stable fix confirmed (β={:.2f}). Return to weekly cadence.".format(beta_72h))
elif beta_72h is not None and beta_72h > 1.1:
    print("Wear-out signal (β={:.2f}). Add drift tests to nightly suite.".format(beta_72h))
```

**Step 5: Report β and budget update to the deploy record.**

After the 72 h window closes, append to the deploy record:

```text
Post-deploy Weibull Report (72 h window)
  β estimate:        0.94 (constant-hazard zone)
  MTBF change:       +34% vs pre-fix baseline
  Error budget delta: −2 min consumed in window
  Cadence decision:  return to standard weekly regression
  Fix status:        CONFIRMED STABLE
```

**Output.** A deploy record combining: pre-deploy error budget state and gate tier, test suite results, post-deploy β estimate, MTBF delta, and cadence decision. This record is the traceability artifact connecting reliability theory to QA execution.

**Verify.** Budget remaining is computed and the correct gate tier is applied. β is estimated at least once before returning to normal cadence. Drift tests are added to the nightly suite if β > 1.1.

---

## Cross-References

**Foundation skill:**
[`foundations-reliability-theory/SKILL.md`](../../foundations-reliability-theory/SKILL.md) — canonical primitive definitions for all 11 reliability primitives referenced in this file.

**Individual primitives:**

| Primitive | File |
|---|---|
| 01 MTBF/MTTR | [`01-mtbf-mttr.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) |
| 02 Availability Formulas | [`02-availability-formulas.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) |
| 03 Hazard Functions | [`03-hazard-functions.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md) |
| 04 Bathtub Curve | [`04-bathtub-curve.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) |
| 05 Fault Tree Analysis | [`05-fault-tree-analysis.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) |
| 06 FMEA | [`06-fmea.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) |
| 07 Redundancy Math | [`07-redundancy-math.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) |
| 08 Error Budgets | [`08-error-budgets.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) |
| 09 Weibull Analysis | [`09-weibull-analysis.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md) |
| 10 System Reliability | [`10-system-reliability.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md) |
| 11 Reliability Allocation | [`11-reliability-allocation.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) |

**Sibling applied recipes in qa-testing-strategy:**

- [`causal-inference-applied.md`](../../qa-debugging/references/causal-inference-applied.md) — Counterfactual RCA, DiD, synthetic control, and mediation for post-mortems. Complements this file: use reliability theory to prioritize what to test before production; use causal inference to attribute what failed after production.
- [`chaos-resilience-testing.md`](chaos-resilience-testing.md) — Chaos engineering execution patterns. R2 in this file generates the MCS-ranked fault list; `chaos-resilience-testing.md` covers the tooling (Chaos Monkey, Litmus, Gremlin) for executing that list.
- [`production-testing-and-shift-right.md`](production-testing-and-shift-right.md) — Synthetic monitoring, dark launches, feature flag rollouts, and MTTR SLO. The error budget state from P6/R3 feeds directly into the release gate patterns in this reference.
- [`quality-metrics-dashboard.md`](quality-metrics-dashboard.md) — Metrics, dashboards, and mutation coverage. β estimates from P5 and FMEA RPN trends from P1 are metrics candidates for the quality dashboard.
