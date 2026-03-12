# Online Evaluation & Feedback Loops

Patterns for collecting production feedback, running online experiments (A/B tests, shadow deployments), building labeled datasets, and closing the feedback loop with automated retraining.

---

## Overview

**Online evaluation** measures model performance in production using real user interactions and business outcomes. Unlike offline evaluation (test sets), online evaluation captures real-world behavior, concept drift, and user satisfaction.

**Key Topics:**
- Feedback signal collection (implicit and explicit)
- Shadow and canary deployments
- A/B testing and statistical significance
- Human-in-the-loop labeling pipelines
- Retraining cadence and triggers
- Eval set protection

---

## Pattern 1: Feedback Signal Collection

### Types of Signals

**Explicit feedback:**
- User ratings (thumbs up/down, 1-5 stars)
- Direct corrections (user edits prediction)
- Reported errors (user flags incorrect result)

**Implicit feedback:**
- Click-through rate (CTR)
- Conversion rate
- Task completion (did user accomplish goal?)
- Time to completion
- Abandonment rate

**Business metrics:**
- Revenue impact
- Customer satisfaction (NPS, CSAT)
- Retention
- Engagement

### Implementation: Capture Signals with Privacy

**1. Log predictions with hashed user IDs**

```python
def log_prediction(user_id, features, prediction, model_version):
    """Log prediction for feedback loop."""
    log_data = {
        'timestamp': datetime.utcnow(),
        'user_id_hash': hashlib.sha256(user_id.encode()).hexdigest(),
        'features': redact_pii(features),
        'prediction': prediction,
        'model_version': model_version,
        'request_id': generate_request_id()
    }
    logger.info(log_data)
    return log_data['request_id']
```

**2. Capture explicit feedback**

```python
@app.post("/feedback")
def submit_feedback(request_id: str, rating: int, comment: str = None):
    """User submits feedback on prediction."""

    # Retrieve original prediction
    prediction_log = db.get_prediction(request_id)

    # Store feedback
    feedback_db.insert({
        'request_id': request_id,
        'rating': rating,  # 1-5 stars
        'comment': redact_pii(comment),
        'timestamp': datetime.utcnow()
    })

    # Update metrics
    metrics.increment('feedback_received', tags={'rating': rating})
```

**3. Capture implicit feedback (clicks, conversions)**

```python
def track_click(request_id, clicked_item):
    """Track user clicks after prediction."""
    feedback_db.insert({
        'request_id': request_id,
        'event_type': 'click',
        'clicked_item': clicked_item,
        'timestamp': datetime.utcnow()
    })

def track_conversion(request_id, converted):
    """Track whether user converted (purchased, signed up, etc.)."""
    feedback_db.insert({
        'request_id': request_id,
        'event_type': 'conversion',
        'converted': converted,
        'timestamp': datetime.utcnow()
    })
```

**4. Aggregate signals into metrics**

```python
def compute_online_metrics(model_version, time_window='24h'):
    """Compute online metrics from feedback."""

    predictions = db.get_predictions(
        model_version=model_version,
        time_window=time_window
    )

    feedbacks = db.get_feedback(
        request_ids=[p.request_id for p in predictions]
    )

    # Compute metrics
    metrics = {
        'num_predictions': len(predictions),
        'num_feedback': len(feedbacks),
        'avg_rating': np.mean([f.rating for f in feedbacks]),
        'ctr': compute_ctr(predictions, feedbacks),
        'conversion_rate': compute_conversion_rate(predictions, feedbacks),
        'task_success_rate': compute_success_rate(predictions, feedbacks)
    }

    return metrics
```

### Privacy Considerations

**PII scrubbing:**
- Hash user IDs before logging
- Redact PII from features and feedback comments
- Aggregate metrics at cohort level (not individual)

**Retention policies:**
- Delete raw logs after aggregation (e.g., 30 days)
- Retain aggregated metrics indefinitely
- Comply with GDPR right to erasure

### Checklist

- [ ] Feedback signals defined (explicit, implicit, business)
- [ ] Logging captures request ID, prediction, model version
- [ ] User IDs hashed before logging
- [ ] PII redacted from logs
- [ ] Feedback aggregated into online metrics
- [ ] Privacy policies documented

---

## Pattern 2: Shadow & Canary Deployments

### Shadow Deployment

**Concept:** Run new model alongside production model, but don't serve its predictions to users. Compare predictions offline.

**When to use:**
- High-risk model changes (new architecture, major refactor)
- Need extensive validation without user impact

**Implementation:**

```python
@app.post("/predict")
def predict_with_shadow(features):
    """Serve production model, shadow new model."""

    # Production model (serve to user)
    prod_prediction = prod_model.predict(features)

    # Shadow model (don't serve, log for analysis)
    if shadow_enabled():
        shadow_prediction = shadow_model.predict(features)

        # Log comparison
        log_shadow_comparison(
            features=features,
            prod_prediction=prod_prediction,
            shadow_prediction=shadow_prediction
        )

    return prod_prediction
```

**Analysis:**

```python
def analyze_shadow_results():
    """Compare shadow and production predictions."""

    comparisons = db.get_shadow_comparisons(last_24h)

    # Agreement rate
    agreement = sum(
        c.prod_prediction == c.shadow_prediction
        for c in comparisons
    ) / len(comparisons)

    # Latency comparison
    avg_latency_diff = np.mean([
        c.shadow_latency - c.prod_latency
        for c in comparisons
    ])

    # Prediction distribution shift
    prod_dist = compute_distribution([c.prod_prediction for c in comparisons])
    shadow_dist = compute_distribution([c.shadow_prediction for c in comparisons])

    return {
        'agreement_rate': agreement,
        'avg_latency_diff_ms': avg_latency_diff,
        'distribution_shift': kl_divergence(prod_dist, shadow_dist)
    }
```

**Promotion decision:**
- Agreement rate > 95% → low risk
- Latency within SLO → acceptable
- Distribution shift small → safe to promote

### Canary Deployment

**Concept:** Route small % of traffic to new model, monitor metrics, expand gradually.

**When to use:**
- Want gradual validation with real users
- Can tolerate partial rollback

**Implementation:**

```python
def route_to_model(user_id):
    """Route user to production or canary model."""

    # Canary traffic % (start at 5%, expand to 100%)
    canary_traffic_pct = get_canary_traffic_pct()

    # Deterministic routing (same user always gets same model)
    user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)

    if user_hash % 100 < canary_traffic_pct:
        return 'canary'
    else:
        return 'production'

@app.post("/predict")
def predict_with_canary(user_id: str, features: dict):
    """Route to canary or production model."""

    model_variant = route_to_model(user_id)

    if model_variant == 'canary':
        prediction = canary_model.predict(features)
    else:
        prediction = prod_model.predict(features)

    # Log for A/B analysis
    log_prediction(user_id, features, prediction, model_variant)

    return prediction
```

**Monitoring:**

```python
def monitor_canary_metrics():
    """Compare canary vs production metrics."""

    prod_metrics = compute_online_metrics(model_version='production')
    canary_metrics = compute_online_metrics(model_version='canary')

    # Check for regressions
    if canary_metrics['error_rate'] > prod_metrics['error_rate'] * 1.5:
        alert("Canary error rate elevated, consider rollback")

    if canary_metrics['latency_p99'] > prod_metrics['latency_p99'] * 1.2:
        alert("Canary latency elevated, consider rollback")

    if canary_metrics['conversion_rate'] < prod_metrics['conversion_rate'] * 0.95:
        alert("Canary conversion rate low, consider rollback")
```

**Gradual rollout:**

```
Day 1: 5% canary traffic → monitor for 24h
Day 2: 10% canary traffic → monitor for 12h
Day 3: 25% canary traffic → monitor for 12h
Day 4: 50% canary traffic → monitor for 12h
Day 5: 100% canary traffic → promote to production
```

**Abort criteria:**
- Error rate > 1.5x baseline
- Latency P99 > 1.2x baseline
- Conversion rate < 0.95x baseline
- User complaints > threshold

### Checklist

- [ ] Shadow deployment captures comparisons
- [ ] Canary routing deterministic (same user → same model)
- [ ] Metrics compared between production and canary
- [ ] Abort criteria defined and automated
- [ ] Gradual rollout schedule documented

---

## Pattern 3: A/B Testing & Statistical Significance

### A/B Test Design

**Hypothesis:** New model (variant B) improves conversion rate vs current model (variant A)

**Randomization:**
- Assign users randomly to A or B
- Ensure balanced assignment (50/50 or 90/10)
- Track assignment in database

**Metrics:**
- Primary: Conversion rate
- Secondary: CTR, latency, error rate

**Sample size:**
- Compute required sample size for statistical power
- Run until statistical significance or time limit

### Implementation

**1. Random assignment**

```python
def assign_variant(user_id, experiment_id='model_v42_test'):
    """Randomly assign user to A or B variant."""

    # Check if user already assigned
    assignment = db.get_assignment(user_id, experiment_id)
    if assignment:
        return assignment.variant

    # New assignment (random)
    variant = 'B' if random.random() < 0.5 else 'A'

    # Store assignment
    db.insert_assignment({
        'user_id': user_id,
        'experiment_id': experiment_id,
        'variant': variant,
        'assigned_at': datetime.utcnow()
    })

    return variant

@app.post("/predict")
def predict_with_ab_test(user_id: str, features: dict):
    """Serve prediction with A/B test."""

    variant = assign_variant(user_id)

    if variant == 'A':
        prediction = model_a.predict(features)  # Production
    else:
        prediction = model_b.predict(features)  # New model

    # Log for analysis
    log_prediction(user_id, features, prediction, variant)

    return prediction
```

**2. Metric computation**

```python
def compute_ab_metrics(experiment_id):
    """Compute metrics for A and B variants."""

    assignments = db.get_assignments(experiment_id)

    variant_a_users = [a.user_id for a in assignments if a.variant == 'A']
    variant_b_users = [a.user_id for a in assignments if a.variant == 'B']

    # Conversion rates
    conversions_a = db.count_conversions(variant_a_users)
    conversions_b = db.count_conversions(variant_b_users)

    conversion_rate_a = conversions_a / len(variant_a_users)
    conversion_rate_b = conversions_b / len(variant_b_users)

    # Statistical test (two-proportion z-test)
    z_stat, p_value = proportions_ztest(
        [conversions_b, conversions_a],
        [len(variant_b_users), len(variant_a_users)]
    )

    return {
        'variant_a': {
            'users': len(variant_a_users),
            'conversions': conversions_a,
            'conversion_rate': conversion_rate_a
        },
        'variant_b': {
            'users': len(variant_b_users),
            'conversions': conversions_b,
            'conversion_rate': conversion_rate_b
        },
        'statistical_test': {
            'z_stat': z_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    }
```

**3. Decision criteria**

```python
def decide_ab_test(experiment_id, min_users=10000, max_days=14):
    """Decide whether to promote variant B."""

    metrics = compute_ab_metrics(experiment_id)

    # Check if enough data
    if metrics['variant_b']['users'] < min_users:
        return 'continue'  # Not enough data

    # Check statistical significance
    if not metrics['statistical_test']['significant']:
        # Check if time limit exceeded
        if experiment_running_days(experiment_id) >= max_days:
            return 'no_difference'  # Inconclusive, use current model
        else:
            return 'continue'  # Keep running

    # Check direction of effect
    if metrics['variant_b']['conversion_rate'] > metrics['variant_a']['conversion_rate']:
        return 'promote_b'  # Variant B wins
    else:
        return 'keep_a'  # Variant A wins
```

### Checklist

- [ ] A/B test hypothesis and metrics defined
- [ ] Random assignment implemented
- [ ] Sample size calculated
- [ ] Statistical test chosen (z-test, t-test, Bayesian)
- [ ] Decision criteria documented
- [ ] Experiment duration defined

---

## Pattern 4: Human-in-the-Loop Labeling

### Use Cases

**1. Failures and edge cases**
- Model predictions with low confidence
- User reported errors
- Adversarial examples

**2. Active learning**
- Select most informative examples for labeling
- Prioritize high-uncertainty predictions

**3. Supervised dataset creation**
- Build training set for new task
- Improve performance on underrepresented slices

**4. Preference dataset creation (RLHF)**
- Rank model outputs (A vs B)
- Build preference pairs for fine-tuning

### Labeling Pipeline

**1. Identify candidates for labeling**

```python
def select_labeling_candidates(model_predictions, strategy='uncertainty'):
    """Select predictions for human labeling."""

    if strategy == 'uncertainty':
        # Low confidence predictions
        candidates = [
            p for p in model_predictions
            if p.confidence < 0.7
        ]

    elif strategy == 'error_reports':
        # User-reported errors
        candidates = [
            p for p in model_predictions
            if p.user_reported_error
        ]

    elif strategy == 'random':
        # Random sample for quality check
        candidates = random.sample(model_predictions, k=100)

    return candidates
```

**2. Queue for labeling**

```python
def queue_for_labeling(candidates):
    """Add candidates to labeling queue."""

    for candidate in candidates:
        labeling_db.insert({
            'request_id': candidate.request_id,
            'features': candidate.features,
            'model_prediction': candidate.prediction,
            'queued_at': datetime.utcnow(),
            'status': 'pending'
        })
```

**3. Labeling interface (human annotators)**

```python
@app.get("/labeling/next")
def get_next_labeling_task(annotator_id: str):
    """Fetch next task for annotator."""

    task = labeling_db.get_next_pending_task()

    if task is None:
        return {'message': 'No tasks available'}

    # Assign to annotator
    labeling_db.update(task.id, {
        'status': 'in_progress',
        'annotator_id': annotator_id,
        'assigned_at': datetime.utcnow()
    })

    return {
        'task_id': task.id,
        'features': task.features,
        'model_prediction': task.model_prediction
    }

@app.post("/labeling/submit")
def submit_label(task_id: str, label: str):
    """Annotator submits label."""

    labeling_db.update(task_id, {
        'status': 'completed',
        'label': label,
        'completed_at': datetime.utcnow()
    })

    # Add to training dataset
    training_db.insert({
        'features': labeling_db.get(task_id).features,
        'label': label,
        'labeled_at': datetime.utcnow()
    })
```

**4. Eval set protection (no contamination)**

```python
def protect_eval_set(labeled_data):
    """Ensure eval set not contaminated."""

    # Eval set users (held out permanently)
    eval_user_ids = db.get_eval_user_ids()

    # Filter out eval users from training data
    training_data = [
        d for d in labeled_data
        if d.user_id not in eval_user_ids
    ]

    return training_data
```

### Checklist

- [ ] Labeling candidates selected (uncertainty, errors, random)
- [ ] Labeling queue managed (pending, in-progress, completed)
- [ ] Annotator interface built
- [ ] Labels added to training dataset
- [ ] Eval set protected from contamination
- [ ] Inter-annotator agreement measured

---

## Pattern 5: Retraining Cadence & Promotion

### Retraining Triggers

**Time-based:**
- Scheduled retraining (weekly, monthly)
- Ensures model stays fresh

**Event-based:**
- Drift detected (data or performance)
- Schema change in upstream data
- Data volume threshold reached (e.g., 10k new labels)
- Manual override (critical bug fix)

### Retraining Pipeline

**1. Trigger retraining job**

```python
def trigger_retraining(trigger_type, trigger_metadata):
    """Start automated retraining job."""

    # Log trigger
    retraining_db.insert({
        'trigger_type': trigger_type,
        'trigger_metadata': trigger_metadata,
        'triggered_at': datetime.utcnow(),
        'status': 'started'
    })

    # Start retraining job (Airflow, Dagster, etc.)
    airflow_client.trigger_dag(
        dag_id='model_retraining_pipeline',
        conf={'trigger_type': trigger_type}
    )
```

**2. Retraining job steps**

```
1. Fetch latest training data (last N days)
2. Preprocess and validate
3. Train model with same hyperparameters
4. Evaluate on held-out test set
5. Register new model in registry
6. Compare to current production model
7. If better, promote to candidate stage
8. Trigger deployment pipeline
```

**3. Promotion gating**

```python
def gate_promotion(new_model, current_model, eval_set):
    """Decide whether to promote new model."""

    # Offline eval
    new_metrics = evaluate(new_model, eval_set)
    current_metrics = evaluate(current_model, eval_set)

    # Check for regression
    if new_metrics['auc'] < current_metrics['auc'] * 0.98:
        return 'reject', 'AUC regression detected'

    # Run regression suite
    regression_tests_passed = run_regression_suite(new_model)
    if not regression_tests_passed:
        return 'reject', 'Regression tests failed'

    # A/B test (online eval)
    ab_test_result = run_ab_test(new_model, current_model)
    if not ab_test_result.significant_improvement:
        return 'reject', 'No significant improvement in A/B test'

    # All gates passed
    return 'promote', 'All checks passed'
```

**4. Automated deployment**

```python
def automated_deployment(model_id):
    """Deploy model with canary rollout."""

    # Deploy to staging
    deploy_to_staging(model_id)

    # Validate staging
    if not validate_staging(model_id):
        rollback_staging(model_id)
        return

    # Deploy to production (canary)
    deploy_canary(model_id, traffic_pct=5)

    # Monitor for 24h
    time.sleep(86400)

    # Check metrics
    if canary_metrics_healthy(model_id):
        expand_canary(model_id, traffic_pct=50)
    else:
        rollback_canary(model_id)
        return

    # Monitor for 24h
    time.sleep(86400)

    # Full rollout
    if canary_metrics_healthy(model_id):
        promote_to_production(model_id)
    else:
        rollback_canary(model_id)
```

### Checklist

- [ ] Retraining triggers defined (time-based, event-based)
- [ ] Retraining pipeline automated
- [ ] Promotion gates configured (offline eval, regression suite, A/B test)
- [ ] Deployment automated (staging → canary → production)
- [ ] Rollback automated on failures
- [ ] All events logged in model registry

---

## Real-World Example: Recommendation Model Feedback Loop

### Context

**Model:** Product recommendations
**Retraining cadence:** Weekly
**Feedback signals:** Clicks, purchases, user ratings

### Feedback Collection

**1. Log predictions and outcomes**

```python
@app.post("/recommend")
def recommend(user_id: str):
    """Serve recommendations and log."""

    recommendations = model.predict(user_id)

    # Log prediction
    request_id = log_prediction(user_id, recommendations, 'model_v15')

    return {'recommendations': recommendations, 'request_id': request_id}

# User clicks on recommendation
@app.post("/click")
def track_click(request_id: str, item_id: str):
    """Track click event."""
    feedback_db.insert({
        'request_id': request_id,
        'event_type': 'click',
        'item_id': item_id,
        'timestamp': datetime.utcnow()
    })

# User purchases item
@app.post("/purchase")
def track_purchase(request_id: str, item_id: str):
    """Track purchase event (conversion)."""
    feedback_db.insert({
        'request_id': request_id,
        'event_type': 'purchase',
        'item_id': item_id,
        'timestamp': datetime.utcnow()
    })
```

**2. Aggregate online metrics**

```python
# Compute daily metrics
ctr = count_clicks / count_recommendations
purchase_rate = count_purchases / count_recommendations
avg_rating = mean(user_ratings)
```

### Retraining Pipeline

**Trigger:** Weekly (every Sunday at 2 AM)

**Steps:**
1. Fetch last 90 days of user interactions
2. Build training set (positive: clicked/purchased, negative: shown but not clicked)
3. Train collaborative filtering model
4. Evaluate on held-out users (last 7 days)
5. Compare to production model (v15)
6. If NDCG@10 improves by > 2%, promote to candidate

### A/B Test

**Setup:**
- Variant A: Production model (v15)
- Variant B: New model (v16)
- Traffic split: 50/50
- Primary metric: Purchase rate
- Secondary metrics: CTR, NDCG@10

**Results (after 7 days):**
- Variant A: Purchase rate = 2.3%
- Variant B: Purchase rate = 2.5%
- Lift: +8.7% (statistically significant, p < 0.01)
- Decision: Promote variant B to production

### Outcome

- Automated weekly retraining maintains model freshness
- Online A/B testing validates improvements before full rollout
- Purchase rate improved 8.7% after promoting v16

---

## Tools & Frameworks

**Experimentation platforms:**
- **Optimizely** (managed A/B testing)
- **LaunchDarkly** (feature flags + experimentation)
- **GrowthBook** (open-source A/B testing)
- **Statsig** (experimentation + feature flags)

**Labeling tools:**
- **Label Studio** (open-source annotation)
- **Prodigy** (active learning + annotation)
- **Scale AI** (managed labeling)
- **Labelbox** (annotation platform)

**Retraining automation:**
- **Airflow, Dagster, Prefect** (orchestration)
- **MLflow** (experiment tracking + model registry)
- **Kubeflow Pipelines** (Kubernetes-native ML pipelines)

---

## Related Resources

- [Monitoring Best Practices](monitoring-best-practices.md) - Metrics collection
- [Drift Detection Guide](drift-detection-guide.md) - Automated retraining triggers
- [Deployment Lifecycle](deployment-lifecycle.md) - Promotion workflows
- **External:** [ai-llm](../../ai-llm/SKILL.md) - Fine-tuning with human feedback

---

## References

- **A/B Testing Statistics:** https://www.exp-platform.com/Documents/2013-02-HEDS-ExPAsStatisticalParadigm.pdf
- **Experimentation at Scale (Netflix):** https://netflixtechblog.com/its-all-a-bout-testing-the-netflix-experimentation-platform-4e1ca458c15
- **Human-in-the-Loop ML:** https://arxiv.org/abs/2108.00941
- **Active Learning:** https://burrsettles.com/pub/settles.activelearning.pdf
