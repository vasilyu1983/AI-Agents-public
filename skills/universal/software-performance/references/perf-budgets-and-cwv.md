# Profiling Tools and Measurement Discipline

The filename is historical. Core Web Vitals thresholds, Lighthouse CI configuration, and k6 load patterns now live in [qa-testing-performance](../../qa-testing-performance/SKILL.md): see [frontend-performance.md](../../qa-testing-performance/references/frontend-performance.md), [performance-budgets-ci.md](../../qa-testing-performance/references/performance-budgets-ci.md), and [load-testing-patterns.md](../../qa-testing-performance/references/load-testing-patterns.md). For how INP measurement has changed, read the Chromium INP changelog (https://chromium.googlesource.com/chromium/src/+/main/docs/speed/metrics_changelog/inp.md) rather than secondary summaries.

## Table of Contents

- [Native Profiling Tools](#native-profiling-tools)
- [Production Traps](#production-traps)
- [Neutral Is a Revert](#neutral-is-a-revert)

---

## Native Profiling Tools

| Ecosystem | Tool | Primary Use |
|-----------|------|-------------|
| Go | `pprof` | CPU, heap, goroutine, mutex, and block profiles via `net/http/pprof` |
| .NET | `dotnet-counters`, `dotnet-trace` | Live runtime counters; traces for flamegraphs |
| JVM | async-profiler, JFR | CPU/allocation flamegraphs without safepoint bias; `-e lock` or JFR lock events for Java monitor contention; `--nativelock` covers native pthread locks only |
| Node.js | `node --cpu-prof` (or `--prof` + `--prof-process`) | V8 CPU profile loadable in Chrome DevTools |
| Python | `py-spy` (sampling) or `cProfile` (deterministic) | Prefer external sampling for a live service; `cProfile` adds per-call overhead, so measure its impact before using it on production traffic ([Python profiler limitations](https://docs.python.org/3/library/profile.html)) |
| iOS/macOS | Instruments (Time Profiler, Allocations) | Xcode-integrated; `xctrace` for CLI |
| Rust | `cargo flamegraph` (via perf/dtrace) | Sampling flamegraphs |
| Linux, any runtime | `perf`, eBPF tools (e.g., `bpftrace`, `offcputime`) | Off-CPU time, run-queue latency, CPU throttling |

### pprof quick start (Go)

```go
import (
    "log"
    "net/http"
    _ "net/http/pprof"
)
// Inside main: serve DefaultServeMux on a local diagnostics listener.
go func() {
    log.Print(http.ListenAndServe("127.0.0.1:6060", nil))
}()
```

```bash
go tool pprof -http=127.0.0.1:6061 'http://127.0.0.1:6060/debug/pprof/profile?seconds=30'
```

The import registers handlers on `http.DefaultServeMux`; it starts no server and does not modify a custom mux. Register the profiling handlers explicitly on a custom diagnostics mux if needed. Block and mutex collection also require `runtime.SetBlockProfileRate` and `runtime.SetMutexProfileFraction`; choose sampling rates and measure overhead ([Go pprof](https://pkg.go.dev/net/http/pprof)).

### dotnet-counters quick start

```bash
dotnet-counters monitor --process-id <PID> \
  System.Runtime Microsoft.AspNetCore.Hosting
```

---

## Production Traps

- **CLI flag drift across profiler and CI tool versions.** Flags on fast-moving CLIs (`lhci`, `dotnet-counters`, `dotnet-trace`, async-profiler) change between releases. Pin the tool version in long-lived scripts and run `--help` against that version when writing them.
- **Profiling a different shape than production.** Debug builds, small datasets, and missing downstream latency move the hot path. Profile the build and data shape that shows the symptom.
- **Sampling only on-CPU time.** If latency is high while CPU is low, an on-CPU flamegraph shows the wrong thing; capture wall-clock or off-CPU profiles.

---

## Neutral Is a Revert

> Source: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), `skills/performance-optimization/SKILL.md`, commit `7676817`, MIT License. Extracted 2026-08-09.

A benchmark-variance rule for judging "did this change actually help," referenced from [SKILL.md's "When NOT to Optimize"](../SKILL.md#when-not-to-optimize).

- Re-measure a performance change under the same conditions as the baseline: same environment, same load shape, same tool, same number of runs.
- Compare the result to the baseline's measured noise band (run-to-run variance), not to a single baseline number.
- If the result falls inside the noise band, the change is reverted. It is not kept as "harmless" or "probably fine" — a result that cannot be distinguished from noise has not been proven to help, and shipped complexity without a proven win is a net cost.
- "Neutral" and "no regression" are not the same as "improvement." Only a delta that clears the noise band counts as a win worth keeping.

### Idea Ledger

Log every attempted optimization — including reverted ones — in a table with this shape (synthetic examples):

| Idea | Baseline → Result | Verdict | Why |
|------|--------------------|---------|-----|
| Add Redis cache in front of `/orders` read path | p95 142ms → 138ms (noise band ±8ms) | Reverted | Delta inside measurement noise; added cache-invalidation complexity for no proven gain |
| Batch N+1 queries in `OrderService.list()` | p95 142ms → 61ms (noise band ±8ms) | Kept | Delta clears noise band by >9x; re-measured 3x to confirm |

- Log the entry at the same time as the revert, not after the fact from memory — a reverted attempt with no record is indistinguishable from an attempt nobody thought of yet.
- Before starting a new optimization, check the ledger for the same idea. A previously reverted attempt is not automatically wrong to retry (baseline conditions can change), but retrying it silently — without checking whether the earlier revert's "why" still applies — re-burns the same investigation.
