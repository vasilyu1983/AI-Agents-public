---
name: foundations-network-science
description: "Network-science primitives: centrality, influence seeding, communities, contagion vs homophily, GNN failures. Use when seeding a referral campaign or finding critical graph nodes."
compatibility: Portable core only.
version: "1.3"
last_validated: 2026-08-14
---

# Network Science Foundations

## When to Apply

**Apply network-science when:**
- The data IS a graph — citations, dependencies, follower graphs, supply chains, knowledge graphs
- The *system* is a graph even if the data is not — LLM multi-agent communication topology, agent memory graphs, tool-call graphs (see [Agent Topology as a Graph Problem](#agent-topology-as-a-graph-problem))
- Spread/contagion question — viral coefficient, R₀, percolation threshold
- Centrality question — "which nodes are critical?" (PageRank, betweenness, eigenvector)
- Community detection — clustering nodes by structural similarity (Louvain, Leiden)
- Blast-radius / dependency-impact analysis on services or modules

**Skip and use simpler alternatives when:**
- Data is tabular and relationships aren't structural — standard analytics suffices
- The decision is already answerable by direct inspection and a graph model adds no stable ranking or counterfactual value
- Question is about strategic interaction at the node level — use foundations-game-theory
- Question is about queue or flow through a single bottleneck — use foundations-queueing-theory or theory-of-constraints
- Edges are weak proxies (e.g. "users who viewed both products") — centrality is unreliable; validate edge semantics first
- A "network effects" claim concerns how product value changes with other users' participation, not referral reproduction R; measure the relevant value effect separately from viral growth ([Easley & Kleinberg, ch. 17](https://www.cs.cornell.edu/home/kleinber/networks-book/networks-book-ch17.pdf))

Before reporting a graph statistic, name the target population, observation window, node/edge inclusion rule, sampling process, and estimand. Centrality and community results can reverse under missing nodes, projection choices, or edge weight definitions. Network size alone is never a validity threshold; compare the result across plausible graph constructions and report unstable ranks.

**The data is tabular but might still be a graph problem.** Three criteria (Broadwater & Stillman 2025, §1.4) — any one is grounds to reframe: *implicit relationships and interdependencies* (entities connected by undocumented influence, co-investment, or co-occurrence rather than a recorded relation); *high dimensionality and sparsity* (many entities, few direct interactions — recommender interaction data, molecules; also the cold-start motivation); *complex nonlocal interactions* (an entity's outcome depends on entities reachable only through intermediaries — supply-chain cascades, propagation through a network over time). Key indicators and the closing self-test questions are in [10-graph-embeddings.md](assets/templates/network-science/10-graph-embeddings.md#is-this-a-gnn-problem-at-all-data-not-obviously-graph-shaped). If a criterion holds, design the structure explicitly with #12 before ingest, and establish a tabular (non-GNN) baseline before attributing anything to the graph.

## Contents

- [When to Apply](#when-to-apply)
- [Quick Reference](#quick-reference)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Expert Judgment](#expert-judgment)
- [Composition Recipes](#composition-recipes)
- [Related Skills](#related-skills)
- [Practical Decision Record](#practical-decision-record)
- [Navigation](#navigation)
- [Workflow](#workflow)
- [Learnings Loop](#learnings-loop)

---

## Quick Reference

Each primitive has a full playbook: Definition / When to use / Inputs / Outputs / Failure modes / Worked example / Sources.

| # | Primitive | Core Question | Typical Input | Failure Mode It Addresses |
|---|-----------|---------------|---------------|---------------------------|
| 1 | [Centrality Measures](assets/templates/network-science/01-centrality-measures.md) | Which node matters most, and by what criterion? | Unweighted or weighted graph | Wrong centrality used — high degree ≠ high betweenness ≠ high influence |
| 2 | [PageRank](assets/templates/network-science/02-pagerank.md) | Who is authoritative via inbound endorsements? | Directed graph with optional weights | Naive in-degree conflates volume with authority |
| 3 | [Community Detection](assets/templates/network-science/03-community-detection.md) | Which nodes form cohesive clusters? | Undirected or directed graph | Arbitrary k-means on graph ignores topology |
| 4 | [Small-World Networks](assets/templates/network-science/04-small-world.md) | Is the graph navigable despite size? | Any graph | Assuming large graphs are either fully random or fully regular |
| 5 | [Scale-Free Networks](assets/templates/network-science/05-scale-free-networks.md) | Does degree follow a power law? | Degree sequence or full graph | Designing resilience for hubs that may not exist |
| 6 | [Percolation](assets/templates/network-science/06-percolation.md) | At what removal threshold does the graph fragment? | Graph + removal strategy | Ignoring phase transitions — small removals can catastrophically fragment |
| 7 | [Contagion / SIR](assets/templates/network-science/07-contagion-sir.md) | How far and fast does influence or disease spread? | Graph + transmission probability | Linear spread assumptions on networked systems |
| 8 | [Link Prediction](assets/templates/network-science/08-link-prediction.md) | Which absent edges are likely to form? | Observed snapshot of graph | Random-guess recommendations miss structural proximity |
| 9 | [Graph Clustering](assets/templates/network-science/09-graph-clustering.md) | How to partition nodes by structural similarity? | Graph with optional edge weights | Treating clustering as unstructured k-means; ignoring conductance |
| 10 | [Graph Embeddings](assets/templates/network-science/10-graph-embeddings.md) | How to represent nodes as dense vectors? | Graph structure + optional node features _(For cross-domain transfer with zero labels, see Graph Foundation Models: Liu et al. TPAMI 2025.)_ | One-hot node encodings lose all structural information |
| 11 | [Temporal Networks](assets/templates/network-science/11-temporal-networks.md) | How does time ordering of edges change reachability? | Time-stamped edge list | Aggregating time-stamped edges loses causal ordering |
| 12 | [Graph Schema Design](assets/templates/network-science/12-graph-schema-design.md) | What should be a node, an edge, or a property — and is that choice testable? | Non-graph source data + use-case queries | Graph structure chosen implicitly at ingest, then frozen as technical debt |

---

## Formal Supporting Theory

Load [references/formal-theory-map.md](references/formal-theory-map.md) when the analysis depends on graph assumptions: directed vs. undirected edges, weighted vs. unweighted measures, random-walk stationarity, modularity limits, power-law testing, percolation thresholds, epidemic dynamics, link-prediction leakage, embedding validity, or temporal reachability.


Primary sources: Newman 2010, Barabási 2016, Easley & Kleinberg 2010, Watts & Strogatz 1998, Barabási & Albert 1999, Fortunato 2010, Brin & Page 1998, Clauset et al. 2009, Broido & Clauset 2019. Power-law and small-world claims must be verified against statistical tests, not visual inspection.

## Misuse Boundaries

Load [references/patterns-scenarios-traps.md](references/patterns-scenarios-traps.md) before publishing graph rankings, communities, scale-free claims, diffusion forecasts, dependency blast-radius scores, or embedding explanations. It contains scenario playbooks, anti-patterns, known traps, and validation checks. Load [references/identification-and-gnn-pitfalls.md](references/identification-and-gnn-pitfalls.md) before a causal peer-effect claim, statistics from a crawled or partial graph, or a GNN / link-prediction comparison: homophily vs contagion, the reflection problem, degree-biased sampling, over-smoothing vs over-squashing, heterophily and split leakage.


The "are scale-free networks rare?" question is contested, not settled: Broido & Clauset (2019) found only ~4% of 927 networks meet their strictest scale-free criterion, but Holme (2019, Nat. Commun., companion piece) and Barabási's public rebuttal argue the result hinges on an unusually strict definitional threshold, and scale-freeness is only cleanly defined in the infinite-size limit. Report the fitted statistics and the tier of evidence, not a binary yes/no claim.

**Tooling check**: Before choosing a NetworkX Leiden implementation, look up `leiden_communities()` in the [documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.leiden.leiden_communities.html) for the installed version. Confirm native/backend requirements and the supported metric and resolution parameters. Select modularity or CPM deliberately and scan resolution under that objective; their resolution values are not interchangeable.

---

## Decision Checklist

- [ ] **Structure not yet fixed**: Is the source data non-graph, or does more than one node/edge/property split look plausible? → graph schema design (#12) *first* — write a conceptual schema, build an instance model on real data, and test the constraints before any algorithm runs. Tabular layout is unambiguous; graph layout is not, and the choice becomes technical debt once a pipeline sits on it.
- [ ] **Influence / importance ranking**: Which single node matters most? → choose the right centrality (#1); if endorsement-weighted → PageRank (#2)
- [ ] **Cluster structure**: Do nodes group into cohesive communities? → community detection (#3) — use Louvain/Leiden for descriptive partitioning; if the question is "does community structure exist?" or requires statistical model comparison → inferential SBM (#3, Failure Mode 7); if cut-minimization is the goal → graph clustering (#9)
- [ ] **Navigation / reachability**: Is average path length short despite size? → small-world test (#4)
- [ ] **Degree distribution**: Does degree follow a power law? Test before claiming scale-free (#5)
- [ ] **Robustness / fragility**: How many nodes must be removed to break connectivity? → percolation (#6)
- [ ] **Spread / contagion**: How far does a signal reach from a seed? → SIR model (#7); if spread requires social reinforcement or multiple exposures (technology adoption, norm diffusion, behaviour change) → threshold / complex contagion model (#7, Failure Mode 7), not SIR
- [ ] **Missing edge inference**: Which edges are likely to form next? → link prediction (#8)
- [ ] **Node similarity / downstream ML**: Need node vectors for classification or recommendation? → graph embeddings (#10)
- [ ] **Temporal causality**: Do edge timestamps change what is reachable? → temporal networks (#11)
- [ ] **Higher-order structure test**: If group interactions (households, teams, co-authorship) are the unit, test reducibility before using pairwise methods. See [research notes](references/research-notes.md#higher-order-structure).


Numeric thresholds (PageRank damping, SIR β/γ, modularity resolution) are dataset-specific — calibrate on held-out snapshots. Community detection quality metrics (modularity, NMI, conductance) are complementary — no single metric is ground truth. Temporal-network results should be compared against static-graph baselines to quantify the timing effect.

---

## Anti-Patterns

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Degree centrality used for every importance question | Degree, shortest-path brokerage and diffusion impact are different objectives | Information brokers → betweenness; most-connected hub → degree; shortest average outward distance → outward closeness; fastest spreader → compare under the fitted diffusion process |
| Modularity treated as ground truth (resolution limit ignored) | Modularity optimization misses small communities and merges large ones at scale | Pair modularity with resolution parameter scan; verify with NMI against ground truth if available (Fortunato 2010) |
| Scale-free claimed without statistical test | Visual inspection of log-log degree plots is unreliable — Gaussian and log-normal distributions look similar in log-log | Run a maximum-likelihood power-law fit and report the p-value and xmin (Clauset, Shalizi & Newman 2009) |
| Percolation reasoning on directed networks treated as undirected | Weak connectivity, strong connectivity and outward reachability answer different failure questions | Compute weak/strong components and directed reachability for the stated failure objective (Newman 2010) |
| Temporal-network paths confused with static-network paths | Time-respecting reachability is a subset of static reachability; it can be equal, and timestamps alone do not identify causal effects | Use time-respecting path algorithms; a static projection can overestimate reachable spread (Holme & Saramäki 2012) |
| PageRank damping copied without sensitivity analysis | Damping changes the balance between link following and teleportation; graph size alone does not determine it | Compare ranks across a justified damping range and personalization choices; report the choice and unstable ranks |
| Community inference justified by graph size alone | Neither a node-count cutoff nor a modularity score proves significance | Use a graph-specific null model, stability and decision relevance; small descriptive partitions are allowed |
| Correlated adoption among neighbours reported as contagion | Homophily and contagion are generically confounded in observational network data (Shalizi & Thomas 2011); similar people link and also adopt alike | Treat neighbour correlation as descriptive; hand peer-effect identification to `foundations-causal-inference` ([Interference and SUTVA](../foundations-causal-inference/SKILL.md#interference-and-sutva-when-randomization-is-not-enough)); use randomized seeding or exposure designs before sizing a contagion effect; reflection and sampling traps: [identification reference](references/identification-and-gnn-pitfalls.md#identification-in-observational-network-data) |
| Greedy or IMM seed set reported as optimal | A model-specific approximation guarantee does not prove exact optimality, even when the diffusion model is correct | Fit and validate the model; report the applicable approximation guarantee and estimation error, and compare with simple seed sets on held-out spread ([Kempe, Kleinberg & Tardos](https://theoryofcomputing.org/articles/v011a004/)) |
| GNN shipped without a non-GNN baseline | With no tabular baseline (logistic regression / gradient-boosted trees / MLP on the same node features) there is no counterfactual, so any claimed benefit of graph structure is unfalsifiable | Train non-GNN baselines first, then a GCN to isolate what graph structure adds, then any attention architecture (Broadwater & Stillman 2025, §4.3–4.4) |
| GNN architecture selected on published Big-O complexity | GNNs mix heterogeneous operations with different complexities and do not all use the same operations; the literature typically compares one major operation, not whole algorithms, and implementation and hardware shift the result | Treat Big-O as an ordering hint only; benchmark candidate architectures on your own data and hardware (§7.6.1) |
| Layers added to reach a distant influencing node | A large "problem radius" is a second cause of over-smoothing, and long-range tasks also over-squash through bottleneck edges — the depth that would solve the task destroys the representation | Reduce the radius instead of adding depth (coarsening, global/virtual nodes, hierarchical message passing); per-architecture ordering in [10-graph-embeddings.md](assets/templates/network-science/10-graph-embeddings.md) Failure Mode 3, diagnostics in the [identification reference](references/identification-and-gnn-pitfalls.md#gnn-failure-modes) |

---

## Expert Judgment

### Which centrality answers which business question

| Business question | Right measure | Why the obvious choice is often wrong |
|---|---|---|
| "Who do we lose the most by losing?" (churn/attrition risk) | Betweenness, or articulation-point test | Degree picks the loudest node, not the one holding two subgraphs together. A quiet node with low degree can be a single point of failure. |
| "Who should get the retention budget to prevent contagion-style churn?" | Expected avoided loss under an identified churn/diffusion model | Eigenvector/PageRank can propose candidates, but neither identifies peer effects nor incorporates retention cost, customer value and intervention response. |
| "Whose endorsement carries the most weight?" (authority, credibility) | PageRank / eigenvector | Volume of inbound links or mentions rewards spam and popularity contests; authority requires weighting by the endorser's own standing. |
| "Who has the shortest average broadcast distance?" | Outward closeness with declared unreachable-node handling | Closeness describes shortest-path distances, not realized diffusion speed; NetworkX's directed closeness uses incoming distances, so reverse the graph for outward distances ([docs](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.closeness_centrality.html)). |
| "Which service/package, if it breaks, takes down the most of the system?" | Directed reverse reachability plus operational dependency conditions | Enumerate exposed dependents and required/optional/version/fallback conditions; PageRank and betweenness are descriptive prioritization proxies, not outage-impact counts. |
| "Who has the biggest raw audience?" | Degree | This is the one case where degree is usually the right answer — but confirm the question is really about raw reach, not influence or bridging. |
| "Where should we seed a marketing campaign?" | Depends on the contagion mechanism — see diffusion-model choice below | PageRank/degree are candidate heuristics, not optimality guarantees for either mechanism. Compare seed sets under the directed, weighted diffusion model and objective, including saturation and overlap; validate on held-out campaigns or simulations. |

The recurring error is treating "importance" as one thing. Before computing anything, restate the business question as "a node such that removing/promoting/notifying it does X" — that sentence usually reveals which centrality is implied.

### Sampling bias: the network you measure is not the network that exists

Almost no analyst works with the true underlying graph. API rate limits, crawl depth limits, consent/opt-in populations, and snowball sampling all produce a **subnet**, not the network. This matters more than most failure-mode checklists suggest, because the bias is not random noise — it is systematic and direction-specific:

- **Degree-biased discovery**: high-degree nodes are easier to find (more paths lead to them), so crawls and snowball samples over-represent hubs and under-represent the long tail. This inflates apparent centralization and can manufacture the appearance of a heavy-tailed degree distribution from a true distribution that is not heavy-tailed at all.
- **The subnet is not the same distribution family as the parent**: Stumpf, Wiuf & May (2005, PNAS) prove that random subsampling of a scale-free network does not, in general, yield a scale-free subnet — and the reverse inference (subnet looks scale-free ⇒ population is scale-free) is equally unsafe. This is a structural reason, independent of the Broido–Clauset debate, to distrust degree-distribution claims made from partial crawls.
- **Survivorship bias compounds it**: inactive, deleted, or churned nodes are typically missing from the snapshot, which further skews measured centrality and community structure toward currently-active, currently-visible entities.
- **What to do**: before reporting a degree distribution, centrality ranking, or community structure, state explicitly how the graph was collected (full census, API crawl to depth d, snowball from k seeds, opt-in panel) and treat any claim about the *shape* of the distribution as conditional on that collection method. If the collection method is degree-biased, prefer rank-based or relative comparisons within the sample over absolute claims about the population.

### When the network frame itself misleads

Not every relational dataset should be analyzed as a network, and not every network metric on a valid graph means what it appears to mean.

- **Near-complete / dense graphs**: centrality and community detection are diagnostic tools for *structure* — variation in connectivity across the graph. Density alone does not imply equal centrality rankings or absent communities: directed, weighted, or block-structured dense graphs can retain substantial variation. Examine degree/weight/direction variation, compare appropriate null models, and test rank/community sensitivity to edge noise before interpreting structure; no degree-within-an-order-of-magnitude cutoff establishes a near-complete graph.
- **Bipartite projection inflates clustering artificially**: converting a two-mode graph (users × products, authors × papers) into a one-mode projection (users connected if they bought the same product) manufactures cliques by construction — any two users of the same popular product become "connected," and any three users of the same product form a "triangle." The resulting clustering coefficient is an artifact of the projection, not evidence of real triadic closure or community structure in user behavior. If a bipartite projection is unavoidable, weight edges by co-occurrence strength and compare against a projected-random-bipartite null model before interpreting clustering or community results — never take the raw projected clustering coefficient at face value.
- **Weak-proxy edges break centrality semantics**: an edge meaning "viewed the same page" or "mentioned in the same document" is not the same kind of relationship as "follows" or "cites," and centrality measures assume a consistent edge semantic across the whole graph. Mixing strong ties (explicit follow) and weak proxies (co-occurrence) in one adjacency matrix produces a centrality score that answers no coherent question. Validate that all edges mean approximately the same thing before computing centrality, and if they don't, build separate graphs per edge type rather than merging them into one weighted graph.

### Diffusion-model choice by phenomenon, not by default

Defaulting to SIR for every spread question is a common judgment error in applied contagion modelling. The right model depends on the exposure mechanism, not on which model is best known:

| Phenomenon | Exposure mechanism | Right model | Signature that distinguishes it |
|---|---|---|---|
| Biological disease, forwarded messages, software vulnerability propagation | Single contact is sufficient to transmit | SIR / SIS (simple contagion) | Clustering may reduce novel exposure, but net spread depends on transmission rules, timing, topology and seeds |
| Technology adoption, norm change, health behaviour change, feature uptake | Requires multiple independent reinforcing exposures before adoption | Watts threshold model (complex contagion) | Clustering may facilitate reinforcement or restrict outward exposure; compare seed strategies under fitted thresholds and topology |
| Household/team/event-based transmission | Group exposure, not pairwise contact | Hypergraph/simplicial contagion model | Higher-order processes can exhibit thresholds/bistability in specified models; pairwise risk bias can have either direction and needs calibrated comparison |
| Rumour/misinformation with source credibility effects | Mixture of single-exposure and reinforcement, credibility-weighted | Neither pure SIR nor pure threshold — hybrid or empirically fit model | Neither pure signature holds cleanly; validate against held-out spread data rather than assuming |

The practical test: ask "would one credible contact be enough, or does this require seeing it from more than one direction first?" If one contact can suffice, evaluate a simple-contagion model; if reinforcement is documented, evaluate a threshold model. Choose seed sets by calibrated temporal simulations and held-out diffusion evidence under the task budget; neither hub nor clustered seeding is universally optimal.

### Agent topology as a graph problem

An LLM multi-agent system is a graph whose nodes are agents and whose edges are permitted message paths: communication topology is designed and learned rather than hand-picked, and the primitives above apply directly to it (Liu et al. 2025, survey; Zhang et al. 2025, G-Designer).

The graph-science content is that topology is a cost/robustness tradeoff, not a style choice:

- **Density creates communication opportunities.** A directed all-to-all graph has n(n−1) communication edges; actual tokens also depend on rounds, scheduling and message length. G-Designer reports up to about 95% token reduction on HumanEval against its evaluated baselines ([ICML 2025 paper](https://proceedings.mlr.press/v267/zhang25cu.html)); this is a benchmark result, not a topology-only cost law.
- **Hubs are single points of failure, exactly as in percolation (#6).** A star topology with one orchestrator has an articulation point; its removal disconnects the system. If reliability matters more than coordination cost, check betweenness (#1) on the agent graph and add a redundant path around the top-betweenness node.
- **Error propagation can be studied as contagion (#7) when the transmission mechanism is defined.** A single flawed artifact may corrupt a consumer, while validation or independent corroboration can change that mechanism. Clustering and density have no universal error-spread direction: redundant paths can propagate common errors or provide detection and recovery. Compare sparse, hub and redundant topologies on matched tasks using measured handoff errors, coverage, recovery and token cost before recommending a topology.
- **Routing is a ranking problem on a heterogeneous graph.** Knowledge-graph-guided routers (Zhang et al., ACL 2026, AgentRouter) score agent fit with a heterogeneous GNN over a query-plus-entity-plus-agent graph rather than a flat classifier.

Caveat before importing results: published agent-topology numbers are benchmark-specific (MMLU, HumanEval) and depend on the model, the task mix, and the prompt scaffold. Treat the *structural* argument as transferable and the *percentages* as not.

---

## Composition Recipes

Full stacks, inputs, rules, outputs and the worked referral example are in [references/composition-recipes.md](references/composition-recipes.md):

- **AI-Search Citation Flow**: PageRank plus community detection on a citation graph.
- **Blast Radius Across a Dependency Graph**: reverse reachability first; centrality, communities and percolation only as prioritization aids.
- **Audience Reach Forecast**: fitted diffusion model plus seed-set comparison; branching referral arithmetic with its assumptions.
- **GraphRAG Corpus Partitioning**: the graph primitives only. Pipeline design, retrieval and evaluation belong to `ai-rag`.

---

## Related Skills

- `foundations-causal-inference` — peer-effect and interference identification ([Interference and SUTVA](../foundations-causal-inference/SKILL.md#interference-and-sutva-when-randomization-is-not-enough)); use it before claiming contagion over homophily
- `ai-rag` — GraphRAG pipelines; this skill supplies only the community-detection and PageRank primitives
- `foundations-graph-theory` — graph structure as a navigation surface (DAGs and cycles, reachability, fan-out and depth budgets, directed gates, orphans, table vs Mermaid); this skill keeps social and agent-network dynamics

_Consumer skills that hold applied copies of these primitives (in their `references/network-science-applied.md`). This skill does not cross-link to them:_

- `marketing-aeo-geo` — citation-flow and topical-authority recipes
- `marketing-seo` — PageRank and link-prediction recipes for backlink strategy
- `marketing-social-media` — seed selection and audience segmentation recipes
- `dev-context-multi-repo` — blast-radius and dependency-graph recipes
- `agents-subagents` — contagion and percolation recipes for agent-network robustness; agent communication topology as a sparsity/robustness tradeoff

## Practical Decision Record

Use [decision and validation worksheet](references/decision-and-validation.md) for intake, model boundaries, uncertainty and checkable acceptance examples. [Regression cases](data/regression-cases.json) provide independent prompts and expected answers; these are fixtures, not executed agent results.

## Navigation

- Per-primitive playbooks: [assets/templates/network-science/](assets/templates/network-science/) (one file per primitive)
- Composition guide: [assets/templates/network-science/README.md](assets/templates/network-science/README.md)
- Domain anti-patterns by field (citation, dependency, social, knowledge-graph): load [references/primitives-overview.md](references/primitives-overview.md) when the question needs a domain-specific anti-pattern rather than the general [Anti-Patterns](#anti-patterns) table above; its own Decision Checklist duplicates the one in this file and should not be treated as a second source of truth
- Composition recipes: [references/composition-recipes.md](references/composition-recipes.md)
- Research notes: [references/research-notes.md](references/research-notes.md)
- Identification and GNN pitfalls: [references/identification-and-gnn-pitfalls.md](references/identification-and-gnn-pitfalls.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Workflow

1. Identify the network analysis question (importance, clustering, robustness, spread, prediction, representation, causality).
2. Use the [Decision Checklist](#decision-checklist) to map question → primitive.
3. Open the per-primitive playbook in [assets/templates/network-science/](assets/templates/network-science/) for the full definition, inputs/outputs, failure modes, and worked example.
4. For multi-question scenarios, use the [composition recipes](references/composition-recipes.md) to stack primitives.
5. Check the [Anti-Patterns](#anti-patterns) table before shipping any analysis, and cite the relevant primary sources in [data/sources.json](data/sources.json).

---

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
