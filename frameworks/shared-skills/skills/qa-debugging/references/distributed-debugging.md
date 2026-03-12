# Distributed Debugging

Techniques and tools for diagnosing issues across microservices, message queues, and distributed infrastructure using tracing, correlation, and structured observability.

---

## Contents

- [Distributed Debugging Fundamentals](#distributed-debugging-fundamentals)
- [Correlation ID Propagation](#correlation-id-propagation)
- [Distributed Tracing with OpenTelemetry](#distributed-tracing-with-opentelemetry)
- [Service Dependency Mapping](#service-dependency-mapping)
- [Log Correlation Across Services](#log-correlation-across-services)
- [Debugging Network Partitions](#debugging-network-partitions)
- [Debugging Eventual Consistency](#debugging-eventual-consistency)
- [Time Synchronization Problems](#time-synchronization-problems)
- [Debugging Message Queue Issues](#debugging-message-queue-issues)
- [Tracing Tools Reference](#tracing-tools-reference)
- [Debugging Kubernetes Networking](#debugging-kubernetes-networking)
- [Distributed Debugging Checklist](#distributed-debugging-checklist)
- [Related Resources](#related-resources)

---

## Distributed Debugging Fundamentals

Distributed debugging is harder than single-service debugging because failures span process and network boundaries.

| Challenge | Single Service | Distributed |
|-----------|---------------|-------------|
| Reproduce bug | Restart with same input | Need state of N services + timing |
| Stack trace | One trace, one process | Fragments across services |
| Timing | Deterministic within process | Clock skew, network latency |
| State inspection | Single debugger attachment | Multiple services, different languages |
| Causality | Clear call stack | Asynchronous, event-driven chains |
| Partial failure | Whole process fails or succeeds | Some services fail, others succeed |

### Debugging Strategy

```text
1. Identify the symptom (error, latency, incorrect data)
2. Find the correlation ID / trace ID from the symptom
3. Reconstruct the full request path using traces
4. Identify which service introduced the error
5. Examine that service's logs at the exact timestamp
6. Check service dependencies (DB, cache, queues) for issues
7. Verify network connectivity and timing between services
```

---

## Correlation ID Propagation

### W3C Traceparent Standard

```text
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             ├──┤ ├────────────────────────────────┤ ├──────────────┤ ├┤
           version          trace-id                   parent-id    flags

- version: 00 (current)
- trace-id: 32 hex chars, globally unique per request
- parent-id: 16 hex chars, unique per span
- flags: 01 = sampled
```

### Python Implementation (FastAPI)

```python
import uuid
from fastapi import FastAPI, Request, Response
from contextvars import ContextVar
import httpx

# Context variable for correlation ID (async-safe)
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

app = FastAPI()

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    # Extract or generate correlation ID
    trace_id = (
        request.headers.get("X-Correlation-ID")
        or request.headers.get("traceparent", "").split("-")[1]
        if len(request.headers.get("traceparent", "").split("-")) > 1
        else str(uuid.uuid4())
    )
    correlation_id.set(trace_id)

    response: Response = await call_next(request)
    response.headers["X-Correlation-ID"] = trace_id
    return response

# Propagate to downstream services
async def call_downstream(url: str, data: dict):
    async with httpx.AsyncClient() as client:
        return await client.post(
            url,
            json=data,
            headers={
                "X-Correlation-ID": correlation_id.get(),
                "traceparent": f"00-{correlation_id.get()}-{uuid.uuid4().hex[:16]}-01",
            },
        )
```

### Node.js Implementation (Express)

```javascript
const { v4: uuidv4 } = require('uuid');
const { AsyncLocalStorage } = require('async_hooks');

const correlationStore = new AsyncLocalStorage();

// Middleware: extract or create correlation ID
function correlationMiddleware(req, res, next) {
  const correlationId =
    req.headers['x-correlation-id'] ||
    extractTraceId(req.headers['traceparent']) ||
    uuidv4();

  res.setHeader('X-Correlation-ID', correlationId);

  correlationStore.run({ correlationId }, () => {
    next();
  });
}

function getCorrelationId() {
  return correlationStore.getStore()?.correlationId || 'unknown';
}

// Propagate in outbound requests
const axios = require('axios');

async function callDownstream(url, data) {
  return axios.post(url, data, {
    headers: {
      'X-Correlation-ID': getCorrelationId(),
    },
  });
}

function extractTraceId(traceparent) {
  if (!traceparent) return null;
  const parts = traceparent.split('-');
  return parts.length >= 2 ? parts[1] : null;
}

app.use(correlationMiddleware);
```

---

## Distributed Tracing with OpenTelemetry

### Python Auto-Instrumentation

```bash
# Install
pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp \
            opentelemetry-instrumentation-fastapi \
            opentelemetry-instrumentation-httpx \
            opentelemetry-instrumentation-sqlalchemy
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

# Configure tracing
provider = TracerProvider()
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://jaeger:4317")
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Auto-instrument frameworks
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()

# Manual span for custom operations
tracer = trace.get_tracer("order-service")

async def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)

        with tracer.start_as_current_span("validate_inventory"):
            inventory = await check_inventory(order_id)
            span.set_attribute("inventory.available", inventory.available)

        with tracer.start_as_current_span("charge_payment"):
            payment = await process_payment(order_id)
            span.set_attribute("payment.status", payment.status)

        if payment.status == "failed":
            span.set_status(trace.StatusCode.ERROR, "Payment failed")
            span.record_exception(PaymentError(payment.error))
```

### Node.js Auto-Instrumentation

```javascript
// tracing.js - Load before application code
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://jaeger:4317',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: 'user-service',
});

sdk.start();
```

```bash
# Run with instrumentation
node --require ./tracing.js app.js
```

### Span Attributes Best Practices

| Attribute | Example | Purpose |
|-----------|---------|---------|
| `service.name` | `order-service` | Identify source service |
| `http.method` | `POST` | Request method |
| `http.status_code` | `500` | Response status |
| `db.statement` | `SELECT * FROM orders` | Database query |
| `error` | `true` | Flag error spans |
| `user.id` | `usr_12345` | Business context |
| `order.id` | `ord_67890` | Domain-specific context |
| `retry.count` | `2` | Retry debugging |
| `queue.name` | `order-events` | Message queue context |

---

## Service Dependency Mapping

### Automated Discovery from Traces

```python
def build_dependency_map(traces: list[dict]) -> dict:
    """Build service dependency graph from trace data."""
    dependencies = {}

    for trace in traces:
        for span in trace["spans"]:
            service = span["service_name"]
            if service not in dependencies:
                dependencies[service] = {
                    "calls": set(),
                    "called_by": set(),
                    "error_rate": 0,
                    "avg_latency_ms": 0,
                }

            # Find parent span's service
            parent = find_parent_span(span, trace["spans"])
            if parent and parent["service_name"] != service:
                dependencies[service]["called_by"].add(parent["service_name"])
                if parent["service_name"] in dependencies:
                    dependencies[parent["service_name"]]["calls"].add(service)

    return dependencies
```

### Dependency Health Dashboard

```text
order-service
  ├── user-service (p99: 45ms, error: 0.1%)
  ├── inventory-service (p99: 120ms, error: 0.5%)  ⚠️ High latency
  ├── payment-service (p99: 800ms, error: 2.1%)    🔴 High errors
  │   └── stripe-api (p99: 750ms, error: 1.8%)     External dependency
  └── notification-service (p99: 30ms, error: 0.0%)
      └── email-provider (p99: 200ms, error: 0.3%) External dependency
```

---

## Log Correlation Across Services

### Structured Logging with Correlation

```python
import structlog
from contextvars import ContextVar

correlation_id: ContextVar[str] = ContextVar('correlation_id', default='unknown')

def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to every log entry."""
    event_dict["correlation_id"] = correlation_id.get()
    return event_dict

structlog.configure(
    processors=[
        add_correlation_id,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()

# All logs from this request automatically include correlation_id
log.info("order_created", order_id="ord_123", total=99.99)
# Output: {"correlation_id":"abc-123","level":"info","event":"order_created",...}
```

### Cross-Service Log Query

```bash
# Search all service logs by correlation ID (using OpenSearch/Kibana)
# KQL query:
correlation_id: "4bf92f3577b34da6a3ce929d0e0e4736"

# Using Loki (LogQL):
{service=~".+"} |= "4bf92f3577b34da6a3ce929d0e0e4736"

# Using grep across log files (emergency debugging):
grep -r "4bf92f35" /var/log/services/*/app.log | sort -t'T' -k2
```

### Log Correlation Checklist

- [ ] Correlation ID present in every log line (structured field, not free text)
- [ ] Correlation ID propagated in all HTTP headers between services
- [ ] Correlation ID included in message queue message metadata
- [ ] Logs are centralized (ELK, Loki, CloudWatch)
- [ ] Log timestamps use UTC and ISO 8601 format
- [ ] Service name included in every log entry
- [ ] Queryable by correlation ID across all services

---

## Debugging Network Partitions

### Symptoms of Network Partitions

| Symptom | Possible Cause | Investigation |
|---------|---------------|---------------|
| Timeouts between specific services | Network partition, DNS failure | `traceroute`, service mesh metrics |
| Intermittent 5xx errors | Partial partition, packet loss | Loss rate metrics, TCP retransmits |
| Split-brain behavior | Leader election during partition | Check consensus logs, fencing tokens |
| Stale data served | Partition isolated read replica | Check replication lag metrics |
| Message queue backlog | Consumer partition from broker | Consumer group lag, broker connectivity |

### Diagnostic Commands

```bash
# Check connectivity between services
kubectl exec -it <pod> -- curl -v http://other-service:8080/health

# DNS resolution
kubectl exec -it <pod> -- nslookup other-service.namespace.svc.cluster.local

# TCP connectivity
kubectl exec -it <pod> -- nc -zv other-service 8080

# Check for packet loss
kubectl exec -it <pod> -- ping -c 100 other-service

# Trace network path
kubectl exec -it <pod> -- traceroute other-service
```

---

## Debugging Eventual Consistency

### Common Consistency Issues

```text
Scenario: User updates profile, then immediately reads stale data.

Timeline:
  T1: User sends PUT /profile (hits Service A, writes to primary DB)
  T2: Service A returns 200 OK
  T3: User sends GET /profile (hits Service B, reads from replica)
  T4: Replica has not yet received the write → stale data returned

Root cause: Read-after-write consistency not guaranteed.

Fixes:
  1. Read from primary after writes (read-your-writes consistency)
  2. Include write timestamp in response, client sends it back
  3. Use sticky sessions to route to same service instance
  4. Add artificial delay or version check before serving reads
```

### Consistency Debugging Queries

```sql
-- Check replication lag (PostgreSQL)
SELECT
  client_addr,
  state,
  sent_lsn,
  write_lsn,
  flush_lsn,
  replay_lsn,
  (sent_lsn - replay_lsn) AS replication_lag_bytes
FROM pg_stat_replication;

-- Check if a specific write has propagated
-- Write includes a monotonic version number
SELECT version, updated_at
FROM users
WHERE id = 'usr_123';
-- Compare version across primary and replicas
```

---

## Time Synchronization Problems

### Clock Skew Impact

| Skew | Impact |
|------|--------|
| < 10ms | Acceptable for most distributed systems |
| 10-100ms | Log ordering may be incorrect, trace timing skewed |
| 100ms-1s | Distributed locks may fail, cache TTLs unreliable |
| > 1s | Consensus algorithms may fail, certificates may error |

### Detecting Clock Skew

```bash
# Check NTP synchronization on each node
timedatectl status
# Look for: "System clock synchronized: yes"

# Check offset from NTP server
chronyc tracking
# Key field: "System time : 0.000001234 seconds fast of NTP time"

# Compare clocks across pods
for pod in $(kubectl get pods -o name); do
  echo "$pod: $(kubectl exec $pod -- date -u +%Y-%m-%dT%H:%M:%S.%NZ)"
done
```

### Mitigating Clock Skew in Application Logic

```python
# DO NOT: Compare timestamps from different services
if service_a_timestamp < service_b_timestamp:  # UNRELIABLE
    pass

# DO: Use logical clocks or sequence numbers
class LamportClock:
    def __init__(self):
        self.counter = 0

    def increment(self) -> int:
        self.counter += 1
        return self.counter

    def receive(self, received_counter: int) -> int:
        self.counter = max(self.counter, received_counter) + 1
        return self.counter

# DO: Use hybrid logical clocks for ordering
# (combines physical time with logical counter for better ordering)
```

---

## Debugging Message Queue Issues

### Dead Letter Queue Analysis

```python
import json
from datetime import datetime

def analyze_dead_letters(dlq_messages: list[dict]) -> dict:
    """Analyze dead letter queue for patterns."""
    analysis = {
        "total": len(dlq_messages),
        "by_error": {},
        "by_source": {},
        "by_hour": {},
        "oldest": None,
        "newest": None,
    }

    for msg in dlq_messages:
        # Group by error type
        error = msg.get("error", "unknown")
        analysis["by_error"][error] = analysis["by_error"].get(error, 0) + 1

        # Group by source service
        source = msg.get("headers", {}).get("source_service", "unknown")
        analysis["by_source"][source] = analysis["by_source"].get(source, 0) + 1

        # Group by hour
        ts = msg.get("timestamp", "")
        hour = ts[:13] if ts else "unknown"
        analysis["by_hour"][hour] = analysis["by_hour"].get(hour, 0) + 1

    return analysis
```

### Message Ordering Issues

```text
Problem: Messages processed out of order.

Scenarios:
1. Multiple partitions: Messages for same entity on different partitions
   Fix: Partition by entity ID (e.g., user_id as partition key)

2. Consumer group rebalancing: Rebalance causes duplicate/reordered processing
   Fix: Idempotent consumers, sequence number validation

3. Retry reordering: Failed message retried after later messages processed
   Fix: Per-entity ordering (sequential processing per key)

Debugging:
  - Check partition assignment for the entity's messages
  - Check consumer group lag per partition
  - Look for rebalance events in consumer logs
  - Verify partition key is set correctly on producer side
```

### Queue Health Checks

```bash
# Kafka: Check consumer lag
kafka-consumer-groups.sh \
    --bootstrap-server localhost:9092 \
    --group my-consumer-group \
    --describe

# RabbitMQ: Check queue depth
rabbitmqctl list_queues name messages consumers

# AWS SQS: Check queue attributes
aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/123456/my-queue \
    --attribute-names ApproximateNumberOfMessages \
                      ApproximateNumberOfMessagesNotVisible \
                      ApproximateNumberOfMessagesDelayed
```

---

## Tracing Tools Reference

| Tool | Type | Best For | Deployment |
|------|------|----------|------------|
| Jaeger | Open source | Full-featured distributed tracing | Self-hosted, K8s operator |
| Zipkin | Open source | Simple tracing, Java ecosystem | Self-hosted |
| AWS X-Ray | Managed | AWS-native services | AWS integration |
| Google Cloud Trace | Managed | GCP-native services | GCP integration |
| Datadog APM | SaaS | Full observability platform | Agent-based |
| Grafana Tempo | Open source | Cost-effective trace storage | Self-hosted, pairs with Grafana |
| Honeycomb | SaaS | High-cardinality debugging | SDK-based |

### Jaeger Quick Setup

```yaml
# docker-compose.yml for local development
services:
  jaeger:
    image: jaegertracing/all-in-one:1.54
    ports:
      - "16686:16686"   # UI
      - "4317:4317"     # OTLP gRPC
      - "4318:4318"     # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

```bash
# Access Jaeger UI
open http://localhost:16686

# Search by trace ID
open http://localhost:16686/trace/<trace-id>

# Search by service and operation
open http://localhost:16686/search?service=order-service&operation=POST%20/orders
```

---

## Debugging Kubernetes Networking

### Common K8s Network Issues

| Issue | Symptom | Debug Command |
|-------|---------|---------------|
| Service DNS failure | Connection refused / timeout | `nslookup <service>.<namespace>.svc.cluster.local` |
| NetworkPolicy blocking | Connection timeout | `kubectl get networkpolicies -A` |
| Pod not ready | 503 from Service | `kubectl get endpoints <service>` |
| Port mismatch | Connection refused | `kubectl describe svc <service>` vs pod port |
| Resource limits (CPU throttle) | High latency | `kubectl top pod`, check throttling metrics |

### Debugging Workflow

```bash
# 1. Verify the service has endpoints
kubectl get endpoints my-service -o yaml

# 2. Verify pods are ready
kubectl get pods -l app=my-service -o wide

# 3. Test connectivity from within the cluster
kubectl run debug --rm -it --image=nicolaka/netshoot -- bash
# Inside debug pod:
curl -v http://my-service.default.svc.cluster.local:8080/health
nslookup my-service.default.svc.cluster.local
traceroute my-service

# 4. Check network policies
kubectl get networkpolicies -A -o yaml

# 5. Check service mesh (if using Istio)
istioctl analyze
istioctl proxy-status
kubectl logs <pod> -c istio-proxy | grep -i error

# 6. Check recent events
kubectl get events --sort-by='.lastTimestamp' -n default | tail -20
```

---

## Distributed Debugging Checklist

- [ ] Correlation IDs propagated across all service calls (HTTP, gRPC, queues)
- [ ] Distributed tracing configured with OpenTelemetry or equivalent
- [ ] All services export traces to centralized backend (Jaeger, Tempo, etc.)
- [ ] Structured logs include correlation ID, service name, and timestamp
- [ ] Logs centralized and queryable by correlation ID
- [ ] Service dependency map documented or auto-generated from traces
- [ ] Clock synchronization verified across all nodes (NTP/chrony)
- [ ] Dead letter queues monitored with alerting on growth
- [ ] Message ordering verified for entity-based workflows
- [ ] Network policies reviewed and documented
- [ ] Runbook exists for common distributed failure scenarios
- [ ] Trace sampling rate appropriate (100% in dev, 1-10% in prod)

---

## Related Resources

- **[debugging-methodologies.md](debugging-methodologies.md)** - General debugging approaches
- **[race-condition-diagnosis.md](race-condition-diagnosis.md)** - Concurrency bug detection
- **[production-debugging-patterns.md](production-debugging-patterns.md)** - Production diagnostics
- **[logging-best-practices.md](logging-best-practices.md)** - Structured logging patterns
- **[SKILL.md](../SKILL.md)** - QA Debugging skill overview
