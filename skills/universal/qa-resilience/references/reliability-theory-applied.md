---
description: Reliability-theory primitives applied to QA resilience work — SLO error-budget burn-rate alerts, chaos steady-state hypothesis design, fault-tree blast-radius scoping, game-day blueprints, MTTR-driven runbook design, and active-replica probe patterns.
status: stable
---

# Reliability Theory Applied to QA Resilience

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

_Link adapter to [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md). The foundation owns the theory (definitions, formulas, derivations, worked examples). This file keeps only what is specific to qa-resilience: which testing decisions each primitive drives, QA-specific thresholds, pitfalls, and checked worked examples._

Foundation templates:
[01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) ·
[02-availability-formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) ·
[04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) ·
[05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) ·
[06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) ·
[07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) ·
[08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) ·
[10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md). Validation and interval machinery: [decision-and-validation.md](../../foundations-reliability-theory/references/decision-and-validation.md). SLO design and alert implementation are owned by [qa-observability `slo-design-guide.md`](../../qa-observability/references/slo-design-guide.md).

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

Without a reliability grounding, resilience testing either detects nothing (over-cautious experiments) or produces unfalsifiable results (no hypothesis). Each primitive fixes one QA gap:

| QA resilience gap | Primitive that fixes it |
|---|---|
| No quantitative pass/fail criterion for a chaos run | Error budget (08): the burn-rate threshold is the abort signal |
| Chaos scope set by gut feel | Fault tree (05): limit each run to one minimal cut set (MCS) |
| Game day ends without knowing if RTO was met | MTTR decomposition (01): time T_detect, T_diagnose, T_remediate, T_verify against RTO |
| Replica count assumed to provide HA | Redundancy math (07): measure switchover coverage c, not just replica count n |
| SLO breaches invisible until the weekly review | Multi-window burn rate (08): Table 5-8 windows page before the budget is gone |
| Runbook time guessed from happy-path walk-throughs | MTTR sampling (01): use the observed incident distribution (p90), not the mean |

---

## Patterns

### P1 — SLO Error-Budget Burn-Rate Alerts (Multi-Window, Multi-Burn)

**Theory:** burn rate, budget-consumed formula, and the SRE Workbook ch. 5 Table 5-8 tiers live in [08-error-budgets § Multi-Window Burn Rate](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md). Alert implementation (recording rules, routing) is owned by [qa-observability](../../qa-observability/references/slo-design-guide.md).

**QA use.** Use SRE Workbook Table 5-8 unchanged, alerting only when both windows exceed the rate: page at 14.4× (1 h / 5 m) and 6× (6 h / 30 m), ticket at 1× (3 d / 6 h). At 99.9% the fast-page error-rate threshold is 1.44%. Full table: [Canonical Multi-Window Burn-Rate Table](../../qa-observability/references/slo-design-guide.md#canonical-multi-window-burn-rate-table).

**Integration with chaos experiments.** The fast-burn page is the abort criterion for a chaos run (fires → abort), and "no burn-rate alert fired during and after the run" is the pass signal. Account for the budget the experiment itself spends (see A1).

---

### P2 — Steady-State Hypothesis Design for Chaos Experiments

**Theory:** SLO-derived bounds from [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md); recovery bound from [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md); failure-mode inventory from [06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md).

**Principle (Basiri et al. 2016, "Chaos Engineering").** An experiment is falsifiable only if the steady state is defined quantitatively *before* it runs. "The system is healthy" is not a hypothesis.

**Hypothesis structure:**

```
Given:    [traffic level, upstream health, time of day]
When:     [fault injected — what, scope, duration]
Then:     error rate < bound; latency-SLI proportion >= bound; burn rate < abort threshold;
          [recovery metric] returns to baseline within T minutes of fault removal
Abort if: [burn-rate threshold or customer-impact signal]
```

**Where each bound comes from:**

- Error-rate bound: `1 − SLO` (99.9% → 0.1%).
- Latency bound: the normal-operation baseline, expressed as a proportion of requests under a threshold (the foundation explains why percentiles do not compose).
- Recovery bound: the MTTR/RTO target (P5).
- Abort: the P1 fast-burn threshold (1.44% error rate at 99.9%).

**FMEA linkage.** The injected failure mode should already be a row in the FMEA. Use its Occurrence (anchored to incident history) and observed per-incident budget spend to size the abort threshold. RPN is an ordinal ranking, not a budget estimate. Always test S ≥ 9 rows regardless of their RPN.

**Example: circuit-breaker experiment (99.9% SLO)**

```
Baseline (10 min): checkout error rate < 0.05%; p99 < 200 ms; payment circuit CLOSED
Fault:             payment-service returns 503 for 100% of requests for 2 min
During fault:      error rate < 0.5% (burn < 5x, fallback active); p99 < 300 ms;
                   circuit OPEN within 30 s
Recovery:          error rate < 0.05% and circuit HALF_OPEN -> CLOSED within 3 min
Abort:             fast-burn page fires (14.4x over 1 h AND 5 m), or an operator
                   early-stop: error rate > 1.44% (14.4x) for > 60 s
```

---

### P3 — Fault-Tree Decomposition for Blast-Radius Scoping

**Theory:** gates, minimal cut sets, and importance measures (Birnbaum, Fussell-Vesely) are in [05-fault-tree-analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md); series/parallel composition in [10-system-reliability](../../foundations-reliability-theory/assets/templates/reliability-theory/10-system-reliability.md).

**QA use of MCS size:**

- Size-1 MCS component: its failure alone fires the top event. Inject only with a rollback plan, reduced traffic, and a wired abort.
- Size-2+ MCS component: one injection alone should not fire the top event. Start here.

**Blast-radius classes and where each is allowed:**

```
CONTAINED  — fault isolated to the injected component
DEGRADED   — fallback path active; some features impaired
CASCADING  — fault propagates along an MCS chain; top event likely

Non-production: any   |   Staging: CONTAINED or DEGRADED   |   Production: CONTAINED only, abort wired
```

This allow-list is a local policy, not a standard. R2 argues a case for DEGRADED in production when the abort is wired and the affected population is bounded.

**Experiment priority.** Rank candidate experiments by Fussell-Vesely importance: the component contributing most to top-event probability has the highest information value. For a series chain of rare failures, FV_i ≈ (1 − A_i) / (1 − A_system) (see R3).

**Example (3-tier web app):**

```
Top event: Checkout unavailable (OR)
  ├── API gateway fails                                     (MCS size 1)
  ├── Auth unavailable AND no cached tokens                 (MCS size 2)
  ├── Core service fails (all replicas)                     (MCS size 1 at the service level)
  └── DB primary unavailable AND replica promotion fails    (MCS size 2)

"Kill one core-service replica": the replica-level cut set needs both replicas → size 2
→ DEGRADED (load shifts to replica 2); staging OK, production only with traffic monitoring
```

---

### P4 — Game-Day Blueprint for Cascading-Failure Rehearsal

**Theory:** MTTR decomposition in [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md); scenario source is the P3 fault tree; budget accounting in [08-error-budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md).

**Purpose.** A game day tests human recovery (coordination, runbook clarity, communications), not just graceful degradation. A cascading game day rehearses the case where the responder's first mitigation triggers a second failure.

```
Pre-game (T−2 weeks):
  [ ] Pick the cascade from a P3 MCS chain; write the P2 hypothesis
  [ ] Roles: incident commander, operators, observers, abort owner
  [ ] Abort criteria: burn-rate threshold + customer-impact signal
  [ ] Rollback procedure confirmed for every injected fault; stakeholders notified

Game day (T=0):
  [ ] 10-min baseline; confirm hypothesis bounds
  [ ] Fault 1 (first MCS element); start timer; did the first fallback activate in time?
  [ ] Fault 2, 5–10 min later, to complete the MCS; graceful degradation or top event?
  [ ] Remove faults; record T_detect, T_diagnose, T_remediate, T_verify

Post-game (T+1 day):
  [ ] MTTR_total vs RTO → one targeted action for the slowest phase only
  [ ] Issue per runbook step that overran; update FMEA O and D scores
  [ ] Update the error-budget model for this failure mode
```

**Timestamp definitions.** T_detect is fault injection to first alert. T_diagnose is alert to IC-confirmed cause. T_remediate is cause to recovery action applied. T_verify is action to SLI back at baseline.

**Why cascades.** Human-triggered cascades are the most dangerous and least rehearsed class. An example is a restart that clears circuit-breaker state that was protecting a downstream. The companion view that recovery is not the mirror of failure (metastability) is in [cascading-failure-prevention.md](cascading-failure-prevention.md).

---

### P5 — MTTR-Driven Runbook Design

**Theory:** MTTR components and why to sample the distribution rather than the mean are in [01-mtbf-mttr](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md). The wear-out analogy is in [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md).

**Runbook sections map to MTTR phases:**

| MTTR phase | Runbook section | Contains |
|---|---|---|
| T_detect | Alert signal and initial triage | Which alert fired, first dashboard, severity |
| T_diagnose | Root-cause identification | Decision tree for top FMEA modes (plus every S ≥ 9 mode), queries, log patterns |
| T_remediate | Recovery actions | Ordered steps, rollback decision point, blast-radius check before each action |
| T_verify | Confirmation and closure | SLI thresholds and the observation duration before declaring resolved |

**MTTR target from the error budget.** The window is a parameter; 43,200 min is a 30-day window.

```
budget_min      = (1 − SLO) × window_min
MTTR_target     = budget_min / expected_incidents_per_window

99.9%, 30 days, 3 incidents: budget = 43.2 min → MTTR_target = 14.4 min
Phase split (local choice, not a standard): 30/30/30/10 %
  T_detect ≤ 4.32 min, T_diagnose ≤ 4.32 min, T_remediate ≤ 4.32 min, T_verify ≤ 1.44 min
```

This spends the whole budget on expected incidents, leaving nothing for deploys or chaos runs. Reserve a share first if those draw from the same budget.

**Runbook freshness (QA thresholds, local policy).** Review any runbook not executed in 90 days. Game days (P4) are the mechanism that keeps runbooks current. When an FMEA re-score raises a mode's Occurrence, review that mode's runbook.

---

### P6 — Redundancy Verification via Active-Replica Probes

**Theory:** parallel availability and the imperfect-coverage mixture `c × A_parallel + (1 − c) × A_single` are in [07-redundancy-math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md). That file also covers how many drills it takes to validate c (§ Validation).

**Two separate things to verify:**

1. **Participation (k of n).** The probe asserts every replica actually serves traffic. If only k < n serve, the redundancy you have is k, not n. The fix is usually a misconfigured health check or load-balancer affinity.
2. **Switchover coverage c.** The probability that failover succeeds when a replica dies. The participation probe does not measure c: k/n is not c. Measure c with fault-injection drills, and size the number of drills from the foundation's confidence bound. Ten successes cannot show c ≥ .995.

**Participation probe (pseudocode):**

```python
import collections, time, requests

def probe_replica_coverage(endpoint, expected_ids, window_seconds=600, sample_interval=5):
    """Sample the LB endpoint; return (k/n, missing replica ids)."""
    seen = collections.Counter()
    deadline = time.time() + window_seconds
    while time.time() < deadline:
        resp = requests.get(endpoint, headers={"X-Probe": "replica-coverage"})
        rid = resp.headers.get("X-Served-By")
        if rid:
            seen[rid] += 1
        time.sleep(sample_interval)
    missing = [r for r in expected_ids if r not in seen]
    return len(set(expected_ids) & set(seen)) / len(expected_ids), missing
```

**CI/CD gate (local policy).** In staging promotion, fail if any expected replica served zero requests in the window. With 120 samples over 10 min and uniform balancing, a healthy replica is essentially never missed. A persistent miss is a configuration bug.

**Worked example (coverage, not participation).** n = 3, A = .999 per replica, drills show c = 0.67:

```
A_parallel = 1 − 0.001³ ≈ 0.999999999
A_achieved = 0.67 × 0.999999999 + 0.33 × 0.999 ≈ 0.99967   (< 0.9999 target → below spec)
```

With perfect switchover, even k = 2 serving replicas would give 1 − 0.001² = 0.999999. Here the switchover, not the replica count, is the binding constraint.

---

## Anti-Patterns

### A1 — Chaos Experiment Without a Steady-State Hypothesis

**Symptom**: The team kills a pod, watches dashboards, and concludes "it looked fine".

**Why it fails**: Without a falsifiable hypothesis every experiment passes, and the budget the experiments spend is never counted. At 99.9%, a 90-second full outage of the targeted path is a 1000× burn. It consumes 1000 × 1.5 / 43,200 ≈ 3.5% of a 30-day budget per run, so a handful of repeat runs can spend a noticeable share of the month.

**Fix**: Apply P2: set SLIs, thresholds, and the abort before the run. Record each run's budget spend against the window.

---

### A2 — Binary Up/Down SLOs That Ignore Partial Failure

**Symptom**: The SLO is "returns HTTP 200". A 30-second 200, or a half-open breaker serving 50% of requests, still counts as "up".

**Why it fails**: Partial-failure modes are more frequent than full outages. A 200-only SLI does not count them against the budget at all. The FMEA lists them as separate rows. Their frequency makes their cumulative budget impact large even though each has lower severity. Do not let RPN ranking push full-outage rows (S ≥ 9) out of review ([06-fmea](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md)).

**Fix**: Use at least an error-rate SLI and a latency SLI (proportion under threshold). Add a fallback-rate SLI where graceful degradation exists. Keep the P1 multi-window alerts so slow partial degradation is caught.

---

### A3 — Untested Runbooks

**Symptom**: Runbooks are written at launch, rarely updated, and executed only in real incidents. Incident MTTR far exceeds the runbook estimate.

**Why it fails**: Unexercised runbooks drift: dead commands, stale thresholds, wrong escalation contacts. This is wear-out by analogy to [04-bathtub-curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md). In FMEA terms the runbook gives no real detection or recovery help.

**Fix**: Exercise every runbook in a game day (P4) at least quarterly (local policy). Time each phase against P5 targets and file an issue per overrun. Treat "runbook last tested" as a release-gate signal.

---

### A4 — MTTR Optimisation That Hides Recurring Root Causes

**Symptom**: Automated restarts and failovers cut T_remediate. MTTR improves, but the same mode recurs monthly.

**Why it fails**: Budget spend is roughly frequency × duration. Shorter incidents at an unchanged frequency still burn budget, and the root cause stays in the FMEA with high Occurrence.

**Fix**: Track MTBF and MTTR separately per failure mode. If Occurrence does not fall after 3 recurrences (local threshold), escalate to a root-cause fix instead of faster remediation.

---

### A5 — Error Budget Measured in a Single Long Window

**Symptom**: Only the 30-day budget is watched. A 4-hour incident that burns 30% of the budget (54× burn, 5.4% error rate at 99.9%) is noticed at the weekly review.

**Why it fails**: A 30-day rolling average smooths a short, intense burn into a small step. Nothing pages while the budget drains.

**Fix**: Alert on the three long-AND-short-window tiers in the [canonical table](../../qa-observability/references/slo-design-guide.md#canonical-multi-window-burn-rate-table) (see P1). The 30-day figure stays a review metric, not an alert.

---

## Recipes

### R1 — Setting a 99.9% SLO with Multi-Window Burn-Rate Alerts

**Objective**: A complete, testable burn-rate alert stack for a 99.9% checkout SLO over a 30-day window, wired into chaos aborts. Canonical alert design lives in [qa-observability](../../qa-observability/references/slo-design-guide.md). This recipe is the QA-facing slice.

**Step 1: SLI.** Count-based: good = non-5xx AND latency < 500 ms; SLI = good / total. Request-based budgets scale with traffic. At low traffic, one failure can exceed 14.4× on its own. With zero failures in n events, the 95% upper bound on the error rate is ≈ 3/n, so showing ≤ 0.1% needs ≈ 3,000 events. The Workbook remedies are synthetic traffic, aggregating small services into one monitored group, product changes so one failure costs less, or reconsidering the SLO's per-failure impact. Details: [08-error-budgets § Measurement Limits](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md).

**Step 2: Budget.** 0.001 × 43,200 min = 43.2 min per 30 days (window is a parameter).

**Step 3–4: Thresholds and rules.** Take the thresholds from the [canonical table](../../qa-observability/references/slo-design-guide.md#canonical-multi-window-burn-rate-table) and generate the long-AND-short-window rules from the SLO spec (see [slo-as-code.md](slo-as-code.md)). qa-observability owns the PromQL and its `promtool` tests; do not keep a hand-written copy here.

**Step 5: Chaos abort.** Wire the chaos framework (LitmusChaos, Gremlin, custom) to abort on the 1 h page condition. For short experiments, a stricter local abort on the 5 m window alone (> 0.0144 for > 60 s) stops the run before the 1 h window catches up. Label it a local choice.

**Step 6: Verify the stack with a synthetic burn (staging).** Workbook detection time = (1 − SLO) / error_rate × window × burn_rate. For the 1 h/14.4× rule:

```
inject 20% errors  → detect ≈ 0.001 / 0.20  × 60 min × 14.4 ≈ 4.3 min
inject 1.5% errors → detect ≈ 0.001 / 0.015 × 60 min × 14.4 ≈ 58 min
```

So inject ≥ 20% for at least 10 min and expect a page in about 4–5 min. After injection stops, expect it to reset within about 5 min, once the 5 m short window drops below 1.44%. A 1.5% injection for 5 min will not fire this rule. That is expected behaviour, not a broken alert.

---

### R2 — Designing a Region-Failover Game Day

**Objective**: Validate a region failover within RTO = 15 min, using MTTR phases to find the improvement target. Primitives: 01, 05, 07, 08 (links above).

**Step 1: Scenario and hypothesis.**

```
Scenario: eu-west-1 unavailable; fail over to us-east-1 within 15 min.
Baseline: error rate < 0.1%; p99 < 300 ms; serving region eu-west-1 (X-Served-Region)
During:   error rate < 2% (burn < 20×) for ≤ 5 min;
          us-east-1 > 95% of pre-failover volume within 15 min;
          us-east-1 error rate < 0.2% within 10 min of failover completion
Abort:    error rate > 5% for > 2 min continuously
```

Budget cost if the hypothesis holds: 20 × 5 / 43,200 ≈ 0.23% of a 30-day budget.

**Step 2: Blast radius (P3).** Top event "all users see errors" needs eu-west-1 down AND us-east-1 routing broken (MCS size 2). A single-region failover is DEGRADED for eu-west-1 users only. It can run in production only with the abort wired. This is a deliberate exception to the P3 production allow-list, because the population and duration are bounded.

**Step 3: Roles and pre-game checks.** IC (owns abort and timeline), Operator A (DNS/routing), Operator B (SLIs and abort trigger), Observer (phase timestamps). Pre-game checks:
- Replication lag < 1 min.
- us-east-1 replicas pass the P6 participation probe.
- DNS TTL ≤ 60 s, required for T_remediate ≤ 5 min.
- Rollback re-routes to eu-west-1 in about 2 min.
- Abort monitors are running.

**Step 4: Execute.** Block inbound to eu-west-1 at T+0. Record the first alert (T_detect), IC confirms "region failover" (T_diagnose), DNS propagated with > 95% in us-east-1 (T_remediate end), us-east-1 < 0.2% error (T_verify).

**Step 5: MTTR vs RTO (example).**

```
Phase targets (sum = RTO 15 min): detect 3, diagnose 4, remediate 5, verify 3
Measured: detect 2:45 [OK], diagnose 6:10 [X, +2:10], remediate 4:30 [OK], verify 2:50 [OK]
MTTR_total = 16:15 [X, 1:15 over RTO]
Action: add a 3-step "region failure vs service failure" decision tree to the runbook
```

**Step 6: FMEA update.** "Primary region unavailable": O stays 2. D improves 3 → 2 because the alert fired reliably in 2:45. Residual risk is T_diagnose; ticket the runbook fix before the next game day.

---

### R3 — Building a Fault Tree for a Cascaded Agent Stack

**Objective**: Fault tree for a multi-agent orchestration stack, MCS list, and chaos priority order. Primitives: 05, 10, 06, 08. Agent-specific reliability patterns are in [ai-agent-reliability.md](../../foundations-reliability-theory/references/ai-agent-reliability.md).

**Step 1: Top event.** "User-visible agent task fails completely". Degraded output is a separate, lower-severity event.

**Step 2: Structure.**

```
User → Orchestrator → [Planner → LLM API, Executor → {Tool-A, Tool-B, Memory-Store}, Validator → LLM API]
LLM API shared by Planner and Validator (common cause); Tool-A external SLA; Tool-B internal, no HA;
Tool-A and Tool-B interchangeable for the task (either suffices)
```

**Step 3: Fault tree and MCS.**

```
Top event (OR):
  ├── Orchestrator crashes                                  MCS {Orchestrator}           size 1
  ├── LLM API unavailable (common cause)                    MCS {LLM API}                size 1
  ├── Memory-Store unavailable AND retries exhausted        size 1 under sustained failure
  ├── Planner fails AND no fallback / Executor fails AND no retry   size 1 each
  └── Tool-A fails AND Tool-B fails                         MCS {Tool-A, Tool-B}         size 2
```

**Step 4: Fussell-Vesely importance** (series approximation, availabilities from incident history):

```
Orchestrator .9998, LLM API .9950, Memory-Store .9995, Tool pair 1 − 0.001² = .999999
A_system ≈ .9998 × .9950 × .9995 × .999999 ≈ 0.99430  → unavailability ≈ 0.0057
FV(LLM API)      ≈ 0.0050 / 0.0057 ≈ 88%
FV(Memory-Store) ≈ 0.0005 / 0.0057 ≈ 8.8%
FV(Orchestrator) ≈ 0.0002 / 0.0057 ≈ 3.5%
```

**Step 5: Experiment order.**

1. LLM API unavailable (FV 88%). Hypothesis: the Planner uses a cached plan and the Validator degrades. Without a fallback the blast radius is CASCADING, so run it in staging only until the fallback exists. Abort if the task failure rate exceeds 10%.
2. Memory-Store unavailable (FV 8.8%). Hypothesis: the Executor goes stateless and the Orchestrator retries with backoff. Blast radius DEGRADED: staging, then production with monitoring.
3. Tool-A + Tool-B simultaneous failure (MCS size 2). Hypothesis: a graceful "tools unavailable" response. Blast radius DEGRADED: staging.

**Step 6: FMEA row.**

```
LLM API | rate limit or outage | task fails completely | S=9, O=5, D=4 | RPN = 180
```

It has the highest RPN in the stack, but it would be reviewed anyway because S ≥ 9. Review every other S ≥ 9 row (e.g. Orchestrator crash) independently of its RPN. Required before the production LLM-API experiment: a circuit breaker plus a degraded-mode fallback.

---

## Cross-References

### Foundation

- [foundations-reliability-theory](../../foundations-reliability-theory/SKILL.md) — canonical source for primitives 01–11; templates linked at the top of this file.
- [decision-and-validation.md](../../foundations-reliability-theory/references/decision-and-validation.md) — confidence bounds, drill counts, and decision rules.
- [foundations-safety-engineering](../../foundations-safety-engineering/SKILL.md) — STPA and Safety-II when FTA's linear-chain model is not enough.
- [qa-observability `slo-design-guide.md`](../../qa-observability/references/slo-design-guide.md) — owner of SLO design and alert implementation.

### Sibling References in This Skill

- [chaos-engineering-guide.md](chaos-engineering-guide.md) — chaos tooling and environments; complements P2 and the R1 abort.
- [disaster-recovery-testing.md](disaster-recovery-testing.md) — DR drill procedures; complements P4 and R2.
- [resilience-checklists.md](resilience-checklists.md) — pre-launch and post-incident checklists; complements P5 and R3.
- [resilience-telemetry.md](resilience-telemetry.md) — SLI/SLO instrumentation for P1 and P2.
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) — the breaker behaviour exercised in the P2 example.
- [cascading-failure-prevention.md](cascading-failure-prevention.md) — prevention mechanisms the P4 game day tests; metastable recovery.

