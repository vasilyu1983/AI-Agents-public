# Resilience Test Plan Template (Timeouts, Retries, Degraded Mode)

Use this plan to validate how the system behaves when dependencies fail or degrade.

## Core

### Scope

- Service/system under test: _________________________________
- Environments: staging / pre-prod / prod (if approved)
- Owners: engineering / QA / SRE: ____________________________

### Dependencies (Inventory)

List critical dependencies and their failure modes.

| Dependency | Type | Failure modes | Expected degraded behavior |
|------------|------|---------------|----------------------------|
| Payments | external API | timeouts, 5xx, rate limits | user sees retryable error; order not duplicated |
| DB | internal | slow queries, pool exhaustion | timeouts, circuit breaker, partial features disabled |

### Steady State (What “Healthy” Means)

- SLIs and targets (SLOs): availability, error rate, p95/p99 latency
- Baseline metrics window: last ____ days

### Fault Matrix (Test Cases)

| Fault | Injection method | Expected behavior | Signals to verify | Pass/fail |
|------|-------------------|------------------|------------------|----------|
| Downstream timeout | network delay / fault proxy | bounded timeout, fallback | traces show timeout, error budget impact bounded | ___ |
| 429 rate limit | mocked responses | Retry-After respected, bounded retries | metrics: retries, rate limit errors | ___ |
| Partial outage | fail 10% calls | degraded UX only for affected feature | logs/traces correlate; alerts fire correctly | ___ |
| Slow DB | throttle / load | query timeout, no cascading | p99 bounded, circuit breaker events | ___ |

### Execution Plan (Right-Sized Chaos)

- Hypothesis and steady state documented (Principles of Chaos Engineering: https://principlesofchaos.org/)
- Blast radius controls:
  - Target scope (service/region/tenant): ______________________
  - Timebox: _________________________________________________
  - Abort criteria: ___________________________________________
- Rollback plan: _____________________________________________

### Observability Requirements

- Correlation IDs captured on failure (request ID / trace ID)
- Dashboards and alerts ready (SLO burn, error rate, tail latency)
- Runbook link: ______________________________________________

### CI Economics and Scheduling

- PR gate: smoke resilience checks only (mocked fault injection)
- Nightly/release: full fault matrix and load/stress scenarios

### Flake Control

- Deterministic experiment parameters (fixed duration, fixed blast radius)
- Clear “expected failure” vs “unexpected collateral damage” signals

## Optional: AI / Automation

Do:
- Use AI to propose scenario candidates from the dependency inventory; keep only scenarios mapped to explicit risks.
- Use AI to summarize experiment results and produce a draft postmortem timeline; verify with telemetry.

Avoid:
- Generating scenarios without a risk map or without observability signals.
