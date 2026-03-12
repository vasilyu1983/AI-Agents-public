# Evaluation Patterns

Operational guidance for evaluating ML models: metric selection, slice analysis, error analysis, evaluation reports, and model cards.

---

## 1. Metric & Threshold Selection

### 1.1 Primary Metrics

**Classification:**
- **ROC-AUC**: Area under ROC curve (good for balanced classes)
- **PR-AUC**: Precision-recall AUC (better for imbalanced classes)
- **F1 / F-beta**: Harmonic mean of precision and recall (beta > 1 favors recall, beta < 1 favors precision)
- **Accuracy**: Only for balanced data
- **Log loss**: Penalizes confident wrong predictions

**Regression:**
- **MAE**: Mean Absolute Error (robust to outliers)
- **RMSE**: Root Mean Squared Error (penalizes large errors)
- **MAPE / sMAPE**: Mean Absolute Percentage Error (scale-independent)
- **R^2**: Coefficient of determination (guardrail only, not for optimization)

**Ranking:**
- **NDCG**: Normalized Discounted Cumulative Gain
- **MAP**: Mean Average Precision
- **Recall@K**: Fraction of relevant items in top K

### 1.2 Guardrail Metrics

**Beyond primary metric:**
- **Calibration**: Do predicted probabilities match actual rates? (Brier score, calibration plots)
- **Fairness**: Performance parity across demographic groups
- **Business constraints**: Profit, cost, latency, model size
- **Operational**: Inference time, memory usage, explainability

### 1.3 Threshold Selection

**Methods:**
1. **ROC / PR curves**: Visualize trade-offs, pick operating point
2. **F1 maximization**: Find threshold that maximizes F1 score
3. **Cost-sensitive**: Assign costs to FP and FN, minimize expected cost
4. **Business rule**: E.g., "flag top 10% riskiest transactions"

**Context-specific examples:**
- **Fraud detection**: High recall (catch fraudsters), tolerate FP
- **Spam filtering**: High precision (don't block legitimate emails)
- **Medical diagnosis**: Balance based on cost of false negatives vs false positives

**Checklist: Metrics & Thresholds**

- [ ] Primary metric chosen and justified
- [ ] Guardrail metrics defined (calibration, fairness, constraints)
- [ ] Threshold selection documented (with trade-offs)
- [ ] Metric definitions and calculations reproducible
- [ ] Per-segment thresholds validated (if applicable)

---

## 2. Slice & Error Analysis

### 2.1 Slice Definition

**Why slice:**
- Overall metrics hide subgroup performance issues
- Fairness: ensure equitable performance
- Business impact: different segments have different value

**Common slices:**
- **Geography**: US, EU, APAC, country-level
- **User segments**: New vs returning, free vs paid, power users
- **Product categories**: Electronics, clothing, books
- **Time periods**: Weekday vs weekend, seasonality, recency
- **Data characteristics**: High vs low confidence, common vs rare events
- **Demographics**: Age groups, language (for fairness analysis)

### 2.2 Slice Metrics

**Analysis:**
1. Compute primary metric per slice
2. Identify slices with largest performance gaps vs overall
3. Rank slices by:
   - Absolute performance (worst performers)
   - Degradation from overall (largest gaps)
   - Business impact (volume x performance gap)

**Visualization:**
- Bar charts: metric by slice
- Heatmaps: 2D slices (e.g., geography x product)
- Time series: metric over time per slice

### 2.3 Error Analysis

**Steps:**

1. **Collect high-error examples**
   - Top 100 highest-loss predictions
   - Misclassified examples (FP and FN separately)
   - Low-confidence correct predictions

2. **Cluster errors**
   - Manual review: identify patterns
   - Automated: cluster by features, error magnitude
   - Tag by error type (e.g., "confuses cats and dogs", "struggles with low light")

3. **Identify systematic failures**
   - Missing features (e.g., "time of day not captured")
   - Data quality issues (e.g., "corrupted images")
   - Modeling gaps (e.g., "rare classes underrepresented")

4. **Propose fixes**
   - New features
   - Data augmentation
   - Re-labeling
   - Model architecture changes

**Checklist: Slice & Error Analysis**

- [ ] Key slices identified and evaluated
- [ ] Weak slices documented with hypotheses
- [ ] Example-level errors reviewed qualitatively (top 50-100)
- [ ] Systematic failure modes identified
- [ ] Candidate feature/model changes proposed
- [ ] Business impact of slice performance gaps quantified

---

## 3. Evaluation Report

### 3.1 Purpose

**When to create:**
- Finalizing a model candidate
- Handing over to production team
- Compliance or audit requirements
- Decision to deploy, iterate, or hold

### 3.2 Report Structure

**Section 1: Objective & Context**
- Business problem and success criteria
- Scope and out-of-scope
- Baseline performance

**Section 2: Data Description & Limitations**
- Data sources and time period
- Sample size (train, val, test)
- Known biases or coverage gaps
- PII handling and privacy considerations

**Section 3: Feature Engineering Summary**
- Key features and transformations
- Feature importance (top 10-20)
- Feature store integration (if applicable)

**Section 4: Modeling Approaches Tried**
- Baseline models
- Candidate models (with hyperparameters)
- Why final model was chosen

**Section 5: Metrics (Primary & Guardrails)**
- Primary metric on test set
- Guardrail metrics (calibration, fairness, latency)
- Statistical significance vs baseline

**Section 6: Slice & Error Analysis**
- Performance by key slices
- Worst-performing slices with hypotheses
- Example errors and failure modes

**Section 7: Risks & Mitigations**
- Known limitations
- Failure modes and edge cases
- Mitigation strategies (fallbacks, monitoring)

**Section 8: Recommendation**
- **Deploy**: Model ready for production
- **Iterate**: Needs improvement before deploy
- **Hold**: Not viable, explore alternatives

**Checklist: Evaluation Report Complete**

- [ ] Report includes enough detail for reviewer to follow decisions
- [ ] Limitations and risks explicitly listed
- [ ] Comparisons vs baselines included
- [ ] Monitoring and retraining expectations noted
- [ ] Recommendation justified with evidence

---

## 4. Model Card

### 4.1 Purpose

**When to create:**
- Documenting model for stakeholders
- Compliance requirements (EU AI Act, etc.)
- Internal governance and model registry
- External-facing models (API products)

### 4.2 Model Card Structure (Short Form)

**Section 1: Model Overview**
- What it does (task, inputs, outputs)
- For whom (intended users, use cases)
- Version and release date

**Section 2: Intended Use and Non-Intended Use**
- **Intended**: Approved use cases with examples
- **Non-intended**: Explicitly out-of-scope uses
- **Misuse risks**: Potential harmful applications

**Section 3: Training Data**
- Data sources and time period
- Sampling strategy
- Known biases (geographic, demographic, temporal)
- PII handling

**Section 4: Performance Summary**
- Primary metric on test set
- Performance by key slices
- Calibration and fairness metrics

**Section 5: Ethical/Fairness Considerations**
- Demographic parity or equalized odds
- Potential discriminatory impacts
- Mitigation strategies

**Section 6: Operational Notes**
- Input schema and expected format
- Output schema and interpretation
- Expected latency (p50, p95, p99)
- Dependencies (feature store, external APIs)

**Section 7: Owners and Contacts**
- Model owner / team
- Maintenance plan (retraining cadence)
- Contact for questions / issues

### 4.3 Model Card (Long Form)

For compliance-critical applications, extend with:

- **Model architecture**: Detailed description
- **Hyperparameters**: Full configuration
- **Metrics**: Complete evaluation results
- **Sensitivity analysis**: Impact of data distribution shifts
- **Uncertainty quantification**: Confidence intervals
- **Environmental impact**: CO2 emissions from training
- **Versioning**: Change log from previous versions

**Checklist: Model Card Ready**

- [ ] Intended/unsafe uses documented
- [ ] Performance by segment summarized
- [ ] Data limitations and biases acknowledged
- [ ] Owners and maintenance plan listed
- [ ] Compliance requirements met (if applicable)

---

## 5. Stability & Reproducibility Checks

### 5.1 Seed Stability

**Why it matters:**
- Ensure results not due to random luck
- Build confidence in model selection
- Detect overfitting to validation set

**Procedure:**
1. Train model with 5-10 different random seeds
2. Report mean +/- std for key metrics
3. Verify rankings stable (best model stays best)

**Red flags:**
- High variance in metrics (std > 5% of mean)
- Model rankings change with different seeds
- Single run significantly outperforms average

### 5.2 Cross-Validation Stability

**When to use:**
- Small datasets (< 10k samples)
- Need robust estimates
- Hyperparameter tuning

**Procedure:**
1. K-fold cross-validation (K = 5 or 10)
2. Report mean +/- std across folds
3. Check consistency of feature importance
4. Validate on final held-out test set

**Checklist: Stability Validated**

- [ ] Multiple seeds tested (5-10 runs)
- [ ] Variance of metrics acceptable (std < 5% of mean)
- [ ] Model rankings stable across seeds
- [ ] Cross-validation used for small datasets
- [ ] Final test set validates CV results

---

## 6. Statistical Significance Testing

### 6.1 When to Test

**Use statistical tests when:**
- Comparing two models with small performance difference
- Need confidence in improvement (e.g., for production deployment)
- Evaluating A/B test results

**Skip when:**
- Large performance differences (obvious winner)
- Exploratory phase (many models to try)
- Computationally expensive

### 6.2 Methods

**Paired t-test:**
- Use when: Comparing two models on same cross-validation folds
- Null hypothesis: No difference in mean performance
- Threshold: p < 0.05 (or p < 0.01 for stricter test)

**Bootstrap confidence intervals:**
- Use when: Want uncertainty estimates
- Procedure: Resample test set 1000 times, compute metric, report 95% CI
- Interpretation: If CIs don't overlap, difference is significant

**Permutation test:**
- Use when: Distribution assumptions unclear
- Procedure: Randomly permute labels, compute metric, compare to actual
- Threshold: p < 0.05

**Checklist: Statistical Testing**

- [ ] Test method chosen and justified
- [ ] Null hypothesis clearly stated
- [ ] p-value or confidence intervals reported
- [ ] Multiple testing correction applied (if comparing many models)
- [ ] Practical significance considered (not just statistical)

---

## Related Resources

- [Modelling Patterns](modelling-patterns.md) - Model selection, hyperparameter tuning, train/test splits
- [Reproducibility Checklist](reproducibility-checklist.md) - Experiment tracking and versioning
- [Production Feedback Loops](production-feedback-loops.md) - Online evaluation and A/B testing  
