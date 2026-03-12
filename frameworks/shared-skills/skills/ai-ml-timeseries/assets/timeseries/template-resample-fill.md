# Resample & Fill Template

Standardized resampling and missing value handling for time series.

---

## 1. Resampling Rule

resample_frequency: <D/H/W/M>
aggregation_method: <sum|mean|max|min|count|custom>

---

## 2. Missing Value Strategy

missing_values:
forward_fill: true
interpolation: "linear" # linear | time | spline
seasonal_interpolation: false
drop_threshold: <percent>

**Notes**

- Use seasonal interpolation for data with strong periodicity  
- Drop periods with > threshold gaps  

---

## 3. Quality Checks

- [ ] Missingness removed  
- [ ] No new anomalies introduced  
- [ ] Rolling window alignment validated  
