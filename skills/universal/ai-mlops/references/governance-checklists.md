# Governance, Compliance & Risk Checklists

Operational governance patterns for ML/LLM/RAG systems, including compliance,
risk audits, documentation, and controls.

---

## Table of Contents

- [1. Governance Artifacts (Required)](#1-governance-artifacts-required)
- [2. Compliance Requirements](#2-compliance-requirements)
- [3. Risk Assessment Template](#3-risk-assessment-template)
- [4. Safety Governance](#4-safety-governance)
- [5. Approval Checklist (Go-Live)](#5-approval-checklist-go-live)
- [6. EU AI Act Compliance Checkpoints](#6-eu-ai-act-compliance-checkpoints)

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

---

## 6. EU AI Act Compliance Checkpoints

### Timeline Is A Lookup Step

Obligation dates depend on the system's risk class and on amendments that move through political agreement, adoption and Official Journal publication at different times. Before committing a date to a roadmap:

1. Classify the system (prohibited, Annex III high-risk, Annex I safety component, transparency-only, general-purpose model).
2. Read the obligation date for that class in the Official Journal text and the Commission's or a tracker's implementation timeline, and note the date you checked.
3. Treat an amendment as binding only once published and in force; "agreed" or "adopted" is not "in force".
4. Record the classification, the source and the check date in the governance evidence.

The canonical AI Act statement for the library lives in startup-compliance-enterprise-readiness regulatory-overlays.

### Compliance Checklist

- [ ] AI features classified against Annex III high-risk categories  
- [ ] Compliance owner assigned for any qualifying feature  
- [ ] Applicable obligation date verified at https://artificialintelligenceact.eu/implementation-timeline/  
- [ ] Design changes tracked — a reclassification may occur if system scope expands  
- [ ] Provider DPAs reviewed for controller/processor classification under AI Act  
