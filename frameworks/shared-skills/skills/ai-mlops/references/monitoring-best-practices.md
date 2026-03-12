# Monitoring Best Practices for Production ML & LLM Systems

Monitoring includes data health, model performance, system reliability, and cost tracking.

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

## 4. Monitoring Setup Checklist

- [ ] Metrics exported to Prometheus / OpenTelemetry  
- [ ] Dashboards in Grafana / Datadog  
- [ ] Synthetic load tests implemented  
- [ ] Canary version tracked  
- [ ] Version tags attached to all metrics  
