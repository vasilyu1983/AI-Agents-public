# Data Product Canvas  

*Purpose: Define a reusable, governed, high-quality data product.*

Use for:  

- Data platform initiatives  
- Data-as-a-product teams (Mesh)  
- ML feature stores  
- Analytics-ready datasets  
- Operational data pipelines  

---

# 1. Data Product Canvas (Copy/Paste)

## 1. Overview

Name:
Owner:
Domain:
Version:
Primary Consumers:
Use Cases:

---

## 2. Problem & Value

Problem This Data Solves:
Why It Matters:
Who Benefits:
Value Metrics (time saved, accuracy increase, cost reduced):

---

## 3. Inputs

Source Systems:
Data Types (structured / semi-structured / logs / text):
Ingestion Method (batch / streaming):
Freshness Target:
Data Contracts in Place? (Y/N)
Known Quality Issues:

---

## 4. Transformations

Business Logic Summary:
Transformation Steps:
Edge-Case Rules:
Dependencies:
Testing Strategy (unit tests, schema checks):

---

## 5. Outputs

Output Format (table, view, API, event stream):
Schema:
Column Definitions:
Sample Records:
Intended Queries / ML Features:

---

## 6. SLAs & Quality

Freshness SLA:
Availability SLA:
Quality Targets:
Completeness:
Accuracy:
Consistency:
Validity:
Timeliness:

Guardrails:
Max latency:
Allowed schema drift:
Cost thresholds:

---

## 7. Governance

Access Rules (RBAC/ABAC):
PII Handling:
Security Measures:
Lineage (source → transform → output):
Retention Policy:
Audit Requirements:

---

## 8. Monitoring & Alerts

Metrics Monitored:
Alert Thresholds:
Alert Recipients:
Incident Response Runbook:
Drift Detection Rules:

---

## 9. Adoption & Documentation

Documentation Links:
How-To Guides:
Query Examples:
Success Metrics (adoption, usage, reliability):
Feedback Channels:

---

# 2. Data Product Checklist

**Problem & Value**

- [ ] Clear value for consumers  
- [ ] Problem documented in plain language  

**Inputs**

- [ ] Sources identified  
- [ ] Contracts established  
- [ ] PII flagged  

**Transformations**

- [ ] Business logic documented  
- [ ] Tests in place  
- [ ] Lineage mapped  

**Outputs**

- [ ] Schema defined  
- [ ] Data dictionary complete  
- [ ] Example queries included  

**SLAs**

- [ ] Freshness targets defined  
- [ ] Availability targets defined  
- [ ] Quality targets set  

**Governance**

- [ ] RBAC configured  
- [ ] Privacy rules applied  
- [ ] Retention documented  

**Monitoring**

- [ ] Alerts configured  
- [ ] Drift detection set  
- [ ] Ownership assigned  

**Adoption**

- [ ] Documentation published  
- [ ] Consumer onboarding defined  
- [ ] Feedback loop established  

---

# 3. Example (Editable)

Data Product Canvas

Name: Shipment Reconciliation Dataset
Owner: Data Product Owner – Logistics
Domain: Operations
Version: v1.0

Consumers: BI team, Ops analysts, ML forecasting team
Use Cases:
• Weekly SLA compliance reporting
• Predicting delay likelihood
• Automated reconciliation tasks

Problem & Value

Problem: Shipment data arrives from 5 carriers with inconsistent formats.
Why It Matters: Ops teams spend 5+ hours weekly reconciling data.
Value Metrics: -80% manual work, +20% SLA compliance.

Inputs

Sources: Carrier APIs, TMS exports, warehouse events
Ingestion: Streaming for real-time alerts
Freshness Target: < 5 minutes

Transformations

• Normalize carrier schemas
• Deduplicate shipments
• Compute ETA deltas
• Identify anomalies
Test Strategy: schema tests + dq checks

Outputs

Format: Analytics table + API
Schema: shipment_id, event_time, carrier, eta, status, anomaly_flag

SLAs & Quality

Freshness: <5 minutes
Availability: 99.9%
Quality:
Completeness: >95%
Accuracy: >98%
Validity: <1% violations

Governance

RBAC: Analysts read, ML write, Ops admin
PII: Must be stripped
Retention: 12 months rolling

Monitoring

Metrics: freshness, errors, anomaly count
Alerts: Slack + PagerDuty
Drift: compare weekly distributions

Adoption

Docs: Confluence page + DBT docs
Feedback: Slack #data-users

---

# 4. Definition of Done (Data Product Canvas)

A data product canvas is **ready** when:

- [ ] Inputs, outputs, and transformations are clear  
- [ ] SLAs and quality metrics defined  
- [ ] Governance documented  
- [ ] Monitoring plan established  
- [ ] Consumers + use cases identified  
- [ ] No unanswered sections  
- [ ] Fits on 1–2 pages  

---

**End of file.**
