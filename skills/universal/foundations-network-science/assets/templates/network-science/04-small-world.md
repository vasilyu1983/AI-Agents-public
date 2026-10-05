# Primitive: Small-World Networks

**Sources**: Watts & Strogatz (1998) Nature; Newman (2010) §15; Easley & Kleinberg (2010) §20.

## Definition

A network has the **small-world property** when it simultaneously exhibits:

1. **High clustering coefficient C**: most neighbours of a node are also neighbours of each other → C ≫ C_random
2. **Short characteristic path length L**: average shortest path between any two nodes is O(log n) → L ≈ L_random

The Watts-Strogatz (WS) model generates small-world graphs by starting from a regular ring lattice and rewiring each edge with probability p:

- p = 0: regular lattice (high C, high L)
- p = 1: random graph (low C, low L)
- p ∈ (0.01, 0.1): small-world regime (high C, low L)

**Test for small-world property**: σ = (C/C_random) / (L/L_random) > 1. Typically σ ≫ 1 for real social and biological networks.

## When to Use

- Assessing whether a graph supports efficient navigation and information diffusion
- Explaining why "six degrees of separation" holds in large social networks
- Baseline structural analysis before modelling spread or routing on any graph
- Identifying whether network topology is closer to random or regular (affects intervention strategy)

## Inputs

- Graph (undirected or directed, but typically undirected for WS analysis)
- Equivalent random graph (same n and m, or same degree sequence) for baseline comparison

## Outputs

- Global clustering coefficient C
- Average shortest path length L (or median for disconnected graphs)
- Small-world coefficient σ = (C/C_random) / (L/L_random)
- Classification: random / small-world / regular

## Failure Modes

1. **Disconnected graphs**: average shortest path L is undefined for disconnected graphs. Use the largest connected component, or use the harmonic mean of finite pairwise distances.
2. **Large graphs — exact L is O(nm)**: for n > 10⁵, estimate L by BFS from a random sample of 1,000 source nodes.
3. **Directed graphs**: clustering coefficient has multiple definitions for directed graphs; specify which variant is used.
4. **σ > 1 claimed without a proper null model**: the null model must have the same degree sequence (configuration model), not just the same n and m.

## Worked Example

**Developer collaboration graph**: 1,200 developers, 4,800 co-authorship edges. Measured: C=0.42, L=4.1. Random graph (same n, m): C_random=0.007, L_random=3.8. σ = (0.42/0.007) / (4.1/3.8) = 60 / 1.08 = 55.6 ≫ 1 → clear small-world property. Interpretation: information spreads fast (low L) and clusters of collaborators form cohesive sub-teams (high C). Three random long-range edges per developer explain the short paths.

## Sources

- Watts and Strogatz (1998). Collective dynamics of small-world networks. Nature. [doi:10.1038/30918](https://doi.org/10.1038/30918)
- Newman (2010). Networks: An Introduction. §15.
- Easley and Kleinberg (2010). Networks, Crowds, and Markets. §20.

## Related

- [`05-scale-free-networks.md`](05-scale-free-networks.md) — scale-free networks are also small-world but with fat-tailed degree distribution
- [`07-contagion-sir.md`](07-contagion-sir.md) — short paths in small-world graphs accelerate epidemic spread
