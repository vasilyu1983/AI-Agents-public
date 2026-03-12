# Observability-Driven Testing

Use production telemetry (traces, metrics, logs) as the foundation for test design, validation, and debugging. OpenTelemetry is the 2026 de facto standard for instrumentation.

## Contents

- When to Use This Reference
- Core Concept: Observability-Driven Development (ODD)
- OpenTelemetry Integration
- Trace-Based Testing with Tracetest
- Production Trace → Test Case Conversion
- Observability in CI/CD
- Debugging with Traces
- Metrics-Based Test Validation
- Best Practices
- Quick Start Checklist
- Related References
- External Resources

---

## When to Use This Reference

- Designing tests for distributed systems and microservices
- Debugging flaky or intermittent test failures
- Converting production incidents into regression tests
- Validating instrumentation coverage
- Building trace-based test assertions

---

## Core Concept: Observability-Driven Development (ODD)

> "The best engineers do a form of observability-driven development — they understand their software as they write it, include instrumentation when they ship it, then check it regularly to make sure it looks as expected." — Charity Majors

### ODD Workflow

```text
1. WRITE CODE
   Include instrumentation (spans, metrics, logs) as you code

2. SHIP WITH TELEMETRY
   Deploy with traces, metrics, structured logs enabled

3. OBSERVE IN PRODUCTION
   Check telemetry matches expectations

4. CONVERT TO TESTS
   Production traces become test assertions
   Real failure patterns become test cases

5. ITERATE
   Use production insights to improve test coverage
```

### Traditional vs Observability-Driven Testing

| Traditional Testing | Observability-Driven Testing |
|---------------------|------------------------------|
| Write tests, hope they catch bugs | Observe production, write tests for real issues |
| Mock everything | Use real traces for validation |
| Test in isolation | Test distributed behavior |
| Debug with logs | Debug with traces |
| Coverage = lines executed | Coverage = behaviors observed |

---

## OpenTelemetry Integration

### The Three Pillars

```text
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   TRACES    │  │   METRICS   │  │    LOGS     │
│             │  │             │  │             │
│ Request flow│  │ Aggregates  │  │ Events      │
│ across      │  │ over time   │  │ with        │
│ services    │  │             │  │ context     │
└─────────────┘  └─────────────┘  └─────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         ▼
              ┌─────────────────────┐
              │   OpenTelemetry     │
              │   Unified Protocol  │
              └─────────────────────┘
```

### Instrumenting Test Code

```typescript
// test-instrumentation.ts
import { trace, SpanStatusCode } from '@opentelemetry/api';
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

// Initialize tracer for tests
const provider = new NodeTracerProvider();
provider.addSpanProcessor(
  new SimpleSpanProcessor(
    new OTLPTraceExporter({ url: 'http://localhost:4318/v1/traces' })
  )
);
provider.register();

const tracer = trace.getTracer('test-suite');

// Instrumented test
describe('Order Service', () => {
  it('should create order with payment', async () => {
    await tracer.startActiveSpan('test:create-order-with-payment', async (span) => {
      try {
        // Arrange
        span.setAttribute('test.phase', 'arrange');
        const user = await createTestUser();
        const product = await createTestProduct();

        // Act
        span.setAttribute('test.phase', 'act');
        const order = await orderService.create({
          userId: user.id,
          productId: product.id,
          quantity: 1
        });

        // Assert
        span.setAttribute('test.phase', 'assert');
        expect(order.status).toBe('paid');
        expect(order.paymentId).toBeDefined();

        span.setStatus({ code: SpanStatusCode.OK });
      } catch (error) {
        span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
        span.recordException(error);
        throw error;
      } finally {
        span.end();
      }
    });
  });
});
```

---

## Trace-Based Testing with Tracetest

Tracetest enables assertions on OpenTelemetry traces, validating distributed behavior.

### Installation

```bash
# Install Tracetest CLI
curl -L https://raw.githubusercontent.com/kubeshop/tracetest/main/install-cli.sh | bash

# Configure backend
tracetest configure --server-url http://localhost:11633
```

### Test Definition

```yaml
# tracetest-order-flow.yaml
type: Test
spec:
  name: Order Creation Flow
  description: Validate order creation spans and attributes
  trigger:
    type: http
    httpRequest:
      url: http://api.example.com/orders
      method: POST
      headers:
        - key: Content-Type
          value: application/json
      body: |
        {
          "userId": "user-123",
          "productId": "prod-456",
          "quantity": 2
        }

  specs:
    # Validate order service span
    - selector: span[name="POST /orders"]
      assertions:
        - attr:http.status_code = 201
        - attr:http.response.body contains "orderId"

    # Validate payment service was called
    - selector: span[name="payment.process"]
      assertions:
        - attr:payment.status = "success"
        - attr:payment.amount > 0

    # Validate database write
    - selector: span[name="db.orders.insert"]
      assertions:
        - attr:db.system = "postgresql"
        - attr:db.operation = "INSERT"

    # Validate total duration
    - selector: span[name="POST /orders"]
      assertions:
        - attr:tracetest.span.duration < 2000ms
```

### Running Trace Tests

```bash
# Run single test
tracetest run test --file tracetest-order-flow.yaml

# Run in CI with JUnit output
tracetest run test --file tracetest-order-flow.yaml --output junit > test-results.xml

# Run test suite
tracetest run test --file tests/*.yaml --parallel 4
```

---

## Production Trace → Test Case Conversion

### Workflow

```text
1. CAPTURE
   Export production traces from observability backend

2. FILTER
   Select traces representing critical user journeys

3. SANITIZE
   Remove PII, replace IDs with test fixtures

4. CONVERT
   Transform trace into executable test case

5. VALIDATE
   Run test, verify it reproduces expected behavior
```

### Automated Conversion Script

```python
# trace_to_test.py
import json
from opentelemetry.proto.trace.v1 import trace_pb2

def trace_to_tracetest(trace_data: dict, test_name: str) -> dict:
    """Convert production trace to Tracetest format."""

    root_span = find_root_span(trace_data['spans'])

    test = {
        'type': 'Test',
        'spec': {
            'name': test_name,
            'description': f'Generated from production trace {trace_data["traceId"]}',
            'trigger': {
                'type': 'http',
                'httpRequest': extract_http_request(root_span)
            },
            'specs': []
        }
    }

    # Generate assertions from span attributes
    for span in trace_data['spans']:
        assertions = generate_assertions(span)
        if assertions:
            test['spec']['specs'].append({
                'selector': f'span[name="{span["name"]}"]',
                'assertions': assertions
            })

    return test

def generate_assertions(span: dict) -> list:
    """Generate assertions from span attributes."""
    assertions = []

    attrs = span.get('attributes', {})

    # HTTP assertions
    if 'http.status_code' in attrs:
        assertions.append(f"attr:http.status_code = {attrs['http.status_code']}")

    # Database assertions
    if 'db.operation' in attrs:
        assertions.append(f"attr:db.operation = \"{attrs['db.operation']}\"")

    # Duration assertion (allow 2x production latency)
    if 'duration_ms' in span:
        assertions.append(f"attr:tracetest.span.duration < {span['duration_ms'] * 2}ms")

    return assertions
```

---

## Observability in CI/CD

### GitHub Actions Integration

```yaml
name: Observability-Driven Tests
on: [push, pull_request]

jobs:
  trace-tests:
    runs-on: ubuntu-latest
    services:
      jaeger:
        image: jaegertracing/all-in-one:latest
        ports:
          - 16686:16686
          - 4317:4317

      tracetest:
        image: kubeshop/tracetest:latest
        ports:
          - 11633:11633
        env:
          TRACETEST_DEV: true

    steps:
      - uses: actions/checkout@v4

      - name: Start Application with Instrumentation
        run: |
          docker-compose -f docker-compose.test.yml up -d
          sleep 10

      - name: Run Trace-Based Tests
        run: |
          tracetest configure --server-url http://localhost:11633
          tracetest run test --file tests/trace-tests/*.yaml --output junit > trace-test-results.xml

      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        with:
          name: trace-test-results
          path: trace-test-results.xml

      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: trace-test-results.xml
```

### Telemetry Validation Gate

```yaml
# Validate instrumentation coverage before deploy
- name: Validate Telemetry Coverage
  run: |
    # Query spans from test run
    SPAN_COUNT=$(curl -s "$JAEGER_URL/api/traces?service=order-service&limit=100" | jq '.data | length')

    # Ensure minimum span coverage
    if [ "$SPAN_COUNT" -lt 10 ]; then
      echo "ERROR: Insufficient instrumentation coverage"
      exit 1
    fi

    # Validate required spans exist
    REQUIRED_SPANS=("POST /orders" "payment.process" "db.orders.insert")
    for span in "${REQUIRED_SPANS[@]}"; do
      if ! curl -s "$JAEGER_URL/api/traces?service=order-service" | grep -q "$span"; then
        echo "ERROR: Missing required span: $span"
        exit 1
      fi
    done
```

---

## Debugging with Traces

### Flaky Test Investigation

```text
Test: Order creation intermittently fails

STEP 1: Collect traces from passing and failing runs
        tracetest run test --file order.yaml --output json > passing.json
        # Wait for failure
        tracetest run test --file order.yaml --output json > failing.json

STEP 2: Compare trace structure
        diff <(jq '.spans[].name' passing.json | sort) \
             <(jq '.spans[].name' failing.json | sort)

STEP 3: Identify timing differences
        jq '.spans[] | {name, duration: .endTime - .startTime}' passing.json
        jq '.spans[] | {name, duration: .endTime - .startTime}' failing.json

STEP 4: Check for missing spans or errors
        jq '.spans[] | select(.status.code == 2)' failing.json
```

### Root Cause Analysis

```typescript
// Use trace context in test assertions
it('should handle concurrent orders', async () => {
  const traceId = generateTraceId();

  // Inject trace context
  const result = await orderService.create(order, {
    traceId,
    spanId: generateSpanId()
  });

  // On failure, print trace link
  if (result.status !== 'success') {
    console.log(`Trace: ${JAEGER_URL}/trace/${traceId}`);
    console.log(`Failing span: ${result.spanId}`);
  }

  expect(result.status).toBe('success');
});
```

---

## Metrics-Based Test Validation

### SLO Validation in Tests

```typescript
// slo-validation.test.ts
describe('SLO Validation', () => {
  it('should meet latency SLO under load', async () => {
    const results = await runLoadTest({
      duration: '5m',
      vus: 100,
      rps: 1000
    });

    // Query actual metrics
    const p99Latency = await prometheus.query(
      'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))'
    );

    const errorRate = await prometheus.query(
      'sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))'
    );

    // Assert SLOs
    expect(p99Latency).toBeLessThan(0.2);  // 200ms
    expect(errorRate).toBeLessThan(0.01);   // 1%
  });
});
```

### Automated SLO Checks

```yaml
# slo-gate.yaml
name: SLO Validation Gate
on:
  schedule:
    - cron: '0 * * * *'  # Hourly

jobs:
  validate-slos:
    runs-on: ubuntu-latest
    steps:
      - name: Check Latency SLO
        run: |
          P99=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=histogram_quantile(0.99,rate(http_request_duration_seconds_bucket[1h]))" | jq '.data.result[0].value[1]')
          if (( $(echo "$P99 > 0.2" | bc -l) )); then
            echo "SLO BREACH: p99 latency $P99 > 200ms"
            exit 1
          fi

      - name: Check Error Rate SLO
        run: |
          ERROR_RATE=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=sum(rate(http_requests_total{status=~'5..'}[1h]))/sum(rate(http_requests_total[1h]))" | jq '.data.result[0].value[1]')
          if (( $(echo "$ERROR_RATE > 0.001" | bc -l) )); then
            echo "SLO BREACH: error rate $ERROR_RATE > 0.1%"
            exit 1
          fi
```

---

## Best Practices

### Do

- Instrument code as you write it, not after
- Use trace IDs to correlate test failures with production behavior
- Convert production incidents into automated regression tests
- Validate instrumentation coverage in CI/CD gates
- Use semantic conventions (OpenTelemetry standards)

### Avoid

- Adding observability only after production issues
- Testing mocked services when traces can validate real behavior
- Ignoring flaky tests without trace investigation
- Shipping code without required spans

---

## Quick Start Checklist

- [ ] Install OpenTelemetry SDK in application
- [ ] Configure trace exporter (Jaeger, Tempo, Honeycomb)
- [ ] Add spans to critical code paths
- [ ] Install Tracetest for trace-based testing
- [ ] Write first trace-based test for happy path
- [ ] Add telemetry coverage validation to CI
- [ ] Create production trace → test conversion workflow

---

## Related References

- [operational-playbook.md](operational-playbook.md) — Test pyramid and CI gates
- [chaos-resilience-testing.md](chaos-resilience-testing.md) — Resilience testing with observability
- [../SKILL.md](../SKILL.md) — Main testing strategy overview
- [../../ops-devops-platform/SKILL.md](../../ops-devops-platform/SKILL.md) — Observability infrastructure

---

## External Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Tracetest](https://tracetest.io/)
- [Observability-Driven Development (Charity Majors)](https://charity.wtf/tag/observability/)
- [Honeycomb Guide to Observability](https://www.honeycomb.io/what-is-observability)
- [Jaeger Tracing](https://www.jaegertracing.io/)
