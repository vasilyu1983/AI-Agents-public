# Resilience Policy Defaults

## Purpose
- Use these defaults as starting points.
- Tune from real latency/error telemetry per dependency.

## Standard handler defaults you must override
`AddStandardResilienceHandler()` ships with built-in defaults. The values below are Microsoft's documented defaults; re-read the `Microsoft.Extensions.Http.Resilience` docs for your package version before relying on them. Strategies are listed outermost first:
| Strategy | Default |
| --- | --- |
| Rate limiter | 1,000 permits, queue 0 |
| Total request timeout | 30s |
| Retry | 3 retries, exponential backoff with jitter, 2s base delay, **all HTTP methods** |
| Circuit breaker | 10% failure ratio, min throughput 100, 30s sampling, 5s break |
| Attempt timeout | 10s |

- For writes, call `DisableForUnsafeHttpMethods()` unless the endpoint is idempotent (for example, it takes an idempotency key).
- Before adding a handler, check whether `ConfigureHttpClientDefaults` already adds one to every client. Stacked handlers multiply retries and nest timeouts; keep one pipeline per client (see `references/reliability-and-resilience.md`).
- Set the total timeout inside the caller's remaining budget. An inner 30s total under a 10s inbound `RequestTimeout` wastes work after the caller has given up.
- For read fan-out to replicas, consider `AddStandardHedgingHandler()` instead of retry.
- The numbers below are starting points. Apply them through the handler options and do not leave the defaults silently in place.

## HTTP internal service calls
- Timeout: `2s` to `5s`.
- Retries: up to `2` attempts for transient failures.
- Backoff: exponential with jitter (`100ms`, `300ms`, `800ms` ranges).
- Circuit breaker: open on high error ratio over short rolling window.

## HTTP third-party APIs
- Timeout: `5s` to `15s` depending on provider SLA.
- Retries: `1` to `2` attempts; honor vendor rate-limit signals.
- Backoff: jittered exponential with longer initial delay.
- Circuit breaker: open quickly to avoid quota burn on outage.

## Database operations
- Query timeout: `1s` to `3s` for hot paths, higher for batch/admin paths.
- Retries: avoid generic retries for writes unless idempotent and safe. A retrying EF Core execution strategy is already a retry layer; do not wrap it in another.
- Connection pool: set conservative max connections and monitor saturation.

## Message processing
- Handler timeout: explicit per message type.
- Retries: bounded with dead-letter after max attempts.
- Idempotency: required for any handler retry path.
- Commit safety: never commit offset or acknowledge after failure. Commit only after success, retry-topic publish, or DLQ publish.
- Failure classification: classify retryable vs non-retryable before the retry loop, not inside it.
- Cancellation: treat `OperationCanceledException` from shutdown as clean exit — do not route to retry/DLQ or commit.
- Failure isolation: if retry/DLQ publish fails, pause the affected partition only — do not kill the entire consumer task.

## Background jobs
- Retry budget: bounded by business tolerance and downstream impact.
- Backoff: progressive with caps; avoid retry storms.
- Concurrency: cap per queue and dependency capacity.

## Safe rollout steps
- Start with conservative retries.
- Add telemetry for timeout, retry attempts, circuit open events.
- Load test before increasing concurrency or retry budgets.
