# MLOps Deployment Template

This template defines a reproducible, production-ready ML deployment process.

---

## 1. Deployment Summary

**Model Name:** <name>  
**Version:** <vX.Y.Z>  
**Owner:** <team>  
**Deployment Type:** <batch / online / hybrid / streaming>  
**Deployment Date:** <date>

---

## 2. Release Inputs

- Model artifact URI: <location>  
- Feature pipeline version: <version>  
- Environment spec: <requirements.txt / Dockerfile>  
- Config file: <yaml/json>  

---

## 3. Readiness Checks

### Functional
- [ ] Evaluation report attached  
- [ ] Slice analysis reviewed  
- [ ] Model card complete  

### Operational
- [ ] Logging configured  
- [ ] Monitoring dashboards ready  
- [ ] Alerts wired to on-call  

### Safety
- [ ] Bias review complete  
- [ ] PII policy validated  
- [ ] Fallback model identified  

---

## 4. Deployment Steps

### 4.1 Build & Package
- Build Docker image  
- Install dependencies  
- Validate GPU/CPU compatibility  

### 4.2 Dev → Staging → Prod Promotion
- Deploy to dev  
- Smoke-test API / batch job  
- Canary in staging  
- Promote to prod upon approval  

### 4.3 Post-Deployment Validation
- Track first 24 hours  
- Validate metrics vs previous version  
- Confirm low-latency and low-error rates  

---

## 5. Rollback Plan

Trigger rollback if:
- Latency spike persists > threshold  
- Error rate > SLO  
- Drift detection triggers emergency thresholds  
- Critical incident opened  

Rollback steps:
1. Revert routing to previous version  
2. Disable new model  
3. Document incident  

---

## 6. Dependencies

| Component | Version | Notes |
|----------|---------|-------|
| Feature pipeline | | |
| Vector DB (if used) | | |
| API layer | | |
| Scheduler | | |

---

## 7. Open Risks

| Risk | Mitigation | Owner |
|------|------------|-------|
|      |            |       |
