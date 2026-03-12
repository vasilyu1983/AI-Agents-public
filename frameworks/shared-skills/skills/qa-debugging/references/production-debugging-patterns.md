# Production Debugging Patterns - Safe Strategies

This guide provides safe, non-intrusive debugging techniques for production environments where traditional debugging tools can't be used.

## Contents

- [Golden Rules of Production Debugging](#golden-rules-of-production-debugging)
- [Safe Production Debugging Techniques](#safe-production-debugging-techniques)
- [Production Debugging Checklist](#production-debugging-checklist)
- [Anti-Patterns (Don't Do This)](#anti-patterns-dont-do-this)
- [Tools for Production Debugging](#tools-for-production-debugging)
- [Real-World Example: Debugging Slow API](#real-world-example-debugging-slow-api)

---

## Golden Rules of Production Debugging

```
1. NEVER restart services without understanding the issue
2. NEVER make code changes directly on servers
3. NEVER delete data without verified backups
4. NEVER disable monitoring or logging
5. NEVER skip change approval processes
6. NEVER use production credentials in development
7. ALWAYS have a rollback plan before deploying fixes
```

---

## Safe Production Debugging Techniques

### 1. Log Analysis (Non-Intrusive)

**Search for Patterns (rg)**

```bash
# Find errors in last hour
rg "ERROR" /var/log/app/app.log --no-filename --no-line-number | \
  rg "$(date -d '1 hour ago' '+%Y-%m-%d %H')" --no-filename --no-line-number

# Find specific user's requests
rg -n "user-id-123" /var/log/app/*.log

# Count errors by type
rg "ERROR" /var/log/app/app.log --no-filename --no-line-number | \
  awk '{print $5}' | \
  sort | uniq -c | sort -rn

# Find slow requests (>1s duration)
rg "duration" /var/log/app/app.log --no-filename --no-line-number | \
  awk '$NF > 1000' | \
  head -20

# Find requests with specific status code
rg "statusCode\":500" /var/log/app/app.log --no-filename --no-line-number | tail -50
```

**Structured Log Queries (JSON)**

```bash
# Using jq to parse JSON logs
cat app.log | jq 'select(.level == "error" and .duration > 1000)'

# Find payment failures
cat app.log | jq 'select(.message | contains("payment")) | select(.level == "error")'

# Group errors by error.code
cat app.log | jq -r 'select(.level == "error") | .error.code' | \
  sort | uniq -c | sort -rn
```

**Log Aggregation Queries (ELK/Datadog)**

```
# Elasticsearch Query (Kibana)
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "error" } },
        { "range": { "@timestamp": { "gte": "now-1h" } } },
        { "match": { "service": "payment-service" } }
      ]
    }
  }
}

# Datadog Query
service:payment-service status:error @duration:>1000
```

---

### 2. Metrics Analysis (Observability)

**Key Metrics to Monitor**

```
REQUEST RATE:
- Requests per second (RPS)
- Requests by endpoint
- Requests by status code

LATENCY:
- P50, P95, P99 latencies
- Endpoint-specific latency
- Database query time

ERROR RATE:
- Total errors per minute
- Error rate by endpoint
- Error types distribution

RESOURCE USAGE:
- CPU utilization
- Memory usage
- Disk I/O
- Network throughput
```

**Prometheus Queries**

```promql
# Error rate last 5 minutes
rate(http_requests_total{status=~"5.."}[5m])

# P95 latency by endpoint
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Memory usage trend
rate(process_resident_memory_bytes[5m])

# Request rate spike detection
rate(http_requests_total[5m]) >
  avg_over_time(rate(http_requests_total[5m])[1h]) * 2
```

---

### 3. Distributed Tracing (Request Flow)

**Trace a Single Request**

```javascript
// Find request ID from user report or logs
const requestId = 'req-abc123';

// Search logs across all services
rg -n "req-abc123" /var/log/*/app.log

// Reconstruct timeline
// 10:30:45.123 [gateway] Request received
// 10:30:45.150 [auth] Token validated
// 10:30:45.200 [order-service] Creating order
// 10:30:47.500 [payment-service] Processing payment <- 2.3s delay
// 10:30:47.550 [order-service] Order created
// 10:30:47.600 [gateway] Response sent

// FINDING: Payment service taking 2.3s (normal: 200ms)
```

**Jaeger/Zipkin Trace Analysis**

```
Request Trace: req-abc123
Total Duration: 2500ms

- API Gateway: 10ms
- Auth Service: 50ms
- Order Service: 2000ms <- Bottleneck
  - Validate Cart: 100ms
  - Check Inventory: 1800ms <- Problem here
  - Create Order Record: 100ms
- Notification Service: 100ms

ACTION: Investigate inventory service - potential database issue
```

---

### 4. Feature Flags for Safe Debugging

**Enable Verbose Logging for Specific Users**

```javascript
// Backend
if (featureFlags.isEnabled('verbose-logging', userId)) {
  logger.debug('Detailed state', {
    inputs,
    intermediateValues,
    outputs,
    stackTrace: new Error().stack
  });
}

// Usage
// 1. Enable flag for affected user
// 2. Ask user to reproduce issue
// 3. Collect verbose logs
// 4. Disable flag
```

**Canary Deployments (Gradual Rollout)**

```yaml
# Kubernetes Canary Deployment
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  # Both stable and canary pods selected

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-stable
spec:
  replicas: 9  # 90% traffic
  template:
    metadata:
      labels:
        app: my-app
        version: v1.2.3

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-canary
spec:
  replicas: 1  # 10% traffic
  template:
    metadata:
      labels:
        app: my-app
        version: v1.2.4-canary
```

**Process**:
```
1. Deploy fix to canary (10% traffic)
2. Monitor error rates and metrics
3. If stable, increase to 50%
4. If still stable, increase to 100%
5. If issues, rollback canary immediately
```

---

### 5. Read-Only Database Access

**Safe Investigation Queries**

```sql
-- DON'T: Make changes
-- UPDATE users SET status = 'active' WHERE id = 123;

-- DO: Query read replica
SELECT * FROM users WHERE id = 123;

-- Find affected records
SELECT COUNT(*) FROM orders
WHERE status = 'pending'
  AND created_at < NOW() - INTERVAL '1 hour';

-- Export data for local reproduction
SELECT * FROM orders
WHERE user_id = 'user-123'
  AND created_at >= '2025-11-20';
```

**Use Read Replicas**

```javascript
// Production database (write)
const primaryDB = new Database(process.env.PRIMARY_DB_URL);

// Read replica (safe for queries)
const replicaDB = new Database(process.env.REPLICA_DB_URL);

// Investigation queries go to replica
const result = await replicaDB.query(`
  SELECT * FROM orders WHERE id = ?
`, [orderId]);
```

---

### 6. Health Checks & Smoke Tests

**Continuous Health Monitoring**

```javascript
// Health check endpoint
app.get('/health', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    cache: await checkRedis(),
    externalAPI: await checkPaymentGateway(),
    diskSpace: await checkDiskSpace(),
    memory: process.memoryUsage()
  };

  const healthy = Object.values(checks).every(c => c.status === 'ok');

  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'degraded',
    checks,
    timestamp: new Date().toISOString()
  });
});
```

**Smoke Tests After Deployment**

```bash
#!/bin/bash
# smoke-test.sh

# Check service is up
curl -f https://api.example.com/health || exit 1

# Test critical endpoints
curl -f -X POST https://api.example.com/api/auth/login \
  -d '{"email":"test@example.com","password":"test123"}' || exit 1

curl -f https://api.example.com/api/orders || exit 1

# Check error rate in last 5 minutes
ERROR_RATE=$(curl -s 'https://monitoring.example.com/api/v1/query?query=rate(errors[5m])' | jq '.data.result[0].value[1]')

if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
  echo "Error rate too high: $ERROR_RATE"
  exit 1
fi

echo "Smoke tests passed"
```

---

### 7. Synthetic Monitoring (Proactive Detection)

**Simulate User Journeys**

```javascript
// Datadog Synthetics / Checkly
const { chromium } = require('playwright');

async function checkoutFlow() {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // 1. Login
    await page.goto('https://example.com/login');
    await page.fill('#email', 'test@example.com');
    await page.fill('#password', 'test123');
    await page.click('#login-button');
    await page.waitForNavigation();

    // 2. Add to cart
    await page.goto('https://example.com/products/123');
    await page.click('#add-to-cart');

    // 3. Checkout
    await page.goto('https://example.com/checkout');
    await page.fill('#credit-card', '4242424242424242');
    await page.click('#submit-order');

    // 4. Verify success
    await page.waitForSelector('.order-confirmation');
    console.log('[OK] Checkout flow successful');

  } catch (error) {
    console.error('[FAIL] Checkout flow failed', error);
    throw error;
  } finally {
    await browser.close();
  }
}

// Run every 5 minutes
setInterval(checkoutFlow, 5 * 60 * 1000);
```

---

### 8. Incident Response Workflow

**Step-by-Step Process**

```
1. DETECT
   [ ] Alert received or user report
   [ ] Verify issue is real (not false alarm)
   [ ] Assess severity and impact

2. TRIAGE
   [ ] Create incident ticket
   [ ] Assemble response team
   [ ] Establish communication channel
   [ ] Notify stakeholders

3. INVESTIGATE
   [ ] Check monitoring dashboards
   [ ] Review recent deployments
   [ ] Analyze logs and traces
   [ ] Form hypothesis

4. MITIGATE
   [ ] Implement immediate fix (if known)
   [ ] OR rollback to last known good version
   [ ] Verify mitigation resolved issue
   [ ] Monitor for recurrence

5. RESOLVE
   [ ] Implement permanent fix
   [ ] Test fix in staging
   [ ] Deploy to production
   [ ] Verify resolution

6. POSTMORTEM
   [ ] Document timeline
   [ ] Identify root cause
   [ ] List action items to prevent recurrence
   [ ] Share learnings with team
```

**Communication Template**

```
INCIDENT: Payment Processing Failure
SEVERITY: Critical (P1)
STATUS: Investigating

IMPACT:
- 15% of payment attempts failing (last 20 minutes)
- ~500 orders affected
- Primarily Stripe payment method

TIMELINE:
10:30 AM - First alerts received
10:35 AM - Issue confirmed, team assembled
10:40 AM - Investigating logs and traces
10:45 AM - Hypothesis: Stripe API timeout increase

CURRENT ACTION:
- Increasing timeout from 5s to 10s
- Monitoring error rates

NEXT UPDATE: 11:00 AM or when status changes

INCIDENT COMMANDER: Jane Doe
TECHNICAL LEAD: John Smith
```

---

## Production Debugging Checklist

**Before Making Changes**:
```
[ ] Can you reproduce the issue in staging?
[ ] Do you have a rollback plan?
[ ] Have you reviewed the blast radius?
[ ] Is the change approved?
[ ] Are stakeholders notified?
```

**While Debugging**:
```
[ ] Analyze logs, metrics, and traces first
[ ] Use read-only database access
[ ] Enable verbose logging via feature flags
[ [ Use canary deployments for fixes
[ ] Document all findings in incident ticket
```

**After Resolution**:
```
[ ] Verify fix in production
[ ] Monitor metrics for 24 hours
[ ] Remove debug flags
[ ] Update runbooks
[ ] Conduct postmortem
[ ] Implement preventive measures
```

---

## Anti-Patterns (Don't Do This)

**1. Making Untested Changes**
```
[FAIL] Bad: "Let's try increasing this timeout to 30s in production"
GOOD: Test timeout change in staging, deploy via canary
```

**2. Debugging Without Logs**
```
[FAIL] Bad: "I have no idea what happened, no logs"
GOOD: Comprehensive structured logging captures all events
```

**3. Modifying Production Data**
```
[FAIL] Bad: UPDATE users SET status = 'active' -- fix bad data
GOOD: Write migration script, test in staging, run with backup
```

**4. Restarting Services Randomly**
```
[FAIL] Bad: "It's slow, let's restart it"
GOOD: Profile, identify bottleneck, fix root cause
```

**5. Deploying Fixes Under Pressure**
```
[FAIL] Bad: "Push this fix now, we'll test later"
GOOD: Quick verification in staging, then canary deployment
```

---

## Tools for Production Debugging

**Log Aggregation**:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Datadog Logs
- Splunk
- Loki + Grafana

**APM & Tracing**:
- Datadog APM
- New Relic
- Jaeger / Zipkin
- AWS X-Ray
- Google Cloud Trace

**Error Tracking**:
- Sentry
- Rollbar
- Bugsnag

**Monitoring**:
- Prometheus + Grafana
- Datadog
- New Relic
- CloudWatch

**Synthetic Monitoring**:
- Datadog Synthetics
- Checkly
- Pingdom

---

## Real-World Example: Debugging Slow API

**Scenario**: `/api/orders` endpoint suddenly slow (P95: 200ms -> 2500ms)

**Investigation**:

```
1. CHECK METRICS (Datadog)
   - Latency spike started at 10:25 AM
   - Only affecting /api/orders endpoint
   - Error rate unchanged (still ~0.1%)

2. CHECK RECENT DEPLOYMENTS
   - Last deployment: 10:20 AM (5 minutes before spike)
   - Deployment: v1.2.4 (added order history feature)

3. ANALYZE TRACES (Jaeger)
   - Total time: 2500ms
   - Order Service: 2000ms (bottleneck)
     - DB Query: 1800ms <- Problem
     - Other: 200ms

4. CHECK DATABASE (Read Replica)
   EXPLAIN ANALYZE SELECT * FROM orders
   WHERE user_id = 'user-123'
   ORDER BY created_at DESC;

   Result: Table scan, 1M rows scanned
   MISSING INDEX on (user_id, created_at)

5. HYPOTHESIS CONFIRMED
   - New feature queries orders by user_id
   - Missing index causes full table scan
   - Under load, queries take 2s instead of 20ms

6. MITIGATION
   - Option A: Rollback to v1.2.3
   - Option B: Add index immediately

   DECISION: Add index (rollback removes feature)

   CREATE INDEX CONCURRENTLY idx_orders_user_created
   ON orders (user_id, created_at DESC);

7. VERIFY
   - Index created in 2 minutes
   - Latency dropped to 180ms (P95)
   - Feature works correctly
   - Monitor for 24 hours

8. POSTMORTEM
   - Root cause: Missing database index
   - Prevention: Add index performance testing to CI
   - Action items: Review all new queries for indexes
```

---

> **Remember**: Production debugging is about gathering evidence, forming hypotheses, and testing changes safely. Always have a rollback plan.
