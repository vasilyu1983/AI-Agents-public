# Resilience Policy Defaults

## Purpose
- Use these defaults as starting points.
- Tune from real latency/error telemetry per dependency.

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
- Retries: avoid generic retries for writes unless idempotent and safe.
- Connection pool: set conservative max connections and monitor saturation.

## Message processing
- Handler timeout: explicit per message type.
- Retries: bounded with dead-letter after max attempts.
- Idempotency: required for any handler retry path.

## Background jobs
- Retry budget: bounded by business tolerance and downstream impact.
- Backoff: progressive with caps; avoid retry storms.
- Concurrency: cap per queue and dependency capacity.

## Safe rollout steps
- Start with conservative retries.
- Add telemetry for timeout, retry attempts, circuit open events.
- Load test before increasing concurrency or retry budgets.
