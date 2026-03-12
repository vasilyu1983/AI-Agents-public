# OpenTelemetry Python Setup Template

Complete setup template for instrumenting a Python/Flask application with OpenTelemetry.

## Project Structure

```
my-app/
  src/
    instrumentation.py       # OpenTelemetry setup
    app.py                   # Flask application
    services/
      order_service.py
    routes/
      orders.py
  requirements.txt
  .env
```

## 1. Install Dependencies

**`requirements.txt`**:

```txt
flask==3.0.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-flask==0.42b0
opentelemetry-instrumentation-requests==0.42b0
opentelemetry-instrumentation-sqlalchemy==0.42b0
opentelemetry-exporter-otlp-proto-http==1.21.0
python-dotenv==1.0.0
```

```bash
pip install -r requirements.txt
```

---

## 2. Create Instrumentation File

**`src/instrumentation.py`**:

```python
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

# Resource attributes (service metadata)
resource = Resource.create({
    "service.name": os.getenv("SERVICE_NAME", "my-service"),
    "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
    "deployment.environment": os.getenv("ENV", "development")
})

# Sampling strategy
sampling_rate = 0.1 if os.getenv("ENV") == "production" else 1.0
sampler = ParentBasedTraceIdRatio(sampling_rate)

# Configure tracing
trace_provider = TracerProvider(resource=resource, sampler=sampler)
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
    export_interval_millis=60000  # Export every 60 seconds
)
metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)

# Graceful shutdown
import atexit

def shutdown_telemetry():
    trace_provider.shutdown()
    metric_provider.shutdown()

atexit.register(shutdown_telemetry)
```

---

## 3. Create Flask Application

**`src/app.py`**:

```python
from flask import Flask, request, jsonify
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry import trace
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import instrumentation FIRST
from instrumentation import trace_provider

# Create Flask app
app = Flask(__name__)

# Instrument Flask (auto-traces all routes)
FlaskInstrumentor().instrument_app(app)

# Import routes
from routes.orders import orders_bp
app.register_blueprint(orders_bp, url_prefix='/api/orders')

# Health check
@app.route('/health')
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
```

---

## 4. Add Custom Spans to Business Logic

**`src/services/order_service.py`**:

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

class OrderService:
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)

    def process_order(self, order_id):
        with self.tracer.start_as_current_span("process-order") as span:
            # Add attributes
            span.set_attribute("order.id", order_id)
            span.set_attribute("order.source", "web")

            try:
                # Validate order
                span.add_event("validation-started")
                is_valid = self._validate_order(order_id)
                span.add_event("validation-completed", {"is_valid": is_valid})

                if not is_valid:
                    span.set_status(Status(StatusCode.ERROR, "Invalid order"))
                    raise ValueError("Invalid order")

                # Process payment
                span.add_event("payment-started")
                payment = self._process_payment(order_id)
                span.set_attribute("payment.id", payment["id"])
                span.set_attribute("payment.amount", payment["amount"])
                span.add_event("payment-completed")

                # Fulfill order
                span.add_event("fulfillment-started")
                self._fulfill_order(order_id)
                span.add_event("fulfillment-completed")

                span.set_status(Status(StatusCode.OK))
                return {
                    "success": True,
                    "order_id": order_id,
                    "payment_id": payment["id"]
                }

            except Exception as error:
                # Record exception
                span.record_exception(error)
                span.set_status(Status(StatusCode.ERROR, str(error)))
                raise

    def _validate_order(self, order_id):
        # Validation logic
        return True

    def _process_payment(self, order_id):
        # Payment logic
        return {"id": "pay_123", "amount": 99.99}

    def _fulfill_order(self, order_id):
        # Fulfillment logic
        pass

order_service = OrderService()
```

---

## 5. Route with Tracing

**`src/routes/orders.py`**:

```python
from flask import Blueprint, request, jsonify
from opentelemetry import trace
from services.order_service import order_service

orders_bp = Blueprint('orders', __name__)
tracer = trace.get_tracer(__name__)

@orders_bp.route('/', methods=['POST'])
def create_order():
    with tracer.start_as_current_span("POST /api/orders") as span:
        span.set_attribute("http.method", "POST")
        span.set_attribute("http.route", "/api/orders")
        span.set_attribute("user.id", request.headers.get("X-User-ID", "anonymous"))

        try:
            data = request.get_json()
            order = order_service.process_order(data.get("order_id"))

            span.set_attribute("http.status_code", 201)
            return jsonify(order), 201

        except Exception as error:
            span.record_exception(error)
            span.set_attribute("http.status_code", 500)
            return jsonify({"error": str(error)}), 500
```

---

## 6. Environment Variables

**`.env`**:

```bash
# Service metadata
SERVICE_NAME=order-api
SERVICE_VERSION=1.0.0
ENV=production

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
      - ENV=development
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
    depends_on:
      - jaeger
```

**`Dockerfile`**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "src/app.py"]
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
        - name: ENV
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
python src/app.py

# Make requests
curl -X POST http://localhost:3000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id": "order-123"}'

# View traces in Jaeger UI
open http://localhost:16686
```

---

## 10. Advanced: Database Instrumentation

**Install SQLAlchemy instrumentation:**

```bash
pip install opentelemetry-instrumentation-sqlalchemy
```

**`src/database.py`**:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Create engine
engine = create_engine('postgresql://user:password@localhost/dbname')

# Instrument SQLAlchemy
SQLAlchemyInstrumentor().instrument(engine=engine)

# Create session
Session = sessionmaker(bind=engine)
```

**Usage:**

```python
from database import Session

with tracer.start_as_current_span("fetch-orders"):
    session = Session()
    orders = session.query(Order).filter_by(status='pending').all()
    # Automatically traced!
```

---

## 11. Debugging

**Enable debug logging:**

```python
# Add to instrumentation.py
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)
```

**Common issues:**

1. **No traces appearing:**
   - Check OTEL_EXPORTER_OTLP_ENDPOINT is reachable
   - Verify instrumentation.py imports before Flask
   - Check sampling rate (set to 1.0 for testing)

2. **Import errors:**
   - Ensure all opentelemetry packages are installed
   - Check version compatibility

3. **High overhead:**
   - Reduce sampling rate (0.01 = 1%)
   - Use BatchSpanProcessor (default)

---

## Next Steps

1. **Add structured logging** with trace correlation
2. **Set up metrics** (custom counters, gauges, histograms)
3. **Configure SLOs** and alerting
4. **Integrate with APM** (Datadog, New Relic, etc.)

Related topics:

- Structured Logging with trace correlation
- Prometheus Metrics configuration
- SLO Definition patterns
