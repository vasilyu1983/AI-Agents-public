# Timeout Policies

Preventing resource exhaustion from slow dependencies with comprehensive timeout strategies.

---

## Pattern: Timeout Policies

**Use when:** Preventing resource exhaustion from slow dependencies.

**Timeout Types:**

**1. Overall Request Deadline (Typical):**

```javascript
// Overall request deadline (fetch does not expose a portable "connect timeout")
const response = await fetch('https://api.example.com/data', {
  signal: AbortSignal.timeout(5000), // 5s total deadline
});
```

**2. Request Deadline (AbortController):**

```javascript
// Total time for request + response
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 10000);

try {
  const response = await fetch('https://api.example.com/data', {
    signal: controller.signal,
  });
  const data = await response.json();
  return data;
} finally {
  clearTimeout(timeoutId);
}
```

**3. Idle / Read Timeout (Streaming):**

Idle/read timeouts are client-specific. For streaming responses, enforce a per-chunk deadline in your HTTP client (or implement an application-level watchdog) rather than relying on a single global timer.

---

## Database Query Timeouts

**PostgreSQL with Prisma:**

```javascript
// Postgres statement_timeout (one option): set it per-transaction.
// Note: adjust the model/query to match your schema.
const result = await prisma.$transaction(async (tx) => {
  await tx.$executeRawUnsafe('SET LOCAL statement_timeout = 5000'); // 5s
  return tx.order.findMany({ where: { userId } });
});
```

**MySQL:**

```javascript
await connection.query({
  sql: 'SELECT * FROM orders WHERE user_id = ?',
  timeout: 5000,
  values: [userId],
});
```

**PostgreSQL with node-postgres:**

```javascript
const client = await pool.connect();
try {
  // Set statement timeout for this connection
  await client.query('SET statement_timeout = 5000'); // 5s
  const result = await client.query('SELECT * FROM large_table WHERE condition = $1', [value]);
  return result.rows;
} finally {
  client.release();
}
```

**Python SQLAlchemy:**

```python
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
import asyncio

async def query_with_timeout(session, query, timeout=5):
    try:
        # Set statement timeout
        await session.execute(text(f"SET statement_timeout = '{timeout * 1000}'"))
        result = await session.execute(query)
        return result.fetchall()
    except DBAPIError as e:
        if 'statement timeout' in str(e):
            raise TimeoutError('Query exceeded timeout')
        raise
```

---

## HTTP Client Timeouts

**Node.js fetch with AbortController:**

```javascript
async function fetchWithTimeout(url, options = {}, timeout = 10000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw error;
  } finally {
    clearTimeout(id);
  }
}

// Usage
try {
  const data = await fetchWithTimeout('https://api.example.com/data', {}, 5000);
} catch (error) {
  console.error('Request failed:', error);
}
```

**Python requests:**

```python
import requests

try:
    response = requests.get(
        'https://api.example.com/data',
        timeout=(5, 10)  # (connect timeout, read timeout)
    )
    response.raise_for_status()
    return response.json()
except requests.Timeout:
    print('Request timeout')
except requests.RequestException as e:
    print(f'Request failed: {e}')
```

---

## Timeout Recommendations

| Operation | Timeout | Notes |
|-----------|---------|-------|
| Connection timeout | 5s | Time to establish TCP connection |
| API call (fast) | 10s | Simple CRUD operations |
| API call (slow) | 30s | Complex queries, aggregations |
| Database query | 5-10s | Statement timeout |
| File upload | 60s | Depends on file size |
| Background job | 5-10 min | Long-running tasks |
| Health check | 1s | Fast liveness/readiness checks |
| Streaming response | 30-60s | Idle timeout between chunks |

---

## Nested Timeout Budgets

**Use when:** Multiple dependent operations with overall deadline.

```javascript
class TimeoutBudget {
  constructor(totalTimeout) {
    this.deadline = Date.now() + totalTimeout;
  }

  remaining() {
    const remaining = this.deadline - Date.now();
    if (remaining <= 0) {
      throw new Error('Budget exhausted');
    }
    return remaining;
  }

  async execute(fn, label) {
    const timeout = this.remaining();
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      return await fn({ signal: controller.signal, timeout });
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error(`${label} timeout (${timeout}ms remaining)`);
      }
      throw error;
    } finally {
      clearTimeout(id);
    }
  }
}

// Usage: Chain operations with shared budget
async function processOrder(orderId) {
  const budget = new TimeoutBudget(30000); // 30s total

  // Step 1: Fetch order (max 10s)
  const order = await budget.execute(
    async ({ signal, timeout }) => {
      return await fetch(`/api/orders/${orderId}`, { signal });
    },
    'Fetch order'
  );

  // Step 2: Process payment (max remaining time)
  const payment = await budget.execute(
    async ({ signal, timeout }) => {
      return await paymentAPI.charge(order, { signal });
    },
    'Process payment'
  );

  // Step 3: Send confirmation (max remaining time)
  await budget.execute(
    async ({ signal, timeout }) => {
      return await emailAPI.send(order.email, { signal });
    },
    'Send confirmation'
  );

  return { order, payment };
}
```

---

## Timeout Error Handling

**Graceful Degradation:**

```javascript
async function getUserProfile(userId) {
  try {
    return await fetchWithTimeout(`/api/users/${userId}`, {}, 5000);
  } catch (error) {
    if (error.message.includes('timeout')) {
      // Return cached data on timeout
      const cached = await cache.get(`user:${userId}`);
      if (cached) {
        return { ...cached, _degraded: true };
      }
    }
    throw error;
  }
}
```

**Logging and Metrics:**

```javascript
async function fetchWithTimeoutAndMetrics(url, options = {}, timeout = 10000) {
  const startTime = Date.now();

  try {
    const result = await fetchWithTimeout(url, options, timeout);
    metrics.histogram('http.request.duration', Date.now() - startTime);
    return result;
  } catch (error) {
    metrics.histogram('http.request.duration', Date.now() - startTime);

    if (error.message.includes('timeout')) {
      metrics.increment('http.request.timeout');
      logger.warn('Request timeout', { url, timeout });
    }

    throw error;
  }
}
```

---

## Checklist

- [ ] All external calls have timeouts
- [ ] Database queries have statement timeouts
- [ ] HTTP client timeouts configured
- [ ] Timeouts logged when exceeded
- [ ] Graceful degradation on timeout
- [ ] Timeout metrics tracked (P50, P99)
- [ ] Connection timeout < request timeout
- [ ] Timeout budgets for nested operations
- [ ] Alerts when timeout rates spike

---

## Related Resources

- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) - Combine timeouts with circuit breakers
- [retry-patterns.md](retry-patterns.md) - Retry timed-out operations
- [graceful-degradation.md](graceful-degradation.md) - Handle timeout failures gracefully
- [resilience-checklists.md](resilience-checklists.md) - Comprehensive timeout hardening
