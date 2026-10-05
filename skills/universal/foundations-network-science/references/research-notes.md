# Network Science Research Notes

Research-level caveats moved out of the root [SKILL.md](../SKILL.md) to keep it short. Load this file when the analysis involves group (higher-order) interactions, very large or changing graphs, or temporal link prediction.

## Contents

- [Higher-order structure](#higher-order-structure)
- [Scale, tooling and evaluation notes](#scale-tooling-and-evaluation-notes)

## Higher-order structure

Before applying community detection (#3) or temporal-network analysis (#11) to a hypergraph dataset, run a reducibility test (Lucas et al. 2026). If degree heterogeneity is low, pairwise methods remain valid; if high, use higher-order methods to avoid underfitting.

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| SIR model run on a group-interaction network (e.g. household spread, team transmission) without higher-order correction | Some higher-order interaction models have dual thresholds or bistability absent from a fitted pairwise model (Ferraz de Arruda 2024, Nat. Rev. Phys.); the risk bias can go either direction | Compare calibrated pairwise and higher-order models against documented group events; establish the direction of bias and check applicable bistability conditions before setting intervention thresholds |
| Applying pairwise community detection to a high-degree-heterogeneity hypergraph | Reducibility analysis (Lucas 2026) shows co-authorship-style networks cannot be collapsed to pairwise edges without dynamical information loss | Run the reducibility test first; if degree heterogeneity is high (e.g. a model-specific irreducibility criterion supported by the original method; no portable χ cutoff is assumed), use a higher-order community detection method |
| Assuming pairwise edges are sufficient for temporal network inference | >60% of real EEG dynamics are non-pairwise; pairwise temporal models can systematically underfit | Before committing to standard temporal edges, test higher-order fit using THIS (Arnaudon 2025) if time-series data is available |

## Scale, tooling and evaluation notes

- Community detection at scale: GVE-Leiden (ICPP 2024) processes billion-edge graphs at 400M edges/s — Louvain is no longer the only practical large-scale option. For graphs with N > 10M, benchmark GVE-Leiden before assuming Louvain is the ceiling. If the graph *changes* rather than being re-analysed from scratch, use an incremental variant: LD-Leiden (Bokov et al. 2025/2026) updates partitions per edge batch instead of rerunning, reporting large speedups over warm-started Leiden at ~0.996 of the full-rerun modularity on graphs up to 3.3B edges. Full reruns on every snapshot are usually wasted compute.
- Community-detection algorithm choice is not neutral for downstream tasks: Ghosh & Saule (2025) find measurable performance variation across graph-mining applications depending on which method produced the partition. Do not treat the partition as a fixed input — evaluate the detector against the downstream metric, not only against modularity.
- For contagion on group-structured networks: pairwise projections can misrepresent risk in either direction, depending on group transmission rules. Group interaction models can produce bistable regimes where the epidemic can either die out or explode depending on initial conditions — not just on R₀ (Ferraz de Arruda 2024, Nat. Rev. Phys.).
- When time-series data is available, higher-order structure (hyperedges) can be recovered without knowing the coupling functions via SINDy-based sparse regression (Arnaudon et al. 2025, Nat. Comms). Check whether non-pairwise contributions exceed pairwise before assuming a standard temporal graph model suffices.
- Temporal link prediction: GNN benchmarks on TGB standard datasets are dominated by edge recurrence; TGB-Seq (Yi et al., ICLR 2025) shows state-of-the-art models break down on sequential non-repeating edges — calibrate evaluation to your dataset's repetition rate. Negative sampling is the other half of this problem: one random negative per positive inflates scores because random negatives are trivially separable in sparse graphs. Evaluate as ranking (multiple negatives, MRR) and include historical negatives — past edges absent at the current step — which are substantially harder than random ones (TGB 2.0).
- Higher-order tooling is no longer siloed: the Hypergraph Interchange Format (Coll et al. 2025, *Network Science* 13, e21) defines a JSON schema for undirected/directed hypergraphs and simplicial complexes, supported across HypergraphX, HyperNetX, XGI, and SimpleHypergraphs.jl. If a higher-order analysis needs more than one package, serialize through HIF rather than writing pairwise adapters.
- Sampling bias is structural, not incidental: Stumpf, Wiuf & May (2005, PNAS) show that random subsampling of a scale-free network does not reliably produce a scale-free subnet. Any degree-distribution or centrality claim made from an API crawl, snowball sample, or opt-in panel should state the collection method, since the bias runs in a predictable direction (toward hubs) rather than washing out as noise.
