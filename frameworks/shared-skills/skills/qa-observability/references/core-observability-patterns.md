# Core Observability Patterns

Detailed implementation patterns for building observable systems with OpenTelemetry, distributed tracing, structured logging, performance profiling, and capacity planning.

## Contents

- Pattern: OpenTelemetry End-to-End Setup
- Pattern: Distributed Tracing Strategy
- Pattern: SLO/SLI Design & Error Budgets
- Pattern: Structured Logging
- Pattern: Performance Profiling
- Pattern: Capacity Planning

## Pattern: OpenTelemetry End-to-End Setup

**Use when:** Building observable services from scratch or migrating to OTel standard.

**Three Pillars of Observability:**
- **Traces** - Request flow across services (distributed tracing)
- **Metrics** - Aggregated numerical data (counters, gauges, histograms)
- **Logs** - Discrete event records (structured logs)

**OpenTelemetry Architecture:**

```
Application Code
    v (instrumentation)
OpenTelemetry SDK
    v (export)
OpenTelemetry Collector (optional)
    v (process & route)
Backend Systems (Jaeger, Prometheus, Loki, etc.)
```

**Node.js/Express Example:**

```javascript
// instrumentation.js - Load FIRST before any other imports
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'my-service',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV,
  }),
  traceExporter: new OTLPTraceExporter({
    url: 'http://localhost:4318/v1/traces',
  }),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter({
      url: 'http://localhost:4318/v1/metrics',
    }),
    exportIntervalMillis: 60000,
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-fs': { enabled: false },
    }),
  ],
});

sdk.start();

process.on('SIGTERM', () => {
  sdk.shutdown().finally(() => process.exit(0));
});

// app.js - Main application
require('./instrumentation'); // Must be first
const express = require('express');
const { trace, context } = require('@opentelemetry/api');

const app = express();

// Custom span for business logic
app.get('/api/orders/:id', async (req, res) => {
  const tracer = trace.getTracer('my-service');
  const span = tracer.startSpan('process-order');

  span.setAttribute('order.id', req.params.id);
  span.setAttribute('user.id', req.user?.id);

  try {
    const order = await getOrder(req.params.id);
    span.setStatus({ code: SpanStatusCode.OK });
    res.json(order);
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
    res.status(500).json({ error: 'Internal error' });
  } finally {
    span.end();
  }
});
```

**Python/Flask Example:**

```python
# instrumentation.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "my-service",
    "service.version": "1.0.0",
    "deployment.environment": os.getenv("ENV", "dev")
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# app.py
from flask import Flask
from instrumentation import provider
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route('/api/orders/<order_id>')
def get_order(order_id):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("process-order") as span:
        span.set_attribute("order.id", order_id)
        order = fetch_order(order_id)
        return order
```

**Checklist:**
- [ ] OpenTelemetry SDK installed and configured
- [ ] Service name, version, environment in resource attributes
- [ ] Auto-instrumentation enabled for frameworks (Express, HTTP, DB)
- [ ] Custom spans for business-critical operations
- [ ] Span attributes capture relevant context (user ID, order ID, etc.)
- [ ] Errors recorded with span.recordException()
- [ ] OTLP exporter configured (collector or direct to backend)
- [ ] Sampling strategy configured (100% dev, 10% prod, or adaptive)

---

## Pattern: Distributed Tracing Strategy

**Use when:** Debugging microservices, understanding request flow, finding bottlenecks.

**Trace Propagation (W3C Trace Context Standard):**

```
Service A -> Service B -> Service C
    v           v           v
traceparent: 00-{trace-id}-{span-id}-{flags}
```

**Node.js Service-to-Service Propagation:**

```javascript
const axios = require('axios');
const { context, propagation } = require('@opentelemetry/api');

// Service A calls Service B
async function callServiceB(data) {
  const headers = {};

  // Inject trace context into headers
  propagation.inject(context.active(), headers);

  const response = await axios.post('http://service-b/api/process', data, {
    headers: {
      ...headers,
      'Content-Type': 'application/json',
    },
  });

  return response.data;
}

// Service B receives request with trace context
app.use((req, res, next) => {
  // Auto-instrumentation extracts trace context from headers
  // Manual extraction if needed:
  const ctx = propagation.extract(context.active(), req.headers);
  context.with(ctx, next);
});
```

**Trace Sampling Strategies:**

**1. Always-On (Development):**
```javascript
const { AlwaysOnSampler } = require('@opentelemetry/sdk-trace-base');
const provider = new TracerProvider({
  sampler: new AlwaysOnSampler(),
});
```

**2. Probabilistic (Production):**
```javascript
const { TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');
const provider = new TracerProvider({
  sampler: new TraceIdRatioBasedSampler(0.1), // 10% of traces
});
```

**3. Parent-Based (Recommended):**
```javascript
const { ParentBasedSampler, TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');
const provider = new TracerProvider({
  sampler: new ParentBasedSampler({
    root: new TraceIdRatioBasedSampler(0.1),
  }),
});
```

**4. Adaptive Sampling (Advanced):**
- Sample 100% of errors
- Sample 100% of slow requests (>1s)
- Sample 1% of successful fast requests
- Requires custom sampler implementation or APM features

**Checklist:**
- [ ] W3C Trace Context propagation enabled
- [ ] Trace IDs logged for correlation
- [ ] Sampling strategy matches traffic volume (1% for 10k RPS, 10% for 1k RPS)
- [ ] Critical paths always sampled (errors, slow requests)
- [ ] Trace backend retention configured (7 days typical)
- [ ] Trace search indexed by service, operation, error status

---

## Pattern: SLO/SLI Design & Error Budgets

**Use when:** Defining reliability targets, balancing velocity vs stability, alerting strategy.

**SLI (Service Level Indicator) - What to Measure:**

**Availability SLI:**
```
SLI = (successful requests / total requests) * 100
Target: 99.9% (three nines)
```

**Latency SLI:**
```
SLI = (requests < 500ms / total requests) * 100
Target: 99% of requests < 500ms
```

**Error Rate SLI:**
```
SLI = 1 - (error requests / total requests)
Target: 99.9% (< 0.1% error rate)
```

**Prometheus Queries for SLIs:**

```promql
# Availability SLI (last 30 days)
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))

# Latency SLI (P99 < 500ms)
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
) < 0.5

# Error rate SLI
1 - (
  sum(rate(http_requests_total{status=~"5.."}[30d]))
  /
  sum(rate(http_requests_total[30d]))
)
```

**SLO (Service Level Objective) - Target:**

```yaml
slos:
  - name: api-availability
    sli: http_requests_success_rate
    target: 99.9%
    window: 30d

  - name: api-latency-p99
    sli: http_request_duration_p99
    target: 500ms
    window: 30d

  - name: api-error-rate
    sli: http_requests_error_rate
    target: 0.1%
    window: 30d
```

**Error Budget Calculation:**

```
SLO: 99.9% availability over 30 days
Allowed downtime: 0.1% of 30 days = 43.2 minutes/month

Error Budget Remaining =
  (Target - Current SLI) / (Target - 100%)

Example:
Target: 99.9%
Current: 99.95%
Error Budget Remaining = (99.9 - 99.95) / (99.9 - 100) = 50%
```

**Error Budget Policy:**

```markdown
| Error Budget Remaining | Action |
|------------------------|--------|
| > 50% | Full velocity (all features, experiments) |
| 25-50% | Cautious (critical features only) |
| 10-25% | Feature freeze (reliability work only) |
| < 10% | Incident mode (stop all releases) |
```

**Alerting on Error Budget Burn Rate:**

```promql
# Fast burn (2% budget in 1 hour = incident)
(1 - slo:availability:ratio_rate1h) > (14.4 * (1 - 0.999))

# Slow burn (5% budget in 6 hours = warning)
(1 - slo:availability:ratio_rate6h) > (2.4 * (1 - 0.999))
```

**Checklist:**
- [ ] SLIs defined for availability, latency, error rate
- [ ] SLOs documented and communicated to team
- [ ] Error budgets calculated and tracked
- [ ] Error budget policy established (freeze/rollback thresholds)
- [ ] Burn rate alerts configured (fast: 1h, slow: 6h)
- [ ] SLO dashboards visible to all engineers
- [ ] Post-incident error budget consumption analyzed

---

## Pattern: Structured Logging

**Use when:** Building production services, debugging issues, audit trails.

**Good Structured Log Format (JSON):**

```json
{
  "timestamp": "2025-11-20T10:30:45.123Z",
  "level": "error",
  "message": "Payment processing failed",
  "service": "payment-service",
  "environment": "production",
  "trace_id": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
  "span_id": "00f067aa0ba902b7",
  "user_id": "user-12345",
  "request_id": "req-abc123",
  "duration_ms": 1234,
  "error": {
    "type": "PaymentGatewayError",
    "message": "Gateway timeout",
    "code": "GATEWAY_TIMEOUT",
    "stack": "...",
  },
  "context": {
    "order_id": "order-789",
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "stripe"
  }
}
```

**Node.js (Pino - Recommended):**

```javascript
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
  base: {
    service: 'my-service',
    environment: process.env.NODE_ENV,
  },
  redact: ['req.headers.authorization', 'password', 'secret'],
});

// Correlation with OpenTelemetry
const { trace } = require('@opentelemetry/api');

app.use((req, res, next) => {
  const span = trace.getActiveSpan();
  const traceId = span?.spanContext().traceId;
  const spanId = span?.spanContext().spanId;

  req.log = logger.child({
    request_id: req.id,
    trace_id: traceId,
    span_id: spanId,
  });

  next();
});

// Usage
req.log.info({ order_id: '123' }, 'Processing order');
req.log.error({ err: error, order_id: '123' }, 'Order failed');
```

**Python (structlog - Recommended):**

```python
import structlog
from opentelemetry import trace

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# Correlation with OpenTelemetry
def log_with_trace():
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')
    span_id = format(span.get_span_context().span_id, '016x')

    return logger.bind(
        trace_id=trace_id,
        span_id=span_id,
        service="my-service",
        environment=os.getenv("ENV")
    )

# Usage
log = log_with_trace()
log.info("processing_order", order_id="123", amount=99.99)
log.error("order_failed", order_id="123", error="timeout")
```

**Log Levels:**
```
FATAL  - Application crash (cannot continue)
ERROR  - Operation failed (handled, but noteworthy)
WARN   - Unexpected situation (not an error, but attention needed)
INFO   - Important business events (user action, state change)
DEBUG  - Detailed diagnostic info (development/troubleshooting)
TRACE  - Very detailed (function entry/exit, variable values)
```

**What NOT to Log:**
- Passwords, API keys, tokens, secrets
- Full credit card numbers, SSNs
- Complete request/response bodies (unless sanitized)
- High-cardinality data in structured fields (use trace attributes instead)

**Checklist:**
- [ ] JSON structured logging enabled
- [ ] Trace ID and span ID included in every log
- [ ] Request ID propagated across services
- [ ] Sensitive data redacted (passwords, tokens, PII)
- [ ] Log levels used correctly (ERROR for failures, INFO for events)
- [ ] Contextual fields included (user_id, order_id, duration_ms)
- [ ] Centralized log aggregation configured (ELK, Loki, Datadog)
- [ ] Log retention policy established (7-30 days typical)

---

## Pattern: Performance Profiling

**Use when:** Application is slow, high CPU/memory usage, investigating bottlenecks.

**CPU Profiling (Node.js):**

```bash
# Built-in profiler
node --prof app.js
# Run load test, generate isolate-*.log
node --prof-process isolate-*.log > profile.txt

# Chrome DevTools
node --inspect app.js
# Open chrome://inspect, click "Open dedicated DevTools for Node"
# Use Performance tab to record CPU profile

# Clinic.js (comprehensive)
npm install -g clinic
clinic doctor -- node app.js  # Diagnose issues
clinic flame -- node app.js   # CPU flame graph
clinic bubbleprof -- node app.js  # Async operations
```

**Memory Profiling (Node.js):**

```javascript
// Heap snapshot
const v8 = require('v8');
const fs = require('fs');

function takeHeapSnapshot() {
  const filename = `heap-${Date.now()}.heapsnapshot`;
  const stream = v8.writeHeapSnapshot(filename);
  console.log(`Heap snapshot written to ${filename}`);
}

// Take snapshots periodically or on demand
setInterval(takeHeapSnapshot, 60 * 60 * 1000); // Every hour

// Memory usage monitoring
setInterval(() => {
  const used = process.memoryUsage();
  console.log({
    rss: `${Math.round(used.rss / 1024 / 1024)} MB`,
    heapTotal: `${Math.round(used.heapTotal / 1024 / 1024)} MB`,
    heapUsed: `${Math.round(used.heapUsed / 1024 / 1024)} MB`,
    external: `${Math.round(used.external / 1024 / 1024)} MB`,
  });
}, 10000);
```

**Database Query Profiling:**

```sql
-- PostgreSQL
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE user_id = 123;

-- Slow query log
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1s
```

**Frontend Performance (Web Vitals):**

```javascript
// Core Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    id: metric.id,
    rating: metric.rating,
  });

  // Use `navigator.sendBeacon()` if available, fallback to `fetch()`
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/analytics', body);
  } else {
    fetch('/analytics', { body, method: 'POST', keepalive: true });
  }
}

getCLS(sendToAnalytics);  // Cumulative Layout Shift
getFID(sendToAnalytics);  // First Input Delay
getFCP(sendToAnalytics);  // First Contentful Paint
getLCP(sendToAnalytics);  // Largest Contentful Paint
getTTFB(sendToAnalytics); // Time to First Byte

// Performance Budget (Lighthouse CI)
{
  "budgets": [
    {
      "path": "/*",
      "timings": [
        { "metric": "first-contentful-paint", "budget": 2000 },
        { "metric": "largest-contentful-paint", "budget": 2500 },
        { "metric": "interactive", "budget": 3500 }
      ],
      "resourceSizes": [
        { "resourceType": "script", "budget": 300 },
        { "resourceType": "image", "budget": 500 },
        { "resourceType": "total", "budget": 1000 }
      ]
    }
  ]
}
```

**Checklist:**
- [ ] Profiling enabled in pre-production environments
- [ ] CPU flame graphs captured for hot paths
- [ ] Heap snapshots analyzed for memory leaks
- [ ] Database queries profiled with EXPLAIN ANALYZE
- [ ] N+1 query problems identified and fixed
- [ ] Frontend performance budgets established
- [ ] Web Vitals monitored in production
- [ ] Performance regression tests in CI/CD

---

## Pattern: Capacity Planning

**Use when:** Planning for scale, optimizing costs, preventing outages.

**Capacity Planning Formula:**

```
Required Capacity = Peak Load * Safety Margin / Resource Efficiency

Example:
Peak Load: 10,000 requests/sec
Safety Margin: 1.5 (50% headroom)
Resource Efficiency: 0.7 (70% utilization target)

Required Capacity = 10,000 * 1.5 / 0.7 = 21,429 requests/sec
```

**Load Testing (k6):**

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'], // 99% of requests < 500ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};

export default function () {
  const res = http.get('https://api.example.com/orders');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

**Resource Forecasting (Time Series):**

```python
import pandas as pd
from prophet import Prophet

# Historical CPU usage data
df = pd.DataFrame({
    'ds': pd.date_range('2025-01-01', periods=90, freq='D'),
    'y': cpu_usage_data  # Daily average CPU %
})

# Forecast next 30 days
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Alert if forecast exceeds threshold
if forecast['yhat'].max() > 80:
    print("Alert: Forecasted CPU will exceed 80%")
    print(f"Scale up by: {(forecast['yhat'].max() - 70) / 70 * 100:.0f}%")
```

**Cost Optimization:**

```
Cost per Request = (Infrastructure Cost per Month) / (Total Requests per Month)

Example:
EC2 Instances: $1000/month
Total Requests: 100M/month
Cost per Request: $0.00001

Optimization Target: Reduce to $0.000005 (50% reduction)
Options:
1. Right-size instances (20% savings)
2. Use Spot instances (60% savings)
3. Optimize code (reduce CPU by 30%)
4. Cache frequently accessed data (reduce DB calls by 50%)
```

**Checklist:**
- [ ] Baseline performance metrics established (latency, throughput, resource usage)
- [ ] Load testing performed at 2x expected peak
- [ ] Bottlenecks identified (CPU, memory, database, network)
- [ ] Scaling triggers defined (CPU >70%, latency >500ms)
- [ ] Auto-scaling configured with min/max bounds
- [ ] Cost per request monitored and optimized
- [ ] Capacity forecast updated quarterly
- [ ] Disaster recovery capacity reserved (multi-region)
