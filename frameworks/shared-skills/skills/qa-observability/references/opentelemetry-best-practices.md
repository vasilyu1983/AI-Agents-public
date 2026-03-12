# OpenTelemetry Best Practices

Operational guide for instrumenting production services with OpenTelemetry. Focus on real-world patterns, common pitfalls, and performance considerations.

## Contents

- Installation & Setup
- Auto-Instrumentation vs Manual
- Span Attributes Best Practices
- Sampling Strategies
- Performance Considerations
- Context Propagation
- Error Handling
- Testing Instrumentation
- Common Pitfalls
- Deployment Patterns
- Migration from Legacy APM
- Troubleshooting
- Further Reading

## Installation & Setup

### Node.js Setup (Recommended Pattern)

**1. Install dependencies:**

```bash
npm install --save \
  @opentelemetry/sdk-node \
  @opentelemetry/auto-instrumentations-node \
  @opentelemetry/exporter-trace-otlp-http \
  @opentelemetry/exporter-metrics-otlp-http \
  @opentelemetry/sdk-metrics \
  @opentelemetry/resources \
  @opentelemetry/semantic-conventions
```

**2. Create instrumentation file (MUST load first):**

```javascript
// instrumentation.js - Load BEFORE any other imports
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: process.env.SERVICE_NAME || 'my-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
  }),
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
  }),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter({
      url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/metrics',
    }),
    exportIntervalMillis: 60000, // Export every 60 seconds
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      // Disable noisy instrumentations
      '@opentelemetry/instrumentation-fs': { enabled: false },
      '@opentelemetry/instrumentation-net': { enabled: false },
      '@opentelemetry/instrumentation-dns': { enabled: false },
    }),
  ],
});

sdk.start();

// Graceful shutdown
process.on('SIGTERM', () => {
  sdk.shutdown()
    .then(() => console.log('OpenTelemetry shut down successfully'))
    .catch((error) => console.error('Error shutting down OpenTelemetry', error))
    .finally(() => process.exit(0));
});

module.exports = sdk;
```

**3. Load in application entry point:**

```javascript
// server.js or index.js - FIRST LINE
require('./instrumentation');

// Now import your app
const express = require('express');
const app = express();

// Your app code...
```

### Python Setup (Recommended Pattern)

**1. Install dependencies:**

```bash
pip install opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-instrumentation-flask \
  opentelemetry-instrumentation-requests \
  opentelemetry-exporter-otlp-proto-http
```

**2. Create instrumentation file:**

```python
# instrumentation.py
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

# Configure resource
resource = Resource.create({
    "service.name": os.getenv("SERVICE_NAME", "my-service"),
    "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
    "deployment.environment": os.getenv("ENV", "development")
})

# Configure tracing
trace_provider = TracerProvider(resource=resource)
trace_processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
    )
)
trace_provider.add_span_processor(trace_processor)
trace.set_tracer_provider(trace_provider)

# Configure metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/metrics")
    ),
    export_interval_millis=60000
)
metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)
```

**3. Instrument Flask app:**

```python
# app.py
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from instrumentation import trace_provider

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# Your app code...
```

---

## Auto-Instrumentation vs Manual

### When to Use Auto-Instrumentation

[OK] **Use auto-instrumentation for:**
- HTTP server (Express, Flask, FastAPI)
- HTTP client (axios, requests)
- Database (PostgreSQL, MySQL, MongoDB, Redis)
- Message queues (RabbitMQ, Kafka)
- gRPC

Auto-instrumentation gives you:
- Request/response traces
- Database query traces
- HTTP client call traces
- Zero code changes required

### When to Add Manual Spans

[OK] **Add manual spans for:**
- Business logic operations
- Complex multi-step workflows
- External API calls not auto-instrumented
- Background jobs
- Cache operations
- Custom metrics

**Example: Manual span for business logic:**

```javascript
const { trace } = require('@opentelemetry/api');

async function processOrder(orderId) {
  const tracer = trace.getTracer('order-service');
  const span = tracer.startSpan('process-order');

  span.setAttribute('order.id', orderId);
  span.setAttribute('order.source', 'web');

  try {
    // Validate order
    const validationSpan = tracer.startSpan('validate-order', { parent: span });
    const isValid = await validateOrder(orderId);
    validationSpan.setAttribute('order.is_valid', isValid);
    validationSpan.end();

    if (!isValid) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: 'Invalid order' });
      throw new Error('Invalid order');
    }

    // Process payment
    const paymentSpan = tracer.startSpan('process-payment', { parent: span });
    paymentSpan.setAttribute('payment.method', 'stripe');
    const payment = await processPayment(orderId);
    paymentSpan.setAttribute('payment.id', payment.id);
    paymentSpan.end();

    // Fulfill order
    const fulfillmentSpan = tracer.startSpan('fulfill-order', { parent: span });
    await fulfillOrder(orderId);
    fulfillmentSpan.end();

    span.setStatus({ code: SpanStatusCode.OK });
    return { success: true, orderId };
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
    throw error;
  } finally {
    span.end();
  }
}
```

---

## Span Attributes Best Practices

### Semantic Conventions

Use semantic conventions for standard attributes:

```javascript
const { SemanticAttributes } = require('@opentelemetry/semantic-conventions');

span.setAttribute(SemanticAttributes.HTTP_METHOD, 'GET');
span.setAttribute(SemanticAttributes.HTTP_URL, 'https://api.example.com/orders');
span.setAttribute(SemanticAttributes.HTTP_STATUS_CODE, 200);
span.setAttribute(SemanticAttributes.DB_SYSTEM, 'postgresql');
span.setAttribute(SemanticAttributes.DB_STATEMENT, 'SELECT * FROM orders WHERE id = $1');
```

**Full list:** https://opentelemetry.io/docs/specs/semconv/

### Custom Attributes

[OK] **Good attributes:**
- Business identifiers: `order.id`, `user.id`, `transaction.id`
- Operation details: `payment.method`, `shipping.carrier`, `order.total`
- Feature flags: `experiment.variant`, `feature.enabled`
- Context: `tenant.id`, `region`, `shard.id`

[FAIL] **Bad attributes:**
- High-cardinality: timestamps, UUIDs as values, full URLs
- Sensitive data: passwords, tokens, credit cards, SSNs
- Large payloads: full request/response bodies

### Attribute Limits

Most backends have limits:
- **Max attributes per span**: 128
- **Max attribute key length**: 128 characters
- **Max attribute value length**: 1024 characters

---

## Sampling Strategies

### Production Sampling (Critical)

**Problem**: 100% sampling = expensive storage and performance impact

**Solution**: Tail-based sampling or adaptive sampling

### Sampling Strategy Comparison

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| **AlwaysOn** | Development | Simple, see everything | Not for production |
| **AlwaysOff** | Disabled | No overhead | No traces |
| **Probabilistic** | Production (uniform) | Consistent sample rate | May miss rare errors |
| **ParentBased** | Production (recommended) | Respects upstream decisions | More complex |
| **Adaptive** | High traffic | Samples errors/slow requests | Requires custom implementation |

### Recommended Sampling Config

```javascript
const { ParentBasedSampler, TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');

const sampler = new ParentBasedSampler({
  root: new TraceIdRatioBasedSampler(0.1), // 10% of root spans
  // Always sample if parent sampled
});

const sdk = new NodeSDK({
  sampler: sampler,
  // ... other config
});
```

### Adaptive Sampling Pattern

Sample based on request characteristics:

```javascript
const { Sampler, SamplingDecision } = require('@opentelemetry/sdk-trace-base');

class AdaptiveSampler extends Sampler {
  shouldSample(context, traceId, spanName, spanKind, attributes) {
    // Always sample errors
    if (attributes['http.status_code'] >= 500) {
      return { decision: SamplingDecision.RECORD_AND_SAMPLED };
    }

    // Always sample slow requests
    if (attributes['http.duration'] > 1000) { // > 1 second
      return { decision: SamplingDecision.RECORD_AND_SAMPLED };
    }

    // Sample 1% of normal requests
    const hash = parseInt(traceId.slice(0, 8), 16);
    if (hash % 100 === 0) {
      return { decision: SamplingDecision.RECORD_AND_SAMPLED };
    }

    return { decision: SamplingDecision.NOT_RECORD };
  }
}
```

---

## Performance Considerations

### Overhead Benchmarks

| Component | Overhead |
|-----------|----------|
| Auto-instrumentation | 2-5% CPU, 10-20 MB memory |
| Manual spans (moderate) | <1% CPU |
| Exporter (batch) | <1% CPU |
| 100% sampling | 5-10% CPU, 50-100 MB memory |
| 1% sampling | <2% CPU, <10 MB memory |

### Optimization Checklist

- [ ] Use batch span processor (default), not simple processor
- [ ] Disable unnecessary auto-instrumentations (fs, net, dns)
- [ ] Set reasonable sampling rate (1-10% for production)
- [ ] Use OTLP HTTP exporter (not gRPC unless needed)
- [ ] Limit span attributes (max 10-20 per span)
- [ ] Avoid high-cardinality attributes
- [ ] Configure max queue size and export timeout
- [ ] Use async logging to avoid blocking

### Batch Processor Configuration

```javascript
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');

const processor = new BatchSpanProcessor(exporter, {
  maxQueueSize: 2048,           // Max spans in queue
  maxExportBatchSize: 512,      // Spans per export
  scheduledDelayMillis: 5000,   // Export every 5 seconds
  exportTimeoutMillis: 30000,   // Timeout after 30 seconds
});
```

---

## Context Propagation

### W3C Trace Context (Standard)

Propagate trace context across service boundaries:

```
traceparent: 00-{trace-id}-{parent-span-id}-{trace-flags}
tracestate: vendor1=value1,vendor2=value2
```

**Node.js (auto-propagation with axios):**

```javascript
const axios = require('axios');
const { context, propagation } = require('@opentelemetry/api');

async function callDownstreamService(data) {
  const headers = {};

  // Inject trace context into headers
  propagation.inject(context.active(), headers);

  const response = await axios.post('http://downstream-service/api', data, {
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
  });

  return response.data;
}
```

**Python (auto-propagation with requests):**

```python
import requests
from opentelemetry import trace, propagation

def call_downstream_service(data):
    headers = {}

    # Inject trace context into headers
    propagation.inject(headers)

    response = requests.post(
        'http://downstream-service/api',
        json=data,
        headers=headers
    )

    return response.json()
```

### Baggage (Cross-service metadata)

Pass metadata across services:

```javascript
const { propagation, context } = require('@opentelemetry/api');

// Set baggage
const baggage = propagation.createBaggage({
  'user.id': { value: '12345' },
  'tenant.id': { value: 'tenant-abc' },
});

context.with(propagation.setBaggage(context.active(), baggage), () => {
  // Call downstream services
  // Baggage is automatically propagated
});

// Read baggage in downstream service
const baggage = propagation.getBaggage(context.active());
const userId = baggage.getEntry('user.id')?.value;
```

---

## Error Handling

### Recording Exceptions

Always record exceptions on spans:

```javascript
try {
  await riskyOperation();
} catch (error) {
  span.recordException(error);
  span.setStatus({
    code: SpanStatusCode.ERROR,
    message: error.message
  });
  throw error; // Re-throw if needed
}
```

### Error Attributes

Add context to errors:

```javascript
span.recordException(error);
span.setAttribute('error.type', error.constructor.name);
span.setAttribute('error.handled', true);
span.setAttribute('retry.count', retryCount);
```

---

## Testing Instrumentation

### Console Exporter (Development)

```javascript
const { ConsoleSpanExporter } = require('@opentelemetry/sdk-trace-base');

const sdk = new NodeSDK({
  traceExporter: new ConsoleSpanExporter(),
});
```

### In-Memory Exporter (Unit Tests)

```javascript
const { InMemorySpanExporter } = require('@opentelemetry/sdk-trace-base');

const memoryExporter = new InMemorySpanExporter();
const sdk = new NodeSDK({
  traceExporter: memoryExporter,
});

// After test, check spans
const spans = memoryExporter.getFinishedSpans();
expect(spans).toHaveLength(1);
expect(spans[0].name).toBe('my-operation');
```

---

## Common Pitfalls

### BAD: Instrumentation loaded too late

**Problem:**
```javascript
const express = require('express'); // BAD: Loaded before instrumentation
require('./instrumentation');
```

**Solution:**
```javascript
require('./instrumentation'); // GOOD: Load FIRST
const express = require('express');
```

### BAD: Not ending spans

**Problem:**
```javascript
const span = tracer.startSpan('operation');
await doWork();
// BAD: Forgot to call span.end()
```

**Solution:**
```javascript
const span = tracer.startSpan('operation');
try {
  await doWork();
} finally {
  span.end(); // GOOD: Always end spans
}
```

### BAD: High-cardinality attributes

**Problem:**
```javascript
span.setAttribute('user.email', email); // BAD: Unbounded cardinality
span.setAttribute('request.timestamp', Date.now()); // BAD: Unique per request
```

**Solution:**
```javascript
span.setAttribute('user.id', userId); // GOOD: Bounded cardinality
// Use span start time, not custom timestamp
```

### BAD: Blocking exports

**Problem:**
```javascript
const { SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
provider.addSpanProcessor(new SimpleSpanProcessor(exporter)); // BAD: Blocks on export
```

**Solution:**
```javascript
const { BatchSpanProcessor } = require('@opentelemetry/sdk-trace-base');
provider.addSpanProcessor(new BatchSpanProcessor(exporter)); // GOOD: Async batch export
```

---

## Deployment Patterns

### Local Development

```yaml
# docker-compose.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "4318:4318"    # OTLP HTTP receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

### Production (Kubernetes)

**Option 1: OpenTelemetry Collector (Recommended)**

```yaml
# otel-collector-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: otel-collector
spec:
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector:latest
        ports:
        - containerPort: 4318
          name: otlp-http
        volumeMounts:
        - name: config
          mountPath: /etc/otel
      volumes:
      - name: config
        configMap:
          name: otel-collector-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          http:
            endpoint: 0.0.0.0:4318
    processors:
      batch:
        timeout: 10s
        send_batch_size: 1024
    exporters:
      jaeger:
        endpoint: jaeger-collector:14250
      prometheus:
        endpoint: 0.0.0.0:8889
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [jaeger]
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheus]
```

**Option 2: Direct to APM**

```javascript
// Use APM-specific exporter
const { DatadogSpanExporter } = require('@opentelemetry/exporter-datadog');

const exporter = new DatadogSpanExporter({
  agentUrl: process.env.DD_AGENT_URL,
});
```

---

## Migration from Legacy APM

### Datadog to OpenTelemetry

**Before (Datadog):**
```javascript
const tracer = require('dd-trace').init();

app.get('/api/users', (req, res) => {
  const span = tracer.startSpan('get-users');
  span.setTag('user.id', req.user.id);
  // ...
  span.finish();
});
```

**After (OpenTelemetry):**
```javascript
require('./instrumentation'); // OTel setup
const { trace } = require('@opentelemetry/api');

app.get('/api/users', (req, res) => {
  const tracer = trace.getTracer('my-service');
  const span = tracer.startSpan('get-users');
  span.setAttribute('user.id', req.user.id);
  // ...
  span.end();
});
```

**Key differences:**
- `dd-trace` -> `@opentelemetry/api`
- `.setTag()` -> `.setAttribute()`
- `.finish()` -> `.end()`

---

## Troubleshooting

### No traces appearing

**Checklist:**
1. [OK] Instrumentation loaded first (`require('./instrumentation')`)
2. [OK] OTLP endpoint reachable (check network, firewall)
3. [OK] Sampling enabled (not `AlwaysOff`)
4. [OK] Exporter configured correctly (URL, credentials)
5. [OK] SDK started (`sdk.start()`)

**Debug logging:**
```javascript
const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');

diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);
```

### High memory usage

**Causes:**
- Too many spans in queue (reduce `maxQueueSize`)
- Not calling `span.end()` (memory leak)
- High sampling rate (reduce to 1-10%)
- Large span attributes (limit to 10-20 per span)

**Fix:**
```javascript
const processor = new BatchSpanProcessor(exporter, {
  maxQueueSize: 1024,        // Reduce from 2048
  maxExportBatchSize: 256,   // Reduce from 512
  scheduledDelayMillis: 2000, // Export more frequently
});
```

### Slow exports

**Causes:**
- Network latency to collector
- Collector overloaded
- Synchronous exports (`SimpleSpanProcessor`)

**Fix:**
- Use `BatchSpanProcessor` (async)
- Increase batch size and delay
- Deploy collector closer to services (sidecar or DaemonSet)

---

## Further Reading

- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Collector Configuration](https://opentelemetry.io/docs/collector/configuration/)
- [Performance Best Practices](https://opentelemetry.io/docs/concepts/performance/)
