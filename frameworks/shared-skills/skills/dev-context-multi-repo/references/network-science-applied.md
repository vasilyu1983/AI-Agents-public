---
description: Network science primitives applied to multi-repo context — blast-radius centrality, community-based context packetizing, PageRank-driven file retrieval, graph embeddings for cross-repo similarity, small-world diagnostics for internal package graphs, percolation analysis for build-graph fragility, link prediction for PR co-touch forecasting, and temporal co-change networks.
last_verified: 2026-05-02
status: stable
---

# Network Science Applied: Multi-Repo Context Layer

> **Gate before invoking:** Check [`foundations-network-science` § When to Apply](../../foundations-network-science/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


## Table of Contents

- [Framing Note](#framing-note)
- [Pattern Catalog](#pattern-catalog)
  - [P1 — Betweenness Centrality for Blast-Radius Dominance Ranking](#p1--betweenness-centrality-for-blast-radius-dominance-ranking)
  - [P2 — PageRank File Ranking for Retrieval Budget Allocation](#p2--pagerank-file-ranking-for-retrieval-budget-allocation)
  - [P3 — Community Detection over Symbol-Import Graph for Context Packetizing](#p3--community-detection-over-symbol-import-graph-for-context-packetizing)
  - [P4 — Graph Embeddings for Cross-Repo Similarity and Clone Detection](#p4--graph-embeddings-for-cross-repo-similarity-and-clone-detection)
  - [P5 — Small-World Diagnostics for Internal Package Graph Navigation](#p5--small-world-diagnostics-for-internal-package-graph-navigation)
  - [P6 — Percolation Analysis for Build-Graph Fragility](#p6--percolation-analysis-for-build-graph-fragility)
  - [P7 — SIR Contagion for Defect and Vulnerability Spread Estimation](#p7--sir-contagion-for-defect-and-vulnerability-spread-estimation)
  - [P8 — Link Prediction for PR Co-Touch Forecasting](#p8--link-prediction-for-pr-co-touch-forecasting)
  - [P9 — Temporal Co-Change Networks for Coupling Detection](#p9--temporal-co-change-networks-for-coupling-detection)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
  - [A1 — Using Degree Centrality Alone to Identify Blast-Radius Bottlenecks](#a1--using-degree-centrality-alone-to-identify-blast-radius-bottlenecks)
  - [A2 — Aggregating Git History Into a Static Graph Before Temporal Analysis](#a2--aggregating-git-history-into-a-static-graph-before-temporal-analysis)
  - [A3 — Running Community Detection Once at Default Resolution](#a3--running-community-detection-once-at-default-resolution)
  - [A4 — Applying Global PageRank When the Question Is Seeded](#a4--applying-global-pagerank-when-the-question-is-seeded)
  - [A5 — Merging Symbol-Level Graphs Into the Portfolio Knowledge Graph](#a5--merging-symbol-level-graphs-into-the-portfolio-knowledge-graph)
- [Recipes](#recipes)
  - [R1 — Refactor Impact Report: Which Repo Owns the Blast Radius?](#r1--refactor-impact-report-which-repo-owns-the-blast-radius)
  - [R2 — Context Packet Assembly for an LLM Repair Task](#r2--context-packet-assembly-for-an-llm-repair-task)
  - [R3 — PR Scope Forecast: Which Sibling Repos Will This PR Touch?](#r3--pr-scope-forecast-which-sibling-repos-will-this-pr-touch)
- [Cross-References](#cross-references)

---

## Framing Note

The `knowledge-graph-patterns.md` file in this skill covers the operational graph model: node and edge schemas, weight calibration, PPR queries, community detection calls, and the bitemporal slice interface. This file is the applied-recipe layer. It maps each relevant network science primitive from `foundations-network-science` to a concrete multi-repo context problem, provides worked examples grounded in cross-repo dependency and commit-history reality, and supplies step-by-step recipes for the three scenarios that recur most: refactor blast-radius ranking, context packet assembly for LLM tasks, and PR co-touch forecasting.

The primitives are referenced by number. Primitive numbers map to files in `foundations-network-science/assets/templates/network-science/`:

| # | Primitive |
|---|-----------|
| 01 | centrality-measures |
| 02 | pagerank |
| 03 | community-detection |
| 04 | small-world |
| 05 | scale-free-networks |
| 06 | percolation |
| 07 | contagion-sir |
| 08 | link-prediction |
| 09 | graph-clustering |
| 10 | graph-embeddings |
| 11 | temporal-networks |

All graph operations described here assume the portfolio knowledge graph produced by `scripts/build_knowledge_graph.py` and queryable via `scripts/query_graph.py`. Symbol-level graphs from `dev-context-code-graph` should not be merged into this portfolio layer; import their summaries or per-repo centrality rankings as node attributes instead.

---

## Pattern Catalog

### P1 — Betweenness Centrality for Blast-Radius Dominance Ranking

**Anchors: #01 centrality-measures, #06 percolation**

**When to use.** A refactor, API break, or security patch touches one or more repos. You need to rank the portfolio by which repos own the structural bottleneck — not simply by how many direct consumers they have, but by how many cross-repo dependency paths pass through them. The repo that is the unavoidable intermediary for the most paths carries the highest blast radius even if its direct-dependent count is modest.

**Mechanic.**

Build the directed cross-repo dependency graph: nodes are repos, edges point from consumer to provider (A → B means A imports B). Compute betweenness centrality B(r) for each repo r:

```
B(r) = Σ_{s≠r≠t} σ_st(r) / σ_st

where σ_st = total shortest paths from s to t
      σ_st(r) = those paths that pass through r
```

Normalise by `(n−1)(n−2)` (directed, n = repo count) before comparing portfolios. Repos with the highest normalised betweenness are the structural brokers. A refactor to such a repo requires the widest regression and the most careful versioning.

**Contrast with degree.** A shared utility repo may have high in-degree (many direct consumers) but low betweenness if those consumers are all also directly connected to each other. Conversely, a thin adapter layer with degree 2 can have high betweenness if it is the only bridge between two sub-clusters of the portfolio.

**Worked example.** A 40-repo platform portfolio. `common-utils` has in-degree 28 (most direct consumers). `schema-bridge` has in-degree 3 but betweenness 0.41 (normalised), compared to `common-utils` at 0.09. A migration of `schema-bridge`'s wire format would disconnect 18 repos from 14 others if it breaks; a `common-utils` change would leave all sub-clusters connected via alternate paths. The refactor plan should front-load `schema-bridge` API stability.

**Percolation connection (#06).** After computing betweenness, simulate targeted percolation: remove the top-k betweenness repos and measure how quickly the giant connected component collapses. This directly answers "how many brittle bridge repos does this architecture have?" If qc (targeted) < 0.10 — the graph fragments after removing fewer than 10% of repos — the portfolio has a fragility budget problem requiring redundancy or decoupling work.

**Computational note.** For portfolios ≤ 200 nodes, exact Brandes betweenness is fast. Above 200 nodes, use the NetworkX approximation with k=500 sample pivots.

---

### P2 — PageRank File Ranking for Retrieval Budget Allocation

**Anchors: #02 pagerank**

**When to use.** An LLM task requires selecting which files to load from a large repo or portfolio. The total file count exceeds the context budget. You need a principled ranking that prefers files that are transitively important — cited by many important files — over files that merely have many direct imports.

**Mechanic.**

Build a directed call or import graph within a repo (or across repos for cross-repo context assembly). Run PageRank with damping factor d calibrated to the graph:

```
PR(f) = (1 − d) / n + d × Σ_{g ∈ In(f)} PR(g) / Out(g)

Default d = 0.85 (web-scale graphs)
Sparse repo import graphs: test d ∈ [0.65, 0.80] and check sensitivity
```

Rank files by PR(f). Load the top-k files that fit within the token budget. For a seeded task (e.g., "fix the authentication module"), use Personalized PageRank (PPR) instead of global PR: seed the teleportation distribution on the files directly touched by the task, then walk the graph to find the most relevant context.

```
PPR seed vector v_s:  v_s[f] = 1/|seed_files| for f in seed_files
                      v_s[f] = 0 otherwise

PPR(f) = (1 − d) × v_s[f] + d × Σ_{g ∈ In(f)} PPR(g) / Out(g)
```

PPR concentrates budget on the neighbourhood of the task rather than global hubs. This is the default mode for `scripts/query_graph.py --ppr`.

**Reverse PageRank for blast-radius ordering.** Reverse all dependency edges before running PR. The resulting scores rank files (or repos) by the breadth of their transitive dependents — which consumer footprint does this file have? This is distinct from betweenness: reverse-PR captures endorsement-chain reach, not structural bridging.

**Worked example.** A monorepo with 1,400 files. Global PageRank top-5: `src/api/router.ts`, `src/core/config.ts`, `src/db/models/base.ts`, `src/auth/session.ts`, `src/utils/logger.ts`. A bug-fix task is seeded on `src/auth/session.ts`. PPR top-5 shifts to: `src/auth/session.ts`, `src/auth/tokens.ts`, `src/middleware/auth.ts`, `src/db/models/user.ts`, `src/api/auth-routes.ts`. The global `config.ts` drops out of the budget; the auth-specific graph neighbourhood fills in. The LLM receives focused, causally connected context instead of platform-wide noise.

---

### P3 — Community Detection over Symbol-Import Graph for Context Packetizing

**Anchors: #03 community-detection, #09 graph-clustering**

**When to use.** A cross-repo LLM task spans multiple files and modules. Naively loading every related file blows the context budget. You need to identify cohesive clusters of files that are internally dense and externally sparse, then load the cluster most relevant to the task as a single "packet" — a bounded, self-coherent unit of context.

**Mechanic.**

Build a directed or undirected symbol-import or function-call graph per repo. Project to undirected (add reverse edge) if the community algorithm requires it. Run Louvain community detection:

```python
import community as community_louvain  # python-louvain
import networkx as nx

G_undirected = G.to_undirected()
partition = community_louvain.best_partition(G_undirected, resolution=gamma)
Q = community_louvain.modularity(partition, G_undirected)
```

Run at γ ∈ {0.5, 1.0, 2.0} and compare community sizes. For context packetizing:

- γ = 1.0 typically produces clusters matching architectural layers (auth, data access, API surface)
- γ = 2.0 splits large clusters into feature-level packets
- Choose the γ whose packet sizes fit the token budget (typically 20–80 files per community)

Select the community whose centroid node (highest internal PageRank within the community) is closest to the task seed node. Load only files in that community, plus their direct cross-community import edges as boundary context.

**Spectral alternative (#09).** When balanced partition size matters more than natural density — for example, when every context packet must be under a hard token limit — use spectral graph clustering (normalised cut) with k = ceil(total_files / budget_per_packet). Spectral clustering enforces rough size parity across packets; Louvain does not.

**Worked example.** A backend service with 380 files and 2,200 import edges. Louvain at γ=1.0, Q=0.47, 9 communities. Community sizes: 68, 55, 42, 38, 34, 31, 28, 24, 20. Task: "trace the billing charge path." The community containing `billing/charge.py` (size 42) is the target packet. Cross-community boundary edges add 8 files from the `payment-gateway` community. Total context: 50 files — within a 60-file budget. The LLM does not receive the authentication or reporting communities (229 files) that are structurally irrelevant to the billing path.

**Per-repo vs. portfolio.** This pattern applies per-repo to build context packets for single-service tasks. At portfolio level, apply community detection over the inter-repo dependency graph to identify service clusters (e.g., "data platform," "auth mesh," "customer-facing APIs") for architecture-wide questions. Both scales use the same algorithm; only the node definition changes.

---

### P4 — Graph Embeddings for Cross-Repo Similarity and Clone Detection

**Anchors: #10 graph-embeddings, #08 link-prediction**

**When to use.** You need to identify repos or files that play structurally similar roles across a portfolio without relying on naming conventions or shared imports. Use cases: detecting functional duplicates before a consolidation, finding the best candidate repo to own a new feature, routing a bug report to the most structurally similar service even when that service is in a different team's namespace.

**Mechanic.**

For repo-level similarity, build an inter-repo dependency graph and apply node2vec with DFS-biased walks (q < 1) to capture structural role equivalence:

```python
from node2vec import Node2Vec

model = Node2Vec(
    G,
    dimensions=64,
    walk_length=30,
    num_walks=200,
    p=1,      # return parameter (default)
    q=0.5,    # in-out parameter: q < 1 = DFS-biased = structural equivalence
    workers=4
)
embeddings = model.fit(window=10, min_count=1)
```

Two repos with similar structural roles (e.g., both are thin adapter layers between a data layer and an API surface) will have high cosine similarity in embedding space even if they share no direct dependency edges. This catches structural clones that lexical search misses.

For code-level cross-repo similarity, embed at the file or module level using a code-aware model: CodeBERT or Code2Vec produce token-informed embeddings that combine syntactic structure with semantic identity. Use these for cross-repo duplicate function detection. Compare structural node2vec embeddings (topology-based) against CodeBERT embeddings (semantic-based): repos that cluster together in both spaces are strong consolidation candidates.

**Link prediction for undeclared dependencies (#08).** Train a link prediction model on the current dependency graph: positive examples are existing edges, negative examples are randomly sampled non-edges. Evaluate Adamic-Adar, Resource Allocation, and node2vec dot-product similarity on held-out edges. Use the trained model to score all absent pairs. High-scoring absent edges are likely undeclared or informal dependencies — repos that co-evolve or share patterns without an explicit import relationship. File these as candidate edges in the knowledge graph marked `inferred`.

**Worked example.** A 60-repo platform. node2vec embeddings at d=64 computed over the inter-repo dependency graph. UMAP projection to 2D: three structural clusters emerge. Two clusters match known domain boundaries (data platform, customer APIs). The third cluster contains 8 repos — 3 labeled "payment," 2 "notification," 2 "webhook," 1 "event-bus" — with high embedding similarity. Manual inspection: all 8 are thin fan-out adapters with identical structural roles. Consolidation proposal: 8 repos → 2 typed adapter libraries. Link prediction on the same graph surfaces 4 absent edges with score > 0.85, all confirmed as informal runtime dependencies not captured in manifests.

---

### P5 — Small-World Diagnostics for Internal Package Graph Navigation

**Anchors: #04 small-world, #05 scale-free-networks**

**When to use.** Before investing in cross-repo search infrastructure or RAG, assess whether the portfolio's package dependency graph already has the small-world property. A small-world graph has short average path length — any file can reach any other file via a small hop count — which means direct graph traversal is cheap and effective. A non-small-world graph (high L, low C) signals that the portfolio is fragmented into silos and graph traversal may require long paths or bridging hubs.

**Mechanic.**

Compute the small-world coefficient σ on the inter-repo dependency graph:

```
σ = (C / C_random) / (L / L_random)

C = global clustering coefficient of the portfolio graph
C_random = 2m / n(n-1)  [expected for Erdős-Rényi with same n, m]
L = average shortest path length (largest connected component)
L_random ≈ ln(n) / ln(⟨k⟩)

σ > 1: small-world property holds
σ ≫ 1 (typically > 5): clear small-world structure
```

Use the harmonic mean for L on disconnected graphs (isolated repos or separate service clusters).

**Scale-free check (#05).** Fit a power law to the in-degree sequence of the portfolio graph. If α̂ ∈ (2, 3) with p > 0.1 (KS test), the portfolio has scale-free structure: a small number of hub repos (high in-degree) are pointed to by most of the portfolio. This confirms preferential attachment dynamics and validates hub-targeted strategies (blast-radius concentration, redundancy investment, targeted immunisation for security vulnerabilities).

**Interpretation for graph traversal.** A small-world + scale-free portfolio graph supports efficient PPR traversal: the short paths and hub connectivity mean that 2–3 hops from a seed repo typically reaches the relevant neighbourhood. A purely random or fragmented graph requires longer walks or topic-based teleportation to cover the relevant context. Set PPR max-hops accordingly.

**Worked example.** A 120-repo microservice portfolio. Measured: C=0.38, L=3.1. C_random=0.018, L_random=2.8. σ = (0.38/0.018) / (3.1/2.8) = 21.1 / 1.11 = 19.0 — clear small-world. Power-law fit on in-degree: α̂=2.6, p=0.21, x_min=4. Top 8 repos (6.7%) account for 43% of all dependency edges. Conclusion: PPR with max-hops=3 is sufficient for context traversal; the 8 hub repos should be treated as required context for any cross-portfolio question; targeted hardening of these hubs reduces build-graph fragility without requiring portfolio-wide changes.

---

### P6 — Percolation Analysis for Build-Graph Fragility

**Anchors: #06 percolation, #01 centrality-measures**

**When to use.** Before a large refactor, merger, or decommission decision, you need to quantify how many removals the build or dependency graph can absorb before becoming disconnected. This is different from blast-radius ranking (which repo causes the most downstream breakage) — percolation answers how many repos you can safely remove before the portfolio loses cohesion as a system.

**Mechanic.**

Run both removal strategies on the inter-repo dependency or build graph:

```python
import networkx as nx
import random

def percolation_curve(G, strategy="random", n_trials=100):
    """Returns list of (removal_fraction, mean_gcc_size_fraction) tuples."""
    results = []
    nodes = list(G.nodes())
    n = len(nodes)
    for q_frac in [i/20 for i in range(21)]:
        gcc_sizes = []
        for _ in range(n_trials):
            G_copy = G.copy()
            if strategy == "random":
                to_remove = random.sample(nodes, int(q_frac * n))
            elif strategy == "betweenness":
                bc = nx.betweenness_centrality(G)
                to_remove = sorted(bc, key=bc.get, reverse=True)[:int(q_frac * n)]
            G_copy.remove_nodes_from(to_remove)
            gcc = max(nx.weakly_connected_components(G_copy), key=len)
            gcc_sizes.append(len(gcc) / n)
        results.append((q_frac, sum(gcc_sizes) / n_trials))
    return results
```

Report `qc_random` (the removal fraction at which the giant component drops below 50% under random removal) and `qc_targeted` (the same threshold under betweenness-order removal). The gap between these two thresholds measures the portfolio's attack surface:

- Large gap (e.g., qc_random=0.55, qc_targeted=0.07): scale-free structure; robust to failures, fragile to targeted decommission or security breach of hub repos
- Small gap: near-random topology; resilient to targeted removal but not to random churn

**Actionable output.** The top-k betweenness repos at which the curve inflects most steeply are the hardening targets: replicate, circuit-break, or version-lock these repos before proceeding with any portfolio-wide refactor. File the qc values and target list in the hub reports directory as `reports/build-fragility.json`.

**Worked example.** A 55-repo build graph. Random percolation: GCC stable until q=0.50. Betweenness-targeted: GCC drops to 40% at q=0.09 (5 repos removed). The 5 repos are `proto-contracts`, `auth-client`, `config-loader`, `event-schema`, and `test-fixtures`. These 5 are scheduled for API-versioning and redundant-path work before the planned Q3 decomposition sprint.

---

### P7 — SIR Contagion for Defect and Vulnerability Spread Estimation

**Anchors: #07 contagion-sir, #05 scale-free-networks**

**When to use.** A critical defect or security vulnerability is discovered in a base library. You need to estimate how far it will propagate through transitive dependents before a patch is deployed — and which repos to patch first to contain the spread below a threshold.

**Mechanic.**

Model the dependency graph as a contact network. An infected repo is one that depends on the vulnerable library version. Recovery (patch) happens at rate γ (average patch cycle time). Transmission rate β is the probability per time step that an infected dependency causes a dependent repo to adopt the vulnerability (e.g., via a forced upgrade or shared artifact cache).

```
Network-aware R₀ = (β / γ) × ⟨k²⟩ / ⟨k⟩

If scale-free (P(k) ~ k^−α, α ∈ [2, 3]):
  ⟨k²⟩ diverges → R₀ > 1 for any β > 0 (vanishing threshold)
  Vulnerability spreads to a finite fraction regardless of how slowly it propagates
```

Run Monte Carlo SIR (≥ 1,000 realisations) from the vulnerable library as seed, with β and γ calibrated from historical patch cycle data:

```python
# Pseudo-code for network SIR
def sir_run(G, seed, beta, gamma, max_steps=50):
    S = set(G.nodes()) - {seed}
    I = {seed}
    R = set()
    history = [(len(S), len(I), len(R))]
    for _ in range(max_steps):
        new_I = set()
        new_R = set()
        for node in I:
            for neighbor in G.successors(node):
                if neighbor in S and random.random() < beta:
                    new_I.add(neighbor)
            if random.random() < gamma:
                new_R.add(node)
        S -= new_I
        I = (I | new_I) - new_R
        R |= new_R
        history.append((len(S), len(I), len(R)))
        if not I:
            break
    return history
```

Report median final infected fraction and 5th–95th percentile range across Monte Carlo runs. Use the community structure (#03) to identify which service cluster will hit epidemic threshold first — inter-community edges with low betweenness act as natural spread barriers.

**Immunisation strategy.** On scale-free graphs, random immunisation is inefficient (requires vaccinating ~80% of nodes to stop spread). Targeted immunisation of the top-betweenness repos reduces R₀ below 1 with far fewer patches. Rank by betweenness, patch in that order, and re-evaluate R₀ after each cohort.

**Worked example.** CVE in a shared logging library used by 32 of 80 repos. β=0.15 (one upgrade per 7-day sprint), γ=0.10 (10% of infected repos patch per sprint). Network-aware R₀=1.8. Without intervention: Monte Carlo median final infected = 61% of portfolio (49 repos), peak at sprint 4. Targeted immunisation of top-8-betweenness repos reduces R₀ to 0.7; median final infected drops to 14% (11 repos). Patch list is output as `reports/vulnerability-patch-order.json`.

---

### P8 — Link Prediction for PR Co-Touch Forecasting

**Anchors: #08 link-prediction, #10 graph-embeddings**

**When to use.** A developer opens a PR that touches repos A and B. Before review, you want to predict whether this PR (or the feature it implements) will also require changes in repos C, D, or E — based on historical co-change patterns. Surface these predictions as a checklist in the PR description or hub catalog page.

**Mechanic.**

Build a temporal co-change graph: nodes are repos, edges carry a weight equal to how many historical PRs (or commits) touched both repos in the same batch. This is an undirected weighted graph. Remove edges older than a configurable time window (default: 90 days) to avoid stale co-change signal.

Apply multiple link prediction indices on this co-change graph. For the PR seed set {A, B}, score all absent edges from {A, B} to the rest of the portfolio:

```
Common Neighbors:     |Γ(A) ∩ Γ(X)| + |Γ(B) ∩ Γ(X)|  for each candidate X
Adamic-Adar:          Σ_{z ∈ Γ(A)∩Γ(X)} 1/log(kz) + (same for B)
node2vec dot product: embed(A)·embed(X) + embed(B)·embed(X)
```

Combine scores by rank-order fusion (Borda count across indices). Threshold at the 80th percentile of historical co-touch rates to produce a short candidate list (≤ 5 repos). Present as a "likely also touches" checklist.

**Temporal leakage guard (#11).** The co-change graph must use only commits and PRs whose timestamps are strictly before the current PR date. Sliding-window evaluation (30/60/90-day windows) on historical data provides AUC estimates; use the window with highest AUC for the production predictor.

**Worked example.** A platform with 45 repos. PR touches `api-gateway` and `auth-service`. Co-change graph (90 days, 340 multi-repo PRs). Adamic-Adar top-3 candidates: `user-profile` (score 4.2), `session-store` (score 3.8), `token-refresh` (score 3.1). Historical precision at top-3: 71% (PR actually touched at least one of the top-3 in 71% of similar historical PRs). The PR checklist adds: "Based on historical co-change, this PR may also require changes in: user-profile, session-store, token-refresh."

---

### P9 — Temporal Co-Change Networks for Coupling Detection

**Anchors: #11 temporal-networks, #03 community-detection**

**When to use.** A portfolio accumulates implicit coupling over time: repos that should be independent are repeatedly modified together. This is invisible in the static dependency graph (no import edges) but visible in git history as temporal co-change patterns. Detecting these temporal edges reveals hidden architectural debt before it becomes a hard dependency.

**Mechanic.**

Parse git log across all repos with a shared timestamp axis:

```bash
# Extract per-repo commit history with timestamps
git -C <repo_path> log --format="%H %ae %ci" --name-only
```

Build a temporal co-change graph: edge (A, B, t) exists if repos A and B were modified in the same commit batch or pull request at time t. Compute the inter-event time distribution per pair (A, B) and the burstiness parameter:

```
B = (σ_τ − μ_τ) / (σ_τ + μ_τ)

B > 0: bursty co-change (episodic coupling — sprints or features)
B ≈ 0: Poisson co-change (persistent coupling — shared codebase)
B < 0: regular co-change (release-cycle coupling)
```

Bursty pairs with high co-change weight are feature-coupled: they move together during specific features but not continuously. These are good candidates for explicit integration tests but not necessarily for dependency edges. Poisson (regular) pairs with B ≈ 0 and high weight are persistently coupled — strong candidates for merge, shared library extraction, or declared dependency.

Run community detection on the aggregated co-change graph (sum edge weights across time window) to identify temporal coupling clusters. Compare these clusters against the static import-graph communities (#03): divergence between the two partitions reveals ghost coupling — repos that are logically independent (no import edges) but operationally coupled (always changed together).

**Worked example.** A 30-repo portfolio over 180 days, 1,200 multi-repo commits. Temporal co-change graph: 22 active pairs. Static import graph: 18 edges. Divergent pairs (co-change but no import edge): `analytics-service` ↔ `event-schema` (B=0.12, 34 co-change events), `pricing-engine` ↔ `feature-flags` (B=0.08, 28 co-change events). Both pairs have Poisson-like burstiness (B ≈ 0) — persistent operational coupling without formal dependency. Recommendation: add declared dependency edges and shared schema versioning for both pairs. Filed as `reports/ghost-coupling.json`.

---

## Anti-Pattern Catalog

### A1 — Using Degree Centrality Alone to Identify Blast-Radius Bottlenecks

**Anchors: #01 centrality-measures**

**Problem.** High in-degree (many direct consumers) is a proxy for importance, not for structural bottleneck risk. A high-degree hub whose consumers are all also directly connected to each other has low betweenness — removing it does not disconnect the graph. A low-degree bridge has high betweenness — removing it splits the portfolio into disjoint clusters.

**Consequence.** Prioritising refactor risk by dependency count will protect the wrong repos. The actual bottlenecks remain unidentified until a change cascades through them unexpectedly.

**Fix.** Always compute betweenness alongside degree when prioritising blast-radius analysis. Report both metrics. Use betweenness as the primary ordering for hardening and versioning decisions. Use degree as a secondary tiebreaker and as a signal for documentation and discoverability investment.

---

### A2 — Aggregating Git History Into a Static Graph Before Temporal Analysis

**Anchors: #11 temporal-networks**

**Problem.** Building a single "co-change graph" by summing all historical co-change events produces an upper-bound reachability estimate that overestimates coupling. It cannot distinguish episodic (feature-sprint) coupling from persistent coupling, and it cannot detect whether a coupling pattern has decayed or shifted in recent history.

**Consequence.** Link prediction trained on the aggregated graph includes stale co-change signal. Coupling reports flag pairs that were coupled during a now-completed migration but have since decoupled.

**Fix.** Use a sliding time window (90 days default; tune per portfolio release cadence). Compute burstiness B per pair to classify coupling type. Re-run community detection on the recent window and compare against the 12-month aggregate to detect decoupling trends. Always timestamp graph snapshots and report the window explicitly.

---

### A3 — Running Community Detection Once at Default Resolution

**Anchors: #03 community-detection**

**Problem.** Louvain at γ=1.0 (default) is subject to the resolution limit: it merges small but dense communities into larger ones and misses fine-grained structure. A single run is also non-deterministic. Running once and treating the result as ground truth produces community assignments that may merge distinct service clusters or split coherent clusters arbitrarily.

**Consequence.** Context packets assembled from a single-run community partition may be too large (budget-busting) or too small (missing required context). Architecture clusters used for portfolio queries will have unstable membership across re-runs.

**Fix.** Run Louvain 10–50 times per resolution level. Use consensus clustering (majority-vote partition) across runs to stabilize membership. Always test γ ∈ {0.5, 1.0, 2.0} and report Q and community size range at each level. Choose γ for context packetizing based on budget fit, not default. Use Leiden (via `igraph` or `graspologic`) for portfolios > 1,000 nodes, as it provides stronger connectedness guarantees.

---

### A4 — Applying Global PageRank When the Question Is Seeded

**Anchors: #02 pagerank**

**Problem.** Global PageRank ranks nodes by their structural authority across the entire graph. For a task seeded on a specific file, module, or repo, global PR will surface platform-wide hubs (config, logger, base classes) that are important globally but often irrelevant to the task at hand. These hubs consume context budget without contributing to the specific repair or analysis.

**Consequence.** LLM tasks receive generic architectural context instead of task-relevant context. Bug-fix context windows fill with unrelated infrastructure files. Retrieval precision drops.

**Fix.** Use Personalized PageRank (PPR) seeded on the task-specific files or repos for any non-global question. Reserve global PR for global questions: "what are the most critical files in the entire portfolio?" or "which repos should be documented first?" The `--ppr` flag in `scripts/query_graph.py` implements seeded PPR.

---

### A5 — Merging Symbol-Level Graphs Into the Portfolio Knowledge Graph

**Anchors: #03 community-detection, #01 centrality-measures**

**Problem.** Symbol-level graphs (function calls, class inheritance, variable references) from `dev-context-code-graph` operate at a different granularity than the portfolio dependency graph. Merging them creates a single giant graph with mixed node types, making centrality and community detection results uninterpretable: a utility function with 500 call sites will dominate betweenness rankings, drowning out repo-level structural signals.

**Consequence.** Centrality rankings mix intra-repo and inter-repo structure. Community detection produces clusters that span both symbol-level and repo-level granularity, resulting in nonsensical context packets.

**Fix.** Keep symbol-level graphs as per-repo artifacts owned by `dev-context-code-graph`. Import only per-repo summary statistics (top-k betweenness files, community assignments, cyclomatic complexity hotspots) as node attributes on the portfolio graph nodes. Apply network science queries at each level independently. Cross-level queries should extract the relevant sub-graph at one level at a time.

---

## Recipes

### R1 — Refactor Impact Report: Which Repo Owns the Blast Radius?

**Scenario.** A breaking API change is planned in one or more source repos. The team needs a ranked list of affected repos and a recommendation on refactor sequencing.

**Steps.**

1. **Build the dependency graph.**

   ```bash
   python scripts/build_knowledge_graph.py --output graphs/system-edges.json
   ```

   Verify that the graph covers all portfolio repos with `scripts/validate_graph.py`.

2. **Compute betweenness centrality (P1).**

   ```bash
   python scripts/query_graph.py --impact <changed-repo> --metric betweenness
   ```

   Output: ranked list of repos by normalised betweenness on the subgraph reachable from the changed repo.

3. **Simulate targeted percolation (P6).**

   Remove the changed repo and its top-3 betweenness neighbours from the graph. Measure GCC size before and after. If GCC drops > 30%, the change crosses a percolation threshold — treat as a high-risk structural change requiring redundancy scaffolding before the refactor proceeds.

4. **Run reverse PageRank for consumer breadth (P2).**

   ```bash
   python scripts/query_graph.py --rank <changed-repo> --reverse
   ```

   Output: repos ranked by transitive consumer footprint. High reverse-PR repos are the most indirect consumers.

5. **Generate the report.**

   Write `reports/refactor-impact-<changed-repo>-<date>.md` with:
   - Top-10 betweenness-ranked affected repos (direct and transitive)
   - GCC impact summary (percolation test result)
   - Top-10 reverse-PR consumer repos
   - Recommended patch order: high-betweenness brokers first, then high-reverse-PR consumers
   - Confidence labels: `verified` for manifest-traced edges, `inferred` for graph-topology-only edges

6. **Link the report from the affected repo's catalog page.**

   ```bash
   # Add to catalog/<changed-repo>.md under ## Reports
   echo "- [Refactor Impact $(date +%Y-%m-%d)](../../reports/refactor-impact-<repo>-<date>.md)" \
     >> catalog/<changed-repo>.md
   ```

**Primitives used:** #01, #02, #06.

---

### R2 — Context Packet Assembly for an LLM Repair Task

**Scenario.** A repair or feature task is assigned to an LLM agent. The task seed is a set of 2–5 files or one repo. The agent needs a focused, self-coherent context packet within a token budget.

**Steps.**

1. **Identify the task seed.**

   Define the seed set S = {files or repo nodes directly touched by the task description}. If the task is repo-level, set S = {repo node}.

2. **Run Personalized PageRank (P2).**

   ```bash
   python scripts/query_graph.py --ppr --seed <comma-sep-nodes> --budget 60
   ```

   Output: ranked list of up to 60 files/repos by PPR score. These are the globally most connected nodes within the task neighbourhood.

3. **Identify the community of the seed node (P3).**

   ```bash
   python scripts/query_graph.py --communities --resolution 1.0 --node <seed-node>
   ```

   Output: community ID and member list for the seed node. Compare community size against the token budget.

4. **Select the context packet.**

   - If PPR top-k (≤ budget) and the seed community members overlap substantially (Jaccard > 0.6), prefer the community as the packet boundary — it is more architecturally coherent.
   - If the community is too large (> 1.5× budget), use PPR top-k as the packet.
   - Add cross-community boundary edges: the 5 highest-weight edges from the selected packet to outside repos/files as boundary context.

5. **Load and validate.**

   Load the selected files. Verify that no file in the packet is stale (check `reports/drift.json`). If stale, note it in the context preface.

6. **Pass to the LLM agent with context preface.**

   ```
   Context Packet: <community-name or PPR-seeded>
   Seed: <seed-nodes>
   Method: [Community γ=1.0 / PPR d=0.85 seed=<seed>]
   Boundaries: <boundary-files>
   Stale: <any stale nodes>
   Token estimate: <n>
   ```

**Primitives used:** #02, #03, #09.

---

### R3 — PR Scope Forecast: Which Sibling Repos Will This PR Touch?

**Scenario.** A developer opens a PR touching repos A and B. The hub agent should predict additional repos likely to require changes and surface them as a checklist before review.

**Steps.**

1. **Build or refresh the co-change graph (P9).**

   ```bash
   python scripts/build_knowledge_graph.py --co-change --window-days 90
   ```

   This produces `graphs/co-change-graph.json` with weighted edges and timestamps.

2. **Compute link prediction scores (P8).**

   For the PR seed set {A, B}, compute Common Neighbors, Adamic-Adar, and (if embeddings are available) node2vec dot-product similarity for all absent edges from {A, B} to the portfolio.

   ```bash
   python scripts/query_graph.py --link-predict --seed A,B --graph co-change --top 5
   ```

3. **Check temporal validity.**

   Ensure the co-change graph snapshot predates the current PR date. Reject any edge whose most recent co-change event is older than the configured window.

4. **Filter by confidence threshold.**

   Retain only candidates above the 80th-percentile historical co-touch rate. This typically yields ≤ 5 candidates.

5. **Run a community check (P3).**

   Verify that the candidates and {A, B} are in the same or adjacent communities in the static dependency graph. Candidates from entirely disconnected communities are likely false positives from coincidental co-change.

6. **Output the checklist.**

   Write to the PR description or the hub catalog page for repo A:

   ```markdown
   ## Predicted Co-Touch Repos
   Based on 90-day co-change history (Adamic-Adar + node2vec):
   - [ ] `repo-C` — co-change score 4.2, historical precision 71%
   - [ ] `repo-D` — co-change score 3.8
   - [ ] `repo-E` — co-change score 3.1
   ```

7. **Measure prediction accuracy post-merge.**

   After the PR merges, record whether the predicted repos were actually touched. Accumulate this as calibration data for the prediction model. Re-run `scripts/calibrate_weights.py` after every 50 PRs.

**Primitives used:** #08, #09, #11.

---

## Cross-References

- Foundation layer: `foundations-network-science` — all 11 primitives referenced in this file live in `assets/templates/network-science/`
- Graph operations: [references/knowledge-graph-patterns.md](knowledge-graph-patterns.md) — schema, weight calibration, PPR, community detection, bitemporal slices
- Single-repo symbol graphs: [dev-context-code-graph SKILL.md](../../dev-context-code-graph/SKILL.md) — use before merging symbol-level centrality into the portfolio graph
- Hub freshness: [references/hub-freshness-checking.md](hub-freshness-checking.md) — stale-graph detection before running centrality or percolation queries
- Large portfolio strategy: [references/large-portfolio-strategy.md](large-portfolio-strategy.md) — incremental graph compilation for portfolios > 100 repos
- Scripts: `scripts/build_knowledge_graph.py`, `scripts/query_graph.py`, `scripts/calibrate_weights.py`, `scripts/validate_graph.py`
