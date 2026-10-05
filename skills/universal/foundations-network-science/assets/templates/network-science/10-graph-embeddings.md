# Primitive: Graph Embeddings

**Sources**: Perozzi et al. (2014) DeepWalk; Grover & Leskovec (2016) node2vec; Kipf & Welling (2017) GCN; Broadwater & Stillman (2025) *Graph Neural Networks in Action*.

## Contents

- [Definition](#definition)
- [When to Use](#when-to-use)
  - [Is this a GNN problem at all?](#is-this-a-gnn-problem-at-all-data-not-obviously-graph-shaped)
  - [GNN vs gradient-boosted trees](#gnn-vs-gradient-boosted-trees-direction-only)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Failure Modes](#failure-modes)
- [Scaling a GNN When the Graph Outgrows the Machine](#scaling-a-gnn-when-the-graph-outgrows-the-machine)
- [Trap: Big-O Comparisons Between GNNs Are Unreliable](#trap-big-o-comparisons-between-gnns-are-unreliable)
- [Worked Example](#worked-example)
- [Sources](#sources)
- [Related](#related)

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

### Is this a GNN problem at all? (data not obviously graph-shaped)

Broadwater & Stillman (2025, §1.4) give three criteria for recognising a GNN problem in data that arrives tabular. Answering *yes* to any one is grounds for framing the problem as a graph:

| Criterion | Key indicators to look for |
|---|---|
| **Implicit relationships and interdependencies** — connections that are real but undocumented | Hidden or indirect connections between entities (customers linked by social influence, peer recommendation, or shared purchasing patterns rather than by any recorded relation). Entities sharing common attributes or activities with no formal link — investors who repeatedly co-invest in the same companies under similar conditions. Shared references or co-occurrence — documents citing each other or sharing authors and topics; terms forming co-occurrence networks. |
| **High dimensionality and sparsity** — many entities, few direct interactions | Numerous entities with limited direct interactions: user–item interaction data is tabular but inherently sparse, since most users touch a small subset of items. Representing users and items as nodes and interactions as edges lets network effects be exploited, and lets **cold-start** be attacked by surfacing explicit and implicit relations for new items or new users. Sparsely connected entities that nonetheless share significant characteristics — molecules, where most atoms form few bonds and much of the structure is distant in the graph. |
| **Complex, nonlocal interactions** — outcomes driven by distant entities | The outcome for one entity depends on entities not directly connected to it but reachable through intermediaries — a supplier delay cascading through several tiers to distributors and consumers. Information, influence, or effects propagating through the network over time — an outbreak spreading via shared providers, common environments, and overlapping social networks. |

Their closing self-test, framed for use before any modelling: *Are there implicit relationships or interdependencies I could model? Do interactions exhibit complex, nonlocal dependencies beyond immediate connections? Is the data high-dimensional and sparse, with a need to capture underlying relational structure?*

Caveat carried from the same section: standard GNNs relying on local message passing may struggle with long-range dependencies. That is a reason to reach for global attention, nonlocal aggregation, or hierarchical message-passing — not a reason to abandon the graph frame. See Failure Mode 3 on over-smoothing, which is the same phenomenon seen from the training side.

### GNN vs gradient-boosted trees (direction only)

Once the graph frame is chosen, the model is not automatically a GNN. Broadwater & Stillman (§4.4.3) put the tradeoff in one direction each way, with no magnitudes attached:

- **XGBoost** offers efficiency and speed, which is the advantage for projects with limited computational resources or where quick model training is required.
- **GAT / GNN** deeply integrates node relational data, which is what matters when internode relationships are pivotal to understanding the data patterns — and GNNs slot into broader deep-learning frameworks, contributing node embeddings that carry contextual information into complex relational datasets.

**Baseline-first is the transferable discipline, not the numbers.** The book's own sequence on its spam-review task is: non-GNN baselines first (logistic regression, XGBoost, MLP on the node features as tabular columns), *then* a GCN baseline to measure what introducing graph structure actually buys, *then* GAT. Establish the tabular baseline before attributing anything to the graph — otherwise there is no counterfactual and any GNN result is unfalsifiable. Do not import their reported accuracies: they are dataset-specific, the authors state they did not optimise the baselines, and on that dataset the tabular baseline was competitive.

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
3. **Over-smoothing in deep GNNs**: stacking many GCN layers causes all node embeddings to converge (over-smoothing). For most tasks, 2–3 GCN layers is optimal. This is why GNNs are typically shallower than conventional deep networks.

   *Second cause — problem radius* (Broadwater & Stillman §4.5.2): over-smoothing also arises when the task itself is long-range in hops, i.e. a node is materially influenced by a far-off node. That is a large **problem radius**, and it usually appears once a graph is large enough to contain distantly connected nodes — a social network where a celebrity influences distantly connected individuals is their example. The bind is structural: solving the task wants depth, and depth is what causes over-smoothing. Treat a suspected large problem radius as a reason to reduce the radius (coarsening, virtual/global nodes, hierarchical message passing) rather than to keep adding layers.

   *Per-architecture risk ordering* (direction only, no magnitudes given): **GraphSAGE** samples a fixed number of neighbours and aggregates them, and that sampling can mitigate over-smoothing. **GCN** is more at risk, having no such sampling step. **GAT** sits between: attention partially lowers the risk, but GATs can still over-smooth because the aggregation remains local.
4. **node2vec hyperparameter sensitivity**: default p=1, q=1 (equivalent to uniform random walk). Tune p and q with a grid search for the specific task.
5. **Disconnected graph components**: nodes in separate components have no common walk context. Handle each component separately or add virtual edges.

## Scaling a GNN When the Graph Outgrows the Machine

Broadwater & Stillman (§7.3.1) separate scale levers into three choices made up front and four techniques applied once the problem overwhelms the system. Technique names only — the book's PyG module paths and its 2025-hardware node-count thresholds are deliberately omitted here, since both date badly.

**Three up-front levers** (planned ahead, reconfigurable during the project):

- **Hardware configuration** — processor type, memory configuration of that processor, and single vs. many machines/processors.
- **Dataset representation** — dense vs. sparse tensors. Converting dense adjacency or node-feature matrices to sparse can significantly reduce the memory footprint on large graphs.
- **GNN architecture** — some architectures are designed to be computationally efficient and to scale; choosing one that scales well mitigates size problems before any workaround is needed.

**Four escape techniques**, each with a stated cost:

| Technique | What it does | Cost |
|---|---|---|
| Sampling | Train on a sampled subset of nodes or subgraphs per iteration instead of the whole graph | Added complexity of sampling and batching routines, traded against memory-efficiency gains |
| Parallelism / distributed computing | Spread the dataset and training across multiple processors or a cluster to cut training time | Development and configuration overhead, varying with how it is done |
| Remote backend | Keep the training graph in a backend database (at simplest, local disk) and pull mini-batches on demand | Highest development and maintenance overhead of the four — and, as of the book, a relatively new path with few worked examples — but the most rewarding on genuinely large data |
| Graph coarsening | Aggregate nodes and edges into a smaller graph that hopefully preserves essential structure | **Representation risk**: you must verify the coarsened graph truly represents the original; and for supervised learning you must decide how targets are consolidated |

*Memory sizing heuristic, carried with its framing*: the authors offer as **a rule of thumb** that memory capacity should ideally be between 4 and 10 times the size of the dataset. It is a planning heuristic, not a measured requirement — benchmark on a representative dataset rather than provisioning to it.

## Trap: Big-O Comparisons Between GNNs Are Unreliable

Do not select a GNN architecture on published complexity analysis alone (Broadwater & Stillman §7.6.1). GNN algorithms mix heterogeneous operations — matrix multiplications, nonlinear transformations, pooling — each with different complexity, and different GNNs do not use the same operations, so side-by-side comparison is of limited use. In practice the literature compares **one major operation rather than an entire algorithm** (their own worked comparison of GCN against GraphSAGE covers only the convolution-like operation in forward propagation, on sparse input). Implementation specifics — libraries, hardware optimisation, parallel strategies — shift the result further. Benchmark on your data; treat Big-O as an ordering hint, not a decision.

## Worked Example

**Package recommendation**: 3,000 npm packages, 12,000 dependency edges. node2vec with p=1, q=0.5 (DFS-biased for structural equivalence), d=128, 10 walks per node. Downstream task: predict co-usage (link prediction). AUC on held-out edges: Common Neighbors=0.72, node2vec dot product=0.86. Inspection: similar-function packages (React/Preact, Lodash/Ramda) cluster together in embedding space even with no direct dependency edges.

## Sources

- Perozzi, Al-Rfou and Skiena (2014). DeepWalk: Online Learning of Social Representations. KDD. [doi:10.1145/2623330.2623732](https://doi.org/10.1145/2623330.2623732)
- Grover and Leskovec (2016). node2vec: Scalable Feature Learning for Networks. KDD. [doi:10.1145/2939672.2939754](https://doi.org/10.1145/2939672.2939754)
- Kipf and Welling (2017). Semi-Supervised Classification with Graph Convolutional Networks. ICLR. [arxiv:1609.02907](https://arxiv.org/abs/1609.02907)
- Hamilton, Ying and Leskovec (2017). Inductive Representation Learning on Large Graphs. NeurIPS. [arxiv:1706.02216](https://arxiv.org/abs/1706.02216)
- Broadwater and Stillman (2025). *Graph Neural Networks in Action*. Manning. §1.4 (three criteria for identifying a GNN problem), §4.3–4.4.3 (baseline-first sequence; GAT vs XGBoost selection), §4.5.2 (over-smoothing, problem radius, per-architecture risk), §7.3.1 (scale levers and escape techniques), §7.6.1 (Big-O comparison caveat).
- Liu, Yang, Lu, Chen, Li, Zhang, Bai, Fang, Sun, Yu, and Shi (2025). Graph Foundation Models: Concepts, Opportunities and Challenges. IEEE TPAMI 47(6):5023-5044. [doi:10.1109/TPAMI.2025.3548729](https://doi.org/10.1109/TPAMI.2025.3548729) — Survey and taxonomy of GFMs; zero-shot cross-domain generalization benchmark. CORRECTED 2026-07-11: previously misattributed to "Wang et al." — no author named Wang appears on this paper; first author is Jiawei Liu.

## Related

- [`08-link-prediction.md`](08-link-prediction.md) — embedding dot product as a link prediction score
- [`09-graph-clustering.md`](09-graph-clustering.md) — embedding-based clustering vs. spectral clustering
- [`03-community-detection.md`](03-community-detection.md) — community membership as a structural signal captured by BFS-biased node2vec
- [`12-graph-schema-design.md`](12-graph-schema-design.md) — what becomes a node before any embedding is learned; heterogeneous vs. homogeneous schema decides which methods apply
