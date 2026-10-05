# Retry Patterns (Backoff, Jitter, Retry Budgets)

Production-ready retry guidance for transient failures in distributed systems.

---
## Table of Contents

- [Core Rules](#core-rules)
- [Expert Judgment: Retry Budget vs. Retry Count](#expert-judgment-retry-budget-vs-retry-count)
- [Retry Decision Table (Starting Point)](#retry-decision-table-starting-point)
- [Reference Implementation (Node.js `fetch`)](#reference-implementation-nodejs-fetch)
- [Library and Mesh Configs](#library-and-mesh-configs)
- [Idempotency Notes](#idempotency-notes)
- [Checklist](#checklist)
- [Related Resources](#related-resources)


## Core Rules

- Classify failures before entering retry logic. Non-retryable exceptions (validation, schema mismatch, deterministic business rejection, poison messages) must be routed to dead-letter or terminal failure handling immediately — never fed into the generic retry loop. Exception classification that happens inside or after the retry loop repeats side effects and violates operator expectations.
- Bound retries by an overall deadline (timeout budget) and a retry budget.
- Use exponential backoff with jitter.
- Retry only idempotent operations (or require idempotency keys / dedupe).
- Respect server guidance (for example `Retry-After`) for `429` / `503`.
- Prevent retry storms: cap attempts, cap max delay, and add client-side rate limiting.

---

## Expert Judgment: Retry Budget vs. Retry Count

A fixed "max 3 retries per call site" rule can amplify traffic when it is a per-request limit applied independently at every layer. Worst-case amplification at the origin is **(retries + 1)^layers**: "3 retries" means 4 attempts, so a 3-layer chain (client → gateway → service) where every layer retries 3 times can send 4 × 4 × 4 = **64×** the original volume to the bottom layer. SRE book ch. 22 uses the same example ("3 retries (4 attempts) … 64 attempts (4^3)"; <https://sre.google/sre-book/addressing-cascading-failures/>). Each layer's retries are invisible to the layers above, so they compound instead of sharing a budget.

Retry **count** answers "how many times may this one request retry?" Retry **budget** answers "what fraction of this client's traffic may be retries right now?" Two widely deployed implementations define it differently:

- **Envoy** `retry_budget`: concurrent retries are capped by `budget_percent` of *active plus pending* requests, with a `min_retry_concurrency` floor. A nonzero `budget_interval` counts recently started requests over that window. Read the [schema for your deployed release](https://github.com/envoyproxy/envoy/blob/main/api/envoy/config/cluster/v3/circuit_breaker.proto) for defaults and field support.
- **Finagle** `RetryBudget`: request-proportional tokens plus a per-second allowance for low-traffic or newly started clients. Read the [Clients guide](https://twitter.github.io/finagle/guide/Clients.html) and installed library for the percentage, floor and expiry window.

Tune the budget against measured healthy load and spare capacity. A request-volume budget does not automatically shrink with error rate, but it bounds retry load: if 40% of calls fail, a fixed per-call count keeps retrying at the same rate and adds load, while a budget rejects new retries once it is exhausted and converts excess load into fast failures.

**Practical rule:** treat retry count as a per-request safety cap (bounding the worst case for a single caller) and retry budget as the system-wide governor (bounding the aggregate). Configure both. A retry-count-only design is a known ingredient of the retry-amplification sustaining cycle described in [cascading-failure-prevention.md](cascading-failure-prevention.md#metastable-failures--the-class-cascading-failure-fixes-do-not-cure) — a fixed count does not relax as conditions worsen, which is exactly the property a sustaining cycle needs to keep itself going.

---

## Retry Decision Table (Starting Point)

| Condition | Retry? | Notes |
|----------|--------|-------|
| Connection errors, DNS errors, TCP resets | Yes | Treat as transient; still bound by deadline + budget |
| Per-try timeout reached | Yes | Prefer fewer retries for user-facing paths; reduce blast radius |
| HTTP 408 | Yes | Usually safe to retry with backoff |
| HTTP 429 | Yes | Respect `Retry-After`; consider per-client rate limiting |
| HTTP 500/502/503/504 | Yes | Prefer pairing with circuit breaker + bulkheads |
| HTTP 400/401/403/404 | No | Fix request/auth/config; retrying rarely helps |
| Non-idempotent POST without idempotency key | No | Add idempotency key / dedupe first |

---

## Reference Implementation (Node.js `fetch`)

Library-agnostic so it can honour `Retry-After` exactly. It retries 5xx, 408 and 429 (with or without `Retry-After`), network errors and per-try timeouts; it refuses to retry a non-idempotent method unless the caller sets an `Idempotency-Key` header; and it asks a shared budget before every retry. Prefer library or mesh config when you have it (see [Library and Mesh Configs](#library-and-mesh-configs)).

```javascript
const IDEMPOTENT = new Set(['GET', 'HEAD', 'OPTIONS', 'PUT', 'DELETE']);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function parseRetryAfterMs(v) {
  if (!v) return null;
  const s = Number(v);
  if (Number.isFinite(s)) return Math.max(0, s * 1000);
  const d = Date.parse(v);
  return Number.isFinite(d) ? Math.max(0, d - Date.now()) : null;
}

// Budget hook: Finagle-style "ratio of requests + small floor". Share one per downstream.
function createRetryBudget({ ratio = 0.2, minRetries = 3 } = {}) {
  let requests = 0, retries = 0; // reset or decay these on a timer in real code
  return {
    onRequest() { requests++; },
    tryAcquire() {
      if (retries < minRetries + ratio * requests) { retries++; return true; }
      return false;
    },
  };
}

function isRetryableStatus(status) {
  return status === 408 || status === 429 || (status >= 500 && status <= 599);
}

async function fetchWithRetry(url, init = {}, {
  attempts = 3, perTryTimeoutMs = 3000, baseBackoffMs = 200, maxBackoffMs = 5000,
  overallDeadlineMs = 10000, budget = createRetryBudget(),
} = {}) {
  const method = (init.method || 'GET').toUpperCase();
  const headers = new Headers(init.headers);
  const safeToRetry = IDEMPOTENT.has(method) || headers.has('Idempotency-Key');
  const deadlineAt = Date.now() + overallDeadlineMs;
  budget.onRequest();

  for (let attempt = 1; ; attempt++) {
    const remaining = deadlineAt - Date.now();
    if (remaining <= 0) throw new Error('Retry deadline exhausted');
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), Math.min(perTryTimeoutMs, remaining));
    let failure;
    try {
      const res = await fetch(url, { ...init, signal: ctrl.signal });
      if (res.ok) return res;
      failure = { status: res.status, retryable: isRetryableStatus(res.status),
                  retryAfterMs: parseRetryAfterMs(res.headers.get('Retry-After')) };
      if (!failure.retryable) return res; // 4xx: caller handles, never retried
    } catch (err) {
      // AbortError = per-try timeout; TypeError = network/DNS/reset in fetch()
      failure = { error: err, retryable: err.name === 'AbortError' || err instanceof TypeError };
    } finally {
      clearTimeout(t);
    }
    const give = () => { if (failure.error) throw failure.error;
                         throw Object.assign(new Error(`HTTP ${failure.status}`), failure); };
    if (!failure.retryable || !safeToRetry || attempt >= attempts) give();
    if (!budget.tryAcquire()) give(); // budget exhausted: fail fast, do not amplify
    const exp = Math.min(maxBackoffMs, baseBackoffMs * 2 ** (attempt - 1));
    const backoff = Math.floor(Math.random() * exp); // full jitter
    const delay = Math.max(failure.retryAfterMs ?? 0, backoff);
    if (delay >= deadlineAt - Date.now()) give(); // Retry-After beyond deadline: stop now
    await sleep(delay);
  }
}
```

Checked against a local mock server: `GET` to a server answering `503` then `200` made 2 attempts and returned 200; a `POST` without `Idempotency-Key` to the same server made 1 attempt and threw `HTTP 503`; the same `POST` with `Idempotency-Key` made 2 attempts; `503` with `Retry-After: 1` waited ≥1 s; a budget with `minRetries: 0, ratio: 0` made 1 attempt.

---

## Library and Mesh Configs

Configure retries in exactly one layer where possible; if the mesh retries, disable client-library retries for that hop. Defaults below come from each project's primary docs; defaults change between releases, so re-check the linked page for the version you run.

**gRPC service config** ([gRFC A6](https://github.com/grpc/proposal/blob/master/A6-client-retries.md)): `maxAttempts` counts the original call and is clamped to 5; jitter is ±20%; `retryThrottling` is the built-in budget.

```json
{
  "methodConfig": [{
    "name": [{ "service": "payments.v1.Payments", "method": "GetPayment" }],
    "retryPolicy": {
      "maxAttempts": 3, "initialBackoff": "0.1s", "maxBackoff": "1s",
      "backoffMultiplier": 2, "retryableStatusCodes": ["UNAVAILABLE"]
    }
  }],
  "retryThrottling": { "maxTokens": 10, "tokenRatio": 0.1 }
}
```

`retryThrottling`: each failure costs 1 token, each success adds `tokenRatio`; retries stop while tokens ≤ `maxTokens/2`. `hedgingPolicy` (`maxAttempts`, `hedgingDelay`, `nonFatalStatusCodes`) replaces `retryPolicy` for a method — use one or the other. Servers can suppress retries with the `grpc-retry-pushback-ms` trailer.

**Envoy / Istio route retry**: `retry_on: "5xx,reset,connect-failure,refused-stream"`, `num_retries`, `per_try_timeout`, `retry_back_off`; `rate_limited_retry_back_off.reset_headers` honours `Retry-After`. `retriable-4xx` only covers 409 — leave it off unless the write is idempotent. Pair with the cluster `circuit_breakers.thresholds[].retry_budget` described above ([router filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/router_filter)).

**Polly v8 / `Microsoft.Extensions.Http.Resilience`**: `AddStandardResilienceHandler()` stacks rate limiter (1,000 permits) → total timeout 30 s → retry (3, exponential, jitter, 2 s base) → circuit breaker (10% failure ratio, min throughput 100, 30 s sampling, 5 s break) → attempt timeout 10 s. It retries 5xx, 408 and 429 **for all HTTP methods by default**; call `DisableFor(HttpMethod.Post, ...)` or `DisableForUnsafeHttpMethods()` on the retry options for non-idempotent calls ([MS Learn](https://learn.microsoft.com/dotnet/core/resilience/http-resilience)). Raw Polly `RetryStrategyOptions` defaults are `MaxRetryAttempts = 3`, `BackoffType = Constant`, `UseJitter = false` — set exponential + jitter explicitly ([Polly retry docs](https://www.pollydocs.org/strategies/retry)).

**resilience4j CircuitBreaker** defaults: `failureRateThreshold` 50, `slowCallRateThreshold` 100, `slowCallDurationThreshold` 60 000 ms, `slidingWindowType` COUNT_BASED, `slidingWindowSize` 100, `minimumNumberOfCalls` 100, `waitDurationInOpenState` 60 000 ms, `permittedNumberOfCallsInHalfOpenState` 10 ([docs](https://resilience4j.readme.io/docs/circuitbreaker)). The 60 s slow-call default means slow-call tripping is effectively off until you set `slowCallDurationThreshold` near your p99 SLO.

---

## Idempotency Notes

> **Exactly-once myth:** No transport protocol delivers a message exactly once. TCP gives at-most-once when packets are lost; application retries yield at-least-once. "Exactly-once" is an application-level illusion: combine at-least-once delivery with idempotent processing and server-side deduplication. Design for at-least-once; dedupe at the receiver. See [idempotency-key-design.md](idempotency-key-design.md).

- Safe to retry: `GET`, `PUT` (same payload), `DELETE`, and `POST` with an idempotency key + server-side dedupe.
- Avoid retrying: non-idempotent writes without a dedupe strategy (creates duplicate side effects).

---

## Checklist

- Exception classification (retryable vs non-retryable) happens before the retry loop, not inside it.
- Every retry loop has an overall deadline and a max-attempt cap.
- Backoff uses jitter and caps maximum delay.
- Retries are safe (idempotent) or protected by idempotency keys/dedup.
- `429`/`503` honor `Retry-After` when provided.
- Retries are paired with timeouts, bulkheads, and circuit breakers to avoid cascading failures.
- For message consumers: `OperationCanceledException` from shutdown exits the loop cleanly — it is not routed through retry logic.

---

## Related Resources

- [timeout-policies.md](timeout-policies.md) - Per-try + overall deadline budgets
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) - Avoid retrying into a broken dependency
- [resilience-checklists.md](resilience-checklists.md) - Release and production hardening checks
