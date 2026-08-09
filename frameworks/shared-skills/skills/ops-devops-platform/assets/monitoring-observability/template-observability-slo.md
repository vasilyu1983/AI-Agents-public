```markdown
# Observability & SLO Template (DevOps)

*Purpose: A complete template for designing, instrumenting, validating, and operating observability systems, including SLOs/SLIs, metrics, logs, traces, alerting, and dashboards.*

---

# 1. Overview

**Service Name:**  
[name]

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] multi-region  

**Purpose of Observability Design:**  
- [ ] New service instrumentation  
- [ ] SLO creation  
- [ ] Alert tuning  
- [ ] Dashboard buildout  
- [ ] On-call readiness  
- [ ] Incident-driven improvement  

**Owner:**  
[Team/Engineer]  
**Date:**  
[YYYY-MM-DD]

---

# 2. SLO Definition

## 2.1 Summary

**SLI Type:**  
- [ ] Latency  
- [ ] Availability  
- [ ] Error rate  
- [ ] Throughput  
- [ ] Freshness (async jobs)  

**SLI Specification:**
```

SLI = % of requests < 300ms latency

```

**SLO Target:**
```

99.5% over 30 days

```

**Error Budget:**
```

0.5% of 30-day window

```

---

## 2.2 Detailed SLO Template

```

Service: <service-name>
Customer Impact: <describe what failure looks like>
SLI: <definition>
SLO: <threshold and measurement window>
Error Budget: <amount and burn alarms>
Data Source: <Prometheus, ELK, Datadog, New Relic, OpenTelemetry>

```

Checklist:
- [ ] SLO tied to customer experience  
- [ ] SLI measurable in production  
- [ ] Multi-region aware  
- [ ] Retention aligns with SLO window  
- [ ] Can compute SLI retrospectively  

---

# 3. Error Budget Policy

## Burn Alerts

**Fast Burn:**  
Triggers when error budget depletes rapidly.
```

if error_budget_burn_rate > 5% / hour → alert P1

```

**Slow Burn:**  
Triggers when remaining budget trends downward.
```

if error_budget_burn_rate > 20% / 24h → alert P2

```

Checklist:
- [ ] Actions defined when burn starts  
- [ ] Deployment freeze criteria established  
- [ ] Escalation path documented  

---

# 4. Metrics (RED & Golden Signals)

## 4.1 Required Metrics

### Golden Signals
- **Latency** (p95, p99)
- **Error Rate**
- **Traffic**
- **Saturation**

### RED Method (for microservices)
- **Rate** (requests/sec)
- **Errors** (5xx + 4xx depending on SLO)
- **Duration** (latency across percentiles)

---

## 4.2 Metric Examples (Prometheus)

```

http_requests_total
http_request_errors_total
http_request_duration_seconds_bucket
kube_pod_container_status_restarts_total
node_cpu_seconds_total
container_memory_working_set_bytes

```

Checklist:
- [ ] p50, p95, p99 latency tracked  
- [ ] Error rate measured over multiple windows  
- [ ] Separate metrics for success vs failure  
- [ ] Resource saturation metrics included  

---

# 5. Logging

## 5.1 Structured Logging Format

```

{
  "ts": "2025-01-01T12:00:00Z",
  "level": "info",
  "msg": "request processed",
  "trace_id": "abc-123",
  "user_id": 42,
  "latency_ms": 85
}

```

Checklist:
- [ ] JSON only  
- [ ] No multi-line logs  
- [ ] No sensitive data (avoid: email, tokens, PII)  
- [ ] Include correlation IDs  
- [ ] Log levels appropriate  

---

# 6. Tracing

## 6.1 OpenTelemetry Standard

Required fields:
- `trace_id`
- `span_id`
- `parent_span_id`
- `service.name`
- `duration_ms`
- `status.code`
- `attributes.*`

## 6.2 Instrumentation Template

```

tracer.start_span("db.query", attributes={
    "db.statement": "...",
    "db.table": "orders",
    "db.operation": "SELECT"
})

```

Checklist:
- [ ] All inbound HTTP requests start a trace  
- [ ] All outbound calls propagate headers  
- [ ] DB calls wrapped in spans  
- [ ] Errors recorded with stack traces  
- [ ] Sampling strategy configured  

---

# 7. Alerting & Monitoring

## 7.1 Alert Design Rules

**Alerts MUST BE:**
- Actionable  
- Measurable  
- Urgent  
- Owned by a team  
- Have a runbook  

**Alerts MUST NOT BE:**
- Based on single data points  
- Flapping  
- Noisy  
- Without an owner  

---

## 7.2 Example Alerts (Prometheus)

### Latency Alert
```

ALERT HighLatencyP99
IF histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5
FOR 10m
LABELS {severity="page"}

```

### Error Rate Alert
```

ALERT ErrorRateSpike
IF rate(http_request_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05
FOR 10m
LABELS {severity="page"}

```

---

# 8. Dashboards

## Required Dashboard Panels

### Traffic
- RPS  
- Active sessions  

### Latency
- p50, p95, p99  
- Tail latencies  

### Errors
- 4xx vs 5xx split  
- Error budget burn chart  

### Saturation
- CPU/memory  
- Disk I/O  
- Queue depth  
- DB connection pools  

Dashboard Checklist:
- [ ] Real-time & historical views  
- [ ] Color-coded thresholds  
- [ ] Links to logs & traces  
- [ ] Summary and detail panels  

---

# 9. On-Call Readiness

## Runbook Template

```

Service:
Alert Name:
SLI:
SLO:
Symptoms:
Immediate Actions:
Mitigation:
Escalation:
Links:

```

---

## On-Call Checklist

- [ ] SLOs defined  
- [ ] Dashboards linked in alerts  
- [ ] Runbooks complete  
- [ ] Alerts tested  
- [ ] Escalation paths defined  
- [ ] No alert without remediation steps  

---

# 10. Observability Anti-Patterns

- AVOID: Logs without trace IDs  
- AVOID: Metrics without units  
- AVOID: Alerts without runbooks  
- AVOID: Dashboards that require tribal knowledge  
- AVOID: Noisy alerts ignored  
- AVOID: Reactive monitoring only  

---

# 11. Verification

### Observability Health Checks

- [ ] Tracing propagation verified  
- [ ] SLO reports generated correctly  
- [ ] Golden signals visible  
- [ ] Alerts fire correctly in intended scenarios  
- [ ] Logs searchable by trace_id  

---

# 12. Complete Example

**Service Name:** Checkout API  
**SLI:** `p95 latency < 400ms`  
**SLO:** 99% monthly  
**Error Budget:** 1%  
**Alerts:**  
- Fast burn (2%/h)  
- Slow burn (10%/24h)  
**Dashboards:**  
- Latency by endpoint  
- Error types  
- DB query latency  
- Queue backlog  

**Result:**  
- SLO tracking automated  
- Alerts actionable  
- On-call rotation effective  
- Latency regressions caught within minutes  

---

# END
```
