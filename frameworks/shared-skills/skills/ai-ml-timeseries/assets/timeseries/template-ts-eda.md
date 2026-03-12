# Time Series EDA Template

A reproducible structure for analyzing any time series dataset.

---

## 1. Series Summary

series_name: <name>
frequency: <D/H/W/M>
start_date: <date>
end_date: <date>
num_points: <int>

---

## 2. Timestamp Validation

- [ ] Sorted  
- [ ] No duplicates  
- [ ] Frequency consistent  
- [ ] Missing timestamps identified  

missing_timestamps: <list_or_count>
duplicate_timestamps: <list_or_count>

---

## 3. Trend & Seasonality

Document:

- Observed trend (up/down/flat)  
- Seasonal cycles (daily/weekly/yearly)  
- Strength of seasonality  
- Change points  

---

## 4. Outliers

outlier_method: <zscore|iqr|rolling>
outliers_detected: <count>
outlier_dates: <sample_list>

---

## 5. Visualizations Checklist

- [ ] Raw line chart  
- [ ] Rolling mean/variance  
- [ ] Seasonal decomposition  
- [ ] ACF/PACF plots  

---

## 6. EDA Findings

Summaries:

- Data quality issues  
- Missingness behavior  
- Stationarity impressions  
