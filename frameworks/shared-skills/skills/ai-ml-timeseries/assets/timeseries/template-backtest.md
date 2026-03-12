# Backtesting Template

Fully defined backtest configuration for forecasting models.

---

## 1. Backtest Window

backtest:
start: "<date>"
end: "<date>"
horizon: <N_days>
frequency: "<D/H/W>"

---

## 2. Window Type

window_type: "<rolling|expanding>"

---

## 3. Backtest Steps

1. Create initial train/val split  
2. Train model on train window  
3. Predict next horizon  
4. Slide window  
5. Repeat N times  
6. Aggregate metrics  

---

## 4. Metrics

metrics:
"mae"
"rmse"
"mape"
"smape"

---

## 5. Output Format

{
"date": "<prediction_date>",
"y_true": <value>,
"y_pred": <value>
}

---

## 6. Checklist

- [ ] Temporal order respected  
- [ ] Multiple windows tested  
- [ ] Horizon-specific error analyzed  
