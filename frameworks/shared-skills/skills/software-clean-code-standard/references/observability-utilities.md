# Observability Utilities

Centralized patterns for OpenTelemetry setup, distributed tracing, and metrics.

**Updated**: December 2025
**Node.js**: 24 LTS | **Python**: 3.14+ | **Go**: 1.25+

---

## File Structure

```text
src/
└── telemetry/
    ├── index.ts         # OTel initialization
    ├── tracing.ts       # Tracing helpers
    └── metrics.ts       # Custom metrics
```

---

## TypeScript/Node.js

### Dependencies

```bash
npm install @opentelemetry/api@^1.9 \
  @opentelemetry/sdk-node@^0.57 \
  @opentelemetry/auto-instrumentations-node@^0.54 \
  @opentelemetry/exporter-trace-otlp-http@^0.57 \
  @opentelemetry/exporter-metrics-otlp-http@^0.57 \
  @opentelemetry/resources@^1.29 \
  @opentelemetry/semantic-conventions@^1.29
```

### OTel Initialization (`src/telemetry/index.ts`)

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { OTLPMetricExporter } from '@opentelemetry/exporter-metrics-otlp-http';
import { PeriodicExportingMetricReader } from '@opentelemetry/sdk-metrics';
import { Resource } from '@opentelemetry/resources';
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
  ATTR_DEPLOYMENT_ENVIRONMENT_NAME,
} from '@opentelemetry/semantic-conventions';
import { config } from '@/config';

// ============================================
// OPENTELEMETRY SDK SETUP
// ============================================

const resource = new Resource({
  [ATTR_SERVICE_NAME]: config.SERVICE_NAME || 'api',
  [ATTR_SERVICE_VERSION]: config.SERVICE_VERSION || '1.0.0',
  [ATTR_DEPLOYMENT_ENVIRONMENT_NAME]: config.NODE_ENV,
});

const traceExporter = new OTLPTraceExporter({
  url: config.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
});

const metricExporter = new OTLPMetricExporter({
  url: config.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/metrics',
});

const sdk = new NodeSDK({
  resource,
  traceExporter,
  metricReader: new PeriodicExportingMetricReader({
    exporter: metricExporter,
    exportIntervalMillis: 60000, // 1 minute
  }),
  instrumentations: [
    getNodeAutoInstrumentations({
      // Disable noisy instrumentations
      '@opentelemetry/instrumentation-fs': { enabled: false },
      '@opentelemetry/instrumentation-dns': { enabled: false },
      // Configure HTTP instrumentation
      '@opentelemetry/instrumentation-http': {
        ignoreIncomingPaths: ['/health', '/ready', '/metrics'],
      },
    }),
  ],
});

export const initTelemetry = (): void => {
  sdk.start();

  // Graceful shutdown
  process.on('SIGTERM', () => {
    sdk.shutdown()
      .then(() => console.log('Telemetry shut down'))
      .catch((err) => console.error('Error shutting down telemetry', err))
      .finally(() => process.exit(0));
  });
};

export const shutdownTelemetry = async (): Promise<void> => {
  await sdk.shutdown();
};
```

### Tracing Helpers (`src/telemetry/tracing.ts`)

```typescript
import {
  trace,
  SpanStatusCode,
  SpanKind,
  context,
  propagation,
  Span,
  Attributes,
} from '@opentelemetry/api';

const tracer = trace.getTracer('app');

// ============================================
// SPAN HELPERS
// ============================================

/**
 * Execute function within a new span
 */
export const withSpan = async <T>(
  name: string,
  fn: (span: Span) => Promise<T>,
  options?: {
    kind?: SpanKind;
    attributes?: Attributes;
  }
): Promise<T> => {
  return tracer.startActiveSpan(
    name,
    {
      kind: options?.kind ?? SpanKind.INTERNAL,
      attributes: options?.attributes,
    },
    async (span) => {
      try {
        const result = await fn(span);
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      } catch (error) {
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : String(error),
        });
        span.recordException(error as Error);
        throw error;
      } finally {
        span.end();
      }
    }
  );
};

/**
 * Add attributes to current span
 */
export const setSpanAttributes = (attributes: Attributes): void => {
  const span = trace.getActiveSpan();
  if (span) {
    span.setAttributes(attributes);
  }
};

/**
 * Add event to current span
 */
export const addSpanEvent = (name: string, attributes?: Attributes): void => {
  const span = trace.getActiveSpan();
  if (span) {
    span.addEvent(name, attributes);
  }
};

/**
 * Get current trace context for propagation
 */
export const getTraceContext = (): Record<string, string> => {
  const carrier: Record<string, string> = {};
  propagation.inject(context.active(), carrier);
  return carrier;
};

/**
 * Extract trace context from headers
 */
export const extractTraceContext = (
  headers: Record<string, string>
): ReturnType<typeof context.active> => {
  return propagation.extract(context.active(), headers);
};

// ============================================
// DECORATOR-STYLE TRACING
// ============================================

/**
 * Decorator for automatic span creation
 */
export function Traced(spanName?: string) {
  return function (
    target: unknown,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    const name = spanName || `${target?.constructor?.name}.${propertyKey}`;

    descriptor.value = async function (...args: unknown[]) {
      return withSpan(name, async (span) => {
        span.setAttribute('args_count', args.length);
        return originalMethod.apply(this, args);
      });
    };

    return descriptor;
  };
}
```

### Custom Metrics (`src/telemetry/metrics.ts`)

```typescript
import { metrics, Counter, Histogram, UpDownCounter } from '@opentelemetry/api';

const meter = metrics.getMeter('app');

// ============================================
// BUSINESS METRICS
// ============================================

// Request metrics
export const httpRequestCounter = meter.createCounter('http_requests_total', {
  description: 'Total HTTP requests',
});

export const httpRequestDuration = meter.createHistogram('http_request_duration_ms', {
  description: 'HTTP request duration in milliseconds',
  unit: 'ms',
});

// Business metrics
export const ordersCreated = meter.createCounter('orders_created_total', {
  description: 'Total orders created',
});

export const orderValue = meter.createHistogram('order_value_usd', {
  description: 'Order value in USD',
  unit: 'USD',
});

export const activeUsers = meter.createUpDownCounter('active_users', {
  description: 'Currently active users',
});

// Error metrics
export const errorCounter = meter.createCounter('errors_total', {
  description: 'Total errors by type',
});

// ============================================
// METRIC HELPERS
// ============================================

export const recordHttpRequest = (
  method: string,
  path: string,
  statusCode: number,
  durationMs: number
): void => {
  const attributes = { method, path, status_code: statusCode };

  httpRequestCounter.add(1, attributes);
  httpRequestDuration.record(durationMs, attributes);
};

export const recordOrder = (amount: number, currency: string): void => {
  ordersCreated.add(1, { currency });
  orderValue.record(amount, { currency });
};

export const recordError = (type: string, source: string): void => {
  errorCounter.add(1, { type, source });
};
```

### Express Middleware (`src/middleware/telemetry.ts`)

```typescript
import { Request, Response, NextFunction } from 'express';
import { trace, SpanKind, SpanStatusCode } from '@opentelemetry/api';
import { recordHttpRequest } from '@/telemetry/metrics';

const tracer = trace.getTracer('http');

export const telemetryMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const span = tracer.startSpan(`${req.method} ${req.route?.path || req.path}`, {
    kind: SpanKind.SERVER,
    attributes: {
      'http.method': req.method,
      'http.url': req.url,
      'http.route': req.route?.path,
      'http.user_agent': req.headers['user-agent'],
    },
  });

  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;

    span.setAttributes({
      'http.status_code': res.statusCode,
      'http.response_content_length': res.get('content-length'),
    });

    if (res.statusCode >= 400) {
      span.setStatus({ code: SpanStatusCode.ERROR });
    } else {
      span.setStatus({ code: SpanStatusCode.OK });
    }

    span.end();

    // Record metrics
    recordHttpRequest(req.method, req.route?.path || req.path, res.statusCode, duration);
  });

  next();
};
```

### Usage

```typescript
import { initTelemetry } from '@/telemetry';
import { withSpan, setSpanAttributes, Traced } from '@/telemetry/tracing';
import { ordersCreated, recordError } from '@/telemetry/metrics';

// Initialize at startup (MUST be first import)
initTelemetry();

// Manual span
const user = await withSpan('fetchUser', async (span) => {
  span.setAttribute('user_id', userId);
  return db.user.findUnique({ where: { id: userId } });
});

// Decorator-based
class UserService {
  @Traced()
  async getUser(id: string) {
    return db.user.findUnique({ where: { id } });
  }
}

// Record metrics
ordersCreated.add(1, { type: 'subscription' });
recordError('validation', 'user_service');
```

---

## Python

### Dependencies

```bash
pip install opentelemetry-api>=1.29 \
  opentelemetry-sdk>=1.29 \
  opentelemetry-exporter-otlp>=1.29 \
  opentelemetry-instrumentation-fastapi>=0.50 \
  opentelemetry-instrumentation-httpx>=0.50 \
  opentelemetry-instrumentation-sqlalchemy>=0.50
```

### OTel Initialization (`src/telemetry/__init__.py`)

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from src.config.settings import settings


def init_telemetry() -> None:
    """Initialize OpenTelemetry SDK."""
    resource = Resource.create({
        SERVICE_NAME: settings.service_name,
        SERVICE_VERSION: settings.service_version,
        "deployment.environment": settings.app_env,
    })

    # Tracing
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=settings.otel_endpoint + "/v1/traces")
        )
    )
    trace.set_tracer_provider(trace_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=settings.otel_endpoint + "/v1/metrics"),
        export_interval_millis=60000,
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Auto-instrumentation
    FastAPIInstrumentor.instrument()
    HTTPXClientInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()


def shutdown_telemetry() -> None:
    """Shutdown telemetry providers."""
    trace.get_tracer_provider().shutdown()
    metrics.get_meter_provider().shutdown()
```

### Tracing Helpers (`src/telemetry/tracing.py`)

```python
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

P = ParamSpec("P")
T = TypeVar("T")

tracer = trace.get_tracer("app")


def with_span(
    name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: dict[str, Any] | None = None,
):
    """Decorator to wrap function in span."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with tracer.start_as_current_span(
                name, kind=kind, attributes=attributes or {}
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with tracer.start_as_current_span(
                name, kind=kind, attributes=attributes or {}
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def set_span_attributes(attributes: dict[str, Any]) -> None:
    """Add attributes to current span."""
    span = trace.get_current_span()
    if span.is_recording():
        span.set_attributes(attributes)


def add_span_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """Add event to current span."""
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event(name, attributes or {})
```

### Custom Metrics (`src/telemetry/metrics.py`)

```python
from opentelemetry import metrics

meter = metrics.get_meter("app")

# Request metrics
http_request_counter = meter.create_counter(
    "http_requests_total",
    description="Total HTTP requests",
)

http_request_duration = meter.create_histogram(
    "http_request_duration_ms",
    description="HTTP request duration in milliseconds",
    unit="ms",
)

# Business metrics
orders_created = meter.create_counter(
    "orders_created_total",
    description="Total orders created",
)

order_value = meter.create_histogram(
    "order_value_usd",
    description="Order value in USD",
    unit="USD",
)

error_counter = meter.create_counter(
    "errors_total",
    description="Total errors by type",
)


def record_http_request(
    method: str, path: str, status_code: int, duration_ms: float
) -> None:
    attributes = {"method": method, "path": path, "status_code": status_code}
    http_request_counter.add(1, attributes)
    http_request_duration.record(duration_ms, attributes)


def record_order(amount: float, currency: str) -> None:
    orders_created.add(1, {"currency": currency})
    order_value.record(amount, {"currency": currency})


def record_error(error_type: str, source: str) -> None:
    error_counter.add(1, {"type": error_type, "source": source})
```

### Usage

```python
from src.telemetry import init_telemetry
from src.telemetry.tracing import with_span, set_span_attributes
from src.telemetry.metrics import orders_created, record_error

# Initialize at startup
init_telemetry()


# Decorator-based tracing
@with_span("fetch_user")
async def get_user(user_id: str) -> User:
    set_span_attributes({"user_id": user_id})
    return await db.get_user(user_id)


# Manual metrics
orders_created.add(1, {"type": "subscription"})
record_error("validation", "user_service")
```

---

## Go

### Dependencies

```bash
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp
go get go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp
go get go.opentelemetry.io/otel/sdk
go get go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp
```

### OTel Initialization (`internal/telemetry/telemetry.go`)

```go
package telemetry

import (
    "context"
    "time"

    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetrichttp"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/metric"
    "go.opentelemetry.io/otel/sdk/resource"
    "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

func Init(ctx context.Context, serviceName, serviceVersion, env string) (func(), error) {
    res, err := resource.New(ctx,
        resource.WithAttributes(
            semconv.ServiceNameKey.String(serviceName),
            semconv.ServiceVersionKey.String(serviceVersion),
            semconv.DeploymentEnvironmentKey.String(env),
        ),
    )
    if err != nil {
        return nil, err
    }

    // Trace exporter
    traceExporter, err := otlptracehttp.New(ctx)
    if err != nil {
        return nil, err
    }

    tracerProvider := trace.NewTracerProvider(
        trace.WithBatcher(traceExporter),
        trace.WithResource(res),
    )
    otel.SetTracerProvider(tracerProvider)

    // Metric exporter
    metricExporter, err := otlpmetrichttp.New(ctx)
    if err != nil {
        return nil, err
    }

    meterProvider := metric.NewMeterProvider(
        metric.WithReader(metric.NewPeriodicReader(metricExporter, metric.WithInterval(time.Minute))),
        metric.WithResource(res),
    )
    otel.SetMeterProvider(meterProvider)

    // Propagator
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    // Shutdown function
    return func() {
        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()
        tracerProvider.Shutdown(ctx)
        meterProvider.Shutdown(ctx)
    }, nil
}
```

### Usage

```go
package main

import (
    "context"
    "myapp/internal/telemetry"
)

func main() {
    ctx := context.Background()

    shutdown, err := telemetry.Init(ctx, "myapp", "1.0.0", "production")
    if err != nil {
        log.Fatal(err)
    }
    defer shutdown()

    // Start server...
}
```

---

## Observability Backends

| Backend | Tracing | Metrics | Logs | Self-Hosted |
|---------|---------|---------|------|-------------|
| **Jaeger** | Yes | No | No | Yes |
| **Grafana Tempo** | Yes | No | No | Yes |
| **Prometheus** | No | Yes | No | Yes |
| **Grafana Loki** | No | No | Yes | Yes |
| **Datadog** | Yes | Yes | Yes | No |
| **Honeycomb** | Yes | Yes | No | No |
| **New Relic** | Yes | Yes | Yes | No |

### Local Development Stack

```yaml
# docker-compose.yml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "4318:4318"    # OTLP HTTP

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
```

---

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [OpenTelemetry JS SDK](https://opentelemetry.io/docs/languages/js/)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/)
- [OpenTelemetry Go SDK](https://opentelemetry.io/docs/languages/go/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
