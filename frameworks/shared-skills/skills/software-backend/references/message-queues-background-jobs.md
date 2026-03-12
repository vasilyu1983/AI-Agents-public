# Message Queues & Background Jobs

Comprehensive guide for message queue patterns, background job design, broker comparison, and reliability guarantees. Covers BullMQ, Redis, SQS, Kafka, RabbitMQ, idempotent job design, dead letter queues, scheduling, and observability.

## Contents

- [BullMQ Patterns](#bullmq-patterns)
- [Message Broker Comparison](#message-broker-comparison)
- [Idempotent Job Design](#idempotent-job-design)
- [Dead Letter Queues and Failure Handling](#dead-letter-queues-and-failure-handling)
- [Job Scheduling and Cron](#job-scheduling-and-cron)
- [Observability for Background Jobs](#observability-for-background-jobs)
- [Fan-Out and Fan-In Patterns](#fan-out-and-fan-in-patterns)
- [Delivery Guarantees](#delivery-guarantees)
- [Anti-Patterns](#anti-patterns)
- [Decision Framework](#decision-framework)
- [Cross-References](#cross-references)

---

## BullMQ Patterns

### Basic Job Processing

```typescript
import { Queue, Worker, QueueEvents } from 'bullmq';
import IORedis from 'ioredis';

const connection = new IORedis({
  host: process.env.REDIS_HOST,
  port: 6379,
  maxRetriesPerRequest: null,  // Required for BullMQ
});

// Producer: add jobs to queue
const emailQueue = new Queue('email', { connection });

await emailQueue.add('send-welcome', {
  userId: 'user-123',
  templateId: 'welcome-email',
}, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 1000 },
  removeOnComplete: { count: 1000 },  // Keep last 1000 completed jobs
  removeOnFail: { count: 5000 },      // Keep last 5000 failed jobs
});

// Consumer: process jobs
const worker = new Worker('email', async (job) => {
  const { userId, templateId } = job.data;

  await job.updateProgress(10);
  const user = await getUserById(userId);

  await job.updateProgress(50);
  await sendEmail(user.email, templateId);

  await job.updateProgress(100);
  return { sentTo: user.email };
}, {
  connection,
  concurrency: 5,          // Process 5 jobs in parallel
  limiter: {
    max: 10,               // Max 10 jobs
    duration: 1000,         // Per second (rate limiting)
  },
});

worker.on('completed', (job, result) => {
  logger.info({ jobId: job.id, result }, 'Job completed');
});

worker.on('failed', (job, err) => {
  logger.error({ jobId: job?.id, err }, 'Job failed');
});
```

### Job Types and Patterns

| Pattern | BullMQ Feature | Use When |
|---------|---------------|----------|
| Simple job | `queue.add()` | One-off tasks (send email, resize image) |
| Delayed job | `delay` option | Future execution (reminder in 24h) |
| Repeatable job | `repeat` option | Recurring tasks (daily report) |
| Priority job | `priority` option | Urgent tasks first |
| Flow (parent-child) | `FlowProducer` | Multi-step workflows with dependencies |
| Bulk add | `queue.addBulk()` | Batch insertion of many jobs |
| Rate limited | `limiter` option | API rate limit compliance |

### Flow (Parent-Child Dependencies)

```typescript
import { FlowProducer } from 'bullmq';

const flowProducer = new FlowProducer({ connection });

// Parent job depends on child jobs completing first
await flowProducer.add({
  name: 'generate-report',
  queueName: 'reports',
  data: { reportId: 'rpt-001' },
  children: [
    {
      name: 'fetch-sales-data',
      queueName: 'data-fetch',
      data: { source: 'sales', reportId: 'rpt-001' },
    },
    {
      name: 'fetch-inventory-data',
      queueName: 'data-fetch',
      data: { source: 'inventory', reportId: 'rpt-001' },
    },
    {
      name: 'fetch-customer-data',
      queueName: 'data-fetch',
      data: { source: 'customers', reportId: 'rpt-001' },
    },
  ],
});

// Parent job runs only after ALL children complete
// Access child results via job.getChildrenValues()
```

### Graceful Shutdown

```typescript
async function shutdown() {
  // 1. Close the worker (finish current jobs)
  await worker.close();

  // 2. Close the queue (stop accepting jobs)
  await emailQueue.close();

  // 3. Close Redis connection
  await connection.quit();
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
```

---

## Message Broker Comparison

| Feature | Redis / BullMQ | SQS | Kafka | RabbitMQ |
|---------|---------------|-----|-------|----------|
| Model | Job queue | Message queue | Event log | Message broker |
| Ordering | FIFO per queue | FIFO (optional) | Per-partition ordering | Per-queue FIFO |
| Delivery | At-least-once | At-least-once | At-least-once (configurable) | At-least-once / at-most-once |
| Retention | Configurable (Redis memory) | 4 days (configurable to 14) | Configurable (days/size/forever) | Until consumed |
| Throughput | 10K-100K/s | 3K/s (standard), 30K/s (FIFO) | 1M+/s per cluster | 50K-100K/s |
| Replay | Limited (requires event store) | No replay | Full replay from any offset | No replay |
| Scaling | Redis cluster | Automatic (managed) | Partition-based | Prefetch + consumers |
| Managed options | Upstash, AWS ElastiCache | AWS native | Confluent, MSK, Redpanda | CloudAMQP, AmazonMQ |
| Best for | Background jobs, task queues | AWS-native workflows, serverless | Event streaming, log aggregation | Complex routing, pub/sub |

### Selection Decision Tree

```text
What do you need?
  ├─ Background job processing (retries, delays, priorities)
  │   └─ BullMQ (Redis-backed, mature, Node.js ecosystem)
  │
  ├─ AWS-native, serverless, managed
  │   └─ SQS + Lambda (zero infrastructure management)
  │
  ├─ Event streaming, replay, high throughput
  │   ├─ Kafka / Redpanda (self-managed or Confluent)
  │   └─ Use when: event sourcing, real-time analytics, CDC
  │
  ├─ Complex routing (topic, fanout, headers)
  │   └─ RabbitMQ (exchange types, routing keys, dead letter)
  │
  └─ Simple pub/sub, real-time notifications
      └─ Redis Pub/Sub (ephemeral, no persistence needed)
```

---

## Idempotent Job Design

### Why Idempotency Matters

```text
Jobs will be delivered more than once because:
  1. Worker crashes after processing but before acknowledging
  2. Network timeout causes retry
  3. Duplicate messages from producer
  4. Manual re-queue for failed jobs

If a job is NOT idempotent, duplicate processing causes:
  - Double charges to customers
  - Duplicate emails sent
  - Inventory decremented twice
  - Inconsistent data state
```

### Idempotency Patterns

**Pattern 1: Idempotency Key**

```typescript
async function processPayment(job: Job) {
  const { orderId, amount, idempotencyKey } = job.data;

  // Check if already processed
  const existing = await redis.get(`idem:payment:${idempotencyKey}`);
  if (existing) {
    logger.info({ idempotencyKey }, 'Payment already processed, skipping');
    return JSON.parse(existing);
  }

  // Process payment
  const result = await paymentGateway.charge(orderId, amount);

  // Mark as processed (with TTL for cleanup)
  await redis.set(
    `idem:payment:${idempotencyKey}`,
    JSON.stringify(result),
    'EX',
    86400 * 7  // 7 days
  );

  return result;
}
```

**Pattern 2: Database Constraint**

```typescript
async function processOrder(job: Job) {
  const { orderId, eventId } = job.data;

  try {
    // Use unique constraint to prevent duplicate processing
    await db.processedEvents.create({
      data: { eventId, processedAt: new Date() },
    });
  } catch (error) {
    if (error.code === 'P2002') {  // Prisma unique constraint violation
      logger.info({ eventId }, 'Event already processed');
      return;
    }
    throw error;
  }

  // Process the order (only runs once per eventId)
  await fulfillOrder(orderId);
}
```

**Pattern 3: Conditional Update**

```sql
-- Only update if current state matches expected state
UPDATE orders
SET status = 'shipped', updated_at = now()
WHERE id = $1 AND status = 'paid';
-- Returns 0 rows affected if already shipped (idempotent)
```

### Idempotency Checklist

- [ ] Every job has a unique idempotency key (job ID, event ID, or business key)
- [ ] Processing check happens BEFORE side effects
- [ ] Side effects are guarded (DB constraints, conditional updates)
- [ ] External API calls use idempotency keys (Stripe, etc.)
- [ ] Idempotency records have TTL for cleanup
- [ ] Logging clearly indicates when duplicates are skipped

---

## Dead Letter Queues and Failure Handling

### BullMQ Failure Handling

```typescript
// Configure retry behavior per job
await queue.add('process-webhook', webhookData, {
  attempts: 5,
  backoff: {
    type: 'exponential',
    delay: 2000,  // 2s, 4s, 8s, 16s, 32s
  },
});

// Custom backoff strategy
await queue.add('critical-job', data, {
  attempts: 10,
  backoff: {
    type: 'custom',
  },
});

// In worker: implement custom backoff
const worker = new Worker('critical', processor, {
  settings: {
    backoffStrategy: (attemptsMade: number) => {
      // Fibonacci backoff: 1s, 1s, 2s, 3s, 5s, 8s, 13s, 21s, 34s, 55s
      const fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55];
      return (fib[attemptsMade - 1] || 55) * 1000;
    },
  },
});
```

### Dead Letter Queue Pattern

```typescript
// Monitor failed jobs and move to DLQ after exhausting retries
const queueEvents = new QueueEvents('orders', { connection });

queueEvents.on('failed', async ({ jobId, failedReason }) => {
  const job = await Job.fromId(queue, jobId);
  if (!job) return;

  // If all retries exhausted, move to DLQ
  if (job.attemptsMade >= job.opts.attempts!) {
    await dlqQueue.add('failed-order', {
      originalJobId: jobId,
      originalQueue: 'orders',
      data: job.data,
      failedReason,
      attempts: job.attemptsMade,
      failedAt: new Date().toISOString(),
    });

    // Alert on DLQ growth
    const dlqSize = await dlqQueue.getJobCounts('waiting');
    if (dlqSize.waiting > 100) {
      await alerting.critical('DLQ size exceeds threshold', { dlqSize });
    }
  }
});
```

### Failure Classification

| Failure Type | Retry? | Example |
|-------------|--------|---------|
| Transient (network timeout) | Yes, with backoff | HTTP 503, connection reset |
| Rate limited | Yes, with longer backoff | HTTP 429, API quota exceeded |
| Bad input (validation) | No (fix data, re-submit) | Invalid email format |
| Business logic error | No (requires investigation) | Insufficient funds |
| Infrastructure failure | Yes, after fix | Database down, Redis unavailable |
| Poison message | No (move to DLQ) | Unparseable payload, corrupted data |

```typescript
// Classify errors in worker to decide retry behavior
const worker = new Worker('orders', async (job) => {
  try {
    await processOrder(job.data);
  } catch (error) {
    if (error instanceof ValidationError) {
      // Do NOT retry validation errors
      await moveToDLQ(job, error);
      return; // Return without throwing to mark as completed
    }
    if (error.status === 429) {
      // Rate limited — retry with extra delay
      throw new DelayedError(error.message, 60_000); // 60s delay
    }
    // All other errors: let BullMQ retry with configured backoff
    throw error;
  }
});
```

---

## Job Scheduling and Cron

### Repeatable Jobs (BullMQ)

```typescript
// Cron-based repeatable jobs
await queue.add('daily-report', { reportType: 'sales' }, {
  repeat: {
    pattern: '0 8 * * *',  // Every day at 8 AM UTC
    tz: 'America/New_York', // Timezone-aware
  },
  jobId: 'daily-sales-report',  // Stable ID prevents duplicates
});

await queue.add('cleanup-expired', {}, {
  repeat: {
    every: 60_000,  // Every 60 seconds
  },
  jobId: 'cleanup-expired-sessions',
});

// List all repeatable jobs
const repeatableJobs = await queue.getRepeatableJobs();
// Remove a repeatable job
await queue.removeRepeatableByKey(repeatableJobs[0].key);
```

### Scheduling Best Practices

| Concern | Recommendation |
|---------|---------------|
| Timezone | Always specify timezone explicitly; UTC is safest for server jobs |
| Overlap prevention | Use a stable `jobId` so BullMQ deduplicates |
| Distributed cron | Only ONE instance should create repeatable jobs (use advisory lock or leader election) |
| Missed schedules | BullMQ does NOT catch up missed runs; if the process was down, those runs are skipped |
| Long-running crons | Set `timeout` on jobs; monitor for stuck jobs |

### Distributed Cron Locking

```typescript
// Ensure only one instance registers repeatable jobs
import { Mutex } from 'redis-semaphore';

const mutex = new Mutex(connection, 'cron-registration-lock', {
  lockTimeout: 30_000,
  acquireTimeout: 5_000,
});

async function registerCronJobs() {
  const acquired = await mutex.tryAcquire();
  if (!acquired) {
    logger.info('Another instance is registering cron jobs');
    return;
  }

  try {
    await queue.add('daily-report', {}, {
      repeat: { pattern: '0 8 * * *' },
      jobId: 'daily-report',
    });
  } finally {
    await mutex.release();
  }
}
```

---

## Observability for Background Jobs

### Key Metrics

| Metric | Description | Alert On |
|--------|-------------|----------|
| `queue.waiting` | Jobs waiting to be processed | Growing queue (consumers too slow) |
| `queue.active` | Jobs currently being processed | Stuck jobs (no movement) |
| `queue.completed` | Completed jobs per time window | Rate drop (processing issues) |
| `queue.failed` | Failed jobs per time window | Spike (upstream error) |
| `queue.delayed` | Delayed jobs count | Unexpected growth |
| `job.duration` | Processing time per job | P95 exceeding threshold |
| `job.attempts` | Retry count per job | Average > 1 (reliability issue) |
| `dlq.size` | Dead letter queue depth | Any growth |

### Structured Logging for Jobs

```typescript
const worker = new Worker('orders', async (job) => {
  const startTime = Date.now();
  const logContext = {
    jobId: job.id,
    jobName: job.name,
    queue: 'orders',
    attempt: job.attemptsMade + 1,
    data: { orderId: job.data.orderId },  // Log safe fields only
  };

  logger.info(logContext, 'Job started');

  try {
    const result = await processOrder(job.data);
    const duration = Date.now() - startTime;

    logger.info({ ...logContext, duration, result: 'success' }, 'Job completed');
    metrics.histogram('job.duration', duration, { queue: 'orders', name: job.name });
    metrics.increment('job.completed', { queue: 'orders' });

    return result;
  } catch (error) {
    const duration = Date.now() - startTime;
    logger.error({ ...logContext, duration, error }, 'Job failed');
    metrics.increment('job.failed', { queue: 'orders' });
    throw error;
  }
});
```

### OpenTelemetry Integration

```typescript
import { trace, SpanKind } from '@opentelemetry/api';

const tracer = trace.getTracer('background-jobs');

const worker = new Worker('orders', async (job) => {
  const span = tracer.startSpan(`job:${job.name}`, {
    kind: SpanKind.CONSUMER,
    attributes: {
      'job.id': job.id!,
      'job.name': job.name,
      'job.queue': 'orders',
      'job.attempt': job.attemptsMade + 1,
    },
  });

  try {
    const result = await trace.getTracer('background-jobs')
      .startActiveSpan('process-order', async (childSpan) => {
        const result = await processOrder(job.data);
        childSpan.end();
        return result;
      });
    span.setStatus({ code: 0 });
    return result;
  } catch (error) {
    span.setStatus({ code: 2, message: (error as Error).message });
    throw error;
  } finally {
    span.end();
  }
});
```

---

## Fan-Out and Fan-In Patterns

### Fan-Out: One Event, Many Consumers

```typescript
// Publish one event, multiple queues consume it
async function onOrderPlaced(order: Order) {
  await Promise.all([
    emailQueue.add('order-confirmation', { orderId: order.id }),
    inventoryQueue.add('reserve-items', { orderId: order.id, items: order.items }),
    analyticsQueue.add('track-purchase', { orderId: order.id, total: order.total }),
    notificationQueue.add('push-notification', { userId: order.userId }),
  ]);
}
```

### Fan-In: Many Jobs, One Aggregation

```typescript
// Use BullMQ flows for fan-in
const flow = await flowProducer.add({
  name: 'aggregate-report',
  queueName: 'reports',
  data: { reportId: 'monthly-2026-01' },
  children: [
    { name: 'fetch-region', queueName: 'data-fetch', data: { region: 'us' } },
    { name: 'fetch-region', queueName: 'data-fetch', data: { region: 'eu' } },
    { name: 'fetch-region', queueName: 'data-fetch', data: { region: 'apac' } },
  ],
});

// Parent job: aggregate when all children complete
const reportWorker = new Worker('reports', async (job) => {
  const childResults = await job.getChildrenValues();
  // childResults contains all region data
  const report = aggregateRegions(Object.values(childResults));
  await saveReport(job.data.reportId, report);
});
```

### Batch Processing Pattern

```typescript
// Process items in batches to reduce overhead
const BATCH_SIZE = 100;
const BATCH_TIMEOUT = 5000; // 5 seconds

let batch: any[] = [];
let timer: NodeJS.Timeout;

async function addToBatch(item: any) {
  batch.push(item);

  if (batch.length >= BATCH_SIZE) {
    await flushBatch();
  } else if (!timer) {
    timer = setTimeout(flushBatch, BATCH_TIMEOUT);
  }
}

async function flushBatch() {
  if (batch.length === 0) return;

  clearTimeout(timer);
  const items = batch.splice(0);
  await processBatch(items);  // Bulk insert, bulk API call, etc.
}
```

---

## Delivery Guarantees

### Comparison

| Guarantee | Description | Achievable With |
|-----------|-------------|-----------------|
| At-most-once | Message processed 0 or 1 times. Fastest, lossy. | Fire-and-forget, no ACK |
| At-least-once | Message processed 1 or more times. Requires idempotency. | ACK after processing + retries |
| Exactly-once | Message processed exactly 1 time. Hard to achieve. | Idempotent consumer + transactional outbox |

### At-Least-Once (Default for BullMQ, SQS, Kafka)

```text
Producer → Broker → Consumer
                      │
                      ├─ Process message
                      ├─ ACK to broker (mark as done)
                      │
                      └─ If crash before ACK → broker redelivers → duplicate
                         → MUST handle idempotently
```

### Exactly-Once (Transactional Outbox Pattern)

```typescript
// Write event AND business data in the same database transaction
async function placeOrder(orderData: CreateOrderData) {
  await db.$transaction(async (tx) => {
    // 1. Write business data
    const order = await tx.order.create({ data: orderData });

    // 2. Write outbox event (same transaction)
    await tx.outboxEvent.create({
      data: {
        aggregateId: order.id,
        eventType: 'OrderPlaced',
        payload: JSON.stringify(order),
        published: false,
      },
    });
  });
  // Both write or neither writes (ACID)
}

// Separate process: poll outbox and publish events
async function publishOutboxEvents() {
  const events = await db.outboxEvent.findMany({
    where: { published: false },
    orderBy: { createdAt: 'asc' },
    take: 100,
  });

  for (const event of events) {
    await queue.add(event.eventType, JSON.parse(event.payload));
    await db.outboxEvent.update({
      where: { id: event.id },
      data: { published: true, publishedAt: new Date() },
    });
  }
}
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No idempotency | Duplicate processing on retries | Idempotency key + dedup check |
| Unbounded retries | Broken jobs retry forever, wasting resources | Set `attempts` limit, use DLQ |
| Large payloads in jobs | Redis memory bloat, slow serialization | Store data in DB, pass ID in job |
| No job timeout | Stuck jobs block workers | Set `timeout` per job type |
| Shared queue for everything | Priority inversion, noisy neighbors | Separate queues per concern |
| No DLQ monitoring | Failed jobs silently accumulate | Alert on DLQ depth |
| Fire-and-forget without logging | Lost jobs, no debugging trail | Always log job lifecycle |
| Processing without tracing | Cannot correlate jobs with requests | Pass `correlationId`, use OTel |

---

## Decision Framework

### Choosing a Message Broker

```text
1. Is this a background job (task queue)?                    → BullMQ (Redis)
2. Is this AWS-native, serverless?                           → SQS + Lambda
3. Do you need event replay / streaming?                     → Kafka or Redpanda
4. Do you need complex routing (topic, headers, fanout)?     → RabbitMQ
5. Do you need managed, zero-ops?                            → SQS (AWS) or Upstash (Redis)
6. Is throughput > 100K events/sec?                          → Kafka
7. Simple pub/sub, ephemeral?                                → Redis Pub/Sub
```

### Sizing Your Queue Workers

```text
Workers per queue = ceil(expected_jobs_per_second / (1 / avg_processing_time_seconds))

Example:
  - 100 jobs/second expected
  - Average processing time: 200ms (0.2s)
  - Jobs per worker per second: 1 / 0.2 = 5
  - Workers needed: 100 / 5 = 20 workers (concurrency setting)

Add 20-50% headroom for spikes.
Monitor queue depth to adjust.
```

---

## Cross-References

- [nodejs-best-practices.md](nodejs-best-practices.md) — Node.js process management, worker threads
- [database-patterns.md](database-patterns.md) — Transactional outbox, database connection patterns
- [infrastructure-economics.md](infrastructure-economics.md) — Queue infrastructure cost modeling
- [../../software-architecture-design/references/data-architecture-patterns.md](../../software-architecture-design/references/data-architecture-patterns.md) — Saga patterns, event sourcing, CQRS
- [../../software-architecture-design/references/modern-patterns.md](../../software-architecture-design/references/modern-patterns.md) — Event-driven architecture patterns
- [../../software-clean-code-standard/references/resilience-utilities.md](../../software-clean-code-standard/references/resilience-utilities.md) — Retry and circuit breaker patterns
