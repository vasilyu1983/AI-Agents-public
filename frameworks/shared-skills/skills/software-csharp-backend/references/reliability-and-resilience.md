# Reliability and Resilience

## Timeout strategy
- Set explicit timeout per outbound dependency based on SLO and dependency behavior.
- Keep request timeout budgeted across retries and downstream calls.
- Fail fast for degraded dependencies when work is non-critical.

## Retry strategy
- Classify exceptions into retryable and non-retryable before entering any retry loop. Non-retryable exceptions (validation, schema, deterministic business rejection) must be routed to dead-letter or terminal failure handling immediately — not after exhausting retry attempts.
- Retry only transient failures (timeouts, 5xx, throttling).
- Use bounded exponential backoff with jitter.
- Never retry non-idempotent writes without idempotency guarantees.
- Emit retry metrics/log events with attempt count and reason.
- If using `AddStandardResilienceHandler()`, remember that retries apply to unsafe HTTP methods unless you disable them or customize the strategy explicitly.

## Circuit breakers and load protection
- Use circuit breakers for unstable dependencies to prevent resource exhaustion.
- Use concurrency limits/bulkheads for expensive outbound calls.
- Define fallback behavior per use case (cached response, partial result, fail closed).

## Cancellation and request lifecycle
- Propagate `CancellationToken` through all async work.
- Stop downstream work quickly after cancellation.
- Ensure disposal and cleanup paths are cancellation-safe.
- Treat cancellation as control flow, not failure handling. In message consumers and background workers, `OperationCanceledException` from host shutdown must exit the processing loop cleanly — never route to retry/DLQ, never commit the message offset, and never log as a processing failure. Consumer loops need an explicit shutdown path that completes before failure routing kicks in.

## Background jobs and workers
- Make job handlers idempotent and resumable.
- Store job progress/checkpoints for long-running workflows.
- Separate retry policy for jobs from online request policy.
- Add dead-letter handling and operator-visible failure diagnostics.
- Choose `IHostedService`/`BackgroundService` for the outer lifecycle (start/stop/graceful shutdown) of any long-running worker — that part is not optional.
- Inside a `BackgroundService`, reach for `System.Threading.Channels` (bounded `Channel<T>`) when you need in-process producer/consumer decoupling with backpressure — for example, an API request enqueueing work for a background drain. Do not fire-and-forget `Task.Run` from a request path as a substitute; unobserved exceptions and process restarts silently drop that work.
- Reach for an external durable queue (message broker, outbox-backed table) instead of an in-memory `Channel<T>` the moment the work must survive a process restart or scale across instances — a `Channel<T>` is a single-process buffer, not a durability guarantee.

## Message consumer commit safety
- Never commit message offsets (or acknowledge messages) after a processing failure. Committing in `finally` regardless of outcome defeats manual commit mode and causes acknowledged message loss.
- With manual commit mode (`enable.auto.commit=false`), commit the source offset only after one durable outcome: successful processing, durable publish to a retry topic, or durable publish to a DLQ topic.
- Isolate failure-routing failures to the narrowest scope possible. If publishing to a retry/DLQ topic fails, pause or park only the affected partition — do not silently kill the entire consumer task or leave a dead background task behind.

## Reliability review checklist
- Are timeouts defined in config and tested?
- Are retries bounded, observable, and idempotent-safe?
- Is worker behavior recoverable after crash/restart?
- Do message consumers commit only after a durable outcome, not in `finally`?
- Is `OperationCanceledException` handled as shutdown, not as processing failure?
- Are non-retryable exceptions classified before entering retry loops?
