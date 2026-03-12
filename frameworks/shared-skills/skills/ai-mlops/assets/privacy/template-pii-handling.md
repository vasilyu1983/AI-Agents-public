# PII Handling Template

Defines how the system detects, sanitizes, and manages personally identifiable information.

---

## 1. PII Classification

pii_types:
email
phone
address
name
ssn
credit_card

---

## 2. Detection

Use both:

- Regex-based extraction  
- ML/NLP-based entity detection  

detection:
regex: true
ner_model: "<model>"
llm_assist: false

---

## 3. Redaction Policy

redaction:
email: "[EMAIL_REDACTED]"
phone: "[PHONE_REDACTED]"
ssn: "[SSN_REDACTED]"
default_mask: "***"

---

## 4. Logging Rules

- Do not log raw PII  
- Do not store full user-provided messages  
- Hash user identifiers  

---

## 5. Storage Rules

- Encrypt sensitive data  
- Enforce access control through RBAC  
- Use anonymized IDs when possible  

---

## 6. Checklist

- [ ] Detection tested  
- [ ] Redaction verified  
- [ ] No PII in logs  
- [ ] Access control validated  
