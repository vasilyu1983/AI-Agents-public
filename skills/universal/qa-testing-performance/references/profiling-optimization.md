# Profiling and Optimization

Language-specific profiling guidance for CPU, memory, I/O, and network. Always profile before optimizing — measure the bottleneck, then fix it.

## Table of Contents

- [General Principles](#general-principles)
- [CPU, Memory, and GC Profiling](#cpu-memory-and-gc-profiling)
- [I/O and Network Profiling](#io-and-network-profiling)
  - [Network Latency Decomposition](#network-latency-decomposition)
  - [Database Query Profiling](#database-query-profiling)
- [Continuous Profiling](#continuous-profiling)
  - [Grafana Pyroscope](#grafana-pyroscope)
  - [When to Use Continuous Profiling vs On-Demand](#when-to-use-continuous-profiling-vs-on-demand)
- [Optimization Workflow](#optimization-workflow)

## General Principles

1. **Profile first, optimize second.** Intuition about bottlenecks is wrong more often than right.
2. **Use percentiles.** A function that is fast on average but has a 500ms p99 is a problem.
3. **Warm up before profiling.** JIT compilation, cache priming, and connection pool fill distort cold-start profiles.
4. **Profile under load.** Single-request profiling misses concurrency issues (lock contention, pool exhaustion, GC pressure).
5. **Compare profiles.** A flamegraph is most useful when compared against a baseline — look for what grew, not just what is large.

## CPU, Memory, and GC Profiling

Per-language profiler commands (flamegraphs, py-spy, cProfile, async-profiler,
JFR, dotnet-trace, GC logging, heap dumps) are owned by
[software-performance](../../software-performance/SKILL.md) — read it for the
current recipe per language/runtime. What belongs here instead is how
profiling connects to a *load test*: always profile under realistic
concurrency (single-request profiling misses lock contention, pool
exhaustion, and GC pressure that only appear under load), and compare a
flamegraph against a pre-change baseline rather than reading it in isolation.

## I/O and Network Profiling

### Network Latency Decomposition

Break down request latency into components:
- DNS resolution
- TCP connection
- TLS handshake
- Time to first byte (server and network waiting; not server CPU time alone)
- Content transfer

```javascript
// k6 — HTTP timing breakdown is built in
// Access via http_req_tls_handshaking, http_req_connecting,
// http_req_waiting (TTFB), http_req_receiving
```

### Database Query Profiling

Query-level profiling (slow query logs, EXPLAIN ANALYZE, index diagnosis) is owned by [data-sql-optimization](../../data-sql-optimization/SKILL.md). This skill's own [database-performance-testing.md](database-performance-testing.md) keeps only the load-generation side: connection-pool pressure testing under concurrency and replica-lag testing during sustained writes.

## Continuous Profiling

Continuous profiling collects CPU, memory, and allocation profiles from production systems on an always-on basis, enabling regression detection at deploy time without manual load tests.

### Grafana Pyroscope

Grafana Pyroscope is an open-source continuous profiling platform. Check its release notes for the current architecture and OTLP support before designing around them. Properties to confirm:

- Architecture: single write path (profiles written once to object storage), stateless read path (queriers scale elastically).
- Supports OpenTelemetry Protocol (OTLP) for profiling data natively.
- Grafana Cloud Profiles is the managed version.
- Integrates with Grafana dashboards and can correlate profiles with traces and logs.

**Installation and basic setup:**

```bash
# Docker Compose — Pyroscope standalone
docker run -d --name pyroscope \
  -p 4040:4040 \
  "grafana/pyroscope:${PYROSCOPE_IMAGE_TAG:?set a reviewed image tag}"

# Agent auto-discovery (eBPF-based, no code changes)
# Verify supported language/runtime combinations and required privileges in
# https://grafana.com/docs/pyroscope/latest/configure-client/grafana-alloy/ebpf/
```

```go
// Go — push profiles via SDK
import "github.com/grafana/pyroscope-go"

func main() {
  pyroscope.Start(pyroscope.Config{
    ApplicationName: "my-service",
    ServerAddress:   "http://pyroscope:4040",
    ProfileTypes:    []pyroscope.ProfileType{
      pyroscope.ProfileCPU,
      pyroscope.ProfileAllocObjects,
      pyroscope.ProfileInuseObjects,
    },
  })
  // application code
}
```

### When to Use Continuous Profiling vs On-Demand

| Approach | When to Use |
|----------|-------------|
| Continuous profiling (Pyroscope) | Always-on in staging and production; detects regressions at deploy time; finds gradual degradation |
| On-demand profiling (py-spy, pprof, async-profiler) | Deep investigation of a known hotspot; short-lived targeted capture |
| Load test + profiling | Reproducing a load-specific issue in a controlled environment |

**Key workflow:** Set up Pyroscope on staging. After each deploy, compare the CPU flamegraph against the previous baseline. A wider frame shows relative sampled profile weight; compare absolute sample totals, workload and duration before claiming added CPU work or an SLO regression.

## Optimization Workflow

1. **Identify** — use profiling to find the actual bottleneck (not the suspected one).
2. **Measure** — record the current metric (p95 latency, throughput, memory usage).
3. **Hypothesize** — propose a specific change with an expected improvement.
4. **Change one thing** — make a single change, re-profile, and measure the delta.
5. **Validate** — run the load test again to confirm the improvement under realistic conditions.
6. **Document** — record what was changed, the before/after metrics, and why.

Avoid:
- Changing multiple things at once (you cannot attribute improvement)
- Micro-optimizing code that is not on the hot path
- Optimizing for a metric that does not affect user experience
- Caching as the first resort (fix the underlying problem first, then cache if still needed)
