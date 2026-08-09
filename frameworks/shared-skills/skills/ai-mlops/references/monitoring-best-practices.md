# Monitoring Best Practices for Production ML & LLM Systems

Monitoring includes data health, model performance, system reliability, and cost tracking.

## Table of Contents

- [1. Monitoring Dimensions](#1-monitoring-dimensions)
- [2. Dashboard Requirements](#2-dashboard-requirements)
- [3. Alerting Best Practices](#3-alerting-best-practices)
- [4. OpenTelemetry for LLM - Maturity Caveat](#4-opentelemetry-for-llm--maturity-caveat)
- [5. Monitoring Setup Checklist](#5-monitoring-setup-checklist)

---

## 1. Monitoring Dimensions

### A. Data Monitoring

- Feature distributions vs training
- Missingness
- Drift detection metrics
- Volume anomalies
- Freshness checks

### B. Prediction Monitoring

- Score distribution stability
- Threshold health
- Unusual spikes or flatlines

### C. Label-Arrival Monitoring

- Delayed labels
- Changed label definitions
- Silent label pipeline failures

### D. System Monitoring

- Latency (P50 / P95 / P99)
- Error rate
- CPU/GPU utilization
- Memory leaks
- Queue backlog (for batch/streaming)

### E. Business KPIs

- Conversion rate
- Fraud detection rate
- Revenue impact

---

## 2. Dashboard Requirements

Must include:

- Live traffic stats
- Latency heatmap
- Drift heatmap
- Slice-level metrics
- Version comparison

---

## 3. Alerting Best Practices

### Alerts must be

- Actionable  
- Routed to right owners  
- Not noisy (avoid alert fatigue)  

### Recommended Alerts

- Latency P99 > SLO
- Data freshness > threshold (e.g., >2 hours delay)
- Feature drift > threshold
- Prediction spike/drop
- Error rate > X%

---

## 4. OpenTelemetry for LLM — Maturity Caveat

OpenTelemetry GenAI semantic conventions cover LLM request/response telemetry (tokens, model IDs, prompt attributes, tool calls). As of mid-2026, all `gen_ai.*` attributes, metrics, events, and spans — including MCP-specific conventions, previously under `model/gen-ai/`, `model/openai/`, and `model/mcp/` in the core `open-telemetry/semantic-conventions` repo — were deprecated there and **moved to a dedicated repository**, `open-telemetry/semantic-conventions-genai`. As of July 2026 that repo has no tagged releases and no published docs site (docs live only in its `/docs` folder); the old opentelemetry.io/docs/specs/semconv/gen-ai/ page is now just a "moved" stub. Treat the whole convention as pre-release and expect churn.

**Operational guidance:**
- Pin an exact commit or schema-version reference from `open-telemetry/semantic-conventions-genai`, not a floating package tag — there is no stable release to pin to yet
- Re-check the repo before upgrading instrumentation: https://github.com/open-telemetry/semantic-conventions-genai
- MCP semantic conventions (for agent–MCP-server interactions) live in the same new repo at an even earlier maturity stage — treat as experimental; verify current state before production use
- Log the semconv version (or commit SHA) alongside every trace batch so you can correlate schema changes with dashboarding breakage

```python
# Pin in requirements.txt or pyproject.toml:
# opentelemetry-semantic-conventions==<version>  # pin, do not float
# opentelemetry-sdk==<version>                   # pin, do not float

# Tag every metric export with the convention version for auditability
resource = Resource(attributes={
    "service.name": "ml-serving",
    "semconv.version": "1.26.0",  # update when you upgrade
})
```

---

## 5. Monitoring Setup Checklist

- [ ] Metrics exported to Prometheus / OpenTelemetry  
- [ ] OTel GenAI semconv version pinned in instrumentation dependencies  
- [ ] Dashboards in Grafana / Datadog  
- [ ] Synthetic load tests implemented  
- [ ] Canary version tracked  
- [ ] Version tags attached to all metrics  
