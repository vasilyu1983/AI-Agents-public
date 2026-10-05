# Health Check Patterns

Liveness, readiness, and startup probes for orchestration systems (Kubernetes and equivalents).

---
## Table of Contents

- [Core Rule: Readiness Checks Local State Only](#core-rule-readiness-checks-local-state-only)
- [Liveness Probe](#liveness-probe)
- [Readiness Probe](#readiness-probe)
- [Startup Probe](#startup-probe)
- [Kubernetes Configuration](#kubernetes-configuration)
- [Dependency Health: Report, Don't Gate](#dependency-health-report-dont-gate)
- [Health Check Security](#health-check-security)
- [Checklist](#checklist)
- [Related Resources](#related-resources)

## Core Rule: Readiness Checks Local State Only

A readiness probe answers one question: **can this specific instance serve traffic right now?** It must not answer "is the database up?" or "is the external API up?" — those are shared-dependency questions, and every instance behind the same load balancer shares the same answer.

If a shared dependency outage flips `readiness` to `false`, the orchestrator removes every instance at the same moment. A partial, degradable dependency failure becomes a total, instance-count-zero outage — the exact failure mode this skill's circuit-breaker and graceful-degradation content exists to prevent. It also removes the instances that could otherwise serve a degraded response (cached data, a fallback, a 503 with `Retry-After`) instead of nothing.

**What readiness may check:** local warm-up state, connection-pool exhaustion, graceful-shutdown draining, whether the process has finished loading its own config/models. All local to the instance, all things restarting or removing *this instance* actually fixes.

**What readiness must not check:** database, cache, message queue, or any external API. Those go through:
- Circuit breakers / bulkheads that let the instance degrade gracefully and keep serving.
- A separate, non-gating diagnostic endpoint or metric (e.g. `/health/dependencies`) that feeds dashboards and alerts, not the load-balancer decision.

This directly contradicts a common pattern of "readiness checks all critical dependencies." That pattern is wrong for a load-balanced, horizontally-scaled service; it is defensible only for a singleton process where there genuinely is nothing else to route to.

---

## Liveness Probe

**Purpose:** is the process alive, or should the orchestrator restart it?

- No dependency checks — never touch the database, cache, or network.
- Detect deadlocks, unrecoverable internal state, or a hung event loop, not upstream health.
- Fast (well under the probe timeout) and side-effect-free.

```javascript
app.get('/health/liveness', (req, res) => res.status(200).json({ status: 'alive' }));
```

---

## Readiness Probe

**Purpose:** should the load balancer route traffic to this instance right now?

Check only this instance's local ability to serve: connection pool has capacity, the process is not draining for shutdown, startup has completed.

```javascript
app.get('/health/readiness', (req, res) => {
  const ready = !isDraining && dbPool.availableConnections() > 0 && startupComplete;
  res.status(ready ? 200 : 503).json({ status: ready ? 'ready' : 'not_ready' });
});
```

A dependency (database, cache, queue) failure should be handled by a circuit breaker or degraded-mode response inside the request path — see [circuit-breaker-patterns.md](circuit-breaker-patterns.md) and [graceful-degradation.md](graceful-degradation.md) — not by flipping readiness.

---

## Startup Probe

For slow-starting apps (model loads, cache warm-up, config fetch): gate the liveness/readiness probes behind it so the orchestrator does not restart a pod still initializing.

```javascript
let isReady = false;
async function initialize() {
  await connectToDatabase();
  await warmupCache();
  isReady = true;
}
app.get('/health/startup', (req, res) => res.status(isReady ? 200 : 503).json({ status: isReady ? 'started' : 'starting' }));
initialize().catch((e) => { console.error('Startup failed:', e); process.exit(1); });
```

---

## Kubernetes Configuration

```yaml
livenessProbe:
  httpGet: { path: /health/liveness, port: 3000 }
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 1
  failureThreshold: 3
readinessProbe:
  httpGet: { path: /health/readiness, port: 3000 }
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 1
  failureThreshold: 3
  successThreshold: 1
startupProbe:
  httpGet: { path: /health/startup, port: 3000 }
  periodSeconds: 5
  failureThreshold: 30   # allow ~150s startup
```

---

## Dependency Health: Report, Don't Gate

Aggregate dependency status for observability and alerting, on an endpoint the load balancer never queries:

```javascript
app.get('/health/dependencies', async (req, res) => {
  const results = await Promise.allSettled([checkDatabase(), checkRedis(), checkExternalAPI()]);
  // Feed this to metrics/alerts, not to the readiness gate.
  res.status(200).json({ checked_at: new Date().toISOString(), results });
});
```

Emit per-dependency gauges (`health_check.dependency.<name>`) and a check-duration histogram; alert on those, and let the circuit breaker decide what the request path does when a dependency is down.

---

## Health Check Security

- Health endpoints should not require auth (load balancers and probes need unauthenticated access).
- Rate-limit them anyway; an unauthenticated endpoint that runs even local-only checks is still a target.
- Log requests to `/health/*` whose `User-Agent` does not match your orchestrator's probe signature, as a low-cost anomaly signal.

---

## Checklist

- [ ] Liveness checks only the process itself — no I/O to dependencies.
- [ ] Readiness checks only local serving capacity — no database/cache/external-API calls.
- [ ] Dependency health is reported on a separate, non-gating endpoint and/or metrics.
- [ ] Startup probe covers slow initialization; liveness/readiness are gated behind it.
- [ ] All probes respond within their configured timeout with margin.
- [ ] Health endpoints are unauthenticated but rate-limited and logged.

---

## Related Resources

- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) — how the request path should degrade when a dependency is down.
- [graceful-degradation.md](graceful-degradation.md) — serving a degraded response instead of failing readiness.
- [timeout-policies.md](timeout-policies.md) — timeouts for probe handlers and dependency checks.
- [resilience-checklists.md](resilience-checklists.md) — release and production hardening checks.
