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

### Current Timeline (verify before acting)

Verify the active enforcement state at https://artificialintelligenceact.eu/implementation-timeline/ before committing dates to any compliance roadmap.

**Key milestones (as of June 2026):**

- **2025-08-02**: GPAI model obligations and governance/penalties framework already in effect.
- **2026-08-02**: Main body of the Act applies (new high-risk AI systems placed on market from this date).

**May 7, 2026 political agreement — deadline extensions (pending formal adoption):**

EU lawmakers agreed on May 7, 2026 to extend compliance deadlines for specific categories:

- **Annex III high-risk systems** (biometrics, critical infrastructure, employment/recruitment, credit scoring, public sector): new or substantially modified systems receive a **16-month extension** to **December 2, 2027** (from the original August 2026 deadline).
- **Annex I AI safety components** (AI embedded in regulated products such as medical devices, machinery): **12-month extension** to **August 2, 2028**.
- **AI-generated content transparency** (watermarking/labeling): **3-month extension** to **December 2, 2026**.

This agreement must still be formally adopted by the Council and European Parliament before it takes legal effect. Do not treat these extended deadlines as final until formal adoption is confirmed.

Source: Travers Smith legal briefing, May 8, 2026 (https://www.traverssmith.com/knowledge/knowledge-container/eu-agrees-to-delay-key-ai-act-compliance-deadlines/).

### Compliance Checklist

- [ ] AI features classified against Annex III high-risk categories  
- [ ] Compliance owner assigned for any qualifying feature  
- [ ] Applicable obligation date verified at https://artificialintelligenceact.eu/implementation-timeline/  
- [ ] Design changes tracked — a reclassification may occur if system scope expands  
- [ ] Provider DPAs reviewed for controller/processor classification under AI Act  
