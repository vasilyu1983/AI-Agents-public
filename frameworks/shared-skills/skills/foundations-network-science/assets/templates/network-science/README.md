# Network-Science Primitives — Composition Guide

11 domain-agnostic network-science primitives. Each file is a standalone playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-centrality-measures.md](01-centrality-measures.md) | Wrong centrality used — high degree ≠ high betweenness ≠ high influence |
| 2 | [02-pagerank.md](02-pagerank.md) | Naive in-degree conflates volume with endorsement-weighted authority |
| 3 | [03-community-detection.md](03-community-detection.md) | Arbitrary k-means on node features ignores graph topology |
| 4 | [04-small-world.md](04-small-world.md) | Assuming large graphs are either fully random or fully regular |
| 5 | [05-scale-free-networks.md](05-scale-free-networks.md) | Scale-free claimed without statistical test on degree distribution |
| 6 | [06-percolation.md](06-percolation.md) | Phase-transition fragility ignored — small targeted removals can catastrophically fragment |
| 7 | [07-contagion-sir.md](07-contagion-sir.md) | Linear or mean-field spread assumptions on heterogeneous graphs |
| 8 | [08-link-prediction.md](08-link-prediction.md) | Random or popularity-based missing-edge inference |
| 9 | [09-graph-clustering.md](09-graph-clustering.md) | Treating graph partitioning as unstructured k-means |
| 10 | [10-graph-embeddings.md](10-graph-embeddings.md) | One-hot node encodings discard all structural information |
| 11 | [11-temporal-networks.md](11-temporal-networks.md) | Aggregating time-stamped edges discards causal ordering |

---

## Domain Scenario Stacks

### AI-Search Citation Flow

- **Objective**: rank documents and authors by structural authority; surface topical communities
- **Stack**: #2 (PageRank — authority via directed citation edges) + #3 (Louvain community detection on undirected projection) + #1 (eigenvector centrality for hub authors)
- **Add if temporal data available**: #11 (temporal-network paths for recency weighting)

### Dependency Graph Blast Radius

- **Objective**: estimate change impact, identify critical bridges, group tightly-coupled modules
- **Stack**: #2 (reverse PageRank — transitive dependents) + #1 (betweenness — bridges) + #3 (community detection — blast clusters) + #6 (percolation — fragility threshold)

### Audience Reach Forecast

- **Objective**: predict spread from a seed set in a social or content network
- **Stack**: #5 (degree distribution test — scale-free?) + #7 (SIR — Monte Carlo spread) + #6 (percolation threshold — R₀ check) + #2 (PageRank — seed selection)

### Recommendation / Knowledge Graph

- **Objective**: infer missing edges and represent nodes for downstream ML
- **Stack**: #8 (Adamic-Adar or Katz for link prediction) + #10 (node2vec or GNN embeddings) + #3 (community detection for candidate filtering)

### Network Robustness Audit

- **Objective**: identify vulnerabilities and design targeted vs. random removal strategies
- **Stack**: #6 (percolation — threshold and giant component) + #1 (degree / betweenness for attack strategy) + #5 (scale-free test — hub concentration)

### Temporal Spread Analysis

- **Objective**: understand how bursty contact patterns change reachability vs. static predictions
- **Stack**: #11 (temporal-network paths) + #7 (SIR with temporal contact sequence) + #4 (small-world baseline for comparison)

---

## Related

- [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md) — full anti-patterns by domain and decision checklist
- [`../../../data/sources.json`](../../../data/sources.json) — primary papers and textbooks
