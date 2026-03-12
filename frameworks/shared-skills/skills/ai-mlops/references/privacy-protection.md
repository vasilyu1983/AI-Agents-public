# Privacy Protection for ML, LLM & RAG Systems

Operational patterns for safeguarding personally identifiable information (PII), sensitive data,
and confidential inputs.

---

## 1. PII Identification & Redaction

### A. Required PII Detectors

Use both:

- Regex-based detection  
- ML classifier (NER or LLM)  

### B. Redaction Strategies

- Replace with tokens: `[EMAIL_REDACTED]`  
- Partial masking: `abc***@domain.com`  
- Remove PII from logs by default  

---

## 2. Data Minimization Rule

Store only:

- What is required for inference  
- What is legally required  
- What is approved by governance  

**Reject storing:**

- Raw chat logs  
- Sensitive identity attributes  
- Arbitrary text inputs without sanitization  

---

## 3. Privacy for RAG Pipelines

### A. Sanitizing documents

- Remove or mask sensitive content  
- Do not index private user messages unless approved  
- Maintain access control for chunks  

### B. Embedding Privacy Requirements

- Never embed raw sensitive fields  
- Replace PII with placeholders before embedding  
- Embeddings count as derived data → protect accordingly  

---

## 4. Differential Privacy (DP) for Training

### DP Requirements

- Define ε (“epsilon”) budget  
- Log DP parameters  
- Apply noise per-batch  
- Ensure DP mechanisms tested with unit tests  

---

## 5. Privacy Checklist

- [ ] Input PII masked  
- [ ] No PII stored in logs  
- [ ] RAG documents sanitized  
- [ ] Embeddings protected  
- [ ] Optional DP applied during training  
- [ ] RBAC controls tested  
