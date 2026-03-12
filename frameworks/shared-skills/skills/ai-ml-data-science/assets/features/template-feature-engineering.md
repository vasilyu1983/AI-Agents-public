# Feature Engineering Template

Use this document to define, track, and validate all engineered features.

---

## 1. Overview

**Target Variable:**  
<describe>  

**Feature Set Version:**  
<vX.Y>  

---

## 2. Raw -> Engineered Feature Mapping

| Raw Column | Transformation | Output Feature | Notes |
|------------|----------------|----------------|-------|
|            |                |                |       |

---

## 3. Numeric Features

**Scaling:**  

- <method>  

**Outlier Handling:**  

- <method>  

**Transformations:**  

- log(x)  
- sqrt(x)  
- binning  

---

## 4. Categorical Features

**Encoding Types:**  

- One-hot  
- Frequency  
- Target (with CV)  
- Hashing  

**Rules:**  

- Handle rare categories  
- Map unseen categories  

---

## 5. Text Features

**Preprocessing:**  

- Lowercase  
- Strip HTML  
- Remove punctuation  

**Representations:**  

- TF-IDF  
- Pretrained embeddings  

---

## 6. Datetime Features

- Day of week  
- Hour of day  
- Weekend flag  
- Holiday flag  

**Leakage Checks:**  

- No use of future information  

---

## 7. Final Feature List

| Feature | Type | Description |
|---------|------|-------------|
|         |      |             |

---

## 8. Validation Checklist

- [ ] Deterministic transformations  
- [ ] Leakage reviewed  
- [ ] Train/serve parity ensured  
- [ ] Versioned in registry  
