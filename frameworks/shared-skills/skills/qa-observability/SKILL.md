---
name: qa-observability
description: "Implement and validate observability for quality engineering: OpenTelemetry logs/metrics/traces, W3C trace context propagation, SLI/SLO + error-budget release gates, burn-rate alerting, trace-based debugging for test failures, sampling/cardinality/cost controls, profiling (CPU/memory/continuous), synthetic/RUM signals, and APM stack integrations (Prometheus/Grafana/Jaeger/Tempo/Loki/Datadog/New Relic)."
---

# QA Observability and Performance Engineering

Use telemetry (logs, metrics, traces, profiles) as a QA signal and a debugging substrate.

Core references:
- OpenTelemetry: https://opentelemetry.io/docs/
- W3C Trace Context: https://www.w3.org/TR/trace-context/
- Google SRE SLOs: https://sre.google/sre-book/service-level-objectives/

## Default QA stance

- Treat telemetry as part of acceptance criteria (especially for integration/E2E tests).
- Require correlation: request_id + trace_id (traceparent) across boundaries.
- Prefer SLO-based release gating and burn-rate alerting over raw infra thresholds.
- Budget overhead: sampling, cardinality, retention, and cost are quality constraints.
- Redact PII/secrets by default (logs and attributes).

## Core workflows

1. Establish the minimum bar (logs + metrics + traces + correlation).
2. Instrument with OpenTelemetry (auto-instrument first, then add manual spans for key paths).
3. Verify context propagation across service boundaries (traceparent in/out).
4. Define SLIs/SLOs and error budget policy; wire burn-rate alerts.
5. Make failures diagnosable: capture a trace link + key logs on every test failure.
6. Profile and load test only after telemetry is reliable; validate against baselines.

## Quick reference

| Task | Recommended default | Notes |
|------|---------------------|-------|
| Tracing | OpenTelemetry + Jaeger/Tempo | Prefer OTLP exporters via Collector when possible |
| Metrics | Prometheus + Grafana | Use histograms for latency; watch cardinality |
| Logging | Structured JSON + correlation IDs | Never log secrets/PII; redact aggressively |
| Reliability gates | SLOs + error budgets + burn-rate alerts | Gate releases on sustained burn/regressions |
| Performance | Profiling + load tests + budgets | Add continuous profiling for intermittent issues |
| Zero-code visibility | eBPF (OpenTelemetry zero-code) + continuous profiling (Parca/Pyroscope) | Use when code changes are not feasible |

## Navigation

Open these guides when needed:

| If the user needs... | Read | Also use |
|---|---|---|
| A minimal, production-ready baseline | `references/core-observability-patterns.md` | `assets/checklists/template-observability-readiness-checklist.md` |
| Node/Python instrumentation setup | `references/opentelemetry-best-practices.md` | `assets/opentelemetry/nodejs/opentelemetry-nodejs-setup.md`, `assets/opentelemetry/python/opentelemetry-python-setup.md` |
| Working trace propagation across services | `references/distributed-tracing-patterns.md` | `assets/checklists/template-observability-readiness-checklist.md` |
| SLOs, burn-rate alerts, and release gates | `references/slo-design-guide.md` | `assets/monitoring/slo/slo-definition.yaml`, `assets/monitoring/slo/prometheus-alert-rules.yaml` |
| Profiling/load testing with evidence | `references/performance-profiling-guide.md` | `assets/load-testing/load-testing-k6.js`, `assets/load-testing/template-load-test-artillery.yaml` |
| A maturity model and roadmap | `references/observability-maturity-model.md` | `assets/checklists/template-observability-readiness-checklist.md` |
| What to avoid and how to fix it | `references/anti-patterns-best-practices.md` | `assets/checklists/template-observability-readiness-checklist.md` |

Implementation guides (deep dives):
- `references/core-observability-patterns.md`
- `references/opentelemetry-best-practices.md`
- `references/distributed-tracing-patterns.md`
- `references/slo-design-guide.md`
- `references/performance-profiling-guide.md`
- `references/observability-maturity-model.md`
- `references/anti-patterns-best-practices.md`

Templates (copy/paste):
- `assets/checklists/template-observability-readiness-checklist.md`
- `assets/opentelemetry/nodejs/opentelemetry-nodejs-setup.md`
- `assets/opentelemetry/python/opentelemetry-python-setup.md`
- `assets/monitoring/slo/slo-definition.yaml`
- `assets/monitoring/slo/prometheus-alert-rules.yaml`
- `assets/monitoring/grafana/grafana-dashboard-slo.json`
- `assets/monitoring/grafana/template-grafana-dashboard-observability.json`
- `assets/load-testing/load-testing-k6.js`
- `assets/load-testing/template-load-test-artillery.yaml`
- `assets/performance/frontend/template-lighthouse-ci.json`
- `assets/performance/backend/template-nodejs-profiling-config.js`

Curated sources:
- `data/sources.json`

## Scope boundaries (handoffs)

- Pure infrastructure monitoring (Kubernetes, Docker, CI/CD): `../ops-devops-platform/SKILL.md`
- Database query optimization (SQL tuning, indexing): `../data-sql-optimization/SKILL.md`
- Application-level debugging (stack traces, breakpoints): `../qa-debugging/SKILL.md`
- Test strategy design (coverage, test pyramids): `../qa-testing-strategy/SKILL.md`
- Resilience patterns (retries, circuit breakers): `../qa-resilience/SKILL.md`
- Architecture decisions (microservices, event-driven): `../software-architecture-design/SKILL.md`

## Tool selection notes (2026)

- Default to OpenTelemetry + OTLP + Collector where possible.
- Prefer burn-rate alerting against SLOs over alerting on raw infra metrics.
- Treat sampling, cardinality, and retention as part of quality (not an afterthought).
- When asked to pick vendors/tools, start from `data/sources.json` and validate time-sensitive claims with current docs/releases if the environment allows it.
