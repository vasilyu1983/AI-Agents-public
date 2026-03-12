# User Feedback & Relevance Learning

Operational patterns for collecting user signals and improving search with feedback loops.

---

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

---

## Pattern 2: Label Generation

### Converting Signals to Labels

**Graded relevance from signals:**

```python
def signal_to_label(interaction, result_position):
    """
    Convert user interaction to relevance label (0-2)
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
- [ ] Position bias corrected (clicks on top positions inflated)
- [ ] Pairwise preferences extracted for learning-to-rank

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

**Checklist**
- [ ] Interleaving/bandit algorithm selected
- [ ] Guardrails defined per metric
- [ ] Auto-abort on critical regressions
- [ ] Sample size calculated for statistical power

---

## Pattern 4: Reranker Training with Feedback

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

# Log model/index versions with queries
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
