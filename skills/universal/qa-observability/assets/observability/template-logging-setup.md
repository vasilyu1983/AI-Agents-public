# Production Logging Setup Template

Copy-paste configurations for structured, correlated logging. Prefer stdout or stderr plus a collector pipeline so logs remain portable across platforms.

---

## Logging defaults

- Emit structured JSON in production.
- Include `service`, `environment`, `request_id`, `trace_id`, and `span_id` on request-scoped logs.
- Keep unique IDs searchable in log bodies, not label sets.
- Redact secrets and PII before logs leave the process.
- Reuse the active trace context when available instead of parsing `traceparent` manually.

---

## Node.js with Pino

### Installation

```bash
npm install pino uuid
```

### Logger configuration

```javascript
// logger.js
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  timestamp: pino.stdTimeFunctions.isoTime,
  base: {
    service: process.env.SERVICE_NAME || 'api-service',
    environment: process.env.NODE_ENV || 'development',
  },
  redact: {
    paths: [
      'req.headers.authorization',
      'req.headers.cookie',
      'password',
      'token',
      'apiKey',
    ],
    censor: '[REDACTED]',
  },
});

module.exports = logger;
```

### Express correlation middleware

```javascript
// middleware/logging.js
const { randomUUID } = require('crypto');
const { trace } = require('@opentelemetry/api');
const logger = require('../logger');

function loggingMiddleware(req, res, next) {
  const requestId = req.headers['x-request-id'] || randomUUID();
  const start = Date.now();
  const span = trace.getActiveSpan();
  const spanContext = span?.spanContext();

  req.log = logger.child({
    request_id: requestId,
    trace_id: spanContext?.traceId,
    span_id: spanContext?.spanId,
    http_method: req.method,
    url_path: req.path,
  });

  res.setHeader('x-request-id', requestId);
  req.log.info({ query: req.query }, 'request.started');

  res.on('finish', () => {
    req.log.info(
      {
        status_code: res.statusCode,
        duration_ms: Date.now() - start,
        content_length: res.getHeader('content-length'),
      },
      'request.completed'
    );
  });

  next();
}

module.exports = loggingMiddleware;
```

---

## Python with structlog

### Installation

```bash
pip install structlog
```

### Logger configuration

```python
# logging_config.py
import logging
import structlog

def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(level=logging.INFO, format="%(message)s")
```

### Flask request middleware

```python
# middleware/logging.py
import time
import uuid
import structlog
from flask import Flask, g, request
from opentelemetry import trace

logger = structlog.get_logger()

def setup_request_logging(app: Flask) -> None:
    @app.before_request
    def before_request():
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        span = trace.get_current_span()
        ctx = span.get_span_context()

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            trace_id=format(ctx.trace_id, "032x") if ctx.is_valid else None,
            span_id=format(ctx.span_id, "016x") if ctx.is_valid else None,
        )

        g.request_id = request_id
        g.started_at = time.time()
        g.log = logger.bind(
            path=request.path,
            method=request.method,
        )
        g.log.info("request.started")

    @app.after_request
    def after_request(response):
        g.log.info(
            "request.completed",
            status_code=response.status_code,
            duration_ms=round((time.time() - g.started_at) * 1000, 2),
            content_length=response.content_length,
        )
        response.headers["X-Request-ID"] = g.request_id
        return response
```

---

## Collector-side guidance

- Parse JSON once in the collector or agent layer.
- Promote only low-cardinality routing fields such as `service`, `environment`, and `level` to labels.
- Keep `trace_id`, `span_id`, `request_id`, user IDs, and order IDs searchable in the log payload, not indexed as labels.
- Drop health checks and known-noisy debug logs before shipping them to long-retention storage.
