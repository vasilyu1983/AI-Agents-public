# Reliability and Resilience

## Timeout strategy
- Set explicit timeout per outbound dependency based on SLO and dependency behavior.
- Keep request timeout budgeted across retries and downstream calls.
- Fail fast for degraded dependencies when work is non-critical.

## Retry strategy
- Retry only transient failures (timeouts, 5xx, throttling).
- Use bounded exponential backoff with jitter.
- Never retry non-idempotent writes without idempotency guarantees.
- Emit retry metrics/log events with attempt count and reason.

## Circuit breakers and load protection
- Use circuit breakers for unstable dependencies to prevent resource exhaustion.
- Use concurrency limits/bulkheads for expensive outbound calls.
- Define fallback behavior per use case (cached response, partial result, fail closed).

## Cancellation and request lifecycle
- Propagate `CancellationToken` through all async work.
- Stop downstream work quickly after cancellation.
- Ensure disposal and cleanup paths are cancellation-safe.

## Background jobs and workers
- Make job handlers idempotent and resumable.
- Store job progress/checkpoints for long-running workflows.
- Separate retry policy for jobs from online request policy.
- Add dead-letter handling and operator-visible failure diagnostics.

## Reliability review checklist
- Are timeouts defined in config and tested?
- Are retries bounded, observable, and idempotent-safe?
- Is worker behavior recoverable after crash/restart?
