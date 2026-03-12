# OpenTelemetry Node.js Setup Template

Complete setup template for instrumenting a Node.js application with OpenTelemetry.

## Project Structure

```
my-app/
  src/
    instrumentation.js       # OpenTelemetry setup (load FIRST)
    server.js                # Express server
    routes/
      orders.js
    services/
      orderService.js
  package.json
  .env
```

## 1. Install Dependencies

```bash
npm install --save \
  @opentelemetry/sdk-node \
  @opentelemetry/auto-instrumentations-node \
  @opentelemetry/exporter-trace-otlp-http \
  @opentelemetry/exporter-metrics-otlp-http \
  @opentelemetry/sdk-metrics \
  @opentelemetry/resources \
  @opentelemetry/semantic-conventions \
  @opentelemetry/api
```

## 2. Create Instrumentation File

**`src/instrumentation.js`** (load BEFORE any other imports):

```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { OTLPMetricExporter } = require('@opentelemetry/exporter-metrics-otlp-http');
const { PeriodicExportingMetricReader } = require('@opentelemetry/sdk-metrics');
const { Resource } = require('@opentelemetry/resources');
const { SemanticResourceAttributes } = require('@opentelemetry/semantic-conventions');
const { ParentBasedSampler, TraceIdRatioBasedSampler } = require('@opentelemetry/sdk-trace-base');

// Resource attributes (service metadata)
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: process.env.SERVICE_NAME || 'my-service',
  [SemanticResourceAttributes.SERVICE_VERSION]: process.env.SERVICE_VERSION || '1.0.0',
  [SemanticResourceAttributes.DEPLOYMENT_ENVIRONMENT]: process.env.NODE_ENV || 'development',
});

// Sampling strategy
const sampler = new ParentBasedSampler({
  root: new TraceIdRatioBasedSampler(
    process.env.NODE_ENV === 'production' ? 0.1 : 1.0 // 10% in prod, 100% in dev
  ),
});

// Initialize OpenTelemetry SDK
const sdk = new NodeSDK({
  resource: resource,
  sampler: sampler,
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

// Start SDK
sdk.start();

// Graceful shutdown
process.on('SIGTERM', () => {
  sdk
    .shutdown()
    .then(() => console.log('OpenTelemetry shut down successfully'))
    .catch((error) => console.error('Error shutting down OpenTelemetry', error))
    .finally(() => process.exit(0));
});

module.exports = sdk;
```

---

## 3. Update Server Entry Point

**`src/server.js`** (load instrumentation FIRST):

```javascript
// MUST BE FIRST LINE
require('./instrumentation');

// Now import your app
const express = require('express');
const { trace, context } = require('@opentelemetry/api');

const app = express();
app.use(express.json());

// Add request ID middleware
app.use((req, res, next) => {
  req.id = Math.random().toString(36).substring(7);
  next();
});

// Import routes
const orderRoutes = require('./routes/orders');
app.use('/api/orders', orderRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
```

---

## 4. Add Custom Spans to Business Logic

**`src/services/orderService.js`**:

```javascript
const { trace, SpanStatusCode } = require('@opentelemetry/api');

class OrderService {
  async processOrder(orderId) {
    const tracer = trace.getTracer('order-service');
    const span = tracer.startSpan('process-order');

    // Add attributes
    span.setAttribute('order.id', orderId);
    span.setAttribute('order.source', 'web');

    try {
      // Validate order
      span.addEvent('validation-started');
      const isValid = await this.validateOrder(orderId);
      span.addEvent('validation-completed', { is_valid: isValid });

      if (!isValid) {
        span.setStatus({ code: SpanStatusCode.ERROR, message: 'Invalid order' });
        throw new Error('Invalid order');
      }

      // Process payment
      span.addEvent('payment-started');
      const payment = await this.processPayment(orderId);
      span.setAttribute('payment.id', payment.id);
      span.setAttribute('payment.amount', payment.amount);
      span.addEvent('payment-completed');

      // Fulfill order
      span.addEvent('fulfillment-started');
      await this.fulfillOrder(orderId);
      span.addEvent('fulfillment-completed');

      span.setStatus({ code: SpanStatusCode.OK });
      return { success: true, orderId, paymentId: payment.id };
    } catch (error) {
      // Record exception
      span.recordException(error);
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message,
      });
      throw error;
    } finally {
      span.end();
    }
  }

  async validateOrder(orderId) {
    // Validation logic
    return true;
  }

  async processPayment(orderId) {
    // Payment logic
    return { id: 'pay_123', amount: 99.99 };
  }

  async fulfillOrder(orderId) {
    // Fulfillment logic
  }
}

module.exports = new OrderService();
```

---

## 5. Route with Tracing

**`src/routes/orders.js`**:

```javascript
const express = require('express');
const { trace } = require('@opentelemetry/api');
const orderService = require('../services/orderService');

const router = express.Router();

router.post('/', async (req, res) => {
  const tracer = trace.getTracer('order-api');
  const span = tracer.startSpan('POST /api/orders');

  span.setAttribute('http.method', 'POST');
  span.setAttribute('http.route', '/api/orders');
  span.setAttribute('user.id', req.user?.id || 'anonymous');

  try {
    const order = await orderService.processOrder(req.body);

    span.setAttribute('http.status_code', 201);
    res.status(201).json(order);
  } catch (error) {
    span.recordException(error);
    span.setAttribute('http.status_code', 500);
    res.status(500).json({ error: error.message });
  } finally {
    span.end();
  }
});

module.exports = router;
```

---

## 6. Environment Variables

**`.env`**:

```bash
# Service metadata
SERVICE_NAME=order-api
SERVICE_VERSION=1.0.0
NODE_ENV=production

# OpenTelemetry exporter
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

# Application
PORT=3000
```

---

## 7. Docker Compose (Local Development)

**`docker-compose.yml`**:

```yaml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "4318:4318"    # OTLP HTTP receiver
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - SERVICE_NAME=order-api
      - SERVICE_VERSION=1.0.0
      - NODE_ENV=development
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
    depends_on:
      - jaeger
```

---

## 8. Kubernetes Deployment

**`k8s/deployment.yaml`**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-api
  template:
    metadata:
      labels:
        app: order-api
    spec:
      containers:
      - name: app
        image: my-registry/order-api:1.0.0
        ports:
        - containerPort: 3000
        env:
        - name: SERVICE_NAME
          value: "order-api"
        - name: SERVICE_VERSION
          value: "1.0.0"
        - name: NODE_ENV
          value: "production"
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://otel-collector:4318"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 9. Testing Instrumentation

**Run application:**

```bash
# Start Jaeger
docker-compose up -d jaeger

# Start app
npm start

# Make requests
curl -X POST http://localhost:3000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"items": [{"id": 123, "quantity": 2}]}'

# View traces in Jaeger UI
open http://localhost:16686
```

---

## 10. Debugging

**Enable debug logging:**

```javascript
// Add to instrumentation.js (before SDK initialization)
const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');

diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);
```

**Common issues:**

1. **No traces appearing:**
   - Check OTEL_EXPORTER_OTLP_ENDPOINT is reachable
   - Verify instrumentation.js loads first
   - Check sampling rate (set to 1.0 for testing)

2. **Broken traces:**
   - Verify trace context propagation in HTTP calls
   - Check that all services use same trace format

3. **High overhead:**
   - Reduce sampling rate (0.01 = 1%)
   - Disable unnecessary instrumentations
   - Use BatchSpanProcessor (default)

---

## Next Steps

1. **Add structured logging** with trace correlation
2. **Set up metrics** (custom counters, gauges, histograms)
3. **Configure SLOs** and alerting
4. **Integrate with APM** (Datadog, New Relic, etc.)
5. **Add trace exemplars** to metrics

Related topics:

- Structured Logging with trace correlation
- Prometheus Metrics configuration
- SLO Definition patterns
