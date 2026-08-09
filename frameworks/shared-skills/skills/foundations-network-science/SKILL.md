---
name: foundations-network-science
description: Network-science primitives for graph systems, centrality, PageRank, communities, contagion, link prediction, and temporal networks. Use when analyzing graph structure.
compatibility: Portable core only.
version: "1.1"
last_validated: 2026-07-11
---

# Network Science Foundations


11 canonical network-science primitives, each solving a distinct structural or dynamic analysis problem. Primitives are domain-agnostic: the same PageRank that ranks web pages ranks citation authority, package influence, and audience amplification. The same percolation threshold that governs epidemic spread governs cascading failure in dependency graphs.

## When to Apply

**Apply network-science when:**
- The data IS a graph — citations, dependencies, follower graphs, supply chains, knowledge graphs
- Spread/contagion question — viral coefficient, R₀, percolation threshold
- Centrality question — "which nodes are critical?" (PageRank, betweenness, eigenvector)
- Community detection — clustering nodes by structural similarity (Louvain, Leiden)
- Blast-radius / dependency-impact analysis on services or modules

**Skip and use simpler alternatives when:**
- Data is tabular and relationships aren't structural — standard analytics suffices
- Graph has < 50 nodes — visual inspection beats algorithmic centrality
- Question is about strategic interaction at the node level — use foundations-game-theory
- Question is about queue or flow through a single bottleneck — use foundations-queueing-theory or theory-of-constraints
- Edges are weak proxies (e.g. "users who viewed both products") — centrality is unreliable; validate edge semantics first
- "Network effects" is a marketing claim, not a measured viral coefficient — quantify R first or skip the analysis

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Expert Judgment](#expert-judgment)
- [Composition Recipes](#composition-recipes)
- [Related Skills](#related-skills)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| Primitive | Core Question | Typical Input |
|-----------|--------------|---------------|
| [Centrality Measures](#1-centrality-measures) | Which node matters most, and by what criterion? | Unweighted or weighted graph |
| [PageRank](#2-pagerank) | Who is authoritative via inbound endorsements? | Directed graph with optional weights |
| [Community Detection](#3-community-detection) | Which nodes form cohesive clusters? | Undirected or directed graph |
| [Small-World Networks](#4-small-world-networks) | Is the graph navigable despite size? | Any graph |
| [Scale-Free Networks](#5-scale-free-networks) | Does degree follow a power law? | Degree sequence or full graph |
| [Percolation](#6-percolation) | At what removal threshold does the graph fragment? | Graph + removal strategy |
| [Contagion / SIR](#7-contagion--sir-model) | How far and fast does influence or disease spread? | Graph + transmission probability |
| [Link Prediction](#8-link-prediction) | Which absent edges are likely to form? | Observed snapshot of graph |
| [Graph Clustering](#9-graph-clustering) | How to partition nodes by structural similarity? | Graph with optional edge weights |
| [Graph Embeddings](#10-graph-embeddings) | How to represent nodes as dense vectors? | Graph structure + optional node features _(For cross-domain transfer with zero labels, see Graph Foundation Models: Liu et al. TPAMI 2025.)_ |
| [Temporal Networks](#11-temporal-networks) | How does time ordering of edges change reachability? | Time-stamped edge list |

---

## Primitive Index

Each primitive has a full playbook: Definition / When to use / Inputs / Outputs / Failure modes / Worked example / Sources.

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [Centrality Measures](assets/templates/network-science/01-centrality-measures.md) | Wrong centrality used — high degree ≠ high betweenness ≠ high influence |
| 2 | [PageRank](assets/templates/network-science/02-pagerank.md) | Naive in-degree conflates volume with authority |
| 3 | [Community Detection](assets/templates/network-science/03-community-detection.md) | Arbitrary k-means on graph ignores topology |
| 4 | [Small-World Networks](assets/templates/network-science/04-small-world.md) | Assuming large graphs are either fully random or fully regular |
| 5 | [Scale-Free Networks](assets/templates/network-science/05-scale-free-networks.md) | Designing resilience for hubs that may not exist |
| 6 | [Percolation](assets/templates/network-science/06-percolation.md) | Ignoring phase transitions — small removals can catastrophically fragment |
| 7 | [Contagion / SIR](assets/templates/network-science/07-contagion-sir.md) | Linear spread assumptions on networked systems |
| 8 | [Link Prediction](assets/templates/network-science/08-link-prediction.md) | Random-guess recommendations miss structural proximity |
| 9 | [Graph Clustering](assets/templates/network-science/09-graph-clustering.md) | Treating clustering as unstructured k-means; ignoring conductance |
| 10 | [Graph Embeddings](assets/templates/network-science/10-graph-embeddings.md) | One-hot node encodings lose all structural information |
| 11 | [Temporal Networks](assets/templates/network-science/11-temporal-networks.md) | Aggregating time-stamped edges loses causal ordering |

---

## Formal Supporting Theory

Load [`references/formal-theory-map.md`](references/formal-theory-map.md) when the analysis depends on graph assumptions: directed vs. undirected edges, weighted vs. unweighted measures, random-walk stationarity, modularity limits, power-law testing, percolation thresholds, epidemic dynamics, link-prediction leakage, embedding validity, or temporal reachability.

## Misuse Boundaries

Load [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before publishing graph rankings, communities, scale-free claims, diffusion forecasts, dependency blast-radius scores, or embedding explanations. It contains scenario playbooks, anti-patterns, known traps, and validation checks.

---

## Decision Checklist

- [ ] **Influence / importance ranking**: Which single node matters most? → choose the right centrality (#1); if endorsement-weighted → PageRank (#2)
- [ ] **Cluster structure**: Do nodes group into cohesive communities? → community detection (#3) — use Louvain/Leiden for descriptive partitioning; if the question is "does community structure exist?" or requires statistical model comparison → inferential SBM (#3, Failure Mode 7); if cut-minimization is the goal → graph clustering (#9)
- [ ] **Navigation / reachability**: Is average path length short despite size? → small-world test (#4)
- [ ] **Degree distribution**: Does degree follow a power law? Test before claiming scale-free (#5)
- [ ] **Robustness / fragility**: How many nodes must be removed to break connectivity? → percolation (#6)
- [ ] **Spread / contagion**: How far does a signal reach from a seed? → SIR model (#7); if spread requires social reinforcement or multiple exposures (technology adoption, norm diffusion, behaviour change) → threshold / complex contagion model (#7, Failure Mode 7), not SIR
- [ ] **Missing edge inference**: Which edges are likely to form next? → link prediction (#8)
- [ ] **Node similarity / downstream ML**: Need node vectors for classification or recommendation? → graph embeddings (#10)
- [ ] **Temporal causality**: Do edge timestamps change what is reachable? → temporal networks (#11)
- [ ] **Higher-order structure test**: Before applying community detection (#3) or temporal-network analysis (#11) to a hypergraph dataset, run a reducibility test (Lucas et al. 2026) — if degree heterogeneity is low, pairwise methods remain valid; if high, use higher-order methods to avoid underfitting.

---

## Anti-Patterns

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Degree centrality used when betweenness is the right measure | High-degree nodes are not always the best bridges; bridges have high betweenness regardless of degree | Clarify the question: information brokers → betweenness; most-connected hub → degree; fastest spreader → closeness |
| Modularity treated as ground truth (resolution limit ignored) | Modularity optimization misses small communities and merges large ones at scale | Pair modularity with resolution parameter scan; verify with NMI against ground truth if available (Fortunato 2010) |
| Scale-free claimed without statistical test | Visual inspection of log-log degree plots is unreliable — Gaussian and log-normal distributions look similar in log-log | Run a maximum-likelihood power-law fit and report the p-value and xmin (Clauset, Shalizi & Newman 2009) |
| Percolation reasoning on directed networks treated as undirected | Directed graphs have separate in-component and out-component; removing a node in-component does not break out-component reachability | Compute giant weakly connected component and giant strongly connected component separately (Newman 2010) |
| Temporal-network paths confused with static-network paths | An edge at t=5 cannot precede an edge at t=3 even if it would on a static graph; temporal reachability is strictly smaller | Use time-respecting path algorithms; static-graph reachability overestimates spread (Holme & Saramäki 2012) |
| PageRank used on sparse undirected graphs without damping tuning | Default damping d=0.85 was calibrated for the web graph; sparse or small graphs need different d | Sensitivity-test d ∈ [0.5, 0.95]; report the chosen value and its effect on rank stability |
| Community detection applied to graphs with < 50 nodes | Modularity gains are trivially achievable on small graphs; results are statistically meaningless | Use visualisation and domain knowledge for small graphs; reserve community detection for N ≥ 100 |
| SIR model run on a group-interaction network (e.g. household spread, team transmission) without higher-order correction | Group interaction models produce a dual epidemic threshold and potential bistable regime absent in pairwise SIR (Ferraz de Arruda 2024, Nat. Rev. Phys.); pairwise SIR systematically understates outbreak risk | If the dataset has documented group events, use a hypergraph contagion model; check for bistability before setting intervention thresholds |
| Applying pairwise community detection to a high-degree-heterogeneity hypergraph | Reducibility analysis (Lucas 2026) shows co-authorship-style networks cannot be collapsed to pairwise edges without dynamical information loss | Run the reducibility test first; if degree heterogeneity is high (e.g. χ > 0.5 for the dataset's irreducibility score), use a higher-order community detection method |
| Assuming pairwise edges are sufficient for temporal network inference | >60% of real EEG dynamics are non-pairwise; pairwise temporal models can systematically underfit | Before committing to standard temporal edges, test higher-order fit using THIS (Arnaudon 2025) if time-series data is available |

---

## Expert Judgment

The failure modes above are mechanical — wrong formula, missing test, unnormalised score. This section is about the judgment calls a mechanical checklist cannot make for you: which question is actually being asked, whether the data supports answering it, and whether "network" is even the right frame.

### Which centrality answers which business question

Centrality choice is usually presented as a technical decision. In practice it is a translation problem: someone asks "who matters most?" in business language, and that phrase maps to different math depending on what they mean by "matters." Get the translation wrong and the analysis is precise but irrelevant.

| Business question | Right measure | Why the obvious choice is often wrong |
|---|---|---|
| "Who do we lose the most by losing?" (churn/attrition risk) | Betweenness, or articulation-point test | Degree picks the loudest node, not the one holding two subgraphs together. A quiet node with low degree can be a single point of failure. |
| "Who should get the retention budget to prevent contagion-style churn?" | Eigenvector / PageRank | Losing a customer connected to other high-value customers has second-order costs that raw connection count misses. |
| "Whose endorsement carries the most weight?" (authority, credibility) | PageRank / eigenvector | Volume of inbound links or mentions rewards spam and popularity contests; authority requires weighting by the endorser's own standing. |
| "Who can broadcast a message fastest?" | Closeness | High degree does not imply short average distance to everyone else if the high-degree node sits in a peripheral cluster. |
| "Which service/package, if it breaks, takes down the most of the system?" | Reverse PageRank (transitive dependents) + betweenness (bridges) | Direct dependents undercount blast radius; betweenness alone misses volume of downstream impact. Use both, not either. |
| "Who has the biggest raw audience?" | Degree | This is the one case where degree is usually the right answer — but confirm the question is really about raw reach, not influence or bridging. |
| "Where should we seed a marketing campaign?" | Depends on the contagion mechanism — see diffusion-model choice below | Seeding by PageRank/degree is correct for simple (single-exposure) contagion but actively wrong for complex (reinforcement-needed) contagion. |

The recurring error is treating "importance" as one thing. Before computing anything, restate the business question as "a node such that removing/promoting/notifying it does X" — that sentence usually reveals which centrality is implied.

### Sampling bias: the network you measure is not the network that exists

Almost no analyst works with the true underlying graph. API rate limits, crawl depth limits, consent/opt-in populations, and snowball sampling all produce a **subnet**, not the network. This matters more than most failure-mode checklists suggest, because the bias is not random noise — it is systematic and direction-specific:

- **Degree-biased discovery**: high-degree nodes are easier to find (more paths lead to them), so crawls and snowball samples over-represent hubs and under-represent the long tail. This inflates apparent centralization and can manufacture the appearance of a heavy-tailed degree distribution from a true distribution that is not heavy-tailed at all.
- **The subnet is not the same distribution family as the parent**: Stumpf, Wiuf & May (2005, PNAS) prove that random subsampling of a scale-free network does not, in general, yield a scale-free subnet — and the reverse inference (subnet looks scale-free ⇒ population is scale-free) is equally unsafe. This is a structural reason, independent of the Broido–Clauset debate, to distrust degree-distribution claims made from partial crawls.
- **Survivorship bias compounds it**: inactive, deleted, or churned nodes are typically missing from the snapshot, which further skews measured centrality and community structure toward currently-active, currently-visible entities.
- **What to do**: before reporting a degree distribution, centrality ranking, or community structure, state explicitly how the graph was collected (full census, API crawl to depth d, snowball from k seeds, opt-in panel) and treat any claim about the *shape* of the distribution as conditional on that collection method. If the collection method is degree-biased, prefer rank-based or relative comparisons within the sample over absolute claims about the population.

### When the network frame itself misleads

Not every relational dataset should be analyzed as a network, and not every network metric on a valid graph means what it appears to mean.

- **Near-complete / dense graphs**: centrality and community detection are diagnostic tools for *structure* — variation in connectivity across the graph. On a graph where most nodes connect to most other nodes (density approaching 1), every centrality measure converges toward the same ranking and modularity cannot find meaningful cuts, because there is no structural variation to detect. If average degree is within an order of magnitude of n−1, run centrality/community detection with the expectation that the output may reflect edge-collection noise more than real structure — check density before, not after, running the analysis.
- **Bipartite projection inflates clustering artificially**: converting a two-mode graph (users × products, authors × papers) into a one-mode projection (users connected if they bought the same product) manufactures cliques by construction — any two users of the same popular product become "connected," and any three users of the same product form a "triangle." The resulting clustering coefficient is an artifact of the projection, not evidence of real triadic closure or community structure in user behavior. If a bipartite projection is unavoidable, weight edges by co-occurrence strength and compare against a projected-random-bipartite null model before interpreting clustering or community results — never take the raw projected clustering coefficient at face value.
- **Weak-proxy edges break centrality semantics**: an edge meaning "viewed the same page" or "mentioned in the same document" is not the same kind of relationship as "follows" or "cites," and centrality measures assume a consistent edge semantic across the whole graph. Mixing strong ties (explicit follow) and weak proxies (co-occurrence) in one adjacency matrix produces a centrality score that answers no coherent question. Validate that all edges mean approximately the same thing before computing centrality, and if they don't, build separate graphs per edge type rather than merging them into one weighted graph.

### Diffusion-model choice by phenomenon, not by default

Defaulting to SIR for every spread question is the single most common judgment error in applied contagion modelling. The right model depends on the exposure mechanism, not on which model is best known:

| Phenomenon | Exposure mechanism | Right model | Signature that distinguishes it |
|---|---|---|---|
| Biological disease, forwarded messages, software vulnerability propagation | Single contact is sufficient to transmit | SIR / SIS (simple contagion) | Clustering *slows* spread (redundant ties waste exposure opportunities on already-infected neighbours) |
| Technology adoption, norm change, health behaviour change, feature uptake | Requires multiple independent reinforcing exposures before adoption | Watts threshold model (complex contagion) | Clustering *accelerates* spread (repeated exposure from the same tight-knit group reinforces the decision); cascades come from clustered seed sets, not high-degree seed sets |
| Household/team/event-based transmission | Group exposure, not pairwise contact | Hypergraph/simplicial contagion model | Dual epidemic threshold and possible bistability — pairwise SIR systematically understates risk (Ferraz de Arruda et al. 2024) |
| Rumour/misinformation with source credibility effects | Mixture of single-exposure and reinforcement, credibility-weighted | Neither pure SIR nor pure threshold — hybrid or empirically fit model | Neither pure signature holds cleanly; validate against held-out spread data rather than assuming |

The practical test: ask "would one credible contact be enough, or does this require seeing it from more than one direction first?" If the answer is "one is enough," use SIR and seed by PageRank/degree/betweenness as appropriate. If the answer is "it takes social proof," use the threshold model and seed clustered, not high-degree, nodes — seeding a threshold-model cascade with the highest-degree hub is a common and costly mistake, because a single hub cannot supply the repeated exposure a threshold model requires.

---

## Composition Recipes

### AI-Search Citation Flow

**Goal**: rank documents and authors by structural authority in a citation network, surface topical clusters.

**Stack**:
1. **PageRank (#2)** — assign authority scores using directed citation edges; damp at 0.85 for large corpora
2. **Topical authority overlay** — weight edges by semantic similarity between citing and cited abstract (cosine on embeddings) before computing PageRank
3. **Community detection (#3)** — Louvain on the undirected projection to surface research communities; label each community with top-PageRank node
4. **Output**: per-node authority score + community membership → ranked results with cluster context

**Failure modes to check**: resolution limit in community detection on very large citation graphs; scale-free test on degree before assuming hub-based spreading.

**Inputs:** directed citation graph (edge list: citing → cited), optional semantic embeddings for abstract-similarity weighting, damping factor d (default 0.85), modularity resolution ε.
**Rules:** PageRank score Pᵢ = (1−d)/N + d·Σⱼ Pⱼ/Lⱼ (Lⱼ = out-degree of j); iterate until max|ΔP|<10⁻⁶. Community detection: Louvain greedy until ΔQ<ε; label each community with its top-PageRank node. Resolution limit: communities smaller than √(m/2) (m = edge count) may be merged — scan ε ∈ [0.5, 1.5] to verify.
**Outputs:** per-node PageRank authority score, community assignment per node, community sizes, ranked results list with cluster label.

---

### Blast Radius Across a Dependency Graph

**Goal**: given a package or module change, estimate how many downstream dependents are affected and identify critical bridges.

**Stack**:
1. **Directed graph construction** — nodes are packages/modules; directed edge A→B means A depends on B
2. **Reverse PageRank (#2)** — reverse all edges; run PageRank to find nodes with most transitive dependents
3. **Betweenness centrality (#1)** — identify bridge packages that, if removed or changed, disconnect large portions of the graph
4. **Community detection (#3)** on the undirected projection — group tightly-coupled modules into blast clusters; a change inside a cluster propagates to the whole cluster
5. **Percolation (#6)** — simulate targeted removal of the changed package(s) to estimate giant-component fragmentation

**Output**: blast-radius score per package + bridge list + cluster boundaries.

**Inputs:** directed dependency graph (edge list: A→B means A depends on B), changed package(s) as seed nodes, removal simulation count (Monte Carlo N ≥ 1 000).
**Rules:** Reverse all edges, then run PageRank to rank transitive dependent exposure. Betweenness centrality Cᴮ(v) = Σₛ≠ᵥ≠ₜ σₛₜ(v)/σₛₜ; flag top-5% as bridge nodes. Percolation: remove seed package(s), measure giant weakly connected component size S; if S drops > 20% of original, classify as critical blast. Community detection (Louvain) groups tightly coupled modules — a change inside a cluster propagates to the full cluster.
**Multilayer caveat (P1):** if the dependency graph spans distinct infrastructure layers (e.g. application tier → database tier → network tier), treat it as an interdependent (multilayer) network. Cross-layer dependency links convert the percolation transition from second-order (gradual) to first-order (abrupt, catastrophic) — a small cascade can produce complete collapse with no early warning signal from the single-layer S(q) curve. Confirm whether cross-layer coupling links exist before reporting single-layer percolation thresholds as the operational limit (Artime et al. 2024, Nat. Rev. Phys.).
**Outputs:** blast-radius score per changed package (% of graph reachable), ranked bridge node list with betweenness scores, community cluster map with cluster sizes, percolation phase indicator (critical / non-critical).

---

### Audience Reach Forecast

**Goal**: predict how far and fast a message spreads from a seed set of users in a social or content network.

**Stack**:
1. **Degree distribution test (#5)** — verify whether the network is scale-free (power-law degree); hubs amplify spread non-linearly
2. **SIR contagion model (#7)** — set β (transmission rate) from historical engagement data; γ (recovery/churn) from observed drop-off; run Monte Carlo over the network
3. **Percolation threshold (#6)** — compute R₀ = β/γ × ⟨k²⟩/⟨k⟩; if R₀ > 1, expect a giant infected component; if R₀ < 1, epidemic dies out
4. **PageRank (#2)** — seed the SIR from high-PageRank nodes to maximise expected reach
5. **Output**: expected reach distribution + confidence interval + percolation-phase indicator (above/below threshold)

**Failure modes to check**: SIR assumes homogeneous mixing; use network-aware SIR not mean-field approximation. Temporal burstiness (#11) reduces effective R₀ compared to static-graph prediction.

**Inputs:** social/content network graph (edge list), average invites per user k, conversion rate p, degree distribution moments ⟨k⟩ and ⟨k²⟩, transmission rate β and recovery rate γ (from historical engagement/drop-off data), target reach metric, seed budget (number of seed nodes).
**Rules:** Viral coefficient R = k·p; subcritical if R < 1 (epidemic dies out), supercritical if R ≥ 1. Network SIR threshold R₀ = (β/γ)·⟨k²⟩/⟨k⟩; if R₀ > 1, giant infected component forms regardless of R. Target R ∈ [0.70, 0.85] for stable durable growth. Cost per acquired user = ($/successful invite) × 1/(1−R). Seed selection: pick top 5% by betweenness centrality for cross-cluster cascade; top 5% by degree for within-neighborhood awareness.
**Outputs:** viral coefficient R and recommendation to adjust k or p, expected viral cycles 1/(1−R), predicted reach percentile with confidence interval, cost-per-acquisition at current and target R, percolation phase indicator (above/below R₀ threshold), ranked seed list with centrality scores.

**Worked example:** Referral program tuning. Network has ⟨k⟩=8, ⟨k²⟩=120 (mildly heavy-tailed). Each user invites k=4 contacts, conversion p=0.15 → viral coefficient R = k·p = 0.60 (subcritical; epidemic dies out). Percolation check: R₀ = β/γ × ⟨k²⟩/⟨k⟩ = 0.15/1.0 × 120/8 = 2.25 — but that is the network-SIR threshold, which is above 1, meaning the network topology can sustain spread if β is raised. To reach viral coefficient R≥1 in the referral flow: raise k to 7 (UX limit) or p to 0.26 (incentive bump). Cost model: $5/successful referral × expected viral cycles 1/(1−R). At R=0.60: 1/0.40 = 2.5 cycles → $12.50/acquired user. At R=0.85: 1/0.15 = 6.7 cycles → $33.50/user but growth is stable. At R=0.97: 33 cycles → $165/user and fragile (one channel drop below 1 kills the wave). Target R∈[0.70, 0.85] for durable growth without runaway cost. Seed-set: pick top 5% by betweenness centrality, not degree — bridge nodes propagate across clusters; high-degree hubs saturate their own neighborhood quickly and stall.

---

### GraphRAG Corpus Partitioning

**Goal**: partition a document corpus into hierarchical communities so that each community can receive a standalone LLM summary, enabling global multi-hop question answering without full-corpus retrieval.

**Stack**:
1. **Entity co-occurrence graph** — nodes are extracted entities; edge weight = co-occurrence count within a chunk window (e.g. ±2 sentences)
2. **Community detection (#3)** — run Leiden (GVE-Leiden for corpora > 1M edges) to produce a hierarchical partition; each level of the hierarchy becomes a summary granularity level; label each community by its top-degree entity
3. **PageRank (#2)** — within each community, rank entities by PageRank on the sub-graph to select the most salient nodes for summary generation; PageRank on the sub-graph functions as memory salience for agent context
4. **Link prediction (#8)** — optionally score candidate cross-community edges (Adamic-Adar or Katz) to surface implicit entity bridges before summarisation
5. **Output**: hierarchical community map + per-community entity ranking + cross-community bridge candidates → feeds LLM summarization pipeline

**Failure modes to check**: resolution limit — large corpora with > 100K nodes need a resolution parameter scan (ε ∈ [0.5, 1.5]) to avoid all entities collapsing into one community. Lazy evaluation (defer community summaries until query time) avoids upfront cost when only a fraction of communities are queried. Do not use Louvain on graphs > 10M edges — benchmark GVE-Leiden first.

**Inputs:** entity co-occurrence edge list, chunk window size, Leiden resolution parameter ε, PageRank damping d (default 0.85), optional link-prediction candidate threshold.
**Outputs:** hierarchical community assignments per entity, per-community PageRank ranking, cross-community bridge edge candidates, community sizes.

---

## Related Skills

_Consumer skills that will receive applied recipes derived from these primitives:_

- `marketing-aeo-geo` — citation-flow and topical-authority recipes
- `marketing-seo` — PageRank and link-prediction recipes for backlink strategy
- `dev-context-multi-repo` — blast-radius and dependency-graph recipes
- `data-analytics-engineering` — graph-embedding and community-detection recipes
- `agents-subagents` — contagion and percolation recipes for agent-network robustness

_Cross-links will be added to consumer skills when applied recipe files are created. This skill does not cross-link to them._

---

## Navigation

- Per-primitive playbooks: [`assets/templates/network-science/`](assets/templates/network-science/) (one file per primitive)
- Composition guide: [`assets/templates/network-science/README.md`](assets/templates/network-science/README.md)
- Domain anti-patterns and decision checklist: [`references/primitives-overview.md`](references/primitives-overview.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Workflow

1. Identify the network analysis question (importance, clustering, robustness, spread, prediction, representation, causality).
2. Use the [Decision Checklist](#decision-checklist) to map question → primitive.
3. Open the per-primitive playbook in [`assets/templates/network-science/`](assets/templates/network-science/) for the full definition, inputs/outputs, failure modes, and worked example.
4. For multi-question scenarios, use the [Composition Recipes](#composition-recipes) to stack primitives.
5. Check the [Anti-Patterns](#anti-patterns) table before shipping any analysis.
6. Cite primary sources (Newman, Barabási, Easley & Kleinberg, Watts & Strogatz, Fortunato) when reporting results.

---

## ASCII Flow

```text
Network question
  -> Define nodes, edges, direction, weight, time, and sampling frame
  -> Classify task: importance, clustering, robustness, spread, prediction, embedding, causality
  -> Select primitive and open playbook
  -> Validate graph assumptions
     +-- sampling or power-law claim weak -> run robustness checks
     +-- assumptions pass -> compute and compare metrics
  -> Report graph result with uncertainty and operational implication
```

---

## Fact-Checking

- Power-law and small-world claims must be verified against statistical tests, not visual inspection.
- Numeric thresholds (PageRank damping, SIR β/γ, modularity resolution) are dataset-specific. Calibrate on held-out snapshots.
- Community detection quality metrics (modularity, NMI, conductance) are complementary — no single metric is ground truth.
- Temporal-network results should be compared against static-graph baselines to quantify the timing effect.
- Primary sources: Newman 2010, Barabási 2016, Easley & Kleinberg 2010, Watts & Strogatz 1998, Barabási & Albert 1999, Fortunato 2010, Brin & Page 1998, Clauset et al. 2009, Broido & Clauset 2019.
- The "are scale-free networks rare?" question is contested, not settled: Broido & Clauset (2019) found only ~4% of 927 networks meet their strictest scale-free criterion, but Holme (2019, Nat. Commun., companion piece) and Barabási's public rebuttal argue the result hinges on an unusually strict definitional threshold, and scale-freeness is only cleanly defined in the infinite-size limit. Report the fitted statistics and the tier of evidence, not a binary yes/no claim.
- Community detection at scale: GVE-Leiden (ICPP 2024) processes billion-edge graphs at 400M edges/s — Louvain is no longer the only practical large-scale option. For graphs with N > 10M, benchmark GVE-Leiden before assuming Louvain is the ceiling.
- For contagion on group-structured networks: classical pairwise SIR R₀ understates risk. Group interaction models can produce bistable regimes where the epidemic can either die out or explode depending on initial conditions — not just on R₀ (Ferraz de Arruda 2024, Nat. Rev. Phys.).
- When time-series data is available, higher-order structure (hyperedges) can be recovered without knowing the coupling functions via SINDy-based sparse regression (Arnaudon et al. 2025, Nat. Comms). Check whether non-pairwise contributions exceed pairwise before assuming a standard temporal graph model suffices.
- Temporal link prediction: GNN benchmarks on TGB standard datasets are dominated by edge recurrence; TGB-Seq (Yi et al., ICLR 2025) shows state-of-the-art models break down on sequential non-repeating edges — calibrate evaluation to your dataset's repetition rate.
- Sampling bias is structural, not incidental: Stumpf, Wiuf & May (2005, PNAS) show that random subsampling of a scale-free network does not reliably produce a scale-free subnet. Any degree-distribution or centrality claim made from an API crawl, snowball sample, or opt-in panel should state the collection method, since the bias runs in a predictable direction (toward hubs) rather than washing out as noise.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
