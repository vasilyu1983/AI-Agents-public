# Drift Detection Guide

A structured approach to detecting and responding to data and concept drift in production ML/LLM/RAG.

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
