# Retry Patterns (Backoff, Jitter, Retry Budgets)

Production-ready retry guidance for transient failures in distributed systems.

---

## Core Rules

- Bound retries by an overall deadline (timeout budget) and a retry budget.
- Use exponential backoff with jitter.
- Retry only idempotent operations (or require idempotency keys / dedupe).
- Respect server guidance (for example `Retry-After`) for `429` / `503`.
- Prevent retry storms: cap attempts, cap max delay, and add client-side rate limiting.

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

- Safe to retry: `GET`, `PUT` (same payload), `DELETE`, and `POST` with an idempotency key + server-side dedupe.
- Avoid retrying: non-idempotent writes without a dedupe strategy (creates duplicate side effects).

---

## Checklist

- Every retry loop has an overall deadline and a max-attempt cap.
- Backoff uses jitter and caps maximum delay.
- Retries are safe (idempotent) or protected by idempotency keys/dedup.
- `429`/`503` honor `Retry-After` when provided.
- Retries are paired with timeouts, bulkheads, and circuit breakers to avoid cascading failures.

---

## Related Resources

- [timeout-policies.md](timeout-policies.md) - Per-try + overall deadline budgets
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) - Avoid retrying into a broken dependency
- [resilience-checklists.md](resilience-checklists.md) - Release and production hardening checks
