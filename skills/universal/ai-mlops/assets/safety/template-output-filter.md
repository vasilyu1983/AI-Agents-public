# Output Filtering Template

A template for filtering model responses prior to delivery to the end user.

---

## 1. Overview

Purpose: Ensure responses adhere to safety, policy, and compliance constraints.

---

## 2. Output Filter Config

output_filter:
check_regex: true
check_classifier: true
check_llm: true
enforce_json: true

---

## 3. Regex Filters

regex_blocklist:
"(?i)kill"
"(?i)attack"
"(?i)bomb"
"(?i)hack"

---

## 4. Safety Classifier

classifier:
model: "<safety_classifier>"
threshold: 0.80
categories:

- harmful
- hateful
- sexually_explicit
- illegal

---

## 5. LLM-Based Rewriter (Optional)

rewriter:
enabled: true
strategy: "safe_completion"

---

## 6. Logging Requirements

- Log blocked outputs with hashed identifiers  
- Never log sensitive input data  

---

## 7. Checklist

- [ ] Regex filters tested  
- [ ] Classifier calibrated  
- [ ] Rewriter validated  
- [ ] Logging secure  
