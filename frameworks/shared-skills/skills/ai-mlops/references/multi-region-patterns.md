# Multi-Region, Data Residency & Rollback Patterns

Operational patterns for deploying ML systems across regions, managing data residency requirements, ensuring consistency, and implementing reliable rollback procedures.

---

## Overview

Modern ML systems often require **multi-region deployment** for low latency, high availability, and regulatory compliance. This guide covers patterns for cross-region deployment, data residency, disaster recovery, and rollback strategies.

**Key Topics:**
- Multi-region deployment architectures
- Data residency and tenant isolation
- Cross-region consistency and rollback
- Disaster recovery and failover
- Change management and auditing

---

## Pattern 1: Multi-Region Deployment

### Use Cases

**1. Low latency for global users**
- Serve users from nearest region (US, EU, APAC)
- Reduce latency by 50-80%

**2. High availability**
- Failover to secondary region if primary fails
- 99.99% uptime SLA

**3. Regulatory compliance**
- EU users' data stays in EU (GDPR)
- Chinese users' data stays in China (Cybersecurity Law)

### Architecture Patterns

**Pattern A: Regional Replicas (Active-Active)**

```
        Global Load Balancer
              │
      ┌───────┼───────┐
      │       │       │
   US-East  EU-West  APAC
    Model    Model    Model
      │       │       │
   US Data  EU Data  APAC Data
```

**Characteristics:**
- Each region has its own model deployment
- Traffic routed to nearest region
- Data isolated per region
- Models trained separately or replicated

**Checklist:**
- [ ] Regional model deployments configured
- [ ] Global load balancer routes by geography
- [ ] Data isolated per region (no cross-region access)
- [ ] Models synchronized across regions (if shared)

**Pattern B: Primary-Secondary (Active-Passive)**

```
    Global Load Balancer
         │
    ┌────┴────┐
    │         │ (failover only)
  Primary   Secondary
  (US-East) (EU-West)
```

**Characteristics:**
- Primary region serves all traffic
- Secondary region warm standby (ready for failover)
- Automatic failover if primary unhealthy

**Checklist:**
- [ ] Primary region handles all traffic
- [ ] Secondary region warm and ready
- [ ] Health checks trigger automatic failover
- [ ] Failover tested quarterly

---

## Pattern 2: Data Residency & Tenant Isolation

### Regulatory Requirements

**GDPR (EU):**
- Personal data of EU citizens must be processed in EU
- Data transfers outside EU require safeguards

**CCPA (California):**
- Consumers have right to know where data is stored

**China Cybersecurity Law:**
- Personal data collected in China must stay in China

### Implementation: Regional Data Segmentation

**1. Segment data by region**

```python
def get_data_region(user_id):
    """Determine data region based on user location."""
    user = db.get_user(user_id)

    if user.country in ['FR', 'DE', 'IT', 'ES']:
        return 'eu-west'
    elif user.country in ['CN']:
        return 'apac-china'
    elif user.country in ['US', 'CA']:
        return 'us-east'
    else:
        return 'us-east'  # Default
```

**2. Route requests to correct region**

```python
@app.post("/predict")
def predict(user_id: str, features: dict):
    """Route prediction to user's region."""
    region = get_data_region(user_id)

    # Call regional model API
    regional_api = f"https://model-{region}.company.com/predict"
    response = requests.post(regional_api, json=features)

    return response.json()
```

**3. Isolate feature stores and data by region**

```
Feature Stores (isolated):
- feature-store-us-east
- feature-store-eu-west
- feature-store-apac-china

Warehouses (isolated):
- warehouse-us-east
- warehouse-eu-west
- warehouse-apac-china
```

**4. Separate model registries per region**

```
Model Registries:
- mlflow-us-east (US models)
- mlflow-eu-west (EU models)
- mlflow-apac-china (China models)
```

### Checklist

- [ ] User data segmented by region
- [ ] Regional routing enforced (no cross-region data access)
- [ ] Feature stores isolated per region
- [ ] Model registries isolated per region
- [ ] Compliance requirements documented
- [ ] Data residency audits run regularly

---

## Pattern 3: Cross-Region Consistency & Versioning

### Challenge

**Consistency:** Ensure same model version deployed across all regions
**Versioning:** Track which version is live in each region
**Rollback:** Ability to rollback one region without affecting others

### Solution: Versioned Artifacts with Registry

**1. Central model registry (metadata only)**

```json
{
  "model_id": "fraud_detection_v42",
  "artifact_uri": "s3://models-global/fraud/v42/model.pkl",
  "deployments": {
    "us-east": {
      "version": "v42",
      "deployed_at": "2025-03-15T10:00:00Z",
      "status": "active"
    },
    "eu-west": {
      "version": "v42",
      "deployed_at": "2025-03-15T10:05:00Z",
      "status": "active"
    },
    "apac": {
      "version": "v41",  # Still on old version
      "deployed_at": "2025-03-10T12:00:00Z",
      "status": "active"
    }
  }
}
```

**2. Promotion workflow (region-by-region)**

```
1. Deploy to us-east (primary)
2. Monitor for 24 hours
3. If stable, deploy to eu-west
4. Monitor for 24 hours
5. If stable, deploy to apac
```

**3. Regional rollback capability**

```bash
# Rollback EU region only (US and APAC unaffected)
$ deploy-cli rollback --region=eu-west --version=v41

# Rollback all regions
$ deploy-cli rollback --all-regions --version=v41
```

### Atomic Promotion Pattern

**Dual-read during migrations:**
```python
def get_features(user_id, feature_version='v2'):
    """Dual-read during feature migration."""

    if feature_version == 'v2':
        features = feature_store_v2.get(user_id)
    else:
        # Fallback to v1 during migration
        features = feature_store_v1.get(user_id)

    return features
```

**Versioned feature views:**
```python
# Old feature view (v1)
user_features_v1 = FeatureView(
    name="user_stats_v1",
    entities=[user],
    schema=[Feature("total_purchases", Int64)]
)

# New feature view (v2, added avg_order_value)
user_features_v2 = FeatureView(
    name="user_stats_v2",
    entities=[user],
    schema=[
        Feature("total_purchases", Int64),
        Feature("avg_order_value", Float32)  # New
    ]
)
```

### Checklist

- [ ] Model registry tracks versions per region
- [ ] Regional deployments staggered (not simultaneous)
- [ ] Rollback procedure tested per region
- [ ] Versioned artifacts stored with unique IDs
- [ ] Dual-read capability during migrations
- [ ] Promotion workflow documented

---

## Pattern 4: Disaster Recovery & Failover

### DR Strategies

**1. Backup and restore**
- Regularly backup models, data, feature stores
- Test restore procedure quarterly
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour

**2. Warm standby**
- Secondary region running with minimal traffic
- Promote to primary if primary fails
- RTO: 5 minutes
- RPO: Near-zero

**3. Active-active (multi-region)**
- All regions serve traffic simultaneously
- No failover needed (traffic automatically rerouted)
- RTO: 0 (automatic)
- RPO: 0

### Failover Triggers

**Health checks:**
- Endpoint responding within SLA (<500ms)
- Error rate < 1%
- Model predictions reasonable (not all zeros)

**Automated failover:**
```yaml
# healthcheck.yaml
health_checks:
  - name: endpoint_latency
    threshold: 500ms
    action: failover_if_exceeded_for_5min

  - name: error_rate
    threshold: 1%
    action: failover_if_exceeded_for_2min

  - name: prediction_sanity
    threshold: 90% predictions are non-zero
    action: failover_if_failed
```

**Circuit breaker pattern:**
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_primary_region(features):
    """Call primary region with circuit breaker."""
    response = requests.post(PRIMARY_API, json=features)
    response.raise_for_status()
    return response.json()

def predict_with_failover(features):
    """Predict with automatic failover."""
    try:
        return call_primary_region(features)
    except CircuitBreakerError:
        # Circuit open, failover to secondary
        log_warning("Primary region unhealthy, using secondary")
        return call_secondary_region(features)
```

### DR Runbook

**Scenario: Primary region (US-East) failure**

**1. Detection (< 1 minute)**
- Health checks fail
- Alerts fire
- On-call paged

**2. Diagnosis (2-5 minutes)**
- Check dashboards (latency, errors, traffic)
- Check upstream dependencies (data sources, feature store)
- Determine if regional issue or service issue

**3. Failover (5 minutes)**
- Route all traffic to EU-West (secondary)
- Validate EU-West handling traffic
- Monitor latency and errors

**4. Incident response**
- Investigate root cause of primary failure
- Fix primary region
- Validate in staging
- Failback to primary when stable

**5. Post-mortem**
- Document timeline and root cause
- Identify preventive actions
- Update runbook

### Checklist

- [ ] Backups scheduled and tested
- [ ] Warm standby region ready
- [ ] Health checks configured
- [ ] Automated failover tested
- [ ] Circuit breakers in place
- [ ] DR runbook documented and rehearsed
- [ ] RTO/RPO targets defined and measured

---

## Pattern 5: Change Management & Auditing

### Change Control

**1. Who can promote models?**
- Data scientists: Promote to staging
- ML engineers: Promote to production
- VP approval: Required for high-risk models

**2. When are promotions allowed?**
- Business hours only (9 AM - 5 PM)
- No promotions during holidays or blackout periods
- Freeze period before major events

**3. Audit log every promotion**

```json
{
  "promotion_id": "promo_12345",
  "model_id": "fraud_detection_v42",
  "promoted_by": "engineer@company.com",
  "promoted_at": "2025-03-15T10:00:00Z",
  "from_stage": "staging",
  "to_stage": "production",
  "region": "us-east",
  "approval_id": "approve_67890",
  "approved_by": "manager@company.com"
}
```

**4. Canary/shadow for infrastructure changes**

**Canary deployment for registry changes:**
```bash
# Deploy new feature store version to 10% traffic
$ deploy-cli canary --feature-store=v2 --traffic=10%

# Monitor for 1 hour
# If stable, expand to 50%
$ deploy-cli canary --feature-store=v2 --traffic=50%

# If stable, expand to 100%
$ deploy-cli canary --feature-store=v2 --traffic=100%
```

**Shadow deployment for index changes:**
```python
def query_with_shadow(query, use_shadow=True):
    """Query new index in shadow mode."""

    # Query production index
    prod_results = vector_db_prod.search(query)

    if use_shadow:
        # Query new index (shadow)
        shadow_results = vector_db_shadow.search(query)

        # Log comparison
        log_comparison(prod_results, shadow_results)

    return prod_results  # Serve production results
```

### Approval Workflow

```
1. Engineer submits promotion request
   ├─> Automated checks (tests, metrics)
   └─> If pass, request manager approval

2. Manager reviews evaluation report
   ├─> Check metrics improvement
   ├─> Check risk assessment
   └─> Approve or reject

3. If approved, deploy with canary
   ├─> 10% traffic for 1 hour
   ├─> 50% traffic for 4 hours
   └─> 100% traffic if stable

4. Log promotion in audit log
```

### Checklist

- [ ] Promotion permissions enforced (RBAC)
- [ ] Approval workflow for production deployments
- [ ] All promotions logged with user ID and timestamp
- [ ] Canary/shadow for infrastructure changes
- [ ] Change freeze periods defined
- [ ] Audit logs queryable for compliance

---

## Pattern 6: Rollback Procedures

### When to Rollback

**Automatic rollback triggers:**
- Error rate > 5%
- Latency > 2x baseline
- Prediction quality drop > 10%
- Safety incidents > threshold

**Manual rollback scenarios:**
- Business KPIs declining
- Customer complaints
- Unexpected behavior
- Regulatory violation

### Rollback Strategies

**1. Instant rollback (traffic switch)**

```bash
# Switch traffic back to previous version
$ deploy-cli rollback --region=us-east --version=v41

# Traffic now served by v41 (previous version)
```

**2. Blue-green rollback**

```bash
# Swap blue and green environments
$ deploy-cli swap-environments --blue=v42 --green=v41

# All traffic now on v41 (green)
```

**3. Feature flag rollback**

```python
# Feature flag controls which model version
if feature_flags.get('use_model_v42'):
    model = load_model('v42')
else:
    model = load_model('v41')  # Rolled back

# Toggle flag without redeployment
feature_flags.set('use_model_v42', False)
```

### Rollback Validation

**Post-rollback checks:**
```python
def validate_rollback(region, expected_version):
    """Validate rollback succeeded."""

    # Check model version
    deployed_version = get_deployed_version(region)
    assert deployed_version == expected_version

    # Check metrics returned to baseline
    error_rate = get_error_rate(region)
    assert error_rate < 1%

    latency_p99 = get_latency_p99(region)
    assert latency_p99 < 500

    log_info(f"Rollback validated for {region}")
```

### Rollback Checklist

- [ ] Previous version available (not deleted)
- [ ] Rollback procedure documented
- [ ] Rollback tested in staging
- [ ] Rollback can be executed in < 5 minutes
- [ ] Post-rollback validation automated
- [ ] Rollback events logged and reviewed

---

## Real-World Example: Fraud Detection Multi-Region

### Context

**Regions:** US-East (primary), EU-West (secondary), APAC
**Model:** Fraud detection (binary classifier)
**Data residency:** EU users' data stays in EU

### Architecture

```
Global Load Balancer (geo-routing)
    │
    ├─> US-East (Primary)
    │     ├─> Model v42
    │     ├─> Feature Store (US data)
    │     └─> Model Registry (US)
    │
    ├─> EU-West (Secondary + EU users)
    │     ├─> Model v42
    │     ├─> Feature Store (EU data)
    │     └─> Model Registry (EU)
    │
    └─> APAC
          ├─> Model v41 (not yet upgraded)
          ├─> Feature Store (APAC data)
          └─> Model Registry (APAC)
```

### Deployment Workflow

**1. Deploy v42 to US-East:**
- Canary: 10% → 50% → 100% over 24 hours
- Monitored: Latency, error rate, fraud detection rate

**2. Deploy v42 to EU-West:**
- Wait 48 hours after US-East stable
- Canary: 10% → 50% → 100% over 24 hours

**3. Deploy v42 to APAC:**
- Wait 48 hours after EU-West stable
- Canary: 10% → 50% → 100% over 24 hours

### Incident: US-East Failure

**Timeline:**
- **10:00 AM:** Health checks fail (error rate 12%)
- **10:01 AM:** Automated failover to EU-West
- **10:02 AM:** US traffic now served by EU-West
- **10:05 AM:** EU latency spike (P99 = 800ms) due to increased load
- **10:10 AM:** Scaled EU-West from 10 → 20 pods
- **10:15 AM:** EU latency normalized (P99 = 450ms)
- **11:30 AM:** Root cause identified (data pipeline failure in US)
- **12:00 PM:** US-East pipeline fixed and redeployed
- **12:30 PM:** US-East validated in staging
- **1:00 PM:** Failback to US-East (gradual)

**Outcome:**
- RTO: 1 minute (automated failover)
- RPO: 0 (no data loss)
- User impact: 15 minutes elevated latency

---

## Tools & Frameworks

**Multi-region deployment:**
- **AWS Global Accelerator** (geo-routing, failover)
- **GCP Cloud Load Balancing** (global load balancing)
- **Cloudflare** (edge routing, DDoS protection)

**Model registries (multi-region):**
- **MLflow** (can sync across regions)
- **Weights & Biases** (cloud-based, global)
- **DVC** (Git-like versioning, regional S3 buckets)

**Disaster recovery:**
- **Terraform** (infrastructure as code, reproducible)
- **AWS Backup** (automated backups)
- **GCP Backup & DR** (managed backups)

**Circuit breakers:**
- **Resilience4j** (Java)
- **Hystrix** (Netflix, deprecated but influential)
- **python-circuitbreaker** (Python)

---

## Related Resources

- [Deployment Lifecycle](deployment-lifecycle.md) - Model deployment process
- [Monitoring Best Practices](monitoring-best-practices.md) - Health checks and alerting
- [Incident Response Playbooks](incident-response-playbooks.md) - Runbooks for failures
- [Model Registry Patterns](model-registry-patterns.md) - Versioning and promotion

---

## References

- **AWS Multi-Region Best Practices:** https://aws.amazon.com/blogs/architecture/disaster-recovery-dr-architecture-on-aws-part-i-strategies-for-recovery-in-the-cloud/
- **GCP Global Load Balancing:** https://cloud.google.com/load-balancing/docs/https
- **GDPR Data Residency:** https://gdpr.eu/data-residency/
- **Circuit Breaker Pattern:** https://martinfowler.com/bliki/CircuitBreaker.html
