```markdown
# Infrastructure Cost Optimization Template (DevOps)

*Purpose: A template for reviewing, analyzing, and optimizing cloud and platform costs across compute, storage, networking, and managed services.*

---

# 1. Overview

**Scope:**  
- [ ] Single service  
- [ ] Entire cluster  
- [ ] Project/account  
- [ ] Multi-cloud  

**Cloud Provider(s):**  
- [ ] AWS  
- [ ] GCP  
- [ ] Azure  
- [ ] Other: _______  

**Period Reviewed:**  
[Last 30 / 90 days]

**Owner:**  
[Name]

---

# 2. Cost Sources

- [ ] Compute (VMs, node pools, serverless)  
- [ ] Storage (block, object, DB)  
- [ ] Managed DB (RDS/CloudSQL/SQL DB)  
- [ ] Network egress  
- [ ] Load balancers & gateways  
- [ ] Observability tooling  
- [ ] CI/CD infrastructure  

---

# 3. High-Level Breakdown

| Category | Monthly Cost | % of Total |
|---------|--------------|------------|
| Compute | | |
| Storage | | |
| DB | | |
| Network | | |
| Other | | |

Identify top 5 cost drivers.

---

# 4. Compute Optimization

Checklist:
- [ ] Right-sizing instances or node pools  
- [ ] Remove idle/underutilized resources  
- [ ] Use autoscaling aggressively  
- [ ] Apply spot/preemptible workloads where safe  
- [ ] Consolidate workloads (bin-packing)  
- [ ] Reserved instances / savings plans / committed use discounts  

---

# 5. Kubernetes-Specific Optimization

Checklist:
- [ ] Resource requests tuned to real usage  
- [ ] No massive overprovisioning  
- [ ] Remove unused deployments/CRDs  
- [ ] Autoscaling for pods & nodes active  
- [ ] Remove zombie pods/namespaces  
- [ ] Right-size cluster node types  

---

# 6. Storage Optimization

Checklist:
- [ ] Unused volumes removed  
- [ ] S3/GCS/Blob lifecycle policies applied  
- [ ] Logs compressed & tiered to cheaper storage  
- [ ] Cold data moved to Glacier/Archive tiers  
- [ ] DB storage right-sized  
- [ ] Duplicate data reduced  

---

# 7. Database Cost Optimization

Checklist:
- [ ] Evaluate read replicas vs cache  
- [ ] Right-size DB instance classes  
- [ ] Storage auto-scaling limits verified  
- [ ] Index bloat under control  
- [ ] Delete stale test databases  
- [ ] Use managed backup retention wisely  

---

# 8. Network & Egress

Checklist:
- [ ] Minimize cross-region traffic  
- [ ] Cache external API calls  
- [ ] Use private connectivity where cheaper  
- [ ] Optimize CDN usage  
- [ ] Reduce unnecessary large payloads  

---

# 9. Observability & Tooling

Checklist:
- [ ] Log volume reduced with sampling / filters  
- [ ] Metrics cardinality under control  
- [ ] Retention periods reasonable  
- [ ] Multiple tools consolidated where possible  

---

# 10. Optimization Actions

List proposed changes:

| Action | Est. Savings | Impact Risk | Owner | ETA |
|-------|--------------|-------------|--------|-----|
| | | | | |

---

# 11. Validation Plan

- [ ] Apply changes in non-prod first  
- [ ] Monitor performance/SLOs after cost changes  
- [ ] Capture before/after cost graphs  
- [ ] Ensure no performance regressions  

---

# 12. Completed Example

**Scope:** K8s cluster + DB + S3 (prod)  
**Findings:**  
- Overprovisioned nodes (50% avg CPU)  
- S3 logs stored in Standard instead of IA  
- DB instance class larger than necessary  

**Actions:**  
- Right-size node pools  
- Apply lifecycle to S3 buckets  
- Reduce DB instance one size  

**Result:**  
- ~25% monthly cost reduction  
- No SLO impact  

---

# END
```
