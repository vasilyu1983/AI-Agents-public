# Primitive: Percolation

**Sources**: Albert, Jeong & Barabási (2000) Nature; Newman (2010) §16; Barabási (2016) §8.

## Definition

Percolation theory studies connectivity under node or edge removal. The central result is the **phase transition**: below a critical removal threshold, the graph retains a giant connected component (GCC) spanning most nodes; above the threshold, the GCC collapses to small disconnected fragments.

**Site percolation (node removal)**: remove each node independently with probability q. The giant component disappears at critical threshold qc.

**Bond percolation (edge removal)**: remove each edge independently with probability q.

**Two removal strategies**:

1. **Random percolation**: nodes removed uniformly at random (models random failures)
2. **Targeted percolation**: nodes removed in order of degree or betweenness (models deliberate attack)

**Critical results**:

- Erdős-Rényi random graph: qc = 1 − 1/⟨k⟩ (giant component disappears when average degree drops below 1)
- Scale-free networks: qc → 1 for random removal (extremely robust); targeted attack causes collapse at qc ≪ 1 (extremely fragile)

**Epidemic threshold connection**: R₀ = β/γ × ⟨k²⟩/⟨k⟩. A network is above the percolation threshold for epidemic spread when R₀ > 1.

## When to Use

- Assessing robustness of infrastructure, dependency, or communication networks
- Planning targeted interventions (hub removal for containment vs. random failures for resilience)
- Estimating how many nodes must be immunised to prevent epidemic spread
- Quantifying the blast radius of a change that propagates like a cascade

## Inputs

- Graph (undirected for symmetric percolation; directed for cascade analysis)
- Removal strategy: random, targeted (degree), targeted (betweenness)
- Removal sequence or fraction q

## Outputs

- Giant component size S(q) as a function of removal fraction q
- Critical threshold qc where S(q) drops sharply
- Number of connected components and their size distribution after removal

## Failure Modes

1. **Directed graphs treated as undirected**: directed graphs have separate in-component, out-component, and strongly connected component. Percolation on directed graphs is more complex and produces different thresholds for each component.
2. **Single removal sequence**: stochastic percolation should average over multiple realisations (≥ 100) to get a smooth S(q) curve.
3. **Ignoring the phase transition**: linear interpolation of S(q) misses the abrupt collapse near qc. The transition is sharp; small additional removals near qc cause disproportionate damage.
4. **Applying random-percolation resilience results to targeted-attack scenarios**: scale-free networks are robust to random failure but fragile to targeted hub attack — these are opposite results.
5. **Single-layer percolation applied to systems with cross-layer dependencies**: microservice stacks where the application tier depends on a database tier which depends on a network/infra tier are interdependent networks. In single-layer percolation, the collapse transition is second-order (gradual) — the giant component shrinks smoothly as nodes are removed. In interdependent (multilayer) networks with dependency links, the transition becomes **first-order (abrupt and catastrophic)**: a small fraction of failures can trigger sudden, complete collapse with no warning from the gradual-degradation signal. This is qualitatively different from single-layer analysis. **Fix**: if the system being modelled has genuine cross-layer dependency links (not just connectivity edges), model it as an interdependent network and expect first-order collapse behavior. Confirm cross-layer coupling before switching from single-layer percolation (Artime et al. 2024, Nat. Rev. Phys.).

## Worked Example

**Microservice dependency graph**: 80 services, 180 dependencies. Random percolation: GCC remains intact until q = 0.55 (can lose 55% of services randomly before disconnection). Targeted percolation (betweenness order): GCC collapses at q = 0.08 — removing 6 high-betweenness services disconnects the whole graph. Actionable result: replicate or circuit-break the top 6 betweenness nodes; random failures are already handled by 45% slack.

## Sources

- Albert, Jeong and Barabási (2000). Error and attack tolerance of complex networks. Nature. [doi:10.1038/35019019](https://doi.org/10.1038/35019019)
- Newman (2010). Networks: An Introduction. §16.
- Barabási (2016). Network Science. §8. [networksciencebook.com](https://networksciencebook.com/)
- Callaway, Newman, Strogatz and Watts (2000). Network robustness and fragility: Percolation on random graphs. Physical Review Letters. [doi:10.1103/PhysRevLett.85.5468](https://doi.org/10.1103/PhysRevLett.85.5468)
- Artime, Grassia, De Domenico, Gleeson, Makse, Mangioni, Perc, and Radicchi (2024). Robustness and resilience of complex networks. Nature Reviews Physics 6, 114–131. [doi:10.1038/s42254-023-00676-y](https://doi.org/10.1038/s42254-023-00676-y) — Covers multilayer/interdependent percolation, abrupt first-order transitions, optimal dismantling. Code: https://github.com/NetworkDismantling/review

## Related

- [`05-scale-free-networks.md`](05-scale-free-networks.md) — scale-free topology determines which percolation regime applies
- [`07-contagion-sir.md`](07-contagion-sir.md) — R₀ > 1 is the percolation threshold for epidemic spread
- [`01-centrality-measures.md`](01-centrality-measures.md) — betweenness identifies the most effective targeted-attack targets
