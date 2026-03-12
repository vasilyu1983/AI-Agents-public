# Logging Utilities

Centralized patterns for structured logging with OpenTelemetry integration.

**Updated**: December 2025
**Node.js**: 24 LTS | **Python**: 3.14+ | **Go**: 1.25+

---

## File Structure

```text
src/
├── utils/
│   └── logger.ts            # Logger singleton with OTel
└── middleware/
    └── request-logger.ts    # HTTP request logging
```

---

## TypeScript/Node.js (pino v9 + OpenTelemetry)

### Dependencies

```bash
npm install pino@^9 pino-pretty@^13 @opentelemetry/api@^1.9
npm install -D @types/pino
```

### Logger Singleton (`src/utils/logger.ts`)

```typescript
import pino, { Logger, LoggerOptions } from 'pino';
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import { config } from '@/config';

// ============================================
// PINO v9 + OPENTELEMETRY INTEGRATION
// ============================================

const formatters: LoggerOptions['formatters'] = {
  level: (label) => ({ level: label.toUpperCase() }),
  bindings: (bindings) => ({
    pid: bindings.pid,
    hostname: bindings.hostname,
    service: config.SERVICE_NAME || 'api',
    environment: config.NODE_ENV,
  }),
  log: (obj) => {
    // Inject trace context into every log
    const span = trace.getActiveSpan();
    if (span) {
      const spanContext = span.spanContext();
      return {
        ...obj,
        trace_id: spanContext.traceId,
        span_id: spanContext.spanId,
        trace_flags: spanContext.traceFlags,
      };
    }
    return obj;
  },
};

// Create single logger instance
export const logger: Logger = pino({
  level: config.LOG_LEVEL || 'info',
  formatters,
  timestamp: pino.stdTimeFunctions.isoTime,
  // Redact sensitive fields
  redact: {
    paths: ['password', 'token', 'authorization', 'cookie', 'secret', '*.password', '*.token'],
    censor: '[REDACTED]',
  },
  // Pretty print in development
  transport:
    config.NODE_ENV !== 'production'
      ? {
          target: 'pino-pretty',
          options: {
            colorize: true,
            translateTime: 'SYS:standard',
            ignore: 'pid,hostname',
          },
        }
      : undefined,
});

// Child logger factory for specific contexts
export const createLogger = (context: string): Logger => {
  return logger.child({ context });
};

// Log with span - automatically creates span and logs
export const logWithSpan = async <T>(
  name: string,
  fn: () => Promise<T>,
  logData?: Record<string, unknown>
): Promise<T> => {
  const tracer = trace.getTracer('logger');

  return tracer.startActiveSpan(name, async (span) => {
    const startTime = Date.now();
    logger.info({ ...logData, spanName: name }, `${name} started`);

    try {
      const result = await fn();
      const duration = Date.now() - startTime;

      span.setStatus({ code: SpanStatusCode.OK });
      logger.info({ ...logData, spanName: name, duration }, `${name} completed`);

      return result;
    } catch (error) {
      const duration = Date.now() - startTime;

      span.setStatus({ code: SpanStatusCode.ERROR, message: String(error) });
      logger.error({ ...logData, spanName: name, duration, error: String(error) }, `${name} failed`);

      throw error;
    } finally {
      span.end();
    }
  });
};
```

### Request Logger Middleware (`src/middleware/request-logger.ts`)

```typescript
import { Request, Response, NextFunction } from 'express';
import { trace, SpanStatusCode } from '@opentelemetry/api';
import { logger } from '@/utils/logger';

export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const tracer = trace.getTracer('http');
  const start = Date.now();

  // Get or create request ID (prefer W3C trace ID)
  const span = trace.getActiveSpan();
  const requestId = span?.spanContext().traceId
    || req.headers['x-request-id'] as string
    || crypto.randomUUID();

  req.id = requestId;
  res.setHeader('x-request-id', requestId);

  // Create child logger with request context
  req.log = logger.child({
    requestId,
    method: req.method,
    path: req.path,
    userAgent: req.headers['user-agent'],
  });

  // Log on response finish
  res.on('finish', () => {
    const duration = Date.now() - start;
    const level = res.statusCode >= 500 ? 'error' : res.statusCode >= 400 ? 'warn' : 'info';

    req.log[level]({
      statusCode: res.statusCode,
      duration,
      contentLength: res.get('content-length'),
    }, `${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
  });

  next();
};

// Extend Express types
declare global {
  namespace Express {
    interface Request {
      id: string;
      log: typeof logger;
    }
  }
}
```

### Usage Examples

```typescript
import { logger, createLogger, logWithSpan } from '@/utils/logger';

// Basic logging (trace context auto-injected)
logger.info('Server started');
logger.error({ err }, 'Database connection failed');
logger.warn({ userId }, 'Invalid login attempt');

// With structured data
logger.info({
  userId: user.id,
  action: 'login',
  ip: req.ip,
}, 'User logged in');

// Child logger for specific module
const authLogger = createLogger('auth');
authLogger.info({ email }, 'Login attempt');

// Log with automatic span creation
const user = await logWithSpan(
  'fetchUser',
  () => db.user.findUnique({ where: { id } }),
  { userId: id }
);

// In request handlers (using req.log)
app.get('/users/:id', async (req, res) => {
  req.log.info({ userId: req.params.id }, 'Fetching user');
  const user = await getUser(req.params.id);
  req.log.info('User fetched');
  res.json(user);
});
```

---

## Python (structlog + OpenTelemetry)

### Dependencies

```bash
pip install structlog>=24.4 opentelemetry-api>=1.29
```

### Logger Setup (`src/utils/logger.py`)

```python
import logging
from typing import Any

import structlog
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from src.config.settings import settings


def add_trace_context(
    logger: structlog.typing.WrappedLogger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Processor that adds OpenTelemetry trace context to every log."""
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def configure_logging() -> None:
    """Configure structlog with OpenTelemetry integration."""

    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_trace_context,  # Add OTel trace context
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_development:
        structlog.configure(
            processors=shared_processors + [
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                logging.getLevelName(settings.log_level)
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        structlog.configure(
            processors=shared_processors + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                logging.getLevelName(settings.log_level)
            ),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a logger instance with optional context name."""
    log = structlog.get_logger()
    if name:
        return log.bind(context=name)
    return log


# Module-level logger
logger = get_logger()


# Log with span helper
async def log_with_span[T](
    name: str,
    fn,
    **log_data: Any,
) -> T:
    """Execute function with automatic span and logging."""
    tracer = trace.get_tracer("logger")

    with tracer.start_as_current_span(name) as span:
        logger.info(f"{name} started", **log_data)
        try:
            result = await fn()
            span.set_status(Status(StatusCode.OK))
            logger.info(f"{name} completed", **log_data)
            return result
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(f"{name} failed", error=str(e), **log_data)
            raise
```

### Request Logging Middleware (`src/middleware/logging.py`)

```python
import time
import uuid

import structlog
from fastapi import Request
from opentelemetry import trace
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.logger import get_logger

logger = get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Prefer OTel trace ID, fallback to header or generate
        span = trace.get_current_span()
        if span.is_recording():
            request_id = format(span.get_span_context().trace_id, "032x")
        else:
            request_id = request.headers.get("x-request-id", str(uuid.uuid4()))

        start_time = time.perf_counter()

        with structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        ):
            response = await call_next(request)

            duration_ms = (time.perf_counter() - start_time) * 1000

            log_method = (
                logger.error if response.status_code >= 500
                else logger.warning if response.status_code >= 400
                else logger.info
            )
            log_method(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            response.headers["x-request-id"] = request_id
            return response
```

### Usage

```python
from src.utils.logger import logger, get_logger, log_with_span

# Basic logging (trace context auto-injected)
logger.info("Server started", port=8000)
logger.error("Database connection failed", error=str(e))

# With context
logger.info("User logged in", user_id=user.id, ip=request.client.host)

# Module-specific logger
auth_logger = get_logger("auth")
auth_logger.info("Login attempt", email=email)

# Log with automatic span
user = await log_with_span("fetch_user", lambda: db.get_user(user_id), user_id=user_id)
```

---

## Go (zap + OpenTelemetry)

### Dependencies

```bash
go get go.uber.org/zap
go get go.opentelemetry.io/otel
go get go.opentelemetry.io/contrib/bridges/otelzap
```

### Logger Setup (`internal/utils/logger.go`)

```go
package utils

import (
    "context"
    "os"

    "go.opentelemetry.io/otel/trace"
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

var Logger *zap.Logger

func InitLogger(env string, level string) error {
    var config zap.Config

    if env == "production" {
        config = zap.NewProductionConfig()
        config.EncoderConfig.TimeKey = "timestamp"
        config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
    } else {
        config = zap.NewDevelopmentConfig()
        config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
    }

    // Set log level
    logLevel := zap.InfoLevel
    switch level {
    case "debug":
        logLevel = zap.DebugLevel
    case "warn":
        logLevel = zap.WarnLevel
    case "error":
        logLevel = zap.ErrorLevel
    }
    config.Level = zap.NewAtomicLevelAt(logLevel)

    var err error
    Logger, err = config.Build(
        zap.AddCallerSkip(1),
        zap.Fields(
            zap.String("service", os.Getenv("SERVICE_NAME")),
            zap.String("environment", env),
        ),
    )
    return err
}

// WithTraceContext adds OpenTelemetry trace context to logger
func WithTraceContext(ctx context.Context) *zap.Logger {
    span := trace.SpanFromContext(ctx)
    if !span.SpanContext().IsValid() {
        return Logger
    }

    sc := span.SpanContext()
    return Logger.With(
        zap.String("trace_id", sc.TraceID().String()),
        zap.String("span_id", sc.SpanID().String()),
    )
}

// Info logs with trace context
func Info(ctx context.Context, msg string, fields ...zap.Field) {
    WithTraceContext(ctx).Info(msg, fields...)
}

// Error logs with trace context
func Error(ctx context.Context, msg string, fields ...zap.Field) {
    WithTraceContext(ctx).Error(msg, fields...)
}

// Warn logs with trace context
func Warn(ctx context.Context, msg string, fields ...zap.Field) {
    WithTraceContext(ctx).Warn(msg, fields...)
}

// Debug logs with trace context
func Debug(ctx context.Context, msg string, fields ...zap.Field) {
    WithTraceContext(ctx).Debug(msg, fields...)
}

// With creates child logger with additional fields
func With(fields ...zap.Field) *zap.Logger {
    return Logger.With(fields...)
}
```

### Request Logger Middleware (`internal/middleware/logger.go`)

```go
package middleware

import (
    "time"

    "github.com/gofiber/fiber/v2"
    "go.opentelemetry.io/otel/trace"
    "go.uber.org/zap"
    "myapp/internal/utils"
)

func RequestLogger() fiber.Handler {
    return func(c *fiber.Ctx) error {
        start := time.Now()
        ctx := c.UserContext()

        // Get trace ID from OTel span or generate
        var requestID string
        span := trace.SpanFromContext(ctx)
        if span.SpanContext().IsValid() {
            requestID = span.SpanContext().TraceID().String()
        } else {
            requestID = c.Get("X-Request-ID")
            if requestID == "" {
                requestID = c.Locals("requestid").(string)
            }
        }
        c.Set("X-Request-ID", requestID)

        // Create request-scoped logger with trace context
        log := utils.WithTraceContext(ctx).With(
            zap.String("request_id", requestID),
            zap.String("method", c.Method()),
            zap.String("path", c.Path()),
        )
        c.Locals("logger", log)

        err := c.Next()

        duration := time.Since(start)
        status := c.Response().StatusCode()

        logFunc := log.Info
        if status >= 500 {
            logFunc = log.Error
        } else if status >= 400 {
            logFunc = log.Warn
        }

        logFunc("Request completed",
            zap.Int("status", status),
            zap.Duration("duration", duration),
        )

        return err
    }
}

func GetLogger(c *fiber.Ctx) *zap.Logger {
    if log, ok := c.Locals("logger").(*zap.Logger); ok {
        return log
    }
    return utils.Logger
}
```

### Usage

```go
import (
    "context"

    "go.uber.org/zap"
    "myapp/internal/utils"
    "myapp/internal/middleware"
)

func main() {
    utils.InitLogger("development", "debug")
    defer utils.Logger.Sync()

    ctx := context.Background()

    // Logging with trace context (auto-injected)
    utils.Info(ctx, "Server started", zap.Int("port", 3000))
    utils.Error(ctx, "Database error", zap.Error(err))

    // With structured data
    utils.Info(ctx, "User logged in",
        zap.String("user_id", user.ID),
        zap.String("ip", c.IP()),
    )

    // In handlers
    app.Get("/users/:id", func(c *fiber.Ctx) error {
        log := middleware.GetLogger(c)
        log.Info("Fetching user", zap.String("user_id", c.Params("id")))
        // ...
    })
}
```

---

## Log Levels Guide

| Level | When to Use |
|-------|-------------|
| `debug` | Detailed diagnostic info (dev only) |
| `info` | Normal operations, business events |
| `warn` | Unexpected but recoverable situations |
| `error` | Failures requiring attention |

### What to Log

```typescript
// Business events
logger.info({ orderId, amount }, 'Order placed');

// Security events
logger.warn({ userId, ip }, 'Failed login attempt');

// Errors with context (no stack traces in API responses!)
logger.error({ err, userId, action }, 'Payment processing failed');

// Performance metrics
logger.info({ duration, query }, 'Slow query detected');
```

### What NOT to Log

```typescript
// NEVER: Sensitive data
logger.info({ password, ssn, creditCard }, 'User data');

// NEVER: High-frequency debug in production
logger.debug('Entering function...');

// AVOID: Duplicate logs
logger.info('Start processing');
logger.info('Processing...');
logger.info('Still processing...');  // Use one log with duration
```

---

## Sensitive Data Redaction

```typescript
// Pino redaction config (in logger setup)
redact: {
  paths: [
    'password',
    'token',
    'authorization',
    'cookie',
    'secret',
    '*.password',
    '*.token',
    'headers.authorization',
    'body.password',
    'body.creditCard',
  ],
  censor: '[REDACTED]',
}
```

---

## Anti-Pattern: Scattered Logger Creation

```typescript
// BAD - New logger in every file
// user.service.ts
import pino from 'pino';
const logger = pino({ level: 'info' });

// order.service.ts
import pino from 'pino';
const logger = pino({ level: 'debug' });  // Inconsistent!

// GOOD - Import singleton
import { logger } from '@/utils/logger';
```

---

## References

- [pino v9 Documentation](https://getpino.io)
- [structlog Documentation](https://www.structlog.org)
- [zap Documentation](https://pkg.go.dev/go.uber.org/zap)
- [OpenTelemetry Logging](https://opentelemetry.io/docs/specs/otel/logs/)
