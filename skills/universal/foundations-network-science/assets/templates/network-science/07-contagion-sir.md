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

**Model-specific thresholds**: homogeneous well-mixed mass-action SIR uses R₀=β/γ when β is a population-normalized contact rate. A per-edge transmission rate has different units/meaning.

For a locally tree-like, uncorrelated configuration-model network with iid bond transmissibility T, the SIR branching factor is B=T(⟨k²⟩−⟨k⟩)/⟨k⟩. B>1 permits a giant outbreak in the infinite-network limit; a finite stochastic seed can still die out. For independent exponential per-edge infection β and recovery γ, marginal edge transmissibility is β/(β+γ); dependence from shared infectious periods must be checked when using a simple iid bond model. The heterogeneous mean-field SIS threshold involving (β/γ)⟨k²⟩/⟨k⟩ is not a universal SIR formula. Finite size, clustering, degree correlations and contact timing change predictions.

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
- Expected reach from each seed node (Monte Carlo average with simulation error and run count chosen for the required precision)

## Failure Modes

1. **Mean-field approximation on structured graphs**: mean-field SIR assumes homogeneous mixing (everyone can infect everyone). On real networks, spread is constrained by topology. Use network-aware SIR.
2. **Single deterministic run**: SIR on networks is stochastic. Choose independent simulation runs from the required Monte Carlo precision and report intervals, especially near the phase transition.
3. **Static graph for contact-driven spread**: if edges change over time (temporal network), static SIR overestimates spread speed. See temporal networks (#11).
4. **Ignoring community boundaries**: Sparse inter-community connectivity or low transmission can impede spread; bridge edges often have high betweenness. Community detection (#3) suggests barriers to test against actual topology and transmission.
5. **Threshold imported from another process**: state SIR vs SIS, rate vs transmissibility, graph model and dependence; use the matching criterion or simulation.
6. **Pairwise SIR on group-interaction networks**: when contagion occurs in groups (household transmission, team exposure, event attendance), standard pairwise SIR misses qualitatively different dynamics. Higher-order (hypergraph/simplicial) contagion models can produce: (a) a dual epidemic threshold — a lower activation threshold below which contagion cannot spread even with high β, and a second extinction threshold creating a bistable regime; (b) hysteresis — the epidemic persists even after R₀ falls below the naive pairwise threshold. Consequence: pairwise projections can misestimate risk and intervention targets; the direction depends on transmission rules. If the dataset has documented group events, use a hypergraph contagion model (Ferraz de Arruda 2024, Nat. Rev. Phys.; Battiston et al. 2026, Nat. Rev. Phys.).
7. **SIR model used for social adoption, norm diffusion, or behaviour-change spread (complex contagion)**: SIR and its variants assume single-exposure transmission — one infected contact is sufficient to trigger transition. Social adoption often requires **multiple independent reinforcing exposures** before a node adopts: the Watts threshold model. Domains where complex contagion dominates: technology adoption, social norm diffusion, feature uptake, behaviour change campaigns. Key qualitative differences from SIR: (a) clustering can facilitate reinforcement while reducing outward exposure; its net effect depends on thresholds, degree, topology and seeds, and is not universally positive for complex or negative for simple contagion; (b) the adoption threshold interacts with degree distribution differently — low-degree nodes with many threshold-crossing neighbours adopt even if global prevalence is low; (c) cascade feasibility depends jointly on thresholds, degree/connectivity, reinforcement, timing and seed placement; high clustering can help some mechanisms but is neither necessary nor sufficient. **Fix**: for social adoption questions, model the threshold fraction φᵢ (fraction of neighbours that must have adopted before node i adopts) and simulate Watts threshold dynamics. **Tool note (verified July 2026): NetworkX has no built-in Watts threshold / complex-contagion function** — there is no `threshold_model` in the NetworkX API (its `algorithms.threshold` module is for a different concept, threshold *graphs*, not contagion). Use NDlib's Linear Threshold Model (`ndlib.models.epidemics.ThresholdModel`) for a ready implementation on top of NetworkX graphs, or implement the neighbour-fraction rule directly (a handful of lines: track cumulative active-neighbour fraction per node per round). Rule: use SIR for biological spread or information forwarding; use threshold/complex contagion when mechanism is documented as requiring social reinforcement.

## Worked Example

**Illustrative model check**: on an infinite locally tree-like degree-3 configuration network, excess degree is 2. With iid transmissibility T=.4, B=.8; with T=.6, B=1.2. This is a threshold calculation, not a measured reach forecast. On a finite graph estimate reach from calibrated simulations and report seed-extinction probability, time horizon, sampling error and model uncertainty separately.

## Sources

- Newman (2010). Networks: An Introduction. §17.
- Barabási (2016). Network Science. §10. [networksciencebook.com](https://networksciencebook.com/)
- Pastor-Satorras and Vespignani (2001). Epidemic Spreading in Scale-Free Networks. Physical Review Letters. [doi:10.1103/PhysRevLett.86.3200](https://doi.org/10.1103/PhysRevLett.86.3200)
- Easley and Kleinberg (2010). Networks, Crowds, and Markets. §21.
- Ferraz de Arruda, Aleta and Moreno (2024). Contagion dynamics on higher-order networks. Nature Reviews Physics. [doi:10.1038/s42254-024-00733-0](https://doi.org/10.1038/s42254-024-00733-0) — Reviews model-dependent higher-order contagion, including bistability; not a universal SIR property.
- Battiston, Bick, Lucas, Millán, Skardal, and Zhang (2026). Collective dynamics on higher-order networks. Nature Reviews Physics 8:146-159 (preprint arXiv:2510.05253, 2025). [doi:10.1038/s42254-025-00916-3](https://doi.org/10.1038/s42254-025-00916-3) — Code: hypersync Python package https://github.com/maximelucas/hypersync. CORRECTED 2026-07-11: previously misattributed to "Iacopini et al." — Iacopini is not an author of this paper.
- Watts (2002). A simple model of global cascades on random networks. PNAS 99(9): 5766–5771. [doi:10.1073/pnas.082090499](https://doi.org/10.1073/pnas.082090499) — Foundational threshold/complex contagion model; introduces node adoption threshold φᵢ and cascade conditions on random networks.

## Related

- [`05-scale-free-networks.md`](05-scale-free-networks.md) — vanishing epidemic threshold on scale-free graphs
- [`06-percolation.md`](06-percolation.md) — SIR/percolation equivalence requires the specified transmissibility and graph assumptions
- [`11-temporal-networks.md`](11-temporal-networks.md) — temporal ordering changes reachable paths and spread predictions
- [`03-community-detection.md`](03-community-detection.md) — community boundaries act as spread barriers

Primary SIR/percolation derivation: Newman (2002), https://arxiv.org/html/cond-mat/0205009v1.
