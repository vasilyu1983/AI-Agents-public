---
name: software-performance
description: "Diagnoses slow services and regressions via profiling and tail-latency math. Use when diagnosing slow services, profiling hot paths, or judging whether an optimization is real."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-27
---

# Performance Diagnosis

Use this skill to find out why something is slow and whether a fix really helped: symptom, profile, bottleneck, smallest proven fix, and re-measurement. It owns profiling, misdiagnosis checks, tail-latency and capacity math, and before/after regression judgment. It does not design load-test campaigns, CI performance gates, or Core Web Vitals budgets.

## Quick Reference

| Task | Use |
|------|-----|
| CPU hot path | Flamegraph-first profiling with the language's own profiler ([references/perf-budgets-and-cwv.md](references/perf-budgets-and-cwv.md#native-profiling-tools)) |
| Pauses, stalls, rising p99 | Lock-aware and off-CPU profiles before GC tuning (see Common Misdiagnoses) |
| "Did this change help?" | Same-conditions re-measure against the baseline noise band ([Neutral Is a Revert](references/perf-budgets-and-cwv.md#neutral-is-a-revert)) |
| Frontend regression from Lighthouse JSON | [scripts/check_perf_budget.py](scripts/check_perf_budget.py) (exit 1 on breach; 2 on invalid input or missing budgeted metrics; missing INP may use an explicit TBT lab budget) |

## Route Elsewhere

- Load, stress, soak, and spike test design, arrival-rate models, CI performance gates, Lighthouse CI, Core Web Vitals budgets: [qa-testing-performance](../qa-testing-performance/SKILL.md) (CWV detail in its [frontend-performance.md](../qa-testing-performance/references/frontend-performance.md)).
- SQL query tuning, plans, and indexing: [data-sql-optimization](../data-sql-optimization/SKILL.md).
- Frontend implementation fixes: [software-frontend](../software-frontend/SKILL.md). Mobile: [software-mobile](../software-mobile/SKILL.md).
- Telemetry and tracing setup: [qa-observability](../qa-observability/SKILL.md). Retries and breakers: [qa-resilience](../qa-resilience/SKILL.md).
- Scaling architecture: [software-architecture-design](../software-architecture-design/SKILL.md). Queueing models and USL curves: [foundations-queueing-theory](../foundations-queueing-theory/SKILL.md).

## Workflow

1. Define the symptom, the metric that shows it (p50/p95/p99, throughput, heap), the traffic shape, and the acceptance threshold.
2. Reproduce under a production-like build, dataset, and deployment shape.
3. Profile the smallest thing that exposes the bottleneck: CPU flamegraph, lock/off-CPU profile, heap snapshot diff, or trace. For a multi-hop path (source event, provider API, worker, queue, cache, edge, client render), write the path down and time each segment separately; the end-to-end number does not say which segment owns the delay.
4. Fix only the measured constraint; resist adjacent cleanups in the same change.
5. Re-measure with the same method and number of runs; keep the change only if it clears the noise band.

### When NOT to Optimize

- The path is not on a measured critical path for users or cost (a report run 3x/week is not worth the profiling sprint a checkout endpoint is).
- The gain is real but below the noise floor of your measurement; you cannot prove it shipped.
- The fix trades a rare but catastrophic failure mode (e.g., removing a safety timeout) for average-case speed.
- The team cannot commit to re-measuring after the change; an unverified "optimization" is a liability.
- The business impact of the current latency is unclear; ship the instrumentation first.

### Common Misdiagnoses

- **Blaming GC for lock contention.** Long pauses under load are just as often monitor/mutex contention, thread-pool starvation, or connection-pool waits. Distinguish with a lock-aware profile before touching heap or GC flags: JFR lock events or async-profiler `-e lock` for Java monitors (its `--nativelock` mode covers native pthread locks only), Go's mutex and block profiles.
- **Blaming the database for time "in the driver".** Driver time can be network wait on sequential calls that could be batched or parallelized, not slow queries.
- **Blaming a cold cache for a new synchronous call in the hot path.** Warm the cache and re-test before concluding the cache is the fix.
- **Blaming "the network" for queueing.** A rising p99 with a flat p50 under increasing load is usually a queueing or concurrency-limit signal (see Little's Law), not a network problem.
- **Reading low latency or a short queue as fresh data.** Freshness (the age of the newest data the user sees) is its own metric. A fast cache hit or an empty queue can still serve stale state; measure age at the visible surface separately from queue depth and request latency.
- **Reading an on-CPU flamegraph for a wait problem.** If CPU is low but latency is high, the time is off-CPU (I/O, locks, run-queue delay, CPU throttling from container quotas); use wall-clock or off-CPU profiling.

## Tail-Latency and Capacity Math

- **Little's Law** `L = λ × W`: at 500 req/s and 0.3 s latency, 150 requests are in flight. A closed-model load generator with 50 VUs and no think time caps out at `50 / 0.3 ≈ 166.7 req/s`, so a clean-looking result never exercised the target. Check `concurrency ≥ target_rps × latency_s`, or use an arrival-rate test (see qa-testing-performance).
- **Pool ceilings:** 20 connections held 50 ms each saturate at `20 / 0.05 = 400 req/s`, whatever the CPU headroom.
- **Amdahl's Law** `speedup = 1 / (s + (1 − s) / N)`: with a 20% serial fraction the ceiling is `1 / 0.2 = 5×`. Measure the serial fraction (locks, single-writer steps, shared queues) before recommending more workers.
- **Fan-out worked example:** if 10 calls independently have a 1% chance of exceeding their respective p99 thresholds, at least one exceeds its threshold with probability `1 − 0.99^10 ≈ 9.6%`. Shared dependencies can correlate slow calls; measure the joint tail rather than assuming independence. Per-service p99s alone do not determine the end-to-end tail.
- **Never average percentiles** across hosts or windows; compute the percentile over the merged sample or merge histograms (HDR/t-digest).

## Benchmark Validity Gate

Record workload, data volume and distribution, concurrency, warm-up, cache state, build mode, hardware, network path, and run-to-run variance with every result. Change one variable at a time. Reject conclusions from a single run, a debug build, a synthetic happy path, or a benchmark whose bottleneck differs from production. Compare distributions (medians and tails over repeated runs, or a confidence interval), not one number against another. Also reject a win where the mean improves while p95/p99 worsen on the user path that matters, and a cache win that hides a missing index or adds invalidation, staleness, or memory cost.

**Search loops** (tuning parameters, trying many variants): log every run with its hypothesis, command, result, and correctness check. Compare each candidate with the current accepted winner, not only the previous run, and confirm a new winner on a holdout or replay workload it was not tuned on. Stop when gains fall inside the noise band, correctness fails, the cost budget is spent, or more variables are changing than you can explain. Report the "best measured variant", not an optimum, unless the search was exhaustive.

Profiler flags, tool capabilities, and version-specific behaviour are time-sensitive: verify them against current primary sources (see [data/sources.json](data/sources.json)) or run `--help` on the pinned version. If live verification is unavailable, give methodology and mark tooling claims provisional.

## Output Modes

- **Performance diagnosis:** suspected bottleneck, evidence, ruled-out misdiagnoses, next measurement.
- **Regression review:** before/after evidence, noise band, ship/revert recommendation.
- **Hand-off:** when the answer is "build a load test" or "add a CI gate", state the target and route to qa-testing-performance.

## Scenarios

- **API p95 regression after a release:** capture a CPU flamegraph under production-like load before bisecting. Check per-request work added by the release (token decode, N+1 calls, new locks). Fix the smallest measured bottleneck, then compare repeated runs' medians and p99s.
- **p99 doubled, p50 flat, CPU at 40%:** suspect queueing or contention, not raw CPU. Check pool and thread-pool saturation, lock profiles, and off-CPU time before GC tuning.
- **Memory growth in a long-running service:** take heap snapshots early and after hours of steady load, diff retained objects (closures, unbounded caches, listeners not removed). Confirm with a flat heap trend on a re-run.
- **Slow LCP in field data:** identify the LCP element and measure TTFB, resource load delay, load duration, and render delay; fix the dominant measured constraint ([LCP breakdown](https://web.dev/articles/optimize-lcp#lcp-breakdown)). A large image or high TTFB alone does not establish the first fix. Hand budget and gate setup to qa-testing-performance.

## Navigation

- Profiling tools and measurement discipline: [references/perf-budgets-and-cwv.md](references/perf-budgets-and-cwv.md)
- Moved content pointer (CWV, k6, Lighthouse CI): [references/web-vitals-and-budgets.md](references/web-vitals-and-budgets.md)
- Source map: [data/sources.json](data/sources.json)

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
