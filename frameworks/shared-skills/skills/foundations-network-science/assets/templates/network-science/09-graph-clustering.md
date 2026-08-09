# Primitive: Graph Clustering

**Sources**: Fortunato (2010) Physics Reports; Von Luxburg (2007) Statistics and Computing; Newman (2010) §11.

## Definition

Graph clustering partitions nodes into groups by optimising a graph-aware objective — typically **conductance** (cut minimisation) or **modularity** (density contrast). Unlike community detection, graph clustering explicitly balances internal density against external sparsity using a min-cut or spectral objective.

**Conductance** of a cut (S, V\S):

φ(S) = cut(S, V\S) / min(vol(S), vol(V\S))

Lower φ = better cut (fewer edges cross, proportional to cluster volume). Optimal partitioning minimises the maximum φ across all clusters.

**Normalised Cut** (Shi & Malik 2000): minimise sum of conductances across k partitions.

**Spectral clustering**:
1. Compute graph Laplacian L = D − A (D = degree matrix, A = adjacency)
2. Compute the k smallest eigenvectors of L (or normalised Laplacian L_sym)
3. Embed each node as its k-dimensional eigenvector row
4. Apply k-means on the embedding

The eigengap between λ_k and λ_(k+1) indicates the natural number of clusters.

## When to Use

- When a balanced partition (similar cluster sizes) is required — modularity does not enforce balance
- When the objective is minimising inter-cluster edges (cut-based), not maximising intra-cluster density
- Graph segmentation: images as pixel graphs, code as call-flow graphs
- When you need a deterministic, reproducible partitioning (spectral is deterministic given eigensolver)

## Inputs

- Undirected weighted or unweighted graph
- Target number of clusters k (or use eigengap to estimate k)
- Normalised or unnormalised Laplacian choice

## Outputs

- Cluster assignment for each node (k partitions)
- Conductance φ for each cluster
- Optional: eigengap plot for k selection

## Failure Modes

1. **Eigengap is ambiguous**: multiple small eigengaps make k selection unclear. Cross-validate with stability analysis (perturb the graph slightly and check cluster consistency).
2. **Scalability**: exact spectral clustering requires O(n²) eigendecomposition. For n > 10⁴, use approximate methods (Nyström approximation, sparse eigensolver).
3. **Equal-cluster-size assumption**: normalised cut tends to produce equal-size clusters. If natural cluster sizes are highly unequal, modularity-based community detection (#3) is more appropriate.
4. **Disconnected graphs**: the Laplacian of a disconnected graph has multiple zero eigenvalues equal to the number of components. Handle each component separately or add a small connectivity regularisation.

## Worked Example

**Call-flow graph**: 200 functions, 600 call edges. Eigengap analysis: λ₄ = 0.12, λ₅ = 0.48 → 4-cluster solution. Spectral clustering with k=4 produces conductance values φ = [0.08, 0.11, 0.09, 0.14]. Manual inspection: the 4 clusters correspond to authentication, data access, business logic, and API surface — matching architectural intent. Community detection (Louvain) on the same graph yields Q = 0.44 with 7 communities, splitting the authentication layer into 3 sub-groups that are too fine-grained for blast-radius analysis.

## Sources

- Fortunato (2010). Community detection in graphs. Physics Reports. [doi:10.1016/j.physrep.2009.11.002](https://doi.org/10.1016/j.physrep.2009.11.002)
- Von Luxburg (2007). A tutorial on spectral clustering. Statistics and Computing. [doi:10.1007/s11222-007-9033-z](https://doi.org/10.1007/s11222-007-9033-z)
- Shi and Malik (2000). Normalized Cuts and Image Segmentation. IEEE TPAMI. [doi:10.1109/34.868688](https://doi.org/10.1109/34.868688)
- Newman (2010). Networks: An Introduction. §11.

## Related

- [`03-community-detection.md`](03-community-detection.md) — modularity-based alternative; preferable when cluster sizes vary naturally
- [`10-graph-embeddings.md`](10-graph-embeddings.md) — learned embeddings as an alternative to spectral embedding
