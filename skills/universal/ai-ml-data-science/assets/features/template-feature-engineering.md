# Feature Engineering Template

Use this document to define, track, and validate engineered features with point-in-time correctness.

---

## 1. Overview

**Target Variable:**  
<describe>

**Prediction Timestamp Rule:**  
<describe what information is available at scoring time>

**Dataset Version:**  
<snapshot or id>

**Feature Set Version:**  
<vX.Y>

---

## 2. Raw -> Engineered Feature Mapping

| Raw Column | Transformation | Output Feature | Available At Prediction Time? | Notes |
|------------|----------------|----------------|-------------------------------|-------|
|            |                |                |                               |       |

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
- Native categorical

**Rules:**  

- Handle rare categories  
- Map unseen categories  
- Version encoder logic

---

## 5. Text Features

**Preprocessing:**  

- Lowercase or preserve case  
- Strip HTML  
- Remove obvious noise

**Representations:**  

- TF-IDF  
- Pretrained embeddings

---

## 6. Datetime Features

- Day of week  
- Hour of day  
- Weekend flag  
- Holiday flag  
- Lag and rolling windows

**Leakage Checks:**  

- No use of future information  
- Timezone alignment confirmed

---

## 7. Contracts And Parity

- Schema validation: <Pandera / GX Core / other>  
- Shared train/serve transforms: <yes/no>  
- Backfill or recompute notes: <notes>  
- Sensitive feature handling: <notes>

---

## 8. Final Feature List

| Feature | Type | Description | Owner |
|---------|------|-------------|-------|
|         |      |             |       |

---

## 9. Validation Checklist

- [ ] Deterministic transformations  
- [ ] Leakage reviewed  
- [ ] Train/serve parity ensured  
- [ ] Dataset and feature versions recorded  
- [ ] Sensitive features reviewed  
- [ ] Validation checks implemented
