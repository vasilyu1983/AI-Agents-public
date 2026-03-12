# Time Series EDA Best Practices

A structured, operational workflow for analyzing univariate and multivariate time series.

---

## 1. Timestamp Integrity

### Required checks:
- [ ] Confirm frequency (daily, hourly, weekly, etc.)
- [ ] Identify missing timestamps
- [ ] Remove or merge duplicates
- [ ] Align timezone information
- [ ] Validate monotonic ordering

### Commands (example):
ts = ts.sort_index()
ts.asfreq('D')
ts.index.is_monotonic_increasing

---

## 2. Visualization Patterns

### Plots:
- Line plot (raw series)
- Rolling mean/variance
- Seasonal decomposition plot
- Weekly/yearly seasonal plot
- Autocorrelation (ACF) and partial autocorrelation (PACF)

**Checklist**
- [ ] Trend observed?
- [ ] Seasonality present?
- [ ] Variance stable or increasing?

---

## 3. Trend & Seasonality Analysis

### Determine:
- Direction (up/down)
- Stability (consistent/inconsistent)
- Strength (e.g., seasonal_strength metric)
- Season length (7, 24, 365, etc.)

---

## 4. Outlier Detection

### Techniques:
- Z-score
- IQR thresholds
- Sudden spikes/drops based on rolling windows

**Checklist**
- [ ] Outliers flagged
- [ ] Outlier handling strategy chosen (cap/remove/flag)

---

## 5. Missing Value Strategies

### Approaches:
- Forward fill  
- Interpolation  
- Seasonal interpolation  
- Leave missing (if models support it)

Choose based on:
- Frequency
- Impact on downstream training

---

## 6. Volume/Granularity Normalization

Aggregate or resample when:
- Granularity doesn’t match business need
- Noise is too high at lower granularity

---

## 7. TS EDA Final Deliverables

- [ ] Frequency validated  
- [ ] Seasonal/trend patterns documented  
- [ ] Outlier plan defined  
- [ ] Missing value rules defined  
- [ ] Data dictionary for temporal features  