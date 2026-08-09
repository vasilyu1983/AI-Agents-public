# ML Model Code Review Checklist

Specialized checklist for reviewing machine learning model code (training, architecture, hyperparameters, evaluation).

---

## Model Architecture & Design

### Architecture Decisions
- [ ] Model type justified (tree-based, neural network, linear, etc.)
- [ ] Baseline model implemented and documented
- [ ] Model complexity appropriate for data size
- [ ] Architecture matches problem constraints (latency, interpretability)
- [ ] Model inputs and outputs clearly defined
- [ ] Feature dimensionality documented

### Modern Best Practices
- [ ] LightGBM/XGBoost considered for tabular data
- [ ] Tree-based methods used as first baseline
- [ ] Computational efficiency considered early
- [ ] Model selection aligns with benchmark results
- [ ] Hyperparameter search space reasonable

### Feature Engineering
- [ ] Feature transformations documented
- [ ] Feature scaling/normalization applied correctly
- [ ] Categorical encoding strategy defined
- [ ] Feature interactions considered where appropriate
- [ ] Feature importance tracked
- [ ] No data leakage in feature creation

---

## Data Validation & Quality

### Data Checks
- [ ] Training data schema validated
- [ ] Missing values handled explicitly
- [ ] Outliers identified and strategy documented
- [ ] Data types correct and consistent
- [ ] Data distribution checked for anomalies
- [ ] Class imbalance identified and addressed

### Train/Test Splitting
- [ ] Split strategy documented (random, time-based, stratified)
- [ ] No data leakage between train and test
- [ ] Time ordering preserved for time series
- [ ] Group/entity leakage prevented
- [ ] Validation set held out from all decisions
- [ ] Test set never used during development

### Data Leakage Prevention
- [ ] No future information in features
- [ ] Target encoding uses only training data
- [ ] Normalization statistics from training set only
- [ ] No test data used in feature selection
- [ ] IDs and timestamps handled safely
- [ ] Leakage checklist completed

---

## Training Pipeline

### Training Process
- [ ] Random seeds set for reproducibility
- [ ] Training loop implemented correctly
- [ ] Early stopping implemented (if applicable)
- [ ] Gradient clipping used (if neural network)
- [ ] Batch size and learning rate justified
- [ ] Training progress logged

### Hyperparameter Tuning
- [ ] Hyperparameter search strategy documented (grid, random, Bayesian)
- [ ] Search space defined and justified
- [ ] Cross-validation used for tuning
- [ ] Overfitting risk assessed
- [ ] Compute budget considered
- [ ] Best hyperparameters documented

### Regularization
- [ ] Regularization techniques applied (L1/L2, dropout, etc.)
- [ ] Regularization strength tuned
- [ ] Early stopping prevents overfitting
- [ ] Model capacity appropriate for data size

---

## Model Evaluation

### Metrics & Validation
- [ ] Primary metric chosen and justified
- [ ] Guardrail metrics defined (fairness, calibration, cost)
- [ ] Metrics calculated on held-out test set
- [ ] Baseline performance documented
- [ ] Performance compared to business requirements
- [ ] Metric definitions reproducible

### Slice Analysis
- [ ] Performance evaluated across key slices
- [ ] Weak segments identified and documented
- [ ] Fairness across sensitive groups checked
- [ ] Error patterns analyzed qualitatively
- [ ] Systematic failures documented

### Robustness Checks
- [ ] Model tested on edge cases
- [ ] Adversarial examples considered (if applicable)
- [ ] Sensitivity to input perturbations checked
- [ ] Out-of-distribution behavior documented
- [ ] Model calibration assessed

---

## Reproducibility & Versioning

### Code & Environment
- [ ] Code version controlled (git commit tracked)
- [ ] Python/package versions pinned
- [ ] Random seeds documented
- [ ] Training can be re-run identically
- [ ] Environment setup documented (requirements.txt, Dockerfile)

### Data & Model Versioning
- [ ] Training data version tracked
- [ ] Data snapshot ID recorded
- [ ] Model artifacts versioned
- [ ] Feature set version documented
- [ ] Model registry entry created

### Experiment Tracking
- [ ] Experiments logged in tracker (MLflow, W&B)
- [ ] Hyperparameters logged
- [ ] Metrics logged
- [ ] Artifacts stored (model, plots, reports)
- [ ] Run comparisons possible

---

## MLOps Integration

### Feature Store Integration
- [ ] Features retrieved from feature store
- [ ] Feature versions tracked
- [ ] Train-serve consistency ensured
- [ ] Feature transformations centralized
- [ ] Feature monitoring enabled

### CI/CD Integration
- [ ] Model training pipeline automated
- [ ] Unit tests for data processing
- [ ] Model validation checks automated
- [ ] Model promotion workflow defined
- [ ] Environment-specific configs (dev/staging/prod)

### Monitoring Setup
- [ ] Data drift detection configured
- [ ] Model performance monitoring planned
- [ ] Retraining triggers defined
- [ ] Alerting thresholds set
- [ ] Fallback strategy documented

---

## Clean Code (Core)

- Clean code standard (cite `CC-*` IDs): [../../../software-clean-code-standard/references/clean-code-standard.md](../../../software-clean-code-standard/references/clean-code-standard.md)
- Standards: cite `CC-*` IDs; do not restate rules.
- Common `CC-*` IDs for model code: `CC-NAM-01`, `CC-FUN-01`, `CC-FUN-05`, `CC-TYP-01`, `CC-TYP-04`, `CC-ERR-01`, `CC-SEC-05`, `CC-DOC-01`, `CC-DOC-04`, `CC-TST-01`, `CC-TST-02`, `CC-TST-04`

### Testing
- [ ] Unit tests for data processing functions
- [ ] Unit tests for feature engineering
- [ ] Integration tests for training pipeline
- [ ] Model output validation tests
- [ ] Edge case tests included

### Documentation
- [ ] Model architecture documented
- [ ] Training procedure documented
- [ ] Hyperparameter choices explained
- [ ] Evaluation approach documented
- [ ] Known limitations listed
- [ ] Model card created (or planned)

---

## Security & Ethics

### Data Privacy
- [ ] PII handling compliant with regulations
- [ ] Sensitive features identified
- [ ] Data anonymization applied where needed
- [ ] Access controls on training data
- [ ] No secrets in code or logs

### Fairness & Bias
- [ ] Protected attributes identified
- [ ] Fairness metrics computed
- [ ] Bias mitigation strategies considered
- [ ] Disparate impact assessed
- [ ] Ethical considerations documented

### Model Safety
- [ ] Failure modes identified
- [ ] Safety checks in prediction pipeline
- [ ] Human-in-the-loop for high-risk decisions
- [ ] Model limitations communicated to stakeholders

---

## Performance & Efficiency

### Computational Efficiency
- [ ] Training time reasonable for iteration cycle
- [ ] Memory usage within constraints
- [ ] GPU utilization optimized (if applicable)
- [ ] Batch processing used where possible
- [ ] Unnecessary computations eliminated

### Inference Performance
- [ ] Inference latency measured
- [ ] Inference meets production requirements
- [ ] Model size acceptable for deployment
- [ ] Quantization or compression considered
- [ ] Batch inference optimized

---

## Documentation & Handover

### Model Documentation
- [ ] Model evaluation report written
- [ ] Model card created
- [ ] Training notebook/script documented
- [ ] Hyperparameters and architecture documented
- [ ] Performance summary clear

### Production Readiness
- [ ] Deployment requirements documented
- [ ] Input/output contracts defined
- [ ] Expected latency and throughput documented
- [ ] Monitoring and alerting plan defined
- [ ] Rollback strategy documented
- [ ] Owners and contacts listed

---

## Final Checklist

Before approving ML model code:
- [ ] Model performance meets requirements
- [ ] No data leakage detected
- [ ] Reproducibility verified
- [ ] Tests passing
- [ ] Documentation complete
- [ ] MLOps integration ready
- [ ] Production deployment plan reviewed
