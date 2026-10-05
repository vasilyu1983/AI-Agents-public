---
name: qa-observability
description: "Implements OpenTelemetry logs/metrics/traces, SLI/SLO gates, burn-rate alerts, and APM integrations. Use when adding or validating observability."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# QA Observability

Use telemetry as a QA signal and a debugging substrate. Treat logs, metrics, traces, and profiles as evidence for test outcomes, release readiness, and production regressions.

Core references live in `data/sources.json`; load the task-specific guide from Navigation.

## Quick Start (Default)

If key context is missing, ask for: critical user journeys, service/dependency inventory, environments (local/staging/prod), current telemetry stack, and current SLO/SLA commitments.

1. Establish the minimum bar: correlation IDs, structured logs, traces, and golden metrics (latency, traffic, errors, saturation).
2. Verify the telemetry transport with one known request or fault: application emission, context propagation, collector acceptance, and backend query. Stop the claim at the last observed stage; static SDK or collector configuration proves configuration only.
3. Make failures diagnosable: every integration or E2E failure should capture a trace link or trace ID plus correlated logs, and critical degraded paths should expose structured error metadata such as rate-limit codes, retry hints, and state-transition markers.
4. When dashboards, SLOs, or alerting are in scope, define the relevant SLI/SLO and error-budget policy, verify that the dashboard selects the known telemetry, and test alert evaluation and routing with a synthetic condition and a controlled non-production receiver. Do not notify real responders without explicit authorization. Record backend-query, dashboard-selection, rule-evaluation, route, and delivery results independently; basic instrumentation can stop after backend-query proof.
5. Produce the artifacts that match the task: a readiness checklist, SLO definition, or alert rules using `assets/checklists/template-observability-readiness-checklist.md`, `assets/monitoring/slo/slo-definition.yaml`, and `assets/monitoring/slo/prometheus-alert-rules.yaml`. Preserve environment, service revision, trace/request ID, query window, sampling decision, and the result of each stage exercised.

## Default QA stance

- Treat telemetry as acceptance criteria, especially for integration and E2E flows.
- Require correlation: request ID plus trace ID across service boundaries.
- For critical journeys, make auth redirects, rate limits, and state-sync lag diagnosable with structured codes or attributes instead of opaque text-only errors.
- Prefer SLO-based release gates and burn-rate alerts over raw infrastructure thresholds.
- Treat sampling, cardinality, retention, and cost as quality constraints.
- Redact PII and secrets by default in logs, spans, and attributes.
- Use OpenTelemetry semantic conventions instead of custom attribute names, and add manual spans at business workflow boundaries: auto-instrumentation alone does not show them.
- Treat logs and profiles as ecosystem-dependent in OpenTelemetry: confirm language and backend support before promising a vendor-neutral implementation.
- The OTel Span Events API (`Span.AddEvent`, `Span.RecordException`) is being deprecated in favour of log-based events ([OTel blog](https://opentelemetry.io/blog/2026/deprecating-span-events/)). Write new event instrumentation via the Logs API; existing span event data remains functional during the gradual transition.

## Expert Judgment (what a checklist misses)

- **Missing telemetry:** Start with one critical journey: a structured request log, golden metrics at its entry point, and a propagated trace. Query a known request before using dashboards or alerts as evidence.
- **Logs or traces:** Use traces for request causality and latency, logs for business state transitions, and metrics for rates and percentiles. Verify retention, sampling, and audit requirements before treating logs or traces as durable records.
- **Sampling:** Tail sampling can only retain spans that reach the sampler. Head-dropped traces cannot be recovered downstream; route all spans of a trace to the same tail-sampling collector and account for buffering. Use unsampled request metrics for SLIs. For configuration constraints, read [OpenTelemetry sampling](https://opentelemetry.io/docs/concepts/sampling/) and `references/sampling-strategies.md`.
- **Paging:** Consolidate duplicate symptoms into actionable SLO alerts. Measure page load and response quality; use the service's staffing and error-budget policy rather than a universal alert-count cap. See `references/alerting-strategies.md`.
- **Cardinality:** Bound metric labels such as user IDs and raw paths; backend cost depends on the signal and storage design. Retain useful log/trace dimensions deliberately, with a stated retention and ingestion budget. Look up the chosen backend's billing dimensions and limits before sizing it.
- **Debugging boundary:** Use telemetry to locate the affected component and request context, then use a debugger when code-level execution evidence is needed.

## Workflow

1. Establish the baseline: logs, metrics, traces, correlation, and at least one diagnosable critical journey.
2. Instrument with OpenTelemetry: auto-instrument first, then add manual spans for business workflow boundaries.
3. Verify context propagation across HTTP, queues, and RPC boundaries.
4. Define SLIs/SLOs, error budgets, and burn-rate alerts from the [canonical burn-rate table](references/slo-design-guide.md#canonical-multi-window-burn-rate-table), which also covers low-traffic services.
5. Make failures diagnosable: attach trace links, key logs, and relevant metrics to failed tests.
6. Add performance evidence only after telemetry is trustworthy: profiling, load tests, exemplars, and baselines.

## Quick reference

| Task | Recommended default | Notes |
|------|---------------------|-------|
| Tracing | OpenTelemetry + Collector + OTLP-compatible backend | Jaeger and Tempo are both fine backends; keep Collector as the default routing layer |
| Metrics | Prometheus + Grafana | Use latency histograms. Check [native histogram documentation](https://prometheus.io/docs/specs/native_histograms/) for the deployed version's scrape and storage settings; treat rollout as an infrastructure change and test dashboards and alerts first |
| Logging | Structured JSON to stdout/stderr + Collector/filelog pipeline | Never log secrets or high-cardinality IDs as labels; OTel Logs SDK maturity varies by language — check status page before adopting direct SDK path |
| Reliability gates | SLIs/SLOs + error budgets + burn-rate alerts | Gate releases on sustained burn and material regressions |
| Performance | Continuous profiling + load tests + budgets | For stable production profiling use Pyroscope or Parca; check [OTel Profiles status](https://opentelemetry.io/docs/concepts/signals/profiles/) before critical production use, and see `references/performance-profiling-guide.md` |
| Zero-code visibility | eBPF-based instrumentation where feasible | Before choosing Beyla/OBI, check [Beyla setup requirements](https://grafana.com/docs/beyla/latest/setup/) and the selected release for kernel, permissions, runtime, and backend compatibility |
| LLM / AI agent visibility | OTel GenAI semconv + cost metrics + eval events | GenAI conventions live in `github.com/open-telemetry/semantic-conventions-genai`; check the repo for their stability status before shipping, pin a semconv version, and expect renames. See `references/tools-ebpf-apm.md` and [ai-coding-agents-observability-evals](../ai-coding-agents-observability-evals/SKILL.md) for agent traces and evals |

## Navigation

Open these guides when needed:

| If the user needs... | Read | Also use |
|---|---|---|
| A minimal production baseline | [references/core-observability-patterns.md](references/core-observability-patterns.md) | [assets/checklists/template-observability-readiness-checklist.md](assets/checklists/template-observability-readiness-checklist.md) |
| Current Node or Python instrumentation | [references/opentelemetry-best-practices.md](references/opentelemetry-best-practices.md) | [assets/opentelemetry/nodejs/opentelemetry-nodejs-setup.md](assets/opentelemetry/nodejs/opentelemetry-nodejs-setup.md), [assets/opentelemetry/python/opentelemetry-python-setup.md](assets/opentelemetry/python/opentelemetry-python-setup.md) |
| Working trace propagation across services | [references/distributed-tracing-patterns.md](references/distributed-tracing-patterns.md) | `assets/checklists/template-observability-readiness-checklist.md` |
| SLOs, burn-rate alerts, and release gates | `references/slo-design-guide.md` (canonical burn-rate table) | [assets/monitoring/slo/slo-definition.yaml](assets/monitoring/slo/slo-definition.yaml), [assets/monitoring/slo/prometheus-alert-rules.yaml](assets/monitoring/slo/prometheus-alert-rules.yaml), [rule tests](assets/monitoring/slo/prometheus-alert-rules.test.yaml) (`promtool test rules`), [assets/monitoring/grafana/grafana-dashboard-slo.json](assets/monitoring/grafana/grafana-dashboard-slo.json) |
| Profiles as telemetry (continuous profiling, exemplars, OTel Profiles) | [references/performance-profiling-guide.md](references/performance-profiling-guide.md) | Diagnosis: [software-performance](../software-performance/SKILL.md); load tests: [qa-testing-performance](../qa-testing-performance/SKILL.md); starter assets: [assets/performance/backend/template-nodejs-profiling-config.js](assets/performance/backend/template-nodejs-profiling-config.js), [assets/performance/frontend/template-lighthouse-ci.json](assets/performance/frontend/template-lighthouse-ci.json), [assets/load-testing/load-testing-k6.js](assets/load-testing/load-testing-k6.js), [assets/load-testing/template-load-test-artillery.yaml](assets/load-testing/template-load-test-artillery.yaml) |
| A maturity model and roadmap | [references/observability-maturity-model.md](references/observability-maturity-model.md) | `assets/checklists/template-observability-readiness-checklist.md` |
| What to avoid and how to fix it | [references/anti-patterns-best-practices.md](references/anti-patterns-best-practices.md) | `assets/checklists/template-observability-readiness-checklist.md` |
| Alert design and fatigue reduction | [references/alerting-strategies.md](references/alerting-strategies.md) | `assets/monitoring/slo/prometheus-alert-rules.yaml` |
| Dashboard hierarchy and layout | [references/dashboard-design-patterns.md](references/dashboard-design-patterns.md) | [assets/monitoring/grafana/template-grafana-dashboard-observability.json](assets/monitoring/grafana/template-grafana-dashboard-observability.json) |
| Structured logging and cost control | [references/log-aggregation-patterns.md](references/log-aggregation-patterns.md) | [assets/observability/template-logging-setup.md](assets/observability/template-logging-setup.md) |
| RED vs USE vs Golden Signals — choosing a metrics framework | [references/methods-red-use-golden.md](references/methods-red-use-golden.md) | `references/slo-design-guide.md` |
| Sampling strategies, tail sampling, exemplars | [references/sampling-strategies.md](references/sampling-strategies.md) | `references/opentelemetry-best-practices.md` |
| eBPF and APM tool stubs (Beyla, Pixie, Honeycomb, SigNoz, Coroot), LLM/AI agent observability | [references/tools-ebpf-apm.md](references/tools-ebpf-apm.md) | `data/sources.json` |
| Debugging a production anomaly with no hypothesis and no reproduction | [references/core-analysis-loop.md](references/core-analysis-loop.md) | `../qa-debugging/references/production-debugging-patterns.md` |
| Reliability, queueing, control, or information theory applied to telemetry | [references/reliability-theory-applied.md](references/reliability-theory-applied.md), [references/queueing-theory-applied.md](references/queueing-theory-applied.md), [references/control-theory-applied.md](references/control-theory-applied.md), [references/information-theory-applied.md](references/information-theory-applied.md) | the matching `foundations-*` skill |

Curated sources: `data/sources.json`.

## Avoid

- Logging secrets or high-cardinality IDs as metric labels
- Inventing custom attribute names when semantic conventions exist
- Adding instrumentation without a sampling and cardinality strategy
- Trusting auto-instrumentation alone for business workflow visibility; add manual spans at business workflow boundaries, not duplicate route spans
- Picking vendors from memory: start from `data/sources.json` and check current docs or releases

## Scripts

Stdlib-only Python CLI tools; run with Python 3.9+. Regression tests require pytest.

| Script | Purpose |
|--------|---------|
| `scripts/observability_scorer.py` | Maturity scoring, SLO error budget analysis, and readiness report generation |

The scorer accepts complete-window SLO measurements only; its status thresholds are local heuristics, not multi-window paging decisions. Supply `target_pct` strictly between 0 and 100, positive integer `window_days`, and either both integer event counts (`total_events` positive, `0 <= good_events <= total_events`) or an explicit finite `current_availability_pct` in 0..100. Counts take precedence over a supplied percentage; zero events cannot establish health. Percentage-only inputs leave remaining event budget unknown. Maturity scores are supplied self-assessments, not runtime proof; each provided dimension needs an integer score in its documented range. Invalid or missing required inputs fail with an error.

Regression tests: [scripts/test_observability_scorer.py](scripts/test_observability_scorer.py). Run `python3 -m pytest scripts/test_observability_scorer.py`; set `OBSERVABILITY_SCORER_SCRIPT` to an alternate script path when comparing a saved implementation.

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
| [software-performance](../software-performance/SKILL.md) | Performance diagnosis and profiling |
| [qa-testing-performance](../qa-testing-performance/SKILL.md) | Load, stress, and soak tests; performance CI gates |
| [ai-coding-agents-observability-evals](../ai-coding-agents-observability-evals/SKILL.md) | Agent traces and eval pipelines |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
