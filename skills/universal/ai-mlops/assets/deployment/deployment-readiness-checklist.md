# MLOps Deployment Readiness Checklist

**Purpose**: Ensure production readiness, document compliance, define monitoring and rollback.

---

## Template Contract

### Goals
- Prevent unsafe or non-repeatable deployments.
- Ensure monitoring, rollback, and ownership are in place.
- Document compliance posture and operational readiness.

### Inputs
- Model artifact + registry entry + provenance (code/data/features).
- Offline evaluation report + model card.
- Deployment plan (mode, traffic ramp, infra requirements).
- Monitoring plan + runbooks + on-call ownership.

### Decisions
- Go/No-Go for production rollout.
- Rollout strategy (canary/blue-green/rolling) and rollback triggers.
- Compliance classification and required controls.

### Risks
- Silent regression, drift, and staleness in upstream features.
- Data leakage/PII exposure and access control failures.
- Inadequate rollback leading to prolonged incidents.

### Metrics
- Latency/throughput/error-rate SLOs and budget adherence.
- Quality metrics by slice; safety pass rate where applicable.
- Drift indicators and alert-to-mitigation time.

## 1. Model Artifacts

### Model Registration

| Field | Value |
|-------|-------|
| Model name | |
| Version | |
| Registry location | |
| Training commit | |
| Training data version | |
| Framework | |
| Format | |

### Provenance Verification
- [ ] Training log available and linked
- [ ] Hyperparameters documented
- [ ] Evaluation results archived
- [ ] Model card created
- [ ] Data lineage documented

### Model Card Contents
- [ ] Model description and intended use
- [ ] Training data summary
- [ ] Evaluation metrics by slice
- [ ] Known limitations
- [ ] Ethical considerations
- [ ] Maintenance contacts

---

## 2. Quality Gates

### Performance Thresholds

| Metric | Required | Actual | Status |
|--------|----------|--------|--------|
| Primary metric | >=___ | | [ ] Pass [ ] Fail |
| Secondary metric | >=___ | | [ ] Pass [ ] Fail |
| Latency P50 | <___ms | | [ ] Pass [ ] Fail |
| Latency P95 | <___ms | | [ ] Pass [ ] Fail |
| Throughput | >=___/s | | [ ] Pass [ ] Fail |
| Cost per inference | <$___ | | [ ] Pass [ ] Fail |

### Fairness & Bias

| Check | Status | Notes |
|-------|--------|-------|
| Sliced metrics computed | [ ] Done | |
| Demographic parity checked | [ ] Pass | |
| Equal opportunity checked | [ ] Pass | |
| Bias mitigation applied | [ ] N/A [ ] Applied | |
| Disparity within threshold | [ ] Pass | Threshold: ___ |

### Security

| Check | Status | Notes |
|-------|--------|-------|
| Model scanned for vulnerabilities | [ ] Done | |
| Input validation configured | [ ] Done | |
| Output filtering enabled | [ ] Done | |
| PII handling documented | [ ] Done | |
| Rate limiting configured | [ ] Done | |
| Authentication required | [ ] Done | |

---

## 3. Compliance

### Regulatory Classification

| Framework | Classification | Requirements |
|-----------|---------------|--------------|
| EU AI Act | [ ] Minimal [ ] Limited [ ] High-risk [ ] Unacceptable | |
| GDPR | [ ] Applicable [ ] N/A | Art. 22 compliance if automated decisions |
| HIPAA | [ ] Applicable [ ] N/A | BAA required |
| SOC2 | [ ] Applicable [ ] N/A | Control mapping |
| CCPA | [ ] Applicable [ ] N/A | |

### EU AI Act High-Risk Requirements (if applicable)
- [ ] Risk management system documented
- [ ] Data governance requirements met
- [ ] Technical documentation complete
- [ ] Record-keeping implemented
- [ ] Transparency provisions met
- [ ] Human oversight provisions met
- [ ] Accuracy, robustness, cybersecurity verified

### Documentation Compliance
- [ ] Model card complete
- [ ] Training data documentation
- [ ] Known limitations documented
- [ ] Intended use defined
- [ ] Prohibited uses defined
- [ ] Version history maintained

---

## 4. Operational Readiness

### Monitoring Setup

| Component | Status | Tool |
|-----------|--------|------|
| Performance dashboards | [ ] Ready | |
| Latency tracking | [ ] Ready | |
| Error rate tracking | [ ] Ready | |
| Cost tracking | [ ] Ready | |
| Data drift detection | [ ] Ready | |
| Prediction drift detection | [ ] Ready | |

### Alert Configuration

| Alert | Condition | Severity | Owner |
|-------|-----------|----------|-------|
| High latency | P95 > ___ms | | |
| Error spike | Rate > ___% | | |
| Drift detected | Score > ___ | | |
| Cost anomaly | >___% above forecast | | |
| Model degradation | Metric < ___ | | |

### Incident Response
- [ ] Runbook created
- [ ] Escalation path defined
- [ ] On-call rotation assigned
- [ ] Communication templates ready
- [ ] Post-mortem process defined

---

## 5. Rollback Plan

### Rollback Triggers

| Condition | Automatic? | Action |
|-----------|------------|--------|
| Error rate > ___% | [ ] Yes [ ] No | |
| Latency P95 > ___ms for ___min | [ ] Yes [ ] No | |
| Primary metric < ___ | [ ] Yes [ ] No | |
| Safety violation detected | [ ] Yes [ ] No | |

### Rollback Procedure
1. _______________
2. _______________
3. _______________

### Rollback Verification
- [ ] Previous version available in registry
- [ ] Rollback tested in staging
- [ ] Estimated rollback time: ___ minutes
- [ ] Data compatibility verified

---

## 6. Deployment Configuration

### Strategy

| Option | Selected | Configuration |
|--------|----------|---------------|
| Canary | [ ] | Initial: ___%, Ramp: ___ |
| Blue-green | [ ] | Switch criterion: ___ |
| Rolling | [ ] | Batch size: ___ |
| A/B test | [ ] | Split: ___/___% |

### Traffic Ramp Schedule

| Stage | Traffic % | Duration | Success Criteria |
|-------|-----------|----------|------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| Full | 100% | | |

### Resource Requirements

| Resource | Minimum | Requested | Limit |
|----------|---------|-----------|-------|
| CPU | | | |
| Memory | | | |
| GPU | | | |
| Replicas | | | |

---

## 7. Testing Verification

### Test Coverage

| Test Type | Status | Results |
|-----------|--------|---------|
| Unit tests | [ ] Pass | ___% coverage |
| Integration tests | [ ] Pass | |
| Load tests | [ ] Pass | Max QPS: ___ |
| Chaos tests | [ ] Pass [ ] N/A | |
| Shadow testing | [ ] Pass [ ] N/A | |

### Pre-Production Validation
- [ ] Staging deployment successful
- [ ] Smoke tests passed
- [ ] Performance benchmarks met
- [ ] Security scan passed

---

## 8. Dependencies

### Upstream Dependencies

| Dependency | Version | Owner | SLA |
|------------|---------|-------|-----|
| | | | |

### Downstream Dependencies

| Consumer | Impact | Notified |
|----------|--------|----------|
| | | [ ] Yes |

---

## 9. Sign-Off

### Required Approvals

| Role | Name | Date | Signature |
|------|------|------|-----------|
| ML Engineer | | | [ ] Approved |
| Platform Engineer | | | [ ] Approved |
| Security (if applicable) | | | [ ] Approved |
| Compliance (if high-risk) | | | [ ] Approved |
| Product Owner | | | [ ] Approved |

### Final Checklist
- [ ] All quality gates passed
- [ ] Monitoring verified
- [ ] Rollback tested
- [ ] Documentation complete
- [ ] All approvals obtained

### Deployment Authorization

**Authorized by**: _______________
**Date**: _______________
**Deployment window**: _______________
