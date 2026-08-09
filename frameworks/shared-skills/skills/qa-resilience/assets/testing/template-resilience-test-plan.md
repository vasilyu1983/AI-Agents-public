# Resilience Test Plan Template (Deadlines, Retries, Hedging, Degraded Mode)

Use this plan to validate how the system behaves when dependencies fail or degrade.

## Core

### Scope

- Service/system under test: _________________________________
- Environments: staging / pre-prod / prod (if approved)
- Owners: engineering / QA / SRE: ____________________________

### Dependencies (Inventory)

List critical dependencies and their failure modes.

| Dependency | Type | Deadline / timeout | Retry or hedge owner | Failure modes | Expected degraded behavior |
|------------|------|--------------------|----------------------|---------------|----------------------------|
| Payments | external API | 2.5s total / 800ms per try | client retry only | timeouts, 5xx, rate limits | user sees retryable error; order not duplicated |
| DB | internal | 1.5s statement / 250ms pool wait | no hedge; retry only if safe | slow queries, pool exhaustion | timeout, no cascade, partial features disabled |

### Steady State (What “Healthy” Means)

- SLIs and targets (SLOs): availability, error rate, p95/p99 latency
- Baseline metrics window: last ____ days

### Fault Matrix (Test Cases)

| Fault | Injection method | Expected behavior | Signals to verify | Pass/fail |
|------|-------------------|------------------|------------------|----------|
| Downstream timeout | network delay / fault proxy | bounded timeout, fallback | timeout metrics, traces show deadline exhaustion, burn impact bounded | ___ |
| 429 rate limit | mocked responses | Retry-After respected, bounded retries | retry count, retry budget, rate limit errors | ___ |
| Partial outage | fail 10% calls | degraded UX only for affected feature | logs/traces correlate; alerts fire correctly | ___ |
| Slow tail latency | inject 1-5% stragglers | hedge only if approved and safe; p99 improves without overload | hedge count, hedge win rate, added load, p99 | ___ |
| Slow DB | throttle / load | query timeout, no cascading | p99 bounded, queue depth, breaker or rejection events | ___ |
| One bad host in pool | target one instance / pod | endpoint ejected or isolated; no pool-wide collapse | outlier/ejection telemetry, error rate stays bounded | ___ |

### Execution Plan (Right-Sized Chaos)

- Hypothesis and steady state documented (Principles of Chaos Engineering: https://principlesofchaos.org/)
- Blast radius controls:
  - Target scope (service/region/tenant): ______________________
  - Timebox: _________________________________________________
  - Abort criteria: ___________________________________________
- Rollback plan: _____________________________________________

### Observability Requirements

- Correlation IDs captured on failure (request ID / trace ID)
- Retry, hedge, breaker, and degraded-mode telemetry defined before execution
- Dashboards and alerts ready (SLO burn, error rate, tail latency)
- Recovery timing and shed / reject volume visible
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
