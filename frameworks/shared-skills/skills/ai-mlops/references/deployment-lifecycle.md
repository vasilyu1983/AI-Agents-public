# ML Deployment Lifecycle Patterns

Standard operational patterns for taking models from development to production with reliability, observability, and maintainability.

---

## Overview

The deployment lifecycle encompasses all stages from freezing training code to decommissioning obsolete models. This guide provides a structured approach to **pre-deploy validation, deployment mechanics, observability, operations, and evolution**.

**Key Topics:**
- Pre-deployment validation and registration
- Environment promotion (dev → staging → prod)
- Smoke testing and validation
- Observability and logging
- Incident handling and operations
- Model evolution and retirement

---

## Pattern 1: Standard Deployment Lifecycle

### Five Phases

```
Pre-Deploy → Deploy → Observe → Operate → Evolve
```

### Phase 1: Pre-Deploy

**Objective:** Ensure model is ready for production

**Activities:**
1. **Freeze training code and artifacts**
   - Lock training pipeline version (git commit, Docker image)
   - Save final model checkpoint
   - Document training data snapshot ID
   - Record hyperparameters and configuration

2. **Register model and metadata**
   - Upload to model registry (MLflow, W&B, Vertex AI)
   - Tag with version, owner, and stage (`candidate`)
   - Link to evaluation report and training run
   - Document acceptance criteria

3. **Validate on held-out data**
   - Test on unseen hold-out set
   - Check for data leakage or overfitting
   - Validate metrics meet acceptance criteria
   - Compare to current production model

4. **Shadow validation**
   - Run model on live traffic without serving predictions
   - Compare predictions to production model
   - Check latency and resource usage
   - Validate input/output schemas

**Checklist: Pre-deploy complete**

- [ ] Training code frozen (git commit documented)
- [ ] Model registered with version, metadata, owner
- [ ] Evaluation metrics meet acceptance criteria
- [ ] Hold-out validation passed
- [ ] Shadow validation passed (if applicable)
- [ ] Deployment plan reviewed and approved
- [ ] Rollback procedure documented

---

### Phase 2: Deploy

**Objective:** Safely promote model through environments

**Environment progression:**
```
dev → staging → prod
```

**Activities:**

**1. Package model + environment**
- Containerize with Docker or define environment spec
- Include all dependencies (Python libs, CUDA, system libs)
- Embed preprocessing/postprocessing code
- Use configurable paths (no hardcoded file paths)

**2. Deploy to dev**
- Deploy to development environment
- Run smoke tests (basic predictions work)
- Validate API endpoints and schemas
- Check logs and metrics collection

**3. Deploy to staging**
- Deploy to staging environment (prod-like)
- Run integration tests
- Validate against staging data
- Check performance under load
- Test monitoring and alerting

**4. Deploy to prod**
- Gradual rollout (canary or blue-green)
- Start with small % of traffic (5-10%)
- Monitor metrics closely
- Expand gradually if healthy
- Full rollout after validation

**Deployment strategies:**

| Strategy | Description | Use When |
|----------|-------------|----------|
| **Blue-Green** | Two identical environments; switch traffic instantly | Need instant rollback, low tolerance for errors |
| **Canary** | Route small % traffic to new version, expand gradually | Want gradual validation, can tolerate partial rollback |
| **Rolling** | Replace instances one-by-one | Zero-downtime updates, batch systems |
| **Shadow** | Run new model alongside old, don't serve predictions yet | High-risk changes, need extensive validation |

**Checklist: Deployment complete**

- [ ] Model packaged with reproducible environment
- [ ] Smoke tests passed in dev
- [ ] Integration tests passed in staging
- [ ] Canary/blue-green deployment executed
- [ ] Production traffic validated (latency, errors, predictions)
- [ ] Rollback procedure tested
- [ ] Deployment recorded in model registry

---

### Phase 3: Observe

**Objective:** Instrument model for continuous monitoring

**Observability pillars:**

**1. Logging**
- Request/response payloads (PII-redacted)
- Prediction scores and confidence
- Model version and timestamp
- Request ID for tracing
- Latency and errors

**2. Metrics**
- Request rate (requests/sec)
- Latency (P50, P95, P99)
- Error rate (4xx, 5xx, timeouts)
- Prediction distributions
- Resource usage (CPU, GPU, memory)

**3. Traces**
- Distributed tracing for multi-service calls
- Feature retrieval latency
- Model inference time
- Postprocessing latency

**Validation in production:**

**Data validation:**
- Input schema compliance
- Feature distributions vs training
- Missing values and outliers
- Data freshness

**Prediction validation:**
- Output distributions stable
- Confidence scores reasonable
- Edge case handling (nulls, extremes)
- A/B test metrics (if applicable)

**Checklist: Observability enabled**

- [ ] Logging captures request ID, model version, latency, errors
- [ ] Metrics collected for rate, latency, errors, predictions
- [ ] Distributed tracing configured
- [ ] Data validation checks run on live traffic
- [ ] Prediction distributions monitored
- [ ] Dashboards created for all key metrics
- [ ] Alerts configured for SLO violations

---

### Phase 4: Operate

**Objective:** Handle incidents and maintain SLAs

**Operational responsibilities:**

**1. Incident handling**
- Monitor alerts and dashboards
- Respond to SLO violations
- Execute runbooks for common failures
- Escalate if needed
- Document incidents in post-mortems

**2. SLA tracking**
- Latency targets (e.g., P99 < 500ms)
- Availability targets (e.g., 99.9% uptime)
- Error rate limits (e.g., < 0.1% errors)
- Data freshness guarantees

**3. Cost management**
- Track inference costs (compute, GPU time)
- Monitor token usage (for LLMs)
- Optimize resource allocation
- Right-size infrastructure

**4. Traffic patterns**
- Monitor daily/weekly patterns
- Plan for peak loads
- Scale resources proactively
- Identify anomalies

**Common failure modes:**

| Failure | Detection | Response |
|---------|-----------|----------|
| **API outage** | Health checks failing, 5xx errors spiking | Rollback to previous version, restart services |
| **Latency spike** | P99 exceeds SLO | Check downstream dependencies, scale up resources |
| **Data quality drop** | Schema violations, missing features | Switch to cached features, alert data team |
| **Prediction drift** | Distribution shift detected | Shadow new model, trigger retraining pipeline |

**Checklist: Operations ready**

- [ ] Runbooks exist for major failure modes
- [ ] On-call rotation or escalation defined
- [ ] SLAs documented and monitored
- [ ] Alert routing configured
- [ ] Cost tracking enabled
- [ ] Capacity planning for peak loads
- [ ] Rollback procedure tested quarterly

---

### Phase 5: Evolve

**Objective:** Continuously improve model performance

**Evolution activities:**

**1. Retrain**
- Scheduled retraining (e.g., monthly)
- Trigger-based retraining (drift detected)
- Incorporate new labeled data
- Experiment with improved architectures

**2. Re-evaluate**
- Offline metrics on new test set
- Online A/B tests vs current production
- Slice analysis (performance by segment)
- Business KPI impact

**3. Promote/Demote versions**
- Promote candidate to production if better
- Demote production to candidate if worse
- Archive old versions (keep for rollback)
- Document promotion decisions

**4. Decommission obsolete models**
- Sunset unused versions
- Clean up infrastructure
- Archive artifacts for compliance
- Update documentation

**Model versioning:**

```
experimental → candidate → staging → production → archived
```

**Promotion criteria:**
- Offline metrics improvement > threshold (e.g., +2% F1)
- Online A/B test shows positive lift
- No latency or cost regression
- Stakeholder approval

**Checklist: Evolution process defined**

- [ ] Retraining schedule or triggers documented
- [ ] Re-evaluation criteria defined
- [ ] Promotion workflow documented
- [ ] Version history tracked in registry
- [ ] Decommissioning procedure defined
- [ ] Archived models retained for compliance period

---

## Pattern 2: Environment Management

### Dev Environment

**Purpose:** Fast iteration and experimentation

**Characteristics:**
- Uses sample data or synthetic data
- Relaxed validation rules
- Manual deployment (no CI/CD required)
- Fast feedback loops

**Checklist:**
- [ ] Sample data representative of production
- [ ] Environment reset procedure documented
- [ ] API endpoints functional

### Staging Environment

**Purpose:** Pre-production validation

**Characteristics:**
- Mirrors production infrastructure
- Uses production-like data (PII-redacted)
- Automated CI/CD deployment
- Full monitoring and alerting

**Checklist:**
- [ ] Infrastructure matches production (same instance types, scaling)
- [ ] Data is realistic (volume, distribution, schema)
- [ ] Integration tests run automatically
- [ ] Monitoring dashboards identical to production
- [ ] Load testing performed

### Production Environment

**Purpose:** Serve live traffic

**Characteristics:**
- High availability and reliability
- Full observability and alerting
- Gradual rollouts (canary, blue-green)
- Strict change management

**Checklist:**
- [ ] SLAs defined and monitored
- [ ] Rollback procedure tested
- [ ] On-call support available
- [ ] Change approval process enforced
- [ ] Capacity planning for peak loads

---

## Pattern 3: Deployment Automation

### CI/CD Pipeline

**Stages:**

1. **Build**
   - Package model and dependencies
   - Build Docker image
   - Run unit tests

2. **Test**
   - Integration tests
   - Validation on test data
   - Schema compliance checks

3. **Deploy**
   - Deploy to staging automatically
   - Run smoke tests
   - Deploy to production with approval

4. **Validate**
   - Monitor metrics post-deployment
   - Compare to baseline
   - Auto-rollback on failures

**Tools:**
- GitHub Actions, GitLab CI, Jenkins
- Docker, Kubernetes
- Terraform or CloudFormation for infrastructure

**Checklist:**
- [ ] CI/CD pipeline defined and tested
- [ ] Automated tests cover critical paths
- [ ] Deployment requires approval for production
- [ ] Rollback automated or one-click
- [ ] Pipeline metrics tracked (build time, success rate)

---

## Pattern 4: Gradual Rollout Strategies

### Canary Deployment

**Process:**
1. Deploy new version to small % of traffic (5-10%)
2. Monitor metrics (latency, errors, predictions)
3. Gradually increase traffic (10% → 25% → 50% → 100%)
4. Rollback if metrics degrade

**When to use:**
- High-risk model changes
- Need gradual validation
- Can tolerate partial rollback

**Checklist:**
- [ ] Traffic splitting configured (load balancer or feature flag)
- [ ] Metrics compared between old and new versions
- [ ] Automated rollback on threshold breach
- [ ] Gradual expansion schedule defined

### Blue-Green Deployment

**Process:**
1. Deploy new version to "green" environment (parallel to "blue")
2. Validate green environment thoroughly
3. Switch all traffic from blue to green instantly
4. Keep blue as rollback option

**When to use:**
- Need instant rollback capability
- Low tolerance for errors
- Can afford duplicate infrastructure temporarily

**Checklist:**
- [ ] Blue and green environments identical
- [ ] Traffic switch mechanism tested
- [ ] Validation complete before traffic switch
- [ ] Blue environment kept warm for fast rollback

### Shadow Deployment

**Process:**
1. Deploy new model alongside production model
2. Send all traffic to both models
3. Serve only production model predictions
4. Compare predictions and metrics offline
5. Promote shadow to production after validation

**When to use:**
- High-risk changes (new architecture, major refactor)
- Need extensive validation without user impact
- Can afford extra compute cost

**Checklist:**
- [ ] Shadow model receives same inputs as production
- [ ] Predictions logged and compared
- [ ] Latency and resource usage measured
- [ ] Promotion criteria defined

---

## Pattern 5: Rollback Procedures

### When to Rollback

**Automatic rollback triggers:**
- Error rate > threshold (e.g., > 1%)
- Latency > SLO (e.g., P99 > 1s)
- Prediction quality drop detected
- Resource exhaustion (OOM, CPU saturation)

**Manual rollback scenarios:**
- Business KPIs declining
- Customer complaints
- Unexpected behavior discovered
- Security vulnerability

### Rollback Checklist

- [ ] Previous model version still deployed (blue-green) or available in registry
- [ ] Traffic can be switched instantly (< 5 minutes)
- [ ] Rollback procedure documented and tested
- [ ] Rollback decision authority defined
- [ ] Post-rollback validation steps defined

### Post-Rollback Actions

1. **Validate stability:** Confirm metrics return to baseline
2. **Investigate root cause:** Analyze logs, traces, data
3. **Document incident:** Write post-mortem
4. **Fix and re-deploy:** Address root cause, re-test, re-deploy

---

## Real-World Example: Fraud Detection Model Deployment

### Context

**Model:** Binary classifier for transaction fraud
**Latency SLO:** P99 < 200ms
**Availability SLO:** 99.95%
**Deployment strategy:** Canary rollout

### Pre-Deploy

1. **Freeze training:**
   - Training code: `git:abc123`
   - Model checkpoint: `fraud_model_v42.pkl`
   - Training data: `transactions_2024_Q4`

2. **Register model:**
   - MLflow registry: `fraud_detection_v42`
   - Metrics: AUC 0.94, Precision 0.89, Recall 0.87
   - Owner: `ml-platform-team`

3. **Validate:**
   - Hold-out AUC: 0.93 (meets threshold > 0.90)
   - Shadow validation: 99.2% agreement with prod model
   - Latency: P99 = 180ms (within SLO)

### Deploy

1. **Package:**
   - Docker image: `fraud-api:v42`
   - Dependencies: Python 3.11, scikit-learn 1.3, FastAPI

2. **Staging:**
   - Deployed to staging Kubernetes cluster
   - Smoke tests passed
   - Load test: 1000 req/s, P99 = 190ms

3. **Production canary:**
   - 10% traffic to v42
   - Monitored for 2 hours
   - Metrics stable → expanded to 50%
   - Expanded to 100% after 24 hours

### Observe

**Logging:**
- Request ID, transaction ID, prediction, confidence
- Model version, latency, timestamp

**Metrics:**
- Request rate: 500 req/s average
- Latency: P99 = 185ms
- Error rate: 0.02%
- Fraud detection rate: 1.2% of transactions

**Alerts:**
- P99 latency > 200ms → page on-call
- Error rate > 0.1% → alert team
- Fraud rate deviation > 50% → investigate

### Operate

**Incident 1:** Latency spike to 450ms
- **Detection:** Alert fired at 03:15 AM
- **Response:** Scaled up pods from 10 to 20
- **Resolution:** Latency returned to 180ms
- **Root cause:** Upstream feature store slow query
- **Preventive action:** Added caching layer

**Incident 2:** Prediction drift detected
- **Detection:** Fraud rate dropped from 1.2% to 0.8%
- **Response:** Investigated recent data changes
- **Root cause:** Schema change in upstream transactions table (new field `is_verified` not in training data)
- **Resolution:** Retrained model with new field, deployed v43

### Evolve

**Retraining schedule:** Monthly
**Trigger-based retraining:** Drift detected (AUC drops > 5%)
**Promotion:** v43 promoted after outperforming v42 in A/B test (precision +3%)

---

## Tools & Frameworks

**Model registries:**
- MLflow (open-source, model tracking + registry)
- Weights & Biases (experiment tracking + registry)
- Vertex AI Model Registry (GCP managed)
- SageMaker Model Registry (AWS managed)

**Deployment platforms:**
- Kubernetes (container orchestration)
- AWS SageMaker (managed ML deployment)
- GCP Vertex AI (managed ML deployment)
- Azure ML (managed ML deployment)

**CI/CD:**
- GitHub Actions, GitLab CI, Jenkins
- ArgoCD (GitOps for Kubernetes)
- Spinnaker (multi-cloud CD)

**Observability:**
- Prometheus + Grafana (metrics + dashboards)
- Datadog, New Relic (APM)
- OpenTelemetry (tracing)

---

## Related Resources

- [Deployment Patterns](deployment-patterns.md) - Batch, online, hybrid deployment modes
- [Monitoring Best Practices](monitoring-best-practices.md) - Observability strategies
- [API Design Patterns](api-design-patterns.md) - Real-time API serving
- [Drift Detection Guide](drift-detection-guide.md) - Automated retraining triggers
- [Model Registry Patterns](model-registry-patterns.md) - Versioning and promotion workflows

---

## References

- **MLOps Principles:** https://ml-ops.org/
- **Google MLOps Maturity Model:** https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
- **MLflow Documentation:** https://mlflow.org/docs/latest/model-registry.html
- **Kubernetes Best Practices:** https://kubernetes.io/docs/concepts/cluster-administration/manage-deployment/
