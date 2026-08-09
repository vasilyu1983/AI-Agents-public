# Observability Readiness Checklist (QA)

Use this checklist before relying on telemetry for test or release decisions.

## Core

### Logs

- [ ] Structured logs (JSON) with consistent fields
- [ ] Correlation IDs present: request ID and trace ID (W3C Trace Context: https://www.w3.org/TR/trace-context/)
- [ ] Sensitive data redacted (no secrets/PII)
- [ ] Log levels enforced (debug not enabled by default in prod)
- [ ] Logs are searchable in a central store (with retention policy)

### Metrics

- [ ] SLIs defined: availability, error rate, latency (p95/p99), saturation
- [ ] Dashboards exist for the above SLIs and have owners
- [ ] Baselines exist (last 7/30 days) so regressions are visible
- [ ] Alerting is tied to symptoms (SLO burn), not raw infra noise

### Traces

- [ ] Trace propagation works across service boundaries (OpenTelemetry: https://opentelemetry.io/docs/)
- [ ] Critical spans exist for key operations (auth, checkout, search, etc.)
- [ ] Spans include useful attributes (route, status code, tenant, dependency)
- [ ] Sampling policy documented (example: 100% errors, sampled successes)

### SLOs and Runbooks

- [ ] Service SLOs and error budget policy defined (Google SRE SLOs: https://sre.google/sre-book/service-level-objectives/)
- [ ] Alerts have runbooks with clear steps, owners, and rollback criteria
- [ ] On-call escalation paths and communication templates exist (if applicable)

### QA and CI Integration

- [ ] Tests emit correlation IDs on failure (request/trace IDs in logs)
- [ ] Test runs are tagged (env, build SHA, suite, shard/worker)
- [ ] Failure artifacts are stored and linked (logs/traces/screenshots)

### Cost and Privacy Guardrails

- [ ] Telemetry retention and sampling tuned for cost
- [ ] Access controls in place for logs/traces (least privilege)
- [ ] PII review completed for log/trace fields

## Optional: AI / Automation

Do:
- Use AI to cluster alert storms and summarize incident timelines; verify via trace/log evidence.
- Use AI to propose missing telemetry fields and dashboards; review with owners.

Avoid:
- Auto-remediation without guardrails and human review for high-severity actions.
- "Black box" anomaly detection without explainability and rollback plans.
