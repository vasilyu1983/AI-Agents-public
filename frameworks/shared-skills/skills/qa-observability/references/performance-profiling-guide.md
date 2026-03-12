# Performance Profiling Guide

Operational guide for profiling CPU, memory, and I/O performance in production applications. Platform-specific techniques and tools.

## Contents

- Node.js Performance Profiling
- Python Performance Profiling
- Database Query Profiling
- Frontend Performance Profiling
- Load Testing & Benchmarking
- Continuous Profiling
- Common Performance Bottlenecks
- Further Reading

## Node.js Performance Profiling

### CPU Profiling

#### Method 1: Built-in Profiler

**Use when:** Quick profiling in any environment

```bash
# Start app with profiler
node --prof app.js

# Run load test to generate workload
# Profiler writes isolate-*.log

# Process the log file
node --prof-process isolate-0x*.log > profile.txt

# View profile.txt
less profile.txt
```

**Profile output structure:**
```
Statistical profiling result from isolate-*.log, (12345 ticks, 678 unaccounted, 0 excluded).

 [Shared libraries]:
   ticks  total  nonlib   name
     45    0.4%

 [JavaScript]:
   ticks  total  nonlib   name
   1234   10.0%   10.1%  LazyCompile: *processOrder /app/orders.js:42:21
    890    7.2%    7.3%  LazyCompile: *validateUser /app/auth.js:15:18
    567    4.6%    4.7%  LazyCompile: *fetchFromDB /app/db.js:89:19
```

**Interpretation:**
- **processOrder**: 10% of CPU time (hotspot)
- **validateUser**: 7.2% of CPU time
- Look for functions with high ticks/total percentage

#### Method 2: Chrome DevTools

**Use when:** Visual flamegraph needed

```bash
# Start app with inspector
node --inspect app.js

# Open Chrome, go to chrome://inspect
# Click "Open dedicated DevTools for Node"
# Go to "Profiler" tab
# Click "Start" -> run workload -> "Stop"
```

**Flamegraph interpretation:**
```
main() ############################ (100%)
 |- processOrder() ############## (50%)
 |  |- validateUser() #### (20%)
 |  `- saveToDatabase() ##### (25%) <- Hotspot
 `- handleRequest() ######## (30%)
```

**Hotspot**: `saveToDatabase()` takes 25% of total CPU time

#### Method 3: Clinic.js (Recommended)

**Use when:** Comprehensive performance diagnosis

```bash
# Install
npm install -g clinic

# Run diagnostics
clinic doctor -- node app.js
# Open http://localhost:3000 and run workload
# Press Ctrl+C to stop
# Opens HTML report in browser

# CPU flame graph
clinic flame -- node app.js
# Opens flamegraph in browser

# Async operations analysis
clinic bubbleprof -- node app.js
# Shows async delay waterfall
```

**clinic doctor output:**
- Event loop delay
- CPU usage
- Memory usage
- Active handles

### Memory Profiling

#### Heap Snapshots

**Use when:** Investigating memory leaks

```javascript
// app.js - Add heap snapshot endpoint
const v8 = require('v8');
const fs = require('fs');

app.get('/heapsnapshot', (req, res) => {
  const filename = `heap-${Date.now()}.heapsnapshot`;
  const stream = v8.writeHeapSnapshot(filename);
  res.send(`Heap snapshot written to ${filename}`);
});

// Or take programmatically
function takeHeapSnapshot() {
  const filename = `heap-${Date.now()}.heapsnapshot`;
  v8.writeHeapSnapshot(filename);
  console.log(`Heap snapshot saved: ${filename}`);
}

// Take snapshot every hour
setInterval(takeHeapSnapshot, 60 * 60 * 1000);
```

**Analyzing heap snapshots:**

1. Take baseline snapshot (after warmup)
2. Run workload
3. Take second snapshot
4. Load both in Chrome DevTools (Memory tab)
5. Compare snapshots to find leaks

**Chrome DevTools -> Memory -> Load snapshot:**
```
Snapshot 1 (baseline): 50 MB
Snapshot 2 (after load): 150 MB

Comparison view:
- Array: +10,000 objects (+50 MB) <- Potential leak
- Closure: +5,000 objects (+20 MB)
```

#### Memory Usage Monitoring

```javascript
// Monitor memory usage
setInterval(() => {
  const usage = process.memoryUsage();
  console.log({
    rss: `${Math.round(usage.rss / 1024 / 1024)} MB`,       // Resident Set Size
    heapTotal: `${Math.round(usage.heapTotal / 1024 / 1024)} MB`,
    heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)} MB`,
    external: `${Math.round(usage.external / 1024 / 1024)} MB`,
    arrayBuffers: `${Math.round(usage.arrayBuffers / 1024 / 1024)} MB`,
  });
}, 10000); // Every 10 seconds
```

**Metrics:**
- **rss**: Total memory (heap + code + stack)
- **heapTotal**: V8 heap allocated
- **heapUsed**: V8 heap in use <- Monitor this for leaks
- **external**: C++ objects bound to JS
- **arrayBuffers**: Allocated for ArrayBuffers and SharedArrayBuffers

#### Heap Growth Detection

```javascript
let lastHeapUsed = 0;
let growthCount = 0;

setInterval(() => {
  const currentHeapUsed = process.memoryUsage().heapUsed;

  if (currentHeapUsed > lastHeapUsed) {
    growthCount++;
    if (growthCount > 10) {
      console.error('Possible memory leak detected (heap growing for 100 seconds)');
      // Take heap snapshot
      v8.writeHeapSnapshot(`leak-${Date.now()}.heapsnapshot`);
      growthCount = 0;
    }
  } else {
    growthCount = 0;
  }

  lastHeapUsed = currentHeapUsed;
}, 10000);
```

---

## Python Performance Profiling

### CPU Profiling

#### Method 1: cProfile (Built-in)

```python
import cProfile
import pstats
from pstats import SortKey

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

# Run your code
process_orders()

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats(SortKey.CUMULATIVE)
stats.print_stats(20)  # Top 20 functions
```

**Output:**
```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1000    0.500    0.001    2.345    0.002 orders.py:42(process_order)
     1000    0.800    0.001    1.500    0.001 db.py:89(fetch_from_db)
     5000    0.400    0.000    0.400    0.000 auth.py:15(validate_user)
```

**Metrics:**
- **ncalls**: Number of calls
- **tottime**: Time in function (excluding subcalls)
- **cumtime**: Time in function (including subcalls) <- Most important

#### Method 2: py-spy (Sampling Profiler)

**Use when:** Profiling production without code changes

```bash
# Install
pip install py-spy

# Attach to running process
py-spy top --pid 12345

# Generate flamegraph
py-spy record -o profile.svg --pid 12345 --duration 60

# Profile subprocess
py-spy record -o profile.svg -- python app.py
```

**py-spy output (top):**
```
Total Samples: 12000
  process_order    45.2% (5424)
    fetch_from_db  30.1% (3612) <- Hotspot
    validate_user  10.5% (1260)
  handle_request   25.3% (3036)
```

### Memory Profiling

#### Method 1: tracemalloc (Built-in)

```python
import tracemalloc

# Start tracing
tracemalloc.start()

# Run your code
process_large_dataset()

# Get current memory usage
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")

# Get top memory allocations
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)
```

**Output:**
```
orders.py:145: 52.3 MB
db.py:89: 31.2 MB <- Large allocation
cache.py:42: 18.5 MB
```

#### Method 2: memory_profiler

```python
from memory_profiler import profile

@profile
def process_orders():
    orders = fetch_orders()  # Line 45
    for order in orders:     # Line 46
        process(order)        # Line 47
    return results            # Line 48

process_orders()
```

**Output:**
```
Line #    Mem usage    Increment   Line Contents
================================================
    45     50.2 MB      0.0 MB   orders = fetch_orders()
    46    150.5 MB    100.3 MB   for order in orders: <- Memory spike
    47    152.1 MB      1.6 MB       process(order)
    48    152.1 MB      0.0 MB   return results
```

---

## Database Query Profiling

### PostgreSQL

#### EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT o.*, u.name, u.email
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.status = 'pending'
  AND o.created_at > NOW() - INTERVAL '7 days'
ORDER BY o.created_at DESC
LIMIT 100;
```

**Output:**
```
Limit  (cost=1234.56..1234.81 rows=100 width=256) (actual time=45.123..45.234 rows=100 loops=1)
  ->  Sort  (cost=1234.56..1250.78 rows=6489 width=256) (actual time=45.120..45.180 rows=100 loops=1)
        Sort Key: o.created_at DESC
        Sort Method: top-N heapsort  Memory: 85kB
        ->  Hash Join  (cost=15.75..1100.45 rows=6489 width=256) (actual time=0.250..38.456 rows=6500 loops=1)
              Hash Cond: (o.user_id = u.id)
              ->  Seq Scan on orders o  (cost=0.00..1000.00 rows=6500 width=200) (actual time=0.010..25.678 rows=6500 loops=1)
                    Filter: ((status = 'pending') AND (created_at > (now() - '7 days'::interval)))
                    Rows Removed by Filter: 23500 <- Problem: scanning 30k rows to get 6.5k
              ->  Hash  (cost=10.50..10.50 rows=420 width=56) (actual time=0.230..0.230 rows=420 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 35kB
                    ->  Seq Scan on users u  (cost=0.00..10.50 rows=420 width=56) (actual time=0.005..0.120 rows=420 loops=1)
Planning Time: 0.345 ms
Execution Time: 45.567 ms <- Total query time
```

**Red flags:**
- **Seq Scan** instead of Index Scan (full table scan)
- **Rows Removed by Filter** high (inefficient filtering)
- **actual time** >> **cost** (estimation wrong)

**Fix:** Add index
```sql
CREATE INDEX idx_orders_status_created_at ON orders (status, created_at DESC);
```

#### Slow Query Log

```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000; -- Log queries > 1s
SELECT pg_reload_conf();

-- View slow queries (PostgreSQL 13+)
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### MySQL

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1; -- Queries slower than 1 second

-- Analyze query
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';
```

### MongoDB

```javascript
// Enable profiling
db.setProfilingLevel(1, { slowms: 100 }); // Log queries > 100ms

// View slow queries
db.system.profile.find({ millis: { $gt: 100 } }).sort({ ts: -1 }).limit(10);

// Explain query
db.orders.find({ status: 'pending' }).explain('executionStats');
```

**Output:**
```json
{
  "executionStats": {
    "executionTimeMillis": 152,
    "totalDocsExamined": 50000, <- Problem: full collection scan
    "totalKeysExamined": 0,     <- No index used
    "nReturned": 1000
  }
}
```

**Fix:** Add index
```javascript
db.orders.createIndex({ status: 1, created_at: -1 });
```

---

## Frontend Performance Profiling

### Core Web Vitals

```javascript
// Install web-vitals
npm install web-vitals

// Track Core Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating, // "good", "needs-improvement", "poor"
    id: metric.id,
  });

  // Send to analytics endpoint
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/analytics', body);
  } else {
    fetch('/analytics', { method: 'POST', body, keepalive: true });
  }
}

// Measure vitals
getCLS(sendToAnalytics);  // Cumulative Layout Shift (< 0.1 good)
getFID(sendToAnalytics);  // First Input Delay (< 100ms good)
getFCP(sendToAnalytics);  // First Contentful Paint (< 1.8s good)
getLCP(sendToAnalytics);  // Largest Contentful Paint (< 2.5s good)
getTTFB(sendToAnalytics); // Time to First Byte (< 800ms good)
```

### Chrome Lighthouse

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://example.com --output html --output-path report.html

# CI/CD integration
lighthouse https://example.com --output json --quiet > lighthouse.json

# Performance budgets
lighthouse https://example.com --budget-path=budget.json
```

**budget.json:**
```json
[
  {
    "path": "/*",
    "timings": [
      {
        "metric": "first-contentful-paint",
        "budget": 2000
      },
      {
        "metric": "interactive",
        "budget": 3500
      }
    ],
    "resourceSizes": [
      {
        "resourceType": "script",
        "budget": 300
      },
      {
        "resourceType": "image",
        "budget": 500
      },
      {
        "resourceType": "total",
        "budget": 1000
      }
    ]
  }
]
```

### Chrome DevTools Performance

**Steps:**
1. Open Chrome DevTools -> Performance tab
2. Click Record (or Cmd+E)
3. Perform actions on page
4. Click Stop
5. Analyze timeline

**Timeline view:**
```
Main Thread:
|- Task (Long) [245ms] <- Blocking the main thread
|  |- parseJSON [150ms] <- Bottleneck
|  `- renderComponent [95ms]
|- Task [15ms]
`- Idle
```

**Red flags:**
- Long tasks (>50ms) block main thread
- Large paint times (>16ms for 60fps)
- Many forced reflows (layout thrashing)

---

## Load Testing & Benchmarking

### k6 (Recommended)

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const orderDuration = new Trend('order_duration');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
    http_req_failed: ['rate<0.01'],                  // Error rate < 1%
    errors: ['rate<0.05'],                           // Custom error rate < 5%
  },
};

export default function () {
  const startTime = Date.now();

  const res = http.post('https://api.example.com/orders', JSON.stringify({
    items: [{ id: 123, quantity: 2 }],
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  const duration = Date.now() - startTime;
  orderDuration.add(duration);

  const success = check(res, {
    'status is 201': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'order ID returned': (r) => JSON.parse(r.body).order_id !== undefined,
  });

  errorRate.add(!success);

  sleep(1);
}
```

**Run load test:**
```bash
k6 run load-test.js

# Cloud execution
k6 cloud load-test.js
```

**Output:**
```
     [check] status is 201
     [check] response time < 500ms
     [check] order ID returned

     checks.........................: 100.00% [check] 3000      [x] 0
     data_received..................: 1.2 MB  4.0 kB/s
     data_sent......................: 500 kB  1.7 kB/s
     http_req_duration..............: avg=245ms min=120ms med=230ms max=980ms p(90)=350ms p(95)=450ms p(99)=800ms
     http_req_failed................: 0.00%   [check] 0        [x] 1000
     iterations.....................: 1000    3.3/s
     vus............................: 200     min=0      max=200
```

### Apache Bench (Quick Tests)

```bash
# 1000 requests, 100 concurrent
ab -n 1000 -c 100 -H "Authorization: Bearer token" https://api.example.com/orders

# POST request
ab -n 1000 -c 100 -p payload.json -T application/json https://api.example.com/orders
```

---

## Continuous Profiling

### Profiling in Production

**Use sampling profilers** (low overhead):
- **Node.js**: Clinic.js, 0x
- **Python**: py-spy, austin
- **Go**: pprof
- **Java**: async-profiler

**Setup:**
```bash
# Node.js with Clinic.js
pm2 start app.js --name api -- --prof

# Python with py-spy
py-spy record -o /tmp/profile.svg --pid $(pgrep -f "python app.py") --duration 300 &

# Scheduled profiling (every 6 hours)
crontab -e
0 */6 * * * py-spy record -o /var/log/profile-$(date +\%Y\%m\%d-\%H\%M).svg --pid $(pgrep -f app.py) --duration 60
```

---

## Common Performance Bottlenecks

### 1. N+1 Query Problem

[FAIL] **Bad (N+1 queries):**
```javascript
// 1 query to get orders
const orders = await Order.findAll();

// N queries to get user for each order
for (const order of orders) {
  const user = await User.findById(order.userId); // <- N queries
}
```

[OK] **Good (2 queries total):**
```javascript
const orders = await Order.findAll();
const userIds = orders.map(o => o.userId);
const users = await User.findAll({ where: { id: userIds } });
const userMap = new Map(users.map(u => [u.id, u]));

for (const order of orders) {
  const user = userMap.get(order.userId);
}
```

### 2. Synchronous I/O

[FAIL] **Bad (blocks event loop):**
```javascript
const data = fs.readFileSync('/large-file.json'); // <- Blocks
const parsed = JSON.parse(data);
```

[OK] **Good (async):**
```javascript
const data = await fs.promises.readFile('/large-file.json');
const parsed = JSON.parse(data);
```

### 3. Large Payload Processing

[FAIL] **Bad (loads entire file into memory):**
```javascript
const data = await fs.promises.readFile('/10gb-file.csv');
processData(data); // <- Memory spike
```

[OK] **Good (streaming):**
```javascript
const stream = fs.createReadStream('/10gb-file.csv');
stream.on('data', chunk => processChunk(chunk));
```

### 4. No Caching

[FAIL] **Bad (fetches from DB every time):**
```javascript
app.get('/api/config', async (req, res) => {
  const config = await Config.findOne(); // <- DB query every request
  res.json(config);
});
```

[OK] **Good (cached):**
```javascript
let configCache = null;
let cacheTime = 0;
const CACHE_TTL = 60000; // 1 minute

app.get('/api/config', async (req, res) => {
  if (!configCache || Date.now() - cacheTime > CACHE_TTL) {
    configCache = await Config.findOne();
    cacheTime = Date.now();
  }
  res.json(configCache);
});
```

---

## Further Reading

- [Node.js Performance Best Practices](https://nodejs.org/en/docs/guides/simple-profiling/)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)
- [web.dev - Performance](https://web.dev/performance/)
- [k6 Documentation](https://k6.io/docs/)
- [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
