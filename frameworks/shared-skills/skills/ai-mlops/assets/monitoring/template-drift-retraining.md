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

Define thresholds as:

| Drift Type | Metric | Threshold | Action |
|------------|--------|-----------|--------|
| Feature | PSI | 0.2 | Investigate |
| Feature | PSI | 0.3 | Retrain |
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
