---
source_snapshot: openai/codex main branch (verified 2026-05-25)
anchors:
  - codex-rs/otel/ — OtelProvider, OtelSettings, SessionTelemetry, MetricsClient, OtelExporter
  - codex-rs/analytics/src/events.rs — TrackEventRequest, SkillInvocation, GuardianReviewAnalyticsResult
  - codex-rs/analytics/src/facts.rs — TurnTokenUsageFact, TurnResolvedConfigFact
---

# OpenAI Codex OTel Config

## Table of Contents

- [When To Use](#when-to-use)
- [What It Covers](#what-it-covers)
- [The `codex-rs/otel` Crate](#the-codex-rsotel-crate)
- [Contrast: OTel vs Analytics Proprietary Events](#contrast-otel-vs-analytics-proprietary-events)
- [Design Rules](#design-rules)
- [Anti-Patterns](#anti-patterns)

## When To Use

Use this reference when wiring OpenTelemetry (OTel) instrumentation into a Codex-class coding-agent runtime, or when contrasting standards-based OTel telemetry with proprietary analytics events.

## What It Covers

- `codex-rs/otel` crate: structs, TOML schema, exporter options, W3C tracestate handling
- Contrast with `codex-rs/analytics` proprietary event types
- TOML config skeleton

## The `codex-rs/otel` Crate

### Key Types

| Type | Role |
|------|------|
| `OtelProvider` | Top-level provider — wires exporters to the global OTel tracer and meter |
| `OtelSettings` | TOML-deserializable settings struct; controls all exporter and span config |
| `SessionTelemetry` | Session-scoped telemetry emission (trace IDs, turn events, W3C tracestate propagation) |
| `MetricsClient` | Abstraction over the OTel metrics API; emits counters and histograms |
| `MetricsConfig` | Configures the metrics pipeline within `OtelSettings` |
| `InMemoryMetricExporter` | Test double for metrics output; used in unit tests |

### `OtelSettings` Fields

```toml
[otel]
environment      = "production"           # deployment environment label
service_name     = "codex"               # OTLP service.name attribute
service_version  = "1.2.3"              # OTLP service.version attribute
codex_home       = "/home/user/.codex"  # base path for local log files
exporter         = "otlp-http"          # shorthand; overridden by trace_exporter/metrics_exporter

# Exporter selection (OtelExporter enum variants):
#   None          — no export; useful for development
#   OtlpHttp      — standard OTLP over HTTP (endpoint, headers, protocol, TLS)
#   Statsig       — shorthand for OTLP/HTTP JSON to Statsig (Codex-internal defaults)

[otel.trace_exporter]
# endpoint, headers, protocol = "binary" | "json", tls settings

[otel.metrics_exporter]
# same fields as trace_exporter

[otel.span_attributes]
custom_key = "custom_value"   # arbitrary k/v pairs added to every span

[otel.tracestate.my_vendor]
key   = "my_vendor"
value = "abc123"              # W3C tracestate member; propagated through async queues
```

### HTTP Protocol Options

`OtelHttpProtocol::Binary` — binary protobuf (default OTLP)
`OtelHttpProtocol::Json` — JSON-encoded OTLP (useful for human debugging or Statsig compatibility)

### W3C Tracestate Handling

`OtelSettings.tracestate` is a map of named members. Each member carries a `key:value` pair injected into the W3C `tracestate` header on outbound HTTP requests. This lets the runtime propagate vendor-specific trace metadata (e.g. Statsig experiment ID, internal request routing metadata) across async queue boundaries without polluting the standard `traceparent`.

Design rule: propagate `traceparent` and `tracestate` through async queues explicitly — they do not survive task-spawning automatically in Tokio unless carried in the span context.

## Contrast: OTel vs Analytics Proprietary Events

Codex ships two parallel telemetry systems. Understanding the boundary prevents mixing them.

| Dimension | `codex-rs/otel` | `codex-rs/analytics` |
|-----------|----------------|----------------------|
| Standard | OpenTelemetry (W3C trace context, OTLP) | Proprietary Codex event schema |
| Export target | Any OTLP-compatible backend (Jaeger, Datadog, Statsig) | Codex internal analytics pipeline |
| Primary types | Spans, metrics, tracestate | `TrackEventRequest` enum variants |
| Audience | Operators, platform teams, external observability tools | OpenAI product analytics |
| Config | `[otel]` TOML section | `analytics_client` / event dispatch in `codex-rs/core` |

### Analytics Proprietary Event Types (from `codex-rs/analytics/src/events.rs`)

Key variants of the `TrackEventRequest` enum:

- `SkillInvocation` — tracks each time a skill is rendered (via `SkillInvocationEventRequest`, includes `skill_id`, `skill_name`, thread/turn IDs, model)
- `GuardianReview` — captures guardian (safety) review outcomes (via `GuardianReviewAnalyticsResult`, includes `decision`, `terminal_status`, `failure_reason`, token usage, timing)
- `TurnEvent` — comprehensive per-turn metrics (`CodexTurnEventParams`: `total_tool_call_count`, `input_tokens`, `output_tokens`, tool-specific counters)
- `HookRun`, `CommandExecution`, `FileChange`, `McpToolCall`, `DynamicToolCall`, `WebSearch`, `Compaction`

### Analytics Fact Types (from `codex-rs/analytics/src/facts.rs`)

- `TurnTokenUsageFact` — `{ turn_id, thread_id, token_usage }` — captures token consumption per turn
- `TurnResolvedConfigFact` — per-turn resolved config snapshot including `approval_policy`, `sandbox_network_access`, `collaboration_mode`, and model metadata

## Design Rules

- Use the `[otel]` config section for any telemetry that must flow to an external observability backend.
- Do not re-implement `traceparent`/`tracestate` propagation by hand — use `SessionTelemetry`'s propagation helpers.
- Treat `TrackEventRequest` variants as internal analytics only; do not build cross-org dashboards on them.
- Keep OTel metric dimensions low-cardinality — `service_name`, `environment`, `model_slug` are safe; raw prompt text, user IDs, and file paths are not.
- The `InMemoryMetricExporter` is the correct test double for unit tests; do not spin up a real OTLP endpoint in tests.

## Anti-Patterns

- Emitting raw user prompts, provider payloads, or file paths as OTel span attributes — these become high-cardinality and may leak PII.
- Conflating the OTel trace pipeline with the analytics pipeline; they have different retention, privacy, and recipient contracts.
- Losing `tracestate` at Tokio task-spawn boundaries because the span context was not explicitly carried across.
