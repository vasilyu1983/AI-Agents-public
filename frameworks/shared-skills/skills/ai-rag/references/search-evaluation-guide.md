# Search Evaluation Guide

Comprehensive guide to measuring and improving search quality.

---

## Core Metrics

### nDCG@k (Normalized Discounted Cumulative Gain)

**Use when:** Graded relevance (highly relevant, somewhat relevant, not relevant)

**Formula:**
```
DCG@k = Σ (2^rel_i - 1) / log2(i + 1)
nDCG@k = DCG@k / IDCG@k
```

**Interpretation:**
- 1.0 = perfect ranking
- 0.7-0.9 = good ranking
- <0.5 = poor ranking

---

### MRR (Mean Reciprocal Rank)

**Use when:** Only first relevant result matters (navigational queries)

**Formula:**
```
MRR = 1/N * Σ (1 / rank_i)
```

**Interpretation:**
- 1.0 = relevant result always first
- 0.5 = relevant result at rank 2 on average

---

### Recall@K

**Use when:** Need to measure coverage of relevant documents

**Formula:**
```
Recall@K = (# relevant docs in top K) / (total # relevant docs)
```

**Target:** 0.85-0.95 for most applications

---

### Precision@K

**Use when:** Need to measure result quality

**Formula:**
```
Precision@K = (# relevant docs in top K) / K
```

**Target:** 0.7-0.9 for most applications

---

## Evaluation Process

### Step 1: Build Labeled Dataset

**Requirements:**
- 20-200 queries (minimum 50 for statistical significance)
- Balanced across query types (keyword, semantic, mixed)
- Multiple relevance grades (0=not relevant, 1=somewhat, 2=highly)
- Representative of production traffic

**Collection methods:**
1. Manual labeling (gold standard)
2. Crowdsourced labels (with quality control)
3. Implied labels from clicks/dwell time
4. LLM-generated labels (validate with human review)

**Checklist**
- [ ] ≥50 queries covering main use cases
- [ ] Multiple graders for inter-annotator agreement
- [ ] Hard negatives included (topically related but not relevant)
- [ ] Edge cases represented (ambiguous, multi-intent queries)

---

### Step 2: Test Variants

Compare these configurations:

**Baseline variants:**
- BM25 only (k1=1.2, b=0.75)
- Dense vector only (HNSW)
- Hybrid (BM25 + vector)

**Advanced variants:**
- Hybrid + reranking
- Hybrid + query rewriting
- Full pipeline (rewrite + hybrid + rerank)

**Checklist**
- [ ] Baseline documented
- [ ] Each variant changes ONE component
- [ ] Metrics computed per variant
- [ ] Statistical significance tested

---

### Step 3: Compute Metrics

Run evaluation script:

```python
from sklearn.metrics import ndcg_score
import numpy as np

def evaluate_search(results, labels, k=10):
    """
    results: list of dicts with 'doc_id' and 'score'
    labels: dict mapping doc_id -> relevance grade (0-2)
    """
    # Extract relevance grades in ranked order
    y_true = [labels.get(r['doc_id'], 0) for r in results[:k]]
    y_score = [r['score'] for r in results[:k]]

    # nDCG@k
    ndcg = ndcg_score([y_true], [y_score], k=k)

    # Recall@k
    relevant_retrieved = sum(1 for grade in y_true if grade > 0)
    total_relevant = sum(1 for grade in labels.values() if grade > 0)
    recall = relevant_retrieved / total_relevant if total_relevant > 0 else 0

    # Precision@k
    precision = relevant_retrieved / k

    # MRR
    first_relevant = next((i for i, grade in enumerate(y_true) if grade > 0), None)
    mrr = 1.0 / (first_relevant + 1) if first_relevant is not None else 0

    return {
        'ndcg@k': ndcg,
        'recall@k': recall,
        'precision@k': precision,
        'mrr': mrr
    }
```

**Checklist**
- [ ] Metrics computed per query
- [ ] Aggregated across query set (mean, median, std)
- [ ] Sliced by query type
- [ ] Outliers investigated

---

### Step 4: Plot Results

**Recommended visualizations:**

1. **Recall curves** (recall vs K)
2. **Precision-Recall curves**
3. **Latency vs Recall tradeoff**
4. **nDCG by query type** (bar chart)

---

## Evaluation Slicing

Slice metrics by:

### Query Type
- Keyword queries
- Semantic queries
- Multi-intent queries
- Navigational queries

### Document Type
- Technical docs
- Marketing content
- Product specs
- Support articles

### Query Characteristics
- Short queries (1-3 words)
- Long queries (>5 words)
- Rare terms vs common terms

**Checklist**
- [ ] Slices defined before evaluation
- [ ] ≥20 queries per slice (for significance)
- [ ] Underperforming slices identified
- [ ] Root cause analysis completed

---

## Statistical Significance Testing

Use paired t-test to compare variants:

```python
from scipy.stats import ttest_rel

def is_significant(baseline_metrics, variant_metrics, alpha=0.05):
    """
    baseline_metrics: list of metric values per query (baseline)
    variant_metrics: list of metric values per query (variant)
    """
    t_stat, p_value = ttest_rel(baseline_metrics, variant_metrics)

    return {
        'p_value': p_value,
        'significant': p_value < alpha,
        'improvement': np.mean(variant_metrics) - np.mean(baseline_metrics),
        'relative_improvement': (np.mean(variant_metrics) - np.mean(baseline_metrics)) / np.mean(baseline_metrics)
    }
```

**Checklist**
- [ ] ≥30 queries for statistical power
- [ ] Paired comparison (same queries for both variants)
- [ ] p < 0.05 for significance
- [ ] Effect size meaningful (≥5% relative improvement)

---

## Continuous Evaluation

### Online Metrics

Track in production:

- **Click-through rate (CTR)** - % queries with click
- **No-result rate (NRR)** - % queries with zero results
- **Dwell time** - Time spent on clicked result
- **Reformulation rate** - % queries followed by refinement

### Monitoring

```python
# Example monitoring dashboard
metrics = {
    'ctr': 0.65,  # Target: >0.6
    'nrr': 0.03,  # Target: <0.05
    'avg_dwell_time': 45,  # Target: >30s
    'reformulation_rate': 0.20  # Target: <0.3
}
```

**Checklist**
- [ ] Online metrics tracked per-query
- [ ] Alerts configured for degradation
- [ ] A/B testing framework in place
- [ ] Offline/online correlation validated

---

## Degradation Alerts

Define thresholds:

| Metric | Warning | Critical |
|--------|---------|----------|
| nDCG@10 | -5% | -10% |
| Recall@10 | -10% | -20% |
| CTR | -5% | -15% |
| NRR | +50% | +100% |
| Latency p95 | +20% | +50% |

**Checklist**
- [ ] Baselines established
- [ ] Thresholds defined per metric
- [ ] Auto-rollback on critical degradation
- [ ] Runbook for investigating alerts

---

## Evaluation Quality Checklist

- [ ] ≥50 labeled queries
- [ ] Multiple relevance grades (0-2)
- [ ] Baseline documented and stable
- [ ] Statistical significance tested
- [ ] Per-slice metrics computed
- [ ] Online/offline correlation validated
- [ ] Degradation alerts configured
- [ ] Regular eval set refresh (quarterly)
