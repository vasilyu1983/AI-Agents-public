---
name: qa-resilience
description: "Resilience engineering for QA: failure mode testing (timeouts/retries/dependency failures), chaos experiments with blast-radius controls, degraded-mode UX expectations, and reliability gates."
---

# QA Resilience (Dec 2025) — Failure Mode Testing & Production Hardening

This skill provides execution-ready patterns for building resilient, fault-tolerant systems that handle failures gracefully, and for validating those behaviors with tests.

Core references: Principles of Chaos Engineering (https://principlesofchaos.org/), AWS Well-Architected Reliability Pillar (https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html), and Kubernetes probes (https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

---

## When to Use This Skill

Claude should invoke this skill when a user requests:

- Circuit breaker implementation
- Retry strategies and exponential backoff
- Bulkhead pattern for resource isolation
- Timeout policies for external dependencies
- Graceful degradation and fallback mechanisms
- Health check design (liveness vs readiness)
- Error handling best practices
- Chaos engineering setup
- Production hardening strategies
- Fault injection testing

---

## Core QA (Default)

### Failure Mode Testing (What to Validate)

- Timeouts: every network call and DB query has a bounded timeout; validate timeout budgets across chained calls.
- Retries: bounded retries with backoff + jitter; validate idempotency and “retry storm” safeguards.
- Dependency failure: partial outage, slow downstream, rate limiting, DNS failures, auth failures.
- Degraded-mode UX: what the user sees/gets when dependencies fail (cached/stale/partial responses).
- Health checks: validate liveness/readiness/startup probe behavior (Kubernetes probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

### Right-Sized Chaos Engineering (Safe by Construction)

- Define steady state and hypothesis (Principles of Chaos Engineering: https://principlesofchaos.org/).
- Start in non-prod; in prod, use minimal blast radius, timeboxed runs, and explicit abort criteria.
- REQUIRED: rollback plan, owners, and observability signals before running experiments.

### Load/Perf + Production Guardrails

- Load tests validate capacity and tail latency; resilience tests validate behavior under failure.
- Guardrails [Inference]:
  - Run heavy resilience/perf suites on schedule (nightly) and on canary deploys, not on every PR.
  - Gate releases on regression budgets (p99 latency, error rate) rather than on raw CPU/memory.

### Flake Control for Resilience Tests

- Chaos/fault injection can look “flaky” if the experiment is not deterministic.
- Stabilize the experiment first: fixed blast radius, controlled fault parameters, deterministic duration, strong observability.

### Debugging Ergonomics

- Every resilience test run should capture: experiment parameters, target scope, timestamps, and trace/log links for failures.
- Prefer tracing/metrics to confirm the failure is the expected one (not collateral damage).

### Do / Avoid

Do:
- Test degraded mode explicitly; document expected UX and API responses.
- Validate retries/timeouts in integration tests with fault injection.

Avoid:
- Unbounded retries and missing timeouts (amplifies incidents).
- “Happy-path only” testing that ignores downstream failure classes.

## Quick Reference

| Pattern | Library/Tool | When to Use | Configuration |
|---------|--------------|-------------|---------------|
| Circuit Breaker | Opossum (Node.js), pybreaker (Python) | External API calls, database connections | Threshold: 50%, timeout: 30s, volume: 10 |
| Retry with Backoff | p-retry (Node.js), tenacity (Python) | Transient failures, rate limits | Max retries: 5, exponential backoff with jitter |
| Bulkhead Isolation | Semaphore pattern, thread pools | Prevent resource exhaustion | Pool size based on workload (CPU cores + wait/service time) |
| Timeout Policies | AbortSignal, statement timeout | Slow dependencies, database queries | Connection: 5s, API: 10-30s, DB query: 5-10s |
| Graceful Degradation | Feature flags, cached fallback | Non-critical features, ML recommendations | Cache recent data, default values, reduced functionality |
| Health Checks | Kubernetes probes, /health endpoints | Service orchestration, load balancing | Liveness: simple, readiness: dependency checks, startup: slow apps |
| Chaos Engineering | Chaos Toolkit, Netflix Chaos Monkey | Proactive resilience testing | Start non-prod, define hypothesis, automate failure injection |

---

## Decision Tree: Resilience Pattern Selection

```text
Failure scenario: [System Dependency Type]
    ├─ External API/Service?
    │   ├─ Transient errors? → Retry with exponential backoff + jitter
    │   ├─ Cascading failures? → Circuit breaker + fallback
    │   ├─ Rate limiting? → Retry with Retry-After header respect
    │   └─ Slow response? → Timeout + circuit breaker
    │
    ├─ Database Dependency?
    │   ├─ Connection pool exhaustion? → Bulkhead isolation + timeout
    │   ├─ Query timeout? → Statement timeout (5-10s)
    │   ├─ Replica lag? → Read from primary fallback
    │   └─ Connection failures? → Retry + circuit breaker
    │
    ├─ Non-Critical Feature?
    │   ├─ ML recommendations? → Feature flag + default values fallback
    │   ├─ Search service? → Cached results or basic SQL fallback
    │   ├─ Email/notifications? → Log error, don't block main flow
    │   └─ Analytics? → Fire-and-forget, circuit breaker for protection
    │
    ├─ Kubernetes/Orchestration?
    │   ├─ Service discovery? → Liveness + readiness + startup probes
    │   ├─ Slow startup? → Startup probe (failureThreshold: 30)
    │   ├─ Load balancing? → Readiness probe (check dependencies)
    │   └─ Auto-restart? → Liveness probe (simple check)
    │
    └─ Testing Resilience?
        ├─ Pre-production? → Chaos Toolkit experiments
        ├─ Production (low risk)? → Feature flags + canary deployments
        ├─ Scheduled testing? → Game days (quarterly)
        └─ Continuous chaos? → Netflix Chaos Monkey (1% failure injection)
```

---

## Navigation: Core Resilience Patterns

- **[Circuit Breaker Patterns](resources/circuit-breaker-patterns.md)** - Prevent cascading failures
  - Classic circuit breaker implementation (Node.js, Python)
  - Adaptive circuit breakers with ML-based thresholds (2024-2025)
  - Fallback strategies and event monitoring

- **[Retry Patterns](resources/retry-patterns.md)** - Handle transient failures
  - Exponential backoff with jitter
  - Retry decision table (which errors to retry)
  - Idempotency patterns and Retry-After headers

- **[Bulkhead Isolation](resources/bulkhead-isolation.md)** - Resource compartmentalization
  - Semaphore pattern for thread/connection pools
  - Database connection pooling strategies
  - Queue-based bulkheads with load shedding

- **[Timeout Policies](resources/timeout-policies.md)** - Prevent resource exhaustion
  - Connection, request, and idle timeouts
  - Database query timeouts (PostgreSQL, MySQL)
  - Nested timeout budgets for chained operations

- **[Graceful Degradation](resources/graceful-degradation.md)** - Maintain partial functionality
  - Cached fallback strategies
  - Default values and feature toggles
  - Partial responses with Promise.allSettled

- **[Health Check Patterns](resources/health-check-patterns.md)** - Service availability monitoring
  - Liveness, readiness, and startup probes
  - Kubernetes probe configuration
  - Shallow vs deep health checks

---

## Navigation: Operational Resources

- **[Resilience Checklists](resources/resilience-checklists.md)** - Production hardening checklists
  - Dependency resilience
  - Health and readiness probes
  - Observability for resilience
  - Failure testing

- **[Chaos Engineering Guide](resources/chaos-engineering-guide.md)** - Safe reliability experiments
  - Planning chaos experiments
  - Common failure injection scenarios
  - Execution steps and debrief checklist

---

## Navigation: Templates

- **[Resilience Runbook Template](templates/runbooks/resilience-runbook-template.md)** - Service hardening profile
  - Dependencies and SLOs
  - Fallback strategies
  - Rollback procedures

- **[Fault Injection Playbook](templates/testing/fault-injection-playbook.md)** - Chaos testing script
  - Success signals
  - Rollback criteria
  - Post-experiment debrief

- **[Resilience Test Plan Template](templates/testing/template-resilience-test-plan.md)** - Failure mode test plan (timeouts/retries/degraded mode)
  - Scope and dependencies
  - Fault matrix and expected behavior
  - Observability signals and pass/fail criteria

---

## Quick Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| External API calls | Circuit breaker + retry with exponential backoff |
| Database queries | Timeout + connection pooling + circuit breaker |
| Slow dependency | Bulkhead isolation + timeout |
| Non-critical feature | Feature flag + graceful degradation |
| Kubernetes deployment | Liveness + readiness + startup probes |
| Testing resilience | Chaos engineering experiments |
| Transient failures | Retry with exponential backoff + jitter |
| Cascading failures | Circuit breaker + bulkhead |

---

## Anti-Patterns to Avoid

- **No timeouts** - Infinite waits exhaust resources
- **Infinite retries** - Amplifies problems (thundering herd)
- **No circuit breakers** - Cascading failures
- **Tight coupling** - One failure breaks everything
- **Silent failures** - No observability into degraded state
- **No bulkheads** - Shared thread pools exhaust all resources
- **Testing only happy path** - Production reveals failures

---

## Optional: AI / Automation

Do:
- Use AI to propose failure-mode scenarios from an explicit risk register; keep only scenarios that map to known dependencies and business journeys.
- Use AI to summarize experiment results (metrics deltas, error clusters) and draft postmortem timelines; verify with telemetry.

Avoid:
- “Scenario generation” without a risk map (creates noise and wasted load).
- Letting AI relax timeouts/retries or remove guardrails.

---

## Related Skills

- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Incident response, SLOs, and platform runbooks
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API error handling, retries, and database reliability patterns
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System decomposition and dependency design for reliability
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) — Regression, load, and fault-injection testing strategies
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Security failure modes and guardrails
- [../qa-observability/SKILL.md](../qa-observability/SKILL.md) — Metrics, tracing, logging, and performance monitoring
- [../qa-debugging/SKILL.md](../qa-debugging/SKILL.md) — Production debugging and incident investigation
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) — Database resilience, connection pooling, and query timeouts
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) — API design patterns including error handling and retry semantics

---

## Usage Notes

**Pattern Selection:**

- Start with circuit breakers for external dependencies
- Add retries for transient failures (network, rate limits)
- Use bulkheads to prevent resource exhaustion
- Combine patterns for defense-in-depth

**Observability:**

- Track circuit breaker state changes
- Monitor retry attempts and success rates
- Alert on degraded mode duration
- Measure recovery time after failures

**Testing:**

- Start chaos experiments in non-production
- Define hypothesis before failure injection
- Set blast radius limits and auto-revert
- Document learnings and action items

---

> **Success Criteria:** Systems gracefully handle failures, recover automatically, maintain partial functionality during outages, and fail fast to prevent cascading failures. Resilience is tested proactively through chaos engineering.
