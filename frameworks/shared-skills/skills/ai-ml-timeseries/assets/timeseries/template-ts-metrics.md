# Time Series Metrics Template

Defines evaluation metrics for point and probabilistic forecasts.

---

## 1. Point Forecast Metrics

point_metrics:
mae: true
rmse: true
mape: true
smape: true
mase: false

---

## 2. Probabilistic Metrics

prob_metrics:
pinball_loss: true
crps: true
quantiles: [0.1, 0.5, 0.9]

---

## 3. Business Metrics (Custom)

business_metrics:
stockout_cost: false
overforecast_cost: false

---

## 4. Output Format

{
"metric": "<name>",
"value": <float>
}

---

## 5. Checklist

- [ ] Metrics aligned with objective  
- [ ] Horizon-specific results included  
- [ ] Slice by product/region if applicable  
