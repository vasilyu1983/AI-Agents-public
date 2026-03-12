# Operational Patterns and Standards

## Contents

- [Core Debugging Patterns](#core-debugging-patterns)
- [Pattern: Systematic Debugging Workflow](#pattern-systematic-debugging-workflow)
- [Pattern: Debugging by Elimination (Binary Search)](#pattern-debugging-by-elimination-binary-search)
- [Pattern: Structured Logging Strategy](#pattern-structured-logging-strategy)
- [Pattern: Stack Trace Analysis](#pattern-stack-trace-analysis)
- [Pattern: Memory Leak Detection](#pattern-memory-leak-detection)
- [Pattern: Performance Profiling](#pattern-performance-profiling)
- [Pattern: Distributed System Debugging](#pattern-distributed-system-debugging)
- [Pattern: Production Debugging](#pattern-production-debugging)
- [Pattern: Timezone Debugging](#pattern-timezone-debugging)
- [JavaScript/Node.js](#javascriptnodejs)
- [Python](#python)
- [Java](#java)
- [Go](#go)
- [Database](#database)
- [Distributed Systems](#distributed-systems)

## Core Debugging Patterns

## Pattern: Systematic Debugging Workflow

**Use when:** Encountering any bug or unexpected behavior.

**The Scientific Method for Debugging:**

1. **Observe** - Reproduce the issue consistently
2. **Question** - Form hypothesis about root cause
3. **Predict** - What should happen if hypothesis is correct?
4. **Experiment** - Test hypothesis with minimal changes
5. **Analyze** - Did results match prediction?
6. **Iterate** - Refine hypothesis and repeat

**Step-by-Step Debugging Checklist:**

```
[ ] Reproduce the issue reliably (write reproduction steps)
[ ] Gather context (environment, inputs, expected vs actual behavior)
[ ] Check recent changes (git log, deployment history)
[ ] Isolate the problem (binary search through code/config)
[ ] Form hypothesis about root cause
[ ] Verify hypothesis with minimal test case
[ ] Fix and validate the fix
[ ] Add regression test to prevent recurrence
[ ] Document the issue and solution
```

**Anti-Patterns:**
- Random code changes without hypothesis ("try this")
- Skipping reproduction steps
- Debugging without logs/observability
- Fixing symptoms instead of root cause
- Not adding tests after fixing

---

## Pattern: Debugging by Elimination (Binary Search)

**Use when:** Issue could be in many places; need to narrow down quickly.

**Strategy:**
1. **Identify the boundaries** - Where does the issue definitely occur? Where does it definitely not occur?
2. **Split in half** - Disable/comment out half the code
3. **Test** - Does issue still occur?
4. **Repeat** - Focus on the half with the issue

**Example (API endpoint failing):**
```
1. Add log at start and end of request handler -> Issue is inside handler
2. Add log in middle of handler -> Issue is in second half
3. Add log in middle of second half -> Issue is in database query
4. Log query parameters -> Found: null parameter
```

**Checklist:**
- [ ] Define clear boundaries (working vs broken state)
- [ ] Add instrumentation at boundaries
- [ ] Binary search through code paths
- [ ] Document elimination steps
- [ ] Verify fix restores working state

---

## Pattern: Structured Logging Strategy

**Use when:** Building observability into applications.

**Log Levels (Standard Hierarchy):**
```
FATAL - Application crash, unrecoverable
ERROR - Error occurred but app continues
WARN  - Unexpected situation but not an error
INFO  - Important business events (user login, order created)
DEBUG - Detailed information for debugging
TRACE - Very detailed (function entry/exit, variable values)
```

**What to Log:**

**DO Log:**
- Request/response metadata (method, path, status, duration)
- User actions (authentication, state changes)
- External API calls (endpoint, status, duration)
- Database queries (with duration, not actual query params in production)
- Background job start/completion
- Errors with full context (stack trace, input data)
- Performance metrics (response time, memory usage)

**DON'T Log:**
- Passwords, API keys, tokens, secrets
- Personally identifiable information (PII) without consent
- Full credit card numbers, SSNs
- Medical records, sensitive personal data
- Complete request/response bodies in production (unless scrubbed)

**Structured Logging Format (JSON):**
```json
{
  "timestamp": "2025-11-20T10:30:45.123Z",
  "level": "error",
  "message": "Failed to process payment",
  "service": "payment-service",
  "environment": "production",
  "requestId": "req-abc123",
  "userId": "user-456",
  "error": {
    "name": "PaymentProcessingError",
    "message": "Gateway timeout",
    "code": "GATEWAY_TIMEOUT",
    "stack": "...",
    "cause": "..."
  },
  "context": {
    "orderId": "order-789",
    "amount": 99.99,
    "currency": "USD",
    "gateway": "stripe"
  },
  "duration": 5234
}
```

**Checklist:**
- [ ] Use structured logging library (Pino, Winston, structlog)
- [ ] Include request ID for tracing
- [ ] Add service and environment tags
- [ ] Log at appropriate levels
- [ ] Sanitize sensitive data
- [ ] Include context for debugging
- [ ] Measure operation duration

---

## Pattern: Stack Trace Analysis

**Use when:** Encountering exceptions or crashes.

**How to Read Stack Traces:**

1. **Start at the top** - Most recent function call
2. **Identify your code** - Look for file paths in your project
3. **Find the trigger** - First line in your code that caused error
4. **Check the inputs** - What values led to this call?
5. **Trace backward** - How did you get to this state?

**Example (JavaScript):**
```
Error: Cannot read property 'email' of undefined
    at getUserEmail (src/services/user.js:42)      <- Your code (trigger)
    at processOrder (src/services/order.js:89)     <- Your code
    at OrderController.create (src/api/orders.js:23) <- Your code
    at Layer.handle (express/lib/router/layer.js:95) <- Framework
```

**Analysis:**
- Error: Trying to access `.email` on `undefined`
- Location: `user.js:42` in `getUserEmail` function
- Hypothesis: User object is undefined
- Next step: Check why user is undefined at line 89 in order.js

**Common Patterns:**
- **TypeError: Cannot read property 'x' of undefined** - Object is null/undefined
- **ReferenceError: x is not defined** - Variable not declared or out of scope
- **SyntaxError** - Code syntax error (usually caught before runtime)
- **RangeError** - Invalid array index or infinite recursion
- **NetworkError/TimeoutError** - External service failure

**Checklist:**
- [ ] Identify the exact error type
- [ ] Find first occurrence in your code
- [ ] Check input values at that point
- [ ] Trace call stack backward
- [ ] Verify assumptions about state
- [ ] Add defensive checks if needed

---

## Pattern: Memory Leak Detection

**Use when:** Application memory usage grows over time or crashes with OOM.

**Detection Strategies:**

**1. Heap Snapshots (Node.js/Chrome DevTools)**
```bash
# Take heap snapshot
node --inspect app.js
# Open chrome://inspect, take snapshots over time
# Compare snapshots to find retained objects
```

**2. Memory Profiling (Python)**
```python
import tracemalloc
tracemalloc.start()
# ... run code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

**3. Monitor Memory Over Time**
```javascript
// Log memory usage periodically
setInterval(() => {
  const used = process.memoryUsage();
  console.log({
    rss: `${Math.round(used.rss / 1024 / 1024)} MB`,
    heapTotal: `${Math.round(used.heapTotal / 1024 / 1024)} MB`,
    heapUsed: `${Math.round(used.heapUsed / 1024 / 1024)} MB`,
    external: `${Math.round(used.external / 1024 / 1024)} MB`,
  });
}, 5000);
```

**Common Memory Leak Causes:**
- Global variables accumulating data
- Event listeners not removed
- Timers (setInterval) not cleared
- Circular references preventing garbage collection
- Large objects in closures
- Cache without eviction policy
- Unclosed database connections
- File handles not closed

**Checklist:**
- [ ] Monitor memory usage over time
- [ ] Take heap snapshots before/after operations
- [ ] Check for event listener leaks
- [ ] Verify timers are cleared
- [ ] Review cache eviction policies
- [ ] Ensure connections are closed
- [ ] Test with realistic load

---

## Pattern: Performance Profiling

**Use when:** Application is slow but you don't know why.

**Profiling Tools by Language:**

**JavaScript/Node.js:**
```bash
# CPU profiling
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# Chrome DevTools
node --inspect app.js
# Open chrome://inspect, use Performance tab
```

**Python:**
```python
import cProfile
cProfile.run('main()', 'profile.stats')

# Or line-by-line profiling
from line_profiler import LineProfiler
lp = LineProfiler()
lp.add_function(my_function)
lp.run('my_function()')
lp.print_stats()
```

**Database Query Profiling:**
```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- MySQL
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE email = 'test@example.com';
```

**Performance Bottleneck Checklist:**
- [ ] Profile CPU usage (hot functions)
- [ ] Profile memory allocations
- [ ] Analyze database query performance (EXPLAIN ANALYZE)
- [ ] Check network latency (external API calls)
- [ ] Review algorithmic complexity (O(n^2) loops)
- [ ] Identify N+1 query problems
- [ ] Measure cold start vs warm cache
- [ ] Test with production-like data volume

---

## Pattern: Distributed System Debugging

**Use when:** Debugging microservices, async workflows, or distributed systems.

**Challenges:**
- Multiple services involved in single request
- Async operations (events, queues, webhooks)
- Network failures and timeouts
- Clock skew between services
- Partial failures

### Sampling Strategies (Cost vs Coverage)

**Head Sampling** - Decision at trace start:
```javascript
// OpenTelemetry head sampling (10% of requests)
const sdk = new NodeSDK({
  sampler: new TraceIdRatioBasedSampler(0.1),
});
```

**Tail Sampling** - Decision after trace complete (recommended for debugging):
```yaml
# OpenTelemetry Collector config - tail sampling
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      # Always capture errors
      - name: errors-policy
        type: status_code
        status_code: {status_codes: [ERROR]}
      # Always capture slow requests
      - name: latency-policy
        type: latency
        latency: {threshold_ms: 1000}
      # Sample 10% of normal traffic
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: {sampling_percentage: 10}
```

**Why tail sampling for debugging:**
- Captures 100% of errors and slow requests
- Samples healthy requests to control costs
- Enables RCA without missing critical traces

### Async Trace Propagation (Event-Driven Systems)

**Challenge:** Message queues break trace context.

**Solution:** Propagate trace context in message headers:

```javascript
// Producer - inject context into message
const { context, propagation } = require('@opentelemetry/api');

async function publishMessage(queue, payload) {
  const carrier = {};
  propagation.inject(context.active(), carrier);

  await queue.send({
    body: payload,
    headers: carrier,  // Contains traceparent header
  });
}

// Consumer - extract context from message
async function handleMessage(message) {
  const parentContext = propagation.extract(
    context.active(),
    message.headers
  );

  return context.with(parentContext, async () => {
    const span = tracer.startSpan('process-message');
    try {
      // Process message - trace continues
      await processPayload(message.body);
    } finally {
      span.end();
    }
  });
}
```

**Kafka example:**
```javascript
// Kafka producer with trace propagation
await producer.send({
  topic: 'orders',
  messages: [{
    value: JSON.stringify(order),
    headers: {
      traceparent: getTraceParentHeader(),
      tracestate: getTraceStateHeader(),
    },
  }],
});
```

### Collector Deployment Patterns

| Pattern | Use Case | Pros | Cons |
|---------|----------|------|------|
| **Agent** | Sidecar per app | Low latency, local processing | More collectors to manage |
| **Gateway** | Centralized | Single config, easier ops | Potential bottleneck |
| **Hierarchical** | Large scale | Best of both | Complex setup |

```text
Agent Pattern:
  App1 -> Collector1 -> Backend
  App2 -> Collector2 -> Backend

Gateway Pattern:
  App1 -> Gateway Collector -> Backend
  App2 -> Gateway Collector -> Backend
  App3 -> Gateway Collector -> Backend

Hierarchical Pattern:
  App1 -> Agent1 -> Gateway -> Backend
  App2 -> Agent2 -> Gateway -> Backend
  App3 -> Agent3 -> Gateway -> Backend
```

**Essential Tools:**

**1. Distributed Tracing (OpenTelemetry)**
```javascript
const { trace } = require('@opentelemetry/api');

const span = trace.getTracer('my-service').startSpan('process-order');
span.setAttribute('orderId', orderId);
try {
  // ... business logic ...
  span.setStatus({ code: SpanStatusCode.OK });
} catch (error) {
  span.recordException(error);
  span.setStatus({ code: SpanStatusCode.ERROR });
} finally {
  span.end();
}
```

**2. Request ID Propagation**
```javascript
// Generate request ID at entry point
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || generateId();
  res.setHeader('x-request-id', req.id);
  logger.child({ requestId: req.id });
  next();
});

// Propagate to downstream services
fetch('https://api.example.com', {
  headers: { 'x-request-id': req.id }
});
```

**3. Correlation IDs**
- Use UUIDs to track requests across services
- Include in all logs
- Pass in HTTP headers
- Store in message queue metadata

**Debugging Workflow:**
1. **Find the request ID** from user report or logs
2. **Grep logs across all services** for that request ID
3. **Reconstruct the timeline** of events
4. **Identify where it failed** (missing logs = failed service)
5. **Check each service's health** at that time
6. **Review network/infrastructure** logs

**Checklist:**
- [ ] Request IDs on all requests
- [ ] Distributed tracing implemented
- [ ] Centralized log aggregation (ELK, Datadog, Splunk)
- [ ] Service health dashboards
- [ ] Network/infrastructure monitoring
- [ ] Timeout and retry policies documented
- [ ] Circuit breakers configured

---

## Pattern: Production Debugging

**Use when:** Issue only occurs in production, not reproducible locally.

**Safe Production Debugging Techniques:**

**1. Log Analysis (Non-Intrusive)**
```bash
# Search for specific user/request
rg -n "user-id-123" /var/log/app/*.log

# Find errors in last hour
rg "ERROR" /var/log/app/app.log --no-filename --no-line-number | rg "$(date -d '1 hour ago' '+%Y-%m-%d %H')" --no-filename --no-line-number

# Count errors by type
rg "ERROR" /var/log/app/app.log --no-filename --no-line-number | awk '{print $5}' | sort | uniq -c | sort -rn
```

**2. Feature Flags for Debugging**
```javascript
if (featureFlags.isEnabled('verbose-logging', userId)) {
  logger.debug('Detailed state', { state, inputs, outputs });
}
```

**3. Canary Deployments**
- Deploy fix to 5% of traffic first
- Monitor error rates and metrics
- Gradually increase percentage
- Rollback immediately if issues

**4. Read-Only Access**
- Use read replicas for investigating data
- Never modify production data directly
- Export data to staging for reproduction

**What NOT to Do in Production:**
- Restart services without understanding the issue
- Make code changes directly on servers
- Delete data without backups
- Disable monitoring/logging
- Skip change approval process
- Debug with production API keys
- Leave debug logging enabled

**Checklist:**
- [ ] Check error tracking dashboard (Sentry, Rollbar)
- [ ] Review monitoring metrics (CPU, memory, latency)
- [ ] Analyze logs for patterns
- [ ] Compare to previous working version
- [ ] Check infrastructure/network status
- [ ] Use feature flags for safe debugging
- [ ] Document incident timeline
- [ ] Prepare rollback plan before deploying fix

---

## Pattern: Timezone Debugging

**Use when:** Date/time issues in applications serving users across timezones.

**Common Symptoms:**

- Data shows wrong times for users in different timezones
- Cron jobs fire at wrong times
- Date comparisons fail near midnight
- "Off by one day" errors
- Scheduled notifications arrive at wrong times
- Analytics/reports showing incorrect dates

**Root Causes by Symptom:**

| Symptom | Likely Cause | Check |
|---------|-------------|-------|
| Wrong display time | Client not converting UTC to local | Browser vs server timezone |
| Off by one day | Date comparison ignoring timezone | Comparing date strings vs timestamps |
| Cron fires wrong time | Server timezone != expected timezone | `TZ` env var, system timezone |
| Midnight bugs | DST transition not handled | Date calculations crossing DST |
| Different users, different bugs | User timezone not stored | Profile timezone field |

**Debugging Checklist:**

```
[ ] Identify storage format (UTC? Local? Timestamp?)
[ ] Check all conversion points (server -> DB, DB -> API, API -> client)
[ ] Log timestamps WITH timezone info (ISO 8601 with offset)
[ ] Test edge cases: midnight UTC, DST transitions, leap years
[ ] Verify server timezone (echo $TZ, check system config)
[ ] Check database timezone settings (SHOW timezone in PostgreSQL)
[ ] Confirm client timezone detection method
```

**Debugging Commands:**

```bash
# Check server timezone
date
TZ='America/New_York' date
TZ='UTC' date

# PostgreSQL timezone
psql -c "SHOW timezone;"
psql -c "SELECT NOW(), NOW() AT TIME ZONE 'UTC', NOW() AT TIME ZONE 'America/New_York';"

# Node.js timezone
node -e "console.log(Intl.DateTimeFormat().resolvedOptions().timeZone)"
```

**Timezone-Safe Logging Pattern:**

```typescript
// BAD: BAD - Ambiguous timestamps
console.log(`Event at ${new Date()}`);
// Output: Event at Wed Nov 20 2024 10:30:45 GMT-0500 (EST)

// GOOD: GOOD - ISO 8601 with timezone offset
console.log(`Event at ${new Date().toISOString()}`);
// Output: Event at 2024-11-20T15:30:45.123Z

// GOOD: BETTER - Include user's timezone context
logger.info({
  event: 'user_login',
  timestamp: new Date().toISOString(),
  serverTimezone: process.env.TZ || 'system',
  userTimezone: user.timezone,
  userLocalTime: new Date().toLocaleString('en-US', { timeZone: user.timezone }),
});
```

**Centralized Timezone Utility Pattern:**

```typescript
// src/lib/timezone.ts
// Centralize timezone handling to avoid scattered conversions

/**
 * Convert UTC date to user's local timezone
 */
export function toUserTimezone(utcDate: Date, timezone: string): Date {
  return new Date(utcDate.toLocaleString('en-US', { timeZone: timezone }));
}

/**
 * Get start of day in user's timezone (for date comparisons)
 */
export function getUserMidnight(timezone: string, date = new Date()): Date {
  const userDate = toUserTimezone(date, timezone);
  userDate.setHours(0, 0, 0, 0);
  return userDate;
}

/**
 * Get user's current date string (YYYY-MM-DD) in their timezone
 */
export function getUserDateString(timezone: string, date = new Date()): string {
  return date.toLocaleDateString('en-CA', { timeZone: timezone }); // en-CA = YYYY-MM-DD format
}

/**
 * Check if two dates are the same day in user's timezone
 */
export function isSameUserDay(date1: Date, date2: Date, timezone: string): boolean {
  return getUserDateString(timezone, date1) === getUserDateString(timezone, date2);
}

/**
 * Get timezone offset in minutes (for cron scheduling)
 */
export function getTimezoneOffsetMinutes(timezone: string): number {
  const now = new Date();
  const utcTime = now.getTime() + now.getTimezoneOffset() * 60000;
  const tzTime = new Date(utcTime).toLocaleString('en-US', { timeZone: timezone });
  return (new Date(tzTime).getTime() - utcTime) / 60000;
}
```

**Cron Job Timezone Handling:**

```typescript
// BAD: BAD - Assumes server timezone matches users
// Cron runs at 8am server time, but users are in different timezones
cron.schedule('0 8 * * *', sendMorningNotifications);

// GOOD: GOOD - Calculate per-user timezone offset
async function scheduleMorningNotifications() {
  const users = await getUsersWithNotificationsEnabled();

  for (const user of users) {
    const userNow = toUserTimezone(new Date(), user.timezone);
    const userHour = userNow.getHours();

    // Only send if it's 8am in USER's timezone
    if (userHour === 8) {
      await sendNotification(user.id);
    }
  }
}

// Run every hour, let function determine who gets notifications
cron.schedule('0 * * * *', scheduleMorningNotifications);
```

**Database Timezone Best Practices:**

```sql
-- Always store in UTC
ALTER DATABASE mydb SET timezone TO 'UTC';

-- Convert on query for user-specific reports
SELECT
  created_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/New_York' as local_time,
  *
FROM orders
WHERE user_id = $1;

-- Use timestamptz (timestamp with time zone) not timestamp
CREATE TABLE events (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  occurs_at TIMESTAMPTZ NOT NULL,  -- [OK] Stores UTC, converts on retrieval
  -- NOT: occurs_at TIMESTAMP       -- [FAIL] Ambiguous timezone
);
```

**Testing Timezone Edge Cases:**

```typescript
describe('Timezone handling', () => {
  const testTimezones = [
    'UTC',
    'America/New_York',      // EST/EDT (DST transition)
    'America/Los_Angeles',   // PST/PDT (DST transition)
    'Europe/London',         // GMT/BST (DST transition)
    'Asia/Tokyo',            // JST (no DST)
    'Pacific/Auckland',      // NZST/NZDT (opposite DST)
  ];

  test.each(testTimezones)('handles midnight correctly in %s', (timezone) => {
    // Test your date logic with each timezone
  });

  test('handles DST spring forward', () => {
    // March 10, 2024 2:00 AM doesn't exist in America/New_York
    const springForward = new Date('2024-03-10T07:00:00Z'); // 2am EST -> 3am EDT
  });

  test('handles DST fall back', () => {
    // November 3, 2024 1:00 AM happens twice in America/New_York
    const fallBack = new Date('2024-11-03T06:00:00Z');
  });
});
```

**Quick Reference - Timezone Conversion:**

| From | To | Method |
|------|-----|--------|
| UTC string | Date object | `new Date('2024-01-15T10:00:00Z')` |
| Date object | UTC string | `date.toISOString()` |
| Date object | User local | `date.toLocaleString('en-US', { timeZone })` |
| User local | UTC | Store as UTC, convert on display |
| DB timestamp | Display | Convert at API layer, not in DB query |

**Checklist:**
- [ ] Store all timestamps in UTC
- [ ] Use `timestamptz` in PostgreSQL, not `timestamp`
- [ ] Store user's preferred timezone in profile
- [ ] Convert to user timezone only at display layer
- [ ] Test with users in different timezones
- [ ] Test DST transitions (spring forward, fall back)
- [ ] Log timestamps in ISO 8601 format with Z suffix
- [ ] Verify server timezone is set correctly
- [ ] Use timezone library for complex calculations (date-fns-tz, luxon)

---

# Debugging Tools by Language/Platform

## JavaScript/Node.js
- **Chrome DevTools** - Browser debugging, CPU/memory profiling
- **Node.js Inspector** - `node --inspect` for server-side debugging
- **ndb** - Improved Node.js debugger by Google
- **Clinic.js** - Performance profiling suite

## Python
- **pdb** - Built-in Python debugger
- **ipdb** - Enhanced pdb with IPython
- **cProfile** - CPU profiling
- **memory_profiler** - Memory usage analysis
- **py-spy** - Sampling profiler (no code changes)

## Java
- **JDB** - Java debugger
- **VisualVM** - All-in-one profiling tool
- **JProfiler** - Commercial profiler
- **Java Flight Recorder** - Production-safe profiling

## Go
- **Delve** - Go debugger
- **pprof** - CPU and memory profiling
- **trace** - Execution tracer

## Database
- **EXPLAIN ANALYZE** - PostgreSQL/MySQL query analysis
- **pg_stat_statements** - PostgreSQL query statistics
- **Slow query log** - MySQL slow query analysis

## Distributed Systems
- **OpenTelemetry** - Distributed tracing standard
- **Jaeger** - Distributed tracing platform
- **Zipkin** - Distributed tracing system
- **ELK Stack** - Log aggregation (Elasticsearch, Logstash, Kibana)
- **Datadog** - Full observability platform
- **New Relic** - APM and monitoring

---
