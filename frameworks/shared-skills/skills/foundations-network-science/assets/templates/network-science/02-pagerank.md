# Primitive: PageRank

**Sources**: Brin & Page (1998); Easley & Kleinberg (2010) §14.

## Definition

PageRank models a random surfer who follows outgoing links with probability d (the damping factor), and teleports to a random node with probability (1−d). The stationary distribution of this Markov chain gives each node a score proportional to the probability of the surfer visiting it.

**Iterative formula**: PR(i) = (1−d)/n + d × Σⱼ∈In(i) PR(j)/Out(j)

- d = damping factor, typically 0.85 for web-scale graphs
- In(i) = nodes with edges pointing to i
- Out(j) = out-degree of node j

PageRank is a special case of eigenvector centrality on directed graphs with teleportation, which prevents it from assigning zero rank to nodes with no inbound links.

## When to Use

- Ranking documents, pages, or nodes by **endorsement-weighted authority** on a directed graph
- Any setting where being linked to by important nodes matters more than being linked to by many unimportant nodes
- Dependency influence: which package changes propagate most widely through transitive dependents
- Citation authority in academic or content networks

## Inputs

- Directed graph (adjacency matrix or edge list with directionality)
- Damping factor d (default 0.85; requires calibration for non-web graphs)
- Convergence criterion ε (default 1×10⁻⁶)
- Optional: initial distribution (uniform or custom)

## Outputs

- Per-node PageRank score (sums to 1 over all nodes)
- Ranking of nodes by authority

## Failure Modes

1. **Default d=0.85 for non-web graphs**: the original calibration was done on web-scale graphs; sparse or small graphs may need d ∈ [0.5, 0.8] for stable results. Sensitivity-test d before reporting.
2. **Dangling nodes** (zero out-degree): they absorb rank without redistributing it, deflating all other nodes. Standard fix: treat dangling nodes as connecting to all nodes uniformly (stochastic complement).
3. **Directed cycles without teleportation**: rank can accumulate in sink cycles without the (1−d) teleportation term. Ensure teleportation is always included.
4. **Interpreting PageRank as reach**: PageRank measures structural authority, not epidemic reach. For spread estimation, combine with SIR (#7).

## Worked Example

**Citation network — 5 papers**:

- Paper A is cited by B, C, D
- Paper B is cited by A, E
- Paper E is cited by D
- Paper D is cited by C

Naive in-degree: A=3, B=2, D=1, E=1, C=0. PageRank with d=0.85: A=0.31, B=0.18, D=0.14, E=0.12, C=0.09 (proportional; teleportation distributes residual). B's rank is elevated because A (high-authority) endorses it. C ranks last despite no inbound links — teleportation prevents zero-rank collapse.

**Reverse PageRank for blast radius**: reverse all dependency edges, run PageRank → nodes with high reverse-PageRank have the most transitive dependents.

## Sources

- Brin and Page (1998). The anatomy of a large-scale hypertextual Web search engine. Computer Networks. [doi:10.1016/S0169-7552(98)00110-X](https://doi.org/10.1016/S0169-7552(98)00110-X)
- Easley and Kleinberg (2010). Networks, Crowds, and Markets. §14. [cs.cornell.edu](https://www.cs.cornell.edu/home/kleinber/networks-book/)
- Page, Brin, Motwani & Winograd (1999). The PageRank Citation Ranking: Bringing Order to the Web. Stanford Technical Report. [ilpubs.stanford.edu](http://ilpubs.stanford.edu:8090/422/)

## Related

- [`01-centrality-measures.md`](01-centrality-measures.md) — eigenvector centrality is the undamped, undirected precursor to PageRank
- [`07-contagion-sir.md`](07-contagion-sir.md) — use PageRank for seed selection in influence maximisation
