# Network Science Composition Recipes

Stacks of [network-science primitives](../SKILL.md#quick-reference) for recurring multi-question analyses. Numbers such as (#2) refer to rows of that table.

For a GraphRAG pipeline (chunking, retrieval, summary evaluation), use `ai-rag`. The GraphRAG recipe below covers only the graph primitives.

## Contents

- [AI-Search Citation Flow](#ai-search-citation-flow)
- [Blast Radius Across a Dependency Graph](#blast-radius-across-a-dependency-graph)
- [Audience Reach Forecast](#audience-reach-forecast)
- [GraphRAG Corpus Partitioning](#graphrag-corpus-partitioning)

## AI-Search Citation Flow

**Goal**: rank documents and authors by structural authority in a citation network, surface topical clusters.

**Stack**:
1. **PageRank (#2)** — assign authority scores using directed citation edges; damp at 0.85 for large corpora
2. **Topical authority overlay** — weight edges by semantic similarity between citing and cited abstract (cosine on embeddings) before computing PageRank
3. **Community detection (#3)** — Louvain on the undirected projection to surface research communities; label each community with top-PageRank node
4. **Output**: per-node authority score + community membership → ranked results with cluster context

**Failure modes to check**: resolution limit in community detection on very large citation graphs; scale-free test on degree before assuming hub-based spreading.

**Inputs:** directed citation graph (edge list: citing → cited), optional semantic embeddings for abstract-similarity weighting, damping factor d (default 0.85), modularity resolution ε.
**Rules:** PageRank score Pᵢ = (1−d)/N + d·Σⱼ Pⱼ/Lⱼ (Lⱼ = out-degree of j); iterate until max|ΔP|<10⁻⁶. Community detection: Louvain greedy until ΔQ<ε; label each community with its top-PageRank node. Resolution limit: communities smaller than √(m/2) (m = edge count) may be merged — scan resolution γ across a justified range (separate from convergence tolerance ε) to verify.
**Outputs:** per-node PageRank authority score, community assignment per node, community sizes, ranked results list with cluster label.

---

## Blast Radius Across a Dependency Graph

**Goal**: given a package or module change, estimate how many downstream dependents are affected and identify critical bridges.

**Stack**:
1. **Directed graph construction** — nodes are packages/modules; directed edge A→B means A depends on B
2. **Reverse reachability (#1)** — for dependent→dependency edges, reverse edges and count reachable exposed dependents; use PageRank only as a descriptive prioritization baseline, not a count of transitive dependents
3. **Betweenness centrality (#1)** — identify bridge packages that, if removed or changed, disconnect large portions of the graph
4. **Community detection (#3)** on the undirected projection — group tightly-coupled modules into blast clusters; a change inside a cluster propagates to the whole cluster
5. **Percolation (#6)** — simulate targeted removal of the changed package(s) to estimate giant-component fragmentation

**Output**: blast-radius score per package + bridge list + cluster boundaries.

**Inputs:** directed dependency graph (edge list: A→B means A depends on B), changed package(s) as seed nodes, removal simulation count (Monte Carlo N ≥ 1 000).
**Rules:** For dependent→dependency edges, reverse edges and compute reachability from changed packages to identify direct/transitive exposed dependents. Distinguish structural exposure from actual failure propagation (optional dependencies, fallbacks, versions and runtime gates). PageRank/betweenness are prioritization proxies. GCC reduction describes connectivity, not blast radius; no universal 20% criticality cutoff applies. Communities help organize review but do not imply all members fail.
**Multilayer caveat (P1):** if the dependency graph spans distinct infrastructure layers (e.g. application tier → database tier → network tier), treat it as an interdependent (multilayer) network. Cross-layer dependency links convert the percolation transition from second-order (gradual) to first-order (abrupt, catastrophic) — a small cascade can produce complete collapse with no early warning signal from the single-layer S(q) curve. Confirm whether cross-layer coupling links exist before reporting single-layer percolation thresholds as the operational limit (Artime et al. 2024, Nat. Rev. Phys.).
**Outputs:** blast-radius score per changed package (% of graph reachable), ranked bridge node list with betweenness scores, community cluster map with cluster sizes, percolation phase indicator (critical / non-critical).

---

## Audience Reach Forecast

**Goal**: predict how far and fast a message spreads from a seed set of users in a social or content network.

**Stack**:
1. **Degree distribution test (#5)** — verify whether the network is scale-free (power-law degree); hubs amplify spread non-linearly
2. **SIR contagion model (#7)** — set β (transmission rate) from historical engagement data; γ (recovery/churn) from observed drop-off; run Monte Carlo over the network
3. **Percolation threshold (#6)** — state the contact process and transmissibility; for iid bond transmission on a locally tree-like uncorrelated configuration model use B=T(⟨k²⟩−⟨k⟩)/⟨k⟩, with B>1 permitting a giant outbreak in the infinite-size limit
4. **Seed comparison (#1, #2)** — compare PageRank, directed out-reach, degree and random seed sets under the fitted SIR/threshold model, budget and overlap constraints; choose by simulated or held-out reach, not centrality alone
5. **Output**: expected reach distribution + confidence interval + percolation-phase indicator (above/below threshold)

**Failure modes to check**: SIR assumes homogeneous mixing; use network-aware SIR not mean-field approximation. Temporal ordering changes reachable paths and can change spread predictions; compare the calibrated temporal process with the static projection.

**Inputs:** social/content network graph (edge list), average invites per user k, conversion rate p, degree distribution moments ⟨k⟩ and ⟨k²⟩, transmission rate β and recovery rate γ (from historical engagement/drop-off data), target reach metric, seed budget (number of seed nodes).
**Rules:** A simple iid branching referral model has R=k·p; expected total cohort including one paid seed is 1/(1−R) only for R<1 without collisions, saturation or changing conversion. It is a cohort-size multiplier, not number of cycles. With seed acquisition cost C_seed and incentive C_ref per successful descendant, amortized CAC=C_seed(1−R)+C_ref R. State costs, horizon, duplicate-user handling and referral dependence. No universal target R or centrality seed rule exists; compare candidate seed sets under the documented diffusion mechanism.
**Outputs:** measured referral coefficient and uncertainty, horizon-specific unique reach, seed-selection comparison, cohort cost assumptions and CAC; report whether branching assumptions survive observed collisions and saturation.

**Worked example:** Illustrative branching referrals: k=4, p=.15 gives R=.6. One $5 paid seed has expected total cohort 2.5 under the stated iid, unlimited-population model. With no referral incentive, amortized CAC=$5/2.5=$2; with $1 per successful descendant, CAC=$5×.4+$1×.6=$2.60. This does not determine an SIR epidemic threshold, cycle count or durable growth target. Validate unique-user cohorts and finite-horizon costs on observed data before recommending incentives.

---

## GraphRAG Corpus Partitioning

**Goal**: partition a document corpus into hierarchical communities so that each community can receive a standalone LLM summary, enabling global multi-hop question answering without full-corpus retrieval.

**Stack**:
0. **Graph-vs-vector gate** — build the graph only for multi-hop, global or summary questions. Baseline vector RAG on the same evaluation set first; the benchmark evidence and pipeline patterns are in `ai-rag` (`references/graph-rag-patterns.md`).
1. **Entity co-occurrence graph** — nodes are extracted entities; edge weight = co-occurrence count within a chunk window (e.g. ±2 sentences)
1b. **Entity resolution check** — measure the duplicate/alias rate after entity resolution and before community detection. Unmerged aliases split communities and deflate centrality.
2. **Community detection (#3)** — run Leiden to produce a hierarchical partition (benchmark Louvain vs. GVE-Leiden on your own graph and hardware before committing to one at scale); each level of the hierarchy becomes a summary granularity level; label each community by its top-degree entity
3. **PageRank (#2)** — within each community, rank entities by PageRank on the sub-graph to select the most salient nodes for summary generation; PageRank on the sub-graph functions as memory salience for agent context
4. **Link prediction (#8)** — optionally score candidate cross-community edges (Adamic-Adar or Katz) to surface implicit entity bridges before summarisation
5. **Output**: hierarchical community map + per-community entity ranking + cross-community bridge candidates → feeds LLM summarization pipeline

**Failure modes to check**: resolution limit — large corpora with > 100K nodes need a resolution parameter γ scan (ε remains convergence tolerance) to avoid all entities collapsing into one community. Lazy evaluation (defer community summaries until query time) avoids upfront cost when only a fraction of communities are queried. Benchmark candidate implementations on the graph and available hardware; edge count alone does not forbid Louvain. Non-overlapping partitioning severs inter-community edges, so multi-hop inference paths that cross a community boundary are lost from every summary — a structural reason GraphRAG under-answers bridging questions. Score cross-community bridge candidates (step 4) *before* summarising, and evaluate the partition on downstream answer quality rather than modularity, since detector choice measurably shifts downstream performance (Ghosh & Saule 2025). If the corpus grows incrementally, re-partition with an incremental Leiden variant rather than rebuilding the hierarchy per ingest.

**Inputs:** entity co-occurrence edge list, chunk window size, Leiden resolution parameter γ and convergence tolerance ε, PageRank damping d (default 0.85), optional link-prediction candidate threshold.
**Outputs:** hierarchical community assignments per entity, per-community PageRank ranking, cross-community bridge edge candidates, community sizes.
