# Network Science Formal Theory Map

Use this map when a graph analysis depends on structural assumptions, statistical claims, or dynamic processes.

## Theory Spine

| Construct | What It Formalizes | Operational Test |
|-----------|--------------------|------------------|
| Graph model | Nodes, edges, direction, weights, attributes, time | Does the graph representation match the real relation? |
| Centrality | Importance under a specific path, flow, or endorsement theory | Which notion of "important" is being measured? |
| Random walk | Movement or attention over edges | Is the chain connected/ergodic enough for PageRank-like scores? |
| Community | Dense internal connectivity relative to external connectivity | Is the resolution level appropriate for the decision? |
| Degree distribution | Frequency of node degrees | Was a power-law fit tested against alternatives? |
| Percolation | Connectivity phase transition under node/edge removal | Is failure random, targeted, or correlated? |
| Epidemic process | Transmission and recovery over contacts | Are time ordering and heterogeneous degree accounted for? |
| Temporal reachability | Paths that respect edge timestamps | Would a static projection create impossible paths? |

## Primitive Dependency Map

| Primitive | Depends On | Boundary |
|-----------|------------|----------|
| Centrality | Path, flow, or neighbor definition | No centrality measure is universally "best" |
| PageRank | Directed endorsement graph and random-surfer assumptions | Sensitive to damping, dangling nodes, and graph construction |
| Community detection | Null model and quality function | Modularity has a resolution limit |
| Small-world test | Clustering and path length compared to a baseline | Must compare to appropriate random/regular reference |
| Scale-free test | Statistical power-law fitting | Log-log plots are not evidence |
| Percolation | Removal model and component definition | Directed graphs need weak/strong component distinction |
| SIR contagion | Transmission, recovery, and contact timing | Mean-field assumptions fail on heterogeneous networks |
| Embeddings | Proximity objective and downstream task | Vectors are predictive features, not explanations by default |

## Evidence Standards

- Centrality claim: state graph type, measure, weighting, and why that measure matches the question.
- PageRank claim: state damping, dangling-node handling, convergence tolerance, and sensitivity.
- Community claim: state algorithm, resolution parameter, quality metric, and stability across seeds.
- Scale-free claim: report fitted xmin, alpha, goodness-of-fit, and alternative distributions.
- Diffusion claim: report beta/gamma, seed selection, time horizon, and uncertainty across simulations.
- Temporal claim: compare time-respecting paths against static projection.

## Common Model Choices

- Directed citation/dependency graph: use in/out direction deliberately; reversing edges changes authority vs. influence.
- Bipartite user-item graph: avoid one-mode projection unless projection weights and information loss are acceptable.
- Weighted graph: normalize weights if they mix different meanings.
- Multigraph: decide whether repeated contacts are count, intensity, or separate temporal events.
- Dynamic graph: use snapshots or event streams; state which one the algorithm expects.

## Source Anchors

- Newman: networks, centrality, random graphs, percolation, epidemics.
- Barabasi: scale-free networks, preferential attachment, robustness.
- Watts and Strogatz: small-world model.
- Brin and Page: PageRank.
- Fortunato: community detection and modularity limits.
- Clauset, Shalizi, Newman: power-law testing.
- Broido and Clauset: strict-taxonomy empirical finding that "strongest" scale-free structure is uncommon (~4% of 927 networks) — contested, not settled; see Holme (2019) for the counter-framing that the finding is an artifact of definitional strictness.
- Holme and Saramaki: temporal networks.
