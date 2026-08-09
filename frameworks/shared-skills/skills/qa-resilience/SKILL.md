---
name: qa-resilience
description: "Designs and tests distributed-system resilience. Use when adding retries, deadlines, hedging, circuit breakers, overload protection, chaos experiments, or SLO reliability gates."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Resilience

Use this skill when reliability work is about failure behavior, overload protection, degraded mode, or resilience testing. The goal is not "add retries everywhere." The goal is predictable failure handling, clear ownership, and testable recovery behavior.

## Quick Reference

| Symptom | Start With |
|--------|------------|
| slow or hanging dependency | deadline and timeout budget |
| transient dependency failure | bounded retry with jitter and retry budget |
| sustained dependency failure | circuit breaker and fallback |
| rate-limited dependency | honor `Retry-After`, expose degraded behavior, and test quota paths intentionally |
| one bad host in a healthy pool | outlier detection or endpoint ejection |
| queue or pool saturation | bulkheads, concurrency limits, load shedding |
| non-critical feature outage | graceful degradation or feature flag fallback |
| resilience validation | deterministic fault injection before chaos |

## When to Use This Skill

- retries, deadlines, hedging, breakers, bulkheads, and overload protection
- degraded-mode UX or API behavior
- service-mesh or gateway resilience policy
- chaos engineering, game days, DR drills, and fault injection
- release gates based on failure behavior, not only happy-path load tests

## Route Elsewhere

- simple CRUD or single-process utilities -> ordinary error handling may be enough
- frontend-only failure behavior -> [software-frontend](../software-frontend/SKILL.md)
- service implementation details -> [software-backend](../software-backend/SKILL.md)
- telemetry instrumentation -> [qa-observability](../qa-observability/SKILL.md)
- broader platform and incident operating model -> [ops-devops-platform](../ops-devops-platform/SKILL.md)

---

## Workflow

1. Identify the critical user journeys and the dependencies that can break them.
2. Define the contract per dependency:
   - timeout or deadline budget
   - retry ownership
   - breaker or outlier policy
   - concurrency and queue limits
   - degraded behavior if the dependency is unavailable
3. Decide where the policy lives:
   - app code
   - client library
   - mesh or gateway
4. Test in stages:
   - deterministic fault injection
   - staged chaos in non-production
   - narrow prod canary or game day only with guardrails
5. Define pass or fail signals:
   - burn rate
   - p95 or p99
   - fallback rate
   - breaker transitions
   - shed volume
   - recovery time

---

## Pattern Rules

- retries happen at one layer only
- deadlines come before retries
- hedging is only for idempotent or cancellation-safe reads
- overload handling must shed early instead of collapsing late
- readiness and liveness must stay bounded and shallow
- resilience behaviors belong in targeted checks; do not let rate-limit or degraded-mode coverage leak into unrelated happy-path suites
- prod experiments require blast-radius limits, abort criteria, dashboards, and owners

## Failure Modes to Validate

- timeouts and deadline propagation
- retry storms and duplicate side effects
- partial dependency outages
- slow downstreams and long-tail latency
- queue buildup and connection-pool exhaustion
- one-bad-host behavior inside a pool
- degraded-mode responses and stale-data fallbacks
- rate-limit handling, `Retry-After`, and client backoff expectations
- visible state convergence after recovery or backend resets
- failover and failback behavior
- metastable failure: a self-sustaining feedback loop (retry amplification, cache-miss stampede, queue backlog, connection-pool churn) that does not self-resolve after the original trigger clears — see [references/cascading-failure-prevention.md](references/cascading-failure-prevention.md#metastable-failures--the-class-cascading-failure-fixes-do-not-cure)

---

## Testing Ladder

### Deterministic first

- inject latency, errors, timeouts, malformed payloads, and unavailable endpoints in controlled tests
- verify the intended control activates and the wrong controls do not

### Chaos second

- start in non-production
- use a small blast radius and a fixed time window
- stop immediately on error-budget or customer-impact breach

### DR and game days last

- validate RTO and RPO claims explicitly
- rehearse recovery ownership, not only technical failover

---

## Operational Guardrails

- every experiment needs a stated hypothesis and steady-state metric
- every run should capture timestamps, targets, blast radius, and dashboard links
- telemetry fields for retries, breaker transitions, hedging, shedding, and fallback are part of the resilience contract
- releases should be gated on reliability behavior, not only resource usage

## Anti-Patterns

- no timeouts
- retries at every hop
- fixed-interval or unbounded retries
- fixed per-call retry count with no system-wide retry budget (does not tighten as error rate rises)
- retries without idempotency
- hedging unsafe writes
- no bulkheads or queue bounds
- deep readiness or liveness checks
- silent degraded mode
- untested failover plans
- happy-path-only load testing

---

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/resilience_checker.py](scripts/resilience_checker.py) | Scores resilience pattern coverage and reports gaps |

Typical usage:

```bash
python scripts/resilience_checker.py assess --input data/sample-service-profile.json
python scripts/resilience_checker.py gaps --input data/sample-service-profile.json
python scripts/resilience_checker.py report --input data/sample-service-profile.json --output resilience-report.md
```

See [scripts/README.md](scripts/README.md) for the input format and scoring logic.

## ASCII Flow

```text
Resilience request
  -> Identify failure mode: slow, transient, sustained, overloaded, or degraded
  -> Set deadlines, retry budgets, isolation, and fallback ownership
  -> Add telemetry for saturation, errors, latency, and degraded behavior
  -> Validate with deterministic fault injection before chaos experiments
  -> Gate release on recovery evidence, SLO impact, and rollback path
  -> Document runbook actions and residual risk
```

## Navigation

### Foundation applied recipes

- [references/reliability-theory-applied.md](references/reliability-theory-applied.md)
- [references/distributed-systems-applied.md](references/distributed-systems-applied.md)

### Core references

- [references/circuit-breaker-patterns.md](references/circuit-breaker-patterns.md)
- [references/retry-patterns.md](references/retry-patterns.md)
- [references/timeout-policies.md](references/timeout-policies.md)
- [references/deadlines-hedging.md](references/deadlines-hedging.md)
- [references/bulkhead-isolation.md](references/bulkhead-isolation.md)
- [references/load-shedding-backpressure.md](references/load-shedding-backpressure.md)
- [references/gateway-mesh-resilience.md](references/gateway-mesh-resilience.md)
- [references/graceful-degradation.md](references/graceful-degradation.md)
- [references/health-check-patterns.md](references/health-check-patterns.md)
- [references/cascading-failure-prevention.md](references/cascading-failure-prevention.md)
- [references/disaster-recovery-testing.md](references/disaster-recovery-testing.md)

### Operational resources

- [references/resilience-checklists.md](references/resilience-checklists.md)
- [references/chaos-engineering-guide.md](references/chaos-engineering-guide.md)
- [references/chaos-tooling-recipes.md](references/chaos-tooling-recipes.md)
- [references/idempotency-key-design.md](references/idempotency-key-design.md)
- [references/resilience-telemetry.md](references/resilience-telemetry.md)
- [references/slo-as-code.md](references/slo-as-code.md)
- [references/ai-llm-resilience-failure-modes.md](references/ai-llm-resilience-failure-modes.md)
- [assets/runbooks/resilience-runbook-template.md](assets/runbooks/resilience-runbook-template.md)
- [assets/testing/fault-injection-playbook.md](assets/testing/fault-injection-playbook.md)
- [assets/testing/template-resilience-test-plan.md](assets/testing/template-resilience-test-plan.md)
- [data/sample-service-profile.json](data/sample-service-profile.json)

## Related Skills

- [ops-devops-platform](../ops-devops-platform/SKILL.md)
- [software-backend](../software-backend/SKILL.md)
- [software-architecture-design](../software-architecture-design/SKILL.md)
- [qa-observability](../qa-observability/SKILL.md)
- [qa-debugging](../qa-debugging/SKILL.md)
- [software-security-appsec](../software-security-appsec/SKILL.md)
- [data-sql-optimization](../data-sql-optimization/SKILL.md)
- [dev-api-design](../dev-api-design/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify current platform features, mesh capabilities, and vendor-specific behavior before final answers when the recommendation depends on a live product.
- Prefer primary docs for runtime or tooling specifics.
- If web access is unavailable, keep external product guidance marked as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

