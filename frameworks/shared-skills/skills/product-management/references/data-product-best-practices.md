# Data Product Best Practices  

*Operational guidance for designing, building, and managing data products.*

This file contains ONLY:

- Templates  
- Checklists  
- Patterns  
- Decision flows  
- Zero theory  

---

# 1. Data Product Definition (Operational Version)

A **data product** is a reusable, trustworthy dataset or data-powered capability with:

- Clear owners  
- Defined consumers  
- Quality guarantees  
- SLAs (freshness, availability)  
- Interfaces (APIs, queries, events)  

---

# 2. Data Product Canvas

Copy-ready template:

Name:
Domain:
Primary Consumers:
Problem this data solves:

Inputs:

Data sources
Ingestion frequency
Contracts with source systems
Transformations (logic rules):
Outputs:

Tables/views/APIs
Intended use cases
SLAs:

Freshness
Quality thresholds
Availability
Quality Dimensions:

Completeness
Validity
Consistency
Timeliness
Accuracy
Ownership:

Data Product Owner
Maintainers
Governance:

Policies
Access rules
Security
Success Metrics:

Adoption
Query volume
Time saved
Incident reduction

---

# 3. Data Product Lifecycle (Operational)

## 3.1 Phase 1 — Problem Framing

**Checklist**

- [ ] Clear consumer use case identified  
- [ ] Source systems known  
- [ ] Data privacy considerations documented  
- [ ] Business metric impacted  

---

## 3.2 Phase 2 — Sourcing & Ingestion

**Checklist**

- [ ] Data contracts in place  
- [ ] Ingestion frequency mapped (batch / streaming)  
- [ ] Source data profiling completed  
- [ ] PII handling rules defined  

**Ingestion Template**
Source:
Format:
Latency target:
Transformation tool:
Load pattern (full vs incremental):

---

## 3.3 Phase 3 — Transformation & Modeling

Use simple modeling first (avoid premature complexity).

**Checklist**

- [ ] Business logic documented  
- [ ] Transformation tests created  
- [ ] Edge cases identified  
- [ ] Definitions aligned with analytics/BI teams  
- [ ] Data lineage documented  

**Patterns**

- Dimensional modeling  
- Event-driven modeling  
- Feature store preparation for ML  

---

## 3.4 Phase 4 — Serving Layer

**Deliverables**

- [ ] API / table / view schema  
- [ ] Access policies  
- [ ] Metadata (column definitions, descriptions)  

**Checklist**

- [ ] Data permissions & entitlements  
- [ ] Cost per query monitored  
- [ ] Versioning plan  

---

## 3.5 Phase 5 — Monitoring & Quality

**Quality Dimensions**

- Completeness  
- Accuracy  
- Timeliness  
- Consistency  
- Validity  

**Quality Alerts Template**
Metric: [Accuracy / Freshness / Completeness]
Threshold:
Alerting channel:
Owner:
Runbook link:

---

# 4. Data Quality Score (Operational)

Score each 1–5:

Completeness: 1 = <60% fields populated, 5 = >98%
Accuracy: 1 = Known errors, 5 = Verified by cross-sources
Timeliness: 1 = >24h lag, 5 = Near real-time
Consistency: 1 = Frequent mismatches, 5 = Schema stable + aligned
Validity: 1 = High rule violations, 5 = <1% violations

**Overall Data Quality Score = Average of all dimensions**

---

# 5. Golden Data Platform Requirements  

*(From Milhomem’s operational guidance)*

Use this list when designing or evaluating your data platform.

**Functional Requirements**

- [ ] Automated ingestion  
- [ ] Schema enforcement  
- [ ] Data catalog & lineage  
- [ ] Transformation orchestration  
- [ ] Data quality monitoring  
- [ ] Version control for transformations  
- [ ] Secure access + governance  
- [ ] Self-service analytics  
- [ ] ML feature store support  

**Non-Functional Requirements**

- [ ] Scalability  
- [ ] High availability  
- [ ] Cost optimization  
- [ ] Data encryption  
- [ ] RBAC/ABAC permissions  
- [ ] Audit logs  

---

# 6. Data Contract Template

Field:
Definition:
Type:
Nullable:
Allowed Values:
Owner:
Change Management Rules:
Downstream Impact:

Checklist:

- [ ] Each upstream dataset has a contract  
- [ ] Versioned  
- [ ] Breaking changes announced prior  
- [ ] Automated schema checks in pipeline  

---

# 7. Data Governance Patterns

## 7.1 Governance Checklist

- [ ] Certified datasets labeled  
- [ ] Sensitive data flagged  
- [ ] PII handling standards followed  
- [ ] Role-based access control implemented  
- [ ] Data retention rules defined  
- [ ] Audit logs enabled  

## 7.2 Decision Workflow for Data Access Requests

Verify user’s role + need
Check PII/sensitive fields
Approve minimal access surface
Set expiration date
Log access approval

---

# 8. ML Data Pipeline Patterns

## 8.1 Feature Store Template

Feature Name:
Description:
Source Table:
Transformation Logic:
Freshness Target:
Owner:
Training/Serving Consistency Check:

## 8.2 Training Data Checklist

- [ ] Representative samples  
- [ ] Balanced labels  
- [ ] Leakage checked  
- [ ] Drift test performed  
- [ ] Bias assessed  

---

# 9. Decision Trees

## 9.1 Should You Create a Data Product?

Is there a repeating analytics or ML use case?
├─ No → Do not create
└─ Yes
↓
Do multiple consumers need the data?
├─ No → Local dataset only
└─ Yes
↓
Does it require SLAs or governance?
├─ Yes → Build as data product
└─ No → Keep ad-hoc

---

## 9.2 Batch vs Streaming

Do consumers need real-time?
├─ Yes → Streaming
└─ No
↓
Can source systems support events?
├─ Yes → Streaming
└─ No → Batch

---

# 10. Definition of Done (Data Product)

A data product is **ready** when:

- [ ] Clear consumer use case  
- [ ] Documented definitions & business logic  
- [ ] Quality dimensions ≥ target  
- [ ] Schema, metadata, lineage published  
- [ ] Access governance in place  
- [ ] Monitoring + alerts configured  
- [ ] SLAs defined & agreed  
- [ ] Adoption plan ready  

---

**End of file.**
