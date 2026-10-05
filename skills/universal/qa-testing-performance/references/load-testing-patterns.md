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

Each virtual user issues a request, **waits for the response, then issues the next**. Throughput is bounded by latency: when the system slows, the client slows in lockstep, and the test stops generating offered load. This is what `vus` / `stages` (k6) and default Locust users produce. Gatling's default injection steps (`atOnceUsers`, `rampUsers`, `constantUsersPerSec`, `rampUsersPerSec`) are open-loop (below) — only `constantConcurrentUsers` / `rampConcurrentUsers` inject closed-loop in Gatling. Source: https://docs.gatling.io/concepts/injection/.

- Models: realistic for thinking users behind a slow client (mobile keyboard).
- Hides: queueing delays, head-of-line blocking, real production behaviour where requests arrive whether or not the server is keeping up.

### Open-loop (arrival-rate)

New iterations start at a scheduled rate independently of earlier completions, while generator capacity remains available. This models exogenous arrivals; interactive user journeys can instead be closed-loop. If an iteration contains multiple sequential requests, its arrival rate is not the request rate.

```javascript
// k6 — open-loop arrival rate (the right default for SLO load tests)
export const options = {
  scenarios: {
    api_slo: {
      executor: 'constant-arrival-rate',
      rate: 500,                  // 500 iterations/sec; 500 RPS only for one request per iteration
      timeUnit: '1s',
      duration: '10m',
      preAllocatedVUs: 200,       // sized via Little's Law: 500 req/s * 0.4s expected latency = 200
      maxVUs: 1000,               // safety ceiling: 500 req/s * 2s SLO-breach latency = 1000
    },
  },
};
```

`preAllocatedVUs` and `maxVUs` are not arbitrary — size them with Little's Law (`L = λ × W`): concurrency needed equals arrival rate times the response time the generator must be able to sustain. See [capacity-planning.md — Little's Law](capacity-planning.md#littles-law-sizing-concurrency-from-rate-and-latency) for the full derivation. If a test starts dropping iterations or timing out at the VU ceiling before the target system shows distress, the load generator is under-provisioned, not the system under test.

Use `ramping-arrival-rate` for stepped open-loop ramps. Gatling's default injection steps — `atOnceUsers`, `rampUsers`, `constantUsersPerSec`, `rampUsersPerSec` — are open-loop. Locust's `wait_time = constant_throughput(...)` is **not** open-loop: it throttles each already-spawned user to at most N task executions/sec (one task can make multiple requests) but does not spawn new users to make up a shortfall when the server is slow, so it stays closed-loop in the sense that matters here (source: https://docs.locust.io/en/stable/writing-a-locustfile.html). A custom `LoadTestShape` controls target user counts and spawn speed; it does not alone make repeated tasks independent of response time. Use k6/Gatling arrival profiles for an arrival-rate gate, or verify a purpose-built Locust arrival model. JMeter has the Concurrency Thread Group + Throughput Shaping Timer plugin combination (open-loop-ish via active throttling) and a core "Open Model Thread Group" in newer releases (check that your installed version has it).

### Coordinated omission (the silent measurement bug)

A closed-loop generator under-reports tail latency because **slow responses delay the next request**, so the slow request count is artificially low. A 1s stall that should produce hundreds of slow samples produces one. Reported p99 looks fine; production p99 is much worse.

Mitigations, in order of preference:

1. Use open-loop / arrival-rate executors (above). Validate achieved arrivals and dropped iterations; an exhausted generator can still omit intended load.
2. If you must use closed-loop, enable a coordinated-omission correction: HdrHistogram's `recordValueWithExpectedInterval` / `copyCorrectedForCoordinatedOmission`, or `wrk2` (Tene's fix to wrk). Gatling's `pause`/`holdFor` control pacing between requests, not CO correction, and `hdr-plot` only plots an existing histogram — neither corrects the bug. Check the current Gatling docs for a built-in CO correction before recommending one.
3. Report deep-tail percentiles only with sufficient samples; p99.9 reporting does not repair coordinated omission.

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

**k6 distributed:** Use k6 Cloud or k6-operator for Kubernetes-native distribution. With k6 2.0, the Go module path changed to `go.k6.io/k6/v2`; custom extensions must update their import paths before they will compile against k6 2.0. k6 2.0 also fully removed the positional `k6 cloud script.js` form; use `k6 cloud run script.js`.

**Gatling distributed:** verify the deployment edition and supported distributed execution in the [official docs](https://docs.gatling.io/); multiple independent OSS runs need explicit coordination and result aggregation.

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

Measure when the workload stabilizes, then separate that warm-up interval from steady-state results. Keep cold-start scenarios separate. During warm-up:
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

**Worked example.** If two equal-size populations have different p99s, their average p99 does not determine the pooled percentile. Under a nearest-rank convention, the p99 of 2,000 pooled samples is the value at ascending rank 1,980; its value requires raw samples or a mergeable histogram. The 20th-worst value of one host is no greater than that host's 10th-worst value, so a pooled p99 near that host's p98 must not be described as necessarily above its p99.

**What to do instead:**
- Aggregate from raw latency samples or merged histograms (e.g., merge HdrHistogram serialized snapshots), then recompute the percentile once, over the combined population.
- If only per-host percentiles are available (common with some APM tools), report them per-host and flag the spread — do not synthesize a fleet-wide number by averaging.
- The same rule applies across time windows: a "weekly p99" is not the average of seven daily p99s; recompute it from the week's combined raw data.
- Dashboards that show "average of p99 across pods" as a fleet SLO indicator are producing a number with no defined statistical meaning — treat any dashboard doing this as reporting an approximation at best, and push to change it to a properly merged histogram.

## LLM / AI API Load Testing

LLM APIs behave fundamentally differently from REST APIs. Standard load testing tools measure the wrong things by default.

### Why Standard Tools Fall Short

k6 and Locust record wall-clock request duration, conflating two separate phases:
- **Prefill (TTFT)** — time until the model returns the first token; **compute-bound** (the full prompt is processed in one parallel forward pass, so it scales with prompt length and GPU FLOPs).
- **Decode (generation throughput)** — tokens per second after the first token; **memory-bandwidth-bound** (each step reads the whole KV cache and model weights to produce one token, so it scales with GPU HBM bandwidth, not compute). This is the premise `ai-llm-inference/references/disaggregated-inference.md` builds on — see that skill for serving-side prefill/decode disaggregation and capacity math.

A 10s request with 9.5s TTFT is a completely different failure mode from one with 500ms TTFT and slow decode. Aggregating them hides both.

Additionally, k6 and Locust treat streaming responses as atomic, so p99 latency reports the end-to-end duration, not the user-perceived first-response latency.

### Key Metrics

| Metric | Definition | Example SLO (set your own from UX research) |
|--------|-----------|-------------|
| TTFT (Time to First Token) | Latency from request to first token received | < 500ms (chat), < 200ms (real-time) |
| ITL (Inter-Token Latency) | Time between consecutive tokens; spikes signal overload | < 100ms (noticeable above this) |
| Tokens/sec (TPS) | Output throughput; varies by model and concurrency | Depends on model; track degradation |
| Goodput | % of requests meeting SLO at current concurrency | Match your SLO target |

### Tooling Approach

1. **Streaming metrics:** choose a harness that timestamps the first content token and subsequent tokens as events arrive. Verify protocol support and metric definitions in [AIPerf docs](https://docs.nvidia.com/aiperf/getting-started/migrating-from-gen-ai-perf) or your selected tool before choosing a release.
2. **CI gates:** use deterministic mocks for application behavior and separate approved live serving-capacity tests. Mock results cannot establish provider or GPU capacity.
3. **Load sweeps:** use progressively finer concurrency steps around the measured saturation knee.

### Realistic Workload Design

- Sample from production logs (sanitized) to get real prompt length distributions.
- Create three scenario classes: short queries (< 100 tokens), medium context (500–2k tokens), long context (> 8k tokens), weighted to production ratios.
- Test warm-cache and cold-cache scenarios separately. Cache state (prefix caching) can shift TTFT substantially for long shared prompts; the effect shrinks for short or unique prompts. Measure it on your own provider rather than quoting a figure.
- Choose soak duration from the suspected accumulation mechanism and observed trend, not a universal four-hour minimum.

**Buffered responses cannot measure TTFT.** `k6/http.post` returns a completed response; parsing `res.body` afterwards timestamps completion, not the first arriving content token. Use a verified streaming extension or event-aware harness for TTFT/ITL, and exclude metadata-only chunks from token timing ([k6 Response](https://grafana.com/docs/k6/latest/javascript-api/k6-http/response/)).

## Anti-Patterns

- **Single-endpoint hammering** — tests one URL at max speed; measures nothing real.
- **Wrong pacing** — model think time for interactive closed-loop users; arrival-rate executors already pace iterations, so do not add an end-of-iteration sleep as a second rate controller.
- **Shared test data** — all VUs use the same user/product; cache hit rate is 100%.
- **Testing from the same machine as the server** — CPU contention between load generator and system under test.
- **Ignoring client-side saturation** — the load generator itself bottlenecks; results plateau but the cause is the test harness, not the server.
- **Running once and calling it done** — single runs do not characterize variance; repeat until the noise/uncertainty estimate supports the decision.
- **Closed-loop generator for SLO testing** — VU-based load with no arrival-rate floor under-reports tail latency due to coordinated omission. Use `constant-arrival-rate` / `ramping-arrival-rate` for SLO load tests; report p99.9 alongside p99.
- **Average-only metrics** — averages hide bimodal distributions and tail outages. Always report p50/p95/p99/p99.9.
- **Averaging percentiles across hosts, pods, or runs** — percentiles do not aggregate linearly; averaging per-host p99s produces a number with no defined statistical meaning. Merge raw histograms and recompute (see [Why You Cannot Average Percentiles](#why-you-cannot-average-percentiles)).
- **Unlabelled warm-up** — mixing stabilization and steady-state samples obscures both; report cold-start behavior separately.
