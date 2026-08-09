# Profiling and Optimization

Language-specific profiling guidance for CPU, memory, I/O, and network. Always profile before optimizing — measure the bottleneck, then fix it.

## Table of Contents

- [General Principles](#general-principles)
- [CPU Profiling](#cpu-profiling)
- [Flamegraphs](#flamegraphs)
- [Node.js](#nodejs)
- [Built-in V8 profiler — generates a .log, convert to flamegraph](#built-in-v8-profiler-—-generates-a-log-convert-to-flamegraph)
- [Clinic.js — automated profiling with visual reports](#clinicjs-—-automated-profiling-with-visual-reports)
- [0x — flamegraph generation](#0x-—-flamegraph-generation)
- [Python](#python)
- [py-spy — sampling profiler, no code changes needed](#py-spy-—-sampling-profiler-no-code-changes-needed)
- [cProfile — built-in deterministic profiler](#cprofile-—-built-in-deterministic-profiler)
- [Visualize with snakeviz](#visualize-with-snakeviz)
- [scalene — CPU + memory + GPU profiler](#scalene-—-cpu-memory-gpu-profiler)
- [Java / Kotlin (JVM)](#java-kotlin-jvm)
- [async-profiler — low-overhead, production-safe](#async-profiler-—-low-overhead-production-safe)
- [CPU profile as flamegraph](#cpu-profile-as-flamegraph)
- [Allocation profile](#allocation-profile)
- [Lock contention profile](#lock-contention-profile)
- [JFR (Java Flight Recorder) — built into JDK](#jfr-java-flight-recorder-—-built-into-jdk)
- [Analyze with JDK Mission Control or IntelliJ](#analyze-with-jdk-mission-control-or-intellij)
- [Go](#go)
- [Capture and visualize](#capture-and-visualize)
- [.NET](#net)
- [dotnet-trace — cross-platform tracing](#dotnet-trace-—-cross-platform-tracing)
- [Analyze with speedscope or PerfView](#analyze-with-speedscope-or-perfview)
- [dotnet-counters — live metrics](#dotnet-counters-—-live-metrics)
- [BenchmarkDotNet for micro-benchmarks](#benchmarkdotnet-for-micro-benchmarks)
- [Add [Benchmark] attributes to methods](#add-benchmark-attributes-to-methods)
- [Memory Profiling](#memory-profiling)
- [Detecting Memory Leaks](#detecting-memory-leaks)
- [Node.js](#nodejs)
- [Using clinic.js for heap analysis](#using-clinicjs-for-heap-analysis)
- [Python](#python)
- [tracemalloc — built-in memory tracking](#tracemalloc-—-built-in-memory-tracking)
- [... run workload ...](#run-workload)
- [memray — modern Python memory profiler](#memray-—-modern-python-memory-profiler)
- [JVM (Java/Kotlin)](#jvm-javakotlin)
- [Heap dump](#heap-dump)
- [Or trigger on OOM: -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/](#or-trigger-on-oom-xxheapdumponoutofmemoryerror-xxheapdumppath=tmp)
- [Analyze with Eclipse MAT, VisualVM, or IntelliJ profiler](#analyze-with-eclipse-mat-visualvm-or-intellij-profiler)
- [Look for: dominator tree, leak suspects, histogram comparison](#look-for-dominator-tree-leak-suspects-histogram-comparison)
- [Go](#go)
- [Heap profile](#heap-profile)
- [Goroutine leak detection](#goroutine-leak-detection)
- [GC Analysis](#gc-analysis)
- [Node.js](#nodejs)
- [V8 GC logging](#v8-gc-logging)
- [Or use --expose-gc and manual GC timing](#or-use-expose-gc-and-manual-gc-timing)
- [JVM](#jvm)
- [GC logging](#gc-logging)
- [Analyze with GCViewer or GCEasy](#analyze-with-gcviewer-or-gceasy)
- [Go](#go)
- [GC trace](#gc-trace)
- [Output: gc 1 @0.012s 2%: pause times, heap sizes](#output-gc-1-@0012s-2%-pause-times-heap-sizes)
- [I/O and Network Profiling](#io-and-network-profiling)
- [Network Latency Decomposition](#network-latency-decomposition)
- [Database Query Profiling](#database-query-profiling)
- [Optimization Workflow](#optimization-workflow)

## General Principles

1. **Profile first, optimize second.** Intuition about bottlenecks is wrong more often than right.
2. **Use percentiles.** A function that is fast on average but has a 500ms p99 is a problem.
3. **Warm up before profiling.** JIT compilation, cache priming, and connection pool fill distort cold-start profiles.
4. **Profile under load.** Single-request profiling misses concurrency issues (lock contention, pool exhaustion, GC pressure).
5. **Compare profiles.** A flamegraph is most useful when compared against a baseline — look for what grew, not just what is large.

## CPU Profiling

### Flamegraphs

Flamegraphs visualize stack trace samples. Width = time spent. Look for wide bars (hot functions) and unexpected depth (unnecessary call chains).

**Reading a flamegraph:**
- X-axis: stack frame width proportional to time on CPU
- Y-axis: call stack depth
- Wide plateaus at the top = leaf functions consuming CPU
- Compare two flamegraphs (differential flamegraph) to see what changed

### Node.js

```bash
# Built-in V8 profiler — generates a .log, convert to flamegraph
node --prof app.js
node --prof-process isolate-*.log > processed.txt

# Clinic.js — automated profiling with visual reports
npx clinic doctor -- node app.js
npx clinic flame -- node app.js
npx clinic bubbleprof -- node app.js  # async bottlenecks

# 0x — flamegraph generation
npx 0x app.js
```

### Python

```bash
# py-spy — sampling profiler, no code changes needed
py-spy record -o profile.svg --pid <PID>
py-spy record -o profile.svg -- python app.py
py-spy top --pid <PID>  # live top-like view

# cProfile — built-in deterministic profiler
python -m cProfile -o output.prof app.py
# Visualize with snakeviz
pip install snakeviz
snakeviz output.prof

# scalene — CPU + memory + GPU profiler
pip install scalene
scalene app.py
```

### Java / Kotlin (JVM)

```bash
# async-profiler — low-overhead, production-safe
# CPU profile as flamegraph
./asprof -d 30 -f cpu.html <PID>

# Allocation profile
./asprof -d 30 -e alloc -f alloc.html <PID>

# Lock contention profile
./asprof -d 30 -e lock -f lock.html <PID>

# JFR (Java Flight Recorder) — built into JDK
java -XX:+FlightRecorder -XX:StartFlightRecording=duration=60s,filename=recording.jfr app.jar
# Analyze with JDK Mission Control or IntelliJ
```

### Go

```go
// Built-in pprof — add to any HTTP server
import _ "net/http/pprof"
// Then: go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

// CPU profile
// go tool pprof -http=:8080 cpu.prof  (opens web UI with flamegraph)

// Benchmark profiling
// go test -bench=. -cpuprofile=cpu.prof -memprofile=mem.prof
```

```bash
# Capture and visualize
curl -o cpu.prof 'http://localhost:6060/debug/pprof/profile?seconds=30'
go tool pprof -http=:8080 cpu.prof
```

### .NET

```bash
# dotnet-trace — cross-platform tracing
dotnet trace collect --process-id <PID> --duration 00:00:30
# Analyze with speedscope or PerfView

# dotnet-counters — live metrics
dotnet counters monitor --process-id <PID>

# BenchmarkDotNet for micro-benchmarks
# Add [Benchmark] attributes to methods
```

## Memory Profiling

### Detecting Memory Leaks

1. Take a heap snapshot at baseline (after warm-up).
2. Run load for a defined period.
3. Take another heap snapshot.
4. Compare retained objects — growing object counts indicate a leak.
5. Repeat at longer intervals to confirm the trend.

### Node.js

```javascript
// Heap snapshot via code
const v8 = require('v8');
const fs = require('fs');

function takeHeapSnapshot(label) {
  const filename = `heap-${label}-${Date.now()}.heapsnapshot`;
  const snapshotStream = v8.writeHeapSnapshot(filename);
  console.log(`Heap snapshot written to ${snapshotStream}`);
}

// Take snapshots at intervals during soak test
// Compare in Chrome DevTools → Memory → Load snapshot
```

```bash
# Using clinic.js for heap analysis
npx clinic heapprofiler -- node app.js
```

### Python

```python
# tracemalloc — built-in memory tracking
import tracemalloc
tracemalloc.start()

# ... run workload ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

```bash
# memray — modern Python memory profiler
pip install memray
memray run app.py
memray flamegraph output.bin  # generates HTML flamegraph
memray table output.bin       # tabular summary
```

### JVM (Java/Kotlin)

```bash
# Heap dump
jmap -dump:format=b,file=heap.hprof <PID>
# Or trigger on OOM: -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/

# Analyze with Eclipse MAT, VisualVM, or IntelliJ profiler
# Look for: dominator tree, leak suspects, histogram comparison
```

### Go

```bash
# Heap profile
curl -o heap.prof http://localhost:6060/debug/pprof/heap
go tool pprof -http=:8080 heap.prof

# Goroutine leak detection
curl http://localhost:6060/debug/pprof/goroutine?debug=2
```

## GC Analysis

Garbage collection pauses affect tail latency. Monitor GC behavior under load.

### Node.js
```bash
# V8 GC logging
node --trace-gc app.js
# Or use --expose-gc and manual GC timing
```

### JVM
```bash
# GC logging
java -Xlog:gc*:file=gc.log:time,tags:filecount=5,filesize=10m -jar app.jar
# Analyze with GCViewer or GCEasy
```

### Go
```bash
# GC trace
GODEBUG=gctrace=1 ./app
# Output: gc 1 @0.012s 2%: pause times, heap sizes
```

## I/O and Network Profiling

### Network Latency Decomposition

Break down request latency into components:
- DNS resolution
- TCP connection
- TLS handshake
- Time to first byte (server processing)
- Content transfer

```javascript
// k6 — HTTP timing breakdown is built in
// Access via http_req_tls_handshaking, http_req_connecting,
// http_req_waiting (TTFB), http_req_receiving
```

### Database Query Profiling

- Enable slow query logging (MySQL: `long_query_time`, PostgreSQL: `log_min_duration_statement`)
- Use EXPLAIN ANALYZE on slow queries
- Track query execution time percentiles, not just averages
- Monitor connection pool metrics: active, idle, waiting, timeouts

## Continuous Profiling

Continuous profiling collects CPU, memory, and allocation profiles from production systems on an always-on basis, enabling regression detection at deploy time without manual load tests.

### Grafana Pyroscope 2.0

Pyroscope 2.0 (GA April 2026) is the primary OSS continuous profiling platform. Key facts for 2026:

- Architecture: single write path (profiles written once to object storage), stateless read path (queriers scale elastically).
- Supports OpenTelemetry Protocol (OTLP) for profiling data natively.
- Grafana Cloud Profiles is the managed version (running Pyroscope 2.0 architecture since April 2025).
- Integrates with Grafana dashboards and can correlate profiles with traces and logs.

**Installation and basic setup:**

```bash
# Docker Compose — Pyroscope standalone
docker run -d --name pyroscope \
  -p 4040:4040 \
  grafana/pyroscope:latest

# Agent auto-discovery (eBPF-based, no code changes)
# Supports: Go, Java, Python, Ruby, .NET, Node.js
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

**Key workflow:** Set up Pyroscope on staging. After each deploy, compare the CPU flamegraph against the previous baseline. Regressions appear as wider frames in hot functions before they reach production SLO breaches.

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
