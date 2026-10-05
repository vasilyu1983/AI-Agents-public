# User Feedback & Relevance Learning

Operational patterns for collecting user signals and improving search with feedback loops.

---
## Table of Contents

- [Overview](#overview)
- [Pattern 1: Signal Capture](#pattern-1-signal-capture)
- [Primary Signals](#primary-signals)
- [Implementation](#implementation)
- [Pattern 2: Label Generation](#pattern-2-label-generation)
- [Converting Signals to Labels](#converting-signals-to-labels)
- [Hard Negative Sampling](#hard-negative-sampling)
- [Pattern 3: Online Experimentation](#pattern-3-online-experimentation)
- [Interleaving (Team Draft)](#interleaving-team-draft)
- [Guardrails & Abort Criteria](#guardrails--abort-criteria)
- [Exploration: Testing What You Never Show](#exploration-testing-what-you-never-show)
- [Monitoring thresholds](#monitoring-thresholds)
- [Pattern 4: Reranker Training with Feedback](#pattern-4-reranker-training-with-feedback)
- [Training Loop](#training-loop)
- [Collect feedback data](#collect-feedback-data)
- [Train reranker (cross-encoder fine-tuning)](#train-reranker-cross-encoder-fine-tuning)
- [Model Versioning](#model-versioning)
- [Tag each model version](#tag-each-model-version)
- [Log model/index versions with queries](#log-modelindex-versions-with-queries)
- [Pattern 5: Continuous Monitoring](#pattern-5-continuous-monitoring)
- [Metrics Dashboard](#metrics-dashboard)
- [Alerting](#alerting)
- [Alert conditions](#alert-conditions)
- [Eval Set Protection](#eval-set-protection)
- [Filter eval set](#filter-eval-set)
- [Feedback Learning Quality Checklist](#feedback-learning-quality-checklist)
- [Cross-References](#cross-references)


## Overview

Use feedback learning when:
- Search is deployed in production
- User interactions are logged
- Need to continuously improve relevance
- Have sufficient traffic for signals

---

## Pattern 1: Signal Capture

### Primary Signals

**Explicit signals:**
- Clicks on results
- Dwell time / scroll depth
- Query reformulations
- Result edits or corrections
- Explicit thumbs up/down

**Implicit signals:**
- Search abandonment (no clicks)
- Quick backs (click + immediate return)
- Deep engagement (long dwell time)
- Query-to-conversion events

### Implementation

```python
class SearchSignalLogger:
    def log_interaction(
        self,
        query_id: str,
        user_id: str,
        query: str,
        results: list,
        interactions: dict
    ):
        """
        interactions = {
            'clicked_doc_ids': ['doc1', 'doc3'],
            'dwell_times': {'doc1': 45, 'doc3': 120},  # seconds
            'abandoned': False,
            'reformulated_to': 'new query text',
            'timestamp': '2024-11-22T10:30:00Z'
        }
        """
        signal = {
            'query_id': query_id,
            'user_id': hash_user_id(user_id),  # Privacy
            'query': query,
            'results': [r['doc_id'] for r in results],
            'interactions': interactions,
            'timestamp': interactions['timestamp']
        }

        # Apply privacy filters
        if self.contains_pii(signal):
            signal = self.sanitize_pii(signal)

        # Store for learning
        self.signal_store.append(signal)
```

**Privacy Checklist**
- [ ] User IDs hashed or anonymized
- [ ] PII detection and scrubbing
- [ ] Compliance with data retention policies
- [ ] User opt-out respected
- [ ] Aggregate-only analysis for sensitive queries

The privacy checklist protects users from your logs. It does not protect your ranking
model from your users — signals are a crowdsourced input and therefore an attack surface.
Pair it with the Adversarial Signal Checklist in
[`click-models-and-bias-correction.md`](click-models-and-bias-correction.md#adversarial-signal-checklist),
whose central control is per-user deduplication at aggregation time.

Per-user dedup needs a stable identifier. If the data-governance decision allows
that signal, use a scoped pseudonymous ID with access and retention limits;
hashing alone does not make the record anonymous. If user-level collection is
not allowed, keep aggregate signals and do not claim per-user vote protection.

---

## Pattern 2: Label Generation

### Converting Signals to Labels

**Use a click model, not a dwell-time heuristic.** The method is
[`click-models-and-bias-correction.md`](click-models-and-bias-correction.md): SDBN
examine-marking to strip position bias (Pattern CM-1), then a beta prior to stop sparse
rows grading 1.0 (Pattern CM-2). That file is the implementation; this section covers
only when a simpler heuristic is defensible and what it costs you.

**Heuristic labelling (fallback only):**

```python
def signal_to_label(interaction, result_position):
    """
    Dwell-based relevance label (0-2). NOT position-bias corrected —
    a click at rank 1 and a click at rank 9 are scored identically,
    and an unclicked rank-1 result is graded the same as an unclicked
    rank-5 result the user never scrolled to.

    Defensible only for: cold start before session logs accumulate, or
    surfaces with a single result per page (no ranked list, no position
    bias to correct). Replace with SDBN as soon as you have per-session
    rank + click data.
    """
    doc_id = interaction['doc_id']

    # Not clicked and seen → label 0 (not relevant)
    if doc_id not in interaction['clicked_doc_ids'] and result_position <= 5:
        return 0

    # Clicked with short dwell → label 1 (somewhat relevant)
    if doc_id in interaction['clicked_doc_ids']:
        dwell = interaction['dwell_times'].get(doc_id, 0)
        if dwell < 10:
            return 1  # Quick back

    # Clicked with deep engagement → label 2 (highly relevant)
    if doc_id in interaction['clicked_doc_ids']:
        dwell = interaction['dwell_times'].get(doc_id, 0)
        if dwell >= 30:
            return 2

    # Default: unlabeled
    return None
```

The `result_position <= 5` cutoff above is a stand-in for an examine: an admission that
you cannot penalise a document the user never looked at. SDBN replaces that guess with
a per-session determination — every result at or above the session's last click counts as
examined — which is both more accurate and free of a magic constant.

### Hard Negative Sampling

```python
def sample_hard_negatives(query, clicked_docs, all_results, k=5):
    """
    Sample documents ranked high but not clicked (hard negatives)
    """
    hard_negatives = []
    for i, doc in enumerate(all_results[:20]):
        if doc['doc_id'] not in clicked_docs and i < 10:
            hard_negatives.append({
                'query': query,
                'doc_id': doc['doc_id'],
                'label': 0,  # Not clicked despite high rank
                'position': i
            })
            if len(hard_negatives) >= k:
                break

    return hard_negatives
```

**Checklist**
- [ ] Signal → label mapping validated with human review
- [ ] Hard negatives sampled from top-k results
- [ ] Position bias corrected via SDBN examines, not a rank cutoff ([CM-1](click-models-and-bias-correction.md#pattern-cm-1-sdbn--correcting-position-bias-with-examines))
- [ ] Confidence bias corrected via beta prior, so sparse rows cannot grade 1.0 ([CM-2](click-models-and-bias-correction.md#pattern-cm-2-beta-prior--correcting-confidence-bias))
- [ ] Signals deduplicated per user before aggregation ([CM-4](click-models-and-bias-correction.md#pattern-cm-4-signal-spam-defence))
- [ ] Pairwise preferences extracted for learning-to-rank ([learning-to-rank-pipeline.md](learning-to-rank-pipeline.md))

---

## Pattern 3: Online Experimentation

### Interleaving (Team Draft)

**Use when:** Testing ranking changes without full traffic split

```python
def team_draft_interleaving(baseline_results, variant_results, k=10):
    """
    Interleave two rankings for unbiased comparison
    """
    interleaved = []
    baseline_pool = baseline_results[:k]
    variant_pool = variant_results[:k]

    teams = {'baseline': [], 'variant': []}

    while len(interleaved) < k:
        # Alternate selection
        if len(interleaved) % 2 == 0:
            # Pick from baseline
            for doc in baseline_pool:
                if doc['doc_id'] not in [d['doc_id'] for d in interleaved]:
                    interleaved.append(doc)
                    teams['baseline'].append(doc['doc_id'])
                    break
        else:
            # Pick from variant
            for doc in variant_pool:
                if doc['doc_id'] not in [d['doc_id'] for d in interleaved]:
                    interleaved.append(doc)
                    teams['variant'].append(doc['doc_id'])
                    break

    return interleaved, teams

def evaluate_interleaving(clicked_docs, teams):
    """
    Determine which ranking won
    """
    baseline_clicks = sum(1 for doc in clicked_docs if doc in teams['baseline'])
    variant_clicks = sum(1 for doc in clicked_docs if doc in teams['variant'])

    if baseline_clicks > variant_clicks:
        return 'baseline'
    elif variant_clicks > baseline_clicks:
        return 'variant'
    else:
        return 'tie'
```

### Guardrails & Abort Criteria

```python
# Monitoring thresholds
guardrails = {
    'ctr_drop_threshold': -0.05,  # -5% CTR → abort
    'nrr_increase_threshold': 0.10,  # +10% no-result rate → abort
    'latency_p95_threshold': 1.5,  # 1.5x latency → abort
    'min_sample_size': 1000  # Minimum queries before decision
}

def should_abort_experiment(variant_metrics, baseline_metrics, guardrails):
    """
    Check if experiment should be aborted
    """
    if variant_metrics['num_queries'] < guardrails['min_sample_size']:
        return False  # Not enough data yet

    # CTR degradation
    ctr_change = (variant_metrics['ctr'] - baseline_metrics['ctr']) / baseline_metrics['ctr']
    if ctr_change < guardrails['ctr_drop_threshold']:
        return True

    # No-result rate increase
    nrr_change = variant_metrics['nrr'] - baseline_metrics['nrr']
    if nrr_change > guardrails['nrr_increase_threshold']:
        return True

    # Latency regression
    latency_ratio = variant_metrics['p95_latency'] / baseline_metrics['p95_latency']
    if latency_ratio > guardrails['latency_p95_threshold']:
        return True

    return False
```

### Exploration: Testing What You Never Show

Interleaving and A/B tests compare two rankings over the documents your system already
surfaces. Neither can tell you anything about documents that have never been shown —
those generate no clicks, so they never earn a rank, so they are never shown. That is
**presentation bias**, and it is a coverage problem in the training data rather than a
measurement problem in the experiment.

Fixing it means deliberately showing results the current model would not have chosen, on
a bounded slice of traffic, and feeding the resulting clicks back as judgments. Method and
tuning — ad-hoc diversification versus Gaussian-process-driven candidate selection — are in
[`click-models-and-bias-correction.md`](click-models-and-bias-correction.md#pattern-cm-3-exploration--correcting-presentation-bias)
Pattern CM-3.

Two operational notes for this file's scope:

- Exploration is a live-traffic intervention that can degrade relevance for the users in
  the slice. The guardrails and abort criteria above apply to it unchanged — wire it as an
  experiment arm, not as an always-on ranking tweak.
- Interleaving and exploration are complementary, not alternatives. Interleaving tells you
  which of two rankings is better; exploration widens the set of documents either ranking
  is able to consider next cycle.

**Checklist**
- [ ] Interleaving/bandit algorithm selected
- [ ] Guardrails defined per metric
- [ ] Auto-abort on critical regressions
- [ ] Sample size calculated for statistical power
- [ ] Exploration slice sized and bounded, under the same guardrails
- [ ] Exploration clicks flow back into judgment generation, not just into metrics

---

## Pattern 4: Reranker Training with Feedback

This pattern retrains the reranker in a periodic batch — feedback accumulates, then a training run consumes it. That is the right shape when the thing being updated is a model. If instead you're maintaining a per-element trust/authority score (not a model) and want it to move continuously with each feedback event rather than waiting on a training cycle, see [confidence-scoring.md P-CS-5](../../ai-rag/references/confidence-scoring.md#p-cs-5--streaming-trust-update-per-element-ema-no-retrain) — a streaming EMA update with O(1) cost per event and no retrain step.

### Training Loop

```python
# Collect feedback data
feedback_dataset = []
for interaction in signals:
    query = interaction['query']
    for i, doc_id in enumerate(interaction['results']):
        label = signal_to_label(interaction, position=i)
        if label is not None:
            feedback_dataset.append({
                'query': query,
                'doc_id': doc_id,
                'label': label,
                'features': extract_features(query, doc_id)
            })

# Train reranker (cross-encoder fine-tuning)
from sentence_transformers import CrossEncoder, InputExample

train_examples = [
    InputExample(texts=[d['query'], get_doc_text(d['doc_id'])], label=d['label'])
    for d in feedback_dataset
]

model = CrossEncoder('ms-marco-TinyBERT-L-2-v2')
model.fit(
    train_dataloader=DataLoader(train_examples, batch_size=16),
    epochs=3,
    warmup_steps=100
)
```

### Model Versioning

```python
# Tag each model version
model_version = {
    'model_id': 'reranker-v2.3',
    'trained_on': '2024-11-22',
    'training_samples': len(feedback_dataset),
    'eval_ndcg@10': 0.82,
    'deployed': True
}

# Log model/index versions; query text below is illustrative and requires an
# approved query-text logging decision, redaction, access, and retention controls.
query_log = {
    'query_id': 'q123',
    'query': 'example query',
    'model_version': 'reranker-v2.3',
    'index_version': 'index-2024-11-20',
    'timestamp': '2024-11-22T10:30:00Z'
}
```

**Checklist**
- [ ] Fresh feedback integrated regularly (weekly/monthly)
- [ ] Eval sets protected from contamination
- [ ] Model versions tracked and logged
- [ ] A/B tested before full rollout

---

## Pattern 5: Continuous Monitoring

### Metrics Dashboard

Track these sliced by time (hourly, daily):

```python
dashboard_metrics = {
    'retrieval_quality': {
        'ctr': 0.65,
        'nrr': 0.03,
        'avg_dwell_time': 45,
        'reformulation_rate': 0.20
    },
    'performance': {
        'p50_latency': 120,
        'p95_latency': 350,
        'p99_latency': 800,
        'qps': 1500
    },
    'data_freshness': {
        'index_lag_minutes': 15,
        'embedding_version': 'v1.2',
        'last_reindex': '2024-11-20T08:00:00Z'
    }
}
```

### Alerting

```python
# Alert conditions
alerts = [
    {
        'metric': 'ctr',
        'condition': 'ctr < 0.55',
        'severity': 'warning',
        'action': 'Investigate query logs'
    },
    {
        'metric': 'nrr',
        'condition': 'nrr > 0.08',
        'severity': 'critical',
        'action': 'Check index health'
    },
    {
        'metric': 'p95_latency',
        'condition': 'p95_latency > 500',
        'severity': 'warning',
        'action': 'Scale resources'
    }
]
```

**Checklist**
- [ ] Online metrics wired (CTR, NRR, dwell, reformulation)
- [ ] Dashboards sliced by query type, domain, language
- [ ] Alerts configured with runbooks
- [ ] Weekly review of metric trends

---

## Eval Set Protection

Prevent contamination:

```python
def is_contaminated(eval_query, production_logs, window_days=30):
    """
    Check if eval query appears in recent production logs
    """
    recent_queries = get_queries_in_window(production_logs, window_days)

    # Hash queries for comparison
    eval_hash = hash(eval_query.lower().strip())

    if eval_hash in [hash(q.lower().strip()) for q in recent_queries]:
        return True

    return False

# Filter eval set
clean_eval_set = [
    q for q in eval_set
    if not is_contaminated(q['query'], production_logs)
]
```

**Checklist**
- [ ] Eval queries not in production logs
- [ ] Hash-based contamination check
- [ ] Periodic eval set refresh (quarterly)
- [ ] Human review of new eval queries

---

## Feedback Learning Quality Checklist

- [ ] Feedback capture + privacy filters in place
- [ ] Pairwise/graded datasets refreshed regularly
- [ ] Online interleaving/bandits with abort rules
- [ ] Reranker updates versioned and regression-tested
- [ ] Metrics dashboards live with alerting
- [ ] Eval contamination checks automated
- [ ] Runbooks for common failure modes
- [ ] Judgments debiased before training (position, confidence, spam)
- [ ] Exploration running so training data covers more than the current ranker shows

---

## Cross-References

- [`click-models-and-bias-correction.md`](click-models-and-bias-correction.md) — the method behind Pattern 2's labels: SDBN examines, beta-prior confidence damping, exploration, and signal-spam defence.
- [`learning-to-rank-pipeline.md`](learning-to-rank-pipeline.md) — the six-step pipeline that consumes these judgments; Pattern 3's guardrails gate its deployment step.
- [`ranking-pipeline-guide.md`](../../ai-rag/references/ranking-pipeline-guide.md) — where a retrained reranker sits in the serving path.
- [`confidence-scoring.md`](../../ai-rag/references/confidence-scoring.md) P-CS-5 — streaming per-element trust updates; contrast with Pattern 4's batch retraining.
- [`search-evaluation-guide.md`](search-evaluation-guide.md) — offline metrics for judging a new model or judgment list.
