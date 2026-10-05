# Distributed Tracing Patterns

Operational patterns for implementing distributed tracing across HTTP, queues, and RPC boundaries.

## Table of Contents

- [Core rules](#core-rules)
- [HTTP propagation](#http-propagation)
- [Message queue propagation](#message-queue-propagation)
- [gRPC propagation](#grpc-propagation)
- [Manual span design](#manual-span-design)
- [Trace, log, and metric correlation](#trace-log-and-metric-correlation)
- [Troubleshooting checklist](#troubleshooting-checklist)

## Core rules

- Propagate W3C trace context everywhere possible.
- Reuse the active context instead of passing parent spans around manually.
- Model protocol work and business work as separate spans.
- Correlate traces with logs and metrics; a trace without supporting evidence is harder to debug.

## HTTP propagation

Use when one service calls another over HTTP.

```javascript
const axios = require('axios');
const { context, propagation, trace } = require('@opentelemetry/api');

async function callServiceB(payload) {
  const tracer = trace.getTracer('service-a');

  return tracer.startActiveSpan('service-b.request', async (span) => {
    const headers = {};
    propagation.inject(context.active(), headers);

    try {
      const response = await axios.post('http://service-b/api/process', payload, {
        headers: {
          ...headers,
          'content-type': 'application/json',
        },
      });

      span.setAttribute('peer.service', 'service-b');
      return response.data;
    } finally {
      span.end();
    }
  });
}
```

Verification checklist:
- `traceparent` is present on the outbound request.
- Service B extracts the same trace ID.
- The resulting trace shows one end-to-end path across both services.

## Message queue propagation

Use when work continues asynchronously via Kafka, RabbitMQ, SQS, or a similar broker.

```javascript
const { context, propagation, trace } = require('@opentelemetry/api');

async function publishMessage(channel, payload) {
  const headers = {};
  propagation.inject(context.active(), headers);

  await channel.publish('orders', 'created', Buffer.from(JSON.stringify(payload)), {
    headers,
  });
}

async function consumeMessage(msg) {
  const ctx = propagation.extract(context.active(), msg.properties.headers || {});
  const tracer = trace.getTracer('order-consumer');

  return context.with(ctx, async () => {
    await tracer.startActiveSpan('order.consume', async (span) => {
      try {
        const payload = JSON.parse(msg.content.toString());
        span.setAttribute('messaging.operation', 'process');
        span.setAttribute('order.id', payload.order_id);
      } finally {
        span.end();
      }
    });
  });
}
```

## gRPC propagation

Use metadata as the carrier.

```javascript
const grpc = require('@grpc/grpc-js');
const { context, propagation } = require('@opentelemetry/api');

function injectMetadata() {
  const metadata = new grpc.Metadata();
  propagation.inject(context.active(), metadata);
  return metadata;
}

function extractContext(metadata) {
  return propagation.extract(context.active(), metadata.getMap());
}
```

## Manual span design

Preferred pattern:
- Use `startActiveSpan` in JavaScript and `start_as_current_span` in Python.
- Keep child operations inside the active context.
- Use links for detached async work, not as a replacement for normal parent-child structure.

```javascript
const { trace } = require('@opentelemetry/api');

async function processOrder(orderId) {
  const tracer = trace.getTracer('order-service');

  return tracer.startActiveSpan('order.process', async (span) => {
    try {
      span.setAttribute('order.id', orderId);

      await tracer.startActiveSpan('order.validate', async (childSpan) => {
        try {
          await validateOrder(orderId);
        } finally {
          childSpan.end();
        }
      });

      await tracer.startActiveSpan('payment.capture', async (childSpan) => {
        try {
          await capturePayment(orderId);
        } finally {
          childSpan.end();
        }
      });
    } finally {
      span.end();
    }
  });
}
```

## Trace, log, and metric correlation

Minimum bar:
- Trace ID appears in request-scoped logs.
- Key latency metrics include exemplars where supported.
- Test failures emit a trace link or trace ID that can be opened from CI artifacts.

Operational pattern:
- Metrics tell you there is a problem.
- Traces show which dependency or workflow step is slow.
- Logs explain the concrete failure and business context.

## Troubleshooting checklist

- Missing child spans: verify active context survives async boundaries.
- Split traces between services: verify `traceparent` propagation or metadata/header extraction.
- Duplicate HTTP spans: remove manual route spans if server auto-instrumentation already exists.
- Too few useful traces in prod: re-check sampling rules and retention for errors and slow paths.
- Trace IDs absent from logs: pull them from the active span context instead of parsing inbound headers manually.
