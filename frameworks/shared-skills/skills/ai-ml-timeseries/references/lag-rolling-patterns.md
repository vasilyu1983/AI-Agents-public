# Lag & Rolling Feature Engineering Patterns

Concrete patterns to generate effective temporal features for time series forecasting using ML or deep models.

---

## 1. Lag Feature Patterns

### Daily Data

- lag_1  
- lag_7  
- lag_14  
- lag_28  

### Hourly Data

- lag_1  
- lag_24  
- lag_48  

**Checklist**

- [ ] All lags based strictly on past timestamps  
- [ ] No future leakage  
- [ ] Seasonal lags included  

---

## 2. Rolling Window Features

### Rolling windows

- mean, std, min, max, median  
- rolling_sum  
- rolling_count  
- exponentially weighted mean  

### Window sizes

- Daily: 7, 14, 30  
- Hourly: 24, 48, 72  

---

## 3. Calendar & Event Features

- Day of week  
- Week of year  
- Month, quarter  
- Holiday flag  
- End-of-quarter flag  
- Weather lag features (no future weather!)

**Checklist**

- [ ] Holidays localized to region  
- [ ] Event flags validated  
- [ ] Weather features lagged  

---

## 4. Categorical & Static Features

Useful for:

- Product hierarchy  
- Region  
- Store type  
- Item category  

Keep static features separate from temporal ones.

---

## 5. Feature Parity for Forecast Horizons

For multi-step prediction, ensure:

- [ ] Covariates aligned with each forecast horizon  
- [ ] Future-known covariates correctly applied (holidays)  
- [ ] Future-unknown covariates excluded or forecasted separately  

---

## 6. Lag/Rolling Feature Checklist

- [ ] No future leakage  
- [ ] Windows computed on historical data only  
- [ ] Seasonal structure captured  
- [ ] Covariates aligned with forecast horizon  
