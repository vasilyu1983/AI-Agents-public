# Feature Engineering Patterns

A collection of operational patterns for transforming raw data into model-ready features.

---

## 1. Numeric Feature Patterns

### 1.1 Standardization

Use when units vary or model sensitive to scale.

- z-score  
- min-max  
- robust scaling (median/IQR)

### 1.2 Outlier Handling

- Winsorize top/bottom 1%  
- Cap values at domain limits  
- Log transform long-tailed distributions  

**Checklist - Numeric Features**

- [ ] Consistent units  
- [ ] Outliers handled  
- [ ] Skew addressed  

---

## 2. Categorical Feature Patterns

### 2.1 Low Cardinality

- One-hot encoding  
- Ordinal encoding (only when true order exists)

### 2.2 High Cardinality

- Target encoding (use CV to avoid leakage)  
- Frequency encoding  
- Hashing  

**Checklist - Categorical Features**

- [ ] Rare categories grouped/flagged  
- [ ] Clear mapping for unseen categories  
- [ ] Encoders versioned for training/serving parity  

---

## 3. Text Feature Patterns

### 3.1 Cleaning

- Strip HTML  
- Lowercase or case-preserve based on domain  
- Remove excessive whitespace  

### 3.2 Representations

- TF-IDF  
- Pretrained embeddings  
- Keyword densities  
- Text length signals  

**Checklist - Text Features**

- [ ] Deterministic preprocessing  
- [ ] PII removed where required  
- [ ] Embedding models versioned  

---

## 4. Time-Based Features

### 4.1 Datetime Decomposition

- Year, month, day  
- Day of week  
- Hour, minute  
- Boolean flags (weekend, holiday)

### 4.2 Lag Features

- lag_1, lag_7, lag_28  
- Rolling windows  

**Checklist - Time Features**

- [ ] Timezone alignment validated  
- [ ] Features do not leak future information  

---

## 5. Interaction Patterns

Use carefully to avoid explosion.

- Crossed categorical features  
- Numeric x categorical interactions  
- Polynomial features (2nd/3rd degree)

**Checklist - Interaction Features**

- [ ] Interaction justified  
- [ ] No combinatorial blow-up  
- [ ] Feature importance reviewed  

---

## 6. Train/Serve Consistency Patterns

### Ensuring parity between offline and production pipelines

- Use shared **feature store** when possible  
- Encode with version-pinned transformers  
- Enforce dtype consistency  

**Checklist - Consistency**

- [ ] Single source of truth for transformations  
- [ ] Serving pipeline tested with training artifacts  
