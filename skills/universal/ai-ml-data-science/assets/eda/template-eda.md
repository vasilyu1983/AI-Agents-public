# EDA Template

A reusable structure for exploratory data analysis with explicit leakage, versioning, and decision-readiness checks.

---

## 1. Run Context

- Dataset version or snapshot  
- Environment or entrypoint (`uv`, script, notebook)  
- Prediction target  
- Prediction timestamp rule  
- Key business question

---

## 2. Dataset Summary

- Shape  
- Columns  
- Dtypes  
- Unique key check  
- Memory usage  
- Time range

---

## 3. Missingness Analysis

| Column | % Missing | Pattern | Action |
|--------|-----------|---------|--------|
|        |           |         |        |

---

## 4. Outlier Analysis

- Outlier definition: <method>  
- Detected outliers: <summary>  
- Treatment plan: <method>  
- Illegal value checks: <notes>

---

## 5. Distribution Analysis

### Numeric

- Histograms  
- Boxplots  
- Quantiles

### Categorical

- Category counts  
- Rare category scan

### Target

- Distribution  
- Class imbalance or skew  
- Baseline expectation

---

## 6. Feature Availability And Leakage

- Features available at prediction time  
- Features that need lagging or windowing  
- Global statistics that must be fit on train only  
- Columns to drop due to leakage risk  
- Entity or time-based split concerns

---

## 7. Important Slices

- Geography or market segments  
- User or account cohorts  
- Product or category groups  
- Rare or high-risk subsets

---

## 8. EDA Deliverables

- Summary of findings  
- Risks  
- Recommended split strategy  
- Recommended next modeling step
