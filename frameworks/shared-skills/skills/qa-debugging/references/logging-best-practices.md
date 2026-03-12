# Logging Best Practices - Production-Grade Strategies

This guide provides actionable logging patterns for production systems with modern structured logging approaches.

## Contents

- [Log Level Hierarchy (Standard)](#log-level-hierarchy-standard)
- [Structured Logging (JSON Format)](#structured-logging-json-format)
- [Logging Implementations by Language](#logging-implementations-by-language)
- [What to Log (DOs and DON'Ts)](#what-to-log-dos-and-donts)
- [Request ID Propagation (Distributed Tracing)](#request-id-propagation-distributed-tracing)
- [Log Sampling (High-Volume Systems)](#log-sampling-high-volume-systems)
- [Performance Considerations](#performance-considerations)
- [Log Aggregation & Search](#log-aggregation--search)
- [Log Retention Policies](#log-retention-policies)
- [Checklist: Production Logging Setup](#checklist-production-logging-setup)
- [Common Mistakes](#common-mistakes)

---

## Log Level Hierarchy (Standard)

```
FATAL   - System crash, unrecoverable error (process termination)
ERROR   - Operation failed, requires attention
WARN    - Unexpected situation, degraded functionality
INFO    - Important business events (user actions, state changes)
DEBUG   - Detailed diagnostic information
TRACE   - Granular execution details (function calls, variable values)
```

### Decision Matrix: Which Level to Use?

| Situation | Level | Example |
|-----------|-------|---------|
| User can't login | ERROR | "Authentication failed for user {id}: Invalid credentials" |
| Payment processed | INFO | "Payment successful: order={id}, amount={amt}" |
| API rate limit approached | WARN | "Rate limit at 90%: client={ip}, requests={count}" |
| Database connection retry | DEBUG | "Retrying DB connection: attempt {n}/3" |
| Function parameter values | TRACE | "processOrder called with: {params}" |
| Server crash | FATAL | "Out of memory: heap exhausted, terminating" |

---

## Structured Logging (JSON Format)

**Why**: Machine-parseable, searchable, aggregatable

### Standard Fields

```json
{
  "timestamp": "2025-11-20T10:30:45.123Z",
  "level": "error",
  "message": "Failed to process payment",
  "service": "payment-service",
  "environment": "production",
  "version": "1.2.3",
  "requestId": "req-abc123",
  "userId": "user-456",
  "duration": 5234
}
```

### Essential Context Fields

```javascript
// Request context
{
  "requestId": "unique-per-request",
  "method": "POST",
  "path": "/api/orders",
  "statusCode": 500,
  "duration": 234
}

// User context
{
  "userId": "user-123",
  "sessionId": "sess-456",
  "ipAddress": "192.168.1.1",
  "userAgent": "Mozilla/5.0..."
}

// Error context
{
  "error": {
    "name": "PaymentProcessingError",
    "message": "Gateway timeout",
    "code": "GATEWAY_TIMEOUT",
    "stack": "...",
    "cause": "..."
  }
}

// Business context
{
  "orderId": "order-789",
  "amount": 99.99,
  "currency": "USD",
  "gateway": "stripe"
}
```

---

## Logging Implementations by Language

### Node.js (Pino)

```javascript
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => {
      return { level: label };
    }
  },
  timestamp: pino.stdTimeFunctions.isoTime
});

// Request logger middleware
app.use((req, res, next) => {
  req.log = logger.child({
    requestId: req.id,
    method: req.method,
    path: req.path
  });

  const start = Date.now();
  res.on('finish', () => {
    req.log.info({
      statusCode: res.statusCode,
      duration: Date.now() - start
    }, 'Request completed');
  });

  next();
});

// Usage
req.log.info({ userId: user.id }, 'User authenticated');
req.log.error({ error, orderId }, 'Payment failed');
```

### Python (structlog)

```python
import structlog

# Configure
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info("user_authenticated", user_id=user.id, email=user.email)
logger.error("payment_failed",
    order_id=order.id,
    amount=order.amount,
    error=str(e),
    exc_info=True
)

# Request logging middleware (Flask)
@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    g.logger = logger.bind(request_id=g.request_id)

@app.after_request
def after_request(response):
    duration = (time.time() - g.start_time) * 1000
    g.logger.info("request_completed",
        method=request.method,
        path=request.path,
        status_code=response.status_code,
        duration_ms=duration
    )
    return response
```

### Go (zap)

```go
import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

// Configure
config := zap.NewProductionConfig()
config.EncoderConfig.TimeKey = "timestamp"
config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

logger, _ := config.Build()
defer logger.Sync()

// Usage
logger.Info("user authenticated",
    zap.String("userId", user.ID),
    zap.String("email", user.Email),
)

logger.Error("payment failed",
    zap.String("orderId", order.ID),
    zap.Float64("amount", order.Amount),
    zap.Error(err),
)

// Request logging middleware
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        requestID := uuid.New().String()

        reqLogger := logger.With(
            zap.String("requestId", requestID),
            zap.String("method", r.Method),
            zap.String("path", r.URL.Path),
        )

        ctx := context.WithValue(r.Context(), "logger", reqLogger)

        next.ServeHTTP(w, r.WithContext(ctx))

        duration := time.Since(start).Milliseconds()
        reqLogger.Info("request completed",
            zap.Int64("duration", duration),
        )
    })
}
```

---

## What to Log (DOs and DON'Ts)

### DO Log

```
[OK] User actions
   - Login attempts (success/failure)
   - State changes (order created, status updated)
   - Permission checks (access granted/denied)

[OK] External API calls
   - Endpoint called
   - HTTP status code
   - Response time
   - Retry attempts

[OK] Database operations
   - Query type (SELECT, UPDATE, DELETE)
   - Execution time (warn if > 1s)
   - Affected rows count
   - Connection pool stats

[OK] Background jobs
   - Job start/completion
   - Processing time
   - Records processed
   - Errors encountered

[OK] Errors with context
   - Full error message
   - Stack trace
   - Input parameters (sanitized)
   - User/request ID for tracing
   - System state at error time

[OK] Performance metrics
   - Request duration
   - Memory usage
   - CPU usage
   - Cache hit/miss rates
```

### DON'T Log

```
[FAIL] Passwords
[FAIL] API keys, tokens, secrets
[FAIL] Credit card numbers (full PAN)
[FAIL] Social Security Numbers
[FAIL] Personal health information
[FAIL] Full request/response bodies in production
[FAIL] Session tokens
[FAIL] Private encryption keys
[FAIL] Unredacted emails/phone numbers (in some jurisdictions)
```

### Sanitization Techniques

```javascript
// Redact sensitive fields
function sanitize(obj) {
  const sensitive = ['password', 'token', 'apiKey', 'creditCard', 'ssn'];
  const redacted = { ...obj };

  for (const key of sensitive) {
    if (redacted[key]) {
      redacted[key] = '[REDACTED]';
    }
  }

  return redacted;
}

// Mask PII
function maskEmail(email) {
  const [local, domain] = email.split('@');
  return `${local[0]}***@${domain}`;
}

// Usage
logger.info('User registered', sanitize({
  email: maskEmail(user.email),
  userId: user.id,
  // password field removed
}));
```

---

## Request ID Propagation (Distributed Tracing)

**Critical**: Every request needs a unique ID that follows it across all services.

### Implementation

**1. Generate at Entry Point**
```javascript
// API Gateway / Load Balancer
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || generateUUID();
  res.setHeader('x-request-id', req.id);
  next();
});
```

**2. Include in All Logs**
```javascript
const logger = pino().child({ requestId: req.id });
logger.info('Processing request');
```

**3. Propagate to Downstream Services**
```javascript
fetch('https://api.service-b.com/orders', {
  headers: {
    'x-request-id': req.id,
    'x-correlation-id': req.id
  }
});
```

**4. Search Logs by Request ID**
```bash
# Find all logs for a specific request across all services
rg -n "req-abc123" /var/log/*/app.log

# Or in log aggregation system
requestId:"req-abc123"
```

---

## Log Sampling (High-Volume Systems)

**Problem**: Logging every request can overwhelm storage and cost.

**Solution**: Sample logs intelligently.

### Strategies

**1. Error Logs (Always 100%)**
```javascript
if (level === 'error' || level === 'fatal') {
  logger.log(level, message); // Always log errors
}
```

**2. Success Logs (Sample 1-10%)**
```javascript
if (level === 'info' && Math.random() > 0.1) {
  return; // Skip 90% of info logs
}
```

**3. Debug Logs (Feature Flag)**
```javascript
if (level === 'debug' && !featureFlags.verboseLogging(userId)) {
  return; // Only log debug for specific users
}
```

**4. Rate Limiting by Category**
```javascript
const rateLimiters = {
  'user.login': new RateLimiter(100, 'per minute'),
  'order.created': new RateLimiter(1000, 'per minute')
};

if (rateLimiters[event].isAllowed()) {
  logger.info(event, data);
}
```

---

## Performance Considerations

### Benchmarks (Requests per Second)

```
console.log():        ~500,000 req/s (synchronous, blocks event loop)
pino (Node.js):      ~2,000,000 req/s (async, non-blocking)
winston (Node.js):     ~100,000 req/s (async)
structlog (Python):    ~150,000 req/s
zap (Go):            ~1,000,000 req/s
```

### Best Practices

```
[OK] Use async/non-blocking loggers
[OK] Write to stdout, let infrastructure handle aggregation
[OK] Avoid string concatenation (use structured fields)
[OK] Batch writes when possible
[OK] Use log levels to filter in production

[FAIL] Don't log in hot paths (tight loops)
[FAIL] Don't format large objects unnecessarily
[FAIL] Don't use synchronous file I/O
```

### Example: Optimized Logging

```javascript
// BAD: Bad: String concatenation
logger.info('User ' + user.id + ' created order ' + order.id);

// GOOD: Good: Structured fields
logger.info({ userId: user.id, orderId: order.id }, 'Order created');

// BAD: Bad: Logging in loop
for (const item of items) {
  logger.debug('Processing item', { item });
}

// GOOD: Good: Log summary
logger.debug({ itemCount: items.length, items: items.map(i => i.id) }, 'Processing batch');
```

---

## Log Aggregation & Search

### ELK Stack (Elasticsearch, Logstash, Kibana)

**1. Ship logs to Logstash**
```javascript
// Pino transport
const transport = pino.transport({
  target: '@logtail/pino',
  options: { sourceToken: 'your-token' }
});
```

**2. Index in Elasticsearch**
```bash
# Logstash config
input {
  beats { port => 5044 }
}
filter {
  json { source => "message" }
}
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

**3. Search in Kibana**
```
# Find all errors for user
userId:"user-123" AND level:"error"

# Find slow requests (> 1s)
duration:>1000

# Find payment failures
message:"payment failed" AND level:"error"
```

---

## Log Retention Policies

```
DEBUG logs:    1-7 days   (development/troubleshooting)
INFO logs:     30-90 days (operational visibility)
WARN logs:     90-180 days (trend analysis)
ERROR logs:    1-2 years (compliance, postmortems)
AUDIT logs:    3-7 years (regulatory requirements)
```

### Cost Optimization

```
Hot tier (fast search):     Last 7 days     - SSD storage
Warm tier (occasional):     8-30 days       - Regular disks
Cold tier (archival):       30+ days        - S3/Glacier
```

---

## Checklist: Production Logging Setup

```
[ ] Structured logging library configured (Pino/structlog/zap)
[ ] Log level set per environment (DEBUG in dev, INFO in prod)
[ ] Request ID generation and propagation
[ ] Sensitive data redaction/sanitization
[ ] Error logs include stack traces and context
[ ] Request/response logging middleware
[ ] Log aggregation configured (ELK, Datadog, etc.)
[ ] Log retention policies defined
[ ] Alerting on error rate spikes
[ ] Sampling configured for high-volume endpoints
[ ] Performance benchmarked (no blocking I/O)
[ ] Correlation IDs for distributed tracing
```

---

## Common Mistakes

**1. Logging Too Much**
```
[FAIL] Bad: DEBUG logs in production without filtering
GOOD: INFO in prod, DEBUG via feature flag for specific users
```

**2. Logging Too Little**
```
[FAIL] Bad: try { ... } catch(e) { console.log('Error') }
GOOD: logger.error({ error, context }, 'Operation failed')
```

**3. No Request Correlation**
```
[FAIL] Bad: Separate logs with no way to connect them
GOOD: Every log has requestId, can reconstruct request flow
```

**4. Synchronous Logging**
```
[FAIL] Bad: fs.appendFileSync() in request handler
GOOD: Async logger writing to stdout, piped to log shipper
```

**5. Logging Secrets**
```
[FAIL] Bad: logger.info('Connecting to DB', { connectionString })
GOOD: logger.info('Connecting to DB', { host, database })
```

---

> **Remember**: Good logging is the foundation of observability. Log strategically, structure consistently, and sanitize rigorously.
