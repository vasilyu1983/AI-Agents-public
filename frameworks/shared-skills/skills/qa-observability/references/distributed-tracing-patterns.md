# Distributed Tracing Patterns

Operational patterns for implementing distributed tracing in microservices. Focus on trace propagation, span design, backend selection, and debugging workflows.

## Contents

- Trace Propagation Patterns
- Span Design Patterns
- Backend Selection Guide
- Debugging Workflows
- Sampling Strategies for Distributed Traces
- Performance Optimization
- Multi-Tenant Tracing
- Trace Storage Retention
- Trace Correlation
- Troubleshooting Common Issues
- Further Reading

## Trace Propagation Patterns

### Pattern 1: HTTP Header Propagation (W3C Standard)

**Use when:** Synchronous HTTP communication between services

**Implementation:**

```javascript
// Service A -> Service B
const axios = require('axios');
const { context, propagation } = require('@opentelemetry/api');

async function callServiceB(data) {
  const headers = {};

  // Inject W3C trace context
  propagation.inject(context.active(), headers);

  const response = await axios.post('http://service-b/api/process', data, {
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
  });

  return response.data;
}
```

**Trace context format:**
```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

Format: version-trace-id-span-id-flags
- version: 2 hex (00)
- trace-id: 32 hex (128-bit)
- span-id: 16 hex (64-bit)
- flags: 2 hex (bit 0: sampled)
```

### Pattern 2: Message Queue Propagation

**Use when:** Async messaging (RabbitMQ, Kafka, SQS)

**Producer (inject trace context):**

```javascript
const { context, propagation } = require('@opentelemetry/api');

async function publishMessage(message) {
  const carrier = {};

  // Inject trace context into message headers
  propagation.inject(context.active(), carrier);

  await channel.publish('exchange', 'routing-key', Buffer.from(JSON.stringify(message)), {
    headers: carrier, // Contains traceparent
  });
}
```

**Consumer (extract trace context):**

```javascript
async function consumeMessage(msg) {
  const carrier = msg.properties.headers || {};

  // Extract trace context from message headers
  const ctx = propagation.extract(context.active(), carrier);

  // Process message within extracted context
  context.with(ctx, () => {
    const tracer = trace.getTracer('consumer-service');
    const span = tracer.startSpan('process-message');

    try {
      // Process message...
      processMessage(msg.content);
      span.end();
    } catch (error) {
      span.recordException(error);
      span.end();
    }
  });
}
```

### Pattern 3: gRPC Metadata Propagation

**Use when:** gRPC service communication

```javascript
const grpc = require('@grpc/grpc-js');
const { context, propagation } = require('@opentelemetry/api');

// Client: inject trace context
function callGrpcService(request) {
  const metadata = new grpc.Metadata();

  // Inject trace context into gRPC metadata
  propagation.inject(context.active(), metadata);

  return new Promise((resolve, reject) => {
    client.myMethod(request, metadata, (error, response) => {
      if (error) reject(error);
      else resolve(response);
    });
  });
}

// Server: extract trace context
function handleGrpcCall(call, callback) {
  const metadata = call.metadata.getMap();

  // Extract trace context from gRPC metadata
  const ctx = propagation.extract(context.active(), metadata);

  context.with(ctx, () => {
    const tracer = trace.getTracer('grpc-service');
    const span = tracer.startSpan('handle-grpc-call');

    try {
      const response = processRequest(call.request);
      span.end();
      callback(null, response);
    } catch (error) {
      span.recordException(error);
      span.end();
      callback(error);
    }
  });
}
```

---

## Span Design Patterns

### Pattern 1: Nested Spans (Parent-Child)

**Use when:** Sequential operations within a workflow

```javascript
const { trace, context } = require('@opentelemetry/api');

async function processOrder(orderId) {
  const tracer = trace.getTracer('order-service');

  // Parent span
  const parentSpan = tracer.startSpan('process-order');
  parentSpan.setAttribute('order.id', orderId);

  try {
    // Child span 1
    const ctx1 = trace.setSpan(context.active(), parentSpan);
    await context.with(ctx1, async () => {
      const validateSpan = tracer.startSpan('validate-order');
      await validateOrder(orderId);
      validateSpan.end();
    });

    // Child span 2
    const ctx2 = trace.setSpan(context.active(), parentSpan);
    await context.with(ctx2, async () => {
      const paymentSpan = tracer.startSpan('process-payment');
      await processPayment(orderId);
      paymentSpan.end();
    });

    parentSpan.end();
  } catch (error) {
    parentSpan.recordException(error);
    parentSpan.end();
    throw error;
  }
}
```

**Trace visualization:**
```
process-order [########################]
  |- validate-order [####]
  `- process-payment [########]
```

### Pattern 2: Linked Spans (Follow-From)

**Use when:** Async operations that don't block parent (fire-and-forget)

```javascript
async function createUser(userData) {
  const tracer = trace.getTracer('user-service');
  const span = tracer.startSpan('create-user');

  try {
    const user = await saveUser(userData);

    // Create linked span for async operation
    const asyncSpan = tracer.startSpan('send-welcome-email', {
      links: [{
        context: span.spanContext(),
        attributes: { 'link.type': 'async' }
      }]
    });

    // Fire-and-forget (don't await)
    sendWelcomeEmail(user.email).finally(() => asyncSpan.end());

    span.end();
    return user;
  } catch (error) {
    span.recordException(error);
    span.end();
    throw error;
  }
}
```

### Pattern 3: Span Events (Annotations)

**Use when:** Marking significant points within a span

```javascript
async function uploadFile(file) {
  const span = tracer.startSpan('upload-file');
  span.setAttribute('file.name', file.name);
  span.setAttribute('file.size', file.size);

  try {
    span.addEvent('validation-started');
    await validateFile(file);
    span.addEvent('validation-completed');

    span.addEvent('upload-started');
    await uploadToS3(file);
    span.addEvent('upload-completed');

    span.addEvent('thumbnail-generation-started');
    await generateThumbnail(file);
    span.addEvent('thumbnail-generation-completed');

    span.end();
  } catch (error) {
    span.addEvent('error-occurred', {
      'error.message': error.message,
      'error.type': error.constructor.name
    });
    span.recordException(error);
    span.end();
    throw error;
  }
}
```

---

## Backend Selection Guide

### Jaeger

**Best for:** General-purpose distributed tracing

**Pros:**
- Open-source
- Full OpenTelemetry support
- Good UI for trace visualization
- Multiple storage backends (Cassandra, Elasticsearch, Badger)

**Deployment:**

```bash
# All-in-one (development)
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest

# Production (Kubernetes Operator)
kubectl create namespace observability
kubectl apply -f https://github.com/jaegertracing/jaeger-operator/releases/latest/download/jaeger-operator.yaml
```

**Retention:** Configure per storage backend (default 2 days)

### Grafana Tempo

**Best for:** High-scale tracing with low cost

**Pros:**
- Cost-effective (object storage: S3, GCS)
- Integrates with Grafana
- No index required (lower storage costs)

**Cons:**
- Basic UI (needs Grafana)
- Limited search capabilities

**Deployment:**

```yaml
# tempo-config.yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
          endpoint: 0.0.0.0:4318

storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      region: us-east-1

compactor:
  compaction:
    block_retention: 168h # 7 days
```

### Zipkin

**Best for:** Legacy systems or simple setups

**Pros:**
- Lightweight
- Easy to deploy

**Cons:**
- Older UI
- Less active development

### APM Platforms (Datadog, New Relic, Dynatrace)

**Best for:** All-in-one observability

**Pros:**
- Unified logs, metrics, traces
- AI-powered insights
- Enterprise support

**Cons:**
- Cost (usage-based pricing)
- Vendor lock-in

---

## Debugging Workflows

### Workflow 1: Find Slow Requests

**1. Query by latency:**

```promql
# Jaeger UI Query
operation = "GET /api/orders" AND duration > 1s
```

**2. Analyze trace waterfall:**
```
GET /api/orders [2.3s]
  |- db.query [1.8s] <- Bottleneck
  |- cache.get [0.3s]
  `- serialize [0.2s]
```

**3. Investigate database span:**
```
Span: db.query
Attributes:
  - db.statement: SELECT * FROM orders WHERE user_id = ? AND status IN (?, ?, ?)
  - db.rows_affected: 5000 <- Problem: N+1 query or missing index
```

### Workflow 2: Debug Failed Requests

**1. Filter by error status:**

```promql
# Jaeger Query
service = "payment-service" AND error = true
```

**2. Examine error span:**
```
Span: process-payment
Status: ERROR
Exception:
  - type: PaymentGatewayTimeout
  - message: Gateway did not respond within 30s
  - stack: ...
```

**3. Correlate with logs:**
```json
{
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "level": "error",
  "message": "Payment gateway timeout",
  "context": {
    "gateway": "stripe",
    "retry_count": 3,
    "last_error": "ETIMEDOUT"
  }
}
```

### Workflow 3: Identify Service Dependencies

**1. View service graph:**

Jaeger UI -> System Architecture -> Dependency Graph

```
frontend -> api-gateway -> [order-service, user-service, payment-service]
                                v              v              v
                              database      cache         stripe-api
```

**2. Analyze call volume:**
```
order-service -> database: 10k req/min
order-service -> cache: 50k req/min <- Good cache hit ratio
payment-service -> stripe-api: 500 req/min
```

### Workflow 4: Root Cause Analysis (Cross-Service)

**1. Identify trace with error:**
```
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736
Root Span: POST /api/checkout (ERROR)
```

**2. Follow trace across services:**
```
frontend (500ms)
  `- api-gateway (450ms)
      `- order-service (400ms)
          |- inventory-service (50ms, OK)
          `- payment-service (350ms, ERROR) <- Root cause
              `- stripe-api (timeout)
```

**3. Correlate with metrics:**
```promql
# Prometheus query
rate(stripe_api_errors_total[5m]) > 10
```

---

## Sampling Strategies for Distributed Traces

### Strategy 1: Head-Based Sampling (Traditional)

**Decision at trace root** (first service in chain)

**Pros:**
- Simple to implement
- Consistent sampling across all spans in trace

**Cons:**
- May miss rare but important errors
- No visibility into full trace before sampling decision

**Implementation:**
```javascript
const { ParentBasedSampler, TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');

const sampler = new ParentBasedSampler({
  root: new TraceIdRatioBasedSampler(0.1), // 10% of traces
});
```

### Strategy 2: Tail-Based Sampling (Advanced)

**Decision after trace completes** (collector aggregates all spans)

**Pros:**
- Sample based on full trace characteristics
- Ensure all errors and slow requests are captured

**Cons:**
- Requires OpenTelemetry Collector
- More complex setup

**Collector config:**
```yaml
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      - name: slow-requests
        type: latency
        latency:
          threshold_ms: 1000
      - name: probabilistic
        type: probabilistic
        probabilistic:
          sampling_percentage: 5
service:
  pipelines:
    traces:
      processors: [tail_sampling, batch]
```

### Strategy 3: Adaptive Sampling (Dynamic)

**Adjust sampling rate based on traffic**

**Example: Sample more during low traffic, less during high traffic**

```javascript
class AdaptiveSampler {
  constructor() {
    this.baseSampleRate = 0.1;
    this.currentRate = this.baseSampleRate;
  }

  updateSampleRate(requestsPerSecond) {
    if (requestsPerSecond < 100) {
      this.currentRate = 1.0; // 100% sampling
    } else if (requestsPerSecond < 1000) {
      this.currentRate = 0.5; // 50% sampling
    } else if (requestsPerSecond < 10000) {
      this.currentRate = 0.1; // 10% sampling
    } else {
      this.currentRate = 0.01; // 1% sampling
    }
  }

  shouldSample() {
    return Math.random() < this.currentRate;
  }
}
```

---

## Performance Optimization

### 1. Reduce Span Cardinality

[FAIL] **Bad:**
```javascript
span.setAttribute('user.email', user.email); // Unbounded
span.setAttribute('request.timestamp', Date.now()); // Unique per request
```

[OK] **Good:**
```javascript
span.setAttribute('user.id', user.id); // Bounded
// Use span start time (built-in)
```

### 2. Limit Span Attributes

**Target:** 5-15 attributes per span

[FAIL] **Bad (35 attributes):**
```javascript
span.setAttribute('user.email', ...);
span.setAttribute('user.name', ...);
span.setAttribute('user.address', ...);
// ... 32 more attributes
```

[OK] **Good (8 attributes):**
```javascript
span.setAttribute('user.id', userId);
span.setAttribute('order.id', orderId);
span.setAttribute('order.total', total);
span.setAttribute('payment.method', method);
```

### 3. Use Batch Exports

**Default batch settings:**
```javascript
const processor = new BatchSpanProcessor(exporter, {
  maxQueueSize: 2048,
  maxExportBatchSize: 512,
  scheduledDelayMillis: 5000,
  exportTimeoutMillis: 30000,
});
```

**High-throughput settings:**
```javascript
const processor = new BatchSpanProcessor(exporter, {
  maxQueueSize: 4096,           // Increase buffer
  maxExportBatchSize: 1024,     // Larger batches
  scheduledDelayMillis: 2000,   // More frequent exports
  exportTimeoutMillis: 10000,   // Faster timeout
});
```

---

## Multi-Tenant Tracing

### Pattern: Tenant ID Propagation

**Add tenant ID to all spans:**

```javascript
const { context, trace } = require('@opentelemetry/api');

// Middleware to set tenant context
app.use((req, res, next) => {
  const tenantId = req.headers['x-tenant-id'];

  if (tenantId) {
    const span = trace.getActiveSpan();
    span?.setAttribute('tenant.id', tenantId);

    // Also add to baggage for cross-service propagation
    const baggage = propagation.createBaggage({
      'tenant.id': { value: tenantId }
    });
    context.with(propagation.setBaggage(context.active(), baggage), next);
  } else {
    next();
  }
});
```

**Query traces by tenant:**
```promql
# Jaeger Query
service = "order-service" AND tenant.id = "tenant-abc"
```

---

## Trace Storage Retention

### Retention Policies

| Environment | Retention | Sampling Rate |
|-------------|-----------|---------------|
| Development | 1-2 days | 100% |
| Staging | 7 days | 50% |
| Production | 7-30 days | 1-10% |

### Cost Optimization

**Example calculation:**

```
Requests per day: 10M
Sampling rate: 1% (100k traces)
Average trace size: 50 KB
Daily storage: 100k * 50 KB = 5 GB
Monthly storage (30 days): 150 GB

Cost (S3 Standard):
150 GB * $0.023/GB = $3.45/month
```

**Cost-saving strategies:**
1. Use object storage (S3, GCS) instead of databases
2. Compress traces (gzip)
3. Lower sampling rate for high-traffic endpoints
4. Shorter retention for non-critical services

---

## Trace Correlation

### Logs <-> Traces

**Add trace ID to logs:**

```javascript
const { trace } = require('@opentelemetry/api');
const logger = require('pino')();

app.use((req, res, next) => {
  const span = trace.getActiveSpan();
  const traceId = span?.spanContext().traceId;

  req.log = logger.child({
    trace_id: traceId,
    span_id: span?.spanContext().spanId
  });

  next();
});

// Usage
req.log.info({ order_id: '123' }, 'Processing order');
// Output: {"trace_id":"4bf92f...","span_id":"00f067...","order_id":"123","msg":"Processing order"}
```

**Jump from logs to traces:**

Logs -> Filter by trace_id -> Jump to Jaeger with trace ID

### Metrics <-> Traces

**Add trace exemplars to metrics:**

```javascript
const { Histogram } = require('prom-client');
const { trace } = require('@opentelemetry/api');

const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'route', 'status_code'],
});

app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const span = trace.getActiveSpan();
    const traceId = span?.spanContext().traceId;

    httpDuration
      .labels(req.method, req.route?.path, res.statusCode)
      .observe(duration, { traceID: traceId }); // Exemplar
  });

  next();
});
```

**Jump from metrics to traces:**

Grafana -> Hover over metric spike -> Click exemplar -> Jump to trace

---

## Troubleshooting Common Issues

### Issue 1: Broken Traces (Missing Spans)

**Symptoms:**
- Gaps in trace timeline
- Parent span completes before child spans

**Causes:**
- Trace context not propagated
- Child service not instrumented
- Network issues during export

**Fix:**
```javascript
// Verify trace propagation
const { propagation, context } = require('@opentelemetry/api');

const headers = {};
propagation.inject(context.active(), headers);
console.log(headers); // Should contain 'traceparent' header
```

### Issue 2: High Overhead

**Symptoms:**
- Increased CPU usage (>5%)
- Increased memory usage (>100 MB)
- Slower response times

**Causes:**
- 100% sampling in production
- Too many manual spans
- Synchronous exports

**Fix:**
```javascript
// Reduce sampling
const sampler = new TraceIdRatioBasedSampler(0.01); // 1%

// Use batch processor
const processor = new BatchSpanProcessor(exporter);

// Disable noisy instrumentations
const sdk = new NodeSDK({
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-fs': { enabled: false },
      '@opentelemetry/instrumentation-dns': { enabled: false },
    }),
  ],
});
```

### Issue 3: Traces Not Searchable

**Symptoms:**
- Can't find traces by attributes
- Slow queries in Jaeger UI

**Causes:**
- Attributes not indexed
- Missing trace tags

**Fix:**
```javascript
// Add indexed attributes
span.setAttribute('http.method', 'GET');
span.setAttribute('http.status_code', 200);
span.setAttribute('user.id', userId); // Searchable
```

---

## Further Reading

- [W3C Trace Context Specification](https://www.w3.org/TR/trace-context/)
- [OpenTelemetry Tracing API](https://opentelemetry.io/docs/specs/otel/trace/api/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Grafana Tempo Documentation](https://grafana.com/docs/tempo/latest/)
