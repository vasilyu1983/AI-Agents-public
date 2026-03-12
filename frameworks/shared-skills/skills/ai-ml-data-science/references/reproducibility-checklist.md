# Reproducibility Checklist

Ensuring ML experiments are reproducible, trackable, and production-ready with modern MLOps practices (CI/CD, CT, CM).

---

## 1. Experiment Tracking & Versioning

### 1.1 What to Track

**Every training run must log:**

- **Code version**: Git commit hash
- **Data version**: Dataset snapshot ID or hash
- **Feature set version**: From feature store
- **Hyperparameters**: All model and training config
- **Random seeds**: For reproducibility
- **Metrics**: Primary and guardrail metrics
- **Artifacts**: Model weights, preprocessors, encoders
- **Drift statistics**: Distribution comparison vs training data

### 1.2 Experiment Tracking Tools

**MLflow:**
- Open-source, self-hosted
- Experiment tracking + model registry
- Integrates with popular frameworks

**Weights & Biases (W&B):**
- Cloud-hosted, polished UI
- Real-time metrics visualization
- Sweep/hyperparameter optimization

**Neptune:**
- Metadata store for ML
- Advanced experiment comparison
- Team collaboration features

**DVC (Data Version Control):**
- Git for data
- Pipeline tracking
- Reproducible experiments

**Checklist: Experiment Tracking**

- [ ] Experiments logged with code + data + params + feature version
- [ ] Best runs easily identifiable with tagged metrics
- [ ] Re-running yields same metrics within noise
- [ ] Model registry entry created for candidate models
- [ ] Drift statistics logged for production monitoring

---

## 2. Modern MLOps Integration (CI/CD/CT/CM)

### 2.1 Continuous Integration (CI)

**Automated testing and validation:**
- Unit tests for data preprocessing and feature engineering
- Integration tests for training pipeline
- Code quality checks (linting, type checking)
- Data validation (schema checks, distribution tests)

**Tools:**
- GitHub Actions, GitLab CI, Jenkins
- Great Expectations (data validation)
- pytest, unittest

### 2.2 Continuous Delivery (CD)

**Automated deployment:**
- Environment-specific model promotion (dev -> staging -> prod)
- Automated model packaging (Docker, model serving format)
- Canary deployment with gradual rollout
- Rollback on regression

**Tools:**
- Kubernetes, Docker
- MLflow Model Registry
- BentoML, Seldon, KServe

### 2.3 Continuous Training (CT)

**Automated retraining:**
- Triggered by drift detection (data or performance)
- Scheduled retraining (weekly, monthly)
- New data availability triggers
- Automated evaluation and promotion

**Triggers:**
- Drift exceeds threshold (PSI, KL divergence)
- Performance degradation (accuracy drop > 5%)
- Calendar schedule (monthly refresh)
- Manual trigger (emergency retrain)

### 2.4 Continuous Monitoring (CM)

**Real-time production monitoring:**
- Data drift (input distribution changes)
- Concept drift (target distribution changes)
- Model performance (accuracy, latency, errors)
- System health (CPU, memory, throughput)

**Metrics:**
- **Data drift**: KL divergence, PSI, KS test
- **Performance**: Online accuracy, solve rate, calibration
- **Operational**: Latency (p50, p95, p99), error rate, cost

**Checklist: MLOps Integration**

- [ ] CI/CD pipeline integrated for automated testing
- [ ] CT configured with drift-based and scheduled triggers
- [ ] CM dashboards active with drift and performance metrics
- [ ] Automated retraining and promotion workflow tested
- [ ] Rollback procedure documented and tested

---

## 3. Environment & Dependency Management

### 3.1 Python Environment

**Requirements:**
- Python version pinned (e.g., 3.10.12)
- Package versions locked (requirements.txt, poetry.lock, Pipfile.lock)
- Virtual environment (venv, conda, poetry)

**Best practices:**
- Use `pip freeze > requirements.txt` or poetry
- Pin all dependencies, including transitive ones
- Test installation on clean environment

### 3.2 System Dependencies

**Document:**
- Operating system (Ubuntu 22.04, macOS 14.2)
- CUDA version (for GPU training)
- System libraries (libgeos, GDAL, etc.)
- Hardware requirements (CPU cores, RAM, GPU)

### 3.3 Docker for Reproducibility

**Benefits:**
- Complete environment specification
- Portable across machines
- Consistent training and serving

**Example Dockerfile:**
```dockerfile
FROM python:3.10.12-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "train.py"]
```

**Checklist: Environment Pinned**

- [ ] Python version documented and pinned
- [ ] All package versions locked (requirements.txt or equivalent)
- [ ] System dependencies documented
- [ ] Docker image built and tested (if applicable)
- [ ] Environment reproducible on fresh machine

---

## 4. Data Versioning

### 4.1 What to Version

**Datasets:**
- Training, validation, test splits
- Raw data snapshots (before preprocessing)
- Processed features (after transformations)
- Data lineage (source -> intermediate -> final)

**Metadata:**
- Extraction timestamp
- Data quality metrics (nulls, outliers, distribution)
- Sampling strategy
- Label quality (inter-annotator agreement)

### 4.2 Data Versioning Tools

**DVC (Data Version Control):**
- Git-like interface for data
- Store data in S3, GCS, Azure Blob
- Track data lineage and pipelines

**LakeFS:**
- Git for data lakes
- Branching and merging for datasets
- Time-travel queries

**Feature stores:**
- Feast, Tecton, Databricks Feature Store
- Centralized feature management
- Version features alongside models

**Checklist: Data Versioned**

- [ ] Dataset snapshots tracked with version IDs
- [ ] Train/validation/test splits documented and versioned
- [ ] Data lineage captured (source -> transformations -> features)
- [ ] Metadata logged (quality metrics, extraction time)
- [ ] Feature store used for centralized versioning (if applicable)

---

## 5. Random Seed Management

### 5.1 Sources of Randomness

**Control seeds for:**
- NumPy (`np.random.seed()`)
- Python random (`random.seed()`)
- Model libraries (LightGBM, XGBoost, PyTorch, TensorFlow)
- Data sampling and train/test splits
- Data augmentation

### 5.2 Setting Seeds

**Example (Python):**
```python
import random
import numpy as np
import torch

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    # For deterministic behavior (slower)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

**LightGBM/XGBoost:**
```python
params = {
    'seed': 42,
    'feature_fraction_seed': 42,
    'bagging_seed': 42
}
```

**Checklist: Randomness Controlled**

- [ ] All random seeds set at script start
- [ ] Seeds logged in experiment tracker
- [ ] Multiple seed runs for stability (5-10 seeds)
- [ ] Deterministic behavior verified (same input -> same output)

---

## 6. Model Artifacts & Registry

### 6.1 What to Archive

**For each model:**
- Model weights (`.pkl`, `.h5`, `.pt`, `.onnx`)
- Preprocessors (scalers, encoders, tokenizers)
- Feature transformations (versioned with feature store)
- Hyperparameters (JSON config)
- Training metadata (metrics, data version, git commit)

### 6.2 Model Registry

**Purpose:**
- Centralized model storage
- Version management
- Stage promotion (dev -> staging -> prod)
- Metadata and lineage

**Tools:**
- MLflow Model Registry
- W&B Model Registry
- Cloud-specific (SageMaker Model Registry, Vertex AI Model Registry)

**Checklist: Model Artifacts Managed**

- [ ] Model weights and preprocessors saved
- [ ] Artifacts uploaded to model registry
- [ ] Model versioned with semantic versioning (v1.0.0, v1.1.0)
- [ ] Stage annotations (dev, staging, production)
- [ ] Metadata linked (training data version, metrics, owner)

---

## 7. Documentation & Model Cards

### 7.1 Code Documentation

**Requirements:**
- README with setup instructions
- Docstrings for functions and classes
- Inline comments for complex logic
- Architecture diagrams (for complex systems)

### 7.2 Model Card

**Essential sections:**
- Model overview and intended use
- Training data description and biases
- Performance metrics and limitations
- Operational requirements (latency, dependencies)
- Owners and maintenance plan

**Checklist: Documentation Complete**

- [ ] README with environment setup and training instructions
- [ ] Model card created with all sections
- [ ] Runbooks for common issues
- [ ] Architecture diagrams (if applicable)

---

## 8. End-to-End Reproducibility Workflow

### 8.1 Reproducibility Test

**Validate reproducibility by:**
1. Clone repository on fresh machine
2. Set up environment from requirements.txt or Dockerfile
3. Download data using DVC or data versioning tool
4. Run training script with documented seed
5. Verify metrics match within tolerance (+/- 1%)

### 8.2 Continuous Validation

**Automated checks:**
- CI pipeline runs reproducibility test on PRs
- Periodic re-training to validate pipeline
- Drift detection triggers investigation

**Checklist: Reproducibility Validated**

- [ ] Reproducibility test passes on fresh environment
- [ ] Same code + data + seed -> same metrics (+/- 1%)
- [ ] CI pipeline validates reproducibility
- [ ] Documentation sufficient for new team member

---

## 9. Production Readiness Checklist

**Before deploying to production:**

- [ ] All randomness seeded and logged
- [ ] Data and code versioned
- [ ] Experiments logged with full context (code, data, params, metrics)
- [ ] Model registry entry created with stage annotation
- [ ] CI/CD pipeline integrated and tested
- [ ] CT (continuous training) configured with triggers
- [ ] CM (continuous monitoring) dashboards active
- [ ] Drift monitoring enabled (data + concept + performance)
- [ ] Feature store tracks all transformations and versions
- [ ] Model card created and approved
- [ ] Rollback procedure tested
- [ ] Reproducibility validated on fresh environment

---

## Related Resources

- [Data Contracts & Lineage](data-contracts-lineage.md) - Data versioning and lineage tracking
- [Feature Freshness & Streaming](feature-freshness-streaming.md) - Real-time feature updates
- [Production Feedback Loops](production-feedback-loops.md) - Online learning and continuous improvement
- [Evaluation Patterns](evaluation-patterns.md) - Metrics and model evaluation
