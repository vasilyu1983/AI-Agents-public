# Network Science Patterns, Scenarios, and Traps

Use this reference before shipping graph rankings, communities, diffusion forecasts, blast-radius analyses, or embedding-based recommendations.

## Core Patterns

| Pattern | Use When | Watch For |
|---------|----------|-----------|
| Graph semantics first | A dataset is converted into nodes and edges | Edge meaning drift or projection artifacts |
| Centrality by question | Someone asks for "most important" nodes | Importance may mean hub, bridge, authority, or spreader |
| Baseline comparison | Claiming small-world, scale-free, or community structure | Need null model or alternative distribution |
| Stability check | Ranking or clustering drives decisions | Sensitivity to weights, damping, resolution, and random seed |
| Temporal validation | Edges have timestamps | Static projections overstate reachability |
| Leakage audit | Link prediction or embeddings feed ML | Future edges or labels may leak into features |

## Scenarios

### Citation Authority Ranking

1. Build a directed graph where edge A -> B means A cites B.
2. Use PageRank for authority and in-degree as a baseline.
3. Run community detection on a symmetrized or bibliographic-coupling graph, not blindly on the citation graph.
4. Check old-node bias; PageRank can favor older papers.
5. Report top nodes with community labels and sensitivity to damping.

### Dependency Blast Radius

1. Define edge direction explicitly: dependent -> dependency.
2. Reverse edges when asking "who depends on this package?"
3. Use reachability for direct/transitive impact.
4. Use betweenness to identify bridge modules.
5. Use percolation only after modeling correlated removals such as shared platform or version family.

### Audience Spread Forecast

1. Fit degree distribution and test scale-free assumptions.
2. Use network-aware SIR, not only a mean-field estimate.
3. Calibrate beta and gamma from historical events.
4. Simulate seed sets across many runs.
5. Compare static and temporal-network forecasts if contacts are bursty.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Corrective Move |
|--------------|--------------|-----------------|
| "High degree means influential" | Hubs may not bridge communities or cause adoption | Pick degree, betweenness, closeness, eigenvector, or PageRank by mechanism |
| PageRank on arbitrary edges | Endorsement semantics may not hold | State why an inbound edge is a vote or flow path |
| Scale-free from log-log plot | Many distributions look linear on log-log axes | Run maximum-likelihood fit and compare alternatives |
| Modularity as ground truth | Resolution limit can merge small communities | Scan resolution and report stability |
| Static graph for temporal process | Time-respecting paths may not exist | Use temporal reachability or snapshot analysis |
| Embedding as explanation | Latent vectors are hard to interpret causally | Pair embeddings with structural features and ablations |
| Link prediction without time split | Future information leaks into training | Use chronological train/test split |
| Louvain/modularity used when the question is inferential | Modularity optimisation always returns a partition and cannot answer "is there community structure at all?" — it has no null model for the absence of structure; the resolution limit additionally distorts community sizes | If the goal is hypothesis testing, model comparison, or posterior inference over partitions, use SBM (`graph-tool minimize_blockmodel_dl()`); reserve Louvain/Leiden for purely descriptive partitioning where statistical significance is not required (Peixoto 2023) |
| SIR model for social adoption or behaviour-change spread | SIR assumes single-exposure transmission; social adoption typically requires multiple independent reinforcing exposures from neighbours (complex contagion / Watts threshold model); SIR predicts wrong intervention targets in this domain | Use Watts threshold model when mechanism involves social reinforcement; NetworkX has no built-in threshold-contagion function (verified July 2026) — use NDlib's `ThresholdModel` or implement the neighbour-fraction rule directly; SIR remains correct for biological disease or information forwarding |

## Known Traps

- Projection trap: one-mode projection of bipartite graphs creates dense cliques and inflated clustering coefficients that are artifacts of the projection, not evidence of real triadic closure — compare against a projected-random-bipartite null model.
- Direction trap: reversing edges flips authority and influence.
- Sampling trap: API crawls and snowball samples distort centrality and degree distribution in a systematic, hub-biased direction, not as random noise — subsampling a true scale-free network does not reliably yield a scale-free subnet, and the inverse inference is equally unsafe (Stumpf, Wiuf & May 2005, PNAS). State the collection method before making any distributional claim.
- Weight trap: mixing frequency, strength, and confidence in one edge weight breaks interpretation.
- Resolution trap: community size depends on algorithm and parameter, not only the graph.
- Survivorship trap: observed networks omit failed or inactive nodes.

## Compact Review Sequence

1. Define nodes and edge semantics.
2. State direction, weights, timestamps, and missing-data limits.
3. Choose primitive by question, not habit.
4. Run at least one baseline.
5. Test sensitivity to parameters and sampling.
6. Validate statistical claims with formal tests.
7. Separate descriptive graph structure from causal claims.
8. Report uncertainty and allowed interpretation.
