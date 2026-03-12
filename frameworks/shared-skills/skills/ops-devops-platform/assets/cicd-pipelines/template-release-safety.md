```markdown
# Release Safety Template (DevOps)

*Purpose: A complete operational template for planning, executing, validating, and safely rolling out production releases using modern DevOps and progressive delivery patterns.*

---

# 1. Release Overview

**Service / Component:**  
[name]

**Release Version / Build ID:**  
[example: v1.7.0 / SHA256: abc123]

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] multi-region  

**Release Owner:**  
[name]

**Release Window:**  
[start / end time]

**Approvals Required:**  
- [ ] Engineering  
- [ ] SRE  
- [ ] Product  
- [ ] Security  

---

# 2. Release Strategy

Choose exactly one:

- [ ] Rolling update  
- [ ] Blue/Green  
- [ ] Canary  
- [ ] Shadow traffic  
- [ ] Feature-flag gated  
- [ ] GitOps promotion  

**Rationale:**  
[Why this strategy is appropriate]

---

# 3. Pre-Release Validation

## 3.1 Deployment Readiness Checklist

- [ ] CI pipeline green  
- [ ] Unit tests passed  
- [ ] Integration tests passed  
- [ ] Security scans passed (SAST/DAST/Image scan)  
- [ ] Dependencies validated  
- [ ] Docker image signed  
- [ ] Infrastructure drift-free  
- [ ] No “freeze” period in effect  
- [ ] Code freeze followed (if applicable)  

---

## 3.2 Observability Readiness

- [ ] Dashboards updated with new version tags  
- [ ] Alerts tuned & non-noisy  
- [ ] Synthetic checks configured  
- [ ] SLO/Error budgets in healthy range  

---

## 3.3 Database Migration Check

- [ ] Schema changes backward compatible  
- [ ] Migrations tested in staging  
- [ ] Safe expand → migrate → contract workflow  
- [ ] Rollback path exists  
- [ ] No destructive operations in peak hours  

---

# 4. Release Steps (Main Plan)

```

1. Prepare artifacts
2. Deploy to staging
3. Run staging smoke tests
4. Validate logs & metrics
5. Trigger approval step
6. Deploy to production using selected strategy
7. Verify deployment
8. Monitor for regression
9. Declare success or rollback

```

---

# 5. Deployment Instructions

## 5.1 Rolling Deployment

```

kubectl set image deployment/app app=registry/app:$VERSION
kubectl rollout status deployment/app

```

Checklist:
- [ ] Readiness probe validated  
- [ ] No pod crash loops  
- [ ] Resource usage stable  

---

## 5.2 Blue/Green Deployment

```

blue = live
green = new candidate

1. Deploy green
2. Smoke test green
3. Shift traffic to green
4. Keep blue as rollback target

```

Checklist:
- [ ] Health checks green  
- [ ] DB schema compatible with both versions  
- [ ] Traffic cutover logged  
- [ ] LB switch reversible  

---

## 5.3 Canary Deployment

```

weights: 1% → 5% → 20% → 50% → 100%

```

Monitoring:
- Error rate  
- P95/P99 latency  
- CPU/memory  
- Queue length  
- DB connections  

Rollback rules:
- > 5% error rate  
- P99 latency > threshold  
- SLO burn rate high  
- Saturation > safe level  

---

# 6. Automated Gating

## 6.1 Quality Gates

- [ ] Unit test coverage > X%  
- [ ] Zero critical vulns  
- [ ] Signed artifacts only  
- [ ] Image scanning passed  
- [ ] Static analysis passed  
- [ ] Integration tests passed  

## 6.2 Deployment Gates

- [ ] Canary performance green  
- [ ] Error rate < threshold  
- [ ] No new alerts triggered  
- [ ] Rollout step < 10 minutes  

---

# 7. Risk Assessment

## 7.1 Release Risk Scoring

Rate each item 1–5 (5 = high risk):

| Area | Score | Notes |
|------|--------|--------|
| Schema changes | | |
| Cross-service dependencies | | |
| External integrations | | |
| Large code diff | | |
| Release frequency | | |
| Operational history | | |

**Total Risk Score:** [sum]

Interpretation:  
- **< 10** → Low risk  
- **10–18** → Moderate risk  
- **18+** → High risk (extra approvals needed)  

---

# 8. Rollback Plan

**Rollback Method (choose one):**
- [ ] Revert deployment (Helm/K8s)  
- [ ] Redeploy previous artifact  
- [ ] GitOps revert  
- [ ] Blue/Green fallback  
- [ ] Disable feature flags  
- [ ] DB rollback via backups/PITR  

### Rollback Template

```

Rollback Trigger:
Rollback Window:
Rollback Steps:
Verification Steps After Rollback:
Communication Plan:

```

Rollback Checklist:
- [ ] DB schema compatible  
- [ ] Previous version tested  
- [ ] Rollback < 2 minutes  
- [ ] Observability dashboard ready  
- [ ] Post-rollback smoke tests  

---

# 9. Post-Deployment Verification

## 9.1 Technical Verification

- [ ] New pods healthy  
- [ ] No CrashLoopBackOff  
- [ ] Metrics stable (latency, errors, saturation)  
- [ ] No increase in p99 latency  
- [ ] No new alerts firing  
- [ ] Logs show expected patterns  

## 9.2 Functional Verification

- [ ] Critical endpoints healthy  
- [ ] User-facing flows validated  
- [ ] Background jobs running correctly  
- [ ] Scheduled tasks unaffected  

---

# 10. Communication Plan

Channels:
- Engineering  
- SRE  
- Product/Business  
- Customer-facing status page  

Templates:

### Start Notification
```

Deploying version X to production.
Expected impact: none.

```

### Completion Notification
```

Deploy version X successful.
All metrics normal.

```

### Rollback Notification
```

Rollback initiated for version X due to <reason>.
Previous version restored.

```

---

# 11. Completed Example

**Service:** Payments API  
**Version:** v3.12.0  
**Strategy:** Canary (1%→5%→20%→100%)  
**Issues:** Slight latency spike at 5% stage  
**Rollback:** Not required  
**Post-Deploy:** Stable for 45 minutes, declared success  
**Next Steps:** Optimize DB connection pool  

---

# END
```
