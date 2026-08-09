# Load Testing Patterns

Design patterns for building effective, repeatable load tests that produce actionable results.

## Table of Contents

- [Scenario Modeling](#scenario-modeling)
- [Map Critical User Journeys](#map-critical-user-journeys)
- [Think Times](#think-times)
- [Data Parameterization](#data-parameterization)
- [Ramp-Up Strategies](#ramp-up-strategies)
- [Gradual Ramp (Standard Load Test)](#gradual-ramp-standard-load-test)
- [Stepped Ramp (Find the Ceiling)](#stepped-ramp-find-the-ceiling)
- [Spike Test](#spike-test)
- [Soak Test](#soak-test)
- [Locust Patterns](#locust-patterns)
- [locust — weighted user journey](#locust-—-weighted-user-journey)
- [locust — custom load shape (stepped ramp)](#locust-—-custom-load-shape-stepped-ramp)
- [Correlation and Authentication](#correlation-and-authentication)
- [Distributed Execution](#distributed-execution)
- [Start master](#start-master)
- [Start workers (one per CPU core, multiple machines)](#start-workers-one-per-cpu-core-multiple-machines)
- [Result Analysis](#result-analysis)
- [Key Metrics to Track](#key-metrics-to-track)
- [Identifying the Saturation Point](#identifying-the-saturation-point)
- [Warm-Up Period](#warm-up-period)
- [Compare Against Baselines](#compare-against-baselines)
- [Throughput Curves and Error Correlation](#throughput-curves-and-error-correlation)
- [Why You Cannot Average Percentiles](#why-you-cannot-average-percentiles)
- [Anti-Patterns](#anti-patterns)

## Scenario Modeling

### Map Critical User Journeys

Each load test scenario should represent a real user journey, not just a single endpoint. Identify the top 5-10 user flows by traffic volume and business impact.

Example journey breakdown:
1. Homepage load (GET /)
2. Search (GET /api/search?q=...)
3. View product (GET /api/products/:id)
4. Add to cart (POST /api/cart)
5. Checkout (POST /api/orders)

Weight scenarios by real traffic distribution. If 60% of traffic is browse-only and 5% reaches checkout, your load test should reflect that ratio.

### Think Times

Real users pause between actions. Without think times, load tests generate unrealistic request rates that inflate apparent throughput.

```javascript
// k6 — realistic think time between actions
import { sleep } from 'k6';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export default function () {
  // Browse product
  http.get('https://api.example.com/products/123');
  sleep(randomIntBetween(2, 5)); // 2-5 seconds think time

  // Add to cart
  http.post('https://api.example.com/cart', JSON.stringify({ productId: 123 }));
  sleep(randomIntBetween(1, 3));
}
```

### Data Parameterization

Avoid testing with a single user or a single product ID. Cache hits from repeated identical requests mask real performance.

```javascript
// k6 — parameterized data from CSV
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';
import { SharedArray } from 'k6/data';

const users = new SharedArray('users', function () {
  return papaparse.parse(open('./test-users.csv'), { header: true }).data;
});

export default function () {
  const user = users[__VU % users.length];
  const loginRes = http.post('https://api.example.com/auth/login', JSON.stringify({
    email: user.email,
    password: user.password,
  }));
}
```

## Workload Model: Open vs Closed Loop

This is the most consequential choice in a load test. Get it wrong and your p99 numbers are systematically optimistic — by orders of magnitude under stress.

### Closed-loop (VU / arrival-by-completion)

Each virtual user issues a request, **waits for the response, then issues the next**. Throughput is bounded by latency: when the system slows, the client slows in lockstep, and the test stops generating offered load. This is what `vus` / `stages` (k6), Locust users, and Gatling scenarios produce by default.

- Models: realistic for thinking users behind a slow client (mobile keyboard).
- Hides: queueing delays, head-of-line blocking, real production behaviour where requests arrive whether or not the server is keeping up.

### Open-loop (arrival-rate)

Requests arrive at a **fixed rate independent of response time** — like real production traffic. If the server slows, the queue grows, and latency reflects both service time *and* queueing time. This is what production actually does.

```javascript
// k6 — open-loop arrival rate (the right default for SLO load tests)
export const options = {
  scenarios: {
    api_slo: {
      executor: 'constant-arrival-rate',
      rate: 500,                  // 500 RPS, regardless of response time
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 200,       // sized via Little's Law: 500 req/s * 0.4s expected latency = 200
      maxVUs: 1000,               // safety ceiling: 500 req/s * 2s SLO-breach latency = 1000
    },
  },
};
```

`preAllocatedVUs` and `maxVUs` are not arbitrary — size them with Little's Law (`L = λ × W`): concurrency needed equals arrival rate times the response time the generator must be able to sustain. See [capacity-planning.md — Little's Law](capacity-planning.md#littles-law-sizing-concurrency-from-rate-and-latency) for the full derivation. If a test starts dropping iterations or timing out at the VU ceiling before the target system shows distress, the load generator is under-provisioned, not the system under test.

Use `ramping-arrival-rate` for stepped open-loop ramps. Locust ≥ 2.x supports `constant_throughput`; Gatling has `constantUsersPerSec` / `rampUsersPerSec`; JMeter has Concurrency Thread Group + Throughput Shaping Timer.

### Coordinated omission (the silent measurement bug)

A closed-loop generator under-reports tail latency because **slow responses delay the next request**, so the slow request count is artificially low. A 1s stall that should produce hundreds of slow samples produces one. Reported p99 looks fine; production p99 is much worse.

Mitigations, in order of preference:

1. Use open-loop / arrival-rate executors (above). This eliminates the bug at the source.
2. If you must use closed-loop, enable a coordinated-omission correction: HdrHistogram's `recordValueWithExpectedInterval`, `wrk2` (Tene's fix to wrk), Gatling's `pause` semantics with `holdFor`, or post-process histograms with `hdr-plot`.
3. Always report **p99.9** alongside p99 — coordinated omission hides most reliably at the deep tail.

### Decision

| Test goal | Workload model |
|---|---|
| Validate SLO under target traffic | Open-loop, arrival-rate at SLO target |
| Find capacity ceiling | Open-loop, ramping-arrival-rate |
| Spike / surge | Open-loop, arrival-rate with sharp jump |
| Mobile/thick-client realism with think time | Closed-loop with explicit think times |
| Soak / leak hunt | Either (closed-loop is fine; latency is secondary) |

## Ramp-Up Strategies

### Gradual Ramp (Standard Load Test)

Start low, ramp linearly to target, hold at target, then ramp down. This reveals at what load level problems appear.

```javascript
// k6 — standard ramp profile
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // ramp to 50 VUs
    { duration: '5m', target: 50 },   // hold at 50
    { duration: '2m', target: 100 },  // ramp to 100
    { duration: '5m', target: 100 },  // hold at 100
    { duration: '2m', target: 0 },    // ramp down
  ],
};
```

### Stepped Ramp (Find the Ceiling)

Increase load in discrete steps with hold periods at each step. Easier to correlate degradation to specific load levels.

```javascript
// k6 — stepped ramp for capacity testing
export const options = {
  stages: [
    { duration: '3m', target: 50 },
    { duration: '3m', target: 50 },   // hold and measure
    { duration: '3m', target: 100 },
    { duration: '3m', target: 100 },  // hold and measure
    { duration: '3m', target: 150 },
    { duration: '3m', target: 150 },  // hold and measure
    { duration: '3m', target: 200 },
    { duration: '3m', target: 200 },  // hold and measure
    { duration: '2m', target: 0 },
  ],
};
```

### Spike Test

Instant jump to high load to test auto-scaling and burst handling.

```javascript
// k6 — spike pattern
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // warm up
    { duration: '10s', target: 500 }, // spike
    { duration: '3m', target: 500 },  // hold spike
    { duration: '10s', target: 10 },  // drop
    { duration: '2m', target: 10 },   // recovery
    { duration: '1m', target: 0 },
  ],
};
```

### Soak Test

Sustained moderate load for hours to detect memory leaks, connection pool exhaustion, and GC degradation.

```javascript
// k6 — soak test (2 hours at moderate load)
export const options = {
  stages: [
    { duration: '5m', target: 50 },
    { duration: '115m', target: 50 }, // 2 hours sustained
    { duration: '5m', target: 0 },
  ],
};
```

## Locust Patterns

```python
# locust — weighted user journey
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(2, 5)  # think time

    @task(6)  # 60% weight
    def browse(self):
        self.client.get("/api/products")

    @task(3)  # 30% weight
    def search(self):
        self.client.get("/api/search", params={"q": "shoes"})

    @task(1)  # 10% weight
    def checkout(self):
        self.client.post("/api/orders", json={"product_id": 123})
```

```python
# locust — custom load shape (stepped ramp)
from locust import LoadTestShape

class SteppedShape(LoadTestShape):
    stages = [
        {"duration": 180, "users": 50, "spawn_rate": 10},
        {"duration": 360, "users": 100, "spawn_rate": 10},
        {"duration": 540, "users": 200, "spawn_rate": 20},
        {"duration": 720, "users": 50, "spawn_rate": 50},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None
```

## Correlation and Authentication

When APIs require authentication, handle token acquisition in setup and pass tokens between requests.

```javascript
// k6 — setup/teardown with auth token
import http from 'k6/http';

export function setup() {
  const res = http.post('https://api.example.com/auth/token', JSON.stringify({
    client_id: __ENV.CLIENT_ID,
    client_secret: __ENV.CLIENT_SECRET,
  }), { headers: { 'Content-Type': 'application/json' } });

  return { token: res.json('access_token') };
}

export default function (data) {
  http.get('https://api.example.com/protected', {
    headers: { Authorization: `Bearer ${data.token}` },
  });
}
```

## Distributed Execution

For high-concurrency tests, distribute load across multiple machines.

**k6 distributed:** Use k6 Cloud or k6-operator for Kubernetes-native distribution. With k6 2.0, the Go module path changed to `go.k6.io/k6/v2`; custom extensions must update their import paths before they will compile against k6 2.0.

**Gatling distributed (Gatling 3.12+):** Gatling now supports Java, Kotlin, Scala, JavaScript, and TypeScript (via GraalVM integration in 3.12). Use Gatling Enterprise or open-source distributed mode with injectors. Gatling Studio (free desktop app) records browser sessions and exports Maven projects.

**Locust distributed:**
```bash
# Start master
locust --master -f load_test.py

# Start workers (one per CPU core, multiple machines)
locust --worker --master-host=<master-ip> -f load_test.py
```

## Result Analysis

### Key Metrics to Track

| Metric | What It Tells You |
|--------|-------------------|
| Response time p50 | Typical user experience |
| Response time p95 | Most users' worst experience |
| Response time p99 | Tail latency (queue effects, GC, etc.) |
| Response time p99.9 | Deep tail — surfaces coordinated-omission and queue-buildup bugs that p99 masks |
| Requests/sec (throughput) | System capacity |
| Error rate | Stability under load |
| Active VUs vs response time | Whether latency scales with concurrency |
| Throughput vs response time | Saturation point (throughput plateaus, latency rises) |

### Identifying the Saturation Point

Plot throughput and p95 latency against concurrent users. The saturation point is where throughput stops increasing but latency starts climbing. This is your system's effective capacity.

### Warm-Up Period

Discard the first 1-2 minutes of results. During warm-up:
- JVM JIT compilation has not kicked in
- Connection pools are not filled
- Caches are cold
- Auto-scaling has not triggered

### Compare Against Baselines

Never interpret results in isolation. Always compare against:
- Previous run with same scenario and environment
- The defined performance budget
- Production telemetry for the same endpoints

### Throughput Curves and Error Correlation

When errors spike, check whether throughput dropped simultaneously. Common pattern: errors start at a specific load level, indicating a resource bottleneck (connection pool, thread pool, database connections, or rate limiting).

### Why You Cannot Average Percentiles

Percentiles are not linear — you cannot average, sum, or otherwise arithmetically combine p99 values from different hosts, pods, or test runs and get a meaningful result. This is one of the most common analysis mistakes in load testing and observability dashboards alike.

**Worked example.** Two instances behind a load balancer each served 1,000 requests in the same window:

- Instance A: p99 = 50ms (its 10 slowest requests were all in the 40–60ms range)
- Instance B: p99 = 500ms (its 10 slowest requests were all in the 400–600ms range)

Naively averaging gives `(50 + 500) / 2 = 275ms` — a number that describes neither instance and does not correspond to any real percentile of the combined 2,000-request population. The **true fleet p99** is the 20th-worst value out of the pooled 2,000 requests (top 1%), and because instance B's 10 slow requests are already worse than *anything* in instance A's distribution, the correct combined p99 is close to instance B's ~15th-worst value — likely in the 450–550ms range, nowhere near 275ms. If the split were uneven (e.g., instance A served 9,000 requests and instance B served 100), the fleet p99 would look very different again — percentile aggregation is sensitive to the request-count weighting per source, not just the reported percentile values.

**What to do instead:**
- Aggregate from raw latency samples or merged histograms (e.g., merge HdrHistogram serialized snapshots), then recompute the percentile once, over the combined population.
- If only per-host percentiles are available (common with some APM tools), report them per-host and flag the spread — do not synthesize a fleet-wide number by averaging.
- The same rule applies across time windows: a "weekly p99" is not the average of seven daily p99s; recompute it from the week's combined raw data.
- Dashboards that show "average of p99 across pods" as a fleet SLO indicator are producing a number with no defined statistical meaning — treat any dashboard doing this as reporting an approximation at best, and push to change it to a properly merged histogram.

## LLM / AI API Load Testing

LLM APIs behave fundamentally differently from REST APIs. Standard load testing tools measure the wrong things by default.

### Why Standard Tools Fall Short

k6 and Locust record wall-clock request duration, conflating two separate phases:
- **Prefill (TTFT)** — time until the model returns the first token; bounded by prompt length and GPU memory bandwidth.
- **Decode (generation throughput)** — tokens per second after the first token; bounded by GPU compute.

A 10s request with 9.5s TTFT is a completely different failure mode from one with 500ms TTFT and slow decode. Aggregating them hides both.

Additionally, k6 and Locust treat streaming responses as atomic, so p99 latency reports the end-to-end duration, not the user-perceived first-response latency.

### Key Metrics

| Metric | Definition | Typical SLO |
|--------|-----------|-------------|
| TTFT (Time to First Token) | Latency from request to first token received | < 500ms (chat), < 200ms (real-time) |
| ITL (Inter-Token Latency) | Time between consecutive tokens; spikes signal overload | < 100ms (noticeable above this) |
| Tokens/sec (TPS) | Output throughput; varies by model and concurrency | Depends on model; track degradation |
| Goodput | % of requests meeting SLO at current concurrency | Match your SLO target |

### Tooling Approach

1. **For OpenAI-compatible endpoints**: Use k6 with a custom SSE parser that timestamps the first token separately. The [periscope](https://github.com/wizenheimer/periscope) OSS project provides pre-built k6 scripts + Grafana dashboards for this pattern.
2. **For CI gates**: Replace live LLM calls with a deterministic mock that returns realistic token-rate distributions. Live LLM testing costs orders of magnitude more and introduces non-deterministic variance.
3. **For load sweeps**: Step concurrency slowly (10 → 20 → 30 → 40 → 45 → 50+). GPU saturation curves are steep and nonlinear — large steps miss the inflection point.

### Realistic Workload Design

- Sample from production logs (sanitized) to get real prompt length distributions.
- Create three scenario classes: short queries (< 100 tokens), medium context (500–2k tokens), long context (> 8k tokens), weighted to production ratios.
- Test warm-cache and cold-cache scenarios separately. Cache state (prefix caching) can shift TTFT by 85%.
- Extend soak tests to 4+ hours minimum; KV cache fragmentation and memory leaks compound slowly.

```javascript
// k6 — measure TTFT for a streaming LLM endpoint
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const payload = JSON.stringify({
    model: 'gpt-4.1-mini',
    messages: [{ role: 'user', content: 'Explain photosynthesis in one sentence.' }],
    stream: true,
  });

  const startTime = Date.now();
  let ttft = null;

  const res = http.post('https://api.openai.com/v1/chat/completions', payload, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${__ENV.OPENAI_API_KEY}`,
    },
    responseType: 'text',
  });

  // Parse SSE stream to find first data chunk
  const lines = res.body.split('\n');
  for (const line of lines) {
    if (line.startsWith('data: ') && line !== 'data: [DONE]') {
      ttft = Date.now() - startTime;
      break;
    }
  }

  check(res, { 'status 200': (r) => r.status === 200 });
  // Record TTFT as a custom metric for threshold evaluation
  // Note: full streaming interception requires a native SSE k6 extension for accurate per-token timestamps
}
```

**Note on tool limitations**: Because k6 buffers the response, the TTFT measured above is the time to *buffer* the first token chunk, not stream it. For true streaming interception, use a native SSE extension or a purpose-built LLM benchmarking tool (e.g., [genai-perf](https://docs.nvidia.com/nim/benchmarking/llm/latest/) for NVIDIA NIM, or a mock-based harness). Use k6 for concurrency/throughput sweeps; use specialized tooling for accurate TTFT distributions.

## Anti-Patterns

- **Single-endpoint hammering** — tests one URL at max speed; measures nothing real.
- **No think time** — generates 10x realistic request rate; every result is inflated.
- **Shared test data** — all VUs use the same user/product; cache hit rate is 100%.
- **Testing from the same machine as the server** — CPU contention between load generator and system under test.
- **Ignoring client-side saturation** — the load generator itself bottlenecks; results plateau but the cause is the test harness, not the server.
- **Running once and calling it done** — single runs have high variance; run at least 3 times for stable results.
- **Closed-loop generator for SLO testing** — VU-based load with no arrival-rate floor under-reports tail latency due to coordinated omission. Use `constant-arrival-rate` / `ramping-arrival-rate` for SLO load tests; report p99.9 alongside p99.
- **Average-only metrics** — averages hide bimodal distributions and tail outages. Always report p50/p95/p99/p99.9.
- **Averaging percentiles across hosts, pods, or runs** — percentiles do not aggregate linearly; averaging per-host p99s produces a number with no defined statistical meaning. Merge raw histograms and recompute (see [Why You Cannot Average Percentiles](#why-you-cannot-average-percentiles)).
- **Ramp without warm-up discard** — first 1-2 minutes include JIT, cold caches, and unfilled pools. Excluding warm-up is positive guidance; *including* it in your reported headline number is the anti-pattern.
