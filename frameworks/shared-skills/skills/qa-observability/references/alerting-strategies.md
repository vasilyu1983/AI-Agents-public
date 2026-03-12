# Alerting Strategies

Alert design, routing, and fatigue reduction for production systems. Build alerts that are actionable, not noisy.

## Contents

- [Alerting Philosophy](#alerting-philosophy)
- [Multi-Window Burn-Rate Alerts](#multi-window-burn-rate-alerts)
- [Alert Severity Levels](#alert-severity-levels)
- [Routing and Escalation](#routing-and-escalation)
- [Alert Fatigue Reduction](#alert-fatigue-reduction)
- [Alert-on-SLO-Burn Approach](#alert-on-slo-burn-approach)
- [Actionable Alert Templates](#actionable-alert-templates)
- [On-Call Rotation Best Practices](#on-call-rotation-best-practices)
- [Alert Testing and Validation](#alert-testing-and-validation)
- [Alert Coverage Audit Checklist](#alert-coverage-audit-checklist)
- [Related Resources](#related-resources)

---

## Alerting Philosophy

### Symptom-Based, Not Cause-Based

Alert on what users experience, not on infrastructure internals.

| Approach | Example | Problem |
|----------|---------|---------|
| **Cause-based** (avoid) | CPU > 80% | CPU can be high without user impact |
| **Cause-based** (avoid) | Disk > 90% | May not affect anything for days |
| **Symptom-based** (prefer) | Error rate > 1% | Users are seeing errors |
| **Symptom-based** (prefer) | P99 latency > 2s | Users are experiencing slowness |
| **SLO-based** (best) | Error budget burn rate > 6x | User experience is degrading at an unsustainable rate |

### Core Principles

1. **Every alert must be actionable** -- if there is no action to take, it should not page someone
2. **Alerts should have runbooks** -- link to resolution steps in the alert itself
3. **Prefer fewer, higher-quality alerts** -- one good SLO alert replaces ten infrastructure alerts
4. **Alert on rates, not absolutes** -- "error rate > 5%" not "errors > 100"
5. **Use appropriate urgency** -- not everything is a page; most things are tickets

### Alert Decision Tree

```
Is a user affected right now?
├── Yes → Is it urgent (revenue, safety, data)?
│   ├── Yes → PAGE (P1/P2)
│   └── No → TICKET (P3)
└── No → Will a user be affected soon?
    ├── Yes (< 24h) → TICKET (P3)
    └── No → DASHBOARD only (P4)
```

---

## Multi-Window Burn-Rate Alerts

Multi-window alerts reduce false positives by requiring sustained error rates across two time windows.

### How Multi-Window Works

```
Single-window alert (noisy):
  "Error rate > threshold for 5 minutes" → fires on brief spikes

Multi-window alert (precise):
  "Error rate > threshold for BOTH 1 hour AND 5 minutes"
  → Long window catches sustained issues
  → Short window confirms issue is current (not just historical)
```

### Prometheus Implementation

```yaml
# prometheus-rules.yaml
groups:
  - name: slo-burn-rate-alerts
    rules:
      # P1: Fast burn - 2% of 30-day budget in 1 hour
      # Long window: 1h at 14.4x burn rate
      # Short window: 5m at 14.4x burn rate
      - alert: SLOBurnRateCritical
        expr: |
          (
            (1 - rate(http_requests_total{status!~"5.."}[1h])
             / rate(http_requests_total[1h]))
            > (14.4 * 0.001)
          )
          and
          (
            (1 - rate(http_requests_total{status!~"5.."}[5m])
             / rate(http_requests_total[5m]))
            > (14.4 * 0.001)
          )
        for: 2m
        labels:
          severity: critical
          team: "{{ $labels.team }}"
        annotations:
          summary: "Critical SLO burn rate for {{ $labels.service }}"
          description: >
            Service {{ $labels.service }} is consuming error budget at 14.4x
            the sustainable rate. At this pace, the 30-day error budget will
            be exhausted in ~50 hours.
          runbook: "https://runbooks.example.com/slo-burn-critical"
          dashboard: "https://grafana.example.com/d/slo-overview"

      # P2: Medium burn - 5% of budget in 6 hours
      - alert: SLOBurnRateHigh
        expr: |
          (
            (1 - rate(http_requests_total{status!~"5.."}[6h])
             / rate(http_requests_total[6h]))
            > (6 * 0.001)
          )
          and
          (
            (1 - rate(http_requests_total{status!~"5.."}[30m])
             / rate(http_requests_total[30m]))
            > (6 * 0.001)
          )
        for: 15m
        labels:
          severity: warning
          team: "{{ $labels.team }}"
        annotations:
          summary: "High SLO burn rate for {{ $labels.service }}"
          runbook: "https://runbooks.example.com/slo-burn-high"

      # P3: Slow burn - 10% of budget in 3 days
      - alert: SLOBurnRateSlow
        expr: |
          (
            (1 - rate(http_requests_total{status!~"5.."}[3d])
             / rate(http_requests_total[3d]))
            > (1 * 0.001)
          )
          and
          (
            (1 - rate(http_requests_total{status!~"5.."}[6h])
             / rate(http_requests_total[6h]))
            > (1 * 0.001)
          )
        for: 1h
        labels:
          severity: info
          team: "{{ $labels.team }}"
        annotations:
          summary: "Slow SLO burn rate for {{ $labels.service }}"
          runbook: "https://runbooks.example.com/slo-burn-slow"
```

### Burn Rate Reference Table

| Alert Level | Long Window | Short Window | Burn Rate | Budget Consumed | Time to Exhaustion |
|------------|-------------|--------------|-----------|-----------------|-------------------|
| Critical (P1) | 1h | 5m | 14.4x | 2% in 1h | ~50 hours |
| High (P2) | 6h | 30m | 6x | 5% in 6h | ~5 days |
| Slow (P3) | 3d | 6h | 1x | 10% in 3d | ~30 days |

---

## Alert Severity Levels

### Severity Definitions

| Level | Name | Response Time | Notification | Examples |
|-------|------|--------------|--------------|----------|
| **P1** | Critical | < 5 min | Page on-call immediately | Service down, data loss, security breach |
| **P2** | High | < 30 min | Page on-call during business hours; Slack + ticket off-hours | Degraded performance, partial outage, SLO burn > 6x |
| **P3** | Medium | < 4 hours | Slack notification + ticket | Slow burn, capacity warning, non-critical errors |
| **P4** | Low | Next business day | Ticket only | Minor issues, cosmetic errors, optimization opportunities |

### Severity Assignment Criteria

```python
"""
Determine alert severity based on user impact and urgency.
"""

def determine_severity(
    users_affected_pct: float,
    is_revenue_impacting: bool,
    is_data_loss_risk: bool,
    is_security_incident: bool,
    can_wait_hours: bool,
) -> str:
    # P1: Immediate page
    if is_security_incident:
        return "P1"
    if is_data_loss_risk:
        return "P1"
    if users_affected_pct > 50 and is_revenue_impacting:
        return "P1"

    # P2: Urgent but not emergency
    if users_affected_pct > 10:
        return "P2"
    if is_revenue_impacting and not can_wait_hours:
        return "P2"

    # P3: Needs attention soon
    if users_affected_pct > 1:
        return "P3"
    if not can_wait_hours:
        return "P3"

    # P4: Track and fix
    return "P4"
```

---

## Routing and Escalation

### PagerDuty Configuration

```yaml
# pagerduty-service-config.yaml
services:
  - name: order-service
    escalation_policy:
      - level: 1
        targets:
          - type: schedule
            id: order-service-oncall
        escalation_timeout_minutes: 15

      - level: 2
        targets:
          - type: schedule
            id: platform-team-oncall
        escalation_timeout_minutes: 30

      - level: 3
        targets:
          - type: user
            id: engineering-manager
        escalation_timeout_minutes: 60

    alert_grouping:
      type: intelligent
      config:
        time_window: 300  # 5 minutes
        fields: ["service", "alert_name"]

    auto_resolve_timeout: 14400  # 4 hours
    acknowledgement_timeout: 1800  # 30 minutes
```

### Routing Rules

```yaml
# alertmanager.yaml (Prometheus Alertmanager)
route:
  receiver: default-slack
  group_by: ["alertname", "service", "namespace"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    # P1 Critical: page immediately
    - match:
        severity: critical
      receiver: pagerduty-critical
      group_wait: 10s
      repeat_interval: 5m
      continue: true

    # P1 also goes to Slack for visibility
    - match:
        severity: critical
      receiver: slack-incidents

    # P2 High: page during business hours, Slack always
    - match:
        severity: warning
      receiver: pagerduty-warning
      active_time_intervals:
        - business_hours
      continue: true

    - match:
        severity: warning
      receiver: slack-alerts

    # P3/P4: Slack and ticket only
    - match:
        severity: info
      receiver: slack-alerts

receivers:
  - name: pagerduty-critical
    pagerduty_configs:
      - routing_key: "<PAGERDUTY_CRITICAL_KEY>"
        severity: critical

  - name: pagerduty-warning
    pagerduty_configs:
      - routing_key: "<PAGERDUTY_WARNING_KEY>"
        severity: warning

  - name: slack-incidents
    slack_configs:
      - channel: "#incidents"
        title: "{{ .GroupLabels.alertname }}"
        text: "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"

  - name: slack-alerts
    slack_configs:
      - channel: "#alerts"
        title: "{{ .GroupLabels.alertname }}"
```

---

## Alert Fatigue Reduction

Alert fatigue is the number one killer of on-call effectiveness. When everything pages, nothing pages.

### Fatigue Reduction Strategies

| Strategy | Description | Impact |
|----------|-------------|--------|
| **Deduplication** | Group identical alerts into one notification | High |
| **Suppression** | Suppress child alerts when parent fires | High |
| **Grouping** | Batch related alerts into single notification | Medium |
| **Inhibition** | Suppress lower-severity alerts when higher fires | Medium |
| **Flap detection** | Suppress alerts that toggle rapidly | Medium |
| **Time-based routing** | Non-critical alerts only during business hours | Medium |
| **Alert review** | Quarterly review: delete, tune, or merge | High |

### Alertmanager Inhibition Rules

```yaml
# Suppress service-level alerts when cluster is down
inhibit_rules:
  - source_match:
      alertname: ClusterDown
    target_match_re:
      alertname: ".+"
    equal: ["namespace"]

  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ["alertname", "service"]
```

### Alert Audit Metrics

Track these metrics to detect and reduce fatigue:

```python
"""
Alert fatigue metrics. Track weekly and trend over time.
"""

FATIGUE_METRICS = {
    "total_alerts_fired": "Total alerts fired this week",
    "unique_alerts_fired": "Unique alert names that fired",
    "pages_per_oncall_shift": "Pages received per on-call shift",
    "acknowledged_within_sla": "% alerts acknowledged within target",
    "auto_resolved_pct": "% alerts that resolved without human action",
    "false_positive_pct": "% alerts that required no action",
    "mean_time_to_ack": "Average time from alert to acknowledgement",
    "repeat_offenders": "Alert names that fired > 5x in a week",
}

# Healthy targets
TARGETS = {
    "pages_per_oncall_shift": {"max": 2, "unit": "pages per 12h shift"},
    "false_positive_pct": {"max": 5, "unit": "%"},
    "auto_resolved_pct": {"max": 20, "unit": "%"},
    "acknowledged_within_sla": {"min": 95, "unit": "%"},
}
```

---

## Alert-on-SLO-Burn Approach

Replace infrastructure-based alerts with SLO-based alerts for fewer, higher-quality notifications.

### Before: Infrastructure Alerts (Noisy)

```yaml
# 15+ alerts per service, most not actionable
alerts:
  - CPU > 80%
  - Memory > 85%
  - Disk > 90%
  - GC pause > 500ms
  - Thread pool exhausted
  - Connection pool > 80%
  - Queue depth > 1000
  - Pod restarts > 3
  - Request count spike
  - Error count > 50
  - Latency P99 > 2s
  - 5xx rate > 1%
  - Health check failed
  - SSL cert expiring
  - DNS resolution slow
```

### After: SLO-Based Alerts (Focused)

```yaml
# 3 alerts per service, all actionable
alerts:
  - name: availability-slo-burn
    description: "Error budget burning faster than sustainable"
    windows: [1h/5m, 6h/30m, 3d/6h]
    action: "Check runbook, likely code or dependency issue"

  - name: latency-slo-burn
    description: "Latency budget burning faster than sustainable"
    windows: [1h/5m, 6h/30m, 3d/6h]
    action: "Check runbook, likely capacity or query issue"

  - name: error-budget-exhausted
    description: "Monthly error budget depleted"
    action: "Feature freeze, reliability work only"
```

### Migration Checklist: Infrastructure to SLO Alerts

- [ ] Define SLIs for each service (availability, latency)
- [ ] Set SLO targets based on historical data
- [ ] Implement multi-window burn-rate alerts
- [ ] Run SLO alerts alongside existing alerts for 2 weeks
- [ ] Compare: which SLO alerts would have caught real incidents?
- [ ] Disable infrastructure alerts caught by SLO alerts
- [ ] Keep infrastructure alerts only for things SLOs cannot detect (disk full, cert expiry)
- [ ] Review monthly: tune thresholds, remove noise

---

## Actionable Alert Templates

Every alert should contain enough context to start diagnosis without looking elsewhere.

### Template Structure

```yaml
# Required fields for every alert
alert_template:
  name: "Descriptive name (not abbreviations)"
  severity: "P1|P2|P3|P4"
  summary: "One sentence: what is happening"
  description: |
    What: Error rate for {{ service }} exceeded {{ threshold }}
    Impact: {{ affected_users }}% of users seeing errors
    Since: {{ started_at }}
    Current value: {{ current_value }}
  runbook_url: "https://runbooks.example.com/{{ alert_name }}"
  dashboard_url: "https://grafana.example.com/d/{{ service }}-overview"
  labels:
    service: "{{ service }}"
    team: "{{ owning_team }}"
    environment: "{{ env }}"
```

### Example: Complete Alert Definition

```yaml
groups:
  - name: order-service-slo
    rules:
      - alert: OrderServiceAvailabilitySLOBurn
        expr: |
          (
            1 - (
              sum(rate(http_requests_total{service="order-service",status!~"5.."}[1h]))
              / sum(rate(http_requests_total{service="order-service"}[1h]))
            )
          ) > (14.4 * 0.001)
        for: 2m
        labels:
          severity: critical
          service: order-service
          team: commerce
          slo: availability
        annotations:
          summary: "Order Service availability SLO burn rate critical"
          description: |
            The order service error budget is burning at 14.4x the
            sustainable rate. At this pace, the monthly budget will be
            exhausted in approximately 50 hours.

            Current error rate: {{ $value | humanizePercentage }}
            SLO target: 99.9%

            Likely causes:
            - Recent deployment (check: kubectl rollout history)
            - Downstream dependency failure (check: dependency dashboard)
            - Database connection issues (check: connection pool metrics)
          runbook_url: "https://runbooks.example.com/order-service/high-error-rate"
          dashboard_url: "https://grafana.example.com/d/order-service-slo"
```

---

## On-Call Rotation Best Practices

| Practice | Recommendation | Rationale |
|----------|---------------|-----------|
| Rotation length | 1 week | Short enough to stay engaged, long enough for context |
| Handoff meeting | 30 min overlap | Transfer active issues, recent changes |
| Shadow shifts | 2 shifts before primary | New on-call shadows experienced engineer |
| Max pages per shift | 2 per 12h shift | More than this indicates alert quality issues |
| Compensation | Extra PTO or pay | On-call has real personal cost |
| Post-incident review | Within 48h | Capture learnings while fresh |
| Quarterly review | Audit alert volume and quality | Continuous improvement |

### Handoff Template

```markdown
## On-Call Handoff: [Date]

### Active Issues
- [ ] Order service elevated latency (P3, tracking in JIRA-1234)
- [ ] Payment provider intermittent timeouts (monitoring, no action needed)

### Recent Changes
- Deployed order-service v2.4.1 (Tuesday)
- Database migration ran (Wednesday, all green)
- New alert added: payment-slo-burn (Thursday)

### Known Risks
- Black Friday traffic expected 3x normal (Saturday)
- Payment provider maintenance window (Sunday 2-4am UTC)

### Runbook Updates
- Updated: order-service/high-error-rate (new rollback command)
- Added: payment-service/provider-timeout
```

---

## Alert Testing and Validation

### Testing Alerts Before Production

```bash
#!/bin/bash
# test-alert-rules.sh: Validate alert rules without deploying

# Syntax check Prometheus alert rules
promtool check rules alerts/*.yaml

# Unit test alert rules against recorded metrics
promtool test rules tests/alert-tests.yaml

# Validate Alertmanager config
amtool check-config alertmanager.yaml

# Test routing decisions
amtool config routes test \
  --config.file=alertmanager.yaml \
  --verify.receivers=pagerduty-critical \
  alertname=SLOBurnRateCritical severity=critical service=order-service
```

### Alert Unit Tests

```yaml
# tests/alert-tests.yaml
rule_files:
  - alerts/slo-burn-rate.yaml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{service="order-service",status="200"}'
        values: "100+100x60"  # 100 requests per minute, all successful
      - series: 'http_requests_total{service="order-service",status="500"}'
        values: "0+0x60"      # No errors

    alert_rule_test:
      - eval_time: 60m
        alertname: SLOBurnRateCritical
        exp_alerts: []  # Should NOT fire when everything is healthy

  - interval: 1m
    input_series:
      - series: 'http_requests_total{service="order-service",status="200"}'
        values: "90+90x60"    # 90% success rate
      - series: 'http_requests_total{service="order-service",status="500"}'
        values: "10+10x60"    # 10% error rate

    alert_rule_test:
      - eval_time: 10m
        alertname: SLOBurnRateCritical
        exp_alerts:
          - exp_labels:
              severity: critical
              service: order-service
```

---

## Alert Coverage Audit Checklist

### Per-Service Alert Audit

- [ ] **SLO alerts exist** for availability and latency
- [ ] **Multi-window burn rates** configured (fast, medium, slow)
- [ ] **Runbook linked** in every alert annotation
- [ ] **Dashboard linked** in every alert annotation
- [ ] **Severity correctly assigned** (P1-P4)
- [ ] **Routing verified** (correct team, correct channel)
- [ ] **Escalation policy defined** (L1, L2, L3)
- [ ] **Alert tested** with unit tests or historical data replay
- [ ] **False positive rate** < 5% over last 30 days
- [ ] **Alert acknowledged** within SLA over last 30 days

### Organizational Alert Health

- [ ] **Pages per on-call shift** < 2 average
- [ ] **No repeat offender alerts** (same alert > 5x/week without fix)
- [ ] **All alerts have owners** (team label)
- [ ] **Quarterly alert review** completed
- [ ] **Alert documentation** up to date
- [ ] **On-call handoff process** documented and followed
- [ ] **Shadow rotation** in place for new team members

---

## Related Resources

- [SLO Design Guide](./slo-design-guide.md) - Defining SLOs and error budgets
- [Dashboard Design Patterns](./dashboard-design-patterns.md) - Visualization for observability
- [Core Observability Patterns](./core-observability-patterns.md) - Metrics, logs, traces fundamentals
- [Log Aggregation Patterns](./log-aggregation-patterns.md) - Structured logging pipelines
- [Anti-Patterns and Best Practices](./anti-patterns-best-practices.md) - Common observability mistakes
- [Runbook Testing](../../qa-docs-coverage/references/runbook-testing.md) - Testing the runbooks alerts link to
- [SKILL.md](../SKILL.md) - Parent skill overview
