# EDA Best Practices

This guide provides a structured, repeatable workflow for exploratory data analysis with
explicit checks, patterns, and decision rules. It is designed for fast onboarding and
consistent DS project execution.

---
## Table of Contents

- [1. Initial Scan Checklist](#1-initial-scan-checklist)
- [2. Data Quality Assessment](#2-data-quality-assessment)
- [2.1 Missingness](#21-missingness)
- [2.2 Outliers](#22-outliers)
- [3. Distribution Analysis](#3-distribution-analysis)
- [Numeric](#numeric)
- [Categorical](#categorical)
- [4. Target Variable Analysis](#4-target-variable-analysis)
- [Classification targets:](#classification-targets)
- [Regression targets:](#regression-targets)
- [5. Leakage Detection](#5-leakage-detection)
- [High-Risk Leakage Types:](#high-risk-leakage-types)
- [6. EDA Deliverables](#6-eda-deliverables)


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

### Expert Instincts (what a non-expert misses)

- **Suspiciously perfect features are the first suspect, not a lucky find.** A single feature with near-perfect separation (AUC > 0.98 alone, or a feature that alone beats the eventual model) is almost always a leak, not a signal — treat it as a bug report before treating it as a discovery.
- **Leakage hides in joins, not just columns.** A feature computed correctly in isolation can still leak if the join key resolves differently at train time (full history available) versus serve time (only history up to the request). Ask "what did this join actually see" per row, not just "is this column defined before the label."
- **Group leakage survives a correct time split.** A time-based split stops future-timestamp leakage but not entity leakage — the same user/account/household appearing in both train and validation with correlated behavior still inflates the score. When entities repeat across time, combine a time split with a group split (or use blocked time-series CV grouped by entity).
- **Aggregation window off-by-one is the most common silent leak.** "Rolling 7-day spend" computed with a window that includes the prediction day itself (not just the 7 days before it) is leakage that will not show up in a schema check — verify window boundaries against the actual prediction timestamp, not just that a window exists.
- **A metric that looks "too good for the domain" is evidence, not a compliment.** If domain experts would be surprised by the reported performance, investigate before presenting it — believable-but-wrong numbers get shipped more often than obviously-broken ones.

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
