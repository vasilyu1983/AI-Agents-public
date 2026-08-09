# Sampling Strategies

Sampling controls the fraction of traces (and associated spans) that are collected, stored, and queryable. A good sampling policy keeps costs and storage predictable without hiding the traces that matter most — errors, slow paths, and production incidents.

## Table of Contents

- [Head sampling](#head-sampling)
- [Tail sampling](#tail-sampling)
- [OTel Collector tail-sampling processor](#otel-collector-tail-sampling-processor)
- [Sampling bias — known trap](#sampling-bias--known-trap)
- [Exemplars: wiring sampled traces to Prometheus metrics](#exemplars-wiring-sampled-traces-to-prometheus-metrics)

## Head sampling

Head sampling makes a keep/drop decision at the root span, before any child spans are created. The decision propagates via the `traceflags` bit in W3C `traceparent`, so every downstream service respects the same decision and the trace is either complete or absent.

**When to use:** Low-volume services, development, staging, and any situation where operational simplicity outweighs the cost of keeping all traces. A parent-based ratio sampler (e.g. keep 10% of roots, always propagate the sampling decision downstream) is the lowest-complexity production option.

**Trade-off:** Head sampling is blind to outcome. A 1%-sampled request that later errors is dropped with 99% probability. For low-traffic services this probability is acceptable; for high-traffic services it hides rare failures.

OpenTelemetry SDK configuration (environment variable):

```bash
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1   # keep 10%
```

## Tail sampling

Tail sampling makes the keep/drop decision after all spans in a trace have been collected, allowing the decision to be based on the actual outcome: was there an error? was the request slow? did it touch a high-value path?

**When to use:** High-traffic services where head sampling would hide low-frequency failures. Tail sampling is more complex to operate because the collector must buffer spans long enough to see the full trace before deciding.

**Trade-off:** Requires stateful buffering in the collector. All spans for the same trace must be routed to the same collector instance (use load-balancing exporter for multi-instance collectors). Adds memory and latency overhead to the pipeline.

## OTel Collector tail-sampling processor

The OpenTelemetry Collector `tailsampling` processor implements tail sampling without changes to application code. Configure it in the collector pipeline:

```yaml
processors:
  tail_sampling:
    decision_wait: 10s          # buffer window to collect all spans
    num_traces: 50000           # max traces held in memory
    expected_new_traces_per_sec: 10
    policies:
      - name: errors-policy
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow-traces-policy
        type: latency
        latency: { threshold_ms: 500 }
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling]
      exporters: [otlp/backend]
```

Key policy types: `status_code`, `latency`, `probabilistic`, `rate_limiting`, `string_attribute`, `composite`. Combine policies in a `composite` policy with `and_sub_policy` / `or_sub_policy` for fine-grained control.

Reference: [opentelemetry.io/docs/collector/](https://opentelemetry.io/docs/collector/) and the `tailsampling` processor source in [github.com/open-telemetry/opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor).

## Sampling bias — known trap

Any sampling strategy that drops requests non-uniformly introduces bias into metric calculations derived from traces.

**Common forms:**

- **Survivor bias from head sampling:** Error rates computed from sampled traces undercount errors when errors are rarer than the sampling ratio. A 1% sampler on a service with a 0.01% error rate will drop most errors.
- **Cardinality-driven bias:** If sampling rules key on an attribute such as `user.tier`, premium-tier traces may be fully retained while free-tier traces are aggressively sampled, making error rates across tiers incomparable.
- **Warm/cold bias:** Services sampled by probabilistic ratio produce uneven coverage when traffic spikes — a sudden burst keeps fewer traces in absolute terms even at a constant ratio.
- **Cascade bias:** When a downstream service applies its own head sampling independently of the upstream decision, traces appear truncated and the sampling rate in the stored trace is a product of multiple independent decisions, not the intended single policy.

**Mitigations:**

- Use parent-based sampling so the upstream decision is respected downstream (no independent re-sampling).
- Derive error rates and latency percentiles from metrics (Prometheus counters and histograms), not from trace data. Metrics are not sampled; traces are.
- Use tail sampling to ensure errors and slow traces are always retained regardless of volume.
- Document and version the sampling policy so engineers know what the expected blind spots are.

## Exemplars: wiring sampled traces to Prometheus metrics

Exemplars are sample data points attached to Prometheus histogram and counter observations. Each exemplar carries a trace ID (and optionally a span ID), linking a specific metric observation to the trace that produced it.

**Why this matters:** Metrics give you aggregated truth; traces give you causal detail. Exemplars bridge the gap: from a latency spike on a Prometheus histogram, a single click navigates to the sampled trace that best represents that spike.

**Requirements:**

- Prometheus must be configured to scrape and store exemplars (enabled by default in Prometheus 2.27+; set `--enable-feature=exemplar-storage`).
- The OpenTelemetry SDK must be configured to emit exemplars. For the metrics SDK, set the exemplar filter:
  ```bash
  OTEL_METRICS_EXEMPLAR_FILTER=TRACE_BASED   # only attach when a sampled trace is active
  ```
- The application must have an active sampled span when the metric observation is recorded. Exemplars are only attached when the current trace is sampled.
- Grafana reads exemplars from Prometheus natively; enable the exemplar toggle on histogram panels.

**Sampling interaction:** `TRACE_BASED` exemplar filter only attaches a trace ID when the current span is sampled. If head sampling drops 99% of traces, 99% of metric observations carry no exemplar. For high-traffic services, consider always-sampling a small trace-exemplar path (e.g. use a sampler that keeps traces sampled solely for exemplar purposes but does not export the full span data).

**PromQL exemplar query example:**

```promql
# Show p99 latency with exemplars enabled in Grafana
histogram_quantile(0.99, rate(http_server_request_duration_seconds_bucket[5m]))
```

Navigate from the histogram panel to the trace: select any exemplar point on the panel to open the linked trace in Tempo or Jaeger.

Reference: [prometheus.io/docs/practices/exemplars](https://prometheus.io/docs/practices/exemplars/) and [opentelemetry.io/docs/specs/otel/metrics/sdk/#exemplar](https://opentelemetry.io/docs/specs/otel/metrics/sdk/#exemplar).
