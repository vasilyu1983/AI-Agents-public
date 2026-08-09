# Drift Detection Guide

A structured approach to detecting and responding to data and concept drift in production ML/LLM/RAG.

Use this when production behavior has shifted and you need to decide whether to alert, retrain, rollback, or investigate further.

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [1. Types of Drift](#1-types-of-drift)
- [A. Feature Drift (Covariate Drift)](#a-feature-drift-covariate-drift)
- [B. Label Drift](#b-label-drift)
- [C. Concept Drift](#c-concept-drift)
- [D. Embedding Drift (LLM/RAG)](#d-embedding-drift-llmrag)
- [2. Drift Metrics](#2-drift-metrics)
- [Numerical Features](#numerical-features)
- [Categorical Features](#categorical-features)
- [Embeddings (LLM/RAG Drift)](#embeddings-llmrag-drift)
- [3. Drift Detection Workflow](#3-drift-detection-workflow)
- [4. Drift Response Checklist](#4-drift-response-checklist)
- [5. Judgment: Avoiding Alert Fatigue](#5-judgment-avoiding-alert-fatigue)

## Quick Navigation

- [Types of Drift](#1-types-of-drift)
- [Drift Metrics](#2-drift-metrics)
- [Drift Detection Workflow](#3-drift-detection-workflow)
- [Drift Response Checklist](#4-drift-response-checklist)
- [Judgment: Avoiding Alert Fatigue](#5-judgment-avoiding-alert-fatigue)

---

## 1. Types of Drift

### A. Feature Drift (Covariate Drift)

Distribution of inputs shifts.

### B. Label Drift

Target distribution changes.

### C. Concept Drift

Relationship between features and target changes.

### D. Embedding Drift (LLM/RAG)

Embedding geometry shifts due to changes in:

- Document corpus updates (new content, removed content)
- Vocabulary evolution (new terms, jargon, abbreviations)
- Query pattern changes (user behavior shifts)
- Model updates (embedding model version changes)

**Why embedding drift matters for LLMs:**

- RAG retrieval quality degrades silently
- Semantic search relevance drops
- Clustering-based features become unreliable
- Fine-tuned model performance declines

---

## 2. Drift Metrics

### Numerical Features

- PSI (Population Stability Index)
- KS test
- Wasserstein distance
- Mean/variance deltas

### Categorical Features

- Chi-squared distance
- Jensen-Shannon divergence

### Embeddings (LLM/RAG Drift)

**Centroid-based metrics:**

- Centroid drift (L2 distance between baseline and current centroids)
- Cosine cluster deviation (angle change in cluster centers)

**Distribution-based metrics:**

- Average pairwise cosine similarity shift
- Embedding space density changes (k-NN distance distributions)
- PCA/UMAP projection drift (visual + quantitative)

**Implementation example:**

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingDriftDetector:
    def __init__(self, baseline_embeddings: np.ndarray):
        self.baseline_centroid = baseline_embeddings.mean(axis=0)
        self.baseline_pairwise_sim = self._avg_pairwise_sim(baseline_embeddings)

    def _avg_pairwise_sim(self, embeddings: np.ndarray, sample_size: int = 1000) -> float:
        """Compute average pairwise cosine similarity (sampled for efficiency)."""
        if len(embeddings) > sample_size:
            idx = np.random.choice(len(embeddings), sample_size, replace=False)
            embeddings = embeddings[idx]
        sim_matrix = cosine_similarity(embeddings)
        # Exclude diagonal (self-similarity)
        return (sim_matrix.sum() - len(embeddings)) / (len(embeddings) * (len(embeddings) - 1))

    def detect_drift(self, current_embeddings: np.ndarray) -> dict:
        current_centroid = current_embeddings.mean(axis=0)

        # Centroid drift (L2)
        centroid_drift = np.linalg.norm(current_centroid - self.baseline_centroid)

        # Cosine similarity of centroids
        centroid_cosine = cosine_similarity(
            [self.baseline_centroid], [current_centroid]
        )[0][0]

        # Pairwise similarity shift
        current_pairwise_sim = self._avg_pairwise_sim(current_embeddings)
        pairwise_shift = abs(current_pairwise_sim - self.baseline_pairwise_sim)

        return {
            'centroid_l2_drift': centroid_drift,
            'centroid_cosine_sim': centroid_cosine,
            'pairwise_sim_shift': pairwise_shift,
            'drift_detected': centroid_cosine < 0.95 or pairwise_shift > 0.05
        }
```

**Thresholds for embedding drift:**

| Metric | Warning | Critical |
|--------|---------|----------|
| Centroid cosine similarity | <0.97 | <0.95 |
| Pairwise similarity shift | >0.03 | >0.05 |
| Centroid L2 drift | >0.5 | >1.0 |

---

## 3. Drift Detection Workflow

1. **Baseline snapshot**
   - Freeze training distribution stats

2. **Continuous monitoring**
   - Compare batch windows to baseline

3. **Thresholding**
   - PSI > 0.2 = moderate drift  
   - PSI > 0.3 = severe drift  

4. **Alerting**
   - Trigger only if sustained over N windows

5. **Triage**
   - Check upstream pipelines
   - Check feature store integrity
   - Check data freshness delays

6. **Response**
   - Retrain  
   - Adjust threshold  
   - Temporarily fallback to baseline model  
   - Fix upstream issue  

---

## 4. Drift Response Checklist

- [ ] Drift source identified (data upstream, concept change)
- [ ] Verified not a transient spike
- [ ] Business impact evaluated
- [ ] Retrain or rollback decision made
- [ ] Documentation updated

---

## 5. Judgment: Avoiding Alert Fatigue

Statistical drift tests are cheap to run and easy to over-alert on. PSI, KS, and chi-squared tests all become *more* sensitive as sample size grows — at production traffic volumes, a KS test will flag a p-value < 0.01 for distribution shifts too small to move any business metric. The expert failure mode here is not "missing drift," it's drowning the on-call rotation in statistically-real but practically-irrelevant alerts until they stop reading them (the same fatigue dynamic as security or observability alerting). A few judgment calls that separate a monitoring system people trust from one they mute:

- **Gate on sample size, not just p-value.** With enough rows, trivial shifts are "significant." Prefer effect-size metrics with fixed thresholds (PSI, Wasserstein distance, Jensen-Shannon divergence) over raw p-values for high-volume features, and reserve p-value tests for lower-traffic segments where sample size is naturally bounded.
- **Require drift + downstream signal to co-occur before paging.** Feature drift alone should open a ticket, not wake someone up. Page only when drift coincides with a performance-proxy signal (delayed-label metric drop, prediction-distribution shift, business KPI move) — this single filter eliminates the majority of false pages from benign, self-correcting shifts (seasonality, a marketing campaign, a one-off upstream backfill).
- **Distinguish recurring/seasonal drift from novel drift.** A retailer's feature distributions shift every Black Friday and every January; a fraud model's shift after a new payment rail launches. Baseline against a rolling comparable period (same week last year, last N complete cycles) for known-seasonal features instead of a single frozen training-time snapshot, or you will alert on the same predictable pattern every cycle.
- **Widen the window before escalating severity.** A single window breaching threshold is noise; require N consecutive windows (or a sustained trend) before treating drift as actionable, and say explicitly in the runbook how many windows and what the escalation path is for each severity tier.
- **Revisit thresholds on a schedule, not by feel.** Thresholds set at launch decay in relevance as the underlying population, product, or upstream systems change. Review PSI/KS thresholds quarterly against realized false-positive and false-negative rates rather than leaving them as launch-day defaults indefinitely.
- **Every alert must map to a decision, not just a notification.** If an alert fires and the response is "note it and move on" more than a handful of times, the threshold is miscalibrated — tune it down, add the co-occurrence gate above, or remove the alert. An alert with no decision attached is training the team to ignore the next one.
