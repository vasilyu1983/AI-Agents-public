---
description: Domain-agnostic overview of 11 network-science primitives with anti-patterns by domain.
last_verified: 2026-08-14
status: stable
---

# Network-Science Primitives Overview

## Table of Contents

- [Why Network Science Matters](#why-network-science-matters)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Network Science Matters

Most real-world systems are not collections of independent objects — they are graphs. The structure of connections determines how information spreads, how failures cascade, which nodes are critical, and where boundaries form. Without network analysis:

| Failure Mode | Network Diagnosis | What Goes Wrong |
|-------------|-------------------|-----------------|
| Ranking by count (citations, followers, links) | Degree centrality ignores topology | High-volume but peripheral nodes outrank genuine bridges |
| Uniform removal resilience assumed | Percolation phase transition ignored | Small targeted attacks destroy connectivity at sub-1% removal |
| Linear spread assumption | Mean-field SIR ignores degree variance | Real spread is faster or slower by orders of magnitude |
| Arbitrary clustering | Community structure in topology ignored | Clusters contain unrelated nodes; cohesive groups split |
| Treating all graphs as the same type | Scale-free vs. random vs. small-world conflated | Wrong interventions applied to wrong network type |

Each primitive in the index below addresses a specific structural or dynamic failure mode.

---

## Primitive Index

11 primitives, each in its own playbook under [`../assets/templates/network-science/`](../assets/templates/network-science/). The table includes primary domain applications.

| # | Primitive | Failure Mode | Primary Domains |
|---|-----------|-------------|-----------------|
| 1 | [Centrality Measures](../assets/templates/network-science/01-centrality-measures.md) | Wrong importance metric for the question | Influence ranking, bridge detection, hub identification |
| 2 | [PageRank](../assets/templates/network-science/02-pagerank.md) | Naive in-degree conflates volume with authority | Search ranking, citation authority, package influence |
| 3 | [Community Detection](../assets/templates/network-science/03-community-detection.md) | Arbitrary partition ignores topology | Social clustering, topic communities, blast-radius grouping |
| 4 | [Small-World Networks](../assets/templates/network-science/04-small-world.md) | Assuming large graphs are random or regular | Social network navigation, routing efficiency analysis |
| 5 | [Scale-Free Networks](../assets/templates/network-science/05-scale-free-networks.md) | Hub claims without statistical evidence | Resilience design, epidemic modelling, influence forecasting |
| 6 | [Percolation](../assets/templates/network-science/06-percolation.md) | Ignoring phase transitions in robustness analysis | Dependency robustness, epidemic containment, infrastructure |
| 7 | [Contagion / SIR](../assets/templates/network-science/07-contagion-sir.md) | Linear or mean-field spread on structured graphs | Viral marketing, misinformation spread, epidemic modelling |
| 8 | [Link Prediction](../assets/templates/network-science/08-link-prediction.md) | Random-guess missing-link inference | Recommendation systems, citation forecasting, knowledge graphs |
| 9 | [Graph Clustering](../assets/templates/network-science/09-graph-clustering.md) | k-means on flat features misses graph cuts | Module detection, spectral partitioning, graph segmentation |
| 10 | [Graph Embeddings](../assets/templates/network-science/10-graph-embeddings.md) | One-hot node encodings lose structural signal | Node classification, link prediction with ML, GNN pipelines |
| 11 | [Temporal Networks](../assets/templates/network-science/11-temporal-networks.md) | Aggregated static graph loses causal ordering | Contact tracing, bursty communication, temporal reachability |

---

## Anti-Patterns by Domain

### Citation and Content Authority

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| In-degree used to rank authority | High in-degree ≠ high authority — spam links inflate counts | PageRank (#2) with damping weights endorser quality |
| Community labels from document content only | Topical similarity ignores citation topology | Community detection (#3) on the citation graph identifies structural clusters |
| Scale-free assumed for all citation networks | Not all citation networks have power-law degree | Statistical test (#5) before claiming hub-based authority |

### Dependency and Software Graphs

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Change impact estimated by direct dependents only | Transitive dependency chains ignored | Reverse PageRank (#2) on directed dependency graph captures transitive reach |
| No bridge detection in dependency audit | High-degree packages ≠ most critical bridges | Betweenness centrality (#1) identifies single-points-of-failure |
| Blast radius estimated without phase-transition test | One-package removal may fragment the whole graph | Percolation threshold (#6) quantifies fragility before threshold |

### Social and Audience Networks

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Spread modelled as linear (each node reaches N) | Degree variance causes super-linear spread on scale-free graphs | SIR on actual network (#7) with R₀ check against percolation threshold (#6) |
| Audience segments from demographics only | Network structure determines actual message flow | Community detection (#3) on follower/interaction graph reveals structural audiences |
| Temporal burstiness ignored | Static-graph SIR overestimates spread speed | Temporal network analysis (#11) reduces predicted R₀ by accounting for bursty contact |

### Knowledge Graphs and Recommendation

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Random or popularity-based recommendations | Miss high-value items in structural proximity | Link prediction (#8) scores candidate edges by Adamic-Adar or Katz |
| Node similarity computed from one-hot features | Structural role and neighbourhood ignored | Graph embeddings (#10) — node2vec or GNN captures topology |
| Static graph used for temporal knowledge graph | Edges timestamped but aggregated | Temporal network methods (#11) ensure time-respecting reasoning |

---

## Decision Checklist

This checklist applies to any graph or network analysis task.

- [ ] **Importance ranking**: Which node matters most? → select centrality type (#1); if endorsement-weighted → PageRank (#2)
- [ ] **Cluster structure**: Are there natural groups? → community detection (#3); if partition by cut → graph clustering (#9)
- [ ] **Navigability**: Are short paths ubiquitous despite network size? → small-world test (#4)
- [ ] **Degree distribution**: Power law? → statistical test for scale-free (#5)
- [ ] **Robustness**: How many removals to fragment? → percolation threshold (#6)
- [ ] **Spread / influence**: How far does a signal reach? → SIR model (#7); pair with percolation threshold check
- [ ] **Missing edge inference**: Which edges form next? → link prediction (#8)
- [ ] **Node vectors for ML**: Need embeddings for downstream tasks? → graph embeddings (#10)
- [ ] **Temporal causality**: Do timestamps constrain paths? → temporal networks (#11)
- [ ] **Scale-free + SIR**: Scale-free network + epidemic? → check vanishing threshold result (Pastor-Satorras & Vespignani 2001)

---

## Sources

Primary sources. Numeric thresholds are dataset-specific — always calibrate.

- Newman (2010). Networks: An Introduction. Oxford. [oup.com](https://global.oup.com/academic/product/networks-9780199206650)
- Barabási (2016). Network Science. Cambridge. [networksciencebook.com](https://networksciencebook.com/)
- Easley & Kleinberg (2010). Networks, Crowds, and Markets. Cambridge. [cs.cornell.edu](https://www.cs.cornell.edu/home/kleinber/networks-book/)
- Watts & Strogatz (1998). Collective dynamics of small-world networks. Nature. [doi:10.1038/30918](https://doi.org/10.1038/30918)
- Barabási & Albert (1999). Emergence of Scaling in Random Networks. Science. [doi:10.1126/science.286.5439.509](https://doi.org/10.1126/science.286.5439.509)
- Fortunato (2010). Community detection in graphs. Physics Reports. [doi:10.1016/j.physrep.2009.11.002](https://doi.org/10.1016/j.physrep.2009.11.002)
- Brin & Page (1998). The anatomy of a large-scale hypertextual Web search engine. Computer Networks. [doi:10.1016/S0169-7552(98)00110-X](https://doi.org/10.1016/S0169-7552(98)00110-X)
- Kossinets & Watts (2006). Empirical analysis of an evolving social network. Science. [doi:10.1126/science.1116869](https://doi.org/10.1126/science.1116869)
- Holme & Saramäki (2012). Temporal networks. Physics Reports. [doi:10.1016/j.physrep.2012.03.001](https://doi.org/10.1016/j.physrep.2012.03.001)
- Adamic & Adar (2003). Friends and neighbors on the Web. Social Networks. [doi:10.1016/S0378-8733(03)00009-1](https://doi.org/10.1016/S0378-8733(03)00009-1)
- Perozzi, Al-Rfou & Skiena (2014). DeepWalk. KDD. [doi:10.1145/2623330.2623732](https://doi.org/10.1145/2623330.2623732)
- Grover & Leskovec (2016). node2vec. KDD. [doi:10.1145/2939672.2939754](https://doi.org/10.1145/2939672.2939754)
