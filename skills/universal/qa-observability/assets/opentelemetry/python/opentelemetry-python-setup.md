# OpenTelemetry Python Setup Template

Production-ready starter for Python services. This template uses Flask, OTLP over HTTP, and a Collector-first deployment model.

## 1. Install dependencies

Pin to a currently tested compatible release set in your app. Do not cargo-cult old example versions.

```txt
Flask>=3.0
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-flask
opentelemetry-instrumentation-requests
```

```bash
pip install -r requirements.txt
```

## 2. Create instrumentation file

**`src/instrumentation.py`**

```python
import atexit
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

resource = Resource.create(
    {
        "service.name": os.getenv("OTEL_SERVICE_NAME", "order-api"),
        "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
        "deployment.environment.name": os.getenv("ENV", "development"),
    }
)

sampler = ParentBased(
    TraceIdRatioBased(0.1 if os.getenv("ENV") == "production" else 1.0)
)

trace_provider = TracerProvider(resource=resource, sampler=sampler)
trace_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(trace_provider)

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(),
    export_interval_millis=60000,
)
metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)

@atexit.register
def shutdown_telemetry() -> None:
    trace_provider.shutdown()
    metric_provider.shutdown()
```

## 3. Instrument Flask app

**`src/app.py`**

```python
from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from instrumentation import trace_provider  # noqa: F401

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/orders")
def create_order():
    tracer = trace.get_tracer("order-service")

    with tracer.start_as_current_span("order.process") as span:
        payload = request.get_json()
        span.set_attribute("order.id", payload["order_id"])

        with tracer.start_as_current_span("payment.capture") as child_span:
            child_span.set_attribute("payment.provider", "stripe")

        return jsonify(
            {
                "order_id": payload["order_id"],
                "payment_id": "pay_123",
            }
        ), 201
```

## 4. Correlate logs with the current span

```python
from opentelemetry import trace

def current_trace_fields() -> dict[str, str | None]:
    ctx = trace.get_current_span().get_span_context()

    if not ctx.is_valid:
        return {"trace_id": None, "span_id": None}

    return {
        "trace_id": format(ctx.trace_id, "032x"),
        "span_id": format(ctx.span_id, "016x"),
    }
```

## 5. Environment variables

```bash
OTEL_SERVICE_NAME=order-api
SERVICE_VERSION=1.0.0
ENV=production

OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

PORT=3000
```

## 6. Operational notes

- Prefer `app -> Collector -> backend` in production.
- Use framework auto-instrumentation for HTTP spans and outbound requests. Add manual spans around business workflows, jobs, and queue consumers.
- Keep trace and request identifiers in logs, but do not promote them to labels or metric dimensions.
- Validate library compatibility at implementation time. Python OTel package releases move independently across API, SDK, and instrumentation packages.
