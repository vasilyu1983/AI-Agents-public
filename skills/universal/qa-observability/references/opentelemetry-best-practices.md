# OpenTelemetry Best Practices

Operational guidance for building OpenTelemetry-based observability today.

## Table of Contents

- [defaults](#defaults)
- [Language-specific guidance](#language-specific-guidance)
- [Auto-instrumentation vs manual spans](#auto-instrumentation-vs-manual-spans)
- [Semantic conventions](#semantic-conventions)
- [GenAI semantic conventions](#genai-semantic-conventions)
- [Sampling](#sampling)
- [Context propagation](#context-propagation)
- [Metrics, logs, and profiles](#metrics-logs-and-profiles)
- [Testing instrumentation](#testing-instrumentation)
- [Common mistakes](#common-mistakes)
- [Source of truth](#source-of-truth)

## defaults

- Prefer `application -> OpenTelemetry Collector -> backend`.
- Use OTLP over HTTP unless your environment requires gRPC.
- Use auto-instrumentation for frameworks and libraries first.
- Add manual spans only for business workflow boundaries, async jobs, and queue consumers.
- Treat logs and profiles as implementation-specific signals. Verify support in the language runtime and backend before standardizing on them.

## Language-specific guidance

- Node.js: use `NodeSDK`, exporter defaults, and active-span patterns such as `startActiveSpan`.
- Python: use framework instrumentors plus `TracerProvider`, `BatchSpanProcessor`, and `PeriodicExportingMetricReader`.
- For both: keep `OTEL_EXPORTER_OTLP_ENDPOINT` as the base endpoint and only use signal-specific endpoint overrides when signals route differently.

See:
- `assets/opentelemetry/nodejs/opentelemetry-nodejs-setup.md`
- `assets/opentelemetry/python/opentelemetry-python-setup.md`

## Auto-instrumentation vs manual spans

Use auto-instrumentation for:
- HTTP servers and clients
- DB drivers and ORMs
- Messaging libraries
- gRPC frameworks

Add manual spans for:
- Order processing, checkout, onboarding, and similar business workflows
- Fan-out and fan-in orchestration
- Queue consumers and batch jobs
- External integrations not covered by auto-instrumentation

Avoid:
- Wrapping every route handler in a manual span when server auto-instrumentation already creates one
- Adding protocol attributes to spans that model business work instead of protocol operations
- Creating spans for trivial helper functions

## Semantic conventions

- Use current stable semantic conventions for protocol-level spans.
- Prefer canonical names such as `http.request.method` and `http.response.status_code` over older aliases.
- Keep business context in your own namespace such as `order.id`, `checkout.step`, or `feature.flag.key`.

Guideline:
- Protocol metadata belongs on protocol spans.
- Business metadata belongs on business spans.
- Sensitive values should be redacted or avoided entirely.

## GenAI semantic conventions

**Status: not stable — check before building on it.** The GenAI conventions moved to the dedicated repo [github.com/open-telemetry/semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai); read the stability marker at the top of each spans, agent-spans and metrics document before depending on a name. Names change between revisions. For example, on the repo's main branch token usage is split into `gen_ai.client.inference.usage.input_tokens` / `.output_tokens` (plus cache and reasoning variants), where older releases used a single `gen_ai.client.token.usage` histogram. Pin the semconv version your instrumentation library implements and read its CHANGELOG before building dashboards or CI gates on attribute names. Existing instrumentations keep older names by default; `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` opts into the newest revision.

To pin to a known-good version while the spec matures, use the opt-in env var:

```bash
# Switch to latest experimental GenAI semconv (breaks on next revision — pin carefully)
OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental
```

### Why emit GenAI semconv instead of bespoke attributes

- Portable signals: backends (Honeycomb, SigNoz, Grafana, Jaeger) can recognise and visualize standardised attribute names without per-team dashboards.
- Regression testing: standardised token-usage metrics (`gen_ai.client.token.usage`) and duration metrics (`gen_ai.client.operation.duration`) make cost/latency regressions detectable with the same SLO tooling used for HTTP services.
- Trace-based testing of agent runs: a single trace can span LLM call → tool execution → second LLM call using span kinds `CLIENT` (inference, retrieval) and `INTERNAL` (tool execution), making failures in multi-step agent flows attributable to a specific hop.
- Eval integration: the `gen_ai.evaluation.result` event (illustrative — subject to change) is designed to carry eval scores alongside the trace that generated the output, enabling eval-in-CI without a separate evaluation store.

### Spans

Model-call spans use span kind `CLIENT`. Agent operation spans (invoke_agent, invoke_workflow) use span kind `INTERNAL` for tool execution.

Illustrative required/recommended attributes (verify against primary docs — these change between spec revisions):

| Attribute | Type | Notes |
|---|---|---|
| `gen_ai.operation.name` | string | e.g. `chat`, `embeddings`, `execute_tool`, `invoke_agent` |
| `gen_ai.provider.name` | string | e.g. `openai`, `anthropic`, `aws.bedrock` |
| `gen_ai.request.model` | string | Model requested |
| `gen_ai.response.model` | string | Model that actually responded |
| `gen_ai.usage.input_tokens` | int | Prompt token count |
| `gen_ai.usage.output_tokens` | int | Completion token count |
| `gen_ai.response.finish_reasons` | string[] | e.g. `stop`, `length`, `tool_calls` |
| `gen_ai.tool.name` | string | Required on tool-execution spans |

Do not log `gen_ai.input.messages` or `gen_ai.output.messages` in production without explicit PII review — these carry the full prompt and completion text.

### Metrics

Illustrative metric names (verify against primary docs):

| Metric | What it measures |
|---|---|
| `gen_ai.client.token.usage` | Input + output token counts per operation |
| `gen_ai.client.operation.duration` | End-to-end latency of the LLM call |
| `gen_ai.client.operation.time_to_first_chunk` | Streaming time-to-first-token |
| `gen_ai.server.request.duration` | Server-side request latency (when instrumenting a hosted model endpoint) |

All metrics carry `gen_ai.operation.name` and `gen_ai.provider.name` as required dimensions.

### Events

Two events are defined (illustrative — verify before use):

- `gen_ai.client.inference.operation.details` — carries chat history, parameters, and token counts alongside the trace.
- `gen_ai.evaluation.result` — carries eval metric name, score, label, and explanation; attach to the trace of the run being evaluated.

### QA checklist additions for AI features

- Every LLM call in an integration or E2E test produces one `CLIENT` span with `gen_ai.operation.name`, `gen_ai.provider.name`, and token-usage attributes.
- Multi-step agent runs produce a connected trace: one span per LLM call, one `INTERNAL` span per tool execution, all sharing the same `trace_id`.
- Token-usage metrics are emitted per operation; cost regressions can be caught by the same SLO burn-rate alerts used for HTTP error rates.
- Eval scores are attached as `gen_ai.evaluation.result` events on the trace of the run under test, making eval-in-CI auditable without a separate evaluation store.
- `gen_ai.input.messages` and `gen_ai.output.messages` are redacted or omitted unless a deliberate decision to capture them has been made and PII risk accepted.

### Source of truth

Always check before shipping:
- Spans: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md
- Agent spans: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md
- Metrics: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md and gen-ai-token-metrics.md
- Events: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-events.md

## Sampling

Recommended baseline:
- Dev and local: `100%`
- Staging: `100%` for critical test journeys, lower elsewhere if volume is high
- Production: parent-based ratio sampling for normal traffic, with explicit retention of errors and high-value slow paths

Rules of thumb:
- Keep sampling policy stable enough that engineers can reason about missing traces.
- Always confirm that tail-based or backend-side sampling preserves the traces you page on.
- Pair sampling changes with retention and cost review.

## Context propagation

Require end-to-end propagation for:
- HTTP headers via `traceparent`
- gRPC metadata
- Message headers on Kafka, RabbitMQ, SQS, or equivalent

QA checks:
- A request that crosses two or more services produces one trace ID end-to-end.
- A failed E2E test captures a trace link or trace ID in its artifacts.
- Logs include `trace_id` and `span_id` from the current active span.

## Metrics, logs, and profiles

Metrics:
- Use latency histograms for SLI math.
- Prometheus native histograms are opt-in at scrape time; how you enable them (feature flag vs `scrape_native_histograms` config) depends on your Prometheus version, so check its release notes and configuration docs. They eliminate the bucket-preselection problem and reduce cardinality. Treat rollout as an infrastructure change: test all dashboards and alert rules against native histogram queries before enabling per job in production. Check whether your client library supports native-histogram exposition before planning the rollout.
- Add exemplars where your stack supports them.
- Treat label cardinality as a design constraint, not an optimization pass.

Logs:
- Keep `trace_id` and `request_id` in structured JSON.
- Do not turn unique IDs into labels or dimensions.
- Use collector-side parsing, filtering, and routing wherever possible.
- OTel Logs SDK maturity differs by language; check the per-language status table at [opentelemetry.io/docs/languages](https://opentelemetry.io/docs/languages/) before adopting it. For languages where the Logs SDK is not stable, use stdout/stderr JSON + Collector filelog receiver as the safe default.
- Span events (`Span.AddEvent`, `Span.RecordException`) are being deprecated in favour of log-based events emitted via the Logs API ([OTel blog](https://opentelemetry.io/blog/2026/deprecating-span-events/)). New instrumentation should use the Logs API for events. Existing span event data and visualizations remain functional during the gradual transition.

Profiles:
- The OTel Profiles signal is not yet stable; check its current status on opentelemetry.io. The reference implementation is `opentelemetry-ebpf-profiler` (donated by Elastic), which operates as an OTel Collector receiver with whole-system Linux eBPF profiling. Do not use it for critical production workloads while it is pre-stable.
- Profiles can be correlated with traces via `trace_id` and `span_id` — link flame graphs directly to the spans that generated the work.
- For production continuous profiling today: use Grafana Pyroscope or Parca (both stable) and plan migration to OTel Profiles once it is stable in your language and backend.

## Testing instrumentation

Minimum validation for a new service:
- Service metadata is present: `service.name`, version, environment
- One inbound request produces one server trace
- One outbound dependency call appears as a child span
- Errors record exceptions and non-OK span status
- Logs for the same request contain the corresponding trace ID
- Golden metrics exist for latency, traffic, errors, and saturation

## Common mistakes

- Using outdated semantic-convention attribute names copied from old blog posts
- Setting `OTEL_EXPORTER_OTLP_ENDPOINT` to a signal path and then also overriding signal-specific exporters
- Duplicating auto-created HTTP spans with manual route spans
- Logging secrets or raw tokens in span attributes
- Exploding label cardinality with user IDs, order IDs, or request IDs

## Source of truth

Check current primary docs before finalizing advice:
- `data/sources.json`
