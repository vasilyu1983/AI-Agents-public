# Prometheus Alert Rules Template

# Purpose: Operational, actionable alert rules for critical metrics and SLOs.

groups:
- name: service-alerts
  rules:
    - alert: HighErrorRate
      expr: sum(rate(http_requests_total{status=~"5.."}[5m])) 
            / sum(rate(http_requests_total[5m])) > 0.001
      for: 10m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected on main API"
        description: "More than 0.1% 5xx responses for 10min"

    - alert: HighLatency
      expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 0.8
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "API latency 95th percentile above 800ms"
        description: "95% of requests slower than SLO for 5 minutes"
---
# Add rules for uptime, resource exhaustion, burn rate, etc.

# Checklist:
# - [ ] All alerts have runbooks/playbooks
# - [ ] Severity and routing correct
# - [ ] Alert noise reviewed after incidents
