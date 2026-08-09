# Log Aggregation Patterns

Structured logging pipelines, correlation rules, and cost-control patterns for production systems.

## Table of Contents

- [Structured logging standard](#structured-logging-standard)
- [Collector-first pipeline](#collector-first-pipeline)
- [Correlation pattern](#correlation-pattern)
- [Python](#python)
- [Node.js](#nodejs)
- [Label discipline](#label-discipline)
- [Retention and cost control](#retention-and-cost-control)
- [Log-based alerts](#log-based-alerts)

## Structured logging standard

Use JSON logs in production with a stable schema.

```json
{
  "timestamp": "2026-03-13T10:30:45.123Z",
  "level": "error",
  "service": "order-api",
  "environment": "production",
  "message": "payment.capture.failed",
  "request_id": "4f6d1d54-92f2-4d90-b8c4-5170fb812d95",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "order_id": "ORD-12345",
  "error_type": "PaymentGatewayTimeout"
}
```

Required fields:
- timestamp
- level
- service
- environment
- message
- request_id when a request exists
- trace_id and span_id when a span exists

## Collector-first pipeline

Recommended pipeline:

```text
application stdout/stderr
  -> per-node shipper or Collector receiver
  -> parse JSON once
  -> filter noise
  -> route to log backend and archive tier
```

Example Collector pipeline:

```yaml
receivers:
  filelog:
    include:
      - /var/log/pods/*/*/*.log

processors:
  batch:
    timeout: 5s
  filter:
    logs:
      exclude:
        match_type: strict
        bodies:
          - "health check"
          - "readiness probe"

exporters:
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
    labels:
      attributes:
        service: ""
        environment: ""
        level: ""

service:
  pipelines:
    logs:
      receivers: [filelog]
      processors: [batch, filter]
      exporters: [loki]
```

## Correlation pattern

Pull trace identifiers from the active span context instead of re-parsing inbound headers.

### Python

```python
import structlog
from opentelemetry import trace

def bind_trace_fields() -> None:
    ctx = trace.get_current_span().get_span_context()

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        trace_id=format(ctx.trace_id, "032x") if ctx.is_valid else None,
        span_id=format(ctx.span_id, "016x") if ctx.is_valid else None,
    )
```

### Node.js

```javascript
const { trace } = require('@opentelemetry/api');

function traceFields() {
  const ctx = trace.getActiveSpan()?.spanContext();

  return {
    trace_id: ctx?.traceId,
    span_id: ctx?.spanId,
  };
}
```

## Label discipline

Good labels:
- service
- environment
- level
- cluster or region when operationally necessary

Bad labels:
- request IDs
- trace IDs
- user IDs
- order IDs
- emails or account identifiers

Rule:
- unique IDs belong in searchable log payloads, not index labels.

## Retention and cost control

Use tiered retention:
- hot retention for operational debugging
- cheaper object storage or archive tier for longer investigations

Reduce waste by:
- dropping health checks and repetitive probe noise
- lowering debug volume in production
- sampling known-high-volume success paths only when they are not required for forensics
- centralizing redaction and field normalization in the collector pipeline

## Log-based alerts

Use log-based alerts only when metrics cannot express the condition cleanly.

Good candidates:
- panics
- crash loops
- specific unhandled exception classes
- parsing failures before metrics exist

Avoid:
- paging directly on generic error strings
- building primary availability alerts from logs when request metrics already exist
