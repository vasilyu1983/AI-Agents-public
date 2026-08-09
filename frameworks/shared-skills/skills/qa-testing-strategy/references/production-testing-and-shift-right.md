# Production Testing and Shift-Right

## Table of Contents

- [Why Shift-Right?](#why-shift-right)
- [Synthetic Monitoring](#synthetic-monitoring)
- [Dark Launches and Gradual Rollouts](#dark-launches-and-gradual-rollouts)
- [Feature Flag-Gated Rollouts](#feature-flag-gated-rollouts)
- [MTTR-Flake SLO](#mttr-flake-slo)
- [Production Replay Testing](#production-replay-testing)
- [Observability-Driven Gates](#observability-driven-gates)
- [Shift-Right Anti-Patterns](#shift-right-anti-patterns)
- [Related Resources](#related-resources)

Shift-right testing validates behaviour in or near production. It complements shift-left gates with continuous verification, gradual exposure, and observability signals that no pre-merge suite can replicate.

---

## Why Shift-Right?

Pre-merge gates (unit, contract, integration, E2E) catch defects before deployment. Shift-right techniques catch the remainder: configuration drift, environment-specific failures, capacity surprises, and subtle regressions that only appear under real traffic.

The four primary shift-right signals are:

| Signal | What it catches |
|--------|-----------------|
| Synthetic monitors | Availability and latency regressions between deployments |
| Dark launches / canary | Real-traffic behaviour before full exposure |
| Feature flags | Decoupled deploy and release; instant rollback without redeployment |
| Production replay | Regressions invisible to synthetic or low-volume canary traffic |

---

## Synthetic Monitoring

Synthetic monitoring runs scripted checks against production (or a production-like environment) on a schedule, independent of CI. It answers: "Is the service healthy right now for an external caller?"

### Tools

| Tool | Strengths | Typical Use |
|------|-----------|-------------|
| **Datadog Synthetics** | Deep APM integration, multi-step API and browser tests, alert-to-trace correlation | Teams already on Datadog |
| **Checkly** | Code-first monitors (Playwright/fetch), Monitoring as Code via CLI/Terraform, GitHub integration | Engineering-owned monitors in source control |
| **Grafana Synthetic Monitoring** | Open-source Blackbox Exporter + Grafana Cloud, Prometheus-native alerting | Grafana/Prometheus stacks |

### What to Monitor Synthetically

1. **Critical journey smoke** – sign-in, core API endpoint, payment ping – at 1-minute intervals.
2. **API contract probes** – POST/GET against key endpoints; assert on status code, response schema, and latency p95.
3. **SSL/TLS expiry** – certificate validity with 30-day and 7-day warning thresholds.
4. **Third-party dependency health** – CDN, auth provider, payment gateway reachability.

### Checkly Monitor as Code (example)

```typescript
// checks/api-health.check.ts
import { ApiCheck, AssertionBuilder } from '@checkly/cli/constructs';

new ApiCheck('api-health', {
  name: 'POST /orders health',
  request: {
    url: 'https://api.example.com/orders',
    method: 'POST',
    body: JSON.stringify({ items: [] }),
    headers: [{ key: 'Content-Type', value: 'application/json' }],
  },
  assertions: [
    AssertionBuilder.statusCode().equals(200),
    AssertionBuilder.jsonBody('$.status').equals('ok'),
    AssertionBuilder.responseTime().lessThan(800),
  ],
  frequency: 1, // minutes
  locations: ['eu-west-1', 'us-east-1'],
});
```

### Alerting Thresholds (defaults)

```yaml
synthetic_slo:
  availability: 99.9%          # alert if 3 consecutive checks fail
  latency_p95_ms: 800          # alert if p95 > 800 ms in a 5-min window
  error_rate_window: 5m
  paging_severity: critical    # page on-call if availability drops below 99%
```

---

## Dark Launches and Gradual Rollouts

A dark launch exposes new code to real traffic without exposing it to users. Three patterns apply at different risk levels:

### Canary Deployment

Route a small percentage of real traffic (1–5%) to the new version. Observe error rates, latency, and business metrics before widening.

```text
Traffic split example (nginx / Envoy):
  prod-v2: 5%   ← canary
  prod-v1: 95%  ← stable baseline

Promotion gates:
  - Error rate delta < 0.1% vs baseline over 15 min
  - Latency p99 regression < 10%
  - No new error classes in logs/traces
```

Tooling: Argo Rollouts, Flagger, AWS CodeDeploy linear/canary, Kubernetes traffic splitting via Gateway API or Istio.

### Ring Deployment

Ordered concentric rings of exposure: internal employees → beta users → 10% of production → full rollout. Each ring is a gate; promotion requires passing observability checks.

```text
Ring 0 (dogfood):    internal users only
Ring 1 (beta):       opted-in users (~1%)
Ring 2 (limited GA): ~10% of production
Ring 3 (full GA):    100%

Gate criteria per ring:
  - Error rate < threshold
  - Latency p95 < budget
  - Support ticket spike absent
  - Business metric (conversion, click-through) not degraded
```

### Traffic Shadowing / Mirroring

Clone production requests and send them to the shadow service in parallel. The shadow response is discarded; only errors and latency are observed. No user impact.

```yaml
# Istio VirtualService mirror example
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: orders-vs
spec:
  hosts: [orders]
  http:
    - route:
        - destination:
            host: orders
            subset: v1
          weight: 100
      mirror:
        host: orders
        subset: v2
      mirrorPercentage:
        value: 100.0
```

Use shadowing to validate a new implementation against a stable one without any user-facing risk.

---

## Feature Flag-Gated Rollouts

Feature flags decouple deployment (code in production) from release (users see the feature). The flag is the rollout mechanism.

### Rollout Progression

```text
1. Deploy with flag OFF (dark code)
2. Enable for internal / QA users (dogfood)
3. Enable for percentage rollout (1% → 10% → 50% → 100%)
4. Promote to permanent-on or remove flag
```

### CI Gate Pattern

Block promotion if the feature flag's targeting rule has drifted from the expected baseline:

```yaml
# GitHub Actions step: verify flag state before promoting
- name: Verify feature flag state
  run: |
    FLAG_STATE=$(curl -s "$LAUNCHDARKLY_API/flags/$FLAG_KEY" \
      -H "Authorization: $LD_API_KEY" | jq -r '.on')
    if [ "$FLAG_STATE" = "true" ] && [ "$ENVIRONMENT" = "production" ]; then
      echo "Flag is live — checking error rate before widening"
      ./scripts/check-canary-health.sh
    fi
```

Tooling: LaunchDarkly, Unleash, Flagsmith, AWS AppConfig, GrowthBook.

### Observability Hooks

Emit a structured log event on every flag evaluation for correlation:

```json
{
  "event": "flag_evaluation",
  "flag": "new-checkout-flow",
  "variant": "treatment",
  "user_segment": "beta",
  "session_id": "abc123",
  "timestamp": "2026-04-27T10:00:00Z"
}
```

This lets you segment error rates and latency dashboards by flag variant without relying on user-attribute joins at query time.

---

## MTTR-Flake SLO

**MTTR-Flake** (Mean Time to Resolve Flake) is the median duration from the moment a test is quarantined to the moment its fix is merged and the quarantine is lifted.

### Formula

```
MTTR-Flake = median(fix_merged_at − quarantine_opened_at)
             for all flake incidents closed in the measurement window
```

### SLO Targets

| Severity | Target MTTR-Flake |
|----------|-------------------|
| Critical path (blocks deploys) | ≤ 2 business days |
| Standard (quarantined, non-blocking) | ≤ 5 business days |
| Low (informational/intermittent) | ≤ 10 business days |

### Why MTTR-Flake Belongs in the SLO Register

A flake quarantine is technical debt with a time cost. Without an SLO, quarantined tests accumulate indefinitely, the effective coverage of CI shrinks, and flaky tests provide cover for real regressions. Tracking MTTR-Flake as a named SLO:

- Makes flake debt visible on the same dashboard as availability SLOs.
- Creates ownership pressure: the team that introduced the flake owns the SLO.
- Provides a leading indicator for suite health before the flake rate metric spikes.

### Collection Script

```python
from datetime import datetime
from statistics import median

def mttr_flake(incidents: list[dict]) -> float:
    """
    incidents: list of dicts with:
      quarantine_opened_at: ISO datetime string
      fix_merged_at: ISO datetime string (or None if still open)
    Returns median MTTR in hours for closed incidents.
    """
    durations = []
    for i in incidents:
        if i.get("fix_merged_at"):
            opened = datetime.fromisoformat(i["quarantine_opened_at"])
            fixed = datetime.fromisoformat(i["fix_merged_at"])
            durations.append((fixed - opened).total_seconds() / 3600)

    return round(median(durations), 1) if durations else float("inf")
```

---

## Production Replay Testing

Production replay captures real request/response pairs from live traffic and replays them against a new version to detect regressions that synthetic tests miss.

### Approaches

| Approach | How it works | Risk |
|----------|-------------|------|
| **Request recording + replay** | Record HTTP requests via a proxy (GoReplay, Gor); replay against shadow | PII in payloads — must scrub before storing |
| **Captured fixture upgrade** | Export a recent slice of production calls; use as integration test fixtures | Fixtures go stale; add a rotation policy |
| **Differential replay** | Replay against old and new simultaneously; diff responses | Diff noise from timestamps, IDs — normalise before diff |

### GoReplay Example

```bash
# Record production traffic to file (sample 10%)
sudo gor --input-raw :8080 \
         --output-file requests.gor \
         --output-file-append \
         --http-pprof :6060 \
         --split-output true \
         --output-file-size-limit 100mb \
         --verbose 1 &

# Replay against staging
gor --input-file requests.gor \
    --output-http http://staging.example.com \
    --stats \
    --output-http-stats
```

### Safety Contract for Replay

1. Strip PII and auth tokens from recorded payloads before storing.
2. Replay against an isolated environment — never against a second production instance.
3. Gate replay results on response-code parity and latency budget, not byte-for-byte body equality.

---

## Observability-Driven Gates

An observability-driven gate uses live telemetry — traces, metrics, error logs — as the promotion criterion instead of (or in addition to) synthetic check pass/fail.

### Gate Signal Hierarchy

```text
Tier 1 (hard block):
  - Error rate > 0.5% (new error classes)
  - p99 latency > 2× baseline
  - Health check endpoint returning non-2xx

Tier 2 (soft block — requires manual approval):
  - p95 latency regression 10–50% vs baseline
  - Increase in warn-level log events > 20% vs baseline
  - Database query plan regressions detected

Tier 3 (informational):
  - Memory / CPU usage increase < 15%
  - New dependency calls (not previously seen in traces)
```

### OpenTelemetry-Based Automated Gate

```yaml
# .github/workflows/deploy.yml (post-deploy check step)
- name: Observability gate
  run: |
    BASELINE_ERROR_RATE=$(./scripts/get-metric.sh error_rate baseline 5m)
    CANARY_ERROR_RATE=$(./scripts/get-metric.sh error_rate canary 5m)

    python3 - <<'EOF'
import sys
baseline = float("$BASELINE_ERROR_RATE")
canary = float("$CANARY_ERROR_RATE")
delta = canary - baseline
if delta > 0.005:
    print(f"BLOCK: error rate delta {delta:.3%} exceeds 0.5% threshold")
    sys.exit(1)
print(f"PASS: error rate delta {delta:.3%}")
EOF
```

### Trace-Based Assertion

Use Tracetest or a custom span query to assert span-level contracts after a canary deployment:

```yaml
# tracetest test: new-checkout-canary.yaml
type: Test
spec:
  name: Checkout canary span assertions
  trigger:
    type: http
    httpRequest:
      url: https://api.example.com/checkout
      method: POST
  specs:
    - selector: span[name="payment.charge"]
      assertions:
        - attr:http.status_code = 200
        - attr:duration < 500ms
    - selector: span[name="inventory.reserve"]
      assertions:
        - attr:db.statement notContains "FULL SCAN"
```

---

## Shift-Right Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| Synthetic monitors that duplicate CI E2E | Redundant; adds noise without production signal | Synthetic monitors test availability and latency, not feature correctness |
| 100% canary traffic immediately | Defeats the purpose of gradual rollout | Start at 1–5%, promote on observability gate pass |
| Feature flags never removed | Flag debt accumulates; runtime branches stay forever | Track flag age; mandate cleanup within 30 days of full rollout |
| Replay without PII scrubbing | Regulatory and privacy risk | Scrub at capture time, not replay time |
| Observability gates checked manually | Humans miss windows; rollbacks are slow | Automate tier-1 gates; require manual approval only for tier-2 |
| MTTR-Flake not tracked | Quarantine lists grow silently | Add MTTR-Flake to team SLO dashboard alongside availability |

---

## Related Resources

- [observability-driven-testing.md](./observability-driven-testing.md) -- OpenTelemetry-first debugging and trace-based validation
- [operational-playbook.md](./operational-playbook.md) -- CI/CD pipeline quality gates hub
- [chaos-resilience-testing.md](./chaos-resilience-testing.md) -- failure injection and resilience testing
- [quality-metrics-dashboard.md](./quality-metrics-dashboard.md) -- metrics collection and dashboards
- [Checkly Monitoring as Code](https://www.checklyhq.com/docs/monitoring-as-code/)
- [Datadog Synthetics](https://docs.datadoghq.com/synthetics/)
- [Argo Rollouts](https://argoproj.github.io/rollouts/)
- [GoReplay](https://goreplay.org/)
