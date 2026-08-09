# Primitive: Centrality Measures

**Sources**: Freeman (1977) betweenness; Bavelas (1950) closeness; Newman (2010) §7.

## Definition

Centrality quantifies the importance of a node within a graph. There is no single correct centrality — each measure answers a different question about importance. The four core measures are:

| Measure | Intuition | Formula sketch |
|---------|-----------|---------------|
| **Degree** | How many direct connections? | kᵢ = number of edges on node i |
| **Closeness** | How quickly can a node reach all others? | Cᵢ = (n−1) / Σⱼ d(i,j) |
| **Betweenness** | How often does a node lie on shortest paths? | Bᵢ = Σₛ≠ᵢ≠ₜ σₛₜ(i)/σₛₜ |
| **Eigenvector** | How connected are a node's neighbours? | xᵢ = (1/λ) Σⱼ Aᵢⱼ xⱼ |

## When to Use

- **Degree**: identify popular or highly connected nodes; useful as a quick baseline
- **Closeness**: find the most efficient broadcast origin; applicable when speed of dissemination matters
- **Betweenness**: detect bridges and brokers — nodes whose removal would disconnect communities
- **Eigenvector / Katz**: rank nodes by the quality (not just count) of their neighbours; foundation of PageRank

## Inputs

- Undirected or directed adjacency matrix or edge list
- Optional: edge weights (for weighted variants)
- For directed graphs: specify whether in-degree or out-degree centrality is intended

## Outputs

- Per-node scalar centrality score (normalised to [0, 1] for comparability)
- Ranking of nodes by chosen measure

## Failure Modes

1. **Wrong measure for the question**: high-degree nodes are not always brokers; only betweenness identifies bridges. A hub (high degree) can have low betweenness if all its neighbours are also connected to each other.
2. **Unnormalised scores compared across graphs of different sizes**: betweenness grows with n²; always normalise when comparing networks.
3. **Directed vs. undirected conflation**: in-degree and out-degree centrality answer different questions on directed graphs (authority vs. influence).
4. **Computational cost on large graphs**: exact betweenness is O(nm) for unweighted graphs; for n > 10⁵ use Brandes (2001) approximation.

## Worked Example

**Dependency graph**: 10 packages, with `lodash` having degree 8 (many direct dependents) and `util` having degree 2. Betweenness analysis reveals `util` has the highest betweenness — all cross-module paths pass through it. Removing `util` disconnects 4 sub-graphs; removing `lodash` leaves the graph connected. Degree alone gives the wrong answer for blast-radius analysis.

## Sources

- Freeman (1977). A set of measures of centrality based on betweenness. Sociometry. [doi:10.2307/3033543](https://doi.org/10.2307/3033543)
- Brandes (2001). A faster algorithm for betweenness centrality. Journal of Mathematical Sociology. [doi:10.1080/0022250X.2001.9990249](https://doi.org/10.1080/0022250X.2001.9990249)
- Newman (2010). Networks: An Introduction. §7. [oup.com](https://global.oup.com/academic/product/networks-9780199206650)

## Related

- [`02-pagerank.md`](02-pagerank.md) — eigenvector centrality generalised with damping and direction
- [`06-percolation.md`](06-percolation.md) — betweenness-based attack strategies in percolation analysis
