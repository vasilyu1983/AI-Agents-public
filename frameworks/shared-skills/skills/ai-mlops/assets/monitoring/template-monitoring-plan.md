# Monitoring Plan Template

A production-ready monitoring plan for ML/LLM systems.

---

## 1. Overview

System: <name>  
Owner: <team>  
Model Version: <vX.Y>  
Monitoring Dashboard: <URL>  

---

## 2. Metrics Monitored

### A. Data Quality

- Missingness  
- Feature drift  
- Schema drift  
- Volume anomalies  

### B. Prediction Quality

- Score distribution  
- Threshold metrics  
- Segment-specific KPIs  

### C. System Health

- Latency (P50, P95, P99)  
- Error rate  
- CPU/GPU usage  
- Queue depth (batch/streaming)  

### D. Business Metrics

- Conversions  
- Fraud catch rate  
- Revenue impact  

---

## 3. Alerts

### Data Alerts

- Missingness > <threshold>  
- Drift > <threshold>  

### System Alerts

- Latency P99 > <threshold>  
- Error rate > <threshold>  

### Business Alerts

- KPI drop > <threshold>  

---

## 4. Alert Routing

- Primary on-call: <team>  
- Secondary: <backup>  
- Slack/PagerDuty channel: <channel>  

---

## 5. Runbooks

Link runbooks for:

- Data pipeline failures  
- API outages  
- Model degradation  
- Vector DB issues (if LLM/RAG)  

---

## 6. Verification Checklist

- [ ] Dashboards reviewed  
- [ ] Alerts tested  
- [ ] Version tags added to metrics
