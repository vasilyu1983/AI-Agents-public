# EDA Best Practices

This guide provides a structured, repeatable workflow for exploratory data analysis with
explicit checks, patterns, and decision rules. It is designed for fast onboarding and
consistent DS project execution.

---

## 1. Initial Scan Checklist

Perform immediately after loading the dataset.

- [ ] Print shape (rows, columns)
- [ ] Inspect dtypes and nullable fields
- [ ] Identify primary keys or unique identifier candidates
- [ ] Check for duplicate rows and duplicate keys
- [ ] Evaluate memory usage
- [ ] Validate expected ranges for numeric columns
- [ ] Confirm presence/absence of target variable

**Pattern: Schema Validation**
df.info()
df.describe(include='all')
df.isna().sum()

---

## 2. Data Quality Assessment

### 2.1 Missingness

- Identify missingness patterns by:
  - Row
  - Column
  - Groups (user, product, geography)
- Evaluate mechanisms:
  - MCAR (random)
  - MAR (depends on other features)
  - MNAR (depends on itself; dangerous)

**Checklist - Missingness Strategy**

- [ ] Strategy per field documented  
- [ ] No target leakage introduced by imputation  
- [ ] Imputation pipelines reproducible  

---

### 2.2 Outliers

**Detection methods (choose at least one):**
- Z-score  
- IQR  
- Winsorization scan  
- Domain-rule scans (e.g., speed < 0 impossible)

**Checklist - Outlier Review**

- [ ] Extreme values inspected manually  
- [ ] Outlier handling strategy defined (cap/remove/flag)  
- [ ] Illegal values corrected or removed  

---

## 3. Distribution Analysis

Perform both univariate and bivariate analysis.

### Numeric
- Histograms  
- Boxplots  
- Quantile tables  
- Skewness/kurtosis review  

### Categorical
- Frequency distributions  
- Top-N categories report  
- Rare category detection (<1% threshold)

**Checklist - Distribution Health**

- [ ] Long tails annotated  
- [ ] Rare categories flagged  
- [ ] Highly skewed features documented for potential transforms  

---

## 4. Target Variable Analysis

### Classification targets:
- Class imbalance  
- Rare event frequency  
- Conditional distributions

### Regression targets:
- Scale and skew  
- Outliers  
- Zero-inflation

**Checklist - Target Evaluation**

- [ ] Imbalance noted  
- [ ] Appropriate metric selection influenced (e.g., PR-AUC for imbalance)  
- [ ] Target leakage checks started  

---

## 5. Leakage Detection

Leakage is the leading cause of unrealistic performance.

### High-Risk Leakage Types:
- Timestamps after event date  
- IDs encoding target  
- Aggregates computed using full window  
- Target visible in free text  
- Future features used in temporal splits  

**Checklist - Leakage Review**

- [ ] Time-based checks performed  
- [ ] ID/cardinality checks performed  
- [ ] No future window features in train set  
- [ ] Free text screened for target bleed  

---

## 6. EDA Deliverables

A complete EDA must include:

- Profile report (summary tables + visualizations)  
- Data dictionary draft  
- Issue register (severity, owner, fix plan)  
- List of known risks  
- Candidate hypotheses  
