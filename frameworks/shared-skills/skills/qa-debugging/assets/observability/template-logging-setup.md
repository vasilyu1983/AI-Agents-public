# Production Logging Setup Template

Copy-paste configurations for structured logging across languages and frameworks.

---

## Node.js with Pino

### Installation

```bash
npm install pino pino-pretty
```

### Basic Configuration

```javascript
// logger.js
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => {
      return { level: label.toUpperCase() };
    },
    bindings: (bindings) => {
      return {
        pid: bindings.pid,
        host: bindings.hostname,
        service: process.env.SERVICE_NAME || 'api-service',
        environment: process.env.NODE_ENV || 'development'
      };
    }
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  serializers: {
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
    err: pino.stdSerializers.err
  },
  redact: {
    paths: ['req.headers.authorization', 'req.headers.cookie', 'password', 'token', 'apiKey'],
    censor: '[REDACTED]'
  }
});

module.exports = logger;
```

### Development Pretty Printing

```javascript
// logger.js (development)
const logger = pino({
  transport: process.env.NODE_ENV === 'development' ? {
    target: 'pino-pretty',
    options: {
      colorize: true,
      translateTime: 'HH:MM:ss Z',
      ignore: 'pid,hostname'
    }
  } : undefined
});
```

### Express Middleware

```javascript
// middleware/logging.js
const { v4: uuidv4 } = require('uuid');
const logger = require('./logger');

function loggingMiddleware(req, res, next) {
  const requestId = req.headers['x-request-id'] || uuidv4();
  const start = Date.now();

  // Attach request-scoped logger
  req.log = logger.child({
    requestId,
    method: req.method,
    path: req.path,
    userId: req.user?.id
  });

  // Log request
  req.log.info({ query: req.query }, 'Incoming request');

  // Log response
  res.on('finish', () => {
    const duration = Date.now() - start;
    const level = res.statusCode >= 500 ? 'error' :
                  res.statusCode >= 400 ? 'warn' : 'info';

    req.log[level]({
      statusCode: res.statusCode,
      duration,
      contentLength: res.get('content-length')
    }, 'Request completed');
  });

  // Set response header
  res.setHeader('x-request-id', requestId);
  next();
}

module.exports = loggingMiddleware;
```

### Usage in Application

```javascript
// app.js
const express = require('express');
const logger = require('./logger');
const loggingMiddleware = require('./middleware/logging');

const app = express();

// Apply logging middleware
app.use(loggingMiddleware);

// Route handlers
app.get('/api/orders', async (req, res) => {
  try {
    req.log.info('Fetching orders');
    const orders = await getOrders(req.query);

    req.log.info({ count: orders.length }, 'Orders retrieved');
    res.json(orders);
  } catch (error) {
    req.log.error({ error, query: req.query }, 'Failed to fetch orders');
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Error handler
app.use((err, req, res, next) => {
  req.log.error({ err }, 'Unhandled error');
  res.status(500).json({ error: 'Internal server error' });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, starting graceful shutdown');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

const server = app.listen(3000, () => {
  logger.info({ port: 3000 }, 'Server started');
});
```

---

## Python with structlog

### Installation

```bash
pip install structlog
```

### Basic Configuration

```python
# logging_config.py
import logging
import structlog
from structlog.processors import JSONRenderer

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
    )

# Call at app startup
configure_logging()
logger = structlog.get_logger()
```

### Flask Middleware

```python
# middleware/logging.py
import time
import uuid
from flask import g, request
import structlog

logger = structlog.get_logger()

def setup_request_logging(app):
    @app.before_request
    def before_request():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.start_time = time.time()
        g.logger = logger.bind(
            request_id=g.request_id,
            method=request.method,
            path=request.path,
            user_id=getattr(g, 'user_id', None)
        )
        g.logger.info("request_started")

    @app.after_request
    def after_request(response):
        duration = (time.time() - g.start_time) * 1000
        level = 'error' if response.status_code >= 500 else \
                'warning' if response.status_code >= 400 else 'info'

        getattr(g.logger, level)(
            "request_completed",
            status_code=response.status_code,
            duration_ms=round(duration, 2),
            content_length=response.content_length
        )

        response.headers['X-Request-ID'] = g.request_id
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        g.logger.error("unhandled_exception", exc_info=True)
        return {"error": "Internal server error"}, 500
```

### Usage in Application

```python
# app.py
from flask import Flask, g
from logging_config import configure_logging
from middleware.logging import setup_request_logging

app = Flask(__name__)
configure_logging()
setup_request_logging(app)

@app.route('/api/orders')
def get_orders():
    try:
        g.logger.info("fetching_orders", user_id=g.user_id)
        orders = fetch_orders()

        g.logger.info("orders_retrieved", count=len(orders))
        return {"orders": orders}
    except Exception as e:
        g.logger.error("failed_to_fetch_orders",
            error=str(e),
            exc_info=True
        )
        return {"error": "Internal server error"}, 500

if __name__ == '__main__':
    logger.info("server_starting", port=5000)
    app.run(port=5000)
```

---

## Go with zap

### Installation

```bash
go get -u go.uber.org/zap
```

### Basic Configuration

```go
// logger/logger.go
package logger

import (
    "os"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

var Log *zap.Logger

func Initialize() error {
    config := zap.NewProductionConfig()

    // Custom time encoding
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

    // Set log level from environment
    level := os.Getenv("LOG_LEVEL")
    if level != "" {
        config.Level.UnmarshalText([]byte(level))
    }

    // Build logger
    logger, err := config.Build(
        zap.Fields(
            zap.String("service", os.Getenv("SERVICE_NAME")),
            zap.String("environment", os.Getenv("ENVIRONMENT")),
        ),
    )
    if err != nil {
        return err
    }

    Log = logger
    return nil
}

func Sync() {
    _ = Log.Sync()
}
```

### HTTP Middleware

```go
// middleware/logging.go
package middleware

import (
    "context"
    "net/http"
    "time"

    "github.com/google/uuid"
    "go.uber.org/zap"
)

type key int

const (
    loggerKey key = iota
    requestIDKey
)

func Logging(logger *zap.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()

            // Generate or extract request ID
            requestID := r.Header.Get("X-Request-ID")
            if requestID == "" {
                requestID = uuid.New().String()
            }

            // Create request-scoped logger
            reqLogger := logger.With(
                zap.String("requestId", requestID),
                zap.String("method", r.Method),
                zap.String("path", r.URL.Path),
            )

            // Add to context
            ctx := context.WithValue(r.Context(), loggerKey, reqLogger)
            ctx = context.WithValue(ctx, requestIDKey, requestID)

            // Wrap response writer to capture status code
            wrapped := &statusWriter{ResponseWriter: w, status: 200}

            // Log request
            reqLogger.Info("request started")

            // Call next handler
            next.ServeHTTP(wrapped, r.WithContext(ctx))

            // Log response
            duration := time.Since(start).Milliseconds()
            level := zap.InfoLevel
            if wrapped.status >= 500 {
                level = zap.ErrorLevel
            } else if wrapped.status >= 400 {
                level = zap.WarnLevel
            }

            reqLogger.Log(level, "request completed",
                zap.Int("statusCode", wrapped.status),
                zap.Int64("duration", duration),
            )

            // Set response header
            w.Header().Set("X-Request-ID", requestID)
        })
    }
}

// Helper to capture status code
type statusWriter struct {
    http.ResponseWriter
    status int
}

func (w *statusWriter) WriteHeader(code int) {
    w.status = code
    w.ResponseWriter.WriteHeader(code)
}

// GetLogger extracts logger from context
func GetLogger(ctx context.Context) *zap.Logger {
    if logger, ok := ctx.Value(loggerKey).(*zap.Logger); ok {
        return logger
    }
    return zap.L()
}
```

### Usage in Application

```go
// main.go
package main

import (
    "context"
    "net/http"
    "os"
    "os/signal"
    "time"

    "github.com/gorilla/mux"
    "go.uber.org/zap"

    "myapp/logger"
    "myapp/middleware"
)

func main() {
    // Initialize logger
    if err := logger.Initialize(); err != nil {
        panic(err)
    }
    defer logger.Sync()

    logger.Log.Info("starting server", zap.Int("port", 8080))

    // Setup router
    r := mux.NewRouter()
    r.Use(middleware.Logging(logger.Log))

    // Routes
    r.HandleFunc("/api/orders", getOrdersHandler).Methods("GET")

    // Server
    srv := &http.Server{
        Addr:    ":8080",
        Handler: r,
    }

    // Graceful shutdown
    go func() {
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            logger.Log.Fatal("server failed", zap.Error(err))
        }
    }()

    // Wait for interrupt signal
    stop := make(chan os.Signal, 1)
    signal.Notify(stop, os.Interrupt)
    <-stop

    logger.Log.Info("shutting down server")
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        logger.Log.Error("shutdown error", zap.Error(err))
    }

    logger.Log.Info("server stopped")
}

func getOrdersHandler(w http.ResponseWriter, r *http.Request) {
    log := middleware.GetLogger(r.Context())

    log.Info("fetching orders")

    // Business logic...
    orders := []string{"order1", "order2"}

    log.Info("orders retrieved", zap.Int("count", len(orders)))
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"orders": ["order1", "order2"]}`))
}
```

---

## Docker Compose Logging

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    image: myapp:latest
    environment:
      LOG_LEVEL: info
      SERVICE_NAME: api-service
      NODE_ENV: production
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service,environment"
    labels:
      service: "api-service"
      environment: "production"

  # Log aggregation (optional)
  fluentd:
    image: fluent/fluentd:latest
    volumes:
      - ./fluentd/conf:/fluentd/etc
    ports:
      - "24224:24224"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
```

---

## Log Shipping (Filebeat)

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/app/*.log
  json.keys_under_root: true
  json.add_error_key: true
  fields:
    service: api-service
    environment: production

output.elasticsearch:
  hosts: ["http://elasticsearch:9200"]
  index: "app-logs-%{+yyyy.MM.dd}"

setup.template.name: "app-logs"
setup.template.pattern: "app-logs-*"
```

---

## Environment Variables

```bash
# .env.production
LOG_LEVEL=info
SERVICE_NAME=api-service
NODE_ENV=production
ENABLE_REQUEST_LOGGING=true
LOG_FORMAT=json
```

```bash
# .env.development
LOG_LEVEL=debug
SERVICE_NAME=api-service
NODE_ENV=development
ENABLE_REQUEST_LOGGING=true
LOG_FORMAT=pretty
```

---

## AWS CloudWatch Integration

### Node.js (Winston CloudWatch)

```javascript
const winston = require('winston');
const CloudWatchTransport = require('winston-cloudwatch');

const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [
    new CloudWatchTransport({
      logGroupName: '/aws/app/api-service',
      logStreamName: () => {
        const date = new Date().toISOString().split('T')[0];
        return `${date}-${process.env.HOSTNAME}`;
      },
      awsRegion: 'us-east-1',
      jsonMessage: true
    })
  ]
});
```

### Python (watchtower)

```python
import logging
import watchtower

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group='/aws/app/api-service',
    stream_name='production',
    use_queues=False
))
logger.setLevel(logging.INFO)
```

---

## Testing Logging Configuration

```javascript
// test/logging.test.js
const logger = require('../logger');

describe('Logging', () => {
  test('logs at correct levels', () => {
    const spy = jest.spyOn(logger, 'info');

    logger.info({ foo: 'bar' }, 'Test message');

    expect(spy).toHaveBeenCalledWith(
      expect.objectContaining({ foo: 'bar' }),
      'Test message'
    );
  });

  test('redacts sensitive fields', () => {
    const spy = jest.spyOn(logger, 'info');

    logger.info({ password: 'secret123' }, 'User login');

    const call = spy.mock.calls[0][0];
    expect(call.password).toBe('[REDACTED]');
  });
});
```

---

## Checklist: Production Logging Setup

```
[ ] Structured logging library installed and configured
[ ] Log level configurable via environment variable
[ ] Request ID generation and propagation
[ ] Request/response logging middleware
[ ] Error logging with stack traces
[ ] Sensitive data redaction (passwords, tokens, PII)
[ ] Service and environment metadata
[ ] JSON formatting for production
[ ] Pretty formatting for development
[ ] Log rotation configured (if file-based)
[ ] Log shipping to aggregation system
[ ] Performance tested (no blocking I/O)
[ ] Graceful shutdown handling
[ ] Health check endpoint
[ ] Tests for logging functionality
```

---

> **Pro Tip**: Start with these templates and customize based on your specific requirements. Always test logging configuration before deploying to production.
