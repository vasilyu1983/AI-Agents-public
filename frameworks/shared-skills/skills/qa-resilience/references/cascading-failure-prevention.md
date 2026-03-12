# Cascading Failure Prevention

Techniques for containing and preventing cascading failures in distributed systems.

## Contents

- [Cascade Anatomy](#cascade-anatomy)
- [Blast Radius Containment](#blast-radius-containment)
- [Dependency Isolation Patterns](#dependency-isolation-patterns)
- [Circuit Breaker and Bulkhead Combination](#circuit-breaker-and-bulkhead-combination)
- [Retry Storm Prevention](#retry-storm-prevention)
- [Connection and Thread Pool Exhaustion](#connection-and-thread-pool-exhaustion)
- [Architectural Isolation](#architectural-isolation)
- [Testing for Cascading Failures](#testing-for-cascading-failures)
- [Real-World Case Studies](#real-world-case-studies)
- [Prevention Checklist](#prevention-checklist)
- [Related Resources](#related-resources)

---

## Cascade Anatomy

A cascading failure follows three phases: trigger, propagation, and amplification.

```text
TRIGGER                    PROPAGATION                   AMPLIFICATION
─────────                  ───────────                   ─────────────
Single component fails     Dependent services slow       Retry storms multiply
  ↓                          ↓                             ↓
Database goes read-only    API gateway queues fill       Clients retry 3x each
  ↓                          ↓                             ↓
Timeouts start             Thread pools exhaust          Load triples
  ↓                          ↓                             ↓
Error rate spikes          Memory pressure rises         Health checks fail
                             ↓                             ↓
                           Cascading service failures    Full system outage
```

### Common Triggers

| Trigger                  | Propagation Path                | Time to Cascade |
|--------------------------|---------------------------------|-----------------|
| Database failover        | Connection pool exhaustion      | 30-120 seconds  |
| DNS resolution failure   | All services lose connectivity  | 5-30 seconds    |
| Certificate expiry       | TLS handshake failures          | Immediate       |
| Memory leak              | OOM kills, pod restarts         | Minutes to hours|
| Deployment rollout       | Mixed versions, schema mismatch | 1-10 minutes    |
| Cloud AZ outage          | Regional dependency failure     | 1-5 minutes     |

---

## Blast Radius Containment

Limit how far a failure can spread by isolating failure domains.

### Failure Domain Hierarchy

```text
Level 1: Process   →  Single container/pod
Level 2: Service   →  All replicas of one service
Level 3: Cell      →  Group of services sharing infrastructure
Level 4: Region    →  Entire cloud region
Level 5: Global    →  Control plane, DNS, CDN
```

### Containment Strategies by Level

```python
# Example: Feature flag kill switch for blast radius control
class FeatureFlags:
    """Disable features under cascading failure conditions."""

    def __init__(self, flag_service):
        self.flags = flag_service

    def should_call_recommendation_engine(self, user_id: str) -> bool:
        # Kill switch: disable non-critical dependency entirely
        if not self.flags.is_enabled("recommendations.enabled"):
            return False

        # Percentage rollout: limit blast radius during incidents
        if self.flags.get_percentage("recommendations.traffic") < 100:
            return hash(user_id) % 100 < self.flags.get_percentage(
                "recommendations.traffic"
            )

        return True

    def get_recommendations(self, user_id: str) -> list:
        if not self.should_call_recommendation_engine(user_id):
            return self.get_cached_recommendations(user_id)

        try:
            return self.recommendation_client.fetch(user_id)
        except Exception:
            return self.get_cached_recommendations(user_id)
```

---

## Dependency Isolation Patterns

### Critical vs Non-Critical Dependencies

Classify every external dependency and apply different failure policies.

| Dependency Type | Failure Policy               | Example                    |
|-----------------|------------------------------|----------------------------|
| **Critical**    | Retry with circuit breaker   | Payment gateway, auth      |
| **Degradable**  | Fallback to cache/default    | Recommendations, analytics |
| **Optional**    | Fail silently, log warning   | Feature flags, A/B testing |
| **Async**       | Queue and retry later        | Email, notifications       |

```javascript
// Node.js: Dependency classification with failure policies
class DependencyManager {
  constructor() {
    this.dependencies = new Map();
  }

  register(name, { type, client, fallback, circuitBreaker }) {
    this.dependencies.set(name, { type, client, fallback, circuitBreaker });
  }

  async call(name, method, ...args) {
    const dep = this.dependencies.get(name);
    if (!dep) throw new Error(`Unknown dependency: ${name}`);

    try {
      if (dep.circuitBreaker) {
        return await dep.circuitBreaker.fire(() => dep.client[method](...args));
      }
      return await dep.client[method](...args);
    } catch (error) {
      switch (dep.type) {
        case 'critical':
          throw error; // propagate -- caller must handle
        case 'degradable':
          console.warn(`${name} degraded: ${error.message}`);
          return dep.fallback ? dep.fallback(...args) : null;
        case 'optional':
          console.warn(`${name} unavailable: ${error.message}`);
          return null;
        case 'async':
          await this.enqueueForRetry(name, method, args);
          return { queued: true };
        default:
          throw error;
      }
    }
  }
}
```

---

## Circuit Breaker and Bulkhead Combination

Use circuit breakers to detect failure and bulkheads to contain resource consumption. Together they prevent both failure propagation and resource exhaustion.

```python
import asyncio
from dataclasses import dataclass, field
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class ProtectedDependency:
    """Combines circuit breaker + bulkhead for a single dependency."""
    name: str
    max_concurrent: int = 10
    failure_threshold: int = 5
    reset_timeout: float = 30.0

    # Bulkhead state
    semaphore: asyncio.Semaphore = field(init=False)
    # Circuit breaker state
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0

    def __post_init__(self):
        self.semaphore = asyncio.Semaphore(self.max_concurrent)

    async def call(self, func, *args, **kwargs):
        # Circuit breaker check
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError(f"{self.name} circuit is open")

        # Bulkhead: non-blocking acquire
        if self.semaphore._value == 0:
            raise BulkheadFullError(
                f"{self.name} bulkhead full ({self.max_concurrent} slots)"
            )

        async with self.semaphore:
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

**Configuration Matrix:**

| Dependency       | Bulkhead Slots | CB Failure Threshold | CB Reset Timeout |
|------------------|----------------|----------------------|------------------|
| Payment API      | 20             | 3                    | 60s              |
| User Service     | 15             | 5                    | 30s              |
| Recommendation   | 5              | 3                    | 30s              |
| Email Service    | 10             | 10                   | 120s             |
| Analytics        | 3              | 5                    | 60s              |

---

## Retry Storm Prevention

Retries amplify failures. Uncoordinated retries across multiple layers can multiply traffic 3x-27x.

### The Multiplication Problem

```text
Client retries 3x → Gateway retries 3x → Service retries 3x
Total attempts per original request: 3 × 3 × 3 = 27

If 1000 requests/sec normally:
During outage with naive retries: up to 27,000 requests/sec
```

### Mitigation Strategies

```javascript
// 1. Retry budget: cap total retries at a percentage of successful requests
class RetryBudget {
  constructor({ ratio = 0.1, minRetries = 10, windowMs = 10_000 }) {
    this.ratio = ratio;
    this.minRetries = minRetries;
    this.windowMs = windowMs;
    this.requests = [];
    this.retries = [];
  }

  canRetry() {
    const now = Date.now();
    this.requests = this.requests.filter(t => now - t < this.windowMs);
    this.retries = this.retries.filter(t => now - t < this.windowMs);

    const budget = Math.max(
      this.minRetries,
      Math.floor(this.requests.length * this.ratio)
    );

    return this.retries.length < budget;
  }

  recordRequest() { this.requests.push(Date.now()); }
  recordRetry()   { this.retries.push(Date.now()); }
}

// 2. Exponential backoff with full jitter
function backoffWithJitter(attempt, baseMs = 100, maxMs = 30_000) {
  const exponential = Math.min(maxMs, baseMs * Math.pow(2, attempt));
  return Math.random() * exponential; // full jitter
}
```

**Retry Rules of Thumb:**

- [ ] Retry only at one layer (closest to the caller, not at every hop)
- [ ] Use exponential backoff with full jitter (not fixed intervals)
- [ ] Implement retry budgets (max 10% of successful request volume)
- [ ] Never retry non-idempotent operations without explicit safeguards
- [ ] Add circuit breakers to stop retries when a dependency is down

---

## Connection and Thread Pool Exhaustion

Pool exhaustion is the most common cascade propagation mechanism.

### Connection Pool Sizing

```python
# SQLAlchemy: properly sized connection pool
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@db:5432/app",
    pool_size=20,          # steady-state connections
    max_overflow=10,       # burst capacity
    pool_timeout=5,        # wait at most 5s for a connection
    pool_recycle=1800,     # recycle connections every 30 min
    pool_pre_ping=True,    # verify connection before use
)
```

### Thread Pool Isolation (Java/Kotlin)

```kotlin
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit

// Separate thread pools per dependency
val paymentExecutor = Executors.newFixedThreadPool(20).also {
    it as java.util.concurrent.ThreadPoolExecutor
    it.setRejectedExecutionHandler { _, _ ->
        throw ServiceUnavailableException("Payment pool exhausted")
    }
}

val analyticsExecutor = Executors.newFixedThreadPool(5)

// If analytics pool exhausts, payments are unaffected
fun processPayment(order: Order) = paymentExecutor.submit {
    paymentGateway.charge(order)
}

fun trackEvent(event: Event) = analyticsExecutor.submit {
    analyticsService.track(event)
}
```

---

## Architectural Isolation

### Shared-Nothing Architecture

Each service owns its data store and has no shared state with other services.

```text
SHARED (risky)                    SHARED-NOTHING (resilient)
──────────────                    ─────────────────────────
Service A ──┐                     Service A → DB-A
             ├── Shared DB        Service B → DB-B
Service B ──┘                     Service C → DB-C
             │
Service C ──┘                     Communication via async events only
```

### Cell-Based Architecture

Partition users into isolated cells. A failure in cell 1 cannot affect cell 2.

```text
Cell 1 (users A-M)          Cell 2 (users N-Z)
┌────────────────┐           ┌────────────────┐
│ API Gateway    │           │ API Gateway    │
│ App Servers    │           │ App Servers    │
│ Database       │           │ Database       │
│ Cache          │           │ Cache          │
└────────────────┘           └────────────────┘

Router (stateless) directs user to correct cell
```

**Cell sizing guidance:**

| Scale              | Cells | Users per Cell | Blast Radius |
|--------------------|-------|----------------|--------------|
| 10K users          | 2     | 5K             | 50%          |
| 100K users         | 5     | 20K            | 20%          |
| 1M users           | 10    | 100K           | 10%          |
| 10M+ users         | 20+   | 500K           | 5%           |

---

## Testing for Cascading Failures

### Chaos Engineering Scenarios

Design experiments that specifically test cascade propagation.

```yaml
# Litmus chaos experiment: kill a critical dependency
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: cascade-test
spec:
  appinfo:
    appns: production
    applabel: app=payment-service
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "120"
            - name: CHAOS_INTERVAL
              value: "10"
            - name: FORCE
              value: "true"
```

### Cascade Test Matrix

| Test Scenario                     | Expected Behavior                    | Pass Criteria            |
|-----------------------------------|--------------------------------------|--------------------------|
| Kill database primary             | Reads served from replica            | < 5s user-facing impact  |
| Saturate payment service          | Other services unaffected            | No error rate increase   |
| DNS resolution failure            | Cached entries used, graceful errors | No 5xx for cached routes |
| 100% packet loss to dependency    | Circuit opens within threshold       | < 30s to detection       |
| Slow dependency (10s latency)     | Timeouts fire, fallbacks activate    | No thread pool exhaustion|
| Simultaneous 3-service failure    | Critical path survives              | Auth + payments work     |

### Gameday Runbook Template

```text
GAMEDAY: Cascading Failure Test
Date: ___________
Participants: ___________

PRE-GAME:
1. [ ] Notify on-call and stakeholders
2. [ ] Verify rollback procedures
3. [ ] Confirm monitoring dashboards are live
4. [ ] Set blast radius limits (which cells/regions)

EXPERIMENT:
1. [ ] Inject failure: ___________
2. [ ] Observe: error rates, latency, dependent services
3. [ ] Record time-to-detection: ___ seconds
4. [ ] Record time-to-mitigation: ___ seconds
5. [ ] Verify blast radius containment

POST-GAME:
1. [ ] Remove fault injection
2. [ ] Verify full recovery
3. [ ] Document findings
4. [ ] Create action items for gaps
```

---

## Real-World Case Studies

### AWS us-east-1 Kinesis Outage (2020)

- **Trigger:** A small capacity addition to Kinesis front-end fleet
- **Propagation:** New servers triggered a burst of thread creation in a shared component; threads exhausted OS limits
- **Amplification:** Cascaded to Cognito, CloudWatch, Lambda, and dozens of services dependent on Kinesis
- **Duration:** ~10 hours
- **Lesson:** Shared dependencies (Kinesis) become single points of failure. Services must handle Kinesis unavailability gracefully.

### Netflix Cascading Failure Prevention

Netflix uses a layered defense:

1. **Hystrix (now Resilience4j):** Circuit breakers per dependency
2. **Zuul:** Adaptive load shedding at the edge
3. **Cell architecture:** Regional isolation with failover
4. **Chaos Monkey / Chaos Kong:** Regular failure injection including full region evacuation

**Key Netflix principle:** "Design for the failure case first. The happy path is the exception in distributed systems."

---

## Prevention Checklist

- [ ] Every dependency classified as critical, degradable, optional, or async
- [ ] Circuit breakers on all synchronous external calls
- [ ] Bulkheads isolate resource pools per dependency
- [ ] Retry logic exists at only one layer with backoff and jitter
- [ ] Retry budgets cap retry volume at 10% of successful traffic
- [ ] Connection pools have bounded size and acquisition timeouts
- [ ] Thread pools are isolated per dependency (no shared pools)
- [ ] Timeouts are set on every network call (connect + read + total)
- [ ] Health checks distinguish between liveness and readiness
- [ ] Feature flags can disable non-critical dependencies instantly
- [ ] Chaos experiments test cascade scenarios quarterly
- [ ] Runbooks document cascade containment procedures
- [ ] Monitoring alerts on early cascade signals (pool utilization, error rate spikes)

---

## Related Resources

- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) -- Circuit breaker implementations
- [bulkhead-isolation.md](bulkhead-isolation.md) -- Bulkhead resource isolation
- [load-shedding-backpressure.md](load-shedding-backpressure.md) -- Overload protection
- [retry-patterns.md](retry-patterns.md) -- Retry strategies with backoff
- [timeout-policies.md](timeout-policies.md) -- Timeout configuration
- [chaos-engineering-guide.md](chaos-engineering-guide.md) -- Chaos experiment design
- [health-check-patterns.md](health-check-patterns.md) -- Liveness and readiness checks
