# OpenAI Codex OTel Config

## Table of Contents

- [When To Use](#when-to-use)
- [Look Up the Current Schema](#look-up-the-current-schema)
- [Two Telemetry Pipelines](#two-telemetry-pipelines)
- [Design Rules](#design-rules)
- [Anti-Patterns](#anti-patterns)

## When To Use

Use this reference when wiring OpenTelemetry (OTel) instrumentation into a Codex-class coding-agent runtime, or when deciding whether a signal belongs in standards-based OTel telemetry or in the runtime's proprietary analytics events.

## Look Up the Current Schema

The `[otel]` config keys, exporter variants, and analytics event names change between Codex releases, so this file does not copy them. Before writing config or dashboards:

1. Read the Codex configuration reference for the release you run, and the `[otel]` example in its sample config.
2. If you need type names (settings struct, exporter enum, metrics client), read the `codex-rs/otel` crate at the tag you deploy, not `main`.
3. Record the release or tag you checked next to the config you ship.

Stable concepts to look for: an exporter choice (none, OTLP over HTTP or gRPC, with binary or JSON encoding), separate trace and metrics exporters, per-span resource attributes such as `service.name` and `environment`, and W3C `tracestate` members propagated alongside `traceparent`.

## Two Telemetry Pipelines

Codex ships two telemetry systems. Keep the boundary explicit.

| Dimension | OTel (`codex-rs/otel`) | Analytics (`codex-rs/analytics`) |
|-----------|------------------------|----------------------------------|
| Standard | OpenTelemetry: W3C trace context, OTLP | Proprietary event schema |
| Export target | Any OTLP-compatible backend | The vendor's product-analytics pipeline |
| Unit | Spans, metrics, tracestate | Typed events and per-turn facts (token usage, resolved config) |
| Audience | Operators, platform teams, external observability tools | The vendor's product analytics |
| Contract | Yours: you choose retention and recipients | The vendor's: you cannot rely on its schema or retention |

## Design Rules

- Route any telemetry that must reach your own observability backend through the OTel config, not through analytics events.
- Propagate `traceparent` and `tracestate` explicitly across async queues and task spawns; in Tokio they do not survive spawning unless the span context is carried.
- Use the runtime's session telemetry helpers for propagation instead of hand-building headers.
- Treat analytics events as vendor-internal; do not build cross-org dashboards on them.
- Keep metric dimensions low-cardinality: service name, environment, and model slug are safe; raw prompt text, user IDs, and file paths are not.
- Test with an in-memory exporter; do not stand up a real OTLP endpoint in unit tests.

## Anti-Patterns

- Emitting raw user prompts, provider payloads, or file paths as span attributes. They are high-cardinality and may leak PII.
- Conflating the OTel pipeline with the analytics pipeline. They have different retention, privacy, and recipient contracts.
- Copying config keys from a `main`-branch read into production config without checking the release you run.
- Losing `tracestate` at task-spawn boundaries because the span context was not carried across.
