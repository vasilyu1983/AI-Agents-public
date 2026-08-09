# eBPF and APM Tools

Stubs for tools that extend or complement the OpenTelemetry-first stack: eBPF-based zero-code instrumentation and open-source or commercial APM backends.

## Beyla (Grafana eBPF auto-instrumentation)

Beyla is an open-source eBPF-based application auto-instrumentation agent from Grafana Labs; it is also available as Grafana's distribution of the upstream `opentelemetry-ebpf-instrumentation` (OBI) project, which Grafana donated to the CNCF OpenTelemetry organisation. Beyla instruments HTTP/HTTPS, HTTP/2, and gRPC traffic at the kernel level by attaching eBPF probes to user-space functions, requiring no code changes and no language-specific SDK. Beyla emits OpenTelemetry traces and Prometheus metrics directly, making it a drop-in complement for services where adding an OTel SDK is blocked by policy or impractical (legacy binaries, third-party processes). Kernel 5.8+ is required; support covers Go, Python, Node.js, Java, Ruby, Rust, C/C++, and .NET runtimes.

Beyla's own versioning has moved well past the 2.x line since the OBI donation (a mid-2026 check found Beyla at v3.27.0, released July 2026, with 3.x releases shipping roughly weekly) — treat any specific minor version cited here as stale by the time you read it and check `github.com/grafana/beyla/releases` or `github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases` for the current version and changelog before quoting feature availability. As of 2026, Beyla/OBI is considered production-ready for Linux/x86-64 and ARM64 environments; Beyla's own repo now vendors most of its code from the upstream OBI project rather than developing independently — check whether a given feature question is best answered from the Beyla docs or the upstream OBI docs.

Reference: [grafana.com/oss/beyla-ebpf](https://grafana.com/oss/beyla-ebpf/) and [github.com/open-telemetry/opentelemetry-ebpf-instrumentation](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation)

## Pixie (eBPF observability, CNCF)

Pixie is a CNCF sandbox project from New Relic that provides instant, no-instrumentation observability for Kubernetes workloads using eBPF. It captures full request/response bodies, latency, error rates, CPU profiles, and network flows at the kernel level without any pod restarts or code changes. Pixie runs in-cluster, streams data to its in-memory data store, and exposes a scripting interface (PxL — Pixie Language) for ad-hoc query and visualization. It is most useful for rapid incident diagnosis when instrumented telemetry is absent or incomplete, and for capturing exact HTTP/gRPC/SQL payloads during debugging sessions. Data retention is short by design; for long-term storage, export to an OTLP-compatible backend via the OTel plugin.

Reference: [github.com/pixie-io/pixie](https://github.com/pixie-io/pixie)

## Honeycomb (high-cardinality wide events)

Honeycomb is a cloud observability platform built around wide events — single, richly attributed log-like records (up to thousands of fields) representing one unit of work such as a request or job execution. Unlike metric-first backends, Honeycomb stores and indexes every field so engineers can `GROUP BY` arbitrary high-cardinality dimensions (user ID, org ID, feature flag value, AB test variant) at query time without pre-aggregation or pre-indexing. This makes it well suited to debugging problems that only affect a specific subset of users or requests, and for product-engineering teams that need to answer "who is affected?" as quickly as "what is broken?". Honeycomb accepts OTel traces natively via OTLP and surfaces BubbleUp for automatic correlation discovery.

2026 additions: Honeycomb Metrics reached GA (March 2026), adding a dedicated metrics store alongside event storage. Canvas (the AI collaborative workspace) was rebuilt as an autonomous investigation agent that accepts plain-English queries and produces visual system snapshots. Agent Timeline and Canvas Skills were added for observing AI agent runs without proprietary SDKs. MCP integrations expanded across major AI development tools.

Reference: [honeycomb.io](https://www.honeycomb.io/)

## SigNoz (open-source OTel-native APM, ClickHouse backend)

SigNoz is an open-source full-stack APM and observability platform with a ClickHouse columnar storage backend. It provides traces, metrics, and logs in a single UI, is natively OpenTelemetry-compatible (OTLP ingestion), and is designed as a self-hosted alternative to Datadog or New Relic. The ClickHouse backend gives it high ingestion throughput and efficient aggregation for high-cardinality trace data. SigNoz ships with pre-built dashboards, alert rules, and correlation views that link metrics, traces, and logs. It is a strong choice for teams that want a unified OSS observability stack without the operational overhead of assembling Prometheus + Tempo + Loki separately.

Reference: [signoz.io](https://signoz.io/)

## Coroot (open-source ClickHouse-backed APM with eBPF)

Coroot is an open-source APM platform that combines eBPF-based zero-instrumentation collection with ClickHouse storage and an automated service-topology map. It detects service dependencies, latency, error rates, and resource saturation automatically from network-layer eBPF data, and enriches the picture with OTel traces and Prometheus metrics when available. Coroot's differentiating feature is its automated "health inspection" engine: it applies a set of opinionated checks to the collected data and surfaces actionable findings (e.g. "this service has p99 latency above SLO and the root cause is database saturation"). It is suitable for teams starting an observability program who need fast time-to-insight without extensive manual dashboard and alert authoring.

Reference: [coroot.com](https://coroot.com/)

## LLM and AI agent observability (2026)

Instrumenting LLM calls and multi-step agent workflows requires the same three-signal discipline (traces, metrics, logs) as service observability, plus two additional concerns: eval integration and cost attribution.

**Recommended approach:**

1. Emit OTel GenAI semconv spans for every LLM call. Use `gen_ai.client` spans for model calls and `gen_ai.agent` spans for agent invocations — their exact stability tier is unverified as of 2026-07-11 (see `references/opentelemetry-best-practices.md#genai-semantic-conventions` for why sources conflict). Prefer OTel-native SDKs over vendor proprietary agents where the platform supports them.
2. Track token usage via the `gen_ai.client.token.usage` metric per operation and provider. Use the same SLO burn-rate tooling for cost regressions as for HTTP error rates — a sudden jump in `gen_ai.usage.input_tokens` is a cost incident.
3. Wire eval scores as `gen_ai.evaluation.result` log events attached to the trace of the run being evaluated. This makes eval-in-CI auditable without a separate evaluation store.
4. Redact `gen_ai.input.messages` and `gen_ai.output.messages` by default. Capture them only when explicitly opted in and PII risk is accepted.

**Tool options (instrument-agnostic):**

| Need | Tool |
|------|------|
| OTel-native backend with GenAI semconv support | SigNoz, Grafana, Datadog (v1.37+ GenAI conventions) |
| High-cardinality query across model/org/user dimensions | Honeycomb (with Agent Timeline for agent runs) |
| Cost across 300+ model providers | Helicone |
| Eval scoring integrated with traces | LangSmith, Braintrust |

See `references/opentelemetry-best-practices.md#genai-semantic-conventions` for full checklist.
