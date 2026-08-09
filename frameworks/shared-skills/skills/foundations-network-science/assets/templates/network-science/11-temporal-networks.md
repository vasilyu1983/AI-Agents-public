# Primitive: Temporal Networks

**Sources**: Holme & Saramäki (2012) Physics Reports; Kossinets & Watts (2006) Science; Newman (2010) §18.

## Definition

A **temporal network** is a graph where each edge (u, v) carries a timestamp t: contact(u, v, t). Unlike a static graph, the temporal ordering of edges constrains which paths are causally valid.

**Time-respecting path**: a sequence of edges (u₁, u₂, t₁), (u₂, u₃, t₂), ..., where t₁ ≤ t₂ ≤ ... (non-decreasing timestamps). A later edge cannot be used to reach a node that needed to be reached earlier.

**Key consequences**:

- **Reachability is strictly smaller** on temporal networks than on the equivalent static graph (aggregate all edges, ignore time)
- **Burstiness**: real contact sequences are bursty (Poisson process predicts too-even timing). Bursty contacts slow epidemic spread because long inter-event gaps create waiting times
- **Temporal diameter**: the longest shortest time-respecting path. Can be infinite if the time window is too short
- **Causal ordering**: information can only flow forward in time; temporal paths encode causality, not just connectivity

**Key metrics**:

| Metric | Definition |
|--------|-----------|
| Temporal reachability | Fraction of node pairs connected by time-respecting paths in window [0, T] |
| Inter-event time distribution | Time between consecutive contacts on the same edge |
| Burstiness parameter B | B = (σ_τ − μ_τ)/(σ_τ + μ_τ) ∈ [−1, 1]; B > 0 = bursty; B = 0 = Poisson |
| Latency | Shortest time from u to v over time-respecting paths |

## When to Use

- Any spread model where the order of contacts matters (epidemic, information, influence)
- Communication network analysis where message delivery depends on availability windows
- Knowledge graph reasoning over time-indexed relations (Company A acquired B before B released Product C)
- Comparing observed temporal spread against a static-graph upper bound

## Inputs

- Time-stamped edge list: (source, target, timestamp) tuples
- Time window [t_start, t_end] for analysis
- Optional: aggregation resolution (minute/hour/day granularity)

## Outputs

- Time-respecting reachability matrix (or sample thereof for large graphs)
- Temporal diameter and temporal path lengths
- Inter-event time distribution and burstiness B per edge or globally
- Comparison of temporal vs. static reachability (the "temporal speed penalty")

## Failure Modes

1. **Aggregating timestamps to build a static graph**: the most common error. Produces an upper-bound-only reachability estimate. Always compare static-graph results against temporal-network results to quantify the overestimate.
2. **Ignoring burstiness in SIR models**: Poisson-contact SIR overestimates epidemic speed on bursty graphs. Burstiness B > 0 increases average inter-contact time, slowing spread.
3. **Short time windows**: temporal reachability can be near zero if the time window is shorter than the temporal diameter. Check that the window covers sufficient activity.
4. **Directed vs. undirected temporal paths**: temporal paths are inherently directed (time flows forward). Do not apply undirected-graph reachability to temporal networks.
5. **Memory effects**: some temporal networks have memory (a contact at time t makes a contact at t+1 more likely). Standard temporal-network models assume independence; check for autocorrelation.
6. **Assuming pairwise edges are sufficient when time-series data reveals higher-order interactions**: pairwise temporal models can systematically underfit when group interactions dominate. When time-series observations are available, higher-order structure (hyperedges) can be recovered without knowing the coupling functions via SINDy-based sparse regression (THIS algorithm, Arnaudon et al. 2025, Nat. Comms). On 109-subject EEG data, >60% of macroscopic brain dynamics arise from non-pairwise interactions. Check whether non-pairwise contributions exceed pairwise before locking in a standard temporal graph model.
7. **GNN-based temporal link predictors on sequential edge streams**: GraphMixer and DyGFormer — previously top-performing temporal GNNs — perform strongly on benchmarks with high edge repetition but collapse on genuinely sequential dynamics where most edges appear only once (TGB-Seq benchmark, ICLR 2025). Before using a GNN for temporal link prediction, check the repetition rate in your edge stream. If most edges are non-recurring, non-GNN baselines (e.g. structural heuristics) may outperform state-of-the-art temporal GNN models.

## Worked Example

**Slack communication network**: 300 employees, 45,000 messages over 30 days. Static-graph reachability: 94% of pairs are reachable. Temporal reachability (time-respecting paths within same 8-hour workday): 31% of pairs are reachable. Burstiness B = 0.63 (highly bursty). Static SIR (β=0.1, γ=0.2) predicts 89% of employees reached a rumour within 5 days. Temporal SIR using the actual message sequence: 54% reached within 5 days, 73% by day 10. Planning intervention on day 3 based on static model would be 2 days too late.

## Sources

- Holme and Saramäki (2012). Temporal networks. Physics Reports. [doi:10.1016/j.physrep.2012.03.001](https://doi.org/10.1016/j.physrep.2012.03.001)
- Kossinets and Watts (2006). Empirical analysis of an evolving social network. Science. [doi:10.1126/science.1116869](https://doi.org/10.1126/science.1116869)
- Karsai, Kivelä, Pan et al. (2011). Small but slow world: How network topology and burstiness slow down spreading. Physical Review E. [doi:10.1103/PhysRevE.83.025102](https://doi.org/10.1103/PhysRevE.83.025102)
- Newman (2010). Networks: An Introduction. §18.
- Arnaudon et al. (2025). Hypergraph reconstruction from dynamics. Nature Communications 16:2691. [doi:10.1038/s41467-025-57664-2](https://doi.org/10.1038/s41467-025-57664-2) — Introduces THIS (Taylor-based Hypergraph Inference using SINDy): reconstructs hyperedges from time-series without knowing coupling functions. Code: Zenodo 10.5281/zenodo.10530470.
- Yi, Peng, Zheng, Mo, Wei, Ye, Zixuan, and Huang (2025). TGB-Seq Benchmark: Challenging Temporal GNNs with Complex Sequential Dynamics. ICLR 2025. [arxiv:2502.02975](https://arxiv.org/abs/2502.02975) — Exposes overfit-to-recurrence failure mode in temporal GNNs. Code + leaderboard: tgb.complexdatalab.com. CORRECTED 2026-07-11: previously cited as "Huang et al." — Zengfeng Huang is the senior (last) author; first author is Lu Yi, so the conventional short-cite is "Yi et al."
- Lucas et al. (2026). Reducibility of higher-order networks from dynamics. Nature Communications. [doi:10.1038/s41467-025-68273-4](https://doi.org/10.1038/s41467-025-68273-4) — Preprocessing test for whether a temporal hypergraph can safely be reduced to pairwise edges.

## Related

- [`07-contagion-sir.md`](07-contagion-sir.md) — temporal contacts reduce effective R₀ vs. static SIR
- [`04-small-world.md`](04-small-world.md) — static small-world baseline for comparison with temporal reachability
- [`08-link-prediction.md`](08-link-prediction.md) — temporal link prediction uses edge timestamps as features
