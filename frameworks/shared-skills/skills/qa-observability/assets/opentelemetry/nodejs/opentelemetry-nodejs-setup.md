# OpenTelemetry Node.js Setup Template

Production-ready starter for Node.js services. This template assumes CommonJS, OTLP over HTTP, and a Collector-first deployment model.

## 1. Install dependencies

```bash
npm install --save \
  @opentelemetry/api \
  @opentelemetry/sdk-node \
  @opentelemetry/sdk-metrics \
  @opentelemetry/sdk-trace-base \
  @opentelemetry/resources \
  @opentelemetry/auto-instrumentations-node \
  @opentelemetry/exporter-trace-otlp-http \
  @opentelemetry/exporter-metrics-otlp-http \
  express
```

## 2. Create instrumentation file

**`src/instrumentation.js`**. Load this before the rest of the app.

```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { ParentBasedSampler, TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');

const resource = resourceFromAttributes({
  'service.name': process.env.OTEL_SERVICE_NAME || 'order-api',
  'service.version': process.env.SERVICE_VERSION || '1.0.0',
  'deployment.environment.name': process.env.NODE_ENV || 'development',
});

const sampler = new ParentBasedSampler({
  root: new TraceIdRatioBasedSampler(
    process.env.NODE_ENV === 'production' ? 0.1 : 1.0
  ),
});

const sdk = new NodeSDK({
  resource,
  sampler,
  traceExporter: new OTLPTraceExporter(),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new OTLPMetricExporter(),
    exportIntervalMillis: 60000,
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      '@opentelemetry/instrumentation-fs': { enabled: false },
      '@opentelemetry/instrumentation-net': { enabled: false },
      '@opentelemetry/instrumentation-dns': { enabled: false },
    }),
  ],
});

sdk.start();

async function shutdown() {
  try {
    await sdk.shutdown();
  } finally {
    process.exit(0);
  }
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
```

## 3. Load instrumentation first

**`src/server.js`**

```javascript
require('./instrumentation');

const express = require('express');
const { randomUUID } = require('crypto');
const { trace } = require('@opentelemetry/api');

const app = express();
app.use(express.json());

app.use((req, res, next) => {
  req.requestId = req.headers['x-request-id'] || randomUUID();
  res.setHeader('x-request-id', req.requestId);
  next();
});

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

app.post('/api/orders', async (req, res, next) => {
  const tracer = trace.getTracer('order-service');

  try {
    const result = await tracer.startActiveSpan('order.process', async (span) => {
      try {
        span.setAttribute('order.id', req.body.order_id);
        span.setAttribute('app.request_id', req.requestId);

        const payment = await tracer.startActiveSpan('payment.capture', async (childSpan) => {
          try {
            childSpan.setAttribute('payment.provider', 'stripe');
            return { id: 'pay_123', status: 'captured' };
          } finally {
            childSpan.end();
          }
        });

        span.setAttribute('payment.id', payment.id);
        return { order_id: req.body.order_id, payment_id: payment.id };
      } catch (error) {
        span.recordException(error);
        throw error;
      } finally {
        span.end();
      }
    });

    res.status(201).json(result);
  } catch (error) {
    next(error);
  }
});

app.use((error, _req, res, _next) => {
  res.status(500).json({ error: error.message });
});

app.listen(process.env.PORT || 3000);
```

## 4. Correlate logs with the active span

```javascript
const { trace } = require('@opentelemetry/api');

function getTelemetryContext() {
  const spanContext = trace.getActiveSpan()?.spanContext();

  return {
    trace_id: spanContext?.traceId,
    span_id: spanContext?.spanId,
  };
}
```

## 5. Environment variables

```bash
OTEL_SERVICE_NAME=order-api
SERVICE_VERSION=1.0.0
NODE_ENV=production

# Keep OTLP base endpoint separate from signal-specific overrides.
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

PORT=3000
```

## 6. Operational notes

- In production, prefer `app -> Collector -> backend` over sending directly to a vendor or trace store.
- Use auto-instrumentation for HTTP servers, clients, DB drivers, and queues. Add manual spans around business workflow boundaries, not around every route handler.
- Do not duplicate protocol attributes such as `http.request.method` on custom workflow spans unless the span itself models an HTTP operation.
- Keep `trace_id`, `span_id`, and `request_id` in logs, but do not promote them to metrics labels or Loki labels.
