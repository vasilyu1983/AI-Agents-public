---
name: qa-testing-performance
description: "Designs performance and load testing: stress, spike, soak, capacity, CI budget gates. Use when planning load tests or perf gates; not code or SQL tuning."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# QA Testing (Performance)

This skill owns load-test design, CI performance gates and capacity validation. Route diagnosis of an observed hot path to [software-performance](../software-performance/SKILL.md).

Sources: [data/sources.json](data/sources.json).

## Workflow

1. Establish realistic baselines, traffic models, and budgets.
2. Choose the right performance test type and toolchain for the risk.
3. Run warm-up separately, then repeat the scenarios against representative environments with monitoring active; preserve raw results rather than selecting the best run.
4. Compare only runs whose workload, data volume, cache state, build, infrastructure allocation, generator capacity, network path, and telemetry query are known. Report a distribution or confidence interval so run noise is visible.
5. Analyze bottlenecks, then convert findings into budgets, profiles, and CI gates. Label evidence `synthetic`, `representative`, or `production-observed`; a budget checker validates supplied measurements, not environment parity or capacity beyond the tested concurrency, duration, and faults.

## Inputs to Gather

- SLOs/SLAs for latency, availability, throughput
- Critical user journeys and their expected traffic volumes
- Infrastructure topology (services, databases, caches, queues, CDN)
- Current performance baselines (if any)
- Traffic patterns: peak hours, seasonal spikes, growth projections
- Database query hotspots and slow query logs
- Frontend targets: Core Web Vitals (LCP, INP, CLS), bundle size limits
- Environment parity: how close is the test environment to production?

## Test Types

| Type | Purpose | When to Run |
|------|---------|-------------|
| Load | Validate behavior under expected traffic | Pre-release, nightly |
| Stress | Find the breaking point beyond expected capacity | Pre-release, capacity planning |
| Soak / Endurance | Detect memory leaks, connection pool exhaustion, GC degradation over hours | Weekly, pre-release |
| Spike | Validate behavior under sudden traffic bursts | Pre-release, after autoscaling changes |
| Capacity | Find the ceiling — max throughput before SLO violation | Quarterly, before major launches |

## When NOT to Load Test

Load testing has a real cost (build time, environment risk, engineer attention). Skip or downscope it when:

- **No SLO exists yet and traffic is trivial.** An internal tool with 5 users and no growth path doesn't need a load-testing harness — define the SLO first, or skip until one exists.
- **Production telemetry already answers the question.** If RUM/APM already shows the system holding p95/p99 comfortably under real peak traffic, a synthetic load test adds little; spend the budget on a soak test only when telemetry leaves a leak or GC-drift hypothesis unresolved.
- **The bottleneck is already known and reproducible.** Don't stand up a load-testing campaign to "confirm" a bug you can already reproduce with a single request under a profiler. Profile, fix, then run one confirmation load test — not a full suite.
- **Pre-product-market-fit.** Traffic shape, critical journeys, and even the API surface are still changing weekly. A load test built now models a system that won't exist in a month; capacity arithmetic is a preliminary sanity check, not evidence of headroom or tail latency.
- **Third-party or partner APIs without an agreement to test.** Load testing a vendor's production endpoint without permission risks rate-limit bans or ToS violations. Use their sandbox/staging tier, or model the dependency's expected latency into your own capacity math instead of hitting it directly.
- **A one-off batch job with no user-facing latency SLO.** Throughput/capacity math (rows/sec needed vs. measured single-run rate) is usually sufficient; a full VU-ramp load test is overkill for a job that runs once a night with no concurrent users.

When in doubt, the cheapest sanity check is Little's Law arithmetic (see [references/capacity-planning.md](references/capacity-planning.md#littles-law-sizing-concurrency-from-rate-and-latency)) — if the back-of-envelope math shows huge headroom, a full load-testing campaign may not be worth the cost yet.

## Tool Selection

| Tool | Language | Strengths | Best For |
|------|----------|-----------|----------|
| k6 | JavaScript | Arrival-rate executors and threshold gates. Verify browser APIs, assertions, extensions and operator compatibility in the [installed-version docs](https://grafana.com/docs/k6/latest/) before choosing a pin. | API/browser load testing, CI gates |
| Locust | Python | Distributed, flexible, real Python scripts | Complex scenarios, Python teams |
| Artillery | YAML + JS | Declarative, good for APIs, scenario chaining | API load testing, quick setup |
| Gatling | Java/Kotlin/Scala/JS/TS | Strong reporting, enterprise support; JS/TS support (GraalVM) | JVM teams, enterprise |
| JMeter | Java/GUI | Widely adopted, protocol support | Legacy, protocol-heavy testing |
| Playwright | JavaScript | Real browser, network interception | Frontend performance, E2E perf |
| Lighthouse CI | JavaScript | Lab performance audits, accessibility, SEO | Frontend budgets, PR gates |

## SLO-Driven Test Design

Design the test from the SLO, not the other way around. Working backward from "let's load test and see what we get" produces budgets that are either too loose (numbers the system already hits) or arbitrary (nobody can say why 500ms and not 600ms).

1. **Start from the availability/latency SLO.** Example: 99.9% of requests must complete under 300ms, measured over a rolling 30-day window.
2. **Keep the error-budget denominator explicit.** For a request-based 99.9% latency SLO, at most 0.1% of eligible requests may breach its target over the chosen window. Minutes of downtime apply to a time-based availability SLI, not automatically to a request-based latency SLO ([SRE SLI definitions](https://sre.google/workbook/implementing-slos/)).
3. **Set the load test's arrival rate at expected peak, not average.** If peak is 500 rps, test at 500 rps (open-loop/arrival-rate — see [references/load-testing-patterns.md](references/load-testing-patterns.md#workload-model-open-vs-closed-loop)), not at a comfortable average that never stresses the tail.
4. **Choose CI margin from baseline variance and release risk.** A tighter CI threshold can warn before the production SLO is breached; a fixed percentage is a policy example, not a universal requirement. Preserve the production SLI denominator and percentile when translating the target.
5. **Goodput, not just percentiles, for SLO-gated systems.** Track the fraction of requests meeting the SLO at the tested concurrency (goodput) alongside p50/p95/p99 — a system can have a "fine" p99 while goodput is dropping because the failure mode is errors, not just slow responses. Whether percentiles include failed requests is tool-dependent — k6's `http_req_duration` includes failed requests by default, so fast failures can pull percentiles down and mask the real problem; verify your tool's convention before trusting a percentile alone.

## CI Integration Patterns

**Performance budgets** — define explicit thresholds:
- API latency: p95 < target, p99 < ceiling
- Throughput: requests/sec >= minimum under load
- Error rate: < threshold (example budget: 0.1-1%; set the actual number from your own SLA/error budget, not this range)
- Core Web Vitals: look up the [official good thresholds](https://web.dev/articles/vitals) before choosing field budgets. Assess field p75 separately from lab runs; CrUX uses its reporting window, while RUM windows are configured by the team
- Bundle size: < budget per entry point
- LLM endpoints: TTFT low enough for the target UX (example budget: <500ms for chat; set your own from UX research, not this figure), tokens/sec >= target, goodput >= SLO at peak concurrency

**When to run each tier:**
- PR gate (lightweight): Lighthouse CI, bundle size check, smoke load test (30s, low VUs)
- Nightly (full): Full load test suite, soak test (1-2 hours), baseline comparison
- Pre-release (capacity): Stress test, spike test, capacity test with production-like data

**Artifact collection:** test results JSON, flamegraphs, comparison reports, Grafana snapshots, Lighthouse HTML reports.

## Frontend, Backend, Profiling, and Capacity

Core Web Vitals (LCP/INP/CLS), Lighthouse CI budgets, bundle-size tracking, and synthetic-vs-RUM monitoring — see [references/frontend-performance.md](references/frontend-performance.md).

Connection-pool pressure and read-replica lag testing under load — see [references/database-performance-testing.md](references/database-performance-testing.md). Query-level diagnosis (EXPLAIN ANALYZE, index effectiveness, N+1 detection) is owned by [data-sql-optimization](../data-sql-optimization/SKILL.md).

How profiling connects to a load test (always profile under realistic concurrency, compare against a pre-change baseline) — see [references/profiling-optimization.md](references/profiling-optimization.md). Per-language profiler commands are owned by [software-performance](../software-performance/SKILL.md).

Sizing instances from stress-test results, cost modeling, and auto-scaling validation — see [references/capacity-planning.md](references/capacity-planning.md).

## Quick Reference

| Task | Approach | Key Metric |
|------|----------|------------|
| API latency regression | k6 with baseline comparison | p95 delta |
| Frontend speed regression | Lighthouse CI lab budget plus field RUM | Lab LCP/CLS/TBT; field LCP/INP/CLS |
| Memory leak detection | Soak test + heap snapshots | Heap growth over time |
| Capacity ceiling | Stress test with ramp-up | Max RPS before SLO breach |
| Database bottleneck | Query benchmark + connection pool test | Query p95, pool wait time |
| Bundle size regression | size-limit or bundlemon in CI | Bundle size delta |
| Auto-scaling validation | Spike test with monitoring | Scale-up latency, error rate during scale |
| LLM/AI API latency | Separate TTFT and generation throughput; test with realistic prompt distributions | TTFT p95, tokens/sec, goodput |
| Continuous profiling | Pyroscope (Grafana) for always-on production profiling | Regression detection at deploy time |

## Decision Tree

```text
Performance concern: [Symptom]
    │
    ├─ Slow API responses?
    │   ├─ Under normal load? → Profile backend (flamegraph + trace spans)
    │   └─ Only under load? → Load test → find bottleneck (CPU, DB, pool, GC)
    │
    ├─ Slow page load?
    │   ├─ Large bundle? → Bundle analysis + code splitting
    │   └─ Slow server response? → API profiling + caching
    │   └─ Layout shift? → CLS debugging (font, image, dynamic content)
    │
    ├─ Unknown capacity?
    │   └─ Stress test → find ceiling → capacity plan with headroom
    │
    ├─ Memory growth over time?
    │   └─ Soak test + heap snapshots at intervals → compare retained objects
    │
    ├─ Latency spikes under traffic bursts?
    │   └─ Spike test → check auto-scaling, connection pools, queue depth
    │
    ├─ LLM/AI endpoint?
    │   ├─ TTFT too high? → prefill optimization (prompt length, batching)
    │   ├─ Throughput degrading? → tokens/sec sweep + concurrency step test
    │   └─ Inconsistent under load? → warm vs cold cache scenario; mock for CI
    │
    └─ Need CI performance gate?
        ├─ API? → k6 thresholds in pipeline
        ├─ Frontend? → Lighthouse CI budgets
        └─ Bundle? → size-limit or bundlemon
```

## Resources

| Resource | Purpose |
|----------|---------|
| [references/load-testing-patterns.md](references/load-testing-patterns.md) | Load test design: scenarios, ramp-up, data, analysis; open/closed loop; LLM/AI API testing |
| [references/performance-budgets-ci.md](references/performance-budgets-ci.md) | CI performance gates and baseline management |
| [references/profiling-optimization.md](references/profiling-optimization.md) | Profiling under load, network latency decomposition, continuous profiling with Pyroscope; per-language profiler commands owned by software-performance |
| [references/frontend-performance.md](references/frontend-performance.md) | Core Web Vitals, Lighthouse CI, bundle tracking |
| [references/database-performance-testing.md](references/database-performance-testing.md) | Connection-pool pressure and replica-lag testing under load; query-level diagnosis owned by data-sql-optimization |
| [references/capacity-planning.md](references/capacity-planning.md) | Load results to infrastructure sizing |

### Data

| File | Purpose |
|------|---------|
| [data/sample-perf-results.json](data/sample-perf-results.json) | Synthetic B2B SaaS performance test results: budgets, measured values, and test scenarios |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-performance-test-plan.md](assets/template-performance-test-plan.md) | Performance test scope, scenarios, and acceptance criteria |
| [assets/template-k6-load-test.js](assets/template-k6-load-test.js) | Starter k6 script with stages, thresholds, and custom metrics |
| [assets/template-performance-budget.md](assets/template-performance-budget.md) | Budget definition for latency, throughput, and Core Web Vitals |

## Scripts

Stdlib-only Python CLI — no external dependencies, runs with Python 3.10+.

| Script | Purpose |
|--------|---------|
| [scripts/perf_budget_checker.py](scripts/perf_budget_checker.py) | Budget validation, CI tier planning, and full Markdown report generation |
| [scripts/test_perf_budget_checker.py](scripts/test_perf_budget_checker.py) | Offline regressions (pytest and Node.js required); run `python3 -m pytest scripts/test_perf_budget_checker.py -q` |

Run from the `qa-testing-performance/` directory:

```bash
# Budget check — PASS/WARN/FAIL per metric, overall CI gate verdict
python scripts/perf_budget_checker.py check --input data/sample-perf-results.json

# CI test tier assignment (PR_gate / nightly / pre_release) for all scenarios
python scripts/perf_budget_checker.py plan --input data/sample-perf-results.json

# Full Markdown performance test report to stdout
python scripts/perf_budget_checker.py report --input data/sample-perf-results.json

# Write report to file
python scripts/perf_budget_checker.py report \
  --input data/sample-perf-results.json \
  --output report.md
```

The `check` and `report` subcommands exit `1` on FAIL, `0` on PASS or advisory WARN, and `2` on invalid input. A nonempty budget and every budgeted measurement are required; `plan` also requires at least one valid scenario. WARN zones are local heuristics that permit small breaches; use explicit k6/LHCI error thresholds for a strict gate. See [scripts/README.md](scripts/README.md) for full format details and threshold reference.

## Navigation

- `## Workflow` and `## Decision Tree` for the baseline sequence and test-type selection
- `## When NOT to Load Test` before committing to a full test campaign
- `## Resources`, `## Templates`, and `## Scripts` for deeper materials and automation
- `## Related Skills` for observability, resilience, and diagnosis handoffs

## Related Skills

| Skill | Purpose |
|-------|---------|
| [qa-observability](../qa-observability/SKILL.md) | Metrics, tracing, and performance monitoring |
| [qa-resilience](../qa-resilience/SKILL.md) | Failure mode testing under load |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Risk-based test strategy |
| [qa-debugging](../qa-debugging/SKILL.md) | Performance debugging and profiling |
| [software-performance](../software-performance/SKILL.md) | Diagnosing an observed regression: profiling, misdiagnoses, tail-latency math, neutral-is-a-revert |
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | CI/CD and infrastructure |
| [software-backend](../software-backend/SKILL.md) | Backend API optimization |
| [data-sql-optimization](../data-sql-optimization/SKILL.md) | Database query tuning |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
