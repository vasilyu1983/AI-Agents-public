---
name: qa-observability
description: "Implement OpenTelemetry logs/metrics/traces, SLI/SLO gates, burn-rate alerts, and APM integrations. Use when adding or validating observability."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Observability

Use telemetry as a QA signal and a debugging substrate. Treat logs, metrics, traces, and profiles as evidence for test outcomes, release readiness, and production regressions.

Core references live in `data/sources.json`. Prefer primary docs and re-check volatile external facts before recommending versions, pricing, or vendor features.

## Quick Start (Default)

If key context is missing, ask for: critical user journeys, service/dependency inventory, environments (local/staging/prod), current telemetry stack, and current SLO/SLA commitments.

1. Establish the minimum bar: correlation IDs, structured logs, traces, and golden metrics (latency, traffic, errors, saturation).
2. Verify propagation: confirm `traceparent` and your request ID flow across boundaries end-to-end.
3. Make failures diagnosable: every integration or E2E failure should capture a trace link or trace ID plus correlated logs, and critical degraded paths should expose structured error metadata such as rate-limit codes, retry hints, and state-transition markers.
4. Define SLIs/SLOs and an error budget policy; wire multi-window burn-rate alerts.
5. Produce artifacts: a readiness checklist, an SLO definition, and alert rules using `assets/checklists/template-observability-readiness-checklist.md`, `assets/monitoring/slo/slo-definition.yaml`, and `assets/monitoring/slo/prometheus-alert-rules.yaml`.

## Default QA stance

- Treat telemetry as acceptance criteria, especially for integration and E2E flows.
- Require correlation: request ID plus trace ID across service boundaries.
- For critical journeys, make auth redirects, rate limits, and state-sync lag diagnosable with structured codes or attributes instead of opaque text-only errors.
- Prefer SLO-based release gates and burn-rate alerts over raw infrastructure thresholds.
- Treat sampling, cardinality, retention, and cost as quality constraints.
- Redact PII and secrets by default in logs, spans, and attributes.
- Treat logs and profiles as ecosystem-dependent in OpenTelemetry: confirm language and backend support before promising a vendor-neutral implementation.
- The OTel Span Events API (`Span.AddEvent`, `Span.RecordException`) is being deprecated in favour of log-based events (announced March 2026). Write new event instrumentation via the Logs API; existing span event data remains functional during the gradual transition.

## Expert Judgment (what a checklist misses)

- **Zero observability, first hour:** Do not start with a dashboard. Instrument, in order: (1) one structured log line per request with `request_id`, `trace_id`, `route`, `status`, `duration_ms`; (2) the four golden metrics (latency histogram, traffic counter, error counter, saturation gauge) on the single busiest entry point; (3) one end-to-end trace for the single highest-revenue or highest-incident-rate user journey. Skip dashboards, SLOs, and alerting until these three exist — they are the substrate everything else reads from, and building alerting on top of nothing produces false confidence, not safety.
- **Logs vs. traces, the actual decision rule:** Reach for a trace when the question is "where in this one request did time or an error go" — traces are cheap to read only when propagation already works end-to-end. Reach for a log when the question is "did this business event happen, and what were its exact values" — logs are the durable record of state transitions (payment captured, order cancelled, flag evaluated) that a trace's short retention window will not have next month. When both would answer the question, prefer the trace for latency/causality debugging and the log for audit, compliance, or anything a support engineer needs six weeks from now. Metrics answer "how often" and "how much" cheaply at scale; never reconstruct a rate or percentile by scanning logs or traces if a metric could have carried it.
- **Sampling, the trade a checklist glosses over:** Head sampling is a bet that the sample is representative — it is not, for errors, once error rate is below the sampling ratio (see `references/sampling-strategies.md` for the survivor-bias math). Tail sampling fixes that at the cost of collector-side buffering, memory, and the operational complexity of routing all spans of one trace to the same collector instance. Default recommendation: head-sample low-value traffic at a low, stable ratio; tail-sample (or always keep) errors and traces above a latency threshold; never derive SLIs from sampled trace data — derive them from metrics, which are not sampled.
- **Alert fatigue is a design failure, not a tuning problem:** if a service has more than 3-5 paging alerts, the fix is consolidation onto SLO burn rate (see `references/alerting-strategies.md`), not better thresholds on the existing alerts. An on-call engineer who receives more than ~2 pages per 12-hour shift will start ignoring pages before the quarter ends, regardless of how correct any individual alert is.
- **Cost control is a first-class design constraint, not a later optimization pass:** cardinality (unique label/attribute combinations) is the dominant cost driver in metrics and the dominant query-latency driver in high-cardinality log/trace backends — a single unbounded label (user ID, order ID, raw URL path) can turn a $200/month Prometheus instance into a $20k/month one. Budget cardinality and retention per signal before instrumenting, not after the bill arrives; treat a proposed new label as a design review item, not a one-line PR.

## Workflow

1. Establish the baseline: logs, metrics, traces, correlation, and at least one diagnosable critical journey.
2. Instrument with OpenTelemetry: auto-instrument first, then add manual spans for business workflow boundaries.
3. Verify context propagation across HTTP, queues, and RPC boundaries.
4. Define SLIs/SLOs, error budgets, and burn-rate alerts. For low-traffic services, prefer event-count or window sizing guidance from SRE workbook material.
5. Make failures diagnosable: attach trace links, key logs, and relevant metrics to failed tests.
6. Add performance evidence only after telemetry is trustworthy: profiling, load tests, exemplars, and baselines.

## Quick reference

| Task | Recommended default | Notes |
|------|---------------------|-------|
| Tracing | OpenTelemetry + Collector + OTLP-compatible backend | Jaeger and Tempo are both fine backends; keep Collector as the default routing layer |
| Metrics | Prometheus + Grafana | Use latency histograms; native histograms are GA (Grafana, Oct 2025) — treat rollout as an infrastructure change, test dashboards and alerts first |
| Logging | Structured JSON to stdout/stderr + Collector/filelog pipeline | Never log secrets or high-cardinality IDs as labels; OTel Logs SDK maturity varies by language — check status page before adopting direct SDK path |
| Reliability gates | SLIs/SLOs + error budgets + burn-rate alerts | Gate releases on sustained burn and material regressions |
| Performance | Continuous profiling + load tests + budgets | For stable production profiling use Pyroscope or Parca today; OTel Profiles signal is Alpha (target GA Q3 2026) |
| Zero-code visibility | eBPF-based instrumentation where feasible | Beyla is production-ready and donated to CNCF as opentelemetry-ebpf-instrumentation (OBI); versioning moves fast (3.x line by mid-2026) — check the current release before citing a version; validate kernel 5.8+, runtime, and backend compatibility |
| LLM / AI agent visibility | OTel GenAI semconv + cost metrics + eval events | Stability tier of `gen_ai.client`/`gen_ai.agent` spans is unverified and sources conflict as of 2026-07-11 — check `github.com/open-telemetry/semantic-conventions-genai` before shipping; see `references/tools-ebpf-apm.md` |

## ASCII Flow

```text
Observability QA request
  -> Identify critical journeys, services, dependencies, and environments
  -> Establish correlation IDs, structured logs, traces, and golden metrics
  -> Verify propagation across HTTP, queues, jobs, and RPC boundaries
  -> Define SLIs, SLOs, error budgets, and burn-rate alerts
  -> Attach trace/log/metric evidence to test and release failures
  -> Use profiles and load evidence only after telemetry is trustworthy
```

## Navigation

Open these guides when needed:

| If the user needs... | Read | Also use |
|---|---|---|
| A minimal production baseline | `references/core-observability-patterns.md` | `assets/checklists/template-observability-readiness-checklist.md` |
| Current Node or Python instrumentation | `references/opentelemetry-best-practices.md` | `assets/opentelemetry/nodejs/opentelemetry-nodejs-setup.md`, `assets/opentelemetry/python/opentelemetry-python-setup.md` |
| Working trace propagation across services | `references/distributed-tracing-patterns.md` | `assets/checklists/template-observability-readiness-checklist.md` |
| SLOs, burn-rate alerts, and release gates | `references/slo-design-guide.md` | `assets/monitoring/slo/slo-definition.yaml`, `assets/monitoring/slo/prometheus-alert-rules.yaml` |
| Profiling and load testing evidence | `references/performance-profiling-guide.md` | `assets/load-testing/load-testing-k6.js`, `assets/load-testing/template-load-test-artillery.yaml` |
| A maturity model and roadmap | `references/observability-maturity-model.md` | `assets/checklists/template-observability-readiness-checklist.md` |
| What to avoid and how to fix it | `references/anti-patterns-best-practices.md` | `assets/checklists/template-observability-readiness-checklist.md` |
| Alert design and fatigue reduction | `references/alerting-strategies.md` | `assets/monitoring/slo/prometheus-alert-rules.yaml` |
| Dashboard hierarchy and layout | `references/dashboard-design-patterns.md` | `assets/monitoring/grafana/template-grafana-dashboard-observability.json` |
| Structured logging and cost control | `references/log-aggregation-patterns.md` | `assets/observability/template-logging-setup.md` |
| RED vs USE vs Golden Signals — choosing a metrics framework | `references/methods-red-use-golden.md` | `references/slo-design-guide.md` |
| Sampling strategies, tail sampling, exemplars | `references/sampling-strategies.md` | `references/opentelemetry-best-practices.md` |
| eBPF and APM tool stubs (Beyla, Pixie, Honeycomb, SigNoz, Coroot), LLM/AI agent observability | `references/tools-ebpf-apm.md` | `data/sources.json` |

Implementation guides:
- `references/core-observability-patterns.md`
- `references/opentelemetry-best-practices.md`
- `references/distributed-tracing-patterns.md`
- `references/slo-design-guide.md`
- `references/performance-profiling-guide.md`
- `references/observability-maturity-model.md`
- `references/anti-patterns-best-practices.md`
- `references/alerting-strategies.md`
- `references/dashboard-design-patterns.md`
- `references/log-aggregation-patterns.md`
- `references/methods-red-use-golden.md`
- `references/sampling-strategies.md`
- `references/tools-ebpf-apm.md`
- [references/information-theory-applied.md](references/information-theory-applied.md) — Information-theory applied recipes for observability: alert-noise audit, sampling budget, KL drift detection.
- [references/control-theory-applied.md](references/control-theory-applied.md) — Control-theory applied recipes for observability: anti-flap thresholds, burn-rate damping, Kalman health score.
- [references/queueing-theory-applied.md](references/queueing-theory-applied.md) — Queueing applied recipes for observability: Little's-Law saturation SLOs, USL release-regression, end-to-end latency budgets.
- [references/reliability-theory-applied.md](references/reliability-theory-applied.md) — Reliability primitives (MTBF/MTTR, availability, FMEA, error budgets) applied to observability and SLO design.

Templates:
- `assets/checklists/template-observability-readiness-checklist.md`
- `assets/observability/template-logging-setup.md`
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

## Do / Avoid

### Do

- Start with correlation IDs, structured logs, and traces as the minimum bar
- Use SLO-based burn-rate alerts over raw infrastructure thresholds
- Redact PII and secrets by default in logs, spans, and attributes
- Use OpenTelemetry semantic conventions for standard protocol attributes
- Add manual spans around business workflow boundaries, not route-level duplicates

### Avoid

- Logging secrets or high-cardinality IDs as metric labels
- Alerting on raw infrastructure metrics without SLO context
- Inventing custom attribute names when semantic conventions exist
- Adding instrumentation without a sampling and cardinality strategy
- Trusting auto-instrumentation alone for business workflow visibility

## Scripts

Stdlib-only Python CLI tools. No pip dependencies — run with Python 3.9+.

| Script | Purpose |
|--------|---------|
| `scripts/observability_scorer.py` | Maturity scoring, SLO error budget analysis, and readiness report generation |

**Quick start:**

```bash
# Score observability maturity (0–100) across 6 signal dimensions
python scripts/observability_scorer.py maturity \
  --input data/sample-observability-profile.json

# Calculate SLO error budget burn rates and status flags
python scripts/observability_scorer.py slo \
  --input data/sample-slo-data.json

# Full readiness report (maturity + SLO) written to a Markdown file
python scripts/observability_scorer.py report \
  --input data/sample-observability-profile.json \
  --slos  data/sample-slo-data.json \
  --output report.md
```

See `scripts/README.md` for full CLI reference and input schema.

## Data

Sample input files for the scripts.

| File | Description |
|------|-------------|
| `data/sample-observability-profile.json` | Realistic B2B SaaS service observability assessment (checkout-service, Node.js) |
| `data/sample-slo-data.json` | Five SLO definitions with current availability and event counts |
| `data/sources.json` | Curated reference sources for the skill |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | Infrastructure monitoring, Kubernetes, CI/CD |
| [data-sql-optimization](../data-sql-optimization/SKILL.md) | Database query optimization and indexing |
| [qa-debugging](../qa-debugging/SKILL.md) | Application-level debugging and stack traces |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Test strategy design and coverage |
| [qa-resilience](../qa-resilience/SKILL.md) | Resilience patterns, retries, and circuit breakers |
| [software-architecture-design](../software-architecture-design/SKILL.md) | Architecture decisions |

## Tool selection notes

- Default to OpenTelemetry + OTLP + Collector where possible.
- Prefer SLO-based burn-rate alerting over alerting on raw infrastructure metrics.
- Use semantic conventions for standard protocol attributes; avoid inventing parallel names for HTTP, DB, messaging, or RPC spans.
- When auto-instrumentation already creates server spans, add manual spans around business workflow boundaries instead of duplicating route spans.
- When asked to pick vendors or tools, start from `data/sources.json` and validate time-sensitive claims with current docs or releases.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search or web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

