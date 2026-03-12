# Production Feedback & Label Loops

Operational patterns for capturing production signals, building labeling pipelines, and implementing continuous model improvement.

---

## Overview

Production ML systems generate valuable feedback signals that can be used to continuously improve models. This guide covers best practices for capturing feedback, managing labeling workflows, and implementing safe online evaluation.

---

## 1. Signal Capture

### 1.1 Types of Production Signals

**Explicit feedback:**
- User ratings (thumbs up/down, stars)
- Corrections/edits to predictions
- Acceptance vs rejection of recommendations
- Manual overrides by operators

**Implicit feedback:**
- Click-through rate (CTR)
- Dwell time / scroll depth
- Bounce rate / abandonment
- Conversion events
- User edits after prediction

**System feedback:**
- Prediction confidence scores
- Latency and error rates
- A/B test outcomes
- Drift detection alerts

### 1.2 Capture Requirements

**What to log:**
```python
feedback_event = {
    "request_id": "req-abc123",
    "model_version": "v1.5.2",
    "feature_version": "v2.1",
    "timestamp": "2024-11-22T10:30:00Z",
    "prediction": {"class": "positive", "score": 0.87},
    "feedback": {"user_action": "accepted", "edited": false},
    "features": {...},  # Feature values at prediction time
    "user_id_hash": "sha256:...",  # Anonymized
    "session_id": "sess-xyz789"
}
```

**Privacy considerations:**
- **Scrub PII**: Remove or hash user identifiers
- **Consent**: Log only when user has consented
- **Retention**: Define and enforce data retention policies
- **Access control**: Restrict who can access feedback data

**Checklist: Signal Capture**

- [ ] Predictions logged with model/feature versions
- [ ] User feedback captured (explicit + implicit)
- [ ] Features at prediction time stored
- [ ] PII removed or anonymized
- [ ] Versioned models linked to feedback
- [ ] Retention policy enforced

---

## 2. Labeling Workflows

### 2.1 Label Sourcing Strategies

**Human labeling:**
- Internal subject matter experts (SMEs)
- Crowdsourcing (Amazon MTurk, Scale AI, Labelbox)
- Active learning: label most informative examples

**Automated labeling:**
- User feedback as implicit labels
- Heuristic rules for high-confidence cases
- Model-assisted labeling (human reviews model suggestions)

**Hybrid approach:**
- Model pre-labels
- Humans review and correct
- High-confidence predictions auto-accepted

### 2.2 Routing to Human Review

**When to route for labeling:**
- Low confidence predictions (score < threshold)
- Disagreement between models (ensemble variance)
- Edge cases / out-of-distribution inputs
- Failed predictions (errors, timeouts)
- Random sampling for quality monitoring

**Prioritization:**
- High business impact cases first
- Informative examples (active learning)
- Diverse coverage (stratified sampling)

**Checklist: Labeling Workflow**

- [ ] Routing rules defined (confidence, errors, edge cases)
- [ ] Labeling queue with prioritization
- [ ] Rubric documented for annotators
- [ ] Inter-annotator agreement tracked
- [ ] Quality control: gold standard examples
- [ ] Feedback loop to improve routing rules

---

## 3. Label Quality Control

### 3.1 Quality Metrics

**Inter-annotator agreement:**
- Cohen's Kappa (2 annotators)
- Fleiss' Kappa (3+ annotators)
- Krippendorff's Alpha (ordinal/continuous labels)

**Gold standard validation:**
- Inject known labels into annotation queue
- Track annotator accuracy on gold examples
- Retrain annotators with low accuracy

**Consistency checks:**
- Same example shown to multiple annotators
- Track agreement rates
- Flag high-disagreement examples for review

### 3.2 Rubric Development

**Components:**
- Clear definition of each class/label
- Edge case handling guidelines
- Examples (positive and negative)
- Decision tree for ambiguous cases

**Iteration:**
- Start with draft rubric
- Run pilot labeling (10-50 examples)
- Analyze disagreements
- Refine rubric
- Repeat until high agreement (Kappa > 0.7)

**Checklist: Label Quality**

- [ ] Labeling rubric documented with examples
- [ ] Inter-annotator agreement measured (Kappa > 0.7 target)
- [ ] Gold standard examples used for QA
- [ ] Annotator performance tracked
- [ ] Disagreements reviewed and rubric updated

---

## 4. Dataset Refresh Cadence

### 4.1 Refresh Strategy

**Frequency options:**
- **Continuous**: Update training set daily/weekly (high-velocity domains)
- **Periodic**: Monthly/quarterly refreshes (stable domains)
- **Event-driven**: Trigger on drift detection or performance drop

**Composition:**
- **Recent data**: Captures latest patterns
- **Historical data**: Maintains coverage of rare events
- **Balanced**: Ensure class balance, slice coverage

**Lineage:**
- Track which production data entered training set
- Version datasets (v1.0, v1.1, ...)
- Document sampling/filtering rules

**Checklist: Dataset Refresh**

- [ ] Refresh cadence defined and justified
- [ ] Dataset composition rules documented
- [ ] Lineage tracked (production -> training)
- [ ] Eval set protected from contamination
- [ ] Class balance and slice coverage validated

---

## 5. Eval Set Contamination Prevention

### 5.1 The Problem

**Contamination sources:**
- Production data leaks into training set
- Test examples seen during development
- Data augmentation creates near-duplicates
- Web scraping captures evaluation examples

**Consequences:**
- Overestimated performance
- Poor generalization
- Failed production deployment

### 5.2 Prevention Strategies

**Temporal split:**
- Eval set from time period T
- Training set from before T
- Never add post-T data to training

**Hashing:**
- Hash all eval examples
- Check training set for hash collisions
- Log warnings if contamination detected

**Periodic refresh:**
- Rotate eval set quarterly/yearly
- Archive old eval sets
- Human review to ensure novelty

**Checklist: Contamination Prevention**

- [ ] Eval set temporally isolated from training
- [ ] Hashing or deduplication checks in place
- [ ] Eval set refresh schedule defined
- [ ] Production data filtered before entering training
- [ ] Automated checks in CI/CD pipeline

---

## 6. Online Evaluation

### 6.1 Shadow Mode

**How it works:**
- New model runs in parallel with production model
- Production uses old model predictions
- Log both model predictions + outcomes
- Compare offline

**When to use:**
- Low-risk initial testing
- Performance comparison without user impact
- Latency/cost validation

**Checklist: Shadow Mode**

- [ ] Shadow model deployed with same inputs
- [ ] Predictions logged with model version
- [ ] Comparison metrics defined (accuracy, latency, cost)
- [ ] Duration defined (e.g., 1 week)
- [ ] Go/no-go criteria for promotion

---

### 6.2 Canary Deployment

**How it works:**
- Route small % of traffic to new model (1-5%)
- Monitor key metrics (accuracy, latency, errors)
- Gradually increase % if metrics healthy
- Auto-abort on regression

**When to use:**
- After successful shadow mode
- Incremental rollout to production
- Real user feedback needed

**Metrics to track:**
- **Solve rate**: % of requests successfully handled
- **Calibration**: Predicted probabilities vs actual rates
- **Latency**: p50, p95, p99
- **Cost**: Inference cost per request
- **Error rate**: 4xx, 5xx errors

**Abort conditions:**
- Solve rate drops > 5%
- Latency p99 > 2x baseline
- Error rate > 2x baseline
- Calibration error > threshold

**Checklist: Canary Deployment**

- [ ] Canary % defined (start with 1-5%)
- [ ] Metrics tracked per model version
- [ ] Abort conditions configured
- [ ] Gradual rollout plan (5% -> 10% -> 50% -> 100%)
- [ ] Rollback procedure tested
- [ ] Incident response plan documented

---

### 6.3 A/B Testing

**How it works:**
- Split traffic randomly into control (A) and treatment (B)
- Measure business metrics (CTR, conversion, revenue)
- Statistical test for significance

**When to use:**
- Validating business impact (not just model metrics)
- Comparing multiple candidates
- Balancing model accuracy vs other factors (latency, cost)

**Statistical considerations:**
- **Sample size**: Calculate required traffic for desired power
- **Duration**: Run long enough for seasonality (1-2 weeks minimum)
- **Multiple testing**: Bonferroni correction if testing multiple variants
- **Novelty effects**: Watch for user behavior changes over time

**Checklist: A/B Testing**

- [ ] Business metrics defined (not just model metrics)
- [ ] Sample size calculated (power analysis)
- [ ] Randomization verified (no selection bias)
- [ ] Duration planned (minimum 1 week)
- [ ] Statistical significance test chosen (t-test, chi-squared)
- [ ] Multiple testing correction applied if needed

---

## 7. Slice-Specific Monitoring

### 7.1 Why Slice Monitoring Matters

**Problem:**
- Overall metrics may look good
- Performance degrades for specific subgroups
- Fairness issues hidden in aggregates

**Example slices:**
- Geography (US vs EU vs APAC)
- User segments (new vs returning, free vs paid)
- Product categories
- Time periods (weekday vs weekend)
- Language/locale
- Device type (mobile vs desktop)

### 7.2 Implementation

**Dashboard design:**
```
Overall Metrics:
  Accuracy: 0.85
  Latency p99: 150ms

Slice Breakdown:
  US:         Accuracy 0.87, Latency 120ms
  EU:         Accuracy 0.84, Latency 180ms  - Flag: high latency
  APAC:       Accuracy 0.78, Latency 200ms  - Flag: low accuracy

  Mobile:     Accuracy 0.82, Latency 100ms
  Desktop:    Accuracy 0.88, Latency 150ms
```

**Alerts:**
- Per-slice accuracy drops > 10% vs baseline
- Per-slice latency > 2x overall p99
- Sample size too small (< 100 requests/day)

**Checklist: Slice Monitoring**

- [ ] Key slices identified (geography, user segments, time)
- [ ] Metrics tracked per slice
- [ ] Dashboards visualize slice performance
- [ ] Alerts configured for slice-specific degradation
- [ ] Sample size tracked (avoid spurious alerts on small slices)

---

## 8. Continuous Improvement Loop

### 8.1 End-to-End Workflow

**Step 1: Capture signals**
- Log predictions, features, feedback

**Step 2: Route to labeling**
- High-value, low-confidence, or failed examples

**Step 3: Quality control**
- Validate labels, track annotator agreement

**Step 4: Dataset refresh**
- Add new labeled data to training set
- Avoid eval contamination

**Step 5: Retrain & evaluate**
- Train new model version
- Validate on held-out eval set

**Step 6: Online evaluation**
- Shadow mode -> Canary -> A/B test

**Step 7: Monitor slices**
- Track per-slice performance
- Identify degradation early

**Step 8: Iterate**
- Analyze failures, update features/model

**Checklist: Feedback Loop Active**

- [ ] Signals captured automatically
- [ ] Labeling queue operational
- [ ] Dataset refresh automated (weekly/monthly)
- [ ] Retraining pipeline automated
- [ ] Online evaluation workflow defined
- [ ] Slice monitoring dashboards active
- [ ] Feedback analyzed for model improvements

---

## 9. Cost-Benefit Analysis

### 9.1 Costs

**Labeling costs:**
- Annotator time ($/hour x hours)
- Tooling (Labelbox, Scale AI fees)
- Quality control overhead

**Infrastructure costs:**
- Logging and storage (S3, BigQuery)
- Shadow/canary deployment resources
- A/B testing traffic allocation

**Engineering costs:**
- Pipeline development and maintenance
- Monitoring and alerting setup
- Incident response

### 9.2 Benefits

**Business impact:**
- Improved model accuracy -> higher conversion/revenue
- Faster time-to-market for model updates
- Reduced manual intervention (automation)

**Risk reduction:**
- Detect degradation before major impact
- Rollback capability (canary abort)
- Compliance and auditability

**Checklist: ROI Justified**

- [ ] Labeling cost per example calculated
- [ ] Infrastructure costs estimated
- [ ] Business impact quantified (revenue, cost savings)
- [ ] ROI positive (benefits > costs)
- [ ] Incremental approach if ROI unclear (start small, scale)

---

## Related Resources

- [Data Contracts & Lineage](data-contracts-lineage.md) - Versioning and lineage tracking
- [Evaluation Patterns](evaluation-patterns.md) - Offline evaluation metrics and methods
- [Feature Freshness & Streaming](feature-freshness-streaming.md) - Real-time feature updates
