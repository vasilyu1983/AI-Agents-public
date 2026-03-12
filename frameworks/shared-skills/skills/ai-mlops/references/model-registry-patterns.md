# Model Registry Patterns

Comprehensive patterns for versioning, packaging, and promoting ML models through the production lifecycle with reproducibility and governance.

---

## Overview

A **model registry** is the central source of truth for all production ML models. It stores model artifacts, metadata, lineage, and lifecycle state, enabling reproducible deployments and auditable governance.

**Key Topics:**
- Model registry structure and metadata
- Packaging models for portability
- Promotion flows (experimental → production)
- Versioning strategies
- Lineage tracking
- Governance and compliance

---

## Pattern 1: Model Registry Structure

### Core Components

**1. Model artifact**
- Binary/serialized model (pickle, joblib, ONNX, TorchScript, SavedModel, checkpoint)
- Model format depends on framework (scikit-learn, PyTorch, TensorFlow, XGBoost, LLM)

**2. Metadata**
- Version identifier (semantic versioning or auto-incremented)
- Git commit hash for training code
- Training data snapshot ID or lineage pointer
- Hyperparameters and configuration
- Metrics summary (train/val/test performance)
- Owner and contact information
- Creation timestamp

**3. Evaluation report**
- Full metrics breakdown (accuracy, precision, recall, AUC, etc.)
- Confusion matrix or performance curves
- Slice analysis (performance by demographic, region, etc.)
- Comparison to baseline or previous version
- Test set details (size, distribution, sampling method)

**4. Dependencies and environment**
- Python/framework version
- Library dependencies with pinned versions
- System dependencies (CUDA, cuDNN)
- Dockerfile or conda environment spec

**5. Lifecycle stage**
- `experimental`: Early development, not validated
- `candidate`: Ready for staging validation
- `staging`: Deployed to staging environment
- `production`: Serving live traffic
- `archived`: Retired, kept for compliance

### Example Registry Entry

```json
{
  "model_id": "fraud_detection_v42",
  "artifact_uri": "s3://models/fraud/v42/model.pkl",
  "version": "42",
  "stage": "production",
  "metadata": {
    "framework": "scikit-learn",
    "algorithm": "XGBClassifier",
    "training_code_commit": "abc123",
    "training_data_snapshot": "transactions_2024_Q4_v2",
    "hyperparameters": {
      "max_depth": 8,
      "learning_rate": 0.1,
      "n_estimators": 200
    },
    "metrics": {
      "auc": 0.94,
      "precision": 0.89,
      "recall": 0.87,
      "f1": 0.88
    },
    "owner": "ml-platform-team@company.com",
    "created_at": "2025-03-15T10:30:00Z"
  },
  "evaluation_report_uri": "s3://reports/fraud/v42/eval.html",
  "environment": {
    "python_version": "3.11",
    "dependencies": "requirements.txt",
    "dockerfile": "Dockerfile"
  },
  "tags": ["production", "fraud", "xgboost"]
}
```

---

## Pattern 2: Model Packaging

### Packaging Goals

**Portability:** Model runs identically across dev, staging, prod
**Reproducibility:** Same inputs → same outputs
**Isolation:** No dependency conflicts with other models

### Packaging Strategies

**1. Containerization (Docker)**

**Advantages:**
- Fully isolated environment
- Reproducible across platforms
- Easy deployment to Kubernetes, cloud services
- Includes system dependencies (CUDA, libraries)

**Structure:**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y libgomp1

# Copy model artifact and dependencies
COPY model.pkl /app/model.pkl
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy inference code
COPY inference.py /app/inference.py

# Set entrypoint
CMD ["python", "/app/inference.py"]
```

**Checklist:**
- [ ] Dockerfile builds successfully
- [ ] Model artifact embedded or mounted
- [ ] Dependencies pinned (requirements.txt with versions)
- [ ] Entrypoint defined (API server or batch script)
- [ ] Image tagged with version

**2. Environment Specification (conda, venv)**

**Advantages:**
- Lightweight (no container overhead)
- Fast iteration during development
- Easy to share and reproduce

**Structure:**
```yaml
# environment.yml
name: fraud-model-v42
channels:
  - conda-forge
dependencies:
  - python=3.11
  - scikit-learn=1.3.0
  - xgboost=2.0.0
  - pandas=2.1.0
  - numpy=1.25.0
```

**Checklist:**
- [ ] Environment file includes all dependencies
- [ ] Versions pinned for reproducibility
- [ ] Environment tested on clean machine
- [ ] Activation instructions documented

**3. Model Format Standardization (ONNX, MLflow)**

**ONNX (Open Neural Network Exchange):**
- Framework-agnostic model format
- Optimized for inference
- Portable across languages (Python, C++, Java)

**MLflow Models:**
- Unified model packaging format
- Includes preprocessing/postprocessing code
- Built-in deployment integrations

**Checklist:**
- [ ] Model exported to standardized format
- [ ] Format validated (loads and predicts correctly)
- [ ] Preprocessing/postprocessing embedded
- [ ] Deployment target supports format

---

### Preprocessing and Postprocessing Code

**Include with model:**
- Feature engineering transformations
- Input validation and cleaning
- Output formatting and thresholds
- Business logic (e.g., minimum score to approve)

**Best practices:**
- Package preprocessing as part of model artifact (not separate service)
- Use same code for training and inference
- Version preprocessing code with model
- Avoid external dependencies (embed scalers, encoders)

**Example:**

```python
# preprocessing.py (embedded with model)
import pickle
import pandas as pd

def preprocess(raw_input):
    """Apply same transformations as training."""
    df = pd.DataFrame([raw_input])

    # Load fitted transformers (saved during training)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)

    # Apply transformations
    df['amount_scaled'] = scaler.transform(df[['amount']])
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour

    return df[['amount_scaled', 'hour', 'merchant_id']]

def postprocess(model_output):
    """Convert model scores to business decision."""
    return {
        'prediction': 'fraud' if model_output > 0.5 else 'legitimate',
        'score': float(model_output),
        'confidence': 'high' if abs(model_output - 0.5) > 0.3 else 'medium'
    }
```

---

## Pattern 3: Promotion Flow

### Stage Progression

```
experimental → candidate → staging → production → archived
```

### Stage Definitions

**Experimental:**
- Early-stage development
- Not validated on hold-out data
- No production readiness guarantees

**Candidate:**
- Validated on hold-out data
- Metrics meet acceptance criteria
- Ready for staging deployment

**Staging:**
- Deployed to staging environment
- Integration tests passing
- Performance validated on production-like data

**Production:**
- Serving live traffic
- Monitored continuously
- SLAs enforced

**Archived:**
- Retired from active use
- Retained for compliance or rollback
- Not receiving updates

### Promotion Criteria

**Experimental → Candidate:**
- [ ] Hold-out metrics meet threshold (e.g., AUC > 0.90)
- [ ] No data leakage detected
- [ ] Training reproducible
- [ ] Code review completed

**Candidate → Staging:**
- [ ] Packaging complete (Docker image or environment)
- [ ] Deployment plan approved
- [ ] Rollback procedure documented

**Staging → Production:**
- [ ] Integration tests passing
- [ ] Shadow validation passed (if applicable)
- [ ] Latency within SLO
- [ ] Stakeholder sign-off

**Production → Archived:**
- [ ] New version promoted to production
- [ ] Grace period elapsed (e.g., 30 days)
- [ ] Compliance retention period defined

### Promotion Workflow

**1. Request promotion**
- Submit promotion request with justification
- Include evaluation report and comparison to current production

**2. Automated checks**
- Verify all artifacts present
- Check metrics meet thresholds
- Validate environment reproducibility

**3. Manual approval**
- Stakeholder review (data scientists, engineers, product)
- Risk assessment for high-impact models
- Compliance approval for regulated domains

**4. Execute promotion**
- Update registry stage
- Trigger deployment pipeline
- Monitor post-deployment metrics

**5. Document decision**
- Log who/when/why promoted
- Link to evaluation report
- Record baseline metrics for comparison

---

## Pattern 4: Versioning Strategies

### Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH` (e.g., `2.3.1`)

**Rules:**
- **MAJOR:** Breaking changes (schema change, algorithm change)
- **MINOR:** Backwards-compatible improvements (retraining with more data)
- **PATCH:** Bug fixes, no model retraining

**Example:**
- `1.0.0`: Initial production model
- `1.1.0`: Retrained with Q4 data (same features)
- `1.2.0`: Added new feature (still backwards-compatible)
- `2.0.0`: Changed schema (removed deprecated field)

### Auto-Incremented Versioning

**Format:** Integer version (e.g., `v42`)

**Rules:**
- Increment on every model registration
- No semantic meaning
- Simpler for high-frequency retraining

**Example:**
- `v1`: Initial model
- `v2`: Retraining with new data
- `v3`: Bug fix
- `v42`: Latest production version

### Git Commit-Based Versioning

**Format:** Git commit hash (e.g., `abc123`)

**Rules:**
- Model version = training code commit hash
- Enables exact reproducibility
- Links model to code changes

**Best practices:**
- Combine with semantic version for clarity (`v2.3.1-abc123`)
- Tag git commits for major releases

---

## Pattern 5: Lineage Tracking

### What to Track

**Upstream lineage (inputs to model):**
- Training data snapshot ID
- Feature definitions and versions
- Preprocessing transformations
- Data sources (tables, APIs, files)

**Downstream lineage (outputs from model):**
- Which services consume predictions
- Which dashboards/reports use model metrics
- Which business processes depend on model

**Model lineage:**
- Parent model (if fine-tuned or retrained)
- Training run ID and hyperparameters
- Evaluation datasets

### Example Lineage Graph

```
Raw Data (user_transactions_v2)
  ├─> Feature Engineering (features_v3.2)
  │     ├─> Model Training (fraud_model_v42)
  │           ├─> Production API (fraud-detection-api)
  │           ├─> Batch Scoring (nightly_fraud_scores)
  │           └─> Dashboard (fraud_metrics_dashboard)
```

### Checklist

- [ ] Training data snapshot ID recorded
- [ ] Feature definitions versioned
- [ ] Model registry links to training run
- [ ] Downstream consumers documented
- [ ] Lineage queryable via catalog or API

---

## Pattern 6: Governance and Compliance

### Model Registry as Audit Trail

**What to log:**
- Who registered the model
- Who approved promotion
- When model was deployed/retired
- Why model was promoted/demoted
- What data was used for training

**Use cases:**
- Regulatory compliance (GDPR, CCPA, banking regulations)
- Debugging: "Which model version was live on date X?"
- Rollback: "What was the previous production version?"
- Attribution: "Who owns this model?"

### Compliance Features

**Access control:**
- Role-based permissions (who can register/promote models)
- Audit logs for all actions
- Approval workflows for regulated models

**Data governance:**
- Track PII usage in training data
- Document data retention policies
- Link to data lineage for GDPR right-to-explanation

**Model risk management:**
- Document model purpose and scope
- Track validation and back-testing
- Monitor for bias and fairness violations

**Checklist:**
- [ ] Access control enforced (RBAC)
- [ ] All actions logged with user ID and timestamp
- [ ] Approval workflows for regulated models
- [ ] PII usage documented
- [ ] Compliance retention periods configured

---

## Pattern 7: Multi-Registry Strategy

### When to Use Multiple Registries

**Scenario 1: Multi-cloud deployment**
- Models deployed to AWS, GCP, Azure
- Each cloud has its own registry
- Sync metadata across registries

**Scenario 2: Regional/tenant isolation**
- Different models per region or customer
- Isolate for compliance (GDPR, data residency)
- Federated registry with regional shards

**Scenario 3: Environment separation**
- Dev registry for experiments
- Staging registry for candidates
- Prod registry for production models

### Synchronization Strategies

**Replicate metadata:**
- Use central metadata store (database, API)
- Sync to regional registries
- Eventual consistency acceptable

**Promotion across registries:**
- Promote from dev registry → staging registry → prod registry
- Artifact copied between registries
- Versioning consistent across registries

**Checklist:**
- [ ] Registry per environment or region defined
- [ ] Synchronization mechanism implemented
- [ ] Version consistency enforced
- [ ] Artifact replication tested

---

## Tools & Frameworks

**Model registries:**
- **MLflow Model Registry** (open-source, popular)
- **Weights & Biases** (experiment tracking + registry)
- **DVC** (Git-like versioning for data and models)
- **Vertex AI Model Registry** (GCP managed)
- **SageMaker Model Registry** (AWS managed)
- **Azure ML Model Registry** (Azure managed)

**Packaging tools:**
- **Docker** (containerization)
- **MLflow Models** (unified packaging format)
- **ONNX** (framework-agnostic model format)
- **BentoML** (model serving framework with packaging)

**Lineage tracking:**
- **MLflow** (built-in lineage for experiments)
- **DVC** (data and model versioning with lineage)
- **Neptune.ai** (experiment tracking with lineage graphs)
- **Pachyderm** (data versioning and lineage)

---

## Real-World Example: Recommendation Model Registry

### Context

**Model:** Product recommendation model (collaborative filtering)
**Framework:** PyTorch
**Deployment:** Kubernetes
**Registry:** MLflow

### Registry Structure

```json
{
  "model_id": "product_recommendations_v15",
  "artifact_uri": "s3://models/recommendations/v15/model.pt",
  "version": "15",
  "stage": "production",
  "metadata": {
    "framework": "pytorch",
    "architecture": "two_tower",
    "training_code_commit": "def456",
    "training_data_snapshot": "user_interactions_2024_Q1",
    "hyperparameters": {
      "embedding_dim": 128,
      "learning_rate": 0.001,
      "batch_size": 512
    },
    "metrics": {
      "ndcg@10": 0.42,
      "recall@10": 0.31,
      "diversity": 0.68
    },
    "owner": "recommendations-team@company.com",
    "created_at": "2025-02-10T14:20:00Z"
  },
  "environment": {
    "python_version": "3.11",
    "torch_version": "2.1.0",
    "cuda_version": "12.1",
    "dockerfile": "Dockerfile.recommendations"
  }
}
```

### Packaging

**Dockerfile:**
```dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

COPY model.pt /app/model.pt
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY inference.py /app/inference.py
CMD ["python", "/app/inference.py"]
```

**Inference code:**
```python
# inference.py
import torch
from model import TwoTowerModel

model = TwoTowerModel.load('/app/model.pt')
model.eval()

def predict(user_id, candidate_items):
    """Return top-10 recommendations."""
    with torch.no_grad():
        scores = model(user_id, candidate_items)
    return torch.topk(scores, k=10).indices.tolist()
```

### Promotion Flow

**v14 → v15 promotion:**
1. **Validation:**
   - NDCG@10 improved from 0.39 to 0.42 (+7.7%)
   - Diversity maintained (0.68 vs 0.67)
   - Latency: P99 = 120ms (within SLO of 150ms)

2. **Approval:**
   - Data science team approved (metrics improvement)
   - Engineering team approved (latency acceptable)
   - Product team approved (A/B test showed +2% CTR)

3. **Deployment:**
   - Canary rollout: 10% → 50% → 100% over 48 hours
   - Monitored CTR, diversity, latency at each stage
   - No rollback needed

4. **Documentation:**
   - Promotion logged in registry with timestamp
   - A/B test report linked
   - Previous version (v14) moved to `archived` after 30 days

---

## Related Resources

- [Deployment Lifecycle](deployment-lifecycle.md) - End-to-end deployment process
- [Deployment Patterns](deployment-patterns.md) - Batch, online, hybrid serving
- [Data Ingestion Patterns](data-ingestion-patterns.md) - Lineage tracking for data
- [Monitoring Best Practices](monitoring-best-practices.md) - Observability for models
- [Drift Detection Guide](drift-detection-guide.md) - Automated retraining triggers

---

## References

- **MLflow Model Registry:** https://mlflow.org/docs/latest/model-registry.html
- **Weights & Biases:** https://docs.wandb.ai/guides/models
- **ONNX Documentation:** https://onnx.ai/
- **DVC for Model Versioning:** https://dvc.org/doc/use-cases/versioning-data-and-models
- **BentoML:** https://docs.bentoml.org/
