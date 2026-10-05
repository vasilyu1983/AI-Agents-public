# Drift Detection & Retraining Template

Template for defining drift-monitoring logic and retraining triggers.

---

## 1. Drift Monitored

### A. Feature Drift

- PSI  
- KS test  
- Mean/variance shifts  

### B. Prediction Drift

- Score distribution changes  
- Threshold drift  

### C. Business Drift

- KPI changes  
- Seasonal changes  

---

## 2. Drift Thresholds

Define thresholds as (same pair as `scripts/drift_check.py`, which prints the no-drift p99 per feature):

| Drift Type | Metric | Threshold | Action |
|------------|--------|-----------|--------|
| Feature | PSI (from bin counts) | > max(0.1, no-drift p99 at this window's n) | Investigate |
| Feature | PSI (from bin counts) | > max(0.2, no-drift p99 at this window's n) | Retrain review |
| Prediction | | | |
| Business | | | |

---

## 3. Retraining Triggers

Retrain when:

- Drift persists > N runs  
- Upstream system changes  
- Business seasonality changes  
- Model performance drops > X%  

---

## 4. Retraining Pipeline

1. Extract latest data  
2. Rebuild features  
3. Train candidate model  
4. Evaluate against baseline  
5. Promote if metrics improve  

---

## 5. Validation Steps

- Compare metrics by slice  
- Run stability tests  
- Validate latency in serving  

---

## 6. Documentation

- Log drift events  
- Document retraining  
- Update model card  
- Update registry entry  
