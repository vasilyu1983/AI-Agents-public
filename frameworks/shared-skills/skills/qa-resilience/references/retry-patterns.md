# Retry Patterns (Backoff, Jitter, Retry Budgets)

Production-ready retry guidance for transient failures in distributed systems.

---
## Table of Contents

- [Core Rules](#core-rules)
- [Expert Judgment: Retry Budget vs. Retry Count](#expert-judgment-retry-budget-vs-retry-count)
- [Retry Decision Table (Starting Point)](#retry-decision-table-starting-point)
- [Reference Implementation (Node.js `fetch`)](#reference-implementation-nodejs-fetch)
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

A fixed "max 3 retries per call site" rule is the most common retry mistake in production systems, because it is a per-request limit applied independently at every layer. In a 3-layer call chain (client → gateway → service) where each layer independently retries 3 times, the worst-case amplification at the origin is 3 × 3 × 3 = **27×** the original request volume — not 3×, and not 9×. This is exact multiplication, not folklore: each layer's retry is invisible to the layers above it, so the layers compound rather than share a budget.

Retry **count** answers "how many times may this one request retry?" Retry **budget** answers "what fraction of this service's total outbound call volume during a rolling window may be retries?" — typically expressed as a ratio, e.g. "retries may not exceed 10% of non-retry requests over a trailing 10-second window" (this is the model used by Envoy's and Finagle's retry-budget implementations). The budget approach is what actually prevents retry storms during partial outages, because it automatically tightens as the system-wide error rate rises: if 40% of calls are already failing, a fixed per-call retry count keeps retrying at the same rate and adds to the overload, while a budget starts rejecting new retries once the budget is exhausted, converting excess load into fast failures instead of amplification.

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

This is intentionally library-agnostic so it works even when retry libraries cannot honor `Retry-After` precisely.

```javascript
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseRetryAfterMs(retryAfter) {
  if (!retryAfter) return null;
  const seconds = Number(retryAfter);
  if (Number.isFinite(seconds)) return Math.max(0, seconds * 1000);
  const dateMs = Date.parse(retryAfter);
  if (Number.isFinite(dateMs)) return Math.max(0, dateMs - Date.now());
  return null;
}

function computeBackoffMs(attempt, baseMs, maxMs) {
  const exp = Math.min(maxMs, baseMs * 2 ** (attempt - 1));
  const jitter = exp * (0.5 + Math.random()); // 0.5x..1.5x
  return Math.min(maxMs, Math.floor(jitter));
}

async function fetchWithRetry(
  url,
  init = {},
  {
    attempts = 3,
    perTryTimeoutMs = 3000,
    baseBackoffMs = 200,
    maxBackoffMs = 5000,
    overallDeadlineMs = 10000,
  } = {}
) {
  const deadlineAt = Date.now() + overallDeadlineMs;

  for (let attempt = 1; attempt <= attempts; attempt++) {
    const remainingMs = deadlineAt - Date.now();
    if (remainingMs <= 0) throw new Error('Retry deadline exhausted');

    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      Math.min(perTryTimeoutMs, remainingMs)
    );

    try {
      const res = await fetch(url, { ...init, signal: controller.signal });

      if (res.status === 429 || res.status === 503) {
        const retryAfterMs = parseRetryAfterMs(res.headers.get('Retry-After'));
        const err = new Error(`HTTP ${res.status}`);
        err.retryAfterMs = retryAfterMs;
        throw err;
      }

      if (res.status >= 500 && res.status < 600) {
        throw new Error(`HTTP ${res.status}`);
      }

      if (!res.ok) {
        const err = new Error(`HTTP ${res.status}`);
        err.retryable = false;
        throw err;
      }

      return res;
    } catch (err) {
      const retryable =
        err?.retryable !== false &&
        (err?.name === 'AbortError' || err?.retryAfterMs != null || err instanceof TypeError);

      if (!retryable || attempt === attempts) throw err;

      const serverDelayMs = err?.retryAfterMs ?? 0;
      const backoffMs = computeBackoffMs(attempt, baseBackoffMs, maxBackoffMs);
      const delayMs = Math.min(
        Math.max(serverDelayMs, backoffMs),
        Math.max(0, deadlineAt - Date.now())
      );

      await sleep(delayMs);
    } finally {
      clearTimeout(timeoutId);
    }
  }

  throw new Error('Unreachable');
}
```

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
