# Capacity Planning

From load test results to infrastructure sizing, cost modeling, and growth projections.

## Table of Contents

- [Little's Law: Sizing Concurrency from Rate and Latency](#littles-law-sizing-concurrency-from-rate-and-latency)
- [From Load Tests to Sizing](#from-load-tests-to-sizing)
- [Step 1: Determine Per-Instance Capacity](#step-1-determine-per-instance-capacity)
- [Step 2: Calculate Instance Count](#step-2-calculate-instance-count)
- [Step 3: Validate with Multi-Instance Load Test](#step-3-validate-with-multi-instance-load-test)
- [Traffic Modeling](#traffic-modeling)
- [Characterize Traffic Patterns](#characterize-traffic-patterns)
- [Growth Projection](#growth-projection)
- [Cost Modeling](#cost-modeling)
- [Compute Cost Estimation](#compute-cost-estimation)
- [Cost per Request](#cost-per-request)
- [Cost Optimization Levers](#cost-optimization-levers)
- [Headroom Calculation](#headroom-calculation)
- [Why Headroom Matters](#why-headroom-matters)
- [Recommended Headroom](#recommended-headroom)
- [Headroom Formula](#headroom-formula)
- [Auto-Scaling Validation](#auto-scaling-validation)
- [What to Validate](#what-to-validate)
- [Testing Auto-Scaling](#testing-auto-scaling)
- [Database Capacity](#database-capacity)
- [Connection Math](#connection-math)
- [Capacity Review Cadence](#capacity-review-cadence)

## Little's Law: Sizing Concurrency from Rate and Latency

Little's Law (`L = λ × W`) relates three quantities in any stable queueing system: the average number of items in the system (`L`), the average arrival rate (`λ`), and the average time each item spends in the system (`W`). It requires no assumption about the distribution of arrivals or service times — it holds for any stable system over a long-enough window. This makes it the fastest sanity check available before running a single load test.

**Use 1 — estimate `preAllocatedVUs`/`maxVUs` for an arrival-rate k6 test.** Use iteration rate and full iteration duration (including sequential requests and journey think time); response time alone works only for a one-request iteration. Treat the product of means as an initial estimate, then add measured variance margin.

If a test targets `λ = 500` requests/sec and the *expected* response time under normal (non-saturated) conditions is `W = 0.4s`, the number of in-flight requests the load generator must be able to sustain is:

```text
L = λ × W = 500 req/s × 0.4 s = 200 concurrent in-flight requests
```

In the one-request worked example, that is why the `preAllocatedVUs: 200` value in the `constant-arrival-rate` example in [load-testing-patterns.md](load-testing-patterns.md#open-loop-arrival-rate) matches `rate: 500` at an assumed 400ms response time. Set `maxVUs` from the *worst-case* latency you want the generator to be able to absorb without dropping iterations — e.g., if the SLO ceiling is 2s before you consider the system failed, `L = 500 × 2 = 1000`, matching the `maxVUs: 1000` safety ceiling in that same example. If measured latency during the test approaches the `maxVUs` bound, the load generator itself may be under-provisioned — check for VU exhaustion before concluding the target system is the bottleneck.

**Use 2 — back-of-envelope check before building a load-testing harness.**

A checkout API needs to sustain `λ = 50` requests/sec at an SLO of `W = 200ms` per request. Required concurrent capacity: `L = 50 × 0.2 = 10`. If the service already runs with 30 worker threads/connections in production, this is a 3x concurrency margin on paper, not proof of throughput or tail-latency headroom; confirm worker occupancy and downstream limits before deciding which test to run (see [When NOT to Load Test](../SKILL.md#when-not-to-load-test)).

**Common misuse:** Little's Law describes averages over a stable window — it does not predict tail latency or say anything about what happens *during* a transient spike, and it breaks down once the system is unstable (arrival rate exceeds service rate and the queue grows without bound; `L` is diverging, not constant). Use it for steady-state sizing, not for capacity-ceiling or spike-test predictions — those require an actual stress/spike test.

## From Load Tests to Sizing

### Step 1: Determine Per-Instance Capacity

Run a stress test against a single instance (or minimal deployment) to find:
- **Max throughput** — requests/sec before SLO violation (latency p95 breach or error rate spike).
- **Resource ceiling** — CPU and other limiting resources at max throughput; choose headroom from measured queueing and failure tolerance.
- **Memory steady state** — stable memory usage under sustained load.

```text
Example:
  Single instance: 2 vCPU, 4GB RAM
  Max throughput at SLO: 250 rps (p95 < 200ms, error rate < 0.1%)
  CPU at max throughput: 85%
  Usable capacity (70% target): ~200 rps per instance
```

### Step 2: Calculate Instance Count

```text
Required instances = (Peak traffic RPS / Per-instance usable capacity) * Safety multiplier

Example:
  Peak traffic: 2000 rps
  Per-instance capacity: 200 rps
  Safety multiplier: 1.3 (30% headroom for variance and growth)
  Required: (2000 / 200) * 1.3 = 13 instances
```

**This synthetic example applies two distinct margins.** The 70% CPU target already discounted the 250 rps max down to ~200 rps; the 1.3 safety multiplier then adds a second margin on top. At 13 instances, effective steady-state load is 2000/13 ≈ 154 rps/instance, about 52% CPU (85% × 154/250) only under an unverified linear CPU-throughput approximation — well under even the 70% target. That is intentional double-margining for a checkout-critical path; for a less critical service, use only one mechanism (either the CPU target or the safety multiplier, not both) to avoid over-provisioning.

A fixed CPU target is a policy example, not a universal saturation point. For an M/M/1 resource, mean time in system `W = S / (1 − ρ)` grows sharply near saturation — about `3.3×` service time at ρ = 0.7 versus `6.7×` at ρ = 0.85. See [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md) for the full utilization-knee math (M/M/c, Erlang, USL) instead of re-deriving it here.

### Step 3: Validate with Multi-Instance Load Test

Run the full load test against the calculated deployment size. Verify:
- Latency SLOs are met at peak load
- Error rate stays within budget
- No single instance is a hotspot (check load balancer distribution)
- Database and downstream dependencies handle the aggregate load

## Traffic Modeling

### Characterize Traffic Patterns

| Pattern | Description | Sizing Implication |
|---------|-------------|--------------------|
| Steady | Consistent traffic with minor variation | Size for average + headroom |
| Diurnal | Peak during business hours, low at night | Auto-scale or size for peak |
| Weekly | Higher traffic on specific days | Size for peak day + headroom |
| Seasonal | Major spikes during events (Black Friday, launches) | Pre-scale for events, auto-scale for organic growth |
| Bursty | Unpredictable spikes (viral content, breaking news) | Auto-scale with fast scale-up, spike test regularly |

### Growth Projection

```text
Current peak: 2000 rps
Monthly growth rate: 8%
12-month projection: 2000 * (1.08)^12 = 2000 * 2.518 = ~5036 rps
Planned capacity (with 30% headroom): 5036 * 1.3 = ~6547 rps
Instances needed: 6547 / 200 = 32.7 -> 33 instances
```

Review projections quarterly. Compare actual growth against projections and adjust.

## Cost Modeling

### Compute Cost Estimation

```text
Instance cost: $0.096/hr — illustrative figure; look up your actual instance's
  on-demand rate in your region from the provider's price list before
  using this math for a real budget.
Instances needed (steady state): 13
Monthly cost (steady state): 13 * $0.096 * 730 = ~$911/month

With auto-scaling (average 10 instances, peak 16):
Monthly cost: 10 * $0.096 * 600 + 16 * $0.096 * 130 = ~$776/month
```

### Cost per Request

Use the **average** request rate over the billing period, not the peak — peak rps sized your instance count, but average rps drives the request volume that cost gets divided across. Using peak rps here overstates the denominator and understates true cost-per-request.

```text
Monthly cost: $911
Average traffic (illustrative, well under the 2000 rps peak): 800 rps
Monthly requests: 800 rps * 86400 sec/day * 30 days = 2.07B requests
Cost per million requests: $911 / 2074 = $0.44/million
```

Track cost per request over time. If it rises without feature changes, investigate efficiency regressions.

### Cost Optimization Levers

The savings figures previously listed here are unverified; estimate savings using the provider's current regional pricing and your measured workload.

| Lever | Measurement needed | Trade-off |
|-------|--------------------|-----------|
| Right-sizing | Same-load cost and SLO comparison | Must preserve tested capacity |
| Spot/preemptible instances | Current discount and interruption behavior | Termination handling |
| Reserved instances / savings plans | Eligible usage, term and break-even | Commitment risk |
| Auto-scaling | Observed instance-hours including bursts | Scale-up latency |
| Caching / CDN | Hit ratio and origin cost reduction | Staleness and invalidation |

## Headroom Calculation

### Why Headroom Matters

Running at 100% capacity means any variance (traffic spike, slow dependency, GC pause) causes SLO violations. Headroom absorbs variance.

### Recommended Headroom

| Context | Headroom | Rationale |
|---------|----------|-----------|
| Steady traffic, auto-scaling | 20% | Auto-scaling handles spikes; headroom covers scale-up lag |
| Steady traffic, fixed capacity | 30% | No auto-scaling; must absorb spikes in-place |
| Bursty traffic | 40-50% | Spikes are unpredictable and large |
| Pre-event (planned spike) | 50-100% | Pre-scale for known peak; cost is temporary |

### Headroom Formula

```text
Provisioned capacity = Peak expected traffic * (1 + extra_capacity_fraction)
# This defines extra capacity relative to peak, not unused fraction of provisioned capacity.

Example:
  Peak: 2000 rps
  Headroom: 30%
  Provisioned: 2000 * 1.3 = 2600 rps
  Instances: 2600 / 200 = 13
```

## Auto-Scaling Validation

### What to Validate

| Metric | Target | Test Method |
|--------|--------|-------------|
| Scale-up trigger latency | < 60s from threshold breach to new instance ready | Spike test + monitoring |
| Cold start impact | < 5% error rate increase during scale-up | Spike test + error tracking |
| Scale-down behavior | No premature scale-down during traffic fluctuation | Variable load test |
| Minimum instances | Sufficient for baseline traffic + immediate spike buffer | Soak test at minimum |
| Maximum instances | Cost-bounded ceiling | Stress test to confirm cap is hit, not exceeded |

### Testing Auto-Scaling

```javascript
// k6 — auto-scaling validation pattern
export const options = {
  stages: [
    { duration: '2m', target: 10 },    // baseline (minimum instances)
    { duration: '30s', target: 200 },   // rapid spike → trigger scale-up
    { duration: '5m', target: 200 },    // hold → verify new instances handle load
    { duration: '30s', target: 10 },    // drop → observe scale-down
    { duration: '5m', target: 10 },     // hold → verify no premature scale-down
    { duration: '30s', target: 300 },   // second spike → verify re-scale
    { duration: '5m', target: 300 },    // hold at higher level
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.05'],  // 5% tolerance during scaling
  },
};
```

Monitor during the test:
- Instance count over time (overlay with traffic)
- Error rate during scale-up window
- Latency during scale-up window
- Time from spike start to instance ready

## Database Capacity

Database is often the bottleneck before compute. Plan database capacity separately.

| Factor | Planning Input |
|--------|---------------|
| Connections | Max pool size * number of app instances |
| Read throughput | Queries/sec from load test, read replica count |
| Write throughput | Writes/sec from load test, single-primary constraint |
| Storage growth | Data volume growth rate, retention policy |
| IOPS | Peak IOPS from load test, provisioned IOPS budget |

### Connection Math

```text
App instances: 13
Pool size per instance: 20
Total connections: 13 * 20 = 260
Database max connections: 300 (synthetic value; read configured max_connections and reserved slots)
Headroom: 300 - 260 = 40 connections for admin, monitoring, migrations
```

If connection count approaches database limits, add a connection pooler (PgBouncer, ProxySQL).

## Capacity Review Cadence

| Review | Frequency | Scope |
|--------|-----------|-------|
| Growth vs projection | Monthly | Compare actual traffic to projected |
| Load test baseline | Monthly | Re-run standard load test, compare to previous |
| Full capacity test | Quarterly | Stress test to find current ceiling |
| Cost review | Quarterly | Cost per request trend, optimization opportunities |
| Pre-event planning | As needed | Dedicated capacity plan for planned traffic spikes |
