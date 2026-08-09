# Primitive: Contagion / SIR Model

**Sources**: Newman (2010) §17; Barabási (2016) §10; Pastor-Satorras & Vespignani (2001).

## Definition

The **SIR model** partitions nodes into three compartments:

- **S** (Susceptible): can be infected
- **I** (Infected / active): spreading the contagion
- **R** (Recovered / removed): no longer spreading

**Transitions**:
- S → I: a susceptible node with an infected neighbour transitions at rate β per infected neighbour per time step
- I → R: an infected node recovers at rate γ per time step

**Basic reproduction number**: R₀ = β/γ

- R₀ > 1: epidemic (spreads to a finite fraction of the population)
- R₀ < 1: epidemic dies out

**Network-aware R₀**: on heterogeneous networks, R₀ = (β/γ) × ⟨k²⟩/⟨k⟩

For scale-free networks where ⟨k²⟩ diverges, R₀ > 1 for any β > 0 — the **vanishing epidemic threshold** (Pastor-Satorras & Vespignani 2001).

**SIS variant** (no permanent recovery): relevant for recurring phenomena — rumours, chronic diseases, software vulnerabilities.

## When to Use

- Modelling viral content spread, misinformation, or adoption in social networks
- Estimating how far a software vulnerability propagates through a dependency graph
- Planning seed selection for influence maximisation campaigns
- Estimating epidemic containment thresholds for immunisation campaigns

## Inputs

- Graph (network topology; contact structure replaces well-mixed assumption)
- Transmission rate β (calibrate from observed spread data or use sensitivity range)
- Recovery rate γ (calibrate from drop-off or removal data)
- Initial infected seed set I₀

## Outputs

- Per-time-step (S, I, R) counts
- Final epidemic size (fraction eventually infected)
- Peak infection time and magnitude
- Expected reach from each seed node (Monte Carlo average over ≥ 1,000 runs)

## Failure Modes

1. **Mean-field approximation on structured graphs**: mean-field SIR assumes homogeneous mixing (everyone can infect everyone). On real networks, spread is constrained by topology. Use network-aware SIR.
2. **Single deterministic run**: SIR on networks is stochastic. Run Monte Carlo (≥ 1,000 realisations) and report confidence intervals, especially near the phase transition.
3. **Static graph for contact-driven spread**: if edges change over time (temporal network), static SIR overestimates spread speed. See temporal networks (#11).
4. **Ignoring community boundaries**: SIR spread slows at inter-community edges with low betweenness. Community detection (#3) can identify spread barriers.
5. **R₀ calibration from mean field**: use the network-aware formula R₀ = (β/γ) × ⟨k²⟩/⟨k⟩ for heterogeneous graphs.
6. **Pairwise SIR on group-interaction networks**: when contagion occurs in groups (household transmission, team exposure, event attendance), standard pairwise SIR misses qualitatively different dynamics. Higher-order (hypergraph/simplicial) contagion models produce: (a) a dual epidemic threshold — a lower activation threshold below which contagion cannot spread even with high β, and a second extinction threshold creating a bistable regime; (b) hysteresis — the epidemic persists even after R₀ falls below the naive pairwise threshold. Consequence: pairwise R₀ understates outbreak risk and gives the wrong intervention target. If the dataset has documented group events, use a hypergraph contagion model (Ferraz de Arruda 2024, Nat. Rev. Phys.; Iacopini 2025, Nat. Rev. Phys.).
7. **SIR model used for social adoption, norm diffusion, or behaviour-change spread (complex contagion)**: SIR and its variants assume single-exposure transmission — one infected contact is sufficient to trigger transition. Social adoption often requires **multiple independent reinforcing exposures** before a node adopts: the Watts threshold model. Domains where complex contagion dominates: technology adoption, social norm diffusion, feature uptake, behaviour change campaigns. Key qualitative differences from SIR: (a) clustered networks *accelerate* complex contagion (by providing repeated exposure from the same local neighbourhood), whereas they *slow* simple contagion; (b) the adoption threshold interacts with degree distribution differently — low-degree nodes with many threshold-crossing neighbours adopt even if global prevalence is low; (c) complex contagion can produce cascades only from high-clustering seed placements, not just high-degree hubs. **Fix**: for social adoption questions, model the threshold fraction φᵢ (fraction of neighbours that must have adopted before node i adopts) and simulate Watts threshold dynamics. **Tool note (verified July 2026): NetworkX has no built-in Watts threshold / complex-contagion function** — there is no `threshold_model` in the NetworkX API (its `algorithms.threshold` module is for a different concept, threshold *graphs*, not contagion). Use NDlib's Linear Threshold Model (`ndlib.models.epidemics.ThresholdModel`) for a ready implementation on top of NetworkX graphs, or implement the neighbour-fraction rule directly (a handful of lines: track cumulative active-neighbour fraction per node per round). Rule: use SIR for biological spread or information forwarding; use threshold/complex contagion when mechanism is documented as requiring social reinforcement.

## Worked Example

**Content network — viral post seeding**: 10,000 nodes, power-law degree (α=2.3). β=0.05 (from historical engagement data), γ=0.3. Mean-field R₀ = 0.05/0.3 = 0.17 < 1 — would predict no epidemic. Network-aware R₀ = (0.05/0.3) × (⟨k²⟩/⟨k⟩) = 0.17 × 8.2 = 1.39 > 1. Monte Carlo (1,000 runs) from the top-PageRank seed: median final reach = 31% of nodes, 5th–95th percentile range = [4%, 67%]. The mean-field model would have suppressed the campaign incorrectly.

## Sources

- Newman (2010). Networks: An Introduction. §17.
- Barabási (2016). Network Science. §10. [networksciencebook.com](https://networksciencebook.com/)
- Pastor-Satorras and Vespignani (2001). Epidemic Spreading in Scale-Free Networks. Physical Review Letters. [doi:10.1103/PhysRevLett.86.3200](https://doi.org/10.1103/PhysRevLett.86.3200)
- Easley and Kleinberg (2010). Networks, Crowds, and Markets. §21.
- Ferraz de Arruda, Aleta and Moreno (2024). Contagion dynamics on higher-order networks. Nature Reviews Physics. [doi:10.1038/s42254-024-00733-0](https://doi.org/10.1038/s42254-024-00733-0) — Establishes dual-threshold and bistability in group-interaction SIR.
- Battiston, Bick, Lucas, Millán, Skardal, and Zhang (2026). Collective dynamics on higher-order networks. Nature Reviews Physics 8:146-159 (preprint arXiv:2510.05253, 2025). [doi:10.1038/s42254-025-00916-3](https://doi.org/10.1038/s42254-025-00916-3) — Code: hypersync Python package https://github.com/maximelucas/hypersync. CORRECTED 2026-07-11: previously misattributed to "Iacopini et al." — Iacopini is not an author of this paper.
- Watts (2002). A simple model of global cascades on random networks. PNAS 99(9): 5766–5771. [doi:10.1073/pnas.082090499](https://doi.org/10.1073/pnas.082090499) — Foundational threshold/complex contagion model; introduces node adoption threshold φᵢ and cascade conditions on random networks.

## Related

- [`05-scale-free-networks.md`](05-scale-free-networks.md) — vanishing epidemic threshold on scale-free graphs
- [`06-percolation.md`](06-percolation.md) — R₀ > 1 is equivalent to being above the percolation threshold
- [`11-temporal-networks.md`](11-temporal-networks.md) — temporal contact patterns reduce effective R₀ vs. static SIR
- [`03-community-detection.md`](03-community-detection.md) — community boundaries act as spread barriers
