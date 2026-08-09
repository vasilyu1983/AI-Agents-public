# Reliability Theory Applied to Observability

> **Gate before invoking:** Check [`foundations-reliability-theory` § When to Apply](../../foundations-reliability-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Observability is the measurement substrate of reliability engineering. Every SLO, burn-rate alert, and incident dashboard is a reliability-theory artefact in disguise. MTBF and MTTR are the quantities behind every "time to detect" and "time to restore" metric. Error budgets are derived from availability formulas. Hazard functions explain why a newly deployed service fails more often in its first hour than in its third week. Fault trees map directly to the alert topology decisions that determine whether an on-call engineer pages on symptoms or root causes.

This reference applies the 11 primitives from [`foundations-reliability-theory`](../../foundations-reliability-theory/SKILL.md) to the specific constraints of incident telemetry, SLO burn-rate alerting, deployment hazard monitoring, and instrumentation coverage decisions in the `qa-observability` domain.

---

## Contents

- [Why Reliability Theory](#why-reliability-theory)
- [Patterns](#patterns)
  - [P1 — MTBF/MTTR Dashboard from Incident Store](#p1--mtbfmttr-dashboard-from-incident-store)
  - [P2 — SLO Burn-Rate Alerting Derived from Error Budgets](#p2--slo-burn-rate-alerting-derived-from-error-budgets)
  - [P3 — Hazard Rate Alerting on Aging Deployments](#p3--hazard-rate-alerting-on-aging-deployments)
  - [P4 — Observability Coverage for Fault-Tree Top Events](#p4--observability-coverage-for-fault-tree-top-events)
  - [P5 — FMEA-Driven Instrumentation Gaps Audit](#p5--fmea-driven-instrumentation-gaps-audit)
  - [P6 — Multi-Window Burn-Rate Alerting from Redundancy Math](#p6--multi-window-burn-rate-alerting-from-redundancy-math)
- [Anti-Patterns](#anti-patterns)
  - [AP1 — MTTR Measured from Detection, Not Occurrence](#ap1--mttr-measured-from-detection-not-occurrence)
  - [AP2 — Single-Window Burn-Rate Alert (Missing Slow-Burn Signal)](#ap2--single-window-burn-rate-alert-missing-slow-burn-signal)
  - [AP3 — Treating Post-Deploy as Steady-State (Bathtub Blindness)](#ap3--treating-post-deploy-as-steady-state-bathtub-blindness)
  - [AP4 — Alerting on Intermediate FTA Events Instead of Top Events](#ap4--alerting-on-intermediate-fta-events-instead-of-top-events)
- [Recipes](#recipes)
  - [R1 — MTBF/MTTR Dashboard with Post-Incident MTTR Decomposition](#r1--mtbfmttr-dashboard-with-post-incident-mttr-decomposition)
  - [R2 — Multi-Window Burn-Rate Alert Stack](#r2--multi-window-burn-rate-alert-stack)
  - [R3 — FMEA-Derived Instrumentation Coverage Audit](#r3--fmea-derived-instrumentation-coverage-audit)
- [Cross-References](#cross-references)

---

## Why Reliability Theory

Reliability theory was developed to answer a narrow question: will this component still be working at time t? Applied to observability, the question expands: do we have enough telemetry to know whether the service is working, to predict when it will fail, and to recover quickly when it does?

The primitives supply five concrete capabilities that observability practice frequently gets wrong by improvising:

1. **Quantitative failure accounting** — MTBF/MTTR (#01) turns post-mortems into a trend line, not a list of stories.
2. **Budget arithmetic** — Error budgets (#08) make SLO design a calculation, not a negotiation.
3. **Phase-aware alerting** — Hazard functions (#03) and the bathtub curve (#04) explain why new deployments need tighter alert thresholds than stable services.
4. **Coverage completeness** — Fault trees (#05) and FMEA (#06) supply a systematic method for finding instrumentation gaps before incidents expose them.
5. **Headroom math** — Redundancy math (#07) and reliability allocation (#11) make it possible to set per-service SLO targets that compose correctly to a system-level SLO.

---

## Patterns

### P1 — MTBF/MTTR Dashboard from Incident Store

**Primitives**: [01 — MTBF and MTTR](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md), [02 — Availability Formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md)

**Problem it solves**: Incident post-mortems produce narrative artefacts but rarely produce numerical trend data. Without tracking MTBF and MTTR as time-series metrics, a team cannot tell whether reliability is improving, degrading, or merely fluctuating.

**Mechanism**:

Derive four metrics from the incident store (PagerDuty, Opsgenie, Jira Incidents, or any structured event log) using two timestamps per incident: `occurred_at` and `resolved_at`.

```
MTBF(window) = total_up_time(window) / incident_count(window)
MTTR(window) = sum(resolved_at - occurred_at) / incident_count(window)

Availability(window) = MTBF / (MTBF + MTTR)
```

Report each metric as a 30-day rolling value updated daily. Expose as Prometheus gauges so they join the rest of the observability stack:

```python
# Minimal incident-store exporter — reads from a structured incident log
from prometheus_client import Gauge

mtbf_gauge   = Gauge("service_mtbf_hours_30d",   "30-day rolling MTBF", ["service"])
mttr_gauge   = Gauge("service_mttr_minutes_30d",  "30-day rolling MTTR", ["service"])
avail_gauge  = Gauge("service_availability_30d",  "30-day availability derived from MTBF/MTTR", ["service"])

def update_reliability_metrics(service: str, incidents: list[dict]) -> None:
    """incidents: list of {"occurred_at": datetime, "resolved_at": datetime}"""
    window_hours = 30 * 24
    count = len(incidents)
    if count == 0:
        mtbf_gauge.labels(service=service).set(window_hours)
        mttr_gauge.labels(service=service).set(0)
        avail_gauge.labels(service=service).set(1.0)
        return
    total_down_hours = sum(
        (i["resolved_at"] - i["occurred_at"]).total_seconds() / 3600
        for i in incidents
    )
    total_up_hours = window_hours - total_down_hours
    mtbf = total_up_hours / count
    mttr_minutes = (total_down_hours / count) * 60
    availability = mtbf / (mtbf + total_down_hours / count)
    mtbf_gauge.labels(service=service).set(mtbf)
    mttr_gauge.labels(service=service).set(mttr_minutes)
    avail_gauge.labels(service=service).set(availability)
```

**Dashboard panels** (Grafana):

| Panel | Query | Purpose |
|-------|-------|---------|
| MTBF trend | `service_mtbf_hours_30d` | Is the service failing less often? |
| MTTR trend | `service_mttr_minutes_30d` | Is the team recovering faster? |
| Derived availability | `service_availability_30d` | Does calculated availability match SLO target? |
| Availability gap | `service_availability_30d - slo_target_ratio` | How much headroom before SLO breach? |

**Key distinction from primitive #01**: measure `occurred_at` from the first anomalous data point in traces or logs (the real failure start), not from when an alert fired. Measuring MTTR from alert fire systematically undercounts the detect-and-diagnose phase, which is often the longest segment.

---

### P2 — SLO Burn-Rate Alerting Derived from Error Budgets

**Primitives**: [08 — Error Budgets](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md), [02 — Availability Formulas](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md)

**Problem it solves**: Raw error rate thresholds do not tell you whether the current incident pace will exhaust the SLO. Error budget arithmetic converts availability math into a concrete spend/remaining signal, and burn-rate ratios convert that into page-worthy thresholds with defined urgency levels.

**Mechanism**:

```
Monthly error budget  = (1 - SLO_target) × 43,200 min   # 30-day window: 30 × 24 × 60
Burn rate             = current_error_rate / (1 - SLO_target)

Burn rate = 1.0   → consuming budget at exactly the sustainable pace
Burn rate = 14.4  → budget exhausted in 30d × 24h / 14.4 = 50 hours
Burn rate = 36    → budget exhausted in 20 hours
```

The Google SRE Workbook (Chapter 5, "Alerting on SLOs") burn-rate table has four rows collapsing into two urgency tiers (Page, Ticket). This table must stay consistent with the same table in [`slo-design-guide.md`](slo-design-guide.md#burn-rate-alerts) and [`alerting-strategies.md`](alerting-strategies.md#multi-window-burn-rate-alerts) — if you edit one, edit all three:

| Tier | Burn rate | Budget consumed in window | Action |
|------|-----------|--------------------------|--------|
| Page | > 14.4× over 1h | > 2% in 1h | Immediate page |
| Page | > 6× over 6h | > 5% in 6h | Immediate page |
| Ticket | > 3× over 1d | > 10% in 1d | Next-business-day ticket |
| Ticket | > 1× over 3d | > 10% in 3d | Reliability review |

Prometheus recording and alert rules:

```yaml
# Recording rules — pre-compute per-window error ratios
- record: job:http_error_ratio:1h
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[1h])) by (job)
    / sum(rate(http_requests_total[1h])) by (job)

- record: job:http_error_ratio:6h
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[6h])) by (job)
    / sum(rate(http_requests_total[6h])) by (job)

# SLO = 99.9%, error budget rate = 0.001
- record: job:slo_burn_rate:1h
  expr: job:http_error_ratio:1h / 0.001

- record: job:slo_burn_rate:6h
  expr: job:http_error_ratio:6h / 0.001

# Alert rules
- alert: SloBurnRateCritical
  expr: |
    job:slo_burn_rate:1h > 14.4
    and
    job:slo_burn_rate:6h > 6
  labels:
    severity: critical
  annotations:
    summary: "SLO budget burning fast — exhaustion in < 50h"

- alert: SloBurnRateWarning
  expr: |
    job:slo_burn_rate:6h > 3
    and
    job:slo_burn_rate:1h > 1
  labels:
    severity: warning
  annotations:
    summary: "Elevated SLO burn — investigate before budget exhaustion"
```

The `and` conjunction between the two windows is the multi-window confirmation: a spike in the 1h window that does not persist to the 6h window is transient noise, not a burn-rate incident.

---

### P3 — Hazard Rate Alerting on Aging Deployments

**Primitives**: [03 — Hazard Functions](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md), [04 — Bathtub Curve](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md), [09 — Weibull Analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/09-weibull-analysis.md)

**Problem it solves**: A single static alert threshold ignores the fact that a service has different failure probabilities at different stages of its deployment lifecycle. A new deploy sits in Phase I (infant mortality) with elevated hazard rate. A stable long-running service that has not been deployed in 90 days may be entering Phase III (wear-out) through dependency drift, memory accumulation, or expiring certificates.

**Mechanism**:

Emit a deployment age metric and layer alert thresholds against known hazard phases:

```yaml
# Record deployment age in seconds (from deployment timestamp label)
- record: job:deployment_age_hours
  expr: (time() - kube_deployment_created) / 3600

# Phase I: infant mortality window — tighten error budget threshold
# First 2 hours after deploy: burn-rate threshold halved (Phase I hazard is elevated)
- alert: PostDeployInfantMortality
  expr: |
    job:slo_burn_rate:1h > 7.2            # half of normal critical threshold
    and
    job:deployment_age_hours < 2
  labels:
    severity: critical
    phase: infant_mortality
  annotations:
    summary: "Post-deploy error burst in infant mortality window (< 2h)"
    runbook: "https://runbooks.example.com/post-deploy-infant-mortality"

# Phase III: wear-out signal — flag aging deployments for proactive rollout
- alert: DeploymentAgeWearoutRisk
  expr: job:deployment_age_hours > 720    # 30 days without re-deploy
  labels:
    severity: warning
    phase: wear_out
  annotations:
    summary: "Deployment age > 30 days — elevated wear-out risk"
    reason: "Dependency drift, log rotation edge cases, or certificate expiry likely"
```

**Phase-aware canary logic**: during the infant mortality window, route canary traffic to the old version while the new version is observed. Promote only after the hazard rate drops below the steady-state baseline. This maps directly to the bathtub curve Phase I mitigation: accelerated burn-in before full promotion.

```python
# Phase I boundary estimation — compare pre- and post-deploy error rates
def deployment_phase(deploy_age_hours: float, error_rate_now: float,
                     baseline_error_rate: float) -> str:
    if deploy_age_hours < 2 and error_rate_now > baseline_error_rate * 2:
        return "infant_mortality"
    if deploy_age_hours > 720:
        return "wear_out_risk"
    return "useful_life"
```

---

### P4 — Observability Coverage for Fault-Tree Top Events

**Primitive**: [05 — Fault Tree Analysis](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md)

**Problem it solves**: Alert designs typically emerge bottom-up: "this metric spiked during an incident, so alert on it." This produces alert coverage for symptoms that were once observed, but misses entire failure branches that have not yet occurred. FTA supplies a top-down method to enumerate all paths to a top event and then check whether each path has telemetry coverage.

**Mechanism**:

1. Define the top event as a measurable, threshold-bounded system state (e.g., "checkout API returns 5xx for > 60s").
2. Build the fault tree. Every leaf (basic event) must map to either an existing alert or an instrumentation gap.
3. Produce a coverage matrix: basic event → alert rule (or "UNMONITORED").

```
Top event: checkout API returns 5xx > 60s
└─ OR
   ├─ Payment provider unreachable                 → ALERT: payment_provider_health < 1
   ├─ Database write timeout                       → ALERT: db_write_p99_ms > 500
   ├─ JWT signing key unavailable (KMS outage)     → UNMONITORED — gap
   └─ App tier fully saturated (CPU > 95%)         → ALERT: cpu_saturation_pct > 90
```

Every UNMONITORED leaf is an instrumentation gap. Priority for closing the gap is proportional to the leaf's Fussell-Vesely importance (fraction of top-event probability it contributes).

**Implementation output**: a gap register that feeds the work backlog:

| Basic event | Fault tree path | Current coverage | Gap action |
|-------------|----------------|------------------|------------|
| KMS outage | Payment → JWT signing key | No alert | Add KMS reachability probe + alert on `kms_api_errors_total` |
| DNS resolution failure | All tiers | Partial (only app tier) | Add resolver latency metric to infra layer |
| Disk full on log volume | App tier crash | No alert | Add `node_filesystem_avail_bytes` alert at 15% free |

---

### P5 — FMEA-Driven Instrumentation Gaps Audit

**Primitive**: [06 — FMEA](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md)

**Problem it solves**: Instrumentation is typically added reactively (after incidents) or aspirationally (everything that seems useful). Neither approach answers: which failure modes have no detection at all? FMEA's Detection (D) score directly quantifies the gap between a failure mode occurring and the team knowing about it.

**Mechanism**:

Run FMEA against each critical service. Score the Detection factor specifically against observability controls: does a metric, alert, trace, or log capture this failure mode before it produces customer impact?

Detection scoring for observability contexts:

| D score | Detection description |
|---------|-----------------------|
| 1–2 | Alert fires before user impact; trace captures root cause automatically |
| 3–4 | Alert fires after brief user impact; correlated log identifies the component |
| 5–6 | Alert fires but requires 10+ min manual investigation in dashboards |
| 7–8 | No alert; failure visible only by examining raw logs or metrics manually |
| 9–10 | No telemetry; failure discovered by user report or external monitor |

The instrumentation gap audit extracts all rows with D ≥ 7 — these are the failure modes with no meaningful detection:

```python
def fmea_instrumentation_gaps(fmea_rows: list[dict]) -> list[dict]:
    """
    Returns FMEA rows where detection is poor (D >= 7) sorted by RPN descending.
    Each row must have: component, failure_mode, severity (S), occurrence (O), detection (D).
    """
    gaps = [
        {**row, "rpn": row["S"] * row["O"] * row["D"]}
        for row in fmea_rows
        if row["D"] >= 7
    ]
    return sorted(gaps, key=lambda r: r["rpn"], reverse=True)
```

**Output**: a prioritised instrumentation backlog where each item has a concrete observability action (add metric, add alert, add trace attribute, add structured log field).

Example output for a checkout service audit:

| Component | Failure mode | S | O | D | RPN | Observability action |
|-----------|-------------|---|---|---|-----|---------------------|
| Payment API | Silent timeout (no 5xx returned) | 9 | 5 | 9 | 405 | Add circuit-breaker open metric + alert |
| Auth cache | Key eviction storm | 7 | 4 | 8 | 224 | Add cache eviction rate metric to golden signals |
| Message queue | Dead letter accumulation | 8 | 3 | 8 | 192 | Alert on DLQ depth > 100 messages |
| DB connection pool | Pool exhaustion | 8 | 3 | 5 | 120 | (existing pool size metric — gap closed) |

---

### P6 — Multi-Window Burn-Rate Alerting from Redundancy Math

**Primitives**: [07 — Redundancy Math](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md), [11 — Reliability Allocation](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md)

**Problem it solves**: A single burn-rate alert window is an unreliable detector. A short window (1h) catches fast burns but generates false positives from noise spikes. A long window (6h) catches slow burns but misses fast exhaustion events. Neither is sufficient alone. Redundancy math explains why parallel detectors with independent windows dramatically improve detection reliability without proportionally increasing false positives.

**Mechanism**:

Model each burn-rate window as a detector with its own sensitivity and false-positive rate:

```
P(detection | real incident) per window:
  1h window:  P_detect = 0.85  (fast, slightly noisy)
  6h window:  P_detect = 0.70  (slower, less noise)
  combined (OR logic):  P_detect = 1 - (1-0.85)(1-0.70) = 1 - 0.045 = 0.955

P(false positive) per window:
  1h window:  P_fp = 0.08
  6h window:  P_fp = 0.03
  combined (AND logic): P_fp = 0.08 × 0.03 = 0.0024
```

The critical alert uses AND logic (both windows must fire) — this exploits the redundancy-math parallel formula for false positives while the OR detection logic ensures neither fast nor slow burns are missed by the other window. The tiered alert stack implements the full reliability allocation (#11) across detection components:

```
CRITICAL tier (AND):  1h window > 14.4× AND 6h window > 6×
  → high confidence; both fast and sustained burn confirmed
  → pages on-call immediately

WARNING tier (OR):    6h window > 3× OR 1h window > 7.2×
  → either window firing alone; one signal may indicate early burn
  → creates ticket, no page

TREND tier:           3d window burn rate > 1.5×
  → slow bleed; budget will be exhausted within the month
  → weekly reliability review agenda item
```

**Reliability allocation for the detection system itself**: each tier has an allocated false-negative budget (allowed missed incidents). If the CRITICAL tier must miss < 5% of genuine incidents, and the 1h window alone misses 15%, the AND logic with the 6h window misses 15% × 30% = 4.5% — within budget. Tune the window thresholds and `for` durations to stay within the allocated false-negative budget.

---

## Anti-Patterns

### AP1 — MTTR Measured from Detection, Not Occurrence

**Description**: MTTR is calculated as `resolved_at - alerted_at` rather than `resolved_at - occurred_at`. Dashboards show impressive MTTR figures (e.g., 8 minutes) that exclude the time from the real failure to the first alert.

**Reliability theory diagnosis**: Primitive #01 explicitly warns: "Measuring MTTR from detection, not from occurrence understates true repair burden; hides detection lag." The detection lag is part of the total user impact window and must be measured separately as MTTD (Mean Time to Detect).

**Consequence**: Teams optimise alert-to-resolve time while ignoring that the alert fires 30 minutes after the failure. The SLO breach window is (MTTD + MTTR), not just MTTR.

**Fix**: Record three timestamps per incident: `occurred_at` (first anomalous signal in telemetry), `alerted_at` (first page), and `resolved_at`. Track MTTD = `alerted_at − occurred_at` and MTTR = `resolved_at − alerted_at` separately. Report total incident duration as MTTD + MTTR.

```yaml
# Incident fields that must be populated (Jira/Linear incident template)
occurred_at:   # Required — first anomalous signal timestamp, from traces/logs
alerted_at:    # Required — timestamp of first PagerDuty page
resolved_at:   # Required — timestamp of service restored to SLO
```

---

### AP2 — Single-Window Burn-Rate Alert (Missing Slow-Burn Signal)

**Description**: Only a 1-hour burn-rate alert is configured. The alert fires correctly for fast outages but never fires for a slow memory leak consuming 5 minutes of error budget per day over three weeks.

**Reliability theory diagnosis**: A single detector has the combined false-negative profile of its window. Primitive #08 specifies multi-window burn rate explicitly: "Use multi-window burn rate: 1-hour and 6-hour windows alongside the monthly window." The slow burn exhausts the monthly budget in 9 days but the 1h window never exceeds the critical threshold.

**Consequence**: The SLO is breached at the end of the month. The team is surprised. Post-mortem attribution is difficult because no single incident was large enough to trigger an alert.

**Fix**: Implement at least three windows: 1h (fast burn), 6h (medium burn), and 3d (slow bleed). The 3d window catches gradual degradation that individually-scoped alerts miss. See Pattern P2 and Recipe R2.

---

### AP3 — Treating Post-Deploy as Steady-State (Bathtub Blindness)

**Description**: The same burn-rate thresholds and canary promotion criteria apply regardless of whether the service was deployed 10 minutes ago or 10 days ago.

**Reliability theory diagnosis**: Primitive #04 (bathtub curve) describes infant mortality as the dominant failure mechanism in the first hours after deployment. A service that produces a 0.2% error rate at 30 minutes post-deploy is in Phase I (elevated hazard, DFR) — this rate would be alarming at day 5, but it is normal burn-in behaviour. Applying steady-state thresholds to Phase I produces both false alarms (blocking legitimate deploys) and false confidence (missing real regressions masked by the noisy Phase I window).

**Consequence**: Either deploys are blocked by normal Phase I noise, or a real regression is missed because the team has learned to ignore post-deploy alerts as "probably just the canary settling."

**Fix**: Parameterise alert thresholds by deployment age. During the 2-hour infant mortality window, tighten error thresholds (P3) but gate on sustained duration rather than instantaneous spikes. After the Phase I window, revert to steady-state thresholds. Explicitly monitor for Phase III wear-out on services with deployment age > 30 days.

---

### AP4 — Alerting on Intermediate FTA Events Instead of Top Events

**Description**: Alerts are built around component metrics (CPU high, DB connection count elevated, queue depth growing) rather than around the top event (user-facing SLO breach). During an incident, five separate alerts fire for intermediate events while the top-event alert — the only one that matters for escalation — either does not exist or is buried.

**Reliability theory diagnosis**: Primitive #05 distinguishes between the top event (the customer-visible failure) and intermediate events (the path through the fault tree). Minimal cut sets identify which combinations of basic events cause the top event — individual events in a cut set do not cause it on their own when the gate is AND. Alerting on intermediate events produces noise without confirming that the top event has actually occurred.

**Consequence**: On-call engineers are overwhelmed by component alerts during an incident and must mentally perform the fault tree traversal that the alert system should have done for them. Alert fatigue accumulates; real incidents are missed.

**Fix**: Structure the alert hierarchy to mirror the fault tree. The top-level page alert is on the SLO burn rate (the top event). Intermediate component alerts are informational context, not pages. Use Alertmanager inhibition to suppress intermediate alerts while the top-event alert is firing. See also the control-theory-applied anti-pattern AP5 (competing alerts with no priority scheduling).

---

## Recipes

### R1 — MTBF/MTTR Dashboard with Post-Incident MTTR Decomposition

**Goal**: Build a Grafana dashboard that tracks MTBF and MTTR trends over 90 days and decomposes each incident's MTTR into detection, diagnosis, and mitigation phases.

**Primitives used**: #01 (MTBF/MTTR), #02 (availability formulas)

**Inputs**: Structured incident store with `occurred_at`, `alerted_at`, `diagnosed_at`, `mitigated_at`, `resolved_at` per incident.

**Step 1 — Define the five timestamps in incident tooling**

Require all five timestamps in your incident management tool. If `diagnosed_at` and `mitigated_at` are not captured, start with `occurred_at`, `alerted_at`, and `resolved_at` — these give MTTD and MTTR.

**Step 2 — Emit Prometheus gauges from the incident store**

```python
from prometheus_client import Gauge, Histogram
from datetime import datetime, timedelta
from typing import Optional

mttd_gauge = Gauge("service_mttd_minutes_30d",  "30-day rolling MTTD", ["service"])
mttr_gauge = Gauge("service_mttr_minutes_30d",  "30-day rolling MTTR", ["service"])
mtbf_gauge = Gauge("service_mtbf_hours_30d",    "30-day rolling MTBF", ["service"])
avail_gauge = Gauge("service_availability_30d", "Availability from MTBF/MTTR", ["service"])

phase_histogram = Histogram(
    "incident_phase_duration_minutes",
    "Duration of each incident phase",
    ["service", "phase"],
    buckets=[1, 5, 10, 30, 60, 120, 240, 480],
)

def process_incidents(service: str, incidents: list[dict]) -> None:
    """
    incidents: list of dicts with datetime fields:
      occurred_at, alerted_at, diagnosed_at (optional),
      mitigated_at (optional), resolved_at
    """
    window = timedelta(days=30)
    now = datetime.utcnow()
    recent = [i for i in incidents if i["occurred_at"] >= now - window]
    count = len(recent)

    if count == 0:
        mtbf_gauge.labels(service=service).set(30 * 24)
        mttr_gauge.labels(service=service).set(0)
        mttd_gauge.labels(service=service).set(0)
        avail_gauge.labels(service=service).set(1.0)
        return

    total_down_min = sum(
        (i["resolved_at"] - i["occurred_at"]).total_seconds() / 60
        for i in recent
    )
    total_detect_min = sum(
        (i["alerted_at"] - i["occurred_at"]).total_seconds() / 60
        for i in recent
    )
    total_window_min = 30 * 24 * 60

    mtbf_h = (total_window_min - total_down_min) / 60 / count
    mttr_m = total_down_min / count
    mttd_m = total_detect_min / count
    avail = mtbf_h / (mtbf_h + (total_down_min / count / 60))

    mtbf_gauge.labels(service=service).set(mtbf_h)
    mttr_gauge.labels(service=service).set(mttr_m)
    mttd_gauge.labels(service=service).set(mttd_m)
    avail_gauge.labels(service=service).set(avail)

    # Per-incident phase decomposition
    for i in recent:
        detect_m = (i["alerted_at"] - i["occurred_at"]).total_seconds() / 60
        phase_histogram.labels(service=service, phase="detect").observe(detect_m)
        if i.get("diagnosed_at"):
            diag_m = (i["diagnosed_at"] - i["alerted_at"]).total_seconds() / 60
            phase_histogram.labels(service=service, phase="diagnose").observe(diag_m)
        if i.get("mitigated_at"):
            mitig_m = (i["mitigated_at"] - i.get("diagnosed_at", i["alerted_at"])).total_seconds() / 60
            phase_histogram.labels(service=service, phase="mitigate").observe(mitig_m)
        resolve_start = i.get("mitigated_at") or i.get("diagnosed_at") or i["alerted_at"]
        resolve_m = (i["resolved_at"] - resolve_start).total_seconds() / 60
        phase_histogram.labels(service=service, phase="resolve").observe(resolve_m)
```

**Step 3 — Dashboard panels**

| Panel | Query | Insight |
|-------|-------|---------|
| MTBF 90-day trend | `service_mtbf_hours_30d` | Is failure frequency improving? |
| MTTR 90-day trend | `service_mttr_minutes_30d` | Is recovery speed improving? |
| MTTD 90-day trend | `service_mttd_minutes_30d` | Is detection speed improving? |
| Detect vs. diagnose vs. resolve split | `histogram_quantile(0.5, incident_phase_duration_minutes_bucket)` per phase | Where is MTTR time actually spent? |
| Availability vs. SLO | `service_availability_30d` vs. SLO target line | Is calculated availability above SLO? |

**Step 4 — Post-incident review action**

In each post-mortem, identify which phase drove MTTR. If detect > 20 min: add or tune alerts. If diagnose > 30 min: add trace attributes or structured log fields. If resolve > 60 min: review runbooks and runbook automation.

**Verify**: MTTD improves after new alert rules are added. MTTR detect-phase drops within 2 months of runbook automation for the top 3 failure modes. Derived `service_availability_30d` matches the SLO dashboard ± 0.01%.

---

### R2 — Multi-Window Burn-Rate Alert Stack

**Goal**: Implement the complete multi-window, multi-tier SLO burn-rate alert stack for a 99.9% SLO, covering fast burn, medium burn, and slow bleed with appropriate urgency tiers and notification routing.

**Primitives used**: #08 (error budgets), #07 (redundancy math for detection reliability)

**Inputs**: Prometheus with `http_requests_total` labelled by status code; Alertmanager; SLO = 99.9%.

**Step 1 — Recording rules**

```yaml
groups:
  - name: slo_recording
    interval: 60s
    rules:
      # Error ratios by window
      - record: job:http_error_ratio:1h
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[1h])) by (job)
          / sum(rate(http_requests_total[1h])) by (job)

      - record: job:http_error_ratio:6h
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[6h])) by (job)
          / sum(rate(http_requests_total[6h])) by (job)

      - record: job:http_error_ratio:1d
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[1d])) by (job)
          / sum(rate(http_requests_total[1d])) by (job)

      - record: job:http_error_ratio:3d
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[3d])) by (job)
          / sum(rate(http_requests_total[3d])) by (job)

      # Burn rates (error ratio / error budget rate; budget rate = 1 - SLO = 0.001)
      - record: job:slo_burn_rate:1h
        expr: job:http_error_ratio:1h / 0.001

      - record: job:slo_burn_rate:6h
        expr: job:http_error_ratio:6h / 0.001

      - record: job:slo_burn_rate:1d
        expr: job:http_error_ratio:1d / 0.001

      - record: job:slo_burn_rate:3d
        expr: job:http_error_ratio:3d / 0.001

      # Budget remaining (fraction of monthly budget left)
      - record: job:slo_budget_remaining:30d
        expr: |
          1 - (
            sum_over_time(job:http_error_ratio:1h[30d])
            / count_over_time(job:http_error_ratio:1h[30d])
          ) / 0.001
```

**Step 2 — Alert rules**

```yaml
groups:
  - name: slo_burn_alerts
    rules:
      # CRITICAL — fast burn: 2% budget in 1h (14.4x) AND 5% in 6h (6x)
      - alert: SloBurnCriticalFast
        expr: |
          job:slo_burn_rate:1h > 14.4
          and
          job:slo_burn_rate:6h > 6
        for: 2m
        labels:
          severity: critical
          burn_tier: fast
        annotations:
          summary: "SLO fast burn — exhaustion in < 50h if sustained"
          budget_consumed_1h: "{{ $value | humanize }}× burn rate"

      # WARNING — medium burn: 10% budget in 6h (3x) with 1h confirmation
      - alert: SloBurnWarningMedium
        expr: |
          job:slo_burn_rate:6h > 3
          and
          job:slo_burn_rate:1h > 1
        for: 5m
        labels:
          severity: warning
          burn_tier: medium
        annotations:
          summary: "SLO medium burn — investigate before budget exhaustion"

      # TICKET — slow bleed: > 1.5x sustained over 3 days
      - alert: SloBurnSlowBleed
        expr: job:slo_burn_rate:3d > 1.5
        for: 30m
        labels:
          severity: info
          burn_tier: slow
        annotations:
          summary: "SLO slow bleed — budget will be exhausted before month end"
          projection: "At current rate, budget exhausted in {{ (1 / $value * 30) | humanize }} days"
```

**Step 3 — Alertmanager routing**

```yaml
route:
  group_by: ["job", "burn_tier"]
  receiver: "default"
  routes:
    - match:
        severity: critical
      receiver: "pagerduty-oncall"
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 1h

    - match:
        severity: warning
      receiver: "slack-incidents"
      group_wait: 5m
      repeat_interval: 4h

    - match:
        severity: info
        burn_tier: slow
      receiver: "jira-ticket"
      group_wait: 30m
      repeat_interval: 24h
```

**Step 4 — Low-traffic service adjustment**

For services with < 10 requests/minute, the 1h window may contain too few events for a stable error ratio. Use event-count-based budget tracking instead:

```yaml
# Minimum event threshold before burn-rate alert is valid
- alert: SloBurnCriticalFast
  expr: |
    job:slo_burn_rate:1h > 14.4
    and job:slo_burn_rate:6h > 6
    and sum(rate(http_requests_total[1h])) by (job) > 0.1  # at least 1 req/10s
```

**Verify**: CRITICAL alert fires within 5 minutes of a simulated 100% error injection. CRITICAL alert does not fire during a 10-second spike to 50% errors followed by recovery. SloBurnSlowBleed fires when 2% of requests fail continuously for > 4 hours.

---

### R3 — FMEA-Derived Instrumentation Coverage Audit

**Goal**: Systematically identify instrumentation gaps by running FMEA against a service's failure modes and scoring Detection (D) against current observability controls. Produce a prioritised backlog of instrumentation work.

**Primitives used**: #06 (FMEA), #05 (FTA for gap cross-validation)

**Inputs**: Service architecture diagram, existing alert rules, existing dashboard panels, recent post-mortems.

**Step 1 — Enumerate failure modes**

Run a 2-hour FMEA sprint per service. For each component, enumerate failure modes. Focus on the interfaces (what happens when this component cannot reach its dependency?) rather than internal implementation.

**Step 2 — Score Detection against observability controls**

For each failure mode, evaluate whether an alert fires before user impact (D = 1–3), after brief impact (D = 4–6), or not at all (D = 7–10).

```python
DETECTION_RUBRIC = {
    "alert_before_impact": 2,        # alert fires before users affected
    "alert_after_brief_impact": 4,   # alert fires within 5 min of impact
    "metric_exists_no_alert": 6,     # metric visible in dashboard; no alert
    "log_only_no_metric": 8,         # failure visible in raw logs only
    "no_telemetry": 10,              # no telemetry; user report required
}
```

**Step 3 — Compute RPN and filter gaps**

```python
import json
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FmeaRow:
    component: str
    failure_mode: str
    severity: int          # S: 1-10
    occurrence: int        # O: 1-10
    detection: int         # D: 1-10
    current_controls: str
    gap_action: Optional[str] = None

    @property
    def rpn(self) -> int:
        return self.severity * self.occurrence * self.detection

def instrumentation_gaps_audit(rows: list[FmeaRow],
                                detection_threshold: int = 7) -> list[FmeaRow]:
    """Return rows with poor detection, sorted by RPN descending."""
    gaps = [r for r in rows if r.detection >= detection_threshold]
    return sorted(gaps, key=lambda r: r.rpn, reverse=True)

def print_audit_report(gaps: list[FmeaRow]) -> None:
    print(f"{'Component':<20} {'Failure Mode':<35} {'S':>2} {'O':>2} {'D':>2} {'RPN':>4}  Gap Action")
    print("-" * 100)
    for g in gaps:
        print(f"{g.component:<20} {g.failure_mode:<35} {g.severity:>2} "
              f"{g.occurrence:>2} {g.detection:>2} {g.rpn:>4}  {g.gap_action or 'TBD'}")
```

**Step 4 — Cross-validate gaps against the fault tree**

For each D ≥ 7 row, check whether the failure mode appears as a leaf event in the service's fault tree. If it does, its Fussell-Vesely importance score provides an additional priority weight. Gaps that appear in high-importance minimal cut sets (especially single-element cut sets — SPOFs) are critical to close immediately.

**Step 5 — Create instrumentation backlog items**

Convert each gap into a concrete work item with defined acceptance criteria:

```
Gap: Silent payment timeout (D=9, RPN=405)
Action: Add circuit-breaker state metric `payment_circuit_state` (open/closed/half-open)
        + alert: payment_circuit_state == "open" for > 30s
AC: Alert fires within 60s of circuit opening in staging test; trace spans carry
    `http.resend_count` attribute for retry detection.
```

**Verify**: After each instrumentation work item ships, re-score Detection for that failure mode. Target: all S ≥ 8 failure modes reach D ≤ 4 within two sprint cycles. Quarterly re-run to catch new failure modes introduced by architecture changes.

---

## Cross-References

| Need | Reference |
|------|-----------|
| Foundation primitives for all formulas cited above | [`foundations-reliability-theory`](../../foundations-reliability-theory/SKILL.md) |
| MTBF/MTTR primitive (P1, R1) | [`01-mtbf-mttr.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/01-mtbf-mttr.md) |
| Availability formulas (P1, P6, R1) | [`02-availability-formulas.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/02-availability-formulas.md) |
| Hazard functions (P3, AP3) | [`03-hazard-functions.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/03-hazard-functions.md) |
| Bathtub curve (P3, AP3) | [`04-bathtub-curve.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/04-bathtub-curve.md) |
| Fault tree analysis (P4, AP4, R3) | [`05-fault-tree-analysis.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/05-fault-tree-analysis.md) |
| FMEA (P5, R3) | [`06-fmea.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/06-fmea.md) |
| Redundancy math (P6) | [`07-redundancy-math.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/07-redundancy-math.md) |
| Error budgets (P2, AP2, R2) | [`08-error-budgets.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/08-error-budgets.md) |
| Reliability allocation (P6) | [`11-reliability-allocation.md`](../../foundations-reliability-theory/assets/templates/reliability-theory/11-reliability-allocation.md) |
| SLO design guide (burn-rate context) | [`slo-design-guide.md`](slo-design-guide.md) |
| Alert design and fatigue reduction | [`alerting-strategies.md`](alerting-strategies.md) |
| Control theory feedback loops in alerting | [`control-theory-applied.md`](control-theory-applied.md) |
| Information theory applied to alert noise | [`information-theory-applied.md`](information-theory-applied.md) |
| Queueing theory applied to latency budgets | [`queueing-theory-applied.md`](queueing-theory-applied.md) |
| SLO alert rule templates | [`../assets/monitoring/slo/prometheus-alert-rules.yaml`](../assets/monitoring/slo/prometheus-alert-rules.yaml) |
