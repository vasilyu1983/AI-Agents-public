# Performance Profiling Guide

Profiling as a diagnosis method (CPU and heap profilers per runtime, database `EXPLAIN`, N+1 and other bottleneck patterns) now lives in [`software-performance`](../../software-performance/SKILL.md). Load, stress and soak tests, performance budgets, Lighthouse and Core Web Vitals CI gates live in [`qa-testing-performance`](../../qa-testing-performance/SKILL.md). This file keeps only the parts where profiles are **telemetry**.

## Continuous profiling as a fourth signal

- **Production default today:** Grafana Pyroscope or Parca. Run always-on, low-overhead sampling profilers and keep profiles with the same `service.name`, version and environment labels as metrics and traces, so a regression can be compared release to release.
- **OTel Profiles:** pre-stable, with `opentelemetry-ebpf-profiler` as the reference implementation running as a Collector receiver. Not for critical production use until it is stable; check the per-language status on [opentelemetry.io/docs/languages](https://opentelemetry.io/docs/languages/) and do not plan around an unannounced GA date.
- **Correlation:** profiles become useful for debugging when they can be linked to traces by `trace_id`/`span_id` (span profiles) or at least by service, time window and version. Confirm that your profiler and backend support that link before promising "click from slow span to flame graph".

## Exemplars: metric to trace to profile

The path from an SLO alert to code is: burn-rate alert, then latency histogram with **exemplars**, then the exemplar's trace, then the profile for that span or time window.

- Prometheus stores exemplars only with `--enable-feature=exemplar-storage`; OTel SDKs attach them by default only when a sampled span is active (`OTEL_METRICS_EXEMPLAR_FILTER=trace_based`). Details and the sampling interaction are in [sampling-strategies.md](sampling-strategies.md#exemplars-wiring-sampled-traces-to-prometheus-metrics).
- Verify the path end to end with one known slow request: exemplar present on the histogram, trace retrievable, profile present for the same service and window.

## Frontend field data

For real-user monitoring, collect Core Web Vitals with the `web-vitals` library's `onLCP`, `onINP` and `onCLS` callbacks (plus `onFCP` and `onTTFB` if needed) and send them as telemetry tagged with release version. FID was replaced by INP and is no longer exported by current `web-vitals` releases ([README](https://github.com/GoogleChrome/web-vitals)). Thresholds and budgets are owned by [frontend-performance.md](../../qa-testing-performance/references/frontend-performance.md).

## Related

- [queueing-theory-applied.md](queueing-theory-applied.md): saturation signals that explain latency
- [slo-design-guide.md](slo-design-guide.md): latency SLIs as ratios
