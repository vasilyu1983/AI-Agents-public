# Primitive: Link Prediction

**Sources**: Adamic & Adar (2003) Social Networks; Lü & Zhou (2011) Physica A; Newman (2010) §14.

## Definition

Link prediction infers which absent edges are most likely to exist (missing edges) or to form in the future (future edges) based on the current graph topology.

**Core similarity indices** (for nodes u and v):

| Index | Formula | Intuition |
|-------|---------|-----------|
| Common Neighbors | \|Γ(u) ∩ Γ(v)\| | Shared contacts |
| Jaccard | \|Γ(u) ∩ Γ(v)\| / \|Γ(u) ∪ Γ(v)\| | Shared contacts normalised by total |
| Adamic-Adar | Σ_{z ∈ Γ(u)∩Γ(v)} 1/log(kz) | Common neighbours weighted by rareness |
| Resource Allocation | Σ_{z ∈ Γ(u)∩Γ(v)} 1/kz | Neighbour transmits 1/degree fraction |
| Katz | Σ_l βˡ \|paths^(l)(u,v)\| | Weighted count of all paths (β ≪ 1) |
| SimRank | Recursive: two nodes are similar if their neighbours are similar | Global structural similarity |

**Embedding-based link prediction**: compute node embeddings (#10), then predict edge probability from embedding dot product or cosine similarity.

**Evaluation metric**: area under the ROC curve (AUC) on held-out removed edges. AUC=1 is perfect; AUC=0.5 is random guessing.

## When to Use

- Recommendation systems: "people you may know," "packages that are often used together"
- Knowledge graph completion: predict missing relations between entities
- Citation forecasting: which papers will cite each other in the next year
- Dependency graph analysis: detect likely but undeclared dependencies

## Inputs

- Current observed graph (snapshot)
- Optional: edge timestamps for temporal prediction
- Optional: node attributes for hybrid methods

## Outputs

- Ranked list of candidate edges sorted by predicted probability
- AUC score on held-out evaluation set

## Failure Modes

1. **Popularity bias**: high-degree nodes appear in almost every candidate pair. Always compute AUC on a balanced evaluation set (equal missing and non-missing edges).
2. **Ignoring graph sparsity**: most node pairs have zero common neighbours. Katz index and embedding methods handle sparsity better than local indices.
3. **Temporal leakage**: if evaluating future-link prediction, ensure the training graph snapshot strictly precedes the evaluation period (no future edges in training).
4. **Local indices fail for large-diameter graphs**: common neighbours is zero for most pairs in sparse or large-diameter graphs. Use Katz or embedding similarity instead.
5. **Symmetric assumptions on directed graphs**: link prediction should distinguish u→v from v→u on directed graphs. Common-neighbor indices are symmetric by default.

## Worked Example

**Academic co-authorship network**: 2,000 authors, 8,000 observed co-authorships. Hold out 10% of edges as test set. Results on test set (AUC):

| Method | AUC |
|--------|-----|
| Random | 0.50 |
| Common Neighbors | 0.72 |
| Adamic-Adar | 0.76 |
| Resource Allocation | 0.78 |
| node2vec similarity | 0.84 |

Adamic-Adar outperforms Common Neighbors because it down-weights highly connected common authors (conference organizers) who appear in many pairs but signal weak collaboration likelihood.

## Sources

- Adamic and Adar (2003). Friends and neighbors on the Web. Social Networks. [doi:10.1016/S0378-8733(03)00009-1](https://doi.org/10.1016/S0378-8733(03)00009-1)
- Lü and Zhou (2011). Link prediction in complex networks: A survey. Physica A. [doi:10.1016/j.physa.2010.11.027](https://doi.org/10.1016/j.physa.2010.11.027)
- Newman (2010). Networks: An Introduction. §14.

## Related

- [`10-graph-embeddings.md`](10-graph-embeddings.md) — node2vec and GNN embeddings for embedding-based link prediction
- [`03-community-detection.md`](03-community-detection.md) — community membership as a feature for link prediction
