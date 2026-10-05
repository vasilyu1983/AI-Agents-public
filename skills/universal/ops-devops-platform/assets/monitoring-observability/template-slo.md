# SLO Definition Template

*Purpose: Define, monitor, and review Service Level Objectives (SLOs) and error budgets.*

## When to Use

- All critical user-facing services
- New or existing SRE monitoring rollouts

---

# TEMPLATE STARTS HERE

## SLO Overview

- **Service:**  
- **Critical User Journey:**  
- **SLO Owner:**  

## SLI (Service Level Indicators)

| Name     | Query/Measurement            | Target           |
|----------|------------------------------|------------------|
| Latency  | 95% requests < 500ms         | >= 99.9%         |
| Error Rate | % 5xx responses/total      | <= 0.1%          |
| Uptime   | Availability over 30d        | >= 99.95%        |

## Error Budget

- **Calculation:**  
  100% - SLO Target = Error Budget  
  (e.g., 100% - 99.9% = 0.1% allowed failure per period)

- **Burn Alerts:**  
  Alert if > 25% of budget used in 24h

## Monitoring/Alerting Config

- Prometheus rule:  

  ```yaml
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / sum(rate(http_requests_total[5m])) > 0.001
    for: 10m
    labels:
      severity: critical

Quality Checklist

 SLO agreed with product/engineering
 SLI queries tested and automated
 Error budget policy documented
 SLO reviews scheduled quarterly
