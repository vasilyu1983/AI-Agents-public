---
description: Reliability-theory primitives applied to QA resilience work — SLO error-budget burn-rate alerts, chaos steady-state hypothesis design, fault-tree blast-radius scoping, game-day blueprints, MTTR-driven runbook design, and active-replica probe patterns.
last_verified: 2026-07-11
status: stable
---

# Reliability Theory Applied to QA Resilience

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Companion to [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md). Applies its 11 primitives to the concrete testing and validation work that sits inside qa-resilience: setting multi-window burn-rate alerts, designing chaos steady-state hypotheses, scoping blast radius via fault trees, rehearsing cascading failures in game days, building MTTR-driven runbooks, and verifying active replicas actually serve traffic._

## Table of Contents

- [Why Reliability Theory for Resilience Testing](#why-reliability-theory-for-resilience-testing)
- [Patterns](#patterns)
  - [P1 — SLO Error-Budget Burn-Rate Alerts (Multi-Window, Multi-Burn)](#p1--slo-error-budget-burn-rate-alerts-multi-window-multi-burn)
  - [P2 — Steady-State Hypothesis Design for Chaos Experiments](#p2--steady-state-hypothesis-design-for-chaos-experiments)
  - [P3 — Fault-Tree Decomposition for Blast-Radius Scoping](#p3--fault-tree-decomposition-for-blast-radius-scoping)
  - [P4 — Game-Day Blueprint for Cascading-Failure Rehearsal](#p4--game-day-blueprint-for-cascading-failure-rehearsal)
  - [P5 — MTTR-Driven Runbook Design](#p5--mttr-driven-runbook-design)
  - [P6 — Redundancy Verification via Active-Replica Probes](#p6--redundancy-verification-via-active-replica-probes)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Chaos Experiment Without a Steady-State Hypothesis](#a1--chaos-experiment-without-a-steady-state-hypothesis)
  - [A2 — Binary Up/Down SLOs That Ignore Partial Failure](#a2--binary-updown-slos-that-ignore-partial-failure)
  - [A3 — Untested Runbooks](#a3--untested-runbooks)
  - [A4 — MTTR Optimisation That Hides Recurring Root Causes](#a4--mttr-optimisation-that-hides-recurring-root-causes)
  - [A5 — Error Budget Measured in a Single Long Window](#a5--error-budget-measured-in-a-single-long-window)
- [Recipes](#recipes)
  - [R1 — Setting a 99.9% SLO with Multi-Window Burn-Rate Alerts](#r1--setting-a-999-slo-with-multi-window-burn-rate-alerts)
  - [R2 — Designing a Region-Failover Game Day](#r2--designing-a-region-failover-game-day)
  - [R3 — Building a Fault Tree for a Cascaded Agent Stack](#r3--building-a-fault-tree-for-a-cascaded-agent-stack)
- [Cross-References](#cross-references)

---

## Why Reliability Theory for Resilience Testing

Resilience testing without a reliability-theory grounding produces one of two failure modes: experiments that are so cautious they detect nothing, or experiments that fire without a falsifiable hypothesis and leave the team arguing about what the results mean.

Reliability primitives resolve both problems:

| QA resilience gap | Reliability-theory fix |
|---|---|
| No quantitative pass/fail criterion for a chaos run | Error budget (#8): derive the burn-rate threshold that constitutes an abort signal |
| Chaos scope set by gut feel | Fault tree (#5): enumerate minimal cut sets; limit blast radius to a single MCS per run |
| Game day ends without knowing if RTO was met | MTTR decomposition (#1): measure T_detect + T_diagnose + T_remediate + T_verify against the RTO bound |
| Replica count assumed to provide HA but never verified | Redundancy math (#7): active-replica probe confirms coverage c, not just replica count n |
| SLO breaches invisible until the weekly review | Multi-window burn rate (#8): 1-hour + 6-hour windows catch fast burns before the 30-day budget is consumed |
| Runbook execution time guessed from happy-path walk-throughs | MTTR sampling (#1): use 90th-percentile incident MTTR, not mean; include detection-to-restore, not just restore duration |

Foundation primitives live in `../../foundations-reliability-theory/assets/templates/reliability-theory/`. Refer to them for derivations; this file applies them.

---

## Patterns

### P1 — SLO Error-Budget Burn-Rate Alerts (Multi-Window, Multi-Burn)

**Primitive anchors**: [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md)

**The problem.** A single 30-day burn-rate alert fires too late: a service can exhaust half its monthly error budget in a 4-hour incident that a 30-day alert will not catch until the budget is already gone. A 1-hour alert fires too often on transient blips. Multi-window, multi-burn-rate alerting solves both: fast windows catch fast burns; slow windows confirm sustained degradation.

**Burn-rate concept.** A burn rate of 1× means the error budget is consumed at exactly the rate that would exhaust it at end of the 30-day window. A burn rate of 14.4× means the budget will be exhausted in 30 days / 14.4 = 2.08 days if the current error rate continues.

**Alert matrix (Google SRE Workbook, Chapter 5):**

```
SLO: 99.9% over 30 days
Monthly budget: 0.1% × 43,200 min (30-day month, 30 × 24 × 60) = 43.2 min

Window 1 (fast / pager):
  Burn rate threshold: 14.4×
  Alert window: 1 hour
  Budget consumed if fires: 14.4 × (1/720) × 100% = 2% of monthly budget
  Action: page; may be a real incident

Window 2 (slow / ticket):
  Burn rate threshold: 6×
  Alert window: 6 hours
  Budget consumed if fires: 6 × (6/720) × 100% = 5% of monthly budget
  Action: ticket; sustained degradation

Window 3 (audit / weekly):
  Burn rate threshold: 1×
  Alert window: 30 days
  Budget consumed if fires: entire budget
  Action: monthly reliability review
```

**Burn-rate formula:**

```
burn_rate = (error_rate_observed / (1 - SLO_target))

Remaining budget:
  budget_remaining = (1 - SLO_target) × window_minutes - bad_minutes_so_far

Projected exhaustion time:
  t_exhaust = budget_remaining / (burn_rate × (1 - SLO_target) × 60)
```

**Alert implementation in Prometheus / OTEL:**

```yaml
# 1-hour fast burn
- alert: SLOFastBurn
  expr: |
    (
      sum(rate(http_requests_total{code=~"5.."}[1h])) /
      sum(rate(http_requests_total[1h]))
    ) > (14.4 * (1 - 0.999))
  for: 2m
  labels:
    severity: pager
  annotations:
    summary: "Fast burn rate exceeds 14.4x SLO budget consumption"

# 6-hour slow burn
- alert: SLOSlowBurn
  expr: |
    (
      sum(rate(http_requests_total{code=~"5.."}[6h])) /
      sum(rate(http_requests_total[6h]))
    ) > (6 * (1 - 0.999))
  for: 15m
  labels:
    severity: ticket
```

**Integration with chaos experiments.** The burn-rate alert is both the abort criterion for a chaos run (if the fast-burn alert fires during the experiment, abort immediately) and the pass/fail signal (if the experiment completes with no burn-rate alert firing, the steady state was preserved).

---

### P2 — Steady-State Hypothesis Design for Chaos Experiments

**Primitive anchors**: [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md), [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md)

**The principle (Chaos Engineering, Basiri et al. 2016).** A chaos experiment is falsifiable only if the steady state is defined quantitatively before the experiment runs. "The system is healthy" is not a hypothesis. "The p99 latency of /checkout remains below 500 ms and the error budget burn rate stays below 1× during and for 5 minutes after the fault is injected" is a hypothesis.

**Hypothesis structure:**

```
Given: [normal operating conditions — traffic level, upstream health, time of day]
When: [fault injected — what, scope, duration]
Then: [these SLI/SLO metrics remain within these bounds]
  - SLI 1: error rate < threshold during fault window
  - SLI 2: p99 latency < threshold during fault window
  - SLI 3: error budget burn rate < abort threshold
  - SLI 4: [recovery metric] returns to baseline within T minutes of fault removal
Abort if: [burn-rate threshold or customer-impact signal]
```

**Deriving the steady-state bounds from reliability primitives:**

- Error rate bound = `1 - SLO_target` from primitive 08. If the SLO is 99.9%, the error rate threshold is 0.1%.
- Latency bound = p99 from the normal operating baseline, not from a capacity headroom calculation.
- Recovery time bound = MTTR target from primitive 01. If the RTO is 5 minutes, the recovery SLI must show return to baseline within 5 minutes.
- Abort criterion = fast burn rate threshold from P1 above.

**FMEA linkage.** Before writing the hypothesis, consult the FMEA worksheet (primitive 06) for the component under test. The failure mode being injected should appear in the FMEA. Its Severity × Occurrence × Detection = RPN tells you how much error budget the failure mode is expected to consume historically — and therefore how tight the abort threshold needs to be.

**Example hypothesis for a circuit breaker experiment:**

```
Experiment: "Circuit breaker prevents error cascade when payment-service is unhealthy"

Steady-state (baseline, 10-minute observation):
  - checkout error rate: < 0.05% (well inside 99.9% SLO)
  - checkout p99 latency: < 200 ms
  - payment circuit state: CLOSED

Fault: Set payment-service to return HTTP 503 for 100% of requests for 2 minutes.

Hypothesis (during fault):
  - checkout error rate: < 0.5% (circuit open, fallback active; budget burn < 5×)
  - checkout p99 latency: < 300 ms (fallback adds < 100 ms)
  - payment circuit state: OPEN within 30 seconds of fault start

Hypothesis (recovery, 5 minutes after fault removed):
  - checkout error rate: returns to < 0.05% within 3 minutes
  - payment circuit state: HALF_OPEN → CLOSED within 3 minutes

Abort criterion: checkout error rate > 1% for > 60 seconds (fast burn > 14.4×)
```

---

### P3 — Fault-Tree Decomposition for Blast-Radius Scoping

**Primitive anchors**: [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md), [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md)

**The blast-radius problem.** Chaos experiments that inject faults at the wrong layer can propagate beyond the intended scope and cause real user impact. Fault-tree analysis identifies which failure modes are isolated (confined to one component) and which are propagating (cascade through other components) before the experiment runs.

**FTA for blast-radius scoping:**

1. Define the top event: "User-visible checkout failure."
2. Draw the fault tree: enumerate intermediate events (payment unavailable, auth unavailable, database unavailable) connected by AND/OR gates.
3. Compute minimal cut sets (MCS):
   - Size-1 MCS: a single component whose failure alone triggers the top event. Injecting a fault here affects all users.
   - Size-2+ MCS: requires two or more simultaneous failures. More experiments can safely inject one component without cascading.
4. Use MCS sizes to scope the experiment:
   - Only inject faults into size-1 MCS components with explicit rollback plans and a reduced traffic percentage.
   - Prefer injecting into size-2+ MCS components first; they are safer for initial experiments.

**Blast-radius classification:**

```
Blast radius scope:
  CONTAINED   — fault is isolated to the injected component; no downstream effect
  DEGRADED    — fault activates a fallback path; some features impaired
  CASCADING   — fault propagates through MCS chain; top event likely

Acceptable experiment blast radii by environment:
  Non-production: any
  Staging:        CONTAINED or DEGRADED only
  Production:     CONTAINED only, with abort criterion wired
```

**Fussell-Vesely importance as experiment priority.** Prioritise chaos experiments on the components with the highest FV importance scores. FV importance ≈ `(1 - A_i) / (1 - A_system)`: high values mean a component contributes disproportionately to system downtime. Experimenting here has the highest information value.

**Example fault tree excerpt for a 3-tier web app:**

```
Top event: Checkout unavailable (OR)
  ├── API gateway fails (MCS size 1 — all traffic lost)
  ├── Auth service unavailable AND no cached tokens (MCS size 2)
  ├── Core service fails (MCS size 1 — all traffic lost)
  └── Database primary unavailable AND replica promotion fails (MCS size 2)

Blast radius for "kill one core service replica":
  MCS containing "core service replica 1 fails" has size 2
  (both replicas must fail for MCS to be satisfied)
  → Blast radius: DEGRADED (load shifts to replica 2)
  → Safe for staging; acceptable in production with traffic monitoring
```

---

### P4 — Game-Day Blueprint for Cascading-Failure Rehearsal

**Primitive anchors**: [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md), [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md)

**Purpose.** A game day validates that the team can execute recovery — not just that the system can fail gracefully. The technical failover is necessary but not sufficient; the human coordination, runbook clarity, and communication path must also be tested. Cascading-failure game days are specifically designed to exercise the scenario where a recovery action for one failure triggers a second failure.

**Game-day blueprint:**

```
Pre-game (T-2 weeks):
  [ ] Select the cascade scenario from the FTA MCS chain (P3)
  [ ] Define the steady-state hypothesis (P2)
  [ ] Identify participants: incident commander, operators, observers, abort owner
  [ ] Set abort criteria: burn-rate threshold + customer-impact signal
  [ ] Confirm rollback procedure for each injected fault
  [ ] Brief on-call rotation; notify stakeholders

Game day (T=0):
  [ ] Baseline: observe steady-state SLIs for 10 minutes; confirm hypothesis bounds
  [ ] Fault 1: inject first failure in the MCS chain; start timer
  [ ] T+N min: observe — does the first fallback activate within the expected window?
  [ ] Fault 2: inject second failure to trigger the cascade
  [ ] Observe: does the system degrade gracefully or does the top event fire?
  [ ] Recovery: remove faults; start recovery timer
  [ ] Measure: T_detect, T_diagnose, T_remediate, T_verify (from MTTR decomposition)

Post-game (T+1 day):
  [ ] Compare measured MTTR components to RTO bound
  [ ] File issues for each runbook step that took longer than expected
  [ ] Update FMEA: revise Occurrence and Detection scores based on observed behaviour
  [ ] Update error-budget model: adjust projected downtime contribution from this failure mode
```

**MTTR measurement during game day.** The game day is the primary instrument for measuring MTTR with real people. Record timestamps for:

```
T_detect:    time from fault injection to first alert fire
T_diagnose:  time from first alert to incident commander confirming root cause
T_remediate: time from root cause confirmation to recovery action applied
T_verify:    time from recovery action to SLI returning to baseline
MTTR_total:  T_detect + T_diagnose + T_remediate + T_verify

Compare to RTO. If MTTR_total > RTO:
  → Identify the slowest component (T_detect? T_diagnose?)
  → File a targeted improvement action for that component only
```

**Cascading scenario selection.** Use the fault tree from P3: choose a scenario where an MCS size-2 chain is reachable by two sequential faults 5–10 minutes apart. This mimics real incidents where the responder's first mitigation action (e.g. restarting a service) triggers a second failure (e.g. the restart clears a circuit-breaker state that was protecting a downstream). These human-triggered cascades are the most dangerous and the least rehearsed.

---

### P5 — MTTR-Driven Runbook Design

**Primitive anchors**: [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md)

**The MTTR decomposition for runbook structure.** A runbook designed without MTTR decomposition is a list of steps. A runbook designed against MTTR targets is a time-bounded procedure with explicit handoffs and escalation criteria.

**MTTR components and corresponding runbook sections:**

```
MTTR = T_detect + T_diagnose + T_remediate + T_verify

T_detect  → Runbook section: "Alert signal and initial triage"
              Target: ≤ [health-check interval × threshold]
              Runbook includes: which alert fired, first dashboard link, severity classification

T_diagnose → Runbook section: "Root-cause identification"
              Target: ≤ [RTO × 0.3]  (30% of RTO budget)
              Runbook includes: decision tree for top-5 failure modes (from FMEA),
              specific metric queries, log patterns, and expected outputs

T_remediate → Runbook section: "Recovery actions"
               Target: ≤ [RTO × 0.5]  (50% of RTO budget)
               Runbook includes: ordered steps, rollback decision point,
               blast-radius confirmation before each action

T_verify → Runbook section: "Confirmation and closure"
            Target: ≤ [RTO × 0.2]
            Runbook includes: specific SLI thresholds that must be met,
            duration to observe before declaring incident resolved
```

**Bathtub-curve implication for runbook freshness.** Runbooks that are not exercised enter the wear-out phase (right tail of the bathtub curve, primitive 04): their commands reference old infrastructure, their thresholds cite stale baselines, and their escalation contacts are no longer current. Treat runbook staleness as a reliability risk:

- Runbooks not executed in the past 90 days must be reviewed for freshness.
- Game days (P4) are the primary mechanism for keeping runbooks in their useful-life phase.
- Every FMEA re-scoring that increases a failure mode's Occurrence should trigger a runbook review for that failure mode.

**MTTR target derivation from SLO.** The MTTR target is not arbitrary; it follows from the error budget:

```
Error budget (30 days) = (1 - SLO) × 43,200 min
Allowed MTTR per incident = error_budget / expected_incidents_per_month

Example: 99.9% SLO, 3 incidents/month expected:
  budget = 43.2 min
  MTTR_target = 43.2 / 3 = 14.4 min per incident

T_detect_target   ≤ 14.4 × 0.3 = 4.3 min
T_diagnose_target ≤ 14.4 × 0.3 = 4.3 min
T_remediate_target ≤ 14.4 × 0.3 = 4.3 min
T_verify_target   ≤ 14.4 × 0.1 = 1.4 min
```

These per-component targets drive the runbook design: T_detect drives the alert configuration; T_diagnose drives the decision-tree depth; T_remediate drives automation coverage.

---

### P6 — Redundancy Verification via Active-Replica Probes

**Primitive anchors**: [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md)

**The coverage gap.** The redundancy math formula `A_parallel = 1 - (1-A)^n` assumes that every replica actually serves traffic and that the switchover mechanism has coverage probability c = 1. In practice, "active" replicas may be stale, unreachable to the load balancer, or idle due to health-check misconfiguration. Measuring n (replica count) without measuring c (switchover reliability) overstates the achieved availability by orders of magnitude.

**Active-replica probe design.** An active-replica probe is a synthetic probe that:
1. Sends a tagged request to the load balancer endpoint.
2. Reads the replica identifier from the response header or trace.
3. Records which replica served the request.
4. Over a 10-minute window, asserts that all n replicas appear in the trace at least once.

If only k < n replicas appear, the effective availability is:

```
A_effective = 1 - (1 - A_single)^k   (k serving replicas)
```

rather than the expected `1 - (1-A)^n`. The coverage probability c ≈ k/n.

**Probe implementation pattern:**

```python
# Pseudocode: active-replica coverage probe
import collections, time

def probe_replica_coverage(endpoint, n_expected, window_seconds=600, sample_interval=5):
    """
    Probe endpoint for window_seconds; assert all n_expected replicas appear.
    Returns: coverage ratio k/n, list of missing replicas.
    """
    seen = collections.Counter()
    deadline = time.time() + window_seconds

    while time.time() < deadline:
        resp = requests.get(endpoint, headers={"X-Probe": "replica-coverage"})
        replica_id = resp.headers.get("X-Served-By") or resp.json().get("replica_id")
        if replica_id:
            seen[replica_id] += 1
        time.sleep(sample_interval)

    coverage = len(seen) / n_expected
    missing = [f"replica-{i}" for i in range(n_expected) if f"replica-{i}" not in seen]
    return coverage, missing
```

**Integration with CI/CD.** Run the active-replica probe as a gate in the staging promotion pipeline:
- Gate passes if coverage c ≥ 0.95 (all replicas served at least 1 request in the probe window).
- Gate fails if any replica is systematically excluded — this indicates a misconfigured health check or a load-balancer affinity bug.

**Imperfect-coverage correction.** When a probe reveals c < 1, apply the imperfect-coverage formula from primitive 07 to compute the true achieved availability:

```
A_achieved = c × A_parallel + (1 - c) × A_single

Example: n=3, A=0.999, c=0.67 (only 2 of 3 replicas serving):
  A_parallel = 1 - (0.001)^3 ≈ 0.999999999
  A_achieved = 0.67 × 0.999999999 + 0.33 × 0.999 ≈ 0.99967
  
  vs. target A_system = 0.9999 — the deployment is below spec.
```

---

## Anti-Patterns

### A1 — Chaos Experiment Without a Steady-State Hypothesis

**Symptom**: The team injects a fault ("kill one pod"), watches dashboards, and concludes "it looked fine" with no quantitative criterion.

**Why it fails**: Without a falsifiable hypothesis, every experiment passes. A 2× error rate spike that lasts 90 seconds looks fine on a dashboard but consumes 5% of the monthly error budget in one run. Repeated such experiments can exhaust the budget before the team registers any concern.

**Fix**: Apply P2. Define the hypothesis before the experiment: which SLIs, which thresholds, and which abort criterion. Record the burn rate consumed by the experiment itself; account for it against the monthly budget.

---

### A2 — Binary Up/Down SLOs That Ignore Partial Failure

**Symptom**: The SLO is defined as "the service must return HTTP 200" with no latency component and no definition of partial degradation. A service returning HTTP 200 in 30 seconds, or serving 50% of requests successfully with a circuit breaker half-open, is considered "up."

**Why it fails**: FMEA (primitive 06) scores partial failure modes differently from complete outages. A partial failure with Severity=7, Occurrence=5 has a higher RPN than a complete outage with Severity=10, Occurrence=1 — and partial failures are far more common. Binary SLOs miss the partial-failure budget consumption entirely.

**Fix**: Define the SLO with at least two SLIs: an error-rate SLI and a latency SLI. Use multi-window burn rate (P1) so partial degradation that accumulates slowly is also caught. Add a fallback-rate SLI if the service has graceful degradation paths — a high fallback rate is a signal that the service is partially degraded even when it is technically "up."

---

### A3 — Untested Runbooks

**Symptom**: Runbooks are written at launch, updated when engineers remember, and never executed except during real incidents. MTTR during incidents is 3× the runbook-estimated time.

**Why it fails**: Unexercised runbooks are in the wear-out phase (bathtub curve, primitive 04): commands reference deprecated infrastructure, threshold values are stale, and escalation contacts have changed. The runbook has a high detection-failure score (D) in the FMEA sense — it provides no practical assistance during the incident.

**Fix**: Execute every runbook at least once per quarter in a game day (P4). Measure T_diagnose and T_remediate against the targets derived in P5. File issues for each step that exceeded its time budget. Treat "runbook last tested" as a release-gate signal.

---

### A4 — MTTR Optimisation That Hides Recurring Root Causes

**Symptom**: The team focuses on reducing T_remediate (time to fix) by automating restarts and failovers. MTTR improves on paper. The same failure mode recurs monthly.

**Why it fails**: MTTR = T_detect + T_diagnose + T_remediate + T_verify. Automating T_remediate reduces the visible downtime but does nothing to prevent the recurrence. The failure mode remains in the FMEA with a high Occurrence score. From the error-budget perspective (primitive 08), the budget burn rate stays constant — incidents are shorter but just as frequent.

**Fix**: After each MTTR improvement, update the FMEA Occurrence score. If the Occurrence score does not decrease after 3 incidents, escalate to a root-cause fix rather than a faster remediation. Track both MTBF (how often it fails) and MTTR (how long it takes to fix) separately in incident reports.

---

### A5 — Error Budget Measured in a Single Long Window

**Symptom**: The team monitors only a 30-day error budget. A 4-hour incident that burns 30% of the monthly budget is not noticed until the weekly review, by which time it is too late to act.

**Why it fails**: A single 30-day window has a detection lag of up to 7 days for incidents that are not individually catastrophic. The burn rate during a fast incident can be 100× or more, but a 30-day rolling window smooths it to invisibility.

**Fix**: Apply the multi-window burn rate from P1. Implement both a fast-burn alert (1-hour window, 14.4× threshold) and a slow-burn alert (6-hour window, 6× threshold). The fast alert pages on-call; the slow alert creates a ticket. The 30-day window remains as a monthly review signal, not a real-time gate.

---

## Recipes

### R1 — Setting a 99.9% SLO with Multi-Window Burn-Rate Alerts

**Objective**: Configure a complete SLO alerting stack for a service with a 99.9% monthly availability target, with fast and slow burn-rate alerts that page and ticket appropriately.

**Primitive stack**: Error Budgets (#8) + Availability Formulas (#2) + MTBF/MTTR (#1)

**Step 1: Define the SLI.**

```
Identify the event type: HTTP request (count-based) or time-based availability.
  - Count-based: SLI = (good_requests / total_requests) × 100%
  - Time-based: SLI = (minutes service was available / total minutes) × 100%

Choose count-based for web services: it handles bursty traffic without inflating
time windows during low-traffic periods.

Define good vs. bad:
  Good: HTTP response code NOT in {500, 502, 503, 504}, latency < 500 ms
  Bad: any of the above codes, OR latency >= 500 ms (latency SLI is optional but recommended)
```

**Step 2: Compute the error budget.**

```python
slo_target = 0.999          # 99.9%
window_days = 30
window_minutes = window_days * 24 * 60  # 43,200 min

error_budget_fraction = 1 - slo_target   # 0.001
error_budget_minutes = error_budget_fraction * window_minutes  # 43.2 min
error_budget_requests = None  # compute from traffic: error_budget_fraction × total_requests
```

**Step 3: Derive burn-rate thresholds.**

```
Fast burn (1-hour alert):
  Threshold: burn_rate > 14.4
  Meaning: budget exhausted in 30d / 14.4 ≈ 2 days at current rate
  Budget consumed when alert fires: 14.4 × (1h / 720h) × 100% = 2%

Slow burn (6-hour alert):
  Threshold: burn_rate > 6
  Meaning: budget exhausted in 5 days at current rate
  Budget consumed when alert fires: 6 × (6h / 720h) × 100% = 5%
```

**Step 4: Implement Prometheus alert rules.**

```yaml
groups:
  - name: slo_alerts
    rules:
      - alert: SLOFastBurnPage
        expr: |
          (
            sum(rate(http_requests_total{job="checkout",code=~"5.."}[1h]))
            /
            sum(rate(http_requests_total{job="checkout"}[1h]))
          ) > 0.01440   # 14.4 × (1 - 0.999)
        for: 2m
        labels:
          severity: critical
          slo: checkout_availability
        annotations:
          summary: "Checkout SLO fast burn: >14.4x error budget consumption"
          runbook: "https://wiki/runbooks/checkout-slo-burn"

      - alert: SLOSlowBurnTicket
        expr: |
          (
            sum(rate(http_requests_total{job="checkout",code=~"5.."}[6h]))
            /
            sum(rate(http_requests_total{job="checkout"}[6h]))
          ) > 0.00600   # 6 × (1 - 0.999)
        for: 15m
        labels:
          severity: warning
          slo: checkout_availability
        annotations:
          summary: "Checkout SLO slow burn: >6x error budget consumption"
```

**Step 5: Wire chaos experiment abort to burn-rate alerts.**

```
In the chaos framework (LitmusChaos, Gremlin, or custom):
  abort_condition:
    prometheus_query: >
      sum(rate(http_requests_total{job="checkout",code=~"5.."}[1h]))
      / sum(rate(http_requests_total{job="checkout"}[1h])) > 0.014

  If abort_condition is true for > 60 seconds: terminate experiment, restore state.
```

**Step 6: Verify the alert stack with a synthetic burn.**

```bash
# Inject 1.5% error rate for 5 minutes to verify fast-burn alert fires
wrk -t4 -c100 -d300s --script inject_errors.lua https://checkout-staging/api

# Confirm: SLOFastBurnPage fires within 2 minutes of error injection start
# Confirm: alert resolves within 2 minutes of error injection stop
```

---

### R2 — Designing a Region-Failover Game Day

**Objective**: Plan and execute a game day that validates the team's ability to complete a region failover within the stated RTO, using MTTR decomposition to measure each phase and identify improvement targets.

**Primitive stack**: MTBF/MTTR (#1) + Error Budgets (#8) + FTA (#5) + Redundancy Math (#7) + Bathtub Curve (#4)

**Step 1: Define the scenario and steady-state hypothesis.**

```
Scenario: Primary region (eu-west-1) becomes unavailable. Traffic must fail over to
secondary region (us-east-1) within RTO = 15 minutes.

Steady-state (before fault injection):
  - Checkout error rate: < 0.1% (SLO: 99.9%)
  - Checkout p99 latency: < 300 ms
  - Active serving region: eu-west-1 (confirmed by X-Served-Region header)

Hypothesis (during failover):
  - Checkout error rate: < 2% during failover window (budget burn < 20× for ≤ 5 min)
  - Traffic in us-east-1: > 95% of pre-failover volume within 15 minutes
  - Error rate in us-east-1: < 0.2% within 10 minutes of failover completion
  
Abort criterion: error rate > 5% for > 2 minutes continuously
```

**Step 2: Run the fault tree to confirm blast radius.**

```
Top event: All users see errors (not just eu-west-1 users)
  Requires: eu-west-1 fails AND us-east-1 DNS/routing fails (MCS size 2)

Single-region failover blast radius: DEGRADED (eu-west-1 users only during failover)
→ Safe for production with abort criterion wired
```

**Step 3: Assign roles and pre-game checks.**

```
Roles:
  Incident Commander (IC):  calls abort, manages timeline
  Operator A:               executes DNS/routing failover steps
  Operator B:               monitors SLIs and fires abort if needed
  Observer:                 records timestamps for each MTTR phase

Pre-game checklist:
  [ ] Verify us-east-1 has current replica data (replication lag < 1 min)
  [ ] Confirm active-replica probe shows us-east-1 replicas are healthy (P6)
  [ ] Verify DNS TTL is ≤ 60 s (required for T_remediate ≤ 5 min target)
  [ ] Confirm rollback procedure: re-route DNS to eu-west-1; estimated time: 2 min
  [ ] All abort monitors are running
```

**Step 4: Execute and instrument.**

```
T+0:00  Fault injection: block all inbound traffic to eu-west-1 at the network layer
T+X:XX  T_detect: record time when first alert fires
T+X:XX  T_diagnose: record time when IC confirms "region failover required"
T+X:XX  T_remediate start: Operator A executes DNS failover runbook
T+X:XX  T_remediate end: DNS propagated; us-east-1 serving > 95% of traffic
T+X:XX  T_verify: SLIs return to < 0.2% error rate in us-east-1
T+X:XX  Fault removed; observe recovery to baseline
```

**Step 5: Compute MTTR and compare to RTO.**

```
RTO = 15 min
MTTR_target per component:
  T_detect_target   = 3 min  (health check interval + threshold)
  T_diagnose_target = 4 min
  T_remediate_target = 5 min
  T_verify_target   = 3 min

Measured results (example):
  T_detect   = 2 min 45 s  [OK]
  T_diagnose = 6 min 10 s  [X] (2 min over target — runbook diagnosis section unclear)
  T_remediate = 4 min 30 s [OK]
  T_verify   = 2 min 50 s  [OK]
  MTTR_total = 16 min 15 s [X] (1 min 15 s over RTO)

Action: Improve T_diagnose. Runbook diagnosis section needs a 3-step decision tree
        for "is this a region failure or a service failure?" — currently requires
        manual log inspection.
```

**Step 6: Post-game FMEA update.**

```
Failure mode: "Primary region unavailable"
  Before game day: O=2 (low — assumed rare), D=3 (low — assumed detectable)
  After game day:  O=2 (unchanged), D=2 (improved — alert fires reliably in 2:45)
  
Residual risk: T_diagnose still above target. Create ticket to add region-failure
diagnostic section to runbook before next game day.
```

---

### R3 — Building a Fault Tree for a Cascaded Agent Stack

**Objective**: Construct a fault tree for a multi-agent orchestration system where agents call downstream agents and external tools, identify the minimal cut sets that could cause the top-level user request to fail, and derive an experiment priority order.

**Primitive stack**: FTA (#5) + System Reliability (#10) + FMEA (#6) + Error Budgets (#8)

**Step 1: Define the top event.**

```
Top event: "User-visible agent task fails completely"
  (Partial failure — degraded output — is a separate, lower-severity event)
```

**Step 2: Map the system structure.**

```
Agent stack (simplified):
  User → Orchestrator → [Planner, Executor, Validator]
                           Planner → LLM API
                           Executor → [Tool-A, Tool-B, Memory-Store]
                           Validator → LLM API

Dependencies:
  - LLM API: shared by Planner and Validator (common-cause risk)
  - Memory-Store: read by Executor; write by Orchestrator
  - Tool-A: external; has its own SLA
  - Tool-B: internal; has no HA
```

**Step 3: Construct the fault tree.**

```
Top event: Agent task fails completely (OR gate — any one of these suffices)
  ├── Orchestrator crashes (MCS size 1)
  ├── LLM API unavailable (MCS size 1 — shared by Planner + Validator)
  ├── Memory-Store unavailable AND no retry budget (MCS size 1 if retries exhausted)
  ├── Planner fails AND fallback not implemented (MCS size 1)
  ├── Executor fails AND no retry (MCS size 1)
  └── Tool-A fails AND Tool-B fails (MCS size 2 — both tools required)

Minimal cut sets:
  MCS-1: {Orchestrator failure}               — size 1
  MCS-2: {LLM API unavailable}                — size 1 (common-cause for Planner+Validator)
  MCS-3: {Memory-Store unavailable, retry exhausted}  — size 1 under sustained failure
  MCS-4: {Tool-A failure, Tool-B failure}      — size 2
```

**Step 4: Compute Fussell-Vesely importance.**

```
Estimated component availabilities (from incident history):
  Orchestrator:  A = 0.9998
  LLM API:       A = 0.9950  (← binding constraint due to rate limits + outages)
  Memory-Store:  A = 0.9995
  Tool-A:        A = 0.9990
  Tool-B:        A = 0.9990
  Tool-A+Tool-B: A_pair = 1 - (1-0.999)^2 = 0.999999

System A_effective ≈ 0.9998 × 0.9950 × 0.9995 × 0.999999 ≈ 0.9943

FV_importance(LLM API) ≈ (1 - 0.995) / (1 - 0.9943) ≈ 0.005 / 0.0057 ≈ 88%
FV_importance(Orchestrator) ≈ (1 - 0.9998) / 0.0057 ≈ 3.5%
FV_importance(Memory-Store) ≈ (1 - 0.9995) / 0.0057 ≈ 8.8%
```

**Step 5: Derive experiment priority order.**

```
1. LLM API unavailability (FV=88%) — highest priority experiment
   Hypothesis: Planner falls back to cached plan; Validator skips or returns degraded output
   Blast radius: CASCADING if no fallback — test in staging only until fallback is implemented
   Abort criterion: top-level task failure rate > 10%

2. Memory-Store unavailability (FV=8.8%)
   Hypothesis: Executor falls back to stateless mode; Orchestrator retries with backoff
   Blast radius: DEGRADED (stateless fallback reduces quality but maintains completion)
   Safe for staging; acceptable in production with traffic monitoring

3. Tool-A + Tool-B simultaneous failure (MCS size 2)
   Hypothesis: Executor returns a graceful "tools unavailable" response
   Blast radius: DEGRADED
   Safe for staging
```

**Step 6: Update the FMEA with FTA results.**

```
Add to FMEA worksheet:
  Component: LLM API
  Failure mode: Rate limit or outage
  Effect: Top-level task fails completely
  S=9, O=5 (multiple incidents last quarter), D=4 (alerts exist but detection lag 3 min)
  RPN = 9 × 5 × 4 = 180 — highest RPN in the stack

Mitigation required: implement LLM API circuit breaker and degraded-mode fallback
before running LLM API chaos experiment in production.
```

---

## Cross-References

### Foundation

All primitives cited by number in this file are defined with inputs, outputs, failure modes, and worked examples in:

- [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md) — canonical source for primitives #1–#11

### Sibling References in This Skill

- [chaos-engineering-guide.md](chaos-engineering-guide.md) — tooling and environment setup for chaos experiments; complements P2 (steady-state hypothesis) and R1 (SLO abort criterion)
- [disaster-recovery-testing.md](disaster-recovery-testing.md) — DR drill procedures; complements P4 (game-day blueprint) and R2 (region failover game day)
- [resilience-checklists.md](resilience-checklists.md) — pre-launch and post-incident checklists; complements P5 (runbook design) and the FMEA linkages in R3
- [resilience-telemetry.md](resilience-telemetry.md) — SLI/SLO instrumentation; required for P1 (burn-rate alerts) and P2 (steady-state measurement)
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) — circuit breaker implementation details; the chaos experiment in P2 targets circuit breaker behaviour
- [cascading-failure-prevention.md](cascading-failure-prevention.md) — prevention patterns; the game-day blueprint in P4 tests these prevention mechanisms

_Last verified: 2026-07-11. Arithmetic in P5/R1 (error-budget minute conversion) corrected to use a 43,200-minute (30-day) reference month consistently; earlier drafts mixed a 43,800-minute average-month figure with the 43,200-minute figure used elsewhere in this file, producing MTTR targets off by ~2%._
