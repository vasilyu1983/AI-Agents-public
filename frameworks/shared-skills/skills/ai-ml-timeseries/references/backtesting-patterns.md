# Backtesting Patterns for Forecasting

Reliable, repeatable frameworks for evaluating forecasting models.

---

## 1. Avoid Random Splits

Forecasting requires temporal integrity → **never** sample randomly.

---

## 2. Valid Backtest Structures

### Pattern A: Holdout Window

- Train on early data  
- Test on final N days/weeks  

### Pattern B: Rolling Window Backtest

Example windows:

- Train: t0 → t100  
- Validate: t101 → t120  
- Slide forward: t20 → t120, validate t121 → t140  

### Pattern C: Expanding Window

- Train expands each iteration  
- Test on next fixed horizon  

---

## 3. Multi-Horizon Evaluation

For horizon H (e.g., 1–30 days):

- Compute error for each horizon separately  
- Plot error curve  
- Identify weaknesses at long horizons  

**Checklist**

- [ ] Horizon-specific metrics computed  
- [ ] Error curves plotted  

---

## 4. Metrics for Forecasting

### Point Forecast Metrics

- MAE  
- RMSE  
- MAPE  
- sMAPE  

### Probabilistic Metrics

- Pinball loss  
- CRPS  

### Business Metrics

- Stockouts  
- Overforecast cost  

---

## 5. Backtest Execution Workflow

1. Freeze target horizon  
2. Select window scheme  
3. Train model per window  
4. Record metrics  
5. Aggregate across all windows  
6. Document results  

---

## 6. Backtesting Checklist

- [ ] Temporal ordering preserved  
- [ ] Enough windows to test variability  
- [ ] Metrics stable  
- [ ] Baseline included  
