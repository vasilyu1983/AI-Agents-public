# Primitive: Community Detection

**Sources**: Fortunato (2010) Physics Reports; Blondel et al. (2008) Louvain; Newman (2010) §11.

## Definition

Community detection identifies groups of nodes that are more densely connected to each other than to the rest of the graph. The dominant objective is **modularity maximisation**:

Q = (1/2m) × Σᵢⱼ [Aᵢⱼ − kᵢkⱼ/2m] δ(cᵢ, cⱼ)

- m = number of edges
- Aᵢⱼ = adjacency matrix entry
- kᵢ, kⱼ = degrees of nodes i and j
- δ(cᵢ, cⱼ) = 1 if nodes i and j are in the same community, 0 otherwise

Higher Q (max 1) indicates stronger community structure relative to a null random graph. Q > 0.3 is conventionally considered meaningful community structure.

**Key algorithms**:

| Algorithm | Complexity | Best For |
|-----------|-----------|---------|
| Louvain | O(n log n) | Large graphs (> 10⁴ nodes); hierarchical output — **descriptive partitioning only** |
| GVE-Leiden | O(n log n) | Billion-edge graphs (N > 1M, E > 100M); 400M edges/s; avoids Louvain's internally-disconnected community defect; supports CPM objective to circumvent resolution limit (Sahu, Kothapalli & Banerjee 2024) — **descriptive** |
| Label Propagation | O(m) | Very large graphs; approximate — **descriptive** |
| Girvan-Newman | O(m²n) | Small graphs; edge-betweenness based — **descriptive** |
| Spectral clustering | O(n³) | Graphs with clear eigengap — **descriptive** |
| SBM (graph-tool) | O(n log² n) typical | **Inferential**: hypothesis testing — "does community structure exist?"; statistical model comparison; nested hierarchical detection; avoids resolution limit by construction (Peixoto 2023) |

**Descriptive vs. Inferential distinction**: Modularity maximisation (Louvain/Leiden/Label Propagation) answers "what is the best partition of this graph?" — it always returns a partition regardless of whether community structure is statistically meaningful. Stochastic Block Model (SBM) inference answers "given a generative model, is there evidence for community structure, and what is the posterior over partitions?" Use SBM when: (a) you need to test whether community structure exists at all; (b) comparing competing partitions statistically; (c) the question is generative or hypothesis-testing in nature. Use Louvain/Leiden when: the question is purely descriptive partitioning for downstream ML (labelling nodes, blast-radius grouping) and statistical significance is not required.

## When to Use

- Discovering cohesive groups in social, citation, dependency, or biological networks
- Reducing a large graph to a community-level summary for blast-radius or contagion analysis
- Identifying topical clusters in content networks without relying on node attributes

## Inputs

- Undirected graph (for most algorithms; directed variants exist for Louvain)
- Optional: resolution parameter γ (default 1.0); higher γ → smaller communities
- Optional: ground-truth labels for quality evaluation (NMI, ARI)

## Outputs

- Community assignment for each node
- Modularity score Q
- Optional: hierarchical dendrogram (Louvain)

## Failure Modes

1. **Resolution limit**: modularity maximisation merges small communities into large ones and misses dense small communities in large graphs (Fortunato & Barthélemy 2007). Fix: run with multiple γ values; compare at γ=0.5, 1.0, 2.0.
2. **Small graphs (N < 50)**: modularity gains are trivially achievable on small graphs. Community detection results are statistically unreliable for small N.
3. **Directed graphs treated as undirected**: most algorithms require undirected input. For directed graphs, either project to undirected (losing directional information) or use a directed-modularity variant.
4. **Single run of Louvain**: Louvain is non-deterministic. Run 10–50 times and take the result with highest Q, or use consensus clustering across runs.
5. **Community count treated as ground truth**: different γ values produce different community counts. Report the range, not a single K.
6. **Applying pairwise community detection to a high-degree-heterogeneity hypergraph without a reducibility check**: co-authorship-style networks with high degree heterogeneity cannot be safely collapsed to pairwise edges without dynamical information loss. Run the reducibility test (Lucas et al. 2026, Nat. Comms) before choosing pairwise vs. higher-order methods — contact networks are typically reducible; co-authorship networks are not.
7. **Using Louvain/Leiden when the question is inferential**: if the goal is to test whether community structure exists, compare competing partitions, or determine the number of communities from data, modularity-based methods cannot answer these questions — they always return a partition and have no null model for "no community structure." Use SBM (`graph-tool minimize_blockmodel_dl()` or `minimize_nested_blockmodel_dl()`) for inferential questions. Key result: Peixoto & Kirkley (2023, Phys. Rev. E) show that inferential methods have implicit biases too, but those biases are auditable and correctable unlike modularity's hidden resolution limit.

## Worked Example

**Tech-blog citation graph**: 500 posts, 2,000 citation edges. Louvain with γ=1.0 produces 12 communities, Q=0.41. Top-PageRank node in each community labels the cluster: "React tooling", "TypeScript migration", "CI/CD", etc. Communities match human editorial judgement in 10 of 12 cases. At γ=2.0, the "React tooling" community splits into "hooks" and "state management" sub-communities, revealing finer structure.

**Tool note (verified July 2026)**: NetworkX ≥3.5 ships `louvain_communities()` natively; `leiden_communities()` exists in the public API but has no native NetworkX implementation — it requires an installable backend (e.g. an nx-cugraph-style plugin) or raises `NetworkXNotImplemented`. Do not assume `leiden_communities()` runs out of the box; check the active backend before relying on it in production. graph-tool's `minimize_blockmodel_dl()` / `minimize_nested_blockmodel_dl()` remain the standard inferential (SBM) entry points.

## Sources

- Fortunato (2010). Community detection in graphs. Physics Reports. [doi:10.1016/j.physrep.2009.11.002](https://doi.org/10.1016/j.physrep.2009.11.002)
- Blondel, Guillaume, Lambiotte and Lefebvre (2008). Fast unfolding of communities in large networks. Journal of Statistical Mechanics. [doi:10.1088/1742-5468/2008/10/P10008](https://doi.org/10.1088/1742-5468/2008/10/P10008)
- Fortunato and Barthélemy (2007). Resolution limit in community detection. PNAS. [doi:10.1073/pnas.0605965104](https://doi.org/10.1073/pnas.0605965104)
- Newman (2010). Networks: An Introduction. §11.
- Sahu, Kothapalli, and Banerjee (2024). GVE-Leiden: Fast Leiden Algorithm for Community Detection in Shared Memory Setting. ICPP 2024, ACM. [doi:10.1145/3673038.3673146](https://doi.org/10.1145/3673038.3673146) — Code: https://github.com/puzzlef/leiden-communities-openmp. CORRECTED 2026-07-11: previously misattributed to "Dhulipala and Shun."
- Lucas et al. (2026). Reducibility of higher-order networks from dynamics. Nature Communications. [doi:10.1038/s41467-025-68273-4](https://doi.org/10.1038/s41467-025-68273-4) — Code: https://github.com/maximelucas/hypergraph_reducibility
- Peixoto (2023). Descriptive vs. Inferential Community Detection in Networks: Pitfalls, Myths and Half-Truths. Cambridge University Press. [doi:10.1017/9781009118897](https://doi.org/10.1017/9781009118897) — arXiv:2112.00183. Code: https://graph-tool.skewed.de/
- Peixoto and Kirkley (2023). Implicit models, latent compression, intrinsic biases, and cheap lunches in community detection. Physical Review E 108, 024309. [doi:10.1103/PhysRevE.108.024309](https://doi.org/10.1103/PhysRevE.108.024309)

## Related

- [`09-graph-clustering.md`](09-graph-clustering.md) — spectral clustering as a graph-cut alternative to modularity
- [`02-pagerank.md`](02-pagerank.md) — PageRank used to label communities by authority
- [`07-contagion-sir.md`](07-contagion-sir.md) — community boundaries can slow epidemic spread
