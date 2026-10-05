# Core Observability Patterns

Detailed implementation patterns for building observable systems with current OpenTelemetry, structured logging, SLO-driven alerting, and performance evidence.

## Table of Contents

- [Pattern: Minimum production baseline](#pattern-minimum-production-baseline)
- [Pattern: Service instrumentation strategy](#pattern-service-instrumentation-strategy)
- [Pattern: Golden signals to SLIs](#pattern-golden-signals-to-slis)
- [Pattern: Release gates with error budgets](#pattern-release-gates-with-error-budgets)
- [Pattern: Correlated logging](#pattern-correlated-logging)
- [Pattern: Performance evidence](#pattern-performance-evidence)
- [Pattern: QA evidence pack](#pattern-qa-evidence-pack)

## Pattern: Message Consumer Observability

**Use when:** Operating Kafka consumers, retry/DLQ topologies, or any durable message processing pipeline.

At minimum, emit and alert on these signals:

| Signal | Why |
|--------|-----|
| Source consumer lag | Detect processing stalls before users notice |
| Retry topic lag by tier | Identify which backoff tier is accumulating |
| DLQ ingress rate | Terminal failures should be rare — alert immediately |
| Oldest message age in retry topics | Detect stuck retries that never resolve |
| Failed publish to retry or DLQ | Failure-routing failures are silent killers |
| Rebalance count | Frequent rebalances signal instability |
| Offset commit latency | Slow commits cause processing delays |
| Downstream HTTP latency and error rate by status code | Map consumer health to dependency health |
| Circuit breaker open state duration | Quantify downstream outage impact |
| Replay success rate | Confirm operator remediation is working |

Tracing requirements:
- Propagate a trace ID from source record to HTTP call and to retry/DLQ record.
- Correlate logs, traces, and replay actions with the same identifier.
- Include consumer group, topic, partition, and offset in structured log context.

---

## Pattern: Minimum production baseline

Every service should have:
- `service.name`, version, and environment metadata
- request-scoped structured logs
- distributed traces for critical user journeys
- golden metrics: latency, traffic, errors, saturation
- one path from failed test to trace and correlated logs

Recommended architecture:

```text
Application
  -> OpenTelemetry SDK / auto-instrumentation
  -> OpenTelemetry Collector
  -> Backend(s): traces, metrics, logs, profiles
```

Why Collector-first:
- decouples application code from vendor choice
- centralizes parsing, filtering, and routing
- reduces app-side configuration drift

## Pattern: Service instrumentation strategy

Use auto-instrumentation for:
- HTTP servers and clients
- database drivers
- messaging frameworks
- RPC frameworks

Add manual spans for:
- checkout, onboarding, order fulfillment, billing, etc.
- batch jobs and queue consumers
- orchestration steps spanning multiple dependencies

Avoid:
- duplicating server-route spans
- adding protocol attributes to non-protocol spans
- manually parsing `traceparent` when the SDK already tracks active context

## Pattern: Golden signals to SLIs

Baseline mapping:

| Signal | Example SLI | Typical source |
|--------|-------------|----------------|
| Latency | Good events under threshold | Histogram |
| Traffic | Requests or jobs processed | Counter |
| Errors | Failed requests or failed jobs | Counter or ratio |
| Saturation | Queue depth, thread pool usage, CPU contention | Gauge or derived metric |

Guidance:
- use histograms for latency SLIs
- use ratios for availability and correctness
- keep label sets small enough to aggregate across fleets

## Pattern: Release gates with error budgets

Release gates should ask:
- Is the service currently inside SLO?
- Is burn rate elevated over short and long windows?
- Did the change materially regress latency, errors, or saturation for a critical journey?

Preferred rule:
- use multi-window burn-rate alerts for paging
- use slower budget-consumption checks for release gating and change review
- for low-traffic services, adjust windows or use event-count thresholds to avoid noisy ratios

## Pattern: Correlated logging

Every request-scoped log should include:
- `service`
- `environment`
- `request_id`
- `trace_id`
- `span_id`
- business identifiers that are safe to log

Do not:
- put unique IDs into metrics labels
- use unique IDs as Loki or Elasticsearch high-cardinality labels
- log secrets, tokens, or raw PII

## Pattern: Performance evidence

Order of operations:
1. Confirm traces and metrics are trustworthy.
2. Add continuous profiling for CPU and memory evidence.
3. Run load tests against explicit performance budgets.
4. Compare against a known baseline, not just an absolute threshold.

Use profiles for:
- CPU hotspots
- memory growth or leaks
- lock contention
- request path regressions hidden by averages

## Pattern: QA evidence pack

For each failed integration or E2E run, capture:
- trace link or trace ID
- last relevant logs
- key latency and error metrics
- environment, build, and release metadata

This is the minimum diagnosability bar for observability used as QA infrastructure.
