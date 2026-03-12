# Governance, Compliance & Risk Checklists

Operational governance patterns for ML/LLM/RAG systems, including compliance,
risk audits, documentation, and controls.

---

## 1. Governance Artifacts (Required)

Every model must have:

- Model card  
- Evaluation report  
- Risk assessment  
- Data lineage log  
- Versioned system prompt  
- Change log for prompt/model updates  

---

## 2. Compliance Requirements

### A. Logging & Auditability

- Maintain secure logs (no PII)  
- Log: model version, request_id, timestamp  
- Keep tamper-proof audit trail (CloudTrail equivalent)  

### B. Access Control

- RBAC at all layers  
- API key rotation  
- Enforce least-privilege  

### C. Data Retention Policy

- Define max retention window  
- Auto-delete old data  
- Document exceptions  

---

## 3. Risk Assessment Template

Risk: <risk name>
Description: <short summary>
Impact: low/medium/high
Likelihood: low/medium/high
Mitigations:
<item>
<item>
Residual Risk: low/medium/high
Owner: <team/member>

---

## 4. Safety Governance

### Requirements

- Safety filters documented  
- Red-team test suite run regularly  
- Known jailbreak patterns updated monthly  
- Incident response plan maintained  

---

## 5. Approval Checklist (Go-Live)

A model cannot enter production unless:

- [ ] Model card complete  
- [ ] Risk assessment reviewed  
- [ ] Audit logging verified  
- [ ] Input/output filters active  
- [ ] Safety tests passed  
- [ ] Governance sign-off documented  
