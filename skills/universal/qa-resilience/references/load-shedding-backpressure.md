# Load Shedding and Backpressure

Overload protection patterns that keep systems stable under extreme traffic.

## Contents

- [Load Shedding Strategies](#load-shedding-strategies)
- [Backpressure Propagation](#backpressure-propagation)
- [Queue-Based Buffering](#queue-based-buffering)
- [Rate Limiting vs Load Shedding](#rate-limiting-vs-load-shedding)
- [Server-Side Admission Control](#server-side-admission-control)
- [Adaptive Concurrency Limits](#adaptive-concurrency-limits)
- [Client-Side Throttling](#client-side-throttling)
- [Implementation Patterns](#implementation-patterns)
- [Monitoring Overload Signals](#monitoring-overload-signals)
- [Kubernetes Resource Limits and HPA](#kubernetes-resource-limits-and-hpa)
- [Related Resources](#related-resources)

---

## Load Shedding Strategies

Load shedding rejects excess work early to protect the system from collapse. Unlike rate limiting (which caps throughput), load shedding adapts dynamically to current capacity.

### Priority-Based Shedding

Assign priority tiers to requests and shed lowest-priority work first.

```python
from enum import IntEnum
from fastapi import FastAPI, Request, HTTPException
import psutil

class Priority(IntEnum):
    CRITICAL = 1   # payments, auth
    HIGH = 2       # user-facing reads
    NORMAL = 3     # background syncs
    LOW = 4        # analytics, telemetry

app = FastAPI()

def get_request_priority(request: Request) -> Priority:
    path = request.url.path
    if path.startswith("/payments") or path.startswith("/auth"):
        return Priority.CRITICAL
    if request.method == "GET" and path.startswith("/api"):
        return Priority.HIGH
    if path.startswith("/analytics"):
        return Priority.LOW
    return Priority.NORMAL

def current_load() -> float:
    """Return CPU utilization as a fraction 0.0-1.0."""
    return psutil.cpu_percent(interval=0.1) / 100.0

SHED_THRESHOLDS = {
    Priority.LOW: 0.70,
    Priority.NORMAL: 0.80,
    Priority.HIGH: 0.90,
    Priority.CRITICAL: 0.98,
}

@app.middleware("http")
async def load_shedding_middleware(request: Request, call_next):
    load = current_load()
    priority = get_request_priority(request)
    threshold = SHED_THRESHOLDS[priority]

    if load > threshold:
        raise HTTPException(
            status_code=503,
            detail="Service overloaded",
            headers={"Retry-After": "5"},
        )

    return await call_next(request)
```

### Random Early Detection (RED)

Probabilistic shedding that increases drop probability as load rises, inspired by network congestion control.

```python
import random

def should_shed(current_load: float, min_thresh: float = 0.6,
                max_thresh: float = 0.9) -> bool:
    """Probabilistic shedding using RED algorithm."""
    if current_load < min_thresh:
        return False
    if current_load > max_thresh:
        return True

    # Linear probability between thresholds
    drop_prob = (current_load - min_thresh) / (max_thresh - min_thresh)
    return random.random() < drop_prob
```

### Adaptive Shedding (CoDel-inspired)

Track request latency and shed when queue delay exceeds a target.

| Signal            | Threshold   | Action                         |
|-------------------|-------------|--------------------------------|
| CPU utilization   | > 80%       | Shed LOW priority              |
| Queue depth       | > 1000      | Shed LOW + NORMAL              |
| P99 latency       | > 2x target | Shed everything below CRITICAL |
| Error rate        | > 10%       | Activate emergency shedding    |
| Memory pressure   | > 85%       | Reject large payloads          |

---

## Backpressure Propagation

Backpressure slows producers when consumers cannot keep up, preventing unbounded resource growth.

### Reactive Streams (Project Reactor / RxJava)

```java
// Reactor: bounded request with backpressure
Flux.range(1, 1_000_000)
    .onBackpressureBuffer(256, dropped -> log.warn("Dropped: {}", dropped))
    .publishOn(Schedulers.boundedElastic())
    .flatMap(this::processItem, /* concurrency */ 16)
    .subscribe();

// Backpressure strategies
Flux.create(sink -> producer.onData(sink::next))
    .onBackpressureDrop(item -> metrics.increment("dropped"))    // drop newest
    .onBackpressureLatest()                                       // keep only latest
    .onBackpressureBuffer(1024, BufferOverflowStrategy.DROP_OLDEST)
    .subscribe();
```

### gRPC Flow Control

gRPC uses HTTP/2 flow control windows. Servers can signal backpressure by pausing reads.

```go
// Go gRPC server-side flow control
func (s *server) StreamData(req *pb.Request,
    stream pb.Service_StreamDataServer) error {

    for item := range dataChannel {
        // stream.Send blocks when the client's receive window is full,
        // naturally applying backpressure to the producer
        if err := stream.Send(&pb.DataItem{Value: item}); err != nil {
            return err
        }
    }
    return nil
}
```

### TCP Backpressure

When the application stops reading from a socket, the TCP receive buffer fills, the window shrinks to zero, and the sender pauses. This is implicit backpressure -- no application code required, but it can cause head-of-line blocking across multiplexed connections.

**Checklist -- Backpressure:**

- [ ] Every producer/consumer pair has an explicit backpressure strategy
- [ ] Bounded buffers are used between pipeline stages
- [ ] Drop/overflow policy is documented and monitored
- [ ] gRPC streaming services rely on HTTP/2 flow control (do not disable)
- [ ] TCP receive buffer sizes are tuned for expected throughput

---

## Queue-Based Buffering

Queues absorb short bursts but must be bounded to prevent memory exhaustion.

### Bounded Queue Patterns

```python
import asyncio

# Bounded asyncio queue with timeout
queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=500)

async def enqueue(item: dict, timeout: float = 1.0):
    try:
        await asyncio.wait_for(queue.put(item), timeout=timeout)
    except asyncio.TimeoutError:
        # Queue full -- shed this request
        metrics.increment("queue.rejected")
        raise ServiceUnavailable("Queue full")
```

### Overflow Policies

| Policy         | Behavior                    | Use When                        |
|----------------|-----------------------------|---------------------------------|
| Block          | Wait for space              | Producer can afford to pause    |
| Drop newest    | Discard incoming item       | Latest data is expendable       |
| Drop oldest    | Evict head of queue         | Freshness matters more          |
| Reject         | Return error to caller      | Caller should retry or redirect |
| Spill to disk  | Write overflow to disk      | All data must be processed      |

```javascript
// Node.js bounded queue with reject policy
class BoundedQueue {
  constructor(maxSize) {
    this.maxSize = maxSize;
    this.items = [];
  }

  enqueue(item) {
    if (this.items.length >= this.maxSize) {
      throw new Error('Queue full');
    }
    this.items.push(item);
  }

  dequeue() {
    return this.items.shift();
  }

  get depth() {
    return this.items.length;
  }

  get utilization() {
    return this.items.length / this.maxSize;
  }
}
```

---

## Rate Limiting vs Load Shedding

| Aspect              | Rate Limiting                    | Load Shedding                   |
|---------------------|----------------------------------|---------------------------------|
| **Trigger**         | Request count per time window    | System resource utilization     |
| **Scope**           | Per client/API key               | Global or per-service           |
| **Goal**            | Fairness and abuse prevention    | System stability                |
| **Response**        | 429 Too Many Requests            | 503 Service Unavailable         |
| **Adaptive**        | Usually static                   | Responds to real-time load      |
| **When to use**     | API quotas, abuse prevention     | Overload protection, cascading failure prevention |

**Use both together:** Rate limiting caps individual clients. Load shedding protects the system when aggregate load from all clients exceeds capacity.

### Per-Caller In-Flight Caps as Isolation

Rate limits count requests over a window; an in-flight cap bounds how much of a *shared, exhaustible* resource one caller can occupy at any instant — threads, connections, or slots against a hot keyspace. This is the control that stops one slow or misbehaving tenant from parking the whole pool while everyone else queues behind it.

*Site Reliability Engineering*, Ch. 21 §"Per-Customer Limits" frames the goal as blast-radius containment: when global overload happens, "it's vital that the service only delivers error responses to misbehaving customers, while other customers remain unaffected." Google provisions per-customer quotas from negotiated usage, and deliberately lets those quotas sum to more than total capacity — relying "on the fact that it's unlikely for all of their customers to hit their resource limits simultaneously."

For the in-flight variant, Ch. 22 §"Bimodal latency" offers a concrete figure: "You might consider only allowing 25% of your threads to be occupied by any one client in order to provide fairness in the face of heavy load by any single client misbehaving."

Treat 25% as **Google's operating choice for that context, not a universal constant.** The right cap depends on how many callers you have and how correlated their load is — a service with four equal tenants and one with four hundred want very different numbers. Derive it, don't copy it:

- Set the cap above each caller's normal peak concurrency, so it only binds during abuse or slowness.
- Keep the sum of caps above 100% of capacity (as Google does with quotas) — sizing every caller to a strict `1/N` share wastes capacity that idle tenants would have left on the table.
- Apply the cap per exhaustible resource, and per keyspace or shard where one hot range can stall requests independently of the caller.
- Reject over-cap requests immediately with a distinct signal (429 plus a reason), so the caller can back off and the rejection stays cheap.
- Export per-caller in-flight counts and rejection rates; without them, an isolation breach looks identical to a general overload.

---

## Server-Side Admission Control

Admission control gates requests before they consume significant resources.

```go
package main

import (
    "net/http"
    "runtime"
    "sync/atomic"
)

type AdmissionController struct {
    inFlight     int64
    maxInFlight  int64
    cpuThreshold float64
}

func NewAdmissionController(maxInFlight int64) *AdmissionController {
    return &AdmissionController{
        maxInFlight:  maxInFlight,
        cpuThreshold: 0.85,
    }
}

func (ac *AdmissionController) Allow() bool {
    current := atomic.LoadInt64(&ac.inFlight)
    if current >= ac.maxInFlight {
        return false
    }

    // Check goroutine count as a proxy for load
    if runtime.NumGoroutine() > 10000 {
        return false
    }

    atomic.AddInt64(&ac.inFlight, 1)
    return true
}

func (ac *AdmissionController) Release() {
    atomic.AddInt64(&ac.inFlight, -1)
}

func (ac *AdmissionController) Middleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if !ac.Allow() {
            w.Header().Set("Retry-After", "5")
            http.Error(w, "Service overloaded", http.StatusServiceUnavailable)
            return
        }
        defer ac.Release()
        next.ServeHTTP(w, r)
    })
}
```

---

## Adaptive Concurrency Limits

A static `maxInFlight` (above) is right only for the capacity it was tuned against. Capacity moves with instance size, autoscaling, noisy neighbours, GC, and downstream latency, so a static limit drifts: too high and requests queue until latency collapses throughput; too low and you shed healthy traffic. Retry budgets do not fix this — they bound *retry* amplification, not first-attempt overload.

**Default:** for a request-serving service with steady, high traffic, put an adaptive concurrency limit at the service ingress (in-process library or sidecar) and keep a static hard ceiling behind it as a backstop. Adaptive limiters apply TCP-style congestion control to in-flight requests: a latency-gradient controller compares a no-load latency baseline (minimum observed RTT) with recent sampled latency and shrinks the limit as queueing delay grows; an AIMD controller adds to the limit on success and cuts it multiplicatively on timeout or drop. Examples are [Netflix concurrency-limits](https://github.com/Netflix/concurrency-limits) (Vegas, Gradient2, AIMD limiters) and the [Envoy adaptive concurrency filter](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/adaptive_concurrency_filter) (gradient controller; rejects over-limit requests with 503). The limit tracks Little's law — in-flight = throughput × latency — so it follows real capacity instead of a guess.

**Do not use a latency-driven limit when:**

- Traffic per instance is low. Too few samples per window make the gradient noisy and the limit flaps; a static limit derived from a load test is more predictable.
- Latency is bimodal or mix-dependent (cache hit vs miss, cheap reads next to expensive reports). A shift in request mix reads as congestion. Partition the limiter per endpoint class, or use static per-class limits.
- Requests are long-running, streaming, or batch. Latency is not a queueing signal there; bound them with bulkheads and queue limits.
- The saturating resource does not show up as latency (memory, file descriptors). Guard it with a separate resource check.
- The service cannot tolerate the brief concurrency dip some gradient controllers take while re-measuring the baseline (Envoy pins the limit to `min_concurrency` while it measures min RTT, and its docs expect extra 503s in that window and recommend retrying them — do so at one layer, within the budget). Check the controller's behaviour before rollout.

**Interaction with retries** (consistent with [retry-patterns.md](retry-patterns.md), which retries 5xx, 408 and 429 under a budget):

- Shed responses are retryable, but only at the one layer that owns retries, only within the retry budget, and never earlier than `Retry-After`. A shed that triggers retries at every hop re-creates the (retries + 1)^layers amplification the budget exists to stop.
- Send 503 with `Retry-After` for server overload and 429 for a caller over its quota or in-flight cap, so clients can distinguish "the service is full" from "you are over your share".
- Make rejection cheap: reject before parsing bodies, opening transactions, or calling dependencies. A shed that costs as much as serving does not protect anything.
- Pair server-side shedding with client-side throttling ([below](#client-side-throttling)). The server protects itself; the client stops spending its budget on requests that will be rejected. Server-side is mandatory; client-side is the complement, because you do not control every client.

**Priority:** partition the limit so low-priority work (analytics, prefetch, batch sync) is shed first and critical paths (auth, payments, health of in-progress user sessions) keep a reserved share. Without partitions an adaptive limit sheds uniformly, which is fair but not what the business wants during overload.

**Verify it** with a load test that ramps offered load well past measured capacity, then drops back:

- Goodput (successful responses within the latency SLO) rises, then **plateaus** near capacity instead of collapsing; admitted-request p99 stays bounded while shed rate absorbs the excess.
- Lowest-priority classes are shed first; critical classes keep their reserved share.
- Retry ratio stays inside the retry budget while shedding; no layer multiplies retries.
- Injected downstream latency lowers the limit, and the limit recovers after the latency is removed without sustained oscillation.
- After offered load returns to normal, goodput recovers promptly — a lingering backlog or retry tail is a metastable-failure signal ([cascading-failure-prevention.md](cascading-failure-prevention.md#metastable-failures--the-class-cascading-failure-fixes-do-not-cure)).

A test that only shows "503s appeared at high load" proves nothing; the pass condition is the goodput curve.

---

## Client-Side Throttling

Clients should self-throttle when receiving overload signals instead of retrying aggressively.

```javascript
class AdaptiveThrottle {
  constructor() {
    this.requests = 0;
    this.accepts = 0;
    this.windowMs = 60_000;
    this.history = [];
  }

  // Google SRE client-side throttling formula
  rejectionProbability() {
    const now = Date.now();
    this.history = this.history.filter(h => now - h.time < this.windowMs);
    const requests = this.history.length;
    const accepts = this.history.filter(h => h.accepted).length;

    // P(reject) = max(0, (requests - K * accepts) / (requests + 1))
    const K = 2.0; // multiplier (higher = more lenient)
    return Math.max(0, (requests - K * accepts) / (requests + 1));
  }

  async send(requestFn) {
    const rejectProb = this.rejectionProbability();
    if (Math.random() < rejectProb) {
      throw new Error('Client-side throttled');
    }

    this.history.push({ time: Date.now(), accepted: false });
    const entry = this.history[this.history.length - 1];

    try {
      const result = await requestFn();
      entry.accepted = true;
      return result;
    } catch (err) {
      if (err.status === 503 || err.status === 429) {
        // Server rejected -- entry stays accepted=false
      } else {
        entry.accepted = true; // non-overload errors count as accepts
      }
      throw err;
    }
  }
}
```

---

## Implementation Patterns

### Node.js -- Express Overload Protection

```javascript
const toobusy = require('toobusy-js');

// Tune lag threshold (ms of event loop delay)
toobusy.maxLag(70);
toobusy.interval(500);

app.use((req, res, next) => {
  if (toobusy()) {
    res.status(503).set('Retry-After', '5').json({
      error: 'Server too busy',
    });
    return;
  }
  next();
});

process.on('SIGINT', () => {
  toobusy.shutdown();
  process.exit();
});
```

### Python -- Uvicorn with Concurrency Limit

```python
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

class ConcurrencyLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_concurrent: int = 100):
        super().__init__(app)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def dispatch(self, request, call_next):
        if self.semaphore._value == 0:
            return JSONResponse(
                {"error": "Too many concurrent requests"},
                status_code=503,
                headers={"Retry-After": "2"},
            )
        async with self.semaphore:
            return await call_next(request)
```

---

## Monitoring Overload Signals

Track these metrics to detect overload before it causes failures.

| Metric                      | Tool/Source           | Alert Threshold       |
|-----------------------------|-----------------------|-----------------------|
| CPU utilization             | node_exporter, cAdvisor | > 80% sustained 2min |
| Event loop lag (Node.js)    | `toobusy-js`, prom-client | > 70ms             |
| Active connections          | nginx, envoy stats    | > 80% of max_connections |
| Queue depth                 | Application metrics   | > 80% of maxSize      |
| P99 latency                 | APM (Datadog, Grafana) | > 2x baseline        |
| 503 response rate           | Load balancer logs    | > 1% of total         |
| Goroutine / thread count    | runtime metrics       | > 2x normal baseline  |
| Memory utilization          | cAdvisor              | > 85%                 |

**Checklist -- Monitoring:**

- [ ] Dashboard shows in-flight requests, queue depth, and shed rate
- [ ] Alerts fire when shedding begins (indicates capacity issue)
- [ ] Shed reason is logged (CPU, queue, concurrency, memory)
- [ ] Client-facing 503 responses include `Retry-After` header
- [ ] Load tests validate shedding activates at expected thresholds

---

## Kubernetes Resource Limits and HPA

### Resource Limits

```yaml
# deployment.yaml
resources:
  requests:
    cpu: "500m"
    memory: "256Mi"
  limits:
    cpu: "1000m"     # hard ceiling prevents noisy neighbors
    memory: "512Mi"  # OOMKill if exceeded
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: http_requests_in_flight
        target:
          type: AverageValue
          averageValue: "50"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

**Key principle:** HPA handles gradual load growth. Load shedding handles sudden spikes that outpace autoscaling (scale-up takes 30-120s; overload happens in seconds).

---

## Related Resources

- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) -- Circuit breakers for dependency failure isolation
- [bulkhead-isolation.md](bulkhead-isolation.md) -- Resource compartmentalization patterns
- [timeout-policies.md](timeout-policies.md) -- Timeout configuration for bounded waits
- [retry-patterns.md](retry-patterns.md) -- Retry strategies that avoid retry storms
- [graceful-degradation.md](graceful-degradation.md) -- Fallback behavior during overload
- [resilience-checklists.md](resilience-checklists.md) -- Comprehensive resilience verification
