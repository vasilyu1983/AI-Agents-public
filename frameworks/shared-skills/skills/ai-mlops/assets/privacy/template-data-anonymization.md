# Data Anonymization Template

Provides patterns for sanitizing sensitive data before storage, embedding, or training.

---

## 1. Anonymization Strategy

Choose between:

- Tokenization (e.g., [NAME_1])  
- Masking (***1234)  
- Removal (drop)  

strategy: "tokenize"

---

## 2. Tokenization Scheme

tokens:
name: "[NAME]"
email: "[EMAIL]"
phone: "[PHONE]"
id: "[ID]"

---

## 3. Fields to Anonymize

fields:
"email"
"phone"
"ip_address"
"customer_id"
"address"

---

## 4. Embedding Safety

NEVER embed:

- Raw messages from private users  
- Highly sensitive categories  
- De-anonymizable sequences  

---

## 5. QA Checklist

- [ ] No reversible tokens  
- [ ] Consistent mapping across dataset  
- [ ] Mapping dictionary stored securely  
- [ ] Sampling spot-check performed  
