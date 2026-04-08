# Bulkhead Isolation Pattern

Preventing resource exhaustion from cascading failures using compartmentalization.

---

## Pattern: Bulkhead Isolation

**Use when:** Preventing resource exhaustion from cascading failures.

**Bulkhead Pattern:**

```text
Thread Pool A (Payment API) - 10 threads
Thread Pool B (Email API) - 5 threads
Thread Pool C (Analytics API) - 3 threads

If Analytics API hangs, only 3 threads blocked.
Payment and Email APIs remain unaffected.
```

**Node.js Implementation (Semaphore Pattern):**

```javascript
class Semaphore {
  constructor(maxConcurrency) {
    this.maxConcurrency = maxConcurrency;
    this.currentConcurrency = 0;
    this.queue = [];
  }

  async acquire() {
    if (this.currentConcurrency < this.maxConcurrency) {
      this.currentConcurrency++;
      return;
    }

    // Wait in queue
    return new Promise((resolve) => {
      this.queue.push(resolve);
    });
  }

  release() {
    this.currentConcurrency--;
    if (this.queue.length > 0) {
      const resolve = this.queue.shift();
      this.currentConcurrency++;
      resolve();
    }
  }

  async runExclusive(fn) {
    await this.acquire();
    try {
      return await fn();
    } finally {
      this.release();
    }
  }
}

// Create bulkheads for different services
const paymentSemaphore = new Semaphore(10);
const emailSemaphore = new Semaphore(5);
const analyticsSemaphore = new Semaphore(3);

// Usage
async function processPayment(order) {
  return paymentSemaphore.runExclusive(async () => {
    return await paymentAPI.charge(order);
  });
}

async function sendEmail(recipient, message) {
  return emailSemaphore.runExclusive(async () => {
    return await emailAPI.send(recipient, message);
  });
}
```

---

## Thread Pool Sizing

**Formulas:**

```text
CPU-bound tasks: threads = CPU cores
I/O-bound tasks: threads = 2 * CPU cores (or higher)
Mixed workload: threads = CPU cores + (wait time / service time)

Example:
Service time: 10ms
Wait time: 90ms (network I/O)
CPU cores: 4

Optimal threads = 4 + (90 / 10) = 4 + 9 = 13 threads
```

**Sizing by Workload Type:**

| Workload | Formula | Example (4 cores) |
|----------|---------|-------------------|
| Pure CPU | CPU cores | 4 threads |
| Pure I/O | 2-10 × CPU cores | 8-40 threads |
| Mixed | cores + (wait/service) | 4 + (90/10) = 13 threads |
| Database | Connection pool size | 10-20 connections |

---

## Database Connection Pooling

**PostgreSQL with node-postgres:**

```javascript
const { Pool } = require('pg');

// Separate pools for different workloads
const readPool = new Pool({
  host: 'replica.db.example.com',
  max: 20,           // Max connections
  min: 2,            // Min idle connections
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

const writePool = new Pool({
  host: 'primary.db.example.com',
  max: 10,           // Smaller pool for writes
  min: 2,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Usage
async function getUser(userId) {
  const client = await readPool.connect();
  try {
    const result = await client.query('SELECT * FROM users WHERE id = $1', [userId]);
    return result.rows[0];
  } finally {
    client.release();
  }
}

async function createUser(userData) {
  const client = await writePool.connect();
  try {
    await client.query('BEGIN');
    const result = await client.query(
      'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
      [userData.name, userData.email]
    );
    await client.query('COMMIT');
    return result.rows[0];
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}
```

**Python with SQLAlchemy:**

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Separate engines for read and write
read_engine = create_engine(
    'postgresql://user:pass@replica.db.example.com/dbname',
    poolclass=QueuePool,
    pool_size=20,           # Max connections
    max_overflow=10,        # Additional connections during spikes
    pool_timeout=30,        # Wait timeout
    pool_pre_ping=True,     # Verify connections before use
)

write_engine = create_engine(
    'postgresql://user:pass@primary.db.example.com/dbname',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_pre_ping=True,
)
```

---

## Queue-Based Bulkheads

**Use when:** Need to throttle work and prevent overload.

```javascript
class WorkQueue {
  constructor(concurrency, queueSize) {
    this.concurrency = concurrency;
    this.queueSize = queueSize;
    this.running = 0;
    this.queue = [];
  }

  async enqueue(fn) {
    // Reject if queue full
    if (this.queue.length >= this.queueSize) {
      throw new Error('Queue full - load shedding');
    }

    // Queue the work
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this.processQueue();
    });
  }

  async processQueue() {
    if (this.running >= this.concurrency || this.queue.length === 0) {
      return;
    }

    this.running++;
    const { fn, resolve, reject } = this.queue.shift();

    try {
      const result = await fn();
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      this.running--;
      this.processQueue();
    }
  }
}

// Create separate queues for different services
const paymentQueue = new WorkQueue(10, 100);  // 10 concurrent, 100 queue size
const emailQueue = new WorkQueue(5, 500);     // 5 concurrent, 500 queue size

// Usage
async function processPayment(order) {
  try {
    return await paymentQueue.enqueue(async () => {
      return await paymentAPI.charge(order);
    });
  } catch (error) {
    if (error.message === 'Queue full - load shedding') {
      // Return 503 Service Unavailable
      throw new Error('Payment system overloaded, try again later');
    }
    throw error;
  }
}
```

---

## Monitoring Bulkheads

**Metrics to Track:**

```javascript
// Track queue depth and active workers
setInterval(() => {
  metrics.gauge('bulkhead.payment.active', paymentSemaphore.currentConcurrency);
  metrics.gauge('bulkhead.payment.queued', paymentSemaphore.queue.length);
  metrics.gauge('bulkhead.email.active', emailSemaphore.currentConcurrency);
  metrics.gauge('bulkhead.email.queued', emailSemaphore.queue.length);
}, 5000);

// Alert when pools saturate
if (paymentSemaphore.currentConcurrency >= paymentSemaphore.maxConcurrency * 0.8) {
  alerts.warn('Payment pool at 80% capacity');
}

if (emailSemaphore.queue.length > 100) {
  alerts.warn('Email queue backing up');
}
```

**Dashboard Queries (Prometheus):**

```promql
# Pool utilization
bulkhead_active_workers / bulkhead_max_workers

# Queue depth
bulkhead_queue_size

# Wait time in queue
rate(bulkhead_queue_wait_seconds_sum[5m]) / rate(bulkhead_queue_wait_seconds_count[5m])
```

---

## Partition-Scoped Failure Isolation

**Use when:** A single consumer or worker handles multiple logical partitions (e.g., Kafka partitions, sharded queues) and a failure in one partition must not affect others.

Partition-scoped isolation is narrower than service-level bulkheads — it applies within a single consumer handling multiple partitions:

- When a retry/DLQ publish fails for one partition, pause only that partition rather than sleeping the entire consumer loop or killing the consumer task.
- Failure-routing failures should produce visible host-level faulting (health check degradation, metrics), not leave a dead background task behind.
- A silent failure in one partition's retry path should not prevent other partitions from making progress.
- This pattern complements service-level bulkheads: bulkheads isolate between services; partition-scoped isolation operates within a single service's internal processing.

---

## Checklist

- [ ] Separate thread pools/queues for different services
- [ ] Pool sizes based on workload characteristics
- [ ] Timeouts prevent thread starvation
- [ ] Queue depth limits prevent memory exhaustion
- [ ] Bulkhead metrics monitored (active threads, queue depth)
- [ ] Alerts when pools saturate
- [ ] Load shedding when queue fills
- [ ] Database connection pools separated (read/write)
- [ ] Partition-scoped failures isolated (no cross-partition impact within a consumer)

---

## Related Resources

- [timeout-policies.md](timeout-policies.md) - Prevent thread starvation with timeouts
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) - Protect bulkheads with circuit breakers
- [resilience-checklists.md](resilience-checklists.md) - Comprehensive bulkhead hardening
