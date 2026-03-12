# Observability Standards

## Structured logging
- Use structured logs with stable property names.
- Include correlation fields (`TraceId`, `SpanId`, `RequestId`, tenant/customer identifiers when allowed).
- Log at appropriate levels: Debug for diagnostics, Information for state transitions, Warning/Error for failures.
- Never log secrets, tokens, or regulated sensitive data.

## Tracing
- Create spans around inbound requests, outbound I/O, and key internal operations.
- Propagate trace context across HTTP, messaging, and background processing.
- Annotate spans with business-relevant tags (operation type, dependency name, retry attempt).

## Metrics
- Emit counters for requests, errors, retries, and dependency failures.
- Emit histograms for latency and payload size where relevant.
- Track saturation/concurrency for critical pools and workers.
- Define SLI/SLO-aligned metrics per service.

## Health checks
- Provide liveness check for process health.
- Provide readiness check for critical dependencies needed to serve traffic.
- Fail readiness when essential dependencies are unavailable.
- Keep health endpoints fast and side-effect free.

## Operability checklist
- Can operators answer "what failed, where, and why" from logs + traces + metrics?
- Are alerts based on actionable symptoms, not noisy low-level signals?
- Do dashboards include latency, error rate, and dependency health at minimum?
