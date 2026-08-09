# Primitive: Graph Embeddings

**Sources**: Perozzi et al. (2014) DeepWalk; Grover & Leskovec (2016) node2vec; Kipf & Welling (2017) GCN.

## Definition

Graph embeddings map nodes (or edges, or entire graphs) to dense real-valued vectors in ℝᵈ (d typically 32–256), such that structurally similar nodes have similar vectors. This enables downstream ML on graphs using standard algorithms (k-means, logistic regression, cosine similarity).

**Three major approaches**:

### 1. Random-Walk Embeddings

- **DeepWalk** (Perozzi et al. 2014): generate random-walk sequences from each node; apply Word2Vec SkipGram to learn embeddings that predict context nodes in the walk
- **node2vec** (Grover & Leskovec 2016): biased random walks with return parameter p and in-out parameter q
  - p < 1 (BFS-biased): captures community membership — similar to homophily
  - q < 1 (DFS-biased): captures structural equivalence — nodes with similar graph roles get similar embeddings

### 2. Graph Neural Networks (GNNs)

- **GCN** (Kipf & Welling 2017): each layer aggregates the mean of neighbour embeddings
- **GraphSAGE**: samples and aggregates neighbours; inductive (handles unseen nodes)
- **GAT**: attentive aggregation — weights neighbours by learned attention

GNNs can incorporate node features alongside topology.

### 4. Graph Foundation Models (2025)

When the task involves transfer to new graph domains with limited or zero labels, **Graph Foundation Models (GFMs)** offer cross-domain generalization that node2vec and GCN cannot. GFMs are pre-trained on large multi-domain graph corpora and generalize via in-context learning or fine-tuning (Liu et al., IEEE TPAMI 2025).

**Three categories** (Liu et al. 2025 taxonomy):
- *Universal GFMs*: pre-trained across all graph types; zero-shot generalization to unseen domains
- *Domain-specific GFMs*: pre-trained on one domain (e.g. molecular); few-shot within-domain transfer
- *Task-specific GFMs*: pre-trained for a task (node classification, link prediction); limited domain transfer

**Representative models**: UniGraph (KDD 2025), GIT — achieves strong zero-shot node classification and link prediction across >30 graphs in 5 domains via in-context learning without fine-tuning.

**Use when**: new citation network, knowledge graph, or social graph with no training labels and a need for immediate node classification or link prediction.

**Kill criteria**: GFMs require large compute and pre-trained checkpoints. For target domains that are highly specialized (e.g. proprietary molecular biology features absent from pretraining corpora), domain-specific fine-tuning or standard transductive embeddings will outperform zero-shot GFMs.

### 3. Matrix-Factorisation Methods

- **LINE**: preserves first-order (direct connections) and second-order (shared neighbourhood) proximity
- **HOPE**: handles directed graphs and asymmetric proximity

## When to Use

- Node classification: predict node labels (author field, package category) from structure
- Link prediction: score candidate edges from embedding dot product or cosine similarity
- Graph visualisation: 2D UMAP/t-SNE projection of embeddings to inspect structure
- Any downstream ML task that requires fixed-size vector representations of nodes

## Inputs

- Graph (adjacency matrix or edge list)
- For GNNs: optional node feature matrix X ∈ ℝ^{n×f}
- Embedding dimension d (typically 64 or 128)
- node2vec: walk length (default 80), walks per node (default 10), p and q parameters

## Outputs

- Node embedding matrix Z ∈ ℝ^{n×d}
- For GNNs: also updated node features after message passing

## Failure Modes

1. **Transductive vs. inductive**: DeepWalk and standard node2vec are transductive — they cannot embed unseen nodes. Use GraphSAGE (inductive) when the graph grows dynamically.
2. **Ignoring node features**: random-walk methods ignore node attributes. When node features are available, GNNs that incorporate features outperform structure-only methods.
3. **Over-smoothing in deep GNNs**: stacking many GCN layers causes all node embeddings to converge (over-smoothing). For most tasks, 2–3 GCN layers is optimal.
4. **node2vec hyperparameter sensitivity**: default p=1, q=1 (equivalent to uniform random walk). Tune p and q with a grid search for the specific task.
5. **Disconnected graph components**: nodes in separate components have no common walk context. Handle each component separately or add virtual edges.

## Worked Example

**Package recommendation**: 3,000 npm packages, 12,000 dependency edges. node2vec with p=1, q=0.5 (DFS-biased for structural equivalence), d=128, 10 walks per node. Downstream task: predict co-usage (link prediction). AUC on held-out edges: Common Neighbors=0.72, node2vec dot product=0.86. Inspection: similar-function packages (React/Preact, Lodash/Ramda) cluster together in embedding space even with no direct dependency edges.

## Sources

- Perozzi, Al-Rfou and Skiena (2014). DeepWalk: Online Learning of Social Representations. KDD. [doi:10.1145/2623330.2623732](https://doi.org/10.1145/2623330.2623732)
- Grover and Leskovec (2016). node2vec: Scalable Feature Learning for Networks. KDD. [doi:10.1145/2939672.2939754](https://doi.org/10.1145/2939672.2939754)
- Kipf and Welling (2017). Semi-Supervised Classification with Graph Convolutional Networks. ICLR. [arxiv:1609.02907](https://arxiv.org/abs/1609.02907)
- Hamilton, Ying and Leskovec (2017). Inductive Representation Learning on Large Graphs. NeurIPS. [arxiv:1706.02216](https://arxiv.org/abs/1706.02216)
- Liu, Yang, Lu, Chen, Li, Zhang, Bai, Fang, Sun, Yu, and Shi (2025). Graph Foundation Models: Concepts, Opportunities and Challenges. IEEE TPAMI 47(6):5023-5044. [doi:10.1109/TPAMI.2025.3548729](https://doi.org/10.1109/TPAMI.2025.3548729) — Survey and taxonomy of GFMs; zero-shot cross-domain generalization benchmark. CORRECTED 2026-07-11: previously misattributed to "Wang et al." — no author named Wang appears on this paper; first author is Jiawei Liu.

## Related

- [`08-link-prediction.md`](08-link-prediction.md) — embedding dot product as a link prediction score
- [`09-graph-clustering.md`](09-graph-clustering.md) — embedding-based clustering vs. spectral clustering
- [`03-community-detection.md`](03-community-detection.md) — community membership as a structural signal captured by BFS-biased node2vec
