# Log Aggregation Patterns

Structured logging pipelines, cost control strategies, and platform comparison for production log management. Covers collection, processing, storage, and querying.

## Contents

- [Structured Logging Standards](#structured-logging-standards)
- [Log Levels Guide](#log-levels-guide)
- [Logging Pipeline Architecture](#logging-pipeline-architecture)
- [Platform Comparison](#platform-comparison)
- [Log Sampling Strategies](#log-sampling-strategies)
- [Cardinality Control](#cardinality-control)
- [PII Redaction in Logs](#pii-redaction-in-logs)
- [Log Retention Policies](#log-retention-policies)
- [Cost Optimization](#cost-optimization)
- [Correlation ID Injection](#correlation-id-injection)
- [Log-Based Alerting](#log-based-alerting)
- [Related Resources](#related-resources)

---

## Structured Logging Standards

Unstructured logs are unqueryable at scale. Structure every log line as JSON with consistent field names.

### JSON Log Format

```json
{
  "timestamp": "2026-01-15T10:30:45.123Z",
  "level": "error",
  "service": "order-api",
  "environment": "production",
  "trace_id": "abc123def456",
  "span_id": "789ghi012",
  "request_id": "req-uuid-here",
  "message": "Failed to process payment",
  "error": {
    "type": "PaymentGatewayTimeout",
    "message": "Connection timed out after 5000ms",
    "stack": "at PaymentClient.charge (payment.ts:42)..."
  },
  "context": {
    "order_id": "ORD-12345",
    "amount": 99.99,
    "currency": "USD",
    "user_id": "usr-67890"
  },
  "http": {
    "method": "POST",
    "path": "/api/v1/orders/ORD-12345/pay",
    "status_code": 504,
    "duration_ms": 5012
  }
}
```

### Field Naming Conventions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 | Yes | When the event occurred |
| `level` | string | Yes | debug, info, warn, error, fatal |
| `service` | string | Yes | Emitting service name |
| `environment` | string | Yes | prod, staging, dev |
| `trace_id` | string | Yes | W3C trace context ID |
| `span_id` | string | Yes | Current span ID |
| `request_id` | string | Yes | Application request ID |
| `message` | string | Yes | Human-readable description |
| `error.type` | string | Conditional | Error class name (when level = error) |
| `error.message` | string | Conditional | Error detail |
| `context.*` | object | Optional | Business context (order_id, user_id) |
| `http.*` | object | Optional | HTTP request metadata |

### Implementation: Python

```python
import structlog
import logging

# Configure structlog for JSON output
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()

# Usage
log.info("order.created", order_id="ORD-123", amount=99.99, user_id="usr-456")
log.error("payment.failed", order_id="ORD-123", error_type="timeout", duration_ms=5012)
```

### Implementation: Node.js

```javascript
const pino = require("pino");

const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  formatters: {
    level(label) {
      return { level: label };
    },
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  base: {
    service: process.env.SERVICE_NAME || "order-api",
    environment: process.env.NODE_ENV || "development",
  },
});

// Usage
logger.info({ order_id: "ORD-123", amount: 99.99 }, "order.created");
logger.error(
  { order_id: "ORD-123", err: new Error("Payment timeout"), duration_ms: 5012 },
  "payment.failed"
);
```

---

## Log Levels Guide

### When to Use Each Level

| Level | When to Use | Examples | Volume Target |
|-------|------------|---------|---------------|
| **FATAL** | Process is about to crash | Unrecoverable errors, out of memory | < 1/day |
| **ERROR** | Operation failed, needs attention | Payment failed, DB connection lost | < 1% of requests |
| **WARN** | Unexpected but recoverable | Retry succeeded, fallback activated, deprecated API used | < 5% of requests |
| **INFO** | Normal operations worth recording | Request completed, order created, deploy started | 1 line per request |
| **DEBUG** | Detailed flow for troubleshooting | SQL queries, cache hits/misses, branch decisions | Off in production |
| **TRACE** | Very granular (method entry/exit) | Function arguments, loop iterations | Off in production |

### Level Selection Decision Tree

```
Is this a normal, expected event?
├── Yes → INFO (or skip if high volume)
└── No → Did something go wrong?
    ├── Yes → Did the operation fail?
    │   ├── Yes → Is the process crashing?
    │   │   ├── Yes → FATAL
    │   │   └── No → ERROR
    │   └── No (recovered) → WARN
    └── No → Is this helpful for debugging?
        ├── Yes → DEBUG
        └── Very granular → TRACE
```

### Common Level Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Logging expected 404s as ERROR | Inflates error count | Use INFO for expected client errors |
| DEBUG in production | Massive volume, high cost | Use INFO in prod, DEBUG only temporarily |
| No WARN level used | Jump from INFO to ERROR | Use WARN for retries, fallbacks |
| Logging secrets at any level | Security vulnerability | Redact before logging |

---

## Logging Pipeline Architecture

### Standard Pipeline

```
Application → Agent → Collector → Aggregator → Storage → Query UI

Components:
  Application: Structured JSON to stdout
  Agent: Filebeat, Fluent Bit, OTEL Collector (per node)
  Collector: Logstash, Fluentd, Vector (centralized)
  Aggregator: Index and enrich
  Storage: Elasticsearch, Loki, S3 (cold)
  Query UI: Kibana, Grafana, Datadog
```

### OpenTelemetry Collector Pipeline

```yaml
# otel-collector-config.yaml
receivers:
  filelog:
    include:
      - /var/log/pods/*/*/*.log
    operators:
      - type: json_parser
        timestamp:
          parse_from: attributes.timestamp
          layout: "%Y-%m-%dT%H:%M:%S.%fZ"

processors:
  batch:
    timeout: 5s
    send_batch_size: 1000

  attributes:
    actions:
      - key: cluster
        value: "prod-us-east-1"
        action: upsert

  filter:
    logs:
      exclude:
        match_type: strict
        bodies:
          - "health check"
          - "readiness probe"

exporters:
  loki:
    endpoint: "http://loki:3100/loki/api/v1/push"
    labels:
      attributes:
        service: ""
        level: ""
        environment: ""

  elasticsearch:
    endpoints: ["https://elasticsearch:9200"]
    index: "logs-${service}-${date}"

service:
  pipelines:
    logs:
      receivers: [filelog]
      processors: [batch, attributes, filter]
      exporters: [loki]
```

### Fluent Bit Configuration

```ini
# fluent-bit.conf
[SERVICE]
    Flush         5
    Log_Level     info
    Parsers_File  parsers.conf

[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    Tag               kube.*
    Refresh_Interval  5
    Mem_Buf_Limit     50MB

[FILTER]
    Name         kubernetes
    Match        kube.*
    Merge_Log    On
    K8S-Logging.Parser On

[FILTER]
    Name    grep
    Match   *
    Exclude log health check

[OUTPUT]
    Name        loki
    Match       *
    Host        loki
    Port        3100
    Labels      job=fluent-bit, service=$kubernetes['labels']['app']
    Auto_Kubernetes_Labels On
```

---

## Platform Comparison

| Feature | ELK (Elasticsearch) | Grafana Loki | Datadog Logs | CloudWatch Logs |
|---------|---------------------|--------------|--------------|-----------------|
| **Architecture** | Full-text index | Label-based, chunk storage | SaaS | SaaS |
| **Query language** | KQL / Lucene | LogQL | Custom | Insights QL |
| **Storage cost** | High (indexes everything) | Low (indexes labels only) | High (per GB ingested) | Medium |
| **Query speed** | Fast (pre-indexed) | Slower for full-text | Fast | Medium |
| **Correlation** | Via Kibana | Native Grafana | Native | Limited |
| **Scaling** | Complex (shard management) | Simple (object storage) | Managed | Managed |
| **Best for** | Complex queries, compliance | Cost-sensitive, Grafana shops | All-in-one APM | AWS-native |
| **Self-hosted** | Yes | Yes | No | No |
| **OSS** | Yes (basic) | Yes | No | No |

### Decision Framework

```
Need full-text search across all fields?
├── Yes → Elasticsearch / Datadog
└── No → Loki (much cheaper)

Already using Grafana for metrics?
├── Yes → Loki (native integration)
└── No → Consider Datadog or ELK

Budget constrained?
├── Yes → Loki (label-indexed, cheap storage)
└── No → Datadog or Elasticsearch

Compliance requires long retention?
├── Yes → S3 + Athena for cold storage
└── No → Standard platform retention
```

---

## Log Sampling Strategies

At scale, logging every event is prohibitively expensive. Sample strategically.

### Sampling Approaches

| Strategy | How It Works | Use Case |
|----------|-------------|----------|
| **Head sampling** | Decide at request start (log 10% of requests) | General volume reduction |
| **Tail sampling** | Log everything, drop after analysis | Keep errors, drop successes |
| **Priority sampling** | Always log errors, sample info/debug | Best balance of cost and visibility |
| **Dynamic sampling** | Adjust rate based on volume | Handle traffic spikes |

### Priority Sampling Implementation

```python
import random
import structlog

log = structlog.get_logger()

# Sampling configuration
SAMPLING_CONFIG = {
    "error": 1.0,    # Log 100% of errors
    "warn": 1.0,     # Log 100% of warnings
    "info": 0.1,     # Log 10% of info
    "debug": 0.01,   # Log 1% of debug (if enabled)
}

def should_sample(level: str, is_error_request: bool = False) -> bool:
    """Determine if this log line should be emitted."""
    # Always log for requests that had errors
    if is_error_request:
        return True

    rate = SAMPLING_CONFIG.get(level, 0.1)
    return random.random() < rate

class SamplingProcessor:
    """Structlog processor that applies sampling."""

    def __call__(self, logger, method_name, event_dict):
        level = event_dict.get("level", "info")
        is_error = event_dict.get("_error_request", False)

        if not should_sample(level, is_error):
            raise structlog.DropEvent

        # Add sampling metadata
        event_dict["_sampled"] = True
        event_dict["_sample_rate"] = SAMPLING_CONFIG.get(level, 0.1)
        return event_dict
```

---

## Cardinality Control

High-cardinality fields (user IDs, request IDs, UUIDs) can explode index sizes and query performance.

### Cardinality Rules

| Field Type | Cardinality | Index? | Store? |
|-----------|-------------|--------|--------|
| `service` | Low (10-50) | Yes (label) | Yes |
| `level` | Very low (5) | Yes (label) | Yes |
| `environment` | Very low (3-5) | Yes (label) | Yes |
| `http.status_code` | Low (~20) | Yes (label) | Yes |
| `http.path` | Medium (100-1000) | Parameterize first | Yes |
| `user_id` | High (millions) | No (search body) | Yes |
| `request_id` | Very high (unique) | No (search body) | Yes |
| `trace_id` | Very high (unique) | No (search body) | Yes |

### URL Parameterization

```python
"""
Reduce cardinality by parameterizing URLs before using as labels.
"""
import re

# BEFORE: /api/users/12345/orders/67890 (infinite cardinality)
# AFTER:  /api/users/:id/orders/:id     (finite cardinality)

URL_PATTERNS = [
    (r'/users/[a-zA-Z0-9-]+', '/users/:id'),
    (r'/orders/[A-Z]+-\d+', '/orders/:id'),
    (r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/:uuid'),
    (r'/\d+', '/:id'),
]

def parameterize_path(path: str) -> str:
    for pattern, replacement in URL_PATTERNS:
        path = re.sub(pattern, replacement, path)
    return path

# Test
assert parameterize_path("/api/users/12345/orders/ORD-789") == "/api/users/:id/orders/:id"
```

---

## PII Redaction in Logs

Never log personally identifiable information. Redact before it reaches the pipeline.

### Redaction at the Application Layer

```python
"""
Log processor that redacts PII fields before emission.
"""
import re
import structlog

PII_PATTERNS = {
    "email": re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    "credit_card": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
    "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
    "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
}

PII_FIELDS = {"email", "phone", "ssn", "credit_card", "password", "token", "secret"}

def redact_pii(logger, method_name, event_dict):
    """Structlog processor to redact PII from log events."""
    for key, value in list(event_dict.items()):
        # Redact known PII field names
        if key.lower() in PII_FIELDS:
            event_dict[key] = "[REDACTED]"
            continue

        # Redact PII patterns in string values
        if isinstance(value, str):
            for pii_type, pattern in PII_PATTERNS.items():
                if pattern.search(value):
                    event_dict[key] = pattern.sub(f"[REDACTED_{pii_type.upper()}]", value)

    return event_dict

# Configure structlog with PII redaction
structlog.configure(
    processors=[
        redact_pii,  # Must be early in the chain
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
```

### Pipeline-Level Redaction (Fluent Bit)

```ini
# Redact email addresses in the pipeline
[FILTER]
    Name          modify
    Match         *
    Condition     Key_Value_Matches log .*@.*\..*
    Set           log [EMAIL REDACTED]

# Remove sensitive fields entirely
[FILTER]
    Name          record_modifier
    Match         *
    Remove_key    password
    Remove_key    authorization
    Remove_key    cookie
```

---

## Log Retention Policies

### Tiered Retention

| Tier | Storage | Retention | Use Case | Cost |
|------|---------|-----------|----------|------|
| **Hot** | Elasticsearch / Loki | 7-14 days | Active debugging, search | $$$ |
| **Warm** | Reduced replicas / S3 IA | 30-90 days | Recent incident investigation | $$ |
| **Cold** | S3 Glacier / Archive | 1-7 years | Compliance, audit, legal | $ |
| **Deleted** | -- | Beyond policy | -- | Free |

### Retention Policy Configuration

```yaml
# Elasticsearch ILM policy
PUT _ilm/policy/log-retention
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50gb",
            "max_age": "1d"
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 },
          "allocate": { "number_of_replicas": 0 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "searchable_snapshot": {
            "snapshot_repository": "s3-logs"
          }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": { "delete": {} }
      }
    }
  }
}
```

---

## Cost Optimization

### Volume Reduction Checklist

- [ ] **Filter health checks** -- do not ingest liveness/readiness probe logs
- [ ] **Sample info-level logs** -- 10% sampling for high-volume services
- [ ] **Remove duplicate fields** -- Kubernetes metadata duplicates, redundant tags
- [ ] **Compress before shipping** -- gzip at the agent level
- [ ] **Parameterize URLs** -- reduce label cardinality
- [ ] **Drop debug/trace in production** -- set minimum level to INFO
- [ ] **Deduplicate repeated errors** -- log once per minute, not per request
- [ ] **Use tiered storage** -- hot/warm/cold based on age
- [ ] **Set retention limits** -- delete logs beyond compliance requirements

### Cost Comparison (Approximate Monthly, 1 TB/day Ingestion)

| Platform | Ingestion Cost | Storage (30d) | Total Estimate |
|----------|---------------|---------------|----------------|
| **ELK self-hosted** | Infrastructure only | ~$2,000/mo | ~$5,000-10,000/mo |
| **Grafana Loki** | Infrastructure only | ~$500/mo (S3) | ~$2,000-5,000/mo |
| **Datadog** | $0.10/GB ingested | Included (15d) | ~$3,000/mo |
| **CloudWatch** | $0.50/GB ingested | $0.03/GB stored | ~$15,000/mo |

---

## Correlation ID Injection

### Middleware Pattern

```python
"""
FastAPI middleware that injects correlation IDs into every log line.
Enables tracing a request across services via logs.
"""
import uuid
from contextvars import ContextVar
from fastapi import FastAPI, Request
import structlog

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="")

app = FastAPI()

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    # Extract or generate correlation IDs
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    trace_id = request.headers.get("traceparent", "").split("-")[1] if "traceparent" in request.headers else str(uuid.uuid4())

    # Set in context for structlog
    request_id_ctx.set(request_id)
    trace_id_ctx.set(trace_id)

    # Bind to structlog context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        trace_id=trace_id,
    )

    response = await call_next(request)

    # Propagate IDs in response headers
    response.headers["X-Request-ID"] = request_id
    return response
```

### Node.js (Express Middleware)

```javascript
const { v4: uuidv4 } = require("uuid");
const pino = require("pino");
const { AsyncLocalStorage } = require("async_hooks");

const asyncLocalStorage = new AsyncLocalStorage();

function correlationMiddleware(req, res, next) {
  const requestId = req.headers["x-request-id"] || uuidv4();
  const traceId = req.headers["traceparent"]?.split("-")[1] || uuidv4();

  const context = { requestId, traceId };
  res.setHeader("X-Request-ID", requestId);

  asyncLocalStorage.run(context, () => next());
}

// Logger that automatically includes correlation IDs
const logger = pino({
  mixin() {
    const store = asyncLocalStorage.getStore();
    return store ? { request_id: store.requestId, trace_id: store.traceId } : {};
  },
});
```

---

## Log-Based Alerting

Alert on log patterns when metrics do not capture the condition.

### Loki Alert Rules

```yaml
# loki-rules.yaml
groups:
  - name: log-based-alerts
    rules:
      - alert: UnexpectedPanicDetected
        expr: |
          count_over_time({service="order-api"} |= "panic" [5m]) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Panic detected in order-api logs"
          runbook: "https://runbooks.example.com/panic-recovery"

      - alert: HighAuthFailureRate
        expr: |
          sum(count_over_time({service="auth-api"} |= "authentication failed" [5m]))
          /
          sum(count_over_time({service="auth-api"} |= "authentication" [5m]))
          > 0.3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Authentication failure rate exceeds 30%"

      - alert: DatabaseConnectionExhausted
        expr: |
          count_over_time({service=~".+"} |= "connection pool exhausted" [5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool exhausted"
```

### When to Use Log-Based vs Metric-Based Alerts

| Condition | Use Logs | Use Metrics |
|-----------|----------|-------------|
| Error message contains specific text | Yes | No |
| Error rate exceeds threshold | No | Yes |
| Stack trace pattern detection | Yes | No |
| Latency exceeds target | No | Yes |
| Security event (brute force) | Yes | Maybe |
| Resource utilization | No | Yes |
| Unique error types trending | Yes | No |

---

## Related Resources

- [Core Observability Patterns](./core-observability-patterns.md) - Metrics, logs, traces overview
- [Alerting Strategies](./alerting-strategies.md) - Alert design and fatigue reduction
- [Dashboard Design Patterns](./dashboard-design-patterns.md) - Visualizing log data
- [Distributed Tracing Patterns](./distributed-tracing-patterns.md) - Trace-log correlation
- [OpenTelemetry Best Practices](./opentelemetry-best-practices.md) - OTEL log collection
- [SKILL.md](../SKILL.md) - Parent skill overview
